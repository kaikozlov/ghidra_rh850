import ghidra.app.util.PseudoInstruction;
import ghidra.pcode.emu.SleighInstructionDecoder;
import ghidra.generic.util.datastruct.SemisparseByteArray;
import ghidra.pcode.emu.PcodeThread;
import ghidra.pcode.emu.jit.JitBytesPcodeExecutorStatePiece;
import ghidra.pcode.emu.jit.JitConfiguration;
import ghidra.pcode.emu.jit.JitDefaultBytesPcodeExecutorState;
import ghidra.pcode.emu.jit.JitPassage;
import ghidra.pcode.emu.jit.JitPassage.AddrCtx;
import ghidra.pcode.emu.jit.JitPassage.CtxReach;
import ghidra.pcode.emu.jit.JitPassage.DecodedPcodeOp;
import ghidra.pcode.emu.jit.JitPassage.EntryPcodeOp;
import ghidra.pcode.emu.jit.JitPassage.ExitPcodeOp;
import ghidra.pcode.emu.jit.JitPassage.NopPcodeOp;
import ghidra.pcode.emu.jit.JitPassage.RExtBranch;
import ghidra.pcode.emu.jit.JitPassage.RIntBranch;
import ghidra.pcode.emu.jit.JitPcodeEmulator;
import ghidra.pcode.emu.jit.JitPcodeThread;
import ghidra.pcode.emu.jit.decode.JitPassageDecoder;
import ghidra.pcode.emu.jit.gen.tgt.JitCompiledPassage.EntryPoint;
import ghidra.pcode.emu.jit.gen.tgt.JitCompiledPassage.EntryPointPrototype;
import ghidra.pcode.emu.jit.gen.tgt.JitCompiledPassageClass;
import ghidra.pcode.exec.PcodeExecutorState;
import ghidra.pcode.opbehavior.BinaryOpBehavior;
import ghidra.pcode.opbehavior.UnaryOpBehavior;
import ghidra.pcode.opbehavior.OpBehavior;
import ghidra.pcode.opbehavior.OpBehaviorFactory;
import ghidra.pcode.exec.PcodeArithmetic.Purpose;
import ghidra.pcode.exec.PcodeExecutionException;
import ghidra.pcode.exec.PcodeExecutorStatePiece;
import ghidra.pcode.exec.PcodeFrame;
import ghidra.pcode.exec.PcodeProgram;
import ghidra.pcode.exec.PcodeStateCallbacks;
import ghidra.pcode.exec.PcodeUseropLibrary.PcodeUseropSymbolMap;
import ghidra.pcode.exec.PcodeExecutorStatePiece.Reason;
import ghidra.pcode.exec.SuspendedPcodeExecutionException;
import ghidra.pcode.utils.Utils;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.lang.Language;
import ghidra.program.model.lang.Register;
import ghidra.program.model.lang.RegisterValue;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.pcode.Varnode;
import ghidra.program.model.mem.MemBuffer;

import java.lang.invoke.MethodHandles;
import java.lang.invoke.VarHandle;
import java.math.BigInteger;
import java.nio.ByteOrder;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.BitSet;
import java.util.HashMap;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.stream.Stream;

/** Instruction-scheduled P1M-E machine with tiered translation of hot p-code. */
public final class P1MEJitMachine extends JitPcodeEmulator {
    private static final MethodHandles.Lookup JIT_LOOKUP = MethodHandles.lookup();
    private static final int PAGE_SIZE = SemisparseByteArray.BLOCK_SIZE;
    private static final int PAGE_MASK = PAGE_SIZE - 1;
    private static final int PAGE_SHIFT = Integer.numberOfTrailingZeros(PAGE_SIZE);
    private static final int PROMOTION_HITS = 64;
    // Require an active working-set share, not a lifetime count accumulated
    // through isolated visits that cannot repay the cost of a JVM class.
    private static final int PROMOTION_WINDOW = 4096;
    private static final VarHandle LE_SHORTS =
        MethodHandles.byteArrayViewVarHandle(short[].class, ByteOrder.LITTLE_ENDIAN);
    private static final VarHandle BE_SHORTS =
        MethodHandles.byteArrayViewVarHandle(short[].class, ByteOrder.BIG_ENDIAN);
    private static final VarHandle LE_INTS =
        MethodHandles.byteArrayViewVarHandle(int[].class, ByteOrder.LITTLE_ENDIAN);
    private static final VarHandle BE_INTS =
        MethodHandles.byteArrayViewVarHandle(int[].class, ByteOrder.BIG_ENDIAN);
    private static final VarHandle LE_LONGS =
        MethodHandles.byteArrayViewVarHandle(long[].class, ByteOrder.LITTLE_ENDIAN);
    private static final VarHandle BE_LONGS =
        MethodHandles.byteArrayViewVarHandle(long[].class, ByteOrder.BIG_ENDIAN);
    private final RunP1MEMachine.Callbacks callbacks;

    /** Live Ghidra page with the byte ranges already proven initialized. */
    private static final class BoundPage {
        final long base;
        final byte[] data;
        final BitSet defined = new BitSet(PAGE_SIZE);

        BoundPage(long base, byte[] data) {
            this.base = base;
            this.data = data;
        }

        long readNumber(int start, int size, boolean bigEndian) {
            if (size == Integer.BYTES) {
                return Integer.toUnsignedLong(bigEndian
                    ? (int) BE_INTS.get(data, start) : (int) LE_INTS.get(data, start));
            }
            if (size == 1) return data[start] & 0xff;
            if (size == Short.BYTES) return 0xffff & (bigEndian
                ? (short) BE_SHORTS.get(data, start) : (short) LE_SHORTS.get(data, start));
            if (size == Long.BYTES) {
                return bigEndian ? (long) BE_LONGS.get(data, start) : (long) LE_LONGS.get(data, start);
            }
            long value = 0;
            int end = start + size;
            if (bigEndian) {
                for (int i = start; i < end; i++) value = (value << 8) | (data[i] & 0xff);
            }
            else {
                for (int i = end - 1; i >= start; i--) value = (value << 8) | (data[i] & 0xff);
            }
            return value;
        }

        void writeNumber(int start, int size, boolean bigEndian, long value) {
            if (size == Integer.BYTES) {
                if (bigEndian) BE_INTS.set(data, start, (int) value);
                else LE_INTS.set(data, start, (int) value);
            }
            else if (size == 1) {
                data[start] = (byte) value;
            }
            else if (size == Short.BYTES) {
                if (bigEndian) BE_SHORTS.set(data, start, (short) value);
                else LE_SHORTS.set(data, start, (short) value);
            }
            else if (size == Long.BYTES) {
                if (bigEndian) BE_LONGS.set(data, start, value);
                else LE_LONGS.set(data, start, value);
            }
            else {
                for (int i = 0; i < size; i++, value >>= 8) {
                    data[start + (bigEndian ? size - i - 1 : i)] = (byte) value;
                }
            }
        }
    }

    private record ScalarOperand(BoundPage page, int start, int size, long constant) {
        long read(boolean bigEndian) {
            return page == null ? constant : page.readNumber(start, size, bigEndian);
        }
    }

    private record ScalarOp(OpBehavior behavior, ScalarOperand output, ScalarOperand left,
            ScalarOperand right, int opcode, Address target) {
        private static final ScalarOp[] EMPTY = {};

        void execute(boolean bigEndian) {
            long leftValue = left.read(bigEndian);
            long value = behavior instanceof UnaryOpBehavior unary
                ? unary.evaluateUnary(output.size, left.size, leftValue)
                : ((BinaryOpBehavior) behavior).evaluateBinary(output.size, left.size,
                    leftValue, right.read(bigEndian));
            output.page.writeNumber(output.start, output.size, bigEndian, value);
        }
    }

    private record CodeBytes(long generation, int start, byte[] first, byte[] second) {
        boolean matches(byte[] encoding, long word) {
            if (second == null) {
                switch (encoding.length) {
                    case 2:
                        return (short) LE_SHORTS.get(first, start) == (short) word;
                    case 4:
                        return (int) LE_INTS.get(first, start) == (int) word;
                    case 6:
                        return (int) LE_INTS.get(first, start) == (int) word
                            && (short) LE_SHORTS.get(first, start + 4) == (short) (word >>> 32);
                    case 8:
                        return (long) LE_LONGS.get(first, start) == word;
                    default:
                        break;
                }
            }
            int split = Math.min(PAGE_SIZE - start, encoding.length);
            return Arrays.equals(first, start, start + split, encoding, 0, split)
                && (second == null ||
                    Arrays.equals(second, 0, encoding.length - split, encoding, split, encoding.length));
        }
    }

    private static final class MachineStatePiece extends JitBytesPcodeExecutorStatePiece {
        private final RunP1MEMachine.Callbacks bus;
        private final AddressSpace registerAddressSpace;
        private final AddressSpace memoryAddressSpace;
        private MachineStateSpace registers;
        private MachineStateSpace uniques;
        private MachineStateSpace memory;
        private long generation;

        MachineStatePiece(Language language, RunP1MEMachine.Callbacks callbacks,
                PcodeThread<byte[]> thread) {
            super(language, callbacks.wrapFor(thread));
            bus = thread == null ? callbacks : null;
            registerAddressSpace = language.getProgramCounter().getAddressSpace();
            memoryAddressSpace = language.getDefaultSpace();
        }

        boolean usesBus(AddressSpace space) {
            return bus != null && space.equals(bus.model.memorySpace);
        }

        private final class MachineStateSpace extends JitBytesPcodeExecutorStateSpace
                implements RunP1MEMachine.InitializedBytes {
            private final long maxOffset;
            private final BoundPage[] pageCache;

            MachineStateSpace(AddressSpace space) {
                super(MachineStatePiece.this.language, space, MachineStatePiece.this);
                maxOffset = space.getMaxAddress().getOffset();
                pageCache = space.isRegisterSpace() || space.isUniqueSpace() || space == memoryAddressSpace
                    ? new BoundPage[64] : null;
            }

            @Override
            public SemisparseByteArray backing() {
                return bytes;
            }

            boolean isInitialized(long offset, int size) {
                return RunP1MEMachine.InitializedBytes.covers(bytes, space, offset, size);
            }

            boolean fitsPage(long offset, int size) {
                return pageCache != null && size > 0 && size <= PAGE_SIZE - ((int) offset & PAGE_MASK)
                    && Long.compareUnsigned(offset + size - 1, maxOffset) <= 0;
            }

            BoundPage initializedLocalPage(long offset, int size) {
                int start = (int) offset & PAGE_MASK;
                long base = offset - start;
                long pageNumber = Long.divideUnsigned(base, PAGE_SIZE);
                int slot = (int) (pageNumber ^ (pageNumber >>> 6)) & (pageCache.length - 1);
                BoundPage page = pageCache[slot];
                if (page != null && page.base == base && page.defined.nextClearBit(start) >= start + size) {
                    return page;
                }
                int available = bytes.contiguousAvailableAfter(offset);
                if (available < size) return null;
                if (page == null || page.base != base) {
                    page = new BoundPage(base, getDirect(base));
                    pageCache[slot] = page;
                }
                page.defined.set(start, start + Math.min(available, PAGE_SIZE - start));
                return page;
            }

            void invalidatePages() {
                if (pageCache != null) Arrays.fill(pageCache, null);
            }

            @Override
            public void clear() {
                invalidatePages();
                if (space == memoryAddressSpace || space == registerAddressSpace) generation++;
                super.clear();
            }

            // Only the short virtual overloads are emitted for indirect LOAD/STORE.
            // The long-offset executor and the bus's own backing I/O use the other overloads.
            @Override
            public byte[] read(long offset, int size) {
                return usesBus(space) ? bus.readBus(offset, size) : super.read(offset, size);
            }

            @Override
            public void write(long offset, byte[] value, int start, int length) {
                if (usesBus(space)) {
                    bus.writeBus(offset, start == 0 && length == value.length
                        ? value : Arrays.copyOfRange(value, start, start + length));
                }
                else {
                    super.write(offset, value, start, length);
                }
            }

            @Override
            public byte[] read(long offset, int size, Reason reason, PcodeStateCallbacks cb) {
                if (space == memoryAddressSpace && fitsPage(offset, size)) {
                    BoundPage page = initializedLocalPage(offset, size);
                    if (page != null) {
                        int start = (int) offset & PAGE_MASK;
                        return Arrays.copyOfRange(page.data, start, start + size);
                    }
                }
                if (isInitialized(offset, size)) return readBytes(offset, size, reason);
                return super.read(offset, size, reason, cb);
            }

            @Override
            public void write(long offset, byte[] value, int start, int length, PcodeStateCallbacks cb) {
                if (space == memoryAddressSpace && fitsPage(offset, length)) {
                    BoundPage page = initializedLocalPage(offset, length);
                    if (page != null) {
                        System.arraycopy(value, start, page.data, (int) offset & PAGE_MASK, length);
                        cb.dataWritten(MachineStatePiece.this, space.getAddress(offset), length, value);
                        return;
                    }
                }
                super.write(offset, value, start, length, cb);
            }

            CodeBytes bindCode(long offset, int size) {
                if (size > PAGE_SIZE || !isInitialized(offset, size)) return null;
                int start = (int) offset & PAGE_MASK;
                long base = offset - start;
                return new CodeBytes(generation, start, getDirect(base),
                    size <= PAGE_SIZE - start ? null : getDirect(base + PAGE_SIZE));
            }
        }

        @Override
        protected MachineStateSpace newSpace(AddressSpace space) {
            return new MachineStateSpace(space);
        }

        @Override
        public MachineStateSpace getForSpace(AddressSpace space, boolean toWrite) {
            if (space == registerAddressSpace) {
                if (registers == null) registers = (MachineStateSpace) super.getForSpace(space, toWrite);
                return registers;
            }
            if (space == uniqueSpace) {
                if (uniques == null) uniques = (MachineStateSpace) super.getForSpace(space, toWrite);
                return uniques;
            }
            if (space == memoryAddressSpace) {
                if (memory == null) memory = (MachineStateSpace) super.getForSpace(space, toWrite);
                return memory;
            }
            return (MachineStateSpace) super.getForSpace(space, toWrite);
        }

        BoundPage initializedLocalPage(AddressSpace space, long offset, int size, boolean quantize) {
            if ((space != registerAddressSpace && space != uniqueSpace) ||
                    (quantize && space.getAddressableUnitSize() != 1)) return null;
            MachineStateSpace storage = getForSpace(space, false);
            return storage != null && storage.fitsPage(offset, size)
                ? storage.initializedLocalPage(offset, size) : null;
        }

        BoundPage numberPage(Varnode node) {
            return node != null && node.getSize() <= Long.BYTES ? initializedLocalPage(
                node.getAddress().getAddressSpace(), node.getOffset(), node.getSize(), true) : null;
        }

        @Override
        public byte[] getVar(AddressSpace space, long offset, int size, boolean quantize, Reason reason) {
            BoundPage page = initializedLocalPage(space, offset, size, quantize);
            if (page == null) return super.getVar(space, offset, size, quantize, reason);
            int start = (int) offset & PAGE_MASK;
            // The byte executor may hold or reuse the returned value. Never expose a live page.
            return Arrays.copyOfRange(page.data, start, start + size);
        }

        @Override
        public void setVar(AddressSpace space, long offset, int size, boolean quantize, byte[] value) {
            BoundPage page = value.length == size
                ? initializedLocalPage(space, offset, size, quantize) : null;
            if (page == null) super.setVar(space, offset, size, quantize, value);
            else System.arraycopy(value, 0, page.data, (int) offset & PAGE_MASK, size);
        }

        boolean isInitialized(Varnode node) {
            AddressSpace space = node.getAddress().getAddressSpace();
            long offset = node.getOffset();
            int size = node.getSize();
            if (initializedLocalPage(space, offset, size, false) != null) return true;
            MachineStateSpace storage = getForSpace(space, false);
            return storage != null && storage.isInitialized(offset, size);
        }

        CodeBytes bindCode(Address address, int size) {
            if (address.getAddressSpace() != memoryAddressSpace) return null;
            MachineStateSpace storage = getForSpace(memoryAddressSpace, false);
            return storage == null ? null : storage.bindCode(address.getOffset(), size);
        }

        RunP1MEMachine.MemoryStateSnapshot checkpoint() {
            return RunP1MEMachine.MemoryStateSnapshot.capture(spaceMap);
        }

        void restore(RunP1MEMachine.MemoryStateSnapshot checkpoint) {
            // Restore replaces pages and can make previously defined bytes undefined.
            for (var space : spaceMap.values()) ((MachineStateSpace) space).invalidatePages();
            registers = uniques = memory = null;
            generation++;
            checkpoint.restore(spaceMap, space -> getForSpace(space, true));
        }
    }

    static final class MachineState extends JitDefaultBytesPcodeExecutorState
            implements RunP1MEMachine.CheckpointableBytesState {
        private final MachineStatePiece backingPiece;

        MachineState(Language language, RunP1MEMachine.Callbacks callbacks,
                PcodeThread<byte[]> thread) {
            // Ghidra 12.2's thread state and generated code require this concrete wrapper.
            // Its constructor fixes the inherited piece; forward its storage API to the
            // same backing piece that getForSpace() exposes to generated code.
            super(language, PcodeStateCallbacks.NONE);
            backingPiece = new MachineStatePiece(language, callbacks, thread);
        }

        @Override
        protected MachineStatePiece getPiece() {
            return backingPiece;
        }

        boolean isInitialized(Varnode node) {
            return backingPiece.isInitialized(node);
        }

        boolean matches(Plan plan, Address address) {
            CodeBytes binding = plan.codeBytes;
            if (binding == null || binding.generation() != backingPiece.generation) {
                plan.codeBytes = binding = backingPiece.bindCode(address, plan.encoding.length);
            }
            return binding != null && binding.matches(plan.encoding, plan.encodingWord);
        }

        @Override
        public Stream<PcodeExecutorStatePiece<?, ?>> streamPieces() {
            return backingPiece.streamPieces();
        }

        @Override
        public byte[] getVar(AddressSpace space, byte[] offset, int size, boolean quantize,
                Reason reason) {
            if (reason == Reason.EXECUTE_READ && backingPiece.usesBus(space)) {
                return backingPiece.bus.readBus(backingPiece.bus.offset(offset), size);
            }
            return backingPiece.getVar(space, offset, size, quantize, reason);
        }

        @Override
        public byte[] getVar(AddressSpace space, long offset, int size, boolean quantize,
                Reason reason) {
            return backingPiece.getVar(space, offset, size, quantize, reason);
        }

        @Override
        public byte[] getVarInternal(AddressSpace space, byte[] offset, int size, Reason reason) {
            return backingPiece.getVarInternal(space, offset, size, reason);
        }

        @Override
        public byte[] getVarInternal(AddressSpace space, long offset, int size, Reason reason) {
            return backingPiece.getVarInternal(space, offset, size, reason);
        }

        @Override
        public void setVar(AddressSpace space, byte[] offset, int size, boolean quantize,
                byte[] value) {
            if (backingPiece.usesBus(space)) {
                backingPiece.bus.writeBus(backingPiece.bus.offset(offset),
                    value.length == size ? value : Arrays.copyOf(value, size));
                return;
            }
            backingPiece.setVar(space, offset, size, quantize, value);
        }

        @Override
        public void setVar(AddressSpace space, long offset, int size, boolean quantize,
                byte[] value) {
            backingPiece.setVar(space, offset, size, quantize, value);
        }

        @Override
        public void setVarInternal(AddressSpace space, byte[] offset, int size, byte[] value) {
            backingPiece.setVarInternal(space, offset, size, value);
        }

        @Override
        public void setVarInternal(AddressSpace space, long offset, int size, byte[] value) {
            backingPiece.setVarInternal(space, offset, size, value);
        }

        @Override
        public Map<Register, byte[]> getRegisterValues() {
            return backingPiece.getRegisterValues();
        }

        @Override
        public MemBuffer getConcreteBuffer(Address address, Purpose purpose) {
            return backingPiece.getConcreteBuffer(address, purpose);
        }

        @Override
        public RunP1MEMachine.MemoryStateSnapshot checkpoint() {
            return backingPiece.checkpoint();
        }

        @Override
        public void restore(RunP1MEMachine.MemoryStateSnapshot checkpoint) {
            backingPiece.restore(checkpoint);
        }
    }

    private record StableContext(Address counter, RegisterValue input, RegisterValue defaults, long bits) {}

    private static final class Plan {
        final RegisterValue context;
        final PseudoInstruction instruction;
        final Address address;
        final byte[] encoding;
        final long encodingWord;
        CodeBytes codeBytes;
        final PcodeProgram program;
        Address fallThrough;
        StableContext stableContext;
        long bindingGeneration = -1;
        long promotionStart;
        int untilCompile = PROMOTION_HITS;
        boolean nativeWarm;
        boolean scalarAttempted;
        boolean scalarBus;
        ScalarOp[] scalar;
        Address indirectTarget;
        int busOpIndex = -1;
        boolean straightLine;
        ScalarOp[] busPrefix;
        JitCompiledPassageClass translation;
        EntryPoint entry;
        RunP1MEMachine.Callbacks.InstructionObservation observation;

        Plan(RegisterValue context, PseudoInstruction instruction) {
            this.context = context;
            this.instruction = instruction;
            address = instruction.getAddress();
            encoding = new byte[instruction.getLength()];
            instruction.getBytes(encoding, 0);
            encodingWord = encoding.length <= Long.BYTES
                ? Utils.bytesToLong(encoding, encoding.length, false) : 0;
            program = PcodeProgram.fromInstruction(instruction);
        }

        boolean isAt(Address address, RegisterValue decodeContext) {
            return this.address.equals(address) && Objects.equals(context, decodeContext);
        }

        // Direct page accesses neither fault on undefined bytes nor define new ones.
        // Interpreted warm-up defines temporaries; a restore drops this proof.
        boolean local(Varnode var, MachineState state) {
            return var == null || var.isConstant() ||
                ((var.isRegister() || var.isUnique()) && state.isInitialized(var));
        }

        // A device call may observe the whole pre-bus state. Keep even the EA's
        // unique writes and STORE's ll_valid update in the interpreted prefix.
        // The tail may touch only GPRs/uniques: the bus does not write these.
        private static boolean gpr(Varnode var) {
            return var != null && var.isRegister() && var.getOffset() >= 0
                && var.getOffset() <= 32 * 4 - var.getSize();
        }

        private static boolean busLocal(Varnode var) {
            return var.isUnique() || gpr(var);
        }

        // Retain the decoder's bus eligibility: live-ins and full-width copies
        // or additions of a constant do not fold. Defer other address shapes.
        boolean hasUnfoldedBusAddress() {
            List<PcodeOp> code = program.getCode();
            Varnode value = code.get(busOpIndex).getInput(1);
            for (int i = busOpIndex - 1; i >= 0; i--) {
                PcodeOp op = code.get(i);
                Varnode output = op.getOutput();
                if (output == null || !value.intersects(output)) continue;
                if (!value.equals(output)) return false;
                if (op.getOpcode() == PcodeOp.COPY) {
                    value = op.getInput(0);
                }
                else if (op.getOpcode() == PcodeOp.INT_ADD) {
                    Varnode first = op.getInput(0);
                    Varnode second = op.getInput(1);
                    if (first.isConstant()) value = second;
                    else if (second.isConstant()) value = first;
                    else return false;
                }
                else {
                    return false;
                }
                if (!busLocal(value) || value.getSize() != output.getSize()) return false;
            }
            return true;
        }

        boolean compilable(MachineState state, AddressSpace memorySpace) {
            List<PcodeOp> code = program.getCode();
            int busIndex = -1;
            Varnode loaded = null;
            boolean straight = true;
            for (int index = 0; index < code.size(); index++) {
                PcodeOp op = code.get(index);
                int kind = op.getOpcode();
                Varnode output = op.getOutput();
                int first = 0;
                if (kind == PcodeOp.LOAD || kind == PcodeOp.STORE) {
                    if (busIndex != -1 || !straight) return false;
                    busIndex = index;
                    boolean load = kind == PcodeOp.LOAD;
                    Varnode address = op.getInput(1);
                    Varnode data = load ? output : op.getInput(2);
                    int width = data.getSize();
                    if (op.getInput(0).getOffset() != memorySpace.getSpaceID()
                            || memorySpace.getAddressableUnitSize() != 1
                            || address.getSize() != memorySpace.getPointerSize()
                            || !busLocal(address)
                            || !(busLocal(data) || (!load && data.isConstant()))
                            || !(width == 1 || width == 2 || width == 4 || width == 8)) {
                        return false;
                    }
                    loaded = output;
                    first = 1; // Skip the encoded address space.
                }
                else if (busIndex != -1) {
                    // A LOAD is removable in 12.2. Require a chain from its
                    // result to a retired GPR, with no independent work after it.
                    if (loaded == null || !(kind == PcodeOp.COPY || kind == PcodeOp.INT_SEXT
                            || kind == PcodeOp.INT_ZEXT || kind == PcodeOp.SUBPIECE)
                            || !loaded.equals(op.getInput(0)) || !busLocal(output)
                            || (kind == PcodeOp.SUBPIECE && !op.getInput(1).isConstant())) {
                        return false;
                    }
                    loaded = output;
                }
                else if (kind == PcodeOp.BRANCH || kind == PcodeOp.CBRANCH || kind == PcodeOp.CALL) {
                    straight = false;
                    Varnode target = op.getInput(0);
                    // A branch back to this instruction could loop inside the passage.
                    if (!target.isAddress() || target.getAddress().equals(address))
                        return false;
                    first = 1;
                }
                else if (!(kind == PcodeOp.COPY || kind == PcodeOp.SUBPIECE ||
                        kind == PcodeOp.PIECE ||
                        (kind >= PcodeOp.INT_EQUAL && kind <= PcodeOp.INT_MULT) ||
                        (kind >= PcodeOp.BOOL_NEGATE && kind <= PcodeOp.BOOL_OR))) {
                    return false;
                }
                if (!local(output, state)) return false;
                for (int i = first; i < op.getNumInputs(); i++) {
                    Varnode input = op.getInput(i);
                    if (!local(input, state)) return false;
                    // Ghidra 12.2 can leave the upper bytes intact for an in-place
                    // extension: r19:4 = zext(r19:1). Let the byte executor handle
                    // mixed-width aliases, without excluding non-aliasing extensions.
                    if (output != null && input.getSize() != output.getSize() &&
                            input.intersects(output)) return false;
                }
            }
            if (loaded != null && !gpr(loaded)) return false;
            busOpIndex = busIndex;
            straightLine = straight;
            return true;
        }
    }

    private static final class Decoder extends SleighInstructionDecoder {
        private static final int TABLE_BITS = 10;
        private static final int TABLE_SIZE = 1 << TABLE_BITS;
        private final Plan[][][] pages = new Plan[1 << (32 - PAGE_SHIFT - TABLE_BITS)][][];
        private final Map<Address, Plan> otherAddresses = new HashMap<>();
        private final AddressSpace codeSpace;
        final MachineState memory;
        Plan current;
        boolean verified;

        Decoder(Language language, MachineState memory) {
            super(language, memory);
            this.memory = memory;
            codeSpace = language.getDefaultSpace();
        }

        @Override
        protected boolean useCachedInstruction(Address address, RegisterValue context) {
            return false; // The upstream block cache doesn't check for modified instruction bytes.
        }

        @Override
        public PseudoInstruction decodeInstruction(Address address, RegisterValue context) {
            long offset = address.getOffset();
            Plan plan;
            if (address.getAddressSpace() == codeSpace && (offset & ~0xffff_fffeL) == 0) {
                int pageIndex = (int) (offset >>> PAGE_SHIFT);
                int groupIndex = pageIndex >>> TABLE_BITS;
                Plan[][] group = pages[groupIndex];
                if (group == null) pages[groupIndex] = group = new Plan[TABLE_SIZE][];
                int withinGroup = pageIndex & (TABLE_SIZE - 1);
                Plan[] page = group[withinGroup];
                if (page == null) group[withinGroup] = page = new Plan[PAGE_SIZE / 2];
                int slot = ((int) offset & PAGE_MASK) >>> 1;
                plan = page[slot];
                verified = plan != null && Objects.equals(plan.context, context) && memory.matches(plan, address);
                if (!verified) page[slot] = plan = new Plan(context, super.decodeInstruction(address, context));
            }
            else {
                plan = otherAddresses.get(address);
                verified = plan != null && Objects.equals(plan.context, context) && memory.matches(plan, address);
                if (!verified) {
                    plan = new Plan(context, super.decodeInstruction(address, context));
                    otherAddresses.put(address, plan);
                }
            }
            current = plan;
            lengthWithDelays = plan.encoding.length; // RH850 has no delay slots.
            return plan.instruction;
        }

        @Override
        public PseudoInstruction getLastInstruction() {
            return current == null ? null : current.instruction;
        }
    }

    final class MachineThread extends JitPcodeThread {
        long compiledInstructions;
        private Plan compiling;
        private Plan pendingBusFrame;
        private int pendingFrameIndex;
        private long instructionVisits;
        private final Map<String, ProcessorRegister> namedRegisters = new HashMap<>();
        private final Map<Register, ProcessorRegister> registerBindings = new IdentityHashMap<>();
        private final ProcessorRegister[] registerSlots = new ProcessorRegister[256];
        private boolean verifiedFetch;
        private final MachineStatePiece retirementState = localPiece();
        private final boolean bigEndian = language.isBigEndian();
        private final PcodeUseropSymbolMap executionSymbols = getUseropLibrary().getSymbols(language);
        private final AddressSpace byteCounterSpace = language.getDefaultSpace().getAddressableUnitSize() == 1
            ? language.getDefaultSpace() : null;
        private final ProcessorRegister counterRetirement = new ProcessorRegister(pc, bigEndian);
        private final ProcessorRegister contextRetirement = contextreg == Register.NO_CONTEXT
            ? null : new ProcessorRegister(contextreg, true);
        private final ProcessorRegister pswRegister = bindNamed("PSW");
        private final ProcessorRegister mpmRegister = bindNamed("MPM");
        private final ProcessorRegister mctlRegister = bindNamed("MCTL");
        private final ProcessorRegister intcfgRegister = bindNamed("INTCFG");
        private final ProcessorRegister isprRegister = bindNamed("ISPR");
        private RegisterValue stableJitContextInput;
        private RegisterValue stableJitContextValue;
        private long stableJitContextBits;

        MachineThread(String name) {
            super(name, P1MEJitMachine.this);
        }

        @Override
        protected PcodeThreadExecutor<byte[]> createExecutor() {
            return new LocalExecutor();
        }

        private final class LocalExecutor extends PcodeThreadExecutor<byte[]> {
            private final MachineStatePiece local = localPiece();
            private final boolean bigEndian = language.isBigEndian();

            LocalExecutor() {
                super(MachineThread.this);
            }

            private boolean isScalarConstant(Varnode node) {
                return node.isConstant() && node.getSize() > 0 && node.getSize() <= Long.BYTES;
            }

            private long number(Varnode node, BoundPage page) {
                return page == null ? node.getOffset() & Utils.calc_mask(node.getSize())
                    : page.readNumber((int) node.getOffset() & PAGE_MASK, node.getSize(), bigEndian);
            }

            private ScalarOperand bindOperand(Varnode node) {
                if (isScalarConstant(node)) {
                    return new ScalarOperand(null, 0, node.getSize(), number(node, null));
                }
                BoundPage page = local.numberPage(node);
                return page == null ? null : new ScalarOperand(
                    page, (int) node.getOffset() & PAGE_MASK, node.getSize(), 0);
            }

            private ScalarOp bindScalarOp(PcodeOp op) {
                OpBehavior behavior = OpBehaviorFactory.getOpBehavior(op.getOpcode());
                int arity = behavior instanceof UnaryOpBehavior ? 1
                    : behavior instanceof BinaryOpBehavior ? 2 : 0;
                Varnode out = op.getOutput();
                if (arity == 0 || op.getNumInputs() != arity || out == null || out.isConstant()) {
                    return null;
                }
                ScalarOperand output = bindOperand(out);
                ScalarOperand left = bindOperand(op.getInput(0));
                ScalarOperand right = arity == 2 ? bindOperand(op.getInput(1)) : null;
                return output == null || left == null || (arity == 2 && right == null)
                    ? null : new ScalarOp(behavior, output, left, right, op.getOpcode(), null);
            }

            private ScalarOp bindInstructionOp(PcodeOp op) {
                int opcode = op.getOpcode();
                switch (opcode) {
                    case PcodeOp.LOAD, PcodeOp.STORE -> {
                        if (byteCounterSpace == null || byteCounterSpace.getPointerSize() != Integer.BYTES ||
                                op.getInput(0).getOffset() != byteCounterSpace.getSpaceID()) return null;
                        ScalarOperand address = bindOperand(op.getInput(1));
                        if (address == null || address.size != Integer.BYTES) return null;
                        boolean load = opcode == PcodeOp.LOAD;
                        ScalarOperand value = bindOperand(load ? op.getOutput() : op.getInput(2));
                        if (value == null || (load && value.page == null)) return null;
                        return new ScalarOp(null, load ? value : null, address, load ? null : value, opcode, null);
                    }
                    case PcodeOp.BRANCH, PcodeOp.CBRANCH, PcodeOp.CALL -> {
                        // Internal p-code control flow keeps the native frame.
                        Address target = op.getInput(0).getAddress();
                        if (byteCounterSpace == null || target.getAddressSpace() != byteCounterSpace) return null;
                        ScalarOperand condition = opcode == PcodeOp.CBRANCH ? bindOperand(op.getInput(1)) : null;
                        if (opcode == PcodeOp.CBRANCH && condition == null) return null;
                        return new ScalarOp(null, null, condition, null, opcode, target);
                    }
                    case PcodeOp.BRANCHIND, PcodeOp.CALLIND, PcodeOp.RETURN -> {
                        Varnode input = op.getInput(0);
                        if (byteCounterSpace == null || byteCounterSpace.getPointerSize() != Integer.BYTES ||
                                byteCounterSpace.getMaxAddress().getOffset() != 0xffff_ffffL ||
                                op.getSeqnum().getTarget().getAddressSpace() != byteCounterSpace ||
                                input.getSize() != Integer.BYTES) return null;
                        ScalarOperand address = bindOperand(input);
                        return address == null ? null : new ScalarOp(null, null, address, null, opcode, null);
                    }
                    default -> {
                        return bindScalarOp(op);
                    }
                }
            }

            @Override
            public void executeUnaryOp(PcodeOp op, UnaryOpBehavior behavior) {
                Varnode out = op.getOutput();
                BoundPage destination = local.numberPage(out);
                if (destination != null) {
                    Varnode input = op.getInput(0);
                    BoundPage source = local.numberPage(input);
                    if (source != null || isScalarConstant(input)) {
                        long value = behavior.evaluateUnary(out.getSize(), input.getSize(), number(input, source));
                        destination.writeNumber((int) out.getOffset() & PAGE_MASK, out.getSize(), bigEndian, value);
                        return;
                    }
                }
                super.executeUnaryOp(op, behavior);
            }

            @Override
            public void executeBinaryOp(PcodeOp op, BinaryOpBehavior behavior) {
                Varnode out = op.getOutput();
                BoundPage destination = local.numberPage(out);
                if (destination != null) {
                    Varnode left = op.getInput(0);
                    Varnode right = op.getInput(1);
                    BoundPage leftPage = local.numberPage(left);
                    BoundPage rightPage = local.numberPage(right);
                    if ((leftPage != null || isScalarConstant(left)) &&
                            (rightPage != null || isScalarConstant(right))) {
                        long value = behavior.evaluateBinary(out.getSize(), left.getSize(),
                            number(left, leftPage), number(right, rightPage));
                        destination.writeNumber((int) out.getOffset() & PAGE_MASK, out.getSize(), bigEndian, value);
                        return;
                    }
                }
                super.executeBinaryOp(op, behavior);
            }
        }

        @Override
        protected SleighInstructionDecoder createInstructionDecoder(PcodeExecutorState<byte[]> shared) {
            return new Decoder(language, (MachineState) shared);
        }

        @Override
        protected JitPassageDecoder createPassageDecoder() {
            return new JitPassageDecoder(this) {
                @Override
                public JitPassage decodePassage(AddrCtx seed, int maxOps) {
                    JitPassage passage = super.decodePassage(seed, maxOps);
                    if (passage.getInstructions().size() != 1 ||
                            passage.getInstructions().getFirst() != compiling.instruction) {
                        throw new IllegalStateException("Expected one scheduled instruction at " + seed);
                    }
                    return passage;
                }

                @Override
                public PseudoInstruction decodeInstruction(Address address, RegisterValue context) {
                    // The scheduler already checked execute access and the exact bytes.
                    // Translate that same instruction, without consulting memory again.
                    if (compiling == null || !compiling.isAt(address, context)) {
                        throw new IllegalStateException("Passage decoded beyond its seed: " + address);
                    }
                    return compiling.instruction;
                }
            };
        }

        @Override
        public boolean hasEntry(AddrCtx at) {
            // Quotas are checked between strides. This hook cuts off the first
            // stride at fall-through, making Ghidra emit its normal side exit.
            return compiling != null && !compiling.isAt(at.address, at.rvCtx);
        }

        @Override
        public EntryPoint getEntry(AddrCtx at) {
            // Generated direct exits retire PC/context before returning the chained
            // entry. Do not let ExitSlot compile or retain a successor binding.
            return null;
        }

        @Override
        public void run() {
            throw new UnsupportedOperationException("Use the P1M-E instruction scheduler");
        }

        private JitCompiledPassageClass compileLinear(Plan plan, AddrCtx seed) {
            if (!plan.straightLine || (plan.busOpIndex >= 0 && !plan.hasUnfoldedBusAddress())) return null;
            Address target = plan.instruction.getMaxAddress().next();
            if (target == null) return null;
            if (seed.rvCtx != null) {
                StableContext stable = plan.stableContext;
                // The interpreter proved this flow idempotent without commits.
                // Ghidra computes fall-through flow from the *source* defaults.
                if (stable == null || !stable.counter().equals(target) || !stable.input().equals(seed.rvCtx)
                        || !Objects.equals(stable.defaults(), defaultContext.getDefaultValue(contextreg, seed.address))) {
                    return null;
                }
            }
            AddrCtx next = new AddrCtx(seed.rvCtx, target);
            List<PcodeOp> source = plan.program.getCode();
            int start = Math.max(0, plan.busOpIndex);
            List<PcodeOp> code = new ArrayList<>(Math.max(1, source.size() - start) + 1);
            for (int i = start; i < source.size(); i++) code.add(new DecodedPcodeOp(seed, source.get(i)));
            if (code.isEmpty()) code.add(new NopPcodeOp(seed, 0));
            PcodeOp entry = new EntryPcodeOp(seed);
            PcodeOp exit = ExitPcodeOp.exit(next);
            PcodeOp first = code.getFirst();
            code.add(exit);
            // This passage has no internal control flow, injections, or userops.
            // Use the already decoded plan, without another folding interpreter pass.
            // A bus tail starts at the virtual operation, with no folded prefix values.
            return compiler.compilePassage(JIT_LOOKUP, new JitPassage(getLanguage(), seed, code,
                passageDecoder.library, List.of(plan.instruction),
                Map.of(entry, new RIntBranch(entry, first, false, CtxReach.WITHOUT_CTXMOD),
                    exit, new RExtBranch(exit, next, null, CtxReach.WITHOUT_CTXMOD)),
                Map.of(first, seed), Map.of()));
        }

        private JitCompiledPassageClass compileBusTail(Plan plan, AddrCtx seed) {
            JitPassage decoded = passageDecoder.decodePassage(seed, getConfiguration().maxPassageOps());
            List<PcodeOp> code = decoded.getCode();
            List<PcodeOp> source = plan.program.getCode();
            if (code.size() != source.size() + 1) return null;
            PcodeOp busOp = code.get(plan.busOpIndex);
            PcodeOp exit = code.getLast();
            // Literal addresses were rejected by admission. Reject addresses
            // folded by the decoder too; 12.2 models those as direct memory.
            if (decoded.getFoldedOperand(busOp, 1) != null) return null;
            var exitBranch = decoded.getBranches().get(exit);
            if (busOp.getOpcode() != source.get(plan.busOpIndex).getOpcode()
                    || !(exit instanceof ExitPcodeOp) || exitBranch == null) {
                return null;
            }
            // The prefix has already committed to backing state when this
            // entry runs. Do not carry any folded values across that boundary.
            PcodeOp entry = new EntryPcodeOp(seed);
            JitPassage tail = new JitPassage(getLanguage(), seed,
                code.subList(plan.busOpIndex, code.size()), decoded.getDecodeLibrary(),
                decoded.getInstructions(),
                Map.of(entry, new RIntBranch(entry, busOp, false, CtxReach.WITHOUT_CTXMOD),
                    exit, exitBranch),
                Map.of(busOp, seed), Map.of());
            return compiler.compilePassage(JIT_LOOKUP, tail);
        }

        private EntryPoint prepareEntry(Plan plan) {
            if (plan.translation == null && instructionVisits - plan.promotionStart > PROMOTION_WINDOW) {
                plan.promotionStart = instructionVisits;
                plan.untilCompile = PROMOTION_HITS - 1;
                return null;
            }
            // Admission covers decoded p-code, not arbitrary Ghidra injections.
            if (getInject(plan.address) != null) return null;
            if (!plan.compilable((MachineState) getState().getLocalState(), language.getDefaultSpace())) {
                if (plan.translation != null) {
                    plan.untilCompile = PROMOTION_HITS; // Restored registers may not have been defined yet.
                }
                return null;
            }
            if (plan.translation == null) {
                AddrCtx seed = new AddrCtx(plan.context, plan.address);
                // The byte-validated plan, not Ghidra's address/context cache,
                // owns this translation across overlays and restores.
                plan.translation = compileLinear(plan, seed);
                if (plan.translation == null) {
                    compiling = plan;
                    try {
                        plan.translation = plan.busOpIndex < 0
                            ? P1MEJitMachine.this.compileWithMaxOpsBackoff(seed, passageDecoder)
                            : compileBusTail(plan, seed);
                    }
                    finally {
                        compiling = null;
                    }
                    if (plan.translation == null) return null;
                }
            }
            // A single scheduled instruction exports exactly its seed at index
            // zero. Always create a fresh instance to bind the current pages.
            plan.entry = new EntryPointPrototype(plan.translation, 0).createInstance(this);
            if (plan.busOpIndex >= 0) {
                plan.busPrefix = plan.scalar == null ? bindBusPrefix(plan) : plan.scalar;
            }
            return plan.entry;
        }

        private ScalarOp[] bindBusPrefix(Plan plan) {
            if (plan.busOpIndex == 0) return ScalarOp.EMPTY;
            ScalarOp[] prefix = new ScalarOp[plan.busOpIndex];
            LocalExecutor local = (LocalExecutor) executor;
            List<PcodeOp> code = plan.program.getCode();
            for (int i = 0; i < prefix.length; i++) {
                ScalarOp op = local.bindScalarOp(code.get(i));
                if (op == null) return null;
                prefix[i] = op;
            }
            return prefix;
        }

        private ScalarOp[] bindScalar(Plan plan) {
            List<PcodeOp> code = plan.program.getCode();
            if (code.isEmpty()) return ScalarOp.EMPTY;
            ScalarOp[] ops = new ScalarOp[code.size()];
            LocalExecutor local = (LocalExecutor) executor;
            boolean bus = false;
            for (int i = 0; i < ops.length; i++) {
                ScalarOp op = local.bindInstructionOp(code.get(i));
                if (op == null) return null;
                bus |= op.opcode == PcodeOp.LOAD || op.opcode == PcodeOp.STORE;
                ops[i] = op;
            }
            plan.scalarBus = bus;
            return ops;
        }

        private PcodeFrame materializeFrame(Plan plan, int nextOp) {
            if (frame == null) {
                frame = beginPlan(plan);
            }
            while (frame.index() >= 0 && frame.index() < nextOp) frame.advance();
            return frame;
        }

        @Override
        public PcodeFrame getFrame() {
            Plan pending = pendingBusFrame;
            return pending == null ? frame : materializeFrame(pending, pendingFrameIndex);
        }

        private void runBoundBusPrefix(Plan plan, ScalarOp[] prefix) {
            for (int i = 0; i < plan.busOpIndex; i++) {
                // Native step advances the frame before checking suspension.
                if (isSuspended() || P1MEJitMachine.this.suspended) {
                    throw new SuspendedPcodeExecutionException(materializeFrame(plan, i + 1), null);
                }
                try {
                    prefix[i].execute(bigEndian);
                    stepped(); // Preserve the native IGNORE_STEP software-interrupt transition.
                }
                catch (RuntimeException fault) {
                    throw new PcodeExecutionException(fault.getMessage(),
                        materializeFrame(plan, i + 1), fault);
                }
            }
        }

        private void runBusTail(Plan plan, EntryPoint entry) {
            ScalarOp[] prefix = plan.busPrefix;
            if (prefix == null) {
                var userops = getUseropLibrary();
                frame = beginPlan(plan);
                while (frame.index() < plan.busOpIndex) executor.step(frame, userops);
            }
            else {
                // These operands were all initialized and bound to live local pages
                // after admission. Write every result before entering the device, even uniques.
                runBoundBusPrefix(plan, prefix);
            }
            if (isSuspended() || P1MEJitMachine.this.suspended) {
                materializeFrame(plan, plan.busOpIndex);
                finishInstruction(); // Retain the executor's native suspension check.
                return;
            }
            if (frame != null) executor.skip(frame);
            else {
                pendingBusFrame = plan;
                pendingFrameIndex = plan.busOpIndex + 1;
            }
            try {
                entry.run();
                stepped();
            }
            catch (RuntimeException fault) {
                // The upstream virtual call does not retire locals or handle
                // exceptions. No p-code preceding the bus is pending here.
                throw new PcodeExecutionException(fault.getMessage(),
                    materializeFrame(plan, plan.busOpIndex + 1), fault);
            }
            finally {
                pendingBusFrame = null;
            }
            frame = null;
            instruction = null;
            compiledInstructions++;
        }

        private void scalarBus(Plan plan, ScalarOp op, int nextOp) {
            long address = op.left.read(bigEndian);
            pendingBusFrame = plan;
            pendingFrameIndex = nextOp;
            try {
                if (op.opcode == PcodeOp.LOAD) {
                    ScalarOperand out = op.output;
                    byte[] value = callbacks.readBus(address, out.size);
                    System.arraycopy(value, 0, out.page.data, out.start, out.size);
                }
                else {
                    ScalarOperand in = op.right;
                    callbacks.writeBus(address, RunP1MEMachine.bytes(in.read(bigEndian), in.size, bigEndian));
                }
            }
            finally {
                pendingBusFrame = null;
            }
        }

        private void runScalar(Plan plan, ScalarOp[] ops) {
            for (int i = 0; i < ops.length; i++) {
                if (frame != null) frame.advance();
                if (isSuspended() || P1MEJitMachine.this.suspended) {
                    throw new SuspendedPcodeExecutionException(materializeFrame(plan, i + 1), null);
                }
                Address target = null;
                ScalarOp op = ops[i];
                try {
                    if (op.behavior != null) op.execute(bigEndian);
                    else if (op.opcode == PcodeOp.LOAD || op.opcode == PcodeOp.STORE) {
                        scalarBus(plan, op, i + 1);
                    }
                    else if (op.target != null) {
                        if (op.left == null || op.left.read(bigEndian) != 0) target = op.target;
                    }
                    else {
                        long offset = op.left.read(bigEndian);
                        target = plan.indirectTarget;
                        if (target == null || target.getOffset() != offset) {
                            plan.indirectTarget = target = byteCounterSpace.getAddress(offset);
                        }
                    }
                    if (target != null) {
                        if (frame != null) frame.finishAsBranch();
                        retireCounter(target);
                        decoder.branched(target);
                    }
                    stepped();
                }
                catch (RuntimeException fault) {
                    throw new PcodeExecutionException(fault.getMessage(), materializeFrame(plan, i + 1), fault);
                }
                if (target != null) {
                    retirePlan(plan, false);
                    return;
                }
            }
            retirePlan(plan, true);
        }

        /** Rebind to live, initialized register bytes after state restore. */
        final class ProcessorRegister {
            private final Register register;
            private final int size;
            private final int start;
            private final boolean bigEndian;
            private final boolean canBind;
            private long generation = -1;
            private BoundPage page;

            ProcessorRegister(Register register, boolean bigEndian) {
                this.register = register;
                this.size = register.getMinimumByteSize();
                this.start = (int) register.getOffset() & PAGE_MASK;
                this.bigEndian = bigEndian;
                AddressSpace space = register.getAddressSpace();
                canBind = space == retirementState.registerAddressSpace && space.getAddressableUnitSize() == 1
                    && size > 0 && size <= Long.BYTES && size <= PAGE_SIZE - start;
            }

            private BoundPage page() {
                if (!canBind) return null;
                long current = retirementState.generation;
                if (page == null || generation != current) {
                    page = retirementState.initializedLocalPage(
                        register.getAddressSpace(), register.getOffset(), size, true);
                    generation = current;
                }
                return page;
            }

            long read() {
                BoundPage source = page();
                return (source == null ? inspectRegister(register) : source.readNumber(start, size, bigEndian))
                    & 0xffff_ffffL;
            }

            boolean write(long value) {
                BoundPage destination = page();
                if (destination == null) return false;
                destination.writeNumber(start, size, bigEndian, value);
                return true;
            }
        }

        private void retireCounter(Address counter) {
            long offset = counter.getAddressSpace() == byteCounterSpace
                ? counter.getOffset() : counter.getAddressableWordOffset();
            if (counterRetirement.write(offset)) setCounter(counter);
            else writeCounter(counter);
        }

        @Override
        public void writeCounterAndContext(Address counter, RegisterValue nextContext) {
            retireCounter(counter);
            if (nextContext == null) return;
            if (contextRetirement == null) {
                writeContext(nextContext);
                return;
            }
            RegisterValue previous = getContext();
            if (nextContext.equals(stableJitContextInput) && Objects.equals(previous, stableJitContextValue)
                    && contextRetirement.write(stableJitContextBits)) return;

            writeContext(nextContext);
            if (contextRetirement.size <= Long.BYTES && previous != null && previous.equals(getContext())) {
                stableJitContextInput = nextContext;
                stableJitContextValue = previous;
                stableJitContextBits = previous.getUnsignedValueIgnoreMask().longValue();
            }
        }

        private void retireInterpretedContext(Plan plan, Address counter) {
            RegisterValue previous = getContext();
            RegisterValue defaults = defaultContext.getDefaultValue(contextreg, counter);
            StableContext stable = plan.stableContext;
            if (stable != null && stable.counter().equals(counter) && stable.input().equals(previous)
                    && Objects.equals(stable.defaults(), defaults)
                    && contextRetirement.write(stable.bits())) return;

            RegisterValue merged = new RegisterValue(contextreg, BigInteger.ZERO).combineValues(defaults)
                .combineValues(defaultContext.getFlowValue(previous));
            RegisterValue commits = getContextAfterCommits();
            writeContext(merged.combineValues(commits));
            if (contextRetirement.size <= Long.BYTES && previous != null && previous.equals(getContext())
                    && commits.getValueMask().signum() == 0) {
                // Retire the same concrete context bytes every time. Only omit recomputing
                // an idempotent transition with no parser commits.
                plan.stableContext = new StableContext(counter, previous, defaults,
                    previous.getUnsignedValueIgnoreMask().longValue());
            }
        }

        private PcodeFrame beginPlan(Plan plan) {
            return executor.begin(plan.program.getCode(), executionSymbols);
        }

        private void finishPlan(Plan plan) {
            if (modifier != null) {
                finishInstruction();
                return;
            }
            executor.finish(frame, getUseropLibrary());
            retirePlan(plan, frame.isFallThrough());
        }

        private void retirePlan(Plan plan, boolean fallThrough) {
            Address counter = getCounter();
            if (fallThrough) {
                if (counter.equals(plan.address)) {
                    if (plan.fallThrough == null) plan.fallThrough = counter.addWrap(plan.encoding.length);
                    counter = plan.fallThrough;
                }
                else {
                    counter = counter.addWrap(decoder.getLastLengthWithDelays());
                }
                retireCounter(counter);
            }
            if (contextreg != Register.NO_CONTEXT) retireInterpretedContext(plan, counter);
            postExecuteInstruction();
            // Ghidra's machine callback is NONE. The scheduler calls the model callback below,
            // after retiring the frame, for both the byte executor and compiled entries.
            frame = null;
            instruction = null;
        }

        RunP1MEMachine.Callbacks.InstructionObservation currentObservation(Instruction instruction) {
            Plan plan = ((Decoder) decoder).current;
            if (plan == null || plan.instruction != instruction) return null;
            if (plan.observation == null) plan.observation = callbacks.decodeObservation(instruction, plan.program);
            return plan.observation;
        }

        boolean hasVerifiedInstructionBytes(Instruction instruction) {
            return verifiedFetch && ((Decoder) decoder).current.instruction == instruction;
        }

        private MachineStatePiece localPiece() {
            return ((MachineState) getState().getLocalState()).backingPiece;
        }

        private long inspectRegister(Register register) {
            byte[] value = getState().getVar(register, Reason.INSPECT);
            return Utils.bytesToLong(value, value.length, bigEndian);
        }

        ProcessorRegister bindProcessorRegister(Register register) {
            int offset = (int) register.getOffset();
            int slot = ((offset >>> 2) ^ (offset >>> 10)) & (registerSlots.length - 1);
            ProcessorRegister binding = registerSlots[slot];
            if (binding != null && binding.register == register) return binding;
            binding = registerBindings.get(register);
            if (binding == null) {
                binding = new ProcessorRegister(register, bigEndian);
                registerBindings.put(register, binding);
            }
            return registerSlots[slot] = binding;
        }

        private ProcessorRegister bindNamed(String name) {
            Register register = language.getRegister(name);
            return register == null ? null : bindProcessorRegister(register);
        }

        private ProcessorRegister namedRegister(String name) {
            // Model-owned literal names dominate processor state checks.
            if (name == "PSW") return pswRegister;
            if (name == "MPM") return mpmRegister;
            if (name == "MCTL") return mctlRegister;
            if (name == "INTCFG") return intcfgRegister;
            if (name == "ISPR") return isprRegister;
            ProcessorRegister binding = namedRegisters.get(name);
            if (binding == null) {
                binding = bindNamed(name);
                if (binding != null) namedRegisters.put(name, binding);
            }
            return binding;
        }

        long processorRegister(String name) {
            ProcessorRegister binding = namedRegister(name);
            if (binding == null) throw new IllegalStateException("processor model lacks register " + name);
            return binding.read();
        }

        long processorRegister(Register register) {
            return bindProcessorRegister(register).read();
        }


        void processorRegister(String name, long value) {
            ProcessorRegister binding = namedRegister(name);
            if (binding == null) throw new IllegalArgumentException("unknown processor register: " + name);
            Register register = binding.register;
            int size = register.getNumBytes();
            if (size == binding.size && binding.write(value)) return;
            getState().setVar(register, RunP1MEMachine.bytes(value, size, bigEndian));
        }

        boolean readObservedRegister(Register register, long[] result, int index) {
            ProcessorRegister binding = bindProcessorRegister(register);
            if (binding.canBind) {
                BoundPage page = binding.page();
                // The machine's INSPECT callback throws without side effects for undefined registers.
                if (page == null) return false;
                result[index] = page.readNumber(binding.start, binding.size, bigEndian);
                return true;
            }
            try {
                result[index] = inspectRegister(register);
                return true;
            }
            catch (RuntimeException unavailable) {
                return false;
            }
        }

        @Override
        public void stepInstruction() {
            assertCompletedInstruction();
            Address fetchStart = getCounter();
            long fetchEnd = callbacks.authorizeInstructionStart(this, fetchStart);
            instruction = decoder.decodeInstruction(getCounter(), getContext());
            Plan plan = ((Decoder) decoder).current;
            preExecuteInstruction();
            // Keep the authorization span on this step's stack. A legacy state modifier
            // invalidates both the permission and decoder byte proofs.
            verifiedFetch = modifier == null && ((Decoder) decoder).verified;
            try {
                callbacks.beforeExecuteInstruction(this, instruction, fetchStart,
                    modifier == null ? fetchEnd : 0);
            }
            finally {
                verifiedFetch = false;
            }
            instructionVisits++;
            long generation = retirementState.generation;
            if (plan.bindingGeneration != generation) {
                plan.bindingGeneration = generation;
                plan.entry = null;
                plan.busPrefix = null;
                plan.scalar = null;
                plan.scalarAttempted = false;
                plan.nativeWarm = false;
                plan.scalarBus = false;
                plan.promotionStart = instructionVisits;
                if (plan.translation != null) plan.untilCompile = 1;
            }
            EntryPoint entry = plan.entry;
            boolean suspended = isSuspended() || P1MEJitMachine.this.suspended;
            if (entry == null && modifier == null && !suspended &&
                    plan.untilCompile > 0 && --plan.untilCompile == 0) {
                entry = prepareEntry(plan);
            }
            if (suspended || (entry != null && plan.busOpIndex >= 0 && !accessBreakpoints.isEmpty())) {
                entry = null;
            }
            if (entry == null) {
                if (modifier == null && !plan.scalarAttempted && plan.nativeWarm) {
                    plan.scalar = bindScalar(plan);
                    plan.scalarAttempted = true;
                }
                if (plan.scalar != null && (!plan.scalarBus || accessBreakpoints.isEmpty())) {
                    runScalar(plan, plan.scalar);
                }
                else {
                    frame = beginPlan(plan);
                    finishPlan(plan);
                    plan.nativeWarm = true;
                }
            }
            else if (plan.busOpIndex >= 0) {
                runBusTail(plan, entry);
            }
            else {
                entry.run();
                if (!plan.program.getCode().isEmpty()) stepped();
                compiledInstructions++;
                instruction = null;
            }
            callbacks.afterExecuteInstruction(this, plan.instruction);
        }

    }

    private static JitConfiguration scheduledConfiguration() {
        JitConfiguration cfg = new JitConfiguration().disable(JitConfiguration.Opt.EMIT_COUNTERS);
        // One stride excludes queued branch targets. hasEntry supplies the hard
        // fall-through cutoff within that stride.
        return new JitConfiguration(1, cfg.maxPassageOps(), 1, cfg.foldConstants(),
            cfg.removeUnreachableBlocks(), cfg.removeUnusedOperations(), cfg.emitCounters(),
            cfg.logStackTraces());
    }

    public P1MEJitMachine(Language language, RunP1MEMachine.Callbacks callbacks) {
        super(language, scheduledConfiguration(), JIT_LOOKUP);
        this.callbacks = callbacks;
    }

    @Override
    protected PcodeExecutorState<byte[]> createSharedState() {
        return new MachineState(language, callbacks, null);
    }

    @Override
    protected PcodeExecutorState<byte[]> createLocalState(PcodeThread<byte[]> thread) {
        return new MachineState(language, callbacks, thread);
    }

    @Override
    protected MachineThread createThread(String name) {
        return new MachineThread(name);
    }

    @Override
    protected ghidra.pcode.exec.PcodeUseropLibrary<byte[]> createUseropLibrary() {
        return new RunP1MEMachine.Rh850Userops();
    }
}
