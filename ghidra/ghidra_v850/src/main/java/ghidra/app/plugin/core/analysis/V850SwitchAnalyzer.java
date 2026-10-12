/* ###
 * IP: GHIDRA
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package ghidra.app.plugin.core.analysis;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import ghidra.app.cmd.label.AddLabelCmd;
import ghidra.app.plugin.core.analysis.AutoAnalysisManager;
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.services.AbstractAnalyzer;
import ghidra.app.services.AnalysisPriority;
import ghidra.app.services.AnalyzerType;
import ghidra.app.util.importer.MessageLog;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.data.ArrayDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.MutabilitySettingsDefinition;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.UnsignedShortDataType;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.CodeUnitIterator;
import ghidra.program.model.listing.CommentType;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.listing.Program;
import ghidra.program.model.lang.Register;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.pcode.Varnode;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Namespace;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;
import ghidra.util.Msg;
import ghidra.util.exception.CancelledException;
import ghidra.util.task.TaskMonitor;

/**
 * Recovers V850/RH850 switch dispatch sites and their jump tables during auto-analysis.
 *
 * <p>Four dispatch families are recognized, mirroring the classic V850/RH850 compiler idioms
 * (GHS MULTI, GCC, CC-RH):
 *
 * <ol>
 * <li><b>native switch</b> — {@code switch reg2} with a signed halfword offset table
 * immediately following the instruction; targets are relative to the table base scaled by
 * two; guarded by a range-check prefix ({@code cmp N, rX} + {@code bh default}, or
 * {@code addi -N, rX, r0} + {@code bc default}, plus the inverted {@code bnh}/{@code bnc}
 * body-branch forms whose fall-through continues at {@code jr default}).</li>
 * <li><b>direct jump table</b> — {@code jmp table[reg]} where the table entries are
 * themselves instructions (typically {@code jr} stubs), reached through
 * {@code shl 1|2, reg} index scaling.</li>
 * <li><b>loaded relative table</b> — {@code ld.b[bu]/ld.h[hu]} of signed or unsigned
 * elements followed by an element-base addition (constant register or the
 * {@code jmp base[reg]} displacement) and {@code jmp [reg]}.</li>
 * <li><b>loaded absolute table</b> — {@code ld.w} of absolute targets followed by
 * {@code jmp [reg]} (element base zero).</li>
 * </ol>
 *
 * <p>The index register is followed backwards through copies ({@code mov}), normalization
 * ({@code movea -minv, rSrc, rIdx}) and shifts; table and element bases are resolved with a
 * bounded constant tracker ({@code mov imm}, {@code movea}, {@code addi}, {@code add},
 * {@code jarl} link values). Candidates without a compiler range-check prefix, with tables
 * outside initialized memory, or with targets that do not land in executable initialized
 * memory are rejected unchanged — this keeps decoded data or partial code from being marked
 * as a switch. Pre-existing defined data and non-analysis symbols inside a table range are
 * never replaced, so the analyzer coexists with later manual curation (for example the
 * RecoverSwitchTables workflow).
 */
public class V850SwitchAnalyzer extends AbstractAnalyzer {

	private static final String NAME = "V850 Switch Analysis";
	private static final String DESCRIPTION = "Recovers V850/RH850 switch jump tables " +
		"(native switch, direct jump tables, loaded relative/absolute tables) including " +
		"bounds, default branches and case normalization.";

	private static final int MAX_TABLE_ENTRIES = Integer.MAX_VALUE;
	private static final int MAX_SLICE = 16;
	private static final int BOUND_BRANCH_WINDOW = 4;
	private static final int BOUND_VALUE_WINDOW = 3;
	private static final int NORMALIZE_WINDOW = 4;
	private static final int CONST_TRACK_LIMIT = 48;

	/** Dispatch families. */
	private enum Family {
		NATIVE_SWITCH, DIRECT_TABLE, LOADED_TABLE
	}

	private Program program;
	private Listing listing;

	public V850SwitchAnalyzer() {
		super(NAME, DESCRIPTION, AnalyzerType.INSTRUCTION_ANALYZER);
		setDefaultEnablement(true);
		setPriority(AnalysisPriority.CODE_ANALYSIS);
	}

	@Override
	public boolean canAnalyze(Program p) {
		return "v850".equalsIgnoreCase(p.getLanguage().getProcessor().toString());
	}

	@Override
	public boolean getDefaultEnablement(Program p) {
		return true;
	}

	@Override
	public boolean added(Program p, AddressSetView set, TaskMonitor monitor, MessageLog log)
			throws CancelledException {
		this.program = p;
		this.listing = p.getListing();
		int recovered = 0;
		try {
			InstructionIterator it = listing.getInstructions(set, true);
			while (it.hasNext()) {
				monitor.checkCancelled();
				Instruction insn = it.next();
				String mnem = insn.getMnemonicString().toLowerCase();
				if (!mnem.equals("switch") && !mnem.equals("jmp")) {
					continue;
				}
				if (!insn.getFlowType().isJump() || !insn.getFlowType().isComputed()) {
					continue;
				}
				if (hasComputedJumpRefs(insn)) {
					continue; // already recovered by this analyzer or by curation
				}
				try {
					if (recover(insn, monitor)) {
						recovered++;
					}
				}
				catch (CancelledException e) {
					throw e;
				}
				catch (Exception e) {
					Msg.debug(this, "switch recovery failed at " + insn.getAddress(), e);
				}
			}
		}
		finally {
			this.program = null;
			this.listing = null;
		}
		if (recovered > 0) {
			Msg.debug(this, "recovered " + recovered + " switch table(s)");
		}
		return true;
	}

	//==============================================================================================
	// Candidate model
	//==============================================================================================

	private class SwitchCase {
		final Family family;
		final Instruction dispatch;
		long lowcase = 0;
		int ncases;
		Address defaultAddr;
		Address tableAddr;
		int elementSize;
		boolean signedElements;
		long elementBase;
		int elementShift = 0;
		private Address[] decodedTargets;

		SwitchCase(Family family, Instruction dispatch) {
			this.family = family;
			this.dispatch = dispatch;
		}

		Address[] targets(Memory memory, TaskMonitor monitor) throws CancelledException {
			if (decodedTargets != null) {
				return decodedTargets;
			}
			try {
				Address[] out = new Address[ncases];
				for (int i = 0; i < ncases; i++) {
					monitor.checkCancelled();
					long targetOffset;
					if (family == Family.DIRECT_TABLE) {
						// entries are instructions: the target is the entry address itself
						targetOffset = (tableAddr.getOffset() + (long) i * elementSize) &
							0xffffffffL;
					}
					else {
						long element = readElement(memory,
							tableAddr.getNewAddress((tableAddr.getOffset() + (long) i * elementSize) &
								0xffffffffL), elementSize);
						if (signedElements) {
							int bits = elementSize * 8;
							if ((element & (1L << (bits - 1))) != 0) {
								element -= (1L << bits);
							}
						}
						long base =
							(family == Family.NATIVE_SWITCH) ? tableAddr.getOffset() : elementBase;
						targetOffset = (base + (element << elementShift)) & 0xffffffffL;
					}
					out[i] = tableAddr.getNewAddress(targetOffset);
				}
				decodedTargets = out;
				return decodedTargets;
			}
			catch (CancelledException e) {
				throw e;
			}
			catch (Exception e) {
				return null;
			}
		}
	}

	private static long readElement(Memory memory, Address addr, int size) throws Exception {
		switch (size) {
			case 1:
				return memory.getByte(addr) & 0xffL;
			case 2:
				return memory.getShort(addr) & 0xffffL;
			case 4:
				return memory.getInt(addr) & 0xffffffffL;
			default:
				throw new Exception("bad element size " + size);
		}
	}

	/** Backward-walk cursor over the instruction slice with the tracked index register. */
	private static class Cursor {
		final List<Instruction> slice;
		int pos;
		int reg;

		Cursor(List<Instruction> slice, int pos, int reg) {
			this.slice = slice;
			this.pos = pos;
			this.reg = reg;
		}

		Instruction peek() {
			return pos < slice.size() ? slice.get(pos) : null;
		}

		Instruction peekAt(int p) {
			return p >= 0 && p < slice.size() ? slice.get(p) : null;
		}
	}

	//==============================================================================================
	// Pattern matching
	//==============================================================================================

	private boolean recover(Instruction dispatch, TaskMonitor monitor) throws CancelledException {
		String mnem = dispatch.getMnemonicString().toLowerCase();
		SwitchCase cand;
		if (mnem.equals("switch")) {
			cand = matchSwitch(dispatch);
		}
		else {
			cand = matchJmp(dispatch);
		}
		if (cand == null || !validate(cand, monitor)) {
			return false;
		}
		apply(cand, monitor);
		return true;
	}

	/** Family 1: [movea -minv, rSrc, rIdx] [cmp N,rIdx | addi -N,rIdx,r0] bh/bc|bnh/bnc switch rIdx. */
	private SwitchCase matchSwitch(Instruction dispatch) {
		Register reg = getRegister(dispatch, 0);
		if (reg == null) {
			return null; // r0 reads-as-zero and exports a constant, never a live index
		}
		int idx = regIndex(reg);
		if (idx <= 0 || idx > 31) {
			return null;
		}
		SwitchCase cand = new SwitchCase(Family.NATIVE_SWITCH, dispatch);
		cand.tableAddr = dispatch.getMaxAddress().add(1);
		cand.elementSize = 2;
		cand.signedElements = true;
		cand.elementShift = 1;
		cand.elementBase = cand.tableAddr.getOffset();
		Cursor cur = new Cursor(buildSlice(dispatch), 0, idx);
		return matchBound(cand, cur) ? cand : null;
	}

	/** Families 2-4: jmp table[reg], jmp base[reg] or jmp [reg]. */
	private SwitchCase matchJmp(Instruction dispatch) {
		int nops = dispatch.getNumOperands();
		if (nops == 2) {
			Scalar disp = getScalar(dispatch, 0);
			Register reg = getRegister(dispatch, 1);
			if (disp == null || reg == null) {
				return null;
			}
			int idx = regIndex(reg);
			// A loaded table keeps its element base in the jmp displacement; a direct
			// jump table uses the displacement as the table address itself.
			SwitchCase loaded = matchLoaded(dispatch, idx);
			if (loaded != null) {
				// the jmp displacement is the element base; fold in any tracked
				// base register that was added between the load and the dispatch
				long dispBase = disp.getUnsignedValue() & 0xffffffffL;
				loaded.elementBase = (dispBase + loaded.elementBase) & 0xffffffffL;
				return loaded;
			}
			return matchDirect(dispatch, idx, disp.getUnsignedValue() & 0xffffffffL);
		}
		if (nops == 1) {
			Register reg = getRegister(dispatch, 0);
			if (reg == null) {
				return null;
			}
			return matchLoaded(dispatch, regIndex(reg));
		}
		return null;
	}

	/** Family 2: bound + shl 1|2, rIdx + jmp table[rIdx] with instruction entries. */
	private SwitchCase matchDirect(Instruction dispatch, int idx, long tableOffset) {
		if (idx <= 0 || idx > 31) {
			return null;
		}
		Cursor cur = new Cursor(buildSlice(dispatch), 0, idx);
		int shift = matchShl(cur);
		if (shift != 1 && shift != 2) {
			return null;
		}
		SwitchCase cand = new SwitchCase(Family.DIRECT_TABLE, dispatch);
		cand.elementSize = 1 << shift;
		cand.tableAddr = dispatch.getAddress().getNewAddress(tableOffset);
		return matchBound(cand, cur) ? cand : null;
	}

	/**
	 * Families 3-4: bound + [shl S,rIdx] + [add table,rIdx] + ld.b[bu]/ld.h[hu]/ld.w
	 * disp[rB],rIdx + [add elbase,rIdx] + jmp [rIdx] | jmp base[rIdx].
	 */
	private SwitchCase matchLoaded(Instruction dispatch, int idx) {
		if (idx <= 0 || idx > 31) {
			return null;
		}
		Cursor cur = new Cursor(buildSlice(dispatch), 0, idx);
		// optional element-base add immediately before the dispatch
		Long elbase = matchBaseAdd(cur);
		// required element load
		ElementLoad load = matchLoad(cur);
		if (load == null) {
			return null;
		}
		// table base: a nonzero load displacement is an absolute table address,
		// otherwise the table comes from a base add before the load
		Address tableAddr;
		if (load.disp != 0) {
			tableAddr = dispatch.getAddress().getNewAddress(load.disp & 0xffffffffL);
		}
		else {
			Long tableBase = matchBaseAdd(cur);
			if (tableBase == null) {
				return null;
			}
			tableAddr = dispatch.getAddress().getNewAddress(tableBase & 0xffffffffL);
		}
		// index scale: required for 2/4-byte elements, optional for byte tables
		if (load.size > 1) {
			int shift = matchShl(cur);
			if (shift < 0 || (1 << shift) != load.size) {
				return null;
			}
		}
		else {
			// byte tables are unscaled; a shift here would be a different idiom
			int shift = matchShl(cur);
			if (shift > 0) {
				return null;
			}
		}
		SwitchCase cand = new SwitchCase(Family.LOADED_TABLE, dispatch);
		cand.elementSize = load.size;
		cand.signedElements = load.signed;
		cand.elementBase = elbase != null ? elbase : 0L;
		cand.tableAddr = tableAddr;
		return matchBound(cand, cur) ? cand : null;
	}

	private static class ElementLoad {
		final int size;
		final boolean signed;
		final long disp;

		ElementLoad(int size, boolean signed, long disp) {
			this.size = size;
			this.signed = signed;
			this.disp = disp;
		}
	}

	private ElementLoad matchLoad(Cursor cur) {
		cur.pos = skipCopies(cur);
		Instruction insn = cur.peek();
		if (insn == null) {
			return null;
		}
		String m = insn.getMnemonicString().toLowerCase();
		int size;
		boolean signed;
		switch (m) {
			case "ld.b":
				size = 1;
				signed = true;
				break;
			case "ld.bu":
				size = 1;
				signed = false;
				break;
			case "ld.h":
				size = 2;
				signed = true;
				break;
			case "ld.hu":
				size = 2;
				signed = false;
				break;
			case "ld.w":
				size = 4;
				signed = false;
				break;
			default:
				return null;
		}
		if (insn.getNumOperands() != 3) {
			return null;
		}
		Scalar disp = getScalar(insn, 0);
		Register base = getRegister(insn, 1);
		Register dest = getRegister(insn, 2);
		if (disp == null || base == null || dest == null || regIndex(dest) != cur.reg) {
			return null;
		}
		cur.pos++;
		// load displacements are signed in the V850 encoding (tables may precede the load)
		return new ElementLoad(size, signed, disp.getSignedValue());
	}

	/**
	 * Matches an immediate or constant-register base addition, following the other
	 * operand as the index. Returns null without consuming an unproven addition.
	 */
	private Long matchBaseAdd(Cursor cur) {
		int p = skipCopies(cur);
		Instruction insn = cur.peekAt(p);
		if (insn == null) {
			return null;
		}
		String mnemonic = insn.getMnemonicString().toLowerCase();
		boolean addi = mnemonic.equals("addi") && insn.getNumOperands() == 3;
		if (!addi && !(mnemonic.equals("add") && insn.getNumOperands() == 2)) {
			return null;
		}
		Register dst = getRegister(insn, addi ? 2 : 1);
		if (dst == null || regIndex(dst) != cur.reg) {
			return null;
		}
		Scalar imm = getScalar(insn, 0);
		Long value;
		int index = cur.reg;
		if (imm != null) {
			value = imm.getSignedValue();
			if (addi) {
				Register src = getRegister(insn, 1);
				if (src == null) {
					return null;
				}
				index = regIndex(src);
			}
		}
		else {
			Register src = getRegister(insn, 0);
			if (src == null) {
				return null;
			}
			value = trackConstant(cur.slice, p + 1, regIndex(src));
			if (value == null) {
				value = trackConstant(cur.slice, p + 1, cur.reg);
				index = regIndex(src);
			}
		}
		if (value == null) {
			return null;
		}
		cur.reg = index;
		cur.pos = p + 1;
		return value;
	}

	/**
	 * Matches {@code shl S, rIdx}; returns S (>= 0) and consumes, or returns -1 without
	 * consuming.
	 */
	private int matchShl(Cursor cur) {
		int p = skipCopies(cur);
		Instruction insn = cur.peekAt(p);
		if (insn == null || !insn.getMnemonicString().equalsIgnoreCase("shl") ||
			insn.getNumOperands() != 2) {
			return -1;
		}
		Scalar amt = getScalar(insn, 0);
		Register dst = getRegister(insn, 1);
		if (amt == null || dst == null || regIndex(dst) != cur.reg) {
			return -1;
		}
		cur.pos = p + 1;
		return (int) amt.getUnsignedValue();
	}

	/**
	 * Bounded constant tracker: the value held by {@code reg} just before slice[pos] executes.
	 * Scans backwards for mov/movhi/movea/addi/add/jarl definitions; stops at unknown writers.
	 */
	private Long trackConstant(List<Instruction> slice, int usePos, int reg) {
		if (reg == 0) {
			return 0L; // reads-as-zero register
		}
		if (usePos >= slice.size()) {
			return null;
		}
		for (int p = usePos; p < Math.min(slice.size(), usePos + CONST_TRACK_LIMIT); p++) {
			Instruction insn = slice.get(p);
			String m = insn.getMnemonicString().toLowerCase();
			int nops = insn.getNumOperands();
			if (m.equals("mov") && nops == 2) {
				Register dst = getRegister(insn, 1);
				if (dst != null && regIndex(dst) == reg) {
					Scalar imm = getScalar(insn, 0);
					if (imm != null) {
						return imm.getUnsignedValue() & 0xffffffffL;
					}
					Register src = getRegister(insn, 0);
					return src != null ? trackConstant(slice, p + 1, regIndex(src)) : null;
				}
			}
			else if ((m.equals("movea") || m.equals("addi") || m.equals("movhi")) && nops == 3) {
				Scalar imm = getScalar(insn, 0);
				Register src = getRegister(insn, 1);
				Register dst = getRegister(insn, 2);
				if (imm != null && src != null && dst != null && regIndex(dst) == reg) {
					Long base = trackConstant(slice, p + 1, regIndex(src));
					long offset = imm.getSignedValue();
					if (m.equals("movhi")) {
						offset <<= 16;
					}
					return base == null ? null : (base + offset) & 0xffffffffL;
				}
			}
			else if (m.equals("add") && nops == 2) {
				Register a = getRegister(insn, 0);
				Register b = getRegister(insn, 1);
				Scalar imm = getScalar(insn, 0);
				if ((a != null || imm != null) && b != null && regIndex(b) == reg) {
					Long va = imm != null ? Long.valueOf(imm.getSignedValue()) :
						trackConstant(slice, p + 1, regIndex(a));
					Long vb = trackConstant(slice, p + 1, reg);
					return (va == null || vb == null) ? null : (va + vb) & 0xffffffffL;
				}
			}
			else if (m.equals("jarl") && nops == 2) {
				Register dst = getRegister(insn, 1);
				if (dst != null && regIndex(dst) == reg) {
					Address fall = insn.getFallThrough();
					return fall != null ? fall.getOffset() : insn.getMaxAddress().add(1).getOffset();
				}
			}
			if (writesReg(insn, reg)) {
				return null; // unrecognized writer reached first: value unknown
			}
		}
		return null;
	}

	/**
	 * Matches the range-check prefix: an unsigned conditional branch (bh/bnh/bc/bnc) near the
	 * dispatch, the cmp/addi providing the bound, and optional index normalization. Advances
	 * the cursor past everything matched.
	 */
	private boolean matchBound(SwitchCase cand, Cursor cur) {
		int start = skipCopies(cur);
		int limit = Math.min(cur.slice.size(), start + BOUND_BRANCH_WINDOW);
		for (int i = start; i < limit; i++) {
			Instruction branch = cur.slice.get(i);
			String m = branch.getMnemonicString().toLowerCase();
			// Unsigned higher forms pair with cmp bounds (N means N+1 cases);
			// carry forms pair with addi -N,rIdx,r0 bounds (N cases exactly).
			boolean takenOutOfRange; // true: branch taken when index out of range
			boolean addOne; // cmp semantics: bound N means N+1 cases
			switch (m) {
				case "bh":
					takenOutOfRange = true;
					addOne = true;
					break;
				case "bnh":
					takenOutOfRange = false;
					addOne = true;
					break;
				case "bc":
					takenOutOfRange = true;
					addOne = false;
					break;
				case "bnc":
					takenOutOfRange = false;
					addOne = false;
					break;
				default:
					continue;
			}
			Address defaultAddr = resolveDefault(cand.dispatch, branch, takenOutOfRange);
			if (defaultAddr == null) {
				continue;
			}
			int vend = Math.min(cur.slice.size(), i + 1 + BOUND_VALUE_WINDOW);
			for (int j = i + 1; j < vend; j++) {
				Long bound = boundValue(cur.slice, j, cur.reg, addOne);
				if (bound == null) {
					continue;
				}
				// instructions between the dispatch and the bound value must not rewrite
				// the tracked index register
				if (spoiledBetween(cur.slice, start, j, cur.reg)) {
					continue;
				}
				cand.ncases = (int) (bound + (addOne ? 1 : 0));
				cand.defaultAddr = defaultAddr;
				matchNormalize(cand, cur.slice, j + 1, cur.reg);
				cur.pos = j + 1;
				return true;
			}
		}
		return false;
	}

	/** Bound from cmp N,rIdx / cmp rN,rIdx, or from addi -N,rIdx,r0 (no +1). */
	private Long boundValue(List<Instruction> slice, int pos, int idx, boolean addOne) {
		Instruction insn = slice.get(pos);
		String m = insn.getMnemonicString().toLowerCase();
		if (m.equals("cmp") && insn.getNumOperands() == 2) {
			Register dst = getRegister(insn, 1);
			if (dst == null || regIndex(dst) != idx) {
				return null;
			}
			Scalar imm = getScalar(insn, 0);
			if (imm != null) {
				long v = imm.getSignedValue();
				return (v >= 0 && v + (addOne ? 1 : 0) <= MAX_TABLE_ENTRIES) ? v : null;
			}
			Register reg = getRegister(insn, 0);
			if (reg != null) {
				Long v = trackConstant(slice, pos, regIndex(reg));
				if (v != null && v >= 0 && v + (addOne ? 1 : 0) <= MAX_TABLE_ENTRIES) {
					return v;
				}
			}
			return null;
		}
		if (!addOne && m.equals("addi") && insn.getNumOperands() == 3) {
			Scalar imm = getScalar(insn, 0);
			Register src = getRegister(insn, 1);
			Register dst = getRegister(insn, 2);
			if (imm == null || src == null || dst == null || regIndex(src) != idx ||
				regIndex(dst) != 0) {
				return null;
			}
			long v = -imm.getSignedValue();
			return (v >= 1 && v <= MAX_TABLE_ENTRIES) ? v : null;
		}
		return null;
	}

	/**
	 * Default-target resolution. Out-of-range forms (bh/bc) branch directly to the default.
	 * Body forms (bnh/bnc) branch to the dispatch site and fall through to the default,
	 * possibly through a {@code jr default}.
	 */
	private Address resolveDefault(Instruction dispatch, Instruction branch, boolean takenOutOfRange) {
		Address target = flowTarget(branch);
		if (target == null) {
			return null;
		}
		if (takenOutOfRange) {
			return target;
		}
		// body-branch: its target must not lie past the dispatch
		if (target.compareTo(dispatch.getAddress()) > 0) {
			return null;
		}
		Address fall = branch.getMaxAddress().add(1);
		Instruction at = listing.getInstructionAt(fall);
		if (at != null && at.getMnemonicString().equalsIgnoreCase("jr")) {
			Address jrTarget = flowTarget(at);
			if (jrTarget != null) {
				return jrTarget;
			}
		}
		return fall;
	}

	/** Optional movea/add-immediate normalization sets the original case-value origin. */
	private void matchNormalize(SwitchCase cand, List<Instruction> slice, int from, int index) {
		int limit = Math.min(slice.size(), from + NORMALIZE_WINDOW);
		for (int k = from; k < limit; k++) {
			Instruction insn = slice.get(k);
			String mnemonic = insn.getMnemonicString().toLowerCase();
			boolean movea = mnemonic.equals("movea") && insn.getNumOperands() == 3;
			boolean add = mnemonic.equals("add") && insn.getNumOperands() == 2;
			if (movea || add) {
				Scalar imm = getScalar(insn, 0);
				Register src = getRegister(insn, 1);
				Register dst = getRegister(insn, movea ? 2 : 1);
				if (imm != null && src != null && dst != null && regIndex(dst) == index) {
					long minv = -imm.getSignedValue();
					if (minv != 0 && Math.abs(minv) < 0x10000L) {
						cand.lowcase = minv;
					}
					return;
				}
			}
			if (writesReg(insn, index)) {
				return;
			}
		}
	}

	/** Advances past mov rSrc, rIdx copies of the tracked register. */
	private int skipCopies(Cursor cur) {
		int pos = cur.pos;
		while (pos < cur.slice.size()) {
			Instruction insn = cur.slice.get(pos);
			if (insn.getMnemonicString().equalsIgnoreCase("mov") && insn.getNumOperands() == 2) {
				Register src = getRegister(insn, 0);
				Register dst = getRegister(insn, 1);
				if (src != null && dst != null && regIndex(dst) == cur.reg) {
					cur.reg = regIndex(src);
					pos++;
					continue;
				}
			}
			break;
		}
		cur.pos = pos;
		return pos;
	}

	/** True when any instruction in [from,to) writes the tracked register. */
	private boolean spoiledBetween(List<Instruction> slice, int from, int to, int reg) {
		for (int i = from; i < Math.min(to, slice.size()); i++) {
			if (writesReg(slice.get(i), reg)) {
				return true;
			}
		}
		return false;
	}

	//==============================================================================================
	// Slice construction
	//==============================================================================================

	/**
	 * Instructions flowing into the dispatch, nearest first, following fall-through and
	 * conditional-branch references only.
	 */
	private List<Instruction> buildSlice(Instruction dispatch) {
		List<Instruction> slice = new ArrayList<>();
		Instruction cur = dispatch;
		Function fn = program.getFunctionManager().getFunctionContaining(dispatch.getAddress());
		for (int i = 0; i < MAX_SLICE; i++) {
			Instruction prev = previousInstruction(cur);
			if (prev == null || prev.getAddress().compareTo(cur.getAddress()) >= 0) {
				break;
			}
			if (fn != null && !fn.getBody().contains(prev.getAddress())) {
				break;
			}
			if (isFlowTarget(prev)) {
				break; // a label inside the prefix: the range check is not guaranteed
			}
			slice.add(prev);
			cur = prev;
		}
		return slice;
	}

	private Instruction previousInstruction(Instruction cur) {
		Address fallFrom = cur.getFallFrom();
		if (fallFrom != null) {
			Instruction p = listing.getInstructionContaining(fallFrom);
			if (p != null) {
				return p;
			}
		}
		ReferenceIterator it = cur.getReferenceIteratorTo();
		while (it.hasNext()) {
			Reference ref = it.next();
			if (ref.getReferenceType().isConditional() && ref.getFromAddress()
					.compareTo(cur.getAddress()) < 0) {
				Instruction p = listing.getInstructionContaining(ref.getFromAddress());
				if (p != null) {
					return p;
				}
			}
		}
		return null;
	}

	/** Any jump reference into this instruction (other than fall-through, which is not a ref). */
	private boolean isFlowTarget(Instruction insn) {
		ReferenceIterator it = insn.getReferenceIteratorTo();
		while (it.hasNext()) {
			Reference ref = it.next();
			if (ref.getReferenceType().isJump() &&
				ref.getFromAddress().compareTo(insn.getAddress()) < 0) {
				return true;
			}
		}
		return false;
	}

	//==============================================================================================
	// Validation
	//==============================================================================================

	private boolean validate(SwitchCase cand, TaskMonitor monitor) throws CancelledException {
		monitor.checkCancelled();
		if (cand.ncases < 1) {
			return false;
		}
		Memory memory = program.getMemory();
		Address table = cand.tableAddr;
		MemoryBlock block = memory.getBlock(table);
		if (block == null || !block.isInitialized() || block.isExternalBlock() ||
			(table.getOffset() % cand.elementSize) != 0) {
			return false;
		}
		if (cand.family == Family.DIRECT_TABLE && !block.isExecute()) {
			return false;
		}
		Address tableEnd = table.add(cand.ncases * (long) cand.elementSize - 1);
		if (!block.contains(tableEnd) &&
			!memory.getAllInitializedAddressSet().contains(table, tableEnd)) {
			return false;
		}
		Address[] targets = cand.targets(memory, monitor);
		if (targets == null) {
			return false;
		}
		for (Address t : targets) {
			monitor.checkCancelled();
			MemoryBlock tb = memory.getBlock(t);
			if ((t.getOffset() & 1) != 0 || tb == null ||
				!tb.isInitialized() || !tb.isExecute() || tb.isExternalBlock()) {
				return false;
			}
			if (cand.family == Family.DIRECT_TABLE) {
				// entries are instructions: each must be code-capable
				if (listing.getInstructionAt(t) == null && listing.getUndefinedDataAt(t) == null) {
					return false;
				}
			}
		}
		return true;
	}

	//==============================================================================================
	// Application
	//==============================================================================================

	private void apply(SwitchCase cand, TaskMonitor monitor) throws CancelledException {
		int tx = program.startTransaction("V850 switch table");
		boolean commit = false;
		try {
			Address[] targets = cand.targets(program.getMemory(), monitor);
			if (targets == null) {
				return;
			}
			Function fn =
				program.getFunctionManager().getFunctionContaining(cand.dispatch.getAddress());
			Namespace space = switchNamespace(cand.dispatch.getAddress());

			if (cand.family == Family.DIRECT_TABLE) {
				labelTable(cand, space);
			}
			else {
				createTableData(cand, targets, space);
			}

			AddressSet disassembly = new AddressSet();
			Set<Address> labeled = new HashSet<>();
			for (int i = 0; i < targets.length; i++) {
				cand.dispatch.addMnemonicReference(targets[i], RefType.COMPUTED_JUMP,
					SourceType.ANALYSIS);
				if (labeled.add(targets[i])) {
					labelCase(space, targets[i], (int) (cand.lowcase + i));
				}
				if (listing.getUndefinedDataAt(targets[i]) != null) {
					disassembly.add(targets[i]);
				}
			}
			if (cand.defaultAddr != null) {
				labelDefault(space, cand.defaultAddr);
				if (listing.getUndefinedDataAt(cand.defaultAddr) != null) {
					disassembly.add(cand.defaultAddr);
				}
			}
			comment(cand);
			if (!disassembly.isEmpty()) {
				// disassemble the case code directly (the upstream switch-analysis
				// pattern), then notify the analysis manager about the new code so
				// the remaining analyzers process it
				DisassembleCommand disCmd = new DisassembleCommand(disassembly, null, true);
				disCmd.applyTo(program, monitor);
				AddressSet disassembled = disCmd.getDisassembledAddressSet();
				if (disassembled != null && !disassembled.isEmpty()) {
					AutoAnalysisManager.getAnalysisManager(program).codeDefined(disassembled);
				}
			}
			if (fn != null) {
				Instruction entryInstr = listing.getInstructionAt(fn.getEntryPoint());
				if (entryInstr != null) {
					CreateFunctionCmd.fixupFunctionBody(program, entryInstr, monitor);
				}
			}
			commit = true;
		}
		catch (Exception e) {
			Msg.error(this, "failed to apply switch at " + cand.dispatch.getAddress(), e);
		}
		finally {
			program.endTransaction(tx, commit);
		}
	}

	/**
	 * Creates the jump-table data for data-backed families. Pre-existing defined data in the
	 * range is treated as curation and left untouched (labels/references are still applied).
	 */
	private void createTableData(SwitchCase cand, Address[] targets, Namespace space) {
		Address start = cand.tableAddr;
		Address end = start.add(cand.ncases * (long) cand.elementSize - 1);
		if (!hasDefinedData(start, end)) {
			try {
				listing.clearCodeUnits(start, end, false);
				DataType element = elementDataType(cand.elementSize, cand.signedElements);
				ArrayDataType array = new ArrayDataType(element, cand.ncases, cand.elementSize);
				listing.createData(start, array);
				Data data = listing.getDataAt(start);
				if (data != null) {
					for (ghidra.docking.settings.SettingsDefinition def : data.getDataType()
							.getSettingsDefinitions()) {
						if (def instanceof MutabilitySettingsDefinition msd) {
							msd.setChoice(data, MutabilitySettingsDefinition.CONSTANT);
						}
					}
				}
			}
			catch (Exception e) {
				Msg.debug(this, "could not create switch table data at " + start, e);
			}
		}
		// References augment curated tables as well as newly defined arrays.
		for (int i = 0; i < targets.length; i++) {
			Address elem = start.add((long) i * cand.elementSize);
			program.getReferenceManager().addMemoryReference(elem, targets[i], RefType.DATA,
				SourceType.ANALYSIS, Reference.MNEMONIC);
		}
		program.getReferenceManager().addMemoryReference(cand.dispatch.getAddress(), start,
			RefType.DATA, SourceType.ANALYSIS, Reference.MNEMONIC);
		labelTable(cand, space);
	}

	private boolean hasDefinedData(Address start, Address end) {
		CodeUnitIterator it = listing.getCodeUnits(new AddressSet(start, end), true);
		while (it.hasNext()) {
			CodeUnit cu = it.next();
			if (cu instanceof Data && ((Data) cu).isDefined()) {
				return true;
			}
		}
		return false;
	}

	private DataType elementDataType(int size, boolean signed) {
		switch (size) {
			case 1:
				return signed ? CharDataType.dataType : ByteDataType.dataType;
			case 2:
				return signed ? ShortDataType.dataType : UnsignedShortDataType.dataType;
			default:
				return signed ? IntegerDataType.dataType : UnsignedIntegerDataType.dataType;
		}
	}

	private void comment(SwitchCase cand) {
		Address at = cand.dispatch.getAddress();
		if (listing.getComment(CommentType.EOL, at) == null) {
			listing.setComment(at, CommentType.EOL,
				String.format("switch table @ %s (%d entries)", cand.tableAddr, cand.ncases));
		}
		if (cand.family != Family.DIRECT_TABLE &&
			listing.getComment(CommentType.PLATE, cand.tableAddr) == null) {
			listing.setComment(cand.tableAddr, CommentType.PLATE,
				String.format("V850 switch jump table (%d %s element%s)", cand.ncases,
					cand.elementSize + "-byte", cand.ncases == 1 ? "" : "s"));
		}
	}

	/**
	 * Namespace for the switch labels, parented by the global namespace. When the decompiler
	 * cannot model a dispatch itself (for example a table it refuses to recover), it maps any
	 * symbol in the function's own scope at the table address to a function-local declaration
	 * referencing that symbol, which Ghidra's ClangVariableDecl decoder then rejects with
	 * "Invalid symbol reference". A global-parented label is rendered as an ordinary global
	 * reference instead, while staying reachable from the symbol tree by its switchD_ name.
	 */
	private Namespace switchNamespace(Address dispatchAddr) {
		SymbolTable symTable = program.getSymbolTable();
		String name = "switchD_" + dispatchAddr;
		Namespace parent = program.getGlobalNamespace();
		try {
			return symTable.createNameSpace(parent, name, SourceType.ANALYSIS);
		}
		catch (Exception e) {
			Namespace existing = symTable.getNamespace(name, parent);
			if (existing != null) {
				return existing;
			}
			return program.getGlobalNamespace();
		}
	}

	private void labelTable(SwitchCase cand, Namespace space) {
		if (cand.family == Family.DIRECT_TABLE) {
			return; // entries are code, not data
		}
		addAnalysisLabel(cand.tableAddr, "switchdataD_" + cand.tableAddr, space);
	}

	private void labelCase(Namespace space, Address target, int value) {
		addAnalysisLabel(target, "caseD_" + Integer.toHexString(value), space);
	}

	private void labelDefault(Namespace space, Address target) {
		addAnalysisLabel(target, "default", space);
	}

	/** Adds a label only when no stronger (non-analysis) symbol exists at the address. */
	private void addAnalysisLabel(Address addr, String name, Namespace space) {
		Symbol primary = program.getSymbolTable().getPrimarySymbol(addr);
		if (primary != null && primary.getSource() != SourceType.ANALYSIS &&
			primary.getSource() != SourceType.DEFAULT) {
			return;
		}
		if (program.getSymbolTable().getSymbol(name, addr, space) != null) {
			return;
		}
		try {
			AddLabelCmd cmd = new AddLabelCmd(addr, name, space, SourceType.ANALYSIS);
			if (!cmd.applyTo(program)) {
				Msg.debug(this, "could not label " + addr + " as " + name);
			}
		}
		catch (Exception e) {
			Msg.debug(this, "could not label " + addr + " as " + name, e);
		}
	}

	//==============================================================================================
	// Instruction helpers
	//==============================================================================================

	private static Register getRegister(Instruction insn, int op) {
		if (op >= insn.getNumOperands()) {
			return null;
		}
		for (Object o : insn.getOpObjects(op)) {
			if (o instanceof Register) {
				return (Register) o;
			}
		}
		return null;
	}

	private static Scalar getScalar(Instruction insn, int op) {
		if (op >= insn.getNumOperands()) {
			return null;
		}
		for (Object o : insn.getOpObjects(op)) {
			if (o instanceof Scalar) {
				return (Scalar) o;
			}
		}
		return null;
	}

	/** Canonical GPR number for a register (aliases sp/gp/tp/ep/lp included), or -1. */
	private static int regIndex(Register reg) {
		if (reg == null || reg.getNumBytes() != 4) {
			return -1;
		}
		// r0 is separate from the r0:r1 pair's discarded low-word sink.
		if (reg.getName().equals("r0")) {
			return 0;
		}
		long off = reg.getAddress().getOffset();
		if (off < 4 || off > 124 || (off & 3) != 0) {
			return -1;
		}
		return (int) (off >>> 2);
	}

	private Address flowTarget(Instruction branch) {
		for (Reference ref : branch.getReferencesFrom()) {
			if (ref.getReferenceType().isJump()) {
				return ref.getToAddress();
			}
		}
		Address[] flows = branch.getFlows();
		return flows.length > 0 ? flows[0] : null;
	}

	private boolean hasComputedJumpRefs(Instruction insn) {
		for (Reference ref : insn.getReferencesFrom()) {
			if (ref.getReferenceType().equals(RefType.COMPUTED_JUMP)) {
				return true;
			}
		}
		return false;
	}

	/** True when the instruction's pcode writes the given GPR. */
	private static boolean writesReg(Instruction insn, int reg) {
		if (reg <= 0) {
			return false;
		}
		try {
			for (PcodeOp op : insn.getPcode()) {
				Varnode out = op.getOutput();
				if (out != null && out.isRegister() && out.getSize() == 4) {
					long off = out.getAddress().getOffset();
					if (off >= 0 && off <= 124 && (off & 3) == 0 && (int) (off >>> 2) == reg) {
						return true;
					}
				}
			}
		}
		catch (Exception e) {
			return true; // without pcode, assume the worst
		}
		return false;
	}
}
