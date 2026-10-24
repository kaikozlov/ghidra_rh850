//@author kaikozlov
//@category Emulation
// Execute exact registered RH850/P1M-E firmware with strict machine-state provenance.
// Args: <absolute-run-contract-json> <absolute-report-json> [--instruction-trace]

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonWriter;
import ghidra.app.plugin.processors.sleigh.SleighLanguage;
import ghidra.app.script.GhidraScript;
import ghidra.framework.model.DomainObjectException;
import ghidra.pcode.emu.PcodeEmulationCallbacks;
import ghidra.pcode.emu.PcodeEmulator;
import ghidra.pcode.emu.PcodeMachine;
import ghidra.pcode.emu.PcodeThread;
import ghidra.pcode.exec.AnnotatedPcodeUseropLibrary;
import ghidra.pcode.exec.PcodeExecutor;
import ghidra.pcode.exec.PcodeExecutorStatePiece;
import ghidra.pcode.exec.PcodeStateCallbacks;
import ghidra.pcode.exec.PcodeExecutorStatePiece.Reason;
import ghidra.pcode.exec.BytesPcodeExecutorState;
import ghidra.pcode.exec.PcodeExecutorState;
import ghidra.pcode.exec.PcodeProgram;
import ghidra.pcode.exec.PcodeUseropLibrary;
import ghidra.pcode.exec.AnnotatedPcodeUseropLibrary.PcodeUserop;
import ghidra.pcode.utils.Utils;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.lang.InstructionPrototype;
import ghidra.program.model.lang.ProcessorContextImpl;
import ghidra.program.model.lang.Register;
import ghidra.program.model.lang.RegisterValue;
import ghidra.program.model.mem.ByteMemBufferImpl;
import ghidra.program.model.mem.MemoryAccessException;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.scalar.Scalar;
import java.io.BufferedWriter;
import java.io.Closeable;
import java.io.IOException;
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
        List<String> reset_classes = List.of();
        Long skipped_value;
        Long reset_mask;
        String behavior;
        String evidence;
        String source_ref;
        String description;
        String trigger;
        Long writable_mask;
        Long read_value;
        boolean read_input;
        Long sync_mask;
        Long active_mask;
        List<Long> allowed_values;
        String status_register;
        String secondary_status_register;
        List<String> capture_registers;
        List<Long> status_masks;
        List<Long> secondary_status_masks;
        Long protection_mask;
        Long protection_value;
        String access_register;
        String history_register;
        String start_address_register;
        String end_address_register;
        String mode_register;
        String emulation_register;
        String enable_register;
        String secondary_enable_register;
        Long payload_address;
        Long completion_value;
        Integer interrupt_channel;
        Integer interrupt_channel_base;
        String interrupt_register;
        String control_register;
        String pointer_register;
        String window_register;
        String channel_control_register;
        String global_control_register;
        Integer fifo_index;
        Integer fifo_channel;

        boolean contains(long candidate, int width) {
            long end = candidate + Integer.toUnsignedLong(width);
            return (Long.compareUnsigned(candidate, address) >= 0
                && Long.compareUnsigned(end, address + size) <= 0)
                // Wider functional read windows are opt-in, exact-base transactions.
                // This never makes the trailing byte lanes independent registers.
                || (candidate == address && width > size && access_widths.contains(width));
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

    static final class FlashCellRange {
        String address;
        int size;
        String state;
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
        String source_address;
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
        Long after_instructions;
        Long after_transmit_words;
        Long delay_instructions;
        Long after_spc_triggers;
        Long delay_hsb_cycles;
        int[] pulse_samples;
        transient long ordinal;
        String evidence;
        String address;
        String register;
        String value;
        String reset_class;
        String pin;
        String drive;
        Long p_bus_cycles;
        Integer fifo;
        Integer channel;
        Integer unit;
        String can_id;
        String data_hex;
        boolean extended;
        boolean fd;
        String boundary;
        int label;
        int timestamp;
    }

    static final class IcusStartupResponse {
        String command;
        String error_bits;
        long completion_hsb_cycles;
        transient long commandValue;
        transient long errorValue;
    }

    static final class IcusStartupConfig {
        String evidence;
        List<IcusStartupResponse> responses;
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
        List<FlashCellRange> dataflash_cells = new ArrayList<>();
        List<ArtifactLoad> artifacts = new ArrayList<>();
        List<CheckDef> checks = new ArrayList<>();
        List<ExternalEvent> events = new ArrayList<>();
        ExpectedFault expected_fault;
        String expected_termination;
        Long hsb_cycles_per_instruction;
        IcusStartupConfig icus_startup_stub;
        String dma_master_rewrite_assumption;
        boolean peripheral_file;
        List<String> bounded_entries;
        List<BoundedEdge> bounded_edges;

        boolean stubbed() {
            return icus_startup_stub != null || dma_master_rewrite_assumption != null;
        }
    }

    static final class BoundedEdge {
        String pc;
        String target;
        String entry;
    }

    static final class RunContract {
        String schema;
        TargetDef target;
        String model_path;
        String model_sha256;
        List<Scenario> scenarios;
    }

    /** Buffered trace storage: retain rows on disk, not for the lifetime of the emulator. */
    static final class JsonRows implements Closeable {
        final Path path;
        final BufferedWriter output;
        final JsonWriter writer;
        final Map<String, long[]> kindCounts;
        long count;
        boolean sealed;

        JsonRows(Path directory, String prefix, boolean countKinds) throws IOException {
            path = Files.createTempFile(directory, prefix, ".json");
            try {
                output = Files.newBufferedWriter(path, StandardCharsets.UTF_8);
            }
            catch (IOException exception) {
                Files.deleteIfExists(path);
                throw exception;
            }
            writer = new JsonWriter(output);
            kindCounts = countKinds ? new HashMap<>() : null;
            try {
                writer.beginArray();
            }
            catch (IOException exception) {
                try { close(); } catch (IOException cleanup) { exception.addSuppressed(cleanup); }
                throw exception;
            }
        }

        void add(JsonObject row) {
            if (sealed) throw new IllegalStateException("cannot append to a sealed trace");
            GSON.toJson(row, writer);
            count++;
            if (kindCounts != null && row.has("kind")) {
                String kind = row.get("kind").getAsString();
                long[] counter = kindCounts.get(kind);
                if (counter == null) {
                    counter = new long[1];
                    kindCounts.put(kind, counter);
                }
                counter[0]++;
            }
        }

        long size() { return count; }

        long countKind(String kind) {
            long[] counter = kindCounts.get(kind);
            return counter == null ? 0 : counter[0];
        }

        private static void copyValue(JsonReader input, JsonWriter output) throws IOException {
            switch (input.peek()) {
                case BEGIN_OBJECT:
                    input.beginObject();
                    output.beginObject();
                    while (input.hasNext()) {
                        output.name(input.nextName());
                        copyValue(input, output);
                    }
                    input.endObject();
                    output.endObject();
                    break;
                case BEGIN_ARRAY:
                    input.beginArray();
                    output.beginArray();
                    while (input.hasNext()) copyValue(input, output);
                    input.endArray();
                    output.endArray();
                    break;
                case STRING: output.value(input.nextString()); break;
                case NUMBER: output.jsonValue(input.nextString()); break;
                case BOOLEAN: output.value(input.nextBoolean()); break;
                case NULL: input.nextNull(); output.nullValue(); break;
                default: throw new IOException("unexpected token in trace spool: " + input.peek());
            }
        }

        void writeTo(JsonWriter destination) throws IOException {
            if (!sealed) {
                writer.endArray();
                writer.close();
                sealed = true;
            }
            try (JsonReader input = new JsonReader(Files.newBufferedReader(path, StandardCharsets.UTF_8))) {
                copyValue(input, destination);
            }
        }

        @Override
        public void close() throws IOException {
            // Cleanup also accepts a partial trace after a runner error.
            try { output.close(); }
            finally { Files.deleteIfExists(path); }
        }
    }

    static final class Trace implements Closeable {
        private static final int TRACE_CHUNK_SIZE = 16384;
        private static final int MAX_TRACE_ENTRIES = 16777216;
        final boolean instructionTraceEnabled;
        final List<int[]> instructionPcs = new ArrayList<>();
        final List<long[]> instructionTicks = new ArrayList<>();
        final List<JsonObject> instructionShortcuts = new ArrayList<>();
        int instructionTraceSize;
        long instructions;
        final List<Long> recentPcs = new ArrayList<>();
        final Set<Long> executed = new HashSet<>();
        final Map<String, Long> syncCounts = new LinkedHashMap<>();
        final JsonRows memoryAccesses;
        final JsonRows deviceEvents;
        final Set<Long> writtenBytes = new HashSet<>();
        boolean traceLostAddress;
        String busInitiator;

        Trace(boolean instructionTraceEnabled, Path directory) throws IOException {
            memoryAccesses = new JsonRows(directory, ".p1me-memory-", false);
            try {
                deviceEvents = new JsonRows(directory, ".p1me-events-", true);
            }
            catch (IOException | RuntimeException exception) {
                try { memoryAccesses.close(); }
                catch (IOException cleanup) { exception.addSuppressed(cleanup); }
                throw exception;
            }
            this.instructionTraceEnabled = instructionTraceEnabled;
            syncCounts.put("SYNCE", 0L);
            syncCounts.put("SYNCM", 0L);
            syncCounts.put("SYNCP", 0L);
            syncCounts.put("SYNCI", 0L);
        }

        @Override
        public void close() throws IOException {
            try (JsonRows memory = memoryAccesses; JsonRows events = deviceEvents) {
                // Both spools are closed/deleted even if one cleanup fails.
            }
        }

        void enterInstruction(long pc) {
            if (!instructionTraceEnabled) return;
            if (instructionTraceSize >= MAX_TRACE_ENTRIES) {
                throw new IllegalStateException(
                    "complete instruction trace exceeds " + MAX_TRACE_ENTRIES + " entries");
            }
            int chunk = instructionTraceSize / TRACE_CHUNK_SIZE;
            int offset = instructionTraceSize % TRACE_CHUNK_SIZE;
            if (offset == 0) {
                try {
                    instructionPcs.add(new int[TRACE_CHUNK_SIZE]);
                    instructionTicks.add(new long[TRACE_CHUNK_SIZE]);
                }
                catch (OutOfMemoryError error) {
                    throw new IllegalStateException("cannot allocate complete instruction trace", error);
                }
            }
            if ((pc & ~0xffffffffL) != 0) {
                throw new IllegalStateException("instruction trace PC outside 32-bit address space");
            }
            instructionPcs.get(chunk)[offset] = (int) pc;
            instructionTicks.get(chunk)[offset] = instructions;
            instructionTraceSize++;
        }

        void shortcut(String kind, long pc, long resumePc) {
            if (!instructionTraceEnabled) return;
            if (instructionShortcuts.size() >= 16384) {
                throw new IllegalStateException("complete instruction shortcut trace exceeds 16384 entries");
            }
            JsonObject row = new JsonObject();
            row.addProperty("kind", kind);
            row.addProperty("pc", hex32(pc));
            row.addProperty("resume_pc", hex32(resumePc));
            row.addProperty("instruction", instructions);
            instructionShortcuts.add(row);
        }

        void writeInstructionTrace(JsonWriter writer) throws Exception {
            writer.beginArray();
            for (int index = 0; index < instructionTraceSize; index++) {
                int chunk = index / TRACE_CHUNK_SIZE;
                int offset = index % TRACE_CHUNK_SIZE;
                writer.beginObject();
                writer.name("pc").value(hex32(Integer.toUnsignedLong(instructionPcs.get(chunk)[offset])));
                writer.name("instruction").value(instructionTicks.get(chunk)[offset]);
                writer.endObject();
            }
            writer.endArray();
        }

        void sync(String operation) {
            syncCounts.put(operation, syncCounts.get(operation) + 1);
        }

        void access(String kind, long pc, long address, int size, String evidence) {
            if (memoryAccesses.size() >= 1048576) {
                // A poll that rewrites the same slots does not hide a later
                // store. A write to an address the trace never recorded does.
                if ("write".equals(kind)) {
                    for (int offset = 0; offset < size; offset++) {
                        if (!writtenBytes.contains(address + offset)) {
                            traceLostAddress = true;
                            return;
                        }
                    }
                }
                return;
            }
            if ("write".equals(kind)) {
                for (int offset = 0; offset < size; offset++)
                    writtenBytes.add(address + offset);
            }
            JsonObject row = new JsonObject();
            row.addProperty("kind", kind);
            row.addProperty("pc", hex32(pc));
            row.addProperty("instruction", instructions);
            row.addProperty("address", hex32(address));
            row.addProperty("size", size);
            row.addProperty("evidence", evidence);
            if (busInitiator != null) row.addProperty("initiator", busInitiator);
            memoryAccesses.add(row);
        }
    }

    static final class ScheduledEvent {
        static final Comparator<ScheduledEvent> ORDER = Comparator
            .comparingLong((ScheduledEvent event) -> event.tick)
            .thenComparingLong(event -> event.ordinal);
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
        static final long FSTATR_FORCED_STOP_CLEAR_MASK = FSTATR_STATUS_CLEAR_MASK | 0x8b40;
        static final long FSTATR_CORRECTION_MASK = 0x10014;
        static final String[] FACI_SETUP_REGISTERS = {
            "FEADDR", "FPROTR", "FCPSR", "FSADDR", "FENTRYR", "FBCCNT", "FAREASELC"
        };
        static final Set<String> FACI_RESULT_REGISTERS =
            Set.of("FSTATR", "FASTAT", "FCMDR", "FBCSTAT", "FPSADDR");
        static final long RSCFD_TX_RAM_BASE = 0xFFD24000L;
        static final long RSCFD_TX_RECORD_SIZE = 0x20L;

        final SleighLanguage language;
        final MachineSpec spec;
        final Trace trace;
        // Shared-memory callbacks have no thread; retain PE1 for fault provenance.
        PcodeThread<byte[]> executionThread;
        final List<RegionDef> regions;
        final List<RegisterDef> registers;
        final Map<String, RegisterDef> registersByName = new HashMap<>();
        final Map<Integer, RegisterDef> interruptRegisters = new LinkedHashMap<>();
        final Map<Integer, ReceiveFifo> receiveFifos = new HashMap<>();
        // R01UH0585EJ0120 Table 17.132: CFDC and CFPLS encodings.
        static final int[] FIFO_DEPTHS = {0, 4, 8, 16, 32, 48, 64, 128};
        static final int[] PAYLOAD_LENGTHS = {8, 12, 16, 20, 24, 32, 48, 64};
        static final String[] PORT_PIN_REGISTERS = {
            "PFC", "PFCE", "PFCAE", "PM", "PIPC", "PMC", "PPR", "P", "PIBC",
            "PBDC", "PD", "PU", "PISA", "PDSC", "PUCC", "PODCE", "PODC", "PINV"
        };
        static final int[] PORT_PIN_BITS = {
            0, 1, 2, 4, 5, 6, 8, 12, 16, 17, 18, 19, 22, 24, 25, 27, 28, 30
        };
        record PortAliasField(RegisterDef source, long aliasMask, long pinMask) {}
        final Map<RegisterDef, List<PortAliasField>> portAliasFields = new HashMap<>();
        final Map<RegisterDef, List<RegisterDef>> portAliasDependents = new HashMap<>();
        static final String[][] ECM_STATUS_REGISTERS = {
            {"ECMMESSTR0", "ECMMESSTR1", "ECMMESSTR2"},
            {"ECMCESSTR0", "ECMCESSTR1", "ECMCESSTR2"}
        };
        static final String[] ECM_ERROR_MASK_REGISTERS = {"ECMEMK0", "ECMEMK1", "ECMEMK2"};
        static final String[][] ECM_NOTIFICATION_REGISTERS = {
            {"ECMMICFG0", "ECMMICFG1", "ECMMICFG2"},
            {"ECMNMICFG0", "ECMNMICFG1", "ECMNMICFG2"},
            {"ECMIRCFG0", "ECMIRCFG1", "ECMIRCFG2"},
            {"ECMDTMCFG0", "ECMDTMCFG1", "ECMDTMCFG2"}
        };
        final Tauj tauj;
        final Taud taud;
        final Tsg tsg;
        final Pic1 pic1;
        final Set<String> declaredTsgRegisters = new HashSet<>();
        RegionDef dataFlash;
        final PriorityQueue<ScheduledEvent> externalEvents = new PriorityQueue<>(ScheduledEvent.ORDER);
        final Map<String, Csih> csihControllers = new HashMap<>();
        final Map<RegisterDef, Csih> csihBindings = new HashMap<>();
        long registerBeforeWrite;
        boolean guardWriteIgnored;
        final RegisterDef[][] gramGuards = new RegisterDef[8][4];
        final Map<RegisterDef, String> peripheralGuards = new HashMap<>();
        final Map<String, GuardCapture> busGuardCaptures = new HashMap<>();
        final GuardCapture pegCapture;
        final GuardCapture gramDmaCapture;
        final Dma dma;
        final Adc adc;
        final Rsent rsent;
        long hsbCyclesPerInstruction;
        long hsbCycles;
        boolean discardBusStore;
        long segFlags;
        boolean segNotificationPending;
        int faciPendingCommand;
        long faciReadErrors;
        long faciDeadline = Long.MAX_VALUE;
        int faciOperation;
        long faciBlankFirst;
        long faciBlankCycles;
        int faciProgramStage;
        long faciTargetOffset;
        int faciTargetSize;
        final byte[] faciProgramData = new byte[4];
        byte[] dataFlashCells;
        // Physical4B cells: 0=undeclared,1=programmed,2=erased,3=interrupted/indeterminate.
        // Dump bytes remain a read-only source observation. A native erase or
        // interrupted write invalidates the emulator payload, not the source.
        boolean[] dataFlashPayloadInvalid;
        IcusStartupStub icusStartupStub;
        final Set<String> dcraSeeded = new HashSet<>();
        boolean cvmEnableWritten;
        int flmdStage;
        long flmdDesired;
        int ecmStage;
        int ecmCommandDomain;
        RegisterDef ecmTarget;
        long ecmDesired;
        // No declared drive means legacy sampled bit31 is authoritative.
        final String[] ecmExternalDrive = new String[2];
        final boolean[] ecmOutputLow = {true, true};
        final Set<String> initializedDeviceRegisters = new HashSet<>();
        final Set<String> missingResetInputs = new HashSet<>();
        // Scenario-supplied bus data is not command storage or effective device state.
        Map<String, Long> readInputResponses;
        boolean fieldBistExecuted;
        long resetFactorKnownMask;
        long unresolvedResetCauses;
        final Map<String, List<RegionDef>> aliases = new HashMap<>();
        final PriorityQueue<ScheduledEvent> scheduledEvents = new PriorityQueue<>(ScheduledEvent.ORDER);
        long nextEventOrdinal;
        PcodeEmulator emulator;
        AddressSpace memorySpace;
        boolean internalWrite;
        boolean peripheralFile;
        boolean peripheralPollBusy;
        // Same threshold as tools/camry_oracle.py PERIPHERAL_POLL_READS.
        static final int PERIPHERAL_POLL_READS = 4096;
        // Legacy peripheral-file exploration only; strict completion never counts reads.
        static final int ICCTRL_BUSY_READS = 4;
        int icctrlBusyReads;
        final Map<Long, Integer> peripheralPolls = new HashMap<>();
        long entrySp = -1;
        final List<long[]> scenarioFills = new ArrayList<>();
        final Set<Long> boundedEntries = new HashSet<>();
        final Map<Long, long[]> boundedEdges = new HashMap<>();
        final Map<Long, ArrayDeque<long[]>> boundedFrames = new HashMap<>();
        long scenarioEntry = -1;
        static final String[] BOUNDED_SAVED = {
            "r20", "r21", "r22", "r23", "r24", "r25", "r26", "r27", "r28", "r29", "ep", "lp",
        };

        Model(SleighLanguage language, MachineSpec spec, Trace trace, String productId) {
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
            resetFactorKnownMask = requiredRegister("reset controller", "status", "RESF").reset_mask;
            bindPortAliases();
            registers.sort(Comparator.comparingLong(row -> row.address));
            for (RegionDef region : regions) {
                if ("dataflash".equals(region.name)) dataFlash = region;
                if (region.alias_group != null) {
                    aliases.computeIfAbsent(region.alias_group, ignored -> new ArrayList<>()).add(region);
                }
            }
            for (RegisterDef register : registers) {
                if (register.window_register != null) {
                    receiveFifos.put(register.fifo_index, new ReceiveFifo(this, register));
                }
                String guard = peripheralReadGuard(register);
                if (guard != null) peripheralGuards.put(register, guard);
            }
            for (int index = 0; index < gramGuards.length; index++) {
                gramGuards[index][0] = requiredRegister("GRAM guard", "protection", "MGDGRPROT" + index);
                gramGuards[index][1] = requiredRegister("GRAM guard", "SPID", "MGDGRSPID" + index);
                gramGuards[index][2] = requiredRegister("GRAM guard", "base", "MGDGRBAD" + index);
                gramGuards[index][3] = requiredRegister("GRAM guard", "valid", "MGDGRADV" + index);
            }
            pegCapture = new GuardCapture("PGERRSTAT_PE1", "PGERRINFO_PE1", 64);
            gramDmaCapture = new GuardCapture("MGDGRSSTAT_VCI2GRAM", "MGDGRSTYPE_VCI2GRAM", 65);
            GuardCapture pfss0 = new GuardCapture("ERRSLVSTAT_PFSS0", "ERRSLVTYPE_PFSS0", 67);
            GuardCapture pfss1 = new GuardCapture("ERRSLVSTAT_PFSS1", "ERRSLVTYPE_PFSS1", 67);
            GuardCapture pbg0 = new GuardCapture("ERRSLV0STAT", "ERRSLV0TYPE", 67);
            GuardCapture pbg1 = new GuardCapture("ERRSLV1STAT", "ERRSLV1TYPE", 67);
            GuardCapture pbg2 = new GuardCapture("ERRSLV2STAT", "ERRSLV2TYPE", 67);
            GuardCapture pbg5 = new GuardCapture("ERRSLV5STAT", "ERRSLV5TYPE", 67);
            for (String guard : peripheralGuards.values()) {
                GuardCapture capture;
                if (guard.startsWith("APBFSGD"))
                    capture = guard.contains("PDMA") || guard.contains("INTC2") ? pfss0 : pfss1;
                else if (guard.startsWith("FSGD0")) capture = pbg0;
                else if (guard.startsWith("FSGD1")) capture = pbg1;
                else if (guard.startsWith("FSGD2")) capture = pbg2;
                else if (guard.startsWith("FSGD5")) capture = pbg5;
                else throw new IllegalStateException("unmapped guard capture bank: " + guard);
                busGuardCaptures.put(guard, capture);
            }
            busGuardCaptures.put("FSGD0PROT04", pbg0);
            dma = new Dma();
            adc = new Adc(productId);
            taud = new Taud();
            tauj = new Tauj();
            tsg = new Tsg();
            pic1 = new Pic1();
            rsent = new Rsent();
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
            PcodeThread<byte[]> source = thread == null ? executionThread : thread;
            return source == null || source.getCounter() == null ? 0 : source.getCounter().getOffset();
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

        void noteBoundedCall(PcodeThread<byte[]> thread, Instruction instruction) {
            // A jarl into a rewritten loop saves the caller's frame. The
            // back-edge returns there after one iteration, as the host does.
            if (!"jarl".equals(instruction.getMnemonicString())) return;
            long next = pc(thread);
            if (!boundedEntries.contains(next) || next == scenarioEntry) return;
            long[] saved = new long[1 + BOUNDED_SAVED.length];
            saved[0] = processorRegister(thread, "sp");
            for (int index = 0; index < BOUNDED_SAVED.length; index++) {
                saved[index + 1] = processorRegister(thread, BOUNDED_SAVED[index]);
            }
            boundedFrames.computeIfAbsent(next, key -> new ArrayDeque<>()).push(saved);
        }

        boolean returnBoundedCallee(PcodeThread<byte[]> thread) {
            long[] edge = boundedEdges.get(pc(thread));
            if (edge == null || edge[1] == scenarioEntry || !trace.executed.contains(edge[0])) {
                return false;
            }
            ArrayDeque<long[]> frames = boundedFrames.get(edge[1]);
            if (frames == null || frames.isEmpty()) return false;
            long[] saved = frames.pop();
            trace.shortcut("bounded-callee-return", pc(thread), saved[saved.length - 1]);
            processorRegister(thread, "sp", saved[0]);
            for (int index = 0; index < BOUNDED_SAVED.length; index++) {
                processorRegister(thread, BOUNDED_SAVED[index], saved[index + 1]);
            }
            thread.overrideCounter(memorySpace.getAddress(saved[saved.length - 1]));
            return true;
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
                Map.entry("MCFG0", 0x00020004L),
                Map.entry("HTCFG0", 0x00018000L),
                Map.entry("ASID", 0L),
                Map.entry("ISPR", 0L),
                Map.entry("PMR", 0L),
                Map.entry("INTCFG", 0L),
                Map.entry("ICSR", 0L),
                // P1M-E Table 3.55 overrides generic G3M's D1EIV reset value.
                Map.entry("ICCTRL", 0x00030003L),
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

        void requireMpu(PcodeThread<byte[]> thread, long address, int size,
                        String access, boolean user) {
            long mpm = processorRegister(thread, "MPM");
            if ((mpm & 1) == 0) return;
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

        boolean isGuard(RegisterDef register) {
            return "peg".equals(register.behavior) || "bus-guard".equals(register.behavior)
                || "gram-guard".equals(register.behavior);
        }

        RegisterDef guardLock(RegisterDef register) {
            long address = "peg".equals(register.behavior) ? (register.address & ~15L) + 4
                : "gram-guard".equals(register.behavior) ? register.address & ~15L
                : register.address & ~7L;
            RegisterDef lock = register(address, 4);
            if (lock == null || !isGuard(lock)) {
                throw new IllegalStateException(register.name + " lacks guard LOCK register");
            }
            return lock;
        }

        int cpuSpid(PcodeThread<byte[]> thread) {
            // Table3.29: reserved SPID0/1 are converted to SPID2 by hardware.
            return Math.max(2, (int) ((processorRegister(thread, "MCFG0") >>> 16) & 31));
        }

        String peripheralReadGuard(RegisterDef target) {
            // Table31.157: only documented module/channel assignments. PEG
            // monitors other masters, never the CPU's own local-RAM accesses.
            String name = target.name;
            long address = target.address;
            if (name.startsWith("APBFSGD")) return "APBFSGDPROT_PBG_A";
            if (name.startsWith("FSGD0")) return "FSGD0PROT00";
            if (name.startsWith("FSGD1")) return "FSGD1APROT00";
            if (name.startsWith("FSGD2")) return "FSGD2APROT00";
            if (name.startsWith("FSGD5")) return "FSGD5APROT00";
            if (name.startsWith("FSGDF0")) return "FSGD2APROT14";
            if (name.startsWith("PGERR") || (name.startsWith("MGDGRS") && name.endsWith("_PE1")))
                return "APBFSGDPROT_SP1_A";
            if (name.startsWith("MGDGR")) return "APBFSGDPROT_SP4_A";
            if (name.startsWith("ERRSLV") && name.contains("_PFSS")) return "APBFSGDPROT_SP4_A";
            if (name.startsWith("ERRSLV0")) return "FSGD0PROT00";
            if (name.startsWith("ERRSLV1")) return "FSGD1APROT00";
            if (name.startsWith("ERRSLV2")) return "FSGD2APROT00";
            if (name.startsWith("ERRSLV5")) return "FSGD5APROT00";
            if ("PDMA_COMP_CNTRL".equals(name)) return "APBFSGDPROT_SP4_A";
            if ("reset-controller".equals(target.behavior)) return "FSGD5APROT04";
            if (name.startsWith("BRAMDAT")) return "FSGD5CPROT04";
            if (name.startsWith("TAUJ0")) return "FSGD1APROT04";
            if (name.startsWith("TAUJ1")) return "FSGD1APROT06";
            if (name.startsWith("TAUD0")) return "FSGD1APROT10";
            if (name.startsWith("TAUD1")) return "FSGD1APROT12";
            if ("pic1-start".equals(target.behavior)) return "FSGD1CPROT00";
            if ("pic-taud".equals(target.behavior) || "pic-tsg".equals(target.behavior))
                return "FSGD1DPROT00";
            if (name.startsWith("TSG30")) return "FSGD1CPROT02";
            if (name.startsWith("TSG31")) return "FSGD1CPROT04";
            if (name.equals("RSENTTSSEL")) return "FSGD1EPROT12";
            if ("rsent".equals(target.behavior))
                return name.startsWith("RSENT0") ? "FSGD1EPROT00" : "FSGD1EPROT02";
            if (name.startsWith("DCRA")) return "FSGD2CPROT02";
            if (name.startsWith("CSIH"))
                return String.format("FSGD2BPROT%02d", 2 + 2 * (name.charAt(4) - '0'));
            if (name.equals("SELCSIHDMA")) return "FSGD2BPROT10";
            if ("ecm".equals(target.behavior)) return "FSGD2CPROT04";
            if (name.startsWith("RSCFD") || name.startsWith("RSCAN"))
                return name.endsWith("CANFDMDR") ? "FSGD2CPROT00" : "FSGD2BPROT12";
            if ("port-config".equals(target.behavior) || "port-input".equals(target.behavior))
                return name.startsWith("J") ? "FSGD5APROT06" : "FSGD5APROT08";
            if (name.startsWith("DNFA") || name.startsWith("LBIST")
                    || name.startsWith("MBIST") || name.equals("BISTST")
                    || name.equals("BSEQ0ST") || name.equals("BSEQ0STB"))
                return "FSGD5APROT02";
            if (name.startsWith("FCLA")) {
                int channel = name.charAt(4) - '0';
                return channel < 3 ? String.format("FSGD5APROT%02d", 10 + 2 * channel)
                    : String.format("FSGD5BPROT%02d", 2 * (channel - 3));
            }
            if (name.startsWith("CVM") || name.startsWith("DNFCK")
                    || name.startsWith("DNFCSC") || name.startsWith("CLKD")
                    || name.startsWith("CKSC") || name.startsWith("STAC_")
                    || name.startsWith("RES") || name.equals("BSEQ0CTL")
                    || name.startsWith("FHVE") || name.equals("MODE")) return "FSGD5APROT04";
            if (name.startsWith("FLMD")) return "FSGD5CPROT00";
            if (address >= 0xffffb000L && address < 0xffffc000L)
                return "APBFSGDPROT_INTC2_A";
            if (name.matches("(DM[01][0-7]|DTS[0-9]{3})CM"))
                return "APBFSGDPROT_PDMACM_A";
            if ("pdma".equals(target.behavior))
                return name.startsWith("DMACTRGSEL") ? "FSGD2CPROT10" : "APBFSGDPROT_PDMACH_A";
            if (name.equals("DFECCCTL") || name.equals("DFTSTCTL"))
                return "FSGD0PROT10";
            if (name.equals("EEPRDCYCL")) return "FSGD0PROT06";
            return null;
        }

        void requireBusGuard(PcodeThread<byte[]> thread, String readGuard,
                             long address, int size, String access) {
            boolean write = access.equals("write");
            RegisterDef read = requiredRegister("P1M-E", "read guard", readGuard);
            RegisterDef protection = write ? register(read.address + 8, 4) : read;
            RegisterDef spid = register(protection.address + 4, 4);
            // Table31.147: CPU is PEID1. PEID4 denotes DMA/DTS/FlexRay,
            // not a CPU privilege mode; this path never impersonates a master.
            if ((registerValue(protection) & (1L << 18)) == 0
                    || (registerValue(spid) & (1L << cpuSpid(thread))) == 0) {
                segError(thread, address, write ? 0x200L : 0x10L);
                if (write) {
                    discardBusStore = true;
                    return;
                }
                throw fault("unsupported-bus-guard-read", thread, address, size, access,
                    protection.evidence,
                    protection.name + " blocks access; error-response read data is unspecified");
            }
        }

        void requireGuards(PcodeThread<byte[]> thread, long address, int size, String access) {
            if (peripheralFile) return;
            RegionDef region = region(address, size);
            if (region != null && "global_ram".equals(region.name) && access.equals("write")) {
                int spid = cpuSpid(thread);
                // Table31.153: every matching enabled region must permit a write.
                // All byte lanes are checked, including a 512-byte boundary crossing.
                for (RegisterDef[] guard : gramGuards) {
                    RegisterDef protection = guard[0];
                    if ((registerValue(protection) & 0x40000000L) == 0) continue;
                    long valid = registerValue(guard[3]);
                    long base = registerValue(guard[2]);
                    if ((registerValue(guard[1]) & (1L << spid)) != 0)
                        continue;
                    for (int lane = 0; lane < size; lane++) {
                        if (((address + lane) & valid) == (base & valid)) {
                            segError(thread, address, 0x10L);
                            discardBusStore = true;
                            return;
                        }
                    }
                }
            }
            if (region != null) {
                if ("dataflash".equals(region.name))
                    requireBusGuard(thread, "FSGD0PROT04", address, size, access);
                return;
            }
            RegisterDef target = register(address, size);
            if (target == null) return; // Preserve the precise unmapped/width boundary.
            String guard = peripheralGuards.get(target);
            if (guard != null) requireBusGuard(thread, guard, address, size, access);
        }

        long segFlagValue() {
            return initializedDeviceRegisters.contains("SEGFLAG")
                ? registerValue(registersByName.get("SEGFLAG")) & 0x354L : segFlags;
        }

        long enabledSegFlags() {
            return segFlagValue() & registerValue(registersByName.get("SEGCONT"));
        }

        void setSegFlags(long flags) {
            segFlags = flags & 0x354L;
            RegisterDef register = registersByName.get("SEGFLAG");
            if (initializedDeviceRegisters.contains("SEGFLAG")) {
                long reserved = registerValue(register) & ~0x354L;
                setRegisterValue("SEGFLAG", reserved | segFlags);
            }
            else {
                // Table3.79 bit5 is undefined. Never resolve a whole-word read
                // from the known functional flags alone.
                setMemory(register.address, bytes(segFlags, 2, language.isBigEndian()));
            }
        }

        void segError(PcodeThread<byte[]> thread, long address, long factor) {
            long enabled = registerValue(registersByName.get("SEGCONT"));
            if ((enabled & factor) != 0 && enabledSegFlags() == 0) {
                long recorded = factor == 0x10L ? address : factor == 0x40L ? address & 0x7ffffL : 0;
                setRegisterValue("SEGADDR", recorded);
            }
            setSegFlags(segFlagValue() | factor);
            if ((enabled & factor) != 0) segNotificationPending = true;
            JsonObject event = new JsonObject();
            event.addProperty("kind", "bus-error");
            event.addProperty("pc", hex32(pc(thread)));
            event.addProperty("address", hex32(address));
            event.addProperty("seg_factor", hex32(factor));
            event.addProperty("notification_enabled", (enabled & factor) != 0);
            event.addProperty("evidence", "manual:R01UH0585EJ0120 Tables3.78-3.81");
            trace.deviceEvents.add(event);
        }

        void deliverSystemError(PcodeThread<byte[]> thread) {
            if (!segNotificationPending) return;
            segNotificationPending = false;
            long flags = enabledSegFlags();
            if (flags == 0) return;
            int cause = 0x10 + Long.numberOfTrailingZeros(flags);
            long psw = processorRegister(thread, "PSW");
            long returnPc = pc(thread);
            long base = processorRegister(thread, (psw & 0x8000L) == 0 ? "RBASE" : "EBASE");
            long handler = (base & 0xfffffe00L) + 0x10;
            // G3M Tables4-1/4-4: SYSERR ignores ID/NP, preserves EBV,
            // clears UM and sets ID/NP/EP; SEGFLAG remains sticky.
            processorRegister(thread, "FEPC", returnPc);
            processorRegister(thread, "FEPSW", psw);
            processorRegister(thread, "FEIC", cause);
            processorRegister(thread, "PSW", (psw & ~0x40000000L) | 0xe0L);
            thread.overrideCounter(memorySpace.getAddress(handler));
            JsonObject event = new JsonObject();
            event.addProperty("kind", "syserr-enter");
            event.addProperty("cause", hex32(cause));
            event.addProperty("return_pc", hex32(returnPc));
            event.addProperty("handler", hex32(handler));
            event.addProperty("evidence", "manual:R01US0123EJ0140 Tables4-1,4-4; R01UH0585EJ0120 Table3.80");
            trace.deviceEvents.add(event);
        }

        void requireAccessProtection(PcodeThread<byte[]> thread, long address, int size, String access) {
            boolean user = (processorRegister(thread, "PSW") & (1L << 30)) != 0;
            requireMpu(thread, address, size, access, user);
            requireGuards(thread, address, size, access);
            if (discardBusStore && access.equals("write")) return;
            if (!user || peripheralFile) return;
            RegisterDef ipg = requiredRegister("P1M-E", "IPG enable", "IPGENUM");
            if ((registerValue(ipg) & 1) == 0) return;
            RegionDef region = region(address, size);
            if (region != null && (region.name.startsWith("codeflash")
                    || "local_ram".equals(region.alias_group))) return;
            throw fault("unsupported-ipg-user-access", thread, address, size, access,
                ipg.evidence, "enabled IPG user-mode peripheral protection requires its group/violation model");
        }

        void requireRegisterPrivilege(PcodeThread<byte[]> thread, RegisterDef register, String access) {
            if ("ipg".equals(register.behavior)
                    && (processorRegister(thread, "PSW") & (1L << 30)) != 0) {
                throw fault("privileged-register-access", thread, register.address,
                    register.size, access, register.evidence, "IPG configuration requires supervisor mode");
            }
        }


        void requireExecute(PcodeThread<byte[]> thread, long address, int size) {
            requireAccessProtection(thread, address, size, "execute");
            RegionDef region = region(address, size);
            if (region == null || !region.executable) {
                throw fault("execute-unmapped", thread, address, size, "execute",
                    region == null ? "unknown" : region.evidence,
                    "instruction fetch outside an executable P1M-E region");
            }
        }

        final class GuardCapture {
            final RegisterDef status;
            final RegisterDef information;
            final int source;

            GuardCapture(String status, String information, int source) {
                this.status = requiredRegister("guard", "error status", status);
                this.information = requiredRegister("guard", "error context", information);
                this.source = source;
            }

            void record(PcodeThread<byte[]> thread, long context) {
                long previous = registerValue(status);
                if ((previous & 1) == 0) setRegisterValue(information.name, context);
                setRegisterValue(status.name, previous | 1 | ((previous & 1) != 0 ? 2 : 0));
                latchEcmError(thread, source);
            }
        }

        boolean dmaBusGuard(PcodeThread<byte[]> thread, String readGuard, int spid, boolean write) {
            RegisterDef read = requiredRegister("DMAC", "bus guard", readGuard);
            RegisterDef protection = write ? register(read.address + 8, 4) : read;
            RegisterDef identities = register(protection.address + 4, 4);
            // Tables31.159,31.166: the DMAC master is PEID4, independent
            // of both the CPU MPU and the channel owner's assigned PEID.
            if ((registerValue(protection) & (1L << 21)) != 0
                    && (registerValue(identities) & (1L << spid)) != 0) return true;
            GuardCapture capture = busGuardCaptures.get(readGuard);
            if (capture == null) throw new IllegalStateException("missing bus guard error bank: " + readGuard);
            capture.record(thread, ((long) spid << 16) | 0x8000 | (write ? 1 : 0));
            return false;
        }

        boolean dmaAccessAllowed(PcodeThread<byte[]> thread, Dma.Channel channel,
                                 long address, int size, boolean write) {
            // Figure4.1 and Section7.6: no local self-view, CPU-local bus,
            // or accesses by a DMAC to its own DMASS register file.
            if ((address >= 0xfede0000L && address < 0xfee00000L)
                    || (address >= 0xfffee000L && address < 0xffff0000L)
                    || (address >= 0xffff8000L && address < 0xffffb000L)) return false;
            RegionDef region = region(address, size);
            int spid = channel.spid();
            if (region != null && "local_ram_pe1".equals(region.name)) {
                int permitted = 0, all = (1 << size) - 1;
                for (RegisterDef[] guard : dma.peg) {
                    long base = registerValue(guard[1]);
                    if ((base & 1) == 0 || (base & (write ? 4 : 2)) == 0
                            || (registerValue(guard[2]) & (1L << spid)) == 0) continue;
                    long mask = ~registerValue(guard[0]) & 0xfffff000L;
                    for (int lane = 0; lane < size; lane++)
                        if (((address + lane) & mask) == (base & mask)) permitted |= 1 << lane;
                    // Overlapping PEG regions are a union, not an intersection.
                    if (permitted == all) return true;
                }
                pegCapture.record(thread, 0x80 | spid);
                return false;
            }
            if (region != null && "global_ram".equals(region.name) && write) {
                for (RegisterDef[] guard : gramGuards) {
                    if ((registerValue(guard[0]) & 0x40000000L) == 0
                            || (registerValue(guard[1]) & (1L << spid)) != 0) continue;
                    long mask = registerValue(guard[3]), base = registerValue(guard[2]);
                    for (int lane = 0; lane < size; lane++) {
                        if (((address + lane) & mask) != (base & mask)) continue;
                        gramDmaCapture.record(thread, ((long) spid << 20) | 0x8000);
                        return false;
                    }
                }
            }
            if (region != null) {
                if (write && (region.name.startsWith("codeflash") || "dataflash".equals(region.name)))
                    return false;
                return !"dataflash".equals(region.name)
                    || dmaBusGuard(thread, "FSGD0PROT04", spid, write);
            }
            RegisterDef target = register(address, size);
            // Unknown peripheral behavior remains a precise model fault below;
            // it is not converted into a fabricated hardware transfer error.
            String guard = target == null ? null : peripheralGuards.get(target);
            return guard == null || dmaBusGuard(thread, guard, spid, write);
        }

        byte[] dmaRead(PcodeThread<byte[]> thread, Dma.Channel channel, long address, int size) {
            String previous = trace.busInitiator;
            trace.busInitiator = channel.initiator;
            try {
                if (!dmaAccessAllowed(thread, channel, address, size, false)) return null;
                RegisterDef register = beforeRead(thread, address, size, false);
                if (register != null && register.read_input) {
                    long response = readInputResponses.get(register.name);
                    int lane = Math.toIntExact(address - register.address);
                    int shift = language.isBigEndian()
                        ? 8 * (register.size - lane - size) : 8 * lane;
                    return bytes(response >>> shift, size, language.isBigEndian());
                }
                byte[] result = memory(thread, address, size);
                adc.readCompleted(thread, address, size);
                rsent.readCompleted(thread, address, size);
                return result;
            } finally {
                trace.busInitiator = previous;
            }
        }

        boolean dmaWrite(PcodeThread<byte[]> thread, Dma.Channel channel, long address, byte[] value) {
            String previous = trace.busInitiator;
            trace.busInitiator = channel.initiator;
            try {
                if (!dmaAccessAllowed(thread, channel, address, value.length, true)) return false;
                beforeWrite(thread, address, value.length, value, false);
                if (discardBusStore) {
                    discardBusStore = false;
                    return false;
                }
                setMemory(address, value);
                afterWrite(thread, address, value.length, value);
                return true;
            } finally {
                trace.busInitiator = previous;
            }
        }

        long ecmLatchedStatus(RegisterDef status) {
            long value = unsigned(emulator.getSharedState().getVar(
                memorySpace, status.address, status.size, true, Reason.INSPECT));
            return missingResetInputs.contains(status.name) ? value & status.reset_mask : value;
        }

        void latchEcmError(PcodeThread<byte[]> thread, int source) {
            int index = source / 32;
            long bit = 1L << (source % 32);
            for (int route = 1; route < ECM_NOTIFICATION_REGISTERS.length; route++) {
                RegisterDef configuration = registersByName.get(ECM_NOTIFICATION_REGISTERS[route][index]);
                if ((registerValue(configuration) & bit) != 0)
                    throw fault("unsupported-ecm-notification", thread, configuration.address,
                        configuration.size, "device", configuration.evidence,
                        "enabled FENMI, internal reset or delay-timer route requires its execution model");
            }
            boolean newlyLatched = false;
            for (int domain = 0; domain < 2; domain++) {
                RegisterDef status = registersByName.get(ECM_STATUS_REGISTERS[domain][index]);
                boolean missing = missingResetInputs.contains(status.name);
                long previous = ecmLatchedStatus(status);
                newlyLatched |= (previous & bit) == 0;
                setRegisterValue(status.name, previous | bit);
                // Internal errors do not identify the external ERROROUT pin.
                if (missing) missingResetInputs.add(status.name);
            }
            refreshEcmFeedback();
            if (newlyLatched && (registerValue(registersByName.get(
                    ECM_NOTIFICATION_REGISTERS[0][index])) & bit) != 0)
                requestInterrupt(thread, 8);
        }

        RegisterDef beforeRead(PcodeThread<byte[]> thread, long address, int size) {
            return beforeRead(thread, address, size, true);
        }

        RegisterDef beforeRead(PcodeThread<byte[]> thread, long address, int size, boolean cpu) {
            requireAlignment(thread, address, size, "read");
            if (cpu) requireAccessProtection(thread, address, size, "read");
            RegionDef region = region(address, size);
            if (region != null) {
                if ("pbg0_unimplemented_channels8_9".equals(region.name)) {
                    segError(thread, address, 0x10L);
                    throw fault("unsupported-unimplemented-pbus-read", thread, address, size,
                        "read", region.evidence, "unimplemented P-Bus read has an unspecified bus-data response");
                }
                if (!region.access.contains("r")) {
                    throw fault("read-prohibited", thread, address, size, "read",
                        region.evidence, "region is not software-readable: " + region.name);
                }
                if ("dataflash".equals(region.name)
                        && (registerValue(registersByName.get("DFECCCTL")) != 0
                            || registerValue(registersByName.get("DFTSTCTL")) != 0)) {
                    throw fault("unsupported-dataflash-ecc-mode", thread, address, size, "read",
                        "manual:R01UH0585EJ0120 Tables31.18 and31.25",
                        "DataFlash payload reads are modeled only with normal ECC enabled and test mode disabled");
                }
                if ("dataflash".equals(region.name)) validateDataFlashRead(thread, address, size);
                trace.access("read", pc(thread), address, size, region.evidence);
                return null;
            }
            if (peripheralFile) {
                // Scenario checks compare these bytes. Keeping them out of the
                // access trace reserves its capacity for RAM traffic.
                scriptPeripheralPoll(thread, address, size);
                return null;
            }
            RegisterDef register = register(address, size);
            if (register == null) {
                throw fault("unmapped-read", thread, address, size, "read", "unknown",
                    "no SystemRDL memory region or register covers this read");
            }
            requireRegisterPrivilege(thread, register, "read");
            if (!register.allows(address, size)) {
                throw fault("mmio-width", thread, address, size, "read",
                    register.evidence, "illegal access width/alignment for register " + register.name);
            }
            if (missingResetInputs.contains(register.name)) {
                throw fault("missing-reset-input", thread, address, size, "read",
                    register.evidence, "reset invalidated opaque hardware result "
                        + register.name + "; supply an explicit post-reset scenario input");
            }
            if (register.read_value != null) {
                setRegisterValue(register.name, register.read_value);
            }
            else if (register.read_input) {
                if (readInputResponses == null || !readInputResponses.containsKey(register.name)) {
                    throw fault("missing-read-input", thread, address, size, "read",
                        register.evidence, "read data is unspecified for write-only command "
                            + register.name + "; supply an explicit register-input bus response");
                }
            }
            else if (!register.access.contains("r")) {
                throw fault("read-prohibited", thread, address, size, "read",
                    register.evidence, "register is not software-readable: " + register.name);
            }
            if ("csih".equals(register.behavior) && !"dma-select".equals(register.trigger)) {
                csih(register).read(thread, register);
            }
            if ("adc".equals(register.behavior) || "adc-clock".equals(register.behavior))
                adc.beforeRead(thread, register);
            if ("tauj".equals(register.behavior)) tauj.read(thread, register);
            if ("taud".equals(register.behavior)) taud.read(register);
            if ("tsg".equals(register.behavior)) tsg.read(thread, register);
            if ("rsent".equals(register.behavior)) rsent.beforeRead(thread, register);
            if ("faci-access-status".equals(register.trigger))
                faciReadErrors |= registerValue(register) & FASTAT_ACCESS_ERROR_MASK;
            if ("port-pin-alias".equals(register.trigger)) refreshPortAlias(register);
            if ("port-masked-alias".equals(register.trigger)) {
                RegisterDef target = requiredRegister(register.name, "control", register.control_register);
                setRegisterValue(register.name, registerValue(target));
            }
            if ("cvm".equals(register.behavior) && register.active_mask != null
                    && !"CVMDE".equals(register.name)) {
                setRegisterValue(register.name, registerValue(register) & register.active_mask);
            }
            if ("port-input".equals(register.behavior)) {
                setRegisterValue(register.name, registerValue(register) & register.active_mask);
            }
            if ("mode-latch".equals(register.behavior)) {
                long latched = registerValue(register);
                setRegisterValue(register.name, (latched & 1) == 0 ? 0 : latched & register.active_mask);
            }
            if ("ECMPS".equals(register.name)) {
                setRegisterValue(register.name, registerValue(register) & 1);
            }
            if ("dcra-seed".equals(register.trigger)) {
                RegisterDef control = requiredRegister(register.name, "mode", register.mode_register);
                long mode = registerValue(control);
                if (mode != 0 && !("DCRA0CTL".equals(control.name) && mode == 0x22)) {
                    throw fault("unsupported-dcra-mode", thread, control.address,
                        control.size, "read", control.evidence,
                        "supported DCRA modes are Ethernet/32-bit and DCRA0 SAEJ1850/8-bit");
                }
            }
            if (size > register.size) {
                // Only a width explicitly declared in RDL reaches this point.
                // Preserve the native register/physical SFR width and normalize
                // the containing transaction's reserved lanes, not all MMIO holes.
                setMemory(address, bytes(registerValue(register), size, language.isBigEndian()));
            }
            trace.access("read", pc(thread), address, size, register.evidence);
            return register;
        }

        void beforeWrite(PcodeThread<byte[]> thread, long address, int size, byte[] value) {
            beforeWrite(thread, address, size, value, true);
        }

        void beforeWrite(PcodeThread<byte[]> thread, long address, int size, byte[] value, boolean cpu) {
            if (internalWrite) return;
            discardBusStore = false;
            requireAlignment(thread, address, size, "write");
            if (cpu) requireAccessProtection(thread, address, size, "write");
            if (discardBusStore) return;
            RegionDef region = region(address, size);
            if (region != null) {
                if ("pbg0_unimplemented_channels8_9".equals(region.name)) {
                    segError(thread, address, 0x200L);
                    discardBusStore = true;
                    trace.access("write", pc(thread), address, size, region.evidence);
                    return;
                }
                if (!region.access.contains("w") || region.name.startsWith("codeflash")
                        || region.name.equals("dataflash")) {
                    // The explicit peripheral-file exploration mode retains its
                    // stub-write experiment; strict device execution never patches ROM.
                    if (peripheralFile && region.name.startsWith("codeflash")
                            && size == 2 && (address & 1) == 0
                            && unsigned(memory(thread, address, 2)) == 0x7fL) {
                        trace.access("write", pc(thread), address, size, region.evidence);
                        return;
                    }
                    throw fault("write-prohibited", thread, address, size, "write",
                        region.evidence, "direct write prohibited for region: " + region.name);
                }
                trace.access("write", pc(thread), address, size, region.evidence);
                return;
            }
            if (peripheralFile) {
                return;
            }
            RegisterDef register = register(address, size);
            if (register == null) {
                throw fault("unmapped-write", thread, address, size, "write", "unknown",
                    "no SystemRDL memory region or register covers this write");
            }
            if (size > register.size || !register.allows(address, size)) {
                throw fault("mmio-width", thread, address, size, "write",
                    register.evidence, "illegal access width/alignment for register " + register.name);
            }
            if ("pdma".equals(register.behavior) && !dma.authorizeCpuWrite(thread, register)) {
                discardBusStore = true;
                return;
            }
            if (!register.access.contains("w")) {
                throw fault("write-prohibited", thread, address, size, "write",
                    register.evidence, "register is not software-writable: " + register.name);
            }
            if ("seg".equals(register.behavior)
                    && (processorRegister(thread, "PSW") & 0x40000000L) != 0) {
                segError(thread, address, 0x10L);
                discardBusStore = true;
                return;
            }
            if ("seg".equals(register.behavior)) {
                if (!"SEGADDR".equals(register.name)) {
                    if ((unsigned(value) & ~register.writable_mask) != 0) {
                        throw fault("prohibited-register-reserved-bits", thread, address, size,
                            "write", register.evidence, "SEG reserved bits must be written as zero");
                    }
                    registerBeforeWrite = "SEGFLAG".equals(register.name)
                            && !initializedDeviceRegisters.contains("SEGFLAG")
                        ? segFlagValue() : registerValue(register);
                }
                else if (enabledSegFlags() != 0) {
                    discardBusStore = true;
                    return;
                }
            }
            if (("banked-ecc-clear".equals(register.trigger)
                    || "ecc-notification".equals(register.trigger))
                    && ((unsigned(value) << (8 * (address - register.address)))
                        & ~register.writable_mask) != 0) {
                throw fault("prohibited-register-reserved-bits", thread, address, size,
                    "write", register.evidence,
                    "reserved ECC clear bits must be written as zero: " + register.name);
            }
            if (isGuard(register)) {
                registerBeforeWrite = registerValue(register);
                RegisterDef lock = guardLock(register);
                long lockMask = "peg".equals(register.behavior) ? 0x10L : 0x80000000L;
                guardWriteIgnored = (registerValue(lock) & lockMask) != 0;
                if (!guardWriteIgnored) {
                    long laneMask = ((1L << (8 * size)) - 1) << (8 * (address - register.address));
                    long incoming = unsigned(value) << (8 * (address - register.address));
                    if (((incoming ^ register.reset) & laneMask & ~register.writable_mask) != 0) {
                        throw fault("prohibited-register-reserved-bits", thread, address, size,
                            "write", register.evidence,
                            "guard reserved bits must retain their reset value: " + register.name);
                    }
                }
            }
            if ("pdma".equals(register.behavior)) dma.validateWrite(thread, register, unsigned(value));
            if ("guard-error-clear".equals(register.trigger)
                    && ((unsigned(value) << (8 * (address - register.address))) & ~register.writable_mask) != 0)
                throw fault("prohibited-register-reserved-bits", thread, address, size,
                    "write", register.evidence, "guard clear reserved bits must be zero");
            if ("csih".equals(register.behavior)) {
                if (!"dma-select".equals(register.trigger)) csih(register).validateWrite(thread, register, unsigned(value));
                else if ((unsigned(value) & ~register.writable_mask) != 0)
                    throw fault("prohibited-csih-register", thread, address, size, "write",
                        register.evidence, "SELCSIHDMA reserved bits must be zero");
                registerBeforeWrite = register.reset == null ? 0 : registerValue(register);
            }
            if ("adc".equals(register.behavior) || "adc-clock".equals(register.behavior)) {
                adc.validateWrite(thread, register, unsigned(value));
                registerBeforeWrite = registerValue(register);
            }
            if ("rsent".equals(register.behavior)) rsent.validateWrite(thread, register, unsigned(value));
            if ("taud".equals(register.behavior)) registerBeforeWrite = registerValue(register);
            if ("dcra-control".equals(register.trigger) || "clock-selector".equals(register.trigger)
                    || "pdma-comparator".equals(register.trigger))
                registerBeforeWrite = registerValue(register);
            validateDeviceWrite(thread, register, value);
            if ("ecm".equals(register.behavior)) {
                registerBeforeWrite = register.reset == null ? 0 : registerValue(register);
            }
            if ("cvm".equals(register.behavior) && register.access.contains("r")) {
                registerBeforeWrite = registerValue(register);
            }
            if ("noise-clock-selector".equals(register.trigger)) {
                registerBeforeWrite = registerValue(register);
            }
            if ("peripheral-ecc".equals(register.behavior)) {
                // Internal RMW uses the stored known bits; ECEMF remains
                // unknown to CPU reads until an explicit input supplies it.
                registerBeforeWrite = unsigned(memory(thread, register.address, register.size));
            }
            if ((register.fifo_index != null && receiveFifos.containsKey(register.fifo_index)
                    && receiveFifos.get(register.fifo_index).status == register)
                    || ("intc_eic".equals(register.behavior) && register.reset != null)
                    || "faci-address".equals(register.trigger)
                    || "faci-dataflash-mode".equals(register.trigger)
                    || "faci-access-status".equals(register.trigger)
                    || "faci-setup-initialize".equals(register.trigger)
                    || "faci-area-selector".equals(register.trigger)
                    || "faci-clock-notify".equals(register.trigger)
                    || "ecc-protected-control".equals(register.trigger)
                    || "flmd-control".equals(register.trigger)) {
                registerBeforeWrite = unsigned(memory(thread, register.address, register.size));
            }
            trace.access("write", pc(thread), address, size, register.evidence);
        }

        void scriptIcctrl(PcodeThread<byte[]> thread) {
            if (!peripheralFile) return;
            long value = processorRegister(thread, "ICCTRL");
            if ((value & 0x100L) == 0) {
                icctrlBusyReads = 0;
                return;
            }
            icctrlBusyReads += 1;
            if (icctrlBusyReads != ICCTRL_BUSY_READS) return;
            processorRegister(thread, "ICCTRL", value & ~0x100L);
            icctrlBusyReads = 0;
        }

        void completeInstructionCacheClear(PcodeThread<byte[]> thread) {
            if (peripheralFile) return;
            // P1M-E Table 3.55 / G3M Table 3-60: ICHCLR reads zero after
            // completion. With no cached instruction state, clearing is complete
            // at retirement of the requesting instruction, independent of STSR.
            // Keep every other control/status bit and the instruction's effects.
            long value = processorRegister(thread, "ICCTRL");
            if ((value & 0x100L) != 0) {
                processorRegister(thread, "ICCTRL", value & ~0x100L);
            }
        }

        void completeCountedDelay(PcodeThread<byte[]> thread) {
            if (!peripheralFile) return;
            long pc = pc(thread);
            long exit = pc == 0x7210L ? 0x721cL : pc == 0x71c70L ? 0x71c7cL : pc == 0x71c88L ? 0x71c94L : -1L;
            if (exit < 0) return;
            trace.shortcut("counted-delay", pc, exit);
            processorRegister(thread, "r12", 0);
            processorRegister(thread, "r13", 0);
            long psw = processorRegister(thread, "PSW");
            processorRegister(thread, "PSW", (psw & ~0xfL) | 0x9L);
            thread.overrideCounter(language.getDefaultSpace().getAddress(exit));
        }

        void scriptPeripheralPoll(PcodeThread<byte[]> thread, long address, int size) {
            if (peripheralPollBusy || size <= 0 || size > 4) return;
            if (Long.compareUnsigned(address, 0xff000000L) < 0
                    || (Long.compareUnsigned(address, 0xff200000L) >= 0
                        && Long.compareUnsigned(address, 0xff208000L) < 0)) {
                return;
            }
            int count = peripheralPolls.getOrDefault(address, 0) + 1;
            peripheralPolls.put(address, count);
            if (count != PERIPHERAL_POLL_READS
                    && !(size == 1 && count == PERIPHERAL_POLL_READS * 2)) return;
            peripheralPollBusy = true;
            try {
                byte[] current;
                try {
                    current = memory(thread, address, size);
                } catch (RuntimeException ex) {
                    current = new byte[size];
                }
                boolean nonzero = false;
                for (byte piece : current) {
                    if (piece != 0) nonzero = true;
                }
                byte[] next = new byte[size];
                // A byte is all-ones, then zero. A word still flips.
                if (size == 1)
                    Arrays.fill(next, count == PERIPHERAL_POLL_READS ? (byte) 0xff : (byte) 0);
                else if (!nonzero) Arrays.fill(next, (byte) 0xff);
                setMemory(address, next);
            } finally {
                peripheralPollBusy = false;
            }
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

        void storeResetFactors(long value) {
            setRegisterValue("RESF", value);
            if (resetFactorKnownMask != 0xffffffffL) {
                initializedDeviceRegisters.remove("RESF");
                missingResetInputs.add("RESF");
            }
        }

        long resetFactorValue() {
            RegisterDef status = registersByName.get("RESF");
            // Internal updates preserve stored known bits while the knowledge
            // mask still prevents CPU reads of unresolved source/read data.
            return unsigned(emulator.getSharedState().getVar(
                memorySpace, status.address, status.size, true, Reason.INSPECT));
        }

        void applyResetFactors(String resetClass) {
            long value = resetFactorValue();
            // Bit6 is undefined read data, not a reset-cause flag.
            resetFactorKnownMask &= ~0x40L;
            switch (resetClass) {
                case "power-on":
                    value = (value & 0x400) | 3;
                    resetFactorKnownMask = (resetFactorKnownMask & 0x400)
                        | (0xffffffffL & ~0x440L);
                    unresolvedResetCauses = 0;
                    break;
                case "system-1-cvm":
                    value = (value & 0x402) | 4;
                    resetFactorKnownMask = (resetFactorKnownMask & 0x402)
                        | (0xffffffffL & ~0x442L);
                    unresolvedResetCauses = 0;
                    break;
                case "system-1-pin":
                    value |= 2;
                    resetFactorKnownMask |= 2;
                    break;
                case "system-2":
                    // The reset class alone cannot distinguish software and ECM.
                    // Already-set sticky flags remain known; only possible new
                    // flags require an explicit source observation.
                    resetFactorKnownMask &= ~(0x28L & ~value);
                    unresolvedResetCauses |= 0x28;
                    break;
                case "application-1":
                    resetFactorKnownMask &= ~(0x280L & ~value);
                    unresolvedResetCauses |= 0x280;
                    break;
                default:
                    throw new IllegalArgumentException("unsupported reset class: " + resetClass);
            }
            if (fieldBistExecuted) {
                value |= 0x400;
                resetFactorKnownMask |= 0x400;
            }
            storeResetFactors(value);
        }

        void validateResetFactorInput(long value) {
            long previous = resetFactorValue();
            if (((previous ^ value) & resetFactorKnownMask) != 0) {
                throw new IllegalArgumentException(
                    "RESF input may resolve unknown source/read bits, not replace derived or retained flags");
            }
            if (((unresolvedResetCauses & 0x28) != 0 && (value & 0x28) == 0)
                    || ((unresolvedResetCauses & 0x280) != 0 && (value & 0x280) == 0)) {
                throw new IllegalArgumentException(
                    "RESF input must identify the software or ECM cause of the declared reset class");
            }
            resetFactorKnownMask = 0xffffffffL;
            unresolvedResetCauses = 0;
        }

        void clearResetFactors(long value) {
            RegisterDef command = registersByName.get("RESFC");
            long clear = value & command.writable_mask;
            long previous = resetFactorValue();
            resetFactorKnownMask |= clear;
            // Clearing a possible cause may erase the only asserted source bit.
            if ((clear & 0x28) != 0) unresolvedResetCauses &= ~0x28L;
            if ((clear & 0x280) != 0) unresolvedResetCauses &= ~0x280L;
            storeResetFactors(previous & ~clear);
            setRegisterValue(command.name, 0);
        }

        void applyReset(String resetClass) {
            if (resetClass == null || resetClass.equals("none")) return;
            if (registersByName.get("FSTATR").reset_classes.contains(resetClass)) resetFaci();
            for (Csih controller : csihControllers.values()) controller.reset();
            dma.reset();
            adc.reset();
            rsent.reset();
            if (icusStartupStub != null) icusStartupStub.reset();
            dcraSeeded.clear();
            segFlags = 0;
            segNotificationPending = false;
            if (readInputResponses != null) readInputResponses.clear();
            if ("power-on".equals(resetClass)) cvmEnableWritten = false;
            ecmStage = 0;
            ecmTarget = null;
            if (!resetClass.equals("application-1")) {
                ecmOutputLow[0] = true;
                ecmOutputLow[1] = true;
            }
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
            // Reset-class metadata is canonical RDL data. Do not turn Table31.194's
            // illustrative signatures into constants or carry old results over SR1/SR2.
            for (RegisterDef register : registers) {
                if (!register.reset_classes.contains(resetClass)) continue;
                if ("peripheral-ecc-control".equals(register.trigger)) {
                    resetPeripheralEccControl(register);
                    continue;
                }
                if (register.reset != null && register.reset_mask == null) {
                    setRegisterValue(register.name, register.reset);
                }
                else if (register.reset != null
                        && initializedDeviceRegisters.contains(register.name)) {
                    long retained = registerValue(register) & ~register.reset_mask;
                    setRegisterValue(register.name, retained | (register.reset & register.reset_mask));
                }
                else {
                    initializedDeviceRegisters.remove(register.name);
                    missingResetInputs.add(register.name);
                }
            }
            if (tauj.units[0].te.reset_classes.contains(resetClass)) tauj.reset();
            if (taud.units[0].enable.reset_classes.contains(resetClass)) taud.reset();
            if (tsg.units[0].bank[0x010 >>> 2].reset_classes.contains(resetClass)) {
                tsg.reset();
                declaredTsgRegisters.clear();
            }
            RegisterDef bistControl = requiredRegister("BIST", "control", "BSEQ0CTL");
            boolean bistReset = !resetClass.equals("application-1");
            fieldBistExecuted = bistReset && (registerValue(bistControl) & 1) != 0;
            if (bistReset) {
                for (RegisterDef register : registers) {
                    if (!"bist".equals(register.behavior) || register.skipped_value == null) continue;
                    if (!fieldBistExecuted) {
                        setRegisterValue(register.name, register.skipped_value);
                    }
                }
                JsonObject event = new JsonObject();
                event.addProperty("kind", fieldBistExecuted
                    ? "field-bist-executed-awaiting-results" : "field-bist-skipped");
                event.addProperty("reset_class", resetClass);
                event.addProperty("evidence", "R01UH0585EJ0120 pages2767-2784,2808 Table8.2");
                trace.deviceEvents.add(event);
            }
            if (fieldBistExecuted) {
                for (RegisterDef register : registers) {
                    if ("ecm-bist-status".equals(register.trigger)
                            && initializedDeviceRegisters.contains(register.name)) {
                        setRegisterValue(register.name, registerValue(register) | (1L << 27));
                    }
                }
            }
            applyResetFactors(resetClass);
            refreshEcmFeedback();
        }

        long unsigned(byte[] value) {
            return Utils.bytesToLong(value, value.length, language.isBigEndian()) & 0xffffffffL;
        }

        byte[] memory(long address, int size) {
            if (!missingResetInputs.isEmpty()) {
                RegisterDef register = register(address, size);
                if (register != null && missingResetInputs.contains(register.name)) {
                    throw new IllegalArgumentException("missing post-reset input for " + register.name);
                }
            }
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
            requireRegisterPrivilege(thread, register, "write");
            if ("tauj".equals(register.behavior)) {
                tauj.validate(thread, register, unsigned(value)); return;
            }
            if ("taud".equals(register.behavior) || "pic-taud".equals(register.behavior)) {
                taud.validate(thread, register, unsigned(value)); return;
            }
            if ("tsg".equals(register.behavior) || "pic-tsg".equals(register.behavior)) {
                tsg.validate(thread, register, unsigned(value)); return;
            }
            if ("pic1-start".equals(register.behavior)) {
                pic1.validate(thread, register, unsigned(value)); return;
            }
            if ("pdma-comparator".equals(register.trigger)) {
                long incoming = unsigned(value);
                if ((incoming & register.protection_mask) == register.protection_value) {
                    long selection = incoming & register.writable_mask;
                    if (selection != 0 && selection != 0x3fff7f7fL) {
                        throw fault("unsupported-pdma-comparator-selection", thread,
                            register.address, value.length, "write", register.evidence,
                            "only the documented mismatch-injection pattern and its cleared state are modeled");
                    }
                    if (selection != 0
                            && ((registerValue(registersByName.get("ECMNMICFG0"))
                                | registerValue(registersByName.get("ECMIRCFG0"))
                                | registerValue(registersByName.get("ECMDTMCFG0"))) & 4) != 0) {
                        throw fault("unsupported-ecm-notification", thread,
                            register.address, value.length, "write", register.evidence,
                            "source2 FENMI, internal reset or delay-timer routing requires the corresponding execution model");
                    }
                }
            }
            if ("peripheral-ecc".equals(register.behavior)) {
                long incoming = unsigned(value);
                long readOnly = "peripheral-ecc-control".equals(register.trigger)
                    ? 0x30807L : 0;
                if ((incoming & ~(register.writable_mask | readOnly)) != 0) {
                    throw fault("prohibited-register-reserved-bits", thread,
                        register.address, value.length, "write", register.evidence,
                        "reserved peripheral ECC bits must be written as zero");
                }
                if ("peripheral-ecc-test".equals(register.trigger)) {
                    long mode = (incoming & 0xc000L) == 0x8000L
                        ? incoming & 0x80L : registerValue(register) & 0x80L;
                    if (mode != 0) {
                        throw fault("unsupported-peripheral-ecc-test", thread,
                            register.address, value.length, "write", register.evidence,
                            "active test mode requires ECC encoder/decoder and peripheral RAM substitution");
                    }
                }
            }
            if ("noise-filter".equals(register.behavior)) {
                long incoming = unsigned(value);
                if ((incoming & ~register.writable_mask) != 0) {
                    throw fault("prohibited-register-reserved-bits", thread, register.address,
                        value.length, "write", register.evidence,
                        "noise-filter reserved bits must remain at reset: " + register.name);
                }
                if ("noise-filter-enable".equals(register.trigger) && incoming != 0) {
                    throw fault("unsupported-noise-filter-operation", thread, register.address,
                        value.length, "write", register.evidence,
                        "enabled filtering requires external signal and sampling-clock behavior");
                }
                if ("noise-clock-selector".equals(register.trigger)
                        && !register.allowed_values.contains(incoming)) {
                    throw fault("prohibited-clock-source", thread, register.address,
                        value.length, "write", register.evidence,
                        "DNF sampling source code is prohibited: " + incoming);
                }
                if (register.enable_register != null) {
                    RegisterDef enable = requiredRegister(register.name, "enable", register.enable_register);
                    if (registerValue(enable) != 0) {
                        throw fault("prohibited-noise-filter-enabled", thread, register.address,
                            value.length, "write", register.evidence,
                            "configuration may change only while the related filter is disabled");
                    }
                }
                if ("noise-clock-selector".equals(register.trigger)) {
                    for (String name : register.capture_registers) {
                        RegisterDef enable = requiredRegister(register.name, "enable", name);
                        if (registerValue(enable) != 0) {
                            throw fault("prohibited-noise-filter-enabled", thread, register.address,
                                value.length, "write", register.evidence,
                                "sampling source may change only while all related filters are disabled");
                        }
                    }
                }
            }
            if (("ipg".equals(register.behavior) || "gram-buffer".equals(register.behavior))
                    && (unsigned(value) & ~register.writable_mask) != 0) {
                throw fault("prohibited-register-reserved-bits", thread, register.address,
                    value.length, "write", register.evidence,
                    "reserved bits must be written as zero: " + register.name);
            }
            if ("bist-control".equals(register.trigger)
                    && (unsigned(value) & ~register.active_mask) != 0) {
                throw fault("prohibited-bist-reserved-bits", thread, register.address,
                    value.length, "write", register.evidence,
                    "BSEQ0CTL reserved bits must be zero");
            }
            if ("clock-divider".equals(register.trigger) || "clock-selector".equals(register.trigger)) {
                long incoming = unsigned(value);
                if ((incoming & ~register.writable_mask) != 0) {
                    throw fault("prohibited-clock-reserved-bits", thread, register.address,
                        value.length, "write", register.evidence,
                        "reserved clock register bits must be written as zero: " + register.name);
                }
                if ("clock-divider".equals(register.trigger)) {
                    RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                    if ((registerValue(status) & register.sync_mask) != register.sync_mask) {
                        throw fault("prohibited-clock-divider-unsynchronized", thread, register.address,
                            value.length, "write", register.evidence,
                            "divider must not be written while SYNC is zero");
                    }
                }
                else {
                    if (!register.allowed_values.contains(incoming)) {
                        throw fault("prohibited-clock-source", thread, register.address,
                            value.length, "write", register.evidence,
                            "clock source ID is prohibited: " + incoming);
                    }
                    RegisterDef divider = requiredRegister(register.name, "control", register.control_register);
                    RegisterDef status = requiredRegister(
                        register.name, "secondary-status", register.secondary_status_register);
                    if (incoming != registerValue(register) && (registerValue(divider) != 0
                            || registerValue(status) != register.completion_value)) {
                        throw fault("prohibited-clock-selector-running", thread, register.address,
                            value.length, "write", register.evidence,
                            "clock source may change only with divider zero and stopped synchronized status");
                    }
                }
            }
            if ("flmd".equals(register.behavior)) {
                long incoming = unsigned(value);
                boolean valid = "flmd-command".equals(register.trigger)
                    ? flmdStage == 0 && incoming == 0xa5
                    : "flmd-control".equals(register.trigger)
                        && (flmdStage == 1 && incoming <= 1
                            || flmdStage == 2 && incoming == (flmdDesired ^ 0xffffffffL)
                            || flmdStage == 3 && incoming == flmdDesired);
                if (!valid) {
                    throw fault("unsupported-flmd-sequence", thread, register.address,
                        value.length, "write", register.evidence,
                        "only uninterrupted A5/value/full-word-inverse/value writes are modeled; malformed-sequence error timing is not modeled");
                }
            }
            if ("dcra".equals(register.behavior)) {
                RegisterDef control = "dcra-control".equals(register.trigger) ? register
                    : requiredRegister(register.name, "mode", register.mode_register);
                long mode = control == register ? unsigned(value) : registerValue(control);
                if (mode != 0 && !("DCRA0CTL".equals(control.name) && mode == 0x22)) {
                    throw fault("unsupported-dcra-mode", thread, control.address,
                        control.size, "write", control.evidence,
                        "supported DCRA modes are Ethernet/32-bit and DCRA0 SAEJ1850/8-bit; reserved bits must be zero");
                }
                if ("dcra-input".equals(register.trigger)) {
                    if (!dcraSeeded.contains(control.name)) {
                        throw fault("uninitialized-dcra-seed", thread, register.address,
                            value.length, "write", register.evidence,
                            "DCRAnCOUT must be explicitly seeded before the first input word");
                    }
                    RegisterDef output = requiredRegister(register.name, "status", register.status_register);
                    memory(thread, output.address, output.size);
                }
            }
            if ("faci-command".equals(register.trigger)) {
                validateFaciWrite(thread, register, value);
            }
            if ("faci-enable".equals(register.trigger)
                    && (registerValue(registersByName.get("FSTATR")) & FSTATR_FRDY) == 0
                    && (unsigned(value) & 1) != registerValue(register))
                throw fault("prohibited-faci-enable-change", thread, register.address, value.length,
                    "write", register.evidence, "FHVE enables must not change during command processing");
            if ("faci-address".equals(register.trigger)) {
                RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                memory(thread, status.address, status.size);
            }
            if ("faci-dataflash-mode".equals(register.trigger)) {
                RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                long previous = unsigned(memory(thread, register.address, register.size));
                long incoming = unsigned(value);
                if ((unsigned(memory(thread, status.address, status.size)) & FSTATR_FRDY) != 0
                        && (previous != 0 && previous != 0x80
                            || (incoming >>> 8) == 0xaa
                                && (incoming & 0xff) != 0 && (incoming & 0xff) != 0x80)) {
                    throw fault("unsupported-faci-mode", thread, register.address,
                        value.length, "write", register.evidence,
                        "mode transitions are bounded to read/DataFlash P/E; CodeFlash/FWE and illegal-mode errors are not modeled");
                }
            }
            if ("faci-normal-emulation".equals(register.trigger)
                    && (unsigned(value) != 0 || unsigned(memory(thread, register.address, register.size)) != 0)) {
                throw fault("unsupported-faci-emulation", thread, register.address,
                    value.length, "write", register.evidence,
                    "only unchanged normal FLEMU mode is modeled; OCD write permission is not inferred");
            }
            if ("dataflash-read-cycle".equals(register.trigger) && (unsigned(value) & 0xf) < 3) {
                throw fault("prohibited-dataflash-read-cycle", thread, register.address,
                    value.length, "write", register.evidence,
                    "EEPRDCYCL codes0..2 are prohibited; no timing behavior is synthesized");
            }
            if ("icus-command".equals(register.trigger)) {
                long word = unsigned(value);
                if (icusStartupStub != null && icusStartupStub.handles(word)) {
                    icusStartupStub.validateCommand(thread, register, word);
                }
                else if ((word & 0xffff) != 5) {
                    throw fault("unsupported-icus-command", thread, register.address,
                        value.length, "write", register.evidence,
                        String.format("ICU-S command 0x%04X has no recovered state transition",
                            word & 0xffff));
                }
            }
            if (icusStartupStub != null && "icus-control".equals(register.trigger))
                icusStartupStub.validateAck(thread, register, unsigned(value));
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
        }

        void setRegisterValue(String name, long value) {
            RegisterDef register = registersByName.get(name);
            if (register == null) throw new IllegalStateException("machine model lacks register " + name);
            setMemory(register.address, bytes(value, register.size, language.isBigEndian()));
            if (register.reset_mask != null) initializedDeviceRegisters.add(register.name);
            missingResetInputs.remove(register.name);
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
            if (trace.busInitiator != null) event.addProperty("initiator", trace.busInitiator);
            trace.deviceEvents.add(event);
        }

        void handleRscfdWrite(PcodeThread<byte[]> thread, RegisterDef register, byte[] value) {
            if ((unsigned(value) & 1) == 0) return;
            if (register.payload_address == null || register.completion_value == null) {
                throw new IllegalStateException(register.name + " lacks RSCFD trigger metadata");
            }
            long base = register.payload_address;
            long bufferOffset = base - RSCFD_TX_RAM_BASE;
            if (bufferOffset < 0 || bufferOffset % RSCFD_TX_RECORD_SIZE != 0) {
                throw new IllegalStateException(
                    register.name + " has an invalid RSCFD payload address");
            }
            long buffer = bufferOffset / RSCFD_TX_RECORD_SIZE;
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
                event.addProperty("buffer", buffer);
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

        void finishPicRouting(PcodeThread<byte[]> thread) {
            if (taud.picDirty) {
                taud.picDirty = false;
                tsg.picSourcesChanged(thread);
            }
            tsg.flushPic(thread);
        }

        void advanceClock(PcodeThread<byte[]> thread, long cycles) {
            if (cycles < 0) throw new IllegalArgumentException("negative CLK_HSB advance");
            while (cycles != 0) {
                long span = Math.min(cycles, adc.hsbCyclesUntilEvent());
                span = Math.min(span, Math.min(tauj.cyclesUntilEvent(),
                    Math.min(taud.cyclesUntilEvent(), tsg.cyclesUntilEvent())));
                span = Math.min(span, rsent.cyclesUntilEvent());
                span = Math.min(span, dma.cyclesUntilEvent());
                if (faciDeadline != Long.MAX_VALUE)
                    span = Math.min(span, faciDeadline - hsbCycles);
                if (icusStartupStub != null && icusStartupStub.deadline != Long.MAX_VALUE)
                    span = Math.min(span, icusStartupStub.deadline - hsbCycles);
                if (span <= 0) throw new IllegalStateException("non-advancing peripheral clock");
                hsbCycles = Math.addExact(hsbCycles, span);
                tsg.deferPicRouting();
                // Commit ADC results before qualifying coincident new triggers.
                // Bus reads see the committed peripheral state at this HSB edge.
                adc.advanceHsbClock(thread, span);
                taud.advanceClock(thread, span);
                tauj.advanceClock(thread, span);
                tsg.advanceClock(thread, span);
                rsent.advanceClock(thread, span);
                finishPicRouting(thread);
                if (hsbCycles == faciDeadline) completeFaciOperation();
                if (icusStartupStub != null && icusStartupStub.deadline != Long.MAX_VALUE
                        && hsbCycles == icusStartupStub.deadline)
                    icusStartupStub.complete();
                dma.advanceClock(thread);
                cycles -= span;
            }
        }

        Csih csih(RegisterDef register) {
            Csih bound = csihBindings.get(register);
            if (bound != null) return bound;
            String prefix = register.name.substring(0, 5);
            return csihControllers.computeIfAbsent(prefix, Csih::new);
        }

        // Section14 word-level wire boundary: no synthetic baud clock or ASIC.
        // FIFO shares 128 entries; dual buffer has separate 64-entry banks.
        final class Csih {
            final String prefix;
            final RegisterDef control;
            final Map<String, RegisterDef> bank = new HashMap<>();
            final Map<RegisterDef, String> suffixes = new HashMap<>();
            final RegisterDef[] configurations = new RegisterDef[8];
            final RegisterDef[] baudRates = new RegisterDef[4];
            final long[] tx = new long[128];
            final long[] rx = new long[128];
            final boolean[] txValid = new boolean[128];
            final boolean[] rxValid = new boolean[128];
            final List<Long> frame = new ArrayList<>();
            int queued;
            int received;
            boolean active;
            boolean launched;
            boolean bufferStarted;
            boolean txHeaderKnown;
            boolean directRxUnread;
            long txHeader;
            long activeWord;
            int generation;
            // Scenario wire ordinals are independent of controller resets.
            long transmittedWords;
            List<ExternalEvent> relativeInputs;
            int nextRelativeInput;

            Csih(String prefix) {
                this.prefix = prefix;
                control = requiredRegister(prefix, "control", prefix + "CTL0");
                if (!control.name.equals(control.control_register) || control.interrupt_channel_base == null)
                    throw new IllegalStateException(prefix + " lacks CSIH controller/IRQ metadata");
                for (RegisterDef register : registers) {
                    if (!"csih".equals(register.behavior) || !register.name.startsWith(prefix)) continue;
                    String suffix = register.name.substring(prefix.length());
                    bank.put(suffix, register);
                    suffixes.put(register, suffix);
                    csihBindings.put(register, this);
                }
                for (int index = 0; index < configurations.length; index++) configurations[index] = reg("CFG" + index);
                for (int index = 0; index < baudRates.length; index++) baudRates[index] = reg("BRS" + index);
            }
            RegisterDef reg(String suffix) {
                RegisterDef register = bank.get(suffix);
                if (register == null) throw new IllegalStateException(prefix + " lacks " + suffix + " metadata");
                return register;
            }
            long cfg(int index) { return registerValue(configurations[index]); }
            long get(String suffix) { return registerValue(reg(suffix)); }
            void put(String suffix, long value) { setRegisterValue(reg(suffix).name, value); }
            int mode() { return (get("CTL0") & 1) != 0 ? -1 : (int) (get("MCTL0") >> 8) & 3; }
            int capacity() { return mode() == 1 ? 64 : 128; }
            int pointer(String suffix, int shift) { return (int) (get(suffix) >> shift) & 127; }
            void pointer(String suffix, int shift, int value) {
                put(suffix, (get(suffix) & ~(127L << shift)) | ((long) value << shift));
            }
            void reset() {
                generation++;
                queued = received = 0;
                active = launched = bufferStarted = txHeaderKnown = directRxUnread = false;
                Arrays.fill(txValid, false);
                Arrays.fill(rxValid, false);
                frame.clear();
            }
            void clearPointers() {
                generation++;
                queued = received = 0;
                active = launched = bufferStarted = directRxUnread = false;
                put("MRWP0", 0);
                put("MCTL2", 0);
                frame.clear();
                status();
            }
            void status() {
                long flags = get("STR0") & 0xC10BL;
                if (active || queued != 0 || bufferStarted) flags |= 0x80;
                if (mode() == 0) {
                    flags |= (long) queued << 16 | (long) received << 24;
                    if (queued + received == 0) flags |= 0x10;
                    if (queued + received >= 128) flags |= 0x20;
                } else flags |= 0x10;
                put("STR0", flags);
            }
            RuntimeException boundary(PcodeThread<byte[]> thread, RegisterDef register, String detail) {
                return fault("unsupported-csih-operation", thread, register.address, register.size,
                    "device", register.evidence, prefix + ": " + detail);
            }
            long mask(RegisterDef register) {
                if (register.writable_mask != null) return register.writable_mask;
                if (register.name.startsWith(prefix + "CFG")) return 0xFF0FFFFFL;
                if (register.name.startsWith(prefix + "BRS")) return 0xFFFL;
                throw new IllegalStateException("CSIH writable mask missing: " + register.name);
            }
            void validateWrite(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                if ((value & ~mask(register)) != 0)
                    throw boundary(thread, register, "reserved bits must be zero");
                String name = suffixes.get(register);
                if ("MCTL0".equals(name) && (value & 0x300) == 0x300)
                    throw boundary(thread, register, "MMS=11 is prohibited");
                if (!"CTL0".equals(name) && !"STCR0".equals(name)
                        && !"MRWP0".equals(name) && !"MCTL1".equals(name)
                        && !"MCTL2".equals(name) && !"tx".equals(register.trigger)
                        && !"tx-half".equals(register.trigger)
                        && (get("CTL0") & 0x80) != 0 && value != get(name))
                    throw boundary(thread, register, "configuration changes require PWR=0");
                if ("CTL0".equals(name) && active && (value & 0x80) != 0
                        && ((value ^ get("CTL0")) & 0x61) != 0)
                    throw boundary(thread, register, "TXE/RXE/MBS changes during active transfer");
                if ("MRWP0".equals(name) && mode() == 1
                        && ((value & 127) >= 64 || ((value >> 16) & 127) >= 64))
                    throw boundary(thread, register, "dual-buffer pointer exceeds 63");
                if ("MCTL2".equals(name) && active && (value & 0xFF007F) != get("MCTL2"))
                    throw boundary(thread, register, "ND/SOP must not change during a buffer transfer");
                if ("MCTL2".equals(name) && mode() != 0 && mode() != -1
                        && (((value >> 16) & 255) > capacity() || (value & 127) >= capacity()))
                    throw boundary(thread, register, "buffer count/start exceeds implemented bank");
                if ("MCTL2".equals(name) && (value & 0x80000000L) != 0
                        && (mode() == 0 || mode() == -1 || active))
                    throw boundary(thread, register, "BTST requires idle dual/transmit-only buffer mode");
                if ("tx-half".equals(register.trigger) && !txHeaderKnown)
                    throw boundary(thread, register, "TX0H requires an earlier TX0W header");
                if ("tx".equals(register.trigger) && (value & 0xFF0000) == 0xFF0000)
                    throw boundary(thread, register, "all chip selects inactive is prohibited");
            }
            void write(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                String name = suffixes.get(register);
                if ("CTL0".equals(name)) {
                    put("CTL0", value & ~2L);
                    if ((registerBeforeWrite & 0x80) != 0 && (value & 0x80) == 0) {
                        clearPointers();
                    }
                    if (((registerBeforeWrite ^ value) & 0x80) != 0) put("STR0", get("STR0") & ~0xC00BL);
                    start(thread);
                } else if ("STCR0".equals(name)) {
                    put("STR0", get("STR0") & ~(value & 0xC00B));
                    if ((value & 0x100) != 0) clearPointers();
                    put("STCR0", 0);
                } else if ("MCTL2".equals(name)) {
                    put("MCTL2", value & 0xFF007F);
                    if ((value & 0x80000000L) != 0) {
                        bufferStarted = ((value >> 16) & 255) != 0;
                        start(thread);
                    }
                } else if ("tx".equals(register.trigger) || "tx-half".equals(register.trigger)) {
                    if ("tx".equals(register.trigger)) {
                        txHeaderKnown = true;
                        txHeader = value & 0xFFFF0000L;
                    } else value |= txHeader;
                    if (mode() == 0 && queued + received >= 128) {
                        put("STR0", get("STR0") | 0x4000);
                        interrupt(thread, 0, value);
                    } else if (mode() == -1 && queued >= 2) {
                        throw boundary(thread, register, "direct shift/data register already occupied");
                    } else {
                        int index = mode() == -1 ? queued : pointer("MRWP0", 0);
                        tx[index] = value;
                        txValid[index] = true;
                        put("TX0W", value);
                        put("TX0H", value & 0xFFFF);
                        if (mode() == 0 || mode() == -1) queued++;
                        if (mode() != -1) pointer("MRWP0", 0, (index + 1) % capacity());
                        start(thread);
                    }
                }
                status();
            }
            void requireNormal(PcodeThread<byte[]> thread) {
                if (mode() == 3)
                    throw boundary(thread, reg("MCTL0"), "MMS=11 is prohibited");
                if ((get("CTL1") & 0x4006BL) != 0)
                    throw boundary(thread, reg("CTL1"), "job, priority, data-consistency, loopback, handshake and slave-select pin modes are not modeled");
                if ((get("MCTL0") & 31) != 0)
                    throw boundary(thread, reg("MCTL0"), "FIFO timeout needs serial-clock elapsed-time input");
                if ((get("CTL0") & 0x60) == 0x20)
                    throw boundary(thread, control, "receive-only clock generation requires explicit pin/clock mode");
            }
            void start(PcodeThread<byte[]> thread) {
                if (active || (get("CTL0") & 0x80) == 0 || (get("CTL0") & 0x60) == 0) return;
                if (mode() <= 0 ? queued == 0 : !bufferStarted) return;
                requireNormal(thread);
                int index = mode() == -1 ? 0 : pointer("MCTL2", 0);
                if (!txValid[index]) throw boundary(thread, reg("TX0W"), "transfer reads unwritten transmit buffer entry " + index);
                int selected = selected(tx[index]);
                long configuration = cfg(selected);
                // Section14.5.3.1: RCB priority applies only to simultaneous CS lines.
                int selectedLines = (int) (~(tx[index] >>> 16)) & 255;
                boolean broadcast = (selectedLines & (selectedLines - 1)) != 0;
                if (broadcast && (configuration & 0x80000) != 0)
                    throw boundary(thread, reg("TX0W"), "broadcast has no dominant chip-select configuration");
                for (int cs = 0; cs < 8; cs++) {
                    long other = cfg(cs);
                    if ((tx[index] & (1L << (16 + cs))) == 0 && (other & 0x80000) == 0
                            && other != configuration)
                        throw boundary(thread, reg("TX0W"), "dominant broadcast configurations disagree");
                }
                if ((get("CTL2") & 0xE000) != 0xE000
                        && registerValue(baudRates[(int) (configuration >> 30) & 3]) == 0) return;
                if (!frame.isEmpty() && (frame.get(0) & 0xFF0000) != (tx[index] & 0xFF0000))
                    throw boundary(thread, reg("TX0W"), "EDL continuation changes chip select");
                activeWord = tx[index];
                active = true;
                launched = false;
                status();
                int epoch = generation;
                scheduleNextTick(() -> {
                    if (epoch != generation || !active) return;
                    launched = true;
                    JsonObject event = event("csih-tx");
                    event.addProperty("word", hex32(activeWord));
                    int bits = dataBits(activeWord);
                    event.addProperty("value", hex32(activeWord & ((1L << bits) - 1)));
                    event.addProperty("chip_select", (activeWord >> 16) & 255);
                    int cs = selected(activeWord);
                    long cfg = cfg(cs);
                    event.addProperty("bits", bits);
                    event.addProperty("lsb_first", (cfg & 0x40000) != 0);
                    long wordOrdinal = ++transmittedWords;
                    event.addProperty("transmit_ordinal", wordOrdinal);
                    trace.deviceEvents.add(event);
                    if (relativeInputs != null && nextRelativeInput < relativeInputs.size()
                            && relativeInputs.get(nextRelativeInput).after_transmit_words == wordOrdinal) {
                        ExternalEvent input = relativeInputs.get(nextRelativeInput++);
                        long tick = Math.addExact(trace.instructions, input.delay_instructions);
                        externalEvents.add(new ScheduledEvent(tick, input.ordinal, () -> {
                            // An aborted transfer cannot consume a later word's input.
                            if (epoch != generation || wordOrdinal != transmittedWords
                                    || !active || !launched) return;
                            complete(thread, input);
                        }));
                    }
                    boolean early = mode() == -1 || mode() == 2;
                    boolean request = mode() == -1 || ((get("MCTL2") >> 16) & 255) == 1;
                    if (early && request && (get("CTL1") & 0x10000) != 0) interrupt(thread, 2, activeWord);
                });
            }
            int dataBits(long word) {
                int bits = (int) (cfg(selected(word)) >> 24) & 15;
                return bits == 0 || ((get("CTL1") & 0x80) != 0 && (word & 0x20000000L) != 0) ? 16 : bits;
            }
            int selected(long word) {
                int selected = (int) (~word >> 16) & 255;
                for (int cs = 0; cs < 8; cs++)
                    if ((selected & (1 << cs)) != 0 && (cfg(cs) & 0x80000) == 0) return cs;
                return Integer.numberOfTrailingZeros(selected);
            }
            JsonObject event(String kind) {
                JsonObject event = new JsonObject();
                event.addProperty("kind", kind);
                event.addProperty("unit", Integer.parseInt(prefix.substring(4)));
                event.addProperty("scheduler_tick", trace.instructions);
                event.addProperty("evidence", "R01UH0585EJ0120 section14.3-14.5");
                return event;
            }
            void interruptSource(PcodeThread<byte[]> thread, int kind) {
                int base = control.interrupt_channel_base;
                requestInterrupt(thread, base + kind);
                if (kind == 0) return; // Communication error has no DMAC trigger.
                if (base == 82 || base == 90)
                    dma.request(thread, (base == 82 ? 64 : 71) + kind);
                else if (kind <= 2)
                    dma.request(thread, (base == 98 ? 78 : 81) + kind);
            }
            void interrupt(PcodeThread<byte[]> thread, int kind, long word) {
                int base = control.interrupt_channel_base;
                if (base == 82 || base == 90) {
                    if (kind == 3) kind = 7;
                    else if (kind == 1 || kind == 2) {
                        int select = (int) registerValue(requiredRegister(prefix, "DMA selector", "SELCSIHDMA"));
                        int shift = base == 82 ? 0 : 2;
                        int bit = kind == 1 ? shift + 1 : shift;
                        if ((select & (1 << bit)) == 0 || (word & 0x10000) == 0)
                            interruptSource(thread, kind);
                        if ((word & 0x20000) == 0) interruptSource(thread, kind + 2);
                        if ((word & 0x40000) == 0) interruptSource(thread, kind + 4);
                        return;
                    }
                }
                interruptSource(thread, kind);
            }
            void complete(PcodeThread<byte[]> thread, ExternalEvent input) {
                if (!active || !launched)
                    throw boundary(thread, control, "csih-word has no launched transfer to complete");
                boolean receive = (get("CTL0") & 0x20) != 0;
                if (receive != (input.value != null))
                    throw boundary(thread, control, "RXE requires explicit wire value; TX-only completion omits value");
                long word = activeWord;
                int memoryMode = mode();
                int index = memoryMode == -1 ? 0 : pointer("MCTL2", 0);
                if (receive) {
                    long receivedWord = (word & 0xFF0000) | (parseUnsigned(input.value) & ((1L << dataBits(word)) - 1));
                    if (memoryMode == 1 || memoryMode == 0) {
                        if (memoryMode == 0) tx[index] = receivedWord;
                        rx[index] = receivedWord;
                        rxValid[index] = true;
                        if (memoryMode == 0) received++;
                    } else {
                        if (directRxUnread) {
                            put("STR0", get("STR0") | 1);
                            interrupt(thread, 0, word);
                        }
                        rx[0] = receivedWord;
                        rxValid[0] = directRxUnread = true;
                    }
                    put("RX0W", receivedWord);
                    put("RX0H", receivedWord & 0xFFFF);
                }
                active = launched = false;
                if (memoryMode <= 0) {
                    queued--;
                    if (memoryMode == -1 && queued != 0) { tx[0] = tx[1]; txValid[0] = txValid[1]; }
                } else {
                    int remaining = (int) (get("MCTL2") >> 16) & 255;
                    put("MCTL2", ((long) (remaining - 1) << 16) | ((index + 1) % capacity()));
                    bufferStarted = remaining > 1;
                }
                if (memoryMode == 0) pointer("MCTL2", 0, (index + 1) % 128);
                boolean last = memoryMode <= 0 ? queued == 0 : !bufferStarted;
                if (receive && (memoryMode == 0 ? received == 128 - (get("MCTL1") & 127)
                        : memoryMode != 1 || last)) interrupt(thread, 1, word);
                boolean communicate = memoryMode == 0 ? queued == ((get("MCTL1") >> 16) & 127)
                    : memoryMode == -1 ? (get("CTL1") & 0x10000) == 0
                    : last;
                if (communicate && !((memoryMode == -1 || memoryMode == 2)
                        && (get("CTL1") & 0x10000) != 0)) interrupt(thread, 2, word);
                frame.add(word);
                boolean continued = (get("CTL1") & 0x80) != 0 && (word & 0x20000000L) != 0;
                if (!continued) {
                    JsonObject evidence = event("csih-frame");
                    evidence.add("words", GSON.toJsonTree(frame));
                    trace.deviceEvents.add(evidence);
                    frame.clear();
                }
                JsonObject evidence = event("csih-word");
                if (receive) evidence.addProperty("value", input.value);
                evidence.addProperty("input_evidence", input.evidence);
                trace.deviceEvents.add(evidence);
                status();
                start(thread);
            }
            void read(PcodeThread<byte[]> thread, RegisterDef register) {
                if ("rx".equals(register.trigger)) {
                    int index = mode() == -1 || mode() == 2 ? 0 : pointer("MRWP0", 16);
                    if (!rxValid[index] || (mode() == 0 && received == 0))
                        throw boundary(thread, register, "receive data is not supplied at buffer entry " + index);
                    setRegisterValue(register.name, register.size == 2 ? rx[index] & 0xFFFF : rx[index]);
                    directRxUnread = false;
                    if (mode() == 0) received--;
                    if (mode() == 0 || mode() == 1) pointer("MRWP0", 16, (index + 1) % capacity());
                    status();
                } else if ("tx".equals(register.trigger) || "tx-half".equals(register.trigger)) {
                    if (mode() == -1) {
                        if (!txHeaderKnown) throw boundary(thread, register, "direct transmit register is unwritten");
                        return;
                    }
                    int index = mode() == -1 ? 0 : pointer("MRWP0", 0);
                    if (!txValid[index]) throw boundary(thread, register, "transmit buffer entry is unwritten");
                    setRegisterValue(register.name, register.size == 2 ? tx[index] & 0xFFFF : tx[index]);
                    if (mode() != -1) pointer("MRWP0", 0, (index + 1) % capacity());
                }
            }
        }

        final class Tsg {
            static final int[] CMP = {0x14c,0x17c,0x178,0x164,0x160,0x174,0x170,
                0x15c,0x158,0x16c,0x168,0x154,0x150};
            static final int[] RELOAD = {0x078,0x06c,0x070,0x140,0x144,0x148,
                0x14c,0x17c,0x178,0x164,0x160,0x174,0x170,0x15c,0x158,
                0x16c,0x168,0x154,0x150};
            static final int[] DUTY_COMPARE = {1,2,5,6,9,10};
            static final int[] PIC_COMPARE = {3,4,7,8,11,12};
            final Unit[] units = {new Unit(0), new Unit(1)};
            final RegisterDef[][] selectors = new RegisterDef[2][5];
            final RegisterDef[] edgeSelect = new RegisterDef[2];
            final boolean[][] picHigh = new boolean[2][5];
            final long[][] picSelect = new long[2][5];
            final int[] picEdges = new int[2];
            long picTsgSources, picOtherSources, nextSources;
            boolean picRoutingDeferred, picDirty, clockHorizonDirty = true;
            long clockHorizon = Long.MAX_VALUE;

            Tsg() {
                for (int n = 0; n < 2; n++) {
                    edgeSelect[n] = requiredRegister("TSG PIC", "edge", "PIC2BADCG" + n + "EDGSEL");
                    for (int g = 0; g < 5; g++) selectors[n][g] = requiredRegister(
                        "TSG PIC", "select", "PIC2BADCG" + n + "TSEL" + g);
                }
            }
            Unit unit(RegisterDef register) {
                return units[register.name.charAt(4) - '0'];
            }
            boolean isTimer(RegisterDef register) { return "tsg".equals(register.behavior); }
            void reset() {
                for (Unit u : units) u.reset();
                picTsgSources = picOtherSources = nextSources = 0;
                picRoutingDeferred = picDirty = false;
                clockHorizonDirty = true; clockHorizon = Long.MAX_VALUE;
                Arrays.fill(picEdges, 0);
                for (int n = 0; n < 2; n++) {
                    Arrays.fill(picHigh[n], false);
                    Arrays.fill(picSelect[n], 0);
                }
            }
            void initializeFromDeclaredState(PcodeThread<byte[]> thread, Set<String> declaredRegisters) {
                if (declaredRegisters == null) throw new IllegalArgumentException("initial register declarations required");
                for (Unit u : units) u.initializeFromDeclaredState(thread, declaredRegisters);
                clockHorizonDirty = true;
                for (int n = 0; n < 2; n++) {
                    picEdges[n] = (int) registerValue(edgeSelect[n]);
                    validate(thread, edgeSelect[n], picEdges[n]);
                    for (int g = 0; g < 5; g++) {
                        picSelect[n][g] = registerValue(selectors[n][g]);
                        validate(thread, selectors[n][g], picSelect[n][g]);
                    }
                }
                // Configuration declarations do not imply live timer/PIC pulses.
            }
            RuntimeException unsupported(PcodeThread<byte[]> thread, RegisterDef register, String detail) {
                return fault("unsupported-tsg-operation", thread, register.address, register.size,
                    "peripheral", register.source_ref, detail);
            }
            void validate(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                long mask = register.writable_mask == null ? 0xffffffffL : register.writable_mask;
                if ((value & ~mask) != 0) throw fault("reserved-tsg-bits", thread,
                    register.address, register.size, "write", register.source_ref,
                    "reserved bits must have their reset value");
                if (isTimer(register)) { unit(register).validate(thread, register, value); return; }
                for (int n = 0; n < 2; n++) if (register == edgeSelect[n]) {
                    for (int g = 0; g < 5; g++) if (((value >>> (2 * g)) & 3) == 3)
                        throw unsupported(thread, register, "PIC2 EDGSEL=3 is prohibited");
                }
            }
            void read(PcodeThread<byte[]> thread, RegisterDef register) {
                Unit u = unit(register);
                if (u.offset(register) == 0x014) throw unsupported(thread, register,
                    "STR1 includes output/input pattern observations; no pin feedback is synthesized");
                u.materialize(register);
            }
            void write(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                if (isTimer(register)) {
                    unit(register).write(thread, register, value);
                    clockHorizonDirty = true;
                    return;
                }
                boolean changed = false;
                for (int n = 0; n < 2; n++) {
                    if (register == edgeSelect[n] && picEdges[n] != (int) value) {
                        picEdges[n] = (int) value; changed = true;
                    }
                    for (int g = 0; g < 5; g++) if (register == selectors[n][g]
                            && picSelect[n][g] != value) {
                        picSelect[n][g] = value; changed = true;
                    }
                }
                if (changed) picSourcesChanged(thread);
            }
            // Only bits 8/9 are consumed. Other timer starts remain the PIC owner's responsibility.
            void validateSimultaneousStart(PcodeThread<byte[]> thread, long selected) {
                for (int n = 0; n < 2; n++) if ((selected & (0x100L << n)) != 0)
                    units[n].validateStart(thread);
            }
            void simultaneousStart(PcodeThread<byte[]> thread, long selected) {
                validateSimultaneousStart(thread, selected);
                for (int n = 0; n < 2; n++) if ((selected & (0x100L << n)) != 0)
                    units[n].start(thread);
            }
            // ENCA/external sources need their own explicit producers; TAUD is group-specific.
            void setOtherPicSources(PcodeThread<byte[]> thread, long mask, boolean high) {
                if ((mask & ~0x10cL) != 0)
                    throw new IllegalArgumentException("PIC2 mask must contain only ENCA bits2/3 or external bit8");
                long next = high ? picOtherSources | mask : picOtherSources & ~mask;
                if (next == picOtherSources) return;
                picOtherSources = next;
                picSourcesChanged(thread);
            }
            // TAUD calls only when its group-specific source bitmap actually changes.
            void picSourcesChanged(PcodeThread<byte[]> thread) {
                picDirty = true;
                routePic(thread);
            }
            void deferPicRouting() { picRoutingDeferred = true; }
            void flushPic(PcodeThread<byte[]> thread) {
                picRoutingDeferred = false;
                routePic(thread);
            }
            void routePic(PcodeThread<byte[]> thread) {
                if (picRoutingDeferred || !picDirty) return;
                picDirty = false;
                for (int g = 0; g < 5; g++) {
                    long sources = picTsgSources | picOtherSources | taud.picSources(g);
                    for (int n = 0; n < 2; n++) {
                        boolean high = (picSelect[n][g] & sources) != 0;
                        boolean old = picHigh[n][g];
                        if (old == high) continue;
                        picHigh[n][g] = high;
                        int edge = (picEdges[n] >>> (2 * g)) & 3;
                        if (edge == 3) throw unsupported(thread, edgeSelect[n], "PIC2 EDGSEL=3 is prohibited");
                        if (edge == 2 || (high && edge == 0) || (!high && edge == 1))
                            adc.hardwareTrigger(thread, n, g);
                    }
                }
            }
            long cyclesUntilEvent() {
                if (clockHorizonDirty) {
                    clockHorizon = picTsgSources == 0 ? Long.MAX_VALUE : 1;
                    for (Unit u : units) clockHorizon = Math.min(clockHorizon, u.cyclesUntilEvent());
                    clockHorizonDirty = false;
                }
                return clockHorizon;
            }
            // hsbCycles is actual divided/gated CLK_HSB; never CPU instruction ticks.
            void advanceClock(PcodeThread<byte[]> thread, long hsbCycles) {
                if (hsbCycles < 0) throw new IllegalArgumentException("negative HSB cycles");
                while (hsbCycles != 0) {
                    long span = cyclesUntilEvent();
                    if (hsbCycles < span) {
                        for (Unit u : units) u.moveQuiet(hsbCycles);
                        if (clockHorizon != Long.MAX_VALUE) clockHorizon -= hsbCycles;
                        return;
                    }
                    if (span > 1) for (Unit u : units) u.moveQuiet(span - 1);
                    nextSources = 0;
                    // Commit every timer's clock edge before DMA can write any timer's shadow bank.
                    for (Unit u : units) u.edge(thread);
                    for (Unit u : units) u.deliver(thread);
                    if (picTsgSources != nextSources) {
                        picTsgSources = nextSources;
                        picSourcesChanged(thread);
                    }
                    clockHorizonDirty = true;
                    hsbCycles -= span;
                }
            }
            // Parent calls once for final raw-register checks, not on each clock quantum.
            void flushSnapshot() {
                for (Unit u : units) u.publish();
            }

            final class Unit {
                final int index, irqBase;
                final long base;
                final RegisterDef[] bank = new RegisterDef[0x88];
                final long[] desired = new long[0x88], active = new long[0x88];
                final int[] adSkip = new int[2];
                boolean enabled, down, subDown, pending, ctl4Dirty, ioc3Dirty, initialSub;
                boolean activeKnown;
                long counter, subCounter;
                int irqSkip, interrupts;
                Unit(int index) {
                    this.index = index;
                    base = 0xffe70000L + index * 0x1000L;
                    irqBase = 40 + 17 * index;
                    for (RegisterDef r : registers) if ("tsg".equals(r.behavior)
                            && r.address >= base && r.address < base + 0x220)
                        bank[(int) (r.address - base) >>> 2] = r;
                }
                int offset(RegisterDef register) { return (int) (register.address - base); }
                long v(int offset) { return desired[offset >>> 2]; }
                long a(int offset) {
                    if (!activeKnown) throw new IllegalStateException("TSG active buffers are unknown before a real start");
                    return active[offset >>> 2];
                }
                void put(int offset, long value) {
                    RegisterDef r = bank[offset >>> 2];
                    if (r == null) throw new IllegalStateException("TSG metadata missing offset " + offset);
                    setRegisterValue(r.name, value);
                }
                void store(int offset, long value) { desired[offset >>> 2] = value; put(offset, value); }
                boolean reloadable(int offset) {
                    for (int candidate : RELOAD) if (candidate == offset) return true;
                    return offset == 0x180 || offset == 0x184 || offset == 0x188;
                }
                boolean runningFixed(int offset) {
                    return offset == 0x208 || offset == 0x20c || offset == 0x210
                        || offset == 0x200 || offset == 0x204;
                }
                void reset() {
                    Arrays.fill(desired, 0); Arrays.fill(active, 0); Arrays.fill(adSkip, 0);
                    desired[0x200 >>> 2] = 0x7e;
                    enabled = down = subDown = pending = ctl4Dirty = ioc3Dirty = initialSub = false;
                    counter = subCounter = 0;
                    irqSkip = interrupts = 0;
                    activeKnown = true;
                }
                RuntimeException initialFault(PcodeThread<byte[]> thread, int offset, String detail) {
                    RegisterDef r = bank[offset >>> 2];
                    return fault("unsupported-tsg-initial-state", thread, r.address, r.size,
                        "initial-state", r.source_ref, detail);
                }
                boolean declared(Set<String> names, int offset) {
                    return names.contains(bank[offset >>> 2].name);
                }
                void initializeCounterPair(PcodeThread<byte[]> thread, Set<String> names,
                                           int extended, int low) {
                    long full = v(extended), half = v(low);
                    if (declared(names, low) && !declared(names, extended))
                        full = (full & 0x30000) | half;
                    else if (declared(names, extended) && !declared(names, low))
                        half = full & 0xffff;
                    if ((full & 0xffff) != half) throw initialFault(thread, extended,
                        "counter and low-counter declarations disagree; no hidden counter value is inferred");
                    store(extended, full); store(low, half);
                }
                void initializeFromDeclaredState(PcodeThread<byte[]> thread, Set<String> names) {
                    reset();
                    for (RegisterDef r : bank) {
                        if (r == null) continue;
                        int o = offset(r);
                        long value = registerValue(r);
                        boolean command = o == 0x01c || o == 0x030 || o == 0x034 || o == 0x038;
                        if (command && value != 0) throw initialFault(thread, o,
                            "nonzero initial command storage is not an executed peripheral command");
                        long mask;
                        if (o == 0x010 || o == 0x014) mask = 0xf;
                        else if (o == 0x018) mask = 0x3fe;
                        else if (o == 0x028 || o == 0x02c) mask = 0xffff;
                        else if (o == 0x1a0 || o == 0x1a4) mask = 0x3ffff;
                        else if (o == 0x06c || o == 0x070) mask = 0x3ff;
                        else mask = r.writable_mask == null ? 0xffffffffL : r.writable_mask;
                        if ((value & ~mask) != 0) throw initialFault(thread, o,
                            "initial register readback contains reserved or write-only code bits");
                        desired[o >>> 2] = value;
                    }
                    if ((v(0x010) & 1) != 0) throw initialFault(thread, 0x010,
                        "TE=1 does not specify hidden active buffers, skip phase or live pulses; resume requires an explicit complete device-state format");
                    if (v(0x014) != 0) throw initialFault(thread, 0x014,
                        "initial pin/output pattern observations are outside this timer lifecycle model");
                    if ((v(0x208) != 0 && v(0x208) != 1) || v(0x004) != 0
                            || v(0x078) != 0 || v(0x20c) != 0 || v(0x204) != 0
                            || v(0x000) != 0 || v(0x074) != 0 || v(0x020) != 0 || v(0x024) != 0)
                        throw initialFault(thread, 0x208,
                            "stopped configuration selects an unsupported mode, input dependency or output override");
                    if (((v(0x06c) | v(0x070) | v(0x14c)) & 1) != 0)
                        throw initialFault(thread, 0x14c, "HT-PWM period and deadtimes must be even");
                    for (int phase = 0; phase < 3; phase++) {
                        int alias = 0x188 - 4 * phase;
                        int first = CMP[1 + 4 * phase], second = CMP[2 + 4 * phase];
                        long value = v(alias);
                        if (declared(names, alias)) {
                            if ((declared(names, first) && v(first) != value)
                                    || (declared(names, second) && v(second) != value))
                                throw initialFault(thread, alias,
                                    "phase alias and extended compare declarations conflict");
                            store(first, value); store(second, value);
                        } else if (value != v(first) && !declared(names, first)) {
                            throw initialFault(thread, alias,
                                "alias override is ambiguous without its exact scenario declaration name");
                        }
                        store(alias, v(first));
                    }
                    initializeCounterPair(thread, names, 0x1a0, 0x028);
                    initializeCounterPair(thread, names, 0x1a4, 0x02c);
                    counter = v(0x1a0); subCounter = v(0x1a4);
                    if (v(0x208) == 1 && ((counter | subCounter) & 1) != 0)
                        throw initialFault(thread, 0x1a0, "HT-PWM counter readback bit0 must be zero");
                    pending = (v(0x010) & 2) != 0;
                    subDown = (v(0x010) & 4) != 0; down = (v(0x010) & 8) != 0;
                    // Visible stopped state has no authoritative active/shadow relationship.
                    activeKnown = false;
                    Arrays.fill(active, -1L);
                    publish();
                }
                void validate(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                    int o = offset(register);
                    if ((o == 0x06c || o == 0x070) && ((v(0x210) & 0x8000) != 0
                            || ((value >>> 16) & 0x7fff) != (v(0x210) & 0x7fff))) return;
                    if ((o == 0x208 && value != 1) || (o == 0x004 && value != 0)
                            || (o == 0x078 && value != 0) || (o == 0x20c && value != 0)
                            || (o == 0x204 && value != 0) || (o == 0x000 && value != 0)
                            || (o == 0x074 && value != 0) || (o == 0x020 && value != 0)
                            || (o == 0x024 && value != 0))
                        throw unsupported(thread, register,
                            "implemented mode is symmetric HT-PWM, direct PCLK, reload RIA=0, no pattern/error detection or output override");
                    if (enabled && runningFixed(o) && value != v(o))
                        throw unsupported(thread, register, "register changes are prohibited while TE=1");
                    if (enabled && pending && reloadable(o))
                        throw fault("prohibited-tsg-reload-write", thread, register.address,
                            register.size, "write", register.source_ref,
                            "registers to reload must not be rewritten while RSF=1 (section25.4.1.3)");
                    if ((o == 0x06c || o == 0x070) && (v(0x210) & 0x8000) == 0
                            && ((value >>> 16) & 0x7fff) == (v(0x210) & 0x7fff)) {
                        if ((value & 1) != 0) throw unsupported(thread, register, "HT-PWM deadtime must be even");
                        if (enabled && (value & 0x3ff) != a(o))
                            throw unsupported(thread, register,
                                "live deadtime change requires the separate conditional rewrite waveform protocol; not selected by original startup/runtime");
                    }
                    if (o == 0x14c && (value & 1) != 0)
                        throw unsupported(thread, register, "HT-PWM period must be even");
                    for (int m = 1; m < CMP.length; m++) if (o == CMP[m] && (value & 1) != 0)
                        throw unsupported(thread, register, "direct HT-PWM CMPmE values must be even; phase aliases own additional-pulse LSB");
                    if (o == 0x038 && value != 0)
                        throw unsupported(thread, register, "IMT is prohibited in reload mode");
                    if (o == 0x030 && (value & 1) != 0) validateStart(thread);
                }
                void validateValues(PcodeThread<byte[]> thread) {
                    long p = v(0x14c), d0 = v(0x06c), d1 = v(0x070);
                    if ((p & 1) != 0 || p <= 3 * Math.max(d0, d1)
                            || p + d0 + d1 > 0x3fffe)
                        throw unsupported(thread, bank[0x14c >>> 2],
                            "HT-PWM requires even CMP0E >3*max(DTC0,DTC1) and CMP0E+DTC0+DTC1<=3FFFE");
                    for (int m : DUTY_COMPARE) if (v(CMP[m]) > p + d0 + d1)
                        throw unsupported(thread, bank[CMP[m] >>> 2], "phase duty exceeds HT-PWM allowed range");
                }
                void validateStart(PcodeThread<byte[]> thread) {
                    if (v(0x208) != 1 || v(0x004) != 0 || v(0x078) != 0
                            || (v(0x07c) & 0x180) == 0)
                        throw unsupported(thread, bank[0x208 >>> 2],
                            "start requires HT-PWM, ungated PCLK, RIA=RMC=0 and a peak or valley reload timing");
                    validateValues(thread);
                }
                void write(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                    int o = offset(register);
                    if (o == 0x030 || o == 0x034 || o == 0x038) {
                        put(o, 0);
                        if ((value & 1) != 0) {
                            if (o == 0x030) start(thread);
                            else if (o == 0x034) { enabled = false; publishStatus(); }
                        }
                        return;
                    }
                    if (o == 0x01c) { store(0x018, v(0x018) & ~value); put(o, 0); return; }
                    if (o == 0x06c || o == 0x070) {
                        if ((v(0x210) & 0x8000) != 0
                                || ((value >>> 16) & 0x7fff) != (v(0x210) & 0x7fff)) {
                            put(o, v(o)); return; // Hardware rejects locked/mismatched deadtime writes.
                        }
                        value &= 0x3ff; // Protection-code lanes are write-only and read zero.
                    }
                    store(o, value);
                    if (o == 0x180 || o == 0x184 || o == 0x188) {
                        int m = o == 0x188 ? 1 : o == 0x184 ? 5 : 9;
                        store(CMP[m], value); store(CMP[m + 1], value);
                    }
                    if (o == 0x17c) put(0x188, v(0x17c));
                    if (o == 0x174) put(0x184, v(0x174));
                    if (o == 0x16c) put(0x180, v(0x16c));
                    if (o == 0x188 || o == 0x17c) pending = true;
                    if (o == 0x07c) ctl4Dirty = true;
                    if (o == 0x074) ioc3Dirty = true;
                    if (o == 0x008) adSkip[0] = 0;
                    if (o == 0x00c) adSkip[1] = 0;
                    publishStatus();
                }
                void start(PcodeThread<byte[]> thread) {
                    validateStart(thread);
                    clockHorizonDirty = true;
                    for (int o : RELOAD) active[o >>> 2] = v(o);
                    active[0x07c >>> 2] = v(0x07c); active[0x074 >>> 2] = v(0x074);
                    activeKnown = true;
                    if (!enabled) store(0x018, 0);
                    else store(0x018, v(0x018) & 0x380);
                    enabled = true; down = false; subDown = true; initialSub = true;
                    counter = subCounter = a(0x06c);
                    pending = ctl4Dirty = ioc3Dirty = false;
                    irqSkip = 0; Arrays.fill(adSkip, 0);
                    publishStatus();
                }
                void materialize(RegisterDef register) {
                    switch (offset(register)) {
                        case 0x010: publishStatus(); break;
                        case 0x028: put(0x028, counter & 0xffff); break;
                        case 0x1a0: put(0x1a0, counter); break;
                        case 0x02c: put(0x02c, subCounter & 0xffff); break;
                        case 0x1a4: put(0x1a4, subCounter); break;
                        default: break;
                    }
                }
                void publishStatus() {
                    put(0x010, (enabled ? 1 : 0) | (pending ? 2 : 0)
                        | (subDown ? 4 : 0) | (down ? 8 : 0));
                }
                void publish() {
                    publishStatus();
                    put(0x1a0, counter); put(0x028, counter & 0xffff);
                    put(0x1a4, subCounter); put(0x02c, subCounter & 0xffff);
                }
                long until(long value, long target, boolean decrement) {
                    long distance = decrement ? value - target : target - value;
                    return distance < 0 || (distance & 1) != 0 ? Long.MAX_VALUE : distance / 2 + 1;
                }
                long cyclesUntilEvent() {
                    if (!enabled) return Long.MAX_VALUE;
                    long limit = down ? a(0x06c) : a(0x14c) + a(0x06c);
                    long result = until(counter, limit, down);
                    // The initial upward departure from DTC0 is also a period interrupt edge.
                    result = Math.min(result, until(counter, a(0x06c), down));
                    for (int m = 1; m < CMP.length; m++)
                        result = Math.min(result, until(counter, a(CMP[m]) & ~1L, down));
                    for (int o = 0x140; o <= 0x148; o += 4)
                        result = Math.min(result, until(counter, a(o), down));
                    return Math.min(result, until(subCounter,
                        subDown ? 0 : a(0x14c) + a(0x06c) + a(0x070), subDown));
                }
                void moveQuiet(long cycles) {
                    if (!enabled) return;
                    counter += (down ? -2 : 2) * cycles;
                    subCounter += (subDown ? -2 : 2) * cycles;
                    initialSub = false;
                }
                void transfer(PcodeThread<byte[]> thread, boolean peak) {
                    if (pending) {
                        validateValues(thread);
                        if (peak && v(0x14c) != a(0x14c)) throw unsupported(thread,
                            bank[0x14c >>> 2], "peak period changes require asymmetric reload waveform handling; selected mode reloads at valley");
                        for (int o : RELOAD) active[o >>> 2] = v(o);
                        pending = false;
                    }
                    // CTL4 and IOC3 are individually reloaded, not CMP1E-armed common-bank writes.
                    if (ctl4Dirty) { active[0x07c >>> 2] = v(0x07c); ctl4Dirty = false; irqSkip = 0; }
                    if (ioc3Dirty) { active[0x074 >>> 2] = v(0x074); ioc3Dirty = false; }
                }
                void edge(PcodeThread<byte[]> thread) {
                    interrupts = 0;
                    if (!enabled) return;
                    boolean wasDown = down;
                    long d0 = a(0x06c), top = a(0x14c) + d0;
                    boolean peak = !down && counter == top;
                    boolean valley = down && counter == d0;
                    int adSources = 0;
                    // Table25.65: matches are emitted when leaving the compare count, not on arrival.
                    if (counter == d0 && (!down || valley)) interrupts |= 1;
                    for (int m = 1; m < CMP.length; m++) {
                        boolean direction = (m % 4 != 3 || wasDown) && (m % 4 != 0 || !wasDown);
                        if (direction && counter == (a(CMP[m]) & ~1L)) interrupts |= 1 << m;
                    }
                    for (int k = 0; k < 3; k++) if (counter == a(0x148 - k * 4))
                        adSources |= 1 << (2 + 2 * k + (wasDown ? 1 : 0));
                    if (peak || valley) {
                        down = peak;
                        long control = a(0x07c);
                        boolean qualified = (control & (peak ? 0x40 : 0x20)) != 0;
                        if (qualified && ++irqSkip > (control & 31)) {
                            irqSkip = 0; interrupts |= 1 << (peak ? 13 : 14);
                            adSources |= peak ? 2 : 1;
                        }
                        if ((control & (peak ? 0x100 : 0x80)) != 0) transfer(thread, peak);
                        // A counter turn loads the old main counter into the sub-counter.
                        subCounter = counter;
                        subDown = valley ? a(0x06c) != 0 : a(0x070) == 0;
                        if (valley && !subDown) adSources |= 0x100;
                        if (peak && subDown) adSources |= 0x200;
                    } else {
                        if (subDown && subCounter == 0) {
                            subDown = false;
                            if (!initialSub) adSources |= 0x100;
                        } else if (!subDown && subCounter == a(0x14c) + a(0x06c) + a(0x070)) {
                            subDown = true; adSources |= 0x200;
                        }
                        subCounter += subDown ? -2 : 2;
                    }
                    initialSub = false;
                    counter += down ? -2 : 2;
                    for (int c = 0; c < 2; c++) {
                        long control = v(c == 0 ? 0x008 : 0x00c);
                        int sourceMask = adSources;
                        if (a(0x06c) == 0 && a(0x070) != 0) sourceMask &= ~0x100;
                        if (a(0x06c) != 0 && a(0x070) == 0) sourceMask &= ~0x200;
                        if ((control & sourceMask & 0x3ff) == 0) continue;
                        int divisor = 1 << ((control >>> 10) & 3);
                        if (++adSkip[c] == divisor) {
                            adSkip[c] = 0;
                            nextSources |= 1L << (4 + 2 * index + c);
                        }
                    }
                    for (int k = 0; k < PIC_COMPARE.length; k++)
                        if ((interrupts & (1 << PIC_COMPARE[k])) != 0)
                            nextSources |= 1L << (16 + 8 * index + k);
                }
                void deliver(PcodeThread<byte[]> thread) {
                    for (int m = 0; m <= 14; m++) if ((interrupts & (1 << m)) != 0) {
                        requestInterrupt(thread, irqBase + m);
                        if (m == 11 || m == 12) dma.request(thread, 99 + 4 * index + m - 11);
                        if (m == 13 || m == 14) dma.request(thread, 101 + 4 * index + m - 13);
                    }
                }
            }
        }

        final class Taud {
            final Unit[] units = {new Unit(0), new Unit(1)};
            final RegisterDef[][] adcEnable = new RegisterDef[2][5];
            final int[][] adcMasks = new int[2][5];
            boolean picDirty;
            Taud() {
                for (int n = 0; n < 2; n++) for (int g = 0; g < 5; g++)
                    adcEnable[n][g] = requiredRegister("TAUD PIC2", "enable", "PIC2BADTEN4" + n + g);
            }
            Unit unit(RegisterDef r) { return units[r.name.charAt(4) - '0']; }
            RuntimeException unsupported(PcodeThread<byte[]> t, RegisterDef r, String detail) {
                return fault("unsupported-taud-operation", t, r.address, r.size,
                    "peripheral", r.source_ref, detail);
            }
            void reset() {
                for (Unit u : units) u.reset();
                for (int n = 0; n < 2; n++) for (int g = 0; g < 5; g++)
                    adcMasks[n][g] = (int)registerValue(adcEnable[n][g]);
                picDirty = true;
            }
            void read(RegisterDef r) {
                Unit u = unit(r); int o = u.offset(r);
                if (o >= 0x80 && o < 0xc0) setRegisterValue(r.name, u.counters[(o - 0x80) / 4]);
            }
            void flush() {
                for (Unit u : units) for (int c = 0; c < 16; c++)
                    setRegisterValue(u.count[c].name, u.counters[c]);
            }
            void validate(PcodeThread<byte[]> t, RegisterDef r, long v) {
                long mask = r.writable_mask == null ? 0xffffL : r.writable_mask;
                if ((v & ~mask) != 0) throw unsupported(t, r, "reserved bits must retain reset value");
                if ("taud".equals(r.behavior)) unit(r).validate(t, r, v);
            }
            void write(PcodeThread<byte[]> t, RegisterDef r, long v) {
                if ("taud".equals(r.behavior)) {
                    unit(r).write(t, r, (int)v);
                    finishEdges(t);
                } else {
                    int n = r.name.charAt(11) - '0', g = r.name.charAt(12) - '0';
                    adcMasks[n][g] = (int)v; picDirty = true;
                }
            }
            void validateSimultaneousStart(PcodeThread<byte[]> t, long sser0, long sser1) {
                units[0].validateStart(t, (int)sser0 & 0xffff);
                units[1].validateStart(t, (int)sser1 & 0xffff);
            }
            void simultaneousStart(PcodeThread<byte[]> t, long sser0, long sser1) {
                validateSimultaneousStart(t, sser0, sser1);
                units[0].start((int)sser0 & 0xffff);
                units[1].start((int)sser1 & 0xffff);
                finishEdges(t);
            }
            long picSources(int group) {
                long v = 0;
                for (Unit u : units) if ((u.signals & adcMasks[u.number][group]) != 0)
                    v |= 1L << u.number;
                return v;
            }
            void driveInput(PcodeThread<byte[]> t, int number, int channel, boolean high) {
                if (number < 0 || number >= 2 || channel < 0 || channel >= 16)
                    throw new IllegalArgumentException("TAUD input unit/channel out of range");
                Unit u = units[number];
                if (!u.known[channel] || !u.enabled(channel)) {
                    u.known[channel] = true; u.sampled[channel] = high;
                }
                u.driven[channel] = high;
            }
            long cyclesUntilEvent() {
                long next = Long.MAX_VALUE;
                for (Unit u : units) next = Math.min(next, u.deadline());
                return next;
            }
            void advanceClock(PcodeThread<byte[]> t, long hsbCycles) {
                if (hsbCycles < 0) throw new IllegalArgumentException("negative HSB clock span");
                while (hsbCycles != 0) {
                    long span = Math.min(hsbCycles, cyclesUntilEvent());
                    for (Unit u : units) u.advance(span);
                    finishEdges(t);
                    hsbCycles -= span;
                }
            }
            void finishEdges(PcodeThread<byte[]> t) {
                // Channel dependency graph points only downward: no recursion or arbitrary cutoff.
                for (Unit u : units) {
                    if ((u.emitted | u.signals | u.priorSignals) == 0) continue;
                    int raised = 0;
                    for (int c = 0; c < 16; c++) {
                        int bit = 1 << c;
                        if ((u.emitted & ~(u.signals | u.priorSignals) & bit) == 0) continue;
                        raised |= bit;
                        u.cascade(c);
                    }
                    if ((u.signals | u.emitted) != (u.signals | u.priorSignals)) picDirty = true;
                    u.signals |= u.emitted;
                    u.emitted = 0;
                    u.priorSignals = 0;
                    for (int c = 0; c < 16; c++) if ((raised & (1 << c)) != 0) {
                        requestInterrupt(t, (u.number == 0 ? 141 : 158) + c);
                        int alternate = u.number == 0 ? c : c - 5;
                        boolean selectable = alternate >= 0 && alternate <= 10;
                        if (!selectable || (registerValue(u.dmaSelect) & (1L << alternate)) == 0)
                            dma.request(t, (u.number == 0 ? 13 : 29) + c);
                    }
                }
            }
            final class Unit {
                final int number;
                final long base;
                final RegisterDef[] data = new RegisterDef[16], count = new RegisterDef[16],
                    mode = new RegisterDef[16], user = new RegisterDef[16], status = new RegisterDef[16];
                final long[] phase = new long[4], ticks = new long[4];
                final int[] modes = new int[16], edges = new int[16], reloads = new int[16], counters = new int[16];
                final long[] divisors = new long[4];
                int enabledMask, tpsValue, brsValue;
                final boolean[] running = new boolean[16], overflow = new boolean[16],
                    known = new boolean[16], sampled = new boolean[16], driven = new boolean[16];
                final RegisterDef enable, tps, brs, output, outputEnable;
                final RegisterDef dmaSelect;
                int signals, emitted, priorSignals;
                Unit(int n) {
                    number = n; base = 0xffe20000L + n * 0x1000L;
                    dmaSelect = requiredRegister("TAUD DMA", "selector", "DMACTRGSEL" + n);
                    for (int c = 0; c < 16; c++) {
                        data[c] = reg("CDR" + c); count[c] = reg("CNT" + c);
                        mode[c] = reg("CMOR" + c); user[c] = reg("CMUR" + c); status[c] = reg("CSR" + c);
                    }
                    enable = reg("TE"); tps = reg("TPS"); brs = reg("BRS");
                    output = reg("TO"); outputEnable = reg("TOE");
                }
                RegisterDef reg(String suffix) { return requiredRegister("TAUD" + number, "register", "TAUD" + number + suffix); }
                int offset(RegisterDef r) { return (int)(r.address - base); }
                int m(int c) { return modes[c]; }
                int kind(int c) { return m(c) & 0x1e; }
                int sts(int c) { return (m(c) >>> 8) & 7; }
                int cks(int c) { return (m(c) >>> 14) & 3; }
                int ccs(int c) { return (m(c) >>> 12) & 3; }
                boolean enabled(int c) { return (enabledMask & (1 << c)) != 0; }
                boolean capture(int c) { return kind(c) == 4 || kind(c) == 12; }
                long divisor(int clock) { return divisors[clock]; }
                void updateDivisors() {
                    for (int ck = 0; ck < 4; ck++) divisors[ck] =
                        (1L << ((tpsValue >>> (4 * ck)) & 15)) * (ck == 3 ? brsValue + 1 : 1);
                }
                int master(int c) {
                    for (int p = (c - 1) & ~1; p >= 0; p -= 2) if ((m(p) & 0x800) != 0) return p;
                    return -1;
                }
                void reset() {
                    Arrays.fill(phase, 0); Arrays.fill(ticks, 0);
                    Arrays.fill(running, false); Arrays.fill(overflow, false);
                    Arrays.fill(known, false); Arrays.fill(sampled, false); Arrays.fill(driven, false);
                    signals = emitted = priorSignals = 0;
                    enabledMask = (int)registerValue(enable);
                    tpsValue = (int)registerValue(tps); brsValue = (int)registerValue(brs); updateDivisors();
                    for (int c = 0; c < 16; c++) {
                        modes[c] = (int)registerValue(mode[c]); edges[c] = (int)registerValue(user[c]) & 3;
                        reloads[c] = (int)registerValue(data[c]); counters[c] = (int)registerValue(count[c]);
                    }
                }
                void validateMode(PcodeThread<byte[]> t, RegisterDef r, int value, int c) {
                    int k = value & 0x1e, s = (value >>> 8) & 7, cc = (value >>> 12) & 3;
                    if ((value & 0x20) != 0 || ((c & 1) != 0 && (value & 0x800) != 0))
                        throw unsupported(t, r, "reserved CMOR bit or odd-channel MAS");
                    if (k != 0 && k != 4 && k != 8 && k != 12)
                        throw unsupported(t, r, "selected model implements interval,one-count,capture,width modes");
                    if (cc != 0 && cc != 3) throw unsupported(t, r, "external counter clock CCS1/prohibited CCS2 not modeled");
                    if (s == 3 || s >= 6) throw unsupported(t, r, "buffer/deadtime/updown start trigger not modeled");
                    if (s == 2 && k != 12) throw unsupported(t, r, "start/stop edge trigger requires width mode");
                    if ((k == 4 || k == 12) && (value & 0x800) != 0)
                        throw unsupported(t, r, "selected capture functions are independent channels");
                    if ((k == 4 && (s != 1 || cc != 0)) ||
                            (k == 12 && (s != 2 || cc != 0 || (value & 1) != 0)))
                        throw unsupported(t, r, "capture uses STS1, width uses STS2 MD0=0, both use internal clock");
                    if (k != 4 && k != 12 && (value & 0xc0) != 0)
                        throw unsupported(t, r, "COS reserved outside capture modes");
                    if ((value & 0x800) != 0 && (s == 4 || cc == 3))
                        throw unsupported(t, r, "master cannot consume upper master trigger");
                }
                void validateStart(PcodeThread<byte[]> t, int mask) {
                    for (int c = 0; c < 16; c++) if ((mask & (1 << c)) != 0) {
                        validateMode(t, mode[c], m(c), c);
                        if (kind(c) == 12 && enabled(c))
                            throw unsupported(t, mode[c], "capture-and-one-count cannot be forcibly restarted");
                        if (sts(c) == 4 || ccs(c) == 3) {
                            int p = master(c);
                            if (p < 0 || cks(c) != cks(p))
                                throw unsupported(t, mode[c], "slave needs upper MAS channel with same operating clock");
                        }
                        if (sts(c) == 5 && c == 0)
                            throw unsupported(t, mode[c], "channel0 has no upper channel");
                    }
                }
                void validate(PcodeThread<byte[]> t, RegisterDef r, long v) {
                    int o = offset(r), c;
                    if (o >= 0x200 && o < 0x240) {
                        c = (o - 0x200) / 4;
                        if (enabled(c)) throw unsupported(t, r, "CMOR write requires channel stopped");
                        validateMode(t, r, (int)v, c);
                    } else if (o == 0x240 || o == 0x244) {
                        for (c = 0; c < 16; c++) if (enabled(c) &&
                                (o == 0x244 ? cks(c) == 3 :
                                 (((v ^ tpsValue) >>> (cks(c) * 4)) & 15) != 0))
                            throw unsupported(t, r, "prescaler change requires all affected channels stopped");
                    } else if (o == 0x1c4) validateStart(t, (int)v);
                    else if ((o == 0x248 || o == 0x24c || o == 0x250 || o == 0x254 ||
                              o == 0x258 || o == 0x25c || o == 0x50 || o == 0x260 ||
                              o == 0x264 || o == 0x268 || o == 0x26c || o == 0x44) && v != 0)
                        throw unsupported(t, r, "synchronous rewrite/advanced output feature not selected by canonical TAUD startup");
                }
                void setCount(int c, long v) { counters[c] = (int)v & 0xffff; }
                void restart(int c) {
                    int k = kind(c);
                    running[c] = true; overflow[c] = false;
                    setCount(c, capture(c) ? 0 : reloads[c]);
                    if ((k == 0 || k == 4) && (m(c) & 1) != 0) emit(c);
                }
                void start(int mask) {
                    enabledMask |= mask; setRegisterValue(enable.name, enabledMask);
                    for (int c = 0; c < 16; c++) if ((mask & (1 << c)) != 0) {
                        running[c] = false; overflow[c] = false;
                        if (kind(c) == 4 || sts(c) == 0 || (kind(c) == 0 && sts(c) == 1)) restart(c);
                    }
                }
                void write(PcodeThread<byte[]> t, RegisterDef r, int v) {
                    int o = offset(r);
                    if (o < 0x40) {
                        int c = o / 4;
                        if (capture(c)) setRegisterValue(r.name, registerBeforeWrite);
                        else reloads[c] = v;
                    }
                    else if (o >= 0xc0 && o < 0x100) edges[(o - 0xc0) / 4] = v & 3;
                    else if (o == 0x58) setRegisterValue(r.name,
                        (registerBeforeWrite & registerValue(outputEnable)) | (v & ~registerValue(outputEnable)));
                    else if (o == 0x1c4) { start(v); setRegisterValue(r.name, 0); }
                    else if (o == 0x1c8) {
                        enabledMask &= ~v; setRegisterValue(enable.name, enabledMask);
                        for (int c = 0; c < 16; c++) if ((v & (1 << c)) != 0) running[c] = false;
                        setRegisterValue(r.name, 0);
                    } else if (o >= 0x180 && o < 0x1c0) {
                        int c = (o - 0x180) / 4;
                        if ((v & 1) != 0) setRegisterValue(status[c].name, registerValue(status[c]) & ~1L);
                        setRegisterValue(r.name, 0);
                    } else if (o >= 0x200 && o < 0x240) {
                        int c = (o - 0x200) / 4;
                        modes[c] = v;
                        reloads[c] = (int)registerValue(data[c]);
                        if (((registerBeforeWrite ^ v) & 0x1e) != 0) setCount(c, capture(c) ? 0 : 0xffff);
                    } else if (o == 0x240) {
                        tpsValue = v; updateDivisors();
                        for (int ck = 0; ck < 4; ck++) if ((((registerBeforeWrite ^ v) >>> (4 * ck)) & 15) != 0)
                            phase[ck] = 0;
                    } else if (o == 0x244) { brsValue = v; updateDivisors(); phase[3] = 0; }
                    else if (o == 0x44) setRegisterValue(r.name, 0);
                }
                void emit(int c) {
                    emitted |= 1 << c;
                    if ((registerValue(outputEnable) & (1 << c)) != 0 && !capture(c))
                        setRegisterValue(output.name, registerValue(output) ^ (1 << c));
                }
                void down(int c, long amount) {
                    long current = counters[c];
                    if (amount <= current) setCount(c, current - amount);
                    else {
                        // deadline() prevents crossing more than one expiry in this span.
                        setCount(c, kind(c) == 8 ? 0xffff : reloads[c]);
                        if (kind(c) == 8) running[c] = false;
                        emit(c);
                    }
                }
                void cascade(int source) {
                    for (int c = source + 1; c < 16; c++) if (enabled(c)) {
                        int p = master(c);
                        if ((sts(c) == 4 && p == source) || (sts(c) == 5 && c == source + 1)) {
                            if (kind(c) != 8 || !running[c] || (m(c) & 1) != 0) restart(c);
                        } else if (ccs(c) == 3 && p == source && running[c]) down(c, 1);
                    }
                }
                void captureValue(int c) {
                    int cos = (m(c) >>> 6) & 3;
                    if ((cos & 2) == 0 || !overflow[c]) setRegisterValue(data[c].name, counters[c]);
                    if (cos == 0) setRegisterValue(status[c].name, overflow[c] ? 1 : 0);
                    overflow[c] = false;
                    emit(c);
                }
                boolean inputEdge(int c) {
                    if (!known[c] || driven[c] == sampled[c]) return false;
                    boolean rising = driven[c]; sampled[c] = driven[c];
                    int edge = edges[c];
                    boolean valid = edge >= 2 || (edge == 1 ? rising : !rising);
                    if (kind(c) == 12) {
                        boolean begin = edge >= 2 ? (edge == 3 ? rising : !rising) : valid;
                        if (begin) { if (!running[c]) restart(c); return true; }
                        if (running[c]) {
                            captureValue(c); running[c] = false;
                            setCount(c, counters[c] + 1);
                            return true;
                        }
                    } else if (valid && kind(c) == 4) {
                        captureValue(c); setCount(c, 0); return true;
                    } else if (valid && sts(c) == 1) {
                        if (kind(c) != 8 || !running[c] || (m(c) & 1) != 0) restart(c);
                        return true;
                    }
                    return false;
                }
                long deadline() {
                    long next = signals == 0 ? Long.MAX_VALUE : 1;
                    if (enabledMask == 0) return next;
                    for (int c = 0; c < 16; c++) if (enabled(c)) {
                        int ck = cks(c); long div = divisor(ck);
                        if (known[c] && driven[c] != sampled[c]) next = Math.min(next, div - phase[ck]);
                        if (!running[c] || ccs(c) != 0) continue;
                        long value = counters[c];
                        long until = capture(c) ? 0x10000L - value : value + 1;
                        next = Math.min(next, until * div - phase[ck]);
                    }
                    return next;
                }
                void advance(long span) {
                    // The coordinator always splits at signal falls and counter/input events.
                    priorSignals = signals;
                    signals = 0;
                    for (int ck = 0; ck < 4; ck++) {
                        long div = divisor(ck), rest = span % div + phase[ck];
                        ticks[ck] = span / div + rest / div; phase[ck] = rest % div;
                    }
                    for (int c = 0; c < 16; c++) if (enabled(c)) {
                        long amount = ticks[cks(c)];
                        if (amount == 0) continue;
                        if (inputEdge(c)) continue;
                        if (!running[c] || ccs(c) != 0) continue;
                        if (!capture(c)) down(c, amount);
                        else {
                            long sum = counters[c] + amount;
                            if (sum >= 0x10000) {
                                overflow[c] = true;
                                int cos = (m(c) >>> 6) & 3;
                                if ((cos & 1) != 0) setRegisterValue(status[c].name, registerValue(status[c]) | 1);
                                if ((cos & 2) != 0) setRegisterValue(data[c].name, 0xffff);
                            }
                            setCount(c, sum);
                        }
                    }
                }
            }
        }

        final class Tauj {
            final Unit[] units = {new Unit(0), new Unit(1)};

            Unit unit(RegisterDef register) {
                int n = (int) ((register.address - 0xffe50000L) / 0x1000);
                if (n < 0 || n >= units.length)
                    throw new IllegalStateException("TAUJ register has no controller: " + register.name);
                return units[n];
            }
            RuntimeException unsupported(PcodeThread<byte[]> thread, RegisterDef register, String detail) {
                return fault("unsupported-tauj-operation", thread, register.address, register.size,
                    "peripheral", register.source_ref, detail);
            }
            void reset() { for (Unit u : units) u.reset(); }
            // Once after explicit scenario register seeding, not on ordinary clock advancement.
            void loadRegisters() { for (Unit u : units) u.loadRegisters(); }
            void read(PcodeThread<byte[]> thread, RegisterDef register) {
                Unit u = unit(register);
                int offset = (int) (register.address - u.base);
                if (offset >= 0x10 && offset <= 0x1c) u.materialize((offset - 0x10) >>> 2);
            }
            void flush() { for (Unit u : units) u.flush(); }
            void validate(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                if ((value & ~register.writable_mask) != 0)
                    throw fault("reserved-tauj-bits", thread, register.address, register.size,
                        "write", register.source_ref, "reserved bits must have their reset value");
                unit(register).validate(thread, register, value);
            }
            void write(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                unit(register).write(thread, register, value);
            }
            void validateSimultaneousStart(PcodeThread<byte[]> thread, long sser2) {
                for (int n = 0; n < 2; n++) units[n].validateStart(thread, (int) (sser2 >>> (4 * n)) & 15);
            }
            void simultaneousStart(PcodeThread<byte[]> thread, long sser2) {
                validateSimultaneousStart(thread, sser2);
                for (int n = 0; n < 2; n++) units[n].start((int) (sser2 >>> (4 * n)) & 15);
            }
            long cyclesUntilEvent() {
                long result = Long.MAX_VALUE;
                for (Unit u : units) result = Math.min(result, u.cyclesUntilEvent());
                return result;
            }
            void advanceClock(PcodeThread<byte[]> thread, long hsbCycles) {
                if (hsbCycles < 0) throw new IllegalArgumentException("negative HSB cycles");
                while (hsbCycles != 0) {
                    long span = Math.min(hsbCycles, cyclesUntilEvent());
                    // Commit every counter/reload before requests can cause DMA writes.
                    // Quiet progression is cached primitive arithmetic: no getVar,
                    // registerValue, byte arrays, backing-counter writes or JSON events.
                    for (Unit u : units) u.move(span);
                    for (Unit u : units) u.deliver(thread, span);
                    hsbCycles -= span;
                }
            }

            final class Unit {
                final int index;
                final String prefix;
                final long base;
                final RegisterDef[] bank = new RegisterDef[0x2a];
                final long[] state = new long[0x2a], pre = new long[4], div = new long[4];
                final RegisterDef te, ts, tt, to, toe, tol, tps, brs, tom, toc, rde, rdm, rdt;
                final RegisterDef[] data = new RegisterDef[4], counter = new RegisterDef[4],
                    mode = new RegisterDef[4], user = new RegisterDef[4];
                final boolean[] pending = new boolean[4], irqHigh = new boolean[4];
                long rootPhase;
                int baudFactor, brgPhase, dirtyCounters, requestMask, startMask, underflowMask;

                Unit(int index) {
                    this.index = index;
                    prefix = "TAUJ" + index;
                    base = 0xffe50000L + index * 0x1000L;
                    te = reg("TE"); ts = reg("TS"); tt = reg("TT");
                    to = reg("TO"); toe = reg("TOE"); tol = reg("TOL");
                    tps = reg("TPS"); brs = reg("BRS"); tom = reg("TOM"); toc = reg("TOC");
                    rde = reg("RDE"); rdm = reg("RDM"); rdt = reg("RDT");
                    reg("RSF");
                    for (int c = 0; c < 4; c++) {
                        data[c] = reg("CDR" + c); counter[c] = reg("CNT" + c);
                        mode[c] = reg("CMOR" + c); user[c] = reg("CMUR" + c);
                    }
                }
                int slot(RegisterDef r) { return (int) (r.address - base) >>> 2; }
                RegisterDef reg(String suffix) {
                    RegisterDef r = requiredRegister(prefix, suffix, prefix + suffix);
                    bank[slot(r)] = r;
                    return r;
                }
                long v(RegisterDef r) { return state[slot(r)]; }
                void put(RegisterDef r, long value) {
                    state[slot(r)] = value;
                    setRegisterValue(r.name, value);
                }
                void count(int c, long value) {
                    if (state[4 + c] == value) return;
                    state[4 + c] = value;
                    dirtyCounters |= 1 << c;
                }
                void materialize(int c) {
                    if ((dirtyCounters & (1 << c)) == 0) return;
                    setRegisterValue(counter[c].name, state[4 + c]);
                    dirtyCounters &= ~(1 << c);
                }
                void flush() {
                    for (int c = 0; c < 4; c++) materialize(c);
                }
                void configureClocks() {
                    long select = v(tps);
                    baudFactor = (int) v(brs) + 1;
                    for (int ck = 0; ck < 4; ck++) {
                        pre[ck] = 1L << ((select >>> (4 * ck)) & 15);
                        div[ck] = pre[ck] * (ck == 3 ? baudFactor : 1);
                    }
                }
                void loadRegisters() {
                    for (RegisterDef r : bank) if (r != null) state[slot(r)] = registerValue(r);
                    dirtyCounters = 0;
                    configureClocks();
                    brgPhase %= baudFactor;
                }
                int enabled() { return (int) v(te) & 15; }
                int clock(int channel) { return (int) (v(mode[channel]) >>> 14) & 3; }
                long phase(int ck) {
                    return (rootPhase & (pre[ck] - 1)) + (ck == 3 ? brgPhase * pre[ck] : 0);
                }
                long ticks(int ck, long cycles) {
                    long divisor = div[ck];
                    if (divisor == 1) return cycles;
                    return cycles / divisor + (cycles % divisor + phase(ck)) / divisor;
                }
                void reset() {
                    rootPhase = 0;
                    brgPhase = requestMask = startMask = underflowMask = 0;
                    Arrays.fill(pending, false);
                    Arrays.fill(irqHigh, false);
                    loadRegisters();
                }
                void validateStart(PcodeThread<byte[]> thread, int mask) {
                    for (int c = 0; c < 4; c++) if ((mask & (1 << c)) != 0) {
                        if ((v(mode[c]) & ~0xc001L) != 0)
                            throw unsupported(thread, mode[c], "only independent software-triggered interval mode is implemented");
                        if (v(user[c]) != 0)
                            throw unsupported(thread, user[c], "interval mode requires CMUR=0; no external input edge is supplied");
                        if (((v(rde) | v(rdm)) & (1L << c)) != 0)
                            throw unsupported(thread, rde, "RDE/RDM must be zero for independent interval operation");
                        if (((v(tom) | v(toc)) & (1L << c)) != 0)
                            throw unsupported(thread, tom, "only independent toggle/software output mode is implemented");
                    }
                }
                void validate(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                    int on = enabled();
                    for (int c = 0; c < 4; c++) {
                        if (register == mode[c]) {
                            if ((on & (1 << c)) != 0)
                                throw unsupported(thread, register, "CMOR is writable only while this channel is stopped");
                            if ((value & ~0xc001L) != 0)
                                throw unsupported(thread, register, "only independent software-triggered interval mode is implemented");
                        }
                        if (register == user[c] && value != 0)
                            throw unsupported(thread, register, "interval mode requires CMUR=0");
                    }
                    if (register == tps) {
                        long old = v(tps);
                        for (int c = 0; c < 4; c++) if ((on & (1 << c)) != 0) {
                            int shift = clock(c) * 4;
                            if (((old ^ value) & (15L << shift)) != 0)
                                throw unsupported(thread, register, "TPS changes require every channel using the affected clock stopped");
                        }
                    }
                    if (register == brs && value != v(brs))
                        for (int c = 0; c < 4; c++) if ((on & (1 << c)) != 0 && clock(c) == 3)
                            throw unsupported(thread, register, "BRG divisor changes while CK3 is in use are outside this functional phase contract");
                    if (register == rde || register == rdm || register == tom || register == toc) {
                        if (value != 0)
                            throw unsupported(thread, register, "nonzero synchronous rewrite/output configuration is not independent interval operation");
                        if (((value ^ v(register)) & on) != 0)
                            throw unsupported(thread, register, "configuration changes require affected channels stopped");
                    }
                    if (register == tol && ((value ^ v(tol)) & on) != 0)
                        throw unsupported(thread, register, "TOL changes during interval operation are prohibited");
                    if (register == ts) validateStart(thread, (int) value & 15);
                    if (register == toe) validateStart(thread, (int) value & on);
                }
                void start(int mask) {
                    if (mask == 0) return;
                    put(te, enabled() | mask);
                    for (int c = 0; c < 4; c++) if ((mask & (1 << c)) != 0) pending[c] = true;
                    // CNT retains its old/reset value until the next shared count-clock edge.
                }
                void write(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                    long old = v(register);
                    state[slot(register)] = value;
                    if (register == ts) {
                        start((int) value & 15);
                        put(ts, 0);
                    } else if (register == tt) {
                        int mask = (int) value & 15;
                        put(te, enabled() & ~mask);
                        for (int c = 0; c < 4; c++) if ((mask & (1 << c)) != 0) {
                            pending[c] = false;
                            irqHigh[c] = false;
                        }
                        put(tt, 0);
                    } else if (register == to) {
                        long protectedBits = v(toe) & 15;
                        put(to, (old & protectedBits) | (value & ~protectedBits));
                    } else if (register == tps || register == brs) {
                        if (register == brs) brgPhase %= (int) value + 1;
                        if (old != value) configureClocks();
                    } else if (register == rdt) {
                        // RDE is disabled on every supported interval channel.
                        put(rdt, 0);
                    }
                    // CDR cache is only the reload latch: never replace active CNT here.
                }
                long cyclesUntilEvent() {
                    long result = Long.MAX_VALUE;
                    int on = enabled();
                    for (int c = 0; c < 4; c++) {
                        if (irqHigh[c]) result = 1;
                        if ((on & (1 << c)) == 0) continue;
                        int ck = clock(c);
                        long counts = pending[c] ? 1 : state[4 + c] + 1;
                        // Maximum = 2^32 * (32768*256) < Long.MAX_VALUE.
                        result = Math.min(result, counts * div[ck] - phase(ck));
                    }
                    return result;
                }
                void move(long cycles) {
                    requestMask = startMask = underflowMask = 0;
                    int on = enabled();
                    long output = v(to), outputsEnabled = v(toe);
                    for (int c = 0; c < 4; c++) {
                        boolean pulse = false;
                        if ((on & (1 << c)) != 0) {
                            long countTicks = ticks(clock(c), cycles);
                            if (countTicks != 0) {
                                if (pending[c]) {
                                    if (countTicks != 1) throw new IllegalStateException("TAUJ start edge was skipped");
                                    pending[c] = false;
                                    count(c, v(data[c]));
                                    startMask |= 1 << c;
                                    pulse = (v(mode[c]) & 1) != 0;
                                } else {
                                    long current = state[4 + c];
                                    if (countTicks <= current) count(c, current - countTicks);
                                    else {
                                        if (countTicks != current + 1)
                                            throw new IllegalStateException("TAUJ underflow edge was skipped");
                                        count(c, v(data[c]));
                                        underflowMask |= 1 << c;
                                        pulse = true;
                                    }
                                }
                            }
                        }
                        // Pulses last one HSB clock. Adjacent pulses remain high,
                        // notably CDR=0/divisor=1 (manual Figure24.17).
                        if (pulse && !(irqHigh[c] && cycles == 1)) requestMask |= 1 << c;
                        irqHigh[c] = pulse;
                        if (pulse && (outputsEnabled & (1L << c)) != 0) output ^= 1L << c;
                    }
                    if (output != v(to)) put(to, output); // output changes only at real edges
                    if (baudFactor != 1) {
                        long preTicks = cycles / pre[3]
                            + (cycles % pre[3] + (rootPhase & (pre[3] - 1))) / pre[3];
                        brgPhase = (int) ((brgPhase + preTicks % baudFactor) % baudFactor);
                    }
                    rootPhase = (rootPhase + (cycles & 32767)) & 32767;
                }
                void deliver(PcodeThread<byte[]> thread, long span) {
                    int events = startMask | underflowMask;
                    if ((events | requestMask) == 0) return;
                    for (int c = 0; c < 4; c++) {
                        if ((events & (1 << c)) != 0) {
                            JsonObject event = new JsonObject();
                            event.addProperty("kind", "tauj-clock");
                            event.addProperty("unit", index);
                            event.addProperty("channel", c);
                            event.addProperty("hsb_cycles", span);
                            event.addProperty("underflows", (underflowMask >>> c) & 1);
                            event.addProperty("start_load", (startMask & (1 << c)) != 0);
                            event.addProperty("counter", state[4 + c]);
                            event.addProperty("scheduler_tick", trace.instructions);
                            trace.deviceEvents.add(event);
                        }
                        if ((requestMask & (1 << c)) != 0) {
                            requestInterrupt(thread, 133 + 4 * index + c);
                            dma.request(thread, 1 + 4 * index + c);
                        }
                    }
                }
            }
        }

        final class Pic1 {
            final RegisterDef start = requiredRegister("PIC1", "start", "PIC1ASST");
            final RegisterDef sser0 = requiredRegister("PIC1", "TAUD0 selection", "PIC1ASSER0");
            final RegisterDef sser1 = requiredRegister("PIC1", "TAUD1 selection", "PIC1ASSER1");
            final RegisterDef sser2 = requiredRegister("PIC1", "TAUJ/TSG/TPBA/ENCA selection", "PIC1ASSER2");
            final RegisterDef sser3 = requiredRegister("PIC1", "OSTM selection", "PIC1ASSER3");
            void validateStart(PcodeThread<byte[]> thread) {
                long selected2 = registerValue(sser2), selected3 = registerValue(sser3);
                if ((selected2 & 0x3c00) != 0 || selected3 != 0) {
                    StringBuilder missing = new StringBuilder();
                    if ((selected2 & 0x0400) != 0) missing.append(" TPBA0");
                    if ((selected2 & 0x0800) != 0) missing.append(" TPBA1");
                    if ((selected2 & 0x1000) != 0) missing.append(" ENCA0");
                    if ((selected2 & 0x2000) != 0) missing.append(" ENCA1");
                    if ((selected3 & 1) != 0) missing.append(" OSTM0");
                    if ((selected3 & 2) != 0) missing.append(" OSTM1");
                    throw fault("unsupported-pic1-start-controller", thread, start.address, start.size,
                        "start", start.source_ref,
                        "selected simultaneous-start controllers require real models:" + missing);
                }
                // Validate the entire request before any timer's TE/counter is changed.
                taud.validateSimultaneousStart(thread, registerValue(sser0), registerValue(sser1));
                tauj.validateSimultaneousStart(thread, selected2);
                tsg.validateSimultaneousStart(thread, selected2);
            }
            void validate(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                if ((value & ~register.writable_mask) != 0)
                    throw fault("reserved-pic1-bits", thread, register.address, register.size,
                        "write", register.source_ref, "reserved PIC1 bits must be zero");
                if (register == start && (value & 1) != 0) validateStart(thread);
            }
            void write(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                if (register != start) return; // SSER0..3 are ordinary selector latches.
                if ((value & 1) != 0) {
                    long selected0 = registerValue(sser0), selected1 = registerValue(sser1),
                        selected2 = registerValue(sser2);
                    // Each controller commits start requests, not invented elapsed cycles.
                    // Main stages cross-device PIC2/DMA delivery until every edge is committed.
                    taud.simultaneousStart(thread, selected0, selected1);
                    tauj.simultaneousStart(thread, selected2);
                    tsg.simultaneousStart(thread, selected2);
                }
                setRegisterValue(start.name, 0);
            }
        }

        final class Adc {
            static final long NEVER = Long.MAX_VALUE;
            final Unit[] units;
            final boolean fullPinPackage;
            final RegisterDef selector = requiredRegister("ADCG", "clock", "CKSC8C");
            final RegisterDef selectorStatus = requiredRegister("ADCG", "clock status", "CKSC8S");
            long now;
            long hsbRemainder;
            int clockSelection = 2;

            Adc(String productId) {
                // Authoritative registry MCU identity, never target-name/filename matching.
                if ("R7F701381".equals(productId)) fullPinPackage = false;
                else if ("R7F701383".equals(productId)) fullPinPackage = true;
                else throw new IllegalArgumentException("unsupported ADC product identity: " + productId);
                units = new Unit[] {new Unit(0), new Unit(1)};
            }

            final class Unit {
                final int number;
                final long base;
                final RegisterDef[] regs = new RegisterDef[0x804 / 4];
                // Separate explicitly supplied voltages for each electrical sampling boundary:
                // normal, mode2 pull-down, mode2 pull-up, mode1 pull-down pulse.
                final int[][] external = new int[4][13];
                final int[] disconnected = new int[13];
                final int[] held = new int[6];
                final long[] samplingSince = new long[6];
                final long[] heldSince = new long[6];
                final boolean[] sampling = new boolean[6];
                final boolean[] heldValid = new boolean[6];
                final boolean[] active = new boolean[5];
                final int[] pointer = new int[5];
                final int[] cyclesLeft = new int[5];
                final long[] timerDue = new long[5];
                final long[] irqDue = new long[5];
                int current = -1;
                int phase;
                int type, id, additions, accumulated, completed;
                long channelControl;
                long conversionDue = NEVER;
                boolean errorLine;

                Unit(int number) {
                    this.number = number;
                    base = 0xfff91000L + number * 0x1000L;
                    for (RegisterDef reg : registers) {
                        if ("adc".equals(reg.behavior) && reg.address >= base
                                && reg.address <= base + 0x800) {
                            regs[(int) (reg.address - base) >>> 2] = reg;
                        }
                    }
                    for (int[] boundary : external) Arrays.fill(boundary, -1);
                    Arrays.fill(disconnected, -1);
                    Arrays.fill(timerDue, NEVER);
                    Arrays.fill(irqDue, NEVER);
                }

                RegisterDef reg(int offset) {
                    RegisterDef result = regs[offset >>> 2];
                    if (result == null) throw new IllegalStateException("missing ADCG register at " + hex32(base + offset));
                    return result;
                }
                long get(int offset) { return registerValue(reg(offset)); }
                void put(int offset, long value) { setRegisterValue(reg(offset).name, value); }
                int sg(int group) { return 0x480 + group * 0x80; }
                int thCount() { return number == 0 ? 6 : 4; }
                int physicalCount() { return fullPinPackage ? 12 : number == 0 ? 9 : 10; }
                int sampleCycles() { return get(0x340) == 0 ? 18 : 204; }
                boolean busy() {
                    if (current >= 0) return true;
                    for (int group = 0; group < 5; group++)
                        if (active[group] || timerDue[group] != NEVER) return true;
                    for (int k = 0; k < thCount(); k++)
                        if (sampling[k] || heldValid[k]) return true;
                    return false;
                }
                void status(int group) {
                    put(sg(group) + 0x24,
                        (active[group] ? 2 : 0) | (timerDue[group] == NEVER ? 0 : 4));
                }
                void halt() {
                    current = -1;
                    conversionDue = NEVER;
                    Arrays.fill(active, false);
                    Arrays.fill(timerDue, NEVER);
                    Arrays.fill(irqDue, NEVER);
                    for (int group = 0; group < 5; group++) status(group);
                }
                void reset() {
                    // Voltages are external testbench state and persist across device reset.
                    halt();
                    Arrays.fill(sampling, false);
                    Arrays.fill(heldValid, false);
                    Arrays.fill(disconnected, -1);
                    errorLine = false;
                }
                void checkTiming(PcodeThread<byte[]> thread) {
                    long sample = get(0x340);
                    if (!((sample == 0 && clockDivisor() == 1)
                            || (sample == 0x90cc && clockDivisor() == 2)))
                        fail(thread, reg(0x340), "prohibited-adc-clock", "SMPCR and CKSC8C require 0/40MHz or 90CC/20MHz");
                }
                void request(PcodeThread<byte[]> thread, int group) {
                    if (active[group]) return;
                    if (current > group && (get(sg(current) + 0x10) & 0x20) != 0) return;
                    checkTiming(thread);
                    int first = (int) get(sg(group) + 0x14);
                    int last = (int) get(sg(group) + 0x18);
                    if (first > last || last >= 24)
                        fail(thread, reg(sg(group) + 0x14), "prohibited-adc-scan", "VCSP must be <= VCEP and both must be <24");
                    active[group] = true;
                    pointer[group] = first;
                    cyclesLeft[group] = (int) get(sg(group) + 0x1c) + 1;
                    status(group);
                    if (current >= 0 && group > current) {
                        int suspend = (int) get(0x384);
                        if (suspend == 2 || (suspend == 1 && current == 0)) {
                            current = -1;
                            conversionDue = NEVER;
                        }
                    }
                    choose(thread);
                }
                void choose(PcodeThread<byte[]> thread) {
                    if (current >= 0) return;
                    for (int group = 4; group >= 0; group--) {
                        if (!active[group]) continue;
                        current = group;
                        beginChannel(thread);
                        return;
                    }
                }
                void beginChannel(PcodeThread<byte[]> thread) {
                    checkTiming(thread);
                    channelControl = get(pointer[current] * 4);
                    type = (int) (channelControl >>> 13) & 7;
                    id = (int) channelControl & 0x3f;
                    if (type == 5 || type == 6)
                        fail(thread, reg(pointer[current] * 4), "unsupported-adc-mpx", "external multiplexer operation is not used by canonical ADC tables and requires a separate mux wire contract");
                    if (type != 0 && type != 1 && type != 3 && type != 4)
                        fail(thread, reg(pointer[current] * 4), "prohibited-adc-conversion", "reserved CNVCLS");
                    if (type == 3) {
                        if (id > 16 || (id & 3) != 0)
                            fail(thread, reg(pointer[current] * 4), "prohibited-adc-source", "self-diagnosis GCTRL must be0,4,8,12,16");
                    } else if (type == 1) {
                        if (id >= thCount() || !heldValid[id])
                            fail(thread, reg(pointer[current] * 4), "missing-adc-held-sample", "held conversion needs an enabled T&H capture before conversion");
                        if ((channelControl & 0x30000) != 0)
                            fail(thread, reg(pointer[current] * 4), "prohibited-adc-pull", "held conversions cannot use VCR pull resistors");
                    } else if (!(id < physicalCount() || (number == 1 && id == 12))) {
                        fail(thread, reg(pointer[current] * 4), "prohibited-adc-source", "physical channel is not present on the registry-selected MCU package");
                    }
                    additions = type == 4 ? ((get(0x398) & 1) == 0 ? 2 : 4) : 1;
                    accumulated = completed = 0;
                    phase = 1;
                    conversionDue = Math.addExact(now, sampleCycles());
                }
                int samplePin(PcodeThread<byte[]> thread, int pin, long vcr) {
                    long tdcr = get(0x3c4);
                    long odcr = get(0x3c8);
                    int pull = (int) (vcr >>> 16) & 3;
                    if ((tdcr & 0x80) != 0) {
                        if (pull != 0)
                            fail(thread, reg(0x3c4), "prohibited-adc-pull", "pin-level diagnosis cannot use PUE/PDE");
                        int level = (int) tdcr & 3;
                        boolean odd = (pin & 1) != 0;
                        int code = level == 0 ? (odd ? 4095 : 0)
                            : level == 1 ? (odd ? 0 : 4095)
                            : level == 2 ? (odd ? 2048 : 0) : (odd ? 0 : 2048);
                        disconnected[pin] = code;
                        return code;
                    }
                    boolean selected = pin < 12 && (get(0x800) & (1L << pin)) != 0;
                    int boundary = (odcr & 0x80) != 0 && selected ? 3 : selected ? pull : 0;
                    if ((odcr & 0x80000000L) != 0) {
                        if (boundary == 1) disconnected[pin] = 0;
                        if (boundary == 2) disconnected[pin] = 4095;
                        if (disconnected[pin] < 0)
                            fail(thread, reg(0x3c8), "missing-adc-disconnected-charge", "ODDE without pull requires a preceding known internal pin sample");
                        return disconnected[pin];
                    }
                    int code = external[boundary][pin];
                    if (code < 0)
                        fail(thread, reg(0x200 + pointer[Math.max(current, 0)] * 4),
                            "missing-adc-sample", "supply adc-sample for unit=" + number + " physical_channel=" + pin + " boundary=" + boundary);
                    return code;
                }
                void sample(PcodeThread<byte[]> thread) {
                    int code;
                    if (type == 3) code = Math.min(4095, id * 256);
                    else if (type == 1) {
                        if (!heldValid[id])
                            fail(thread, reg(pointer[current] * 4), "missing-adc-held-sample", "T&H no longer holds a sample");
                        if (now - heldSince[id] > 400L / clockDivisor())
                            fail(thread, reg(pointer[current] * 4), "expired-adc-held-sample", "T&H value exceeded documented10us retention");
                        code = held[id];
                    } else code = samplePin(thread, id, channelControl);
                    accumulated += code;
                    phase = 2;
                    conversionDue = Math.addExact(now, 22);
                }
                void captureError(PcodeThread<byte[]> thread, int offset, int vc) {
                    if ((get(offset) & 0x80) == 0) put(offset, 0x80 | vc);
                    refreshError(thread);
                }
                void refreshError(PcodeThread<byte[]> thread) {
                    long enables = get(0x3c0);
                    boolean asserted = ((enables & 8) != 0 && (get(0x3dc) & 0x80) != 0)
                        || ((enables & 4) != 0 && (get(0x3e0) & 0x80) != 0)
                        || ((enables & 1) != 0 && (get(0x3e8) & 0x80) != 0);
                    if (asserted && !errorLine) requestInterrupt(thread, number == 0 ? 76 : 177);
                    errorLine = asserted;
                }
                void pair(int vc) {
                    int even = vc & ~1;
                    put(0x100 + even * 2,
                        (get(0x200 + even * 4) & 0xffff)
                        | ((get(0x204 + even * 4) & 0xffff) << 16));
                }
                void result(PcodeThread<byte[]> thread) {
                    completed++;
                    if (completed < additions) {
                        phase = 1;
                        conversionDue = Math.addExact(now, sampleCycles());
                        return;
                    }
                    int group = current;
                    int vc = pointer[group];
                    int fixed = accumulated << (additions == 1 ? 3 : additions == 2 ? 2 : 1);
                    int data = (get(0x398) & 0x10) != 0 ? accumulated : fixed;
                    if ((get(0x200 + vc * 4) & 0x2000000) != 0) captureError(thread, 0x3e0, vc);
                    int parity = Integer.bitCount(data ^ (id << 16)) & 1;
                    put(0x200 + vc * 4, 0x2000000L | ((long) parity << 24) | ((long) id << 16) | data);
                    pair(vc);
                    int limits = (int) get(sg(group) + 0x30);
                    if (limits != 0) {
                        long table = get(0x3cc + (limits - 1) * 4);
                        if (fixed < (table & 0xffff) || fixed > (table >>> 16)) captureError(thread, 0x3dc, vc);
                    }
                    if (type == 1 && (get(0x408) & 1) == 0 && (get(0x430) & (1L << id)) != 0) {
                        sampling[id] = true;
                        samplingSince[id] = now;
                        heldValid[id] = false;
                    }
                    boolean endOfCycle = vc == (int) get(sg(group) + 0x18);
                    boolean continuous = (get(sg(group) + 0x10) & 0x20) != 0;
                    boolean endOfScan = endOfCycle && (continuous || cyclesLeft[group] == 1);
                    boolean output = (channelControl & 0x80) != 0
                        || (endOfScan && (get(sg(group) + 0x10) & 0x10) != 0);
                    if (output) irqDue[group] = Math.addExact(now, 6 / clockDivisor());
                    if (endOfCycle) {
                        if (!continuous && --cyclesLeft[group] == 0) {
                            active[group] = false;
                            status(group);
                        } else pointer[group] = (int) get(sg(group) + 0x14);
                    } else pointer[group]++;
                    current = -1;
                    conversionDue = NEVER;
                    choose(thread);
                }
                void hold(PcodeThread<byte[]> thread, int bank) {
                    int controlOffset = bank == 0 ? 0x420 : 0x424;
                    long control = get(controlOffset);
                    int group = ((int) control & 3) + 1;
                    if ((control & 0x20) == 0) return;
                    if ((get(sg(group) + 0x10) & 3) != 1 || get(0x384) != 2)
                        fail(thread, reg(controlOffset), "prohibited-adc-hold-mode", "hold trigger requires SG.TRGMD=1 and SUSMTD=2");
                    if (active[group]) return;
                    for (int k = 0; k < thCount(); k++) {
                        if ((get(0x430) & (1L << k)) == 0 || ((get(0x434) >>> (k * 2)) & 1) != bank) continue;
                        if (!sampling[k] || now - samplingSince[k] < 32)
                            fail(thread, reg(0x400), "adc-acquisition-time", "T&H requires32 CLK_ADC cycles of sampling before hold");
                        held[k] = samplePin(thread, k, 0);
                        sampling[k] = false;
                        heldValid[k] = true;
                        heldSince[k] = now;
                    }
                    // Hold force-suspends any ongoing VC, irrespective of SG priority.
                    current = -1;
                    conversionDue = NEVER;
                    request(thread, group);
                }
                void startTimer(PcodeThread<byte[]> thread, int group) {
                    if (timerDue[group] != NEVER) return;
                    timerDue[group] = Math.addExact(now, get(sg(group) + 0x28));
                    status(group);
                    // ADTIP=0 emits its first trigger simultaneously with start.
                    if (timerDue[group] == now) timer(thread, group);
                }
                void timer(PcodeThread<byte[]> thread, int group) {
                    timerDue[group] = Math.addExact(now, get(sg(group) + 0x2c) + 1);
                    if ((get(sg(group) + 0x10) & 3) >= 2) request(thread, group);
                }
                long nextDeadline() {
                    long next = conversionDue;
                    for (int group = 0; group < 5; group++) next = Math.min(next, Math.min(timerDue[group], irqDue[group]));
                    return next;
                }
                void advance(PcodeThread<byte[]> thread) {
                    // Stable ordering for coincident timer/results: result commits before a new edge.
                    if (conversionDue == now) {
                        if (phase == 1) sample(thread); else result(thread);
                    }
                    for (int group = 0; group < 5; group++) {
                        if (timerDue[group] == now) timer(thread, group);
                        if (irqDue[group] == now) {
                            irqDue[group] = NEVER;
                            requestInterrupt(thread, (number == 0 ? 77 : 178) + group);
                            // Tap the peripheral edge irrespective of CPU EIMK.
                            dma.request(thread, 55 + number * 5 + group);
                        }
                    }
                }
                void readOne(PcodeThread<byte[]> thread, int vc) {
                    long info = get(0x200 + vc * 4);
                    long payload = info & 0x11fffffL;
                    if ((Long.bitCount(payload) & 1) != 0) {
                        captureError(thread, 0x3e4, vc);
                        if ((get(0x3c0) & 2) != 0) latchEcmError(thread, 84);
                    }
                    put(0x200 + vc * 4, (get(0x3c0) & 0x10) != 0 ? 0 : info & ~0x2000000L);
                    pair(vc);
                }
                void write(PcodeThread<byte[]> thread, int offset, long value) {
                    if (offset == 0x300 || offset == 0x304) {
                        if ((value & 1) != 0) synchronizationStart(thread, offset == 0x304);
                    } else if (offset == 0x380 && (value & 1) != 0) halt();
                    else if (offset == 0x3c8 && (value & 0x80000000L) != 0) put(0x3c4, get(0x3c4) & ~0x80L);
                    else if (offset == 0x3c0) refreshError(thread);
                    else if (offset == 0x3d8) {
                        for (int bit = 0; bit < 4; bit++)
                            if ((value & (1L << bit)) != 0) put(0x3e8 - bit * 4, 0);
                        refreshError(thread);
                    } else if (offset == 0x400 && (value & 1) != 0) {
                        for (int k = 0; k < thCount(); k++) if ((get(0x430) & (1L << k)) != 0) {
                            sampling[k] = true;
                            samplingSince[k] = now;
                            heldValid[k] = false;
                        }
                    } else if (offset == 0x404 && (value & 1) != 0) {
                        Arrays.fill(sampling, false);
                        Arrays.fill(heldValid, false);
                    } else if (offset == 0x410 || offset == 0x414) {
                        int bank = offset == 0x410 ? 0 : 1;
                        if ((value & 1) != 0 && (get(bank == 0 ? 0x420 : 0x424) & 0x30) == 0x20) hold(thread, bank);
                    } else if (offset == 0x430) {
                        for (int k = 0; k < thCount(); k++) if ((value & (1L << k)) == 0) {
                            sampling[k] = heldValid[k] = false;
                        }
                    } else if (offset >= 0x480 && offset < 0x700) {
                        int group = (offset - 0x480) / 0x80;
                        int sub = (offset - 0x480) % 0x80;
                        if (sub == 0 && (value & 1) != 0) request(thread, group);
                        if (sub == 8 && (value & 1) != 0 && (get(sg(group) + 0x10) & 3) >= 2) startTimer(thread, group);
                        if (sub == 12 && (value & 1) != 0) { timerDue[group] = NEVER; status(group); }
                    }
                    if (!reg(offset).access.contains("r")) put(offset, 0);
                }
            }

            void initializeClock() {
                long control = registerValue(selector);
                if (control != 2 && control != 4)
                    throw new IllegalArgumentException("CKSC8C requires 2 or 4");
                clockSelection = (int) control;
            }
            int clockDivisor() { return clockSelection >>> 1; }
            void fail(PcodeThread<byte[]> thread, RegisterDef reg, String kind, String detail) {
                throw fault(kind, thread, reg.address, reg.size, "adc", reg.evidence, detail);
            }
            Unit unit(long address) {
                if (address >= 0xfff91000L && address <= 0xfff91800L) return units[0];
                if (address >= 0xfff92000L && address <= 0xfff92800L) return units[1];
                throw new IllegalArgumentException("not an ADC unit address: " + hex32(address));
            }
            void advanceClock(PcodeThread<byte[]> thread, long adcClockCycles) {
                if (adcClockCycles < 0) throw new IllegalArgumentException("negative CLK_ADC advance");
                long target = Math.addExact(now, adcClockCycles);
                for (;;) {
                    long next = Math.min(units[0].nextDeadline(), units[1].nextDeadline());
                    if (next == NEVER || next > target) break;
                    now = next;
                    units[0].advance(thread);
                    units[1].advance(thread);
                }
                now = target;
            }
            void advanceHsbClock(PcodeThread<byte[]> thread, long hsbCycles) {
                if (hsbCycles < 0) throw new IllegalArgumentException("negative CLK_HSB advance");
                int divisor = 2 * clockDivisor();
                long total = Math.addExact(hsbRemainder, hsbCycles);
                long cycles = total / divisor;
                hsbRemainder = total % divisor;
                advanceClock(thread, cycles);
            }
            void hardwareTrigger(PcodeThread<byte[]> thread, int unit, int group) {
                if (unit < 0 || unit > 1 || group < 0 || group > 4) throw new IllegalArgumentException("invalid ADC hardware trigger");
                Unit adc = units[unit];
                int mode = (int) adc.get(adc.sg(group) + 0x10) & 3;
                if (group >= 3 && mode == 3) { adc.startTimer(thread, group); return; }
                if (mode != 1) return;
                for (int bank = 0; bank < 2; bank++) {
                    long control = adc.get(bank == 0 ? 0x420 : 0x424);
                    if ((control & 0x30) == 0x30 && ((control & 3) + 1) == group) {
                        adc.hold(thread, bank);
                        return;
                    }
                }
                adc.request(thread, group);
            }
            void synchronizationStart(PcodeThread<byte[]> thread, boolean timerStart) {
                for (Unit adc : units) for (int group = timerStart ? 3 : 0; group < 5; group++) {
                    long control = adc.get(adc.sg(group) + 0x10);
                    if ((control & (timerStart ? 0x80 : 0x40)) == 0) continue;
                    if (timerStart) adc.startTimer(thread, group); else adc.request(thread, group);
                }
            }
            long hsbCyclesUntilEvent() {
                long next = Math.min(units[0].nextDeadline(), units[1].nextDeadline());
                return next == NEVER ? NEVER
                    : Math.subtractExact(Math.multiplyExact(next - now, 2L * clockDivisor()), hsbRemainder);
            }
            void reset() {
                for (Unit adc : units) adc.reset();
                hsbRemainder = 0;
                clockSelection = 2;
                // Keep monotonic named-domain time; reset invalidates all live deadlines.
            }
            void beforeRead(PcodeThread<byte[]> thread, RegisterDef register) {
                // Results and busy flags are committed only by named clock progress, not polling.
                if ("adc-clock".equals(register.behavior) && register == selectorStatus)
                    setRegisterValue(selectorStatus.name, clockSelection | 1);
            }
            void readCompleted(PcodeThread<byte[]> thread, long address, int size) {
                if (!((address >= 0xfff91100L && address < 0xfff91260L)
                        || (address >= 0xfff92100L && address < 0xfff92260L))) return;
                Unit adc = unit(address);
                int offset = (int) (address - adc.base);
                if (offset >= 0x200 && offset < 0x260 && size == 4 && (offset & 3) == 0)
                    adc.readOne(thread, (offset - 0x200) / 4);
                else if (offset >= 0x100 && offset < 0x130) {
                    // Even a 16-bit DR transaction accesses BOTH packed results (§30.3.5).
                    int even = ((offset - 0x100) / 4) * 2;
                    adc.readOne(thread, even);
                    adc.readOne(thread, even + 1);
                }
            }
            void validateWrite(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                if ((value & ~register.writable_mask) != 0)
                    fail(thread, register, "prohibited-adc-reserved-bits", "reserved ADC bits must retain reset values");
                if ("adc-clock".equals(register.behavior)) {
                    if (value != 2 && value != 4) fail(thread, register, "prohibited-adc-clock", "CKSC8C allows2 or4");
                    if (value != clockSelection && (units[0].busy() || units[1].busy()))
                        fail(thread, register, "prohibited-adc-clock-change", "cannot change CLK_ADC while ADC is in use");
                    return;
                }
                Unit adc = unit(register.address);
                int offset = (int) (register.address - adc.base);
                if (offset == 0x340 && value != 0 && value != 0x90cc)
                    fail(thread, register, "prohibited-adc-sampling", "SMPCR allows0 or90CC");
                if (offset == 0x384 && value == 3)
                    fail(thread, register, "prohibited-adc-suspend", "SUSMTD3 is prohibited");
                if (offset < 0x60) {
                    int conversion = (int) (value >>> 13) & 7;
                    if (conversion == 2 || conversion == 7 || (value & 0x30000) == 0x30000)
                        fail(thread, register, "prohibited-adc-vcr", "reserved CNVCLS or simultaneous PUE/PDE");
                    for (boolean active : adc.active) if (active)
                        fail(thread, register, "prohibited-adc-active-vcr-write", "change VCR only while scan groups are idle");
                }
                if (offset == 0x3c8 && ((value & 0x80000080L) == 0x80000080L
                        || (value & 0x3f) < 4 || (value & 0x3f) > 0x14))
                    fail(thread, register, "prohibited-adc-odcr", "ODDE and ODE cannot both be1; ODPW must be04..14");
                if ((offset == 0x420 || offset == 0x424) && (value & 0x30) == 0x10)
                    fail(thread, register, "prohibited-adc-hold", "HLDCTE0/HLDTE1 is prohibited");
                if (offset >= 0x480 && offset < 0x700) {
                    int group = (offset - 0x480) / 0x80;
                    int sub = (offset - 0x480) % 0x80;
                    if ((sub == 0x14 || sub == 0x18) && value >= 24)
                        fail(thread, register, "prohibited-adc-scan", "virtual channel pointer exceeds23");
                    if (adc.active[group] && (sub == 0x14 || sub == 0x18 || sub == 0x1c || sub == 0x30))
                        fail(thread, register, "prohibited-adc-active-group-write", "scan pointers/count/limits may change only while group is idle");
                    if (adc.active[group] && sub == 0x10 && ((value ^ adc.get(offset)) & 0x30) != 0)
                        fail(thread, register, "prohibited-adc-active-group-write", "SCANMD/ADIE may change only while group is idle");
                }
            }
            void handleWrite(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                if ("adc-clock".equals(register.behavior)) {
                    if (value != registerBeforeWrite) hsbRemainder %= 2; // Preserve HSB-to-LSB half-cycle phase.
                    clockSelection = (int) value;
                    setRegisterValue(selectorStatus.name, value | 1);
                    return;
                }
                Unit adc = unit(register.address);
                adc.write(thread, (int) (register.address - adc.base), value);
            }
            void input(ExternalEvent input) {
                if (input.unit == null || input.unit < 0 || input.unit > 1 || input.channel == null)
                    throw new IllegalArgumentException("adc-sample needs unit0..1 and physical channel");
                Unit adc = units[input.unit];
                int pin = input.channel;
                if (!(pin >= 0 && (pin < adc.physicalCount() || (input.unit == 1 && pin == 12))))
                    throw new IllegalArgumentException("adc-sample channel not present on registry-selected MCU package");
                int boundary = "normal".equals(input.boundary) ? 0
                    : "pull-down".equals(input.boundary) ? 1
                    : "pull-up".equals(input.boundary) ? 2
                    : "mode1".equals(input.boundary) ? 3 : -1;
                if (boundary < 0 || (pin == 12 && boundary != 0))
                    throw new IllegalArgumentException("invalid adc-sample boundary");
                long code = parseUnsigned(input.value);
                if (code < 0 || code > 4095) throw new IllegalArgumentException("adc-sample must be12-bit unsigned");
                adc.external[boundary][pin] = (int) code;
                JsonObject event = GSON.toJsonTree(input).getAsJsonObject();
                event.addProperty("kind", "external-adc-sample");
                event.addProperty("adc_clock", now);
                event.addProperty("scheduler_tick", trace.instructions);
                trace.deviceEvents.add(event);
            }
        }

        final class Rsent {
            static final long NEVER = Long.MAX_VALUE;
            static final int TSPC=0, TSC=1, CC=4, BRP=5, IDE=6, MDC=7,
                SPCT=8, MST=9, CS=10, CSC=11, SRTS=12, SRXD=13,
                CPL=14, ML=15, FRTS=16, FRXD=17;
            final String evidence = "manual:R01UH0585EJ0120 section19";
            final String[] suffix = {"TSPC","TSC",null,null,"CC","BRP","IDE","MDC",
                "SPCT","MST","CS","CSC","SRTS","SRXD","CPL","ML","FRTS","FRXD"};
            final RegisterDef selector = requiredRegister("RSENT", "timestamp master", "RSENTTSSEL");
            final Unit[] units = {new Unit(0),new Unit(1)};
            final PriorityQueue<ScheduledEvent> wireEvents = new PriorityQueue<>(ScheduledEvent.ORDER);
            long now, masterSelect;

            final class Unit {
                final int number;
                final long base;
                final RegisterDef statusInterrupt;
                final RegisterDef[] regs = new RegisterDef[18];
                final long[] v = new long[18];
                // Buffer2 stores status nibble,CPL,ML,FRTS,FRXD. No per-clock allocation.
                final long[] back = new long[5];
                boolean backValid, receiveLine, outstanding, idlePending;
                long timestampRemainder, spcDue=NEVER, pulseDue=NEVER;
                // Explicit wire ordinals, like CSIH, survive peripheral resets.
                long spcSequence;
                List<ExternalEvent> relativeInputs;
                int nextRelativeInput, generation;
                int[] pulses;
                int phase, statusNibble, crc, packed;
                long calibration, messageSamples, capturedTimestamp;
                String inputEvidence;
                Unit(int number) {
                    this.number=number;
                    base=0xffe05000L+number*0x1000L;
                    statusInterrupt=requiredRegister("RSENT"+number,"level status interrupt","EIC"+(232+2*number));
                    for (int i=0;i<regs.length;i++) if (suffix[i]!=null)
                        regs[i]=requiredRegister("RSENT"+number,"native register","RSENT"+number+suffix[i]);
                }
                int mode() { return (int)v[MST]; }
                boolean running() { return mode()==3 || mode()==5; }
                long timestampDivisor() { return ((v[TSPC]&127)+1)*(((v[TSPC]>>>8)&127)+1); }
                long tickCycles() { return 8*((((v[BRP]>>>16)&127)+1)*10+((v[BRP]>>>24)&15)); }
                int dataCount() { return (int)((v[CC]>>>1)&7)+1; }
                void put(int index,long value) {
                    v[index]=value&0xffffffffL;
                    setRegisterValue(regs[index].name,v[index]);
                }
                void driveStatus(boolean asserted) {
                    // Table6.11: this source is a level, unlike the receive IRQ.
                    // Follow existing CAN level-source convention; preserve EIMK/EIP/EITB.
                    long old=registerValue(statusInterrupt);
                    long next=(old&~0x1000L)|(asserted ? 0x1000L : 0);
                    if(next!=old) setRegisterValue(statusInterrupt.name,next);
                }
                void signals(PcodeThread<byte[]> thread) {
                    boolean r=(v[CS]&v[IDE]&1)!=0;
                    boolean s=(v[CS]&v[IDE]&0x7fe)!=0;
                    if (r && !receiveLine) {
                        requestInterrupt(thread,233+2*number);
                        dma.request(thread,119+number);
                    }
                    driveStatus(s);
                    receiveLine=r;
                }
                void flag(PcodeThread<byte[]> thread,long bit) {
                    put(CS,v[CS]|bit);
                    signals(thread);
                }
                void stopReceive() { pulses=null; pulseDue=NEVER; inputEvidence=null; }
                void clearBuffers() {
                    generation++;
                    backValid=false;
                    stopReceive();
                    for(int i=CS;i<18;i++) put(i,0);
                    receiveLine=false;
                    driveStatus(false);
                    outstanding=idlePending=false;
                    spcDue=NEVER;
                }
                void resetUnit() {
                    clearBuffers();
                    for(int i=0;i<CS;i++) if(regs[i]!=null) put(i,0);
                    timestampRemainder=0;
                }
                void selectedMode(PcodeThread<byte[]> thread,RegisterDef reg) {
                    // Complete selected nominal SPC/SMF0 path only. Configuration is not operation.
                    if ((v[CC]&0xf1)!=1)
                        fail(thread,reg,"unsupported-rsent-communication",
                            "operation requires SPC, no pause and SMF0; no serial extraction/SAE acknowledgement");
                    long mult=(v[BRP]&31)+1, div=((v[BRP]>>>8)&127)+1;
                    if (80*mult!=16*div)
                        fail(thread,reg,"unsupported-rsent-sample-clock","BRP must derive the documented16MHz sample clock from80MHz HSB");
                }
                void requestMode(PcodeThread<byte[]> thread,int requested) {
                    put(MDC,requested);
                    if(requested==mode()) { if(requested==5) idlePending=false; return; }
                    if(requested==0) { resetUnit(); return; }
                    if(requested==1) { clearBuffers(); put(MST,1); return; }
                    if(requested==3 && outstanding) { idlePending=true; return; }
                    if(requested==3) { spcDue=NEVER; outstanding=false; }
                    put(MST,requested);
                    idlePending=false;
                }
                void idleAfterReceive() {
                    if(idlePending) {
                        put(MST,3);
                        idlePending=false;
                        outstanding=false;
                        spcDue=NEVER;
                    }
                }
                void rejectPulse(PcodeThread<byte[]> thread,long flag) {
                    // Pending IDLE discards the frame and suppresses reception diagnostics.
                    if(!idlePending) flag(thread,flag);
                    stopReceive();
                    idleAfterReceive();
                }
                void startSpc(PcodeThread<byte[]> thread,long value) {
                    put(SPCT,value);
                    if(outstanding || (v[CS]&128)!=0) {
                        outstanding=false;
                        spcDue=NEVER;
                        stopReceive();
                        flag(thread,128);
                        event("rsent-spc-rejected",this,"previous response incomplete; clear NRS then retry");
                        idleAfterReceive();
                        return;
                    }
                    outstanding=true;
                    spcSequence++;
                    spcDue=Math.addExact(now,(value+1)*tickCycles());
                    event("rsent-spc-start",this,"SPCT write generates output pulse, not a sensor response");
                    if (relativeInputs != null && nextRelativeInput < relativeInputs.size()
                            && relativeInputs.get(nextRelativeInput).after_spc_triggers == spcSequence) {
                        ExternalEvent input = relativeInputs.get(nextRelativeInput++);
                        if (input.delay_hsb_cycles < spcDue - now)
                            throw new IllegalArgumentException("RSENT response overlaps its SPC output pulse");
                        int epoch = generation;
                        long sequence = spcSequence;
                        wireEvents.add(new ScheduledEvent(Math.addExact(now, input.delay_hsb_cycles),
                            input.ordinal, () -> {
                                if (epoch != generation || sequence != spcSequence || !outstanding) return;
                                receive(thread, number, input.pulse_samples, input.evidence);
                            }));
                    }
                }
                void promote(PcodeThread<byte[]> thread) {
                    // A read consumed buffer1 even if buffer2 is waiting: generate a new edge.
                    put(FRXD,v[FRXD]&~0x40000000L);
                    put(CS,v[CS]&~1L);
                    receiveLine=false;
                    if(backValid) {
                        put(SRXD,back[0]); put(CPL,back[1]); put(ML,back[2]);
                        put(FRTS,back[3]); put(FRXD,back[4]);
                        backValid=false;
                        put(CS,v[CS]|1);
                    }
                    signals(thread);
                }
                void finish(PcodeThread<byte[]> thread,int receivedCrc) {
                    if(idlePending) { stopReceive(); idleAfterReceive(); return; }
                    if((v[CC]&0x200)==0 && receivedCrc!=crcTable(crc)) {
                        rejectPulse(thread,2); return;
                    }
                    long result=0x40000000L|((long)(statusNibble&3)<<28)
                        |((long)receivedCrc<<24)|packed;
                    if((v[FRXD]&0x40000000L)!=0) {
                        if(backValid) flag(thread,4);
                        back[0]=statusNibble; back[1]=calibration; back[2]=messageSamples;
                        back[3]=capturedTimestamp; back[4]=result;
                        backValid=true;
                    } else {
                        put(SRXD,statusNibble); put(CPL,calibration); put(ML,messageSamples);
                        put(FRTS,capturedTimestamp); put(FRXD,result);
                        put(CS,v[CS]|1);
                        signals(thread);
                    }
                    outstanding=false;
                    event("rsent-frame-complete",this,inputEvidence);
                    stopReceive();
                }
                void pulseBoundary(PcodeThread<byte[]> thread) {
                    int samples=pulses[phase];
                    if(phase==0) {
                        calibration=samples;
                        // Native CLS uses nominal configured tick; independent of fast CRC.
                        if(samples*5L<42*tickCycles() || samples*5L>70*tickCycles()) {
                            rejectPulse(thread,32); return;
                        }
                        capturedTimestamp=v[TSC];
                    } else {
                        long scaled=samples*56L;
                        if(scaled<12*calibration || scaled>27*calibration) {
                            rejectPulse(thread,8); return;
                        }
                        int nibble=(int)((scaled+calibration/2)/calibration)-12;
                        if(phase==1) statusNibble=nibble;
                        else if(phase<=dataCount()+1) {
                            packed=(packed<<4)|nibble;
                            crc=nibble^crcTable(crc);
                        } else { finish(thread,nibble); return; }
                    }
                    phase++;
                    pulseDue=Math.addExact(now,pulses[phase]*5L);
                }
            }

            int crcTable(int value) {
                // Nibble-indexed polynomial table encoded without a temporary array.
                return (int)((0x582fb6c1493ea7d0L >>> (value*4))&15);
            }
            Unit unit(int number) {
                if(number<0 || number>=units.length)
                    throw new IllegalArgumentException("RSENT frame requires native modeled unit0 or1");
                return units[number];
            }
            Unit unit(RegisterDef register) {
                int number=(int)((register.address-0xffe05000L)/0x1000L);
                Unit u=unit(number);
                int index=(int)((register.address-u.base)/4);
                if(index<0 || index>=18 || u.regs[index]!=register)
                    throw new IllegalArgumentException("not a native RSENT0/1 register: "+register.name);
                return u;
            }
            void fail(PcodeThread<byte[]> thread,RegisterDef reg,String kind,String detail) {
                throw fault(kind,thread,reg.address,reg.size,"write",reg.evidence,detail);
            }
            void event(String kind,Unit u,String detail) {
                JsonObject event=new JsonObject();
                event.addProperty("kind",kind);
                event.addProperty("unit",u.number);
                event.addProperty("hsb_cycles",now);
                event.addProperty("spc_sequence",u.spcSequence);
                event.addProperty("spc_end_hsb_cycles",u.spcDue==NEVER ? -1 : u.spcDue);
                event.addProperty("sent_spc_active",u.spcDue!=NEVER);
                event.addProperty("sent_spc_level",u.spcDue!=NEVER ? ((u.v[CC]&0x1000)==0 ? 1:0)
                    : (u.mode()==5 && (u.v[CC]&0x1000)!=0 ? 1:0));
                event.addProperty("detail",detail);
                event.addProperty("evidence",evidence);
                trace.deviceEvents.add(event);
            }

            void validateWrite(PcodeThread<byte[]> thread,RegisterDef reg,long value) {
                if((value&~reg.writable_mask)!=0)
                    fail(thread,reg,"prohibited-rsent-reserved-bits","reserved RSENT bits must be written0");
                if(reg==selector) {
                    for(Unit u:units) if(u.mode()!=0)
                        fail(thread,reg,"prohibited-rsent-master-select","change TSSEL only with RSENT stopped in RESET");
                    // Native TSSEL exposes all six fields; only0/1 units are integrated here.
                    if((value&~0x77L)!=0 || (value&7)>2 || ((value>>>4)&7)>2)
                        fail(thread,reg,"unsupported-rsent-master-select","timestamp master refers to a channel outside modeled0/1");
                    return;
                }
                Unit u=unit(reg);
                int i=(int)((reg.address-u.base)/4), mode=u.mode();
                if(i==MDC) {
                    if(value!=0 && value!=1 && value!=3 && value!=5)
                        fail(thread,reg,"prohibited-rsent-mode","OMC permits0,1,3,5 only");
                    if(value!=mode && ((mode==0 && value!=1) || (mode==1 && value!=0 && value!=5)))
                        fail(thread,reg,"prohibited-rsent-mode-transition","mode transition violates Table19.14");
                    if(value==5 && mode!=5) u.selectedMode(thread,reg);
                    return;
                }
                if(mode==0) fail(thread,reg,"prohibited-rsent-reset-write","only MDC is writable in RESET");
                if((i==TSPC || i==CC || i==BRP) && mode!=1)
                    fail(thread,reg,"prohibited-rsent-config-write","configuration requires OMS1");
                if(i==CC && (((value>>>1)&7)>5 || (value&0xc0)==0xc0 || (value&0x30)==0x20))
                    fail(thread,reg,"prohibited-rsent-configuration","invalid NDN/SMF or fixed-length pause without pause");
                if(i==BRP && (((value>>>24)&15)>9 || ((value>>>16)&127)>89
                        || (((value>>>16)&127)==89 && ((value>>>24)&15)!=0)))
                    fail(thread,reg,"prohibited-rsent-baud","tick must be1.0..90.0us");
                if(i==TSC && mode!=1 && (u.v[TSPC]&0x10000)==0 && value!=0)
                    fail(thread,reg,"prohibited-rsent-timestamp-write","running master permits zero-clear only");
                if(i==SPCT && (mode!=5 || (u.v[CC]&1)==0))
                    fail(thread,reg,"prohibited-rsent-spc-write","SPCT requires active SPC operation");
            }
            void handleWrite(PcodeThread<byte[]> thread,RegisterDef reg,long value) {
                if(reg==selector) { masterSelect=value; return; }
                Unit u=unit(reg);
                int i=(int)((reg.address-u.base)/4);
                if(i==MDC) { u.requestMode(thread,(int)value); return; }
                if(i==SPCT) { u.startSpc(thread,value); return; }
                if(i==CSC) {
                    u.put(CS,u.v[CS]&~value); u.put(CSC,0); u.signals(thread); return;
                }
                if(i==TSC) {
                    if(u.mode()==1) { u.put(TSC,value); u.timestampRemainder=0; return; }
                    if((u.v[TSPC]&0x10000)!=0) { u.put(TSC,u.v[TSC]); return; }
                    u.put(TSC,0); u.timestampRemainder=0;
                    for(Unit slave:units) if(slave!=u && slave.running()
                            && (slave.v[TSPC]&0x10000)!=0
                            && ((masterSelect>>>(4*slave.number))&7)==u.number+1) {
                        slave.put(TSC,0); slave.timestampRemainder=0;
                    }
                    return;
                }
                u.put(i,value);
                if(i==IDE) u.signals(thread);
                if(i==TSPC) u.timestampRemainder=0;
            }
            void beforeRead(PcodeThread<byte[]> thread,RegisterDef reg) {
                if(reg==selector) return;
                Unit u=unit(reg);
                int i=(int)((reg.address-u.base)/4);
                // Only TSC backing is lazy; no reads alter time or synthesize frames.
                if(i==TSC) u.put(TSC,u.v[TSC]);
            }
            void readCompleted(PcodeThread<byte[]> thread,long address,int size) {
                if(size!=4) return;
                if(address==0xffe05044L) units[0].promote(thread);
                else if(address==0xffe06044L) units[1].promote(thread);
            }
            boolean receive(PcodeThread<byte[]> thread,int number,int[] pulseSamples,String source) {
                Unit u=unit(number);
                if(source==null || source.isBlank() || pulseSamples==null
                        || pulseSamples.length<4 || pulseSamples.length>9)
                    throw new IllegalArgumentException("rsent-frame needs evidence and4..9 calibration/status/data/CRC intervals");
                long sum=0;
                for(int sample:pulseSamples) {
                    if(sample<=0 || sample>131071)
                        throw new IllegalArgumentException("rsent-frame pulse_samples must be1..131071");
                    sum+=sample;
                }
                if(sum>0x1fffff)
                    throw new IllegalArgumentException("rsent-frame exceeds native21-bit message-sample counter");
                if(u.mode()!=5) {
                    event("rsent-input-ignored",u,source); return false;
                }
                if(pulseSamples.length!=u.dataCount()+3)
                    throw new IllegalArgumentException("rsent-frame interval count must match configured data count plus3");
                if(!u.outstanding || u.spcDue!=NEVER || u.pulses!=null || (u.v[CS]&128)!=0)
                    throw fault("rsent-input-boundary",thread,u.base+0x30,4,"external-input",source,
                        "SPC pulse must have completed and exactly one response request must be outstanding");
                // Scenario intervals are immutable and can be consumed without copying.
                u.pulses=pulseSamples;
                u.phase=0; u.crc=5; u.packed=u.statusNibble=0;
                u.messageSamples=sum; u.inputEvidence=source;
                u.pulseDue=Math.addExact(now,pulseSamples[0]*5L);
                event("rsent-frame-start",u,source);
                return true;
            }
            long cyclesUntilEvent() {
                long due=wireEvents.isEmpty() ? NEVER : wireEvents.peek().tick;
                for(Unit u:units) due=Math.min(due,Math.min(u.spcDue,u.pulseDue));
                return due==NEVER ? NEVER : Math.max(0,due-now);
            }
            void advanceClock(PcodeThread<byte[]> thread,long hsbCycles) {
                if(hsbCycles<0) throw new IllegalArgumentException("negative HSB progress");
                long end=Math.addExact(now,hsbCycles);
                do {
                    long step=Math.min(end-now,cyclesUntilEvent());
                    if(step>0) {
                        for(Unit u:units) if(u.running()) {
                            long divisor=u.timestampDivisor();
                            long ticks=step/divisor;
                            long rem=u.timestampRemainder+step%divisor;
                            u.v[TSC]=(u.v[TSC]+ticks+rem/divisor)&0xffffffffL;
                            u.timestampRemainder=rem%divisor;
                        }
                        now+=step;
                    }
                    for(Unit u:units) {
                        if(u.spcDue==now) {
                            u.spcDue=NEVER;
                            event("rsent-spc-end",u,"trigger waveform complete; response still outstanding");
                        }
                        if(u.pulseDue==now) u.pulseBoundary(thread);
                    }
                    while (!wireEvents.isEmpty() && wireEvents.peek().tick <= now)
                        wireEvents.remove().action.run();
                } while(now<end || cyclesUntilEvent()==0);
            }
            void flush() { for(Unit u:units) u.put(TSC,u.v[TSC]); }
            void reset() {
                // Keep monotonic HSB time, invalidate every live deadline and frame.
                masterSelect=0; setRegisterValue(selector.name,0);
                for(Unit u:units) u.resetUnit();
            }
            void loadInitialState(PcodeThread<byte[]> thread) {
                // Call ONCE after reset plus scenario register initialization. Do not call on every read.
                masterSelect=registerValue(selector);
                for(Unit u:units) {
                    for(int i=0;i<u.regs.length;i++) if(u.regs[i]!=null) u.v[i]=registerValue(u.regs[i]);
                    if(u.v[MST]!=u.v[MDC] || (u.mode()!=0 && u.mode()!=1 && u.mode()!=3 && u.mode()!=5)
                            || (u.v[CS]!=0) || (u.v[FRXD]&0xc0000000L)!=0 || (u.v[SRXD]&0x80000000L)!=0)
                        throw new IllegalArgumentException("initial RSENT state cannot inject pending frames/interrupts or mismatched modes");
                    if(u.running()) u.selectedMode(thread,u.regs[MDC]);
                    u.driveStatus(false);
                }
            }
        }

        // Sections7.3.2 and12.3: HSB-clocked DMACs, fixed channel priorities
        // and independent round-robin read/write interfaces. Bus accesses are
        // functional transactions; additional interconnect wait states are not modeled.
        final class Dma {
            static final int DSA = 0, DDA = 1, DTC = 2, DTCT = 3, DRSA = 4,
                DRDA = 5, DRTC = 6, DTCC = 7, DCEN = 8, DCST = 9,
                DCSTS = 10, DCSTC = 11, DTFR = 12, DTFRRQ = 13, DTFRRQC = 14;
            final Channel[] channels = new Channel[16];
            final Channel[] active = new Channel[2];
            final Channel[] blockOwner = new Channel[2];
            final RegisterDef suspension = requiredRegister("DMAC", "suspension", "DMACTL");
            final RegisterDef errors = requiredRegister("DMAC", "errors", "DMACER");
            final RegisterDef cycles = requiredRegister("DMAC", "cycles", "TFRSTS");
            final RegisterDef[] violations = {
                requiredRegister("DMAC", "master violation", "DM0CMV"),
                requiredRegister("DMAC", "master violation", "DM1CMV"),
                requiredRegister("DTS", "master violation", "DTSCMV")
            };
            final RegisterDef[][] peg = new RegisterDef[8][3];
            PcodeThread<byte[]> thread;
            long nextService = Long.MAX_VALUE;
            int readTurn, writeTurn;
            String masterRewriteAssumption;

            Dma() {
                for (int n = 0; n < channels.length; n++) channels[n] = new Channel(n);
                for (int n = 0; n < peg.length; n++) {
                    peg[n][0] = requiredRegister("PEG", "mask", "PEGG" + n + "MK");
                    peg[n][1] = requiredRegister("PEG", "base", "PEGG" + n + "BA");
                    peg[n][2] = requiredRegister("PEG", "SPID", "PEGG" + n + "SP");
                }
            }

            final class Channel {
                final int number;
                final String initiator;
                final RegisterDef[] bank = new RegisterDef[15];
                final RegisterDef master;
                long source, destination, count, control;
                int size;
                byte[] data;
                boolean readDone;

                Channel(int number) {
                    this.number = number;
                    initiator = "DMAC" + (number / 8) + "." + (number % 8);
                    for (int n = 0; n < bank.length; n++) {
                        bank[n] = register(0xffff8400L + number * 64L + n * 4L, 4);
                        if (bank[n] == null)
                            throw new IllegalStateException("DMAC channel register missing: " + number + "/" + n);
                    }
                    master = requiredRegister(initiator, "master configuration",
                        "DM" + (number / 8) + (number % 8) + "CM");
                }

                long get(int index) { return registerValue(bank[index]); }
                void put(int index, long value) { setRegisterValue(bank[index].name, value); }
                int spid() { return Math.max(2, (int) (registerValue(master) >>> 2) & 31); }

                void refreshRequest() {
                    boolean hardware = (get(DTCT) & 0x04000000L) != 0;
                    boolean requested = hardware && (get(DTFR) & get(DTFRRQ) & 1) != 0;
                    put(DCST, (get(DCST) & ~2L) | (requested ? 2 : 0));
                }

                boolean enabled() {
                    long configuration = get(DTCT), status = get(DCST);
                    return (get(DCEN) & 1) != 0
                        && ((configuration & 0x2000) != 0 || (status & 0x10) == 0)
                        && ((configuration & 0x08000000L) == 0 || (status & 0x80) == 0);
                }

                boolean ready() {
                    return enabled()
                        && (get(DCST) & ((get(DTCT) & 0x04000000L) != 0 ? 2 : 1)) != 0;
                }

                boolean continuesBlock() {
                    int mode = (int) control & 3;
                    return mode != 0 && (count & 0xffff) != 1
                        && (mode != 2 || (count >>> 16) != 1);
                }

                void begin() {
                    source = get(DSA);
                    destination = get(DDA);
                    count = get(DTC);
                    control = get(DTCT);
                    size = 1 << ((control >>> 2) & 7);
                    data = null;
                    readDone = false;
                    if (((source | destination) & (size - 1)) != 0)
                        throw fault("prohibited-dma-alignment", thread, source, size,
                            "dma", bank[DSA].evidence, "Section7.7 requires transfer-size-aligned addresses");
                    long status = get(DCST) | 0x100;
                    // Section7.3.5: acknowledge at single-cycle acceptance, or
                    // at the beginning of the final cycle of the selected block.
                    int mode = (int) control & 3;
                    boolean acknowledge = mode == 0 || (count & 0xffff) == 1
                        || (mode == 2 && (count >>> 16) == 1);
                    if (acknowledge) {
                        if ((control & 0x04000000L) != 0) put(DTFRRQ, get(DTFRRQ) & ~1L);
                        else status &= ~1L;
                    }
                    put(DCST, status);
                    refreshRequest();
                    setRegisterValue(cycles.name, registerValue(cycles) | (1L << number));
                }

                void read() {
                    data = dmaRead(thread, this, source, size);
                    readDone = true;
                }

                void complete() {
                    // MLE may be cleared while enabled; other transfer settings
                    // remain latched for the current bus cycle.
                    control = (control & ~0x2000L) | (get(DTCT) & 0x2000L);
                    boolean writeError = data != null && !dmaWrite(thread, this, destination, data);
                    boolean error = data == null || writeError;
                    data = null;
                    long status = get(DCST) & ~0x100L;
                    if (error) {
                        if ((status & 0x80) == 0)
                            status = (status & ~0x800L) | 0x80 | (writeError ? 0x800 : 0);
                        setRegisterValue(errors.name, registerValue(errors) | (1L << number));
                        latchEcmError(thread, 80);
                    }
                    boolean last = (count & 0xffff) == 1;
                    int reload1 = (int) (control >>> 9) & 3;
                    int reload2 = (int) (control >>> 11) & 3;
                    boolean reloadAddress = reload2 != 0 && (count >>> 16) == 1;
                    int reload = (last ? reload1 : 0) | (reloadAddress ? reload2 : 0);
                    long nextSource = nextAddress(source, (int) (control >>> 5) & 3, size);
                    long nextDestination = nextAddress(destination, (int) (control >>> 7) & 3, size);
                    put(DSA, (reload & 1) != 0 ? get(DRSA) : nextSource);
                    put(DDA, (reload & 2) != 0 ? get(DRDA) : nextDestination);
                    long remaining = (count - 1) & 0xffff;
                    long addressCount = count >>> 16;
                    if (reload2 != 0 || (control & 3) == 2) addressCount = (addressCount - 1) & 0xffff;
                    if (last && reload1 != 0) remaining = get(DRTC) & 0xffff;
                    if (reloadAddress || (last && reload1 != 0 && reload2 != 0))
                        addressCount = get(DRTC) >>> 16;
                    put(DTC, remaining | (addressCount << 16));
                    boolean match = get(DTCC) != 0 && (count & 0xffff) == get(DTCC);
                    if (last) {
                        status |= 0x10;
                        if ((control & 0x2000) == 0) put(DCEN, 0);
                    }
                    if (match) status |= 0x20;
                    put(DCST, status);
                    setRegisterValue(cycles.name, registerValue(cycles) & ~(1L << number));
                    if ((last && (control & 0x4000) != 0) || (match && (control & 0x8000) != 0))
                        requestInterrupt(thread, 16 + number);
                    int chain = (int) (control >>> 16) & 3;
                    if (chain == 3 || (chain == 1 && last)) {
                        Channel next = channels[(number & 8) | ((int) (control >>> 18) & 7)];
                        // Section7.5.4: chain compares PEID and UM, not SPID.
                        if (((registerValue(master) ^ registerValue(next.master)) & 0xe002) == 0)
                            next.put(DCST, next.get(DCST) | 1);
                    }
                    JsonObject event = new JsonObject();
                    event.addProperty("kind", "dma-transfer");
                    event.addProperty("channel", number);
                    event.addProperty("source", hex32(source));
                    event.addProperty("destination", hex32(destination));
                    event.addProperty("size", size);
                    event.addProperty("remaining", remaining);
                    event.addProperty("error", error);
                    event.addProperty("scheduler_tick", trace.instructions);
                    event.addProperty("hsb_cycles", hsbCycles);
                    event.addProperty("evidence", "R01UH0585EJ0120 Section7");
                    trace.deviceEvents.add(event);
                }
            }

            long nextAddress(long address, int mode, int size) {
                return (address + (mode == 0 ? size : mode == 1 ? -size : 0)) & 0xffffffffL;
            }

            Channel channel(RegisterDef register) {
                if (register.address >= 0xffff8400L && register.address < 0xffff8800L)
                    return channels[(int) ((register.address - 0xffff8400L) >>> 6)];
                return null;
            }

            void reset() {
                Arrays.fill(active, null);
                Arrays.fill(blockOwner, null);
                for (Channel channel : channels) {
                    channel.data = null;
                    channel.readDone = false;
                }
                nextService = Long.MAX_VALUE;
                readTurn = writeTurn = 0;
            }

            void schedule(PcodeThread<byte[]> thread) {
                this.thread = thread;
                if (nextService != Long.MAX_VALUE) return;
                for (Channel channel : active) {
                    if (channel == null) continue;
                    nextService = Math.addExact(hsbCycles, 1);
                    return;
                }
                if ((registerValue(suspension) & 1) != 0) return;
                for (Channel channel : blockOwner) {
                    if (channel == null || !channel.enabled()) continue;
                    nextService = Math.addExact(hsbCycles, 1);
                    return;
                }
                for (Channel channel : channels) {
                    if (!channel.ready()) continue;
                    nextService = Math.addExact(hsbCycles, 1);
                    return;
                }
            }

            long cyclesUntilEvent() {
                return nextService == Long.MAX_VALUE ? Long.MAX_VALUE : nextService - hsbCycles;
            }

            void advanceClock(PcodeThread<byte[]> thread) {
                if (nextService > hsbCycles) return;
                this.thread = thread;
                nextService = Long.MAX_VALUE;
                if ((registerValue(suspension) & 1) == 0) {
                    for (int group = 0; group < active.length; group++) {
                        if (active[group] != null) continue;
                        Channel selected = blockOwner[group];
                        if (selected != null && !selected.enabled()) selected = null;
                        if (selected == null) {
                            for (int n = group * 8; n < group * 8 + 8; n++) {
                                if (!channels[n].ready()) continue;
                                selected = channels[n];
                                break;
                            }
                        }
                        blockOwner[group] = selected;
                        if (selected != null) {
                            selected.begin();
                            active[group] = selected;
                        }
                    }
                }
                // Write responses retire before new reads, but a newly read word
                // cannot be written at the same edge. Each interface grants once.
                for (int n = 0; n < active.length; n++) {
                    int group = (writeTurn + n) % active.length;
                    Channel channel = active[group];
                    if (channel == null || !channel.readDone) continue;
                    channel.complete();
                    if (!channel.continuesBlock()) blockOwner[group] = null;
                    active[group] = null;
                    writeTurn = (group + 1) % active.length;
                    break;
                }
                for (int n = 0; n < active.length; n++) {
                    int group = (readTurn + n) % active.length;
                    Channel channel = active[group];
                    if (channel == null || channel.readDone) continue;
                    channel.read();
                    readTurn = (group + 1) % active.length;
                    break;
                }
                schedule(thread);
            }

            void request(PcodeThread<byte[]> thread, int source) {
                boolean selected = false;
                for (Channel channel : channels) {
                    if ((channel.get(DTFR) >>> 1) != source) continue;
                    // The selector/hold circuit runs even when REQEN or DTE
                    // is zero (Section7.4.3). A second edge latches OVF.
                    long request = channel.get(DTFRRQ);
                    channel.put(DTFRRQ, request | 1 | ((request & 1) != 0 ? 2 : 0));
                    channel.refreshRequest();
                    selected = true;
                }
                if (selected) schedule(thread);
            }

            boolean authorizeCpuWrite(PcodeThread<byte[]> thread, RegisterDef register) {
                if (register.address < 0xffff8000L || register.address >= 0xffff8800L
                        || (processorRegister(thread, "PSW") & 0x40000000L) == 0) return true;
                Channel channel = channel(register);
                // Table7.12: only CPU1 supervisor is the special master.
                // General masters cannot change common configuration.
                if (channel == null) return false;
                long identity = registerValue(channel.master);
                int spid = cpuSpid(thread);
                if ((identity & 0xe002) == 0x2002 && channel.spid() == spid) return true;
                RegisterDef captured = violations[channel.number / 8];
                if ((registerValue(captured) & 1) == 0)
                    setRegisterValue(captured.name,
                        0x20020001L | ((long) spid << 18) | ((channel.number & 7L) << 4));
                latchEcmError(thread, 81);
                return false;
            }

            void validateWrite(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                if ((value & ~register.writable_mask) != 0)
                    throw fault("prohibited-dma-register", thread, register.address, 4,
                        "write", register.evidence, "reserved DMA register bits must be zero");
                Channel channel = channel(register);
                if (channel == null) {
                    if (register.address >= 0xffff8100L && register.address < 0xffff8140L
                            && (channels[(int) ((register.address - 0xffff8100L) / 4)].get(DCEN) & 1) != 0) {
                        // Section7.8.1 forbids even identical writes while DTE=1.
                        // The opt-in bench assumption permits only a state-preserving rewrite.
                        if (masterRewriteAssumption == null || value != registerValue(register))
                            throw fault("prohibited-dma-register", thread, register.address, 4,
                                "write", register.evidence, "master configuration requires DTE=0");
                        JsonObject event = new JsonObject();
                        event.addProperty("kind", "dma-master-rewrite-assumption");
                        event.addProperty("register", register.name);
                        event.addProperty("value", hex32(value));
                        event.addProperty("pc", hex32(pc(thread)));
                        event.addProperty("instruction", trace.instructions);
                        event.addProperty("evidence", masterRewriteAssumption);
                        trace.deviceEvents.add(event);
                    }
                    return;
                }
                int index = (int) (register.address & 63) / 4;
                long previous = channel.get(index);
                if ((channel.get(DCEN) & 1) != 0 && index <= DTCT
                        && !(index == DTCT && (value == previous || value == (previous & ~0x2000L))))
                    throw fault("prohibited-dma-register", thread, register.address, 4,
                        "write", register.evidence, "transfer configuration requires DTE=0; only clearing MLE is permitted");
                if (index == DTFR && (previous & 1) != 0 && ((previous ^ value) & 0xfe) != 0)
                    throw fault("prohibited-dma-register", thread, register.address, 4,
                        "write", register.evidence, "REQSEL changes require REQEN=0");
                if (index == DTCT && ((value & 3) == 3 || ((value >>> 2) & 7) > 4
                        || ((value >>> 5) & 3) == 3 || ((value >>> 7) & 3) == 3
                        || ((value >>> 16) & 3) == 2
                        || (((value >>> 16) & 3) != 0 && ((value >>> 18) & 7) == (channel.number & 7))))
                    throw fault("prohibited-dma-register", thread, register.address, 4,
                        "write", register.evidence, "undefined transfer/address/chain selection");
            }

            void write(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                Channel channel = channel(register);
                if (channel != null) {
                    int index = (int) (register.address & 63) / 4;
                    if (index == DCSTS) channel.put(DCST, channel.get(DCST) | (value & 1));
                    else if (index == DCSTC) {
                        channel.put(DCST, channel.get(DCST) & ~(value | ((value & 0x80) != 0 ? 0x800 : 0)));
                        if ((value & 0x80) != 0)
                            setRegisterValue(errors.name, registerValue(errors) & ~(1L << channel.number));
                    } else if (index == DTFRRQC) channel.put(DTFRRQ, channel.get(DTFRRQ) & ~value);
                    channel.refreshRequest();
                } else if ("CMVC".equals(register.name)) {
                    for (int n = 0; n < violations.length; n++)
                        if ((value & (1L << n)) != 0)
                            setRegisterValue(violations[n].name, registerValue(violations[n]) & ~1L);
                }
                if (register.read_value != null) setRegisterValue(register.name, register.read_value);
                schedule(thread);
            }
        }

        void configureExternalEvents(PcodeThread<byte[]> thread, List<ExternalEvent> inputs) {
            long ordinal = 0;
            for (ExternalEvent input : inputs) {
                input.ordinal = ordinal++;
                if (input.after_transmit_words != null) {
                    Csih controller = csih(requiredRegister(
                        "csih-word", "controller", "CSIH" + input.unit + "CTL0"));
                    if (controller.relativeInputs == null) controller.relativeInputs = new ArrayList<>();
                    controller.relativeInputs.add(input);
                }
                else if (input.after_spc_triggers != null) {
                    Rsent.Unit receiver = rsent.unit(input.unit);
                    if (receiver.relativeInputs == null) receiver.relativeInputs = new ArrayList<>();
                    receiver.relativeInputs.add(input);
                }
                else {
                    externalEvents.add(new ScheduledEvent(input.after_instructions, input.ordinal,
                        () -> applyExternalEvent(thread, input)));
                }
            }
            Comparator<ExternalEvent> order = Comparator.comparingLong(input -> input.after_transmit_words);
            for (Csih controller : csihControllers.values()) {
                if (controller.relativeInputs != null) controller.relativeInputs.sort(order);
            }
            for (Rsent.Unit receiver : rsent.units) {
                if (receiver.relativeInputs != null)
                    receiver.relativeInputs.sort(Comparator.comparingLong(input -> input.after_spc_triggers));
            }
        }

        void dispatchExternalEvents() {
            while (!externalEvents.isEmpty() && externalEvents.peek().tick <= trace.instructions)
                externalEvents.remove().action.run();
        }

        void applyExternalEvent(PcodeThread<byte[]> thread, ExternalEvent input) {
            switch (input.kind) {
                case "clock": advanceClock(thread, input.p_bus_cycles); break;
                case "adc-sample": adc.input(input); break;
                case "rsent-frame":
                    rsent.receive(thread, input.unit, input.pulse_samples, input.evidence);
                    break;
                case "can-rx": receiveFrame(thread, input); break;
                case "csih-word":
                    csih(requiredRegister("csih-word", "controller", "CSIH" + input.unit + "CTL0"))
                        .complete(thread, input);
                    break;
                case "interrupt": requestInterrupt(thread, input.channel); break;
                case "memory-write": externalMemoryWrite(input); break;
                case "register-input": externalRegisterInput(input); break;
                case "ecm-pin-drive": externalEcmPinDrive(input); break;
                case "peripheral-reset": externalPeripheralReset(input); break;
                default: throw new IllegalArgumentException("unknown external event " + input.kind);
            }
        }

        void initializeDataFlashCells(List<FlashCellRange> ranges) {
            if (dataFlash == null) {
                if (!ranges.isEmpty()) throw new IllegalArgumentException("target has no DataFlash");
                return;
            }
            dataFlashCells = new byte[Math.toIntExact(dataFlash.size / 4)];
            // The registered dump supplies initial payload observations independently
            // of cell-state assumptions. A modeled erase/interruption invalidates them.
            dataFlashPayloadInvalid = new boolean[dataFlashCells.length];
            for (FlashCellRange range : ranges) {
                long address = parseUnsigned(range.address);
                if ((address & 3) != 0 || range.size <= 0 || (range.size & 3) != 0
                        || address < dataFlash.start || address + range.size > dataFlash.end_exclusive
                        || range.evidence == null || range.evidence.isBlank())
                    throw new IllegalArgumentException("invalid DataFlash cell-state range");
                byte state = switch (range.state == null ? "" : range.state) {
                    case "programmed" -> 1;
                    case "erased" -> 2;
                    default -> throw new IllegalArgumentException("unknown DataFlash cell state");
                };
                int first = Math.toIntExact((address - dataFlash.start) / 4);
                int last = first + range.size / 4;
                for (int cell = first; cell < last; cell++) {
                    if (dataFlashCells[cell] != 0)
                        throw new IllegalArgumentException("overlapping DataFlash cell-state ranges");
                    dataFlashCells[cell] = state;
                }
                JsonObject event = new JsonObject();
                event.addProperty("kind", "dataflash-cell-state");
                event.addProperty("address", hex32(address));
                event.addProperty("size", range.size);
                event.addProperty("state", range.state);
                event.addProperty("evidence", range.evidence);
                trace.deviceEvents.add(event);
            }
        }

        void validateDataFlashRead(PcodeThread<byte[]> thread, long address, int size) {
            long offset = address - dataFlash.start;
            if ((faciOperation == 0x20 || faciOperation == 0xe8)
                    && offset < faciTargetOffset + faciTargetSize && offset + size > faciTargetOffset)
                throw fault("dataflash-operation-in-progress", thread, address, size, "read",
                    "manual:R01UH0615EJ0120 section9", "target payload is unavailable during program/erase");
            int first = (int)(offset / 4), last = (int)((offset + size - 1) / 4);
            for (int cell = first; cell <= last; cell++) {
                if (dataFlashPayloadInvalid != null && dataFlashPayloadInvalid[cell])
                    throw fault("undefined-dataflash-payload", thread, address, size, "read",
                        "manual:R01UH0615EJ0120 sections6.3.14,6.3.15,9",
                        "erased or interrupted cells have no defined payload; successful programming is required");
            }
        }

        long faciCycles(long microseconds) {
            // Table37.14: characterized hardware maxima, not the software's 1.1x timeout.
            // The functional machine contract fixes CLK_HSB/P-Bus to 80MHz.
            if (spec.p_bus_hz != 80_000_000L)
                throw new IllegalStateException("FACI timing requires the declared 80MHz HSB/P-Bus contract");
            return Math.multiplyExact(microseconds, 80);
        }

        long faciTarget(RegisterDef register, PcodeThread<byte[]> thread, int operation) {
            RegisterDef start = requiredRegister(register.name, "start-address", register.start_address_register);
            // Table4.5: bits31:19 and address bits below the operation boundary are ignored.
            long offset = unsigned(memory(thread, start.address, start.size))
                & (operation == 0x20 ? 0x7ffc0 : 0x7fffc);
            int size = operation == 0x20 ? 64 : 4;
            if (dataFlash == null || offset + size > dataFlash.size)
                throw fault("unsupported-faci-range", thread, register.address, 1, "write",
                    register.evidence, "DataFlash target must be contained in the registered product region");
            if (operation == 0xe8) {
                int state = dataFlashCells == null ? 0 : dataFlashCells[(int)(offset / 4)];
                if (state != 2)
                    throw fault(state == 1 ? "prohibited-dataflash-overwrite" : "missing-dataflash-cell-state",
                        thread, dataFlash.start + offset, 4, "device", register.evidence,
                        "programming requires a known erased cell; additional writes and interrupted-cell writes require erase");
            }
            return offset;
        }

        void validateFaciWrite(PcodeThread<byte[]> thread, RegisterDef register, byte[] value) {
            int command = value[0] & 0xff;
            boolean program = faciPendingCommand == 0xe8;
            boolean data = program && (faciProgramStage == 1 || faciProgramStage == 2);
            if (value.length != (data ? 2 : 1))
                throw fault("unsupported-faci-width", thread, register.address, value.length,
                    "write", register.evidence, "FACI commands/count require byte writes; each program word requires a halfword");
            if (!data) {
                boolean valid = program && faciProgramStage == 0 ? command == 2
                    : faciPendingCommand != 0 ? command == 0xd0
                    : command == 0x50 || command == 0xb3 || command == 0x71
                        || command == 0x20 || command == 0xe8;
                if (!valid)
                    throw fault(faciPendingCommand == 0 ? "unsupported-faci-command" : "unsupported-faci-sequence",
                        thread, register.address, value.length, "write", register.evidence,
                        "supported sequences: 50; B3; 71,D0; 20,D0; E8,02,two halfwords,D0");
            }
            boolean stop = !data && command == 0xb3;
            RegisterDef status = requiredRegister(register.name, "status", register.status_register);
            long statusValue = unsigned(memory(thread, status.address, status.size));
            if (!stop && (statusValue & FSTATR_FRDY) == 0 && !program)
                throw fault("faci-not-ready", thread, register.address, value.length, "write",
                    register.evidence, "new FACI commands require FSTATR.FRDY=1");
            RegisterDef access = requiredRegister(register.name, "access-status", register.access_register);
            RegisterDef history = requiredRegister(register.name, "history", register.history_register);
            long accessValue = unsigned(memory(thread, access.address, access.size));
            memory(thread, history.address, history.size);
            RegisterDef control = requiredRegister(register.name, "control", register.control_register);
            long controlValue = unsigned(memory(thread, control.address, control.size)) & 0x81;
            if (!data && (command == 0x50 || stop)) {
                if (controlValue != 1 && controlValue != 0x80)
                    throw fault("unsupported-faci-mode", thread, register.address, value.length,
                        "write", register.evidence, "status clear/forced stop requires CodeFlash or DataFlash P/E mode");
                if (stop) {
                    RegisterDef emulation = requiredRegister(register.name, "emulation", register.emulation_register);
                    if (unsigned(memory(thread, emulation.address, emulation.size)) != 0)
                        throw fault("unsupported-faci-emulation", thread, register.address, value.length,
                            "write", register.evidence, "forced stop is bounded to normal FLEMU mode");
                }
                return;
            }
            RegisterDef mode = requiredRegister(register.name, "mode", register.mode_register);
            RegisterDef emulation = requiredRegister(register.name, "emulation", register.emulation_register);
            RegisterDef enable = requiredRegister(register.name, "enable", register.enable_register);
            RegisterDef secondaryEnable = requiredRegister(register.name, "secondary-enable", register.secondary_enable_register);
            if ((accessValue & FASTAT_CMDLK) != 0 || controlValue != 0x80
                    || (unsigned(memory(thread, mode.address, mode.size)) & ~1L) != 0
                    || unsigned(memory(thread, emulation.address, emulation.size)) != 0
                    || unsigned(memory(thread, enable.address, enable.size)) != 1
                    || unsigned(memory(thread, secondaryEnable.address, secondaryEnable.size)) != 1)
                throw fault("unsupported-faci-mode", thread, register.address, value.length, "write",
                    register.evidence, "submission requires both FHVE enables, unlocked DataFlash P/E and normal mode");
            if (program || command == 0xe8) {
                RegisterDef ecc = requiredRegister(register.name, "ECC mode", "FECCTMD");
                RegisterDef clock = requiredRegister(register.name, "clock", "FPCKAR");
                if ((unsigned(memory(thread, ecc.address, ecc.size)) & 0xff) != 0x30
                        || unsigned(memory(thread, clock.address, clock.size)) != 40)
                    throw fault("unsupported-faci-mode", thread, register.address, value.length, "write",
                        register.evidence, "programming requires normal ECC encoding/verification and FPCKAR=40MHz");
                if (!data && (command == 0xe8 || command == 0xd0)) faciTarget(register, thread, 0xe8);
                faciCycles(1700);
                return;
            }
            if (command == 0x20 || faciPendingCommand == 0x20) {
                faciTarget(register, thread, 0x20); // FEADDR is not used for block erase (Table4.6).
                RegisterDef clock = requiredRegister(register.name, "clock", "FPCKAR");
                if (unsigned(memory(thread, clock.address, clock.size)) != 40)
                    throw fault("unsupported-faci-mode", thread, register.address, value.length, "write",
                        register.evidence, "erase timing requires FPCKAR=40MHz");
                faciCycles(10000);
                return;
            }
            if (command == 0x71) return;
            RegisterDef start = requiredRegister(register.name, "start-address", register.start_address_register);
            RegisterDef end = requiredRegister(register.name, "end-address", register.end_address_register);
            long first = unsigned(memory(thread, start.address, start.size)) & 0x7fffc;
            long last = unsigned(memory(thread, end.address, end.size)) & 0x7fffc;
            if (dataFlash == null) throw new IllegalStateException("FACI blank check lacks DataFlash region");
            boolean decrement = (registerValue(mode) & 1) != 0;
            if ((decrement ? first < last : first > last)
                    || Math.max(first, last) + 4 > dataFlash.size || Math.abs(last - first) + 4 > 0x10000)
                throw fault("unsupported-faci-range", thread, register.address, value.length, "write",
                    register.evidence, "blank-check range must be ordered and contained in the registered DataFlash region");
            faciBlankFirst = -1;
            long scanned = 0;
            for (long offset = first;; offset += decrement ? -4 : 4) {
                int state = dataFlashCells == null ? 0 : dataFlashCells[(int)(offset / 4)];
                if (state == 0 || state == 3)
                    throw fault("missing-dataflash-cell-state", thread, dataFlash.start + offset, 4,
                        "device", "scenario", "blank checking requires known erased/programmed cells; interrupted cells require erase");
                scanned += 4;
                if (state == 1) {
                    faciBlankFirst = offset;
                    break;
                }
                if (offset == last) break;
            }
            // Functional upper envelope: partial64B groups cost100us except a lone4B word (30us).
            long remainder = scanned % 64;
            faciBlankCycles = faciCycles((scanned / 64) * 100
                + (remainder == 0 ? 0 : remainder == 4 ? 30 : 100));
        }

        void faciTransition(PcodeThread<byte[]> thread, RegisterDef register, int command,
                            String transition, JsonArray sequence) {
            JsonObject event = new JsonObject();
            event.addProperty("kind", register.trigger);
            event.addProperty("pc", hex32(pc(thread)));
            event.addProperty("command", String.format("0x%02X", command));
            event.add("sequence", sequence);
            event.addProperty("transition", transition);
            event.addProperty("hsb_cycles", hsbCycles);
            event.addProperty("scheduler_tick", trace.instructions);
            if (faciOperation != 0 && faciDeadline != Long.MAX_VALUE)
                event.addProperty("completion_hsb_cycles", faciDeadline);
            if (faciOperation == 0x20 || faciOperation == 0xe8) {
                event.addProperty("address", hex32(dataFlash.start + faciTargetOffset));
                event.addProperty("size", faciTargetSize);
            }
            event.addProperty("evidence", register.source_ref);
            trace.deviceEvents.add(event);
        }

        void dataFlashTransition(String transition, byte state, boolean payloadKnown) {
            int first = (int)(faciTargetOffset / 4), last = first + faciTargetSize / 4;
            Arrays.fill(dataFlashCells, first, last, state);
            Arrays.fill(dataFlashPayloadInvalid, first, last, !payloadKnown);
            JsonObject event = new JsonObject();
            event.addProperty("kind", "dataflash-cell-state");
            event.addProperty("transition", transition);
            event.addProperty("address", hex32(dataFlash.start + faciTargetOffset));
            event.addProperty("size", faciTargetSize);
            event.addProperty("state", state == 1 ? "programmed" : state == 2 ? "erased" : "indeterminate");
            event.addProperty("payload_known", payloadKnown);
            if (payloadKnown) {
                StringBuilder payload = new StringBuilder(8);
                for (byte b : faciProgramData) payload.append(String.format("%02x", b & 0xff));
                event.addProperty("data_hex", payload.toString());
            }
            event.addProperty("hsb_cycles", hsbCycles);
            event.addProperty("scheduler_tick", trace.instructions);
            event.addProperty("evidence", "R01UH0615EJ0120 sections6.3.8,6.3.10,6.3.14,6.3.15,9");
            trace.deviceEvents.add(event);
        }

        void cancelFaciMutation(String reason) {
            if (faciOperation == 0x20 || faciOperation == 0xe8)
                dataFlashTransition(reason, (byte)3, false);
        }

        void resetFaci() {
            cancelFaciMutation("reset-cancelled");
            if (faciOperation != 0 || faciPendingCommand != 0) {
                JsonObject event = new JsonObject();
                event.addProperty("kind", "faci-reset-cancelled");
                event.addProperty("operation", faciOperation);
                event.addProperty("pending_command", faciPendingCommand);
                event.addProperty("hsb_cycles", hsbCycles);
                event.addProperty("scheduler_tick", trace.instructions);
                event.addProperty("evidence", "R01UH0615EJ0120 section9");
                trace.deviceEvents.add(event);
            }
            faciPendingCommand = 0;
            faciProgramStage = 0;
            faciOperation = 0;
            faciReadErrors = 0;
            faciDeadline = Long.MAX_VALUE;
            faciTargetSize = 0;
            Arrays.fill(faciProgramData, (byte)0);
        }

        void handleFaciWrite(PcodeThread<byte[]> thread, RegisterDef register, byte[] value) {
            int command = value[0] & 0xff;
            JsonArray sequence = new JsonArray();
            if (faciPendingCommand == 0xe8) {
                if (faciProgramStage == 0) {
                    faciProgramStage = 1;
                    sequence.add(0xe8);
                    sequence.add(2);
                    faciTransition(thread, register, command, "program-count-accepted", sequence);
                    return;
                }
                if (faciProgramStage <= 2) {
                    System.arraycopy(value, 0, faciProgramData, (faciProgramStage - 1) * 2, 2);
                    faciProgramStage++;
                    sequence.add(unsigned(value));
                    faciTransition(thread, register, command, "program-data-buffered", sequence);
                    return;
                }
            }
            RegisterDef statusRegister = requiredRegister(register.name, "status", register.status_register);
            RegisterDef accessRegister = requiredRegister(register.name, "access-status", register.access_register);
            RegisterDef historyRegister = requiredRegister(register.name, "history", register.history_register);
            long status = unsigned(memory(statusRegister.address, statusRegister.size));
            long history = unsigned(memory(historyRegister.address, historyRegister.size));
            if (command == 0x71 || command == 0x20 || command == 0xe8) {
                faciPendingCommand = command;
                if (command == 0xe8) {
                    faciProgramStage = 0;
                    faciTargetOffset = faciTarget(register, thread, command);
                    faciTargetSize = 4;
                    Arrays.fill(faciProgramData, (byte)0);
                    // Table4.7: Program clears FRDY at the FIRST access, unlike erase/blank check.
                    setRegisterValue(statusRegister.name, status & ~FSTATR_FRDY);
                    setRegisterValue(historyRegister.name, (command << 8) | ((history >>> 8) & 0xff));
                }
                sequence.add(command);
                faciTransition(thread, register, command, command == 0xe8 ? "program-buffer-started"
                    : command == 0x20 ? "erase-prefix-accepted" : "blank-check-prefix-accepted", sequence);
                return;
            }
            String transition;
            if (command == 0xd0) {
                faciOperation = faciPendingCommand;
                sequence.add(faciPendingCommand);
                if (faciOperation == 0xe8) {
                    sequence.add(2);
                    sequence.add((faciProgramData[0] & 0xff) | ((faciProgramData[1] & 0xff) << 8));
                    sequence.add((faciProgramData[2] & 0xff) | ((faciProgramData[3] & 0xff) << 8));
                } else {
                    setRegisterValue(historyRegister.name, 0xd000 | faciPendingCommand);
                }
                if (faciOperation == 0x20) {
                    faciTargetOffset = faciTarget(register, thread, 0x20);
                    faciTargetSize = 64;
                }
                setRegisterValue(statusRegister.name, status & ~FSTATR_FRDY);
                faciDeadline = Math.addExact(hsbCycles, faciOperation == 0x20 ? faciCycles(10000)
                    : faciOperation == 0xe8 ? faciCycles(1700) : faciBlankCycles);
                transition = faciOperation == 0x20 ? "erase-started"
                    : faciOperation == 0xe8 ? "program-started" : "blank-check-started";
            }
            else {
                long accessStatus = unsigned(memory(accessRegister.address, accessRegister.size));
                long nextStatus, nextAccessStatus;
                if (command == 0xb3) {
                    cancelFaciMutation("forced-stop-cancelled");
                    nextStatus = status & ~FSTATR_FORCED_STOP_CLEAR_MASK;
                    nextAccessStatus = (accessStatus & FASTAT_ACCESS_ERROR_MASK) != 0
                        ? accessStatus : accessStatus & ~FASTAT_CMDLK;
                    faciOperation = 0xb3;
                    faciDeadline = Math.addExact(hsbCycles, faciCycles(20));
                    transition = "forced-stop-started";
                }
                else {
                    nextStatus = status & ~FSTATR_STATUS_CLEAR_MASK;
                    if ((accessStatus & FASTAT_ACCESS_ERROR_MASK) != 0) nextStatus |= FSTATR_ILGLERR;
                    nextAccessStatus = (nextStatus & FSTATR_COMMAND_LOCK_MASK) != 0
                        ? accessStatus | FASTAT_CMDLK : accessStatus & ~FASTAT_CMDLK;
                    transition = "status-cleared";
                }
                if ((status & FSTATR_CORRECTION_MASK) != 0) nextAccessStatus &= ~1L;
                setRegisterValue(historyRegister.name, (command << 8) | ((history >>> 8) & 0xff));
                setRegisterValue(statusRegister.name, nextStatus);
                setRegisterValue(accessRegister.name, nextAccessStatus);
            }
            sequence.add(command);
            faciTransition(thread, register, command, transition, sequence);
            faciPendingCommand = 0;
            faciProgramStage = 0;
        }

        void completeFaciOperation() {
            faciDeadline = Long.MAX_VALUE;
            long access = registerValue(registersByName.get("FASTAT"));
            long previousStatus = registerValue(registersByName.get("FSTATR"));
            long status = previousStatus | FSTATR_FRDY;
            if ((access & FASTAT_ACCESS_ERROR_MASK) != 0) {
                status |= FSTATR_ILGLERR;
                access |= FASTAT_CMDLK;
            }
            if (faciOperation == 0x71) {
                setRegisterValue("FBCSTAT", faciBlankFirst < 0 ? 0 : 1);
                if (faciBlankFirst >= 0) setRegisterValue("FPSADDR", faciBlankFirst);
            }
            else if (faciOperation == 0x20 || faciOperation == 0xe8) {
                if ((status & FSTATR_COMMAND_LOCK_MASK) != 0 || (access & FASTAT_CMDLK) != 0)
                    cancelFaciMutation("error-completion");
                else if (faciOperation == 0x20) {
                    // Erased DataFlash reads are undefined: never synthesize FF bytes.
                    dataFlashTransition("erase-completed", (byte)2, false);
                }
                else {
                    setMemory(dataFlash.start + faciTargetOffset, faciProgramData);
                    dataFlashTransition("program-completed", (byte)1, true);
                }
            }
            setRegisterValue("FSTATR", status);
            setRegisterValue("FASTAT", access);
            JsonObject event = new JsonObject();
            event.addProperty("kind", "faci-completion");
            event.addProperty("command", faciOperation == 0xb3 ? "0xB3" : "0xD0");
            event.addProperty("operation", faciOperation == 0x20 ? "erase"
                : faciOperation == 0xe8 ? "program" : faciOperation == 0x71 ? "blank-check" : "forced-stop");
            event.addProperty("hsb_cycles", hsbCycles);
            event.addProperty("scheduler_tick", trace.instructions);
            event.addProperty("evidence", "R01UH0615EJ0120 Tables4.7,4.15,6.2,sections6.3.8-6.3.15,9,Tables10.1,10.2; R01UH0585EJ0120 Table37.14,Table6.11");
            trace.deviceEvents.add(event);
            // FRDY's physical 0->1 completion edge, routed through the existing INTC.
            if ((previousStatus & FSTATR_FRDY) == 0) requestInterrupt(executionThread, 379);
            faciOperation = 0;
            faciTargetSize = 0;
        }

        // An opt-in scripted diagnostic peer, not an ICU-S implementation.
        // Only the caller's two startup self-check commands are admitted.
        final class IcusStartupStub {
            final IcusStartupConfig config;
            int nextResponse;
            IcusStartupResponse active;
            long deadline = Long.MAX_VALUE;
            boolean completed;

            IcusStartupStub(IcusStartupConfig config) {
                this.config = config;
                if (config.evidence == null || config.evidence.isBlank()
                        || config.responses == null || config.responses.isEmpty())
                    throw new IllegalArgumentException("ICU-S startup stub needs explicit evidence and responses");
                for (IcusStartupResponse response : config.responses) {
                    if (response == null || response.command == null || response.error_bits == null)
                        throw new IllegalArgumentException("incomplete ICU-S startup response");
                    response.commandValue = parseUnsigned(response.command);
                    response.errorValue = parseUnsigned(response.error_bits);
                    if (!handles(response.commandValue) || response.errorValue < 0
                            || response.errorValue > 0xfff || response.completion_hsb_cycles <= 0)
                        throw new IllegalArgumentException("invalid ICU-S diagnostic response");
                }
            }

            boolean handles(long word) {
                return word == 0x7000 || word == 0x7100;
            }

            void event(String action, IcusStartupResponse response) {
                JsonObject event = new JsonObject();
                event.addProperty("kind", "icus-startup-stub-" + action);
                event.addProperty("evidence", config.evidence);
                event.addProperty("hsb_cycles", hsbCycles);
                event.addProperty("instruction", trace.instructions);
                if (response != null) {
                    event.addProperty("command", response.command);
                    event.addProperty("error_bits", response.error_bits);
                }
                trace.deviceEvents.add(event);
            }

            void validateCommand(PcodeThread<byte[]> thread, RegisterDef register, long word) {
                if (active != null || nextResponse >= config.responses.size()
                        || config.responses.get(nextResponse).commandValue != word)
                    throw fault("icus-startup-stub-mismatch", thread, register.address,
                        register.size, "write", "scenario-stub",
                        "diagnostic command is overlapping, out of order, or has no declared response");
            }

            void start() {
                active = config.responses.get(nextResponse++);
                completed = false;
                deadline = Math.addExact(hsbCycles, active.completion_hsb_cycles);
                setRegisterValue("ICUSREG10", 0);
                setRegisterValue("ICUSSTS", 1);
                setRegisterValue("ICUSSTS2", 0);
                event("start", active);
            }

            void complete() {
                deadline = Long.MAX_VALUE;
                completed = true;
                setRegisterValue("ICUSREG10", active.errorValue);
                setRegisterValue("ICUSSTS", 0);
                setRegisterValue("ICUSSTS2", 2);
                event("complete", active);
            }

            void validateAck(PcodeThread<byte[]> thread, RegisterDef register, long word) {
                if (active != null && (!completed || word != 3))
                    throw fault("icus-startup-stub-mismatch", thread, register.address,
                        register.size, "write", "scenario-stub",
                        "diagnostic acknowledgement differs from the declared completed-command contract");
            }

            void acknowledge() {
                if (active == null) return;
                // The original completion callback reads the error word AFTER
                // this write; retain it until the next command or stub reset.
                setRegisterValue("ICUSSTS2", 0);
                event("ack", active);
                active = null;
                completed = false;
            }

            void reset() {
                if (active != null) event("cancel", active);
                active = null;
                completed = false;
                deadline = Long.MAX_VALUE;
                // Explicit idle-state assumption of this opt-in bench peer.
                // Consumed replies are not replayed after a peripheral reset.
                setRegisterValue("ICUSSTS", 0);
                setRegisterValue("ICUSSTS2", 0);
                setRegisterValue("ICUSIRQSTS", 0);
                setRegisterValue("ICUSREG10", 0);
                event("reset", null);
            }
        }

        void handleIcusWrite(PcodeThread<byte[]> thread, RegisterDef register, byte[] value) {
            long word = unsigned(value);
            if (icusStartupStub != null && icusStartupStub.handles(word)) {
                icusStartupStub.start();
                return;
            }
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

        void handleDcraInput(RegisterDef register, byte[] value) {
            RegisterDef output = requiredRegister(register.name, "status", register.status_register);
            RegisterDef control = requiredRegister(register.name, "mode", register.mode_register);
            if (registerValue(control) == 0x22) {
                // Tables33.8-33.9: raw CRC8 XOR FF on read, MSB-first 0x1D.
                long previous = registerValue(output);
                int crc = (int) ((previous ^ 0xFF) ^ unsigned(value)) & 0xFF;
                for (int bit = 0; bit < 8; bit++)
                    crc = ((crc << 1) ^ ((crc & 0x80) != 0 ? 0x1D : 0)) & 0xFF;
                // Only low8 are defined in this mode; high lanes keep explicit seed data.
                setRegisterValue(output.name, (previous & 0xFFFFFF00L) | (crc ^ 0xFF));
                return;
            }
            // R01UH0585EJ0120 pp2845–2846,2850–2851: LSB first, reflected
            // 04C11DB7 polynomial; COUT reads expose internal state XOR FFFFFFFF.
            int crc = ~(int) registerValue(output) ^ (int) unsigned(value);
            for (int bit = 0; bit < 32; bit++) {
                crc = (crc >>> 1) ^ ((crc & 1) != 0 ? 0xedb88320 : 0);
            }
            setRegisterValue(output.name, Integer.toUnsignedLong(~crc));
        }

        int ecmDomain(RegisterDef register) {
            if (register.address < 0xffd61000L) return 0;
            if (register.address < 0xffd62000L) return 1;
            return 2;
        }

        void bindPortAliases() {
            for (RegisterDef alias : registers) {
                if (!"port-pin-alias".equals(alias.trigger)) continue;
                int separator = alias.name.indexOf('_');
                String prefix = alias.name.startsWith("J") ? "J" : "";
                String group = alias.name.substring(separator - 1, separator);
                long pin = 1L << Integer.parseInt(alias.name.substring(separator + 1));
                List<PortAliasField> fields = new ArrayList<>();
                for (int index = 0; index < PORT_PIN_BITS.length; index++) {
                    RegisterDef source = registersByName.get(prefix + PORT_PIN_REGISTERS[index] + group);
                    if (source == null) continue; // Table2.42 omits several JP group functions.
                    long effective = "port-input".equals(source.behavior)
                        ? source.active_mask : source.writable_mask;
                    if ((effective & pin) == 0) continue;
                    fields.add(new PortAliasField(source, 1L << PORT_PIN_BITS[index], pin));
                    portAliasDependents.computeIfAbsent(source, ignored -> new ArrayList<>()).add(alias);
                }
                portAliasFields.put(alias, fields);
            }
        }

        void refreshPortAlias(RegisterDef alias) {
            long value = alias.reset;
            for (PortAliasField field : portAliasFields.get(alias)) {
                value = (value & ~field.aliasMask) | ((registerValue(field.source) & field.pinMask) != 0
                    ? field.aliasMask : 0);
            }
            setRegisterValue(alias.name, value);
        }

        void refreshPortDependents(RegisterDef source) {
            List<RegisterDef> dependents = portAliasDependents.get(source);
            if (dependents != null) {
                for (RegisterDef alias : dependents) refreshPortAlias(alias);
            }
        }

        void handlePortWrite(RegisterDef register, long value) {
            if ("port-pin-alias".equals(register.trigger)) {
                for (PortAliasField field : portAliasFields.get(register)) {
                    if ((register.writable_mask & field.aliasMask) == 0) continue;
                    long bit = (value & field.aliasMask) != 0 ? field.pinMask : 0;
                    setRegisterValue(field.source.name,
                        (registerValue(field.source) & ~field.pinMask) | bit);
                }
                refreshPortAlias(register);
            }
            else if ("port-masked-alias".equals(register.trigger)) {
                RegisterDef target = requiredRegister(register.name, "control", register.control_register);
                long enabled = (value >>> 16) & target.writable_mask;
                long next = (registerValue(target) & ~enabled) | (value & enabled);
                setRegisterValue(target.name, next);
                setRegisterValue(register.name, next);
                refreshPortDependents(target);
            }
            else {
                setRegisterValue(register.name,
                    (register.reset & ~register.writable_mask) | (value & register.writable_mask));
                refreshPortDependents(register);
            }
        }

        boolean ecmHasUnmaskedErrors(int domain) {
            for (int index = 0; index < 3; index++) {
                RegisterDef status = registersByName.get(ECM_STATUS_REGISTERS[domain][index]);
                long errors = ecmLatchedStatus(status);
                long mask = registerValue(registersByName.get(ECM_ERROR_MASK_REGISTERS[index]));
                if ((errors & ~mask & (index == 2 ? 0x7fffffffL : 0xffffffffL)) != 0)
                    return true;
            }
            return false;
        }

        boolean checkerOutputLoopback() {
            // P3_11, fifth alternative output: PFCAE/PFCE/PFC = 1/0/0.
            // R01UH0585EJ0120 Tables2.18,2.46 and section2.3.4.3.
            return (registerValue(registersByName.get("PMC3")) & 0x800) != 0
                && (registerValue(registersByName.get("PM3")) & 0x800) == 0
                && (registerValue(registersByName.get("PIPC3")) & 0x800) == 0
                && (registerValue(registersByName.get("PFCAE3")) & 0x800) != 0
                && (registerValue(registersByName.get("PFCE3")) & 0x800) == 0
                && (registerValue(registersByName.get("PFC3")) & 0x800) == 0
                && (registerValue(registersByName.get("PBDC3")) & 0x800) != 0
                && (registerValue(registersByName.get("PIBC3")) & 0x800) == 0;
        }

        void refreshEcmFeedback() {
            for (int domain = 0; domain < 2; domain++) {
                // An asserted output already dominates unknown error inputs.
                // Do not demand an undeclared pin sample just to keep it low.
                if (!ecmOutputLow[domain] && ecmHasUnmaskedErrors(domain))
                    ecmOutputLow[domain] = true;
                String drive = ecmExternalDrive[domain];
                if (drive == null) continue;
                // An unrouted checker is not an ECM observation. Keep the
                // explicitly supplied sample rather than invent a Hi-Z level.
                if (domain == 1 && !checkerOutputLoopback() && !"low".equals(drive))
                    continue;
                RegisterDef status = registersByName.get(
                    domain == 0 ? "ECMMESSTR2" : "ECMCESSTR2");
                long latched = ecmLatchedStatus(status);
                if (fieldBistExecuted && missingResetInputs.contains(status.name))
                    latched |= 1L << 27;
                // PINV applies to alternate outputs before their pin-level
                // loopback (Table2.24). Camry inverts P3_11 during boot.
                boolean outputHigh = !ecmOutputLow[domain];
                if (domain == 1 && (registerValue(registersByName.get("PINV3")) & 0x800) != 0)
                    outputHigh = !outputHigh;
                boolean high = !"low".equals(drive) && outputHigh;
                setRegisterValue(status.name,
                    (latched & 0x7fffffffL) | (high ? 0x80000000L : 0));
            }
        }

        void externalEcmPinDrive(ExternalEvent input) {
            int domain;
            if ("ERROROUT".equals(input.pin)) domain = 0;
            else if ("ERROROUT_C".equals(input.pin)) domain = 1;
            else throw new IllegalArgumentException("unsupported ECM pin: " + input.pin);
            if (!"released".equals(input.drive) && !"low".equals(input.drive))
                throw new IllegalArgumentException("ECM pin drive must be released or low");
            ecmExternalDrive[domain] = input.drive;
            refreshEcmFeedback();
            JsonObject event = new JsonObject();
            event.addProperty("kind", "ecm-pin-drive");
            event.addProperty("pin", input.pin);
            event.addProperty("drive", input.drive);
            event.addProperty("scheduler_tick", trace.instructions);
            event.addProperty("evidence", input.evidence);
            trace.deviceEvents.add(event);
        }

        void ecmProtectionEvent(PcodeThread<byte[]> thread, RegisterDef register,
                                String kind, long value, String detail) {
            JsonObject event = new JsonObject();
            event.addProperty("kind", kind);
            event.addProperty("pc", hex32(pc(thread)));
            event.addProperty("register", register.name);
            event.addProperty("value", hex32(value));
            event.addProperty("detail", detail);
            event.addProperty("evidence", "R01UH0585EJ0120 section32.3.5");
            trace.deviceEvents.add(event);
        }

        void failEcmProtection(PcodeThread<byte[]> thread, RegisterDef register, long value) {
            ecmStage = 0;
            ecmTarget = null;
            setRegisterValue("ECMPS", 1);
            ecmProtectionEvent(thread, register, "ecm-protection-rejected", value,
                "missing command, intervening same-module write, wrong target or wrong data");
        }

        void handlePdmaComparatorWrite(PcodeThread<byte[]> thread, RegisterDef register, long value) {
            if ((value & register.protection_mask) != register.protection_value) {
                setRegisterValue(register.name, registerBeforeWrite);
                return;
            }
            long selection = value & register.writable_mask;
            setRegisterValue(register.name, selection);
            if (selection == 0) return; // Removing injection does not clear latched error status.
            long master = registerValue(registersByName.get("ECMMESSTR0"));
            long checker = registerValue(registersByName.get("ECMCESSTR0"));
            setRegisterValue("ECMMESSTR0", master | 4);
            setRegisterValue("ECMCESSTR0", checker | 4);
            refreshEcmFeedback();
            // Table32.5 emits a pulse when enabled error-source status is set.
            if ((master & checker & 4) == 0
                    && (registerValue(registersByName.get("ECMMICFG0")) & 4) != 0)
                requestInterrupt(thread, 8);
            JsonObject event = new JsonObject();
            event.addProperty("kind", "pdma-comparison-error");
            event.addProperty("pc", hex32(pc(thread)));
            event.addProperty("source", 2);
            event.addProperty("evidence", "R01UH0585EJ0120 Tables31.145,32.5,32.9");
            trace.deviceEvents.add(event);
        }

        void commitEcmWrite(PcodeThread<byte[]> thread, RegisterDef register, long value) {
            if ("ecm-status-clear".equals(register.trigger)) {
                int index = register.name.charAt(register.name.length() - 1) - '0';
                long clear = value & (index == 2 ? 0x7fffffffL : 0xffffffffL);
                // Read both before mutating either, so missing external pin state
                // stays an explicit prerequisite rather than a fabricated value.
                RegisterDef master = registersByName.get("ECMMESSTR" + index);
                RegisterDef checker = registersByName.get("ECMCESSTR" + index);
                long masterValue = registerValue(master);
                long checkerValue = registerValue(checker);
                setRegisterValue(master.name, masterValue & ~clear);
                setRegisterValue(checker.name, checkerValue & ~clear);
                return;
            }
            if ("ecm-pseudo-error".equals(register.trigger) && value != 0) {
                throw fault("unsupported-ecm-event", thread, register.address, register.size,
                    "write", register.evidence,
                    "pseudo error routing/interrupt/reset effects are not modeled");
            }
            if ((register.name.equals("ECMEPCFG") || register.name.equals("ECMDTMCTL")
                    || register.name.equals("ECMDTMCMP") || register.name.equals("ECMEOCCFG"))
                    && value != 0) {
                throw fault("unsupported-ecm-mode", thread, register.address, register.size,
                    "write", register.evidence,
                    "dynamic output, active delay timer and nonzero cross-clock compare configuration require unmodeled clock progression");
            }
            if ("ecm-output-set".equals(register.trigger)
                    || "ecm-output-clear".equals(register.trigger)) {
                if ((value & 1) == 0) return;
                String prefix = ecmDomain(register) == 0 ? "ECMMESSTR" : "ECMCESSTR";
                RegisterDef status = registersByName.get(prefix + "2");
                long status2 = registerValue(status);
                boolean set = "ecm-output-set".equals(register.trigger);
                if (set) {
                    setRegisterValue(status.name, status2 | 0x40000000L);
                }
                else {
                    if (registerValue(registersByName.get("ECMEOCCFG")) != 0) {
                        throw fault("unsupported-ecm-mode", thread, register.address,
                            register.size, "write", register.evidence,
                            "output clear invalidation counter expiry requires clock progression");
                    }
                    if (ecmHasUnmaskedErrors(ecmDomain(register))) return;
                }
                ecmOutputLow[ecmDomain(register)] = set;
                refreshEcmFeedback();
                ecmProtectionEvent(thread, register, "ecm-output-request", set ? 0 : 1,
                    "internal output updated; only declared external drives resolve pin feedback");
                return;
            }
            if (register.access.contains("r")) setRegisterValue(register.name, value);
            if (register.name.startsWith("ECMEMK")) refreshEcmFeedback();
        }

        void handleEcmWrite(PcodeThread<byte[]> thread, RegisterDef register, long value) {
            int domain = ecmDomain(register);
            boolean command = "ecm-command".equals(register.trigger);
            boolean unprotected = register.name.equals("ECMPEM")
                || register.name.equals("ECMEPCTL");
            // The p-code store already occurred. Neither an intermediate
            // protocol word nor a failed write may change the effective register.
            if (!command) setRegisterValue(register.name, registerBeforeWrite);
            if (command) {
                if (ecmStage != 0) failEcmProtection(thread, register, value);
                if (value != 0xa5) {
                    failEcmProtection(thread, register, value);
                    return;
                }
                ecmStage = 1;
                ecmCommandDomain = domain;
                ecmTarget = null;
                return;
            }
            if (unprotected) {
                if (ecmStage != 0) failEcmProtection(thread, register, value);
                setRegisterValue(register.name, value & register.writable_mask);
                return;
            }
            int stage = ecmCommandDomain == domain ? ecmStage : 0;
            long nativeMask = register.size == 4 ? 0xffffffffL
                : (1L << (register.size * 8)) - 1;
            if (stage == 1) {
                ecmTarget = register;
                ecmDesired = value;
                ecmStage = 2;
            }
            else if (stage == 2 && ecmTarget == register
                    && value == (ecmDesired ^ nativeMask)) {
                ecmStage = 3;
            }
            else if (stage == 3 && ecmTarget == register && value == ecmDesired) {
                ecmStage = 0;
                ecmTarget = null;
                commitEcmWrite(thread, register, value);
                setRegisterValue("ECMPS", 0);
                ecmProtectionEvent(thread, register, "ecm-protection-accepted", value,
                    "A5/value/inverted-value/value completed; protected effect committed");
            }
            else {
                failEcmProtection(thread, register, value);
            }
        }

        void handleCvmWrite(RegisterDef register, long value) {
            if ("cvm-enable-once".equals(register.trigger)) {
                if (!cvmEnableWritten) {
                    RegisterDef enable = requiredRegister(register.name, "status", register.status_register);
                    setRegisterValue(enable.name,
                        (registerValue(enable) & ~register.writable_mask)
                            | (value & register.writable_mask));
                    cvmEnableWritten = true;
                }
                setRegisterValue(register.name, 0);
            }
            else if ("cvm-factor-clear".equals(register.trigger)) {
                RegisterDef factors = requiredRegister(register.name, "status", register.status_register);
                setRegisterValue(factors.name, registerValue(factors) & ~(value & register.writable_mask));
                setRegisterValue(register.name, 0);
            }
            else {
                setRegisterValue(register.name,
                    (registerBeforeWrite & ~register.writable_mask) | (value & register.writable_mask));
            }
        }

        void resetPeripheralEccControl(RegisterDef register) {
            // Table31.79 defines every reset bit except the live RAM-output
            // ECEMF input. Store known bits for internal RMW, not a CPU-readable
            // assertion that ECEMF is zero or retained across reset.
            setMemory(register.address, bytes(register.reset & register.reset_mask,
                register.size, language.isBigEndian()));
            initializedDeviceRegisters.remove(register.name);
            missingResetInputs.add(register.name);
        }

        void handlePeripheralEccWrite(RegisterDef register, long value) {
            if ("peripheral-ecc-test".equals(register.trigger)) {
                // Validation excludes effective ECTMCE=1. Table31.80 clears
                // all test-control bits in normal mode; ETMA always reads zero.
                setRegisterValue(register.name, 0);
                return;
            }
            long next = (registerBeforeWrite & ~0x38L) | (value & 0x38L);
            if ((value & 0xc000L) == 0x4000L) {
                next = (next & ~0x80L) | (value & 0x80L);
            }
            if ((value & 0x200L) != 0) next &= ~2L;
            if ((value & 0x400L) != 0) next &= ~4L;
            if ((value & 0x600L) != 0
                    || ((next & 0x80L) != 0 && (registerBeforeWrite & 0x80L) == 0)) {
                next &= ~0x30800L;
            }
            next &= ~0xc600L;
            if (initializedDeviceRegisters.contains(register.name)) {
                setRegisterValue(register.name, next);
            }
            else {
                // Clearing latched flags cannot resolve the live ECEMF input.
                setMemory(register.address, bytes(next, register.size, language.isBigEndian()));
            }
        }

        void handleBankedEccClear(RegisterDef command, long selected) {
            setRegisterValue(command.name, 0);
            if (selected == 0) return;
            RegisterDef status = requiredRegister(command.name, "status", command.status_register);
            RegisterDef overflow = command.secondary_status_register == null ? null
                : requiredRegister(command.name, "secondary-status", command.secondary_status_register);
            long statusValue = registerValue(status);
            // A clear determines only selected functional bits, never undefined
            // reset bits (ITOVFSTR bit 4, Table31.71). Keep the whole-word input
            // prerequisite until a scenario supplies those bits.
            boolean unknownOverflow = overflow != null && overflow.reset_mask != null
                && !initializedDeviceRegisters.contains(overflow.name);
            long overflowValue = overflow == null ? 0 : unknownOverflow
                ? overflow.reset & overflow.reset_mask : registerValue(overflow);
            for (int bank = 0; bank < command.status_masks.size(); bank++) {
                if ((selected & (1L << bank)) == 0) continue;
                statusValue &= ~command.status_masks.get(bank);
                overflowValue &= ~(command.secondary_status_masks == null
                    ? 1L << bank : command.secondary_status_masks.get(bank));
                if (command.capture_registers != null) {
                    String captureName = command.capture_registers.get(bank);
                    RegisterDef capture = requiredRegister(command.name, "capture", captureName);
                    setRegisterValue(capture.name, 0);
                }
            }
            setRegisterValue(status.name, statusValue);
            if (unknownOverflow) {
                setMemory(overflow.address, bytes(overflowValue, overflow.size, language.isBigEndian()));
                missingResetInputs.add(overflow.name);
            }
            else if (overflow != null) {
                setRegisterValue(overflow.name, overflowValue);
            }
        }

        void externalPeripheralReset(ExternalEvent input) {
            // An isolated peripheral reset boundary, not a CPU restart or a
            // claim that CVM voltage/reset feedback has physically occurred.
            applyReset(input.reset_class);
            JsonObject event = new JsonObject();
            event.addProperty("kind", "external-peripheral-reset");
            event.addProperty("reset_class", input.reset_class);
            event.addProperty("scheduler_tick", trace.instructions);
            event.addProperty("evidence", input.evidence);
            trace.deviceEvents.add(event);
        }

        void handleRegisterWrite(PcodeThread<byte[]> thread, long address, int size, byte[] value) {
            RegisterDef register = register(address, size);
            if (register == null) return;
            registerWriteEvent(thread, register, value);
            if ("tauj".equals(register.behavior)) {
                tauj.write(thread, register, unsigned(value)); return;
            }
            if ("taud".equals(register.behavior) || "pic-taud".equals(register.behavior)) {
                tsg.deferPicRouting();
                taud.write(thread, register, unsigned(value));
                finishPicRouting(thread);
                return;
            }
            if ("tsg".equals(register.behavior) || "pic-tsg".equals(register.behavior)) {
                tsg.write(thread, register, unsigned(value)); return;
            }
            if ("pic1-start".equals(register.behavior)) {
                tsg.deferPicRouting();
                pic1.write(thread, register, unsigned(value));
                finishPicRouting(thread);
                return;
            }
            if ("pdma".equals(register.behavior)) {
                dma.write(thread, register, unsigned(value));
                return;
            }
            if ("adc".equals(register.behavior) || "adc-clock".equals(register.behavior)) {
                adc.handleWrite(thread, register, unsigned(value));
                return;
            }
            if ("rsent".equals(register.behavior)) {
                rsent.handleWrite(thread, register, unsigned(value));
                return;
            }
            if ("guard-error-clear".equals(register.trigger)) {
                RegisterDef status = requiredRegister(register.name, "error status", register.status_register);
                long clear = unsigned(value) << (8 * (address - register.address));
                setRegisterValue(status.name, registerValue(status) & ~clear);
                setRegisterValue(register.name, 0);
                return;
            }
            if ("pdma-comparator".equals(register.trigger)) {
                handlePdmaComparatorWrite(thread, register, unsigned(value));
                return;
            }
            if ("reset-factor-clear".equals(register.trigger)) {
                clearResetFactors(unsigned(value));
                return;
            }
            if ("csih".equals(register.behavior)) {
                if (!"dma-select".equals(register.trigger)) csih(register).write(thread, register, unsigned(value));
                return;
            }
            if ("seg".equals(register.behavior)) {
                if ("SEGFLAG".equals(register.name)) {
                    if (initializedDeviceRegisters.contains("SEGFLAG")) {
                        setRegisterValue("SEGFLAG",
                            (registerBeforeWrite & ~0x354L) | (unsigned(value) & 0x354L));
                    }
                    setSegFlags(unsigned(value));
                    if ((registerBeforeWrite & ~unsigned(value) & 0x354L) != 0)
                        segNotificationPending = enabledSegFlags() != 0;
                }
                else if ("SEGCONT".equals(register.name)) {
                    segNotificationPending = enabledSegFlags() != 0;
                }
                return;
            }
            if (isGuard(register)) {
                if (guardWriteIgnored) {
                    setRegisterValue(register.name, registerBeforeWrite);
                }
                else {
                    setRegisterValue(register.name,
                        (registerBeforeWrite & ~register.writable_mask)
                            | (registerValue(register) & register.writable_mask));
                    if ("peg-mask".equals(register.trigger)) {
                        RegisterDef base = guardLock(register);
                        setRegisterValue(base.name, registerValue(base) & ~1L);
                    }
                }
                return;
            }
            if ("peripheral-ecc".equals(register.behavior)) {
                handlePeripheralEccWrite(register, unsigned(value));
                return;
            }
            if ("cvm".equals(register.behavior)) {
                handleCvmWrite(register, unsigned(value));
                return;
            }
            if ("ecm".equals(register.behavior)) {
                handleEcmWrite(thread, register, unsigned(value));
                return;
            }
            if ("port-config".equals(register.behavior)) {
                handlePortWrite(register, unsigned(value));
                refreshEcmFeedback();
                return;
            }
            if ("noise-filter".equals(register.behavior)) {
                if ("noise-clock-selector".equals(register.trigger)
                        && unsigned(value) != registerBeforeWrite) {
                    RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                    // Do not turn a requested source into an asserted CLKACT.
                    // Its actual activity must be supplied as a new external input.
                    setRegisterValue(status.name, unsigned(value));
                    missingResetInputs.add(status.name);
                }
                return;
            }
            if ("intc_eic".equals(register.behavior) && register.reset != null) {
                boolean level = (register.reset & 0x8000) != 0;
                long writable = level ? 0xcfL : 0x10cfL;
                // Table6.4: EICT and reserved bits read their reset value.
                // Level EIRF follows its source, not the software write.
                setRegisterValue(register.name, (register.reset & 0x8000L)
                    | (level ? registerBeforeWrite & 0x1000L : 0)
                    | (registerValue(register) & writable));
            }
            handleReceiveWrite(thread, register, value);
            if (register.trigger == null) return;
            switch (register.trigger) {
                case "clock-divider": {
                    RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                    // Functional completion at the write boundary, not oscillator startup,
                    // waveform frequency qualification, or cycle-accurate synchronization.
                    setRegisterValue(status.name, register.completion_value
                        | (unsigned(value) == 0 ? 0 : register.active_mask));
                    break;
                }
                case "clock-selector": {
                    if (registerBeforeWrite != unsigned(value)) {
                        RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                        setRegisterValue(status.name, unsigned(value));
                    }
                    break;
                }
                case "flmd-command":
                    flmdStage = 1;
                    break;
                case "flmd-control":
                    if (flmdStage == 3) {
                        flmdStage = 0;
                        RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                        setRegisterValue(status.name, 0);
                    }
                    else {
                        if (flmdStage == 1) flmdDesired = unsigned(value);
                        flmdStage++;
                        setRegisterValue(register.name, registerBeforeWrite);
                    }
                    break;
                case "bist-control":
                    break; // Validated HWBISTEXE storage affects the next applicable reset only.
                case "dcra-control":
                    if (registerBeforeWrite != unsigned(value)) dcraSeeded.remove(register.name);
                    break;
                case "dcra-seed":
                    // Writes initialize raw state; reads apply the hardware's final XOR.
                    RegisterDef crcControl = requiredRegister(register.name, "mode", register.mode_register);
                    setRegisterValue(register.name, unsigned(value)
                        ^ (registerValue(crcControl) == 0x22 ? 0xFF : 0xFFFFFFFFL));
                    dcraSeeded.add(crcControl.name);
                    break;
                case "dcra-input": handleDcraInput(register, value); break;
                case "rscfd-transmit": handleRscfdWrite(thread, register, value); break;
                case "faci-command": handleFaciWrite(thread, register, value); break;
                case "faci-access-status": {
                    long next = registerBeforeWrite
                        & ~(faciReadErrors & ~unsigned(value) & FASTAT_ACCESS_ERROR_MASK);
                    setRegisterValue(register.name, next);
                    faciReadErrors &= next;
                    break;
                }
                case "faci-setup-initialize":
                case "faci-area-selector":
                case "faci-clock-notify": {
                    boolean setup = "faci-setup-initialize".equals(register.trigger);
                    long incoming = unsigned(value);
                    long next = registerBeforeWrite;
                    if ((registerValue(registersByName.get("FSTATR")) & FSTATR_FRDY) != 0
                            && (incoming & register.protection_mask) == register.protection_value) {
                        next = incoming & register.writable_mask;
                        if (setup && next != 0) {
                            for (String name : FACI_SETUP_REGISTERS)
                                setRegisterValue(name, 0);
                        }
                    }
                    setRegisterValue(register.name, next);
                    break;
                }
                case "faci-address":
                    RegisterDef addressStatus = requiredRegister(register.name, "status", register.status_register);
                    setRegisterValue(register.name, (registerValue(addressStatus) & FSTATR_FRDY) != 0
                        ? unsigned(value) & ~3L : registerBeforeWrite);
                    break;
                case "faci-dataflash-mode": {
                    RegisterDef modeStatus = requiredRegister(register.name, "status", register.status_register);
                    long incoming = unsigned(value);
                    long next = registerBeforeWrite;
                    if ((registerValue(modeStatus) & FSTATR_FRDY) != 0) {
                        next = (incoming >>> 8) == 0xaa && registerBeforeWrite == 0
                            ? incoming & 0x80 : 0;
                    }
                    setRegisterValue(register.name, next);
                    break;
                }
                case "faci-normal-emulation":
                    break; // Validated zero-to-zero write; no OCD-mode behavior is inferred.
                case "faci-enable":
                    setRegisterValue(register.name, unsigned(value) & 1);
                    break;
                case "banked-ecc-clear":
                    handleBankedEccClear(register,
                        unsigned(value) << (8 * (address - register.address)));
                    break;
                case "ecc-notification":
                    // The validated byte lanes already updated the ordinary enable latches.
                    break;
                case "dataflash-read-cycle":
                    setRegisterValue(register.name, unsigned(value) & 0xf);
                    break;
                case "ecc-protected-control": {
                    long incoming = unsigned(value);
                    long writable = register.writable_mask;
                    long protectionMask = register.protection_mask == null
                        ? 0xc000L : register.protection_mask;
                    long protectionValue = register.protection_value == null
                        ? 0x4000L : register.protection_value;
                    // Narrow writes must include the key and the data in the same access.
                    long next = address == register.address
                            && (incoming & protectionMask) == protectionValue
                        ? incoming & writable : registerBeforeWrite;
                    setRegisterValue(register.name, next & writable);
                    break;
                }
                case "icus-command": handleIcusWrite(thread, register, value); break;
                case "icus-control":
                    if (icusStartupStub != null) icusStartupStub.acknowledge();
                    break;
                default: throw new IllegalStateException(
                    "unknown machine-model trigger: " + register.trigger);
            }
        }

        void afterWrite(PcodeThread<byte[]> thread, long address, int size, byte[] value) {
            if (internalWrite) return;
            if (discardBusStore) {
                discardBusStore = false;
                return;
            }
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
            if (!peripheralFile) handleRegisterWrite(thread, address, size, value);
        }

        void initializeResetRegisters() {
            dcraSeeded.clear();
            segFlags = 0;
            segNotificationPending = false;
            flmdStage = 0;
            cvmEnableWritten = false;
            resetFaci();
            // Table10.3: no reset defines the CVMOUT pin level.
            if (registersByName.containsKey("CVMMON")) missingResetInputs.add("CVMMON");
            for (RegisterDef register : registers) {
                if ("peripheral-ecc-control".equals(register.trigger)) {
                    resetPeripheralEccControl(register);
                    continue;
                }
                // Partial reset values do not determine a readable whole word.
                if (register.reset_mask != null) {
                    missingResetInputs.add(register.name);
                    if ("reset-factors".equals(register.trigger)
                            || "ecm-bist-status".equals(register.trigger)) {
                        // Backing bits for controller-side RMW only. The
                        // separate knowledge mask still forbids unresolved CPU reads.
                        setMemory(register.address, bytes(register.reset & register.reset_mask,
                            register.size, language.isBigEndian()));
                    }
                    continue;
                }
                if (register.reset == null) continue;
                setRegisterValue(register.name, register.reset);
            }
            taud.reset();
            tauj.reset();
            tsg.reset();
            rsent.reset();
            if (icusStartupStub != null) icusStartupStub.reset();
            declaredTsgRegisters.clear();
        }

        void clearPreparedFrame(PcodeThread<byte[]> thread, Instruction instruction) {
            // Explicit exploration aid only. Architectural PREPARE allocates
            // locals without initializing or erasing their pre-existing bytes.
            if (!peripheralFile || entrySp < 0) return;
            byte[] raw;
            try {
                raw = instruction.getBytes();
            }
            catch (MemoryAccessException exc) {
                return;
            }
            if (raw == null || raw.length < 2) return;
            int slots = ((raw[0] & 0xff) | ((raw[1] & 0xff) << 8)) >> 1 & 0x1f;
            if (slots == 0) return;
            long sp = processorRegister(thread, "sp");
            long lo = entrySp - 0x1000L;
            long hi = entrySp + 0x200L;
            for (int offset = 0; offset < (slots << 2); offset++) {
                long addr = (sp + offset) & 0xffffffffL;
                if (Long.compareUnsigned(addr, lo) < 0 || Long.compareUnsigned(addr, hi) >= 0)
                    continue;
                int fill = -1;
                for (long[] row : scenarioFills) {
                    if (Long.compareUnsigned(addr, row[0]) >= 0
                            && Long.compareUnsigned(addr, row[1]) < 0) {
                        fill = (int) row[2];
                        break;
                    }
                }
                if (fill < 0) continue;
                setMemory(addr, new byte[] {(byte) fill});
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

        void externalMemoryWrite(ExternalEvent input) {
            long address = parseUnsigned(input.address);
            byte[] value = parseHex(input.data_hex);
            RegionDef region = region(address, value.length);
            if (region == null
                    || "pbg0_unimplemented_channels8_9".equals(region.name)
                    || region.name.startsWith("codeflash")
                    || region.name.equals("dataflash")) {
                throw new IllegalArgumentException("external memory-write requires mapped writable RAM at "
                    + hex32(address) + " size=" + value.length);
            }
            setMemory(address, value);
            if (region.alias_group != null) {
                long delta = address - region.start;
                for (RegionDef alias : aliases.get(region.alias_group)) {
                    if (alias != region) setMemory(alias.start + delta, value);
                }
            }
            JsonObject event = new JsonObject();
            event.addProperty("kind", "external-memory-write");
            event.addProperty("address", hex32(address));
            event.addProperty("size", value.length);
            event.addProperty("scheduler_tick", trace.instructions);
            event.addProperty("evidence", input.evidence);
            trace.deviceEvents.add(event);
        }

        void externalRegisterInput(ExternalEvent input) {
            RegisterDef register = registersByName.get(input.register);
            if (register == null || (!register.access.contains("r") && !register.read_input)) {
                throw new IllegalArgumentException(
                    "external register-input requires a readable register or declared bus response: "
                    + input.register);
            }
            if (isGuard(register) || ("seg".equals(register.behavior)
                    && !"SEGFLAG".equals(register.name))) {
                throw new IllegalArgumentException(
                    "register-input cannot impersonate an external master or inject guard/SEG configuration: "
                        + input.register);
            }
            if ("faci".equals(register.behavior) && (register.trigger != null
                    || FACI_RESULT_REGISTERS.contains(register.name)))
                throw new IllegalArgumentException(
                    "register-input cannot inject modeled flash sequencer state: " + input.register);
            if ("pdma".equals(register.behavior) || "guard-error".equals(register.behavior))
                throw new IllegalArgumentException(
                    "register-input cannot inject DMA or guard-derived state: " + input.register);
            if ("adc".equals(register.behavior) || "adc-clock".equals(register.behavior))
                throw new IllegalArgumentException(
                    "ADC functional state requires clock and adc-sample events, not register-input");
            if ("rsent".equals(register.behavior))
                throw new IllegalArgumentException(
                    "RSENT receive state requires clock and rsent-frame events, not register-input");
            if ("tauj".equals(register.behavior) || "taud".equals(register.behavior)
                    || "tsg".equals(register.behavior) || "pic-taud".equals(register.behavior)
                    || "pic-tsg".equals(register.behavior) || "pic1-start".equals(register.behavior))
                throw new IllegalArgumentException(
                    "timer/PIC functional state requires real commands and clock events, not register-input");
            if ("csih".equals(register.behavior)) {
                throw new IllegalArgumentException("CSIH functional state requires csih-word wire events, not register-input");
            }
            if ("dcra".equals(register.behavior)) {
                throw new IllegalArgumentException(
                    "DCRA has no external input pins; register-input cannot inject CRC state: "
                    + input.register);
            }
            if ("flmd".equals(register.behavior)) {
                throw new IllegalArgumentException(
                    "register-input cannot inject protected FLMD control or sequence status: "
                    + input.register);
            }
            if ("clock".equals(register.behavior)) {
                throw new IllegalArgumentException(
                    "register-input cannot inject clock control or derived functional status: "
                    + input.register);
            }
            if ("cvm".equals(register.behavior)
                    && !"CVMF".equals(register.name) && !"CVMMON".equals(register.name)) {
                throw new IllegalArgumentException(
                    "register-input cannot inject CVM configuration or write-once state: " + input.register);
            }
            if ("ecm".equals(register.behavior) && !register.name.contains("ESSTR")) {
                throw new IllegalArgumentException(
                    "register-input cannot inject ECM protection or configuration state: "
                    + input.register);
            }
            if ("port-config".equals(register.behavior) || "noise-filter".equals(register.behavior)) {
                throw new IllegalArgumentException(
                    "register-input cannot inject port/filter configuration: " + input.register);
            }
            if ("lockstep".equals(register.behavior)) {
                throw new IllegalArgumentException(
                    "register-input cannot inject comparator configuration: " + input.register);
            }
            if ("reset-controller".equals(register.behavior) && !"RESF".equals(register.name)) {
                throw new IllegalArgumentException(
                    "register-input cannot inject reset-controller commands: " + input.register);
            }
            long value = parseUnsigned(input.value);
            long maximum = register.size >= 4 ? 0xffffffffL
                : (1L << (register.size * 8)) - 1;
            if (Long.compareUnsigned(value, maximum) > 0) {
                throw new IllegalArgumentException(
                    "external register-input exceeds register width: " + input.register);
            }
            if ("cvm".equals(register.behavior) && (value & ~register.active_mask) != 0) {
                throw new IllegalArgumentException("external CVM input sets reserved bits: " + input.register);
            }
            if ("bist".equals(register.behavior)) {
                validateBistInput(register, register.address,
                    bytes(value, register.size, language.isBigEndian()), input.evidence);
            }
            if ("SEGFLAG".equals(register.name) && (value & 0x354L) != segFlagValue()) {
                throw new IllegalArgumentException(
                    "SEGFLAG input may resolve undefined bits, not inject hardware error flags");
            }
            if ("RESF".equals(register.name)) validateResetFactorInput(value);
            if (register.read_input) {
                if (readInputResponses == null) readInputResponses = new HashMap<>();
                readInputResponses.put(register.name, value);
            }
            else {
                setRegisterValue(register.name, value);
                if ("ecm".equals(register.behavior)) refreshEcmFeedback();
            }
            JsonObject event = new JsonObject();
            event.addProperty("kind", register.read_input
                ? "external-register-read-response" : "external-register-input");
            event.addProperty("register", register.name);
            event.addProperty("address", hex32(register.address));
            event.addProperty("value", hex32(value));
            event.addProperty("scheduler_tick", trace.instructions);
            event.addProperty("evidence", input.evidence);
            trace.deviceEvents.add(event);
        }

        boolean overlapsRegion(long address, int size) {
            long end = address + Integer.toUnsignedLong(size);
            for (RegionDef candidate : regions) {
                if (Long.compareUnsigned(address, candidate.end_exclusive) < 0
                        && Long.compareUnsigned(candidate.start, end) < 0) {
                    return true;
                }
            }
            return false;
        }

        void initializeMemory(long address, byte[] value, String evidence) {
            RegionDef region = region(address, value.length);
            RegisterDef register = register(address, value.length);
            if (region != null && "pbg0_unimplemented_channels8_9".equals(region.name)) {
                throw new IllegalArgumentException("unimplemented P-Bus lanes have no scenario-initializable storage");
            }
            if (region == null && register == null) {
                if (!peripheralFile || overlapsRegion(address, value.length)) {
                    throw new IllegalArgumentException("scenario initializes unmapped state at "
                        + hex32(address) + " size=" + value.length);
                }
                setMemory(address, value);
                JsonObject peripheral = new JsonObject();
                peripheral.addProperty("kind", "scenario-initialization");
                peripheral.addProperty("address", hex32(address));
                peripheral.addProperty("size", value.length);
                peripheral.addProperty("evidence", evidence == null ? "scenario" : evidence);
                trace.deviceEvents.add(peripheral);
                return;
            }
            if (region != null
                    && (region.name.startsWith("codeflash") || region.name.equals("dataflash"))) {
                throw new IllegalArgumentException("scenario cannot overlay registered image region "
                    + region.name + " at " + hex32(address));
            }
            if (register != null && "bist".equals(register.behavior)) {
                validateBistInput(register, address, value, evidence);
            }
            if (register != null && "ecm-bist-status".equals(register.trigger)
                    && fieldBistExecuted) {
                if (address != register.address || value.length != register.size) {
                    throw new IllegalArgumentException("post-BIST ECM input requires the complete status word");
                }
                value = bytes(unsigned(value) | (1L << 27), register.size, language.isBigEndian());
            }
            if (register != null && "RESF".equals(register.name)) {
                if (address != register.address || value.length != register.size)
                    throw new IllegalArgumentException("RESF input requires the complete status word");
                validateResetFactorInput(unsigned(value));
            }
            setMemory(address, value);
            if (register != null && "tsg".equals(register.behavior))
                declaredTsgRegisters.add(register.name);
            if (register != null && register.address == address && register.size == value.length) {
                if (register.reset_mask != null) initializedDeviceRegisters.add(register.name);
                missingResetInputs.remove(register.name);
                if ("port-config".equals(register.behavior))
                    handlePortWrite(register, unsigned(value));
            }
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

        void validateBistInput(RegisterDef register, long address, byte[] value, String evidence) {
            if (address != register.address || value.length != register.size
                    || (unsigned(value) & ~register.active_mask) != 0
                    || evidence == null || evidence.isBlank()) {
                throw new IllegalArgumentException("BIST input requires an identified, complete "
                    + "32-bit word with reserved bits zero: " + register.name);
            }
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
        boolean icctrlWrite;
        long isprBeforeInstruction;
        byte[] readInputBacking;

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
            model.trace.enterInstruction(instruction.getAddress().getOffset());
            model.requireExecute(
                thread, instruction.getAddress().getOffset(), instruction.getLength());
            thread.getState().getVar(model.memorySpace, instruction.getAddress().getOffset(),
                instruction.getLength(), true, Reason.EXECUTE_READ);
            String mnemonic = instruction.getMnemonicString();
            if (model.peripheralFile && "stsr".equals(mnemonic)) {
                for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
                    Register system = instruction.getRegister(operand);
                    if (system != null && "ICCTRL".equals(system.getName())) {
                        model.scriptIcctrl(thread);
                        break;
                    }
                }
            }
            interruptReturn = "eiret".equals(mnemonic);
            automaticPriorityReturn = interruptReturn
                && (model.processorRegister(thread, "PSW") & 0x40) == 0
                && (model.processorRegister(thread, "INTCFG") & 1) == 0;
            Register destination = "ldsr".equals(mnemonic) ? instruction.getRegister(1) : null;
            icctrlWrite = !model.peripheralFile && destination != null
                && "ICCTRL".equals(destination.getName());
            protectedIsprWrite = destination != null && "ISPR".equals(destination.getName())
                && (model.processorRegister(thread, "INTCFG") & 1) == 0;
            if (automaticPriorityReturn || protectedIsprWrite) {
                isprBeforeInstruction = model.processorRegister(thread, "ISPR");
            }
        }

        @Override
        public void beforeLoad(PcodeThread<byte[]> thread, PcodeOp op, AddressSpace space,
                               byte[] offset, int size) {
            if (space.equals(language.getDefaultSpace())) {
                long address = offset(offset);
                RegisterDef register = model.beforeRead(thread, address, size);
                if (register != null && register.read_input) {
                    // Materialize only this LOAD's bus lanes, then restore command
                    // backing bytes in afterLoad. CPU writes never alter the response.
                    readInputBacking = model.memory(address, size);
                    long response = model.readInputResponses.get(register.name);
                    int lane = Math.toIntExact(address - register.address);
                    int shift = language.isBigEndian()
                        ? 8 * (register.size - lane - size) : 8 * lane;
                    model.setMemory(address, bytes(response >>> shift, size, language.isBigEndian()));
                }
            }
        }

        @Override
        public void afterLoad(PcodeThread<byte[]> thread, PcodeOp op, AddressSpace space,
                              byte[] offset, int size, byte[] value) {
            if (readInputBacking != null) {
                model.setMemory(offset(offset), readInputBacking);
                readInputBacking = null;
            }
            if (space.equals(language.getDefaultSpace())) {
                long address = offset(offset);
                model.adc.readCompleted(thread, address, size);
                model.rsent.readCompleted(thread, address, size);
            }
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
            if ("prepare".equals(instruction.getMnemonicString())) {
                model.clearPreparedFrame(thread, instruction);
            }
            if (icctrlWrite) model.completeInstructionCacheClear(thread);
            model.trace.instructions++;
            model.trace.executed.add(instruction.getAddress().getOffset());
            model.noteBoundedCall(thread, instruction);
            model.trace.recentPcs.add(instruction.getAddress().getOffset());
            if (model.trace.recentPcs.size() > 16) model.trace.recentPcs.remove(0);
            if (model.hsbCyclesPerInstruction != 0)
                model.advanceClock(thread, model.hsbCyclesPerInstruction);
            model.dispatchDueEvents();
            model.deliverSystemError(thread);
        }

        @Override
        public <A, U> AddressSetView readUninitialized(PcodeThread<byte[]> thread,
                PcodeExecutorStatePiece<A, U> piece, AddressSetView set, Reason reason) {
            Address reinitAddress = set.getMinAddress();
            // The decoder buffers ahead. Returning the unchanged set lets the
            // byte state expose only its initialized prefix, without filling RAM.
            // The complete decoded instruction is checked again before execution.
            if (reason == Reason.EXECUTE_DECODE && reinitAddress != null
                    && reinitAddress.getAddressSpace().equals(model.memorySpace)) {
                return set;
            }
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
            if (model.peripheralFile && reason != Reason.INSPECT && reinitAddress != null
                    && reinitAddress.getAddressSpace().equals(model.memorySpace)) {
                boolean outside = set.getNumAddresses() > 0;
                for (AddressRange range : set.getAddressRanges()) {
                    long rangeLength = range.getLength();
                    if (rangeLength <= 0 || rangeLength > 4096
                            || model.region(range.getMinAddress().getOffset(), (int) rangeLength) != null) {
                        outside = false;
                        break;
                    }
                }
                if (outside) {
                    PcodeExecutorStatePiece<A, byte[]> concrete =
                        PcodeStateCallbacks.checkValueDomain(piece, byte[].class);
                    if (concrete == null) {
                        throw new IllegalStateException(
                            "RH850 machine requires concrete memory state");
                    }
                    for (AddressRange range : set.getAddressRanges()) {
                        int rangeLength = (int) range.getLength();
                        concrete.setVar(range.getMinAddress(), rangeLength, false, new byte[rangeLength]);
                    }
                    return set;
                }
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
            EntrySelector selector, byte[] codeflash, long imageBase,
            Model model, PcodeThread<byte[]> thread, Scenario scenario) throws Exception {
        if (selector == null || selector.role == null || selector.role.isBlank()) {
            throw new IllegalArgumentException("entry selector is incomplete");
        }
        if ("resolved-address".equals(selector.scope)) {
            if (selector.address == null) {
                throw new IllegalArgumentException("resolved entry selector has no address");
            }
            long resolved = parseUnsigned(selector.address);
            if (resolved < imageBase || resolved >= imageBase + codeflash.length) {
                RegionDef region = model.region(resolved, 2);
                int available = 0;
                for (MemoryInit init : scenario.memory) {
                    long base = parseUnsigned(init.address);
                    int size = init.hex == null ? init.size : parseHex(init.hex).length;
                    if (resolved >= base && resolved < base + size) {
                        available = init.hex == null ? 0 : (int) Math.min(16, base + size - resolved);
                    }
                }
                if (region == null || !region.executable || !"rw".equals(region.access)
                        || available < 2) {
                    throw new IllegalArgumentException(
                        "resolved entry lacks initialized executable RAM: " + hex32(resolved));
                }
                byte[] window = model.memory(thread, resolved, available);
                SleighLanguage language = (SleighLanguage) currentProgram.getLanguage();
                InstructionPrototype prototype = language.parse(
                    new ByteMemBufferImpl(language.getDefaultSpace().getAddress(resolved),
                        window, language.isBigEndian()),
                    new ProcessorContextImpl(language), false);
                int length = prototype.getLength();
                if (length > available || model.region(resolved, length) != region) {
                    throw new IllegalArgumentException(
                        "resolved RAM entry instruction leaves initialized region: " + hex32(resolved));
                }
                String instructionHash = sha256(Arrays.copyOf(window, length));
                JsonObject proof = new JsonObject();
                proof.addProperty("role", selector.role);
                proof.addProperty("scope", selector.scope);
                proof.addProperty("source", "scenario-initialized executable RAM");
                proof.addProperty("candidate_count", 1);
                proof.addProperty("base_address", hex32(resolved));
                proof.addProperty("offset", 0);
                proof.addProperty("resolved_address", hex32(resolved));
                proof.addProperty("matched_code_sha256", instructionHash);
                proof.addProperty("entry_instruction_sha256", instructionHash);
                return new ResolvedEntry(resolved, proof);
            }
            int offset = Math.toIntExact(resolved - imageBase);
            int length = entryInstructionLength(codeflash, imageBase, resolved);
            String instructionHash = sha256(Arrays.copyOfRange(
                codeflash, offset, offset + length));
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
        int bodyOffset = Math.toIntExact(match.address - imageBase);
        int entryOffset = Math.toIntExact(resolved - imageBase);
        int entryLength = entryInstructionLength(codeflash, imageBase, resolved);
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
            codeflash, entryOffset, entryOffset + entryLength)));
        return new ResolvedEntry(resolved, proof);
    }

    private int entryInstructionLength(byte[] codeflash, long imageBase, long resolved)
            throws Exception {
        Address address = currentProgram.getLanguage().getDefaultSpace().getAddress(resolved);
        try {
            Instruction instruction = currentProgram.getListing().getInstructionAt(address);
            if (instruction != null) {
                return instruction.getLength();
            }
        }
        catch (DomainObjectException exc) {
        }
        SleighLanguage language = (SleighLanguage) currentProgram.getLanguage();
        int offset = Math.toIntExact(resolved - imageBase);
        int window = Math.min(16, codeflash.length - offset);
        if (window <= 0) {
            throw new IllegalArgumentException(
                "resolved entry leaves CodeFlash: " + hex32(resolved));
        }
        byte[] bytes = Arrays.copyOfRange(codeflash, offset, offset + window);
        InstructionPrototype prototype = language.parse(
            new ByteMemBufferImpl(address, bytes, language.isBigEndian()),
            new ProcessorContextImpl(language),
            false);
        return prototype.getLength();
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
                model.scenarioFills.add(new long[] {
                    address, address + init.size, init.fill & 0xff
                });
            }
            model.initializeMemory(address, value, init.evidence);
        }
    }

    private void initializeScenario(Model model, PcodeThread<byte[]> thread,
                                    SleighLanguage language, Scenario scenario) throws Exception {
        for (Map.Entry<String, String> row : scenario.registers.entrySet()) {
            setRegister(thread, language, row.getKey(), parseUnsigned(row.getValue()));
        }
        if (scenario.registers.containsKey("sp")) {
            model.entrySp = parseUnsigned(scenario.registers.get("sp"));
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
                    case "memory-equal": {
                        if (check.size == null || check.size <= 0) {
                            throw new IllegalArgumentException("memory-equal check requires positive size");
                        }
                        byte[] value = model.emulator.getSharedState().getVar(model.memorySpace,
                            parseUnsigned(check.address), check.size, true, Reason.INSPECT);
                        byte[] source = model.emulator.getSharedState().getVar(model.memorySpace,
                            parseUnsigned(check.source_address), check.size, true, Reason.INSPECT);
                        passed = java.util.Arrays.equals(value, source);
                        expected = "equal";
                        actual = passed ? "equal" : "different";
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
                        long count = model.trace.deviceEvents.countKind(check.operation);
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
        report.addProperty("stubbed_execution", scenario.stubbed());
        report.add("entry_resolution", resolution);
        JsonObject resolvedContract = new JsonObject();
        resolvedContract.add("entry", resolution.deepCopy());
        resolvedContract.add("stop_addresses", GSON.toJsonTree(scenario.stop_addresses));
        resolvedContract.addProperty("max_instructions", scenario.max_instructions);
        resolvedContract.addProperty("hsb_cycles_per_instruction", scenario.hsb_cycles_per_instruction);
        resolvedContract.addProperty("expected_termination", scenario.expected_termination);
        resolvedContract.addProperty("reset", scenario.reset);
        resolvedContract.add("events", GSON.toJsonTree(scenario.events));
        if (scenario.icus_startup_stub != null)
            resolvedContract.add("icus_startup_stub", GSON.toJsonTree(scenario.icus_startup_stub));
        if (scenario.dma_master_rewrite_assumption != null)
            resolvedContract.addProperty("dma_master_rewrite_assumption", scenario.dma_master_rewrite_assumption);
        report.add("resolved_run_contract", resolvedContract);
        report.addProperty("instruction_count", trace.instructions);
        report.addProperty("unique_instruction_addresses", trace.executed.size());
        JsonArray recent = new JsonArray();
        for (long pc : trace.recentPcs) recent.add(hex32(pc));
        report.add("recent_pcs", recent);
        report.add("sync_counts", GSON.toJsonTree(trace.syncCounts));
        report.addProperty("trace_lost_address", trace.traceLostAddress);
        if (trace.instructionTraceEnabled) {
            report.addProperty("instruction_trace_semantics",
                "entered instructions in callback order; instruction is the retired count before "
                + "entry (terminal fault/halt may not retire); modeled shortcuts do not retire "
                + "or synthesize instructions and appear separately in instruction_trace_shortcuts");
        }
        return report;
    }

    private JsonObject runScenario(
            RunContract contract, MachineSpec machineSpec, SleighLanguage language,
            Scenario scenario, byte[] codeflash, byte[] dataflash, Trace trace) throws Exception {
        if (scenario.hsb_cycles_per_instruction != null && scenario.hsb_cycles_per_instruction <= 0)
            throw new IllegalArgumentException("hsb_cycles_per_instruction must be positive");
        Model model = new Model(language, machineSpec, trace, contract.target.mcu);
        model.hsbCyclesPerInstruction = scenario.hsb_cycles_per_instruction == null
            ? 0 : scenario.hsb_cycles_per_instruction;
        model.peripheralFile = scenario.peripheral_file;
        Callbacks callbacks = new Callbacks(language, model);
        PcodeEmulator emulator = new PcodeEmulator(language, callbacks) {
            @Override
            protected PcodeExecutorState<byte[]> createSharedState() {
                return new BytesPcodeExecutorState(language, callbacks.wrapFor(null)) {
                    @Override
                    public void setVar(AddressSpace space, byte[] offset, int size,
                                       boolean quantize, byte[] value) {
                        // A failed transaction retires STORE's instruction,
                        // without ever turning the target into backing storage.
                        if (model.discardBusStore && !model.internalWrite
                                && space.equals(language.getDefaultSpace())) return;
                        super.setVar(space, offset, size, quantize, value);
                    }
                };
            }
            @Override
            protected PcodeUseropLibrary<byte[]> createUseropLibrary() {
                return new Rh850Userops();
            }
        };
        model.attach(emulator);
        if (scenario.icus_startup_stub != null)
            model.icusStartupStub = model.new IcusStartupStub(scenario.icus_startup_stub);
        model.dma.masterRewriteAssumption = scenario.dma_master_rewrite_assumption;
        PcodeThread<byte[]> thread = emulator.newThread("PE1");
        model.executionThread = thread;
        model.initializeProcessorReset(thread);
        model.setMemory(parseUnsigned(contract.target.codeflash.base), codeflash);
        if (contract.target.dataflash != null) {
            model.setMemory(parseUnsigned(contract.target.dataflash.base), dataflash);
        }
        model.initializeDataFlashCells(scenario.dataflash_cells);
        model.initializeResetRegisters();
        initializeMemoryRows(model, scenario.pre_reset_memory);
        model.applyReset(scenario.reset);
        initializeScenario(model, thread, language, scenario);
        model.adc.initializeClock();
        model.taud.reset();
        model.tauj.loadRegisters();
        model.tsg.initializeFromDeclaredState(thread, model.declaredTsgRegisters);
        model.rsent.loadInitialState(thread);
        model.dma.schedule(thread);
        ResolvedEntry resolved = resolveEntry(
            scenario.entry, codeflash, parseUnsigned(contract.target.codeflash.base),
            model, thread, scenario);

        model.configureExternalEvents(thread, scenario.events);
        thread.overrideCounter(language.getDefaultSpace().getAddress(resolved.address));
        thread.overrideContextWithDefault();
        Set<Long> stops = new HashSet<>();
        for (String value : scenario.stop_addresses) stops.add(parseUnsigned(value));
        if (scenario.bounded_entries != null) {
            for (String value : scenario.bounded_entries) {
                model.boundedEntries.add(parseUnsigned(value));
            }
        }
        if (scenario.bounded_edges != null) {
            for (BoundedEdge edge : scenario.bounded_edges) {
                model.boundedEdges.put(parseUnsigned(edge.pc), new long[] {
                    parseUnsigned(edge.target), parseUnsigned(edge.entry),
                });
            }
        }
        model.scenarioEntry = resolved.address;

        MachineFault fault = null;
        MachineHalt halt = null;
        try {
            while (trace.instructions < scenario.max_instructions
                    && !stops.contains(thread.getCounter().getOffset())) {
                if (model.returnBoundedCallee(thread)) continue;
                model.dispatchDueEvents();
                model.dispatchExternalEvents();
                model.deliverInterrupt(thread);
                model.completeCountedDelay(thread);
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

        model.taud.flush();
        model.tauj.flush();
        model.tsg.flushSnapshot();
        model.rsent.flush();
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
            termination = fault != null ? "unexpected-fault"
                : halt != null ? "halt"
                : atStop ? "stop-address"
                : trace.instructions >= scenario.max_instructions ? "instruction-budget"
                : "incomplete";
            boolean expectedTermination = scenario.expected_termination == null
                ? completed : scenario.expected_termination.equals(termination);
            passed = fault == null && expectedTermination && checksPassed;
        }
        report.addProperty("termination_reason", termination);
        report.addProperty("passed", passed);
        report.addProperty("status",
            passed && scenario.expected_fault != null
                ? "verified-expected-fault"
                : !passed ? "failed"
                : scenario.stubbed()
                    ? "verified-stubbed-execution" : "verified-local-execution");
        report.addProperty("evidence_boundary", scenario.stubbed()
            ? "exact firmware bytes with explicit peripheral assumptions recorded in resolved_run_contract; no ICU-S hardware, cryptography, authentication, silicon or vehicle claim"
            : "exact firmware bytes plus explicit manual/recovered model rules; no silicon or vehicle claim");
        return report;
    }

    private void validateScenarioJson(JsonObject scenarioJson) {
        requireKeys(scenarioJson, Set.of("schema", "name", "entry", "max_instructions",
            "stop_addresses", "registers", "memory", "pre_reset_memory", "artifacts", "checks",
            "expected_fault", "expected_termination", "reset", "events", "peripheral_file",
            "bounded_entries", "bounded_edges", "hsb_cycles_per_instruction", "dataflash_cells",
            "icus_startup_stub", "dma_master_rewrite_assumption"), "scenario");
        JsonElement stub = scenarioJson.get("icus_startup_stub");
        if (stub != null && !stub.isJsonNull()) {
            JsonObject config = stub.getAsJsonObject();
            requireKeys(config, Set.of("evidence", "responses"), "ICU-S startup stub");
            for (JsonElement response : config.getAsJsonArray("responses"))
                requireKeys(response.getAsJsonObject(),
                    Set.of("command", "error_bits", "completion_hsb_cycles"), "ICU-S startup response");
        }
        JsonElement rewrite = scenarioJson.get("dma_master_rewrite_assumption");
        if (rewrite != null && !rewrite.isJsonNull()
                && (!rewrite.isJsonPrimitive() || !rewrite.getAsJsonPrimitive().isString()
                    || rewrite.getAsString().isBlank()))
            throw new IllegalArgumentException("DMA master rewrite requires a nonempty assumption string");
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

    private void writeBatchReport(Path path, JsonObject batch, List<Trace> traces) throws Exception {
        try (BufferedWriter output = Files.newBufferedWriter(path, StandardCharsets.UTF_8);
                JsonWriter writer = new JsonWriter(output)) {
            writer.setIndent("  ");
            writer.beginObject();
            for (Map.Entry<String, JsonElement> field : batch.entrySet()) {
                writer.name(field.getKey());
                if (!"reports".equals(field.getKey())) {
                    GSON.toJson(field.getValue(), writer);
                    continue;
                }
                writer.beginArray();
                JsonArray reports = field.getValue().getAsJsonArray();
                for (int index = 0; index < reports.size(); index++) {
                    writer.beginObject();
                    for (Map.Entry<String, JsonElement> reportField :
                            reports.get(index).getAsJsonObject().entrySet()) {
                        writer.name(reportField.getKey());
                        GSON.toJson(reportField.getValue(), writer);
                    }
                    Trace trace = traces.get(index);
                    if (!"runner-error".equals(reports.get(index).getAsJsonObject()
                            .get("termination_reason").getAsString())) {
                        writer.name("memory_accesses");
                        trace.memoryAccesses.writeTo(writer);
                        writer.name("device_events");
                        trace.deviceEvents.writeTo(writer);
                        if (trace.instructionTraceEnabled) {
                            writer.name("instruction_trace_shortcuts");
                            GSON.toJson(trace.instructionShortcuts, List.class, writer);
                            writer.name("instruction_trace");
                            trace.writeInstructionTrace(writer);
                        }
                    }
                    writer.endObject();
                }
                writer.endArray();
            }
            writer.endObject();
            writer.flush();
            output.newLine();
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2 || args.length > 3
                || (args.length == 3 && !"--instruction-trace".equals(args[2]))) {
            throw new IllegalArgumentException(
                "expected contract JSON and report JSON paths [--instruction-trace]");
        }
        boolean instructionTraceEnabled = args.length == 3;
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
        List<Trace> traces = new ArrayList<>();
        boolean passed = true;
        Files.createDirectories(reportPath.getParent());
        try (Closeable cleanup = () -> {
            IOException failure = null;
            for (Trace trace : traces) {
                try { trace.close(); }
                catch (IOException exception) {
                    if (failure == null) failure = exception;
                    else failure.addSuppressed(exception);
                }
            }
            if (failure != null) throw failure;
        }) {
            for (Scenario scenario : contract.scenarios) {
                JsonObject report;
                Trace trace = new Trace(instructionTraceEnabled, reportPath.getParent());
                traces.add(trace);
                try {
                    report = runScenario(
                        contract, machineSpec, language, scenario, codeflash, dataflash, trace);
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
            writeBatchReport(reportPath, batch, traces);
            println("P1ME_MACHINE_REPORT=" + reportPath);
            println("P1ME_MACHINE_RESULT=" + (passed ? "PASS" : "FAIL"));
            if (!passed) throw new IllegalStateException("P1M-E machine batch failed; see " + reportPath);
        }
    }
}
