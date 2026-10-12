/* V850/RH850 compiler-helper identification.
 *
 * Recovers the stripped prologue/epilogue helper functions emitted by the GCC
 * and Green Hills MULTI V850/RH850 code generators, and applies the GHS MULTI
 * 64-bit arithmetic runtime contracts to contract-established names.
 *
 * The recognized bodies, entry offsets, register layouts and call/tail
 * conventions follow the public behavior of the IDA SDK nec850 sample module
 * (src/module/nec850/spcfuncs.cpp, emu_frame.cpp) and the observed GHS MULTI
 * RH850 runtime ABI (64-bit operands in r6:r7 / r8:r9, result in r10:r11,
 * boolean results in r10).
 *
 * Recognized helper families (byte/instruction-exact, near-matches rejected):
 *   GCC  __save_rN[_rM[_r31]]       add -N,sp; st.w...; jmp [r10]
 *   GCC  __return_rN[_rM[_r31]]     ld.w...; add N,sp; jmp [lp] (jr tail form)
 *   GHS  __ghssaveNN[a] / __ghssavelp[a]
 *   GHS  __ghsloadNN
 *   GHS  ___ghssv{4,5}{lp,rNN}      callt save (prepare/stsr/ctret)
 *   GHS  ___ghsld{2,4}{lp,rNN}      callt return (dispose/release)
 *
 * 64-bit arithmetic contracts (call fixups + signatures) are applied to
 * contract-established names: the GHS MULTI runtime (gh_add64, gh_div64,
 * ...) and the GCC libgcc DI-mode routines (__adddi3, __udivdi3, __negdi2,
 * __ashldi3, the three-way __cmpdi2/__ucmpdi2, the overflow-checked
 * __addvdi3 family). Stripped (default-named) bodies are recovered only by
 * equivalence-grade recognition: the shared V850ArithmeticReferenceMatcher
 * proves the body against the pinned GCC 16.2.0 reference corpus (libgcc
 * objects and the compiler's freestanding -O2 idioms, with validated
 * relocation/constant-table bindings), and a byte-exact linear idiom
 * covers the GHS register-pair logic helpers. The earlier symbolic
 * path-set engine was removed: an unordered set of exit expressions cannot
 * prove branch-predicate association, stack/preserved-register/lp
 * preservation, r0 discard semantics, or non-returning call targets.
 *
 * Compiler effects are real p-code, not labels: save/restore helpers are
 * marked inline so the decompiler executes their true store/stack p-code in
 * the caller, including the GHS dynamic locals allocation read from the
 * halfword preceding the helper call. Arithmetic helpers receive compiler-spec
 * call fixups (see data/languages/v850_helper_callfixups.xml) that fold the
 * call into the corresponding 64-bit p-code operation with correct
 * signedness. GHS CALLT call sites are resolved by V850RegisterAnalyzer (the
 * CTBP/CALLT dataflow owner, which runs earlier); this analyzer consumes the
 * recovered call references to identify, inline, and annotate the helpers.
 * The arithmetic payloads come from the module's shared fragment
 * (data/languages/v850_helper_callfixups.xml), installed per-program via a
 * compiler-spec extension; a missing payload fails the analyzer loudly.
 */
package ghidra.app.plugin.core.analysis;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.io.IOException;
import java.io.StringWriter;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

import generic.jar.ResourceFile;
import ghidra.app.cmd.function.ApplyFunctionSignatureCmd;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.plugin.core.clear.ClearFlowAndRepairCmd;
import ghidra.framework.Application;
import ghidra.framework.options.Options;
import ghidra.app.services.AbstractAnalyzer;
import ghidra.app.services.AnalysisPriority;
import ghidra.app.services.AnalyzerType;
import ghidra.app.util.importer.MessageLog;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.data.CategoryPath;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DataTypeManager;
import ghidra.program.model.data.FunctionDefinitionDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.LongLongDataType;
import ghidra.program.model.data.ParameterDefinitionImpl;
import ghidra.program.model.data.Undefined8DataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.UnsignedLongLongDataType;
import ghidra.program.model.data.WordDataType;
import ghidra.program.model.lang.InjectPayload;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.listing.Program;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.util.exception.CancelledException;
import ghidra.util.exception.DuplicateNameException;
import ghidra.util.exception.InvalidInputException;
import ghidra.util.task.TaskMonitor;
import ghidra.program.database.SpecExtension;
import ghidra.util.Msg;

public class V850CompilerHelperAnalyzer extends AbstractAnalyzer {

	private static final String NAME = "V850 Compiler Helper Identification";
	private static final String DESCRIPTION = "Recovers stripped GCC/GHS MULTI V850 save/restore helper " +
		"functions (with real decompiler stack/saved-register effects via inlining), GHS CALLT helper " +
		"tables, and 64-bit arithmetic runtime contracts via compiler-spec call fixups - applied to " +
		"GHS/GCC runtime names and to stripped bodies proven equivalent to the pinned GCC reference " +
		"corpus by the shared arithmetic reference matcher (plus exact linear GHS idioms)";

	private static final String PROCESSOR = "v850";

	/** Module data path of the shared GHS call-fixup fragment (sole source). */
	private static final String FRAGMENT_PATH = "languages/v850_helper_callfixups.xml";

	/** Helper families, mirroring the public IDA SDK nec850 classification. */
	enum HelperKind {
		GCC_SAVE, GCC_RETURN, GHS_SAVE, GHS_LOAD, GHS_CALLT_SAVE, GHS_CALLT_LOAD
	}

	/** Recognition result shared by the body matchers and the name grammar. */
	static class HelperInfo {
		Address entry;
		String name;
		HelperKind kind;
		/** First saved register rN (20..29), or -1 when only LP is saved. */
		int reglo = -1;
		/** Registers stored by the helper, in store order. */
		List<String> savedRegs = new ArrayList<>();
		/** True when the helper performs the GHS dynamic locals allocation/release. */
		boolean locals;
		/** True when this is a CALLT save/return helper (invoked via callt). */
		boolean callt;

		HelperInfo(Address entry, String name, HelperKind kind) {
			this.entry = entry;
			this.name = name;
			this.kind = kind;
		}

		boolean isSave() {
			return kind == HelperKind.GCC_SAVE || kind == HelperKind.GHS_SAVE ||
				kind == HelperKind.GHS_CALLT_SAVE;
		}
	}

	/** GHS MULTI 64-bit arithmetic runtime contract (call-fixup + signature). */
	static class ArithContract {
		final String fixupName;
		final String returnType;
		final String[] argTypes;

		ArithContract(String fixupName, String returnType, String... argTypes) {
			this.fixupName = fixupName;
			this.returnType = returnType;
			this.argTypes = argTypes;
		}
	}

	/**
	 * GHS MULTI 64-bit runtime names (normalized: leading underscores stripped).
	 * Semantics follow the RH850 MULTI contracts: 64-bit arguments in
	 * r6:r7 and r8:r9, 64-bit results in r10:r11, boolean results in r10.
	 */
	private static final Map<String, ArithContract> ARITH_CONTRACTS = buildArithContracts();

	private static Map<String, ArithContract> buildArithContracts() {
		Map<String, ArithContract> m = new HashMap<>();
		// 64-bit binary arithmetic/logic.
		m.put("gh_add64", new ArithContract("v850_ghs_add64", "longlong", "longlong", "longlong"));
		m.put("gh_sub64", new ArithContract("v850_ghs_sub64", "longlong", "longlong", "longlong"));
		m.put("gh_mul64", new ArithContract("v850_ghs_mul64", "longlong", "longlong", "longlong"));
		m.put("gh_mul64o", new ArithContract("v850_ghs_mul64", "longlong", "longlong", "longlong"));
		m.put("COM_mul64", new ArithContract("v850_ghs_mul64", "longlong", "longlong", "longlong"));
		m.put("gh_and64", new ArithContract("v850_ghs_and64", "longlong", "longlong", "longlong"));
		m.put("gh_or64", new ArithContract("v850_ghs_or64", "longlong", "longlong", "longlong"));
		m.put("gh_xor64", new ArithContract("v850_ghs_xor64", "longlong", "longlong", "longlong"));
		// Division/remainder with explicit signedness.
		m.put("gh_div64", new ArithContract("v850_ghs_div64", "longlong", "longlong", "longlong"));
		m.put("COM_div64", new ArithContract("v850_ghs_div64", "longlong", "longlong", "longlong"));
		m.put("gh_udiv64",
			new ArithContract("v850_ghs_udiv64", "ulonglong", "ulonglong", "ulonglong"));
		m.put("COM_udiv64",
			new ArithContract("v850_ghs_udiv64", "ulonglong", "ulonglong", "ulonglong"));
		m.put("gh_rem64", new ArithContract("v850_ghs_rem64", "longlong", "longlong", "longlong"));
		m.put("COM_rem64", new ArithContract("v850_ghs_rem64", "longlong", "longlong", "longlong"));
		m.put("gh_urem64",
			new ArithContract("v850_ghs_urem64", "ulonglong", "ulonglong", "ulonglong"));
		m.put("COM_urem64",
			new ArithContract("v850_ghs_urem64", "ulonglong", "ulonglong", "ulonglong"));
		// Unary.
		m.put("gh_neg64", new ArithContract("v850_ghs_neg64", "longlong", "longlong"));
		m.put("COM_neg64", new ArithContract("v850_ghs_neg64", "longlong", "longlong"));
		m.put("gh_abs64", new ArithContract("v850_ghs_abs64", "longlong", "longlong"));
		// Shifts: 64-bit value, count in r8 (32-bit) or r8:r9 (64-bit).
		m.put("gh_shll_64_32",
			new ArithContract("v850_ghs_shll_64_32", "ulonglong", "ulonglong", "uint"));
		m.put("gh_shll64_32",
			new ArithContract("v850_ghs_shll_64_32", "ulonglong", "ulonglong", "uint"));
		m.put("COM_shll_64_32",
			new ArithContract("v850_ghs_shll_64_32", "ulonglong", "ulonglong", "uint"));
		m.put("gh_shrl_64_32",
			new ArithContract("v850_ghs_shrl_64_32", "ulonglong", "ulonglong", "uint"));
		m.put("gh_shrl64_32",
			new ArithContract("v850_ghs_shrl_64_32", "ulonglong", "ulonglong", "uint"));
		m.put("COM_shrl_64_32",
			new ArithContract("v850_ghs_shrl_64_32", "ulonglong", "ulonglong", "uint"));
		m.put("gh_shra_64_32",
			new ArithContract("v850_ghs_shra_64_32", "longlong", "longlong", "uint"));
		m.put("gh_shra64_32",
			new ArithContract("v850_ghs_shra_64_32", "longlong", "longlong", "uint"));
		m.put("COM_shra_64_32",
			new ArithContract("v850_ghs_shra_64_32", "longlong", "longlong", "uint"));
		m.put("gh_shll_64_64",
			new ArithContract("v850_ghs_shll_64_64", "ulonglong", "ulonglong", "ulonglong"));
		m.put("gh_shll64_64",
			new ArithContract("v850_ghs_shll_64_64", "ulonglong", "ulonglong", "ulonglong"));
		m.put("gh_shrl_64_64",
			new ArithContract("v850_ghs_shrl_64_64", "ulonglong", "ulonglong", "ulonglong"));
		m.put("gh_shrl64_64",
			new ArithContract("v850_ghs_shrl_64_64", "ulonglong", "ulonglong", "ulonglong"));
		m.put("gh_shra_64_64",
			new ArithContract("v850_ghs_shra_64_64", "longlong", "longlong", "longlong"));
		m.put("gh_shra64_64",
			new ArithContract("v850_ghs_shra_64_64", "longlong", "longlong", "longlong"));
		// Combined long shifts (GHS __gh_* spellings).
		m.put("gh_lsh64",
			new ArithContract("v850_ghs_shll_64_32", "ulonglong", "ulonglong", "uint"));
		m.put("gh_rsh64",
			new ArithContract("v850_ghs_shrl_64_32", "ulonglong", "ulonglong", "uint"));
		m.put("gh_rsa64", new ArithContract("v850_ghs_shra_64_32", "longlong", "longlong", "uint"));
		m.put("gh_lsa64",
			new ArithContract("v850_ghs_shll_64_32", "ulonglong", "ulonglong", "uint"));
		// Comparisons: boolean result in r10.
		m.put("gh_eq64", new ArithContract("v850_ghs_eq64", "int", "longlong", "longlong"));
		m.put("gh_ne64", new ArithContract("v850_ghs_ne64", "int", "longlong", "longlong"));
		m.put("gh_lt64", new ArithContract("v850_ghs_lt64", "int", "longlong", "longlong"));
		m.put("gh_le64", new ArithContract("v850_ghs_le64", "int", "longlong", "longlong"));
		m.put("gh_ult64", new ArithContract("v850_ghs_ult64", "int", "ulonglong", "ulonglong"));
		m.put("gh_ule64", new ArithContract("v850_ghs_ule64", "int", "ulonglong", "ulonglong"));
		// GCC libgcc DI-mode arithmetic (leading underscores are normalized
		// away by applyNamedContract, so __adddi3 is keyed as adddi3). The
		// register ABI matches the GHS contracts (GCC 16.2 v850: DImode
		// arguments occupy the r6:r7 / r8:r9 pairs, results return in
		// r10:r11). GCC shifts have separate payloads: their compiled
		// 32-bit branch/count behavior is not a modulo-64 shift.
		m.put("adddi3", new ArithContract("v850_ghs_add64", "longlong", "longlong", "longlong"));
		m.put("subdi3", new ArithContract("v850_ghs_sub64", "longlong", "longlong", "longlong"));
		m.put("muldi3", new ArithContract("v850_ghs_mul64", "longlong", "longlong", "longlong"));
		m.put("divdi3", new ArithContract("v850_ghs_div64", "longlong", "longlong", "longlong"));
		m.put("udivdi3",
			new ArithContract("v850_ghs_udiv64", "ulonglong", "ulonglong", "ulonglong"));
		m.put("moddi3", new ArithContract("v850_ghs_rem64", "longlong", "longlong", "longlong"));
		m.put("umoddi3",
			new ArithContract("v850_ghs_urem64", "ulonglong", "ulonglong", "ulonglong"));
		m.put("negdi2", new ArithContract("v850_ghs_neg64", "longlong", "longlong"));
		m.put("ashldi3",
			new ArithContract("v850_gcc_ashldi3", "ulonglong", "ulonglong", "uint"));
		m.put("ashrdi3", new ArithContract("v850_gcc_ashrdi3", "longlong", "longlong", "uint"));
		m.put("lshrdi3",
			new ArithContract("v850_gcc_lshrdi3", "ulonglong", "ulonglong", "uint"));
		// libgcc __cmpdi2/__ucmpdi2 return three-way 0 (a<b), 1 (a==b),
		// 2 (a>b) in r10 - NOT a boolean.
		m.put("cmpdi2", new ArithContract("v850_gcc_cmpdi2", "int", "longlong", "longlong"));
		m.put("ucmpdi2", new ArithContract("v850_gcc_ucmpdi2", "int", "ulonglong", "ulonglong"));
		// Overflow-checked libgcc variants (__addvDI3 & family, libgcc2.c
		// L_addvdi3/...): they return the wrapping 64-bit result but CALL
		// abort() on signed overflow. A call fixup would delete that
		// observable control flow, so these get an accurately typed and
		// named contract with NO p-code fixup: the call stays intact.
		m.put("addvdi3", new ArithContract(null, "longlong", "longlong", "longlong"));
		m.put("subvdi3", new ArithContract(null, "longlong", "longlong", "longlong"));
		m.put("mulvdi3", new ArithContract(null, "longlong", "longlong", "longlong"));
		m.put("negvdi2", new ArithContract(null, "longlong", "longlong"));
		return m;
	}

	/**
	 * All call-fixup payload names required by ARITH_CONTRACTS; used to check
	 * availability and drive the runtime fragment installation.
	 */
	private static Set<String> requiredFixupNames() {
		Set<String> names = new TreeSet<>();
		for (ArithContract c : ARITH_CONTRACTS.values()) {
			if (c.fixupName != null) {
				names.add(c.fixupName);
			}
		}
		return names;
	}

	private static boolean payloadAvailable(Program program, String fixupName) {
		try {
			return program.getCompilerSpec()
					.getPcodeInjectLibrary()
					.getPayload(InjectPayload.CALLFIXUP_TYPE, fixupName) != null;
		}
		catch (Exception e) {
		}
		return false;
	}

	/**
	 * Installs or updates the module-owned arithmetic call-fixup payloads.
	 * Compiler-spec extensions persist in programs, so merely checking that
	 * a name exists would leave an old semantic payload installed forever.
	 * The shared fragment is authoritative; identical extensions are kept.
	 *
	 * @return true when every required payload is available afterwards
	 */
	boolean ensureCallFixups(Program program, TaskMonitor monitor, MessageLog log) {
		Map<String, String> documents =
			loadFragmentDocuments(program, requiredFixupNames(), log);
		for (Map.Entry<String, String> entry : documents.entrySet()) {
			Options options = program.getOptions(SpecExtension.SPEC_EXTENSION);
			String optionName = "callfixup_" + entry.getKey();
			if (entry.getValue().equals(options.getString(optionName, null))) {
				continue; // identical extension already installed
			}
			try {
				new SpecExtension(program).addReplaceCompilerSpecExtension(entry.getValue(),
					monitor);
			}
			catch (Exception e) {
				Msg.error(this, "V850 helper: failed to install call fixup " + entry.getKey() +
					" (" + e.getMessage() + ")");
				log.appendMsg("V850 helper: call fixup install failed for " + entry.getKey());
			}
		}
		Set<String> still = new TreeSet<>();
		for (String name : requiredFixupNames()) {
			if (!payloadAvailable(program, name)) {
				still.add(name);
			}
		}
		if (!still.isEmpty()) {
			Msg.error(this, "V850 helper: GHS arithmetic call fixups unavailable: " + still +
				"; module fragment " + FRAGMENT_PATH + " could not be loaded");
		}
		return still.isEmpty();
	}

	/**
	 * Parses the module fragment and returns the raw <callfixup> documents for
	 * the requested fixup names (name -> element source).
	 */
	private Map<String, String> loadFragmentDocuments(Program program, Set<String> wanted,
			MessageLog log) {
		Map<String, String> docs = new HashMap<>();
		ResourceFile file = null;
		try {
			file = Application.getModuleDataFile(FRAGMENT_PATH);
		}
		catch (IOException e) {
			// handled below
		}
		if (file == null || !file.exists()) {
			Msg.error(this, "V850 helper: module data file not found: " + FRAGMENT_PATH);
			return docs;
		}
		try {
			DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
			Document doc = factory.newDocumentBuilder().parse(file.getInputStream());
			NodeList fixups = doc.getElementsByTagName("callfixup");
			for (int i = 0; i < fixups.getLength(); i++) {
				Element el = (Element) fixups.item(i);
				String name = el.getAttribute("name");
				if (!wanted.contains(name)) {
					continue;
				}
				appendAbiClobbers(program, el);
				docs.put(name, elementToString(el));
			}
		}
		catch (Exception e) {
			Msg.error(this,
				"V850 helper: failed to parse " + FRAGMENT_PATH + ": " + e.getMessage());
		}
		return docs;
	}

	/** Serializes a DOM element (and children) back to XML text. */
	private static String elementToString(Element el) throws Exception {
		TransformerFactory factory = TransformerFactory.newInstance();
		Transformer transformer = factory.newTransformer();
		transformer.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION, "yes");
		StringWriter writer = new StringWriter();
		transformer.transform(new DOMSource(el), new StreamResult(writer));
		return writer.toString();
	}

	/**
	 * A native callfixup destroys CALL and its call specification. Keep the
	 * selected compiler model's killed-register effects after computing the
	 * mathematical return value; never infer that argument/scratch registers
	 * survive merely because the value-lowering payload does not write them.
	 * Distinct CALLOTHER results are deliberately unconstrained. An unwritten
	 * unique temporary is not suitable: native heritage treats it as one
	 * function input and falsely correlates separate calls. Every discriminator
	 * constant is explicitly size-typed (:4) because the snippet parser never
	 * infers a size for CALLOTHER inputs, and every __v850_abi_clobber call
	 * keeps its own register as the sized destination so the opaque effect
	 * stays an independent call result.
	 */
	private static void appendAbiClobbers(Program program, Element fixup) {
		boolean wideResult = false;
		String name = fixup.getAttribute("name");
		for (ArithContract contract : ARITH_CONTRACTS.values()) {
			if (name.equals(contract.fixupName) &&
				(contract.returnType.equals("longlong") ||
					contract.returnType.equals("ulonglong"))) {
				wideResult = true;
				break;
			}
		}
		Element body = (Element) fixup.getElementsByTagName("body").item(0);
		StringBuilder text = new StringBuilder(body.getTextContent());
		for (var killed : program.getCompilerSpec().getDefaultCallingConvention()
				.getKilledByCallList()) {
			Register register = program.getLanguage().getRegister(killed.getAddress(),
				killed.getSize());
			if (register == null) {
				throw new IllegalStateException("V850 helper: unnamed ABI-killed storage " + killed);
			}
			String reg = register.getName();
			if (reg.equals("r0") || reg.equals("r10") || (wideResult && reg.equals("r11"))) {
				continue;
			}
			text.append('\n').append(reg).append(" = __v850_abi_clobber(")
					.append(killed.getOffset() / 4).append(":4);");
		}
		// Ordinary arithmetic runtime helpers do not change CPU operating
		// mode. Their five condition flags are unspecified, matching the
		// recovered IDA helper-lowering spoil set.
		text.append("\nPSW = (PSW & 0xffffffe0) | (__v850_abi_clobber(32:4) & 0x1f);\n");
		body.setTextContent(text.toString());
	}

	/** General purpose register names in architectural order. */
	private static final String[] GPRS = { "r0", "r1", "r2", "sp", "gp", "tp", "r6", "r7", "r8",
		"r9", "r10", "r11", "r12", "r13", "r14", "r15", "r16", "r17", "r18", "r19", "r20", "r21",
		"r22", "r23", "r24", "r25", "r26", "r27", "r28", "r29", "ep", "lp" };


	private static String gpr(int n) {
		return GPRS[n & 0x1f];
	}

	private static int gprNumber(String name) {
		for (int i = 0; i < GPRS.length; i++) {
			if (GPRS[i].equals(name)) {
				return i;
			}
		}
		return -1;
	}

	public V850CompilerHelperAnalyzer() {
		super(NAME, DESCRIPTION, AnalyzerType.FUNCTION_ANALYZER);
		setDefaultEnablement(true);
		setPriority(AnalysisPriority.FUNCTION_ANALYSIS);
	}

	@Override
	public boolean canAnalyze(Program program) {
		return PROCESSOR.equals(program.getLanguage().getProcessor().toString());
	}

	@Override
	public boolean added(Program program, AddressSetView set, TaskMonitor monitor, MessageLog log)
			throws CancelledException {
		Listing listing = program.getListing();
		Map<Address, HelperInfo> found = new HashMap<>();

		// Pass 1: instruction-exact recognition of stripped helper bodies.
		List<Address> sites = new ArrayList<>();
		InstructionIterator it = listing.getInstructions(set, true);
		while (it.hasNext()) {
			monitor.checkCancelled();
			Instruction ins = it.next();
			sites.add(ins.getMinAddress());
		}
		for (Address a : sites) {
			monitor.checkCancelled();
			Function existing = listing.getFunctionAt(a);
			if (existing != null && existing.isInline()) {
				continue;
			}
			if (!isIndependentEntry(program, a)) {
				continue;
			}
			HelperInfo info = matchAt(program, a);
			if (info != null) {
				markHelper(program, info, monitor, log);
				found.put(info.entry, info);
			}
		}

		// Pass 2: contract-established names (GCC/GHS save/restore names and
		// the GHS 64-bit arithmetic runtime contracts).
		Iterator<Function> funcs = listing.getFunctions(set, true);
		while (funcs.hasNext()) {
			monitor.checkCancelled();
			Function f = funcs.next();
			applyNamedContract(program, f, found, monitor, log);
		}

		// Pass 3: GHS CALLT tables and callt call sites.
		processCalltSites(program, set, found, monitor, log);

		// Pass 4: GHS dynamic-locals halfwords at confirmed helper calls.
		applyLocalsWords(program, found, monitor, log);

		return true;
	}

	/**
	 * Epilogue bytes alone, whether in a function or orphaned by incomplete
	 * analysis, do not establish an out-of-line helper. False splits can
	 * make no-return analysis truncate real callers. Known entries, calls
	 * and direct unconditional tail jumps from other functions are evidence.
	 */
	private static boolean isIndependentEntry(Program program, Address entry) {
		Listing listing = program.getListing();
		if (listing.getFunctionAt(entry) != null) return true;
		Function owner = listing.getFunctionContaining(entry);
		ReferenceIterator refs = program.getReferenceManager().getReferencesTo(entry);
		while (refs.hasNext()) {
			Reference ref = refs.next();
			if (ref.getReferenceType().isCall()) return true;
			RefType type = ref.getReferenceType();
			if (type.isJump() && !type.isConditional() && !type.isComputed()) {
				Function source = listing.getFunctionContaining(ref.getFromAddress());
				if (source != null && (owner == null ||
					!source.getEntryPoint().equals(owner.getEntryPoint()))) return true;
			}
		}
		return false;
	}

	// -------------------------------------------------------------------------
	// Instruction-exact body matchers (ports of the public nec850 behavior).
	// -------------------------------------------------------------------------

	private HelperInfo matchAt(Program program, Address a) {
		Instruction i0 = program.getListing().getInstructionAt(a);
		if (i0 == null) {
			return null;
		}
		String mnem = i0.getMnemonicString();
		switch (mnem) {
			case "add":
			case "addi":
				return matchGccSave(program, a);
			case "ld.w":
				return matchGccReturn(program, a);
			case "mov": {
				Object[] op0 = i0.getOpObjects(0);
				if (firstRegister(op0) != null) {
					return matchGhsSave(program, a);
				}
				if (firstScalar(op0) != null) {
					return matchGhsLoad(program, a);
				}
				return null;
			}
			case "prepare":
				return matchGhsCalltSave(program, a);
			case "stsr":
			case "dispose":
				return matchGhsCalltLoad(program, a);
			default:
				return null;
		}
	}

	/**
	 * GCC save helper: add -N,sp ; st.w r29..[sp] ; jmp [r10].
	 * Slot i holds register (i==10 ? r2 : 29-i) at offset i*4; the final slot
	 * may be LP for the *_r31 forms.
	 */
	private HelperInfo matchGccSave(Program program, Address a) {
		Instruction i0 = program.getListing().getInstructionAt(a);
		Long imm = addImmToSp(i0);
		if (imm == null || (imm & 3) != 0 || imm < -0x30 || imm > -4) {
			return null;
		}
		int nregs = (int) (-imm / 4);
		int reghi = nregs == 12 ? 31 : 29;
		Address ea = a.add(i0.getLength());
		List<String> regs = new ArrayList<>();
		for (int i = 0; i < nregs; i++, ea = ea.add(4)) {
			int want = i == 10 ? 2 : 29 - i;
			boolean ok = false;
			if (i != 11 && isStwSp(program, ea, want, i * 4)) {
				regs.add(gpr(want));
				ok = true;
			}
			if (!ok) {
				// The last register in *_r31 functions is LP.
				if (i == nregs - 1 && isStwSp(program, ea, 31, i * 4)) {
					reghi = 31;
					regs.add("lp");
				}
				else {
					return null;
				}
			}
		}
		if (!isJmpReg(program, ea, "r10")) {
			return null;
		}
		HelperInfo info = new HelperInfo(a, gccName("save", nregs, reghi), HelperKind.GCC_SAVE);
		info.savedRegs = regs;
		return info;
	}

	/**
	 * GCC return helper: ld.w 0[sp],r29|lp ; ... ; add N,sp ; jmp [lp].
	 * Reached through `jarl ...,lp` or as a `jr` tail call.
	 */
	private HelperInfo matchGccReturn(Program program, Address a) {
		Instruction i0 = program.getListing().getInstructionAt(a);
		int reghi;
		if (isLdwSp(program, a, 29, 0)) {
			reghi = 29;
		}
		else if (isLdwSp(program, a, 31, 0)) {
			reghi = 31;
		}
		else {
			return null;
		}
		List<String> regs = new ArrayList<>();
		regs.add(gpr(reghi));
		Address ea = a.add(i0.getLength());
		int nregs = 1;
		while (reghi != 31 && nregs <= 12) {
			int want = nregs == 10 ? 2 : 29 - nregs;
			if (nregs != 11 && isLdwSp(program, ea, want, nregs * 4)) {
				regs.add(gpr(want));
			}
			else if (isLdwSp(program, ea, 31, nregs * 4)) {
				reghi = 31;
				regs.add("lp");
				nregs++;
				ea = ea.add(4);
				break;
			}
			else {
				break;
			}
			nregs++;
			ea = ea.add(4);
		}
		Instruction add = program.getListing().getInstructionAt(ea);
		Long imm = addImmToSp(add);
		if (imm == null || imm != (long) nregs * 4) {
			return null;
		}
		ea = ea.add(add.getLength());
		if (!isJmpReg(program, ea, "lp")) {
			return null;
		}
		HelperInfo info = new HelperInfo(a, gccName("return", nregs, reghi), HelperKind.GCC_RETURN);
		info.savedRegs = regs;
		return info;
	}


	/**
	 * GHS save helper:
	 *   mov sp,r12 ; add -N,sp ; [br] ; st.w {r29..rN},(split-r)*4[sp] ;
	 *   [add -16|-12,sp ; jr] ; mov r10,r29 ; st.w lp,-4[r12] ;
	 *   [ld.h -6[r10],r12 ; andi 0xffff,r12,r12 ; shl 2,r12 ; sub r12,sp] ;
	 *   jmp [r10]
	 */
	private HelperInfo matchGhsSave(Program program, Address a) {
		Instruction i0 = program.getListing().getInstructionAt(a);
		if (!isMovRegReg(i0, "sp", "r12")) {
			return null;
		}
		Address ea = a.add(i0.getLength());
		Instruction i1 = program.getListing().getInstructionAt(ea);
		Long imm = addImmToSp(i1);
		if (imm == null || (imm & 3) != 0 || imm < -0x14 || imm > -4) {
			return null;
		}
		int nregs = (int) (-imm / 4);
		ea = ea.add(i1.getLength());
		// Optional branch to the register save part.
		Address follow = branchTarget(program, ea);
		if (follow != null) {
			ea = follow;
		}

		int reglo = firstStwDataReg(program, ea);
		if (reglo < 0 || reglo < 20 || reglo == 30) {
			return null;
		}
		int[] splits = { 22, 26, 29 };
		if (reglo == 31) {
			if (nregs != 1) {
				return null;
			}
		}
		else {
			for (int split : splits) {
				if (reglo <= split) {
					if (nregs + reglo - split != 2) {
						return null;
					}
					break;
				}
			}
		}
		List<String> regs = new ArrayList<>();
		int reg = reglo;
		for (int split : splits) {
			if (reg > split) {
				continue;
			}
			for (; reg <= split; reg++) {
				long off = (split - reg) * 4;
				if (!isStwSp(program, ea, reg, off)) {
					return null;
				}
				regs.add(gpr(reg));
				ea = ea.add(4);
			}
			if (split == 29) {
				break;
			}
			Instruction add = program.getListing().getInstructionAt(ea);
			Long adj = addImmToSp(add);
			if (adj == null || adj != (split == 22 ? -16 : -12)) {
				return null;
			}
			ea = ea.add(add.getLength());
			Address jr = jumpTarget(program, ea);
			if (jr == null) {
				return null;
			}
			ea = jr;
		}
		if (reglo != 31) {
			Instruction mov = program.getListing().getInstructionAt(ea);
			if (!isMovRegReg(mov, "r10", "r29")) {
				return null;
			}
			ea = ea.add(mov.getLength());
		}
		if (!isStwBase(program, ea, "lp", "r12", -4)) {
			return null;
		}
		ea = ea.add(4);
		int alloc = matchGhsAllocCode(program, ea);
		ea = ea.add(alloc);
		if (!isJmpReg(program, ea, "r10")) {
			return null;
		}
		String suffix = alloc > 0 ? "" : "a";
		HelperInfo info = new HelperInfo(a,
			reglo == 31 ? "__ghssavelp" + suffix : "__ghssave" + reglo + suffix, HelperKind.GHS_SAVE);
		info.savedRegs = regs;
		info.locals = alloc > 0;
		return info;
	}

	/**
	 * GHS load helper:
	 *   mov n,r12 ; [br] ; ld.w (29-r)*4[sp],{r29..rN} ; [jr] ;
	 *   shl 2,r12 ; add r12,sp ; ld.w 4[sp],lp ; add 8,sp ; jmp [lp]
	 */
	private HelperInfo matchGhsLoad(Program program, Address a) {
		Instruction i0 = program.getListing().getInstructionAt(a);
		Scalar imm = firstScalar(i0.getOpObjects(0));
		Register dst = firstRegister(i0.getOpObjects(1));
		if (imm == null || dst == null || !dst.getName().equals("r12")) {
			return null;
		}
		long nregs = imm.getValue();
		if (nregs > 9) {
			return null;
		}
		Address ea = a.add(i0.getLength());
		Address follow = branchTarget(program, ea);
		if (follow != null) {
			ea = follow;
		}
		int reglo = 29 - (int) nregs;
		int[] splits = { 22, 26, 29 };
		List<String> regs = new ArrayList<>();
		int reg = reglo;
		for (int split : splits) {
			if (reg > split) {
				continue;
			}
			for (; reg <= split; reg++) {
				long off = (29 - reg) * 4;
				if (!isLdwSp(program, ea, reg, off)) {
					return null;
				}
				regs.add(gpr(reg));
				ea = ea.add(4);
			}
			if (split == 29) {
				break;
			}
			Address jr = jumpTarget(program, ea);
			if (jr == null) {
				return null;
			}
			ea = jr;
		}
		Instruction shl = program.getListing().getInstructionAt(ea);
		if (!isShiftImm(shl, "shl", 2, "r12")) {
			return null;
		}
		ea = ea.add(shl.getLength());
		Instruction addSp = program.getListing().getInstructionAt(ea);
		if (!isOpRegReg(addSp, "add", "r12", "sp")) {
			return null;
		}
		ea = ea.add(addSp.getLength());
		if (!isLdwSp(program, ea, 31, 4)) {
			return null;
		}
		ea = ea.add(4);
		Instruction add = program.getListing().getInstructionAt(ea);
		Long adj = addImmToSp(add);
		if (adj == null || adj != 8) {
			return null;
		}
		ea = ea.add(add.getLength());
		if (!isJmpReg(program, ea, "lp")) {
			return null;
		}
		HelperInfo info = new HelperInfo(a, "__ghsload" + reglo, HelperKind.GHS_LOAD);
		info.savedRegs = regs;
		return info;
	}

	/**
	 * GHS CALLT save helpers:
	 *   prepare {lp},0 ; [prepare {rN-r29},0] ; [br|jr] ; [stsr ctpc,r29] ;
	 *   ctret                                   (___ghssv4*)
	 *   stsr ctpc,r10 ; ld.hu -4[r10],r11 ; sub r11,sp ; jmp [r10]  (___ghssv5*)
	 */
	private HelperInfo matchGhsCalltSave(Program program, Address a) {
		Instruction i0 = program.getListing().getInstructionAt(a);
		if (!isPrepareList(i0, "lp", 0)) {
			return null;
		}
		Address ea = a.add(i0.getLength());
		int reglo = -1;
		Instruction ins = program.getListing().getInstructionAt(ea);
		Integer listLo = prepareRange(program, ea);
		if (listLo != null) {
			reglo = listLo;
			ea = ea.add(ins.getLength());
			ins = program.getListing().getInstructionAt(ea);
		}
		Address follow = branchTarget(program, ea);
		if (follow != null) {
			ea = follow;
			ins = program.getListing().getInstructionAt(ea);
		}
		follow = jumpTarget(program, ea);
		if (follow != null) {
			ea = follow;
			ins = program.getListing().getInstructionAt(ea);
		}
		if (reglo != -1) {
			if (!isStsr(ins, "CTPC", "r29")) {
				return null;
			}
			ea = ea.add(ins.getLength());
			ins = program.getListing().getInstructionAt(ea);
		}
		char flag;
		if (ins != null && "ctret".equals(ins.getMnemonicString())) {
			flag = '4';
			ea = ea.add(ins.getLength());
		}
		else {
			follow = branchTarget(program, ea);
			if (follow != null) {
				ea = follow;
				ins = program.getListing().getInstructionAt(ea);
			}
			if (!isStsr(ins, "CTPC", "r10")) {
				return null;
			}
			Address h = ea.add(ins.getLength());
			if (!isLdhuBase(program, h, "r11", "r10", -4)) {
				return null;
			}
			h = h.add(4);
			Instruction sub = program.getListing().getInstructionAt(h);
			if (!isOpRegReg(sub, "sub", "r11", "sp")) {
				return null;
			}
			h = h.add(sub.getLength());
			if (!isJmpReg(program, h, "r10")) {
				return null;
			}
			flag = '5';
		}
		String name = reglo == -1 ? "___ghssv" + flag + "lp" : "___ghssv" + flag + "r" + reglo;
		HelperInfo info = new HelperInfo(a, name, HelperKind.GHS_CALLT_SAVE);
		info.callt = true;
		info.locals = flag == '5';
		if (reglo != -1) {
			for (int r = reglo; r <= 29; r++) {
				info.savedRegs.add(gpr(r));
			}
		}
		info.savedRegs.add("lp");
		return info;
	}

	private static String gccName(String verb, int nregs, int reghi) {
		if (nregs == 1) {
			// A single saved LP matches GHS's own ghssavelpa/ghsloadlp shape.
			if (reghi == 31) {
				return verb.equals("save") ? "__ghssavelpa" : "__ghsloadlp";
			}
			return "__" + verb + "_r" + reghi;
		}
		int n = reghi == 31 ? nregs - 1 : nregs;
		int reglo = n == 11 ? 2 : 30 - n;
		return "__" + verb + "_r" + reglo + "_r" + reghi;
	}

	/**
	 * GHS CALLT return helpers:
	 *   [stsr ctpc,lp ; ld.hu 0[lp],r12|r29 ; add r12|r29,sp]  (release)
	 *   [dispose 0,{rN-r29}] ; [br] ; dispose 0,{lp},[lp]
	 */
	private HelperInfo matchGhsCalltLoad(Program program, Address a) {
		Address ea = a;
		int release = matchGhsReleaseCode(program, ea);
		ea = ea.add(release);
		Address follow = release > 0 ? branchTarget(program, ea) : null;
		if (follow != null) {
			ea = follow;
		}
		int reglo = -1;
		Integer disposeLo = disposeRange(program, ea);
		if (disposeLo != null) {
			reglo = disposeLo;
			Instruction d = program.getListing().getInstructionAt(ea);
			ea = ea.add(d.getLength());
			follow = branchTarget(program, ea);
			if (follow != null) {
				ea = follow;
			}
		}
		if (!isDisposeLpReturn(program, ea)) {
			return null;
		}
		char flag = release > 0 ? '4' : '2';
		String name = reglo == -1 ? "___ghsld" + flag + "lp" : "___ghsld" + flag + "r" + reglo;
		HelperInfo info = new HelperInfo(a, name, HelperKind.GHS_CALLT_LOAD);
		info.callt = true;
		info.locals = release > 0;
		if (reglo != -1) {
			for (int r = reglo; r <= 29; r++) {
				info.savedRegs.add(gpr(r));
			}
		}
		info.savedRegs.add("lp");
		return info;
	}

	/** ld.h -6[r10],rX ; andi 0xffff,rX,rX ; shl 2,rX ; sub rX,sp */
	private int matchGhsAllocCode(Program program, Address ea) {
		for (String tmp : new String[] { "r12", "r11" }) {
			Address h = ea;
			if (!isLdhBase(program, h, tmp, "r10", -6)) {
				continue;
			}
			h = h.add(4);
			Instruction and = program.getListing().getInstructionAt(h);
			if (!isAndiR(and, 0xffff, tmp)) {
				continue;
			}
			h = h.add(and.getLength());
			Instruction shl = program.getListing().getInstructionAt(h);
			if (!isShiftImm(shl, "shl", 2, tmp)) {
				continue;
			}
			h = h.add(shl.getLength());
			Instruction sub = program.getListing().getInstructionAt(h);
			if (!isOpRegReg(sub, "sub", tmp, "sp")) {
				continue;
			}
			return 4 + 4 + 2 + 2;
		}
		return 0;
	}

	/** stsr ctpc,lp ; ld.hu 0[lp],r12|r29 ; add r12|r29,sp */
	private int matchGhsReleaseCode(Program program, Address ea) {
		Instruction stsr = program.getListing().getInstructionAt(ea);
		if (!isStsr(stsr, "CTPC", "lp")) {
			return 0;
		}
		for (String tmp : new String[] { "r12", "r29" }) {
			Address h = ea.add(4);
			if (!isLdhuBase(program, h, tmp, "lp", 0)) {
				continue;
			}
			h = h.add(4);
			Instruction add = program.getListing().getInstructionAt(h);
			if (!isOpRegReg(add, "add", tmp, "sp")) {
				continue;
			}
			return 4 + 4 + 2;
		}
		return 0;
	}

	// -------------------------------------------------------------------------
	// Instruction predicates. Memory displacements are decoded from the raw
	// instruction words (V850 format VII encodings) so recognition is exact
	// regardless of operand-presentation details.
	// -------------------------------------------------------------------------

	private static Register firstRegister(Object[] objects) {
		if (objects == null) {
			return null;
		}
		for (Object o : objects) {
			if (o instanceof Register) {
				return (Register) o;
			}
		}
		return null;
	}

	private static Scalar firstScalar(Object[] objects) {
		if (objects == null) {
			return null;
		}
		for (Object o : objects) {
			if (o instanceof Scalar) {
				return (Scalar) o;
			}
		}
		return null;
	}

	/** Decoded format VII load/store: data reg, base reg, displacement. */
	private static class MemOp {
		int dataReg;
		int baseReg;
		long disp;
	}

	/**
	 * Decodes the 32-bit format VII load/store at ea from raw bytes.
	 *
	 * @param opcode 0x39 ld.w/ld.h, 0x3B st.w/st.h, 0x3F ld.hu (extension bit)
	 * @param requireExt true for the scaled disp16 form (word/halfword-extend)
	 */
	private MemOp memOp(Program program, Address ea, int opcode, boolean requireExt) {
		Instruction ins = program.getListing().getInstructionAt(ea);
		if (ins == null || ins.getLength() != 4) {
			return null;
		}
		byte[] b = new byte[4];
		try {
			int n = program.getMemory().getBytes(ea, b);
			if (n != 4) {
				return null;
			}
		}
		catch (Exception e) {
			return null;
		}
		int w1 = (b[0] & 0xff) | ((b[1] & 0xff) << 8);
		int w2 = (b[2] & 0xff) | ((b[3] & 0xff) << 8);
		if (((w1 >> 5) & 0x3f) != opcode) {
			return null;
		}
		if (((w2 & 1) != 0) != requireExt) {
			return null;
		}
		MemOp m = new MemOp();
		m.dataReg = (w1 >> 11) & 0x1f;
		m.baseReg = w1 & 0x1f;
		if (requireExt) {
			// disp16 = sext15(bits 17..31) * 2
			long s = (w2 >> 1) & 0x7fff;
			if ((s & 0x4000) != 0) {
				s -= 0x8000;
			}
			m.disp = s * 2;
		}
		else {
			// disp16 = sext16(second word), unscaled (ld.h form)
			long s = w2 & 0xffff;
			if ((s & 0x8000) != 0) {
				s -= 0x10000;
			}
			m.disp = s;
		}
		return m;
	}

	private boolean isStwSp(Program program, Address ea, int reg, long off) {
		if (!hasMnem(program, ea, "st.w")) {
			return false;
		}
		MemOp m = memOp(program, ea, 0x3B, true);
		return m != null && m.dataReg == reg && m.baseReg == 3 && m.disp == off;
	}

	private boolean isStwBase(Program program, Address ea, String reg, String base, long off) {
		if (!hasMnem(program, ea, "st.w")) {
			return false;
		}
		MemOp m = memOp(program, ea, 0x3B, true);
		return m != null && gpr(m.dataReg).equals(reg) && gpr(m.baseReg).equals(base) &&
			m.disp == off;
	}

	/** Data register of the first st.w at ea (base-agnostic), or -1. */
	private int firstStwDataReg(Program program, Address ea) {
		if (!hasMnem(program, ea, "st.w")) {
			return -1;
		}
		MemOp m = memOp(program, ea, 0x3B, true);
		return m == null ? -1 : m.dataReg;
	}

	private boolean isLdwSp(Program program, Address ea, int reg, long off) {
		if (!hasMnem(program, ea, "ld.w")) {
			return false;
		}
		MemOp m = memOp(program, ea, 0x39, true);
		return m != null && m.dataReg == reg && m.baseReg == 3 && m.disp == off;
	}

	private boolean isLdhBase(Program program, Address ea, String reg, String base, long off) {
		if (!hasMnem(program, ea, "ld.h")) {
			return false;
		}
		MemOp m = memOp(program, ea, 0x39, false);
		return m != null && gpr(m.dataReg).equals(reg) && gpr(m.baseReg).equals(base) &&
			m.disp == off;
	}

	private boolean isLdhuBase(Program program, Address ea, String reg, String base, long off) {
		if (!hasMnem(program, ea, "ld.hu")) {
			return false;
		}
		MemOp m = memOp(program, ea, 0x3F, true);
		return m != null && gpr(m.dataReg).equals(reg) && gpr(m.baseReg).equals(base) &&
			m.disp == off;
	}

	private static boolean hasMnem(Program program, Address ea, String mnem) {
		Instruction ins = program.getListing().getInstructionAt(ea);
		return ins != null && mnem.equals(ins.getMnemonicString());
	}

	private boolean isJmpReg(Program program, Address ea, String reg) {
		Instruction ins = program.getListing().getInstructionAt(ea);
		if (ins == null || !"jmp".equals(ins.getMnemonicString()) || ins.getNumOperands() != 1) {
			return false;
		}
		Register target = firstRegister(ins.getOpObjects(0));
		return target != null && reg.equals(target.getName());
	}

	private static boolean isMovRegReg(Instruction ins, String src, String dst) {
		if (ins == null || !"mov".equals(ins.getMnemonicString()) || ins.getNumOperands() != 2) {
			return false;
		}
		Register s = firstRegister(ins.getOpObjects(0));
		Register d = firstRegister(ins.getOpObjects(1));
		return s != null && d != null && src.equals(s.getName()) && dst.equals(d.getName());
	}

	private static boolean isOpRegReg(Instruction ins, String mnem, String src, String dst) {
		if (ins == null || !mnem.equals(ins.getMnemonicString()) || ins.getNumOperands() != 2) {
			return false;
		}
		Register s = firstRegister(ins.getOpObjects(0));
		Register d = firstRegister(ins.getOpObjects(1));
		return s != null && d != null && src.equals(s.getName()) && dst.equals(d.getName());
	}

	private static boolean isShiftImm(Instruction ins, String mnem, long imm, String dst) {
		if (ins == null || !mnem.equals(ins.getMnemonicString()) || ins.getNumOperands() != 2) {
			return false;
		}
		Scalar s = firstScalar(ins.getOpObjects(0));
		Register d = firstRegister(ins.getOpObjects(1));
		return s != null && d != null && s.getSignedValue() == imm && dst.equals(d.getName());
	}

	private static boolean isAndiR(Instruction ins, long imm, String reg) {
		if (ins == null || !"andi".equals(ins.getMnemonicString()) || ins.getNumOperands() != 3) {
			return false;
		}
		Scalar s = firstScalar(ins.getOpObjects(0));
		Register r1 = firstRegister(ins.getOpObjects(1));
		Register r2 = firstRegister(ins.getOpObjects(2));
		return s != null && r1 != null && r2 != null && (s.getValue() & 0xffffL) == imm &&
			reg.equals(r1.getName()) && reg.equals(r2.getName());
	}

	private static boolean isStsr(Instruction ins, String sr, String dst) {
		if (ins == null || !"stsr".equals(ins.getMnemonicString()) || ins.getNumOperands() != 2) {
			return false;
		}
		Register s = firstRegister(ins.getOpObjects(0));
		Register d = firstRegister(ins.getOpObjects(1));
		return s != null && d != null && sr.equals(s.getName()) && dst.equals(d.getName());
	}

	/** add imm,sp (imm5 form) or addi imm,sp,sp. */
	private static Long addImmToSp(Instruction ins) {
		if (ins == null) {
			return null;
		}
		String mnem = ins.getMnemonicString();
		if ("add".equals(mnem) && ins.getNumOperands() == 2) {
			Scalar s = firstScalar(ins.getOpObjects(0));
			Register r = firstRegister(ins.getOpObjects(1));
			if (s != null && r != null && "sp".equals(r.getName())) {
				return s.getSignedValue();
			}
		}
		else if ("addi".equals(mnem) && ins.getNumOperands() == 3) {
			Scalar s = firstScalar(ins.getOpObjects(0));
			Register r1 = firstRegister(ins.getOpObjects(1));
			Register r2 = firstRegister(ins.getOpObjects(2));
			if (s != null && r1 != null && r2 != null && "sp".equals(r1.getName()) &&
				"sp".equals(r2.getName())) {
				return s.getSignedValue();
			}
		}
		return null;
	}

	/** prepare {regs},imm with an exact single-register list. */
	private static boolean isPrepareList(Instruction ins, String reg, long imm) {
		if (ins == null || !"prepare".equals(ins.getMnemonicString()) || ins.getNumOperands() != 2) {
			return false;
		}
		String[] list = regListNames(ins, 0);
		Scalar s = firstScalar(ins.getOpObjects(1));
		return list != null && list.length == 1 && reg.equals(list[0]) && s != null &&
			s.getSignedValue() == imm;
	}

	/** prepare {rN-r29},imm: returns N, or null when the list is not that range. */
	private static Integer prepareRange(Program program, Address ea) {
		Instruction ins = program.getListing().getInstructionAt(ea);
		if (ins == null || !"prepare".equals(ins.getMnemonicString()) || ins.getNumOperands() != 2) {
			return null;
		}
		Scalar s = firstScalar(ins.getOpObjects(1));
		if (s == null || s.getSignedValue() != 0) {
			return null;
		}
		return contiguousListRange(regListNames(ins, 0));
	}

	private static Integer disposeRange(Program program, Address ea) {
		Instruction ins = program.getListing().getInstructionAt(ea);
		if (ins == null || !"dispose".equals(ins.getMnemonicString()) || ins.getNumOperands() != 2) {
			return null;
		}
		Scalar s = firstScalar(ins.getOpObjects(0));
		if (s == null || s.getSignedValue() != 0) {
			return null;
		}
		return contiguousListRange(regListNames(ins, 1));
	}

	/** dispose 0,{lp},[lp] */
	private static boolean isDisposeLpReturn(Program program, Address ea) {
		Instruction ins = program.getListing().getInstructionAt(ea);
		if (ins == null || !"dispose".equals(ins.getMnemonicString()) || ins.getNumOperands() != 3) {
			return false;
		}
		Scalar s = firstScalar(ins.getOpObjects(0));
		String[] list = regListNames(ins, 1);
		Register via = firstRegister(ins.getOpObjects(2));
		return s != null && s.getSignedValue() == 0 && list != null && list.length == 1 &&
			"lp".equals(list[0]) && via != null && "lp".equals(via.getName());
	}

	/**
	 * Names of the registers of a register-list operand (PREPARE/DISPOSE
	 * list12), in operand order. SleighInstructionPrototype.getOpObjects
	 * returns the list's registers as flat individual Register elements
	 * (addHandleObject appends one object per register), not a nested
	 * Register[]; both shapes are accepted.
	 */
	private static String[] regListNames(Instruction ins, int opIndex) {
		Object[] objects = ins.getOpObjects(opIndex);
		if (objects == null || objects.length == 0) {
			return null;
		}
		List<String> names = new ArrayList<>();
		for (Object o : objects) {
			if (o instanceof Register) {
				names.add(((Register) o).getName());
			}
			else if (o instanceof Register[]) {
				for (Register r : (Register[]) o) {
					names.add(r.getName());
				}
			}
		}
		return names.isEmpty() ? null : names.toArray(new String[0]);
	}

	/** Exact contiguous rN..r29 set (N in 20..29), order-agnostic. */
	private static Integer contiguousListRange(String[] names) {
		if (names == null || names.length == 0) {
			return null;
		}
		Set<Integer> numbers = new HashSet<>();
		for (String n : names) {
			int num = gprNumber(n);
			if (num < 20 || num > 29 || !numbers.add(num)) {
				return null;
			}
		}
		int lo = 29 - numbers.size() + 1;
		for (int r = lo; r <= 29; r++) {
			if (!numbers.contains(r)) {
				return null;
			}
		}
		return lo;
	}

	/** Target of an unconditional `br` at ea, or null. */
	private static Address branchTarget(Program program, Address ea) {
		Instruction ins = program.getListing().getInstructionAt(ea);
		if (ins == null || !"br".equals(ins.getMnemonicString())) {
			return null;
		}
		Address[] flows = ins.getFlows();
		return flows.length == 1 ? flows[0] : null;
	}

	/** Target of an unconditional `jr` at ea, or null. */
	private static Address jumpTarget(Program program, Address ea) {
		Instruction ins = program.getListing().getInstructionAt(ea);
		if (ins == null || !"jr".equals(ins.getMnemonicString())) {
			return null;
		}
		Address[] flows = ins.getFlows();
		return flows.length == 1 ? flows[0] : null;
	}

	// -------------------------------------------------------------------------
	// Helper marking and effects.
	// -------------------------------------------------------------------------

	private void markHelper(Program program, HelperInfo info, TaskMonitor monitor, MessageLog log) {
		Listing listing = program.getListing();
		Function function = listing.getFunctionAt(info.entry);
		if (function == null) {
			CreateFunctionCmd cmd = new CreateFunctionCmd(info.entry);
			if (!cmd.applyTo(program, monitor)) {
				log.appendMsg("V850 helper: failed to create function at " + info.entry);
				return;
			}
			function = cmd.getFunction();
			if (function == null) {
				function = listing.getFunctionAt(info.entry);
			}
		}
		if (function == null) {
			return;
		}
		rename(program, info.entry, info.name, log);
		if (!function.isInline()) {
			// The helper body is the ground truth: inlining splices its real
			// store/stack/return p-code into every caller, including the GHS
			// dynamic locals allocation read through the link register.
			function.setInline(true);
		}
	}

	private void rename(Program program, Address entry, String name, MessageLog log) {
		Function function = program.getListing().getFunctionAt(entry);
		if (function == null) {
			return;
		}
		Symbol symbol = function.getSymbol();
		if (symbol.getSource() != SourceType.DEFAULT && name.equals(symbol.getName())) {
			return;
		}
		String candidate = name;
		boolean suffixed = false;
		while (true) {
			try {
				function.setName(candidate, SourceType.ANALYSIS);
				return;
			}
			catch (DuplicateNameException e) {
				if (suffixed) {
					return;
				}
				suffixed = true;
				candidate = name + "@" + entry;
			}
			catch (InvalidInputException e) {
				log.appendMsg("V850 helper: invalid name " + candidate);
				return;
			}
		}
	}

	// -------------------------------------------------------------------------
	// Contract-established names.
	// -------------------------------------------------------------------------

	private void applyNamedContract(Program program, Function f, Map<Address, HelperInfo> found,
			TaskMonitor monitor, MessageLog log) throws CancelledException {
		String name = f.getName();
		if (name == null) {
			return;
		}
		if (name.startsWith("FUN_") || name.startsWith("Default_")) {
			// Stripped symbol: recover arithmetic helpers by proving the
			// body against the pinned GCC reference corpus (shared
			// V850ArithmeticReferenceMatcher) or the exact linear GHS
			// idioms. Unproven bodies stay untouched.
			recoverStrippedArithmetic(program, f, monitor, log);
			return;
		}
		String normalized = name;
		if (normalized.startsWith("libID_conflict_")) {
			normalized = normalized.substring("libID_conflict_".length());
		}
		while (!normalized.isEmpty() && normalized.charAt(0) == '_') {
			normalized = normalized.substring(1);
		}
		if (normalized.isEmpty()) {
			return;
		}
		ArithContract contract = ARITH_CONTRACTS.get(normalized);
		if (contract != null) {
			applyArithContract(program, f, contract, monitor, log);
			return;
		}
		if (f.isInline()) {
			return;
		}
		HelperInfo info = recognizeHelperName(normalized);
		if (info != null) {
			info.entry = f.getEntryPoint();
			markHelper(program, info, monitor, log);
			found.put(info.entry, info);
		}
	}

	/** Name grammar for the save/restore helper families. */
	static HelperInfo recognizeHelperName(String name) {
		try {
			if (name.startsWith("save_") || name.startsWith("return_")) {
				boolean save = name.startsWith("save_");
				String rest = name.substring(save ? 5 : 7);
				HelperInfo info = new HelperInfo(null, name,
					save ? HelperKind.GCC_SAVE : HelperKind.GCC_RETURN);
				if (rest.equals("r2_r29")) {
					addRange(info, 2, 2);
					addRange(info, 20, 29);
				}
				else if (rest.equals("r2_r31")) {
					addRange(info, 2, 2);
					addRange(info, 20, 29);
					info.savedRegs.add("lp");
				}
				else if (rest.equals("r29")) {
					addRange(info, 29, 29);
				}
				else if (rest.equals("r31")) {
					info.savedRegs.add("lp");
				}
				else {
					int us = rest.indexOf('_');
					if (us <= 0 || !rest.startsWith("r")) {
						return null;
					}
					int lo = Integer.parseInt(rest.substring(1, us));
					if (!rest.substring(us + 1).startsWith("r")) {
						return null;
					}
					int hi = Integer.parseInt(rest.substring(us + 2));
					if (hi == 29) {
						if (lo < 20 || lo > 28) {
							return null;
						}
						addRange(info, lo, 29);
					}
					else if (hi == 31) {
						if (lo < 20 || lo > 29) {
							return null;
						}
						addRange(info, lo, 29);
						info.savedRegs.add("lp");
					}
					else {
						return null;
					}
				}
				return info;
			}
			if (name.startsWith("ghssave") || name.startsWith("ghsload")) {
				boolean save = name.startsWith("ghssave");
				String rest = name.substring(7);
				HelperInfo info = new HelperInfo(null, name,
					save ? HelperKind.GHS_SAVE : HelperKind.GHS_LOAD);
				int reglo;
				if (rest.startsWith("lp")) {
					reglo = 31;
					rest = rest.substring(2);
					if (!rest.isEmpty() && !rest.equals("a")) {
						return null;
					}
				}
				else {
					int digits = 0;
					while (digits < rest.length() && Character.isDigit(rest.charAt(digits))) {
						digits++;
					}
					if (digits == 0) {
						return null;
					}
					reglo = Integer.parseInt(rest.substring(0, digits));
					rest = rest.substring(digits);
					if (reglo < 20 || reglo > 29) {
						return null;
					}
					if (!rest.isEmpty() && !rest.equals("a")) {
						return null;
					}
					addRange(info, reglo, 29);
				}
				info.reglo = reglo == 31 ? -1 : reglo;
				info.locals = rest.isEmpty() && save;
				info.savedRegs.add("lp");
				return info;
			}
			if (name.startsWith("ghssv") || name.startsWith("ghsld")) {
				boolean save = name.startsWith("ghssv");
				String rest = name.substring(5);
				HelperInfo info = new HelperInfo(null, name,
					save ? HelperKind.GHS_CALLT_SAVE : HelperKind.GHS_CALLT_LOAD);
				info.callt = true;
				char flag = rest.charAt(0);
				boolean flagOk = save ? (flag == '4' || flag == '5') : (flag == '2' || flag == '4');
				if (!flagOk) {
					return null;
				}
				info.locals = save ? flag == '5' : flag == '4';
				rest = rest.substring(1);
				if (rest.equals("lp")) {
					info.savedRegs.add("lp");
				}
				else if (rest.startsWith("r")) {
					int reglo = Integer.parseInt(rest.substring(1));
					if (reglo < 20 || reglo > 29) {
						return null;
					}
					info.reglo = reglo;
					addRange(info, reglo, 29);
					info.savedRegs.add("lp");
				}
				else {
					return null;
				}
				return info;
			}
		}
		catch (NumberFormatException e) {
			return null;
		}
		return null;
	}

	private static void addRange(HelperInfo info, int lo, int hi) {
		for (int r = lo; r <= hi; r++) {
			info.savedRegs.add(gpr(r));
		}
		if (info.reglo < 0 && lo >= 20) {
			info.reglo = lo;
		}
	}

	private void applyArithContract(Program program, Function f, ArithContract contract,
			TaskMonitor monitor, MessageLog log) {
		// A value-lowering fixup removes the call. Never erase an
		// explicitly non-returning helper's control-flow contract.
		if (f.hasNoReturn()) {
			String existing = f.getCallFixup();
			if (existing != null && requiredFixupNames().contains(existing)) {
				f.setCallFixup(null);
			}
			return;
		}
		if (contract.fixupName == null) {
			// Trapping helpers (the *v family call abort() on overflow): the
			// conditional call is observable control flow a fixup would
			// delete, so the contract is name + signature only and the call
			// stays intact. Clear any fixup a previous analyzer version may
			// have installed before the cutover.
			String existing = f.getCallFixup();
			if (existing != null && (existing.equals("v850_gcc_addvdi3") ||
				existing.equals("v850_gcc_subvdi3") || existing.equals("v850_gcc_mulvdi3") ||
				existing.equals("v850_gcc_negvdi2"))) {
				f.setCallFixup(null);
			}
		}
		else {
			String existing = f.getCallFixup();
			if (existing == null ||
				(requiredFixupNames().contains(existing) && !existing.equals(contract.fixupName))) {
				if (!payloadAvailable(program, contract.fixupName)) {
					// Real error, never a silent label without effects:
					// install the missing payload from the shared fragment.
					ensureCallFixups(program, monitor, log);
				}
				if (payloadAvailable(program, contract.fixupName)) {
					f.setCallFixup(contract.fixupName);
				}
				else {
					// Never a label without effects: fail the analyzer
					// loudly so the missing payload is fixed instead of
					// silently skipped.
					throw new IllegalStateException("V850 helper: no p-code payload for " +
						contract.fixupName + "; GHS arithmetic contract for " + f.getName() +
						" at " + f.getEntryPoint() +
						" requires the module fragment " + FRAGMENT_PATH);
				}
			}
		}
		if (f.getSignatureSource() != SourceType.DEFAULT &&
			f.getSignatureSource() != SourceType.ANALYSIS) {
			return;
		}
		DataTypeManager dtm = program.getDataTypeManager();
		DataType ret = resolveType(dtm, contract.returnType);
		ParameterDefinitionImpl[] args = new ParameterDefinitionImpl[contract.argTypes.length];
		for (int i = 0; i < args.length; i++) {
			args[i] = new ParameterDefinitionImpl(i == 0 ? "a" : "b",
				resolveType(dtm, contract.argTypes[i]), null);
		}
		FunctionDefinitionDataType sig =
			new FunctionDefinitionDataType(CategoryPath.ROOT, f.getName());
		sig.setReturnType(ret);
		sig.setArguments(args);
		new ApplyFunctionSignatureCmd(f.getEntryPoint(), sig, SourceType.ANALYSIS)
				.applyTo(program, monitor);
	}

	private static DataType resolveType(DataTypeManager dtm, String name) {
		// Builtins are NOT reachable via dtm.getDataType(ROOT, ...) on a
		// fresh program (that only queries the program category); use the
		// builtin classes and resolve through the manager so undefined
		// imports never degrade the contract signatures.
		DataType t;
		switch (name) {
			case "int":
				t = IntegerDataType.dataType;
				break;
			case "uint":
				t = UnsignedIntegerDataType.dataType;
				break;
			case "longlong":
				t = LongLongDataType.dataType;
				break;
			case "ulonglong":
				t = UnsignedLongLongDataType.dataType;
				break;
			default:
				t = dtm.getDataType(CategoryPath.ROOT, name);
				break;
		}
		if (t != null) {
			return t;
		}
		return new Undefined8DataType();
	}

	// -------------------------------------------------------------------------
	// GHS CALLT tables.
	// -------------------------------------------------------------------------

	private void processCalltSites(Program program, AddressSetView set,
			Map<Address, HelperInfo> found, TaskMonitor monitor, MessageLog log)
			throws CancelledException {
		// V850RegisterAnalyzer owns CTBP/CALLT dataflow and runs earlier in
		// the pipeline; it emits the callt target references (COMPUTED_CALL)
		// and creates the valid function starts. Consume those references
		// here to identify and inline the helpers they reach.
		Listing listing = program.getListing();
		InstructionIterator it = listing.getInstructions(set, true);
		while (it.hasNext()) {
			monitor.checkCancelled();
			Instruction ins = it.next();
			if (!"callt".equals(ins.getMnemonicString())) {
				continue;
			}
			for (Reference ref : program.getReferenceManager()
					.getReferencesFrom(ins.getMinAddress())) {
				if (!ref.getReferenceType().isCall() || !ref.isMemoryReference()) {
					continue;
				}
				Address target = ref.getToAddress();
				if (!isMarked(program, target)) {
					HelperInfo info = matchAt(program, target);
					if (info != null) {
						markHelper(program, info, monitor, log);
						found.put(info.entry, info);
					}
				}
			}
		}
	}

	private boolean isMarked(Program program, Address target) {
		Function f = program.getListing().getFunctionAt(target);
		return f != null && (f.isInline() || f.getCallFixup() != null);
	}

	// -------------------------------------------------------------------------
	// GHS dynamic locals halfwords at confirmed helper call sites.
	// -------------------------------------------------------------------------

	private void applyLocalsWords(Program program, Map<Address, HelperInfo> found,
			TaskMonitor monitor, MessageLog log) throws CancelledException {
		TreeSet<HelperInfo> ordered = new TreeSet<>((l, r) -> l.entry.compareTo(r.entry));
		ordered.addAll(found.values());
		for (HelperInfo info : ordered) {
			monitor.checkCancelled();
			boolean before = info.isSave() && info.locals;
			boolean after = info.kind == HelperKind.GHS_CALLT_LOAD && info.locals;
			if (!before && !after) {
				continue;
			}
			ReferenceIterator refs = program.getReferenceManager().getReferencesTo(info.entry);
			List<Reference> callRefs = new ArrayList<>();
			while (refs.hasNext()) {
				Reference ref = refs.next();
				if (ref.getReferenceType().isCall()) {
					callRefs.add(ref);
				}
			}
			for (Reference ref : callRefs) {
				Address from = ref.getFromAddress();
				Instruction callIns = program.getListing().getInstructionAt(from);
				if (info.callt) {
					if (callIns == null || !"callt".equals(callIns.getMnemonicString())) {
						continue;
					}
				}
				else {
					if (callIns == null || !"jarl".equals(callIns.getMnemonicString()) ||
						!isSaveLinkRegister(callIns)) {
						continue;
					}
				}
				Address word = before ? from.subtract(2) : from.add(2);
				if (before) {
					createLocalsWord(program, word);
				}
				else {
					clearAndCreateLocalsWord(program, word, monitor);
				}
			}
		}
	}

	/** jarl ...,r10 links the GHS/GCC save helpers; the locals word sits at -2. */
	private static boolean isSaveLinkRegister(Instruction jarl) {
		Register link = firstRegister(jarl.getOpObjects(1));
		return link != null && "r10".equals(link.getName());
	}

	private static void createLocalsWord(Program program, Address word) {
		Listing listing = program.getListing();
		Data existing = listing.getDataAt(word);
		// Ghidra lazily materializes UNDEFINED DataDB placeholders for gaps
		// (getCodeUnitContaining and the clear/repair commands do this), and
		// getDataAt happily returns them. An undefined placeholder is not
		// user data: it must never block the word definition, otherwise the
		// dynamic-locals halfword stays undefined forever.
		if (listing.getInstructionAt(word) != null || (existing != null && existing.isDefined())) {
			return;
		}
		try {
			listing.createData(word, WordDataType.dataType);
		}
		catch (Exception e) {
			// leave undefined; the analyzer will retry on the next pass
		}
	}

	/**
	 * The word after a ghsld4 callt is never executed (the helper returns via
	 * the restored LP), but linear disassembly decodes it. Clear it and any
	 * fallout, then define the halfword data.
	 */
	private void clearAndCreateLocalsWord(Program program, Address word, TaskMonitor monitor) {
		Listing listing = program.getListing();
		Data existing = listing.getDataAt(word);
		// See createLocalsWord: lazily materialized undefined placeholders are
		// not data and must not abort the definition.
		if (existing != null && existing.isDefined()) {
			return;
		}
		Instruction bad = listing.getInstructionAt(word);
		if (bad == null) {
			createLocalsWord(program, word);
			return;
		}
		AddressSet protect = new AddressSet();
		Function f = program.getFunctionManager().getFunctionContaining(word);
		if (f != null) {
			protect.add(f.getBody());
		}
		protect.deleteRange(word, word.add(1));
		ClearFlowAndRepairCmd cmd = new ClearFlowAndRepairCmd(new AddressSet(word, word.add(1)),
			protect, true, false, true);
		cmd.applyTo(program, monitor);
		// The repair pass re-disassembles every address that still receives
		// flow references into the cleared range - the callt's fall-through -
		// which can resurrect the dead halfword as an instruction. The word
		// after a GHS CALLT return helper is pure data (the helper returns
		// through the LP restored by the CALLT save, never through CTPC), so
		// remove any resurrection without repair before defining the word.
		if (listing.getInstructionAt(word) != null) {
			listing.clearCodeUnits(word, word.add(1), false);
		}
		createLocalsWord(program, word);
	}

	// -------------------------------------------------------------------------
	// Stripped (default-named) 64-bit arithmetic recovery.
	//
	// GCC libgcc's DI-mode routines and the GHS MULTI 64-bit runtime share
	// the register ABI r6:r7 / r8:r9 -> r10:r11 (verified against the pinned
	// GCC 16.2.0 v850 backend: arguments are allocated from r6 in word
	// units, DImode values occupy register pairs, and scalar results return
	// in r10, DImode results in r10:r11). When the symbol table is stripped,
	// the contract is recovered only from equivalence-grade proofs:
	//
	//  * V850ArithmeticReferenceMatcher (shared module component) matches
	//    the body's normalized instruction sequence against templates
	//    derived from the pinned GCC 16.2.0 v850-elf reference output -
	//    the libgcc objects (_negdi2, the variable shifts and three-way
	//    compares, _muldi3, the inlined-udivmoddi4 division family, the
	//    checked *v routines) and the compiler's freestanding -O2 idioms -
	//    binding branch structure, called dependencies (save/return
	//    helpers, the ___udivsi3 family) and movhi/movea relocation pairs
	//    to validated targets. It returns the canonical libgcc stem, or
	//    null.
	//  * The GHS register-pair logic idiom below is byte-exact over the
	//    entire body; GCC emits no libgcc routine for 64-bit logic, so that
	//    family has no reference stem.
	//
	// The earlier symbolic path-set engine was deleted on review: accepting
	// an unordered collection of exit expressions proved neither the branch
	// predicates that select them (inverted condition arms folded the same
	// way), nor preservation of SP/gp/r20-r31/LP (a prepended stack
	// adjustment or callee-save clobber was erased by the installed fixup),
	// nor r0's architecturally-zero read/write behavior, and its jarl-to-lp
	// handling discarded arbitrary calls as abort paths. Semantically
	// different near-misses now simply match no reference and stay
	// untouched.
	// -------------------------------------------------------------------------

	/**
	 * Attempts stripped-arithmetic recovery on one default-named function:
	 * proves the body against the shared reference matcher (or the exact
	 * linear GHS logic idiom) and, on a match, renames the function and
	// applies the contract exactly as the named path does - call fixup plus
	// signature, with the trapping *v family keeping name + signature only
	// so their abort calls remain observable.
	 */
	private void recoverStrippedArithmetic(Program program, Function f, TaskMonitor monitor,
			MessageLog log) throws CancelledException {
		if (f.getCallFixup() != null || f.isInline()) {
			return;
		}
		String stem = V850ArithmeticReferenceMatcher.match(program, f, monitor);
		if (stem == null) {
			stem = matchLinearLogicPair(program, f);
		}
		if (stem == null) {
			return;
		}
		ArithContract contract = ARITH_CONTRACTS.get(stem);
		if (contract == null) {
			Msg.warn(this, "V850 helper: reference matcher returned unknown stem '" + stem +
				"' for " + f.getName() + " at " + f.getEntryPoint());
			return;
		}
		rename(program, f.getEntryPoint(), "__" + stem, log);
		Function named = program.getListing().getFunctionAt(f.getEntryPoint());
		if (named != null) {
			applyArithContract(program, named, contract, monitor, log);
		}
	}

	/**
	 * GHS register-pair logic helper: the entire body is exactly
	 * 
	 * <pre>
	 *   mov r6,r10 ; op r8,r10 ; mov r7,r11 ; op r9,r11 ; jmp [lp]
	 * </pre>
	 * 
	 * with op in {and,or,xor}: one straight-line basic block and nothing
	 * else, so the machine computes r10:r11 = a op b with no other
	 * observable effect - no branches, loads/stores, stack writes, calls,
	 * or r0/preserved-register hazards to mis-model. Byte-exact over the
	 * whole body: any extra or mutated instruction rejects the match.
	 *
	 * @return the ARITH_CONTRACTS key (gh_and64/gh_or64/gh_xor64), or null
	 */
	private String matchLinearLogicPair(Program program, Function f) {
		AddressSetView view = f.getBody();
		if (view == null || view.getNumAddressRanges() != 1) {
			return null;
		}
		Iterator<AddressRange> ranges = view.getAddressRanges();
		AddressRange range = ranges.next();
		// The whole entry body, exactly: the first listed instruction starts
		// at the entry point (the listing iterator skips undefined bytes, so
		// the range minimum alone would not prove a leading gap is absent);
		// the contiguity + trailing checks below close the rest.
		List<Instruction> body = new ArrayList<>();
		InstructionIterator it = program.getListing().getInstructions(view, true);
		while (it.hasNext()) {
			body.add(it.next());
			if (body.size() > 5) {
				return null;
			}
		}
		if (body.size() != 5) {
			return null;
		}
		if (!body.get(0).getMinAddress().equals(f.getEntryPoint())) {
			return null; // leading undefined bytes inside the body: reject
		}
		// One contiguous straight-line block ending in the return.
		for (int i = 0; i < 4; i++) {
			Instruction ins = body.get(i);
			if (ins.getFlows().length != 0) {
				return null;
			}
			if (!ins.getMinAddress()
					.equals(body.get(i + 1).getMinAddress().subtract(ins.getLength()))) {
				return null;
			}
		}
		if (!body.get(4).getMaxAddress().equals(range.getMaxAddress())) {
			return null; // trailing bytes inside the body: not the whole body
		}
		String op = logicOp(body.get(1));
		if (op == null || !op.equals(logicOp(body.get(3)))) {
			return null;
		}
		if (!isMovRegReg(body.get(0), "r6", "r10") || !isOpRegReg(body.get(1), op, "r8", "r10") ||
			!isMovRegReg(body.get(2), "r7", "r11") ||
			!isOpRegReg(body.get(3), op, "r9", "r11")) {
			return null;
		}
		if (!isJmpReg(program, body.get(4).getMinAddress(), "lp")) {
			return null;
		}
		return "gh_" + op + "64";
	}

	/** The and/or/xor mnemonic of a two-register data op, or null. */
	private static String logicOp(Instruction ins) {
		String m = ins == null ? null : ins.getMnemonicString();
		return ("and".equals(m) || "or".equals(m) || "xor".equals(m)) ? m : null;
	}
}
