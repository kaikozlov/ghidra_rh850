package coherentslab.proof;

import java.io.File;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodHandles.Lookup;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

import ghidra.GhidraApplicationLayout;
import ghidra.app.plugin.processors.sleigh.SleighLanguage;
import ghidra.framework.Application;
import ghidra.framework.ApplicationConfiguration;
import ghidra.generic.util.datastruct.SemisparseByteArray;
import ghidra.generic.util.datastruct.SemisparseByteArray.DirectPage;
import ghidra.pcode.emu.PcodeThread;
import ghidra.pcode.emu.jit.JitBytesPcodeExecutorStatePiece;
import ghidra.pcode.emu.jit.JitCompiler;
import ghidra.pcode.emu.jit.JitConfiguration;
import ghidra.pcode.emu.jit.JitConfiguration.Opt;
import ghidra.pcode.emu.jit.JitDefaultBytesPcodeExecutorState;
import ghidra.pcode.emu.jit.JitPcodeEmulator;
import ghidra.pcode.emu.jit.JitPcodeThread;
import ghidra.pcode.emu.jit.JitPassage;
import ghidra.pcode.emu.jit.JitPassage.AddrCtx;
import ghidra.pcode.emu.jit.JitPassage.CtxReach;
import ghidra.pcode.emu.jit.JitPassage.DecodedPcodeOp;
import ghidra.pcode.emu.jit.JitPassage.EntryPcodeOp;
import ghidra.pcode.emu.jit.JitPassage.ExitPcodeOp;
import ghidra.pcode.emu.jit.JitPassage.PBranch;
import ghidra.pcode.emu.jit.JitPassage.RExtBranch;
import ghidra.pcode.emu.jit.JitPassage.RIntBranch;
import ghidra.pcode.emu.jit.gen.tgt.JitCompiledPassage;
import ghidra.pcode.emu.jit.gen.tgt.JitCompiledPassage.EntryPoint;
import ghidra.pcode.emu.jit.gen.tgt.JitCompiledPassage.EntryPointPrototype;
import ghidra.pcode.exec.PcodeExecutorState;
import ghidra.pcode.exec.PcodeStateCallbacks;
import ghidra.pcode.exec.PcodeUseropLibrary;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressFactory;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.lang.Language;
import ghidra.program.model.lang.LanguageID;
import ghidra.program.model.lang.LanguageService;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.pcode.Varnode;
import ghidra.program.util.DefaultLanguageService;

/**
 * Standalone proof for the opt-in coherent-slab overlay. It must run with the overlay
 * classes ahead of the installed module jars on the class path.
 * <ol>
 * <li>Storage: page identity, reverse slab binding, sparse overflow, clear and both restore
 * paths, and unchanged behavior for arrays without a slab.</li>
 * <li>Generated code: every emitted access width, every cross-page split, signed and unsigned
 * reads, cross-page writes, in little- and big-endian languages, in register and unique
 * spaces, with a slab too small for every page, with mixed slab and sparse pages, and without a
 * slab.</li>
 * </ol>
 */
public class CoherentSlabProof {
	private static final int PAGE = SemisparseByteArray.BLOCK_SIZE;
	/** Three pages, so that one read and one write cross each page boundary. */
	private static final int MODEL_SIZE = 3 * PAGE;
	private static final Lookup LOOKUP = MethodHandles.lookup();
	private static final JitConfiguration CONFIG =
		new JitConfiguration().disable(Opt.FOLD_CONSTANTS).disable(Opt.EMIT_COUNTERS);

	/** Both endiannesses come from processor definitions shipped with Ghidra 12.2. */
	private static final List<String> LANGUAGE_IDS =
		List.of("MIPS:LE:32:default", "MIPS:BE:32:default");

	private static void check(boolean condition, String message) {
		if (!condition) {
			throw new AssertionError(message);
		}
	}

	private static void expect(Class<? extends Throwable> type, Runnable action) {
		try {
			action.run();
		}
		catch (Throwable t) {
			if (type.isInstance(t)) {
				return;
			}
			throw new AssertionError("unexpected " + t, t);
		}
		throw new AssertionError("expected " + type.getSimpleName());
	}

	public static void main(String[] args) throws Exception {
		check(args.length == 1, "usage: CoherentSlabProof GHIDRA_HOME");
		proveStorage();

		Application.initializeApplication(new GhidraApplicationLayout(new File(args[0])),
			new ApplicationConfiguration());
		LanguageService languages = DefaultLanguageService.getLanguageService();
		int passages = 0;
		for (String id : LANGUAGE_IDS) {
			SleighLanguage language = (SleighLanguage) languages.getLanguage(new LanguageID(id));
			for (int slabPages : new int[] { 2, 1, 0 }) {
				for (boolean unique : new boolean[] { false, true }) {
					passages += proveGeneratedCode(language, id, slabPages, unique);
				}
			}
		}
		System.out.println("Coherent slab overlay proof passed: " + passages +
			" JIT passages across " + LANGUAGE_IDS.size() + " endiannesses");
	}

	// ---------------------------------------------------------------- storage

	private static void proveStorage() {
		byte[] slab = new byte[3 * PAGE];
		var live = new SemisparseByteArray(slab);
		// Bind in reverse numerical order, so using guest offsets as slab indices fails.
		var third = live.getDirectPage(2 * PAGE);
		var second = live.getDirectPage(PAGE);
		var first = live.getDirectPage(0);
		check(third.array() == slab && second.array() == slab && first.array() == slab,
			"bound pages share the slab");
		check(third.offset() == 0 && second.offset() == PAGE && first.offset() == 2 * PAGE,
			"bound pages are distinct slab slices");
		check(live.getDirectArray(PAGE) == slab && live.getDirectArrayOffset(PAGE) == PAGE,
			"generated-code array and index agree with the page");
		check(live.getDirectArray(2 * PAGE) == slab && live.getDirectArrayOffset(2 * PAGE) == 0,
			"generated-code array and index agree with the first slice");
		expect(IllegalArgumentException.class, () -> live.getDirectPage(1));
		expect(IllegalArgumentException.class, () -> live.getDirectArrayOffset(3));
		expect(IllegalArgumentException.class, () -> new SemisparseByteArray(new byte[0]));
		expect(IllegalArgumentException.class, () -> new SemisparseByteArray(new byte[PAGE + 1]));

		// A write that straddles two slices lands in guest order, not slab order.
		live.putData(PAGE - 1, new byte[] { 7, 9, 10, 11, 12 });
		check(first.array()[first.offset() + PAGE - 1] == 7, "tail of the first page");
		check(JitCompiledPassage.readIntLE4(second.array(), second.offset()) == 0x0c0b0a09,
			"head of the second page");
		JitCompiledPassage.writeIntLE4(0x10203040, second.array(), second.offset());
		byte[] mixed = new byte[5];
		live.getData(PAGE - 1, mixed);
		check(Arrays.equals(mixed, new byte[] { 7, 0x40, 0x30, 0x20, 0x10 }),
			"read back across two slices");
		check(!live.isInitialized(PAGE + 4), "bytes beyond the write stay undefined");

		// Once the slab is full, new pages are ordinary sparse blocks at index zero.
		var overflow = live.getDirectPage(3L * PAGE);
		check(overflow.offset() == 0 && overflow.array() != slab, "overflow page is sparse");
		check(live.getDirect(3L * PAGE) == overflow.array(), "sparse identity is preserved");
		check(live.getDirectArray(3L * PAGE) == overflow.array() &&
			live.getDirectArrayOffset(3L * PAGE) == 0, "overflow index is zero");
		live.putData(3L * PAGE + 2, new byte[] { 1, 2, 3 });
		check(overflow.array()[2] == 1 && overflow.array()[4] == 3, "overflow write");
		byte[] across = new byte[6];
		live.getData(3L * PAGE - 2, across);
		check(Arrays.equals(across, new byte[] { 0, 0, 0, 0, 1, 2 }),
			"read across a slab slice and a sparse block");
		// The offset-less API cannot describe a slice, so it refuses slab-backed pages.
		expect(IllegalStateException.class, () -> live.getDirect(PAGE));
		byte[] fresh = live.getDirect(8L * PAGE);
		check(live.getDirect(8L * PAGE) == fresh, "unbound sparse pages keep their identity");
		expect(IllegalArgumentException.class, () -> live.copyDirectPage(0, new byte[PAGE - 1]));

		var snapshot = live.fork();
		check(snapshot.getDirectPage(PAGE).array() != slab, "a fork never aliases the slab");

		// Native kernels may zero the slab in place; initialized ranges survive.
		Arrays.fill(slab, (byte) 0);
		live.getData(PAGE - 1, mixed);
		check(Arrays.equals(mixed, new byte[5]), "native zeroing is observed");
		check(live.isInitialized(PAGE - 1, PAGE + 3), "native zeroing keeps ranges");

		// Restore path one: raw page copies keep identity and the initialized ranges.
		live.copyDirectPage(0, snapshot.getDirect(0));
		live.copyDirectPage(PAGE, snapshot.getDirect(PAGE));
		live.copyDirectPage(2L * PAGE, snapshot.getDirect(2L * PAGE));
		live.copyDirectPage(3L * PAGE, snapshot.getDirect(3L * PAGE));
		check(live.getDirectPage(0) == first && live.getDirectPage(PAGE) == second &&
			live.getDirectPage(2L * PAGE) == third &&
				live.getDirectPage(3L * PAGE).array() == overflow.array(),
			"page copies restore in place");
		check(JitCompiledPassage.readIntLE4(second.array(), second.offset()) == 0x10203040,
			"page copy content");
		check(!live.isInitialized(PAGE + 4), "page copies do not define ranges");

		// Clear revokes values but keeps every page generated code may still hold.
		live.clear();
		check(!live.isInitialized(PAGE - 1, PAGE + 3), "clear revokes ranges");
		check(live.getDirectPage(0) == first && live.getDirectPage(PAGE) == second &&
			live.getDirectPage(2L * PAGE) == third &&
				live.getDirectPage(3L * PAGE).array() == overflow.array(),
			"clear keeps slab slices and overflow pages");
		check(JitCompiledPassage.readIntLE4(second.array(), second.offset()) == 0 &&
			overflow.array()[2] == 0, "clear zeroes every retained page");

		// Restore path two: putAll writes through the ordinary block path.
		live.putAll(snapshot);
		check(live.getDirectPage(0) == first && live.getDirectPage(PAGE) == second &&
			live.getDirectPage(3L * PAGE).array() == overflow.array(),
			"putAll restores in place");
		live.getData(PAGE - 1, mixed);
		check(Arrays.equals(mixed, new byte[] { 7, 0x40, 0x30, 0x20, 0x10 }), "putAll content");
		live.getData(3L * PAGE + 2, across, 0, 3);
		check(Arrays.equals(across, 0, 3, new byte[] { 1, 2, 3 }, 0, 3),
			"putAll overflow content");
		check(live.isInitialized(PAGE - 1, PAGE + 3) && !live.isInitialized(PAGE + 4),
			"putAll restores ranges only");

		// Without a slab, upstream behavior is unchanged.
		var plain = new SemisparseByteArray();
		byte[] block = plain.getDirect(0);
		check(plain.getDirectArray(0) == block && plain.getDirectArrayOffset(0) == 0,
			"plain array array and index");
		var plainPage = plain.getDirectPage(PAGE);
		check(plainPage.array() == plain.getDirect(PAGE) && plainPage.offset() == 0,
			"plain array page");
		plain.putData(PAGE - 2, new byte[] { 1, 2, 3, 4 });
		check(block[PAGE - 2] == 1 && block[PAGE - 1] == 2 && plainPage.array()[0] == 3 &&
			plainPage.array()[1] == 4, "plain cross-page write");
		byte[] untouched = new byte[4];
		Arrays.fill(untouched, (byte) 0x55);
		plain.getData(5L * PAGE, untouched);
		check(Arrays.equals(untouched, new byte[] { 0x55, 0x55, 0x55, 0x55 }),
			"uninitialized plain reads leave the destination alone");
		plain.clear();
		check(plain.getDirect(0) != block && !plain.isInitialized(PAGE - 2),
			"plain clear drops blocks as before");
		plain.copyDirectPage(0, new byte[PAGE]);
		check(!plain.isInitialized(0, PAGE - 1), "plain page copy does not define");
	}

	// ---------------------------------------------------------- generated code

	/** A state piece whose register and unique spaces own one slab each. */
	private static final class SlabPiece extends JitBytesPcodeExecutorStatePiece {
		private final int slabPages;

		SlabPiece(Language language, PcodeStateCallbacks cb, int slabPages) {
			super(language, cb);
			this.slabPages = slabPages;
		}

		// The upstream space is an inner class of the piece, so the subclass lives here too.
		private final class SlabSpace extends JitBytesPcodeExecutorStateSpace {
			SlabSpace(Language language, AddressSpace space, SemisparseByteArray bytes) {
				super(language, space, SlabPiece.this, bytes);
			}

			SemisparseByteArray bytes() {
				return bytes;
			}
		}

		@Override
		protected SlabSpace newSpace(AddressSpace space) {
			boolean local = space.isRegisterSpace() || space.isUniqueSpace();
			return new SlabSpace(language, space, new SemisparseByteArray(
				local && slabPages > 0 ? new byte[slabPages * PAGE] : null));
		}

		SemisparseByteArray bytesOf(AddressSpace space) {
			return ((SlabSpace) getForSpace(space, true)).bytes();
		}
	}

	/** The concrete wrapper the JIT requires, handing out the slab-backed piece. */
	private static final class SlabState extends JitDefaultBytesPcodeExecutorState {
		private final SlabPiece slabPiece;

		SlabState(Language language, PcodeStateCallbacks cb, int slabPages) {
			super(language, cb);
			slabPiece = new SlabPiece(language, cb, slabPages);
		}

		@Override
		protected SlabPiece getPiece() {
			return slabPiece;
		}

		SlabPiece slabPiece() {
			return slabPiece;
		}
	}

	private static final class SlabEmulator extends JitPcodeEmulator {
		private final int slabPages;

		SlabEmulator(SleighLanguage language, int slabPages) {
			super(language, CONFIG, LOOKUP);
			this.slabPages = slabPages;
		}

		@Override
		protected PcodeExecutorState<byte[]> createSharedState() {
			return new SlabState(language, cb.wrapFor(null), 0);
		}

		@Override
		protected PcodeExecutorState<byte[]> createLocalState(PcodeThread<byte[]> thread) {
			return new SlabState(language, cb.wrapFor(thread), slabPages);
		}
	}

	private static Varnode vn(AddressSpace space, long offset, int size) {
		return new Varnode(space.getAddress(offset), size);
	}

	/** p-code reads a varnode as an unsigned integer in the byte order of its space. */
	private static long unsigned(byte[] model, int offset, int size, boolean bigEndian) {
		long value = 0;
		for (int i = 0; i < size; i++) {
			int index = bigEndian ? offset + i : offset + size - 1 - i;
			value = (value << 8) | (model[index] & 0xffL);
		}
		return value;
	}

	private static long signed(byte[] model, int offset, int size, boolean bigEndian) {
		long value = unsigned(model, offset, size, bigEndian);
		if (size < 8 && (value & (1L << (8 * size - 1))) != 0) {
			value |= -1L << (8 * size);
		}
		return value;
	}

	private static void store(byte[] model, int offset, int size, long value,
			boolean bigEndian) {
		for (int i = 0; i < size; i++) {
			int shift = 8 * (bigEndian ? size - 1 - i : i);
			model[offset + i] = (byte) (value >>> shift);
		}
	}

	/** Compare the whole model except the bytes the passage exit is allowed to retire. */
	private static void compare(SemisparseByteArray live, byte[] model, long maskedOffset,
			int maskedSize, String context) {
		byte[] actual = new byte[MODEL_SIZE];
		Arrays.fill(actual, (byte) 0x55);
		live.getData(0, actual);
		for (int i = 0; i < actual.length; i++) {
			if (i >= maskedOffset && i < maskedOffset + maskedSize) {
				continue;
			}
			check(actual[i] == model[i],
				context + ": byte 0x%x is 0x%02x, expected 0x%02x".formatted(i, actual[i],
					model[i]));
		}
	}

	private static int proveGeneratedCode(SleighLanguage language, String id, int slabPages,
			boolean unique) {
		boolean bigEndian = language.isBigEndian();
		SlabEmulator machine = new SlabEmulator(language, slabPages);
		JitPcodeThread thread = machine.newThread("proof");
		AddressFactory factory = language.getAddressFactory();
		AddressSpace space = unique ? factory.getUniqueSpace() : factory.getRegisterSpace();
		AddressSpace ram = language.getDefaultSpace();
		// The exit retires the program counter; it is not part of what the cases assert.
		long maskedOffset = unique ? -1 : language.getProgramCounter().getAddress().getOffset();
		int maskedSize = unique ? 0 : 8;

		SlabState local = (SlabState) thread.getState().getLocalState();
		SemisparseByteArray bytes = local.slabPiece().bytesOf(space);
		if (slabPages > 0) {
			// Bind the last page first, so slab indices differ from guest pages.
			bytes.getDirectPage(2 * PAGE);
			check(bytes.getDirectPage(2 * PAGE).offset() != 2 * PAGE,
				"page two must not sit at its guest index");
		}

		JitCompiler compiler = new JitCompiler(CONFIG);
		PcodeUseropLibrary<?> library = machine.getStubUseropLibrary();
		Random random = new Random(id.hashCode() * 31L + slabPages * 2L + (unique ? 1 : 0));
		int caseIndex = 0;
		EntryPoint firstEntry = null;
		byte[] firstFill = null;
		byte[] firstExpected = null;
		for (int size = 1; size <= 8; size++) {
			// Size one cannot straddle a page; every other size takes every split once.
			for (int low = size == 1 ? 0 : 1; low < size; low++) {
				// The source straddles pages zero and one; the xor output straddles one and two.
				long source = PAGE - low;
				long other = 0x800;
				long zeroExtended = PAGE + 0x800;
				long signExtended = PAGE + 0x808;
				long less = PAGE + 0x810;
				long negated = PAGE + 0x811;
				long signedLess = PAGE + 0x812;
				long flag = PAGE + 0x813;
				long xorWrite = 2 * PAGE - (size - low);
				long copyWrite = 2 * PAGE + 8;

				byte[] fill = new byte[MODEL_SIZE];
				random.nextBytes(fill);
				fill[(int) flag] = (byte) (caseIndex & 1);
				byte[] expected = fill.clone();

				// The same program in the byte order of the space.
				long value = unsigned(fill, (int) source, size, bigEndian);
				long signedValue = signed(fill, (int) source, size, bigEndian);
				long otherValue = unsigned(fill, (int) other, size, bigEndian);
				long signedOther = signed(fill, (int) other, size, bigEndian);
				store(expected, (int) zeroExtended, 8, value, bigEndian);
				if (size < 8) {
					store(expected, (int) signExtended, 8, signedValue, bigEndian);
				}
				store(expected, (int) xorWrite, size, value ^ otherValue, bigEndian);
				store(expected, (int) copyWrite, size, otherValue, bigEndian);
				store(expected, (int) less, 1,
					Long.compareUnsigned(value, otherValue) < 0 ? 1 : 0, bigEndian);
				store(expected, (int) negated, 1, fill[(int) flag] == 0 ? 1 : 0, bigEndian);
				store(expected, (int) signedLess, 1, signedValue < signedOther ? 1 : 0,
					bigEndian);

				bytes.putData(0, fill);

				Address at = ram.getAddress(0x10000L + caseIndex * 0x10);
				// These hand-built p-code ops do not depend on decode context.
				// Ghidra 12.2 emits context fields before registering entry-only requests.
				AddrCtx seed = new AddrCtx(null, at);
				AddrCtx exitTo = new AddrCtx(null, ram.getAddress(0x20000L));
				Varnode sourceNode = vn(space, source, size);
				Varnode otherNode = vn(space, other, size);
				List<PcodeOp> ops = new ArrayList<>();
				// Zero-extended read of a crossing varnode, written within one page.
				ops.add(new PcodeOp(at, ops.size(), size < 8 ? PcodeOp.INT_ZEXT : PcodeOp.COPY,
					new Varnode[] { sourceNode }, vn(space, zeroExtended, 8)));
				if (size < 8) {
					// Sign-extended read of the same varnode.
					ops.add(new PcodeOp(at, ops.size(), PcodeOp.INT_SEXT,
						new Varnode[] { sourceNode }, vn(space, signExtended, 8)));
				}
				// Crossing read with one split, crossing write with the other split.
				ops.add(new PcodeOp(at, ops.size(), PcodeOp.INT_XOR,
					new Varnode[] { sourceNode, otherNode }, vn(space, xorWrite, size)));
				// Page-local read and page-local write.
				ops.add(new PcodeOp(at, ops.size(), PcodeOp.COPY, new Varnode[] { otherNode },
					vn(space, copyWrite, size)));
				// Unsigned and signed compares of a crossing varnode.
				ops.add(new PcodeOp(at, ops.size(), PcodeOp.INT_LESS,
					new Varnode[] { sourceNode, otherNode }, vn(space, less, 1)));
				ops.add(new PcodeOp(at, ops.size(), PcodeOp.BOOL_NEGATE,
					new Varnode[] { vn(space, flag, 1) }, vn(space, negated, 1)));
				ops.add(new PcodeOp(at, ops.size(), PcodeOp.INT_SLESS,
					new Varnode[] { sourceNode, otherNode }, vn(space, signedLess, 1)));

				EntryPoint entry =
					compile(compiler, language, library, seed, exitTo, ops).createInstance(thread);
				entry.run();
				compare(bytes, expected, maskedOffset, maskedSize,
					"%s %s slab=%d %s size=%d low=%d".formatted(id, bigEndian ? "BE" : "LE",
						slabPages, unique ? "unique" : "register", size, low));
				if (firstEntry == null) {
					firstEntry = entry;
					firstFill = fill;
					firstExpected = expected;
				}
				caseIndex++;
			}
		}

		// A compiled passage keeps working across clear and refill: every page it
		// captured at construction is still the live page.
		if (slabPages > 0) {
			DirectPage[] held = new DirectPage[MODEL_SIZE / PAGE];
			for (int page = 0; page < held.length; page++) {
				held[page] = bytes.getDirectPage(page * PAGE);
			}
			bytes.clear();
			for (int page = 0; page < held.length; page++) {
				DirectPage current = bytes.getDirectPage(page * PAGE);
				check(current.array() == held[page].array() &&
					current.offset() == held[page].offset(),
					"clear must keep the pages held by compiled passages");
			}
			check(!bytes.isInitialized(0, MODEL_SIZE - 1L), "clear revokes everything");
			compare(bytes, new byte[MODEL_SIZE], maskedOffset, maskedSize, "cleared");
			bytes.putData(0, firstFill);
			firstEntry.run();
			compare(bytes, firstExpected, maskedOffset, maskedSize, "rerun after clear");
		}
		return caseIndex;
	}

	/** A straight-line single-instruction passage that exits without chaining. */
	private static EntryPointPrototype compile(JitCompiler compiler, SleighLanguage language,
			PcodeUseropLibrary<?> library, AddrCtx seed, AddrCtx exitTo, List<PcodeOp> ops) {
		List<PcodeOp> code = new ArrayList<>();
		for (PcodeOp op : ops) {
			code.add(new DecodedPcodeOp(seed, op));
		}
		ExitPcodeOp exit = ExitPcodeOp.exit(exitTo);
		code.add(exit);
		Map<PcodeOp, PBranch> branches = new HashMap<>();
		branches.put(exit, new RExtBranch(exit, exitTo, null, CtxReach.WITH_CTXMOD));
		PcodeOp entryOp = new EntryPcodeOp(seed);
		branches.put(entryOp,
			new RIntBranch(entryOp, code.getFirst(), false, CtxReach.WITHOUT_CTXMOD));
		JitPassage passage = new JitPassage(language, seed, code, library, List.of(), branches,
			Map.of(code.getFirst(), seed), Map.of());
		EntryPointPrototype prototype =
			compiler.compilePassage(LOOKUP, passage).getBlockEntries().get(seed);
		check(prototype != null, "the seed must be an entry of the compiled passage");
		return prototype;
	}
}
