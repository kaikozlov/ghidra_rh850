/* V850 arithmetic reference matcher: exact normalized-template recognition of
 * stripped GCC libgcc DImode arithmetic helpers.
 *
 * Recognizes the canonical libgcc routines (adddi3 ... negvdi2) by exact
 * comparison against reference templates derived from genuine GCC 16.2.0
 * v850-elf libgcc objects (committed module data, produced by
 * tools/testing/processor/build_v850_arithmetic_reference_templates.py - see
 * that producer's provenance block for the pinned toolchain, sources, and
 * rebuild recipe). Nothing at runtime depends on inputs outside the module.
 *
 * A match requires EVERY instruction of the reference body to agree in
 * mnemonic, encoded length, operand registers, immediates (signed or unsigned
 * rendering of the same bit pattern), memory displacements and
 * intra-function branch targets (offsets relative to the entry), the only
 * variability being link-time addresses captured by validated external
 * bindings:
 *
 *   - R_V810_WHI1/R_V810_WLO movhi/movea pairs compose the target address
 *     (((hi << 16) + sext16(lo)) mod 2^32, correct under arbitrary rebase
 *     including HIGH-ADJ forms) of a data symbol (___clz_tab, validated by
 *     its exact 256 table bytes) or a called function (validated recursively
 *     by that dependency's own template, never by its name);
 *   - R_V850_PCR22 jarl/jr targets (calls, tail jumps to the shared
 *     save/return helpers, and the abort call of the checked *v routines)
 *     are bound to functions validated the same way, with _abort
 *     additionally required to be a real function that is canonically named
 *     or marked no-return.
 * All references to one symbol must resolve to a single consistent address.
 * The register-call idiom (jarl next,lp / add 4,lp / ... / jmp [reg], where
 * reg was loaded by the bound movhi/movea pair) needs no extra machinery:
 * the idiom's rows are matched exactly, so the register provably holds the
 * validated target and the return-flow continuation target is pinned by the
 * exact jarl/add offsets.
 *
 * Boundary decision: the matched region is exactly the template's byte span
 * (per-row encoded lengths from the reference object, contiguous from the
 * entry). The Ghidra function body is deliberately NOT used as the bound:
 * GCC tail-jumps to shared save/return helpers make flow-discovered bodies
 * legitimately extend outside the function's own code, so the span is the
 * precise extent. Within the span, every byte is covered by exactly the
 * template rows: row 0 sits at the entry, consecutive rows are contiguous,
 * each row's encoded length matches, and no extra instruction may start at
 * any non-row offset inside the span. Appended unreachable code after the
 * span (dead fallthrough past a final call, for instance) is outside the
 * reference function and therefore outside this matcher's claim.
 *
 * Hidden-block disassembly: the register-call idiom has no static flow to
 * its continuation, so Ghidra's flow-driven discovery legitimately leaves
 * interior blocks of the large division templates undefined. Undefined rows
 * ("gaps") are only ever disassembled after EVERY already-defined row has
 * matched exactly in mnemonic/operand shape, so a mismatching candidate
 * never triggers disassembly side effects; after the fill, the complete row
 * set is re-verified in original program order with the real binding state
 * (a movhi half may live in a filled block while its movea half was already
 * defined, or vice versa).
 *
 * The public match() returns only the GCC contract stems consumed by
 * V850CompilerHelperAnalyzer.ARITH_CONTRACTS; the dependency templates
 * (udivsi3/umodsi3/mulsi3/udivmoddi4, the save/return bodies) validate
 * recursively inside a match and are not standalone results.
 */
package ghidra.app.plugin.core.analysis;

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.framework.Application;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.listing.Program;
import ghidra.program.model.lang.Register;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.scalar.Scalar;
import ghidra.util.Msg;
import ghidra.util.exception.CancelledException;
import ghidra.util.task.TaskMonitor;

import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

/**
 * Exact reference-template matcher for stripped GCC libgcc DImode arithmetic
 * helpers on V850/RH850. See the class-level block comment for the matching
 * contract and boundary decisions.
 */
public final class V850ArithmeticReferenceMatcher {

	private static final String CATALOG_PATH = "arithmetic/v850_arithmetic_reference_templates.json";

	/** Architectural register order (index == register number). */
	private static final String[] GPRS = { "r0", "r1", "r2", "sp", "gp", "tp", "r6", "r7", "r8",
		"r9", "r10", "r11", "r12", "r13", "r14", "r15", "r16", "r17", "r18", "r19", "r20", "r21",
		"r22", "r23", "r24", "r25", "r26", "r27", "r28", "r29", "ep", "lp" };

	/** Numeric aliases for the architectural register names (defensive). */
	private static final Map<String, Integer> REGISTER_NUMBERS = buildRegisterNumbers();

	/**
	 * Stems consumable by V850CompilerHelperAnalyzer.ARITH_CONTRACTS (its GCC
	 * libgcc keys). Only these are returned by {@link #match}; dependency
	 * templates validate recursively inside a match.
	 */
	private static final Set<String> CONTRACT_STEMS = new HashSet<>(Arrays.asList(
		"adddi3", "subdi3", "muldi3", "divdi3", "udivdi3", "moddi3", "umoddi3", "negdi2",
		"ashldi3", "ashrdi3", "lshrdi3", "cmpdi2", "ucmpdi2", "addvdi3", "subvdi3", "mulvdi3",
		"negvdi2"));

	private static final int MAX_DEPTH = 4;

	private static volatile Catalog catalog;
	private static volatile boolean loadFailed;

	/** One normalized reference body: rows of [offset, mnemonic, tokens...]. */
	private static final class Template {
		final String stem;
		final long[] offsets;
		final String[] mnemonics;
		final String[][] tokens;
		final int[] lengths;
		/** Exact byte extent: last row offset + last row length. */
		final long span;

		Template(String stem, List<List<String>> rows, int[] lengths) {
			this.stem = stem;
			int n = rows.size();
			if (n == 0 || lengths.length != n) {
				throw new IllegalStateException("template " + stem + ": bad row/length counts");
			}
			this.offsets = new long[n];
			this.mnemonics = new String[n];
			this.tokens = new String[n][];
			this.lengths = lengths;
			for (int i = 0; i < n; i++) {
				List<String> row = rows.get(i);
				if (row.size() < 2) {
					throw new IllegalStateException(
						"template " + stem + " row " + i + ": missing mnemonic");
				}
				offsets[i] = Long.parseLong(row.get(0));
				mnemonics[i] = row.get(1);
				tokens[i] = row.subList(2, row.size()).toArray(new String[0]);
				if (lengths[i] != 2 && lengths[i] != 4) {
					throw new IllegalStateException(
						"template " + stem + " row " + i + ": bad length " + lengths[i]);
				}
				if (offsets[i] < 0 || (i > 0 && offsets[i] != offsets[i - 1] + lengths[i - 1])) {
					throw new IllegalStateException(
						"template " + stem + " row " + i + ": non-contiguous offsets");
				}
				validateTokens(stem, i, tokens[i]);
			}
			if (offsets[0] != 0) {
				throw new IllegalStateException("template " + stem + ": does not start at entry");
			}
			this.span = offsets[n - 1] + lengths[n - 1];
		}

		/** Validates the token grammar once at load so matching never throws. */
		private static void validateTokens(String stem, int row, String[] toks) {
			for (String tok : toks) {
				char kind = tok.charAt(0);
				try {
					switch (kind) {
						case 'r': {
							int reg = Integer.parseInt(tok.substring(1));
							if (reg < 0 || reg > 31) {
								throw new IllegalStateException("bad register " + tok);
							}
							break;
						}
						case '#': {
							Long.decode(tok.substring(1));
							break;
						}
						case '@': {
							long off = Long.decode(tok.substring(1));
							if (off < 0) {
								throw new IllegalStateException("negative branch offset " + tok);
							}
							break;
						}
						case 'P':
						case 'H':
						case 'L': {
							if (tok.length() < 3) {
								throw new IllegalStateException("empty binding symbol");
							}
							break;
						}
						default:
							throw new IllegalStateException("unknown token kind " + tok);
					}
				}
				catch (NumberFormatException e) {
					throw new IllegalStateException(
						"template " + stem + " row " + row + ": unparseable token " + tok);
				}
			}
		}
	}

	/** External symbol kinds used for binding validation. */
	private static final String KIND_FUNCTION = "function";
	private static final String KIND_CLZTAB = "clztab";
	private static final String KIND_ABORT = "abort";
	private static final Set<String> ABORT_NAMES =
		new HashSet<>(Arrays.asList("abort", "_abort", "___abort"));

	private static final class SymbolInfo {
		final String kind;
		final String stem;

		SymbolInfo(String kind, String stem) {
			this.kind = kind;
			this.stem = stem;
		}
	}

	/** Accumulated external bindings for one template attempt. */
	private static final class Bindings {
		final Map<String, Address> calls = new HashMap<>();
		/** Symbol -> FIFO of pending movhi halves, drained by matching movea halves. */
		final Map<String, List<Long>> pendingHis = new HashMap<>();
		/** Symbol -> composed addresses from closed movhi/movea pairs. */
		final Map<String, List<Long>> composed = new HashMap<>();

		boolean noteCall(String sym, Address a) {
			Address prev = calls.get(sym);
			if (prev != null && !prev.equals(a)) {
				return false;
			}
			calls.put(sym, a);
			return true;
		}

		/** Records one half of a movhi/movea address pair; returns false on
		 *  a movea without a pending movhi or a disagreement between pairs. */
		boolean noteHalf(String sym, boolean hi, long value) {
			if (hi) {
				pendingHis.computeIfAbsent(sym, s -> new ArrayList<>()).add(value);
				return true;
			}
			List<Long> pending = pendingHis.get(sym);
			if (pending == null || pending.isEmpty()) {
				return false;
			}
			long hiVal = pending.remove(0);
			// Compose modulo 2^32: HIGH-ADJ link-time immediates legitimately
			// produce a negative 16-bit sum before wrapping (e.g. target
			// 0xfffffff0 encodes as hi=0, lo=-16), so mask, never reject.
			long addr = ((hiVal << 16) + (short) value) & 0xffffffffL;
			List<Long> seen = composed.computeIfAbsent(sym, s -> new ArrayList<>());
			for (long prev : seen) {
				if (prev != addr) {
					return false;
				}
			}
			seen.add(addr);
			return true;
		}

		/**
		 * Resolves each externally bound symbol to a single address. All
		 * movhi/movea pairs of a symbol must have composed the same address
		 * ((hi << 16) + sext16(lo)), every pair must be closed, and a
		 * call-relocated target must agree with the composed address when
		 * both exist.
		 */
		Map<String, Address> resolve(Program program) {
			for (List<Long> pending : pendingHis.values()) {
				if (!pending.isEmpty()) {
					return null;
				}
			}
			Map<String, Address> out = new HashMap<>();
			for (Map.Entry<String, List<Long>> e : composed.entrySet()) {
				if (e.getValue().isEmpty()) {
					return null;
				}
				long addr = e.getValue().get(0);
				Address a = program.getAddressFactory().getDefaultAddressSpace().getAddress(addr);
				out.put(e.getKey(), a);
			}
			for (Map.Entry<String, Address> e : calls.entrySet()) {
				Address prev = out.put(e.getKey(), e.getValue());
				if (prev != null && !prev.equals(e.getValue())) {
					return null;
				}
			}
			return out;
		}
	}

	/** The loaded reference catalog (immutable after loading). */
	private static final class Catalog {
		final List<Template> templates = new ArrayList<>();
		final Map<String, SymbolInfo> symbols = new HashMap<>();
		final Map<String, Template> byStem = new HashMap<>();
		final byte[] clzTab;

		Catalog(byte[] clzTab) {
			this.clzTab = clzTab;
		}
	}

	private V850ArithmeticReferenceMatcher() {
		// utility class
	}

	/**
	 * Matches a stripped function body against the reference-template
	 * catalog. The whole reference body must be present and exact (see the
	 * class-level comment); candidates are rejected fast by entry opcode and
	 * by the defined-instruction count inside the template span before any
	 * row-by-row comparison, and the monitor is honoured throughout.
	 *
	 * @param program the program under analysis
	 * @param function the candidate function (entry instruction sequence)
	 * @param monitor task monitor for cancellation
	 * @return the canonical GCC libgcc contract stem (adddi3, subdi3, muldi3,
	 *         divdi3, udivdi3, moddi3, umoddi3, negdi2, ashldi3, ashrdi3,
	 *         lshrdi3, cmpdi2, ucmpdi2, addvdi3, subvdi3, mulvdi3, negvdi2),
	 *         or null when the body is not an exact reference match
	 */
	public static String match(Program program, Function function, TaskMonitor monitor)
			throws CancelledException {
		Catalog cat = catalog();
		if (cat == null || function == null) {
			return null;
		}
		Address entry = function.getEntryPoint();
		Instruction first = program.getListing().getInstructionAt(entry);
		Set<Long> visited = new HashSet<>();
		for (Template t : cat.templates) {
			if (!CONTRACT_STEMS.contains(t.stem)) {
				continue;
			}
			monitor.checkCancelled();
			// Fast reject, opcode first: the entry instruction's mnemonic.
			if (first != null && !first.getMnemonicString().equals(t.mnemonics[0])) {
				continue;
			}
			String stem = matchTemplate(program, cat, t, entry, visited, 0, monitor);
			if (stem != null) {
				return stem;
			}
		}
		return null;
	}

	// -------------------------------------------------------------------------
	// Catalog loading
	// -------------------------------------------------------------------------

	private static Catalog catalog() {
		Catalog c = catalog;
		if (c != null || loadFailed) {
			return c;
		}
		synchronized (V850ArithmeticReferenceMatcher.class) {
			c = catalog;
			if (c != null || loadFailed) {
				return c;
			}
			try {
				c = loadCatalog();
			}
			catch (Exception e) {
				loadFailed = true;
				Msg.error(V850ArithmeticReferenceMatcher.class,
					"V850 arithmetic reference catalog unavailable (" + CATALOG_PATH + "): " +
						e.getMessage());
				return null;
			}
			catalog = c;
			return c;
		}
	}

	private static Catalog loadCatalog() throws Exception {
		InputStream in = Application.getModuleDataFile(CATALOG_PATH).getInputStream();
		String text;
		try {
			text = new String(in.readAllBytes(), StandardCharsets.UTF_8);
		}
		finally {
			in.close();
		}
		JsonObject root = JsonParser.parseString(text).getAsJsonObject();
		byte[] clz = hex(root.getAsJsonObject("clz_tab").get("bytes").getAsString());
		if (clz.length != 256) {
			throw new IllegalStateException("___clz_tab must be 256 bytes");
		}
		Catalog cat = new Catalog(clz);
		for (JsonElement el : root.getAsJsonArray("helpers")) {
			JsonObject h = el.getAsJsonObject();
			List<List<String>> rows = new ArrayList<>();
			for (JsonElement ie : h.getAsJsonArray("instructions")) {
				List<String> row = new ArrayList<>();
				for (JsonElement te : ie.getAsJsonArray()) {
					row.add(te.getAsString());
				}
				rows.add(row);
			}
			int[] lengths = new int[rows.size()];
			int k = 0;
			for (JsonElement le : h.getAsJsonArray("lengths")) {
				lengths[k++] = le.getAsInt();
			}
			Template t = new Template(h.get("stem").getAsString(), rows, lengths);
			if (cat.byStem.put(t.stem, t) != null) {
				throw new IllegalStateException("duplicate template stem " + t.stem);
			}
			cat.templates.add(t);
		}
		for (Map.Entry<String, JsonElement> e : root.getAsJsonObject("symbols").entrySet()) {
			JsonObject s = e.getValue().getAsJsonObject();
			cat.symbols.put(e.getKey(), new SymbolInfo(s.get("kind").getAsString(),
				s.has("stem") && !s.get("stem").isJsonNull() ? s.get("stem").getAsString() : null));
		}
		return cat;
	}

	// -------------------------------------------------------------------------
	// Structural matching
	// -------------------------------------------------------------------------

	private static String matchTemplate(Program program, Catalog cat, Template t, Address entry,
			Set<Long> visited, int depth, TaskMonitor monitor) throws CancelledException {
		if (depth > MAX_DEPTH || !visited.add(entry.getOffset())) {
			return null;
		}
		try {
			Bindings binds = new Bindings();
			if (!structuralMatch(program, t, entry, binds, monitor)) {
				return null;
			}
			Map<String, Address> resolved = binds.resolve(program);
			if (resolved == null) {
				return null;
			}
			if (!validateBindings(program, cat, resolved, visited, depth, monitor)) {
				return null;
			}
			return t.stem;
		}
		finally {
			visited.remove(entry.getOffset());
		}
	}

	/**
	 * Verifies every template row against the listing at entry-relative
	 * offsets, in original program order, with the exact byte extent taken
	 * from the template's per-row lengths. Rows at addresses without a
	 * defined instruction are collected and only disassembled after every
	 * defined row already matches exactly in shape (mnemonic, length,
	 * registers, scalars, branch offsets - external bindings excluded, since
	 * a movhi half may sit in a gap while its movea half is defined), so
	 * wrong templates never trigger disassembly side effects; the
	 * jarl/add/jmp register-call idiom legitimately hides continuation
	 * blocks from pure static flow, and those gaps are filled from the image
	 * bytes and the complete row set is then re-verified in order with the
	 * real binding state. Extra defined instructions inside the body span
	 * reject the match (inserted or deleted code).
	 */
	private static boolean structuralMatch(Program program, Template t, Address entry,
			Bindings binds, TaskMonitor monitor) throws CancelledException {
		Listing listing = program.getListing();
		Address spanEnd = entry.add(t.span - 1);

		// Fast reject, instruction count first: more defined instructions
		// inside the span than template rows can never match.
		int defined = 0;
		InstructionIterator it = listing.getInstructions(new AddressSet(entry, spanEnd), true);
		while (it.hasNext()) {
			monitor.checkCancelled();
			it.next();
			if (++defined > t.offsets.length) {
				return false;
			}
		}

		// Locate undefined rows (hidden continuation blocks).
		List<Integer> gaps = new ArrayList<>();
		for (int i = 0; i < t.offsets.length; i++) {
			monitor.checkCancelled();
			if (listing.getInstructionAt(entry.add(t.offsets[i])) == null) {
				gaps.add(i);
			}
		}

		if (gaps.isEmpty()) {
			// Common case: the whole body is already defined; verify every
			// row in order directly with the real binding state.
			for (int i = 0; i < t.offsets.length; i++) {
				monitor.checkCancelled();
				Instruction ins = listing.getInstructionAt(entry.add(t.offsets[i]));
				if (ins == null || !rowMatches(ins, t, i, entry, binds)) {
					return false;
				}
			}
		}
		else {
			// Gate: every DEFINED row must already match exactly in shape
			// (position-local facts only) before any disassembly runs.
			for (int i = 0; i < t.offsets.length; i++) {
				monitor.checkCancelled();
				Instruction ins = listing.getInstructionAt(entry.add(t.offsets[i]));
				if (ins != null && !rowMatches(ins, t, i, entry, null)) {
					return false;
				}
			}
			for (int i : gaps) {
				monitor.checkCancelled();
				Address a = entry.add(t.offsets[i]);
				if (listing.getInstructionAt(a) == null) {
					new DisassembleCommand(a, null, true).applyTo(program, monitor);
				}
			}
			// Full re-verification in original program order with the real
			// binding state (binds the H:/L: halves across gap boundaries in
			// program order, not pass order).
			for (int i = 0; i < t.offsets.length; i++) {
				monitor.checkCancelled();
				Instruction ins = listing.getInstructionAt(entry.add(t.offsets[i]));
				if (ins == null || !rowMatches(ins, t, i, entry, binds)) {
					return false;
				}
			}
		}

		// Exact extent: every byte of the span is covered by exactly the
		// template rows - no extra instruction may start inside the span.
		int count = 0;
		it = listing.getInstructions(new AddressSet(entry, spanEnd), true);
		while (it.hasNext()) {
			monitor.checkCancelled();
			it.next();
			count++;
		}
		return count == t.offsets.length;
	}


	/**
	 * Compares one live instruction against template row i. Operand objects
	 * are consumed FLAT, positionally across all operands (Registers,
	 * Scalars, Addresses): the module renders memory operands as separate
	 * displacement/base operands, and a compound operand would contribute
	 * its objects in display order either way - no nested-array assumption.
	 * A null {@code binds} requests shape-only comparison: every
	 * position-local fact (mnemonic, encoded length, register numbers,
	 * scalar bit patterns, relative branch targets, binding-token operand
	 * kinds) is still enforced; only the cross-row binding bookkeeping is
	 * deferred.
	 */
	private static boolean rowMatches(Instruction ins, Template t, int i, Address entry,
			Bindings binds) {
		if (ins.getLength() != t.lengths[i]) {
			return false;
		}
		if (!ins.getMnemonicString().equals(t.mnemonics[i])) {
			return false;
		}
		String[] toks = t.tokens[i];
		Object[] objs = flatOperandObjects(ins);
		if (objs.length != toks.length) {
			return false;
		}
		for (int k = 0; k < toks.length; k++) {
			String tok = toks[k];
			Object o = objs[k];
			char kind = tok.charAt(0);
			if (kind == 'r') {
				if (!(o instanceof Register) ||
					registerNumber((Register) o) != Integer.parseInt(tok.substring(1))) {
					return false;
				}
			}
			else if (kind == '#') {
				if (!(o instanceof Scalar) || !scalarEquals((Scalar) o, tok.substring(1))) {
					return false;
				}
			}
			else if (kind == '@') {
				if (!(o instanceof Address)) {
					return false;
				}
				long want = Long.decode(tok.substring(1));
				if (((Address) o).getOffset() - entry.getOffset() != want) {
					return false;
				}
			}
			else if (kind == 'P') {
				if (!(o instanceof Address)) {
					return false;
				}
				if (binds != null && !binds.noteCall(tok.substring(2), (Address) o)) {
					return false;
				}
			}
			else if (kind == 'H' || kind == 'L') {
				if (!(o instanceof Scalar)) {
					return false;
				}
				if (binds != null && !binds.noteHalf(tok.substring(2), kind == 'H',
					((Scalar) o).getUnsignedValue() & 0xffffL)) {
					return false;
				}
			}
			else {
				return false;
			}
		}
		return true;
	}

	/**
	 * All operand objects of the instruction, flattened in operand and
	 * display order.
	 */
	private static Object[] flatOperandObjects(Instruction ins) {
		int n = ins.getNumOperands();
		int total = 0;
		for (int k = 0; k < n; k++) {
			Object[] ops = ins.getOpObjects(k);
			if (ops != null) {
				total += ops.length;
			}
		}
		Object[] out = new Object[total];
		int at = 0;
		for (int k = 0; k < n; k++) {
			Object[] ops = ins.getOpObjects(k);
			if (ops == null) {
				continue;
			}
			System.arraycopy(ops, 0, out, at, ops.length);
			at += ops.length;
		}
		return out;
	}

	/**
	 * Scalar comparison accepting either rendering of the same encoded bit
	 * pattern: the module renders sign-extended immediates (movhi/movea
	 * s1631, add imm5) as negative values and zero-extended ones (andi z1631)
	 * as positive values, and the catalog recorded objdump's per-instruction
	 * rendering of the same bits.
	 */
	private static boolean scalarEquals(Scalar s, String token) {
		long want;
		try {
			want = Long.decode(token);
		}
		catch (NumberFormatException e) {
			return false;
		}
		return s.getSignedValue() == want || s.getUnsignedValue() == want;
	}

	// -------------------------------------------------------------------------
	// Binding validation
	// -------------------------------------------------------------------------

	private static boolean validateBindings(Program program, Catalog cat,
			Map<String, Address> resolved, Set<Long> visited, int depth, TaskMonitor monitor)
			throws CancelledException {
		for (Map.Entry<String, Address> e : resolved.entrySet()) {
			monitor.checkCancelled();
			SymbolInfo info = cat.symbols.get(e.getKey());
			if (info == null) {
				return false;
			}
			Address a = e.getValue();
			switch (info.kind) {
				case KIND_CLZTAB: {
					byte[] got = new byte[256];
					try {
						Memory mem = program.getMemory();
						if (!mem.contains(a) || !mem.contains(a.add(255))) {
							return false;
						}
						mem.getBytes(a, got);
					}
					catch (Exception ex) {
						return false;
					}
					if (!Arrays.equals(cat.clzTab, got)) {
						return false;
					}
					break;
				}
				case KIND_FUNCTION: {
					Template dep = cat.byStem.get(info.stem);
					if (dep == null) {
						return false;
					}
					if (matchTemplate(program, cat, dep, a, visited, depth + 1, monitor) == null) {
						return false;
					}
					break;
				}
				case KIND_ABORT: {
					Function abort = program.getFunctionManager().getFunctionAt(a);
					if (abort == null) {
						return false;
					}
					if (!ABORT_NAMES.contains(abort.getName()) && !abort.hasNoReturn()) {
						return false;
					}
					break;
				}
				default:
					return false;
			}
		}
		return true;
	}

	// -------------------------------------------------------------------------
	// Helpers
	// -------------------------------------------------------------------------

	private static Map<String, Integer> buildRegisterNumbers() {
		Map<String, Integer> m = new HashMap<>();
		for (int i = 0; i < GPRS.length; i++) {
			m.put(GPRS[i], i);
		}
		for (int i = 0; i < 32; i++) {
			m.putIfAbsent("r" + i, i);
		}
		return m;
	}

	private static int registerNumber(Register reg) {
		Integer n = REGISTER_NUMBERS.get(reg.getName());
		return n == null ? -1 : n;
	}

	private static byte[] hex(String s) {
		byte[] out = new byte[s.length() / 2];
		for (int i = 0; i < out.length; i++) {
			out[i] = (byte) Integer.parseInt(s.substring(i * 2, i * 2 + 2), 16);
		}
		return out;
	}
}
