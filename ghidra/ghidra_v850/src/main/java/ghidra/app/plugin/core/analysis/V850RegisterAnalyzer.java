package ghidra.app.plugin.core.analysis;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import generic.stl.Pair;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.util.importer.MessageLog;
import ghidra.framework.options.Options;
import ghidra.program.database.ProgramCompilerSpec;
import ghidra.program.database.SpecExtension;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.data.DataType;
import ghidra.program.model.lang.CompilerSpecID;
import ghidra.program.model.lang.DecompilerLanguage;
import ghidra.program.model.lang.PrototypeModel;
import ghidra.program.model.lang.Register;
import ghidra.program.model.lang.RegisterValue;
import ghidra.program.model.listing.ContextChangeException;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Program;
import ghidra.program.model.listing.ProgramContext;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryAccessException;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.pcode.Varnode;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.util.SymbolicPropogator;
import ghidra.program.util.VarnodeContext;
import ghidra.program.model.util.PropertyMapManager;
import ghidra.program.model.util.StringPropertyMap;
import ghidra.util.Msg;
import ghidra.util.exception.CancelledException;
import ghidra.util.exception.AssertException;
import ghidra.util.exception.DuplicateNameException;
import ghidra.util.task.TaskMonitor;

/**
 * V850/RH850 constant and register propagation analyzer.
 *
 * Extends the generic constant propagation framework for the v850 processor:
 * <ul>
 * <li>tracks copies, arithmetic, initialized-memory loads, LDSR/STSR system-register
 *     moves, CFG joins and calling-convention call clobbers through the standard
 *     {@link ghidra.program.util.SymbolicPropogator} p-code flow (path-local, per
 *     function; no whole-program register value is ever assumed from a single
 *     writer);</li>
 * <li>recovers CALLT table entry addresses, data references and call targets from a
 *     path-computed CTBP (LDSR reg, CTBP with a tracked constant register) or an
 *     explicitly configured fixed seed. Recovery is two-phase: the flow only
 *     records the CTBP seen at each CALLT site on every path, and sites whose
 *     value did not agree on all flowed paths (conditional or conflicting
 *     setups) stay unresolved; the generic LOAD/CALLIND references the
 *     propagator would derive from the callt p-code are suppressed, since they
 *     would be single-path speculation and would treat values read from
 *     untrusted writable memory as call targets. Table entries are only read
 *     from initialized memory trusted per the analyzer's writable-memory
 *     option, and a target must be mapped, executable and 2-byte aligned
 *     before any COMPUTED_CALL reference, disassembly or function is produced.
 *     A halfword offset of zero is a legal relative offset (target = CTBP
 *     itself) and is not special-cased;</li>
 * <li>seeds fixed CTBP/GP/TP/EP values at flow starts when explicitly configured.
 *     Persisted ownership records retain the prior context, so clearing a fixed
 *     option restores only this analyzer's seeds and leaves externally supplied
 *     context intact. Defaults preserve existing context and recover dynamic
 *     values from the instruction flow;</li>
 * <li>supports an exact selectable callee-save policy over {ep, gp, tp, r2}: empty
 *     keeps the program's compiler spec untouched; "none" makes all four volatile;
 *     a non-empty subset makes the selected registers callee-saved and forces the
 *     remaining registers volatile. The policy selects a generated native
 *     compiler spec, preserving argument/return placement while changing the
 *     default and EVAL_CALLED contracts for direct and unresolved indirect calls.
 *     Clearing the option restores only this analyzer's owned compiler choice.
 *     Existing program extensions and their consumers survive the migration.
 *     Non-default explicit conventions and custom storage are preserved;
 *     user-supplied types still receive the selected compiler ABI.</li>
 * </ul>
 */
public class V850RegisterAnalyzer extends ConstantPropagationAnalyzer {

	private static final String PROCESSOR_NAME = "v850";

	static final String OPTION_FIXED_CTBP = "Fixed CTBP value";
	static final String OPTION_FIXED_CTBP_DESC =
		"Hex address of the CALLT table base (CTBP) to seed at function entries. " +
			"Empty (default) preserves existing context and recovers dynamic values per path.";

	static final String OPTION_FIXED_GP = "Fixed GP value";
	static final String OPTION_FIXED_GP_DESC =
		"Hex address to seed into the global pointer (r4) at function entries. " +
			"Empty (default) preserves existing GP context.";

	static final String OPTION_FIXED_TP = "Fixed TP value";
	static final String OPTION_FIXED_TP_DESC =
		"Hex address to seed into the text/small-data pointer (r5) at function entries. " +
			"Empty (default) preserves existing TP context.";

	static final String OPTION_FIXED_EP = "Fixed EP value";
	static final String OPTION_FIXED_EP_DESC =
		"Hex address to seed into the element pointer (r30) at function entries. " +
			"Empty (default) preserves existing EP context.";

	static final String OPTION_RECOVER_CALLT = "Recover CALLT targets";
	static final String OPTION_RECOVER_CALLT_DESC =
		"Lay down READ references and word data at CALLT table entries and, for " +
			"mapped executable 2-byte-aligned targets, COMPUTED_CALL references, " +
			"disassembly and functions. Writable table memory is trusted only when " +
			"\"Trust values read from writable memory\" is enabled.";

	static final String OPTION_CALLEE_SAVE_REGISTERS = "Callee-save policy registers";
	static final String OPTION_CALLEE_SAVE_REGISTERS_DESC =
		"Exact callee-save policy over the four IDA-style global registers: empty " +
			"(default) keeps the program's compiler spec unchanged; \"none\" makes " +
			"ep, gp, tp and r2 all volatile; a comma/space-separated subset of " +
			"ep, gp, tp, r2 makes those registers callee-saved and forces the rest " +
			"of the four volatile. Selects a native compiler-spec policy variant " +
			"for direct and unresolved indirect calls, changing both decompiler " +
			"call contracts and call-clobber tracking. Clearing restores the prior " +
			"compiler choice without discarding user extensions. " +
			"Argument and return placement are preserved.";

	/** Registers governed by the callee-save policy, in canonical name order. */
	static final List<String> POLICY_REGISTERS = List.of("ep", "gp", "tp", "r2");

	private static final String POLICY_NONE = "none";

	private Register ctbpReg;
	private Register gpReg;
	private Register tpReg;
	private Register epReg;

	private Address fixedCtbp;
	private Address fixedGp;
	private Address fixedTp;
	private Address fixedEp;

	private boolean recoverCalltTargets = true;

	private String policyConventionName;

	public V850RegisterAnalyzer() {
		super(PROCESSOR_NAME);
	}

	@Override
	public boolean canAnalyze(Program program) {
		boolean canAnalyze = super.canAnalyze(program);
		if (!canAnalyze) {
			return false;
		}
		ctbpReg = program.getRegister("CTBP");
		gpReg = program.getRegister("gp");
		tpReg = program.getRegister("tp");
		epReg = program.getRegister("ep");
		return true;
	}

	@Override
	public boolean getDefaultEnablement(Program program) {
		return true;
	}

	@Override
	public boolean added(Program program, AddressSetView set, TaskMonitor monitor, MessageLog log)
			throws CancelledException {
		applyCalleeSavePolicy(program, monitor);
		return super.added(program, set, monitor, log);
	}

	@Override
	public AddressSetView flowConstants(final Program program, Address flowStart,
			AddressSetView flowSet, final SymbolicPropogator symEval, final TaskMonitor monitor)
			throws CancelledException {

		final Function func = program.getFunctionManager().getFunctionContaining(flowStart);
		Address start = flowStart;
		if (func != null) {
			start = func.getEntryPoint();
			V850GccReturnAnalyzer.applyToFunction(program, func, monitor);
		}

		seedRegister(program, ctbpReg, fixedCtbp, start, "V850 fixed CTBP seed");
		seedRegister(program, gpReg, fixedGp, start, "V850 fixed GP seed");
		seedRegister(program, tpReg, fixedTp, start, "V850 fixed TP seed");
		seedRegister(program, epReg, fixedEp, start, "V850 fixed EP seed");

		Map<Address, CalltSite> calltSites = new LinkedHashMap<>();
		ConstantPropagationContextEvaluator eval = new V850ContextEvaluator(monitor, calltSites);
		// NB: setMinStoreLoadOffset first; in this Ghidra version it (buggily)
		// assigns maxSpeculativeOffset, so a later order would clobber the
		// speculative bound computed in canAnalyze().
		eval.setMinStoreLoadOffset(minStoreLoadRefAddress)
				.setMinSpeculativeOffset(minSpeculativeRefAddress)
				.setMaxSpeculativeOffset(maxSpeculativeRefAddress)
				.setCreateComplexDataFromPointers(createComplexDataFromPointers)
				.setTrustWritableMemory(trustWriteMemOption);

		AddressSetView flowed = symEval.flowConstants(start, flowSet, eval, true, monitor);
		resolveCalltSites(program, calltSites, monitor);
		return flowed;
	}

	@Override
	public void registerOptions(Options options, Program program) {
		super.registerOptions(options, program);
		options.registerOption(OPTION_FIXED_CTBP, "", null, OPTION_FIXED_CTBP_DESC);
		options.registerOption(OPTION_FIXED_GP, "", null, OPTION_FIXED_GP_DESC);
		options.registerOption(OPTION_FIXED_TP, "", null, OPTION_FIXED_TP_DESC);
		options.registerOption(OPTION_FIXED_EP, "", null, OPTION_FIXED_EP_DESC);
		options.registerOption(OPTION_RECOVER_CALLT, recoverCalltTargets, null,
			OPTION_RECOVER_CALLT_DESC);
		options.registerOption(OPTION_CALLEE_SAVE_REGISTERS, "", null,
			OPTION_CALLEE_SAVE_REGISTERS_DESC);
	}

	@Override
	public void optionsChanged(Options options, Program program) {
		super.optionsChanged(options, program);
		fixedCtbp = parseSeed(program, options.getString(OPTION_FIXED_CTBP, ""), OPTION_FIXED_CTBP);
		fixedGp = parseSeed(program, options.getString(OPTION_FIXED_GP, ""), OPTION_FIXED_GP);
		fixedTp = parseSeed(program, options.getString(OPTION_FIXED_TP, ""), OPTION_FIXED_TP);
		fixedEp = parseSeed(program, options.getString(OPTION_FIXED_EP, ""), OPTION_FIXED_EP);
		recoverCalltTargets = options.getBoolean(OPTION_RECOVER_CALLT, recoverCalltTargets);
		parseCalleeSaveRegisters(options.getString(OPTION_CALLEE_SAVE_REGISTERS, ""));
	}

	/**
	 * Parse the exact callee-save policy. Empty keeps the compiler default,
	 * "none" selects the all-volatile policy, otherwise a subset of
	 * {@link #POLICY_REGISTERS}. An invalid document (including "none" mixed
	 * with register names) disables the policy loudly.
	 */
	private void parseCalleeSaveRegisters(String value) {
		policyConventionName = null;
		if (value == null || value.trim().isEmpty()) {
			return;
		}
		Set<String> selected = new LinkedHashSet<>();
		for (String token : value.trim().split("[,;\\s]+")) {
			String name = token.toLowerCase();
			if (POLICY_NONE.equals(name) && selected.isEmpty() &&
				value.trim().split("[,;\\s]+").length == 1) {
				policyConventionName = POLICY_NONE;
				return;
			}
			if (!POLICY_REGISTERS.contains(name)) {
				Msg.error(this, "v850: unrecognized " + OPTION_CALLEE_SAVE_REGISTERS +
					" token \"" + token + "\"; expected \"none\" or a subset of " +
					POLICY_REGISTERS + "; ignoring the whole option");
				policyConventionName = null;
				return;
			}
			selected.add(name);
		}
		List<String> ordered = new ArrayList<>();
		for (String name : POLICY_REGISTERS) {
			if (selected.contains(name)) {
				ordered.add(name);
			}
		}
		policyConventionName = String.join("_", ordered);
	}

	private Address parseSeed(Program program, String value, String optionName) {
		if (value == null) {
			return null;
		}
		String trimmed = value.trim();
		if (trimmed.isEmpty()) {
			return null;
		}
		try {
			long offset = Long.decode(trimmed);
			return program.getAddressFactory()
					.getDefaultAddressSpace()
					.getAddress(offset, true);
		}
		catch (NumberFormatException e) {
			Msg.error(this, "v850: invalid address for " + optionName + ": \"" + value + "\"");
			return null;
		}
	}

	/**
	 * Fixed options temporarily own an entry-point context value. Record both the
	 * original masked value and the installed seed; never remove another producer's
	 * context when the option is empty or the user has since changed the value.
	 */
	private void seedRegister(Program program, Register reg, Address value, Address at,
			String propertyName) {
		if (reg == null) {
			return;
		}
		PropertyMapManager properties = program.getUsrPropertyManager();
		StringPropertyMap seeds = properties.getStringPropertyMap(propertyName);
		String owned = seeds == null ? null : seeds.getString(at);
		if (value == null && owned == null) {
			return;
		}
		ProgramContext context = program.getProgramContext();
		RegisterValue current = context.getRegisterValue(reg, at);
		int separator = owned == null ? -1 : owned.indexOf(':');
		boolean stillOwned = owned != null && current != null && current.hasValue() &&
			current.getUnsignedValue().equals(new BigInteger(owned.substring(separator + 1), 16));
		try {
			if (value == null) {
				if (stillOwned) {
					context.remove(at, at, reg);
					String original = owned.substring(0, separator);
					if (!original.equals("-")) {
						context.setRegisterValue(at, at,
							new RegisterValue(reg, HexFormat.of().parseHex(original)));
					}
				}
				seeds.remove(at);
				return;
			}
			BigInteger desired = BigInteger.valueOf(value.getOffset());
			if (current != null && current.hasValue() &&
				current.getUnsignedValue().equals(desired)) {
				return;
			}
			String original = stillOwned ? owned.substring(0, separator) :
				current == null ? "-" : HexFormat.of().formatHex(current.toBytes());
			if (seeds == null) {
				synchronized (properties) {
					seeds = properties.getStringPropertyMap(propertyName);
					if (seeds == null) {
						seeds = properties.createStringPropertyMap(propertyName);
					}
				}
			}
			context.setRegisterValue(at, at, new RegisterValue(reg, desired));
			seeds.add(at, original + ":" + desired.toString(16));
		}
		catch (ContextChangeException | DuplicateNameException e) {
			throw new AssertException("Cannot record fixed " + reg.getName(), e);
		}
	}

	// ------------------------------------------------------------------
	// Callee-save policy (exact ep/gp/tp/r2 preserved/volatile selection)
	// ------------------------------------------------------------------

	private void applyCalleeSavePolicy(Program program, TaskMonitor monitor)
			throws CancelledException {
		Options ownership = program.getOptions("V850 ABI policy");
		String current = program.getCompilerSpec().getCompilerSpecID().toString();
		String owned = ownership.getString("Owned compiler spec", "");
		String original = ownership.getString("Original compiler spec", "");
		String desired = current;
		if (policyConventionName == null) {
			if (current.equals(owned) && !original.isEmpty()) {
				desired = original;
			}
		}
		else {
			if (!current.equals(owned)) {
				original = current;
			}
			String base = current.split("-callee-", 2)[0];
			desired = base + "-callee-" + policyConventionName;
		}
		boolean changed = !desired.equals(current);
		if (changed) {
			changeCompilerSpec(program, desired, monitor);
		}
		if (policyConventionName == null) {
			ownership.removeOption("Owned compiler spec");
			ownership.removeOption("Original compiler spec");
		}
		else {
			ownership.setString("Original compiler spec", original);
			ownership.setString("Owned compiler spec", desired);
		}
		if (!changed || !V850GccReturnAnalyzer.usesOldGcc(program)) {
			return;
		}
		FunctionIterator iterator = program.getFunctionManager().getFunctions(true);
		while (iterator.hasNext()) {
			monitor.checkCancelled();
			V850GccReturnAnalyzer.applyToFunction(program, iterator.next(), monitor);
		}
	}

	private record ExtensionContract(Address entry, String convention, String fixup) {}

	/**
	 * Compiler-only migration uses Ghidra's native default/EVAL_CALLED model,
	 * so an unresolved CALLIND receives the same preservation as a direct call.
	 * setLanguage clears program extensions; retain their XML and consumers.
	 */
	private void changeCompilerSpec(Program program, String desired, TaskMonitor monitor)
			throws CancelledException {
		List<Pair<String, String>> extensions = SpecExtension.getCompilerSpecExtensions(program);
		List<ExtensionContract> contracts = new ArrayList<>();
		FunctionIterator iterator = program.getFunctionManager().getFunctions(true);
		while (iterator.hasNext()) {
			monitor.checkCancelled();
			Function function = iterator.next();
			PrototypeModel model = function.getCallingConvention();
			String convention = model != null && model.isProgramExtension() ? model.getName() : null;
			String fixup = function.getCallFixup();
			if (convention != null || fixup != null) {
				contracts.add(new ExtensionContract(function.getEntryPoint(), convention, fixup));
			}
		}
		Options decompiler = program.getOptions(ProgramCompilerSpec.DECOMPILER_PROPERTY_LIST_NAME);
		String evaluation = decompiler.getString(ProgramCompilerSpec.EVALUATION_MODEL_PROPERTY_NAME, null);
		DecompilerLanguage output = decompiler.getEnum(
			ProgramCompilerSpec.DECOMPILER_OUTPUT_LANGUAGE, ProgramCompilerSpec.DECOMPILER_OUTPUT_DEF);
		try {
			program.setLanguage(program.getLanguage(), new CompilerSpecID(desired), false, monitor);
			SpecExtension installer = new SpecExtension(program);
			for (Pair<String, String> extension : extensions) {
				monitor.checkCancelled();
				installer.addReplaceCompilerSpecExtension(extension.second, monitor);
			}
			for (ExtensionContract contract : contracts) {
				monitor.checkCancelled();
				Function function = program.getFunctionManager().getFunctionAt(contract.entry());
				if (contract.convention() != null) {
					function.setCallingConvention(contract.convention());
				}
				if (contract.fixup() != null) {
					function.setCallFixup(contract.fixup());
				}
			}
			if (evaluation != null) {
				decompiler.setString(ProgramCompilerSpec.EVALUATION_MODEL_PROPERTY_NAME, evaluation);
			}
			decompiler.setEnum(ProgramCompilerSpec.DECOMPILER_OUTPUT_LANGUAGE, output);
		}
		catch (CancelledException e) {
			throw e;
		}
		catch (Exception e) {
			throw new AssertException("Cannot select V850 callee-save compiler spec " + desired, e);
		}
	}


	// ------------------------------------------------------------------
	// CALLT recovery (join-consistent CTBP or explicit fixed seed)
	// ------------------------------------------------------------------

	/**
	 * Evaluator hooking CALLT recovery into the standard constant propagation
	 * flow. Generic p-code tracking (copies, arithmetic, loads, LDSR/STSR,
	 * joins, call clobbers) is inherited from the propagator; CALLT sites are
	 * recovered by this analyzer in two phases.
	 * <p>
	 * During the flow the evaluator only records, per CALLT site, the CTBP
	 * value seen on each flowed path. It also suppresses the references the
	 * generic propagator would derive from the callt p-code itself: the LOAD
	 * of the table entry and the indirect call both feed
	 * {@code makeReference}, and {@code VarnodeContext.isConstant} treats
	 * suspect constants (values read from memory the writable-memory trust
	 * option rejects) as constants, so those references would be single-path
	 * speculation that bypasses both the trust option and CFG joins.
	 * <p>
	 * Once the flow completes, {@link #resolveCalltSites} commits only the
	 * sites whose CTBP value agreed on every flowed path.
	 */
	private class V850ContextEvaluator extends ConstantPropagationContextEvaluator {

		private final Map<Address, CalltSite> calltSites;
		/** True when this analyzer's CALLT recovery is operational and owns
		 *  all reference production for callt instructions. */
		private final boolean ownsCallt;

		V850ContextEvaluator(TaskMonitor monitor, Map<Address, CalltSite> calltSites) {
			super(monitor);
			this.calltSites = calltSites;
			this.ownsCallt = recoverCalltTargets && ctbpReg != null;
		}

		@Override
		public boolean evaluateContextBefore(VarnodeContext context, Instruction instr) {
			// Capture the incoming base before CALLIND invalidates volatile
			// registers. Post-instruction CTBP describes the callee's effects.
			if (ownsCallt && "callt".equals(instr.getMnemonicString())) {
				observeCallt(context, instr, calltSites);
			}
			return false; // never stop the flow
		}

		@Override
		public boolean evaluateReference(VarnodeContext context, Instruction instr, int pcodeop,
				Address address, int size, DataType dataType, RefType refType) {
			if (ownsCallt && "callt".equals(instr.getMnemonicString())) {
				// CALLT references (table-entry READ, COMPUTED_CALL target)
				// are produced only by the join-consistent commit phase; the
				// generic LOAD/CALLIND path would emit them from a single
				// path's speculation, treating suspect constants read from
				// untrusted writable memory as call targets.
				return false;
			}
			return super.evaluateReference(context, instr, pcodeop, address, size, dataType,
				refType);
		}
	}

	/** One CALLT site with every CTBP value observed on paths that reached it. */
	private static final class CalltSite {
		final long imm;
		final Set<Long> ctbpValues = new LinkedHashSet<>();
		boolean unknownPath;

		CalltSite(long imm) {
			this.imm = imm;
		}
	}

	private void observeCallt(VarnodeContext context, Instruction instr,
			Map<Address, CalltSite> calltSites) {
		if (!recoverCalltTargets || ctbpReg == null) {
			return;
		}
		Object[] operands = instr.getOpObjects(0);
		if (operands == null || operands.length == 0 || !(operands[0] instanceof Scalar scalar)) {
			return;
		}
		CalltSite site = calltSites.computeIfAbsent(instr.getMinAddress(),
			address -> new CalltSite(scalar.getUnsignedValue()));
		BigInteger value = context.getValue(ctbpReg, false);
		if (value == null) {
			site.unknownPath = true; // CTBP unknown on this path (unset, conflicting or unknown source)
		}
		else {
			site.ctbpValues.add(Long.valueOf(value.longValue() & 0xffffffffL));
		}
	}

	/**
	 * Commit CALLT recovery for the sites whose CTBP value is identical on
	 * every flowed path that reached the instruction. A CTBP established on
	 * only some paths (conditional setup, conflicting writers) leaves the
	 * site unresolved: references, data and functions must not be produced
	 * from single-path speculation.
	 */
	private void resolveCalltSites(Program program, Map<Address, CalltSite> calltSites,
			TaskMonitor monitor) throws CancelledException {
		if (!recoverCalltTargets || ctbpReg == null || calltSites.isEmpty()) {
			return;
		}
		for (Map.Entry<Address, CalltSite> entry : calltSites.entrySet()) {
			monitor.checkCancelled();
			CalltSite site = entry.getValue();
			if (site.unknownPath || site.ctbpValues.size() != 1) {
				continue;
			}
			Instruction instr = program.getListing().getInstructionAt(entry.getKey());
			if (instr == null || !"callt".equals(instr.getMnemonicString())) {
				continue;
			}
			resolveCallt(program, instr, site.imm, site.ctbpValues.iterator().next(), monitor);
		}
	}

	private void resolveCallt(Program program, Instruction instr, long imm, long ctbp,
			TaskMonitor monitor) {
		Memory memory = program.getMemory();

		Address tableEntry = instr.getMinAddress()
				.getAddressSpace()
				.getAddress((ctbp + (imm << 1)) & 0xffffffffL, true);
		MemoryBlock block = memory.getBlock(tableEntry);
		if (block == null || !block.isInitialized()) {
			return;
		}
		// Writable CALLT tables are only trusted when the analyzer is
		// configured to trust writable memory.
		if (block.isWrite() && !trustWriteMemOption) {
			return;
		}
		int halfword;
		try {
			halfword = memory.getShort(tableEntry) & 0xffff;
		}
		catch (MemoryAccessException e) {
			return;
		}
		// A halfword offset of zero is legal: the target is CTBP itself.

		Address target = instr.getMinAddress()
				.getAddressSpace()
				.getAddress((ctbp + halfword) & 0xffffffffL, true);

		if (!hasReference(instr, tableEntry, RefType.READ)) {
			instr.addOperandReference(0, tableEntry, RefType.READ, SourceType.ANALYSIS);
		}
		createData(program, tableEntry, 2);

		// Only resolve flow for mapped, executable, 2-byte-aligned instruction
		// starts; never emit COMPUTED_CALL into data, unmapped or odd targets.
		if (!memory.contains(target) || !memory.getExecuteSet().contains(target) ||
			(target.getOffset() & 1) != 0) {
			return;
		}
		if (!hasReference(instr, target, RefType.COMPUTED_CALL)) {
			instr.addMnemonicReference(target, RefType.COMPUTED_CALL, SourceType.ANALYSIS);
		}
		if (program.getListing().getUndefinedDataAt(target) != null) {
			new DisassembleCommand(target, null, true).applyTo(program, monitor);
		}
		if (program.getListing().getInstructionAt(target) != null &&
			program.getFunctionManager().getFunctionAt(target) == null &&
			program.getFunctionManager().getFunctionContaining(target) == null) {
			CreateFunctionCmd cmd = new CreateFunctionCmd(target);
			cmd.applyTo(program, monitor);
		}
	}

	private boolean hasReference(Instruction instr, Address toAddress, RefType refType) {
		for (Reference reference : instr.getReferencesFrom()) {
			if (reference.getToAddress().equals(toAddress) &&
				reference.getReferenceType() == refType) {
				return true;
			}
		}
		return false;
	}
}
