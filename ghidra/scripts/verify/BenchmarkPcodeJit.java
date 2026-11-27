//@author OpenAI
//@category Verification
// Benchmark Ghidra's interpreter and JIT on the Camry application-RAM clear loop.
import ghidra.app.script.GhidraScript;
import ghidra.app.util.PseudoDisassembler;
import ghidra.framework.Application;
import ghidra.pcode.emu.PcodeEmulator;
import ghidra.pcode.emu.PcodeThread;
import ghidra.pcode.emu.jit.JitConfiguration;
import ghidra.pcode.emu.jit.JitConfiguration.Opt;
import ghidra.pcode.emu.jit.JitPcodeEmulator;
import ghidra.pcode.emu.jit.JitPcodeThread;
import ghidra.pcode.exec.PcodeExecutorStatePiece.Reason;
import ghidra.pcode.exec.SuspendedPcodeExecutionException;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.lang.Language;
import ghidra.program.model.lang.Register;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.pcode.PcodeOp;

import java.lang.invoke.MethodHandles;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.HexFormat;

public class BenchmarkPcodeJit extends GhidraScript {
    private static final int ENTRY = 0x632b2;
    private static final byte[] LOOP_CODE =
        HexFormat.of().parseHex("3e060070befe010544f221060080befee1f1a1fd7f00");
    private static final long RAM_START = 0xfebe7000L;
    private static final int RAM_SIZE = 0x1000;

    private static final class CountingJitThread extends JitPcodeThread {
        private long compiledInstructions;
        private long limit;
        private boolean reachedLimit;

        CountingJitThread(String name, JitPcodeEmulator machine) {
            super(name, machine);
        }

        @Override
        public void count(int instructions, int trailingOps) {
            super.count(instructions, trailingOps);
            // This hook runs before the block. The validated workload has no
            // intra-instruction p-code branches, so an over-budget block can
            // be rejected and resumed by the interpreter at its first PC.
            if (instructions > limit - compiledInstructions) {
                reachedLimit = true;
                setSuspended(true);
                throw new SuspendedPcodeExecutionException(null, null);
            }
            compiledInstructions += instructions;
        }

        long runCompiled(long count) {
            compiledInstructions = 0;
            limit = count;
            reachedLimit = false;
            try {
                run();
            }
            finally {
                setSuspended(false);
            }
            if (!reachedLimit) {
                throw new IllegalStateException("JIT stopped without reaching its instruction budget");
            }
            return compiledInstructions;
        }
    }

    private static final class CountingJitEmulator extends JitPcodeEmulator {
        CountingJitEmulator(Language language) {
            super(language, new JitConfiguration().enable(Opt.EMIT_COUNTERS), MethodHandles.lookup());
        }

        @Override
        protected CountingJitThread createThread(String name) {
            return new CountingJitThread(name, this);
        }
    }

    private record Snapshot(String pc, String registersSha256, String codeFlashSha256, String ramSha256) {
        String toJson() {
            return """
                {"pc":"%s","registers_sha256":"%s","code_flash_sha256":"%s","ram_sha256":"%s"}"""
                .formatted(pc, registersSha256, codeFlashSha256, ramSha256);
        }
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 5) {
            throw new IllegalArgumentException(
                "usage: BenchmarkPcodeJit.java ENGINE INSTRUCTIONS WARMUP IMAGE_SIZE OUTPUT");
        }
        String engine = args[0];
        long instructions = Long.parseLong(args[1]);
        long warmup = Long.parseLong(args[2]);
        int imageSize = Integer.parseInt(args[3]);
        Path output = Path.of(args[4]).toAbsolutePath();
        if (!(engine.equals("plain") || engine.equals("jit"))) {
            throw new IllegalArgumentException("ENGINE must be plain or jit");
        }
        if (instructions <= 0 || warmup < 0 || imageSize <= 0) {
            throw new IllegalArgumentException("invalid benchmark count or image size");
        }

        byte[] code = readCodeFlash(imageSize);
        verifyWorkload(code);
        Language language = currentProgram.getLanguage();
        PcodeEmulator emulator = engine.equals("jit")
            ? new CountingJitEmulator(language)
            : new PcodeEmulator(language);
        PcodeThread<byte[]> thread = emulator.newThread("benchmark");

        initialize(thread, code);
        long warmupCompiled = 0;
        if (warmup != 0) {
            warmupCompiled = execute(thread, warmup);
            initialize(thread, code);
        }
        Snapshot initial = snapshot(thread, code.length);
        long started = System.nanoTime();
        long compiled = execute(thread, instructions);
        long elapsed = System.nanoTime() - started;
        Snapshot end = snapshot(thread, code.length);

        Files.createDirectories(output.getParent());
        try (var writer = Files.newBufferedWriter(output, StandardCharsets.UTF_8)) {
            writer.write("""
                {
                  "engine": "%s",
                  "ghidra_version": "%s",
                  "instructions": %d,
                  "compiled_instructions": %d,
                  "interpreted_instructions": %d,
                  "warmup_instructions": %d,
                  "warmup_compiled_instructions": %d,
                  "warmup_interpreted_instructions": %d,
                  "wall_nanoseconds": %d,
                  "initial_snapshot": %s,
                  "final_snapshot": %s
                }
                """.formatted(engine, Application.getApplicationVersion(), instructions, compiled,
                    instructions - compiled, warmup, warmupCompiled, warmup - warmupCompiled,
                    elapsed, initial.toJson(), end.toJson()));
        }
        println("BENCHMARK_PCODE_JIT " + output);
    }

    private byte[] readCodeFlash(int imageSize) throws Exception {
        Memory memory = currentProgram.getMemory();
        byte[] code = new byte[imageSize];
        int read = memory.getBytes(toAddr(0), code);
        if (read != imageSize) {
            throw new IllegalStateException(
                "imported program supplied " + read + " of " + imageSize + " image bytes");
        }
        return code;
    }

    private void verifyWorkload(byte[] code) throws Exception {
        int end = ENTRY + LOOP_CODE.length;
        if (code.length < end || !Arrays.equals(code, ENTRY, end, LOOP_CODE, 0, LOOP_CODE.length)) {
            throw new IllegalArgumentException("image does not contain the RAM-clear loop at 0x632b2");
        }
        PseudoDisassembler disassembler = new PseudoDisassembler(currentProgram);
        for (int offset = ENTRY; offset < end;) {
            var instruction = disassembler.disassemble(toAddr(offset));
            if (instruction == null || offset + instruction.getLength() > end) {
                throw new IllegalStateException("cannot decode RAM-clear loop at " + toAddr(offset));
            }
            for (PcodeOp op : instruction.getPcode()) {
                if ((op.getOpcode() == PcodeOp.BRANCH || op.getOpcode() == PcodeOp.CBRANCH)
                    && op.getInput(0).isConstant()) {
                    throw new IllegalStateException(
                        "instruction at " + toAddr(offset) + " has internal p-code control flow");
                }
            }
            offset += instruction.getLength();
        }
    }

    private void initialize(PcodeThread<byte[]> thread, byte[] code) {
        Language language = currentProgram.getLanguage();
        AddressSpace memory = language.getDefaultSpace();
        thread.getState().getSharedState().setVar(memory, 0, code.length, true, code);
        byte[] ram = new byte[RAM_SIZE];
        Arrays.fill(ram, (byte) 0xa5);
        thread.getState().getSharedState().setVar(memory, RAM_START, RAM_SIZE, true, ram);

        AddressSetView registerAddresses = language.getRegisterAddresses();
        for (AddressRange range : registerAddresses) {
            int size = Math.toIntExact(range.getLength());
            thread.getState().setVar(
                range.getAddressSpace(), range.getMinAddress().getOffset(), size, false,
                new byte[size]);
        }
        Register lp = language.getRegister("lp");
        if (lp == null) {
            throw new IllegalStateException("missing register lp");
        }
        thread.getState().setVar(lp, thread.getArithmetic().fromConst(ENTRY, lp.getMinimumByteSize()));
        thread.overrideCounter(memory.getAddress(ENTRY));
        thread.overrideContextWithDefault();
    }

    private long execute(PcodeThread<byte[]> thread, long count) throws Exception {
        monitor.checkCancelled();
        long compiled = thread instanceof CountingJitThread jit ? jit.runCompiled(count) : 0;
        for (long remaining = count - compiled; remaining > 0;) {
            monitor.checkCancelled();
            long chunk = Math.min(remaining, 65_536);
            thread.stepInstruction(chunk);
            remaining -= chunk;
        }
        monitor.checkCancelled();
        return compiled;
    }

    private Snapshot snapshot(PcodeThread<byte[]> thread, int codeSize) throws Exception {
        Language language = currentProgram.getLanguage();
        MessageDigest registers = MessageDigest.getInstance("SHA-256");
        AddressSetView registerAddresses = language.getRegisterAddresses();
        for (AddressRange range : registerAddresses) {
            int size = Math.toIntExact(range.getLength());
            registers.update(thread.getState().getVar(
                range.getAddressSpace(), range.getMinAddress().getOffset(), size, false,
                Reason.INSPECT));
        }
        String registersSha = HexFormat.of().formatHex(registers.digest());

        AddressSpace memorySpace = language.getDefaultSpace();
        byte[] code = thread.getState().getSharedState().getVar(
            memorySpace, 0, codeSize, true, Reason.INSPECT);
        byte[] ram = thread.getState().getSharedState().getVar(
            memorySpace, RAM_START, RAM_SIZE, true, Reason.INSPECT);
        return new Snapshot(String.format("0x%08x", thread.getCounter().getOffset()),
            registersSha, sha256(code), sha256(ram));
    }

    private static String sha256(byte[] value) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(value));
    }
}
