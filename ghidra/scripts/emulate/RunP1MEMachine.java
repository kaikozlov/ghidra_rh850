//@author kaikozlov
//@category Emulation
// Execute exact registered RH850/P1M-E firmware with strict machine-state provenance.
// Args: <absolute-run-contract-json> <absolute-report-json>

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import ghidra.app.plugin.processors.sleigh.SleighLanguage;
import ghidra.app.script.GhidraScript;
import ghidra.pcode.emu.PcodeEmulationCallbacks;
import ghidra.pcode.emu.PcodeEmulator;
import ghidra.pcode.emu.PcodeMachine;
import ghidra.pcode.emu.PcodeThread;
import ghidra.pcode.exec.AnnotatedPcodeUseropLibrary;
import ghidra.pcode.exec.PcodeExecutor;
import ghidra.pcode.exec.PcodeExecutorStatePiece;
import ghidra.pcode.exec.PcodeStateCallbacks;
import ghidra.pcode.exec.PcodeExecutorStatePiece.Reason;
import ghidra.pcode.exec.PcodeProgram;
import ghidra.pcode.exec.PcodeUseropLibrary;
import ghidra.pcode.exec.AnnotatedPcodeUseropLibrary.PcodeUserop;
import ghidra.pcode.utils.Utils;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.lang.Register;
import ghidra.program.model.lang.RegisterValue;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.scalar.Scalar;
import java.nio.charset.StandardCharsets;

import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.PriorityQueue;
import java.util.Map;
import java.util.Set;

public class RunP1MEMachine extends GhidraScript {
    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final String CONTRACT_SCHEMA = "rh850-p1me-machine-run-v2";
    private static final String MODEL_SCHEMA = "rh850-p1me-machine-v2";
    private static final String SCENARIO_SCHEMA = "rh850-p1me-machine-scenario-v2";

    static final class MachineFault extends RuntimeException {
        final String kind;
        final long pc;
        final long address;
        final int size;
        final String access;
        final String provenance;

        MachineFault(String kind, long pc, long address, int size, String access,
                     String provenance, String detail) {
            super(detail + " pc=" + hex32(pc) + " address=" + hex32(address)
                + " size=" + size + " access=" + access);
            this.kind = kind;
            this.pc = pc;
            this.address = address;
            this.size = size;
            this.access = access;
            this.provenance = provenance;
        }

        JsonObject toJson() {
            JsonObject out = new JsonObject();
            out.addProperty("kind", kind);
            out.addProperty("pc", hex32(pc));
            out.addProperty("address", hex32(address));
            out.addProperty("size", size);
            out.addProperty("access", access);
            out.addProperty("provenance", provenance);
            out.addProperty("detail", getMessage());
            return out;
        }
    }

    static final class MachineHalt extends RuntimeException {
        final String operation;

        MachineHalt(String operation) {
            super(operation);
            this.operation = operation;
        }
    }
    static final class ResetRule {
        String reset_class;
        String mode;
    }


    static final class RegionDef {
        String name;
        long start;
        long end_exclusive;
        int size;
        String access;
        boolean executable;
        String alias_group;
        String reset_control;
        List<ResetRule> reset_rules = new ArrayList<>();
        String reset_policy;
        String evidence;
        String source_ref;

        boolean contains(long address, int width) {
            long end = address + Integer.toUnsignedLong(width);
            return Long.compareUnsigned(address, start) >= 0
                && Long.compareUnsigned(end, end_exclusive) <= 0;
        }
    }

    static final class RegisterDef {
        String name;
        long address;
        int size;
        List<Integer> access_widths;
        String access;
        Long reset;
        String behavior;
        String evidence;
        String source_ref;
        String description;
        String trigger;
        String status_register;
        String secondary_status_register;
        String access_register;
        String history_register;
        String reload_prefix;
        String counter_prefix;
        Long payload_address;
        Long completion_value;
        Long channel_count;
        Integer interrupt_channel;
        Integer interrupt_channel_base;
        String interrupt_register_prefix;
        String interrupt_register;
        String mode_prefix;
        String prescaler_register;
        String control_register;
        String pointer_register;
        String window_register;
        String channel_control_register;
        String global_control_register;
        Integer fifo_index;
        Integer fifo_channel;

        boolean contains(long candidate, int width) {
            long end = candidate + Integer.toUnsignedLong(width);
            return Long.compareUnsigned(candidate, address) >= 0
                && Long.compareUnsigned(end, address + size) <= 0;
        }

        boolean allows(long candidate, int width) {
            return contains(candidate, width)
                && access_widths.contains(width)
                && Long.remainderUnsigned(candidate - address, width) == 0;
        }
    }

    static final class ProductDef {
        String product_id;
    }

    static final class EvidenceLayer {
        List<RegionDef> regions = new ArrayList<>();
        List<RegisterDef> registers = new ArrayList<>();
    }

    static final class MachineSpec {
        String schema;
        List<ProductDef> products;
        long p_bus_hz;
        EvidenceLayer manual;
        EvidenceLayer target_derived;
    }

    static final class ImageDef {
        String path;
        String sha256;
        int size;
        String base;
    }

    static final class TargetDef {
        String name;
        String mcu;
        String processor;
        ImageDef codeflash;
        ImageDef dataflash;
    }

    static final class MemoryInit {
        String address;
        Integer size;
        String hex;
        Integer fill;
        String evidence;
    }

    static final class ArtifactLoad {
        String address;
        String path;
        String sha256;
        boolean executable;
        String evidence;
    }

    static final class CheckDef {
        String name;
        String kind;
        String register;
        String address;
        Integer size;
        String operation;
        String equals;
        String equals_hex;
    }

    static final class ExpectedFault {
        String kind;
        String address;
        String access;
    }

    static final class EntryRequirement {
        int index;
        String mnemonic;
        Integer operand;
        String scalar;
    }

    static final class EntrySelector {
        String role;
        String scope;
        String address;
        String shape_sha256;
        int instruction_count;
        int body_size;
        int offset;
        List<EntryRequirement> requirements = new ArrayList<>();
    }
    static final class ResolvedEntry {
        final long address;
        final JsonObject proof;

        ResolvedEntry(long address, JsonObject proof) {
            this.address = address;
            this.proof = proof;
        }
    }

    static final class SelectorCandidate {
        final long address;
        final int bodySize;
        final List<Instruction> instructions;

        SelectorCandidate(long address, int bodySize, List<Instruction> instructions) {
            this.address = address;
            this.bodySize = bodySize;
            this.instructions = instructions;
        }
    }

    static final class ExternalEvent {
        String kind;
        long after_instructions;
        String evidence;
        Long p_bus_cycles;
        Integer fifo;
        Integer channel;
        String can_id;
        String data_hex;
        boolean extended;
        boolean fd;
        String boundary;
        int label;
        int timestamp;
    }


    static final class Scenario {
        String schema;
        String name;
        EntrySelector entry;
        long max_instructions;
        String reset = "none";
        List<String> stop_addresses = new ArrayList<>();
        Map<String, String> registers = new LinkedHashMap<>();
        List<MemoryInit> memory = new ArrayList<>();
        List<MemoryInit> pre_reset_memory = new ArrayList<>();
        List<ArtifactLoad> artifacts = new ArrayList<>();
        List<CheckDef> checks = new ArrayList<>();
        List<ExternalEvent> events = new ArrayList<>();
        ExpectedFault expected_fault;
    }

    static final class RunContract {
        String schema;
        TargetDef target;
        String model_path;
        String model_sha256;
        List<Scenario> scenarios;
    }

    static final class Trace {
        long instructions;
        final List<Long> recentPcs = new ArrayList<>();
        final Set<Long> executed = new HashSet<>();
        final Map<String, Long> syncCounts = new LinkedHashMap<>();
        final List<JsonObject> memoryAccesses = new ArrayList<>();
        final List<JsonObject> deviceEvents = new ArrayList<>();

        Trace() {
            syncCounts.put("SYNCE", 0L);
            syncCounts.put("SYNCM", 0L);
            syncCounts.put("SYNCP", 0L);
            syncCounts.put("SYNCI", 0L);
        }

        void sync(String operation) {
            syncCounts.put(operation, syncCounts.get(operation) + 1);
        }

        void access(String kind, long pc, long address, int size, String evidence) {
            if (memoryAccesses.size() >= 4096) return;
            JsonObject row = new JsonObject();
            row.addProperty("kind", kind);
            row.addProperty("pc", hex32(pc));
            row.addProperty("address", hex32(address));
            row.addProperty("size", size);
            row.addProperty("evidence", evidence);
            memoryAccesses.add(row);
        }
    }

    static final class ScheduledEvent {
        final long tick;
        final long ordinal;
        final Runnable action;

        ScheduledEvent(long tick, long ordinal, Runnable action) {
            this.tick = tick;
            this.ordinal = ordinal;
            this.action = action;
        }
    }

    static final class ReceiveFifo {
        final RegisterDef control, status, pointer, window, global, channel, interrupt;
        final ArrayDeque<byte[]> messages = new ArrayDeque<>();

        ReceiveFifo(Model model, RegisterDef control) {
            this.control = control;
            status = model.requiredRegister(control.name, "status", control.status_register);
            pointer = model.requiredRegister(control.name, "pointer", control.pointer_register);
            window = model.requiredRegister(control.name, "window", control.window_register);
            global = model.requiredRegister(control.name, "global", control.global_control_register);
            channel = model.requiredRegister(control.name, "channel", control.channel_control_register);
            interrupt = model.requiredRegister(control.name, "interrupt", control.interrupt_register);
        }
    }

    static final class Model {
        static final long FASTAT_ACCESS_ERROR_MASK = 0x88;
        static final long FASTAT_CMDLK = 0x10;
        static final long FSTATR_FRDY = 0x8000;
        static final long FSTATR_ILGLERR = 0x4000;
        static final long FSTATR_STATUS_CLEAR_MASK = 0x3703c;
        static final long FSTATR_COMMAND_LOCK_MASK = 0x27068;

        final SleighLanguage language;
        final MachineSpec spec;
        final Trace trace;
        final List<RegionDef> regions;
        final List<RegisterDef> registers;
        final Map<String, RegisterDef> registersByName = new HashMap<>();
        final Map<Integer, RegisterDef> interruptRegisters = new LinkedHashMap<>();
        final Map<Integer, ReceiveFifo> receiveFifos = new HashMap<>();
        // R01UH0585EJ0120 Table 17.132: CFDC and CFPLS encodings.
        static final int[] FIFO_DEPTHS = {0, 4, 8, 16, 32, 48, 64, 128};
        static final int[] PAYLOAD_LENGTHS = {8, 12, 16, 20, 24, 32, 48, 64};
        RegisterDef timerStart;
        long[] timerRemainders;
        List<ExternalEvent> externalEvents = List.of();
        int nextExternalEvent;
        long registerBeforeWrite;
        final List<Integer> faciSequence = new ArrayList<>();
        final Map<String, List<RegionDef>> aliases = new HashMap<>();
        final PriorityQueue<ScheduledEvent> scheduledEvents = new PriorityQueue<>(
            Comparator.comparingLong((ScheduledEvent event) -> event.tick)
                .thenComparingLong(event -> event.ordinal));
        long nextEventOrdinal;
        PcodeEmulator emulator;
        AddressSpace memorySpace;
        boolean internalWrite;

        Model(SleighLanguage language, MachineSpec spec, Trace trace) {
            this.language = language;
            this.spec = spec;
            this.trace = trace;
            this.regions = new ArrayList<>(spec.manual.regions);
            this.registers = new ArrayList<>(spec.manual.registers);
            this.registers.addAll(spec.target_derived.registers);
            regions.sort(Comparator.comparingLong(row -> row.start));
            for (RegisterDef register : registers) {
                registersByName.put(register.name, register);
                if ("intc_eic".equals(register.behavior)) {
                    if (register.interrupt_channel == null) {
                        throw new IllegalArgumentException(register.name + " lacks interrupt channel metadata");
                    }
                    interruptRegisters.put(register.interrupt_channel, register);
                }
            }
            registers.sort(Comparator.comparingLong(row -> row.address));
            for (RegionDef region : regions) {
                if (region.alias_group != null) {
                    aliases.computeIfAbsent(region.alias_group, ignored -> new ArrayList<>()).add(region);
                }
            }
            for (RegisterDef register : registers) {
                if (register.window_register != null) {
                    receiveFifos.put(register.fifo_index, new ReceiveFifo(this, register));
                }
                if ("tauj-start".equals(register.trigger)) {
                    timerStart = register;
                    timerRemainders = new long[Math.toIntExact(register.channel_count)];
                }
            }
        }

        void attach(PcodeEmulator emulator) {
            this.emulator = emulator;
            this.memorySpace = language.getDefaultSpace();
        }

        long scheduleNextTick(Runnable action) {
            long tick = trace.instructions + 1;
            scheduledEvents.add(new ScheduledEvent(tick, nextEventOrdinal++, action));
            return tick;
        }

        void dispatchDueEvents() {
            while (!scheduledEvents.isEmpty() && scheduledEvents.peek().tick <= trace.instructions) {
                scheduledEvents.remove().action.run();
            }
        }

        RegionDef region(long address, int size) {
            int low = 0;
            int high = regions.size() - 1;
            int candidate = -1;
            while (low <= high) {
                int middle = (low + high) >>> 1;
                if (Long.compareUnsigned(regions.get(middle).start, address) <= 0) {
                    candidate = middle;
                    low = middle + 1;
                }
                else {
                    high = middle - 1;
                }
            }
            if (candidate < 0) return null;
            RegionDef region = regions.get(candidate);
            return region.contains(address, size) ? region : null;
        }

        RegisterDef register(long address, int size) {
            int low = 0;
            int high = registers.size() - 1;
            int candidate = -1;
            while (low <= high) {
                int middle = (low + high) >>> 1;
                if (Long.compareUnsigned(registers.get(middle).address, address) <= 0) {
                    candidate = middle;
                    low = middle + 1;
                }
                else {
                    high = middle - 1;
                }
            }
            if (candidate < 0) return null;
            RegisterDef register = registers.get(candidate);
            return register.contains(address, size) ? register : null;
        }

        long pc(PcodeThread<byte[]> thread) {
            return thread == null || thread.getCounter() == null ? 0 : thread.getCounter().getOffset();
        }
        long processorRegister(PcodeThread<byte[]> thread, String name) {
            Register register = language.getRegister(name);
            if (register == null) {
                throw new IllegalStateException("processor model lacks register " + name);
            }
            byte[] value = thread.getState().getVar(register, Reason.INSPECT);
            return Utils.bytesToLong(value, value.length, language.isBigEndian()) & 0xffffffffL;
        }

        void processorRegister(PcodeThread<byte[]> thread, String name, long value) {
            Register register = language.getRegister(name);
            if (register == null) throw new IllegalArgumentException("unknown processor register: " + name);
            thread.getState().setVar(register, bytes(value, register.getNumBytes(), language.isBigEndian()));
        }

        void requestInterrupt(PcodeThread<byte[]> thread, int channel) {
            RegisterDef eic = interruptRegisters.get(channel);
            if (eic == null || eic.reset == null) {
                throw fault("unsupported-interrupt", thread, channel, 0, "request", "manual",
                    "interrupt channel is not described by the device model");
            }
            setRegisterValue(eic.name, unsigned(memory(eic.address, eic.size)) | 0x1000);
            JsonObject event = new JsonObject();
            event.addProperty("kind", "interrupt-request");
            event.addProperty("channel", channel);
            event.addProperty("scheduler_tick", trace.instructions);
            trace.deviceEvents.add(event);
        }

        void deliverInterrupt(PcodeThread<byte[]> thread) {
            long psw = processorRegister(thread, "PSW");
            if ((psw & 0xa0) != 0) return;
            long serviced = processorRegister(thread, "ISPR") & 0xffff;
            int ceiling = serviced == 0 ? 16 : Long.numberOfTrailingZeros(serviced);
            long pmr = processorRegister(thread, "PMR");
            RegisterDef selected = null;
            int priority = 16;
            boolean priorityMasked = false;
            for (RegisterDef eic : interruptRegisters.values()) {
                if (eic.reset == null) continue;
                long value = unsigned(memory(eic.address, eic.size));
                if ((value & 0x1080) != 0x1000) continue;
                int candidate = (int) value & 15;
                if (candidate >= ceiling) continue;
                if ((pmr & (1L << candidate)) != 0) {
                    priorityMasked = true;
                    continue;
                }
                if (candidate < priority || (candidate == priority && selected != null
                        && eic.interrupt_channel < selected.interrupt_channel)) {
                    priority = candidate;
                    selected = eic;
                }
            }
            long icsr = processorRegister(thread, "ICSR");
            processorRegister(thread, "ICSR", (icsr & ~1L) | (priorityMasked ? 1L : 0L));
            if (selected == null) return;
            long control = unsigned(memory(selected.address, selected.size));
            long base = processorRegister(thread, (psw & 0x8000) == 0 ? "RBASE" : "EBASE");
            long handler;
            if ((control & 0x40) != 0 && (base & 1) == 0) {
                long vector = (processorRegister(thread, "INTBP") & 0xfffffe00L)
                    + selected.interrupt_channel * 4L;
                beforeRead(thread, vector, 4);
                handler = unsigned(memory(thread, vector, 4));
            }
            else {
                handler = (base & 0xfffffe00L) + 0x100 + ((base & 1) == 0 ? priority * 16 : 0);
            }
            long returnPc = pc(thread);
            processorRegister(thread, "EIPC", returnPc);
            processorRegister(thread, "EIPSW", psw);
            processorRegister(thread, "EIIC", 0x1000 + selected.interrupt_channel);
            processorRegister(thread, "PSW", (psw & ~0x40000040L) | 0x20);
            processorRegister(thread, "ll_valid", 0);
            if ((processorRegister(thread, "INTCFG") & 1) == 0) {
                processorRegister(thread, "ISPR", serviced | (1L << priority));
            }
            // Edge requests clear on acceptance; level requests remain until their source clears.
            if ((control & 0x8000) == 0) setRegisterValue(selected.name, control & ~0x1000L);
            thread.overrideCounter(memorySpace.getAddress(handler));
            JsonObject event = new JsonObject();
            event.addProperty("kind", "interrupt-enter");
            event.addProperty("channel", selected.interrupt_channel);
            event.addProperty("priority", priority);
            event.addProperty("return_pc", hex32(returnPc));
            event.addProperty("handler", hex32(handler));
            event.addProperty("scheduler_tick", trace.instructions);
            trace.deviceEvents.add(event);
        }

        void initializeProcessorReset(PcodeThread<byte[]> thread) {
            Map<String, Long> resetValues = Map.ofEntries(
                Map.entry("PSW", 0x20L),
                Map.entry("FPEC", 0L),
                Map.entry("MCTL", 0L),
                Map.entry("MPM", 0L),
                Map.entry("ASID", 0L),
                Map.entry("ISPR", 0L),
                Map.entry("PMR", 0L),
                Map.entry("INTCFG", 0L),
                Map.entry("ICSR", 0L),
                // SLEIGH-internal monitor state: a fresh machine has no reservation.
                Map.entry("ll_addr", 0L),
                Map.entry("ll_valid", 0L)
            );
            for (Map.Entry<String, Long> row : resetValues.entrySet()) {
                Register register = language.getRegister(row.getKey());
                if (register != null) {
                    thread.getState().setVar(register,
                        bytes(row.getValue(), register.getNumBytes(), language.isBigEndian()));
                }
            }
            for (int index = 0; index < 16; index++) {
                for (String prefix : List.of("MPLA", "MPUA", "MPAT")) {
                    Register register = language.getRegister(prefix + index);
                    if (register != null) {
                        thread.getState().setVar(register,
                            bytes(0, register.getNumBytes(), language.isBigEndian()));
                    }
                }
            }
        }

        void requireAlignment(PcodeThread<byte[]> thread, long address, int size, String access) {
            if (size <= 1) return;
            long mctl = processorRegister(thread, "MCTL");
            int alignment = size;
            if ((mctl & 2) != 0) {
                if (size < 8) return;
                alignment = 4;
            }
            if (Long.remainderUnsigned(address, alignment) != 0) {
                throw fault("misaligned-" + access, thread, address, size, access,
                    "manual:R01US0123EJ0140 section 2.6.3 and Table 3-29",
                    "MCTL.MA does not permit this data alignment");
            }
        }

        void requireMpu(PcodeThread<byte[]> thread, long address, int size, String access) {
            long mpm = processorRegister(thread, "MPM");
            if ((mpm & 1) == 0) return;
            long psw = processorRegister(thread, "PSW");
            boolean user = (psw & (1L << 30)) != 0;
            if (!user && (mpm & 2) == 0) return;
            long last = address + Integer.toUnsignedLong(size) - 1;
            long asid = processorRegister(thread, "ASID") & 0x3ff;
            int permission = access.equals("execute") ? (user ? 2 : 5)
                : access.equals("write") ? (user ? 1 : 4) : (user ? 0 : 3);
            boolean matched = false;
            for (int index = 0; index < 16; index++) {
                long attributes = processorRegister(thread, "MPAT" + index);
                if ((attributes & 0x80) == 0) continue;
                if ((attributes & 0x40) == 0 && ((attributes >>> 16) & 0x3ff) != asid) {
                    continue;
                }
                long lower = processorRegister(thread, "MPLA" + index) & 0xfffffffcL;
                long upper = processorRegister(thread, "MPUA" + index) | 3L;
                if (Long.compareUnsigned(address, lower) < 0
                        || Long.compareUnsigned(last, upper) > 0) continue;
                matched = true;
                if ((attributes & (1L << permission)) != 0) return;
            }
            throw fault("mpu-" + access, thread, address, size, access,
                "manual:R01US0123EJ0140 sections 3.5 and 5.1",
                matched ? "all matching MPU regions deny " + access
                    : "MPU has no matching enabled region and G3M defaults deny access");
        }


        void requireExecute(PcodeThread<byte[]> thread, long address, int size) {
            requireMpu(thread, address, size, "execute");
            RegionDef region = region(address, size);
            if (region == null || !region.executable) {
                throw fault("execute-unmapped", thread, address, size, "execute",
                    region == null ? "unknown" : region.evidence,
                    "instruction fetch outside an executable P1M-E region");
            }
        }

        void beforeRead(PcodeThread<byte[]> thread, long address, int size) {
            requireAlignment(thread, address, size, "read");
            requireMpu(thread, address, size, "read");
            RegionDef region = region(address, size);
            if (region != null) {
                if (!region.access.contains("r")) {
                    throw fault("read-prohibited", thread, address, size, "read",
                        region.evidence, "region is not software-readable: " + region.name);
                }
                trace.access("read", pc(thread), address, size, region.evidence);
                return;
            }
            RegisterDef register = register(address, size);
            if (register == null) {
                throw fault("unmapped-read", thread, address, size, "read", "unknown",
                    "no SystemRDL memory region or register covers this read");
            }
            if (!register.allows(address, size)) {
                throw fault("mmio-width", thread, address, size, "read",
                    register.evidence, "illegal access width/alignment for register " + register.name);
            }
            if (!register.access.contains("r")) {
                throw fault("read-prohibited", thread, address, size, "read",
                    register.evidence, "register is not software-readable: " + register.name);
            }
            trace.access("read", pc(thread), address, size, register.evidence);
        }

        void beforeWrite(PcodeThread<byte[]> thread, long address, int size, byte[] value) {
            if (internalWrite) return;
            requireAlignment(thread, address, size, "write");
            requireMpu(thread, address, size, "write");
            RegionDef region = region(address, size);
            if (region != null) {
                if (!region.access.contains("w") || region.name.startsWith("codeflash")
                        || region.name.equals("dataflash")) {
                    throw fault("write-prohibited", thread, address, size, "write",
                        region.evidence, "direct write prohibited for region: " + region.name);
                }
                trace.access("write", pc(thread), address, size, region.evidence);
                return;
            }
            RegisterDef register = register(address, size);
            if (register == null) {
                throw fault("unmapped-write", thread, address, size, "write", "unknown",
                    "no SystemRDL memory region or register covers this write");
            }
            if (!register.allows(address, size)) {
                throw fault("mmio-width", thread, address, size, "write",
                    register.evidence, "illegal access width/alignment for register " + register.name);
            }
            if (!register.access.contains("w")) {
                throw fault("write-prohibited", thread, address, size, "write",
                    register.evidence, "register is not software-writable: " + register.name);
            }
            validateDeviceWrite(thread, register, value);
            if ((register.fifo_index != null && receiveFifos.containsKey(register.fifo_index)
                    && receiveFifos.get(register.fifo_index).status == register)
                    || ("intc_eic".equals(register.behavior) && register.reset != null)) {
                registerBeforeWrite = unsigned(memory(thread, register.address, register.size));
            }
            trace.access("write", pc(thread), address, size, register.evidence);
        }

        void resetRegion(RegionDef region, String resetClass) {
            byte[] zero = new byte[region.size];
            setMemory(region.start, zero);
            if (region.alias_group != null) {
                for (RegionDef alias : aliases.get(region.alias_group)) {
                    if (alias != region) setMemory(alias.start, zero);
                }
            }
            JsonObject event = new JsonObject();
            event.addProperty("kind", "reset-initialization");
            event.addProperty("reset_class", resetClass);
            event.addProperty("region", region.name);
            event.addProperty("size", region.size);
            event.addProperty("evidence", region.source_ref);
            trace.deviceEvents.add(event);
        }

        boolean resetControlEnabled(String name) {
            RegisterDef control = registersByName.get(name);
            long mode = unsigned(memory(control.address, control.size)) & 3;
            if (mode == 1) {
                throw new IllegalArgumentException(name + " has prohibited RZEROMD=01");
            }
            return mode == 3;
        }

        void resetControl(String name) {
            setRegisterValue(name, 3);
        }

        void applyReset(String resetClass) {
            if (resetClass == null || resetClass.equals("none")) return;
            boolean matched = false;
            for (RegionDef region : regions) {
                for (ResetRule rule : region.reset_rules) {
                    if (!resetClass.equals(rule.reset_class)) continue;
                    matched = true;
                    if ("force".equals(rule.mode)) {
                        resetControl(region.reset_control);
                        resetRegion(region, resetClass);
                    }
                    else if ("controlled".equals(rule.mode)) {
                        if (resetControlEnabled(region.reset_control)) {
                            resetRegion(region, resetClass);
                        }
                    }
                    else {
                        throw new IllegalStateException(
                            "machine model has unknown reset mode: " + rule.mode);
                    }
                }
            }
            if (!matched) {
                throw new IllegalArgumentException("unsupported reset class: " + resetClass);
            }
        }

        long unsigned(byte[] value) {
            return Utils.bytesToLong(value, value.length, language.isBigEndian()) & 0xffffffffL;
        }

        byte[] memory(long address, int size) {
            return emulator.getSharedState().getVar(
                memorySpace, address, size, true, Reason.INSPECT);
        }

        byte[] memory(PcodeThread<byte[]> thread, long address, int size) {
            return thread.getState().getVar(
                memorySpace, address, size, true, Reason.INSPECT);
        }

        RegisterDef requiredRegister(String owner, String relation, String name) {
            RegisterDef register = name == null ? null : registersByName.get(name);
            if (register == null) {
                throw new IllegalStateException(owner + " lacks " + relation + " register metadata");
            }
            return register;
        }

        void validateDeviceWrite(PcodeThread<byte[]> thread, RegisterDef register,
                                 byte[] value) {
            if ("faci-command".equals(register.trigger)) {
                int command = value[0] & 0xff;
                if (command != 0x50) {
                    throw fault("unsupported-faci-command", thread, register.address,
                        value.length, "write", register.evidence,
                        String.format("FACI command 0x%02X has no implemented state transition",
                            command));
                }
                RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                long statusValue = unsigned(memory(thread, status.address, status.size));
                if ((statusValue & FSTATR_FRDY) == 0) {
                    throw fault("faci-not-ready", thread, register.address,
                        value.length, "write", register.evidence,
                        "FACI status-clear command requires FSTATR.FRDY=1");
                }
                RegisterDef accessStatus = requiredRegister(
                    register.name, "access-status", register.access_register);
                RegisterDef commandHistory = requiredRegister(
                    register.name, "history", register.history_register);
                memory(thread, accessStatus.address, accessStatus.size);
                memory(thread, commandHistory.address, commandHistory.size);
            }
            if ("icus-command".equals(register.trigger) && (unsigned(value) & 0xffff) != 5) {
                throw fault("unsupported-icus-command", thread, register.address,
                    value.length, "write", register.evidence,
                    String.format("ICU-S command 0x%04X has no recovered state transition",
                        unsigned(value) & 0xffff));
            }
            if ("rscfd-transmit".equals(register.trigger) && (unsigned(value) & 1) != 0) {
                if (register.payload_address == null) {
                    throw new IllegalStateException(register.name + " lacks payload_address metadata");
                }
                long base = register.payload_address;
                memory(thread, base, 4);
                memory(thread, base + 4, 4);
                memory(thread, base + 12, 4);
                memory(thread, base + 16, 4);
            }
            if ("tauj-start".equals(register.trigger) || "tauj-stop".equals(register.trigger)) {
                RegisterDef enabled = requiredRegister(
                    register.name, "status", register.status_register);
                memory(thread, enabled.address, enabled.size);
                if ("tauj-start".equals(register.trigger)) {
                    long mask = unsigned(value);
                    int channels = Math.toIntExact(register.channel_count);
                    for (int channel = 0; channel < channels; channel++) {
                        if ((mask & (1L << channel)) == 0) continue;
                        RegisterDef reload = requiredRegister(
                            register.name, "reload", register.reload_prefix + channel);
                        memory(thread, reload.address, reload.size);
                        timerClockDivisor(thread, channel);
                    }
                }
            }
        }

        void setRegisterValue(String name, long value) {
            RegisterDef register = registersByName.get(name);
            if (register == null) throw new IllegalStateException("machine model lacks register " + name);
            setMemory(register.address, bytes(value, register.size, language.isBigEndian()));
        }

        void registerWriteEvent(PcodeThread<byte[]> thread, RegisterDef register, byte[] value) {
            JsonObject event = new JsonObject();
            event.addProperty("kind", "register-write");
            event.addProperty("pc", hex32(pc(thread)));
            event.addProperty("register", register.name);
            event.addProperty("behavior", register.behavior);
            event.addProperty("trigger", register.trigger);
            event.addProperty("value", hex32(unsigned(value)));
            event.addProperty("evidence", register.evidence);
            trace.deviceEvents.add(event);
        }

        void handleRscfdWrite(PcodeThread<byte[]> thread, RegisterDef register, byte[] value) {
            if ((unsigned(value) & 1) == 0) return;
            if (register.payload_address == null || register.completion_value == null) {
                throw new IllegalStateException(register.name + " lacks RSCFD trigger metadata");
            }
            long base = register.payload_address;
            RegisterDef status = requiredRegister(
                register.name, "completion-status", register.status_register);
            byte[] header = memory(base, 8);
            byte[] data = memory(base + 12, 8);
            long id = unsigned(Arrays.copyOfRange(header, 0, 4)) & 0x1fffffffL;
            long pointerRaw = unsigned(Arrays.copyOfRange(header, 4, 8));
            long issuePc = pc(thread);
            StringBuilder payload = new StringBuilder();
            for (byte b : data) payload.append(String.format("%02x", b & 0xff));
            String payloadHex = payload.toString();
            scheduleNextTick(() -> {
                JsonObject event = new JsonObject();
                event.addProperty("kind", "can-tx");
                event.addProperty("pc", hex32(issuePc));
                event.addProperty("scheduler_tick", trace.instructions);
                event.addProperty("controller", "RSCFD");
                event.addProperty("buffer", 16);
                event.addProperty("can_id", hex32(id));
                event.addProperty("pointer_raw", hex32(pointerRaw));
                event.addProperty("data_hex", payloadHex);
                event.addProperty("evidence", register.source_ref);
                trace.deviceEvents.add(event);
                setRegisterValue(status.name, register.completion_value);
                setRegisterValue(register.name, 0);
            });
        }

        long registerValue(RegisterDef register) {
            return unsigned(memory(register.address, register.size));
        }

        void refreshReceiveFifo(ReceiveFifo fifo) {
            long control = registerValue(fifo.control);
            int depth = FIFO_DEPTHS[(int) (control >>> 8) & 7];
            int count = fifo.messages.size();
            long status = registerValue(fifo.status) & 0x1c;
            status |= ((long) count << 8) | (count == 0 ? 1 : 0)
                | (depth != 0 && count == depth ? 2 : 0);
            setRegisterValue(fifo.status.name, status);
            if (count != 0) setMemory(fifo.window.address, fifo.messages.peek());
            refreshReceiveInterrupt(fifo);
        }

        void refreshReceiveInterrupt(ReceiveFifo fifo) {
            long old = registerValue(fifo.interrupt);
            boolean requested = false;
            for (ReceiveFifo source : receiveFifos.values()) {
                if (source.interrupt == fifo.interrupt && (registerValue(source.status) & 8) != 0
                        && (registerValue(source.control) & 2) != 0) {
                    requested = true;
                    break;
                }
            }
            setRegisterValue(fifo.interrupt.name, (old & ~0x1000L) | (requested ? 0x1000 : 0));
        }

        void receiveFrame(PcodeThread<byte[]> thread, ExternalEvent input) {
            ReceiveFifo fifo = receiveFifos.get(input.fifo);
            if (fifo == null || !"post-filter".equals(input.boundary)) {
                throw fault("unsupported-can-receive", thread, 0, 0, "event", "scenario",
                    "only a modeled common FIFO at the explicit post-filter boundary is supported");
            }
            long control = registerValue(fifo.control);
            if ((control & 0x30000) != 0) {
                throw fault("unsupported-fifo-mode", thread, fifo.control.address, 4,
                    "event", "manual", "only common-FIFO receive mode is implemented");
            }
            int depth = FIFO_DEPTHS[(int) (control >>> 8) & 7];
            int capacity = PAYLOAD_LENGTHS[(int) (control >>> 4) & 7];
            byte[] payload = parseHex(input.data_hex);
            long config = registerValue(requiredRegister(fifo.control.name, "configuration", "GCFG"));
            String discarded = null;
            if ((registerValue(fifo.global) & 7) != 0 || (registerValue(fifo.channel) & 7) != 0) {
                discarded = "controller-not-operating";
            }
            else if ((control & 1) == 0 || depth == 0) discarded = "fifo-disabled";
            else if (payload.length > capacity && (config & 0x20) == 0) discarded = "payload-capacity";
            else if (fifo.messages.size() == depth) {
                setRegisterValue(fifo.status.name, registerValue(fifo.status) | 4);
                discarded = "fifo-full";
            }
            if (discarded == null) {
                int thresholdEighths = ((int) (control >>> 13) & 7) + 1;
                if ((control & 0x1000) == 0 && depth == 4 && (thresholdEighths & 1) != 0) {
                    throw fault("unsupported-fifo-threshold", thread, fifo.control.address, 4,
                        "event", "manual", "four-message FIFO requires an even threshold eighth");
                }
                byte[] window = new byte[76];
                int dlc = payload.length <= 8 ? payload.length : 9;
                while (dlc > 8 && PAYLOAD_LENGTHS[dlc - 8] != payload.length) dlc++;
                System.arraycopy(bytes(parseUnsigned(input.can_id) | (input.extended ? 0x80000000L : 0),
                    4, false), 0, window, 0, 4);
                System.arraycopy(bytes(((long) dlc << 28) | ((long) input.label << 16) | input.timestamp,
                    4, false), 0, window, 4, 4);
                window[8] = (byte) (input.fd ? 4 : 0);
                System.arraycopy(payload, 0, window, 12, Math.min(payload.length, capacity));
                fifo.messages.add(window);
                if ((control & 0x1000) != 0 || fifo.messages.size() * 8 >= depth * thresholdEighths) {
                    setRegisterValue(fifo.status.name, registerValue(fifo.status) | 8);
                }
                refreshReceiveFifo(fifo);
            }
            JsonObject event = GSON.toJsonTree(input).getAsJsonObject();
            event.addProperty("kind", discarded == null ? "can-rx" : "can-rx-discard");
            if (discarded != null) event.addProperty("reason", discarded);
            event.addProperty("scheduler_tick", trace.instructions);
            trace.deviceEvents.add(event);
        }

        void handleReceiveWrite(PcodeThread<byte[]> thread, RegisterDef register, byte[] value) {
            ReceiveFifo fifo = register.fifo_index == null ? null : receiveFifos.get(register.fifo_index);
            if (fifo == null) return;
            if (register == fifo.status) {
                // CFMC/CFEMP/CFFLL are read-only; the three sticky flags clear by writing zero.
                setRegisterValue(register.name, registerBeforeWrite & (registerValue(register) | ~0x1cL));
                refreshReceiveInterrupt(fifo);
            }
            else if (register == fifo.control) {
                if ((registerValue(register) & 1) == 0) {
                    fifo.messages.clear();
                    refreshReceiveFifo(fifo);
                }
                else refreshReceiveInterrupt(fifo);
            }
            else if (register == fifo.pointer) {
                if ((unsigned(value) & 0xff) != 0xff || (registerValue(fifo.control) & 1) == 0
                        || fifo.messages.isEmpty()) {
                    throw fault("invalid-fifo-pop", thread, register.address, value.length,
                        "write", "manual", "receive FIFO pop requires CFE=1, unread data, and CFPC=0xFF");
                }
                fifo.messages.remove();
                refreshReceiveFifo(fifo);
                JsonObject event = new JsonObject();
                event.addProperty("kind", "can-rx-pop");
                event.addProperty("fifo", register.fifo_index);
                event.addProperty("remaining", fifo.messages.size());
                event.addProperty("scheduler_tick", trace.instructions);
                trace.deviceEvents.add(event);
            }
        }

        long timerClockDivisor(PcodeThread<byte[]> thread, int channel) {
            RegisterDef modeReg = requiredRegister(timerStart.name, "mode", timerStart.mode_prefix + channel);
            long mode = registerValue(modeReg);
            int clock = (int) (mode >>> 14) & 3;
            if ((mode & 0x371e) != 0 || clock == 3) {
                throw fault("unsupported-timer-mode", thread, modeReg.address, modeReg.size,
                    "clock", "manual", "only software-triggered interval mode on CK0..CK2 is implemented");
            }
            long prescaler = registerValue(requiredRegister(timerStart.name, "prescaler", timerStart.prescaler_register));
            return 1L << ((prescaler >>> (clock * 4)) & 15);
        }

        void advanceClock(PcodeThread<byte[]> thread, long cycles) {
            if (timerStart == null) throw new IllegalStateException("machine model lacks TAUJ");
            long enabled = registerValue(requiredRegister(timerStart.name, "status", timerStart.status_register));
            for (int channel = 0; channel < timerRemainders.length; channel++) {
                if ((enabled & (1L << channel)) == 0) continue;
                long divisor = timerClockDivisor(thread, channel);
                long remainder = cycles % divisor + timerRemainders[channel];
                long ticks = cycles / divisor + remainder / divisor;
                timerRemainders[channel] = remainder % divisor;
                RegisterDef counter = requiredRegister(timerStart.name, "counter", timerStart.counter_prefix + channel);
                RegisterDef reload = requiredRegister(timerStart.name, "reload", timerStart.reload_prefix + channel);
                long current = registerValue(counter);
                long underflows = 0;
                if (ticks <= current) current -= ticks;
                else {
                    long period = registerValue(reload) + 1;
                    long remaining = ticks - current - 1;
                    underflows = 1 + remaining / period;
                    current = period - 1 - remaining % period;
                    requestInterrupt(thread, timerStart.interrupt_channel_base + channel);
                }
                setRegisterValue(counter.name, current);
                JsonObject event = new JsonObject();
                event.addProperty("kind", "tauj-clock");
                event.addProperty("channel", channel);
                event.addProperty("p_bus_cycles", cycles);
                event.addProperty("underflows", underflows);
                event.addProperty("counter", current);
                event.addProperty("scheduler_tick", trace.instructions);
                trace.deviceEvents.add(event);
            }
        }

        void dispatchExternalEvents(PcodeThread<byte[]> thread) {
            while (nextExternalEvent < externalEvents.size()
                    && externalEvents.get(nextExternalEvent).after_instructions <= trace.instructions) {
                ExternalEvent input = externalEvents.get(nextExternalEvent++);
                switch (input.kind) {
                    case "clock": advanceClock(thread, input.p_bus_cycles); break;
                    case "can-rx": receiveFrame(thread, input); break;
                    case "interrupt": requestInterrupt(thread, input.channel); break;
                    default: throw new IllegalArgumentException("unknown external event " + input.kind);
                }
            }
        }

        void handleTaujWrite(PcodeThread<byte[]> thread, RegisterDef register, byte[] value) {
            boolean starting = "tauj-start".equals(register.trigger);
            if (!starting && !"tauj-stop".equals(register.trigger)) return;
            int channels = Math.toIntExact(register.channel_count);
            long mask = unsigned(value) & ((1L << channels) - 1);
            RegisterDef enabledRegister = requiredRegister(
                register.name, "status", register.status_register);
            long enabled = unsigned(memory(enabledRegister.address, enabledRegister.size));
            long next = starting ? enabled | mask : enabled & ~mask;
            long issuePc = pc(thread);
            setRegisterValue(enabledRegister.name, next);
            scheduleNextTick(() -> {
                if (starting) {
                    for (int channel = 0; channel < channels; channel++) {
                        if ((mask & (1L << channel)) == 0) continue;
                        RegisterDef reload = requiredRegister(
                            register.name, "reload", register.reload_prefix + channel);
                        RegisterDef counter = requiredRegister(
                            register.name, "counter", register.counter_prefix + channel);
                        setMemory(counter.address, memory(reload.address, reload.size));
                        timerRemainders[channel] = 0;
                        RegisterDef mode = requiredRegister(register.name, "mode", register.mode_prefix + channel);
                        if ((registerValue(mode) & 1) != 0) {
                            requestInterrupt(thread, register.interrupt_channel_base + channel);
                        }
                    }
                }
                JsonObject event = new JsonObject();
                event.addProperty("kind", register.trigger);
                event.addProperty("pc", hex32(issuePc));
                event.addProperty("scheduler_tick", trace.instructions);
                event.addProperty("unit", 0);
                event.addProperty("channel_mask", String.format("0x%X", mask));
                event.addProperty("evidence", register.source_ref);
                trace.deviceEvents.add(event);
            });
        }

        void handleFaciWrite(PcodeThread<byte[]> thread, RegisterDef register, byte[] value) {
            int command = value[0] & 0xff;
            if (command != 0x50) {
                throw new IllegalStateException("FACI write validation was bypassed");
            }
            RegisterDef statusRegister = requiredRegister(
                register.name, "status", register.status_register);
            RegisterDef accessRegister = requiredRegister(
                register.name, "access-status", register.access_register);
            RegisterDef historyRegister = requiredRegister(
                register.name, "history", register.history_register);
            long status = unsigned(memory(statusRegister.address, statusRegister.size));
            long accessStatus = unsigned(memory(accessRegister.address, accessRegister.size));
            long commandHistory = unsigned(memory(historyRegister.address, historyRegister.size));
            long nextStatus = status & ~FSTATR_STATUS_CLEAR_MASK;
            if ((accessStatus & FASTAT_ACCESS_ERROR_MASK) != 0) {
                nextStatus |= FSTATR_ILGLERR;
            }
            long nextAccessStatus = (nextStatus & FSTATR_COMMAND_LOCK_MASK) != 0
                ? accessStatus | FASTAT_CMDLK : accessStatus & ~FASTAT_CMDLK;
            faciSequence.add(command);
            setRegisterValue(historyRegister.name, (command << 8) | ((commandHistory >>> 8) & 0xff));
            setRegisterValue(statusRegister.name, nextStatus);
            setRegisterValue(accessRegister.name, nextAccessStatus);
            JsonObject event = new JsonObject();
            event.addProperty("kind", register.trigger);
            event.addProperty("pc", hex32(pc(thread)));
            event.addProperty("command", String.format("0x%02X", command));
            event.add("sequence", GSON.toJsonTree(faciSequence));
            event.addProperty("evidence", register.source_ref);
            trace.deviceEvents.add(event);
            faciSequence.clear();
        }

        void handleIcusWrite(PcodeThread<byte[]> thread, RegisterDef register, byte[] value) {
            long word = unsigned(value);
            JsonObject event = new JsonObject();
            event.addProperty("kind", register.trigger);
            event.addProperty("pc", hex32(pc(thread)));
            event.addProperty("selector", (word >>> 16) & 0xffff);
            event.addProperty("command", word & 0xffff);
            event.addProperty("evidence", register.source_ref);
            trace.deviceEvents.add(event);
            RegisterDef status = requiredRegister(register.name, "status", register.status_register);
            RegisterDef secondary = requiredRegister(
                register.name, "secondary-status", register.secondary_status_register);
            setRegisterValue(status.name, 0);
            setRegisterValue(secondary.name, 0);
        }

        void handleRegisterWrite(PcodeThread<byte[]> thread, long address, int size, byte[] value) {
            RegisterDef register = register(address, size);
            if (register == null) return;
            registerWriteEvent(thread, register, value);
            if ("intc_eic".equals(register.behavior) && register.reset != null) {
                long writable = (register.reset & 0x8000) == 0 ? 0x10cf : 0xcf;
                setRegisterValue(register.name,
                    (registerBeforeWrite & ~writable) | (registerValue(register) & writable));
            }
            handleReceiveWrite(thread, register, value);
            if (register.trigger == null) return;
            switch (register.trigger) {
                case "rscfd-transmit": handleRscfdWrite(thread, register, value); break;
                case "faci-command": handleFaciWrite(thread, register, value); break;
                case "icus-command": handleIcusWrite(thread, register, value); break;
                case "tauj-start":
                case "tauj-stop": handleTaujWrite(thread, register, value); break;
                default: throw new IllegalStateException(
                    "unknown machine-model trigger: " + register.trigger);
            }
        }

        void afterWrite(PcodeThread<byte[]> thread, long address, int size, byte[] value) {
            if (internalWrite) return;
            RegionDef region = region(address, size);
            if (region != null && region.alias_group != null) {
                long delta = address - region.start;
                List<RegionDef> group = aliases.get(region.alias_group);
                if (group != null) {
                    for (RegionDef alias : group) {
                        if (alias == region) continue;
                        setMemory(alias.start + delta, value);
                        JsonObject event = new JsonObject();
                        event.addProperty("kind", "alias-write");
                        event.addProperty("from", hex32(address));
                        event.addProperty("to", hex32(alias.start + delta));
                        event.addProperty("size", size);
                        trace.deviceEvents.add(event);
                    }
                }
            }
            handleRegisterWrite(thread, address, size, value);
        }

        void initializeResetRegisters() {
            for (RegisterDef register : registers) {
                if (register.reset == null) continue;
                setMemory(register.address, bytes(register.reset, register.size, language.isBigEndian()));
            }
        }

        void setMemory(long address, byte[] value) {
            internalWrite = true;
            try {
                emulator.getSharedState().setVar(memorySpace, address, value.length, true, value);
            }
            finally {
                internalWrite = false;
            }
        }

        void initializeMemory(long address, byte[] value, String evidence) {
            RegionDef region = region(address, value.length);
            RegisterDef register = register(address, value.length);
            if (region == null && register == null) {
                throw new IllegalArgumentException("scenario initializes unmapped state at "
                    + hex32(address) + " size=" + value.length);
            }
            if (region != null
                    && (region.name.startsWith("codeflash") || region.name.equals("dataflash"))) {
                throw new IllegalArgumentException("scenario cannot overlay registered image region "
                    + region.name + " at " + hex32(address));
            }
            setMemory(address, value);
            if (region != null && region.alias_group != null) {
                long delta = address - region.start;
                for (RegionDef alias : aliases.get(region.alias_group)) {
                    if (alias != region) setMemory(alias.start + delta, value);
                }
            }
            JsonObject event = new JsonObject();
            event.addProperty("kind", "scenario-initialization");
            event.addProperty("address", hex32(address));
            event.addProperty("size", value.length);
            event.addProperty("evidence", evidence == null ? "scenario" : evidence);
            trace.deviceEvents.add(event);
        }

        MachineFault uninitialized(PcodeThread<byte[]> thread, long address, int size,
                                   String space, Reason reason) {
            if (!space.equals(memorySpace.getName())) {
                return fault("uninitialized-register", thread, address, size, "read",
                    "processor", "uninitialized processor state in " + space
                        + " for reason " + reason);
            }
            RegionDef region = region(address, size);
            RegisterDef register = register(address, size);
            String provenance = region != null ? region.evidence
                : register != null ? register.evidence : "unknown";
            String owner = region != null ? region.name
                : register != null ? register.name : "unmapped";
            return fault("uninitialized-read", thread, address, size, "read", provenance,
                "uninitialized " + space + " state in " + owner + " for reason " + reason);
        }

        MachineFault fault(String kind, PcodeThread<byte[]> thread, long address, int size,
                           String access, String provenance, String detail) {
            return new MachineFault(kind, pc(thread), address, size, access, provenance, detail);
        }
    }

    static final class Callbacks implements PcodeEmulationCallbacks<byte[]> {
        final SleighLanguage language;
        final Model model;
        boolean interruptReturn;
        boolean automaticPriorityReturn;
        boolean protectedIsprWrite;
        long isprBeforeInstruction;

        Callbacks(SleighLanguage language, Model model) {
            this.language = language;
            this.model = model;
        }

        private long offset(byte[] value) {
            return Utils.bytesToLong(value, value.length, language.isBigEndian()) & 0xffffffffL;
        }

        @Override
        public void beforeDecodeInstruction(PcodeThread<byte[]> thread, Address counter,
                                            RegisterValue context) {
            model.requireExecute(thread, counter.getOffset(), 1);
        }

        @Override
        public void beforeExecuteInstruction(PcodeThread<byte[]> thread,
                                             Instruction instruction, PcodeProgram program) {
            model.requireExecute(
                thread, instruction.getAddress().getOffset(), instruction.getLength());
            String mnemonic = instruction.getMnemonicString();
            interruptReturn = "eiret".equals(mnemonic);
            automaticPriorityReturn = interruptReturn
                && (model.processorRegister(thread, "PSW") & 0x40) == 0
                && (model.processorRegister(thread, "INTCFG") & 1) == 0;
            Register destination = "ldsr".equals(mnemonic) ? instruction.getRegister(1) : null;
            protectedIsprWrite = destination != null && "ISPR".equals(destination.getName())
                && (model.processorRegister(thread, "INTCFG") & 1) == 0;
            if (automaticPriorityReturn || protectedIsprWrite) {
                isprBeforeInstruction = model.processorRegister(thread, "ISPR");
            }
        }

        @Override
        public void beforeLoad(PcodeThread<byte[]> thread, PcodeOp op, AddressSpace space,
                               byte[] offset, int size) {
            if (space.equals(language.getDefaultSpace())) model.beforeRead(thread, offset(offset), size);
        }

        @Override
        public void beforeStore(PcodeThread<byte[]> thread, PcodeOp op, AddressSpace space,
                                byte[] offset, int size, byte[] value) {
            if (space.equals(language.getDefaultSpace())) {
                model.beforeWrite(thread, offset(offset), size, Arrays.copyOf(value, size));
            }
        }

        @Override
        public void afterStore(PcodeThread<byte[]> thread, PcodeOp op, AddressSpace space,
                               byte[] offset, int size, byte[] value) {
            if (space.equals(language.getDefaultSpace())) {
                model.afterWrite(thread, offset(offset), size, Arrays.copyOf(value, size));
            }
        }

        @Override
        public void afterExecuteInstruction(PcodeThread<byte[]> thread, Instruction instruction) {
            if (automaticPriorityReturn) {
                model.processorRegister(thread, "ISPR", isprBeforeInstruction & (isprBeforeInstruction - 1));
            }
            else if (protectedIsprWrite) {
                model.processorRegister(thread, "ISPR", isprBeforeInstruction);
            }
            if (interruptReturn) {
                JsonObject event = new JsonObject();
                event.addProperty("kind", "interrupt-return");
                event.addProperty("pc", hex32(instruction.getAddress().getOffset()));
                event.addProperty("return_pc", hex32(model.pc(thread)));
                event.addProperty("scheduler_tick", model.trace.instructions + 1);
                model.trace.deviceEvents.add(event);
            }
            switch (instruction.getMnemonicString()) {
                case "synce" -> model.trace.sync("SYNCE");
                case "syncm" -> model.trace.sync("SYNCM");
                case "syncp" -> model.trace.sync("SYNCP");
                case "synci" -> model.trace.sync("SYNCI");
                default -> { }
            }
            model.trace.instructions++;
            model.trace.executed.add(instruction.getAddress().getOffset());
            model.trace.recentPcs.add(instruction.getAddress().getOffset());
            if (model.trace.recentPcs.size() > 16) model.trace.recentPcs.remove(0);
            model.dispatchDueEvents();
        }

        @Override
        public <A, U> AddressSetView readUninitialized(PcodeThread<byte[]> thread,
                PcodeExecutorStatePiece<A, U> piece, AddressSetView set, Reason reason) {
            Address reinitAddress = set.getMinAddress();
            if (reinitAddress != null && reason == Reason.RE_INIT
                    && reinitAddress.getAddressSpace().isRegisterSpace()) {
                PcodeExecutorStatePiece<A, byte[]> concrete =
                    PcodeStateCallbacks.checkValueDomain(piece, byte[].class);
                if (concrete == null) {
                    throw new IllegalStateException(
                        "RH850 machine requires concrete register state");
                }
                for (AddressRange range : set.getAddressRanges()) {
                    long reinitLength = range.getLength();
                    if (reinitLength > Integer.MAX_VALUE) {
                        throw new IllegalStateException(
                            "oversized register initialization range");
                    }
                    concrete.setVar(range.getMinAddress(), (int) reinitLength, false,
                        new byte[(int) reinitLength]);
                }
                return set;
            }
            Address address = set.getMinAddress();
            if (address == null) {
                throw model.fault("uninitialized-read", thread, 0, 0, "read", "unknown",
                    "empty uninitialized address set");
            }
            long length = set.getNumAddresses();
            int size = length > Integer.MAX_VALUE ? Integer.MAX_VALUE : (int) length;
            throw model.uninitialized(thread, address.getOffset(), size,
                address.getAddressSpace().getName(), reason);
        }
    }

    public static final class Rh850Userops extends AnnotatedPcodeUseropLibrary<byte[]> {
        @PcodeUserop public void __nop() {}
        @PcodeUserop public void __synchronize() {}
        @PcodeUserop public void __disable_irq() {}
        @PcodeUserop public void __enable_irq() {}
        @PcodeUserop public void __snooze() { throw new MachineHalt("SNOOZE"); }
        @PcodeUserop public void __halt() { throw new MachineHalt("HALT"); }
    }

    static long parseUnsigned(String value) {
        if (value == null) throw new IllegalArgumentException("missing integer string");
        String text = value.trim().replace("_", "");
        if (text.startsWith("0x") || text.startsWith("0X")) {
            return Long.parseUnsignedLong(text.substring(2), 16);
        }
        return Long.parseUnsignedLong(text, 10);
    }

    static String hex32(long value) {
        return String.format("0x%08X", value & 0xffffffffL);
    }

    static byte[] bytes(long value, int size, boolean bigEndian) {
        return Arrays.copyOf(Utils.longToBytes(value, size, bigEndian), size);
    }

    static byte[] parseHex(String value) {
        String text = value.replace(" ", "").replace("_", "");
        if ((text.length() & 1) != 0) throw new IllegalArgumentException("odd-length hex bytes");
        byte[] out = new byte[text.length() / 2];
        for (int i = 0; i < out.length; i++) {
            out[i] = (byte) Integer.parseInt(text.substring(i * 2, i * 2 + 2), 16);
        }
        return out;
    }

    static String sha256(byte[] value) throws Exception {
        byte[] digest = MessageDigest.getInstance("SHA-256").digest(value);
        StringBuilder out = new StringBuilder();
        for (byte b : digest) out.append(String.format("%02x", b & 0xff));
        return out.toString();
    }

    static void requireKeys(JsonObject object, Set<String> allowed, String context) {
        for (String key : object.keySet()) {
            if (!allowed.contains(key)) {
                throw new IllegalArgumentException(context + " contains unsupported field: " + key);
            }
        }
    }

    private static <T extends Throwable> T cause(Throwable value, Class<T> type) {
        Throwable current = value;
        while (current != null) {
            if (type.isInstance(current)) return type.cast(current);
            current = current.getCause();
        }
        return null;
    }
    private String shapeHash(List<Instruction> instructions) throws Exception {
        StringBuilder canonical = new StringBuilder();
        for (Instruction instruction : instructions) {
            canonical.append(instruction.getMnemonicString().toLowerCase())
                .append(':').append(instruction.getLength()).append('\n');
        }
        return sha256(canonical.toString().getBytes(StandardCharsets.UTF_8));
    }

    private boolean requirementsMatch(
            List<Instruction> instructions, List<EntryRequirement> requirements) {
        for (EntryRequirement requirement : requirements) {
            if (requirement.index < 0 || requirement.index >= instructions.size()) return false;
            Instruction instruction = instructions.get(requirement.index);
            if (!instruction.getMnemonicString().equalsIgnoreCase(requirement.mnemonic)) return false;
            if (requirement.scalar != null) {
                if (requirement.operand == null) return false;
                Scalar scalar = instruction.getScalar(requirement.operand);
                if (scalar == null || scalar.getUnsignedValue() != parseUnsigned(requirement.scalar)) {
                    return false;
                }
            }
        }
        return true;
    }

    private List<SelectorCandidate> functionCandidates(
            EntrySelector selector, long imageBase, int imageSize) throws Exception {
        List<SelectorCandidate> matches = new ArrayList<>();
        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
        while (functions.hasNext()) {
            Function function = functions.next();
            long address = function.getEntryPoint().getOffset();
            if (address < imageBase || address >= imageBase + imageSize) continue;
            long bodyLength = function.getBody().getNumAddresses();
            if (bodyLength != selector.body_size
                    || function.getBody().getMinAddress().getOffset() != address
                    || function.getBody().getMaxAddress().getOffset() - address + 1 != bodyLength) {
                continue;
            }
            List<Instruction> instructions = new ArrayList<>();
            InstructionIterator iterator =
                currentProgram.getListing().getInstructions(function.getBody(), true);
            while (iterator.hasNext()) instructions.add(iterator.next());
            if (instructions.size() != selector.instruction_count
                    || !shapeHash(instructions).equalsIgnoreCase(selector.shape_sha256)
                    || !requirementsMatch(instructions, selector.requirements)) {
                continue;
            }
            matches.add(new SelectorCandidate(address, Math.toIntExact(bodyLength), instructions));
        }
        return matches;
    }

    private List<SelectorCandidate> instructionCandidates(
            EntrySelector selector, long imageBase, int imageSize) throws Exception {
        List<Instruction> all = new ArrayList<>();
        InstructionIterator iterator =
            currentProgram.getListing().getInstructions(currentProgram.getMemory(), true);
        while (iterator.hasNext()) {
            Instruction instruction = iterator.next();
            long address = instruction.getAddress().getOffset();
            if (address >= imageBase && address < imageBase + imageSize) all.add(instruction);
        }
        List<SelectorCandidate> matches = new ArrayList<>();
        for (int start = 0; start + selector.instruction_count <= all.size(); start++) {
            List<Instruction> sequence =
                all.subList(start, start + selector.instruction_count);
            long expected = sequence.get(0).getAddress().getOffset();
            int bodySize = 0;
            boolean contiguous = true;
            for (Instruction instruction : sequence) {
                if (instruction.getAddress().getOffset() != expected) {
                    contiguous = false;
                    break;
                }
                bodySize += instruction.getLength();
                expected += instruction.getLength();
            }
            if (!contiguous || bodySize != selector.body_size
                    || !shapeHash(sequence).equalsIgnoreCase(selector.shape_sha256)
                    || !requirementsMatch(sequence, selector.requirements)) {
                continue;
            }
            matches.add(new SelectorCandidate(
                sequence.get(0).getAddress().getOffset(), bodySize, new ArrayList<>(sequence)));
        }
        return matches;
    }

    private ResolvedEntry resolveEntry(
            EntrySelector selector, byte[] codeflash, long imageBase) throws Exception {
        if (selector == null || selector.role == null || selector.role.isBlank()) {
            throw new IllegalArgumentException("entry selector is incomplete");
        }
        if ("resolved-address".equals(selector.scope)) {
            if (selector.address == null) {
                throw new IllegalArgumentException("resolved entry selector has no address");
            }
            long resolved = parseUnsigned(selector.address);
            if (resolved < imageBase || resolved >= imageBase + codeflash.length) {
                throw new IllegalArgumentException(
                    "resolved entry leaves CodeFlash: " + hex32(resolved));
            }
            Instruction instruction = currentProgram.getListing().getInstructionAt(
                currentProgram.getLanguage().getDefaultSpace().getAddress(resolved));
            if (instruction == null) {
                throw new IllegalArgumentException(
                    "resolved entry is not an instruction: " + hex32(resolved));
            }
            int offset = Math.toIntExact(resolved - imageBase);
            String instructionHash = sha256(Arrays.copyOfRange(
                codeflash, offset, offset + instruction.getLength()));
            JsonObject proof = new JsonObject();
            proof.addProperty("role", selector.role);
            proof.addProperty("scope", selector.scope);
            proof.addProperty("source", "dump-resolved runtime contract");
            proof.addProperty("candidate_count", 1);
            proof.addProperty("base_address", hex32(resolved));
            proof.addProperty("offset", 0);
            proof.addProperty("resolved_address", hex32(resolved));
            proof.addProperty("matched_code_sha256", instructionHash);
            proof.addProperty("entry_instruction_sha256", instructionHash);
            return new ResolvedEntry(resolved, proof);
        }
        if (selector.shape_sha256 == null || selector.shape_sha256.length() != 64
                || selector.instruction_count <= 0 || selector.body_size <= 0) {
            throw new IllegalArgumentException("entry selector is incomplete");
        }
        List<SelectorCandidate> matches;
        if ("function".equals(selector.scope)) {
            matches = functionCandidates(selector, imageBase, codeflash.length);
        }
        else if ("instructions".equals(selector.scope)) {
            matches = instructionCandidates(selector, imageBase, codeflash.length);
        }
        else {
            throw new IllegalArgumentException("unsupported entry selector scope: " + selector.scope);
        }
        if (matches.size() != 1) {
            throw new IllegalArgumentException(
                "entry role " + selector.role + " resolved to " + matches.size() + " candidates");
        }
        SelectorCandidate match = matches.get(0);
        long resolved = match.address + selector.offset;
        if (resolved < imageBase || resolved >= imageBase + codeflash.length) {
            throw new IllegalArgumentException("resolved entry leaves CodeFlash: " + hex32(resolved));
        }
        Instruction entryInstruction = currentProgram.getListing().getInstructionAt(
            currentProgram.getLanguage().getDefaultSpace().getAddress(resolved));
        if (entryInstruction == null) {
            throw new IllegalArgumentException("resolved entry is not an instruction: " + hex32(resolved));
        }
        int bodyOffset = Math.toIntExact(match.address - imageBase);
        int entryOffset = Math.toIntExact(resolved - imageBase);
        JsonObject proof = new JsonObject();
        proof.addProperty("role", selector.role);
        proof.addProperty("scope", selector.scope);
        proof.addProperty("shape_sha256", selector.shape_sha256.toLowerCase());
        proof.addProperty("candidate_count", matches.size());
        proof.addProperty("base_address", hex32(match.address));
        proof.addProperty("offset", selector.offset);
        proof.addProperty("resolved_address", hex32(resolved));
        proof.addProperty("matched_code_sha256", sha256(Arrays.copyOfRange(
            codeflash, bodyOffset, bodyOffset + match.bodySize)));
        proof.addProperty("entry_instruction_sha256", sha256(Arrays.copyOfRange(
            codeflash, entryOffset, entryOffset + entryInstruction.getLength())));
        return new ResolvedEntry(resolved, proof);
    }


    private byte[] loadImage(ImageDef image, String label) throws Exception {
        Path path = Path.of(image.path);
        byte[] bytes = Files.readAllBytes(path);
        if (bytes.length != image.size) {
            throw new IllegalArgumentException(label + " size drift: " + bytes.length + " != " + image.size);
        }
        String actual = sha256(bytes);
        if (!actual.equalsIgnoreCase(image.sha256)) {
            throw new IllegalArgumentException(label + " SHA-256 drift: " + actual);
        }
        return bytes;
    }

    private void setRegister(PcodeThread<byte[]> thread, SleighLanguage language,
                             String name, long value) {
        Register register = language.getRegister(name);
        if (register == null) throw new IllegalArgumentException("unknown processor register: " + name);
        thread.getState().setVar(register, bytes(value, register.getNumBytes(), language.isBigEndian()));
    }

    private void initializeMemoryRows(Model model, List<MemoryInit> rows) {
        for (MemoryInit init : rows) {
            long address = parseUnsigned(init.address);
            byte[] value;
            if (init.hex != null) {
                if (init.size != null) throw new IllegalArgumentException("memory init cannot combine hex and size");
                value = parseHex(init.hex);
            }
            else {
                if (init.size == null || init.size <= 0) {
                    throw new IllegalArgumentException("filled memory init requires positive size");
                }
                if (init.fill == null || init.fill < 0 || init.fill > 255) {
                    throw new IllegalArgumentException("memory fill must be one byte");
                }
                value = new byte[init.size];
                Arrays.fill(value, (byte) (init.fill & 0xff));
            }
            model.initializeMemory(address, value, init.evidence);
        }
    }

    private void initializeScenario(Model model, PcodeThread<byte[]> thread,
                                    SleighLanguage language, Scenario scenario) throws Exception {
        for (Map.Entry<String, String> row : scenario.registers.entrySet()) {
            setRegister(thread, language, row.getKey(), parseUnsigned(row.getValue()));
        }
        initializeMemoryRows(model, scenario.memory);
        for (ArtifactLoad load : scenario.artifacts) {
            Path path = Path.of(load.path);
            byte[] value = Files.readAllBytes(path);
            String digest = sha256(value);
            if (!digest.equalsIgnoreCase(load.sha256)) {
                throw new IllegalArgumentException("artifact SHA-256 drift: " + path);
            }
            long address = parseUnsigned(load.address);
            RegionDef region = model.region(address, value.length);
            if (region == null || (load.executable && !region.executable)) {
                throw new IllegalArgumentException("artifact load does not fit requested memory permissions at "
                    + hex32(address));
            }
            model.initializeMemory(address, value, load.evidence);
        }
    }

    private List<JsonObject> evaluateChecks(Model model, PcodeThread<byte[]> thread,
                                            SleighLanguage language, Scenario scenario) {
        List<JsonObject> results = new ArrayList<>();
        for (CheckDef check : scenario.checks) {
            JsonObject result = new JsonObject();
            result.addProperty("name", check.name);
            result.addProperty("kind", check.kind);
            boolean passed;
            String actual;
            String expected = check.equals != null ? check.equals : check.equals_hex;
            try {
                switch (check.kind) {
                    case "register": {
                        Register register = language.getRegister(check.register);
                        if (register == null) throw new IllegalArgumentException("unknown check register: " + check.register);
                        byte[] value = thread.getState().getVar(register, Reason.INSPECT);
                        long number = Utils.bytesToLong(value, value.length, language.isBigEndian());
                        actual = hex32(number);
                        passed = number == parseUnsigned(check.equals);
                        break;
                    }
                    case "memory": {
                        if (check.size == null || check.size <= 0) {
                            throw new IllegalArgumentException("memory check requires positive size");
                        }
                        long address = parseUnsigned(check.address);
                        byte[] value = model.emulator.getSharedState().getVar(
                            model.memorySpace, address, check.size, true, Reason.INSPECT);
                        StringBuilder text = new StringBuilder();
                        for (byte b : value) text.append(String.format("%02x", b & 0xff));
                        actual = text.toString();
                        passed = actual.equalsIgnoreCase(check.equals_hex);
                        break;
                    }
                    case "sync-count": {
                        Long count = model.trace.syncCounts.get(check.operation);
                        if (count == null) throw new IllegalArgumentException("unknown sync operation: " + check.operation);
                        actual = Long.toString(count);
                        passed = count == parseUnsigned(check.equals);
                        break;
                    }
                    case "event-count": {
                        long count = model.trace.deviceEvents.stream()
                            .filter(row -> row.has("kind")
                                && row.get("kind").getAsString().equals(check.operation))
                            .count();
                        actual = Long.toString(count);
                        passed = count == parseUnsigned(check.equals);
                        break;
                    }
                    default:
                        throw new IllegalArgumentException("unknown check kind: " + check.kind);
                }
            }
            catch (RuntimeException exc) {
                MachineFault inspectionFault = cause(exc, MachineFault.class);
                if (inspectionFault == null) throw exc;
                result.add("error", inspectionFault.toJson());
                actual = "unavailable";
                passed = false;
            }
            result.addProperty("expected", expected);
            result.addProperty("actual", actual);
            result.addProperty("passed", passed);
            results.add(result);
        }
        return results;
    }

    private JsonObject reportBase(
            RunContract contract, Scenario scenario, Trace trace, JsonObject resolution) {
        JsonObject report = new JsonObject();
        report.addProperty("schema", "rh850-p1me-machine-report-v2");
        report.addProperty("target", contract.target.name);
        report.addProperty("mcu", contract.target.mcu);
        report.addProperty("scenario", scenario.name);
        report.addProperty("engine", "Ghidra PcodeEmulator");
        report.addProperty("codeflash_sha256", contract.target.codeflash.sha256);
        report.addProperty("model_sha256", contract.model_sha256);
        report.addProperty("executable_overlays", false);
        report.add("entry_resolution", resolution);
        JsonObject resolvedContract = new JsonObject();
        resolvedContract.add("entry", resolution.deepCopy());
        resolvedContract.add("stop_addresses", GSON.toJsonTree(scenario.stop_addresses));
        resolvedContract.addProperty("max_instructions", scenario.max_instructions);
        resolvedContract.addProperty("reset", scenario.reset);
        resolvedContract.add("events", GSON.toJsonTree(scenario.events));
        report.add("resolved_run_contract", resolvedContract);
        report.addProperty("instruction_count", trace.instructions);
        report.addProperty("unique_instruction_addresses", trace.executed.size());
        JsonArray recent = new JsonArray();
        for (long pc : trace.recentPcs) recent.add(hex32(pc));
        report.add("recent_pcs", recent);
        report.add("sync_counts", GSON.toJsonTree(trace.syncCounts));
        report.add("memory_accesses", GSON.toJsonTree(trace.memoryAccesses));
        report.add("device_events", GSON.toJsonTree(trace.deviceEvents));
        return report;
    }

    private JsonObject runScenario(
            RunContract contract, MachineSpec machineSpec, SleighLanguage language,
            Scenario scenario, byte[] codeflash, byte[] dataflash) throws Exception {
        ResolvedEntry resolved = resolveEntry(
            scenario.entry, codeflash, parseUnsigned(contract.target.codeflash.base));
        Trace trace = new Trace();
        Model model = new Model(language, machineSpec, trace);
        Callbacks callbacks = new Callbacks(language, model);
        PcodeEmulator emulator = new PcodeEmulator(language, callbacks) {
            @Override
            protected PcodeUseropLibrary<byte[]> createUseropLibrary() {
                return new Rh850Userops();
            }
        };
        model.attach(emulator);
        PcodeThread<byte[]> thread = emulator.newThread("PE1");
        model.initializeProcessorReset(thread);
        model.setMemory(parseUnsigned(contract.target.codeflash.base), codeflash);
        if (contract.target.dataflash != null) {
            model.setMemory(parseUnsigned(contract.target.dataflash.base), dataflash);
        }
        model.initializeResetRegisters();
        initializeMemoryRows(model, scenario.pre_reset_memory);
        model.applyReset(scenario.reset);
        initializeScenario(model, thread, language, scenario);

        model.externalEvents = new ArrayList<>(scenario.events);
        model.externalEvents.sort(Comparator.comparingLong(event -> event.after_instructions));
        thread.overrideCounter(language.getDefaultSpace().getAddress(resolved.address));
        thread.overrideContextWithDefault();
        Set<Long> stops = new HashSet<>();
        for (String value : scenario.stop_addresses) stops.add(parseUnsigned(value));

        MachineFault fault = null;
        MachineHalt halt = null;
        try {
            while (trace.instructions < scenario.max_instructions
                    && !stops.contains(thread.getCounter().getOffset())) {
                model.dispatchDueEvents();
                model.dispatchExternalEvents(thread);
                model.deliverInterrupt(thread);
                thread.stepInstruction();
            }
        }
        catch (RuntimeException exc) {
            fault = cause(exc, MachineFault.class);
            halt = cause(exc, MachineHalt.class);
            if (fault == null && halt == null) throw exc;
        }

        JsonObject report = reportBase(contract, scenario, trace, resolved.proof);
        long finalPc = thread.getCounter().getOffset();
        report.addProperty("final_pc", hex32(finalPc));
        if (fault != null) report.add("fault", fault.toJson());
        if (halt != null) report.addProperty("halt", halt.operation);

        List<JsonObject> checks = evaluateChecks(model, thread, language, scenario);
        report.add("checks", GSON.toJsonTree(checks));
        boolean checksPassed = checks.stream().allMatch(row -> row.get("passed").getAsBoolean());
        boolean passed;
        String termination;
        if (scenario.expected_fault != null) {
            ExpectedFault expected = scenario.expected_fault;
            boolean expectedFault = fault != null
                && (expected.kind == null || expected.kind.equals(fault.kind))
                && (expected.address == null || parseUnsigned(expected.address) == fault.address)
                && (expected.access == null || expected.access.equals(fault.access));
            passed = expectedFault && checksPassed;
            termination = expectedFault ? "expected-fault"
                : fault != null ? "unexpected-fault" : "missing-expected-fault";
        }
        else {
            boolean atStop = stops.contains(finalPc);
            boolean completed = halt != null || atStop;
            passed = fault == null && completed && checksPassed;
            termination = fault != null ? "unexpected-fault"
                : halt != null ? "halt"
                : atStop ? "stop-address"
                : trace.instructions >= scenario.max_instructions ? "instruction-budget"
                : "incomplete";
        }
        report.addProperty("termination_reason", termination);
        report.addProperty("passed", passed);
        report.addProperty("status",
            passed && scenario.expected_fault != null
                ? "verified-expected-fault"
                : passed ? "verified-local-execution" : "failed");
        report.addProperty("evidence_boundary",
            "exact firmware bytes plus explicit manual/recovered model rules; no silicon or vehicle claim");
        return report;
    }

    private void validateScenarioJson(JsonObject scenarioJson) {
        requireKeys(scenarioJson, Set.of("schema", "name", "entry", "max_instructions",
            "stop_addresses", "registers", "memory", "pre_reset_memory", "artifacts", "checks",
            "expected_fault", "reset", "events"), "scenario");
        JsonObject entry = scenarioJson.getAsJsonObject("entry");
        if ("resolved-address".equals(entry.get("scope").getAsString())) {
            requireKeys(entry, Set.of("role", "scope", "address"), "entry selector");
        }
        else {
            requireKeys(entry, Set.of("role", "scope", "shape_sha256", "instruction_count",
                "body_size", "offset", "requirements"), "entry selector");
            JsonArray requirements = entry.getAsJsonArray("requirements");
            for (JsonElement element : requirements) {
                requireKeys(element.getAsJsonObject(),
                    Set.of("index", "mnemonic", "operand", "scalar"), "entry requirement");
            }
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) {
            throw new IllegalArgumentException("expected contract JSON and report JSON paths");
        }
        Path contractPath = Path.of(args[0]);
        Path reportPath = Path.of(args[1]);
        JsonObject contractJson = GSON.fromJson(Files.readString(contractPath), JsonObject.class);
        requireKeys(contractJson,
            Set.of("schema", "target", "model_path", "model_sha256", "scenarios"),
            "run contract");
        for (JsonElement scenarioJson : contractJson.getAsJsonArray("scenarios")) {
            validateScenarioJson(scenarioJson.getAsJsonObject());
        }
        RunContract contract = GSON.fromJson(contractJson, RunContract.class);
        if (!CONTRACT_SCHEMA.equals(contract.schema)) {
            throw new IllegalArgumentException("run contract schema drift");
        }
        if (contract.scenarios == null || contract.scenarios.isEmpty()) {
            throw new IllegalArgumentException("run contract requires at least one scenario");
        }
        for (Scenario scenario : contract.scenarios) {
            if (!SCENARIO_SCHEMA.equals(scenario.schema)) {
                throw new IllegalArgumentException("scenario schema drift: " + scenario.name);
            }
            if (scenario.max_instructions <= 0) {
                throw new IllegalArgumentException("max_instructions must be positive: " + scenario.name);
            }
        }

        byte[] modelBytes = Files.readAllBytes(Path.of(contract.model_path));
        if (!sha256(modelBytes).equalsIgnoreCase(contract.model_sha256)) {
            throw new IllegalArgumentException("machine model SHA-256 drift");
        }
        MachineSpec machineSpec = GSON.fromJson(
            new String(modelBytes, StandardCharsets.UTF_8), MachineSpec.class);
        if (!MODEL_SCHEMA.equals(machineSpec.schema)) {
            throw new IllegalArgumentException("machine model schema drift");
        }
        boolean productSupported = machineSpec.products.stream()
            .anyMatch(product -> product.product_id.equals(contract.target.mcu));
        if (!productSupported) {
            throw new IllegalArgumentException("machine model does not describe MCU " + contract.target.mcu);
        }

        SleighLanguage language = (SleighLanguage) currentProgram.getLanguage();
        if (!language.getLanguageID().getIdAsString().equals(contract.target.processor)) {
            throw new IllegalArgumentException("processor mismatch: " + language.getLanguageID());
        }
        byte[] codeflash = loadImage(contract.target.codeflash, "CodeFlash");
        byte[] dataflash = contract.target.dataflash == null
            ? null : loadImage(contract.target.dataflash, "DataFlash");

        JsonArray reports = new JsonArray();
        boolean passed = true;
        for (Scenario scenario : contract.scenarios) {
            JsonObject report;
            try {
                report = runScenario(
                    contract, machineSpec, language, scenario, codeflash, dataflash);
            }
            catch (Exception exc) {
                report = new JsonObject();
                report.addProperty("schema", "rh850-p1me-machine-report-v2");
                report.addProperty("target", contract.target.name);
                report.addProperty("mcu", contract.target.mcu);
                report.addProperty("scenario", scenario.name);
                report.addProperty("status", "failed");
                report.addProperty("passed", false);
                report.addProperty("termination_reason", "runner-error");
                JsonObject error = new JsonObject();
                error.addProperty("type", exc.getClass().getSimpleName());
                error.addProperty("detail", exc.getMessage());
                report.add("error", error);
            }
            reports.add(report);
            passed &= report.get("passed").getAsBoolean();
        }
        JsonObject batch = new JsonObject();
        batch.addProperty("schema", "rh850-p1me-machine-batch-report-v1");
        batch.addProperty("target", contract.target.name);
        batch.addProperty("mcu", contract.target.mcu);
        batch.addProperty("passed", passed);
        batch.add("reports", reports);
        Files.createDirectories(reportPath.getParent());
        Files.writeString(reportPath, GSON.toJson(batch) + "\n");
        println("P1ME_MACHINE_REPORT=" + reportPath);
        println("P1ME_MACHINE_RESULT=" + (passed ? "PASS" : "FAIL"));
        if (!passed) throw new IllegalStateException("P1M-E machine batch failed; see " + reportPath);
    }
}
