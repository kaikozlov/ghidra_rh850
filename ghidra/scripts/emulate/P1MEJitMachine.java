import ghidra.app.plugin.processors.sleigh.SleighInstructionPrototype;
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
import ghidra.pcode.emu.jit.gen.tgt.JitCompiledPassage;
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

import java.lang.foreign.*;
import static java.lang.foreign.ValueLayout.*;
import java.lang.invoke.MethodHandles;
import java.math.BigInteger;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.BitSet;
import java.util.HashMap;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
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
    private static final int TEMPLATE_HITS = 2;
    private static final int MAX_INSTRUCTION_OPS = 200;

    private enum SyncOp { SYNCM, SYNCP, SYNCI }
    private static final SyncOp[] SYNC_OPS = SyncOp.values();
    private static final long GUARD_TAKEN = 1; // preserveMask on a guarded CBRANCH
    private final RunP1MEMachine.Callbacks callbacks;
    private final MemorySegment machineStop=Arena.ofAuto().allocate(JAVA_INT);
    @Override public void setSuspended(boolean s){
        if(s)JAVA_INT.varHandle().setVolatile(machineStop,0L,1);
        super.setSuspended(s);
        if(!s)JAVA_INT.varHandle().setVolatile(machineStop,0L,0);
    }

    private static final java.lang.invoke.VarHandle WORD = MethodHandles.byteArrayViewVarHandle(
        int[].class, java.nio.ByteOrder.LITTLE_ENDIAN);

    private static final java.lang.invoke.VarHandle HALF = MethodHandles.byteArrayViewVarHandle(
        short[].class, java.nio.ByteOrder.LITTLE_ENDIAN);
    private static final java.lang.invoke.VarHandle DOUBLE_WORD = MethodHandles.byteArrayViewVarHandle(
        long[].class, java.nio.ByteOrder.LITTLE_ENDIAN);

    static void writeNumber(byte[] data, int start, int size, boolean bigEndian, long value) {
        if (size == Integer.BYTES) {
            WORD.set(data, start, bigEndian ? Integer.reverseBytes((int) value) : (int) value);
        }
        else if (size == 1) {
            data[start] = (byte) value;
        }
        else if (size == Short.BYTES) {
            HALF.set(data, start, bigEndian ? Short.reverseBytes((short) value) : (short) value);
        }
        else if (size == Long.BYTES) {
            DOUBLE_WORD.set(data, start, bigEndian ? Long.reverseBytes(value) : value);
        }
        else {
            for (int i = 0; i < size; i++, value >>= 8) {
                data[start + (bigEndian ? size - i - 1 : i)] = (byte) value;
            }
        }
    }

    /** Live Ghidra page with the byte ranges already proven initialized. */
    private static final class BoundPage {
        final long base;
        final byte[] data;
        final int arrayOffset, localSlot;
        final MemorySegment segment;
        BitSet defined;
        int knownStart, knownEnd;

        BoundPage(long base, byte[] data, int arrayOffset, int localSlot, MemorySegment segment) {
            this.base = base;
            this.data = data;
            this.arrayOffset = arrayOffset;
            this.localSlot = localSlot;
            this.segment = segment;
        }

        int index(int offset) {
            return arrayOffset + offset;
        }
        int unsignedByte(int offset) {
            return data[index(offset)] & 0xff;
        }

        void define(int start, int end) {
            if (knownEnd == 0 || (start <= knownEnd && end >= knownStart)) {
                if (knownEnd == 0 || start < knownStart) knownStart = start;
                knownEnd = Math.max(knownEnd, end);
            }
            else {
                if (defined == null) defined = new BitSet();
                defined.set(knownStart, knownEnd);
                knownStart = start;
                knownEnd = end;
            }
        }

        long readNumber(int start, int size, boolean bigEndian) {
            return readNumberAt(data, index(start), size, bigEndian);
        }

        static long readNumberAt(byte[] data, int start, int size, boolean bigEndian) {
            if (size == Integer.BYTES) {
                int word = (int) WORD.get(data, start);
                return Integer.toUnsignedLong(bigEndian ? Integer.reverseBytes(word) : word);
            }
            if (size == 1) return data[start] & 0xff;
            if (size == Short.BYTES) {
                short half = (short) HALF.get(data, start);
                return Short.toUnsignedInt(bigEndian ? Short.reverseBytes(half) : half);
            }
            if (size == Long.BYTES) {
                long value = (long) DOUBLE_WORD.get(data, start);
                return bigEndian ? Long.reverseBytes(value) : value;
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
            P1MEJitMachine.writeNumber(data, index(start), size, bigEndian, value);
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

        private long evaluate(long a, long b) {
            // Concrete receivers let HotSpot inline common ops without duplicating Sleigh semantics.
            int out = output.size, in = left.size;
            return switch (opcode) {
                case PcodeOp.INT_AND -> OpBehavior.INT_AND.evaluateBinary(out, in, a, b);
                case PcodeOp.INT_ZEXT -> OpBehavior.INT_ZEXT.evaluateUnary(out, in, a);
                case PcodeOp.INT_OR -> OpBehavior.INT_OR.evaluateBinary(out, in, a, b);
                case PcodeOp.COPY -> OpBehavior.COPY.evaluateUnary(out, in, a);
                case PcodeOp.INT_LEFT -> OpBehavior.INT_LEFT.evaluateBinary(out, in, a, b);
                case PcodeOp.INT_SLESS -> OpBehavior.INT_SLESS.evaluateBinary(out, in, a, b);
                case PcodeOp.INT_ADD -> OpBehavior.INT_ADD.evaluateBinary(out, in, a, b);
                case PcodeOp.INT_EQUAL -> OpBehavior.INT_EQUAL.evaluateBinary(out, in, a, b);
                case PcodeOp.INT_NOTEQUAL -> OpBehavior.INT_NOTEQUAL.evaluateBinary(out, in, a, b);
                case PcodeOp.INT_SUB -> OpBehavior.INT_SUB.evaluateBinary(out, in, a, b);
                default -> behavior instanceof UnaryOpBehavior unary ? unary.evaluateUnary(out, in, a)
                    : ((BinaryOpBehavior) behavior).evaluateBinary(out, in, a, b);
            };
        }

        void execute(boolean bigEndian) {
            long leftValue = left.read(bigEndian);
            long rightValue = right == null ? 0 : right.read(bigEndian);
            output.page.writeNumber(output.start, output.size, bigEndian,
                evaluate(leftValue, rightValue));
        }
    }

    private record Operand(BoundPage page, int offset, int size, long value) {
        private byte[] backing() {
            return page == null ? null : page.data;
        }

        @Override
        public boolean equals(Object obj) {
            return obj instanceof Operand other && backing() == other.backing() &&
                offset == other.offset && size == other.size && value == other.value;
        }

        @Override
        public int hashCode() {
            int hash = System.identityHashCode(backing());
            hash = 31 * hash + offset;
            hash = 31 * hash + size;
            return 31 * hash + Long.hashCode(value);
        }

        boolean overlaps(Operand other) {
            return other != null && page != null && backing() == other.backing() &&
                offset < other.offset + other.size && other.offset < offset + size;
        }

    }

    private static int laneShift(int width, int offset, int size, boolean bigEndian) {
        return Byte.SIZE * (bigEndian ? width - offset - size : offset);
    }

    private record RegionOp(int opcode, Operand out, Operand left, Operand right, int localTarget,
            long preserveMask) {}

    private record Node(Plan plan, RegionOp[] ops, int bus, Address next, Address taken,
            boolean indirect, boolean relative, boolean guarded, boolean stack) {}

    private static boolean isIndirect(int opcode) {
        return opcode == PcodeOp.BRANCHIND || opcode == PcodeOp.CALLIND || opcode == PcodeOp.RETURN;
    }

    private static boolean isDivision(int opcode) {
        return opcode == PcodeOp.INT_DIV || opcode == PcodeOp.INT_SDIV ||
            opcode == PcodeOp.INT_REM || opcode == PcodeOp.INT_SREM;
    }

    /** Immutable stop PCs for one run, independent of all decoder and memory generations. */
    static final class StopIndex {
        private static final StopIndex EMPTY = new StopIndex(Set.of());

        private final long[] addresses;

        static StopIndex of(Set<Long> pcs) {
            return pcs.isEmpty() ? EMPTY : new StopIndex(pcs);
        }

        private StopIndex(Set<Long> pcs) {
            addresses = new long[pcs.size()];
            int i = 0;
            for (long pc : pcs) addresses[i++] = pc;
            if (addresses.length > 3) Arrays.sort(addresses);
        }

        boolean contains(long pc) {
            return switch (addresses.length) {
                case 0 -> false;
                case 1 -> addresses[0] == pc;
                case 2 -> addresses[0] == pc || addresses[1] == pc;
                case 3 -> addresses[0] == pc || addresses[1] == pc || addresses[2] == pc;
                default -> Arrays.binarySearch(addresses, pc) >= 0;
            };
        }

    }

    private static final class Site {
        final long localGeneration;
        final Plan plan;
        final long pc, predicted;
        final int width;
        final Address nextAddress;
        final Address takenAddress;
        final boolean acceptsFlow;
        final RunP1MEMachine.RegionDef fetchRegion;
        final NativeBinding nativeBinding;
        NativeGroup group;
        int groupOffset;
        long groupEpoch;

        void invalidate() {
            if (group != null && groupEpoch == group.epoch) {
                int loc = group.location(pc);
                if ((group.index[loc] & ~NativeGroup.STOP_BIT) == groupOffset) {
                    group.code[groupOffset] = 0;
                    group.index[loc] &= NativeGroup.STOP_BIT;
                }
            }
            group = null;
            plan.site = null;
        }

        Site(MachineStatePiece local, Node node, NativeBinding nativeBinding,
                RunP1MEMachine.RegionDef fetchRegion, boolean acceptsFlow) {
            this.fetchRegion = fetchRegion;
            this.acceptsFlow = acceptsFlow;
            this.nativeBinding = nativeBinding;
            localGeneration = local.generation;
            plan = node.plan;
            pc = plan.address.getOffset();
            width = plan.encoding.length;
            nextAddress = node.next;
            takenAddress = node.taken == null ? nextAddress : node.taken;
            predicted = nextAddress.getOffset();
        }

        static Site bind(MachineStatePiece local, Node node, boolean bigEndian,
                RunP1MEMachine.RegionDef fetchRegion, boolean acceptsFlow) {
            if (bigEndian || java.nio.ByteOrder.nativeOrder() != java.nio.ByteOrder.LITTLE_ENDIAN) return null;
            List<Operand> operands = new ArrayList<>();
            List<Slot> slots = new ArrayList<>();
            List<TemplateOp> ops = new ArrayList<>(node.ops.length);
            for (int i = 0; i < node.ops.length; i++) {
                RegionOp op = node.ops[i];
                Read left = bindRead(operands, slots, node, bigEndian, i, op.left);
                Read right = bindRead(operands, slots, node, bigEndian, i, op.right);
                int out = slot(operands, slots, op.out);
                ops.add(new TemplateOp(op.opcode, out, left, right, op.localTarget, op.preserveMask));
            }
            Template shape = new Template(bigEndian, node.bus, node.indirect, node.relative,
                node.guarded, node.plan.templateControl, node.plan.irqOnly, node.plan.templateSync, node.stack,
                slots, ops);
            var body = NativeSite.resolve(shape);
            if (body == null) return null;
            return new Site(local, node, new NativeBinding(body, NativeSite.pack(shape, operands)), fetchRegion, acceptsFlow);
        }


        private static int slot(List<Operand> operands,
                List<Slot> slots, Operand op) {
            if (op == null) return -1;
            int index = operands.indexOf(op);
            if (index >= 0) return index;
            int next = slots.size();
            // Share one instruction body across displacements, scratch offsets and register numbers.
            SlotKind kind = op.page != null ? SlotKind.PAGE
                : ((op.value >= 0 && op.value <= 8) || op.value == 15 || op.value == 16 ||
                   op.value == 31 || op.value == 32 || op.value == 63 || op.value == 64 ||
                   op.value == 255 || op.value == 65535 || op.value == 0xffff_ffffL || op.value == -1L)
                    ? SlotKind.LITERAL : SlotKind.ARG;
            operands.add(op);
            // Unique temporaries and subword register lanes have fixed offsets in each layout.
            // Retain register-number parameters for interchangeable general registers.
            long layoutOffset = kind == SlotKind.PAGE && op.page.localSlot >= 0 &&
                (op.page.localSlot == 1 || op.size < Integer.BYTES) ? 1L + op.offset : 0;
            slots.add(new Slot(kind, op.size, kind == SlotKind.LITERAL ? op.value : layoutOffset,
                op.page == null ? -1 : op.page.localSlot));
            return next;
        }

        private static int forwarded(RegionOp[] ops, int before, Operand read) {
            if (read == null) return -1;
            for (int i = before - 1; i >= 0; i--) {
                Operand written = ops[i].out;
                if (read.overlaps(written)) return read.equals(written) ? i : -1;
            }
            return -1;
        }

        private static Read bindRead(List<Operand> operands,
                List<Slot> slots, Node node, boolean bigEndian, int before, Operand operand) {
            if (operand == null) return null;
            int index = slot(operands, slots, operand);
            int write = node.relative ? -1 : forwarded(node.ops, before, operand);
            boolean deferred = node.guarded || node.indirect || node.stack || before <= node.bus;
            if (!deferred || write >= 0 || operand.page == null)
                return new Read(index, write, 0, List.of());

            // Deferred writes may alias at different widths. For each byte, read the
            // last speculative writer or, if none, the untouched backing page.
            int[] writers = null;
            for (int i = before - 1; i >= 0; i--) {
                Operand out = node.ops[i].out;
                if (!operand.overlaps(out)) continue;
                if (writers == null) {
                    writers = new int[operand.size];
                    Arrays.fill(writers, -1);
                }
                int start = Math.max(0, out.offset - operand.offset);
                int end = Math.min(operand.size, out.offset + out.size - operand.offset);
                for (int j = start; j < end; j++) {
                    if (writers[j] < 0) writers[j] = i;
                }
            }
            if (writers == null) return new Read(index, -1, 0, List.of());

            long liveMask = 0;
            List<ReadPatch> patches = new ArrayList<>();
            for (int start = 0; start < writers.length;) {
                int writer = writers[start], end = start + 1;
                while (end < writers.length && writers[end] == writer) end++;
                int size = end - start;
                int destShift = laneShift(operand.size, start, size, bigEndian);
                long mask = Utils.calc_mask(size);
                if (writer < 0) liveMask |= mask << destShift;
                else {
                    Operand out = node.ops[writer].out;
                    int sourceShift = laneShift(out.size, operand.offset + start - out.offset, size,
                        bigEndian);
                    patches.add(new ReadPatch(writer, sourceShift, destShift, mask));
                }
                start = end;
            }
            return new Read(index, -1, liveMask, List.copyOf(patches));
        }
    }

    private enum SlotKind { LITERAL, ARG, PAGE }

    private record Slot(SlotKind kind, int size, long immediate, int localSlot) {}

    private record ReadPatch(int write, int sourceShift, int destShift, long mask) {}

    private record Read(int slot, int write, long liveMask, List<ReadPatch> patches) {}

    private record TemplateOp(int opcode, int out, Read left, Read right, int localTarget,
            long preserveMask) {}

    private record Template(boolean bigEndian, int bus, boolean indirect, boolean relative,
            boolean guarded, boolean control, boolean irqOnly, SyncOp sync, boolean stack,
            List<Slot> slots, List<TemplateOp> ops) {}

    // No page, PC, Plan, or machine reference may escape through the shape cache.
    private record NativeBinding(P1MENativeBodyCache.Body body, long[] args) {}
    private static final class NativeSite {
        private static String libraryStatus = "disabled";
        private record Runner(P1MENativeBodyCache cache, SymbolLookup library, java.lang.invoke.MethodHandle run) {}

        private static final Runner RUNNER = openRunner();
        static final P1MENativeBodyCache CACHE = RUNNER == null ? null : RUNNER.cache;
        private static final Map<Template, P1MENativeBodyCache.Body> shapes = new HashMap<>();
        private static boolean shapeLimitReported;

        private static Runner openRunner() {
            try {
                String sources = System.getenv("P1ME_WINDOWGRAPH_SOURCE");
                String directory = System.getenv("P1ME_WINDOWGRAPH_CACHE");
                if (Boolean.getBoolean("p1me.windowGraph.disableNative") || sources == null) return null;
                if (directory == null) throw new IllegalArgumentException("set P1ME_WINDOWGRAPH_CACHE");
                String compiler = System.getenv("P1ME_WINDOWGRAPH_CC");
                var cache = new P1MENativeBodyCache(java.nio.file.Path.of(sources),
                    java.nio.file.Path.of(directory), compiler == null || compiler.isBlank() ? "cc" : compiler);
                String installed = System.getenv("P1ME_WINDOWGRAPH_RUNNER_CACHE");
                SymbolLookup library = installed == null ? cache.openRunner()
                    : cache.openRunner(java.nio.file.Path.of(installed));
                Runner runner = new Runner(cache, library, groupRunner(library));
                cache.installShutdownHook();
                libraryStatus = "ready";
                return runner;
            }
            catch (java.io.IOException | RuntimeException | LinkageError e) {
                libraryStatus = P1MENativeBodyCache.bounded(e.toString());
                return null;
            }
        }

        private static java.lang.invoke.MethodHandle groupRunner(SymbolLookup library) {
            MemoryLayout[] params = new MemoryLayout[12];
            Arrays.fill(params, ADDRESS);
            params[0] = params[1] = params[2] = JAVA_INT;
            String name = "window_run";
            return Linker.nativeLinker().downcallHandle(library.find(name)
                .orElseThrow(() -> new IllegalArgumentException("runner does not export " + name)),
                FunctionDescriptor.of(JAVA_INT, params), Linker.Option.critical(true));
        }
        static synchronized P1MENativeBodyCache.Body resolve(Template shape) {
            var known = shapes.get(shape);
            if (known != null || shapes.containsKey(shape)) return known;
            if (shapes.size() >= P1MENativeBodyCache.MAX_SHAPES) {
                if (!shapeLimitReported) CACHE.failure("lowering", "process template limit reached");
                shapeLimitReported = true;
                return null;
            }
            P1MENativeBodyCache.Body body = null;
            try {
                String source = lower(shape);
                if (source != null) body = CACHE.request(source);
            }
            catch (RuntimeException | LinkageError e) {
                CACHE.failure("lowering", e.toString());
            }
            shapes.put(shape, body);
            return body;
        }

        static String diagnostic() {
            return "library=" + (RUNNER != null) + ", native-cache=" + libraryStatus +
                (CACHE == null ? "" : ", " + CACHE.diagnostic());
        }

        private static boolean fixedWidth(int size) {
            return (size & (size - 1)) == 0;
        }

        private static String mask(long bits) {
            return "0x" + Long.toHexString(bits) + "ULL";
        }

        private static String signed(String value, int size) {
            int bits = size * Byte.SIZE;
            if (fixedWidth(size)) return "((int" + bits + "_t)" + value + ")";
            String sign = mask(1L << (bits - 1));
            return "((int64_t)((" + value + "^" + sign + ")-" + sign + "))";
        }

        private static String narrow(String value, int size) {
            return fixedWidth(size) ? "(uint" + size * Byte.SIZE + "_t)(" + value + ")"
                : "((" + value + ")&" + mask(Utils.calc_mask(size)) + ")";
        }

        private static long[] pack(Template shape, List<Operand> operands) {
            int constants = 0, pages = 0;
            for (Slot slot : shape.slots) {
                if (slot.kind == SlotKind.ARG) constants++;
                else if (slot.kind == SlotKind.PAGE && slot.immediate == 0) pages++;
            }
            long[] words = new long[constants + ((pages + 1) >>> 1)];
            int arg = 0, page = 0;
            for (int i = 0; i < operands.size(); i++) {
                switch (shape.slots.get(i).kind) {
                    case ARG -> words[arg++] = operands.get(i).value;
                    case PAGE -> {
                        if (shape.slots.get(i).immediate == 0) {
                            words[constants + (page >>> 1)] |= Integer.toUnsignedLong(operands.get(i).offset) << ((page & 1) * 32);
                            page++;
                        }
                    }
                    case LITERAL -> {}
                }
            }
            return words;
        }

        private static String packedSource(Template shape, String code) {
            int constants=0;
            for (Slot slot : shape.slots) if (slot.kind==SlotKind.ARG) constants++;
            int arg=0, page=0;
            String[] expressions = new String[shape.slots.size()];
            for (int i=0;i<expressions.length;i++) {
                switch (shape.slots.get(i).kind) {
                    case ARG -> expressions[i]="a["+(arg++)+"]";
                    case PAGE -> {
                        long fixed = shape.slots.get(i).immediate;
                        expressions[i] = fixed == 0 ? "rd4((uint8_t*)a+" + (8*constants+4*page++) + ")" : Long.toString(fixed-1);
                    }
                    case LITERAL -> {}
                }
            }
            StringBuilder result = new StringBuilder(code.length());
            for(int i=0;;) {
                int start=code.indexOf("a[",i);
                if(start<0) return result.append(code,i,code.length()).toString();
                int end=code.indexOf(']',start+2);
                String expression=expressions[Integer.parseInt(code,start+2,end,10)];
                if(expression==null) throw new AssertionError("literal used as native operand");
                result.append(code,i,start).append(expression);
                i=end+1;
            }
        }

        private static String live(Slot slot, int index) {
            return "rd" + slot.size + "(p" + slot.localSlot + "+a[" + index + "])";
        }
        static String input(Template s,Read r){
            if(r==null)return null;
            if(r.write>=0)return "v"+r.write;
            Slot b=s.slots.get(r.slot);
            return switch (b.kind) {
                case LITERAL -> b.immediate + "ULL";
                case ARG -> "a[" + r.slot + "]";
                case PAGE -> {
                    String value = live(b, r.slot);
                    if (r.patches.isEmpty()) yield value;
                    StringBuilder expression = new StringBuilder("(");
                    if (r.liveMask != 0) expression.append('(').append(value).append('&')
                        .append(mask(r.liveMask)).append(")|");
                    for (ReadPatch patch : r.patches) {
                        expression.append("(((v").append(patch.write).append(">>").append(patch.sourceShift)
                            .append(")&").append(mask(patch.mask)).append(")<<")
                            .append(patch.destShift).append(")|");
                    }
                    expression.setCharAt(expression.length() - 1, ')');
                    yield expression.toString();
                }
            };
        }
        private static void stackCheck(StringBuilder code, int op) {
            code.append("if(stack_suspend(ctx,").append(op + 1).append("))return -2;\n");
        }

        private static String lower(Template s) {
            StringBuilder code=new StringBuilder();
            StringBuilder pending=new StringBuilder();
            // Stack bodies first evaluate SSA values and prove every RAM word and branch.
            // Only pending contains architectural writes; each gets its original stop point.
            if (s.stack) code.append("if(!stack_mode_ready(ctx))return -1;\n");
            String edge = "0";
            for (Slot slot : s.slots) {
                if ((slot.kind == SlotKind.PAGE && slot.localSlot < 0)
                        || slot.size < 1 || slot.size > Long.BYTES)
                    return null;
            }
            if (s.control) code.append("int changed=0;\n");
            for(int i=0;i<s.ops.size();i++){
                var o=s.ops.get(i);String x=input(s,o.left),y=input(s,o.right);
                if(s.relative)code.append("label").append(i).append(":;\n");
                if(o.localTarget>=0){if(o.opcode!=PcodeOp.BRANCH)code.append("if(").append(x).append(")");
                    code.append("goto label").append(o.localTarget).append(";\n");continue;}
                if (s.stack) stackCheck(pending, i);
                if (s.indirect && i == s.ops.size() - 1) {
                    code.append("int return_edge=indirect_edge(ctx,a,").append(x).append(");")
                        .append("if(return_edge<0)return -1;\n");
                    edge = "return_edge";
                    if (!s.stack) code.append(pending);
                    break;
                }
                if(o.opcode==PcodeOp.BRANCH||o.opcode==PcodeOp.CALL)break;
                if (s.guarded && o.opcode == PcodeOp.CBRANCH) {
                    if (o.preserveMask == GUARD_TAKEN) code.append("if(!(").append(x).append("))return -1;\n");
                    else code.append("if(").append(x).append(")return -1;\n");
                    continue;
                }
                if (o.opcode == PcodeOp.CBRANCH) {
                    edge = "!!(" + x + ")";
                    break;
                }
                if (s.stack && (o.opcode == PcodeOp.LOAD || o.opcode == PcodeOp.STORE)) {
                    boolean store = o.opcode == PcodeOp.STORE;
                    String word = "word" + i;
                    code.append("struct stack_word ").append(word).append(";if(!stack_fit(ctx,")
                        .append(x).append(',').append(store ? 1 : 0).append(",&").append(word)
                        .append("))return GUEST_BUS_MISS;\n");
                    if (store) {
                        String value = "value" + i;
                        pending.append("uint64_t ").append(value).append('=').append(y).append(";\n")
                            .append("wr4(").append(word).append(".primary,").append(value).append(");")
                            .append("if(").append(word).append(".mirror)wr4(").append(word)
                            .append(".mirror,").append(value).append(");\n");
                    }
                    else {
                        Slot out = s.slots.get(o.out);
                        code.append("uint64_t v").append(i).append("=rd4(").append(word).append(".primary);\n");
                        pending.append("wr4(p").append(out.localSlot).append("+a[").append(o.out)
                            .append("],v").append(i).append(");\n");
                    }
                    if (store) pending.append("retire_store(ctx,").append(word).append(".address,4,")
                        .append(word).append(".mirror!=NULL);\n");
                    continue;
                }
                if(i==s.bus){
                    boolean st=o.opcode==PcodeOp.STORE;
                    int bytes=s.slots.get(st?o.right.slot:o.out).size;
                    code.append("uint64_t addr=").append(x).append(";if(!fits(ctx,addr,")
                        .append(bytes).append(",").append(st?1:0).append("))");
                    code.append("return GUEST_BUS_MISS;\n");
                    code.append(pending);
                    if(st){code.append("wr").append(bytes).append("(ctx->w+(addr-ctx->cache_low[1]),").append(y).append(");")
                        .append("if(ctx->m)wr").append(bytes).append("(ctx->m+(addr-ctx->cache_low[1]),").append(y).append(");\n");continue;}
                    Slot out=s.slots.get(o.out);
                    code.append("uint64_t v").append(i).append("=rd").append(bytes).append("(ctx->r+(addr-ctx->cache_low[0]));")
                        .append("wr").append(out.size).append("(p").append(out.localSlot).append("+a[").append(o.out).append("],v").append(i).append(");\n");
                    continue;
                }
                if(o.out<0 || o.left==null)return null;
                Slot out=s.slots.get(o.out);
                int inputSize = s.slots.get(o.left.slot).size;
                int width = inputSize * Byte.SIZE;
                String X = signed(x, inputSize), Y = signed(y, inputSize);
                if (isDivision(o.opcode)) {
                    if (!s.guarded) return null;
                    code.append("if(!(").append(y).append("))return -1;\n");
                }
                String expr=switch(o.opcode){
                    case PcodeOp.COPY,PcodeOp.INT_ZEXT->x;case PcodeOp.INT_SEXT->"(uint64_t)(int64_t)"+X;
                    case PcodeOp.INT_AND->x+"&"+y;case PcodeOp.INT_OR->x+"|"+y;
                    case PcodeOp.INT_XOR->x+"^"+y;case PcodeOp.INT_NEGATE->"~"+x;
                    case PcodeOp.INT_2COMP->"0ULL-"+x;
                    case PcodeOp.INT_ADD->x+"+"+y;case PcodeOp.INT_SUB->x+"-"+y;case PcodeOp.INT_MULT->x+"*"+y;
                    case PcodeOp.INT_EQUAL->x+"=="+y;case PcodeOp.INT_NOTEQUAL->x+"!="+y;
                    case PcodeOp.INT_LESS->x+"<"+y;case PcodeOp.INT_LESSEQUAL->x+"<="+y;
                    case PcodeOp.INT_SLESS->X+"<"+Y;case PcodeOp.INT_SLESSEQUAL->X+"<="+Y;
                    case PcodeOp.BOOL_NEGATE->"!"+x;case PcodeOp.BOOL_AND->x+"&&"+y;
                    case PcodeOp.BOOL_OR->x+"||"+y;case PcodeOp.BOOL_XOR->"(!!"+x+")^(!!"+y+")";
                    case PcodeOp.INT_LEFT->"("+y+"<64?"+x+"<<"+y+":0)";
                    case PcodeOp.INT_RIGHT->"("+y+"<64?"+x+">>"+y+":0)";
                    case PcodeOp.INT_SRIGHT->"("+y+"<64?(uint64_t)((int64_t)"+X+">>"+y+"):(uint64_t)((int64_t)"+X+">>63))";
                    case PcodeOp.SUBPIECE->"("+y+"<8?"+x+">>(8*"+y+"):0)";
                    case PcodeOp.INT_CARRY->narrow(x+"+"+y,inputSize)+"<"+x;
                    case PcodeOp.INT_SCARRY->"(("+x+"^~"+y+")&("+x+"^("+x+"+"+y+"))& (1ULL<<"+(width-1)+"))!=0";
                    case PcodeOp.INT_SBORROW->"(("+x+"^"+y+")&("+x+"^("+x+"-"+y+"))& (1ULL<<"+(width-1)+"))!=0";
                    case PcodeOp.PIECE->s.slots.get(o.right.slot).size>=8?null:"("+x+"<<"+(s.slots.get(o.right.slot).size*8)+")|"+y;
                    case PcodeOp.INT_DIV -> x + "/" + y;
                    case PcodeOp.INT_REM -> x + "%" + y;
                    // Widen sub-64-bit signed operations before dividing. For 64
                    // bits the p-code result wraps where C would overflow.
                    case PcodeOp.INT_SDIV -> "(uint64_t)(" + (width == 64
                        ? "(" + X + "==INT64_MIN&&" + Y + "==-1)?INT64_MIN:" : "") +
                        "(int64_t)" + X + "/(int64_t)" + Y + ")";
                    case PcodeOp.INT_SREM -> "(uint64_t)(" + (width == 64
                        ? "(" + X + "==INT64_MIN&&" + Y + "==-1)?0:" : "") +
                        "(int64_t)" + X + "%(int64_t)" + Y + ")";
                    default->null;
                };
                if(expr==null)return null;
                code.append("uint64_t v").append(i).append('=').append(narrow(expr, out.size)).append(";\n");
                if (o.preserveMask != 0) {
                    code.append("if((v").append(i).append('^').append(live(out, o.out)).append(")&")
                        .append(mask(o.preserveMask)).append(")return -1;\n");
                }
                if (s.control && out.localSlot == 0) {
                    // Control writes compare with live state before any write commits.
                    code.append("changed|=v").append(i).append("!=").append(live(out, o.out)).append(";\n");
                }
                (s.stack||s.guarded||s.indirect||i<s.bus?pending:code).append("wr").append(out.size).append("(p").append(out.localSlot).append("+a[").append(o.out)
                    .append("],v").append(i).append(");\n");
            }
            if(s.relative)code.append("label").append(s.ops.size()).append(":;\n");
            if (s.guarded || s.stack) code.append(pending);
            if (!s.stack && s.bus >= 0 && s.ops.get(s.bus).opcode == PcodeOp.STORE) {
                int width = s.slots.get(s.ops.get(s.bus).right.slot).size;
                code.append("retire_store(ctx,addr,").append(width).append(",ctx->m!=NULL);\n");
            }
            if (s.sync != null) code.append("if(ctx->retire_flags&COUNT_SYNC)++ctx->words[CTL_SYNC+")
                .append(s.sync.ordinal()).append("];\n");
            if (s.control) code.append(s.irqOnly ?
                "return changed && !(ctx->words[CTL_MODE]&256) ? GUEST_CONTROL : 0;\n" :
                "return changed?GUEST_CONTROL:0;\n");
            else code.append("return ").append(edge).append(";\n");
            return packedSource(s, code.toString());
        }
    }
    private static final class NativeGroup {
        private static final int HEADER = 4, STOP_BIT = Integer.MIN_VALUE;
        private static final long MAX_FETCH_BANK = 4L * 1024 * 1024;
        final long base;
        final int fetchLocations;
        final int[] index;
        final MemorySegment indices;
        long[] code = new long[4096];
        MemorySegment words = MemorySegment.ofArray(code);
        Site[] members = new Site[512];
        int top = 1, count;
        RegisterValue context;
        long generation, local, codeVersion, epoch, contextBits;
        RunP1MEMachine.Trace.ExecutedPcs coverage;
        StopIndex stops = StopIndex.EMPTY;

        NativeGroup(RunP1MEMachine.RegionDef region) {
            base = region.start;
            fetchLocations = (int) ((region.end_exclusive - base + 1) / 2);
            index = new int[fetchLocations];
            indices = MemorySegment.ofArray(index);
        }

        int location(long pc) {
            long off = pc - base;
            return off >= 0 && (off & 1) == 0 && off / 2 < fetchLocations ? (int) (off / 2) : -1;
        }

        void refresh(MachineStatePiece memory, long localGeneration, RegisterValue ctx,
                RunP1MEMachine.Trace.ExecutedPcs recorded) {
            if (epoch != 0 && local == localGeneration && generation == memory.generation &&
                    codeVersion == memory.codeGeneration && Objects.equals(context, ctx) && coverage == recorded) return;
            coverage = recorded;
            local = localGeneration;
            generation = memory.generation;
            codeVersion = memory.codeGeneration;
            context = ctx;
            contextBits = ctx == null ? 0 : ctx.getUnsignedValueIgnoreMask().longValue();
            epoch++;
            top = 1;
            Arrays.fill(members, 0, count, null);
            count = 0;
            Arrays.fill(index, 0, fetchLocations, 0);
            stops = StopIndex.EMPTY;
        }

        void stops(StopIndex current) {
            if (stops == current) return;
            for (long pc : stops.addresses) {
                int loc = location(pc);
                if (loc >= 0) {
                    int pos = index[loc] & ~STOP_BIT;
                    index[loc] = pos;
                    if (pos != 0) code[pos+2] &= Long.MAX_VALUE;
                }
            }
            for (long pc : current.addresses) {
                int loc = location(pc);
                if (loc >= 0) {
                    int pos = index[loc] & ~STOP_BIT;
                    index[loc] = pos | STOP_BIT;
                    if (pos != 0) code[pos+2] |= Long.MIN_VALUE;
                }
            }
            stops = current;
        }

        int entry(Site site) {
            int loc = location(site.pc);
            if (loc < 0 || index[loc] < 0) return -1;
            if (site.group == this && site.groupEpoch == epoch && index[loc] == site.groupOffset) return loc;
            // First retirement goes through the recording path, including after a restore.
            if (coverage != null && !coverage.contains(site.pc)) return -1;
            NativeBinding e = site.nativeBinding;
            MemorySegment fn = e.body.function;
            if (fn == null || (site.predicted >>> 32) != 0 || fn.address() == 0 ||
                    site.width <= 0 || site.width > 255 || site.width > 2L * (fetchLocations - loc)) return -1;
            int end = Math.addExact(top, HEADER + e.args.length);
            if (end > code.length) {
                code = Arrays.copyOf(code, Math.max(code.length * 2, end));
                words = MemorySegment.ofArray(code);
            }
            if (count == members.length) members = Arrays.copyOf(members, count * 2);
            int k = top;
            top = end;
            site.group = this;
            site.groupOffset = k;
            site.groupEpoch = epoch;
            int ordinal = count;
            members[count++] = site;
            code[k] = fn.address();
            code[k + 1] = Integer.toUnsignedLong(location(site.nextAddress.getOffset())) |
                ((long)location(site.takenAddress.getOffset()) << 32);
            int previous = index[loc];
            if ((previous & ~STOP_BIT) != 0) code[previous & ~STOP_BIT] = 0;
            code[k + 2] = ordinal | ((long)site.width << 32) | ((long)loc << 40) |
                (site.acceptsFlow ? 1L << 62 : 0) | (previous < 0 ? Long.MIN_VALUE : 0);
            code[k + 3] = site.predicted;
            System.arraycopy(e.args, 0, code, k + HEADER, e.args.length);
            index[loc] = (index[loc] & STOP_BIT) | k;
            return loc;
        }
    }
    /**
     * One bounded set of physical words with up to 64 independently invalidated
     * groups. The device owns the projection; storage only tracks byte overlap.
     */
    static final class DeviceWordIndex {
        private final long first, end, addressLimit;
        private final long[] groupsByWord;
        private final long allGroups;
        private long dirty;

        private DeviceWordIndex(long first, long end, long addressLimit,
                RunP1MEMachine.RegisterDef[][] groups) {
            this.first = first;
            this.end = end;
            this.addressLimit = addressLimit;
            groupsByWord = new long[(int) (end - first) / Integer.BYTES];
            long all = 0;
            for (int group = 0; group < groups.length; group++) {
                for (var word : groups[group]) {
                    long bit = 1L << group;
                    groupsByWord[(int) (word.address - first) / Integer.BYTES] |= bit;
                    all |= bit;
                }
            }
            allGroups = dirty = all;
        }

        long takeDirty(long interests) {
            long changed = dirty & interests;
            dirty ^= changed;
            return changed;
        }

        void invalidateAll() {
            dirty = allGroups;
        }

        void invalidate(long offset, int size) {
            dirty |= overlapMask(offset, size);
        }

        private long overlapMask(long offset, int size) {
            if (size <= 0) return 0;
            long limit = offset + size;
            if (offset < 0 || limit > addressLimit || limit < offset) return allGroups;
            if (offset >= end || limit <= first) return 0;
            if (offset >= first && ((offset ^ (limit - 1)) & -4L) == 0)
                return groupsByWord[(int) (offset - first) / Integer.BYTES];
            int low = (int) (Math.max(offset, first) - first) / Integer.BYTES;
            int high = (int) (Math.min(limit, end) - 1 - first) / Integer.BYTES;
            long mask = 0;
            for (int word = low; word <= high; word++) mask |= groupsByWord[word];
            return mask;
        }
    }

    // Owns no guest values. The array is the live Ghidra page, not a device copy.
    private record DeviceLeaf(byte[] data, int offset, int width, int codePage, long watchedWords) {
        long read(boolean bigEndian) {
            return BoundPage.readNumberAt(data, offset, width, bigEndian);
        }
    }

    private static final class MachineStatePiece extends JitBytesPcodeExecutorStatePiece {
        private final RunP1MEMachine.Callbacks bus;
        private final AddressSpace registerAddressSpace;
        private final AddressSpace memoryAddressSpace;
        private MachineStateSpace registers;
        private MachineStateSpace uniques;
        private MachineStateSpace memory;
        // A page becomes executable only after its first byte-proven decode.
        // Writes elsewhere cannot invalidate its plans.
        private final BitSet codePages = new BitSet();
        private long generation;
        private long codeGeneration, codeCoverage;
        private DeviceWordIndex deviceWordIndex;
        private final DeviceLeaf[] deviceLeaves;

        MachineStatePiece(Language language, RunP1MEMachine.Callbacks callbacks,
                PcodeThread<byte[]> thread) {
            super(language, callbacks.wrapFor(thread));
            bus = thread == null ? callbacks : null;
            registerAddressSpace = language.getProgramCounter().getAddressSpace();
            memoryAddressSpace = language.getDefaultSpace();
            deviceLeaves = bus == null ? null : new DeviceLeaf[bus.model.registers.size()];
        }

        boolean usesBus(AddressSpace space) {
            return bus != null && space.equals(bus.model.memorySpace);
        }

        private static boolean slabRegion(RunP1MEMachine.RegionDef region) {
            long size=region.end_exclusive-region.start;
            return (region.templateReads || region.templateWrites) && size>0 && size<=4L*1024*1024 &&
                ((region.start|region.end_exclusive)&PAGE_MASK)==0;
        }
        private byte[] localSlab(AddressSpace space) {
            if (space==memoryAddressSpace && bus!=null) {
                long size=0;
                for(var r:bus.model.regions) if(slabRegion(r))size+=r.end_exclusive-r.start;
                return size==0 || size>8L*1024*1024 ? null : new byte[(int)size];
            }
            // These are host storage budgets, not guest-address windows.
            int pages = space.isRegisterSpace() ? 16 : space.isUniqueSpace() ? 256 : 0;
            return pages == 0 ? null : new byte[pages * PAGE_SIZE];
        }

        private final class MachineStateSpace extends JitBytesPcodeExecutorStateSpace
                implements RunP1MEMachine.InitializedBytes {
            private final long maxOffset;
            private final BoundPage[] pageCache;
            private final byte[] slab;
            private final MemorySegment slabSegment;
            private BoundPage[][] groups;

            MachineStateSpace(AddressSpace space) {
                this(space, localSlab(space));
            }

            private MachineStateSpace(AddressSpace space, byte[] slab) {
                super(MachineStatePiece.this.language, space, MachineStatePiece.this,
                    new SemisparseByteArray(slab));
                this.slab = slab;
                slabSegment = slab == null ? null : MemorySegment.ofArray(slab);
                if (slab!=null && space==memoryAddressSpace) {
                    for(var r:bus.model.regions) if(slabRegion(r)) {
                        int start=-1;
                        for(long a=r.start;a<r.end_exclusive;a+=PAGE_SIZE){
                            var p=bytes.getDirectPage(a);
                            if(start<0)start=p.offset();
                            if(p.array()!=slab || p.offset()!=start+(a-r.start))throw new AssertionError("shared slab mapping");
                        }
                    }
                }
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
                BoundPage[] group = null;
                if ((page == null || page.base != base) && (base >>> 32) == 0 && groups != null) {
                    group = groups[(int) (pageNumber >>> 8)];
                    if (group != null && (page = group[(int) pageNumber & 255]) != null)
                        pageCache[slot] = page;
                }
                if (page != null && page.base == base && ((start >= page.knownStart &&
                        start + size <= page.knownEnd) || (page.defined != null &&
                        page.defined.nextClearBit(start) >= start + size))) {
                    return page;
                }
                int available = bytes.contiguousAvailableAfter(offset);
                if (available < size) return null;
                if (page == null || page.base != base) {
                    if (slab == null) {
                        byte[] data = getDirect(base);
                        page = new BoundPage(base, data, 0, -1, MemorySegment.ofArray(data));
                    }
                    else {
                        var direct = bytes.getDirectPage(base);
                        boolean resident = direct.array() == slab;
                        int localSlot = !resident ? -1 : space.isRegisterSpace() ? 0 : space.isUniqueSpace() ? 1 : -1;
                        page = new BoundPage(base, direct.array(), direct.offset(), localSlot,
                            resident ? slabSegment : MemorySegment.ofArray(direct.array()));
                    }
                    pageCache[slot] = page;
                    if ((base >>> 32) == 0) {
                        if (groups == null) {
                            long last = Long.compareUnsigned(maxOffset, 0xffff_ffffL) <= 0
                                ? maxOffset : 0xffff_ffffL;
                            groups = new BoundPage[(int) (last >>> (PAGE_SHIFT + 8)) + 1][];
                        }
                        int index = (int) (pageNumber >>> 8);
                        if (group == null) groups[index] = group = new BoundPage[256];
                        group[(int) pageNumber & 255] = page;
                    }
                }
                page.define(start, start + Math.min(available, PAGE_SIZE - start));
                return page;
            }

            void invalidatePages() {
                if (pageCache != null) Arrays.fill(pageCache, null);
                groups = null;
            }

            @Override
            public void clear() {
                invalidatePages();
                if (space == memoryAddressSpace) {
                    if (deviceWordIndex != null) deviceWordIndex.invalidateAll();
                    if (deviceLeaves != null) Arrays.fill(deviceLeaves, null);
                }
                if (space == memoryAddressSpace || space == registerAddressSpace || space == uniqueSpace)
                    generation++;
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
                    markCodeWrite(space, offset, length);
                    super.write(offset, value, start, length);
                }
            }

            @Override
            public byte[] read(long offset, int size, Reason reason, PcodeStateCallbacks cb) {
                if (space == memoryAddressSpace && fitsPage(offset, size)) {
                    BoundPage page = initializedLocalPage(offset, size);
                    if (page != null) {
                        int start = page.index((int) offset & PAGE_MASK);
                        return Arrays.copyOfRange(page.data, start, start + size);
                    }
                }
                if (isInitialized(offset, size)) return readBytes(offset, size, reason);
                return super.read(offset, size, reason, cb);
            }

            @Override
            public void write(long offset, byte[] value, int start, int length, PcodeStateCallbacks cb) {
                markCodeWrite(space, offset, length);
                if (space == memoryAddressSpace && fitsPage(offset, length)) {
                    BoundPage page = initializedLocalPage(offset, length);
                    if (page != null) {
                        System.arraycopy(value, start, page.data, page.index((int) offset & PAGE_MASK), length);
                        cb.dataWritten(MachineStatePiece.this, space.getAddress(offset), length, value);
                        return;
                    }
                }
                super.write(offset, value, start, length, cb);
            }

            boolean verifyCode(long offset, byte[] encoding) {
                int size = encoding.length;
                if (size == 0 || size > PAGE_SIZE || !isInitialized(offset, size)) return false;
                int start = (int) offset & PAGE_MASK;
                long base = offset - start;
                int split = Math.min(size, PAGE_SIZE - start);
                var first = bytes.getDirectPage(base);
                start += first.offset();
                if (!Arrays.equals(first.array(), start, start + split, encoding, 0, split)) return false;
                if (split < size) {
                    var tail = bytes.getDirectPage(base + PAGE_SIZE);
                    if (!Arrays.equals(tail.array(), tail.offset(), tail.offset() + size - split,
                            encoding, split, size)) return false;
                }
                int low = (int) (offset >>> PAGE_SHIFT);
                int high = (int) ((offset + size - 1L) >>> PAGE_SHIFT);
                if (!codePages.get(low) || !codePages.get(high)) {
                    codeCoverage++;
                    codePages.set(low, high + 1);
                }
                return true;
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

        @Override
        public MemBuffer getConcreteBuffer(Address address, Purpose purpose) {
            if (purpose == Purpose.DECODE && address.getAddressSpace() == memoryAddressSpace &&
                    memoryAddressSpace.getAddressableUnitSize() == 1 &&
                    memoryAddressSpace.getSize() <= Integer.SIZE &&
                    memoryAddressSpace.getMinAddress().getOffset() == 0) {
                return new DecodeMemBuffer(address);
            }
            return super.getConcreteBuffer(address, purpose);
        }

        private final class DecodeMemBuffer extends StateMemBuffer {
            DecodeMemBuffer(Address address) {
                super(address, null, Reason.EXECUTE_DECODE);
            }

            @Override
            public int getBytes(byte[] target, int displacement) {
                // Fill Ghidra's own decode window directly, without a ByteBuffer or a
                // temporary state-read array. Borrow the live page only for this copy.
                var storage = getForSpace(memoryAddressSpace, false);
                long offset = address.getOffset() + displacement;
                int length = target.length;
                if (storage != null && offset >= 0 && storage.fitsPage(offset, length)) {
                    BoundPage page = storage.initializedLocalPage(offset, length);
                    if (page != null) {
                        System.arraycopy(page.data, page.index((int) offset & PAGE_MASK),
                            target, 0, length);
                        return length;
                    }
                }
                // Keep stock callbacks, short reads and boundary faults for all other requests.
                return super.getBytes(target, displacement);
            }

            @Override
            public int getBytes(ByteBuffer target, int displacement) {
                source = getForSpace(memoryAddressSpace, false);
                return super.getBytes(target, displacement);
            }
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
            int start = page.index((int) offset & PAGE_MASK);
            // The byte executor may hold or reuse the returned value. Never expose a live page.
            return Arrays.copyOfRange(page.data, start, start + size);
        }

        @Override
        public void setVar(AddressSpace space, long offset, int size, boolean quantize, byte[] value) {
            BoundPage page = value.length == size
                ? initializedLocalPage(space, offset, size, quantize) : null;
            if (page == null) super.setVar(space, offset, size, quantize, value);
            else System.arraycopy(value, 0, page.data, page.index((int) offset & PAGE_MASK), size);
        }

        boolean isInitialized(Varnode node) {
            AddressSpace space = node.getAddress().getAddressSpace();
            long offset = node.getOffset();
            int size = node.getSize();
            if (initializedLocalPage(space, offset, size, false) != null) return true;
            MachineStateSpace storage = getForSpace(space, false);
            return storage != null && storage.isInitialized(offset, size);
        }

        private void markCodeWrite(AddressSpace space, long offset, int size) {
            if (space != memoryAddressSpace || size <= 0) return;
            // Byte and numeric writes both reach this hook. Direct guest RAM
            // bindings are admitted only for regions without register overlap.
            if (deviceWordIndex != null) deviceWordIndex.invalidate(offset, size);
            // An untracked executable page still receives its first byte comparison.
            if (codePages.isEmpty()) return;
            long end = offset + size - 1L;
            if (Long.compareUnsigned(offset, end) > 0 ||
                    Long.compareUnsigned(end, space.getMaxAddress().getOffset()) > 0) {
                generation++;
                return;
            }
            long firstPage = offset >>> PAGE_SHIFT;
            long lastPage = end >>> PAGE_SHIFT;
            if (lastPage > Integer.MAX_VALUE) {
                generation++;
                return;
            }
            if (firstPage == lastPage) {
                if (!codePages.get((int) firstPage)) return;
            }
            else {
                int tracked = codePages.nextSetBit((int) firstPage);
                if (tracked < 0 || tracked > lastPage) return;
            }
            if (++codeGeneration == 0) generation++;
        }

        RunP1MEMachine.MemoryStateSnapshot checkpoint() {
            return RunP1MEMachine.MemoryStateSnapshot.capture(spaceMap);
        }

        boolean hasSameDefinedBytes(RunP1MEMachine.MemoryStateSnapshot snapshot) {
            return snapshot.hasSameDefinedBytes(spaceMap);
        }

        void restoreBoundPages(RunP1MEMachine.MemoryStateSnapshot snapshot) {
            if (deviceWordIndex != null) deviceWordIndex.invalidateAll();
            if (snapshot.copyIntoBoundPages(spaceMap, memoryAddressSpace, codePages) && ++codeGeneration == 0)
                generation++;
        }

        void restore(RunP1MEMachine.MemoryStateSnapshot checkpoint) {
            if (deviceWordIndex != null) deviceWordIndex.invalidateAll();
            // Restore replaces pages and can make previously defined bytes undefined.
            if (deviceLeaves != null) Arrays.fill(deviceLeaves, null);
            for (var space : spaceMap.values()) ((MachineStateSpace) space).invalidatePages();
            registers = uniques = memory = null;
            generation++;
            checkpoint.restore(spaceMap, space -> getForSpace(space, true));
        }

        void release() {
            for (var storage : spaceMap.values()) {
                ((MachineStateSpace) storage).clear();
            }
            spaceMap.clear();
            registers = uniques = memory = null;
            codePages.clear();
            generation++;
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

        DeviceWordIndex watchDeviceWords(RunP1MEMachine.RegisterDef[][] groups) {
            AddressSpace space = backingPiece.memoryAddressSpace;
            long max = space.getMaxAddress().getOffset();
            if (backingPiece.bus == null || backingPiece.deviceWordIndex != null ||
                    groups.length > Long.SIZE || space.getAddressableUnitSize() != 1 ||
                    max < 0 || max > 0xffff_ffffL) return null;
            long first = Long.MAX_VALUE, last = -1;
            for (var group : groups) {
                for (var word : group) {
                    if (word.size != Integer.BYTES || (word.address & 3) != 0 ||
                            word.address < 0 || word.address > max - 3) return null;
                    var region = backingPiece.bus.model.region(word.address, Integer.BYTES);
                    if (region != null && region.templateWrites) return null;
                    first = Math.min(first, word.address);
                    last = Math.max(last, word.address);
                }
            }
            if (last < first || (first >>> PAGE_SHIFT) != (last >>> PAGE_SHIFT)) return null;
            // A leaf's word projection belongs to this index, not the register definition.
            Arrays.fill(backingPiece.deviceLeaves, null);
            return backingPiece.deviceWordIndex =
                new DeviceWordIndex(first, last + Integer.BYTES, max + 1, groups);
        }

        private DeviceLeaf bindDeviceLeaf(RunP1MEMachine.RegisterDef register) {
            long address = register.address;
            int width = register.size;
            AddressSpace space = backingPiece.memoryAddressSpace;
            if ((address >>> 32) != 0 || space.getAddressableUnitSize() != 1) return null;
            var storage = backingPiece.getForSpace(space, false);
            if (storage == null || !storage.fitsPage(address, width)) return null;
            BoundPage page = storage.initializedLocalPage(address, width);
            if (page == null) return null;
            DeviceWordIndex index = backingPiece.deviceWordIndex;
            DeviceLeaf leaf = new DeviceLeaf(page.data, page.index((int) address & PAGE_MASK),
                width, (int) (address >>> PAGE_SHIFT), index == null ? 0 : index.overlapMask(address, width));
            backingPiece.deviceLeaves[register.bindingIndex] = leaf;
            return leaf;
        }

        long readBusBacking(RunP1MEMachine.RegisterDef register, long offset, int size, boolean bigEndian, Reason reason) {
            if (register != null) {
                long lane = offset - register.address;
                if (size > 0 && lane >= 0 && lane <= register.size - size) {
                    DeviceLeaf leaf = backingPiece.deviceLeaves[register.bindingIndex];
                    if (leaf == null) leaf = bindDeviceLeaf(register);
                    if (leaf != null)
                        return BoundPage.readNumberAt(leaf.data, leaf.offset + (int) lane, size, bigEndian);
                }
            }
            return readMemoryNumber(offset, size, reason, bigEndian);
        }

        long inspectDevice(RunP1MEMachine.RegisterDef register, boolean bigEndian) {
            DeviceLeaf leaf = backingPiece.deviceLeaves[register.bindingIndex];
            if (leaf == null) leaf = bindDeviceLeaf(register);
            return leaf == null
                ? readMemoryNumber(register.address, register.size, Reason.INSPECT, bigEndian)
                : leaf.read(bigEndian);
        }

        long inspectInitializedDevice(RunP1MEMachine.RegisterDef register, boolean bigEndian) {
            if (register.size < 1 || register.size > Integer.BYTES) return -1;
            DeviceLeaf leaf = backingPiece.deviceLeaves[register.bindingIndex];
            if (leaf == null) leaf = bindDeviceLeaf(register);
            return leaf == null ? -1 : leaf.read(bigEndian) & 0xffff_ffffL;
        }

        boolean writeDevice(RunP1MEMachine.RegisterDef register, long value, boolean bigEndian) {
            DeviceLeaf leaf = backingPiece.deviceLeaves[register.bindingIndex];
            if (leaf == null) leaf = bindDeviceLeaf(register);
            if (leaf == null) return false;
            if (leaf.watchedWords != 0) backingPiece.deviceWordIndex.dirty |= leaf.watchedWords;
            // A page can become executable after the leaf was bound.
            if (backingPiece.codePages.get(leaf.codePage) && ++backingPiece.codeGeneration == 0)
                backingPiece.generation++;
            writeNumber(leaf.data, leaf.offset, leaf.width, bigEndian, value);
            return true;
        }

        void invalidateDeviceWord(RunP1MEMachine.RegisterDef register) {
            DeviceWordIndex words = backingPiece.deviceWordIndex;
            DeviceLeaf leaf = backingPiece.deviceLeaves[register.bindingIndex];
            if (leaf == null) words.invalidate(register.address, register.size);
            else words.dirty |= leaf.watchedWords;
        }

        long readMemoryNumber(long offset, int size, Reason reason, boolean bigEndian) {
            AddressSpace space = backingPiece.memoryAddressSpace;
            var storage = backingPiece.getForSpace(space, false);
            if (storage != null && storage.fitsPage(offset, size)) {
                BoundPage page = storage.initializedLocalPage(offset, size);
                if (page != null) return page.readNumber((int) offset & PAGE_MASK, size, bigEndian);
            }
            // Cross-page and undefined reads still pass through Ghidra's normal callbacks.
            return Utils.bytesToLong(getVar(space, offset, size, true, reason), size, bigEndian);
        }

        boolean writeMemoryNumberIfInitialized(long offset, int size, long value,
                boolean bigEndian) {
            AddressSpace space = backingPiece.memoryAddressSpace;
            var storage = backingPiece.getForSpace(space, false);
            if (storage == null || !storage.fitsPage(offset, size)) return false;
            BoundPage page = storage.initializedLocalPage(offset, size);
            if (page == null) return false;
            backingPiece.markCodeWrite(space, offset, size);
            page.writeNumber((int) offset & PAGE_MASK, size, bigEndian, value);
            return true;
        }

        private BoundPage initializedMemoryPage(long offset, int size) {
            var storage = backingPiece.getForSpace(backingPiece.memoryAddressSpace, false);
            return storage != null && storage.fitsPage(offset, size)
                ? storage.initializedLocalPage(offset, size) : null;
        }

        private boolean trackedCodePage(long offset) {
            return backingPiece.codePages.get((int) (offset >>> PAGE_SHIFT));
        }

        boolean matches(Plan plan, Address address) {
            if (address.getAddressSpace() != backingPiece.memoryAddressSpace) return false;
            if (plan.verifiedGeneration == backingPiece.generation &&
                    plan.verifiedCodeGeneration == backingPiece.codeGeneration) return true;
            var memory = backingPiece.getForSpace(backingPiece.memoryAddressSpace, false);
            if (memory == null || !memory.verifyCode(address.getOffset(), plan.encoding)) return false;
            plan.verifiedGeneration = backingPiece.generation;
            plan.verifiedCodeGeneration = backingPiece.codeGeneration;
            return true;
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

        boolean restoreBoundPair(RunP1MEMachine.MemoryStateSnapshot sharedSnapshot,
                MachineState local, RunP1MEMachine.MemoryStateSnapshot localSnapshot) {
            // A generated passage can hold pages in either piece. Keep its bindings
            // only if both sets of initialized operands survive the restore.
            if (!backingPiece.hasSameDefinedBytes(sharedSnapshot) ||
                    !local.backingPiece.hasSameDefinedBytes(localSnapshot)) return false;
            backingPiece.restoreBoundPages(sharedSnapshot);
            local.backingPiece.restoreBoundPages(localSnapshot);
            return true;
        }

        @Override
        public void restore(RunP1MEMachine.MemoryStateSnapshot checkpoint) {
            backingPiece.restore(checkpoint);
        }

        void release() {
            backingPiece.release();
        }
    }


    private static final class Plan {
        final RegisterValue context;
        final PseudoInstruction instruction;
        final Address address;
        final byte[] encoding;
        long verifiedGeneration = -1;
        long verifiedCodeGeneration;
        final PcodeProgram program;
        Address fallThrough;
        final boolean contextCommits;
        long bindingGeneration = -1;
        long promotionStart;
        int untilCompile = PROMOTION_HITS;
        int scalarAttempts;
        boolean scalarBus;
        boolean scalarInternalFlow;
        ScalarOp[] scalar;
        Address indirectTarget;
        int busOpIndex = -1;
        boolean straightLine;
        ScalarOp[] busPrefix;
        JitCompiledPassageClass translation;
        EntryPoint entry;
        RunP1MEMachine.Callbacks.InstructionObservation observation;
        final boolean repeatedSelfBranch;
        boolean polledBitTest;
        Address equalPollTarget;
        Site site;
        int templateHits, templateMisses;
        SyncOp templateSync;
        boolean templateControl, irqOnly;
        long templateRetryAt;
        final boolean indirect;
        Address predictedTarget;

        Plan(RegisterValue context, PseudoInstruction instruction) {
            this.context = context;
            this.instruction = instruction;
            address = instruction.getAddress();
            encoding = new byte[instruction.getLength()];
            instruction.getBytes(encoding, 0);
            program = PcodeProgram.fromInstruction(instruction);
            contextCommits = !(instruction.getPrototype() instanceof SleighInstructionPrototype proto) ||
                proto.hasContextCommits();
            repeatedSelfBranch = isRepeatedSelfBranch(program, address);
            List<PcodeOp> ops = program.getCode();
            indirect = !ops.isEmpty() && isIndirect(ops.getLast().getOpcode());
        }

        private static boolean isRepeatedSelfBranch(PcodeProgram program, Address address) {
            List<PcodeOp> code = program.getCode();
            if (code.size() != 1) return false;
            PcodeOp op = code.getFirst();
            if (op.getOpcode() != PcodeOp.BRANCH || op.getOutput() != null ||
                    op.getNumInputs() != 1) return false;
            Varnode target = op.getInput(0);
            return target.isAddress() && target.getAddress().equals(address);
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

    /** Decoded instructions only; a device edge never lends this pair a read witness. */
    static final class PolledBitLoop {
        private final Plan test, branch;

        private PolledBitLoop(Plan test, Plan branch) {
            this.test = test;
            this.branch = branch;
        }

        long testPc() { return test.address.getOffset(); }
        long branchPc() { return branch.address.getOffset(); }
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
                verified = plan != null && !plan.contextCommits && Objects.equals(plan.context, context) && memory.matches(plan, address);
                if (!verified) page[slot] = plan = decodePlan(plan, address, context);
            }
            else {
                plan = otherAddresses.get(address);
                verified = plan != null && !plan.contextCommits && Objects.equals(plan.context, context) && memory.matches(plan, address);
                if (!verified) {
                    plan = decodePlan(plan, address, context);
                    otherAddresses.put(address, plan);
                }
            }
            current = plan;
            lengthWithDelays = plan.encoding.length; // RH850 has no delay slots.
            return plan.instruction;
        }

        private Plan decodePlan(Plan previous, Address address, RegisterValue context) {
            if (previous != null && previous.site != null) previous.site.invalidate();
            PseudoInstruction decoded = super.decodeInstruction(address, context);
            block = null; // Only byte-validated plans are reused.
            return new Plan(context, decoded);
        }

        Plan peekPlan(Address address, RegisterValue context) {
            long offset = address.getOffset();
            Plan plan;
            if (address.getAddressSpace() == codeSpace && (offset & ~0xffff_fffeL) == 0) {
                int pageIndex = (int) (offset >>> PAGE_SHIFT);
                Plan[][] group = pages[pageIndex >>> TABLE_BITS];
                if (group == null) return null;
                Plan[] page = group[pageIndex & (TABLE_SIZE - 1)];
                if (page == null) return null;
                plan = page[((int) offset & PAGE_MASK) >>> 1];
            }
            else {
                plan = otherAddresses.get(address);
            }
            return plan != null && plan.isAt(address, context) ? plan : null;
        }

        void activate(Plan plan) {
            current = plan;
            lengthWithDelays = plan.encoding.length;
        }

        @Override
        public PseudoInstruction getLastInstruction() {
            return current == null ? null : current.instruction;
        }

        void release() {
            Arrays.fill(pages, null);
            otherAddresses.clear();
            current = null;
        }
    }

    final class MachineThread extends JitPcodeThread {
        final MemorySegment threadStop=Arena.ofAuto().allocate(JAVA_INT);
        @Override public void setSuspended(boolean s){
            if(s)JAVA_INT.varHandle().setVolatile(threadStop,0L,1);
            super.setSuspended(s);
            if(!s)JAVA_INT.varHandle().setVolatile(threadStop,0L,0);
        }
        private static final int WINDOWS_PER_KIND = 4;
        // Word offsets in windowgraph-abi.h.
        private static final int CTL_EXIT = 2, CTL_READS = 3, CTL_COUNT = 4;
        private static final int CTL_MODE = 5;
        private static final int CTL_FETCH_LO = 6, CTL_FETCH_HI = 7;
        private static final int CTL_INDEX = 8, CTL_BASE = 9, CTL_WINDOWS = 10;
        private static final int WINDOW_WORDS = 5;
        private static final int CTL_PARTIAL_OP = CTL_WINDOWS + WINDOW_WORDS * 2 * WINDOWS_PER_KIND;
        private static final int CTL_PARTIAL_SITE = CTL_PARTIAL_OP + 1;
        private static final int CTL_MISS_ADDRESS = CTL_PARTIAL_SITE + 1, CTL_MISS_TRANSFER = CTL_MISS_ADDRESS + 1;
        // The shared history uses a fixed start cursor for the whole graph batch.
        private static final int MISS_STACK = 128, NATIVE_LIMIT = 256, MAX_STACK_WORDS = 32;
        private static final int CTL_RETIRE_FLAGS = CTL_MISS_TRANSFER + 1;
        private static final int CTL_STORED = CTL_RETIRE_FLAGS + 1, CTL_WRITE_LOST = CTL_STORED + 1;
        private static final int CTL_ALIASES = CTL_WRITE_LOST + 1, CTL_SYNC = CTL_ALIASES + 1;
        private static final int CTL_WRITE_COUNT = CTL_SYNC + 3;
        private static final int CTL_RECENT_START = CTL_WRITE_COUNT + 1, CTL_RECENT = CTL_RECENT_START + 1;
        private static final int CTL_WRITE_MISSES = CTL_RECENT + RunP1MEMachine.Trace.RECENT_PC_COUNT;
        private static final int STACK_RAM = 256;
        private static final int MODE_CHECKED_DESCRIPTORS = 512;
        private static final int EXIT_BUS = 1, EXIT_INDIRECT = 2;
        final long[] nativeCtl = new long[CTL_WRITE_MISSES + NATIVE_LIMIT * MAX_STACK_WORDS];
        final MemorySegment controls = MemorySegment.ofArray(nativeCtl);
        final Map<RunP1MEMachine.RegionDef,NativeGroup> nativeBanks = new IdentityHashMap<>();
        boolean apertureDirty = true;

        String nativeDiagnostic() {
            return NativeSite.diagnostic();
        }

        private long apertureCodeCoverage = -1;
        private long grantBacking = -1, grantCode = -1, grantCoverage = -1;
        private long grantPolicy = -1;
        private boolean hasGlobalStore;

        private void beginDataWindows(MachineStatePiece storage) {
            if (fetchPolicy < 0 || fetchPolicy != grantPolicy || grantBacking != storage.generation ||
                    grantCode != storage.codeGeneration) {
                dataNext[0] = dataNext[1] = 0;
                apertureDirty = true;
            } else if (hasGlobalStore || grantCoverage != storage.codeCoverage) {
                dataNext[1] = 0;
                apertureDirty = true;
            }
            grantPolicy = fetchPolicy;
            hasGlobalStore = false;
            grantBacking = storage.generation;
            grantCode = storage.codeGeneration;
            grantCoverage = storage.codeCoverage;
        }

        private void bindApertures() {
            MachineStatePiece backend = ((Decoder) decoder).memory.backingPiece;
            if (!apertureDirty && apertureCodeCoverage == backend.codeCoverage) return;
            apertureCodeCoverage = backend.codeCoverage;
            apertureDirty = false;
            int count = 0;
            for (int kind = 0; kind < 2; kind++) {
                for (int i = 0, n = Math.min(WINDOWS_PER_KIND, dataNext[kind]); i < n; i++) {
                    DataWindow window = dataWindow(kind, i);
                    long lo = window.start, hi = window.end;
                    boolean mirrored = window.mirror != null;
                    if (kind == 1) {
                        var code = backend.codePages;
                        for (int pass = 0; pass < (mirrored ? 2 : 1); pass++) {
                            long delta = pass == 0 ? 0 : window.mirrorDelta;
                            int page = (int) ((window.probe + delta) >>> PAGE_SHIFT);
                            if (code.get(page)) { hi = lo; break; }
                            int before = code.previousSetBit(page), after = code.nextSetBit(page);
                            if (before >= 0) lo = Math.max(lo, ((long) (before + 1) << PAGE_SHIFT) - delta);
                            if (after >= 0) hi = Math.min(hi, ((long) after << PAGE_SHIFT) - delta);
                        }
                    }
                    if (hi <= lo) continue;
                    long primaryOffset = lo - window.primary.base + window.primary.arrayOffset;
                    long mirrorOffset = mirrored ? lo + window.mirrorDelta - window.mirror.base +
                        window.mirror.arrayOffset : 0;
                    if (primaryOffset < 0 || primaryOffset + hi - lo > window.primary.data.length ||
                            (mirrored && (mirrorOffset < 0 || mirrorOffset + hi - lo > window.mirror.data.length)))
                        throw new AssertionError("bad live data span");
                    int row = CTL_WINDOWS + WINDOW_WORDS * count;
                    nativeCtl[row] = lo;
                    nativeCtl[row + 1] = hi;
                    nativeCtl[row + 2] = (window.region.templateRam ? STACK_RAM : 0) | (mirrored ? 1 : 0);
                    nativeCtl[row + 3] = primaryOffset;
                    nativeCtl[row + 4] = mirrorOffset;
                    count++;
                }
                if (kind == 0) nativeCtl[CTL_READS] = count;
            }
            nativeCtl[CTL_COUNT] = count;
        }

        private int nativeRun(NativeGroup bank, Site site, int entry, int retired, int limit) {
            boolean canAdmit = !RunP1MEMachine.Model.descriptorMpuEnabled(templateProtectionMode) || grantPolicy > 0;
            nativeCtl[CTL_FETCH_LO] = fetchMpu.start;
            nativeCtl[CTL_MODE] = templateProtectionMode | (grantPolicy > 0 ? MODE_CHECKED_DESCRIPTORS : 0) |
                (callbacks.model.pendingPriorityMask == 0 &&
                interruptStatusAlreadyClear() ? 256 : 0);
            nativeCtl[CTL_FETCH_HI] = fetchMpu.end;
            nativeCtl[CTL_INDEX] = bank.fetchLocations;
            nativeCtl[CTL_BASE] = bank.base;
            int start = retired;
            for (int refills = 0;; refills++) {
                bindApertures();
                retired += invokeNative(bank, site, entry, retired, limit);
                if (!canAdmit || refills == 2 || retired >= limit - 1 ||
                        nativeCtl[CTL_EXIT] != EXIT_BUS || suspended()) break;
                long transfer = nativeCtl[CTL_MISS_TRANSFER];
                long address = nativeCtl[CTL_MISS_ADDRESS];
                int size = ((int) transfer & 127) >>> 1, kind = (int) transfer & 1;
                boolean stack = (transfer & MISS_STACK) != 0;
                if (!admitDataWindow(address, size, kind == 1, stack)) break;

                // This miss committed none of its instruction, including a stack
                // prefix. The summary for its predecessors was applied on return.
                entry = (int) (transfer >>> 8);
            }
            return retired - start;
        }

        private int invokeNative(NativeGroup bank, Site site, int entry, int retired, int limit) {
            var model = callbacks.model;
            var trace = model.trace;
            int flags = trace.nativeRetirementFlags();
            nativeCtl[CTL_RETIRE_FLAGS] = flags;
            MemorySegment written = (flags & (RunP1MEMachine.Trace.NATIVE_MARK | RunP1MEMachine.Trace.NATIVE_COVER)) != 0
                ? trace.nativeWrittenBytes() : MemorySegment.NULL;
            int n;
            try {
                var memory = ((Decoder) decoder).memory.backingPiece.memory;
                MemorySegment bus = memory == null || memory.slabSegment == null ? MemorySegment.NULL : memory.slabSegment;
                var r = retirementState.registers;
                var u = retirementState.uniques;
                MemorySegment registers = r == null || r.slabSegment == null ? MemorySegment.NULL : r.slabSegment;
                MemorySegment unique = u == null || u.slabSegment == null ? MemorySegment.NULL : u.slabSegment;
                n = (int) NativeSite.RUNNER.run.invokeExact(entry, retired, limit, bank.words, bank.indices,
                    controls, written, machineStop, threadStop, registers, unique, bus);
            }
            catch (Throwable e) {
                throw new AssertionError(e);
            }
            if (n < 0 || n > limit - retired) throw new AssertionError("Invalid native retirement count " + n + " at " + site.pc);
            if (nativeCtl[CTL_STORED] != 0) {
                model.discardBusStore = false;
                trace.finishNativeWrites(nativeCtl[CTL_ALIASES], nativeCtl[CTL_WRITE_LOST] != 0,
                    nativeCtl, CTL_WRITE_MISSES, (int) nativeCtl[CTL_WRITE_COUNT]);
            }
            for (int i = 0; i < SYNC_OPS.length; i++) {
                long count = nativeCtl[CTL_SYNC + i];
                if (count != 0) trace.addNativeSync(SYNC_OPS[i].name(), count);
            }
            return n;
        }

        long compiledInstructions;
        long idleInstructions;
        long templateInstructions;
        private final RunP1MEMachine.Model.MpuWindow fetchReceipt = new RunP1MEMachine.Model.MpuWindow();
        private long receiptPolicy = -1, fetchPolicy = -1;
        private byte[] policyBank, policyBytes;
        private int policyStart, policyAsid;
        private long policyGeneration = -1, policyRevision;
        private final RunP1MEMachine.Model.MpuWindow fetchMpu = new RunP1MEMachine.Model.MpuWindow();
        private final RunP1MEMachine.Model.MpuWindow readMpu = new RunP1MEMachine.Model.MpuWindow();
        private final RunP1MEMachine.Model.MpuWindow writeMpu = new RunP1MEMachine.Model.MpuWindow();
        private int templateProtectionMode;
        private static final class DataWindow {
            long start, end, mirrorDelta, probe;
            BoundPage primary, mirror;
            RunP1MEMachine.RegionDef region;
        }
        private final RunP1MEMachine.Model.MpuWindow transfer = new RunP1MEMachine.Model.MpuWindow();
        private final int[] dataNext = new int[2];
        private final DataWindow[] dataWindows = new DataWindow[2 * WINDOWS_PER_KIND];
        { Arrays.setAll(dataWindows, i -> new DataWindow()); }

        private DataWindow dataWindow(int kind, int newest) {
            return dataWindows[kind * WINDOWS_PER_KIND +
                ((dataNext[kind] - 1 - newest) & (WINDOWS_PER_KIND - 1))];
        }
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
        final class RegisterImage {
            private final MachineStatePiece shared = ((MachineState) getState().getSharedState()).backingPiece;
            private final AddressSpace space = pc.getAddressSpace();
            private final long generation = retirementState.generation;
            private final List<generic.ULongSpan> defined;
            final byte[][] bytes;
            final int[] offsets;

            private RegisterImage(MachineStatePiece.MachineStateSpace bank, Register[] registers) {
                defined = List.copyOf(bank.backing().getInitialized().spans());
                bytes = new byte[registers.length][];
                offsets = new int[registers.length];
                for (int i = 0; i < registers.length; i++) {
                    Register reg = registers[i];
                    long offset = reg.getAddress().getOffset();
                    var page = bank.initializedLocalPage(offset, reg.getNumBytes());
                    bytes[i] = page.data;
                    offsets[i] = page.index((int) offset & PAGE_MASK);
                }
            }

            boolean current() {
                if (generation != retirementState.generation || shared.getForSpace(space, false) != null) return false;
                var live = retirementState.getForSpace(space, false).backing().getInitialized().spans();
                if (live.size() != defined.size()) return false;
                int i = 0;
                for (var span : live) {
                    var old = defined.get(i++);
                    if (old.min() != span.min() || old.max() != span.max()) return false;
                }
                return true;
            }
        }

        RegisterImage bindRegisterImage(Register[] registers) {
            var space = pc.getAddressSpace();
            var bank = retirementState.getForSpace(space, false);
            if (bank == null || ((MachineState) getState().getSharedState()).backingPiece.getForSpace(space, false) != null ||
                    language.getRegisters().stream().anyMatch(r -> r.getAddressSpace() != space)) return null;
            for (Register reg : registers) {
                long offset = reg.getAddress().getOffset();
                if (!bank.fitsPage(offset, reg.getNumBytes())) return null;
            }
            return new RegisterImage(bank, registers);
        }

        private final ProcessorRegister counterRetirement = new ProcessorRegister(pc, bigEndian);
        private final ProcessorRegister contextRetirement = contextreg == Register.NO_CONTEXT
            ? null : new ProcessorRegister(contextreg, true);
        private final ProcessorRegister pswRegister = bindNamed("PSW");
        private final ProcessorRegister mpmRegister = bindNamed("MPM");
        private final ProcessorRegister asidRegister = bindNamed("ASID");
        private final ProcessorRegister mctlRegister = bindNamed("MCTL");
        private final int pswUserLane = pswRegister == null ? 0 : pswRegister.byteLane(3);
        private final int mpmModeLane = mpmRegister == null ? 0 : mpmRegister.byteLane(0);
        private BoundPage protectionModePage;
        private long protectionModeGeneration = -1;
        private final ProcessorRegister intcfgRegister = bindNamed("INTCFG");
        private final ProcessorRegister isprRegister = bindNamed("ISPR");
        private final ProcessorRegister icsrRegister = bindNamed("ICSR");
        private final ProcessorRegister pmrRegister = bindNamed("PMR");
        private final Register zeroRegister = language.getRegister("r0");
        private final Register linkAddress = language.getRegister("ll_addr");
        private final Register linkValid = language.getRegister("ll_valid");
        private final Register stackPointer = language.getRegister("sp");
        private final Varnode stackInput = stackPointer == null || stackPointer.getNumBytes() != Integer.BYTES
            ? null : new Varnode(stackPointer.getAddress(), Integer.BYTES);
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
            // Raw Sleigh varnodes compare by space, offset, and width. One bank
            // binding can serve every instruction using that register or temporary.
            private final Map<Varnode, ScalarOperand> boundOperands = new HashMap<>();
            private final ScalarOperand[] constants = new ScalarOperand[256];
            private long operandGeneration = -1;

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
                    long value = number(node, null);
                    int slot = node.hashCode() * 0x9e3779b9 >>> 24;
                    ScalarOperand operand = constants[slot];
                    if (operand == null || operand.size != node.getSize() || operand.constant != value)
                        constants[slot] = operand = new ScalarOperand(null, 0, node.getSize(), value);
                    return operand;
                }
                if (operandGeneration != local.generation) {
                    boundOperands.clear();
                    operandGeneration = local.generation;
                }
                ScalarOperand operand = boundOperands.get(node);
                if (operand != null) return operand;
                BoundPage page = local.numberPage(node);
                if (page == null) return null;
                operand = new ScalarOperand(page, (int) node.getOffset() & PAGE_MASK, node.getSize(), 0);
                boundOperands.put(node, operand);
                return operand;
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
                        Address target = op.getInput(0).getAddress();
                        if (target.isConstantAddress()) {
                            if (opcode == PcodeOp.CALL) return null;
                        }
                        else if (byteCounterSpace == null || target.getAddressSpace() != byteCounterSpace)
                            return null;
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

        private JitCompiledPassageClass compilePlan(Plan plan, AddrCtx seed) {
            List<PcodeOp> source = plan.program.getCode();
            Address target = plan.instruction.getMaxAddress().next();
            boolean linear = plan.straightLine && target != null && (seed.rvCtx == null ||
                (!plan.contextCommits && seed.rvCtx.equals(plan.context) &&
                stableFlow(seed.rvCtx, seed.address) && stableFlow(seed.rvCtx, target)));
            List<PcodeOp> code;
            PcodeOp exit;
            JitPassage.PBranch exitBranch;
            if (linear) {
                AddrCtx next = new AddrCtx(seed.rvCtx, target);
                int start = Math.max(0, plan.busOpIndex);
                code = new ArrayList<>(Math.max(1, source.size() - start) + 1);
                for (int i = start; i < source.size(); i++) code.add(new DecodedPcodeOp(seed, source.get(i)));
                if (code.isEmpty()) code.add(new NopPcodeOp(seed, 0));
                exit = ExitPcodeOp.exit(next);
                exitBranch = new RExtBranch(exit, next, null, CtxReach.WITHOUT_CTXMOD);
                code.add(exit);
            }
            else if (plan.busOpIndex < 0) {
                return P1MEJitMachine.this.compileWithMaxOpsBackoff(seed, passageDecoder);
            }
            else {
                // The decoder owns the exit when the instruction changes context.
                JitPassage decoded = passageDecoder.decodePassage(seed, getConfiguration().maxPassageOps());
                List<PcodeOp> all = decoded.getCode();
                if (all.size() != source.size() + 1) return null;
                code = all.subList(plan.busOpIndex, all.size());
                exit = code.getLast();
                exitBranch = decoded.getBranches().get(exit);
                if (!(exit instanceof ExitPcodeOp) || exitBranch == null ||
                        code.getFirst().getOpcode() != source.get(plan.busOpIndex).getOpcode()) return null;
            }
            // The bus prefix commits before entry. Its address is a live variable,
            // even when the excluded prefix could have folded it to a constant.
            PcodeOp first = code.getFirst();
            PcodeOp entry = new EntryPcodeOp(seed);
            return compiler.compilePassage(JIT_LOOKUP, new JitPassage(getLanguage(), seed, code,
                passageDecoder.library, List.of(plan.instruction),
                Map.of(entry, new RIntBranch(entry, first, false, CtxReach.WITHOUT_CTXMOD), exit, exitBranch),
                Map.of(first, seed), Map.of()));
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
                compiling = plan;
                try {
                    plan.translation = compilePlan(plan, seed);
                }
                finally {
                    compiling = null;
                }
                if (plan.translation == null) return null;
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
            boolean internal = false;
            boolean unbound = false;
            for (int i = 0; i < ops.length; i++) {
                ScalarOp op = local.bindInstructionOp(code.get(i));
                if (op == null) {
                    OpBehavior behavior = OpBehaviorFactory.getOpBehavior(code.get(i).getOpcode());
                    if (!(behavior instanceof UnaryOpBehavior || behavior instanceof BinaryOpBehavior))
                        return null;
                    unbound = true;
                    continue;
                }
                bus |= op.opcode == PcodeOp.LOAD || op.opcode == PcodeOp.STORE;
                if (op.target != null && op.target.isConstantAddress()) {
                    long next = (long) i + (int) op.target.getOffset();
                    if (next < 0 || next > ops.length) return null;
                    internal = true;
                }
                ops[i] = op;
            }
            // A cold arm may still have undefined temporaries. Only internal-flow
            // instructions have a live frame for resuming at such an operation.
            if (unbound && (!internal || bus)) return null;
            plan.scalarBus = bus;
            plan.scalarInternalFlow = internal;
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
                    long value = callbacks.readBusNumber(address, out.size);
                    out.page.writeNumber(out.start, out.size, bigEndian, value);
                }
                else {
                    ScalarOperand in = op.right;
                    callbacks.writeBusNumber(address, in.size, in.read(bigEndian));
                }
            }
            finally {
                pendingBusFrame = null;
            }
        }

        private void runScalar(Plan plan, ScalarOp[] ops) {
            // An internal branch changes the frame's index but not its executed-op count.
            if (plan.scalarInternalFlow) frame = beginPlan(plan);
            for (int i = 0; i < ops.length; i++) {
                ScalarOp op = ops[i];
                if (op == null) {
                    op = ((LocalExecutor) executor).bindInstructionOp(plan.program.getCode().get(i));
                    if (op == null) {
                        finishPlan(plan);
                        return;
                    }
                    ops[i] = op;
                }
                if (frame != null) frame.advance();
                if (isSuspended() || P1MEJitMachine.this.suspended) {
                    throw new SuspendedPcodeExecutionException(materializeFrame(plan, i + 1), null);
                }
                Address target = null;
                try {
                    if (op.behavior != null) op.execute(bigEndian);
                    else if (op.opcode == PcodeOp.LOAD || op.opcode == PcodeOp.STORE) {
                        scalarBus(plan, op, i + 1);
                    }
                    else if (op.target != null) {
                        if (op.left == null || op.left.read(bigEndian) != 0) {
                            if (op.target.isConstantAddress()) {
                                frame.branch((int) op.target.getOffset());
                                i = frame.index() - 1;
                            }
                            else target = op.target;
                        }
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
                    throw new PcodeExecutionException(fault.getMessage(),
                        frame != null ? frame : materializeFrame(plan, i + 1), fault);
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

            int readByte(int index) {
                // Bind the whole register, not just the selected lane: an
                // undefined neighboring byte must still fail the INSPECT read.
                BoundPage source = page();
                if (source == null) return (int) (inspectRegister(register) >>> (index * 8)) & 0xff;
                return index >= size ? 0 : source.unsignedByte(byteLane(index));
            }

            int byteLane(int index) {
                return start + (bigEndian ? size - 1 - index : index);
            }

            boolean write(long value) {
                BoundPage destination = page();
                if (destination == null) return false;
                destination.writeNumber(start, size, bigEndian, value);
                return true;
            }

            void release() {
                page = null;
                generation = -1;
            }
        }

        private final class MpuDescriptorBinding implements RunP1MEMachine.Model.MpuDescriptor {
            private final ProcessorRegister attributes, lower, upper;
            private final boolean contiguousBounds;
            private BoundPage boundsPage;
            private long boundsGeneration = -1;

            MpuDescriptorBinding(Register attributes, Register lower, Register upper) {
                this.attributes = bindProcessorRegister(attributes);
                this.lower = bindProcessorRegister(lower);
                this.upper = bindProcessorRegister(upper);
                contiguousBounds = this.lower.canBind && this.upper.canBind &&
                    this.lower.size == Integer.BYTES && this.upper.size == Integer.BYTES &&
                    lower.getOffset() + Integer.BYTES == upper.getOffset() &&
                    this.lower.start <= PAGE_SIZE - Long.BYTES;
            }

            @Override
            public long attributes() {
                return attributes.read();
            }

            @Override
            public long bounds() {
                if (contiguousBounds) {
                    long current = retirementState.generation;
                    if (boundsPage == null || boundsGeneration != current) {
                        Register base = lower.register;
                        boundsPage = retirementState.initializedLocalPage(
                            base.getAddressSpace(), base.getOffset(), Long.BYTES, true);
                        boundsGeneration = current;
                    }
                    if (boundsPage != null) {
                        long value = boundsPage.readNumber(lower.start, Long.BYTES, bigEndian);
                        return bigEndian ? Long.rotateLeft(value, 32) : value;
                    }
                }
                // Keep the definedness checks in the same order as scalar INSPECT.
                return lower.read() | (upper.read() << 32);
            }
        }

        RunP1MEMachine.Model.MpuDescriptor bindMpuDescriptor(
                Register attributes, Register lower, Register upper) {
            return new MpuDescriptorBinding(attributes, lower, upper);
        }

        int processorUserMode() {
            int psw = pswRegister == null ? (int) (processorRegister("PSW") >>> 24)
                : pswRegister.readByte(3);
            return psw & RunP1MEMachine.Model.CPU_USER_MODE;
        }

        int processorProtectionMode() {
            BoundPage source = protectionModePage;
            if (source != null && protectionModeGeneration == retirementState.generation) {
                return (source.unsignedByte(pswUserLane) & RunP1MEMachine.Model.CPU_USER_MODE) |
                    (source.unsignedByte(mpmModeLane) & 3);
            }
            return bindProtectionMode();
        }

        private int bindProtectionMode() {
            int user = processorUserMode();
            int mpm = mpmRegister == null ? (int) processorRegister("MPM") : mpmRegister.readByte(0);
            // Only after both complete registers were inspected can their
            // byte lanes be read from a single known-defined, live page.
            long generation = retirementState.generation;
            if (pswRegister != null && mpmRegister != null && pswRegister.size == Integer.BYTES &&
                    mpmRegister.size == Integer.BYTES && pswRegister.page == mpmRegister.page &&
                    pswRegister.generation == generation && mpmRegister.generation == generation) {
                protectionModePage = pswRegister.page;
                protectionModeGeneration = generation;
            }
            return user | (mpm & 3);
        }

        int processorAsid() {
            return (int) (asidRegister == null ? processorRegister("ASID") : asidRegister.read()) & 0x3ff;
        }

        boolean interruptStatusAlreadyClear() {
            // Only use bytes which an ordinary register read has proved available.
            // A changed status bit is visible immediately; restore replaces both pages.
            long generation = retirementState.generation;
            if (pswRegister == null || pswRegister.generation != generation || pswRegister.page == null
                    || icsrRegister == null || icsrRegister.generation != generation || icsrRegister.page == null)
                return false;
            int lowByte = icsrRegister.start + (bigEndian ? icsrRegister.size - 1 : 0);
            return (icsrRegister.page.unsignedByte(lowByte) & 1) == 0;
        }

        boolean interruptDisabledAtBusBoundary() {
            if (pswRegister == null || pswRegister.generation != retirementState.generation ||
                    pswRegister.page == null) return false;
            int lowByte = pswRegister.start + (bigEndian ? pswRegister.size - 1 : 0);
            return (pswRegister.page.unsignedByte(lowByte) & 0xa0) != 0;
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

        private RegisterValue flowInput, flowDefaults, flowResult;
        private long flowBits;

        private RegisterValue flowingContext(RegisterValue input, Address target) {
            RegisterValue defaults = defaultContext.getDefaultValue(contextreg, target);
            if (flowResult == null || !Objects.equals(input, flowInput) || !Objects.equals(defaults, flowDefaults)) {
                flowInput = input;
                flowDefaults = defaults;
                flowResult = new RegisterValue(contextreg, BigInteger.ZERO).combineValues(defaults)
                    .combineValues(defaultContext.getFlowValue(input));
                if (contextRetirement.size <= Long.BYTES) flowBits = flowResult.getUnsignedValueIgnoreMask().longValue();
            }
            return flowResult;
        }

        private boolean stableFlow(RegisterValue input, Address target) {
            return input != null && input.equals(flowingContext(input, target));
        }

        private void retireInterpretedContext(Plan plan, Address counter) {
            RegisterValue previous = getContext();
            RegisterValue flow = flowingContext(previous, counter);
            if (plan.contextCommits) writeContext(flow.combineValues(getContextAfterCommits()));
            else if (!flow.equals(previous) || contextRetirement.size > Long.BYTES ||
                    !contextRetirement.write(flowBits)) writeContext(flow);
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

        private boolean stableRetirementContext(Plan plan, RegisterValue context, Address next) {
            if (contextreg == Register.NO_CONTEXT) return true;
            return context != null && contextRetirement.size <= Long.BYTES &&
                context.equals(plan.context) && stableTemplateContext(plan, next);
        }

        private boolean isPolledBitTest(Plan plan) {
            if (plan.polledBitTest) return true;
            if (pswRegister == null || plan.observation == null ||
                    !"tst1".equals(plan.observation.mnemonic)) {
                return false;
            }
            boolean load = false;
            boolean psw = false;
            for (PcodeOp op : plan.program.getCode()) {
                int kind = op.getOpcode();
                Varnode output = op.getOutput();
                if (kind == PcodeOp.LOAD) {
                    if (load || op.getNumInputs() != 2 ||
                            op.getInput(0).getOffset() != byteCounterSpace.getSpaceID() ||
                            output == null || !output.isUnique() || output.getSize() != 1) {
                        return false;
                    }
                    load = true;
                }
                else if (!(kind == PcodeOp.COPY || kind == PcodeOp.SUBPIECE ||
                        kind == PcodeOp.PIECE ||
                        (kind >= PcodeOp.INT_EQUAL && kind <= PcodeOp.INT_MULT) ||
                        (kind >= PcodeOp.BOOL_NEGATE && kind <= PcodeOp.BOOL_OR))) {
                    return false;
                }
                if (output == null || output.isUnique()) continue;
                if (!output.isRegister() || !overlapsRegister(output, pswRegister.register)) {
                    return false;
                }
                psw = true;
            }
            plan.polledBitTest = load && psw;
            return plan.polledBitTest;
        }

        private boolean isTakenEqualBranch(Plan plan, Address target) {
            if (plan.equalPollTarget != null) return plan.equalPollTarget.equals(target);
            if (plan.observation == null || !"be".equals(plan.observation.mnemonic)) return false;
            boolean branch = false;
            for (PcodeOp op : plan.program.getCode()) {
                int kind = op.getOpcode();
                if (kind == PcodeOp.CBRANCH) {
                    if (branch || op.getNumInputs() != 2 || op.getOutput() != null) return false;
                    Varnode destination = op.getInput(0);
                    if (!destination.isAddress() || !destination.getAddress().equals(target)) {
                        return false;
                    }
                    branch = true;
                }
                else {
                    Varnode output = op.getOutput();
                    if (!(kind == PcodeOp.COPY || kind == PcodeOp.SUBPIECE ||
                            kind == PcodeOp.PIECE ||
                            (kind >= PcodeOp.INT_EQUAL && kind <= PcodeOp.INT_MULT) ||
                            (kind >= PcodeOp.BOOL_NEGATE && kind <= PcodeOp.BOOL_OR)) ||
                            (output != null && !output.isUnique())) {
                        return false;
                    }
                }
            }
            if (branch) plan.equalPollTarget = target;
            return branch;
        }

        // A policy version says previously granted ranges are unchanged; it grants no access itself.
        // Cache only when every descriptor has defined, directly readable bounds and attributes.
        private boolean bindPolicyBank() {
            BoundPage bank = null;
            int lo = PAGE_SIZE, hi = 0;
            for (var raw : callbacks.model.mpu) {
                if (!(raw instanceof MpuDescriptorBinding d)) return false;
                BoundPage page = d.attributes.page();
                if (page == null || d.attributes.size != 4 || d.lower.size != 4 || d.upper.size != 4 ||
                        d.lower.page() != page || d.upper.page() != page || (bank != null && bank != page)) return false;
                bank = page;
                lo = Math.min(lo, Math.min(d.attributes.start, Math.min(d.lower.start, d.upper.start)));
                hi = Math.max(hi, Math.max(d.attributes.start, Math.max(d.lower.start, d.upper.start)) + 4);
            }
            if (bank == null || asidRegister == null || asidRegister.page() == null) return false;
            policyBank = bank.data;
            policyStart = bank.index(lo);
            policyBytes = Arrays.copyOfRange(policyBank, policyStart, bank.index(hi));
            policyGeneration = retirementState.generation;
            policyAsid = processorAsid();
            policyRevision++;
            return true;
        }

        private long policyVersion(int mode) {
            if ((mode & RunP1MEMachine.Model.CPU_USER_MODE) != 0) return -1;
            if (!RunP1MEMachine.Model.descriptorMpuEnabled(mode)) return 0;
            if (policyGeneration != retirementState.generation) return bindPolicyBank() ? policyRevision : -1;
            int asid = processorAsid();
            if (asid != policyAsid || !Arrays.equals(policyBank, policyStart, policyStart + policyBytes.length,
                    policyBytes, 0, policyBytes.length)) {
                System.arraycopy(policyBank, policyStart, policyBytes, 0, policyBytes.length);
                policyAsid = asid;
                policyRevision++;
            }
            return policyRevision;
        }

        private long authorizeFetch(long pc, int mode, RunP1MEMachine.Model.MpuWindow window) {
            fetchPolicy = policyVersion(mode);
            if (fetchPolicy >= 0 && receiptPolicy == fetchPolicy && fetchReceipt.covers(pc, 1)) {
                if (window != null) window.set(fetchReceipt.start, fetchReceipt.end);
                return fetchReceipt.end;
            }
            var model = callbacks.model;
            var grant = window == null ? fetchReceipt : window;
            receiptPolicy = -1;
            grant.clear();
            long end = model.requireExecute(this, pc, 1, mode, grant);
            if (fetchPolicy >= 0 && end > pc) {
                var region = model.region(pc, 1);
                if (region != null && region.executable && !"dataflash".equals(region.name)) {
                    fetchReceipt.set(Math.max(grant.start, region.start), Math.min(end, region.lookupEnd));
                    if (window != null) window.set(fetchReceipt.start, fetchReceipt.end);
                    receiptPolicy = fetchPolicy;
                    return fetchReceipt.end;
                }
            }
            return end;
        }

        /**
         * Retire a scheduler-proven quiet span at an idempotent instruction boundary.
         * The scheduler owns trace, clock, and event accounting for the returned count.
         */
        long batchIdle(long maxInstructions) {
            if (maxInstructions <= 0 || frame != null || instruction != null ||
                    modifier != null || isSuspended() || P1MEJitMachine.this.suspended ||
                    !accessBreakpoints.isEmpty()) return 0;

            Address counter = getCounter();
            RegisterValue context = getContext();
            Decoder activeDecoder = (Decoder) decoder;
            Plan plan = activeDecoder.current;
            if (plan == null || !plan.repeatedSelfBranch || !plan.isAt(counter, context) ||
                    getInject(counter) != null || !activeDecoder.memory.matches(plan, counter)) {
                return 0;
            }
            if (!stableRetirementContext(plan, context, counter)) return 0;

            long fetchEnd = callbacks.authorizeInstructionStart(this, counter);
            long end = counter.getOffset() + plan.encoding.length;
            if (plan.encoding.length <= 0 || Long.compareUnsigned(end, fetchEnd) > 0) return 0;
            instructionVisits += maxInstructions;
            idleInstructions += maxInstructions;
            return maxInstructions;
        }

        private boolean batchDispatchAllowed() {
            return frame == null && instruction == null && modifier == null && !suspended()
                && accessBreakpoints.isEmpty() && injects.isEmpty() && P1MEJitMachine.this.injects.isEmpty()
                && getSoftwareInterruptMode() != SwiMode.IGNORE_STEP && byteCounterSpace != null;
        }

        PolledBitLoop decodedPolledBitLoop(PolledBitLoop previous, Instruction test, long branchPc) {
            Address counter = getCounter();
            if (!counter.equals(test.getAddress()) || !batchDispatchAllowed() ||
                    counter.getAddressSpace() != byteCounterSpace) return null;
            Decoder activeDecoder = (Decoder) decoder;
            Plan branch = activeDecoder.current;
            if (branch == null || branch.address.getAddressSpace() != byteCounterSpace ||
                    branch.address.getOffset() != branchPc) return null;
            if (previous != null && previous.test.instruction == test && previous.branch == branch)
                return previous;
            RegisterValue context = getContext();
            Plan testPlan = activeDecoder.peekPlan(counter, context);
            if (testPlan == null || testPlan.instruction != test ||
                    !branch.address.equals(testPlan.fallThrough) || !branch.isAt(branch.address, context) ||
                    !isPolledBitTest(testPlan) || !isTakenEqualBranch(branch, counter)) return null;
            return new PolledBitLoop(testPlan, branch);
        }

        /**
         * Retire whole pairs within an already-proven quiet span. The caller
         * requires an actual read and taken branch since the last invalidation.
         */
        long batchPolledBit(long maxInstructions, PolledBitLoop loop, long readAddress) {
            long retired = maxInstructions & ~1L;
            if (retired <= 0 || !batchDispatchAllowed()) return 0;
            Plan test = loop.test;
            Plan branch = loop.branch;
            Address counter = getCounter();
            RegisterValue context = getContext();
            long generation = retirementState.generation;
            Decoder activeDecoder = (Decoder) decoder;
            if (activeDecoder.current != branch || !test.isAt(counter, context) ||
                    !branch.isAt(branch.address, context) || test.bindingGeneration != generation ||
                    branch.bindingGeneration != generation || !activeDecoder.memory.matches(test, counter) ||
                    !activeDecoder.memory.matches(branch, branch.address) ||
                    !stableRetirementContext(test, context, branch.address) ||
                    !stableRetirementContext(branch, context, counter)) return 0;
            int mode = processorProtectionMode();
            long policy = policyVersion(mode);
            if (policy < 0 || policy != receiptPolicy || !fetchReceipt.covers(test.address.getOffset(), test.encoding.length) ||
                    !fetchReceipt.covers(branch.address.getOffset(), branch.encoding.length)) return 0;
            if (policy != 0 && callbacks.model.mpuGrant(this, readAddress, 1,
                    RunP1MEMachine.Model.CpuAccess.READ, mode, null) <= 0) return 0;

            instructionVisits = Math.addExact(instructionVisits, retired);
            idleInstructions = Math.addExact(idleInstructions, retired);
            return retired;
        }

        /** Execute just the next guest, including the live data read and all retirement callbacks. */
        boolean stepPollBoundary(PolledBitLoop loop, long lastPc) {
            if (!batchDispatchAllowed()) return false;
            Address counter = getCounter();
            Plan plan;
            if (lastPc == loop.branchPc() && counter.equals(loop.test.address)) plan = loop.test;
            else if (lastPc == loop.testPc() && counter.equals(loop.branch.address)) plan = loop.branch;
            else return false;
            Decoder activeDecoder = (Decoder) decoder;
            if (!plan.isAt(counter, getContext()) || !activeDecoder.memory.matches(plan, counter))
                return false;
            assertCompletedInstruction();
            long fetchEnd = authorizeFetch(counter.getOffset(), processorProtectionMode(), null);
            activeDecoder.activate(plan);
            activeDecoder.verified = true;
            executeOrdinaryPlan(activeDecoder, plan, counter, fetchEnd);
            return true;
        }

        private boolean overlapsRegister(Varnode var, Register register) {
            if (var == null || !var.isRegister() || register == null ||
                    register == Register.NO_CONTEXT ||
                    var.getAddress().getAddressSpace() != register.getAddressSpace()) return false;
            long start = var.getOffset();
            long registerStart = register.getOffset();
            return start < registerStart + register.getNumBytes()
                && registerStart < start + var.getSize();
        }

        private boolean suspended() {
            return isSuspended() || P1MEJitMachine.this.suspended;
        }

        private boolean codeReady(long pc, int width) {
            if (fetchMpu.covers(pc, width)) return true;
            try {
                return callbacks.model.mpuGrant(this, pc, width, RunP1MEMachine.Model.CpuAccess.EXECUTE,
                    templateProtectionMode, fetchMpu) > 0;
            }
            catch (RunP1MEMachine.MachineFault fault) {
                // The ordinary fetch reports undefined processor permission state at this PC.
                return false;
            }
        }

        private boolean admitDataWindow(long address, int size, boolean store, boolean stack) {
            if ((address >>> 32) != 0 || (address & (size - 1)) != 0) return false;
            int kind = store ? 1 : 0;
            RunP1MEMachine.RegionDef region;
            try {
                region = callbacks.model.templateData(this, address, size, store, templateProtectionMode,
                    store ? writeMpu : readMpu, transfer);
            }
            catch (RunP1MEMachine.MachineFault fault) {
                // The ordinary bus path reports the fault after executing its p-code prefix.
                return false;
            }
            if (region == null || (stack && !region.templateRam) || !MachineStatePiece.slabRegion(region)) return false;
            MachineState memory = ((Decoder) decoder).memory;
            var storage = memory.backingPiece.memory;
            if (storage == null || storage.slab == null) return false;
            BoundPage primary = memory.initializedMemoryPage(address, size);
            if (primary == null || primary.data != storage.slab || (store && memory.trackedCodePage(address))) return false;
            long lo = transfer.start, hi = transfer.end, delta = 0;
            BoundPage mirror = null;
            var alias = region.templateMirror;
            if (store && alias != null) {
                delta = alias.start - region.start;
                long target = address + delta;
                if (!MachineStatePiece.slabRegion(alias) || !alias.contains(target, size) || memory.trackedCodePage(target)) return false;
                mirror = memory.initializedMemoryPage(target, size);
                if (mirror == null || mirror.data != storage.slab) return false;
            }
            var initialized = storage.backing().getInitialized();
            for (int bank = 0; bank < (mirror == null ? 1 : 2); bank++) {
                long shift = bank == 0 ? 0 : delta;
                var view = bank == 0 ? region : alias;
                var span = initialized.spanContaining(address + shift);
                if (span == null) return false;
                lo = Math.max(lo, Math.max(view.start, span.min()) - shift);
                long end = Long.compareUnsigned(span.max(), view.end_exclusive - 1) >= 0 ? view.end_exclusive : span.max() + 1;
                hi = Math.min(hi, end - shift);
            }
            DataWindow window = dataWindows[kind * WINDOWS_PER_KIND +
                (dataNext[kind]++ & (WINDOWS_PER_KIND - 1))];
            window.start = lo;
            window.end = hi;
            if (store && "global_ram".equals(region.name)) hasGlobalStore = true;
            window.probe = address;
            window.mirrorDelta = delta;
            window.primary = primary;
            window.mirror = mirror;
            window.region = region;
            apertureDirty = true;
            return true;
        }

        private boolean stableTemplateContext(Plan plan, Address next) {
            return contextreg == Register.NO_CONTEXT || !plan.contextCommits && stableFlow(plan.context, next);
        }

        private boolean templateRegister(Varnode var, long word, boolean write, boolean flags,
                boolean store) {
            if (var.getOffset() - word + var.getSize() > Integer.BYTES) return false;
            if (Plan.gpr(var)) return true;
            if (pswRegister != null && word == pswRegister.register.getOffset()) return !write || flags;
            if (!write && zeroRegister != null && word == zeroRegister.getOffset()) return true;
            return store && ((linkValid != null && word == linkValid.getOffset()) ||
                (!write && linkAddress != null && word == linkAddress.getOffset()));
        }

        private Operand templateOperand(Varnode var, boolean write, boolean flags, boolean store,
                boolean allowPc) {
            return templateOperand(var, write, flags, store, allowPc, false);
        }

        private Operand templateOperand(Varnode var, boolean write, boolean flags, boolean store,
                boolean allowPc, boolean systemCopy) {
            int size = var.getSize();
            if (size < 1 || size > Long.BYTES) return null;
            if (!write && var.isConstant()) {
                return new Operand(null, 0, size, var.getOffset() & Utils.calc_mask(size));
            }
            int offset = (int) var.getOffset() & PAGE_MASK;
            if (var.isUnique()) {
                BoundPage page = retirementState.numberPage(var);
                return templatePageOperand(page, offset, size);
            }
            if (!var.isRegister() || var.getAddress().getAddressSpace() != retirementState.registerAddressSpace
                    || overlapsRegister(var, contextreg)) return null;
            boolean pcLane = overlapsRegister(var, pc);
            if (pcLane && (!allowPc || !isFullPc(var))) return null;
            long word = pcLane ? var.getOffset() : var.getOffset() & ~3L;
            if (!pcLane && !systemCopy && !templateRegister(var, word, write, flags, store)) return null;
            BoundPage page = retirementState.initializedLocalPage(
                retirementState.registerAddressSpace, word, Integer.BYTES, true);
            return templatePageOperand(page, offset, size);
        }

        private Operand templatePageOperand(BoundPage page, int offset, int size) {
            if (page == null || page.localSlot < 0) return null;
            return new Operand(page, page.index(offset), size, 0);
        }

        private boolean isFullPc(Varnode var) {
            return var != null && var.isRegister() && pc.getNumBytes() == Integer.BYTES &&
                var.getSize() == Integer.BYTES && var.getAddress().equals(pc.getAddress());
        }

        private boolean linksPc(List<PcodeOp> raw, String mnemonic) {
            if (raw.size() < 2) return false;
            PcodeOp update = raw.get(raw.size() - 2);
            PcodeOp jump = raw.getLast();
            if (!isFullPc(update.getOutput()) || jump.getNumInputs() != 1 || jump.getOutput() != null)
                return false;
            Varnode target = jump.getInput(0);
            boolean copy = update.getOpcode() == PcodeOp.COPY && update.getNumInputs() == 1;
            if (copy && ((jump.getOpcode() == PcodeOp.CALL && "jarl".equals(mnemonic)) ||
                    (jump.getOpcode() == PcodeOp.BRANCH && "jr".equals(mnemonic)))) {
                Varnode value = update.getInput(0);
                return target.getAddress().getAddressSpace() == byteCounterSpace &&
                    value.isConstant() && value.getSize() == Integer.BYTES &&
                    Integer.toUnsignedLong((int) value.getOffset()) == target.getOffset();
            }
            return isIndirect(jump.getOpcode()) &&
                (isFullPc(target) || (copy && update.getInput(0).equals(target)));
        }

        private static boolean isDirectBranch(int opcode) {
            return opcode == PcodeOp.BRANCH || opcode == PcodeOp.CBRANCH || opcode == PcodeOp.CALL;
        }

        private static long stackConstant(List<PcodeOp> raw, Varnode value, int before) {
            if (value.getSize() != Integer.BYTES) return -1;
            if (value.isConstant()) return Integer.toUnsignedLong((int) value.getOffset());
            for (int i = before - 1; i >= 0; i--) {
                PcodeOp op = raw.get(i);
                Varnode out = op.getOutput();
                if (out == null || !out.intersects(value)) continue;
                int opcode = op.getOpcode();
                if (!out.equals(value) || (opcode != PcodeOp.COPY && opcode != PcodeOp.INT_LEFT) ||
                        op.getNumInputs() != (opcode == PcodeOp.COPY ? 1 : 2)) return -1;
                Varnode left = op.getInput(0);
                if (!left.isConstant() || left.getSize() != Integer.BYTES) return -1;
                if (opcode == PcodeOp.COPY) return Integer.toUnsignedLong((int) left.getOffset());
                if (op.getInput(1).isConstant()) {
                    int shift = op.getInput(1).getSize();
                    long amount = op.getInput(1).getOffset() & Utils.calc_mask(shift);
                    return Integer.toUnsignedLong(JitCompiledPassage.intLeft((int) left.getOffset(), amount));
                }
                return -1;
            }
            return -1;
        }

        // Recognize stack transfers whose addresses can all be checked before the first word commits.
        // The C guest checks the address independently, from the actual p-code value.
        private long stackWordAddress(List<PcodeOp> raw, Varnode value, int before) {
            if (value.getSize() != Integer.BYTES) return -1;
            int offset = 0;
            long aligned = 0;
            for (int i = before - 1; i >= 0; i--) {
                PcodeOp op = raw.get(i);
                Varnode out = op.getOutput();
                if (out == null || !out.intersects(value)) continue;
                int opcode = op.getOpcode();
                if (!out.equals(value) || (opcode != PcodeOp.COPY && opcode != PcodeOp.INT_ADD &&
                        opcode != PcodeOp.INT_SUB && opcode != PcodeOp.INT_AND) ||
                        op.getNumInputs() != (opcode == PcodeOp.COPY ? 1 : 2)) return -1;
                Varnode base = op.getInput(0);
                if (opcode != PcodeOp.COPY) {
                    Varnode other = op.getInput(1);
                    long constant = stackConstant(raw, other, i);
                    if (constant < 0 && opcode != PcodeOp.INT_SUB) {
                        constant = stackConstant(raw, base, i);
                        base = other;
                    }
                    if (constant < 0 || (constant & 3) != 0) return -1;
                    if (opcode == PcodeOp.INT_AND) {
                        if (constant != 0xffff_fffcL) return -1;
                        aligned = 1L << 32;
                    }
                    else offset += opcode == PcodeOp.INT_ADD ? (int) constant : -(int) constant;
                }
                if (base.getSize() != Integer.BYTES) return -1;
                value = base;
            }
            return value.equals(stackInput) ? aligned | Integer.toUnsignedLong(offset) : -1;
        }

        private boolean isStackTransfer(List<PcodeOp> raw, int words, boolean store) {
            if (stackInput == null || words > MAX_STACK_WORDS) return false;
            int first = 0, mask = -1, stride = 0, word = 0;
            for (int i = 0; i < raw.size(); i++) {
                PcodeOp op = raw.get(i);
                if (op.getOpcode() != PcodeOp.LOAD && op.getOpcode() != PcodeOp.STORE) continue;
                if ((op.getOpcode() == PcodeOp.STORE) != store ||
                        op.getNumInputs() != (store ? 3 : 2) ||
                        (op.getOutput() == null) != store ||
                        (store ? op.getInput(2) : op.getOutput()).getSize() != Integer.BYTES) return false;
                long address = stackWordAddress(raw, op.getInput(1), i);
                if (address < 0) return false;
                int offset = (int) address;
                int wordMask = address >>> 32 == 0 ? -1 : ~3;
                if (word == 0) {
                    first = offset;
                    mask = wordMask;
                }
                else {
                    if (mask != wordMask) return false;
                    if (word == 1) {
                        stride = offset - first;
                        if (stride != Integer.BYTES && stride != -Integer.BYTES) return false;
                    }
                    else if (offset != first + word * stride) return false;
                }
                word++;
            }
            return true;
        }

        private Node templateNode(Plan plan, int remainingOps) {
            var observation = plan.observation;
            if (observation == null) {
                return null;
            }
            if (observation.readsIcctrl || plan.repeatedSelfBranch ||
                    plan.instruction.getDelaySlotDepth() != 0) return null;
            List<PcodeOp> raw = plan.program.getCode();
            if (raw.size() > remainingOps) return null;
            // PREPARE's only extra model action is the peripheral-file experiment's stack fill.
            var model = callbacks.model;
            boolean stackBatch = !model.peripheralFile && !model.inputDerivedTableIndices;
            boolean prepare = stackBatch && "prepare".equals(observation.mnemonic);
            if (!observation.ordinaryRetirement && !prepare &&
                    !("jarl".equals(observation.mnemonic) && callbacks.model.boundedEntries.isEmpty())) {
                SyncOp sync = templateSync(observation.mnemonic, raw);
                if (sync == null) return null;
                Address next = plan.address.addWrap(plan.encoding.length);
                if (!stableTemplateContext(plan, next)) return null;
                plan.templateSync = sync;
                return new Node(plan, new RegionOp[0], -1, next, null, false, false, false, false);
            }
            String mnemonic = observation.mnemonic.toLowerCase(java.util.Locale.ROOT);
            if ("ldsr".equals(mnemonic) || "di".equals(mnemonic) || "ei".equals(mnemonic)) {
                Node control = templateControl(plan, raw, mnemonic);
                if (control != null) return control;
            }
            boolean flags = RunP1MEMachine.Callbacks.FLAG_ARITHMETIC.contains(mnemonic)
                || mnemonic.equals("cmp") || mnemonic.equals("tst") || mnemonic.equals("tst1")
                || mnemonic.equals("andi") || mnemonic.equals("ori") || mnemonic.equals("xori");
            int bus = -1, words = 0;
            boolean store = false;
            boolean relative = false;
            for (int i = 0; i < raw.size(); i++) {
                PcodeOp op = raw.get(i);
                int opcode = op.getOpcode();
                if ((opcode == PcodeOp.BRANCH || opcode == PcodeOp.CBRANCH) &&
                        op.getNumInputs() > 0 && op.getInput(0).isConstant()) relative = true;
                if (opcode != PcodeOp.LOAD && opcode != PcodeOp.STORE) continue;
                words++;
                bus = i;
                store = opcode == PcodeOp.STORE;
            }
            if (relative && (bus >= 0 || plan.indirect)) return null;
            boolean stack = words > 1 || (words != 0 && (prepare || "dispose".equals(mnemonic)));
            if (stack && (!stackBatch || !isStackTransfer(raw, words, store))) return null;
            Node ordinary = ordinaryTemplateNode(plan, raw, mnemonic, flags, bus, store, relative, stack);
            if (ordinary != null || !relative || !observation.ordinaryRetirement) return ordinary;
            return guardedArithmeticNode(plan, raw);
        }

        private SyncOp templateSync(String mnemonic, List<PcodeOp> raw) {
            SyncOp sync = switch (mnemonic) {
                case "syncm" -> SyncOp.SYNCM;
                case "syncp" -> SyncOp.SYNCP;
                case "synci" -> SyncOp.SYNCI;
                default -> null;
            };
            if (sync == null || raw.size() != 1) return null;
            PcodeOp op = raw.getFirst();
            // The exact P1M-E __synchronize userop is empty. Don't erase any
            // other effects (notably SYNCE's FP acknowledgement).
            return emptyUserop(op, "__synchronize") ? sync : null;
        }

        private boolean emptyUserop(PcodeOp op, String name) {
            return op.getOpcode() == PcodeOp.CALLOTHER && op.getNumInputs() == 1 &&
                op.getOutput() == null && op.getInput(0).isConstant() &&
                name.equals(language.getUserDefinedOpName((int) op.getInput(0).getOffset()));
        }

        private static final Set<String> COPY_CONTROLS = Set.of("ASID", "MPM", "MCTL", "RBASE", "EBASE", "INTBP");
        private static final Set<String> FP_CONTROLS = Set.of("PSW", "PMR", "FPIPR", "INTCFG");

        private static boolean descriptorControl(String name) {
            if (name.length() < 5 || name.length() > 6 ||
                    !(name.startsWith("MPLA") || name.startsWith("MPUA") || name.startsWith("MPAT")))
                return false;
            char first = name.charAt(4);
            if (name.length() == 5) return first >= '0' && first <= '9';
            char second = name.charAt(5);
            return first == '1' && second >= '0' && second <= '5';
        }

        private static boolean fullRegister(Varnode var, Register register) {
            return var != null && register != null && register.getNumBytes() == Integer.BYTES &&
                var.getSize() == Integer.BYTES && var.getAddress().equals(register.getAddress());
        }

        private static boolean controlLane(Varnode var, Register register) {
            if (var == null || register == null || register.getNumBytes() != Integer.BYTES ||
                    var.getAddress().getAddressSpace() != register.getAddressSpace()) return false;
            long displacement = var.getOffset() - register.getOffset();
            return displacement >= 0 && displacement <= Integer.BYTES - var.getSize();
        }

        private Node templateControl(Plan plan, List<PcodeOp> raw, String mnemonic) {
            if (raw.isEmpty() || !language.getLanguageID().toString().equals("v850e3:LE:32:default")) return null;
            boolean ldsr = "ldsr".equals(mnemonic);
            boolean ei = "ei".equals(mnemonic);
            Register written = ldsr ? plan.instruction.getRegister(1) : language.getRegister("PSW");
            if (written == null) return null;
            String name = written.getName();
            boolean fp = ei || (ldsr && FP_CONTROLS.contains(name));
            if (ldsr) {
                // Admit only an exact decoded transfer, not an MPU indexed view,
                // ICCTRL commands, or the ISPR-specific protected-write callback.
                if (!fp && (!(COPY_CONTROLS.contains(name) || descriptorControl(name)) || raw.size() != 1))
                    return null;
                PcodeOp copy = raw.getFirst();
                if (copy.getOpcode() != PcodeOp.COPY || copy.getNumInputs() != 1 ||
                        !fullRegister(copy.getOutput(), written)) return null;
                Varnode in = copy.getInput(0);
                if (in.getSize() != Integer.BYTES ||
                        !(Plan.gpr(in) || (in.isConstant() && in.getOffset() == 0))) return null;
            }
            else if (!emptyUserop(raw.getLast(), ei ? "__enable_irq" : "__disable_irq")) return null;

            int end = ldsr ? raw.size() : raw.size() - 1;
            List<RegionOp> path = new ArrayList<>(end);
            Register fpStatus = fp && icsrRegister != null ? icsrRegister.register : null;
            boolean irqOnly = name.equals("PSW") || name.equals("PMR");
            boolean sawWrite = false, sawGuard = false;
            for (int i = 0; i < end; i++) {
                PcodeOp op = raw.get(i);
                int opcode = op.getOpcode(), inputs = op.getNumInputs();
                Varnode output = op.getOutput();
                if (opcode == PcodeOp.CBRANCH) {
                    // The non-exception FP path jumps past the rest of the packet.
                    // If the live condition disagrees, commit nothing; Ghidra
                    // must run the pending-FPI/ISPR/PMR path in full.
                    if (!fp || output != null || inputs != 2 || !op.getInput(0).isConstant()) return null;
                    long target = i + (long) (int) op.getInput(0).getOffset();
                    if (target < end || target > raw.size()) return null;
                    Operand condition = templateOperand(op.getInput(1), false, false, false, false);
                    if (condition == null) return null;
                    path.add(new RegionOp(opcode, null, condition, null, -1, GUARD_TAKEN));
                    sawGuard = true;
                    break;
                }
                if (!templateArithmetic(opcode, inputs, output)) return null;
                boolean mainWrite = controlLane(output, written);
                boolean systemWrite = mainWrite || controlLane(output, fpStatus);
                if (!systemWrite && !output.isUnique()) return null;
                sawWrite |= mainWrite;
                Operand out = templateOperand(output, true, false, false, false, systemWrite);
                Operand left = templateOperand(op.getInput(0), false, false, false, false, true);
                Operand right = inputs == 1 ? null
                    : templateOperand(op.getInput(1), false, false, false, false, true);
                if (out == null || left == null || (inputs == 2 && right == null)) return null;
                long invariant = 0;
                if (irqOnly && mainWrite && name.equals("PSW")) {
                    int shift = (int) (output.getOffset() - written.getOffset()) * Byte.SIZE;
                    invariant = (0x40000000L >>> shift) & Utils.calc_mask(output.getSize());
                } else if (irqOnly && controlLane(output, fpStatus) &&
                        output.getOffset() == fpStatus.getOffset()) invariant = 1L;
                path.add(new RegionOp(opcode, out, left, right, -1, invariant));
            }
            Address next = plan.address.addWrap(plan.encoding.length);
            if (!sawWrite || fp != sawGuard || !stableTemplateContext(plan, next)) return null;
            plan.templateControl = true;
            plan.irqOnly = irqOnly;
            return new Node(plan, path.toArray(RegionOp[]::new), -1, next, null, false, false, true, false);
        }

        private Node ordinaryTemplateNode(Plan plan, List<PcodeOp> raw, String mnemonic,
                boolean flags, int bus, boolean store, boolean relative, boolean stack) {
            boolean linkPc = (bus < 0 || stack) && !relative && linksPc(raw, mnemonic);
            if (plan.indirect && ((bus >= 0 && !stack) || (plan.predictedTarget != null &&
                    plan.predictedTarget.getAddressSpace() != byteCounterSpace))) return null;
            if (plan.indirect && plan.predictedTarget == null) {
                return null;
            }
            boolean systemCopy = raw.size() == 1 && plainSystemCopy(raw.getFirst(), mnemonic);

            Address next = plan.address.addWrap(plan.encoding.length);
            Address taken = null;
            RegionOp[] ops = new RegionOp[raw.size()];
            for (int i = 0; i < ops.length; i++) {
                PcodeOp op = raw.get(i);
                int opcode = op.getOpcode(), inputs = op.getNumInputs(), first = 0;
                int localTarget = -1;
                Varnode output = op.getOutput();
                if (isDirectBranch(opcode)) {
                    if (output != null || inputs != (opcode == PcodeOp.CBRANCH ? 2 : 1))
                        return null;
                    Address target = op.getInput(0).getAddress();
                    if (relative) {
                        // In a pure packet, an edge to code.size() is ordinary fall-through.
                        long delta = target.getOffset();
                        if (opcode == PcodeOp.CALL || !target.isConstantAddress() ||
                                delta <= 0 || delta > ops.length - i) return null;
                        localTarget = i + (int) delta;
                    }
                    else {
                        if (i != ops.length - 1 || target.getAddressSpace() != byteCounterSpace)
                            return null;
                        if (opcode == PcodeOp.CBRANCH) taken = target;
                        else next = target;
                    }
                    first = 1;
                }
                else if (isIndirect(opcode)) {
                    if (!plan.indirect || i != ops.length - 1 || inputs != 1 || output != null ||
                            op.getInput(0).getSize() != Integer.BYTES) return null;
                    next = plan.predictedTarget;
                }
                else if (opcode == PcodeOp.LOAD || opcode == PcodeOp.STORE) {
                    if (inputs != (store ? 3 : 2) || (output == null) != store) return null;
                    Varnode space = op.getInput(0);
                    int width = (store ? op.getInput(2) : output).getSize();
                    if (!space.isConstant() || space.getOffset() != byteCounterSpace.getSpaceID() ||
                            op.getInput(1).getSize() != Integer.BYTES ||
                            (width != 1 && width != 2 && width != 4 && width != 8)) return null;
                    first = 1;
                }
                else if (!templateArithmetic(opcode, inputs, output)) return null;

                Operand out = output == null ? null : templateOperand(output, true, flags, store,
                    linkPc && i == ops.length - 2, systemCopy && "ldsr".equals(mnemonic));
                Operand left = first == inputs ? null : templateOperand(op.getInput(first),
                    false, flags, store, linkPc && plan.indirect && i == ops.length - 1,
                    systemCopy && "stsr".equals(mnemonic));
                Operand right = first + 1 >= inputs ? null
                    : templateOperand(op.getInput(first + 1), false, flags, store, false);
                if ((output != null && out == null) || (first < inputs && left == null) ||
                        (first + 1 < inputs && right == null)) return null;
                ops[i] = new RegionOp(opcode, out, left, right, localTarget, 0);
            }
            if (!stableTemplateContext(plan, next) ||
                    (taken != null && !stableTemplateContext(plan, taken))) return null;
            return new Node(plan, ops, bus, next, taken, plan.indirect, relative, false, stack);
        }

        private boolean plainSystemCopy(PcodeOp op, String mnemonic) {
            if (op.getOpcode() != PcodeOp.COPY || op.getNumInputs() != 1 ||
                    op.getOutput() == null || op.getOutput().getSize() != Integer.BYTES ||
                    op.getInput(0).getSize() != Integer.BYTES) return false;
            if ("stsr".equals(mnemonic)) {
                // The observation already excluded scripted ICCTRL reads. A pure copy has
                // no userop, privilege side effect, flow change, or system register write.
                return op.getInput(0).isRegister() && Plan.gpr(op.getOutput());
            }
            if (!"ldsr".equals(mnemonic) || !Plan.gpr(op.getInput(0))) return false;
            // Only saved exception state, not live PSW, MPU or interrupt controls. The
            // remaining LDSR constructors may call userops or change scheduler inputs.
            for (String name : SAVED_EXCEPTION_REGISTERS) {
                Register register = language.getRegister(name);
                if (register != null && op.getOutput().getAddress().equals(register.getAddress()))
                    return true;
            }
            return false;
        }

        private static final String[] SAVED_EXCEPTION_REGISTERS = {"EIPC", "EIPSW", "FEPC", "FEPSW"};

        private Node guardedArithmeticNode(Plan plan, List<PcodeOp> raw) {
            // Specialize a single path, not an entire internal CFG. Only reached
            // operands need initialized bindings: a different path exits before
            // doing any state write, and runs the original instruction normally.
            List<RegionOp> path = new ArrayList<>(raw.size());
            boolean hasGuard = false;
            for (int i = 0; i < raw.size();) {
                PcodeOp op = raw.get(i);
                int opcode = op.getOpcode(), inputs = op.getNumInputs();
                Varnode output = op.getOutput();
                if (opcode == PcodeOp.BRANCH || opcode == PcodeOp.CBRANCH) {
                    if (output != null || inputs != (opcode == PcodeOp.CBRANCH ? 2 : 1) ||
                            !op.getInput(0).isConstant()) return null;
                    long target = i + (long) (int) op.getInput(0).getOffset();
                    if (target < 0 || target > raw.size()) return null;
                    if (opcode == PcodeOp.BRANCH) {
                        if (target <= i) return null;
                        i = (int) target;
                        continue;
                    }
                    Operand condition = templateOperand(op.getInput(1), false, false, false, false);
                    if (condition == null) return null;
                    path.add(new RegionOp(opcode, null, condition, null, -1, 0));
                    hasGuard = true;
                }
                else {
                    if (isDivision(opcode)) {
                        if (output == null || inputs != 2 ||
                                op.getInput(0).getSize() != output.getSize() ||
                                op.getInput(1).getSize() != output.getSize()) return null;
                    }
                    else if (!templateArithmetic(opcode, inputs, output)) return null;
                    Operand out = templateOperand(output, true, true, false, false);
                    Operand left = templateOperand(op.getInput(0), false, false, false, false);
                    Operand right = inputs == 1 ? null
                        : templateOperand(op.getInput(1), false, false, false, false);
                    if (out == null || left == null || (inputs == 2 && right == null)) return null;
                    long preserve = 0;
                    Register psw = pswRegister == null ? null : pswRegister.register;
                    if (overlapsRegister(output, psw)) {
                        int offset = (int) (output.getOffset() - psw.getOffset());
                        if (psw.getNumBytes() != Integer.BYTES ||
                                offset < 0 || offset + out.size > Integer.BYTES) return null;
                        int shift = laneShift(Integer.BYTES, offset, out.size, bigEndian);
                        // Only SAT/CY/OV/S/Z may change; this does not depend on
                        // the mnemonic or trust that a PSW write only sets flags.
                        preserve = Utils.calc_mask(out.size) & ~(0x1fL >>> shift);
                    }
                    path.add(new RegionOp(opcode, out, left, right, -1, preserve));
                }
                i++;
            }
            Address next = plan.address.addWrap(plan.encoding.length);
            if (!hasGuard || !stableTemplateContext(plan, next)) return null;
            return new Node(plan, path.toArray(RegionOp[]::new), -1, next, null,
                false, false, true, false);
        }

        private static boolean templateArithmetic(int opcode, int inputs, Varnode output) {
            if (output == null || !(opcode == PcodeOp.COPY || opcode == PcodeOp.SUBPIECE ||
                    opcode == PcodeOp.PIECE || (opcode >= PcodeOp.INT_EQUAL && opcode <= PcodeOp.INT_MULT) ||
                    (opcode >= PcodeOp.BOOL_NEGATE && opcode <= PcodeOp.BOOL_OR))) return false;
            OpBehavior behavior = OpBehaviorFactory.getOpBehavior(opcode);
            return inputs == 1 && behavior instanceof UnaryOpBehavior || inputs == 2 && behavior instanceof BinaryOpBehavior;
        }

        private int batchTemplates(Decoder activeDecoder, Plan first, RegisterValue context,
                long fetchEnd, int limit, StopIndex stops) {
            Site site = first.site;
            if (site == null && (instructionVisits < first.templateRetryAt ||
                    ++first.templateHits < TEMPLATE_HITS)) return 0;
            if (fetchEnd == 0 || !batchDispatchAllowed() || (contextRetirement != null && context == null)) return 0;
            var model = callbacks.model;
            if (NativeSite.CACHE == null || !model.trace.canDeferNativeBus()) return 0;
            if (site != null && site.localGeneration != retirementState.generation) {
                site.invalidate();
                site = null;
            }
            if (site == null) {
                var region = model.region(first.address.getOffset(), first.encoding.length);
                if (first.encoding.length <= 0 || region == null || !region.executable || "dataflash".equals(region.name) ||
                        region.end_exclusive - region.start > NativeGroup.MAX_FETCH_BANK) return 0;
                first.templateHits = 0;
                Node node = templateNode(first, MAX_INSTRUCTION_OPS);
                if (node == null || (site = Site.bind(retirementState, node, bigEndian, region,
                        contextreg == Register.NO_CONTEXT || stableFlow(context, first.address))) == null) {
                    first.templateRetryAt = instructionVisits + (2048L << Math.min(first.templateMisses++, 12));
                    return 0;
                }
                first.site = site;
                first.templateMisses = 0;
                first.templateRetryAt = 0;
            }
            return runNativeSites(activeDecoder, site, context, Math.min(limit, NATIVE_LIMIT), stops);
        }

        private int runNativeSites(Decoder activeDecoder, Site site, RegisterValue context,
                int limit, StopIndex stops) {
            MachineStatePiece memory = activeDecoder.memory.backingPiece;
            var trace = callbacks.model.trace;
            if (site.nativeBinding.body.function == null) return 0;
            NativeGroup bank = site.group != null ? site.group : nativeBanks.computeIfAbsent(site.fetchRegion, NativeGroup::new);
            bank.refresh(memory, site.localGeneration, context, trace.recordsInstructionMetadata() ? trace.executed : null);
            bank.stops(stops);
            int entry = bank.entry(site);
            if (entry < 0 || suspended() || !codeReady(site.pc, site.width)) return 0;
            readMpu.clear();
            writeMpu.clear();
            beginDataWindows(memory);
            nativeCtl[CTL_RECENT_START] = trace.bindNativeHistory(nativeCtl, CTL_RECENT);
            nativeCtl[CTL_EXIT] = nativeCtl[CTL_PARTIAL_OP] = 0;
            int retired = nativeRun(bank, site, entry, 0, limit);
            if (nativeCtl[CTL_PARTIAL_OP] != 0) {
                int nextOp = (int) nativeCtl[CTL_PARTIAL_OP];
                nativeCtl[CTL_PARTIAL_OP] = 0;
                Site partial = bank.members[(int) nativeCtl[CTL_PARTIAL_SITE]];
                if (retired != 0) retireNativeSites(retired);
                var plan = partial.plan;
                // The branch's PC-producing p-code may already have committed.
                List<PcodeOp> ops = plan.program.getCode();
                boolean wrotePc = false;
                for (int i = 0; i < nextOp - 1; i++) wrotePc |= isFullPc(ops.get(i).getOutput());
                if (wrotePc) setCounter(plan.address);
                else retireCounter(plan.address);
                activeDecoder.activate(plan);
                instruction = plan.instruction;
                throw new SuspendedPcodeExecutionException(materializeFrame(plan, nextOp), null);
            }
            if (retired == 0) return 0;
            Site last = bank.members[(int) nativeCtl[0]];
            int edge = (int) nativeCtl[1];
            Address next = edge == 0 ? last.nextAddress : edge == 1 ? last.takenAddress : bank.members[edge - 3].plan.address;
            int reason = (int) nativeCtl[CTL_EXIT];
            retireCounter(next);
            if (contextRetirement != null && (contextRetirement.size > Long.BYTES ||
                    !contextRetirement.write(bank.contextBits))) writeContext(context);
            activeDecoder.activate(last.plan);
            activeDecoder.branched(next);
            retireNativeSites(retired);
            if ((reason == EXIT_BUS || reason == EXIT_INDIRECT) && !suspended()) {
                // A miss precedes the end of this admitted span and committed none of
                // its instruction. Execute it through the normal bus and fault callbacks.
                activeDecoder.decodeInstruction(next, context);
                executeOrdinaryPlan(activeDecoder, activeDecoder.current, next, fetchMpu.end);
                return retired + 1;
            }
            return retired;
        }

        private void retireNativeSites(int retired) {
            instructionVisits += retired;
            compiledInstructions += retired;
            templateInstructions += retired;
            callbacks.model.retireNativeBatch(retired);
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
            if (name == "ICSR") return icsrRegister;
            if (name == "PMR") return pmrRegister;
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
            stepOrBatch(0, StopIndex.EMPTY);
        }

        /** Zero is ordinary retirement; a negative count carries one staged bus miss. */
        void stepOrBatch(int maxInstructions, StopIndex stops) {
            assertCompletedInstruction();
            Address fetchStart = getCounter();
            long fetchEnd;
            if (maxInstructions >= 2) {
                fetchMpu.clear();
                // A changed control write terminates the batch before the next
                // instruction. Fetch and data proofs never cross a mode change.
                templateProtectionMode = processorProtectionMode();
                fetchEnd = authorizeFetch(fetchStart.getOffset(), templateProtectionMode, fetchMpu);
            }
            else {
                fetchEnd = authorizeFetch(fetchStart.getOffset(), processorProtectionMode(), null);
            }
            Decoder activeDecoder = (Decoder) decoder;
            RegisterValue context = getContext();
            activeDecoder.decodeInstruction(fetchStart, context);
            Plan plan = activeDecoder.current;
            if (maxInstructions >= 2 && activeDecoder.verified) {
                int retired = batchTemplates(activeDecoder, plan, context, fetchEnd,
                    maxInstructions, stops);
                if (retired != 0) return;
            }
            executeOrdinaryPlan(activeDecoder, plan, fetchStart, fetchEnd);
        }

        private void executeOrdinaryPlan(Decoder activeDecoder, Plan plan, Address fetchStart, long fetchEnd) {
            beginOrdinary(activeDecoder, plan.instruction, fetchStart, fetchEnd);
            instructionVisits++;
            long generation = retirementState.generation;
            if (plan.bindingGeneration != generation) {
                plan.bindingGeneration = generation;
                plan.entry = null;
                plan.busPrefix = null;
                plan.scalar = null;
                plan.scalarAttempts = 0;
                plan.scalarBus = false;
                plan.promotionStart = instructionVisits;
                if (plan.translation != null) plan.untilCompile = 1;
            }
            executeFallback(plan, suspended());
            if (plan.indirect) plan.predictedTarget = getCounter();
            callbacks.afterExecuteInstruction(this, plan.instruction);
        }

        private void executeFallback(Plan plan, boolean suspended) {
            EntryPoint entry = plan.entry;
            if (entry == null && modifier == null && !suspended &&
                    plan.untilCompile > 0 && --plan.untilCompile == 0) {
                entry = prepareEntry(plan);
            }
            if (suspended || (entry != null && plan.busOpIndex >= 0 && !accessBreakpoints.isEmpty())) {
                entry = null;
            }
            if (entry == null) {
                // The first execution can define unique bytes needed by the binding.
                if (modifier == null && !suspended && plan.scalar == null && plan.scalarAttempts < 2) {
                    plan.scalarAttempts++;
                    plan.scalar = bindScalar(plan);
                }
                if (plan.scalar != null && (!plan.scalarBus || accessBreakpoints.isEmpty())) {
                    runScalar(plan, plan.scalar);
                }
                else {
                    frame = beginPlan(plan);
                    finishPlan(plan);
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
        }

        private void beginOrdinary(Decoder activeDecoder, PseudoInstruction decoded,
                Address fetchStart, long fetchEnd) {
            instruction = decoded;
            preExecuteInstruction();
            // A legacy state modifier invalidates both permission and decoder byte proofs.
            verifiedFetch = modifier == null && activeDecoder.verified;
            try {
                callbacks.beforeExecuteInstruction(this, instruction, fetchStart,
                    modifier == null ? fetchEnd : 0);
            }
            finally {
                verifiedFetch = false;
            }
        }

        void release() {
            ((LocalExecutor) executor).boundOperands.clear();
            codeCache.clear();
            ((Decoder) decoder).release();
            ((MachineState) getState().getLocalState()).release();
            namedRegisters.values().forEach(ProcessorRegister::release);
            registerBindings.values().forEach(ProcessorRegister::release);
            Arrays.fill(registerSlots, null);
            namedRegisters.clear();
            registerBindings.clear();
            protectionModePage = null;
            policyBank = policyBytes = null;
            counterRetirement.release();
            if (contextRetirement != null) contextRetirement.release();
            compiling = pendingBusFrame = null;
            for (DataWindow window : dataWindows) {
                window.primary = window.mirror = null;
                window.region = null;
            }
            nativeBanks.clear();
            callbacks.model.trace.unbindNativeHistory(nativeCtl);
            instruction = null;
            frame = null;
            stableJitContextInput = stableJitContextValue = null;
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

    /**
     * Break the machine's large translation, decode-plan, and state graphs once
     * a scenario report has been written. Ghidra's script host may retain the
     * script instance past execute(), so collection cannot be the disposal API.
     */
    void release() {
        for (PcodeThread<byte[]> thread : threads.values()) {
            ((MachineThread) thread).release();
        }
        threads.clear();
        codeCache.clear();
        ((MachineState) getSharedState()).release();
        clearAllInjects();
        clearAccessBreakpoints();
    }

    @Override
    protected ghidra.pcode.exec.PcodeUseropLibrary<byte[]> createUseropLibrary() {
        return new RunP1MEMachine.Rh850Userops();
    }
}
