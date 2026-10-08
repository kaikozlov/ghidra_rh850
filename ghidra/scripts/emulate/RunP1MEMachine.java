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
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.pcode.PcodeOp;

import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
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
    private static final String CONTRACT_SCHEMA = "rh850-p1me-machine-run-v1";
    private static final String MODEL_SCHEMA = "rh850-p1me-machine-v1";
    private static final String SCENARIO_SCHEMA = "rh850-p1me-machine-scenario-v1";

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

    static final class RegionDef {
        String name;
        long start;
        long end_exclusive;
        int size;
        String access;
        boolean executable;
        String alias_group;
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

    static final class MachineSpec {
        String schema;
        List<String> product_ids;
        long p_bus_hz;
        List<RegionDef> regions;
        List<RegisterDef> registers;
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

    static final class Scenario {
        String schema;
        String name;
        String entry;
        long max_instructions;
        String reset = "none";
        List<String> stop_addresses = new ArrayList<>();
        Map<String, String> registers = new LinkedHashMap<>();
        List<MemoryInit> memory = new ArrayList<>();
        List<MemoryInit> pre_reset_memory = new ArrayList<>();
        List<ArtifactLoad> artifacts = new ArrayList<>();
        List<CheckDef> checks = new ArrayList<>();
        ExpectedFault expected_fault;
    }

    static final class RunContract {
        String schema;
        TargetDef target;
        String model_path;
        String model_sha256;
        Scenario scenario;
    }

    static final class Trace {
        long instructions;
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
            this.regions = new ArrayList<>(spec.regions);
            this.registers = new ArrayList<>(spec.registers);
            regions.sort(Comparator.comparingLong(row -> row.start));
            for (RegisterDef register : registers) registersByName.put(register.name, register);
            registers.sort(Comparator.comparingLong(row -> row.address));
            for (RegionDef region : regions) {
                if (region.alias_group != null) {
                    aliases.computeIfAbsent(region.alias_group, ignored -> new ArrayList<>()).add(region);
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
            for (RegionDef region : regions) if (region.contains(address, size)) return region;
            return null;
        }

        RegisterDef register(long address, int size) {
            for (RegisterDef register : registers) if (register.contains(address, size)) return register;
            return null;
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

        void initializeProcessorReset(PcodeThread<byte[]> thread) {
            Map<String, Long> resetValues = Map.of(
                "PSW", 0x20L,
                "MCTL", 0L,
                "MPM", 0L,
                "ASID", 0L
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
            trace.access("write", pc(thread), address, size, register.evidence);
        }

        void resetRegion(String name, String resetClass) {
            RegionDef region = null;
            for (RegionDef candidate : regions) {
                if (candidate.name.equals(name)) {
                    region = candidate;
                    break;
                }
            }
            if (region == null) throw new IllegalStateException("machine model lacks region " + name);
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
            event.addProperty("region", name);
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
            if (resetClass.equals("power-on")) {
                resetControl("STAC_LM0");
                resetControl("STAC_GRAM");
                resetRegion("local_ram_pe1", resetClass);
                resetRegion("global_ram", resetClass);
                return;
            }
            if (resetClass.equals("system-1-cvm")) {
                resetControl("STAC_LM0");
                resetControl("STAC_GRAM");
                resetRegion("local_ram_pe1", resetClass);
                resetRegion("global_ram", resetClass);
                return;
            }
            if (resetClass.equals("system-1-pin") || resetClass.equals("system-2")) {
                resetControl("STAC_GRAM");
                if (resetControlEnabled("STAC_LM0")) {
                    resetRegion("local_ram_pe1", resetClass);
                }
                resetRegion("global_ram", resetClass);
                return;
            }
            if (resetClass.equals("application-1")) {
                if (resetControlEnabled("STAC_LM0")) {
                    resetRegion("local_ram_pe1", resetClass);
                }
                if (resetControlEnabled("STAC_GRAM")) {
                    resetRegion("global_ram", resetClass);
                }
                return;
            }
            throw new IllegalArgumentException("unsupported reset class: " + resetClass);
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

        void validateDeviceWrite(PcodeThread<byte[]> thread, RegisterDef register,
                                 byte[] value) {
            if (register.name.equals("FACI_COMMAND_AREA")) {
                int command = value[0] & 0xff;
                if (command != 0x50) {
                    throw fault("unsupported-faci-command", thread, register.address,
                        value.length, "write", register.evidence,
                        String.format("FACI command 0x%02X has no implemented state transition",
                            command));
                }
                RegisterDef status = registersByName.get("FSTATR");
                long statusValue = unsigned(memory(thread, status.address, status.size));
                if ((statusValue & FSTATR_FRDY) == 0) {
                    throw fault("faci-not-ready", thread, register.address,
                        value.length, "write", register.evidence,
                        "FACI status-clear command requires FSTATR.FRDY=1");
                }
                RegisterDef accessStatus = registersByName.get("FASTAT");
                RegisterDef commandHistory = registersByName.get("FCMDR");
                memory(thread, accessStatus.address, accessStatus.size);
                memory(thread, commandHistory.address, commandHistory.size);
            }
            if (register.name.equals("ICUSCMD") && (unsigned(value) & 0xffff) != 5) {
                throw fault("unsupported-icus-command", thread, register.address,
                    value.length, "write", register.evidence,
                    String.format("ICU-S command 0x%04X has no recovered state transition",
                        unsigned(value) & 0xffff));
            }
            if ("rscfd".equals(register.behavior) && (unsigned(value) & 1) != 0) {
                long base = register.name.equals("CFDTMC16") ? 0xFFD24200L
                    : register.name.equals("CFDTMC_CH1_16") ? 0xFFD24400L : 0;
                if (base != 0) {
                    memory(thread, base, 4);
                    memory(thread, base + 4, 4);
                    memory(thread, base + 12, 4);
                    memory(thread, base + 16, 4);
                }
            }
            if ("tauj".equals(register.behavior)
                    && (register.name.equals("TAUJ0TS") || register.name.equals("TAUJ0TT"))) {
                memory(thread, registersByName.get("TAUJ0TE").address, 1);
                if (register.name.equals("TAUJ0TS")) {
                    long mask = unsigned(value) & 0xf;
                    for (int channel = 0; channel < 4; channel++) {
                        if ((mask & (1L << channel)) == 0) continue;
                        RegisterDef reload = registersByName.get("TAUJ0CDR" + channel);
                        memory(thread, reload.address, reload.size);
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
            event.addProperty("value", hex32(unsigned(value)));
            event.addProperty("evidence", register.evidence);
            trace.deviceEvents.add(event);
        }

        void handleRscfdWrite(PcodeThread<byte[]> thread, RegisterDef register, byte[] value) {
            if ((unsigned(value) & 1) == 0) return;
            long base;
            String statusName;
            if (register.name.equals("CFDTMC16")) {
                base = 0xFFD24200L;
                statusName = "CFDTMSTS_CH1";
            }
            else if (register.name.equals("CFDTMC_CH1_16")) {
                base = 0xFFD24400L;
                statusName = "CFDTMSTS_CH1_16";
            }
            else {
                return;
            }
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
                setRegisterValue(statusName, 0x04);
                setRegisterValue(register.name, 0);
            });
        }

        void handleTaujWrite(PcodeThread<byte[]> thread, RegisterDef register, byte[] value) {
            long mask = unsigned(value) & 0xf;
            if (!register.name.equals("TAUJ0TS") && !register.name.equals("TAUJ0TT")) return;
            long enabled = unsigned(memory(registersByName.get("TAUJ0TE").address, 1));
            boolean starting = register.name.equals("TAUJ0TS");
            long next = starting ? enabled | mask : enabled & ~mask;
            long issuePc = pc(thread);
            setRegisterValue("TAUJ0TE", next);
            scheduleNextTick(() -> {
                if (starting) {
                    for (int channel = 0; channel < 4; channel++) {
                        if ((mask & (1L << channel)) == 0) continue;
                        RegisterDef reload = registersByName.get("TAUJ0CDR" + channel);
                        RegisterDef counter = registersByName.get("TAUJ0CNT" + channel);
                        setMemory(counter.address, memory(reload.address, reload.size));
                    }
                }
                JsonObject event = new JsonObject();
                event.addProperty("kind", starting ? "tauj-start" : "tauj-stop");
                event.addProperty("pc", hex32(issuePc));
                event.addProperty("scheduler_tick", trace.instructions);
                event.addProperty("unit", 0);
                event.addProperty("channel_mask", String.format("0x%X", mask));
                event.addProperty("evidence", register.source_ref);
                trace.deviceEvents.add(event);
            });
        }

        void handleFaciWrite(PcodeThread<byte[]> thread, RegisterDef register, byte[] value) {
            if (!register.name.equals("FACI_COMMAND_AREA")) return;
            int command = value[0] & 0xff;
            if (command != 0x50) {
                throw new IllegalStateException("FACI write validation was bypassed");
            }
            long status = unsigned(memory(registersByName.get("FSTATR").address, 4));
            long accessStatus = unsigned(memory(registersByName.get("FASTAT").address, 1));
            long commandHistory = unsigned(memory(registersByName.get("FCMDR").address, 2));
            long nextStatus = status & ~FSTATR_STATUS_CLEAR_MASK;
            if ((accessStatus & FASTAT_ACCESS_ERROR_MASK) != 0) {
                nextStatus |= FSTATR_ILGLERR;
            }
            long nextAccessStatus = (nextStatus & FSTATR_COMMAND_LOCK_MASK) != 0
                ? accessStatus | FASTAT_CMDLK : accessStatus & ~FASTAT_CMDLK;
            faciSequence.add(command);
            setRegisterValue("FCMDR", (command << 8) | ((commandHistory >>> 8) & 0xff));
            setRegisterValue("FSTATR", nextStatus);
            setRegisterValue("FASTAT", nextAccessStatus);
            JsonObject event = new JsonObject();
            event.addProperty("kind", "faci-command");
            event.addProperty("pc", hex32(pc(thread)));
            event.addProperty("command", String.format("0x%02X", command));
            event.add("sequence", GSON.toJsonTree(faciSequence));
            event.addProperty("evidence", register.source_ref);
            trace.deviceEvents.add(event);
            faciSequence.clear();
        }

        void handleIcusWrite(PcodeThread<byte[]> thread, RegisterDef register, byte[] value) {
            if (!register.name.equals("ICUSCMD")) return;
            long word = unsigned(value);
            JsonObject event = new JsonObject();
            event.addProperty("kind", "icus-command");
            event.addProperty("pc", hex32(pc(thread)));
            event.addProperty("selector", (word >>> 16) & 0xffff);
            event.addProperty("command", word & 0xffff);
            event.addProperty("evidence", register.source_ref);
            trace.deviceEvents.add(event);
            setRegisterValue("ICUSSTS", 0);
            setRegisterValue("ICUSSTS2", 0);
        }

        void handleRegisterWrite(PcodeThread<byte[]> thread, long address, int size, byte[] value) {
            RegisterDef register = register(address, size);
            if (register == null) return;
            registerWriteEvent(thread, register, value);
            if ("rscfd".equals(register.behavior)) handleRscfdWrite(thread, register, value);
            else if ("faci".equals(register.behavior)) handleFaciWrite(thread, register, value);
            else if ("icus_recovered".equals(register.behavior)) {
                handleIcusWrite(thread, register, value);
            }
            else if ("tauj".equals(register.behavior)) handleTaujWrite(thread, register, value);
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
            switch (instruction.getMnemonicString()) {
                case "synce" -> model.trace.sync("SYNCE");
                case "syncm" -> model.trace.sync("SYNCM");
                case "syncp" -> model.trace.sync("SYNCP");
                case "synci" -> model.trace.sync("SYNCI");
                default -> { }
            }
            model.trace.instructions++;
            model.trace.executed.add(instruction.getAddress().getOffset());
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
            result.addProperty("expected", expected);
            result.addProperty("actual", actual);
            result.addProperty("passed", passed);
            results.add(result);
        }
        return results;
    }

    private JsonObject reportBase(RunContract contract, Trace trace) {
        JsonObject report = new JsonObject();
        report.addProperty("schema", "rh850-p1me-machine-report-v1");
        report.addProperty("target", contract.target.name);
        report.addProperty("mcu", contract.target.mcu);
        report.addProperty("scenario", contract.scenario.name);
        report.addProperty("engine", "Ghidra PcodeEmulator");
        report.addProperty("codeflash_sha256", contract.target.codeflash.sha256);
        report.addProperty("model_sha256", contract.model_sha256);
        report.addProperty("executable_overlays", false);
        report.addProperty("instruction_count", trace.instructions);
        report.addProperty("unique_instruction_addresses", trace.executed.size());
        report.add("sync_counts", GSON.toJsonTree(trace.syncCounts));
        report.add("memory_accesses", GSON.toJsonTree(trace.memoryAccesses));
        report.add("device_events", GSON.toJsonTree(trace.deviceEvents));
        return report;
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
        requireKeys(contractJson, Set.of("schema", "target", "model_path", "model_sha256", "scenario"), "run contract");
        JsonObject scenarioJson = contractJson.getAsJsonObject("scenario");
        requireKeys(scenarioJson, Set.of("schema", "name", "entry", "max_instructions",
            "stop_addresses", "registers", "memory", "pre_reset_memory", "artifacts", "checks",
            "expected_fault", "reset"), "scenario");
        RunContract contract = GSON.fromJson(contractJson, RunContract.class);
        if (!CONTRACT_SCHEMA.equals(contract.schema)) throw new IllegalArgumentException("run contract schema drift");
        if (!SCENARIO_SCHEMA.equals(contract.scenario.schema)) throw new IllegalArgumentException("scenario schema drift");
        if (contract.scenario.max_instructions <= 0) throw new IllegalArgumentException("max_instructions must be positive");

        byte[] modelBytes = Files.readAllBytes(Path.of(contract.model_path));
        if (!sha256(modelBytes).equalsIgnoreCase(contract.model_sha256)) {
            throw new IllegalArgumentException("machine model SHA-256 drift");
        }
        MachineSpec machineSpec = GSON.fromJson(new String(modelBytes), MachineSpec.class);
        if (!MODEL_SCHEMA.equals(machineSpec.schema)) throw new IllegalArgumentException("machine model schema drift");
        if (!machineSpec.product_ids.contains(contract.target.mcu)) {
            throw new IllegalArgumentException("machine model does not support MCU " + contract.target.mcu);
        }

        SleighLanguage language = (SleighLanguage) currentProgram.getLanguage();
        if (!language.getLanguageID().getIdAsString().equals(contract.target.processor)) {
            throw new IllegalArgumentException("processor mismatch: " + language.getLanguageID());
        }

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

        byte[] codeflash = loadImage(contract.target.codeflash, "CodeFlash");
        model.setMemory(parseUnsigned(contract.target.codeflash.base), codeflash);
        if (contract.target.dataflash != null) {
            byte[] dataflash = loadImage(contract.target.dataflash, "DataFlash");
            model.setMemory(parseUnsigned(contract.target.dataflash.base), dataflash);
        }
        model.initializeResetRegisters();
        initializeMemoryRows(model, contract.scenario.pre_reset_memory);
        model.applyReset(contract.scenario.reset);
        initializeScenario(model, thread, language, contract.scenario);

        long entry = parseUnsigned(contract.scenario.entry);
        thread.overrideCounter(language.getDefaultSpace().getAddress(entry));
        thread.overrideContextWithDefault();
        Set<Long> stops = new HashSet<>();
        for (String value : contract.scenario.stop_addresses) stops.add(parseUnsigned(value));

        MachineFault fault = null;
        MachineHalt halt = null;
        try {
            while (trace.instructions < contract.scenario.max_instructions
                    && !stops.contains(thread.getCounter().getOffset())) {
                thread.stepInstruction();
            }
        }
        catch (RuntimeException exc) {
            fault = cause(exc, MachineFault.class);
            halt = cause(exc, MachineHalt.class);
            if (fault == null && halt == null) throw exc;
        }

        JsonObject report = reportBase(contract, trace);
        report.addProperty("final_pc", hex32(thread.getCounter().getOffset()));
        if (fault != null) report.add("fault", fault.toJson());
        if (halt != null) report.addProperty("halt", halt.operation);

        List<JsonObject> checks = evaluateChecks(model, thread, language, contract.scenario);
        report.add("checks", GSON.toJsonTree(checks));
        boolean checksPassed = checks.stream().allMatch(row -> row.get("passed").getAsBoolean());
        boolean passed;
        if (contract.scenario.expected_fault != null) {
            ExpectedFault expected = contract.scenario.expected_fault;
            passed = fault != null
                && (expected.kind == null || expected.kind.equals(fault.kind))
                && (expected.address == null || parseUnsigned(expected.address) == fault.address)
                && (expected.access == null || expected.access.equals(fault.access))
                && checksPassed;
        }
        else {
            boolean completed = halt != null
                || stops.contains(thread.getCounter().getOffset());
            passed = fault == null && completed && checksPassed;
        }
        report.addProperty("passed", passed);
        report.addProperty("status",
            passed && contract.scenario.expected_fault != null
                ? "verified-expected-fault"
                : passed ? "verified-local-execution" : "failed");
        report.addProperty("evidence_boundary",
            "exact firmware bytes plus manual/recovered model rules; no silicon or vehicle claim");
        Files.createDirectories(reportPath.getParent());
        Files.writeString(reportPath, GSON.toJson(report) + "\n");
        println("P1ME_MACHINE_REPORT=" + reportPath);
        println("P1ME_MACHINE_RESULT=" + (passed ? "PASS" : "FAIL"));
        if (!passed) throw new IllegalStateException("P1M-E machine scenario failed; see " + reportPath);
    }
}
