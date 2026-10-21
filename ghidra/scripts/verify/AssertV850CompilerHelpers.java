//@category Verification
/* Asserts V850 compiler-helper recovery end to end: stripped GCC/GHS MULTI
 * save/restore helpers (with real decompiler stack effects via inlining),
 * GHS CALLT table recovery, and 64-bit arithmetic contracts with real
 * p-code folding and correct signedness. Every stripped arithmetic body is
 * relocated verbatim from the pinned GCC 16.2.0 v850-elf toolchain objects
 * committed under data/reference/v850-gcc-libgcc/16.2.0 (helpers.o
 * freestanding -O2 idioms plus the libgcc add/sub/neg/shift/cmp/mul family,
 * addvdi3/subvdi3/negvdi2/mulvdi3, divdi3/udivdi3/moddi3/umoddi3 and their
 * REAL dependency bodies ___udivsi3/___umodsi3/___mulsi3, the GCC
 * __return_r20_r31/__return_r24_r31 register-restore helpers, and the exact
 * ___clz_tab bit-length table), with every external R_V810_WHI1/WLO and
 * R_V850_PCR22 relocation rewritten to fixture addresses - never stubs or
 * hand-built lookalikes. Callers are ABI-correct functions: they save and
 * restore LP and the nonvolatile data base r20 across every call, feed
 * genuinely variable runtime arguments loaded from writable data memory
 * (neither constants nor read-only image values, so constant folding cannot
 * erase the folded operations), and store every result to a distinct
 * escaping memory slot. A separate constant-driven consumer proves the
 * recovered three-way compare selection and signedness boundaries through
 * decompiler-folded STORE constants, and a twin-call consumer proves the
 * ABI-clobber semantics stay NON-deterministic: two identical calls must
 * never have their opaque killed-register effects CSE-equated. Both
 * analyzers are driven through their real lifecycle (canAnalyze before
 * added) over executable-but-read-only flash, exactly as
 * AutoAnalysisManager would schedule them. Behavioral assertions check the
 * folded p-code operations (in the decompiler's canonical forms), retained
 * trapping calls, ABI parameter/return widths and signedness, real
 * dependency structure, escaping stack-pointer effects, and independent
 * caller-clobbered values. Machine execution additionally verifies unsigned
 * remainder boundaries and frame restoration through the real dependencies.
 * Prints "ASSERT v850-compiler-helpers: passed".
 */
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

import ghidra.app.plugin.core.analysis.V850RegisterAnalyzer;
import ghidra.app.plugin.core.analysis.V850CompilerHelperAnalyzer;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import ghidra.app.util.importer.MessageLog;
import ghidra.program.database.ProgramDB;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.data.WordDataType;
import ghidra.program.model.lang.Language;
import ghidra.program.model.lang.LanguageID;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.pcode.PcodeOpAST;
import ghidra.program.model.pcode.Varnode;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.SymbolTable;
import ghidra.program.util.DefaultLanguageService;
import ghidra.util.task.TaskMonitor;
public class AssertV850CompilerHelpers extends GhidraScript {

	private final List<String> failures = new ArrayList<>();
	/** Decompiled p-code cache keyed by function entry (one decompile each). */
	private final Map<Long, PcodeOp[]> pcodeCache = new HashMap<>();

	@Override
	protected void run() throws Exception {
		Language language = DefaultLanguageService.getLanguageService()
			.getLanguage(new LanguageID("v850e3:LE:32:default"));
		ProgramDB program = new ProgramDB("v850-compiler-helpers", language,
			language.getDefaultCompilerSpec(), this);
		int tx = program.startTransaction("fixture");
		try {
		buildFixtures(program);
		// Pipeline order: the register analyzer owns CTBP/CALLT dataflow
		// and emits the callt references; the helper analyzer consumes.
		// Both flash blocks are analyzed (the GCC shift constant-edge
		// consumer lives in the second block at 0x20000). Both analyzers
		// are driven through the real lifecycle - canAnalyze resolves the
		// architecture registers (CTBP/GP/TP/EP) exactly as
		// AutoAnalysisManager would before added(); calling added()
		// without it silently falls back to the generic no-CALLT-recovery
		// path instead of the production join-consistent resolver.
		AddressSet analyzed = new AddressSet(addr(program, 0x10000), addr(program, 0x13fff));
		analyzed.add(addr(program, 0x20000), addr(program, 0x207ff));
		V850RegisterAnalyzer registerAnalyzer = new V850RegisterAnalyzer();
		if (registerAnalyzer.canAnalyze(program)) {
			registerAnalyzer.added(program, analyzed, monitor, new MessageLog());
		}
		V850CompilerHelperAnalyzer helperAnalyzer = new V850CompilerHelperAnalyzer();
		if (helperAnalyzer.canAnalyze(program)) {
			helperAnalyzer.added(program, analyzed, monitor, new MessageLog());
		}
		runAssertions(program);
		}
		finally {
			program.endTransaction(tx, true);
			program.release(this);
		}
		if (!failures.isEmpty()) {
			throw new IllegalStateException("v850-compiler-helpers failures:\n  " +
				String.join("\n  ", failures));
		}
		println("ASSERT v850-compiler-helpers: passed");
	}

	private Address addr(ProgramDB program, long off) {
		return program.getAddressFactory().getDefaultAddressSpace().getAddress(off);
	}

	private void check(boolean ok, String what) {
		if (!ok) {
			failures.add(what);
		}
	}

	// ------------------------------------------------------------------
	// Fixtures (V850 encodings; each int is one little-endian 16-bit word).
	// ------------------------------------------------------------------

	private void put(ProgramDB program, long off, int... words) throws Exception {
		byte[] bytes = new byte[words.length * 2];
		for (int i = 0; i < words.length; i++) {
			bytes[i * 2] = (byte) (words[i] & 0xff);
			bytes[i * 2 + 1] = (byte) ((words[i] >> 8) & 0xff);
		}
		program.getMemory().setBytes(addr(program, off), bytes);
	}

	/** jarl target,link at address `at` (4-byte disp22 form, inst_start-relative). */
	private int[] jarl(long at, long target, int link) {
		int disp = (int) (target - at);
		return new int[] { (link << 11) | (0x1e << 6) | ((disp >> 16) & 0x3f), disp & 0xffff };
	}

	/** ld.w disp[reg1],reg2 (format VII; even byte displacement, LSB form tag). */
	private int[] ldw(int reg2, int disp, int reg1) {
		return new int[] { (reg2 << 11) | (0x39 << 5) | reg1, (disp & ~1) | 1 };
	}

	/** st.w reg2,disp[reg1]. */
	private int[] stw(int reg2, int disp, int reg1) {
		return new int[] { (reg2 << 11) | (0x3b << 5) | reg1, (disp & ~1) | 1 };
	}

	/**
	 * ABI-correct caller prologue: addi -8,sp,sp; st.w r20,0[sp];
	 * st.w lp,4[sp] (save the nonvolatile data base and LP across the
	 * helper calls); movhi 1,r0,r20; movea 0x4000,r20,r20 establishes
	 * r20 = 0x14000 as the writable-data base. 10 halfwords, 20 bytes.
	 */
	private void callerPrologue(ProgramDB program, long at) throws Exception {
		put(program, at, 0x1e03, 0xfff8, 0xa763, 0x0001, 0xff63, 0x0005, 0xa640, 0x0001,
			0xa634, 0x4000);
	}

	/**
	 * Matching epilogue: ld.w 0[sp],r20; ld.w 4[sp],lp; addi 8,sp,sp;
	 * jmp [lp] (restore LP last so the caller returns to its own caller).
	 * 8 halfwords, 16 bytes.
	 */
	private void callerEpilogue(ProgramDB program, long at) throws Exception {
		put(program, at, 0xa723, 0x0001, 0xff23, 0x0005, 0x1e03, 0x0008, 0x007f);
	}

	/**
	 * Emits one helper-call site with genuinely variable runtime arguments:
	 * the 8-byte argument pair r6:r7 / r8:r9 is loaded from writable data
	 * memory at 0x14000+argSlot*16 relative to the r20 base (loaded values
	 * are neither constants nor read-only image substitutions, so
	 * constant-folding rules cannot erase the folded arithmetic), the call
	 * goes out via jarl lp (LP is saved in the prologue), and both result
	 * words are stored to a distinct escaping global slot at
	 * 0x14300+resIndex*8 so every call's effects stay observable in the
	 * decompiled caller. Seven 4-byte instructions: exactly 28 bytes;
	 * returns the address just past the block.
	 */
	private long strippedCall(ProgramDB program, long at, long target, int argSlot, int resIndex)
			throws Exception {
		int argOff = argSlot * 16;
		int resOff = 0x300 + resIndex * 8;
		int[] words = new int[14];
		int k = 0;
		for (int r = 6; r <= 9; r++) {
			int[] w = ldw(r, argOff + (r - 6) * 4, 20);
			words[k++] = w[0];
			words[k++] = w[1];
		}
		int[] j = jarl(at + 16, target, 31);
		words[k++] = j[0];
		words[k++] = j[1];
		int[] s10 = stw(10, resOff, 20);
		words[k++] = s10[0];
		words[k++] = s10[1];
		int[] s11 = stw(11, resOff + 4, 20);
		words[k++] = s11[0];
		words[k++] = s11[1];
		put(program, at, words);
		return at + words.length * 2;
	}

	/**
	 * One constant-driven value-selection site for the compare consumers:
	 * the four 16-bit constant materializers in `argWords` load r6..r9
	 * (finite constants are deliberate here: the decompiler must fold the
	 * recovered helper payloads against them), the call goes out via
	 * jarl lp, and the 32-bit r10 result is stored to the 4-byte escaping
	 * slot 0x14400+storeDisp relative to the r20 base. 16 bytes.
	 */
	private void constSite(ProgramDB program, long at, long target, int[] argWords,
			int storeDisp) throws Exception {
		int[] words = new int[8];
		words[0] = argWords[0];
		words[1] = argWords[1];
		words[2] = argWords[2];
		words[3] = argWords[3];
		int[] j = jarl(at + 8, target, 31);
		words[4] = j[0];
		words[5] = j[1];
		int[] s10 = stw(10, storeDisp, 20);
		words[6] = s10[0];
		words[7] = s10[1];
		put(program, at, words);
	}

	/**
	 * One ABI-clobber witness site: identical finite constants a=3,b=4 are
	 * MOV'd into r6..r9, the helper is called via jarl lp, and the killed
	 * scratch r2 is stored to the escaping slot 0x14000+storeDisp relative
	 * to the r20 base. 16 bytes. Every site loads identical arguments, so
	 * the ONLY observable difference between two sites is which opaque
	 * __v850_abi_clobber result lands in the slot - exactly what the
	 * CSE-independence assertion observes.
	 */
	private void clobberWitnessSite(ProgramDB program, long at, long target, int storeDisp)
			throws Exception {
		int[] words = { (6 << 11) | (0x10 << 5) | 3, // mov 3,r6
			(7 << 11) | (0x10 << 5) | 0, // mov 0,r7
			(8 << 11) | (0x10 << 5) | 4, // mov 4,r8
			(9 << 11) | (0x10 << 5) | 0, // mov 0,r9
			0, 0, 0, 0 };
		int[] j = jarl(at + 8, target, 31);
		words[4] = j[0];
		words[5] = j[1];
		int[] s2 = stw(2, storeDisp, 20);
		words[6] = s2[0];
		words[7] = s2[1];
		put(program, at, words);
	}

	/**
	 * Materializes an exact 32-bit constant into reg (movhi hi16,r0,reg;
	 * movea lo16,reg,reg; all 32-bit instructions, 4-byte aligned). 8 bytes.
	 */
	private long mat32(ProgramDB program, long at, int reg, int value) throws Exception {
		int hi = (value >>> 16) & 0xffff;
		int lo = value & 0xffff;
		// movea sign-extends its 16-bit immediate, so a high-bit lo16 must
		// borrow one unit from the movhi half (0x9abcdef0 -> movhi 0x9abd,
		// movea 0xdef0) or the materialized constant is off by 0x10000.
		if ((lo & 0x8000) != 0) {
			hi = (hi + 1) & 0xffff;
		}
		put(program, at, ((reg << 11) | (0x32 << 5)) & 0xffff, hi,
			((reg << 11) | (0x31 << 5) | reg) & 0xffff, lo);
		return at + 8;
	}

	/**
	 * One ABI-correct GCC shift site: a (r6/r7) and the count (r8) are
	 * rematerialized before EVERY call, because the real bodies mutate
	 * their argument registers (lshrdi3 writes r7, ashldi3 writes r6) and
	 * the fixup models those native clobbers; then jarl lp and both result
	 * words to the escaping slot pair 0x14000+slotDisp relative to the r20
	 * base. 36 bytes.
	 */
	private long gccShiftSite(ProgramDB program, long at, int aLow, int aHigh, int count,
			long target, int slotDisp) throws Exception {
		at = mat32(program, at, 6, aLow);
		at = mat32(program, at, 7, aHigh);
		at = mat32(program, at, 8, count);
		int[] j = jarl(at, target, 31);
		int[] s10 = stw(10, slotDisp, 20);
		int[] s11 = stw(11, slotDisp + 4, 20);
		put(program, at, j[0], j[1], s10[0], s10[1], s11[0], s11[1]);
		return at + 12;
	}
	/** Two calls deliberately share r7; each call's unchanged r6/r7 escape. */
	private void copyConsumer(ProgramDB program, long entry, long helper, int source,
			int destination, int slot) throws Exception {
		callerPrologue(program, entry);
		long at = mat32(program, entry + 20, 7, source);
		for (int i = 0; i < 2; i++) {
			at = mat32(program, at, 6, destination + i * 0x80);
			put(program, at, jarl(at, helper, 31));
			put(program, at + 4, stw(6, slot + i * 8, 20));
			put(program, at + 8, stw(7, slot + i * 8 + 4, 20));
			at += 12;
		}
		callerEpilogue(program, at);
	}


	/** 64-bit constant materializers for r6..r9: `mov imm5, reg` (format VIII,
	 * opcode bits 10:5 = 0x10). The imm5 is sign-extended, and reg1 r0
	 * supplies zero, so a=-1 loads both halves with mov -1 while b=0 loads
	 * mov 0. (0x12 would be ADD imm5, incrementing unknown entry registers
	 * at runtime, so the payloads could never fold to constants.) */
	private static final int[] NEG64_A = { 0x321f, 0x3a1f, 0x4000, 0x4800 }; // a=-1, b=0
	private static final int[] NEG64_B = { 0x3000, 0x3800, 0x421f, 0x4a1f }; // a=0, b=-1
	private static final int[] SEVEN = { 0x3207, 0x3a07, 0x4207, 0x4a07 };   // a=b=7

	private void buildFixtures(ProgramDB program) throws Exception {
		MemoryBlock flash = program.getMemory()
			.createInitializedBlock("flash", addr(program, 0x10000), 0x4000, (byte) 0, monitor,
				false);
		// Read + execute, never writable: the join-consistent CALLT
		// resolver only commits targets in executable memory, and a
		// read-only CALLT table passes the writable-memory trust check.
		flash.setPermissions(true, false, true);

		// Writable stack image for the machine-level runs (outside the
		// analyzed set: purely an execution resource for the consumers and
		// the real div/mod/mul dependency bodies).
		MemoryBlock stackImage = program.getMemory()
			.createInitializedBlock("stack", addr(program, 0x3f000), 0x1000, (byte) 0, monitor,
				false);
		stackImage.setPermissions(true, true, false);

		// --- GCC save/return pair (r29+lp) and callers ------------------
		// 0x10000: real consumer of the stripped save helper: jarl links
		// r10 (the helper returns through it), then the helper-adjusted sp
		// itself is stored to escaping RAM via the r20 data base (the
		// observable stack effect - a local dead store would be correctly
		// elided by the decompiler and prove nothing), r6 is spilled into
		// the freshly allocated frame and read back into the second
		// escaping slot (value round-trip), and the frame is dropped before
		// returning through the untouched lp.
		put(program, 0x10000, jarl(0x10000, 0x10100, 10));
		put(program, 0x10004, stw(3, 0x520, 20)); // st.w sp,0x520[r20]
		put(program, 0x10008, stw(6, 0x0, 3)); // st.w r6,0[sp]
		put(program, 0x1000c, ldw(7, 0x0, 3)); // ld.w 0[sp],r7
		put(program, 0x10010, stw(7, 0x524, 20)); // st.w r7,0x524[r20]
		put(program, 0x10014, 0x1e03, 0x0008); // addi 8,sp,sp
		put(program, 0x10018, 0x007f); // jmp [lp]
		// 0x10100: __save_r29_r31: addi -8,sp,sp; st.w r29,0[sp];
		//          st.w lp,4[sp]; jmp [r10]
		put(program, 0x10100, 0x1e03, 0xfff8);
		put(program, 0x10104, 0xef63, 0x0001);
		put(program, 0x10108, 0xff63, 0x0005);
		put(program, 0x1010c, 0x006a);
		// 0x10020: caller: jarl 0x10120,lp ; jmp [lp]
		put(program, 0x10020, jarl(0x10020, 0x10120, 31));
		put(program, 0x10024, 0x007f);
		// 0x10120: __return_r29: ld.w 0[sp],r29; add 4,sp; jmp [lp]
		// (one restored register: the stack adjust must be nregs*4 = 4)
		put(program, 0x10120, 0xef23, 0x0001);
		put(program, 0x10124, 0x1a44);
		put(program, 0x10126, 0x007f);

		// --- GHS save27 (dynamic-locals variant) and load27 -------------
		// 0x10200: __ghssave27
		put(program, 0x10200, 0x6003); // mov sp,r12
		put(program, 0x10202, 0x1a50); // add -16,sp
		put(program, 0x10204, 0xdf63, 0x0009); // st.w r27,8[sp]
		put(program, 0x10208, 0xe763, 0x0005); // st.w r28,4[sp]
		put(program, 0x1020c, 0xef63, 0x0001); // st.w r29,0[sp]
		put(program, 0x10210, 0xe80a); // mov r10,r29
		put(program, 0x10212, 0xff6c, 0xfffd); // st.w lp,-4[r12]
		put(program, 0x10216, 0x672a, 0xfffa); // ld.h -6[r10],r12
		put(program, 0x1021a, 0x66cc, 0xffff); // andi 0xffff,r12,r12
		put(program, 0x1021e, 0x62c2); // shl 2,r12
		put(program, 0x10220, 0x19ac); // sub r12,sp
		put(program, 0x10222, 0x006a); // jmp [r10]
		// 0x10230: __ghsload27
		put(program, 0x10230, 0x6202); // mov 2,r12
		put(program, 0x10232, 0xdf23, 0x0009); // ld.w 8[sp],r27
		put(program, 0x10236, 0xe723, 0x0005); // ld.w 4[sp],r28
		put(program, 0x1023a, 0xef23, 0x0001); // ld.w 0[sp],r29
		put(program, 0x1023e, 0x62c2); // shl 2,r12
		put(program, 0x10240, 0x19cc); // add r12,sp
		put(program, 0x10242, 0xff23, 0x0005); // ld.w 4[sp],lp
		put(program, 0x10246, 0x1a48); // add 8,sp
		put(program, 0x10248, 0x007f); // jmp [lp]
		// 0x103fe: dynamic locals halfword (word 2 -> 8 bytes), dead to flow.
		put(program, 0x103fe, 0x0002);
		// 0x10400: real consumer of the dynamic-locals save helper: jarl
		// links r10, the helper-adjusted sp (fixed 16 bytes plus 4*dynamic
		// word) is stored to escaping RAM via the r20 data base, r6 spills
		// into the allocated frame and round-trips to the second slot, and
		// the full 16+4*word frame is dropped before returning.
		put(program, 0x10400, jarl(0x10400, 0x10200, 10));
		put(program, 0x10404, stw(3, 0x528, 20)); // st.w sp,0x528[r20]
		put(program, 0x10408, stw(6, 0x0, 3)); // st.w r6,0[sp]
		put(program, 0x1040c, ldw(7, 0x0, 3)); // ld.w 0[sp],r7
		put(program, 0x10410, stw(7, 0x52c, 20)); // st.w r7,0x52c[r20]
		put(program, 0x10414, 0x1e03, 0x0018); // addi 24,sp,sp
		put(program, 0x10418, 0x007f); // jmp [lp]

		// --- GHS CALLT table and helpers ---------------------------------
		// 0x11000: callt table (16-bit offsets from table base).
		put(program, 0x11000, 0x0020); // entry 0 -> 0x11020
		put(program, 0x11002, 0x0028); // entry 1 -> 0x11028
		// 0x11020: ___ghssv4lp: prepare {lp},0 ; ctret  (8 bytes total)
		put(program, 0x11020, 0x0780, 0x0021, 0x07e0, 0x0144);
		// 0x11028: ___ghsld4lp: stsr ctpc,lp; ld.hu 0[lp],r12; add r12,sp;
		//          dispose 0,{lp},[lp]
		put(program, 0x11028, 0xfff0, 0x0040, 0x67ff, 0x0001, 0x19cc, 0x0640, 0x003f);
		// 0x10500: callt caller with CTBP setup: prepare {lp},0;
		// movhi 1,r0,r1; movea 0x1000,r1,r1; ldsr r1,ctbp; callt 0; jmp [lp]
		put(program, 0x10500, 0x0780, 0x0021, 0x0e40, 0x0001, 0x0e21, 0x1000, 0xa7e1, 0x0020,
			0x0200, 0x007f);
		// 0x10520: second callt caller with its own local CTBP setup (the
		// register analyzer's path-local dataflow resolves it): prepare
		// {lp},0; movhi/movea/ldsr ctbp; callt 1; <word>; jmp [lp]
		put(program, 0x10520, 0x0780, 0x0021, 0x0e40, 0x0001, 0x0e21, 0x1000, 0xa7e1, 0x0020,
			0x0201, 0x0002, 0x007f);
		// 0x10600: ABI-clobber CSE-independence witness (52 halfwords): two
		// IDENTICAL gh_add64 calls with identical finite constants. The
		// injected payload models the call's killed-register effects with
		// opaque __v850_abi_clobber user-ops; after each call the consumer
		// stores the killed scratch r2 to its own escaping slot. The two
		// clobbers are independent nondeterministic values: the decompiler
		// must keep two distinct CALLOTHER results and never CSE-equated
		// stores (the pre-fix payload wrote both stores from one shared
		// varnode - a false equality between independent calls).
		callerPrologue(program, 0x10600);
		clobberWitnessSite(program, 0x10614, 0x11500, 0x510);
		clobberWitnessSite(program, 0x10624, 0x11500, 0x514);
		callerEpilogue(program, 0x10634);

		// --- GHS 64-bit arithmetic helpers (name-established contracts) --
		long[] arith = { 0x11500, 0x11510, 0x11520, 0x11530, 0x11540, 0x11550, 0x11560, 0x11570,
			0x11580, 0x11590, 0x115a0 };
		String[] names = { "gh_add64", "gh_div64", "gh_udiv64", "gh_urem64", "gh_rem64",
			"gh_ult64", "gh_lt64", "gh_eq64", "gh_shra_64_32", "gh_mul64", "___gh_mul64o" };
		for (int i = 0; i < arith.length; i++) {
			put(program, arith[i], 0x007f); // jmp [lp]
		}
		// 0x11600: ABI-correct caller over the writable-data base calling
		// every named helper with a DISTINCT argument slot (gh_mul64 and
		// ___gh_mul64o share one a*b payload: identical arguments would let
		// the decompiler CSE the two folds into one INT_MULT) and storing
		// each result pair to its own escaping slot. 172 halfwords.
		callerPrologue(program, 0x11600);
		long at = 0x11614;
		for (int i = 0; i < arith.length; i++) {
			at = strippedCall(program, at, arith[i], i, i);
		}
		callerEpilogue(program, at);

		// --- Near-match negatives (must NOT be recognized) ---------------
		// 0x11800: mutated GCC save (lp stored at the wrong offset).
		put(program, 0x11800, 0x1e03, 0xfff8, 0xef63, 0x0001, 0xff63, 0x0009, 0x006a);
		// 0x11820: truncated GHS load (add 12,sp instead of add 8,sp).
		put(program, 0x11820, 0x6202, 0xdf23, 0x0009, 0xe723, 0x0005, 0xef23, 0x0001, 0x62c2,
			0x19cc, 0xff23, 0x0005, 0x1a4c, 0x007f);
		// 0x11860: arithmetic name near-miss.
		put(program, 0x11860, 0x007f);
		// 0x11880: caller E (ABI-correct, 32 halfwords): the real mulvdi3
		// body with variable arguments; the trapping call must survive.
		callerPrologue(program, 0x11880);
		strippedCall(program, 0x11894, 0x11e80, 41, 41);
		callerEpilogue(program, 0x118b0);

		// --- Stripped (default-named) 64-bit arithmetic recovery -----------
		// Bodies relocated verbatim from the pinned GCC 16.2.0 v850-elf
		// objects (libgcc and the freestanding -O2 helpers.o idioms) exercise
		// recognition on compiler-produced code.
		// Function names stay FUN_* (created without labels).
		// 0x11900: adddi3 (helpers.o _t_add): mov r8,r10; add r6,r10;
		//          cmp r6,r10; mov r7,r11; setf c,r6; add r9,r11;
		//          add r6,r11; jmp [lp]
		put(program, 0x11900, 0x5008, 0x51c6, 0x51e6, 0x5807, 0x37e1, 0x0000, 0x59c9, 0x59c6, 0x007f);
		// 0x11920: subdi3 (helpers.o _t_sub): mov r8,r10; subr r6,r10;
		//          cmp r6,r10; setf h,r11; sub r9,r7; subr r7,r11; jmp [lp]
		put(program, 0x11920, 0x5008, 0x5186, 0x51e6, 0x5feb, 0x0000, 0x39a9, 0x5987, 0x007f);
		// 0x11940: negdi2 (libgcc _negdi2.o).
		put(program, 0x11940, 0x5026, 0x5241, 0x37e1, 0x0000, 0x5827, 0x59c6, 0x007f);
		// 0x11960: lshrdi3 (libgcc _lshrdi3.o): dual-path variable shift.
		// 0x119a0: ashldi3, 0x119e0: ashrdi3 (same shape, other direction).
		put(program, 0x11960, 0x4260, 0x15f2, 0x5e20, 0x0020, 0x59a8, 0x5a60, 0x0dc7, 0x5006, 0x6007, 0x67eb, 0x00c0);
		put(program, 0x11976, 0x57e8, 0x0080, 0x3fe8, 0x0080, 0x510c, 0x5807, 0x007f, 0x5007, 0x3a00, 0x57e8, 0x0080);
		put(program, 0x1198c, 0x5807, 0x007f, 0x5006, 0x5807, 0x007f);
		put(program, 0x119a0, 0x4260, 0x15f2, 0x5620, 0x0020, 0x51a8, 0x5260, 0x0dc7, 0x5807, 0x6006, 0x67ea, 0x0080);
		put(program, 0x119b6, 0x5fe8, 0x00c0, 0x37e8, 0x00c0, 0x590c, 0x5006, 0x007f, 0x5806, 0x3200, 0x5fe8, 0x00c0);
		put(program, 0x119cc, 0x5006, 0x007f, 0x5006, 0x5807, 0x007f);
		put(program, 0x119e0, 0x4260, 0x15f2, 0x5e20, 0x0020, 0x59a8, 0x5a60, 0x0dc7, 0x5006, 0x6007, 0x67eb, 0x00c0);
		put(program, 0x119f6, 0x57e8, 0x0080, 0x5807, 0x5fe8, 0x00a0, 0x510c, 0x007f, 0x5807, 0x5007, 0x5abf, 0x57e8);
		put(program, 0x11a0c, 0x00a0, 0x007f, 0x5006, 0x5807, 0x007f);
		// 0x11a20: cmpdi2 / 0x11a40: ucmpdi2 (libgcc three-way compares).
		put(program, 0x11a20, 0x39e9, 0x05f2, 0x57ee, 0x0000, 0x37ef, 0x0000, 0x51c6, 0x007f, 0x31e8, 0x57e9, 0x0000);
		put(program, 0x11a36, 0x37eb, 0x0000, 0x51c6, 0x007f);
		put(program, 0x11a40, 0x39e9, 0x05aa, 0x31e8, 0x57e9, 0x0000, 0x37eb, 0x0000, 0x51c6, 0x007f);
		// 0x11a60: xor64 pair (exact GHS linear logic-pair idiom):
		// mov r6,r10; xor r8,r10; mov r7,r11; xor r9,r11; jmp [lp]
		put(program, 0x11a60, 0x5006, 0x5128, 0x5807, 0x5929, 0x007f);
		// 0x11a80: muldi3 (libgcc _muldi3.o, 9 mulh digits; tail-jumps to
		// the real GCC save/return helpers below).
		put(program, 0x11a80, 0x5780, 0x00e0, 0xe006, 0xe28f, 0x7620, 0x7fff, 0xe14e, 0x5008, 0x528f, 0x514e, 0x9806);
		put(program, 0x11a96, 0x9a9e, 0x6007, 0x62c2, 0x990c, 0x994e, 0x6808, 0x6a9e, 0x6009, 0x62c2, 0x690c, 0x694e);
		put(program, 0x11aac, 0x5807, 0x5a8d, 0x594e, 0xf809, 0xfa8d, 0xf94e, 0xe807, 0xea9c, 0xe94e, 0x6009, 0x629c);
		put(program, 0x11ac2, 0x614e, 0x314e, 0x414e, 0x7006, 0x70e8, 0x8006, 0x80ea, 0x9006, 0x90ed, 0x7806, 0x78ff);
		put(program, 0x11ad8, 0x30ec, 0x881c, 0x88ea, 0x601c, 0x60e8, 0x91d1, 0x881c, 0x88ff, 0x81cc, 0x601c, 0x60ed);
		put(program, 0x11aee, 0x31d1, 0x8813, 0x79cc, 0x6013, 0x60e8, 0x88ea, 0x91cc, 0x6013, 0x60ed, 0x79d1, 0x680b);
		put(program, 0x11b04, 0x68e8, 0x31cc, 0x600b, 0x60ea, 0x79cd, 0x40fd, 0x31cc, 0x6810, 0x6acf, 0x69ce, 0x6012);
		put(program, 0x11b1a, 0x62de, 0xd00d, 0xd1cc, 0x728f, 0x6640, 0x0002, 0x6e2c, 0xffff, 0x714d, 0x6010, 0x614d);
		put(program, 0x11b30, 0x71cc, 0x6012, 0x62cf, 0x614d, 0x71cc, 0x7291, 0x8291, 0x81ce, 0x7acd, 0x9282, 0x79d2);
		put(program, 0x11b46, 0x81cf, 0xd810, 0x31c8, 0x32dc, 0xd9c6, 0x501a, 0x581b, 0x0780, 0x002c);
		// 0x11b60: __save_r26_r31 and 0x11b80: __return_r26_r31 (real GCC
		// encodings from _save_26c.o, used by muldi3), 0x11ba0:
		// __return_r31 (from _save_31c.o, used by the *v family).
		put(program, 0x11b60, 0x1e03, 0xffec, 0xef63, 0x0001, 0xe763, 0x0005, 0xdf63, 0x0009, 0xd763, 0x000d, 0xff63);
		put(program, 0x11b76, 0x0011, 0x006a);
		put(program, 0x11b80, 0xef23, 0x0001, 0xe723, 0x0005, 0xdf23, 0x0009, 0xd723, 0x000d, 0xff23, 0x0011, 0x1e03);
		put(program, 0x11b96, 0x0014, 0x007f);
		put(program, 0x11ba0, 0xff23, 0x0001, 0x1e03, 0x0004, 0x007f);
		// 0x11bb0: addvdi3 (libgcc _addvdi3.o): carry-add core + xor-based
		// signed-overflow test + blt to the abort call + return-r31 tail.
		put(program, 0x11bb0, 0x5008, 0x1a5c, 0x51c6, 0x51e6, 0x5807, 0x37e1, 0x0000, 0x59c9, 0x3929, 0x59c6, 0x492b);
		put(program, 0x11bc6, 0x3827, 0x4947, 0x4a60, 0xff63, 0x0001, 0x05b6, 0x07bf, 0xffce, 0xff80, 0x028a);
		// 0x11be0: subvdi3 and 0x11c10: negvdi2 (libgcc overflow-checked
		// family; both keep the abort() control flow).
		put(program, 0x11be0, 0x5008, 0x1a5c, 0x5186, 0x51e6, 0x5807, 0x37eb, 0x0000, 0x59a9, 0x59a6, 0x600b, 0x6129);
		put(program, 0x11bf6, 0x3929, 0x602c, 0x394c, 0x3a60, 0xff63, 0x0001, 0x05b6, 0x07bf, 0xff9c, 0xff80, 0x0258);
		put(program, 0x11c10, 0x1a5c, 0x3260, 0x5807, 0x6fea, 0x0000, 0x5006, 0x5980, 0x5180, 0x59ad, 0x3260, 0xff63);
		put(program, 0x11c26, 0x0001, 0x6200, 0x05d2, 0x6260, 0x0d9a, 0x07bf, 0xff70, 0x6e40, 0x8000, 0x39ed, 0xfd9a);
		put(program, 0x11c3c, 0x6201, 0xf5f5, 0xff80, 0x0220);

		// --- ABI-correct callers of the stripped helpers ------------------
		// 0x11c60: caller A (102 halfwords): add64, sub64, negdi2 and the
		// three trapping *v helpers; every call reloads its arguments from
		// writable memory and stores results to distinct escaping slots.
		callerPrologue(program, 0x11c60);
		at = strippedCall(program, 0x11c74, 0x11900, 24, 24);
		at = strippedCall(program, at, 0x11920, 25, 25);
		at = strippedCall(program, at, 0x11940, 26, 26);
		at = strippedCall(program, at, 0x11bb0, 27, 27);
		at = strippedCall(program, at, 0x11be0, 28, 28);
		at = strippedCall(program, at, 0x11c10, 29, 29);
		callerEpilogue(program, at);
		// 0x11d40: caller B (60 halfwords): the dual-path variable shifts.
		callerPrologue(program, 0x11d40);
		at = strippedCall(program, 0x11d54, 0x11960, 30, 30);
		at = strippedCall(program, at, 0x119a0, 31, 31);
		at = strippedCall(program, at, 0x119e0, 32, 32);
		callerEpilogue(program, at);
		// 0x11dc0: caller C (74 halfwords): compares, logic pair, muldi3.
		callerPrologue(program, 0x11dc0);
		at = strippedCall(program, 0x11dd4, 0x11a20, 33, 33);
		at = strippedCall(program, at, 0x11a40, 34, 34);
		at = strippedCall(program, at, 0x11a60, 35, 35);
		at = strippedCall(program, at, 0x11a80, 36, 36);
		callerEpilogue(program, at);
		// 0x11e60: abort() cold stub (br .): a real named function so the
		// *v bodies' _abort bindings validate against it.
		put(program, 0x11e60, 0x0585);
		// 0x11e80: mulvdi3 (libgcc _mulvdi3.o, 184 halfwords): calls the
		// real ___muldi3 body, tail-jumps to the real __return_r24_r31,
		// and keeps the abort() overflow path.
		put(program, 0x11e80, 0x6006, 0x5008, 0x1e03, 0xffe4, 0x62bf, 0x52bf, 0xd763, 0x000d, 0xdf63, 0x0009, 0xe763);
		put(program, 0x11e96, 0x0005, 0xef63, 0x0001, 0x61e7, 0xff63, 0x0019, 0xc763, 0x0015, 0xcf63, 0x0011, 0xd006);
		put(program, 0x11eac, 0xd808, 0xe007, 0xe809, 0x05fa, 0x51e9, 0x35da, 0xffbf, 0xfbc8, 0x0780, 0x0304, 0x51e9);
		put(program, 0x11ec2, 0x5dfa, 0xc640, 0x0001, 0xc638, 0x1a80, 0x4a00, 0x3a00, 0xff80, 0x0004, 0xfa44, 0x0078);
		put(program, 0x11ed8, 0x401b, 0x4a00, 0x301c, 0x3a00, 0xe80a, 0xc80b, 0xff80, 0x0004, 0xfa44, 0x0078, 0xe260);
		put(program, 0x11eee, 0x600a, 0x680b, 0x05ae, 0x69bb, 0xda60, 0x0d8e, 0x601a, 0x618a, 0x61ea, 0x57eb, 0x0000);
		put(program, 0x11f04, 0x69bc, 0x69aa, 0x580c, 0x59d9, 0x59f9, 0xcfe1, 0x0000, 0x500b, 0xc9cd, 0x52bf, 0x51f9);
		put(program, 0x11f1a, 0x458a, 0x501d, 0xcdf5, 0xc640, 0x0001, 0x4006, 0xc638, 0x1a80, 0x4a00, 0x301b, 0x3a00);
		put(program, 0x11f30, 0xff80, 0x0004, 0xfa44, 0x0078, 0x401a, 0x4a00, 0x301d, 0x3a00, 0xe00a, 0xc80b, 0xff80);
		put(program, 0x11f46, 0x0004, 0xfa44, 0x0078, 0xea60, 0x680a, 0x600b, 0x05ae, 0x61ba, 0xd260, 0x0d8e, 0x681b);
		put(program, 0x11f5c, 0x698a, 0x69ea, 0x57eb, 0x0000, 0x61bd, 0x61aa, 0x580d, 0x59d9, 0x59f9, 0xcfe1, 0x0000);
		put(program, 0x11f72, 0x500b, 0xc9cc, 0x52bf, 0x51f9, 0x158a, 0x501c, 0x9df5, 0x3a60, 0x0de6, 0x4a60, 0x1d86);
		put(program, 0x11f88, 0xe907, 0xea60, 0x05fa, 0x4a00, 0x3a00, 0xffbf, 0xfaee, 0x5a60, 0x95ae, 0xffbf, 0xfec6);
		put(program, 0x11f9e, 0x4a60, 0x15f6, 0x3a7f, 0xfdba, 0x4a60, 0xfd9a, 0x3a00, 0xffbf, 0xfad4, 0x59bb, 0x85d4);
		put(program, 0x11fb4, 0xf5b5, 0x3a60, 0xf59a, 0x4a7f, 0xedfa, 0x4a00, 0xffbf, 0xfac0, 0x59ba, 0x05bc, 0x07bf);
		put(program, 0x11fca, 0xfef4, 0xe5f5, 0xe947, 0xea7f, 0xe5ca, 0x5008, 0x5106, 0x5260, 0xe582, 0x4a00, 0x3a00);
		put(program, 0x11fe0, 0xffbf, 0xfaa0, 0x59ba, 0x59bb, 0x05b4, 0x07bf, 0xfed2, 0xd5e5);

		// --- Real div/mod dependency data + stripped div/mod/mul recovery --
		// 0x12000: ___clz_tab: the GCC libgcc2 constant table exactly as
		// defined by L_clz (libgcc2.c) and committed in the templates
		// catalog: t[0] = 0 and t[i] = bit length of i
		// (1,2,2,3,3,3,3, ... ,8 for 128..255) - NOT floor(log2).
		byte[] clzTab = new byte[256];
		for (int i = 1; i < 256; i++) {
			clzTab[i] = (byte) (32 - Integer.numberOfLeadingZeros(i));
		}
		program.getMemory().setBytes(addr(program, 0x12000), clzTab);
		// 0x12100: ___udivsi3, 0x12140: ___umodsi3, 0x12180: ___mulsi3 and
		// 0x121c0: __return_r24_r31, 0x12200: __return_r20_r31: the real
		// GCC 16.2 libgcc dependency bodies relocated verbatim from the
		// committed _udivsi3.o / _umodsi3.o / _mulsi3.o / _save_24c.o /
		// _save_20c.o objects (the div bodies call/tail-call them through
		// movhi/movea pairs and the jarl .+4,lp / add 4,lp / jmp rX idiom).
		put(program, 0x12100, 0x6201, 0x5200, 0x39e6, 0x15d9, 0x6e40, 0x8000, 0x39e0, 0x1596, 0x3ac1, 0x62c1, 0x39e6);
		put(program, 0x12116, 0x0dd9, 0x61e0, 0x0dd2, 0x9807, 0x994d, 0xfd82, 0x05f5, 0x31e7, 0x05b1, 0x31a7, 0x510c);
		put(program, 0x1212c, 0x6281, 0x3a81, 0x61e0, 0xfd9a, 0x007f);
		put(program, 0x12140, 0x1a54, 0xff63, 0x0009, 0x3f63, 0x0005, 0x3763, 0x0001, 0xffbf, 0xffb2, 0x3f23, 0x0005);
		put(program, 0x12156, 0x300a, 0xff80, 0x0028, 0x3723, 0x0001, 0x5186, 0xff23, 0x0009, 0x1a4c, 0x007f);
		put(program, 0x12180, 0x7006, 0x5620, 0x7fff, 0x714a, 0x7807, 0x794a, 0x328f, 0x6806, 0x694a, 0x3a8f, 0x6007);
		put(program, 0x12196, 0x614a, 0x328f, 0x3a8f, 0x500e, 0x50ef, 0x580e, 0x58ec, 0x800d, 0x80ef, 0x38ee, 0x30ef);
		put(program, 0x121ac, 0x59d0, 0x60ed, 0x5acf, 0x51cb, 0x39cc, 0x39c6, 0x3ade, 0x51c7, 0x007f);
		put(program, 0x121c0, 0xef23, 0x0001, 0xe723, 0x0005, 0xdf23, 0x0009, 0xd723, 0x000d, 0xcf23, 0x0011, 0xc723);
		put(program, 0x121d6, 0x0015, 0xff23, 0x0019, 0x1e03, 0x001c, 0x007f);
		put(program, 0x12200, 0xef23, 0x0001, 0xe723, 0x0005, 0xdf23, 0x0009, 0xd723, 0x000d, 0xcf23, 0x0011, 0xc723);
		put(program, 0x12216, 0x0015, 0xbf23, 0x0019, 0xb723, 0x001d, 0xaf23, 0x0021, 0xa723, 0x0025, 0xff23, 0x0029);
		put(program, 0x1222c, 0x1e03, 0x002c, 0x007f);
		// 0x12240: ___divdi3 and 0x128e0: ___umoddi3, relocated verbatim
		// from the committed _divdi3.o / _umoddi3.o objects with their
		// R_V810_WHI1/WLO and R_V850_PCR22 relocations rewritten to the
		// fixture addresses above (validated byte-for-byte against the
		// objects by the fixture generator).
		put(program, 0x12240, 0x1e03, 0xffd4, 0xa763, 0x0025, 0xe763, 0x0005, 0xef63, 0x0001, 0xff63, 0x0029, 0xaf63);
		put(program, 0x12256, 0x0021, 0xb763, 0x001d, 0xbf63, 0x0019, 0xc763, 0x0015, 0xcf63, 0x0011, 0xd763, 0x000d);
		put(program, 0x1226c, 0xdf63, 0x0009, 0x1a50, 0x3a60, 0xe803, 0xe007, 0xa006, 0x05be, 0x0780, 0x02ee, 0xda00);
		put(program, 0x12282, 0x4a60, 0x0d8e, 0x4260, 0x57ea, 0x0000, 0x4980, 0xd83b, 0x49aa, 0x4180, 0x4a60, 0xa808);
		put(program, 0x12298, 0xd014, 0xc81c, 0x05b2, 0x0780, 0x0130, 0x41fc, 0x05bb, 0x0780, 0x01a4, 0x5640, 0x0001);
		put(program, 0x122ae, 0x41ea, 0x05b9, 0x0780, 0x02ca, 0x5640, 0x0100, 0x41ea, 0x05b1, 0x0780, 0x05cc, 0x6620);
		put(program, 0x122c4, 0x0010, 0x5008, 0x5e40, 0x0001, 0x57ec, 0x0080, 0x5e2b, 0x2000, 0x51cb, 0x570a, 0x0000);
		put(program, 0x122da, 0x6e20, 0x0020, 0x56ca, 0x00ff, 0x51cc, 0x600d, 0x61aa, 0x69ea, 0x0dd2, 0xc814, 0xe7ec);
		put(program, 0x122f0, 0x00c0, 0xcfea, 0x0080, 0x47ec, 0x00c0, 0xd014, 0xa808, 0xc91c, 0xd7ec, 0x00c0, 0xb815);
		put(program, 0x12306, 0xba90, 0x6640, 0x0001, 0x662c, 0x2140, 0x3019, 0x3817, 0x677d, 0x000d, 0xc640, 0x0001);
		put(program, 0x1231c, 0xff80, 0x0004, 0xfa44, 0x006c, 0x3019, 0x3817, 0xc638, 0x2100, 0xb6d5, 0xffff, 0xa00a);
		put(program, 0x12332, 0xce40, 0x0001, 0xff80, 0x0004, 0xfa44, 0x0078, 0x3016, 0xce39, 0x2180, 0x380a, 0xe00a);
		put(program, 0x12348, 0xff80, 0x0004, 0xfa44, 0x0079, 0x3014, 0x581a, 0x32d0, 0x5a90, 0x310b, 0x51e6, 0x673d);
		put(program, 0x1235e, 0x000d, 0x0db3, 0x31d5, 0x5e1c, 0xffff, 0xa9e6, 0x05db, 0x51e6, 0x05b3, 0x0780, 0x0554);
		put(program, 0x12374, 0xe00b, 0x31aa, 0x3817, 0x377d, 0x000d, 0xff80, 0x0004, 0xfa44, 0x006c, 0x373d, 0x000d);
		put(program, 0x1238a, 0x3817, 0xb80a, 0xff80, 0x0004, 0xfa44, 0x0078, 0xbad0, 0xd6da, 0xffff, 0x380a, 0x3016);
		put(program, 0x123a0, 0xc00a, 0xd117, 0xff80, 0x0004, 0xfa44, 0x0079, 0x51fa, 0x0db3, 0xd1d5, 0x5e18, 0xffff);
		put(program, 0x123b6, 0xa9fa, 0x05db, 0x51fa, 0x05b3, 0x0780, 0x04f8, 0xc00b, 0x501c, 0x52d0, 0x5118, 0xba00);
		put(program, 0x123cc, 0x05d5, 0x49fc, 0x1593, 0xba00, 0x5200, 0xda60, 0x5817, 0x05f2, 0x5260, 0x67ea, 0x0000);
		put(program, 0x123e2, 0x5980, 0x59ac, 0x5180, 0x181d, 0x1e03, 0x0010, 0x07bf, 0xfe12, 0x5640, 0x0001, 0x49ea);
		put(program, 0x123f8, 0x05b9, 0x0780, 0x01ac, 0x5640, 0x0100, 0x49ea, 0x05b1, 0x0780, 0x047c, 0x6620, 0x0010);
		put(program, 0x1240e, 0x5009, 0x5e40, 0x0001, 0x57ec, 0x0080, 0x5e2b, 0x2000, 0x51cb, 0x570a, 0x0000, 0x6e20);
		put(program, 0x12424, 0x0020, 0x56ca, 0x00ff, 0x51cc, 0xd00d, 0xd1aa, 0x69ea, 0x05b2, 0x0780, 0x028c, 0x49fc);
		put(program, 0x1243a, 0x05b9, 0x0780, 0x0456, 0x41f4, 0x57e3, 0x0000, 0xba00, 0xc5f5, 0x4260, 0x05ba, 0x0780);
		put(program, 0x12450, 0x013e, 0x5640, 0x0001, 0x41ea, 0x05b1, 0x0780, 0x0410, 0xc640, 0x0001, 0xc638, 0x2100);
		put(program, 0x12466, 0x6620, 0x00ff, 0xa9ec, 0x67eb, 0x0000, 0x62c3, 0x5015, 0x5e40, 0x0001, 0x57ec, 0x0080);
		put(program, 0x1247c, 0x5e2b, 0x2000, 0x51cb, 0x570a, 0x0000, 0x6e20, 0x0020, 0x56ca, 0x00ff, 0x51cc, 0x700d);
		put(program, 0x12492, 0x71aa, 0x69ea, 0x05b2, 0x0780, 0x011e, 0xb015, 0x6640, 0x0001, 0xce40, 0x0001, 0xe1b5);
		put(program, 0x124a8, 0xb290, 0xa6d5, 0xffff, 0xba01, 0x662c, 0x2140, 0xce39, 0x2180, 0x301c, 0x3816, 0x677d);
		put(program, 0x124be, 0x0009, 0xff80, 0x0004, 0xfa44, 0x006c, 0x301c, 0x3816, 0x577d, 0x000d, 0xff80, 0x0004);
		put(program, 0x124d4, 0xfa44, 0x0078, 0x300a, 0x3814, 0xe00a, 0xff80, 0x0004, 0xfa44, 0x0079, 0x5f3d, 0x000d);
		put(program, 0x124ea, 0x673d, 0x0009, 0x5ad0, 0x300b, 0x581a, 0x5a90, 0x310b, 0x51e6, 0x0db3, 0x31d5, 0x5e1c);
		put(program, 0x12500, 0xffff, 0xa9e6, 0x05db, 0x51e6, 0x05b3, 0x0780, 0x03b2, 0xe00b, 0x31aa, 0x3816, 0x377d);
		put(program, 0x12516, 0x000d, 0xff80, 0x0004, 0xfa44, 0x006c, 0x373d, 0x000d, 0x3816, 0xb00a, 0xff80, 0x0004);
		put(program, 0x1252c, 0xfa44, 0x0078, 0x3814, 0x300a, 0xc00a, 0xff80, 0x0004, 0xfa44, 0x0079, 0x5816, 0x5ad0);
		put(program, 0x12542, 0xd6da, 0xffff, 0x591a, 0x51eb, 0x0db3, 0x59d5, 0x6618, 0xffff, 0xa9eb, 0x05db, 0x51eb);
		put(program, 0x12558, 0x05b3, 0x0780, 0x0356, 0xc00c, 0x501c, 0x52d0, 0x5118, 0x07bf, 0xfe70, 0x3260, 0x57ea);
		put(program, 0x1256e, 0x0000, 0xe180, 0xe1aa, 0xa180, 0xda1f, 0x07bf, 0xfd0a, 0x6620, 0x00ff, 0x41ec, 0x67eb);
		put(program, 0x12584, 0x0000, 0x62c3, 0x07bf, 0xfd3e, 0xc640, 0x0001, 0xc638, 0x2100, 0x3a00, 0x3201, 0xff80);
		put(program, 0x1259a, 0x0004, 0xfa44, 0x0078, 0xa80a, 0x07bf, 0xfec4, 0x6620, 0x00ff, 0x49ec, 0x67eb, 0x0000);
		put(program, 0x125b0, 0x62c3, 0x07bf, 0xfe5c, 0xafee, 0x00c0, 0xc81c, 0xb015, 0xcfea, 0x0080, 0xb290, 0x681c);
		put(program, 0x125c6, 0x6640, 0x0001, 0xe014, 0x6fee, 0x00c0, 0x662c, 0x2140, 0xe7ea, 0x0080, 0x3019, 0x3816);
		put(program, 0x125dc, 0xd014, 0xe10d, 0xd7ee, 0x00c0, 0x677d, 0x0009, 0xff80, 0x0004, 0xfa44, 0x006c, 0x3019);
		put(program, 0x125f2, 0x3816, 0xa6d5, 0xffff, 0xb80a, 0xce40, 0x0001, 0xff80, 0x0004, 0xfa44, 0x0078, 0x3014);
		put(program, 0x12608, 0xce39, 0x2180, 0x380a, 0x577d, 0x000d, 0xff80, 0x0004, 0xfa44, 0x0079, 0x3017, 0x681c);
		put(program, 0x1261e, 0x32d0, 0x6a90, 0x310d, 0x51e6, 0x5f3d, 0x000d, 0x673d, 0x0009, 0x0de3, 0x31d5, 0x6e0b);
		put(program, 0x12634, 0xffff, 0xa9e6, 0x05b3, 0x0780, 0x0270, 0x51e6, 0x05bb, 0x0780, 0x0268, 0x5a5e, 0x31d5);
		put(program, 0x1264a, 0x31aa, 0x3816, 0x5f7d, 0x0005, 0x677d, 0x0009, 0x377d, 0x000d, 0xff80, 0x0004, 0xfa44);
		put(program, 0x12660, 0x006c, 0x373d, 0x000d, 0x3816, 0xb80a, 0xff80, 0x0004, 0xfa44, 0x0078, 0x380a, 0xbad0);
		put(program, 0x12676, 0xe6dc, 0xffff, 0x3014, 0xe117, 0x577d, 0x000d, 0xff80, 0x0004, 0xfa44, 0x0079, 0x51fc);
		put(program, 0x1268c, 0x3f3d, 0x000d, 0x673d, 0x0009, 0x5f3d, 0x0005, 0x0de3, 0xe1d5, 0x6e07, 0xffff, 0xa9fc);
		put(program, 0x126a2, 0x05b3, 0x0780, 0x01fa, 0x51fc, 0x05bb, 0x0780, 0x01f2, 0x3a5e, 0xe1d5, 0x5ad0, 0x5907);
		put(program, 0x126b8, 0xe1aa, 0xb80b, 0x07bf, 0xfdfc, 0x7008, 0x4ffa, 0x00c0, 0x77ea, 0x0080, 0x7109, 0xb80e);
		put(program, 0x126ce, 0xc81c, 0xcfea, 0x0080, 0xba90, 0x6640, 0x0001, 0xa814, 0x662c, 0x2140, 0x47fa, 0x00c0);
		put(program, 0x126e4, 0xafea, 0x0080, 0x3019, 0x56ce, 0xffff, 0x3817, 0x777d, 0x0001, 0x677d, 0x0005, 0xb008);
		put(program, 0x126fa, 0xc640, 0x0001, 0x577d, 0x000d, 0xff80, 0x0004, 0xfa44, 0x006c, 0x3019, 0x3817, 0xc638);
		put(program, 0x12710, 0x2100, 0x577d, 0x0009, 0xff80, 0x0004, 0xfa44, 0x0078, 0x373d, 0x000d, 0xce40, 0x0001);
		put(program, 0x12726, 0xe7fa, 0x00c0, 0xce39, 0x2180, 0x380a, 0xa91c, 0xe00a, 0xff80, 0x0004, 0xfa44, 0x0079);
		put(program, 0x1273c, 0x6f3d, 0x0009, 0x673d, 0x0005, 0x6ad0, 0x300d, 0x6815, 0x6a90, 0x310d, 0x51e6, 0x773d);
		put(program, 0x12752, 0x0001, 0x0de3, 0x31ce, 0x6e1c, 0xffff, 0x71e6, 0x05b3, 0x0780, 0x0144, 0x51e6, 0x05bb);
		put(program, 0x12768, 0x0780, 0x013c, 0xe25e, 0x31ce, 0x31aa, 0x3817, 0x777d, 0x0005, 0x377d, 0x0009, 0xff80);
		put(program, 0x1277e, 0x0004, 0xfa44, 0x006c, 0x373d, 0x0009, 0x3817, 0xb80a, 0xff80, 0x0004, 0xfa44, 0x0078);
		put(program, 0x12794, 0x373d, 0x000d, 0xbad0, 0xaed5, 0xffff, 0x380a, 0xc00a, 0xa917, 0xff80, 0x0004, 0xfa44);
		put(program, 0x127aa, 0x0079, 0x51f5, 0x600a, 0x0dc3, 0x773d, 0x0005, 0x5618, 0xffff, 0xa9ce, 0x71f5, 0x6deb);
		put(program, 0x127c0, 0x61f5, 0x6dc3, 0xc25e, 0xa9ce, 0x501c, 0x6ed8, 0xffff, 0x52d0, 0x3ed6, 0xffff, 0x5118);
		put(program, 0x127d6, 0x300d, 0xa9ac, 0x6f7d, 0x0009, 0xb80a, 0x3f7d, 0x000d, 0xe00a, 0xff80, 0x0004, 0xfa44);
		put(program, 0x127ec, 0x0079, 0xba90, 0x3f3d, 0x000d, 0x3017, 0xb290, 0x577d, 0x000d, 0xff80, 0x0004, 0xfa44);
		put(program, 0x12802, 0x0079, 0x3017, 0x3816, 0xc00a, 0xff80, 0x0004, 0xfa44, 0x0079, 0x6f3d, 0x0009, 0x3816);
		put(program, 0x12818, 0x300d, 0xb80a, 0xff80, 0x0004, 0xfa44, 0x0079, 0x5f3d, 0x000d, 0x51d8, 0x600b, 0x6290);
		put(program, 0x1282e, 0x61ca, 0xc1ec, 0x05c3, 0x5640, 0x0001, 0xb9ca, 0x500c, 0x5290, 0x51d7, 0xa9ea, 0x0df1);
		put(program, 0x12844, 0x05d2, 0x501c, 0xba00, 0x07bf, 0xfb8c, 0x56cb, 0xffff, 0x62d0, 0x5814, 0x5ffa, 0x00c0);
		put(program, 0x1285a, 0x61ca, 0x59ec, 0xf5c9, 0x561c, 0xffff, 0xba00, 0x07bf, 0xfb70, 0x5640, 0x0100, 0x41ea);
		put(program, 0x12870, 0x2de9, 0xc640, 0x0001, 0x6620, 0x0010, 0xc638, 0x2100, 0x07bf, 0xfbf4, 0x6620, 0x0018);
		put(program, 0x12886, 0x07bf, 0xfb88, 0x6620, 0x0018, 0x07bf, 0xfa38, 0xba00, 0x5201, 0x07bf, 0xfb40, 0xc00a);
		put(program, 0x1289c, 0x95e5, 0x380d, 0x07bf, 0xfe14, 0xe00d, 0x07bf, 0xfeca, 0x580d, 0x07bf, 0xfd9e, 0xc25e);
		put(program, 0x128b2, 0x07bf, 0xfcae, 0xc25e, 0x07bf, 0xfb0c, 0xe25e, 0x31d5, 0x07bf, 0xfc50, 0xe25e, 0x31d5);
		put(program, 0x128c8, 0x07bf, 0xfaae, 0xc640, 0x0001, 0x6620, 0x0018, 0xc638, 0x2100, 0x07bf, 0xfb9a);
		put(program, 0x128e0, 0x1e03, 0xffd4, 0xbf63, 0x0019, 0xc763, 0x0015, 0xd763, 0x000d, 0xe763, 0x0005, 0xef63);
		put(program, 0x128f6, 0x0001, 0xff63, 0x0029, 0xa763, 0x0025, 0xaf63, 0x0021, 0xb763, 0x001d, 0xcf63, 0x0011);
		put(program, 0x1290c, 0xdf63, 0x0009, 0x1a54, 0x4a60, 0xc006, 0xd006, 0xe803, 0xe007, 0xb808, 0x6007, 0x3007);
		put(program, 0x12922, 0x7d8a, 0x41e7, 0x05bb, 0x0780, 0x0164, 0x5640, 0x0001, 0x41ea, 0x05b9, 0x0780, 0x0258);
		put(program, 0x12938, 0x5640, 0x0100, 0x41ea, 0x05b1, 0x0780, 0x0526, 0x5e20, 0x0010, 0x5008, 0x6640, 0x0001);
		put(program, 0x1294e, 0x57eb, 0x0080, 0x662c, 0x2000, 0x51cc, 0x570a, 0x0000, 0x6620, 0x0020, 0x56ca, 0x00ff);
		put(program, 0x12964, 0x51cb, 0xd80c, 0xd9aa, 0x61ea, 0x0dd2, 0x3018, 0xe7fb, 0x00c0, 0x37ea, 0x0080, 0x47fb);
		put(program, 0x1297a, 0x00c0, 0xd018, 0xb808, 0x311c, 0xd7fb, 0x00c0, 0xa817, 0xaa90, 0xa640, 0x0001, 0x3815);
		put(program, 0x12990, 0xa634, 0x2140, 0x377d, 0x0009, 0xff80, 0x0004, 0xfa44, 0x0074, 0x373d, 0x0009, 0xce40);
		put(program, 0x129a6, 0x0001, 0x3815, 0xce39, 0x2100, 0xb6d7, 0xffff, 0xe00a, 0xc640, 0x0001, 0xff80, 0x0004);
		put(program, 0x129bc, 0xfa44, 0x0079, 0x3016, 0xc638, 0x2180, 0x380a, 0xff80, 0x0004, 0xfa44, 0x0078, 0x301c);
		put(program, 0x129d2, 0x581a, 0x32d0, 0x5a90, 0x310b, 0x51e6, 0x05f3, 0x31d7, 0xb9e6, 0x05cb, 0x51e6, 0x05a3);
		put(program, 0x129e8, 0x31d7, 0x31aa, 0x3815, 0x377d, 0x0009, 0xff80, 0x0004, 0xfa44, 0x0074, 0x373d, 0x0009);
		put(program, 0x129fe, 0x3815, 0xe00a, 0xff80, 0x0004, 0xfa44, 0x0079, 0x380a, 0x3016, 0x0780, 0x014c, 0x49e7);
		put(program, 0x12a14, 0x7018, 0x05f3, 0x181d, 0x1a4c, 0x5018, 0x5807, 0x07bf, 0xf7e0, 0x5640, 0x0001, 0x49ea);
		put(program, 0x12a2a, 0x05b9, 0x0780, 0x018a, 0x5640, 0x0100, 0x49ea, 0x05b1, 0x0780, 0x0426, 0x5620, 0x0010);
		put(program, 0x12a40, 0x5809, 0x6e40, 0x0001, 0x5fea, 0x0080, 0x6e2d, 0x2000, 0x59cd, 0x6f0b, 0x0000, 0x5e20);
		put(program, 0x12a56, 0x0020, 0x6ecd, 0x00ff, 0x69ca, 0xb80b, 0xb9ad, 0x59ed, 0x05b2, 0x0780, 0x0230, 0x49fc);
		put(program, 0x12a6c, 0x05b1, 0x41f8, 0x0d8b, 0x7008, 0x499c, 0x7198, 0xc1ee, 0x67e1, 0x0000, 0x6189, 0x181d);
		put(program, 0x12a82, 0x1a4c, 0x500e, 0x580c, 0x07bf, 0xf778, 0x4260, 0x05ba, 0x0780, 0x010c, 0x5640, 0x0001);
		put(program, 0x12a98, 0x41ea, 0x05b1, 0x0780, 0x03d2, 0xce40, 0x0001, 0xce39, 0x2100, 0x5e20, 0x00ff, 0xb9eb);
		put(program, 0x12aae, 0x5feb, 0x0000, 0x5ac3, 0x5017, 0x6640, 0x0001, 0x57eb, 0x0080, 0x662c, 0x2000, 0x51cc);
		put(program, 0x12ac4, 0x570a, 0x0000, 0x6620, 0x0020, 0x56ca, 0x00ff, 0x51cb, 0xd80c, 0xd9aa, 0x61ea, 0x75fa);
		put(program, 0x12ada, 0xb017, 0xa640, 0x0001, 0xc640, 0x0001, 0xe1b7, 0xb290, 0xaed7, 0xffff, 0xa634, 0x2140);
		put(program, 0x12af0, 0xc638, 0x2180, 0x301c, 0x3816, 0xff80, 0x0004, 0xfa44, 0x0074, 0x301c, 0x3816, 0xe00a);
		put(program, 0x12b06, 0xff80, 0x0004, 0xfa44, 0x0079, 0x300a, 0x3815, 0xff80, 0x0004, 0xfa44, 0x0078, 0x301c);
		put(program, 0x12b1c, 0x581a, 0x32d0, 0x5a90, 0x310b, 0x51e6, 0x0d83, 0x31d7, 0xb9e6, 0x05db, 0x51e6, 0x05b3);
		put(program, 0x12b32, 0x0780, 0x035e, 0x31aa, 0x3816, 0x377d, 0x0009, 0xff80, 0x0004, 0xfa44, 0x0074, 0x373d);
		put(program, 0x12b48, 0x0009, 0x3816, 0xe00a, 0xff80, 0x0004, 0xfa44, 0x0079, 0x3815, 0x300a, 0xff80, 0x0004);
		put(program, 0x12b5e, 0xfa44, 0x0078, 0x581c, 0x5ad0, 0xd6da, 0xffff, 0x591a, 0x51eb, 0x05f3, 0x59d7, 0xb9eb);
		put(program, 0x12b74, 0x05cb, 0x51eb, 0x05a3, 0x59d7, 0x181d, 0x518b, 0x1a4c, 0x57fb, 0x0080, 0x5a00, 0x07bf);
		put(program, 0x12b8a, 0xf678, 0x5e20, 0x00ff, 0x41eb, 0x5feb, 0x0000, 0x5ac3, 0x07bf, 0xfdb0, 0xce40, 0x0001);
		put(program, 0x12ba0, 0xce39, 0x2100, 0x3a00, 0x3201, 0xff80, 0x0004, 0xfa44, 0x0079, 0xb80a, 0x07bf, 0xfef6);
		put(program, 0x12bb6, 0x5620, 0x00ff, 0x49ea, 0x57eb, 0x0000, 0x52c3, 0x07bf, 0xfe7e, 0xbffb, 0x00c0, 0xb017);
		put(program, 0x12bcc, 0xb290, 0x301c, 0x581c, 0xa640, 0x0001, 0xe018, 0x5ffb, 0x00c0, 0x37ea, 0x0080, 0xe7ea);
		put(program, 0x12be2, 0x0080, 0x3816, 0xa634, 0x2140, 0xe10b, 0x377d, 0x0009, 0xff80, 0x0004, 0xfa44, 0x0074);
		put(program, 0x12bf8, 0x373d, 0x0009, 0x3816, 0xd018, 0xaed7, 0xffff, 0xc640, 0x0001, 0x577d, 0x0009, 0xff80);
		put(program, 0x12c0e, 0x0004, 0xfa44, 0x0079, 0x3015, 0xc638, 0x2180, 0x380a, 0xff80, 0x0004, 0xfa44, 0x0078);
		put(program, 0x12c24, 0x5f3d, 0x0009, 0xd7fb, 0x00c0, 0x5ad0, 0x300b, 0x581c, 0x5a90, 0x310b, 0x51e6, 0x05f3);
		put(program, 0x12c3a, 0x31d7, 0xb9e6, 0x05cb, 0x51e6, 0x05a3, 0x31d7, 0x31aa, 0x3816, 0x377d, 0x0009, 0xff80);
		put(program, 0x12c50, 0x0004, 0xfa44, 0x0074, 0x373d, 0x0009, 0x3816, 0x577d, 0x0009, 0xff80, 0x0004, 0xfa44);
		put(program, 0x12c66, 0x0079, 0x380a, 0x3015, 0xff80, 0x0004, 0xfa44, 0x0078, 0x5f3d, 0x0009, 0xe6dc, 0xffff);
		put(program, 0x12c7c, 0x5ad0, 0xe10b, 0x51fc, 0x05f3, 0xe1d7, 0xb9fc, 0x05cb, 0x51fc, 0x05a3, 0xe1d7, 0xe1aa);
		put(program, 0x12c92, 0x07bf, 0xfe62, 0x7008, 0x77ed, 0x0080, 0x4ff7, 0x00c0, 0x7109, 0xb00e, 0xa81c, 0x5018);
		put(program, 0x12ca8, 0xafed, 0x0080, 0x57ed, 0x0080, 0xb290, 0xe7f7, 0x00c0, 0xa640, 0x0001, 0x47f7, 0x00c0);
		put(program, 0x12cbe, 0x3015, 0xe10a, 0xc7f7, 0x00c0, 0x56ce, 0xffff, 0x3816, 0xa634, 0x2140, 0xd80e, 0x6f7d);
		put(program, 0x12cd4, 0x0001, 0xd008, 0xc77d, 0x0009, 0xce40, 0x0001, 0x577d, 0x0005, 0xff80, 0x0004, 0xfa44);
		put(program, 0x12cea, 0x0074, 0x3015, 0x3816, 0xce39, 0x2100, 0xc640, 0x0001, 0x577d, 0x0005, 0xff80, 0x0004);
		put(program, 0x12d00, 0xfa44, 0x0079, 0x36db, 0xffff, 0xc638, 0x2180, 0x380a, 0xa80a, 0xff80, 0x0004, 0xfa44);
		put(program, 0x12d16, 0x0078, 0x5f3d, 0x0005, 0x6f3d, 0x0001, 0x5ad0, 0x300b, 0x581c, 0x5a90, 0x310b, 0x51e6);
		put(program, 0x12d2c, 0x0de3, 0x31db, 0x5e15, 0xffff, 0xd9e6, 0x05b3, 0x0780, 0x0152, 0x51e6, 0x05bb, 0x0780);
		put(program, 0x12d42, 0x014a, 0xaa5e, 0x31db, 0x31aa, 0x3816, 0x6f7d, 0x0001, 0x377d, 0x0005, 0xff80, 0x0004);
		put(program, 0x12d58, 0xfa44, 0x0074, 0x373d, 0x0005, 0x3816, 0xb00a, 0xff80, 0x0004, 0xfa44, 0x0079, 0x36db);
		put(program, 0x12d6e, 0xffff, 0x380a, 0xa00a, 0xff80, 0x0004, 0xfa44, 0x0078, 0x5816, 0x5ad0, 0xe6dc, 0xffff);
		put(program, 0x12d84, 0x591c, 0x51eb, 0x6f3d, 0x0001, 0x0da3, 0x59db, 0x7e14, 0xffff, 0xd9eb, 0x7d8b, 0x51eb);
		put(program, 0x12d9a, 0x75e3, 0xa25e, 0x59db, 0xc815, 0xb6da, 0xffff, 0xaed4, 0xffff, 0xcad0, 0x59aa, 0xc914);
		put(program, 0x12db0, 0x3816, 0x3015, 0x6f7d, 0x0005, 0xa00b, 0xca90, 0xff80, 0x0004, 0xfa44, 0x0078, 0x3816);
		put(program, 0x12dc6, 0x3019, 0xb01a, 0xb290, 0xe00a, 0xff80, 0x0004, 0xfa44, 0x0078, 0x3816, 0x3019, 0xc80a);
		put(program, 0x12ddc, 0xff80, 0x0004, 0xfa44, 0x0078, 0x3816, 0x3015, 0xb00a, 0xff80, 0x0004, 0xfa44, 0x0078);
		put(program, 0x12df2, 0x601c, 0x51d9, 0x6290, 0x61ca, 0xc9ec, 0x6f3d, 0x0005, 0x05c3, 0x5640, 0x0001, 0xb1ca);
		put(program, 0x12e08, 0x500c, 0x5290, 0x62d0, 0xe6dc, 0xffff, 0x51d6, 0x61dc, 0xa1ea, 0x1db1, 0x15e2, 0x773d);
		put(program, 0x12e1e, 0x0009, 0x5814, 0x59aa, 0x618e, 0x71ec, 0xdfe1, 0x0000, 0x59bb, 0x500b, 0x181d, 0x57ed);
		put(program, 0x12e34, 0x00c0, 0x67f7, 0x0080, 0x1a4c, 0x510c, 0x5ff7, 0x0080, 0x07bf, 0xf3be, 0x5f3d, 0x0009);
		put(program, 0x12e4a, 0x59ec, 0xed89, 0xd18c, 0x61fa, 0x67e1, 0x0000, 0x61db, 0x51ac, 0x601a, 0xe585, 0x5620);
		put(program, 0x12e60, 0x0018, 0x07bf, 0xfbde, 0x5e20, 0x0018, 0x07bf, 0xfade, 0x5640, 0x0100, 0x41ea, 0x1599);
		put(program, 0x12e76, 0xce40, 0x0001, 0x5e20, 0x0010, 0xce39, 0x2100, 0x07bf, 0xfc32, 0xa00f, 0x8dc5, 0xa80b);
		put(program, 0x12e8c, 0x07bf, 0xfebc, 0x31d7, 0x07bf, 0xfca4, 0xce40, 0x0001, 0x5e20, 0x0018, 0xce39, 0x2100);
		put(program, 0x12ea2, 0x07bf, 0xfc12);

		// 0x12ec0: caller D (74 halfwords): the real div/mod family with
		// variable runtime arguments and escaping result stores - signed
		// and unsigned division and remainder all in one consumer.
		callerPrologue(program, 0x12ec0);
		at = strippedCall(program, 0x12ed4, 0x12240, 37, 37);
		at = strippedCall(program, at, 0x128e0, 38, 38);
		at = strippedCall(program, at, 0x13000, 39, 39);
		at = strippedCall(program, at, 0x136a0, 40, 40);
		callerEpilogue(program, at);

		// 0x13000: ___udivdi3 and 0x136a0: ___moddi3, relocated verbatim
		// from the committed _udivdi3.o / _moddi3.o objects to complete
		// the four-family division coverage.
		put(program, 0x13000, 0x1e03, 0xffd4, 0xb763, 0x001d, 0xcf63, 0x0011, 0xd763, 0x000d, 0xdf63, 0x0009, 0xe763);
		put(program, 0x13016, 0x0005, 0xef63, 0x0001, 0xff63, 0x0029, 0xa763, 0x0025, 0xaf63, 0x0021, 0xbf63, 0x0019);
		put(program, 0x1302c, 0xc763, 0x0015, 0x1a58, 0x4a60, 0xe803, 0xd806, 0xd007, 0xe008, 0xc806, 0xb007, 0x05b2);
		put(program, 0x13042, 0x0780, 0x013c, 0x41e7, 0x05bb, 0x0780, 0x019e, 0x5640, 0x0001, 0x41ea, 0x05b9, 0x0780);
		put(program, 0x13058, 0x02b6, 0x5640, 0x0100, 0x41ea, 0x05b1, 0x0780, 0x0588, 0x5e20, 0x0010, 0x5008, 0x6640);
		put(program, 0x1306e, 0x0001, 0x57eb, 0x0080, 0x662c, 0x2000, 0x51cc, 0x570a, 0x0000, 0x6620, 0x0020, 0x56ca);
		put(program, 0x13084, 0x00ff, 0x51cb, 0x680c, 0x69aa, 0x61ea, 0x0de2, 0xb01b, 0x581a, 0x5fed, 0x00c0, 0xb7ea);
		put(program, 0x1309a, 0x0080, 0x47ed, 0x00c0, 0xdfed, 0x00c0, 0xe008, 0xb10b, 0xc81b, 0xd81c, 0xda90, 0x6640);
		put(program, 0x130b0, 0x0001, 0x662c, 0x2140, 0x3016, 0x381b, 0x677d, 0x0005, 0xc640, 0x0001, 0xff80, 0x0004);
		put(program, 0x130c6, 0xfa44, 0x006c, 0x3016, 0x381b, 0xc638, 0x2100, 0xbedc, 0xffff, 0xb00a, 0xd640, 0x0001);
		put(program, 0x130dc, 0xff80, 0x0004, 0xfa44, 0x0078, 0x3017, 0xd63a, 0x2180, 0x380a, 0xa80a, 0xff80, 0x0004);
		put(program, 0x130f2, 0xfa44, 0x007a, 0x3016, 0x5819, 0x32d0, 0x5a90, 0x310b, 0x51e6, 0x673d, 0x0005, 0x0db3);
		put(program, 0x13108, 0x31dc, 0x5e15, 0xffff, 0xe1e6, 0x05db, 0x51e6, 0x05b3, 0x0780, 0x050e, 0xa80b, 0x31aa);
		put(program, 0x1311e, 0x381b, 0x377d, 0x0005, 0xff80, 0x0004, 0xfa44, 0x006c, 0x373d, 0x0005, 0x381b, 0xd80a);
		put(program, 0x13134, 0xff80, 0x0004, 0xfa44, 0x0078, 0xdad0, 0xced9, 0xffff, 0x380a, 0x3017, 0xc00a, 0xc91b);
		put(program, 0x1314a, 0xff80, 0x0004, 0xfa44, 0x007a, 0x51f9, 0x0db3, 0xc9dc, 0x5e18, 0xffff, 0xe1f9, 0x05db);
		put(program, 0x13160, 0x51f9, 0x05b3, 0x0780, 0x04b2, 0xc00b, 0x4015, 0x42d0, 0x181d, 0x5008, 0xaa00, 0x1a48);
		put(program, 0x13176, 0x5118, 0x5815, 0x07bf, 0xf086, 0x49e7, 0x0d83, 0xaa00, 0x5200, 0x181d, 0x1a48, 0x5815);
		put(program, 0x1318c, 0x07bf, 0xf074, 0x5640, 0x0001, 0x49ea, 0x05b9, 0x0780, 0x019e, 0x5640, 0x0100, 0x49ea);
		put(program, 0x131a2, 0x05b1, 0x0780, 0x043e, 0x5620, 0x0010, 0x5809, 0x6640, 0x0001, 0x5fea, 0x0080, 0x662c);
		put(program, 0x131b8, 0x2000, 0x59cc, 0x6f0b, 0x0000, 0x5e20, 0x0020, 0x6ecd, 0x00ff, 0x69ca, 0xc80b, 0xc9ad);
		put(program, 0x131ce, 0x59ed, 0x05b2, 0x0780, 0x026e, 0x49fa, 0x05b9, 0x0780, 0x0418, 0x41fb, 0x57e3, 0x0000);
		put(program, 0x131e4, 0xaa00, 0xd585, 0x4260, 0x05ba, 0x0780, 0x0130, 0x5640, 0x0001, 0x41ea, 0x05b1, 0x0780);
		put(program, 0x131fa, 0x03d2, 0xc640, 0x0001, 0xc638, 0x2100, 0x5e20, 0x00ff, 0xe1eb, 0x5feb, 0x0000, 0x5ac3);
		put(program, 0x13210, 0x501c, 0x6640, 0x0001, 0x57eb, 0x0080, 0x662c, 0x2000, 0x51cc, 0x570a, 0x0000, 0x6620);
		put(program, 0x13226, 0x0020, 0x56ca, 0x00ff, 0x51cb, 0x680c, 0x69aa, 0x61ea, 0x05b2, 0x0780, 0x0110, 0xd81a);
		put(program, 0x1323c, 0xb81c, 0x6640, 0x0001, 0xd640, 0x0001, 0xd9bc, 0xba90, 0xb6dc, 0xffff, 0xaa01, 0x662c);
		put(program, 0x13252, 0x2140, 0xd63a, 0x2180, 0x301b, 0x3817, 0x677d, 0x0005, 0xff80, 0x0004, 0xfa44, 0x006c);
		put(program, 0x13268, 0x301b, 0x3817, 0xd80a, 0xff80, 0x0004, 0xfa44, 0x0078, 0x300a, 0x3816, 0xa00a, 0xff80);
		put(program, 0x1327e, 0x0004, 0xfa44, 0x007a, 0x301b, 0x5819, 0x32d0, 0x5a90, 0x310b, 0x51e6, 0x673d, 0x0005);
		put(program, 0x13294, 0x0db3, 0x31dc, 0x5e14, 0xffff, 0xe1e6, 0x05db, 0x51e6, 0x05b3, 0x0780, 0x0378, 0xa00b);
		put(program, 0x132aa, 0x31aa, 0x3817, 0x377d, 0x0005, 0xff80, 0x0004, 0xfa44, 0x006c, 0x373d, 0x0005, 0x3817);
		put(program, 0x132c0, 0xd80a, 0xff80, 0x0004, 0xfa44, 0x0078, 0x3816, 0x300a, 0xc00a, 0xff80, 0x0004, 0xfa44);
		put(program, 0x132d6, 0x007a, 0x581b, 0x5ad0, 0xced9, 0xffff, 0x5919, 0x51eb, 0x0db3, 0x59dc, 0x6618, 0xffff);
		put(program, 0x132ec, 0xe1eb, 0x05db, 0x51eb, 0x05b3, 0x0780, 0x031c, 0xc00c, 0x4014, 0x42d0, 0x181d, 0x5008);
		put(program, 0x13302, 0x1a48, 0x5118, 0x5815, 0x07bf, 0xeef8, 0x5e20, 0x00ff, 0x41eb, 0x5feb, 0x0000, 0x5ac3);
		put(program, 0x13318, 0x07bf, 0xfd52, 0xc640, 0x0001, 0xc638, 0x2100, 0x3a00, 0x3201, 0xff80, 0x0004, 0xfa44);
		put(program, 0x1332e, 0x0078, 0xe00a, 0x07bf, 0xfed2, 0x5620, 0x00ff, 0x49ea, 0x57eb, 0x0000, 0x52c3, 0x07bf);
		put(program, 0x13344, 0xfe6a, 0xe7ed, 0x00c0, 0xa81a, 0xb81c, 0xafea, 0x0080, 0xba90, 0x581a, 0xa01b, 0x6640);
		put(program, 0x1335a, 0x0001, 0x5fed, 0x00c0, 0x662c, 0x2140, 0xa7ea, 0x0080, 0x3015, 0x3817, 0xdfed, 0x00c0);
		put(program, 0x13370, 0xa10b, 0x677d, 0x0005, 0xff80, 0x0004, 0xfa44, 0x006c, 0x3015, 0x3817, 0xb6dc, 0xffff);
		put(program, 0x13386, 0xc81b, 0xd640, 0x0001, 0xd80a, 0xff80, 0x0004, 0xfa44, 0x0078, 0x3016, 0xd63a, 0x2180);
		put(program, 0x1339c, 0x380a, 0xa80a, 0xff80, 0x0004, 0xfa44, 0x007a, 0x301b, 0x5814, 0x32d0, 0x5a90, 0x310b);
		put(program, 0x133b2, 0x51e6, 0x673d, 0x0005, 0x0de3, 0x31dc, 0x5e15, 0xffff, 0xe1e6, 0x05b3, 0x0780, 0x0246);
		put(program, 0x133c8, 0x51e6, 0x05bb, 0x0780, 0x023e, 0xaa5e, 0x31dc, 0x31aa, 0x3817, 0x677d, 0x0001, 0x377d);
		put(program, 0x133de, 0x0005, 0xff80, 0x0004, 0xfa44, 0x006c, 0x373d, 0x0005, 0x3817, 0xd80a, 0xff80, 0x0004);
		put(program, 0x133f4, 0xfa44, 0x0078, 0x380a, 0xdad0, 0xa6d4, 0xffff, 0x3016, 0xd914, 0x577d, 0x0005, 0xff80);
		put(program, 0x1340a, 0x0004, 0xfa44, 0x007a, 0x51fb, 0x3f3d, 0x0005, 0x673d, 0x0001, 0x0de3, 0xd9dc, 0x5e07);
		put(program, 0x13420, 0xffff, 0xe1fb, 0x05b3, 0x0780, 0x01d8, 0x51fb, 0x05bb, 0x0780, 0x01d0, 0x3a5e, 0xd9dc);
		put(program, 0x13436, 0xaad0, 0xd9aa, 0xa907, 0x07bf, 0xfe1c, 0x7008, 0x4ff9, 0x00c0, 0x77ed, 0x0080, 0x7109);
		put(program, 0x1344c, 0xb00e, 0xe01a, 0xe7ed, 0x0080, 0xb290, 0x581a, 0x6640, 0x0001, 0xa81b, 0x5ff9, 0x00c0);
		put(program, 0x13462, 0xafed, 0x0080, 0x662c, 0x2140, 0x47f9, 0x00c0, 0x56ce, 0xffff, 0x301c, 0x3816, 0xa90b);
		put(program, 0x13478, 0xa00e, 0x677d, 0x0001, 0xb808, 0xc640, 0x0001, 0x577d, 0x0005, 0xff80, 0x0004, 0xfa44);
		put(program, 0x1348e, 0x006c, 0x301c, 0x3816, 0xc638, 0x2100, 0xd640, 0x0001, 0x577d, 0x0005, 0xff80, 0x0004);
		put(program, 0x134a4, 0xfa44, 0x0078, 0x36d4, 0xffff, 0xd63a, 0x2180, 0x380a, 0xe00a, 0xff80, 0x0004, 0xfa44);
		put(program, 0x134ba, 0x007a, 0x5f3d, 0x0005, 0x673d, 0x0001, 0x5ad0, 0x300b, 0x5815, 0x5a90, 0x310b, 0x51e6);
		put(program, 0x134d0, 0x0de3, 0x31d4, 0x5e1c, 0xffff, 0xa1e6, 0x05b3, 0x0780, 0x0128, 0x51e6, 0x05bb, 0x0780);
		put(program, 0x134e6, 0x0120, 0xe25e, 0x31d4, 0x31aa, 0x3816, 0x377d, 0x0005, 0xff80, 0x0004, 0xfa44, 0x006c);
		put(program, 0x134fc, 0x373d, 0x0005, 0x3816, 0xb00a, 0xff80, 0x0004, 0xfa44, 0x0078, 0x36d4, 0xffff, 0xb2d0);
		put(program, 0x13512, 0xaed5, 0xffff, 0x380a, 0xc00a, 0xa916, 0xff80, 0x0004, 0xfa44, 0x007a, 0x51f5, 0x580a);
		put(program, 0x13528, 0x0da3, 0xa9d4, 0x5618, 0xffff, 0xa1f5, 0x65cb, 0x59f5, 0x65a3, 0xc25e, 0xa9d4, 0x501c);
		put(program, 0x1353e, 0x52d0, 0xb6d7, 0xffff, 0xa6d8, 0xffff, 0x5118, 0x3816, 0x3014, 0xc00a, 0xa9ab, 0xc290);
		put(program, 0x13554, 0xe00a, 0xff80, 0x0004, 0xfa44, 0x007a, 0x3816, 0x3018, 0xba90, 0xb00a, 0xff80, 0x0004);
		put(program, 0x1356a, 0xfa44, 0x007a, 0x3817, 0x3018, 0xc00a, 0xff80, 0x0004, 0xfa44, 0x007a, 0x3817, 0x3014);
		put(program, 0x13580, 0xb80a, 0xff80, 0x0004, 0xfa44, 0x007a, 0x5816, 0x51d8, 0x5a90, 0x59ca, 0xc1eb, 0x05c3);
		put(program, 0x13596, 0x5640, 0x0001, 0xb9ca, 0x500b, 0x5290, 0x51d7, 0xa9ea, 0x0de1, 0x05d2, 0x501c, 0xaa00);
		put(program, 0x135ac, 0x07bf, 0xfbda, 0x5ad0, 0xb6d6, 0xffff, 0xdff9, 0x00c0, 0x59d6, 0xd9eb, 0xf5d9, 0x561c);
		put(program, 0x135c2, 0xffff, 0xaa00, 0x07bf, 0xfbc0, 0x5640, 0x0100, 0x41ea, 0x2de9, 0xc640, 0x0001, 0x5e20);
		put(program, 0x135d8, 0x0010, 0xc638, 0x2100, 0x07bf, 0xfc32, 0x5620, 0x0018, 0x07bf, 0xfbc6, 0x5e20, 0x0018);
		put(program, 0x135ee, 0x07bf, 0xfa7c, 0xaa00, 0x5201, 0x07bf, 0xfb90, 0xc00a, 0xa585, 0x380b, 0x07bf, 0xfe36);
		put(program, 0x13604, 0xe00b, 0x07bf, 0xfee6, 0xa80b, 0x07bf, 0xfdc8, 0xc25e, 0x07bf, 0xfce8, 0xc25e, 0x07bf);
		put(program, 0x1361a, 0xfb52, 0xa25e, 0x31dc, 0x07bf, 0xfc8a, 0xaa5e, 0x31dc, 0x07bf, 0xfaf4, 0xc640, 0x0001);
		put(program, 0x13630, 0x5e20, 0x0018, 0xc638, 0x2100, 0x07bf, 0xfbd8);
		put(program, 0x136a0, 0x1e03, 0xffd4, 0xbf63, 0x0019, 0xe763, 0x0005, 0xef63, 0x0001, 0xff63, 0x0029, 0xa763);
		put(program, 0x136b6, 0x0025, 0xaf63, 0x0021, 0xb763, 0x001d, 0xc763, 0x0015, 0xcf63, 0x0011, 0xd763, 0x000d);
		put(program, 0x136cc, 0xdf63, 0x0009, 0x1e03, 0xffec, 0x3a60, 0xe803, 0xe007, 0xb806, 0x05be, 0x0780, 0x02a2);
		put(program, 0x136e2, 0xda00, 0x4a60, 0x05fe, 0x4260, 0x57ea, 0x0000, 0x4980, 0x49aa, 0x4180, 0x4a60, 0xa008);
		put(program, 0x136f8, 0xc817, 0xb01c, 0x7daa, 0x41fc, 0x05bb, 0x0780, 0x0176, 0x5640, 0x0001, 0x41ea, 0x05b9);
		put(program, 0x1370e, 0x0780, 0x0284, 0x5640, 0x0100, 0x41ea, 0x05b1, 0x0780, 0x0568, 0x5e20, 0x0010, 0x5008);
		put(program, 0x13724, 0x6640, 0x0001, 0x57eb, 0x0080, 0x662c, 0x2000, 0x51cc, 0x570a, 0x0000, 0x6620, 0x0020);
		put(program, 0x1373a, 0x56ca, 0x00ff, 0x51cb, 0xd00c, 0xd1aa, 0x61ea, 0x0dd2, 0xb017, 0xe7fa, 0x00c0, 0xb7ea);
		put(program, 0x13750, 0x0080, 0x47fa, 0x00c0, 0xc817, 0xa008, 0xb11c, 0xcffa, 0x00c0, 0xa814, 0xaa90, 0x6640);
		put(program, 0x13766, 0x0001, 0x662c, 0x2140, 0x3016, 0x3815, 0x677d, 0x0011, 0xc640, 0x0001, 0xff80, 0x0004);
		put(program, 0x1377c, 0xfa44, 0x006c, 0x3016, 0x3815, 0xc638, 0x2100, 0xbed4, 0xffff, 0xe00a, 0xb640, 0x0001);
		put(program, 0x13792, 0xff80, 0x0004, 0xfa44, 0x0078, 0x3017, 0xb636, 0x2180, 0x380a, 0xff80, 0x0004, 0xfa44);
		put(program, 0x137a8, 0x0076, 0x301c, 0x5819, 0x32d0, 0x5a90, 0x310b, 0x51e6, 0x673d, 0x0011, 0x05f3, 0x31d4);
		put(program, 0x137be, 0xa1e6, 0x05cb, 0x51e6, 0x05a3, 0x31d4, 0x31aa, 0x3815, 0x377d, 0x0011, 0xff80, 0x0004);
		put(program, 0x137d4, 0xfa44, 0x006c, 0x373d, 0x0011, 0x3815, 0xe00a, 0xff80, 0x0004, 0xfa44, 0x0078, 0x380a);
		put(program, 0x137ea, 0x3017, 0x0780, 0x0166, 0x49fc, 0x6017, 0x1583, 0x5017, 0x581c, 0xda60, 0x05f2, 0x5260);
		put(program, 0x13800, 0x67ea, 0x0000, 0x5980, 0x59ac, 0x5180, 0x181d, 0x1e03, 0x0014, 0x07bf, 0xe9f0, 0x5640);
		put(program, 0x13816, 0x0001, 0x49ea, 0x05b9, 0x0780, 0x01a0, 0x5640, 0x0100, 0x49ea, 0x05b1, 0x0780, 0x0452);
		put(program, 0x1382c, 0x5620, 0x0010, 0x5809, 0x6e40, 0x0001, 0x5fea, 0x0080, 0x6e2d, 0x2000, 0x59cd, 0x6f0b);
		put(program, 0x13842, 0x0000, 0x5e20, 0x0020, 0x6ecd, 0x00ff, 0x69ca, 0xa80b, 0xa9ad, 0x59ed, 0xd00d, 0x05b2);
		put(program, 0x13858, 0x0780, 0x0250, 0x49fc, 0x05b1, 0x41f7, 0x0d8b, 0x6008, 0x499c, 0x6197, 0xb9ec, 0xe7e1);
		put(program, 0x1386e, 0x0000, 0xe189, 0x500c, 0x581c, 0xc5a5, 0x4260, 0x05ba, 0x0780, 0x0126, 0x5640, 0x0001);
		put(program, 0x13884, 0x41ea, 0x05b1, 0x0780, 0x0402, 0xc640, 0x0001, 0xc638, 0x2100, 0x5e20, 0x00ff, 0xa1eb);
		put(program, 0x1389a, 0x5feb, 0x0000, 0x5ac3, 0x5014, 0x6640, 0x0001, 0x57eb, 0x0080, 0x662c, 0x2000, 0x51cc);
		put(program, 0x138b0, 0x570a, 0x0000, 0x6620, 0x0020, 0x56ca, 0x00ff, 0x51cb, 0xd00c, 0xd1aa, 0x61ea, 0x05b2);
		put(program, 0x138c6, 0x0780, 0x0106, 0xa814, 0x6640, 0x0001, 0xb640, 0x0001, 0xe1b4, 0xaa90, 0xbed4, 0xffff);
		put(program, 0x138dc, 0x662c, 0x2140, 0xb636, 0x2180, 0x301c, 0x3815, 0x677d, 0x0011, 0xff80, 0x0004, 0xfa44);
		put(program, 0x138f2, 0x006c, 0x301c, 0x3815, 0xe00a, 0xff80, 0x0004, 0xfa44, 0x0078, 0x300a, 0x3817, 0xff80);
		put(program, 0x13908, 0x0004, 0xfa44, 0x0076, 0x301c, 0x5819, 0x32d0, 0x5a90, 0x310b, 0x51e6, 0x673d, 0x0011);
		put(program, 0x1391e, 0x0d83, 0x31d4, 0xa1e6, 0x05db, 0x51e6, 0x05b3, 0x0780, 0x0382, 0x31aa, 0x3815, 0x377d);
		put(program, 0x13934, 0x0011, 0xff80, 0x0004, 0xfa44, 0x006c, 0x373d, 0x0011, 0x3815, 0xe00a, 0xff80, 0x0004);
		put(program, 0x1394a, 0xfa44, 0x0078, 0x3817, 0x300a, 0xff80, 0x0004, 0xfa44, 0x0076, 0x581c, 0x5ad0, 0xced9);
		put(program, 0x13960, 0xffff, 0x5919, 0x51eb, 0x05f3, 0x59d4, 0xa1eb, 0x05cb, 0x51eb, 0x05a3, 0x59d4, 0x518b);
		put(program, 0x13976, 0x57fa, 0x0080, 0x5a00, 0x07bf, 0xfe7e, 0x3260, 0x57ea, 0x0000, 0xe180, 0xe1aa, 0xb980);
		put(program, 0x1398c, 0xda1f, 0x07bf, 0xfd56, 0x5e20, 0x00ff, 0x41eb, 0x5feb, 0x0000, 0x5ac3, 0x07bf, 0xfd84);
		put(program, 0x139a2, 0xc640, 0x0001, 0xc638, 0x2100, 0x3a00, 0x3201, 0xff80, 0x0004, 0xfa44, 0x0078, 0xa00a);
		put(program, 0x139b8, 0x07bf, 0xfedc, 0x5620, 0x00ff, 0x49ea, 0x57eb, 0x0000, 0x52c3, 0x07bf, 0xfe68, 0xa7fa);
		put(program, 0x139ce, 0x00c0, 0xb01c, 0xa814, 0xb7ea, 0x0080, 0xaa90, 0x581c, 0x6640, 0x0001, 0xe017, 0x5ffa);
		put(program, 0x139e4, 0x00c0, 0x662c, 0x2140, 0xe7ea, 0x0080, 0x3016, 0x3815, 0xe10b, 0x677d, 0x000d, 0xff80);
		put(program, 0x139fa, 0x0004, 0xfa44, 0x006c, 0x3016, 0x3815, 0xc817, 0xb640, 0x0001, 0xbed4, 0xffff, 0x577d);
		put(program, 0x13a10, 0x0011, 0xff80, 0x0004, 0xfa44, 0x0078, 0x3017, 0xb636, 0x2180, 0x380a, 0xff80, 0x0004);
		put(program, 0x13a26, 0xfa44, 0x0076, 0x5f3d, 0x0011, 0xcffa, 0x00c0, 0x5ad0, 0x300b, 0x581c, 0x5a90, 0x310b);
		put(program, 0x13a3c, 0x51e6, 0x673d, 0x000d, 0x05f3, 0x31d4, 0xa1e6, 0x05cb, 0x51e6, 0x05a3, 0x31d4, 0x31aa);
		put(program, 0x13a52, 0x3815, 0x677d, 0x000d, 0x377d, 0x0011, 0xff80, 0x0004, 0xfa44, 0x006c, 0x373d, 0x0011);
		put(program, 0x13a68, 0x3815, 0x577d, 0x0011, 0xff80, 0x0004, 0xfa44, 0x0078, 0x380a, 0x3017, 0xff80, 0x0004);
		put(program, 0x13a7e, 0xfa44, 0x0076, 0x5f3d, 0x0011, 0xe6dc, 0xffff, 0x5ad0, 0xe10b, 0x51fc, 0x673d, 0x000d);
		put(program, 0x13a94, 0x05f3, 0xe1d4, 0xa1fc, 0x05cb, 0x51fc, 0x05a3, 0xe1d4, 0xe1aa, 0x07bf, 0xfe40, 0x7008);
		put(program, 0x13aaa, 0x4ff5, 0x00c0, 0x77ed, 0x0080, 0x7109, 0xc80e, 0xb01c, 0xb7ed, 0x0080, 0xca90, 0x6640);
		put(program, 0x13ac0, 0x0001, 0x56ce, 0xffff, 0x662c, 0x2140, 0x47f5, 0x00c0, 0x3016, 0xa017, 0x3819, 0xa7ed);
		put(program, 0x13ad6, 0x0080, 0x777d, 0x0001, 0x677d, 0x0005, 0x477d, 0x0011, 0xc640, 0x0001, 0x577d, 0x000d);
		put(program, 0x13aec, 0xff80, 0x0004, 0xfa44, 0x006c, 0x3016, 0x3819, 0xc638, 0x2100, 0x577d, 0x0009, 0xff80);
		put(program, 0x13b02, 0x0004, 0xfa44, 0x0078, 0x373d, 0x000d, 0xb640, 0x0001, 0xe7f5, 0x00c0, 0xb636, 0x2180);
		put(program, 0x13b18, 0x380a, 0xa11c, 0xe00a, 0xff80, 0x0004, 0xfa44, 0x0076, 0x5f3d, 0x0009, 0xbff5, 0x00c0);
		put(program, 0x13b2e, 0x5ad0, 0x300b, 0x5814, 0x5a90, 0x310b, 0x51e6, 0x673d, 0x0005, 0x773d, 0x0001, 0x0de3);
		put(program, 0x13b44, 0x31ce, 0x5e1c, 0xffff, 0x71e6, 0x05b3, 0x0780, 0x0158, 0x51e6, 0x05bb, 0x0780, 0x0150);
		put(program, 0x13b5a, 0xe25e, 0x31ce, 0x31aa, 0x3819, 0x777d, 0x0005, 0x377d, 0x0009, 0xff80, 0x0004, 0xfa44);
		put(program, 0x13b70, 0x006c, 0x373d, 0x0009, 0x3819, 0xc80a, 0xff80, 0x0004, 0xfa44, 0x0078, 0x373d, 0x000d);
		put(program, 0x13b86, 0x380a, 0xc00a, 0xff80, 0x0004, 0xfa44, 0x0076, 0x5819, 0x5ad0, 0xa6d4, 0xffff, 0x5914);
		put(program, 0x13b9c, 0x51eb, 0x773d, 0x0005, 0x0da3, 0x59ce, 0x6618, 0xffff, 0x71eb, 0x7dbb, 0x51eb, 0x7d93);
		put(program, 0x13bb2, 0xc25e, 0x59ce, 0x6f3d, 0x0011, 0xe2d0, 0x66d8, 0xffff, 0xa6cd, 0xffff, 0xc81c, 0x59aa);
		put(program, 0x13bc8, 0x300c, 0xc918, 0x3814, 0x777d, 0x0009, 0xe00b, 0xca90, 0x677d, 0x000d, 0xff80, 0x0004);
		put(program, 0x13bde, 0xfa44, 0x0076, 0x3814, 0x3019, 0xc00a, 0xff80, 0x0004, 0xfa44, 0x0076, 0xa73d, 0x0011);
		put(program, 0x13bf4, 0x3019, 0xa290, 0x3814, 0xc80a, 0xff80, 0x0004, 0xfa44, 0x0076, 0x673d, 0x000d, 0x3814);
		put(program, 0x13c0a, 0x300c, 0xa00a, 0xff80, 0x0004, 0xfa44, 0x0076, 0x6018, 0x51d9, 0x6290, 0x61ca, 0xc9ec);
		put(program, 0x13c20, 0x773d, 0x0009, 0x05c3, 0x5640, 0x0001, 0xa1ca, 0x500c, 0x5290, 0x62d0, 0xc6d8, 0xffff);
		put(program, 0x13c36, 0x51d4, 0x61d8, 0xe1ea, 0x15d1, 0x15a2, 0x581c, 0x6197, 0x59aa, 0xb9ec, 0xbfe1, 0x0000);
		put(program, 0x13c4c, 0x59b7, 0x500b, 0x57fa, 0x00c0, 0x67f5, 0x0080, 0x510c, 0x5ff5, 0x0080, 0x07bf, 0xfb9c);
		put(program, 0x13c62, 0xb9ec, 0xede9, 0x473d, 0x0011, 0x418c, 0x61e8, 0x67e1, 0x0000, 0x61ce, 0x51ac, 0x6008);
		put(program, 0x13c78, 0xe5c5, 0x5620, 0x0018, 0x07bf, 0xfbb2, 0x5e20, 0x0018, 0x07bf, 0xfa9c, 0x5640, 0x0100);
		put(program, 0x13c8e, 0x41ea, 0x1599, 0xc640, 0x0001, 0x5e20, 0x0010, 0xc638, 0x2100, 0x07bf, 0xfc02, 0xc00c);
		put(program, 0x13ca4, 0x8d95, 0xe00b, 0x07bf, 0xfeb6, 0x31d4, 0x07bf, 0xfc80, 0xc640, 0x0001, 0x5e20, 0x0018);
		put(program, 0x13cba, 0xc638, 0x2100, 0x07bf, 0xfbe2);

		// --- Regressed mutants of REAL bodies (must NOT be recognized) -----
		// 0x12f60: lshrdi3 with its first `be` condition inverted to `bne`
		// (altered branch predicate: cc nibble 2 -> 0xA flips one bit).
		put(program, 0x12f60, 0x4260, 0x15fa, 0x5e20, 0x0020, 0x59a8, 0x5a60, 0x0dc7, 0x5006,
			0x6007, 0x67eb, 0x00c0, 0x57e8, 0x0080, 0x3fe8, 0x0080, 0x510c, 0x5807, 0x007f,
			0x5007, 0x3a00, 0x57e8, 0x0080, 0x5807, 0x007f, 0x5006, 0x5807, 0x007f);
		// 0x12fa0: cmpdi2 with its `be` condition inverted to `bne`.
		put(program, 0x12fa0, 0x39e9, 0x05fa, 0x57ee, 0x0000, 0x37ef, 0x0000, 0x51c6, 0x007f,
			0x31e8, 0x57e9, 0x0000, 0x37eb, 0x0000, 0x51c6, 0x007f);
		// 0x12fc0: __ghssave27 shape saving r26 instead of r27 (changed
		// saved-register effect).
		put(program, 0x12fc0, 0x6003, 0x1a50, 0xd763, 0x0009, 0xe763, 0x0005, 0xef63, 0x0001,
			0xe80a, 0xff6c, 0xfffd, 0x672a, 0xfffa, 0x66cc, 0xffff, 0x62c2, 0x19ac, 0x006a);
		// 0x12ff0: __save_r29_r31 shape with addi -12 for two saved words
		// (changed stack effect: adjust must equal nregs*4).
		put(program, 0x12ff0, 0x1e03, 0xfff4, 0xef63, 0x0001, 0xff63, 0x0005, 0x006a);

		// --- Stripped near-misses (must NOT be recognized) -----------------
		// 0x13d00: half-wise add without carry propagation.
		put(program, 0x13d00, 0x5008, 0x51c6, 0x5807, 0x59c9, 0x007f);
		// 0x13d20: three-way comparator with a foreign result encoding.
		put(program, 0x13d20, 0x39e9, 0x05aa, 0x31e8, 0x57e9, 0x0000, 0x67eb, 0x0000, 0x51ac,
			0x007f);
		// 0x13d40: 64-bit rotate-left-by-r8 composition (shift shapes with
		// a cross term in BOTH words).
		put(program, 0x13d40, 0x5006, 0x57e8, 0x00c0, 0x5807, 0x5fe8, 0x00c0, 0x6620, 0x0020,
			0x61a8, 0x6806, 0x6fec, 0x0080, 0x510d, 0x6806, 0x6fec, 0x0080, 0x590d, 0x007f);
		// 0x13d80: constant-count shift (count must come from r8).
		put(program, 0x13d80, 0x5006, 0x52c3, 0x5807, 0x5aa3, 0x007f);
		// 0x13da0: subtract with the borrow ADDED into the high word.
		put(program, 0x13da0, 0x5008, 0x5186, 0x51e6, 0x5feb, 0x0000, 0x39a9, 0x39cb, 0x5807,
			0x007f);
		// 0x13dc0: lshrdi3 with its `movea 32` boundary constant changed to
		// 31 (altered branch-select constant: the 32-boundary picks the
		// dual paths, so this is a different algorithm).
		put(program, 0x13dc0, 0x4260, 0x15f2, 0x5e20, 0x001f, 0x59a8, 0x5a60, 0x0dc7, 0x5006,
			0x6007, 0x67eb, 0x00c0, 0x57e8, 0x0080, 0x3fe8, 0x0080, 0x510c, 0x5807, 0x007f,
			0x5007, 0x3a00, 0x57e8, 0x0080, 0x5807, 0x007f, 0x5006, 0x5807, 0x007f);
		// 0x13e00: sub64 with an extra st.w r24,0[sp] (side effect on a
		// preserved register that folding would drop).
		put(program, 0x13e00, 0x5008, 0x5186, 0x51e6, 0x5feb, 0x0000, 0x39a9, 0x5987, 0xc763,
			0x0001, 0x007f);

		// 0x13e40: constant-driven value-selection consumer (82 halfwords).
		// The recovered payloads fold against the finite constants, so the
		// decompiler must constant-fold each STORE: the three-way compares
		// select 0 (a<b) / 1 (a==b) / 2 (a>b) per the committed payload
		// contract, and the 0xFFFF..F vs 0 bit patterns discriminate
		// signedness (signed: cmp(-1,0)=0 vs unsigned: ucmp(max,0)=2; the
		// boolean lt64(0,-1)=0 vs ult64(0,max)=1 pair does the same for
		// the named contracts).
		callerPrologue(program, 0x13e40);
		constSite(program, 0x13e54, 0x11a20, NEG64_A, 0x480);  // cmpdi2(-1, 0)  -> 0
		constSite(program, 0x13e64, 0x11a20, NEG64_B, 0x484);  // cmpdi2(0, -1)  -> 2
		constSite(program, 0x13e74, 0x11a20, SEVEN, 0x488);    // cmpdi2(7, 7)   -> 1
		constSite(program, 0x13e84, 0x11a40, NEG64_A, 0x48c);  // ucmpdi2(max,0) -> 2
		constSite(program, 0x13e94, 0x11a40, NEG64_B, 0x490);  // ucmpdi2(0,max) -> 0
		constSite(program, 0x13ea4, 0x11a40, SEVEN, 0x494);    // ucmpdi2(7, 7)  -> 1
		constSite(program, 0x13eb4, 0x11560, NEG64_B, 0x498);  // gh_lt64(0,-1)  -> 0
		constSite(program, 0x13ec4, 0x11550, NEG64_B, 0x49c);  // gh_ult64(0,max)-> 1
		callerEpilogue(program, 0x13ed4);

		// 0x20000 (separate flash block): GCC shift constant-edge consumer
		// (252 halfwords). A REAL machine caller: the GCC shift helpers take
		// a (r6/r7) and count (r8) as volatile arguments - lshrdi3's body
		// mutates r7 and ashldi3's mutates r6 - so every site rematerializes
		// a and the count before its call; nothing assumes the fixup
		// preserves argument registers. The committed bodies' ACTUAL machine
		// behavior is asserted through folded STORE constants: the large arm
		// (signed 32-count <= 0, i.e. count >= 32) moves the surviving word
		// with count&31 (NOT count&63 and NOT the spec's ">=64 gives 0"),
		// and count=0xffffffff takes the SMALL arm (32-(-1)=33>0) with the
		// same &31 masking. a = 0x1122334455667788 throughout; one extra
		// negative-input site proves ashrdi3's sign replication.
		MemoryBlock flash2 = program.getMemory()
			.createInitializedBlock("flash2", addr(program, 0x20000), 0x800, (byte) 0, monitor,
				false);
		flash2.setPermissions(true, false, true);
		callerPrologue(program, 0x20000);
		long gs = gccShiftSite(program, 0x20014, 0x55667788, 0x11223344, 64, 0x11960, 0x4a0);
		gs = gccShiftSite(program, gs, 0x55667788, 0x11223344, 64, 0x119e0, 0x4a8);
		gs = gccShiftSite(program, gs, 0x55667788, 0x11223344, 64, 0x119a0, 0x4b0);
		gs = gccShiftSite(program, gs, 0x55667788, 0x11223344, 65, 0x11960, 0x4b8);
		gs = gccShiftSite(program, gs, 0x55667788, 0x11223344, 65, 0x119e0, 0x4c0);
		gs = gccShiftSite(program, gs, 0x55667788, 0x11223344, 65, 0x119a0, 0x4c8);
		gs = gccShiftSite(program, gs, 0x55667788, 0x11223344, 96, 0x11960, 0x4d0);
		gs = gccShiftSite(program, gs, 0x55667788, 0x11223344, 96, 0x119e0, 0x4d8);
		gs = gccShiftSite(program, gs, 0x55667788, 0x11223344, 96, 0x119a0, 0x4e0);
		gs = gccShiftSite(program, gs, 0x55667788, 0x11223344, -1, 0x11960, 0x4e8);
		gs = gccShiftSite(program, gs, 0x55667788, 0x11223344, -1, 0x119e0, 0x4f0);
		gs = gccShiftSite(program, gs, 0x55667788, 0x11223344, -1, 0x119a0, 0x4f8);
		gs = gccShiftSite(program, gs, 0x12345678, 0x9abcdef0, 64, 0x119e0, 0x500);
		callerEpilogue(program, gs);

		// Exact fixed-copy bodies relocated independently of firmware addresses.
		// Both loop forms leave their r6/r7 inputs unchanged.
		put(program, 0x20400, 0x9a00, 0x0813, 0x0ac2, 0xf001, 0xf1c6, 0x09c7, 0x9a41,
			0x0f21, 0x0001, 0x0613, 0xffe8, 0x0d01, 0xf5d9, 0x007f);
		put(program, 0x20420, 0x9a00, 0x0813, 0x0ac2, 0xf001, 0xf1c6, 0x09c7, 0x9a41,
			0x0f21, 0x0001, 0x9a68, 0x0d01, 0xf5e1, 0x007f);
		// Near misses: write r6 instead of r1, invert the loop condition,
		// and add a source-argument clobber just before the return.
		put(program, 0x20440, 0x9a00, 0x0813, 0x0ac2, 0xf001, 0xf1c6, 0x31c7, 0x9a41,
			0x0f21, 0x0001, 0x9a68, 0x0d01, 0xf5e1, 0x007f);
		put(program, 0x20460, 0x9a00, 0x0813, 0x0ac2, 0xf001, 0xf1c6, 0x09c7, 0x9a41,
			0x0f21, 0x0001, 0x9a68, 0x0d01, 0xf5e9, 0x007f);
		put(program, 0x20480, 0x9a00, 0x0813, 0x0ac2, 0xf001, 0xf1c6, 0x09c7, 0x9a41,
			0x0f21, 0x0001, 0x9a68, 0x0d01, 0xf5e1, 0x3a00, 0x007f);
		copyConsumer(program, 0x20500, 0x20400, 0x14000, 0x14100, 0x560);
		copyConsumer(program, 0x20600, 0x20420, 0x14080, 0x14200, 0x570);

		// Ordinary in-function GHS/GCC epilogues are not standalone
		// helpers, even when their bytes match an out-of-line return helper.
		put(program, 0x13f00, 0x0780, 0x0021); // prepare {lp},0
		put(program, 0x13f04, jarl(0x13f04, 0x13f40, 31));
		put(program, 0x13f08, 0x5207); // mov 7,r10
		put(program, 0x13f0a, 0x0640, 0x003f); // dispose 0,{lp},[lp]
		put(program, 0x13f40, 0x5201, 0x007f); // mov 1,r10; jmp [lp]
		put(program, 0x13f80, 0x1e03, 0xfffc); // addi -4,sp,sp
		put(program, 0x13f84, stw(31, 0, 3));
		put(program, 0x13f88, jarl(0x13f88, 0x13f40, 31));
		put(program, 0x13f8c, 0x5209); // mov 9,r10
		put(program, 0x13f8e, ldw(31, 0, 3));
		put(program, 0x13f92, 0x1e03, 0x0004, 0x007f); // release and return
		// Orphaned code and a conditional local exit are not entry evidence.
		put(program, 0x13fc0, 0x1582, 0x007f); // be 0x13fe0; jmp [lp]
		put(program, 0x13fe0, 0x0640, 0x003f);
		put(program, 0x13ff0, 0x0640, 0x003f);

		// --- Variable runtime-argument data (writable: loads stay unknown) -
		MemoryBlock args = program.getMemory()
			.createInitializedBlock("data", addr(program, 0x14000), 0x600, (byte) 0, monitor,
				false);
		args.setPermissions(true, true, false);
		byte[] argBytes = new byte[0x2a0];
		for (int i = 0; i < argBytes.length; i++) {
			argBytes[i] = (byte) (0x5a ^ (i * 41 + 3));
		}
		program.getMemory().setBytes(addr(program, 0x14000), argBytes);

		// Disassemble function entries (flows reach the helper bodies).
		long[] entries = { 0x10000, 0x10020, 0x10100, 0x10120, 0x10200, 0x10230, 0x10400, 0x10500,
			0x10520, 0x10600, 0x11020, 0x11028, 0x11600, 0x11800, 0x11820, 0x11860, 0x11880,
			// stripped arithmetic bodies (no labels: names must stay default)
			0x11900, 0x11920, 0x11940, 0x11960, 0x119a0, 0x119e0, 0x11a20, 0x11a40, 0x11a60,
			0x11a80, 0x11b60, 0x11b80, 0x11ba0, 0x11bb0, 0x11be0, 0x11c10,
			// ABI-correct stripped-helper callers and the abort stub
			0x11c60, 0x11d40, 0x11dc0, 0x11e60, 0x11e80,
			// real div/mod dependencies and bodies
			0x12100, 0x12140, 0x12180, 0x121c0, 0x12200, 0x12240, 0x128e0,
			0x12ec0, 0x13000, 0x136a0,
			// stripped near-miss bodies and regressed mutants
			0x12f60, 0x12fa0, 0x12fc0, 0x12ff0, 0x13d00, 0x13d20, 0x13d40, 0x13d80, 0x13da0,
			0x13dc0, 0x13e00,
			// the constant-driven value-selection consumer and the GCC
			// shift constant-edge consumer
			0x13e40, 0x13f00, 0x13f40, 0x13f80, 0x13fc0, 0x13fe0, 0x13ff0, 0x20000,
			0x20400, 0x20420, 0x20440, 0x20460, 0x20480, 0x20500, 0x20600 };
		for (long e : entries) {
			new DisassembleCommand(addr(program, e), null, true).applyTo(program, monitor);
		}

		// Create the caller functions and name the arithmetic contracts.
		long[] callers = { 0x10000, 0x10020, 0x10400, 0x10500, 0x10520, 0x10600, 0x11600,
			0x11880, 0x11c60, 0x11d40, 0x11dc0, 0x12ec0, 0x13e40,
			0x10230, 0x13f00, 0x13f40, 0x13f80, 0x20000, 0x20500, 0x20600 };
		for (long c : callers) {
			new CreateFunctionCmd(addr(program, c)).applyTo(program, monitor);
		}
		SymbolTable symbols = program.getSymbolTable();
		for (int i = 0; i < arith.length; i++) {
			symbols.createLabel(addr(program, arith[i]), names[i], SourceType.IMPORTED);
			new CreateFunctionCmd(addr(program, arith[i])).applyTo(program, monitor);
		}
		symbols.createLabel(addr(program, 0x11860), "gh_add65", SourceType.IMPORTED);
		new CreateFunctionCmd(addr(program, 0x11860)).applyTo(program, monitor);
		// Div/mod dependency labels (the reference matcher proves the dep
		// BODIES recursively; the names are for navigation only).
		symbols.createLabel(addr(program, 0x12000), "___clz_tab", SourceType.IMPORTED);
		symbols.createLabel(addr(program, 0x12100), "___udivsi3", SourceType.IMPORTED);
		symbols.createLabel(addr(program, 0x12140), "___umodsi3", SourceType.IMPORTED);
		symbols.createLabel(addr(program, 0x12180), "___mulsi3", SourceType.IMPORTED);
		new CreateFunctionCmd(addr(program, 0x12100)).applyTo(program, monitor);
		new CreateFunctionCmd(addr(program, 0x12140)).applyTo(program, monitor);
		new CreateFunctionCmd(addr(program, 0x12180)).applyTo(program, monitor);
		// The *v family's abort() target: a real (named, non-returning
		// br .) function so the reference matcher's _abort binding
		// validation succeeds.
		symbols.createLabel(addr(program, 0x11e60), "abort", SourceType.IMPORTED);
		new CreateFunctionCmd(addr(program, 0x11e60)).applyTo(program, monitor);
		// Stripped bodies, near-misses and mutants: functions only, never
		// labels, so recognition must come from the bodies themselves.
		long[] stripped = { 0x11900, 0x11920, 0x11940, 0x11960, 0x119a0, 0x119e0, 0x11a20,
			0x11a40, 0x11a60, 0x11a80, 0x11b60, 0x11b80, 0x11ba0, 0x11bb0, 0x11be0, 0x11c10,
			0x121c0, 0x12200, 0x12240, 0x128e0, 0x13000, 0x136a0,
			// mulvdi3: the *v family body (calls ___muldi3 + abort, tails
			// into __return_r24_r31) - created here so Pass 2 recovery and
			// its callers' observation assertions have a real function to
			// work on; CreateFunctionCmd carves the tail-shared epilogue
			// back out of the existing 0x121c0 function.
			0x11e80,
			0x12f60, 0x12fa0, 0x12fc0, 0x12ff0, 0x13d00, 0x13d20, 0x13d40, 0x13d80, 0x13da0,
			0x13dc0, 0x13e00, 0x20400, 0x20420, 0x20440, 0x20460, 0x20480 };
		for (long s : stripped) {
			new CreateFunctionCmd(addr(program, s)).applyTo(program, monitor);
		}
	}

	// ------------------------------------------------------------------
	// Behavioral assertions.
	// ------------------------------------------------------------------

	private void runAssertions(ProgramDB program) throws Exception {
		Listing listing = program.getListing();
		boolean killsR6 = false;
		boolean killsR7 = false;
		for (Varnode killed : program.getCompilerSpec().getDefaultCallingConvention()
				.getKilledByCallList()) {
			killsR6 |= killed.getAddress().equals(program.getRegister("r6").getAddress());
			killsR7 |= killed.getAddress().equals(program.getRegister("r7").getAddress());
		}
		check(killsR6 && killsR7, "ordinary ABI still clobbers r6/r7 outside proven copy bodies");
		for (int i = 0; i < 2; i++) {
			long helper = 0x20400 + i * 0x20;
			Function copy = listing.getFunctionAt(addr(program, helper));
			check(copy != null && !copy.isInline() && copy.getCallFixup() == null &&
				copy.getCallingConventionName().equals("__v850_copy_words"),
				"fixed-word copy has a body-proven local convention, not unsafe repeated inlining");
			Function consumer = listing.getFunctionAt(addr(program, 0x20500 + i * 0x100));
			int source = i == 0 ? 0x14000 : 0x14080;
			int destination = i == 0 ? 0x14100 : 0x14200;
			int slot = 0x14560 + i * 0x10;
			for (int call = 0; call < 2; call++) {
				check(storesConstAt(program, consumer, slot + call * 8,
					destination + call * 0x80),
					"copy caller retains live r6 after call " + call + " in variant " + i);
				check(storesConstAt(program, consumer, slot + call * 8 + 4, source),
					"copy caller retains/reuses source r7 across call " + call + " in variant " + i);
			}
			check(callsCopyWithPointers(program, consumer, helper, source, destination),
				"both real copy calls retain their destination and shared source arguments");
			check(countOps(program, copy, PcodeOp.LOAD, 0) >= 1 &&
				countOps(program, copy, PcodeOp.STORE, 0) >= 1,
				"real copy helper retains its loop memory effects");
			check(execCopyConsumer(program, 0x20500 + i * 0x100, source, destination,
				slot, i == 0 ? 24 : 8),
				"machine copy executes both calls with preserved arguments, exact bounds and data");
		}
		for (long entry : new long[] { 0x20440, 0x20460, 0x20480 }) {
			Function mutant = listing.getFunctionAt(addr(program, entry));
			check(mutant != null && !mutant.isInline() && mutant.getCallFixup() == null &&
				mutant.getName().startsWith("FUN_"),
				"mutated copy is not granted an instruction-unproven preservation contract");
		}
		check(listing.getFunctionAt(addr(program, 0x13f0a)) == null &&
			listing.getFunctionAt(addr(program, 0x13f00)).getBody().contains(addr(program, 0x13f0a)),
			"GHS inline epilogue remains inside its caller, not a false helper entry");
		check(listing.getFunctionAt(addr(program, 0x13f8e)) == null &&
			listing.getFunctionAt(addr(program, 0x13f80)).getBody().contains(addr(program, 0x13f96)),
			"GCC inline epilogue remains inside its caller, not a false helper entry");
		check(listing.getFunctionAt(addr(program, 0x13fe0)) == null &&
			listing.getFunctionAt(addr(program, 0x13ff0)) == null,
			"orphan and conditionally reached epilogues do not become helper entries");

		// GCC/GHS save+restore recognition and effects.
		Function save = listing.getFunctionAt(addr(program, 0x10100));
		check(save != null && save.getName().equals("__save_r29_r31") && save.isInline(),
			"GCC __save_r29_r31 recognized, named, inline (got " +
				(save == null ? "<none>" : save.getName() + " inline=" + save.isInline()) + ")");
		Function ret = listing.getFunctionAt(addr(program, 0x10120));
		check(ret != null && ret.getName().equals("__return_r29") && ret.isInline(),
			"GCC __return_r29 recognized, named, inline (got " +
				(ret == null ? "<none>" : ret.getName()) + ")");
		Function ghsSave = listing.getFunctionAt(addr(program, 0x10200));
		check(ghsSave != null && ghsSave.getName().equals("__ghssave27") && ghsSave.isInline(),
			"GHS __ghssave27 recognized, named, inline (got " +
				(ghsSave == null ? "<none>" : ghsSave.getName()) + ")");
		Function ghsLoad = listing.getFunctionAt(addr(program, 0x10230));
		check(ghsLoad != null && ghsLoad.getName().equals("__ghsload27") && ghsLoad.isInline(),
			"GHS __ghsload27 recognized, named, inline (got " +
				(ghsLoad == null ? "<none>" : ghsLoad.getName()) + ")");

		// Real stack effect of the inlined GCC save on its caller: the
		// consumer stores the helper-adjusted sp ITSELF into escaping RAM
		// (a local dead store is correctly elided by the decompiler and
		// proves nothing), so the -8 delta must be observable in the
		// decompiled pcode - an sp-derived value reaching an escaping
		// store - and at machine level as the escaped pointer value.
		Function gccCaller = listing.getFunctionAt(addr(program, 0x10000));
		check(storesConstSpDelta(program, gccCaller, -8),
			"inlined __save_r29_r31 escapes its caller-adjusted sp at -8 in decompiled pcode");
		check(execConsumerSp(program, 0x10000, 0x14520, 0x14524, 8, 0x13572468L),
			"machine run: GCC save consumer escapes sp == entry-8, round-trips its r6 spill, restores sp");
		// The linker-fixed locals word is read from read-only code. With
		// ordinary Ghidra decompiler options its allocation folds to -24.
		Data locals = listing.getDataAt(addr(program, 0x103fe));
		check(locals != null && locals.getDataType() instanceof WordDataType &&
			(locals.getValue() instanceof Scalar) &&
			((Scalar) locals.getValue()).getUnsignedValue() == 2,
			"GHS dynamic locals halfword created as word data at jarl-2 (got " +
				(locals == null ? "<none>" : locals.getDataType().getName()) + ")");
		Function ghsCaller = listing.getFunctionAt(addr(program, 0x10400));
		check(storesConstSpDelta(program, ghsCaller, -24),
			"inlined __ghssave27 escapes sp with its 16+8 dynamic-locals allocation");
		check(execConsumerSp(program, 0x10400, 0x14528, 0x1452c, 24, 0x2468ace0L),
			"machine run: GHS save consumer escapes sp == entry-24 (16 fixed + 8 dynamic locals)");

		// CALLT recovery: register-analyzer call refs, helpers, dead word.
		check(hasReference(program, 0x10510, 0x11020),
			"callt 0 site references ___ghssv4lp");
		check(hasReference(program, 0x10530, 0x11028),
			"callt 1 site references ___ghsld4lp");
		Function sv4 = listing.getFunctionAt(addr(program, 0x11020));
		check(sv4 != null && sv4.getName().equals("___ghssv4lp") && sv4.isInline(),
			"___ghssv4lp recognized from callt reference (got " +
				(sv4 == null ? "<none>" : sv4.getName()) + ")");
		Function ld4 = listing.getFunctionAt(addr(program, 0x11028));
		check(ld4 != null && ld4.getName().equals("___ghsld4lp") && ld4.isInline(),
			"___ghsld4lp recognized from callt reference (got " +
				(ld4 == null ? "<none>" : ld4.getName()) + ")");
		Data dead = listing.getDataAt(addr(program, 0x10532));
		check(dead != null && dead.getDataType() instanceof WordDataType,
			"dead word after ghsld4 callt defined as data (got " +
				(dead == null ? "<none>" : dead.getDataType().getName()) + ")");

		// Named GHS contracts: typed 32-vs-64 ABI (joined register pairs for
		// 8-byte values, 4-byte int results and shift counts, unsigned
		// variants for the u-family).
		checkAbi(program, listing, 0x11500, "gh_add64", "longlong", "longlong", "longlong");
		checkAbi(program, listing, 0x11520, "gh_udiv64", "ulonglong", "ulonglong", "ulonglong");
		checkAbi(program, listing, 0x11550, "gh_ult64", "int", "ulonglong", "ulonglong");
		checkAbi(program, listing, 0x11580, "gh_shra_64_32", "longlong", "longlong", "uint");
		checkAbiLengths(program, listing, 0x115a0, "___gh_mul64o", 8, 8, 8);

		// Behavioral folds in the named caller: with variable runtime
		// arguments and DISTINCT argument slots (gh_mul64 and ___gh_mul64o
		// share one a*b payload; identical arguments would let the
		// decompiler CSE the two folds), the folded 8-byte p-code ops are
		// live and signedness is observable. These payloads are straight
		// line, so each contributes exactly one op.
		Function arithCaller = listing.getFunctionAt(addr(program, 0x11600));
		check(countOps(program, arithCaller, PcodeOp.INT_ADD, 8) == 1,
			"gh_add64 folds to exactly one 8-byte INT_ADD");
		check(countOps(program, arithCaller, PcodeOp.INT_SDIV, 8) == 1,
			"gh_div64 folds to one signed 8-byte INT_SDIV");
		check(countOps(program, arithCaller, PcodeOp.INT_DIV, 8) == 1,
			"gh_udiv64 folds to one unsigned 8-byte INT_DIV");
		check(countOps(program, arithCaller, PcodeOp.INT_SREM, 8) == 1,
			"gh_rem64 folds to one signed 8-byte INT_SREM");
		check(countOps(program, arithCaller, PcodeOp.INT_REM, 8) == 1,
			"gh_urem64 folds to one unsigned 8-byte INT_REM");
		check(countOps(program, arithCaller, PcodeOp.INT_SLESS, 8) == 1,
			"gh_lt64 folds to one 8-byte INT_SLESS");
		check(countOps(program, arithCaller, PcodeOp.INT_LESS, 8) == 1,
			"gh_ult64 folds to one 8-byte INT_LESS");
		check(countOps(program, arithCaller, PcodeOp.INT_EQUAL, 8) == 1,
			"gh_eq64 folds to one 8-byte INT_EQUAL");
		check(countOpsDynamicCount(program, arithCaller, PcodeOp.INT_SRIGHT, 8) == 1,
			"gh_shra_64_32 folds to one 8-byte INT_SRIGHT with variable count");
		check(countOps(program, arithCaller, PcodeOp.INT_MULT, 8) == 2,
			"gh_mul64 and ___gh_mul64o fold to two distinct 8-byte INT_MULTs");

		// Near-miss negatives (named path).
		Function badSave = listing.getFunctionAt(addr(program, 0x11800));
		check(badSave == null || !(badSave.isInline() || badSave.getName().startsWith("__save")),
			"mutated GCC save NOT recognized (got " +
				(badSave == null ? "<none>" : badSave.getName()) + ")");
		Function badLoad = listing.getFunctionAt(addr(program, 0x11820));
		check(badLoad == null || !(badLoad.isInline() || badLoad.getName().startsWith("__ghs")),
			"truncated GHS load NOT recognized (got " +
				(badLoad == null ? "<none>" : badLoad.getName()) + ")");
		Function badArith = listing.getFunctionAt(addr(program, 0x11860));
		check(badArith != null && badArith.getCallFixup() == null && !badArith.isInline(),
			"near-miss name gh_add65 NOT contracted (got fixup=" +
				(badArith == null ? "<none>" : badArith.getCallFixup()) + ")");

		// Stripped (default-named) arithmetic recovery, proven BEHAVIORALLY
		// through the callers' decompiled p-code: with variable arguments
		// the folded 8-byte operations can only come from the recovered
		// stripped bodies. Canonical forms are accommodated rather than
		// pinning injected opcodes: the decompiler's RuleSub2Add +
		// RuleMultNegOne rewrite the negdi2 payload (0 - a) to a unary
		// INT_2COMP, while the binary sub64 payload (a - b, both variable)
		// stays INT_SUB, so caller A must show exactly one of each - never
		// two INT_SUBs.
		Function callerA = listing.getFunctionAt(addr(program, 0x11c60));
		check(countOps(program, callerA, PcodeOp.INT_ADD, 8) == 1,
			"caller A folds exactly one 8-byte INT_ADD (add64)");
		check(countOps(program, callerA, PcodeOp.INT_SUB, 8) == 1,
			"caller A folds sub64 into one binary 8-byte INT_SUB");
		check(countOps(program, callerA, PcodeOp.INT_2COMP, 8) == 1,
			"caller A folds negdi2 into one canonical unary 8-byte INT_2COMP");
		check(hasCallTo(program, callerA, 0x11bb0) && hasCallTo(program, callerA, 0x11be0) &&
			hasCallTo(program, callerA, 0x11c10),
			"caller A keeps the addvdi3/subvdi3/negvdi2 trapping calls un-folded");
		Function callerB = listing.getFunctionAt(addr(program, 0x11d40));
		// The GCC-specific shift payloads preserve the compiled arm/count
		// structure (word-level shifts with r8&31 masking and select
		// between arms), so caller B checks for the folded shift ops
		// without pinning their count or width; the GCC shift constant-edge
		// consumer below proves the exact behavioral results.
		check(countOpsDynamicCount(program, callerB, PcodeOp.INT_RIGHT, 4) >= 1,
			"caller B folds lshrdi3 into logical right shifts with variable count");
		check(countOpsDynamicCount(program, callerB, PcodeOp.INT_LEFT, 4) >= 1,
			"caller B folds ashldi3 into logical left shifts with variable count");
		check(countOpsDynamicCount(program, callerB, PcodeOp.INT_SRIGHT, 4) >= 1,
			"caller B folds ashrdi3 into arithmetic right shifts with variable count");
		// The three-way compare payloads contain TWO relations each
		// (a s< b and a s> b); the SLEIGH parser lowers `a s> b` to a
		// REVERSED INT_SLESS (there is no INT_SGREAT p-code op), so each
		// payload contributes two INT_SLESS / two INT_LESS ops. The
		// value-selection consumer below proves the actual 0/1/2 result
		// selection, which a bare predicate count cannot.
		Function callerC = listing.getFunctionAt(addr(program, 0x11dc0));
		check(countOps(program, callerC, PcodeOp.INT_XOR, 8) == 1,
			"caller C folds xor64 into one 8-byte INT_XOR");
		check(countOps(program, callerC, PcodeOp.INT_SLESS, 8) == 2,
			"caller C folds cmpdi2 into two 8-byte INT_SLESS (both relations)");
		check(countOps(program, callerC, PcodeOp.INT_LESS, 8) == 2,
			"caller C folds ucmpdi2 into two 8-byte INT_LESS (both relations)");
		check(countOps(program, callerC, PcodeOp.INT_MULT, 8) == 1,
			"caller C folds the real muldi3 body into one 8-byte INT_MULT");
		Function callerD = listing.getFunctionAt(addr(program, 0x12ec0));
		check(countOps(program, callerD, PcodeOp.INT_SDIV, 8) == 1,
			"caller D folds the real divdi3 body into one 8-byte INT_SDIV");
		check(countOps(program, callerD, PcodeOp.INT_REM, 8) == 1,
			"caller D folds the real umoddi3 body into one 8-byte INT_REM");
		check(countOps(program, callerD, PcodeOp.INT_DIV, 8) == 1,
			"caller D folds the real udivdi3 body into one 8-byte INT_DIV");
		check(countOps(program, callerD, PcodeOp.INT_SREM, 8) == 1,
			"caller D folds the real moddi3 body into one 8-byte INT_SREM");

		// The trapping *v family: mulvdi3 itself is typed with no fixup, so
		// its caller keeps the CALL and gets NO wrapping INT_MULT payload.
		// Inside the body, the recovered ___muldi3's call fixup is consumed
		// by the decompiler, so the normal path shows the inlined 8-byte
		// INT_MULT (not a CALL), while the overflow path's abort() CALL
		// stays observable.
		Function callerE = listing.getFunctionAt(addr(program, 0x11880));
		check(hasCallTo(program, callerE, 0x11e80),
			"caller E keeps the mulvdi3 trapping call un-folded");
		check(countOps(program, callerE, PcodeOp.INT_MULT, 8) == 0,
			"caller E injects no wrapping 8-byte INT_MULT payload for mulvdi3");
		Function mulvBody = listing.getFunctionAt(addr(program, 0x11e80));
		check(countOps(program, mulvBody, PcodeOp.INT_MULT, 8) >= 1,
			"mulvdi3 body shows the inlined ___muldi3 fixup (normal path INT_MULT)");
		check(hasCallTo(program, mulvBody, 0x11e60),
			"mulvdi3 body keeps the abort() call observable (overflow path)");

		// Value-selection consumer: the folded payloads must produce the
		// committed 0 (a<b) / 1 (a==b) / 2 (a>b) three-way results and the
		// correct boolean results at the signedness boundary, observable as
		// decompiler constant-folded STORE values (slot = 0x14400+disp).
		Function valueSel = listing.getFunctionAt(addr(program, 0x13e40));
		check(storesConstAt(program, valueSel, 0x14480, 0),
			"cmpdi2(-1, 0) selects 0 (signed less)");
		check(storesConstAt(program, valueSel, 0x14484, 2),
			"cmpdi2(0, -1) selects 2 (signed greater)");
		check(storesConstAt(program, valueSel, 0x14488, 1),
			"cmpdi2(7, 7) selects 1 (equal)");
		check(storesConstAt(program, valueSel, 0x1448c, 2),
			"ucmpdi2(max, 0) selects 2 (unsigned greater)");
		check(storesConstAt(program, valueSel, 0x14490, 0),
			"ucmpdi2(0, max) selects 0 (unsigned less)");
		check(storesConstAt(program, valueSel, 0x14494, 1),
			"ucmpdi2(7, 7) selects 1 (equal)");
		check(storesConstAt(program, valueSel, 0x14498, 0),
			"gh_lt64(0, -1) selects 0 (signed: 0 is not < -1)");
		check(storesConstAt(program, valueSel, 0x1449c, 1),
			"gh_ult64(0, max) selects 1 (unsigned: 0 < max)");
		check(!hasCallTo(program, valueSel, 0x11a20) &&
			!hasCallTo(program, valueSel, 0x11a40) &&
			!hasCallTo(program, valueSel, 0x11560) &&
			!hasCallTo(program, valueSel, 0x11550),
			"value-selection calls are folded away (payloads inlined)");

		// GCC shift constant edges: the recovered GCC shift payloads must
		// reproduce the committed bodies' machine behavior at the edges the
		// spec and a shared count&63 payload get wrong: count >= 32 moves
		// the surviving word with count&31 (so 64 and 96 keep the high word
		// in place instead of yielding 0), and count=0xffffffff takes the
		// small arm with the same masking. Slots 0x144a0+ (low, high per
		// site, groups of three sites per count).
		Function shiftConsumer = listing.getFunctionAt(addr(program, 0x20000));
		long[][] edges = {
			// count 64: large arm, shift 0
			{ 0x144a0, 0x11223344L }, { 0x144a4, 0 },        // lshrdi3(a, 64)
			{ 0x144a8, 0x11223344L }, { 0x144ac, 0 },        // ashrdi3(a, 64)
			{ 0x144b0, 0 }, { 0x144b4, 0x55667788L },        // ashldi3(a, 64)
			// count 65: large arm, shift 1
			{ 0x144b8, 0x089119a2L }, { 0x144bc, 0 },        // lshrdi3(a, 65)
			{ 0x144c0, 0x089119a2L }, { 0x144c4, 0 },        // ashrdi3(a, 65)
			{ 0x144c8, 0 }, { 0x144cc, 0xaaccef10L },       // ashldi3(a, 65)
			// count 96: large arm, shift 0 again (not zero output)
			{ 0x144d0, 0x11223344L }, { 0x144d4, 0 },        // lshrdi3(a, 96)
			{ 0x144d8, 0x11223344L }, { 0x144dc, 0 },        // ashrdi3(a, 96)
			{ 0x144e0, 0 }, { 0x144e4, 0x55667788L },        // ashldi3(a, 96)
			// count -1: small arm (32-(-1)=33>0), shifts by 31 and 1
			{ 0x144e8, 0x22446688L }, { 0x144ec, 0 },        // lshrdi3(a, -1)
			{ 0x144f0, 0x22446688L }, { 0x144f4, 0 },        // ashrdi3(a, -1)
			{ 0x144f8, 0 }, { 0x144fc, 0x2ab33bc4L },       // ashldi3(a, -1)
			// ashrdi3 with negative input at count 64 replicates the sign
			{ 0x14500, 0x9abcdef0L }, { 0x14504, 0xffffffffL } }; // ashrdi3(neg, 64)
		for (long[] e : edges) {
			check(storesConstAt(program, shiftConsumer, e[0], e[1]),
				"GCC shift edge slot 0x" + Long.toHexString(e[0]) + " == 0x" +
					Long.toHexString(e[1]) + " (true committed-body result)");
		}
		check(!hasCallTo(program, shiftConsumer, 0x11960) &&
			!hasCallTo(program, shiftConsumer, 0x119a0) &&
			!hasCallTo(program, shiftConsumer, 0x119e0),
			"GCC shift consumer's calls are folded away (payloads inlined)");

		// Typed 32-vs-64 ABI on the recovered stripped bodies: 8-byte joined
		// results/operands, 4-byte int compare results, 4-byte uint shift
		// counts, unsigned u-family parameters.
		checkAbi(program, listing, 0x11a80, "recovered muldi3", "longlong", "longlong",
			"longlong");
		checkAbi(program, listing, 0x11960, "recovered lshrdi3", "ulonglong", "ulonglong",
			"uint");
		checkAbi(program, listing, 0x11a20, "recovered cmpdi2", "int", "longlong", "longlong");
		checkAbi(program, listing, 0x11a40, "recovered ucmpdi2", "int", "ulonglong", "ulonglong");
		checkAbi(program, listing, 0x12240, "recovered divdi3", "longlong", "longlong",
			"longlong");
		checkAbi(program, listing, 0x128e0, "recovered umoddi3", "ulonglong", "ulonglong",
			"ulonglong");
		checkAbi(program, listing, 0x13000, "recovered udivdi3", "ulonglong", "ulonglong",
			"ulonglong");
		checkAbi(program, listing, 0x136a0, "recovered moddi3", "longlong", "longlong",
			"longlong");

		// The trapping *v helpers: typed contract, call retained, and the
		// abort() control flow stays observable in each decompiled body.
		Function addvBody = listing.getFunctionAt(addr(program, 0x11bb0));
		checkAbi(program, listing, 0x11bb0, "addvdi3", "longlong", "longlong", "longlong");
		check(addvBody != null && addvBody.getCallFixup() == null,
			"stripped addvdi3 keeps its call (no fixup)");
		check(hasCallTo(program, addvBody, 0x11e60),
			"addvdi3 body keeps the abort() call observable (control flow not deleted)");
		checkAbi(program, listing, 0x11be0, "subvdi3", "longlong", "longlong", "longlong");
		Function subvBody = listing.getFunctionAt(addr(program, 0x11be0));
		check(subvBody != null && subvBody.getCallFixup() == null &&
			hasCallTo(program, subvBody, 0x11e60),
			"stripped subvdi3 keeps its call and abort() control flow");
		checkAbi(program, listing, 0x11c10, "negvdi2", "longlong", "longlong");
		Function negvBody = listing.getFunctionAt(addr(program, 0x11c10));
		check(negvBody != null && negvBody.getCallFixup() == null &&
			hasCallTo(program, negvBody, 0x11e60),
			"stripped negvdi2 keeps its call and abort() control flow");
		checkAbi(program, listing, 0x11e80, "mulvdi3", "longlong", "longlong", "longlong");

		// Verify dependency structure directly: each dependency body contains
		// many instructions. Recognize GCC register-restore helpers from their
		// bodies. umodsi3 retains its relocated prologue/epilogue and calls into
		// udivsi3/mulsi3. The si3 bodies decompile to arithmetic.
		check(instructionCount(program, 0x12100) > 10 && instructionCount(program, 0x12140) > 10 &&
			instructionCount(program, 0x12180) > 10,
			"udivsi3/umodsi3/mulsi3 dependency bodies are real code, not stubs");
		Function ret20 = listing.getFunctionAt(addr(program, 0x12200));
		check(ret20 != null && ret20.getName().equals("__return_r20_r31") && ret20.isInline(),
			"real __return_r20_r31 body recognized by the analyzer (got " +
				(ret20 == null ? "<none>" : ret20.getName()) + ")");
		Function ret24 = listing.getFunctionAt(addr(program, 0x121c0));
		check(ret24 != null && ret24.getName().equals("__return_r24_r31") && ret24.isInline(),
			"real __return_r24_r31 body recognized by the analyzer (got " +
				(ret24 == null ? "<none>" : ret24.getName()) + ")");
		Function umodsi = listing.getFunctionAt(addr(program, 0x12140));
		check(hasCallTo(program, umodsi, 0x12100) && hasCallTo(program, umodsi, 0x12180),
			"real ___umodsi3 keeps its calls to ___udivsi3 and ___mulsi3");
		// Spill/reload pairs legitimately disappear from optimized p-code.
		// Execute the real body and its division/multiply dependencies to
		// check unsigned results and restored caller state instead.
		check(execUmodSi3(program),
			"real ___umodsi3 executes unsigned remainder and restores sp/lp");

		// ABI-clobber CSE independence: two IDENTICAL gh_add64 calls with
		// identical constants must keep two independent opaque clobber
		// results - the decompiler must never equate the two calls'
		// killed-register effects, and the two escaping stores must observe
		// distinct values.
		Function clobWitness = listing.getFunctionAt(addr(program, 0x10600));
		int r2Clobbers = countCallotherWrites(program, clobWitness, "r2");
		check(r2Clobbers == 2, "two identical helper calls keep two independent r2 " +
			"__v850_abi_clobber results (got " + r2Clobbers + ")");
		check(clobberStoresIndependent(program, clobWitness, 0x14510, 0x14514),
			"identical __v850_abi_clobber results are not CSE-equated (independent " +
				"values stored to 0x14510/0x14514)");
		Function mulsi = listing.getFunctionAt(addr(program, 0x12180));
		check(countOps(program, mulsi, PcodeOp.INT_MULT, 4) >= 1,
			"real ___mulsi3 decompiles to INT_MULT arithmetic (mulh digits)");
		Function udivsi = listing.getFunctionAt(addr(program, 0x12100));
		check(countOps(program, udivsi, PcodeOp.INT_SUB, 4) >= 1 &&
			countOps(program, udivsi, PcodeOp.INT_RIGHT, 4) >= 1,
			"real ___udivsi3 decompiles to shift-subtract loop arithmetic");

		// The clz table content is the GCC bit-length table (guards the
		// floor(log2) regression that corrupts the division normalization).
		byte[] clz = new byte[256];
		program.getMemory().getBytes(addr(program, 0x12000), clz);
		int[] edge = { 0, 1, 2, 3, 4, 7, 8, 15, 16, 31, 32, 63, 64, 127, 128, 255 };
		int[] want = { 0, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8 };
		boolean clzOk = true;
		for (int i = 0; i < edge.length; i++) {
			clzOk &= (clz[edge[i]] & 0xff) == want[i];
		}
		check(clzOk, "___clz_tab holds GCC bit lengths 0,1,2,2,3,...,8 (t[128..255]=8)");

		// Stripped near-misses and regressed mutants of real bodies must
		// retain FUN_ names and calls without fixups or inlining. This applies
		// to branch-predicate and branch-constant mutants and the
		// preserved-register side-effect mutant.
		long[] nearMisses = { 0x13d00, 0x13d20, 0x13d40, 0x13d80, 0x13da0, 0x12f60, 0x12fa0,
			0x12fc0, 0x12ff0, 0x13dc0, 0x13e00 };
		for (long nm : nearMisses) {
			Function f = listing.getFunctionAt(addr(program, nm));
			check(f != null && f.getCallFixup() == null && !f.isInline() &&
				f.getName().startsWith("FUN_"),
				"stripped body 0x" + Long.toHexString(nm) + " NOT recovered (got " +
					(f == null ? "<none>" : f.getName() + "/" + f.getCallFixup()) + ")");
		}
	}

	// ------------------------------------------------------------------
	// Assertion helpers.
	// ------------------------------------------------------------------

	private boolean hasReference(ProgramDB program, long from, long to) {
		for (Reference ref : program.getReferenceManager().getReferencesFrom(addr(program, from))) {
			if (ref.getToAddress().equals(addr(program, to)) &&
				ref.getReferenceType().isCall()) {
				return true;
			}
		}
		return false;
	}


	private static final long ENTRY_SP = 0x3fff0;
	private static final long RETURN_PC = 0x3f000;

	private EmulatorHelper machine(ProgramDB program, long entry) {
		EmulatorHelper emu = new EmulatorHelper(program);
		emu.writeRegister("PC", entry);
		emu.writeRegister("PSW", 0);
		emu.writeRegister("sp", ENTRY_SP);
		emu.writeRegister("ll_valid", 0);
		emu.writeRegister("ll_addr", 0);
		emu.writeRegister("lp", RETURN_PC);
		return emu;
	}

	private void runToReturn(EmulatorHelper emu) throws Exception {
		for (int steps = 0; steps < 4096; steps++) {
			if (emu.readRegister("PC").longValue() == RETURN_PC) return;
			if (!emu.step(monitor)) {
				throw new IllegalStateException("helper machine execution: " + emu.getLastError());
			}
		}
		throw new IllegalStateException("helper machine failed to return");
	}

	private long readWord(ProgramDB program, EmulatorHelper emu, long address) throws Exception {
		byte[] bytes = emu.readMemory(addr(program, address), 4);
		long value = 0;
		for (int i = 0; i < 4; i++) value |= (bytes[i] & 0xffL) << (8 * i);
		return value;
	}

	private boolean execConsumerSp(ProgramDB program, long entry, long pointerSlot,
			long valueSlot, long frameSize, long argument) throws Exception {
		EmulatorHelper emu = machine(program, entry);
		try {
			emu.writeRegister("r20", 0x14000);
			emu.writeRegister("r6", argument);
			runToReturn(emu);
			return readWord(program, emu, pointerSlot) == ENTRY_SP - frameSize &&
				readWord(program, emu, valueSlot) == argument &&
				emu.readRegister("sp").longValue() == ENTRY_SP &&
				emu.readRegister("lp").longValue() == RETURN_PC;
		}
		finally { emu.dispose(); }
	}

	private boolean execCopyConsumer(ProgramDB program, long entry, int source,
			int destination, int slot, int count) throws Exception {
		EmulatorHelper emu = machine(program, entry);
		try {
			// Poison the copied range and its guard words independently of
			// source data, so skipped stores and off-by-one writes are visible.
			byte[] poison = new byte[count * 4 + 8];
			java.util.Arrays.fill(poison, (byte) 0xa5);
			for (int call = 0; call < 2; call++) {
				emu.writeMemory(addr(program, destination + call * 0x80 - 4), poison);
			}
			runToReturn(emu);
			for (int call = 0; call < 2; call++) {
				long target = destination + call * 0x80;
				if (readWord(program, emu, slot + call * 8) != target ||
					readWord(program, emu, slot + call * 8 + 4) != source ||
					readWord(program, emu, target - 4) != 0xa5a5a5a5L ||
					readWord(program, emu, target + count * 4) != 0xa5a5a5a5L) {
					return false;
				}
				for (int word = 0; word < count; word++) {
					if (readWord(program, emu, target + word * 4) !=
						readWord(program, emu, source + word * 4)) return false;
				}
			}
			return emu.readRegister("sp").longValue() == ENTRY_SP &&
				emu.readRegister("lp").longValue() == RETURN_PC;
		}
		finally { emu.dispose(); }
	}

	private boolean execUmodSi3(ProgramDB program) throws Exception {
		long[][] inputs = {{37, 5}, {0, 7}, {0xffffffffL, 3},
			{0x80000000L, 0x7fffffffL}, {0xffffffffL, 0x80000000L},
			{0xffffffffL, 0xffffffffL}, {0xffffffffL, 1}};
		for (long[] input : inputs) {
			EmulatorHelper emu = machine(program, 0x12140);
			try {
				emu.writeRegister("r6", input[0]);
				emu.writeRegister("r7", input[1]);
				runToReturn(emu);
				if ((emu.readRegister("r10").longValue() & 0xffffffffL) != input[0] % input[1] ||
					emu.readRegister("sp").longValue() != ENTRY_SP ||
					emu.readRegister("lp").longValue() != RETURN_PC ||
					readWord(program, emu, ENTRY_SP - 4) != RETURN_PC) {
					println(String.format("umodsi(%08x,%08x): r10=%08x r6=%08x r7=%08x sp=%08x lp=%08x saved-lp=%08x",
						input[0], input[1], emu.readRegister("r10").longValue(),
						emu.readRegister("r6").longValue(), emu.readRegister("r7").longValue(),
						emu.readRegister("sp").longValue(), emu.readRegister("lp").longValue(),
						readWord(program, emu, ENTRY_SP - 4)));
					return false;
				}
			}
			finally { emu.dispose(); }
		}
		return true;
	}

	private boolean storesConstSpDelta(ProgramDB program, Function function, long expected) {
		PcodeOp[] ops = decompiledPcode(program, function);
		if (ops == null) return false;
		for (PcodeOp op : ops) {
			if (op.getOpcode() != PcodeOp.STORE) continue;
			Long delta = spOffset(program, op.getInput(2), 0);
			if (delta != null && delta == expected) return true;
		}
		return false;
	}

	/**
	 * Counts CALLOTHER user-ops writing the named register in the
	 * decompiled function. The injected payloads model killed-by-call
	 * registers as opaque __v850_abi_clobber CALLOTHERs; a correct
	 * decompiler must keep one per executed call site (each result is
	 * consumed by its store) and must never common them up.
	 */
	private int countCallotherWrites(ProgramDB program, Function f, String reg) {
		if (f == null) {
			return -1;
		}
		PcodeOp[] ops = decompiledPcode(program, f);
		if (ops == null) {
			return -1;
		}
		Varnode regVn = registerVarnode(program, reg);
		int n = 0;
		for (PcodeOp op : ops) {
			if (op.getOpcode() == PcodeOp.CALLOTHER && op.getOutput() != null &&
				op.getOutput().getAddress().equals(regVn.getAddress()) &&
				op.getOutput().getSize() == regVn.getSize()) {
				n++;
			}
		}
		return n;
	}

	/**
	 * True when the values stored to the two absolute RAM slots trace to
	 * DIFFERENT varnodes (following one COPY level, as RuleStoreVarnode
	 * rewrites absolute stores into COPYs of the stored varnode). Two
	 * identical calls must produce two independent opaque results; a single
	 * shared varnode feeding both stores is the false CSE equality.
	 */
	private boolean clobberStoresIndependent(ProgramDB program, Function f, long slotA, long slotB) {
		if (f == null) {
			return false;
		}
		PcodeOp[] ops = decompiledPcode(program, f);
		if (ops == null) {
			return false;
		}
		Varnode va = null;
		Varnode vb = null;
		AddressSpace ram = program.getAddressFactory().getDefaultAddressSpace();
		for (PcodeOp op : ops) {
			long slot;
			Varnode value;
			if (op.getOpcode() == PcodeOp.STORE && op.getInput(1).isConstant()) {
				slot = op.getInput(1).getOffset();
				value = op.getInput(2);
			}
			else if (op.getOpcode() == PcodeOp.COPY && op.getOutput() != null &&
				op.getOutput().getAddress().getAddressSpace().equals(ram)) {
				slot = op.getOutput().getOffset();
				value = op.getInput(0);
			}
			else continue;
			if (slot != slotA && slot != slotB) continue;
			for (int depth = 0; depth < 16 && value.getDef() != null &&
				value.getDef().getOpcode() == PcodeOp.COPY; depth++) {
				value = value.getDef().getInput(0);
			}
			// Ignore artificial RAM self-copies. Retain executed call results.
			if (value.getDef() == null || value.getDef().getOpcode() != PcodeOp.CALLOTHER) continue;
			if (slot == slotA) va = value;
			else vb = value;
		}
		// Varnode.equals compares only space/offset/size, so two distinct
		// defs of the same register would compare equal. Compare by object
		// identity instead: each def is its own VarnodeAST node, and a
		// CSE-merged pair feeds both stores from the one shared node.
		return va != null && vb != null && va != vb;
	}

	/** Resolve SP offsets through SSA arithmetic on the entry SP. */
	private Long spOffset(ProgramDB program, Varnode value, int depth) {
		if (depth > 32) return null;
		PcodeOp def = value.getDef();
		if (def == null) {
			return value.getAddress().equals(program.getRegister("sp").getAddress()) ? 0L : null;
		}
		int opcode = def.getOpcode();
		if (opcode == PcodeOp.COPY || opcode == PcodeOp.CAST) {
			return spOffset(program, def.getInput(0), depth + 1);
		}
		if (opcode == PcodeOp.INT_ADD || opcode == PcodeOp.PTRSUB || opcode == PcodeOp.INT_SUB) {
			Varnode base = def.getInput(0), offset = def.getInput(1);
			if (opcode == PcodeOp.INT_ADD && base.isConstant()) {
				Varnode swap = base; base = offset; offset = swap;
			}
			if (!offset.isConstant()) return null;
			Long parent = spOffset(program, base, depth + 1);
			if (parent == null) return null;
			long delta = (int) offset.getOffset();
			return parent + (opcode == PcodeOp.INT_SUB ? -delta : delta);
		}
		return null;
	}

	/**
	 * True when a constant reaches an escaping RAM slot. Pointer constants may
	 * be expressed as PTRSUB(0,address), including as the RAM varnode's defining
	 * operation, rather than a literal COPY. Inspect the actual expression.
	 */
	private boolean storesConstAt(ProgramDB program, Function f, long slotAddr, long expected) {
		if (f == null) {
			return false;
		}
		PcodeOp[] ops = decompiledPcode(program, f);
		if (ops == null) {
			return false;
		}
		Varnode slot = new Varnode(addr(program, slotAddr), 4);
		for (PcodeOp op : ops) {
			if (op.getOpcode() == PcodeOp.STORE) {
				Varnode address = op.getInput(1);
				Varnode value = op.getInput(2);
				Long addressValue = constantValue(address, 0);
				Long storedValue = constantValue(value, 0);
				if (addressValue != null && addressValue.longValue() == slotAddr &&
					storedValue != null && storedValue.longValue() == expected) {
					return true;
				}
			}
			else {
				Varnode out = op.getOutput();
				Long value = constantValue(out, 0);
				if (out != null && out.getSize() == 4 &&
					out.getAddress().equals(slot.getAddress()) && value != null &&
					value.longValue() == expected) {
					return true;
				}
			}
		}
		return false;
	}

	private Long constantValue(Varnode value, int depth) {
		if (value == null || depth > 16) return null;
		if (value.isConstant()) return value.getOffset();
		PcodeOp def = value.getDef();
		if (def == null) return null;
		int opcode = def.getOpcode();
		if (opcode == PcodeOp.COPY || opcode == PcodeOp.CAST) {
			return constantValue(def.getInput(0), depth + 1);
		}
		if (opcode == PcodeOp.PTRSUB || opcode == PcodeOp.INT_ADD) {
			Long base = constantValue(def.getInput(0), depth + 1);
			Long offset = constantValue(def.getInput(1), depth + 1);
			if (base != null && offset != null) return (base + offset) & 0xffffffffL;
		}
		return null;
	}

	private boolean callsCopyWithPointers(ProgramDB program, Function caller, long helper,
			int source, int destination) {
		PcodeOp[] ops = decompiledPcode(program, caller);
		if (ops == null) return false;
		int calls = 0;
		int destinations = 0;
		for (PcodeOp op : ops) {
			if (op.getOpcode() != PcodeOp.CALL ||
				!op.getInput(0).getAddress().equals(addr(program, helper))) continue;
			if (op.getNumInputs() != 3) return false;
			Long actualDestination = constantValue(op.getInput(1), 0);
			Long actualSource = constantValue(op.getInput(2), 0);
			if (actualSource == null || actualSource.longValue() != source ||
				actualDestination == null) return false;
			if (actualDestination.longValue() == destination) destinations |= 1;
			else if (actualDestination.longValue() == destination + 0x80) destinations |= 2;
			else return false;
			calls++;
		}
		return calls == 2 && destinations == 3;
	}

	/** Defined instructions within the first 0x40 bytes at an entry. */
	private int instructionCount(ProgramDB program, long entry) {
		int count = 0;
		Iterator<ghidra.program.model.listing.Instruction> it = program.getListing()
			.getInstructions(new AddressSet(addr(program, entry), addr(program, entry + 0x40)),
				true);
		while (it.hasNext()) {
			it.next();
			count++;
		}
		return count;
	}

	/** Number of matching decompiled ops with big-enough first inputs. */
	private int countOps(ProgramDB program, Function f, int opcode, int minInputSize) {
		return countOps(program, f, opcode, minInputSize, false);
	}

	/**
	 * Number of matching decompiled ops; with {@code variableSecondInput}
	 * only ops whose second input is non-constant count, which separates
	 * real variable-count shifts from the constant <<32 join operations in
	 * injected fixup payloads.
	 */
	private int countOps(ProgramDB program, Function f, int opcode, int minInputSize,
			boolean variableSecondInput) {
		if (f == null) {
			return 0;
		}
		PcodeOp[] ops = decompiledPcode(program, f);
		if (ops == null) {
			return 0;
		}
		int count = 0;
		for (PcodeOp op : ops) {
			if (op.getOpcode() != opcode) {
				continue;
			}
			Varnode in0 = op.getInput(0);
			if (in0 == null || in0.getSize() < minInputSize) {
				continue;
			}
			if (variableSecondInput) {
				Varnode in1 = op.getInput(1);
				if (in1 == null || in1.isConstant()) {
					continue;
				}
			}
			count++;
		}
		return count;
	}

	private int countOpsDynamicCount(ProgramDB program, Function f, int opcode, int minInputSize) {
		return countOps(program, f, opcode, minInputSize, true);
	}

	/**
	 * True when a CALL to the given entry address survives decompilation:
	 * direct CALL input zero is a destination-address varnode in code space.
	 */
	private boolean hasCallTo(ProgramDB program, Function f, long target) {
		if (f == null) {
			return false;
		}
		PcodeOp[] ops = decompiledPcode(program, f);
		if (ops == null) {
			return false;
		}
		for (PcodeOp op : ops) {
			if (op.getOpcode() != PcodeOp.CALL) {
				continue;
			}
			Varnode t = op.getInput(0);
			if (t != null && t.getAddress().equals(addr(program, target))) {
				return true;
			}
		}
		return false;
	}

	/** Collects (and caches) the decompiled p-code of a function. */
	private PcodeOp[] decompiledPcode(ProgramDB program, Function f) {
		if (f == null) {
			return null;
		}
		Long key = Long.valueOf(f.getEntryPoint().getOffset());
		PcodeOp[] cached = pcodeCache.get(key);
		if (cached != null) {
			return cached;
		}
		DecompInterface ifc = openDecompiler(program);
		try {
			DecompileResults results = ifc.decompileFunction(f, 120, TaskMonitor.DUMMY);
			if (!results.decompileCompleted() || results.getHighFunction() == null) {
				return null;
			}
			List<PcodeOp> ops = new ArrayList<>();
			Iterator<PcodeOpAST> it = results.getHighFunction().getPcodeOps();
			while (it.hasNext()) {
				ops.add(it.next());
			}
			cached = ops.toArray(new PcodeOp[0]);
		}
		finally {
			ifc.dispose();
		}
		pcodeCache.put(key, cached);
		return cached;
	}

	private DecompInterface openDecompiler(ProgramDB program) {
		DecompInterface ifc = new DecompInterface();
		// Use Ghidra's ordinary defaults; a bare native interface otherwise
		// leaves readonly propagation disabled despite the GUI default.
		ifc.setOptions(new DecompileOptions());
		ifc.openProgram(program);
		return ifc;
	}

	private Varnode registerVarnode(ProgramDB program, String name) {
		ghidra.program.model.lang.Register r = program.getRegister(name);
		return new Varnode(r.getAddress(), r.getBitLength() / 8);
	}

	private static int typeSize(String name) {
		return name.equals("int") || name.equals("uint") ? 4 : 8;
	}

	/**
	 * Checks a recovered helper's ABI: the return type and every parameter
	 * must have the expected builtin type name (and width), proving real
	 * 32-vs-64-bit typing rather than Undefined fallbacks.
	 */
	private void checkAbi(ProgramDB program, Listing listing, long entry, String what,
			String retType, String... paramTypes) {
		Function f = listing.getFunctionAt(addr(program, entry));
		String got = "<none>";
		boolean ok = false;
		if (f != null) {
			got = describeSignature(f);
			ok = retType.equals(f.getReturnType().getName()) &&
				f.getReturnType().getLength() == typeSize(retType);
			Parameter[] ps = f.getParameters();
			ok &= ps.length == paramTypes.length;
			if (ok) {
				for (int i = 0; i < ps.length; i++) {
					ok &= paramTypes[i].equals(ps[i].getDataType().getName()) &&
						ps[i].getDataType().getLength() == typeSize(paramTypes[i]);
				}
			}
		}
		check(ok, what + " ABI is " + retType + "(" + String.join(",", paramTypes) + ") (got " +
			got + ")");
	}

	/** Width-only ABI check (for contracts whose signedness may vary). */
	private void checkAbiLengths(ProgramDB program, Listing listing, long entry, String what,
			int retLen, int... paramLens) {
		Function f = listing.getFunctionAt(addr(program, entry));
		String got = "<none>";
		boolean ok = false;
		if (f != null) {
			got = describeSignature(f);
			ok = f.getReturnType().getLength() == retLen;
			Parameter[] ps = f.getParameters();
			ok &= ps.length == paramLens.length;
			if (ok) {
				for (int i = 0; i < ps.length; i++) {
					ok &= ps[i].getDataType().getLength() == paramLens[i];
				}
			}
		}
		check(ok, what + " ABI is " + retLen + "-byte return with " + paramLens.length +
			" x 8-byte parameters (got " + got + ")");
	}

	private String describeSignature(Function f) {
		StringBuilder b = new StringBuilder(f.getReturnType().getName());
		b.append('(');
		for (Parameter p : f.getParameters()) {
			b.append(p.getDataType().getName()).append(',');
		}
		return b.append(')').toString();
	}
}
