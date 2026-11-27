//@author kaikozlov
//@category Emulation
// Execute exact registered RH850/P1M-E firmware with strict machine-state provenance.
// Args: <absolute-run-contract-json> <absolute-report-json> [--instruction-trace]
//       [--report-outputs <absolute-staging-plan-json>]

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonIOException;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;
import com.google.gson.stream.JsonWriter;
import ghidra.app.plugin.processors.sleigh.SleighLanguage;
import ghidra.generic.util.datastruct.SemisparseByteArray;
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
import ghidra.pcode.exec.BytesPcodeExecutorStatePiece;
import ghidra.pcode.exec.BytesPcodeExecutorStateSpace;
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
import ghidra.program.model.lang.Language;
import ghidra.program.model.lang.ProcessorContextImpl;
import ghidra.program.model.lang.Register;
import ghidra.program.model.lang.RegisterValue;
import ghidra.program.model.mem.ByteMemBufferImpl;
import ghidra.program.model.mem.MemoryAccessException;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;
import ghidra.util.exception.CancelledException;
import java.io.BufferedOutputStream;
import java.io.BufferedWriter;
import java.io.Closeable;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.lang.foreign.MemorySegment;
import java.nio.ByteBuffer;
import java.nio.channels.Channels;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.lang.reflect.Field;
import java.lang.reflect.Modifier;
import java.lang.reflect.Array;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.BitSet;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.PriorityQueue;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.function.Consumer;

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
        transient boolean directPageWrites;
        transient boolean templateRam, templateReads, templateWrites;
        transient RegionDef templateMirror;
        transient long lookupEnd;

        boolean contains(long address, int width) {
            long end = address + Integer.toUnsignedLong(width);
            return Long.compareUnsigned(address, start) >= 0
                && Long.compareUnsigned(end, end_exclusive) <= 0;
        }
    }

    private enum WriteDevice {
        TAUJ, TAUD, PIC_TAUD, TSG, PIC_TSG, PIC1_START, PDMA, ADC, RSENT, CSIH,
        SEG, PEG, BUS_GUARD, GRAM_GUARD, PERIPHERAL_ECC, CVM, ECM, PORT_CONFIG,
        NOISE_FILTER, INTC_EIC, IPG, GRAM_BUFFER, FLMD, DCRA, NONE;

        static WriteDevice bind(String behavior) {
            return switch (behavior == null ? "" : behavior) {
                case "tauj" -> TAUJ;
                case "taud" -> TAUD;
                case "pic-taud" -> PIC_TAUD;
                case "tsg" -> TSG;
                case "pic-tsg" -> PIC_TSG;
                case "pic1-start" -> PIC1_START;
                case "pdma" -> PDMA;
                case "adc", "adc-clock" -> ADC;
                case "rsent" -> RSENT;
                case "csih" -> CSIH;
                case "seg" -> SEG;
                case "peg" -> PEG;
                case "bus-guard" -> BUS_GUARD;
                case "gram-guard" -> GRAM_GUARD;
                case "peripheral-ecc" -> PERIPHERAL_ECC;
                case "cvm" -> CVM;
                case "ecm" -> ECM;
                case "port-config" -> PORT_CONFIG;
                case "noise-filter" -> NOISE_FILTER;
                case "intc_eic" -> INTC_EIC;
                case "ipg" -> IPG;
                case "gram-buffer" -> GRAM_BUFFER;
                case "flmd" -> FLMD;
                case "dcra" -> DCRA;
                default -> NONE;
            };
        }
    }

    private enum WriteTrigger {
        DMA_SELECT, TX, TX_HALF, PEG_MASK, GUARD_ERROR_CLEAR, PDMA_COMPARATOR,
        RESET_FACTOR_CLEAR, PORT_MASKED_ALIAS, NOISE_CLOCK_SELECTOR, NOISE_FILTER_ENABLE,
        PERIPHERAL_ECC_CONTROL, PERIPHERAL_ECC_TEST, BANKED_ECC_CLEAR, ECC_NOTIFICATION,
        ECC_PROTECTED_CONTROL, CLOCK_DIVIDER, CLOCK_SELECTOR, FLMD_COMMAND, FLMD_CONTROL,
        BIST_CONTROL, DCRA_CONTROL, DCRA_SEED, DCRA_INPUT, RSCFD_TRANSMIT,
        RSCFD_TRANSMIT_STATUS, RSCFD_GLOBAL_CONTROL, RSCFD_CHANNEL_CONTROL,
        RSCFD_FD_COUNTER_CLEAR, RSCFD_FD_STATUS, FACI_COMMAND, FACI_ACCESS_STATUS,
        FACI_SETUP_INITIALIZE, FACI_AREA_SELECTOR, FACI_CLOCK_NOTIFY, FACI_ADDRESS,
        FACI_DATAFLASH_MODE, FACI_NORMAL_EMULATION, FACI_ENABLE, DATAFLASH_READ_CYCLE,
        ICUS_COMMAND, ICUS_CONTROL, NONE, OTHER;

        static WriteTrigger bind(String trigger) {
            if (trigger == null) return NONE;
            return switch (trigger) {
                case "dma-select" -> DMA_SELECT;
                case "tx" -> TX;
                case "tx-half" -> TX_HALF;
                case "peg-mask" -> PEG_MASK;
                case "guard-error-clear" -> GUARD_ERROR_CLEAR;
                case "pdma-comparator" -> PDMA_COMPARATOR;
                case "reset-factor-clear" -> RESET_FACTOR_CLEAR;
                case "port-masked-alias" -> PORT_MASKED_ALIAS;
                case "noise-clock-selector" -> NOISE_CLOCK_SELECTOR;
                case "noise-filter-enable" -> NOISE_FILTER_ENABLE;
                case "peripheral-ecc-control" -> PERIPHERAL_ECC_CONTROL;
                case "peripheral-ecc-test" -> PERIPHERAL_ECC_TEST;
                case "banked-ecc-clear" -> BANKED_ECC_CLEAR;
                case "ecc-notification" -> ECC_NOTIFICATION;
                case "ecc-protected-control" -> ECC_PROTECTED_CONTROL;
                case "clock-divider" -> CLOCK_DIVIDER;
                case "clock-selector" -> CLOCK_SELECTOR;
                case "flmd-command" -> FLMD_COMMAND;
                case "flmd-control" -> FLMD_CONTROL;
                case "bist-control" -> BIST_CONTROL;
                case "dcra-control" -> DCRA_CONTROL;
                case "dcra-seed" -> DCRA_SEED;
                case "dcra-input" -> DCRA_INPUT;
                case "rscfd-transmit" -> RSCFD_TRANSMIT;
                case "rscfd-transmit-status" -> RSCFD_TRANSMIT_STATUS;
                case "rscfd-global-control" -> RSCFD_GLOBAL_CONTROL;
                case "rscfd-channel-control" -> RSCFD_CHANNEL_CONTROL;
                case "rscfd-fd-counter-clear" -> RSCFD_FD_COUNTER_CLEAR;
                case "rscfd-fd-status" -> RSCFD_FD_STATUS;
                case "faci-command" -> FACI_COMMAND;
                case "faci-access-status" -> FACI_ACCESS_STATUS;
                case "faci-setup-initialize" -> FACI_SETUP_INITIALIZE;
                case "faci-area-selector" -> FACI_AREA_SELECTOR;
                case "faci-clock-notify" -> FACI_CLOCK_NOTIFY;
                case "faci-address" -> FACI_ADDRESS;
                case "faci-dataflash-mode" -> FACI_DATAFLASH_MODE;
                case "faci-normal-emulation" -> FACI_NORMAL_EMULATION;
                case "faci-enable" -> FACI_ENABLE;
                case "dataflash-read-cycle" -> DATAFLASH_READ_CYCLE;
                case "icus-command" -> ICUS_COMMAND;
                case "icus-control" -> ICUS_CONTROL;
                default -> OTHER;
            };
        }
    }

    static final class RegisterDef {
        String name;
        long address;
        int size;
        transient int bindingIndex;
        transient RegisterDef nameBinding, guardLockBinding;
        transient int pendingBinding;
        transient long lookupEnd;
        transient JsonRows.RegisterWriteFields writeFields;
        transient boolean changesClockSchedule;
        transient WriteDevice writeDevice;
        transient WriteTrigger writeTrigger;
        transient boolean validateBusWrite, snapshotWriteBacking, busWritable, completesBusWrite;
        transient boolean fifoBusWrite;
        transient Model.Csih.Word csihWriteWord;
        transient String csihSuffix;
        transient int busReadEffects;
        transient byte busReadCompletion;
        transient short busWidths;
        transient boolean busReadable, passiveBusRead, plainEicRead;
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

        // Bus ownership has already tested contains at this address and width.
        boolean allowsOwnedBusAccess(long candidate, int width) {
            if (busWidths >= 0 && width > 0 && width <= Long.BYTES && (width & (width - 1)) == 0) {
                return (busWidths & (1 << width)) != 0
                    && ((candidate - address) & (width - 1)) == 0;
            }
            return access_widths.contains(width) && Long.remainderUnsigned(candidate - address, width) == 0;
        }

        boolean permitsBusRead() {
            return busReadable || access.contains("r");
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
        // Set on the rows of `reset_replay`; never read from scenario JSON.
        boolean replayedAfterReset;
        String kind;
        Long after_instructions;
        Long after_transmit_words;
        Long delay_instructions;
        Long repeat;
        Long stride_words;
        boolean repeat_forever;
        Long after_spc_triggers;
        Long after_reset_instructions;
        Long delay_hsb_cycles;
        int[] pulse_samples;
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
        Integer buffer;
        Integer unit;
        String firmware_control;
        String can_id;
        String data_hex;
        boolean extended;
        boolean fd;
        String boundary;
        int label;
        int timestamp;
        boolean tolerate_no_pending;
        Long socket_poll_instruction;
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

    static final class ResetReplay {
        String scenario;
        List<MemoryInit> memory = new ArrayList<>();
        List<ExternalEvent> events = new ArrayList<>();
        Long hsb_cycles_per_instruction;
        List<FlashCellRange> dataflash_cells = new ArrayList<>();
        IcusStartupConfig icus_startup_stub;
        String dma_master_rewrite_assumption;
    }

    static final class EventSocketConfig {
        String host;
        int port;
        String ready_address;
        StopArrival ready_after_arrivals;
        boolean hold_when_ready;
    }

    static final class SnapshotOutput {
        String path;
        String address;
        int size;
        String evidence;
    }



    static final class Scenario {
        String schema;
        String name;
        JsonObject source;
        EntrySelector entry;
        long max_instructions;
        String engine = "jit";
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
        boolean compare_operands;
        boolean input_derived_table_indices;
        ResetReplay reset_replay;
        EventSocketConfig event_socket;
        List<SnapshotOutput> snapshot_outputs = new ArrayList<>();
        String instruction_trace_start_step;
        List<ScenarioStep> steps = new ArrayList<>();

        boolean stubbed() {
            return icus_startup_stub != null || dma_master_rewrite_assumption != null;
        }
    }

    static final class StopArrival {
        String address;
        long count;
    }

    static final class ScenarioStep {
        String kind;
        String name;
        String checkpoint;
        Long after_instructions;
        long max_instructions;
        List<String> stop_addresses = new ArrayList<>();
        List<StopArrival> stop_after_arrivals = new ArrayList<>();
        List<ExternalEvent> events = new ArrayList<>();
        List<CheckDef> checks = new ArrayList<>();
        Boolean capture_rows;
        List<String> capture_event_kinds;
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
        final FileChannel spool;
        final Utf8JsonWriter writer;
        final Map<String, long[]> kindCounts;
        long count;
        boolean sealed;
        record Span(long start, long end) {}
        private final List<Span> trials = new ArrayList<>();
        private long trialStart = -1;
        Consumer<JsonObject> listener;
        boolean discard;
        private Set<String> projectedKinds;
        private Map<String, Long> trialKindBaseline;
        private boolean includesAlias = true;
        private String lastCountedKind;
        private long[] lastKindCounter;
        private final EventRow event = new EventRow();

        private record EventKind(String name, byte[] head) {
            EventKind(String name) {
                this(name, Utf8JsonWriter.encodeTextField("kind", name, true));
            }
        }

        private record EventField(String name, byte[] prefix) {
            EventField(String name) {
                this(name, Utf8JsonWriter.encodeNamePrefix(name, false));
            }
        }

        private record EventText(EventField field, String value, byte[] encoded) {
            EventText(EventField field, String value) {
                this(field, value, value == null ? null :
                    Utf8JsonWriter.encodeTextField(field.name, value, false));
            }
        }

        private static final String ALIAS_WRITE = "alias-write";
        private static final String INTERRUPT_REQUEST = "interrupt-request";
        private static final EventKind REGISTER_WRITE = new EventKind("register-write");
        private static final EventKind CSIH_TX = new EventKind("csih-tx");
        private static final EventKind CSIH_FRAME = new EventKind("csih-frame");
        private static final EventKind CSIH_WORD = new EventKind("csih-word");
        private static final EventKind DMA_TRANSFER = new EventKind("dma-transfer");
        private static final EventField PC = new EventField("pc");
        private static final EventField REGISTER = new EventField("register");
        private static final EventField BEHAVIOR = new EventField("behavior");
        private static final EventField TRIGGER = new EventField("trigger");
        private static final EventField VALUE = new EventField("value");
        private static final EventField EVIDENCE = new EventField("evidence");
        private static final EventField INITIATOR = new EventField("initiator");
        private static final EventField UNIT = new EventField("unit");
        private static final EventField SCHEDULER_TICK = new EventField("scheduler_tick");
        private static final EventField WORD = new EventField("word");
        private static final EventField CHIP_SELECT = new EventField("chip_select");
        private static final EventField BITS = new EventField("bits");
        private static final EventField LSB_FIRST = new EventField("lsb_first");
        private static final EventField TRANSMIT_ORDINAL = new EventField("transmit_ordinal");
        private static final EventField WORDS = new EventField("words");
        private static final EventField INPUT_EVIDENCE = new EventField("input_evidence");
        private static final EventField CHANNEL = new EventField("channel");
        private static final EventField SOURCE = new EventField("source");
        private static final EventField DESTINATION = new EventField("destination");
        private static final EventField SIZE = new EventField("size");
        private static final EventField REMAINING = new EventField("remaining");
        private static final EventField ERROR = new EventField("error");
        private static final EventField HSB_CYCLES = new EventField("hsb_cycles");
        private static final EventText CSIH_EVIDENCE =
            new EventText(EVIDENCE, "R01UH0585EJ0120 section14.3-14.5");
        private static final EventText DMA_EVIDENCE =
            new EventText(EVIDENCE, "R01UH0585EJ0120 Section7");

        // Register metadata is immutable once the device model is constructed.
        private record RegisterWriteFields(EventText name, EventText behavior, EventText trigger,
                EventText evidence) {
            RegisterWriteFields(RegisterDef register) {
                this(new EventText(REGISTER, register.name), new EventText(BEHAVIOR, register.behavior),
                    new EventText(TRIGGER, register.trigger), new EventText(EVIDENCE, register.evidence));
            }
        }

        private final class EventRow {
            private JsonObject tree;

            void begin(EventKind kind) throws IOException {
                if (listener != null) {
                    tree = new JsonObject();
                    tree.addProperty("kind", kind.name);
                    return;
                }
                tree = null;
                requireOpen();
                writer.beforeRow();
                writer.output.write(kind.head);
            }

            void text(EventField field, String value) throws IOException {
                if (tree != null) tree.addProperty(field.name, value);
                else if (value != null) {
                    writer.output.write(field.prefix);
                    writer.writeString(value);
                }
            }

            void text(EventText text) throws IOException {
                if (tree != null) tree.addProperty(text.field.name, text.value);
                else if (text.encoded != null) writer.output.write(text.encoded);
            }

            void hex(EventField field, long value) throws IOException {
                if (tree != null) tree.addProperty(field.name, hex32(value));
                else {
                    writer.output.write(field.prefix);
                    writer.writeHexValue(value);
                }
            }

            void number(EventField field, int value) throws IOException {
                if (tree != null) tree.addProperty(field.name, value);
                else writeNumber(field, value);
            }

            void number(EventField field, long value) throws IOException {
                if (tree != null) tree.addProperty(field.name, value);
                else writeNumber(field, value);
            }

            private void writeNumber(EventField field, long value) throws IOException {
                writer.output.write(field.prefix);
                writer.writeLong(value);
            }

            void bool(EventField field, boolean value) throws IOException {
                if (tree != null) tree.addProperty(field.name, value);
                else {
                    writer.output.write(field.prefix);
                    writer.output.write(value ? Utf8JsonWriter.TRUE : Utf8JsonWriter.FALSE);
                }
            }

            void numbers(EventField field, List<Long> values) throws IOException {
                if (tree != null) {
                    tree.add(field.name, GSON.toJsonTree(values));
                    return;
                }
                writer.output.write(field.prefix);
                writer.output.write('[');
                for (int i = 0; i < values.size(); i++) {
                    if (i != 0) writer.output.write(',');
                    Long value = values.get(i);
                    if (value == null) writer.output.write(Utf8JsonWriter.NULL);
                    else writer.writeLong(value);
                }
                writer.output.write(']');
            }

            void end(EventKind kind) throws IOException {
                if (tree != null) {
                    JsonObject row = tree;
                    tree = null;
                    add(row, kind.name, spoolsKind(kind.name));
                }
                else {
                    writer.output.write('}');
                    finishRow(null, kind.name, true);
                }
            }
        }

        /**
         * Minimal tree writer for the trace spool. Gson's JsonWriter formats through UTF-16
         * Writers; trace rows are already trees, so encoding directly into a byte buffer avoids
         * that conversion and lets the report splice the same bytes without rebuilding them.
         */
        private static final class Utf8JsonWriter implements Closeable {
            private static final byte[] ALIAS_PREFIX =
                "{\"kind\":\"alias-write\",\"from\":\"0x".getBytes(StandardCharsets.US_ASCII);
            private static final byte[] ALIAS_MIDDLE =
                "\",\"to\":\"0x".getBytes(StandardCharsets.US_ASCII);
            private static final byte[] ALIAS_SIZE =
                "\",\"size\":".getBytes(StandardCharsets.US_ASCII);
            private static final byte[] LONG_MIN =
                "-9223372036854775808".getBytes(StandardCharsets.US_ASCII);
            private static final byte[] TRUE = {'t', 'r', 'u', 'e'};
            private static final byte[] FALSE = {'f', 'a', 'l', 's', 'e'};
            private static final byte[] NULL = {'n', 'u', 'l', 'l'};
            private static final byte[] HEX = "0123456789abcdef".getBytes(StandardCharsets.US_ASCII);
            private static final byte[] ADDRESS_HEX =
                "0123456789ABCDEF".getBytes(StandardCharsets.US_ASCII);

            private static final class ByteSink implements Closeable {
                private final FileChannel channel;
                private final byte[] bytes = new byte[1048576];
                private final ByteBuffer transfer = ByteBuffer.wrap(bytes);
                private int size;

                ByteSink(FileChannel channel) {
                    this.channel = channel;
                }

                int remaining() {
                    return bytes.length - size;
                }

                void write(int value) throws IOException {
                    if (size == bytes.length) flush();
                    bytes[size++] = (byte) value;
                }

                void write(byte[] source) throws IOException {
                    write(source, 0, source.length);
                }

                void write(byte[] source, int offset, int length) throws IOException {
                    while (length != 0) {
                        if (size == bytes.length) flush();
                        int copied = Math.min(length, bytes.length - size);
                        System.arraycopy(source, offset, bytes, size, copied);
                        size += copied;
                        offset += copied;
                        length -= copied;
                    }
                }
                void writeAscii(String source, int start, int end) throws IOException {
                    while (start < end) {
                        if (size == bytes.length) flush();
                        int copied = Math.min(end - start, bytes.length - size);
                        for (int i = 0; i < copied; i++)
                            bytes[size + i] = (byte) source.charAt(start + i);
                        size += copied;
                        start += copied;
                    }
                }

                void flush() throws IOException {
                    transfer.clear();
                    transfer.limit(size);
                    while (transfer.hasRemaining()) channel.write(transfer);
                    size = 0;
                }

                @Override
                public void close() throws IOException {
                    try { flush(); }
                    finally { channel.close(); }
                }
            }
            private static final class RowSchema {
                final String[] names;
                final boolean[] omitted;
                final byte[][] prefixes;
                final String[] constantStrings;
                final byte[][] constantValues;
                final String[] lastStrings;
                final byte[][] lastStringValues;

                RowSchema(JsonObject row) {
                    names = new String[row.size()];
                    omitted = new boolean[names.length];
                    prefixes = new byte[names.length][];
                    constantStrings = new String[names.length];
                    constantValues = new byte[names.length][];
                    lastStrings = new String[names.length];
                    lastStringValues = new byte[names.length][];
                    boolean first = true;
                    int index = 0;
                    for (Map.Entry<String, JsonElement> field : row.entrySet()) {
                        names[index] = field.getKey();
                        JsonElement value = field.getValue();
                        omitted[index] = value == null || value.isJsonNull();
                        if (!omitted[index]) {
                            prefixes[index] = encodeNamePrefix(field.getKey(), first);
                            first = false;
                            if ("kind".equals(field.getKey()) && value.isJsonPrimitive()
                                    && value.getAsJsonPrimitive().isString()) {
                                constantStrings[index] = value.getAsString();
                                constantValues[index] = encodeStringValue(constantStrings[index]);
                            }
                        }
                        index++;
                    }
                }

                boolean matches(JsonObject row, JsonElement[] values) {
                    if (row.size() != names.length) return false;
                    int index = 0;
                    for (Map.Entry<String, JsonElement> field : row.entrySet()) {
                        JsonElement value = field.getValue();
                        boolean fieldOmitted = value == null || value.isJsonNull();
                        String constant = constantStrings[index];
                        if (!names[index].equals(field.getKey())
                                || omitted[index] != fieldOmitted
                                || constant != null && (!value.isJsonPrimitive()
                                    || !value.getAsJsonPrimitive().isString()
                                    || !constant.equals(value.getAsString()))) return false;
                        values[index++] = value;
                    }
                    return true;
                }
            }


            private final ByteSink output;
            private final byte[] numberBuffer = new byte[20];
            private final byte[] hexBuffer = {'"', '0', 'x', 0, 0, 0, 0, 0, 0, 0, 0, '"'};
            private static final byte[] INTERRUPT_PREFIX =
                "{\"kind\":\"interrupt-request\",\"channel\":".getBytes(StandardCharsets.US_ASCII);
            private static final byte[] TICK_FIELD =
                ",\"scheduler_tick\":".getBytes(StandardCharsets.US_ASCII);
            private final byte[] aliasBuffer =
                new byte[ALIAS_PREFIX.length + 8 + ALIAS_MIDDLE.length + 8
                    + ALIAS_SIZE.length + 2];
            private final Map<String, List<RowSchema>> rowSchemas = new HashMap<>();
            private JsonElement[] rowValues = new JsonElement[16];
            private boolean firstRow = true;

            Utf8JsonWriter(FileChannel channel) throws IOException {
                output = new ByteSink(channel);
                int offset = 0;
                System.arraycopy(ALIAS_PREFIX, 0, aliasBuffer, offset, ALIAS_PREFIX.length);
                offset += ALIAS_PREFIX.length + 8;
                System.arraycopy(ALIAS_MIDDLE, 0, aliasBuffer, offset, ALIAS_MIDDLE.length);
                offset += ALIAS_MIDDLE.length + 8;
                System.arraycopy(ALIAS_SIZE, 0, aliasBuffer, offset, ALIAS_SIZE.length);
                output.write('[');
            }

            private void beforeRow() throws IOException {
                if (firstRow) firstRow = false;
                else output.write(',');
            }

            void writeRow(JsonElement value) throws IOException {
                beforeRow();
                if (value.isJsonObject()) writeRowObject(value.getAsJsonObject());
                else write(value);
            }

            void writeInterruptRequest(int channel, long tick) throws IOException {
                beforeRow();
                output.write(INTERRUPT_PREFIX);
                writeLong(channel);
                output.write(TICK_FIELD);
                writeLong(tick);
                output.write('}');
            }

            void writeAccess(String kind, String pc, long instruction, String address, int size,
                    String evidence, String initiator) throws IOException {
                beforeRow();
                output.write('{');
                writeName("kind", true);
                writeString(kind);
                writeName("pc", false);
                writeString(pc);
                writeName("instruction", false);
                writeLong(instruction);
                writeName("address", false);
                writeString(address);
                writeName("size", false);
                writeLong(size);
                writeName("evidence", false);
                writeString(evidence);
                if (initiator != null) {
                    writeName("initiator", false);
                    writeString(initiator);
                }
                output.write('}');
            }

            void writeAlias(long from, long to, int size) throws IOException {
                beforeRow();
                int firstAddress = ALIAS_PREFIX.length;
                int secondAddress = firstAddress + 8 + ALIAS_MIDDLE.length;
                writeHex32(aliasBuffer, firstAddress, (int) from);
                writeHex32(aliasBuffer, secondAddress, (int) to);
                int number = secondAddress + 8 + ALIAS_SIZE.length;
                if (size >= 0 && size < 10) {
                    aliasBuffer[number] = (byte) ('0' + size);
                    aliasBuffer[number + 1] = '}';
                    output.write(aliasBuffer);
                }
                else {
                    output.write(aliasBuffer, 0, number);
                    writeLong(size);
                    output.write('}');
                }
            }

            private void writeRowObject(JsonObject row) throws IOException {
                if (row.size() > rowValues.length)
                    rowValues = new JsonElement[Integer.highestOneBit(row.size() - 1) << 1];
                JsonElement kindElement = row.get("kind");
                String kind = kindElement != null && kindElement.isJsonPrimitive()
                    ? kindElement.getAsString() : "";
                List<RowSchema> schemas = rowSchemas.get(kind);
                RowSchema schema = null;
                if (schemas != null) {
                    for (RowSchema candidate : schemas) {
                        if (candidate.matches(row, rowValues)) {
                            schema = candidate;
                            break;
                        }
                    }
                }
                if (schema == null) {
                    schema = new RowSchema(row);
                    schema.matches(row, rowValues);
                    if (schemas == null) {
                        schemas = new ArrayList<>();
                        rowSchemas.put(kind, schemas);
                    }
                    schemas.add(schema);
                }
                boolean wroteField = false;
                for (int index = 0; index < schema.names.length; index++) {
                    if (!schema.omitted[index]) {
                        output.write(schema.prefixes[index]);
                        byte[] constant = schema.constantValues[index];
                        if (constant != null) output.write(constant);
                        else {
                            JsonElement value = rowValues[index];
                            if (value.isJsonPrimitive()
                                    && value.getAsJsonPrimitive().isString()) {
                                String string = value.getAsString();
                                if (!string.equals(schema.lastStrings[index])) {
                                    schema.lastStrings[index] = string;
                                    schema.lastStringValues[index] = encodeStringValue(string);
                                }
                                output.write(schema.lastStringValues[index]);
                            }
                            else write(value);
                        }
                        wroteField = true;
                    }
                }
                if (!wroteField) output.write('{');
                output.write('}');
            }

            private void write(JsonElement value) throws IOException {
                if (value == null || value.isJsonNull()) {
                    output.write(NULL);
                }
                else if (value.isJsonObject()) {
                    output.write('{');
                    boolean first = true;
                    for (Map.Entry<String, JsonElement> field : value.getAsJsonObject().entrySet()) {
                        if (field.getValue() == null || field.getValue().isJsonNull()) continue;
                        writeName(field.getKey(), first);
                        first = false;
                        write(field.getValue());
                    }
                    output.write('}');
                }
                else if (value.isJsonArray()) {
                    output.write('[');
                    boolean first = true;
                    for (JsonElement element : value.getAsJsonArray()) {
                        if (first) first = false;
                        else output.write(',');
                        write(element);
                    }
                    output.write(']');
                }
                else {
                    JsonPrimitive primitive = value.getAsJsonPrimitive();
                    if (primitive.isString()) writeString(primitive.getAsString());
                    else if (primitive.isBoolean())
                        output.write(primitive.getAsBoolean() ? TRUE : FALSE);
                    else {
                        String number = primitive.getAsNumber().toString();
                        if ("NaN".equals(number) || "Infinity".equals(number)
                                || "-Infinity".equals(number)) {
                            throw new IllegalArgumentException("JSON forbids non-finite numbers");
                        }
                        writeAscii(number);
                    }
                }
            }

            private void writeName(String name, boolean first) throws IOException {
                if (!first) output.write(',');
                writeString(name);
                output.write(':');
            }

            private void writeAscii(String value) throws IOException {
                output.writeAscii(value, 0, value.length());
            }

            private void writeLong(long value) throws IOException {
                if (value == Long.MIN_VALUE) {
                    output.write(LONG_MIN);
                    return;
                }
                boolean negative = value < 0;
                if (negative) value = -value;
                int start = numberBuffer.length;
                do {
                    numberBuffer[--start] = (byte) ('0' + value % 10);
                    value /= 10;
                } while (value != 0);
                if (negative) numberBuffer[--start] = '-';
                output.write(numberBuffer, start, numberBuffer.length - start);
            }

            private static void writeHex32(byte[] destination, int offset, int value) {
                for (int shift = 28; shift >= 0; shift -= 4)
                    destination[offset++] = ADDRESS_HEX[(value >>> shift) & 15];
            }

            private void writeHexValue(long value) throws IOException {
                writeHex32(hexBuffer, 3, (int) value);
                output.write(hexBuffer);
            }

            private void writeUnicodeEscape(char value) throws IOException {
                output.write('\\');
                output.write('u');
                output.write(HEX[(value >>> 12) & 15]);
                output.write(HEX[(value >>> 8) & 15]);
                output.write(HEX[(value >>> 4) & 15]);
                output.write(HEX[value & 15]);
            }

            private void writeCodePoint(int value) throws IOException {
                if (value < 0x800) {
                    output.write(0xc0 | value >>> 6);
                    output.write(0x80 | value & 0x3f);
                }
                else if (value < 0x10000) {
                    output.write(0xe0 | value >>> 12);
                    output.write(0x80 | value >>> 6 & 0x3f);
                    output.write(0x80 | value & 0x3f);
                }
                else {
                    output.write(0xf0 | value >>> 18);
                    output.write(0x80 | value >>> 12 & 0x3f);
                    output.write(0x80 | value >>> 6 & 0x3f);
                    output.write(0x80 | value & 0x3f);
                }
            }

            private void writeString(String value) throws IOException {
                output.write('"');
                for (int index = 0; index < value.length(); index++) {
                    char ch = value.charAt(index);
                    switch (ch) {
                        case '"' -> { output.write('\\'); output.write('"'); }
                        case '\\' -> { output.write('\\'); output.write('\\'); }
                        case '\t' -> { output.write('\\'); output.write('t'); }
                        case '\b' -> { output.write('\\'); output.write('b'); }
                        case '\n' -> { output.write('\\'); output.write('n'); }
                        case '\r' -> { output.write('\\'); output.write('r'); }
                        case '\f' -> { output.write('\\'); output.write('f'); }
                        case '<', '>', '&', '=', '\'', '\u2028', '\u2029' ->
                            writeUnicodeEscape(ch);
                        default -> {
                            if (ch < 0x20) writeUnicodeEscape(ch);
                            else if (ch < 0x80) output.write(ch);
                            else if (Character.isHighSurrogate(ch) && index + 1 < value.length()
                                    && Character.isLowSurrogate(value.charAt(index + 1))) {
                                writeCodePoint(Character.toCodePoint(ch, value.charAt(++index)));
                            }
                            else if (Character.isSurrogate(ch)) writeCodePoint(0xfffd);
                            else writeCodePoint(ch);
                        }
                    }
                }
                output.write('"');
            }

            private static byte[] encodeNamePrefix(String name, boolean first) {
                StringBuilder encoded = new StringBuilder(name.length() + 4);
                encoded.append(first ? '{' : ',').append('"');
                appendEscaped(encoded, name);
                encoded.append('"').append(':');
                return encoded.toString().getBytes(StandardCharsets.UTF_8);
            }

            private static byte[] encodeTextField(String name, String value, boolean first) {
                StringBuilder encoded = new StringBuilder(name.length() + value.length() + 6);
                encoded.append(first ? '{' : ',').append('"');
                appendEscaped(encoded, name);
                encoded.append("\":\"");
                appendEscaped(encoded, value);
                encoded.append('"');
                return encoded.toString().getBytes(StandardCharsets.UTF_8);
            }

            private static byte[] encodeStringValue(String value) {
                StringBuilder encoded = new StringBuilder(value.length() + 2);
                encoded.append('"');
                appendEscaped(encoded, value);
                encoded.append('"');
                return encoded.toString().getBytes(StandardCharsets.UTF_8);
            }

            private static void appendEscaped(StringBuilder encoded, String value) {
                for (int index = 0; index < value.length(); index++) {
                    char ch = value.charAt(index);
                    switch (ch) {
                        case '"' -> encoded.append("\\\"");
                        case '\\' -> encoded.append("\\\\");
                        case '\t' -> encoded.append("\\t");
                        case '\b' -> encoded.append("\\b");
                        case '\n' -> encoded.append("\\n");
                        case '\r' -> encoded.append("\\r");
                        case '\f' -> encoded.append("\\f");
                        case '<', '>', '&', '=', '\'', '\u2028', '\u2029' ->
                            appendUnicodeEscape(encoded, ch);
                        default -> {
                            if (ch < 0x20) appendUnicodeEscape(encoded, ch);
                            else if (Character.isHighSurrogate(ch) && index + 1 < value.length()
                                    && Character.isLowSurrogate(value.charAt(index + 1))) {
                                encoded.append(ch).append(value.charAt(++index));
                            }
                            else if (Character.isSurrogate(ch)) encoded.append('\ufffd');
                            else encoded.append(ch);
                        }
                    }
                }
            }

            private static void appendUnicodeEscape(StringBuilder destination, char value) {
                destination.append("\\u")
                    .append((char) HEX[(value >>> 12) & 15])
                    .append((char) HEX[(value >>> 8) & 15])
                    .append((char) HEX[(value >>> 4) & 15])
                    .append((char) HEX[value & 15]);
            }

            void finish() throws IOException {
                output.write(']');
                output.flush();
            }

            void flush() throws IOException {
                output.flush();
            }

            @Override
            public void close() throws IOException {
                output.close();
            }
        }

        JsonRows(Path directory, String prefix, boolean countKinds) throws IOException {
            path = Files.createTempFile(directory, prefix, ".json");
            try {
                spool = FileChannel.open(path, StandardOpenOption.READ, StandardOpenOption.WRITE);
                writer = new Utf8JsonWriter(spool);
            }
            catch (IOException exception) {
                Files.deleteIfExists(path);
                throw exception;
            }
            kindCounts = countKinds ? new HashMap<>() : null;
        }

        void add(JsonObject row) {
            if (discard) {
                if (listener != null) listener.accept(row);
                return;
            }
            JsonElement kindValue = kindCounts == null ? null : row.get("kind");
            String kind = kindValue == null ? null : kindValue.getAsString();
            add(row, kind, spoolsKind(kind));
        }

        private void add(JsonObject row, String kind, boolean stored) {
            if (stored) {
                requireOpen();
                try {
                    writer.writeRow(row);
                }
                catch (IOException e) {
                    throw new JsonIOException(e);
                }
            }
            finishRow(row, kind, stored);
        }

        private void incrementKind(String kind) {
            incrementKind(kind, 1);
        }

        private void incrementKind(String kind, long count) {
            long[] counter = lastKindCounter;
            if (counter == null || !kind.equals(lastCountedKind)) {
                counter = kindCounts.get(kind);
                if (counter == null) {
                    counter = new long[1];
                    kindCounts.put(kind, counter);
                }
                lastCountedKind = kind;
                lastKindCounter = counter;
            }
            counter[0] += count;
        }

        private void requireOpen() {
            if (sealed) throw new IllegalStateException("cannot append to a sealed trace");
        }

        private boolean spoolsKind(String kind) {
            return !discard && (projectedKinds == null
                || kind != null && projectedKinds.contains(kind));
        }

        private boolean spoolsAlias() {
            return !discard && includesAlias;
        }

        // Call once before computing an optional typed payload. If it is omitted, account for
        // the event here; otherwise the typed writer will account for it when the row is ready.
        private boolean omitsEventPayload(String kind) {
            if (spoolsKind(kind) || listener != null) return false;
            if (projectedKinds != null) incrementKind(kind);
            return true;
        }

        private void finishRow(JsonObject row, String kind, boolean stored) {
            if (stored) count++;
            if (kindCounts != null && kind != null && (stored || projectedKinds != null))
                incrementKind(kind);
            if (listener != null) listener.accept(row);
        }

        private void addRegisterWrite(long pc, RegisterDef register, long value, String initiator) {
            RegisterWriteFields fields = register.writeFields;
            if (fields == null) register.writeFields = fields = new RegisterWriteFields(register);
            try {
                event.begin(REGISTER_WRITE);
                event.hex(PC, pc);
                event.text(fields.name);
                event.text(fields.behavior);
                event.text(fields.trigger);
                event.hex(VALUE, value);
                event.text(fields.evidence);
                if (initiator != null) event.text(INITIATOR, initiator);
                event.end(REGISTER_WRITE);
            }
            catch (IOException e) {
                throw new JsonIOException(e);
            }
        }

        private void beginCsih(EventKind kind, int unit, long tick) throws IOException {
            event.begin(kind);
            event.number(UNIT, unit);
            event.number(SCHEDULER_TICK, tick);
            event.text(CSIH_EVIDENCE);
        }

        private void addCsihTx(int unit, long tick, long word, int bits, boolean lsbFirst,
                long ordinal) {
            try {
                beginCsih(CSIH_TX, unit, tick);
                event.hex(WORD, word);
                event.hex(VALUE, word & ((1L << bits) - 1));
                event.number(CHIP_SELECT, (word >> 16) & 255);
                event.number(BITS, bits);
                event.bool(LSB_FIRST, lsbFirst);
                event.number(TRANSMIT_ORDINAL, ordinal);
                event.end(CSIH_TX);
            }
            catch (IOException e) {
                throw new JsonIOException(e);
            }
        }

        private void addCsihFrame(int unit, long tick, List<Long> words) {
            try {
                beginCsih(CSIH_FRAME, unit, tick);
                event.numbers(WORDS, words);
                event.end(CSIH_FRAME);
            }
            catch (IOException e) {
                throw new JsonIOException(e);
            }
        }

        private void addCsihWord(int unit, long tick, String value, String evidence) {
            try {
                beginCsih(CSIH_WORD, unit, tick);
                if (value != null) event.text(VALUE, value);
                event.text(INPUT_EVIDENCE, evidence);
                event.end(CSIH_WORD);
            }
            catch (IOException e) {
                throw new JsonIOException(e);
            }
        }

        private void addDmaTransfer(int channel, long source, long destination, int size,
                long remaining, boolean error, long tick, long cycles) {
            if (omitsEventPayload(DMA_TRANSFER.name)) return;
            try {
                event.begin(DMA_TRANSFER);
                event.number(CHANNEL, channel);
                event.hex(SOURCE, source);
                event.hex(DESTINATION, destination);
                event.number(SIZE, size);
                event.number(REMAINING, remaining);
                event.bool(ERROR, error);
                event.number(SCHEDULER_TICK, tick);
                event.number(HSB_CYCLES, cycles);
                event.text(DMA_EVIDENCE);
                event.end(DMA_TRANSFER);
            }
            catch (IOException e) {
                throw new JsonIOException(e);
            }
        }

        private void writeAccess(String kind, JsonPrimitive pc, long instruction,
                                 JsonPrimitive address, int size, String evidence,
                                 String initiator) {
            try {
                writer.writeAccess(kind, pc.getAsString(), instruction, address.getAsString(),
                    size, evidence, initiator);
            }
            catch (IOException e) {
                throw new JsonIOException(e);
            }
        }

        private void addAccess(String kind, JsonPrimitive pc, long instruction,
                               JsonPrimitive address, int size, String evidence, String initiator) {
            if (!discard) {
                requireOpen();
                writeAccess(kind, pc, instruction, address, size, evidence, initiator);
            }
            JsonObject row = null;
            if (listener != null) {
                row = new JsonObject();
                row.addProperty("kind", kind);
                row.add("pc", pc);
                row.addProperty("instruction", instruction);
                row.add("address", address);
                row.addProperty("size", size);
                row.addProperty("evidence", evidence);
                if (initiator != null) row.addProperty("initiator", initiator);
            }
            finishRow(row, kind, !discard);
        }

        private void writeAlias(long from, long to, int size) {
            try {
                writer.writeAlias(from, to, size);
            }
            catch (IOException e) {
                throw new JsonIOException(e);
            }
        }

        private void addAlias(long from, long to, int size) {
            boolean stored = spoolsAlias();
            if (stored) {
                requireOpen();
                writeAlias(from, to, size);
            }
            JsonObject row = null;
            if (listener != null) {
                row = new JsonObject();
                row.addProperty("kind", ALIAS_WRITE);
                row.addProperty("from", hex32(from));
                row.addProperty("to", hex32(to));
                row.addProperty("size", size);
            }
            finishRow(row, ALIAS_WRITE, stored);
        }

        boolean wantsRows() {
            return !discard || listener != null;
        }

        void addInterruptRequest(int channel, long tick, boolean firmwareOnly, long control) {
            boolean stored = spoolsKind(INTERRUPT_REQUEST);
            if (listener != null || (stored && firmwareOnly)) {
                JsonObject event = new JsonObject();
                event.addProperty("kind", INTERRUPT_REQUEST);
                event.addProperty("channel", channel);
                if (firmwareOnly)
                    event.addProperty("firmware_control", String.format("0x%04X", control & 0xffff));
                event.addProperty("scheduler_tick", tick);
                add(event, INTERRUPT_REQUEST, stored);
                return;
            }
            if (stored) {
                requireOpen();
                try {
                    writer.writeInterruptRequest(channel, tick);
                }
                catch (IOException e) {
                    throw new JsonIOException(e);
                }
            }
            finishRow(null, INTERRUPT_REQUEST, stored);
        }

        long size() { return count; }

        long countKind(String kind) {
            long[] counter = kindCounts.get(kind);
            return counter == null ? 0 : counter[0];
        }
        record Counters(long count, Map<String, Long> kinds) {}

        private Map<String, Long> snapshotKindCounts() {
            Map<String, Long> kinds = new LinkedHashMap<>();
            if (kindCounts != null) {
                for (Map.Entry<String, long[]> entry : kindCounts.entrySet())
                    kinds.put(entry.getKey(), entry.getValue()[0]);
            }
            return kinds;
        }

        Counters checkpointCounters() {
            return new Counters(count, snapshotKindCounts());
        }

        void restoreCounters(Counters counters) {
            count = counters.count();
            lastCountedKind = null;
            lastKindCounter = null;
            if (kindCounts != null) {
                kindCounts.clear();
                for (Map.Entry<String, Long> entry : counters.kinds().entrySet())
                    kindCounts.put(entry.getKey(), new long[] {entry.getValue()});
            }
        }

        private long position() throws IOException {
            writer.flush();
            return spool.position();
        }

        void beginTrial(boolean capture, List<String> eventKinds) throws IOException {
            if (trialStart != -1 || discard) throw new IllegalStateException("trial already active");
            discard = !capture;
            if (capture) trialStart = position();
            if (eventKinds != null) {
                projectedKinds = Set.copyOf(eventKinds);
                includesAlias = projectedKinds.contains(ALIAS_WRITE);
                // Checks still use the cumulative, checkpointed counts. Report only the
                // events since this trial began, even when no restore preceded it.
                trialKindBaseline = snapshotKindCounts();
            }
        }

        JsonObject endTrial() throws IOException {
            if (discard) trials.add(new Span(0, 0));
            else {
                if (trialStart < 0) throw new IllegalStateException("trial not active");
                long end = position();
                // If the spool already had a row, the first new row starts with a comma.
                long start = trialStart > 1 && end > trialStart ? trialStart + 1 : trialStart;
                trials.add(new Span(start, end));
            }
            trialStart = -1;
            discard = false;
            if (projectedKinds == null) return null;
            JsonObject counts = new JsonObject();
            for (Map.Entry<String, long[]> entry : kindCounts.entrySet()) {
                String kind = entry.getKey();
                long delta = entry.getValue()[0] - trialKindBaseline.getOrDefault(kind, 0L);
                if (delta != 0) counts.addProperty(kind, delta);
            }
            projectedKinds = null;
            trialKindBaseline = null;
            includesAlias = true;
            return counts;
        }

        // Copy the encoded rows between the destination's array delimiters.
        void writeTo(JsonWriter destination, FileChannel report, int trial) throws IOException {
            if (!sealed) {
                writer.finish();
                sealed = true;
            }
            Span span = trial < 0 ? new Span(1, spool.size() - 1) : trials.get(trial);
            destination.beginArray();
            if (span.start < span.end) {
                destination.flush();
                for (long at = span.start; at < span.end;) {
                    long n = spool.transferTo(at, span.end - at, report);
                    if (n == 0) throw new IOException("incomplete trace spool: " + path);
                    at += n;
                }
            }
            destination.endArray();
        }

        @Override
        public void close() throws IOException {
            try { writer.close(); }
            finally { Files.deleteIfExists(path); }
        }
    }

    static final class Trace implements Closeable {
        private static final int MAX_TRACE_ENTRIES = 16777216;
        static final int RECENT_PC_COUNT = 16;
        private static final int INSTRUCTION_RECORD_SIZE = Integer.BYTES + Byte.BYTES + Long.BYTES;
        final boolean instructionTraceEnabled;
        private boolean instructionRecordingActive = true;
        private final InstructionRows instructionRows;
        final List<JsonObject> instructionShortcuts = new ArrayList<>();
        private final ObservationRows compareOperands;
        private final ObservationRows tableIndices;
        private TupleKeys compareKeys = new TupleKeys();
        private TupleKeys indexKeys = new TupleKeys();
        int instructionTraceSize;
        long instructions;
        private long[] recentPcs = new long[RECENT_PC_COUNT];
        private int recentOffset;
        private int recentNext;
        private int recentSize;
        ExecutedPcs executed = new ExecutedPcs();
        final Map<String, Long> syncCounts = new LinkedHashMap<>();
        final JsonRows memoryAccesses;
        final JsonRows deviceEvents;
        final WrittenBytes writtenBytes = new WrittenBytes();
        private static final int HEX_CACHE_BITS = 12;
        private final int[] hexKeys = new int[1 << HEX_CACHE_BITS];
        private final JsonPrimitive[] hexValues = new JsonPrimitive[hexKeys.length];
        boolean traceLostAddress;
        boolean unobservedWrites;
        String busInitiator;

        private record InstructionSpan(long start, long end) {}
        private record InstructionSegment(InstructionSegment previous, InstructionSpan range) {}

        /** Append-only binary trace with logical checkpoint branches and per-trial ranges. */
        private static final class InstructionRows implements Closeable {
            private static final int BUFFER_RECORDS = 4096;
            private final Path path;
            private final FileChannel spool;
            private final ByteBuffer output =
                ByteBuffer.allocate(BUFFER_RECORDS * INSTRUCTION_RECORD_SIZE);
            // Export is synchronous and starts after flush(); the read cursor shares its storage.
            private final ByteBuffer input = output.duplicate();
            private final List<InstructionSpan> trials = new ArrayList<>();
            private long count;
            private long segmentStart;
            private long trialStart;
            private InstructionSegment segments;

            InstructionRows(Path directory) throws IOException {
                path = Files.createTempFile(directory, ".p1me-instructions-", ".bin");
                try {
                    spool = FileChannel.open(path,
                        StandardOpenOption.READ, StandardOpenOption.WRITE);
                }
                catch (IOException exception) {
                    Files.deleteIfExists(path);
                    throw exception;
                }
            }

            void add(long pc, int size, long tick) {
                try {
                    if (output.remaining() < INSTRUCTION_RECORD_SIZE) flush();
                    output.putInt((int) pc).put((byte) size).putLong(tick);
                    count++;
                }
                catch (IOException exception) {
                    throw new JsonIOException(exception);
                }
            }

            private void flush() throws IOException {
                output.flip();
                while (output.hasRemaining()) spool.write(output);
                output.clear();
            }

            InstructionSegment checkpoint() {
                if (segmentStart != count) {
                    InstructionSpan appended = new InstructionSpan(segmentStart, count);
                    if (segments != null && segments.range.end == appended.start) {
                        segments = new InstructionSegment(
                            segments.previous,
                            new InstructionSpan(segments.range.start, appended.end));
                    }
                    else segments = new InstructionSegment(segments, appended);
                    segmentStart = count;
                }
                return segments;
            }

            void restore(InstructionSegment snapshot) {
                segments = snapshot;
                segmentStart = count;
            }

            void beginTrial() {
                trialStart = count;
            }

            void endTrial() {
                trials.add(new InstructionSpan(trialStart, count));
            }

            private ArrayDeque<InstructionSpan> logicalSpans() {
                InstructionSegment segment = checkpoint();
                ArrayDeque<InstructionSpan> reversed = new ArrayDeque<>();
                while (segment != null) {
                    reversed.push(segment.range);
                    segment = segment.previous;
                }
                return reversed;
            }

            private int readChunk(long at, long end) throws IOException {
                int records = (int) Math.min(BUFFER_RECORDS, end - at);
                long byteOffset = Math.multiplyExact(at, INSTRUCTION_RECORD_SIZE);
                input.clear().limit(records * INSTRUCTION_RECORD_SIZE);
                while (input.hasRemaining()) {
                    int read = spool.read(input, byteOffset);
                    if (read <= 0)
                        throw new IOException("incomplete instruction spool: " + path);
                    byteOffset += read;
                }
                input.flip();
                return records;
            }

            private void writeJsonSpan(JsonWriter writer, InstructionSpan span) throws IOException {
                long at = span.start;
                while (at < span.end) {
                    int records = readChunk(at, span.end);
                    for (int index = 0; index < records; index++) {
                        int pc = input.getInt();
                        int size = Byte.toUnsignedInt(input.get());
                        long tick = input.getLong();
                        writer.beginObject()
                            .name("pc").value(hex32(pc))
                            .name("size").value(size)
                            .name("instruction").value(tick)
                            .endObject();
                    }
                    at += records;
                }
            }

            void writeTo(JsonWriter writer, int trial) throws IOException {
                flush();
                writer.beginArray();
                if (trial < 0) {
                    for (InstructionSpan span : logicalSpans())
                        writeJsonSpan(writer, span);
                }
                else writeJsonSpan(writer, trials.get(trial));
                writer.endArray();
            }

            void writeCompact(Path destination) throws IOException {
                flush();
                try (DataOutputStream stream = new DataOutputStream(
                        new BufferedOutputStream(Files.newOutputStream(destination), 65536))) {
                    for (InstructionSpan span : logicalSpans()) {
                        long at = span.start;
                        while (at < span.end) {
                            int records = readChunk(at, span.end);
                            for (int index = 0; index < records; index++) {
                                stream.writeInt(input.getInt());
                                stream.writeByte(input.get());
                                input.getLong();
                            }
                            at += records;
                        }
                    }
                }
            }

            @Override
            public void close() throws IOException {
                trials.clear();
                try { spool.close(); }
                finally { Files.deleteIfExists(path); }
            }
        }
        Trace(boolean instructionTraceEnabled, Path directory) throws IOException {
            JsonRows memory = new JsonRows(directory, ".p1me-memory-", false);
            JsonRows events = null;
            try {
                events = new JsonRows(directory, ".p1me-events-", true);
                this.instructionRows = new InstructionRows(directory);
            }
            catch (IOException | RuntimeException exception) {
                if (events != null) {
                    try { events.close(); }
                    catch (IOException cleanup) { exception.addSuppressed(cleanup); }
                }
                try { memory.close(); }
                catch (IOException cleanup) { exception.addSuppressed(cleanup); }
                throw exception;
            }
            memoryAccesses = memory;
            deviceEvents = events;
            compareOperands = new ObservationRows(directory, ".p1me-compares-");
            tableIndices = new ObservationRows(directory, ".p1me-indices-");
            this.instructionTraceEnabled = instructionTraceEnabled;
            syncCounts.put("SYNCE", 0L);
            syncCounts.put("SYNCM", 0L);
            syncCounts.put("SYNCP", 0L);
            syncCounts.put("SYNCI", 0L);
        }

        void deferInstructionRecording() {
            if (instructions != 0 || instructionTraceSize != 0)
                throw new IllegalStateException("instruction recording must be deferred before execution");
            instructionRecordingActive = false;
        }

        void startInstructionRecording() {
            instructionRecordingActive = true;
        }

        boolean recordsInstructionTrace() {
            return instructionTraceEnabled && instructionRecordingActive;
        }

        boolean recordsInstructionMetadata() {
            return instructionRecordingActive;
        }

        void recordExecutedPc(long pc) {
            if (instructionRecordingActive) executed.add(pc);
        }

        @Override
        public void close() throws IOException {
            try (InstructionRows instructions = instructionRows;
                 JsonRows memory = memoryAccesses; JsonRows events = deviceEvents;
                 ObservationRows compares = compareOperands; ObservationRows indices = tableIndices) {
                // Close every spool even if one cleanup fails.
            }
            finally {
                instructionShortcuts.clear();
                instructionTraceSize = 0;
                compareKeys = new TupleKeys();
                indexKeys = new TupleKeys();
                executed = new ExecutedPcs();
                syncCounts.clear();
                writtenBytes.clear();
                Arrays.fill(hexValues, null);
            }
        }

        void enterInstruction(long pc, int size) {
            if (!recordsInstructionTrace()) return;
            if (instructionTraceSize >= MAX_TRACE_ENTRIES) {
                throw new IllegalStateException(
                    "complete instruction trace exceeds " + MAX_TRACE_ENTRIES + " entries");
            }
            if (size <= 0 || size > 0xff) {
                throw new IllegalStateException("instruction trace size outside 1..255");
            }
            if ((pc & ~0xffffffffL) != 0) {
                throw new IllegalStateException("instruction trace PC outside 32-bit address space");
            }
            instructionRows.add(pc, size, instructions);
            instructionTraceSize++;
        }

        void noteRecentPc(long pc) {
            recentPcs[recentOffset + recentNext] = pc;
            recentNext = (recentNext + 1) & (RECENT_PC_COUNT - 1);
            if (recentSize < RECENT_PC_COUNT) recentSize++;
        }

        // Use the controls array itself, not a second ring to merge after each batch.
        // The trace only borrows primitive storage; it never holds a thread or machine.
        int bindNativeHistory(long[] controls, int offset) {
            if (recentPcs != controls) {
                System.arraycopy(recentPcs, recentOffset, controls, offset, RECENT_PC_COUNT);
                recentPcs = controls;
                recentOffset = offset;
            }
            return recentNext;
        }

        void unbindNativeHistory(long[] controls) {
            if (recentPcs == controls) {
                recentPcs = copyRecentPcs();
                recentOffset = 0;
            }
        }

        private long[] copyRecentPcs() {
            return Arrays.copyOfRange(recentPcs, recentOffset, recentOffset + RECENT_PC_COUNT);
        }

        long retireNativePcs(int count) {
            // Native already wrote these slots. Publish only the retired prefix.
            recentNext = (recentNext + count) & (RECENT_PC_COUNT - 1);
            recentSize = Math.min(recentSize + count, RECENT_PC_COUNT);
            return recentPcs[recentOffset + ((recentNext - 1) & (RECENT_PC_COUNT - 1))];
        }

        JsonArray recentPcs() {
            JsonArray rows = new JsonArray();
            int start = recentNext - recentSize;
            for (int i = 0; i < recentSize; i++) {
                rows.add(hex32(recentPcs[recentOffset + ((start + i) & (RECENT_PC_COUNT - 1))]));
            }
            return rows;
        }

        void compare(long pc, long branch, String mnemonic, int width, long left, long right) {
            if (!instructionRecordingActive) return;
            if (compareKeys.add(pc, left, right)) {
                compareOperands.addCompare(pc, branch, mnemonic, width, left, right);
            }
        }

        void tableIndex(long pc, long base, long index, int scale, long effective, int width, String access) {
            if (!instructionRecordingActive) return;
            if (indexKeys.add(pc, index, effective)) {
                tableIndices.addIndex(pc, base, index, scale, effective, width, access);
            }
        }

        void writeCompareOperands(JsonWriter writer, FileChannel output, int trial) throws IOException {
            compareOperands.writeTo(writer, output, trial);
        }

        void writeTableIndices(JsonWriter writer, FileChannel output, int trial) throws IOException {
            tableIndices.writeTo(writer, output, trial);
        }

        void shortcut(String kind, long pc, long resumePc) {
            if (!recordsInstructionTrace()) return;
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

        void writeInstructionTrace(JsonWriter writer, int trial) throws IOException {
            instructionRows.writeTo(writer, trial);
        }

        void sync(String operation) {
            if (instructionRecordingActive) addNativeSync(operation, 1);
        }

        void addNativeSync(String operation, long count) {
            syncCounts.put(operation, syncCounts.get(operation) + count);
        }

        // Only immutable values are cached. No cached value depends on a checkpoint.
        private JsonPrimitive hexAddress(long value) {
            int key = (int) value;
            int slot = (key * 0x9e3779b9) >>> (32 - HEX_CACHE_BITS);
            JsonPrimitive cached = hexValues[slot];
            if (cached == null || hexKeys[slot] != key) {
                cached = new JsonPrimitive(hex32(key));
                hexKeys[slot] = key;
                hexValues[slot] = cached;
            }
            return cached;
        }

        private static final int MAX_MEMORY_ROWS = 1 << 20;

        boolean retainsRead() {
            return memoryAccesses.size() < MAX_MEMORY_ROWS
                && (!memoryAccesses.discard || memoryAccesses.listener != null);
        }
        boolean canDeferNativeBus(){
            return !memoryAccesses.wantsRows() && memoryAccesses.listener==null &&
                deviceEvents.listener==null && !deviceEvents.spoolsAlias();
        }

        // ABI flags shared with windowgraph-abi.h. Omitted rows do not imply omitted
        // coverage, and unprojected discarded aliases have no kind count.
        static final int NATIVE_ALIAS = 2, NATIVE_MARK = 4,
            NATIVE_COVER = 8, NATIVE_SYNC = 16;

        int nativeRetirementFlags() {
            int flags = instructionRecordingActive ? NATIVE_SYNC : 0;
            boolean projected = deviceEvents.projectedKinds != null;
            if (projected) flags |= NATIVE_ALIAS;
            if (unobservedWrites) return flags;
            if (!projected && memoryAccesses.size() < MAX_MEMORY_ROWS) flags |= NATIVE_MARK;
            else if (!traceLostAddress) flags |= NATIVE_COVER;
            return flags;
        }

        MemorySegment nativeWrittenBytes() {
            return writtenBytes.segment;
        }

        void finishNativeWrites(long aliases, boolean lost, long[] state, int from, int count) {
            if (aliases != 0) deviceEvents.incrementKind(JsonRows.ALIAS_WRITE, aliases);
            traceLostAddress |= lost;
            for (int i = from, end = from + count; i < end; i++) {
                long event = state[i];
                writtenBytes.markOrCovers(event & 0xffff_ffffL, (int) (event >>> 32) & 255, true);
            }
        }

        private boolean markBusWrite(long address, int size) {
            boolean full = memoryAccesses.size() >= MAX_MEMORY_ROWS;
            if (!unobservedWrites) {
                if (!full && deviceEvents.projectedKinds == null) {
                    writtenBytes.markOrCovers(address, size, true);
                }
                else if (!traceLostAddress && !writtenBytes.markOrCovers(address, size, false)) {
                    traceLostAddress = true;
                }
            }
            return !full && memoryAccesses.wantsRows();
        }

        private void addBusAccess(String kind, long pc, long address, int size, String evidence) {
            memoryAccesses.addAccess(kind, hexAddress(pc), instructions,
                hexAddress(address), size, evidence, busInitiator);
        }

        void aliasWrite(long from, long to, int size) {
            deviceEvents.addAlias(from, to, size);
        }

        // Store the exact tuples, not just their hashes. PC is a 32-bit address,
        // so PC + 1 reserves zero for an empty slot without restricting operands.
        private static final class TupleKeys {
            private static final long[] EMPTY = new long[0];
            private long[] pcs = EMPTY;
            private long[] first = EMPTY;
            private long[] second = EMPTY;
            private int size;

            private int slot(long pc, long left, long right) {
                long hash = (pc * 0x9e3779b97f4a7c15L)
                    ^ (left * 0xc2b2ae3d27d4eb4fL) ^ (right * 0x165667b19e3779f9L);
                hash = (hash ^ (hash >>> 33)) * 0xff51afd7ed558ccdL;
                int mask = pcs.length - 1;
                int slot = (int) (hash ^ (hash >>> 32)) & mask;
                while (pcs[slot] != 0
                        && (pcs[slot] != pc || first[slot] != left || second[slot] != right)) {
                    slot = (slot + 1) & mask;
                }
                return slot;
            }

            private void resize(int capacity) {
                long[] oldPcs = pcs, oldFirst = first, oldSecond = second;
                pcs = new long[capacity];
                first = new long[capacity];
                second = new long[capacity];
                for (int i = 0; i < oldPcs.length; i++) {
                    if (oldPcs[i] == 0) continue;
                    int slot = slot(oldPcs[i], oldFirst[i], oldSecond[i]);
                    pcs[slot] = oldPcs[i];
                    first[slot] = oldFirst[i];
                    second[slot] = oldSecond[i];
                }
            }

            boolean add(long pc, long left, long right) {
                long key = pc + 1;
                if (pcs.length == 0) resize(16);
                int slot = slot(key, left, right);
                if (pcs[slot] != 0) return false;
                if (size == pcs.length - (pcs.length >>> 2)) {
                    resize(Math.multiplyExact(pcs.length, 2));
                    slot = slot(key, left, right);
                }
                pcs[slot] = key;
                first[slot] = left;
                second[slot] = right;
                size++;
                return true;
            }

            TupleKeys copy() {
                TupleKeys result = new TupleKeys();
                if (size != 0) {
                    result.pcs = pcs.clone();
                    result.first = first.clone();
                    result.second = second.clone();
                    result.size = size;
                }
                return result;
            }
        }

        static final class ExecutedPcs {
            private static final int PAGE_BITS = 12;
            private static final int GROUP_BITS = 8;
            private static final int GROUP_MASK = (1 << GROUP_BITS) - 1;
            private static final int WORD_MASK = (1 << (PAGE_BITS - 6)) - 1;
            private long[][][] groups;
            private int lastPageNumber = -1;
            private long[] lastPage;
            private int size;

            private long[] page(int number, boolean create) {
                if (groups == null) {
                    if (!create) return null;
                    groups = new long[1 << (32 - PAGE_BITS - GROUP_BITS)][][];
                }
                int groupIndex = number >>> GROUP_BITS;
                long[][] group = groups[groupIndex];
                if (group == null) {
                    if (!create) return null;
                    groups[groupIndex] = group = new long[1 << GROUP_BITS][];
                }
                int pageIndex = number & GROUP_MASK;
                long[] page = group[pageIndex];
                if (page == null && create) group[pageIndex] = page = new long[WORD_MASK + 1];
                return page;
            }

            void add(long pc) {
                int addressWord = (int) pc >>> 6;
                int number = addressWord >>> (PAGE_BITS - 6);
                if (number != lastPageNumber) {
                    lastPage = page(number, true);
                    lastPageNumber = number;
                }
                int word = addressWord & WORD_MASK;
                long mask = 1L << pc;
                if ((lastPage[word] & mask) == 0) {
                    lastPage[word] |= mask;
                    size++;
                }
            }

            boolean contains(long pc) {
                if ((pc & ~0xffffffffL) != 0) return false;
                int address = (int) pc;
                int addressWord = address >>> 6;
                long[] page = page(address >>> PAGE_BITS, false);
                return page != null && (page[addressWord & WORD_MASK] & (1L << address)) != 0;
            }

            int size() {
                return size;
            }

            ExecutedPcs copy() {
                ExecutedPcs result = new ExecutedPcs();
                result.size = size;
                if (groups == null) return result;
                result.groups = groups.clone();
                for (int i = 0; i < groups.length; i++) {
                    if (groups[i] == null) continue;
                    long[][] group = groups[i];
                    long[][] copy = result.groups[i] = group.clone();
                    for (int j = 0; j < group.length; j++) {
                        if (group[j] != null) copy[j] = group[j].clone();
                    }
                }
                return result;
            }
        }

        /** Restores select a logical prefix; completed trials keep their original spool ranges. */
        private static final class ObservationRows implements Closeable {
            private static final String HEX = "0123456789ABCDEF";
            private record Segment(Segment previous, JsonRows.Span range) {}
            private final Path directory;
            private final String prefix;
            private final List<JsonRows.Span> trials = new ArrayList<>();
            private final char[] digits = new char[18];
            private Path path;
            private FileChannel spool;
            private BufferedWriter output;
            private boolean haveRows;
            private Segment segments;
            private long segmentStart;
            private long trialStart;

            ObservationRows(Path directory, String prefix) {
                this.directory = directory;
                this.prefix = prefix;
                digits[0] = '0';
                digits[1] = 'x';
            }

            private void beginRow() throws IOException {
                if (output == null) {
                    path = Files.createTempFile(directory, prefix, ".json");
                    spool = FileChannel.open(path, StandardOpenOption.READ, StandardOpenOption.WRITE);
                    output = new BufferedWriter(Channels.newWriter(spool, StandardCharsets.UTF_8), 65536);
                }
                if (haveRows) output.write(',');
                haveRows = true;
            }

            private void hex(long value, int width) throws IOException {
                for (int i = width + 1; i >= 2; i--, value >>>= 4) {
                    digits[i] = HEX.charAt((int) value & 15);
                }
                output.write(digits, 0, width + 2);
            }

            private void operand(long value, int minimum) throws IOException {
                if (minimum == 0 || minimum > 16) {
                    output.write(String.format("0x%0" + minimum + "X", value));
                    return;
                }
                int significant = (67 - Long.numberOfLeadingZeros(value)) >>> 2;
                hex(value, Math.max(minimum, significant));
            }

            private void integer(int number) throws IOException {
                long value = number;
                if (value < 0) {
                    output.write('-');
                    value = -value;
                }
                int i = digits.length;
                do {
                    digits[--i] = (char) ('0' + value % 10);
                    value /= 10;
                } while (value != 0);
                output.write(digits, i, digits.length - i);
            }

            void addCompare(long pc, long branch, String mnemonic, int width, long left, long right) {
                try {
                    beginRow();
                    output.write("{\"compare_pc\":\"");
                    hex(pc, 8);
                    output.write("\",\"branch_pc\":\"");
                    hex(branch, 8);
                    // The observer accepts only the fixed set of comparison mnemonics.
                    output.write("\",\"mnemonic\":\"");
                    output.write(mnemonic);
                    output.write("\",\"width_bits\":");
                    integer(width);
                    output.write(",\"left\":\"");
                    operand(left, width / 4);
                    output.write("\",\"right\":\"");
                    operand(right, width / 4);
                    output.write("\"}");
                }
                catch (IOException e) {
                    throw new JsonIOException(e);
                }
            }

            void addIndex(long pc, long base, long index, int scale, long effective, int width, String access) {
                try {
                    beginRow();
                    output.write("{\"pc\":\"");
                    hex(pc, 8);
                    output.write("\",\"base\":\"");
                    hex(base, 8);
                    output.write("\",\"index\":\"");
                    hex(index, 8);
                    output.write("\",\"scale\":");
                    integer(scale);
                    output.write(",\"effective_address\":\"");
                    hex(effective, 8);
                    output.write("\",\"access_width_bits\":");
                    integer(width);
                    // The bus callbacks supply only load/store/branch.
                    output.write(",\"access\":\"");
                    output.write(access);
                    output.write("\"}");
                }
                catch (IOException e) {
                    throw new JsonIOException(e);
                }
            }

            private long position() throws IOException {
                if (output == null) return 0;
                output.flush();
                return spool.position();
            }

            private static JsonRows.Span range(long start, long end) {
                // Every row except the very first has a leading separator.
                return new JsonRows.Span(start > 0 && end > start ? start + 1 : start, end);
            }

            void beginTrial() throws IOException { trialStart = position(); }
            void endTrial() throws IOException { trials.add(range(trialStart, position())); }

            Segment checkpoint() throws IOException {
                long end = position();
                if (segmentStart != end) {
                    JsonRows.Span appended = range(segmentStart, end);
                    if (segments != null && segments.range.end + 1 == appended.start) {
                        // Include the spool's separator between adjacent ranges.
                        segments = new Segment(segments.previous, new JsonRows.Span(segments.range.start, end));
                    }
                    else segments = new Segment(segments, appended);
                    segmentStart = end;
                }
                return segments;
            }

            void restore(Segment snapshot) throws IOException {
                segments = snapshot;
                segmentStart = position();
            }

            private void transfer(JsonRows.Span range, FileChannel report) throws IOException {
                for (long at = range.start; at < range.end;) {
                    long copied = spool.transferTo(at, range.end - at, report);
                    if (copied == 0) throw new IOException("incomplete observation spool: " + path);
                    at += copied;
                }
            }

            void writeTo(JsonWriter writer, FileChannel report, int trial) throws IOException {
                writer.beginArray();
                if (trial >= 0) {
                    JsonRows.Span range = trials.get(trial);
                    if (range.start < range.end) {
                        writer.flush();
                        transfer(range, report);
                    }
                }
                else {
                    Segment segment = checkpoint();
                    if (segment != null) {
                        ArrayDeque<JsonRows.Span> ranges = new ArrayDeque<>();
                        for (; segment != null; segment = segment.previous) ranges.push(segment.range);
                        writer.flush();
                        transfer(ranges.pop(), report);
                        if (!ranges.isEmpty()) {
                            var comma = java.nio.ByteBuffer.wrap(new byte[] {','});
                            do {
                                comma.rewind();
                                while (comma.hasRemaining()) report.write(comma);
                                transfer(ranges.pop(), report);
                            } while (!ranges.isEmpty());
                        }
                    }
                }
                writer.endArray();
            }

            @Override
            public void close() throws IOException {
                try {
                    if (output != null) output.close();
                    else if (spool != null) spool.close();
                }
                finally {
                    if (path != null) Files.deleteIfExists(path);
                }
            }
        }

        private static final class WrittenBytes {
            // All scalar and native accesses share this exact byte coverage.
            // Slot zero is the hash mask; each entry is a 64-byte word key + bits.
            // Zero keys are vacant. Native can update existing words; only Java
            // inserts and resizes, after a downcall.
            private static final long HASH_MULTIPLIER = 0x9e3779b97f4a7c15L;
            private long[] cells;
            private MemorySegment segment;
            private int words;

            WrittenBytes() {
                reset(new long[1 + 2 * 16], 0);
            }

            private void reset(long[] storage, int count) {
                cells = storage;
                cells[0] = (cells.length >>> 1) - 1;
                segment = MemorySegment.ofArray(cells);
                words = count;
            }

            private int slot(long key) {
                int mask = (int) cells[0];
                int i = (int) ((key * HASH_MULTIPLIER) >>> 32) & mask;
                for (;; i = (i + 1) & mask) {
                    int slot = 1 + 2 * i;
                    long old = cells[slot];
                    if (old == 0 || old == key) return slot;
                }
            }

            private void grow() {
                long[] old = cells;
                reset(new long[2 * old.length - 1], words);
                for (int i = 1; i < old.length; i += 2) {
                    long key = old[i];
                    if (key == 0) continue;
                    int slot = slot(key);
                    cells[slot] = key;
                    cells[slot + 1] = old[i + 1];
                }
            }

            boolean markOrCovers(long address, int size, boolean mark) {
                while (size > 0) {
                    long key = (address >>> 6) + 1;
                    int first = (int) address & 63;
                    int length = Math.min(size, Long.SIZE - first);
                    long bits = length == Long.SIZE ? -1L : ((1L << length) - 1) << first;
                    int slot = slot(key);
                    if (mark) {
                        if (cells[slot] == 0) {
                            if (words > (int) cells[0] / 2) {
                                grow();
                                slot = slot(key);
                            }
                            cells[slot] = key;
                            words++;
                        }
                        cells[slot + 1] |= bits;
                    }
                    else if ((cells[slot + 1] & bits) != bits) return false;
                    address += length;
                    size -= length;
                }
                return true;
            }

            void restore(long[] snapshot, int count) {
                reset(snapshot.clone(), count);
            }

            void clear() {
                reset(new long[1 + 2 * 16], 0);
            }
        }
        static final class Checkpoint {
            final long instructions;
            final int instructionTraceSize;
            final InstructionSegment instructionSegments;
            final List<JsonObject> instructionShortcuts;
            final ObservationRows.Segment compareRows;
            final ObservationRows.Segment indexRows;
            final TupleKeys compareKeys;
            final TupleKeys indexKeys;
            final long[] recentPcs;
            final int recentNext;
            final int recentSize;
            final ExecutedPcs executed;
            final Map<String, Long> syncCounts;
            final long[] writtenCells;
            final int writtenWords;
            final boolean traceLostAddress;
            final String busInitiator;
            final JsonRows.Counters memoryCounters;
            final JsonRows.Counters eventCounters;
            Checkpoint(Trace trace) throws IOException {
                instructions = trace.instructions;
                instructionTraceSize = trace.instructionTraceSize;
                instructionSegments = trace.instructionRows.checkpoint();
                instructionShortcuts = List.copyOf(trace.instructionShortcuts);
                recentPcs = trace.copyRecentPcs();
                recentNext = trace.recentNext;
                recentSize = trace.recentSize;
                executed = trace.executed.copy();
                compareRows = trace.compareOperands.checkpoint();
                indexRows = trace.tableIndices.checkpoint();
                compareKeys = trace.compareKeys.copy();
                indexKeys = trace.indexKeys.copy();
                syncCounts = new LinkedHashMap<>(trace.syncCounts);
                writtenCells = trace.writtenBytes.cells.clone();
                writtenWords = trace.writtenBytes.words;
                traceLostAddress = trace.traceLostAddress;
                busInitiator = trace.busInitiator;
                memoryCounters = trace.memoryAccesses.checkpointCounters();
                eventCounters = trace.deviceEvents.checkpointCounters();
            }
        }

        Checkpoint checkpoint() throws IOException {
            return new Checkpoint(this);
        }

        void restore(Checkpoint checkpoint) throws IOException {
            instructions = checkpoint.instructions;
            instructionTraceSize = checkpoint.instructionTraceSize;
            instructionRows.restore(checkpoint.instructionSegments);
            instructionShortcuts.clear();
            instructionShortcuts.addAll(checkpoint.instructionShortcuts);
            compareOperands.restore(checkpoint.compareRows);
            tableIndices.restore(checkpoint.indexRows);
            compareKeys = checkpoint.compareKeys.copy();
            indexKeys = checkpoint.indexKeys.copy();
            System.arraycopy(checkpoint.recentPcs, 0, recentPcs, recentOffset, RECENT_PC_COUNT);
            recentNext = checkpoint.recentNext;
            recentSize = checkpoint.recentSize;
            executed = checkpoint.executed.copy();
            syncCounts.clear();
            syncCounts.putAll(checkpoint.syncCounts);
            writtenBytes.restore(checkpoint.writtenCells, checkpoint.writtenWords);
            traceLostAddress = checkpoint.traceLostAddress;
            busInitiator = checkpoint.busInitiator;
            memoryAccesses.restoreCounters(checkpoint.memoryCounters);
            deviceEvents.restoreCounters(checkpoint.eventCounters);
        }

        void beginTrial(boolean captureRows, List<String> eventKinds) throws IOException {
            memoryAccesses.beginTrial(captureRows && eventKinds == null, null);
            deviceEvents.beginTrial(captureRows, eventKinds);
            instructionRows.beginTrial();
            compareOperands.beginTrial();
            tableIndices.beginTrial();
        }

        JsonObject endTrial() throws IOException {
            memoryAccesses.endTrial();
            JsonObject eventKindCounts = deviceEvents.endTrial();
            instructionRows.endTrial();
            compareOperands.endTrial();
            tableIndices.endTrial();
            return eventKindCounts;
        }
    }

    // The payload is immutable after deserialization. Keep scheduling state in
    // the queue instead of cloning or modifying every scenario event on restore.
    record WireInput(long trigger, long ordinal, ExternalEvent payload, long repeat, long stride) {}

    static final class WireInputs {
        final List<WireInput> rows = new ArrayList<>();
        final List<WireInput> patterns = new ArrayList<>();
        int next;
        boolean unordered;

        void add(long trigger, long ordinal, ExternalEvent payload) {
            long repeat = payload.repeat == null ? 1 : payload.repeat;
            long stride = payload.stride_words == null ? 1 : payload.stride_words;
            if (payload.repeat_forever || repeat != 1) {
                patterns.add(new WireInput(
                    trigger, ordinal, payload, payload.repeat_forever ? Long.MAX_VALUE : repeat, stride));
                return;
            }
            if (next < rows.size() && trigger < rows.getLast().trigger) unordered = true;
            rows.add(new WireInput(trigger, ordinal, payload, 1, 1));
        }

        // A reset restarts the serial timeline the words are counted against.
        void clear() {
            rows.clear();
            patterns.clear();
            next = 0;
            unordered = false;
        }

        WireInput take(long trigger) {
            if (unordered) {
                rows.subList(next, rows.size()).sort(Comparator.comparingLong(WireInput::trigger));
                unordered = false;
            }
            if (next != rows.size() && rows.get(next).trigger == trigger) return rows.get(next++);
            WireInput match = null;
            for (int i = 0; i < patterns.size(); i++) {
                WireInput pattern = patterns.get(i);
                if (trigger < pattern.trigger) continue;
                long delta = trigger - pattern.trigger;
                if (delta % pattern.stride != 0 || delta / pattern.stride >= pattern.repeat) continue;
                if (match != null)
                    throw new IllegalStateException("multiple CSIH wire inputs at transmit word " + trigger);
                match = pattern;
            }
            return match;
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
        static final long RSCFD_RAM_INITIALIZATION_CYCLES = 3794;

        final SleighLanguage language;
        final boolean bigEndian;
        final MachineSpec spec;
        final Trace trace;
        // Shared-memory callbacks have no thread; retain PE1 for fault provenance.
        PcodeThread<byte[]> executionThread;
        final List<RegionDef> regions;
        final List<RegisterDef> registers;
        // Immutable address definitions; lookaside entries hold no guest state.
        final RegionDef[] regionCache = new RegionDef[64];
        // Sparse byte-lane decode for the immutable, address-sorted SFR catalog.
        final RegisterDef[][][] registerPages = new RegisterDef[256][][];
        final int[] registerPageBase = new int[256];
        interface MpuDescriptor {
            long attributes();
            // Low word is MPLA, high word is MPUA; inspect in that order.
            long bounds();
        }

        private record StateMpuDescriptor(Model model, PcodeThread<byte[]> thread,
                Register attributeRegister, Register lowerRegister, Register upperRegister)
                implements MpuDescriptor {
            @Override
            public long attributes() {
                return model.processorRegister(thread, attributeRegister);
            }

            @Override
            public long bounds() {
                return model.processorRegister(thread, lowerRegister)
                    | (model.processorRegister(thread, upperRegister) << 32);
            }
        }
        final MpuDescriptor[] mpu = new MpuDescriptor[16];
        final int[] mpuHints = new int[64];
        final Map<String, RegisterDef> registersByName = new HashMap<>();
        final RegisterDef segFlagRegister, ipgEnableRegister;
        final Map<Integer, RegisterDef> interruptRegisters = new LinkedHashMap<>();
        final RegisterDef[] interruptRegistersByAddress;
        final BitSet pendingInterrupts;
        final byte[] pendingPriorities; // -1 if masked or no longer asserted; indexed by EIC
        final BitSet[] channelsByPriority = new BitSet[16];
        int pendingPriorityMask;
        final ArrayDeque<Integer> activeInterruptChannels = new ArrayDeque<>();
        final Map<Integer, ReceiveFifo> receiveFifos = new HashMap<>();
        final Map<Long, RegisterDef> pendingRscfdTransmits = new HashMap<>();
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
        record PortPinField(RegisterDef source, int column, int aliasMask, long pins) {}
        record PortPinAlias(RegisterDef register, long pinMask, PortPinField[] fields,
                int overwrittenColumns) {}
        record PortBindings(PortPinAlias[] pinAliases, PortPinAlias[][] dependents,
                RegisterDef[] maskedTargets) {}
        final PortBindings portBindings;
        final long[] portColumnValues = new long[PORT_PIN_BITS.length];
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
        final RegisterDef[][] ecmStatus, ecmNotification;
        final RegisterDef[] ecmErrorMask;
        final RegisterDef checkerPmc, checkerPm, checkerPipc, checkerPfcae,
            checkerPfce, checkerPfc, checkerPbdc, checkerPibc, checkerPinv;
        final Tauj tauj;
        final Taud taud;
        final Tsg tsg;
        final Pic1 pic1;
        final Set<String> declaredTsgRegisters = new HashSet<>();
        RegionDef dataFlash;
        final PriorityQueue<ScheduledEvent> externalEvents = new PriorityQueue<>(ScheduledEvent.ORDER);
        final Map<String, Csih> csihControllers = new HashMap<>();
        final List<ExternalEvent> resetRelativeEvents = new ArrayList<>();
        ResetReplay resetReplay;
        EventSocket eventSocket;
        final Csih[] csihBindings;
        long registerBeforeWrite;
        boolean guardWriteIgnored;
        final RegisterDef[][] gramGuards = new RegisterDef[8][4];
        private record BusGuard(String name, RegisterDef read, RegisterDef readSpid,
                RegisterDef write, RegisterDef writeSpid, GuardCapture capture) {}
        final BusGuard[] peripheralGuards;
        final BusGuard dataFlashGuard;
        // Action bits are ordered by the device effects of a single bus read.
        private static final int READ_FACI_COMMAND = 1, READ_CSIH_BIND = 1 << 1,
            READ_CSIH_RX = 1 << 2, READ_CSIH_TX = 1 << 3, READ_ADC = 1 << 4,
            READ_ADC_SELECTOR = 1 << 5, READ_TAUJ = 1 << 6, READ_TAUD = 1 << 7,
            READ_TSG = 1 << 8, READ_RSENT = 1 << 9, READ_FACI_STATUS = 1 << 10,
            READ_PORT_PIN = 1 << 11, READ_PORT_MASKED = 1 << 12, READ_CVM = 1 << 13,
            READ_PORT_INPUT = 1 << 14, READ_MODE_LATCH = 1 << 15, READ_ECMPS = 1 << 16,
            READ_DCRA_SEED = 1 << 17, READ_PRIVILEGED = 1 << 18;
        private static final int COMPLETE_ADC_READ = 1, COMPLETE_RSENT_READ = 2;
        final GuardCapture pegCapture;
        final GuardCapture gramDmaCapture;
        final Dma dma;
        final Adc adc;
        final Rsent rsent;
        long hsbCyclesPerInstruction;
        long hsbCycles;
        // Exclusive absolute endpoint of the proven quiet span; zero invalidates the proof.
        private long quietUntil;
        private int quietClockEvents;
        private static final int QUIET_ADC_DUE = 1;
        private static final int QUIET_RSENT_DUE = 2;
        private static final int QUIET_TSG_KNOWN = 4;
        private static final int QUIET_TSG_DUE = 8;
        // Cached deadlines: zero is unknown, -1 is no edge. A finite
        // deadline may wrap past MAX: subtracting the current HSB tick recovers
        // the remaining span without conflating a real edge at MAX with "never".
        private static final long NO_CLOCK_EDGE = -1;
        private long taudClockTick, taujClockTick, rsentClockTick;
        private long taudClockDue, taujClockDue, rsentClockDue = -1;
        // An asynchronous mutation must cross one ordinary instruction boundary before
        // decoded instructions can retire without their model callbacks.
        private boolean idleBatchBarrier = true;
        private long lastRetiredPc = -1;
        private Instruction pollTest;
        private long pollReadTick, pollReadAddress;

        private void invalidateBatchProof() {
            idleBatchBarrier = true;
            pollTest = null;
        }
        boolean compareOperands;
        boolean inputDerivedTableIndices;
        boolean discardBusStore;
        long segFlags;
        boolean segNotificationPending;
        int faciPendingCommand;
        long faciReadErrors;
        long faciDeadline = Long.MAX_VALUE;
        long rscfdRamInitDeadline = RSCFD_RAM_INITIALIZATION_CYCLES;
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
        static final int MISSING_RESET_INPUT = 1;
        static final int DEVICE_REGISTER_INITIALIZED = 2;
        final byte[] registerState;
        int missingResetInputCount;
        Dma.WordIndex dmaWordIndex;
        // Scenario-supplied bus data is not command storage or effective device state.
        Map<String, Long> readInputResponses;
        boolean fieldBistExecuted;
        long resetFactorKnownMask;
        long unresolvedResetCauses;
        final Map<String, List<RegionDef>> aliases = new HashMap<>();
        long nextScheduledTick = Long.MAX_VALUE;
        final PriorityQueue<ScheduledEvent> scheduledEvents = new PriorityQueue<>(ScheduledEvent.ORDER);
        long nextEventOrdinal;
        PcodeMachine<byte[]> emulator;
        AddressSpace memorySpace;
        boolean peripheralFile;
        private P1MEJitMachine.MachineState deviceState;
        boolean peripheralPollBusy;
        static final int PERIPHERAL_POLL_READS = 4096;
        // Peripheral-file mode advances ICCTRL on reads.
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
            this.bigEndian = language.isBigEndian();
            this.spec = spec;
            this.trace = trace;
            this.regions = new ArrayList<>(spec.manual.regions);
            this.registers = new ArrayList<>(spec.manual.registers);
            this.registers.addAll(spec.target_derived.registers);
            regions.sort(Comparator.comparingLong(row -> row.start));
            for (int i = 0; i < regions.size(); i++)
                regions.get(i).lookupEnd = i + 1 < regions.size() ? regions.get(i + 1).start : 1L << 32;
            for (RegisterDef register : registers) {
                registersByName.put(register.name, register);
                if ("intc_eic".equals(register.behavior)) {
                    if (register.interrupt_channel == null) {
                        throw new IllegalArgumentException(register.name + " lacks interrupt channel metadata");
                    }
                    interruptRegisters.put(register.interrupt_channel, register);
                }
            }
            interruptRegistersByAddress = interruptRegisters.values().toArray(RegisterDef[]::new);
            Arrays.sort(interruptRegistersByAddress, Comparator.comparingLong(row -> row.address));
            pendingInterrupts = new BitSet(interruptRegistersByAddress.length);
            pendingPriorities = new byte[interruptRegistersByAddress.length];
            Arrays.fill(pendingPriorities, (byte) -1);
            Arrays.setAll(channelsByPriority, ignored -> new BitSet());
            segFlagRegister = registersByName.get("SEGFLAG");
            ipgEnableRegister = registersByName.get("IPGENUM");
            resetFactorKnownMask = requiredRegister("reset controller", "status", "RESF").reset_mask;
            registers.sort(Comparator.comparingLong(row -> row.address));
            csihBindings = new Csih[registers.size()];
            for (int i = 0; i < registers.size(); i++) {
                RegisterDef register = registers.get(i);
                register.bindingIndex = i;
                register.nameBinding = registersByName.get(register.name);
                register.lookupEnd = i + 1 < registers.size() ? registers.get(i + 1).address : 1L << 32;
                bindBusWrite(register);
            }
            int irq = 0;
            for (RegisterDef register : registers) {
                while (irq < interruptRegistersByAddress.length &&
                        interruptRegistersByAddress[irq].address + interruptRegistersByAddress[irq].size <= register.address) irq++;
                register.pendingBinding = -1;
                if (irq < interruptRegistersByAddress.length) {
                    RegisterDef eic = interruptRegistersByAddress[irq];
                    long end = register.address + register.size;
                    if (eic.address < end) register.pendingBinding = eic == register &&
                        (irq + 1 == interruptRegistersByAddress.length || interruptRegistersByAddress[irq+1].address >= end) ? irq : -2;
                }
            }
            bindRegisterPages();
            registerState = new byte[registers.size()];
            portBindings = bindPortAliases();
            // A missing optional definition must still fail at its original use.
            ecmStatus = bindRegisterRows(ECM_STATUS_REGISTERS);
            ecmNotification = bindRegisterRows(ECM_NOTIFICATION_REGISTERS);
            ecmErrorMask = bindRegisterNames(ECM_ERROR_MASK_REGISTERS);
            checkerPmc = registersByName.get("PMC3");
            checkerPm = registersByName.get("PM3");
            checkerPipc = registersByName.get("PIPC3");
            checkerPfcae = registersByName.get("PFCAE3");
            checkerPfce = registersByName.get("PFCE3");
            checkerPfc = registersByName.get("PFC3");
            checkerPbdc = registersByName.get("PBDC3");
            checkerPibc = registersByName.get("PIBC3");
            checkerPinv = registersByName.get("PINV3");
            int registerIndex = 0;
            for (RegionDef region : regions) {
                while (registerIndex < registers.size()
                        && registers.get(registerIndex).address
                            + registers.get(registerIndex).size <= region.start) {
                    registerIndex++;
                }
                boolean registerOverlap = registerIndex < registers.size()
                    && registers.get(registerIndex).address < region.end_exclusive;
                region.directPageWrites = region.access.contains("w") && !registerOverlap
                    && !"pbg0_unimplemented_channels8_9".equals(region.name)
                    && !region.name.startsWith("codeflash") && !"dataflash".equals(region.name);
                boolean ram = "local_ram".equals(region.alias_group) || "global_ram".equals(region.name);
                region.templateRam = ram;
                region.templateReads = !registerOverlap && region.access.contains("r") &&
                    (ram || region.name.startsWith("codeflash"));
                region.templateWrites = ram && region.directPageWrites;
                if ("dataflash".equals(region.name)) dataFlash = region;
                if (region.alias_group != null) {
                    aliases.computeIfAbsent(region.alias_group, ignored -> new ArrayList<>()).add(region);
                }
            }
            for (List<RegionDef> group : aliases.values()) {
                if (group.size() == 2 && group.get(0).templateWrites && group.get(1).templateWrites) {
                    group.get(0).templateMirror = group.get(1);
                    group.get(1).templateMirror = group.get(0);
                }
                else if (group.size() > 1) {
                    for (RegionDef region : group) region.templateWrites = false;
                }
            }
            String[] guardNames = new String[registers.size()];
            for (RegisterDef register : registers) {
                // These handlers can change the next HSB edge or synthesize a PIC edge.
                // CSIH can arm DMA indirectly; DMA's idle-to-armed transition invalidates
                // the proof itself. Other scheduler events are bounded separately.
                register.changesClockSchedule = switch (register.writeDevice) {
                    case TAUJ, TAUD, TSG, PIC_TAUD, PIC_TSG, PIC1_START, PDMA, ADC, RSENT -> true;
                    default -> register.writeTrigger == WriteTrigger.FACI_COMMAND
                        || register.writeTrigger == WriteTrigger.ICUS_COMMAND;
                };
                if (register.window_register != null) {
                    receiveFifos.put(register.fifo_index, new ReceiveFifo(this, register));
                }
                guardNames[register.bindingIndex] = peripheralReadGuard(register);
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
            peripheralGuards = new BusGuard[registers.size()];
            Map<String, BusGuard> guardBindings = new HashMap<>();
            for (int i = 0; i < guardNames.length; i++) {
                String guard = guardNames[i];
                if (guard == null) continue;
                BusGuard binding = guardBindings.get(guard);
                if (binding != null) {
                    peripheralGuards[i] = binding;
                    continue;
                }
                GuardCapture capture;
                if (guard.startsWith("APBFSGD"))
                    capture = guard.contains("PDMA") || guard.contains("INTC2") ? pfss0 : pfss1;
                else if (guard.startsWith("FSGD0")) capture = pbg0;
                else if (guard.startsWith("FSGD1")) capture = pbg1;
                else if (guard.startsWith("FSGD2")) capture = pbg2;
                else if (guard.startsWith("FSGD5")) capture = pbg5;
                else throw new IllegalStateException("unmapped guard capture bank: " + guard);
                peripheralGuards[i] = binding = bindBusGuard(guard, capture);
                guardBindings.put(guard, binding);
            }
            dataFlashGuard = guardBindings.computeIfAbsent("FSGD0PROT04", name -> bindBusGuard(name, pbg0));
            dma = new Dma();
            adc = new Adc(productId);
            taud = new Taud();
            tauj = new Tauj();
            tsg = new Tsg();
            pic1 = new Pic1();
            rsent = new Rsent();
            for (RegisterDef register : registers) bindBusRead(register);
            for (RegisterDef register : registers) bindBusWriteCompletion(register);
        }

        private static void bindBusWrite(RegisterDef register) {
            // These are independent: behavior supplies the device, while a trigger
            // may impose an additional check, snapshot, or effect (e.g. FACI/ECC).
            WriteDevice device = register.writeDevice = WriteDevice.bind(register.behavior);
            WriteTrigger trigger = register.writeTrigger = WriteTrigger.bind(register.trigger);
            register.busWritable = register.access != null && register.access.contains("w");
            register.validateBusWrite = switch (device) {
                case TAUJ, TAUD, PIC_TAUD, TSG, PIC_TSG, PIC1_START,
                        IPG, GRAM_BUFFER, PERIPHERAL_ECC, NOISE_FILTER, FLMD, DCRA -> true;
                default -> switch (trigger) {
                    case PDMA_COMPARATOR, BIST_CONTROL, CLOCK_DIVIDER, CLOCK_SELECTOR,
                            FACI_COMMAND, FACI_ENABLE, FACI_ADDRESS, FACI_DATAFLASH_MODE,
                            FACI_NORMAL_EMULATION, DATAFLASH_READ_CYCLE, ICUS_COMMAND,
                            ICUS_CONTROL, RSCFD_TRANSMIT -> true;
                    default -> false;
                };
            };
            register.snapshotWriteBacking = (device == WriteDevice.INTC_EIC && register.reset != null)
                || switch (trigger) {
                    case FACI_ADDRESS, FACI_DATAFLASH_MODE, FACI_ACCESS_STATUS, FACI_SETUP_INITIALIZE,
                            FACI_AREA_SELECTOR, FACI_CLOCK_NOTIFY, ECC_PROTECTED_CONTROL,
                            RSCFD_FD_STATUS, FLMD_CONTROL -> true;
                    default -> false;
                };
        }

        private void bindBusWriteCompletion(RegisterDef register) {
            if (isGuard(register)) {
                long address = switch (register.writeDevice) {
                    case PEG -> (register.address & ~15L) + 4;
                    case GRAM_GUARD -> register.address & ~15L;
                    default -> register.address & ~7L;
                };
                RegisterDef lock = register(address, 4);
                register.guardLockBinding = lock != null && isGuard(lock) ? lock : null;
            }
            ReceiveFifo fifo = register.fifo_index == null ? null : receiveFifos.get(register.fifo_index);
            register.fifoBusWrite = fifo != null &&
                (register == fifo.status || register == fifo.control || register == fifo.pointer);
            register.snapshotWriteBacking |= fifo != null && register == fifo.status;
            register.completesBusWrite = register.fifoBusWrite || register.writeTrigger != WriteTrigger.NONE
                || switch (register.writeDevice) {
                    case IPG, GRAM_BUFFER, FLMD, DCRA, NONE -> false;
                    default -> true;
                };
        }

        private void bindBusRead(RegisterDef register) {
            String behavior = register.behavior == null ? "" : register.behavior;
            String trigger = register.trigger == null ? "" : register.trigger;
            int effects = switch (behavior) {
                case "csih" -> switch (trigger) {
                    case "dma-select" -> 0;
                    case "rx" -> READ_CSIH_RX;
                    case "tx", "tx-half" -> READ_CSIH_TX;
                    default -> READ_CSIH_BIND;
                };
                case "adc", "adc-clock" -> "adc-clock".equals(behavior) && register == adc.selectorStatus
                    ? READ_ADC_SELECTOR : READ_ADC;
                case "tauj" -> READ_TAUJ;
                case "taud" -> READ_TAUD;
                case "tsg" -> READ_TSG;
                case "rsent" -> READ_RSENT;
                case "cvm" -> register.active_mask != null && !"CVMDE".equals(register.name)
                    ? READ_CVM : 0;
                case "port-input" -> READ_PORT_INPUT;
                case "mode-latch" -> READ_MODE_LATCH;
                case "ipg" -> READ_PRIVILEGED;
                default -> 0;
            };
            effects |= switch (trigger) {
                case "faci-command" -> READ_FACI_COMMAND;
                case "faci-access-status" -> READ_FACI_STATUS;
                case "port-pin-alias" -> READ_PORT_PIN;
                case "port-masked-alias" -> READ_PORT_MASKED;
                case "dcra-seed" -> READ_DCRA_SEED;
                default -> 0;
            };
            if ("ECMPS".equals(register.name)) effects |= READ_ECMPS;
            register.busReadEffects = effects;
            register.busReadable = register.access != null && register.access.contains("r");
            boolean hardwareBacking = register.read_value == null && !register.read_input;
            register.passiveBusRead = hardwareBacking && register.busReadable
                && (effects & ~READ_CSIH_BIND) == 0;
            register.plainEicRead = hardwareBacking && "intc_eic".equals(behavior)
                && register.trigger == null;
            short widths = 0;
            if (register.access_widths == null) widths = -1; // Keep the metadata fault at use.
            else {
                for (int width = 1; width <= Long.BYTES; width <<= 1)
                    if (register.access_widths.contains(width)) widths |= 1 << width;
            }
            register.busWidths = widths;
            register.busReadCompletion = readCompletion(register.address,
                register.address + Math.max(0, register.size - 1));
        }

        private static byte readCompletion(long first, long last) {
            // Ownership supplies a whole register at bind time. Mark any possible
            // access start, including narrow lanes, regardless of behavior or alias name.
            if (last < Rsent.FIRST_RX_DATA) return 0;
            int effects = 0;
            if (first < Adc.END_ADDRESS && last >= Adc.FIRST_ADDRESS)
                effects |= COMPLETE_ADC_READ;
            if ((first <= Rsent.FIRST_RX_DATA && last >= Rsent.FIRST_RX_DATA)
                    || (first <= Rsent.SECOND_RX_DATA && last >= Rsent.SECOND_RX_DATA))
                effects |= COMPLETE_RSENT_READ;
            return (byte) effects;
        }

        private void completeBusRead(PcodeThread<byte[]> thread, RegisterDef register, long address, int size) {
            int effects = register == null ? readCompletion(address, address) : register.busReadCompletion;
            if ((effects & COMPLETE_ADC_READ) != 0) adc.readCompleted(thread, address, size);
            if ((effects & COMPLETE_RSENT_READ) != 0) rsent.readCompleted(thread, address, size);
        }

        void attach(PcodeMachine<byte[]> emulator) {
            this.emulator = emulator;
            this.memorySpace = language.getDefaultSpace();
            if (emulator.getSharedState() instanceof P1MEJitMachine.MachineState state) {
                deviceState = state;
                dmaWordIndex = dma.watchWords(state);
            }
        }

        long scheduleNextTick(Runnable action) {
            return scheduleAt(trace.instructions + 1, action);
        }

        long scheduleAt(long tick, Runnable action) {
            scheduledEvents.add(new ScheduledEvent(tick, nextEventOrdinal++, action));
            nextScheduledTick = Math.min(nextScheduledTick, tick);
            return tick;
        }

        void dispatchDueEvents() {
            if (trace.instructions < nextScheduledTick) return;
            ScheduledEvent next = scheduledEvents.peek();
            if (next == null || next.tick > trace.instructions) return;
            invalidateBatchProof();
            invalidateClockHorizon();
            do {
                Runnable action = scheduledEvents.remove().action;
                next = scheduledEvents.peek();
                nextScheduledTick = next == null ? Long.MAX_VALUE : next.tick;
                action.run();
                next = scheduledEvents.peek();
            } while (next != null && next.tick <= trace.instructions);
        }

        private static long instructionsBefore(PriorityQueue<ScheduledEvent> events, long tick) {
            ScheduledEvent next = events.peek();
            if (next == null) return Long.MAX_VALUE;
            if (next.tick <= tick) return 0;
            return next.tick - tick - 1;
        }

        private long quietBatchLimit(long instructionLimit, long maximum) {
            return batchLimit(instructionLimit, maximum, false, false);
        }

        private long nextBusClockEdge(long adcDeadline, long rsentDeadline) {
            long next = Math.min(adcDeadline, Math.min(rsentDeadline, dma.cyclesUntilEvent()));
            if (faciDeadline != Long.MAX_VALUE) next = Math.min(next, faciDeadline - hsbCycles);
            if (icusStartupStub != null && icusStartupStub.deadline != Long.MAX_VALUE)
                next = Math.min(next, icusStartupStub.deadline - hsbCycles);
            if (rscfdRamInitDeadline != Long.MAX_VALUE) next = Math.min(next, rscfdRamInitDeadline - hsbCycles);
            return next;
        }

        private void setClockHorizon(long bound, long adc, long rsent, long tsg) {
            quietUntil = hsbCycles + bound;
            if (quietUntil != Long.MAX_VALUE) quietClockEvents = clockEventMask(bound, adc, rsent, tsg);
        }

        private void openClockLease() {
            if (quietUntil != 0 || taudClockDue == 0 || taujClockDue == 0 ||
                    taud.picDirty || tsg.picDirty || tsg.picRoutingDeferred || tsg.clockHorizonDirty || rsentClockDue < 0) return;
            long adcDeadline;
            try { adcDeadline = adc.cyclesUntilEvent(); }
            catch (ArithmeticException overflow) { return; }
            long rsentDeadline = rsentCyclesUntilEvent();
            long tsgDeadline = tsg.cyclesUntilEvent(hsbCycles);
            long next = nextBusClockEdge(adcDeadline, rsentDeadline);
            next = Math.min(next, Math.min(tsgDeadline, Math.min(taujCyclesUntilEvent(), taudCyclesUntilEvent())));
            long bound = Math.min(next, Long.MAX_VALUE - hsbCycles);
            if (bound <= 1 || hsbCyclesPerInstruction > (bound - 1) / 2) return;
            setClockHorizon(bound, adcDeadline, rsentDeadline, tsgDeadline);
        }

        private long batchLimit(long instructionLimit, long maximum, boolean freshFetch, boolean retireEdge) {
            if ((!freshFetch && idleBatchBarrier) || segNotificationPending || eventSocket != null
                    || trace.recordsInstructionTrace()) return 0;
            long tick = trace.instructions;
            long remaining = instructionLimit - tick;
            if (remaining <= 1) return 0;
            // Leave the final budget boundary to the ordinary callback path. It
            // performs scheduled-event and fault ordering exactly once.
            long limit = Math.min(remaining - 1, maximum);
            limit = Math.min(limit, instructionsBefore(scheduledEvents, tick));
            limit = Math.min(limit, instructionsBefore(externalEvents, tick));
            if (hsbCyclesPerInstruction < 0)
                throw new IllegalStateException("negative CLK_HSB cycles per instruction");
            if (hsbCyclesPerInstruction != 0) {
                if ((freshFetch || retireEdge) && limit >= 2 && quietUntil == 0) openClockLease();
                long quiet = quietRemaining() / hsbCyclesPerInstruction;
                if (retireEdge && quiet < limit) quiet++;
                limit = Math.min(limit, quiet);
            }
            return Math.max(limit, 0);
        }

        long idleBatchLimit(long instructionLimit, long pc) {
            return pc == lastRetiredPc ? quietBatchLimit(instructionLimit, 1L << 20) : 0;
        }

        int instructionBatchLimit(long instructionLimit) {
            if ((trace.recordsInstructionMetadata()
                        && (compareOperands || inputDerivedTableIndices))
                    || peripheralFile || !boundedEdges.isEmpty()) return 0;
            return (int) batchLimit(instructionLimit, 256, true, true);
        }

        RegionDef templateData(PcodeThread<byte[]> thread, long address, int size,
                boolean write, int mode, MpuWindow mpu, MpuWindow transfer) {
            RegionDef region = region(address, size);
            if (region == null || !(write ? region.templateWrites : region.templateReads)) return null;
            if (mpuGrant(thread, address, size, write ? CpuAccess.WRITE : CpuAccess.READ, mode, mpu) <= 0)
                return null;
            transfer.set(Math.max(region.start, mpu.start),
                Math.min(Math.min(region.end_exclusive, region.lookupEnd), mpu.end));
            if (!transfer.covers(address, size)) return null;
            if (write && "global_ram".equals(region.name) &&
                    !templateGramWriteBounds(thread, address, size, transfer)) return null;
            return (mode & CPU_USER_MODE) != 0 && !userIpgAllows(region) ? null : region;
        }

        private boolean templateGramWriteBounds(PcodeThread<byte[]> thread, long address,
                int size, MpuWindow transfer) {
            int spid = cpuSpid(thread);
            for (RegisterDef[] guard : gramGuards) {
                long protection = guardValue(guard[0], true);
                if (protection < 0) return false;
                if ((protection & 0x40000000L) == 0) continue;
                long allowed = guardValue(guard[1], true);
                long base = guardValue(guard[2], true);
                long valid = guardValue(guard[3], true);
                if ((allowed | base | valid) < 0) return false;
                if ((allowed & (1L << spid)) != 0) continue;

                // Native admission checks natural alignment. A mismatched
                // masked bit above the lane index excludes every byte in its block.
                // If none differs, some lane of this transaction matches the guard.
                long bit = Long.highestOneBit((address ^ base) & valid & -((long) size));
                if (bit == 0) return false;
                long block = address & -bit;
                transfer.set(Math.max(transfer.start, block), Math.min(transfer.end, block + bit));
            }
            return true;
        }

        private void retireBatchClock(long instructions) {
            long cycles = Math.multiplyExact(instructions, hsbCyclesPerInstruction);
            if (cycles > quietRemaining())
                throw new IllegalStateException("batch crosses observable clock edge");
            hsbCycles = Math.addExact(hsbCycles, cycles);
        }

        // An instruction's bus effects precede its retirement clock. Only the final
        // guest may reach an edge; commit every earlier tick before that edge can fault.
        private void retireThroughEdge(long instructions) {
            if (hsbCyclesPerInstruction == 0 || instructions <= quietRemaining() / hsbCyclesPerInstruction) {
                retireBatchClock(instructions);
                return;
            }
            retireBatchClock(instructions - 1);
            retireClock(executionThread);
            dispatchDueEvents();
            deliverSystemError(executionThread);
        }

        void retireIdleBatch(long pc, long instructions) {
            if (instructions <= 0 || instructions > idleBatchLimit(Long.MAX_VALUE, pc))
                throw new IllegalStateException("idle batch exceeds scheduler boundary");
            trace.instructions = Math.addExact(trace.instructions, instructions);
            trace.recordExecutedPc(pc);
            int recent = (int) Math.min(instructions, 16);
            for (int i = 0; i < recent; i++) trace.noteRecentPc(pc);
            retireBatchClock(instructions);
        }

        private boolean repeatPoll(P1MEJitMachine.MachineThread thread, long instructionLimit,
                P1MEJitMachine.StopIndex stops, P1MEJitMachine.PolledBitLoop loop) {
            long pc = loop.testPc(), branchPc = loop.branchPc();
            if (stops.contains(pc) || stops.contains(branchPc) ||
                    (trace.recordsInstructionMetadata()
                        && (compareOperands || inputDerivedTableIndices)) || trace.retainsRead() ||
                    !((pendingPriorityMask == 0 && thread.interruptStatusAlreadyClear()) ||
                        thread.interruptDisabledAtBusBoundary())) return false;
            long limit = batchLimit(instructionLimit, 1L << 16, false, true);
            if (limit < 2) return false;
            long retired = thread.batchPolledBit(limit, loop, pollReadAddress);
            if (retired == 0) return false;
            trace.instructions = Math.addExact(trace.instructions, retired);
            for (int i = 0; i < Math.min(retired, Trace.RECENT_PC_COUNT); i += 2) {
                trace.noteRecentPc(pc);
                trace.noteRecentPc(branchPc);
            }
            retireThroughEdge(retired);
            return true;
        }

        void retireNativeBatch(int instructions) {
            idleBatchBarrier = false;
            trace.instructions = Math.addExact(trace.instructions, instructions);
            lastRetiredPc = trace.retireNativePcs(instructions);
            retireThroughEdge(instructions);
        }

        RegionDef region(long address, int size) {
            int slot = (int) (address >>> 12 ^ address >>> 20) & (regionCache.length - 1);
            RegionDef hit = regionCache[slot];
            if (hit != null && address >= hit.start && address < hit.lookupEnd)
                return hit.contains(address, size) ? hit : null;
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
            regionCache[slot] = region;
            return region.contains(address, size) ? region : null;
        }

        private void bindRegisterPages() {
            int[] last = new int[256];
            Arrays.fill(registerPageBase, 1 << 16);
            for (RegisterDef reg : registers) {
                long end = Math.min(reg.lookupEnd, reg.address + reg.size);
                for (long page = reg.address >>> 8; (page << 8) < end; page++) {
                    int bank = (int)(page >>> 16), slot = (int)page & 0xffff;
                    registerPageBase[bank] = Math.min(registerPageBase[bank], slot);
                    last[bank] = Math.max(last[bank], slot);
                }
            }
            for (int bank = 0; bank < 256; bank++) {
                if (last[bank] >= registerPageBase[bank])
                    registerPages[bank] = new RegisterDef[last[bank] - registerPageBase[bank] + 1][];
            }
            for (RegisterDef reg : registers) {
                long end = Math.min(reg.lookupEnd, reg.address + reg.size);
                for (long address = reg.address; address < end;) {
                    int bank = (int)(address >>> 24);
                    int slot = ((int)(address >>> 8) & 0xffff) - registerPageBase[bank];
                    RegisterDef[] lanes = registerPages[bank][slot];
                    if (lanes == null) registerPages[bank][slot] = lanes = new RegisterDef[256];
                    int lane = (int)address & 255;
                    int count = (int)Math.min(end - address, 256 - lane);
                    Arrays.fill(lanes, lane, lane + count, reg);
                    address += count;
                }
            }
        }

        RegisterDef register(long address, int size) {
            if ((address >>> 32) != 0 || size <= 0) return registerByPredecessor(address, size);
            int bank = (int)(address >>> 24);
            RegisterDef[][] pages = registerPages[bank];
            if (pages == null) return null;
            int slot = ((int)(address >>> 8) & 0xffff) - registerPageBase[bank];
            if (slot < 0 || slot >= pages.length || pages[slot] == null) return null;
            RegisterDef reg = pages[slot][(int)address & 255];
            return reg != null && reg.contains(address, size) ? reg : null;
        }

        private RegisterDef registerByPredecessor(long address, int size) {
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
            if (thread instanceof P1MEJitMachine.MachineThread jit) {
                return jit.processorRegister(name);
            }
            Register register = language.getRegister(name);
            if (register == null) {
                throw new IllegalStateException("processor model lacks register " + name);
            }
            return processorRegister(thread, register);
        }

        long processorRegister(PcodeThread<byte[]> thread, Register register) {
            if (thread instanceof P1MEJitMachine.MachineThread jit) return jit.processorRegister(register);
            byte[] value = thread.getState().getVar(register, Reason.INSPECT);
            return Utils.bytesToLong(value, value.length, language.isBigEndian()) & 0xffffffffL;
        }

        void bindMpu(PcodeThread<byte[]> thread) {
            for (int i = 0; i < mpu.length; i++) {
                Register attributes = language.getRegister("MPAT" + i);
                Register lower = language.getRegister("MPLA" + i);
                Register upper = language.getRegister("MPUA" + i);
                mpu[i] = thread instanceof P1MEJitMachine.MachineThread jit
                    ? jit.bindMpuDescriptor(attributes, lower, upper)
                    : new StateMpuDescriptor(this, thread, attributes, lower, upper);
            }
        }

        void processorRegister(PcodeThread<byte[]> thread, String name, long value) {
            if (thread instanceof P1MEJitMachine.MachineThread jit) {
                jit.processorRegister(name, value);
                return;
            }
            Register register = language.getRegister(name);
            if (register == null) throw new IllegalArgumentException("unknown processor register: " + name);
            thread.getState().setVar(register, bytes(value, register.getNumBytes(), language.isBigEndian()));
        }

        void noteBoundedCall(PcodeThread<byte[]> thread) {
            // A jarl into a rewritten loop saves the caller's frame. The
            // back-edge returns there after one iteration, as the host does.
            if (boundedEntries.isEmpty()) return;
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
            requestInterrupt(thread, channel, null);
        }

        void requestInterrupt(PcodeThread<byte[]> thread, int channel, String firmwareControl) {
            RegisterDef eic = interruptRegisters.get(channel);
            if (eic == null || (eic.reset == null && firmwareControl == null)) {
                throw fault("unsupported-interrupt", thread, channel, 0, "request", "manual",
                    "interrupt channel is not described by the device model");
            }
            long control = eic.reset == null
                ? parseUnsigned(firmwareControl)
                : registerValue(eic);
            setRegisterValue(eic.nameBinding, control | 0x1000);
            trace.deviceEvents.addInterruptRequest(channel, trace.instructions, eic.reset == null, control);
        }

        void deliverInterrupt(PcodeThread<byte[]> thread) {
            if (pendingPriorityMask == 0 && thread instanceof P1MEJitMachine.MachineThread jit
                    && jit.interruptStatusAlreadyClear()) return;
            long psw = processorRegister(thread, "PSW");
            if ((psw & 0xa0) != 0) return;
            int eligible = pendingPriorityMask;
            int serviced = 0, pmr = 0;
            if (eligible != 0) {
                serviced = (int) processorRegister(thread, "ISPR") & 0xffff;
                if (serviced != 0) eligible &= Integer.lowestOneBit(serviced) - 1;
                pmr = (int) processorRegister(thread, "PMR");
            }
            boolean priorityMasked = (eligible & pmr) != 0;
            long icsr = processorRegister(thread, "ICSR");
            if (((icsr & 1) != 0) != priorityMasked)
                processorRegister(thread, "ICSR", icsr ^ 1);
            eligible &= ~pmr;
            if (eligible == 0) return;
            int priority = Integer.numberOfTrailingZeros(eligible);
            int channel = channelsByPriority[priority].nextSetBit(0);
            RegisterDef selected = interruptRegisters.get(channel);
            long control = registerValue(selected);
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
            if ((control & 0x8000) == 0) setRegisterValue(selected.nameBinding, control & ~0x1000L);
            invalidateBatchProof();
            thread.overrideCounter(memorySpace.getAddress(handler));
            if (!trace.deviceEvents.omitsEventPayload("interrupt-enter")) {
                JsonObject event = new JsonObject();
                event.addProperty("kind", "interrupt-enter");
                event.addProperty("channel", selected.interrupt_channel);
                event.addProperty("priority", priority);
                event.addProperty("return_pc", hex32(returnPc));
                event.addProperty("handler", hex32(handler));
                event.addProperty("scheduler_tick", trace.instructions);
                trace.deviceEvents.add(event);
            }
            activeInterruptChannels.addLast(selected.interrupt_channel);
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
            if (size <= 1 || ((size & (size - 1)) == 0 && (address & (size - 1)) == 0)) return;
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

        /** A grant for one access kind and CPU mode, valid only during a quiet batch. */
        static final class MpuWindow {
            long start, end;

            void clear() {
                end = 0;
            }

            boolean covers(long address, int size) {
                return address >= start && address + size <= end;
            }

            void set(long start, long end) {
                this.start = start;
                this.end = end;
            }
        }

        // Mode packs PSW.UM in its high-byte position and MPM.MPE/SVP in bits 0/1.
        static final int CPU_USER_MODE = 0x40;
        private static final long MPU_ADDRESS_END = 0x1_0000_0000L;

        enum CpuAccess {
            READ("read", 0), WRITE("write", 1), EXECUTE("execute", 2);

            final String name;
            final int userPermission;

            CpuAccess(String name, int userPermission) {
                this.name = name;
                this.userPermission = userPermission;
            }
        }

        private boolean userMode(PcodeThread<byte[]> thread) {
            return thread instanceof P1MEJitMachine.MachineThread jit ? jit.processorUserMode() != 0
                : (processorRegister(thread, "PSW") & (1L << 30)) != 0;
        }

        private int protectionMode(PcodeThread<byte[]> thread) {
            if (thread instanceof P1MEJitMachine.MachineThread jit) return jit.processorProtectionMode();
            int user = userMode(thread) ? CPU_USER_MODE : 0;
            return user | ((int) processorRegister(thread, "MPM") & 3);
        }

        private long requireMpu(PcodeThread<byte[]> thread, long address, int size,
                CpuAccess access, int mode, MpuWindow window) {
            long grant = mpuGrant(thread, address, size, access, mode, window);
            if (grant > 0) return grant;
            throw mpuFault(thread, address, size, access.name, grant);
        }

        private MachineFault mpuFault(PcodeThread<byte[]> thread, long address, int size,
                String access, long grant) {
            return fault("mpu-" + access, thread, address, size, access,
                "manual:R01US0123EJ0140 sections 3.5 and 5.1",
                grant < 0 ? "all matching MPU regions deny " + access
                    : "MPU has no matching enabled region and G3M defaults deny access");
        }

        long mpuGrant(PcodeThread<byte[]> thread, long address, int size,
                CpuAccess access, int mode, MpuWindow window) {
            if (window != null && window.covers(address, size)) return window.end;
            if (!descriptorMpuEnabled(mode)) {
                if (window != null) window.set(0, MPU_ADDRESS_END);
                return MPU_ADDRESS_END;
            }
            int permission = access.userPermission + ((mode & CPU_USER_MODE) == 0 ? 3 : 0);
            return descriptorGrant(thread, address, size, permission, window);
        }

        static boolean descriptorMpuEnabled(int mode) {
            return (mode & 1) != 0 && (mode & (CPU_USER_MODE | 2)) != 0;
        }

        private long descriptorGrant(PcodeThread<byte[]> thread, long address, int size,
                int permission, MpuWindow window) {
            long last = address + Integer.toUnsignedLong(size) - 1;
            int asid = -1;
            int mask = 1 << permission;
            boolean matched = false;
            // Permission is the union of matching descriptors. A hint is only
            // an index: attributes, ASID, and bounds still come from live bytes.
            int slot = (int) (address >>> 12 ^ address >>> 20 ^ permission) & (mpuHints.length - 1);
            int first = mpuHints[slot];
            for (int i = 0; i < mpu.length; i++) {
                int index = (first + i) & 15;
                MpuDescriptor descriptor = mpu[index];
                long attributes = descriptor.attributes();
                if ((attributes & 0x80) == 0) continue;
                if ((attributes & 0x40) == 0) {
                    if (asid < 0) asid = thread instanceof P1MEJitMachine.MachineThread jit
                        ? jit.processorAsid() : (int) processorRegister(thread, "ASID") & 0x3ff;
                    if (((attributes >>> 16) & 0x3ff) != asid) continue;
                }
                long bounds = descriptor.bounds();
                long lower = bounds & 0xfffffffcL;
                long upper = (bounds >>> 32) | 3L;
                if (Long.compareUnsigned(address, lower) < 0
                        || Long.compareUnsigned(last, upper) > 0) continue;
                matched = true;
                if ((attributes & mask) != 0) {
                    mpuHints[slot] = index;
                    if (window != null) window.set(lower, upper + 1);
                    return upper + 1;
                }
            }
            return matched ? -1 : 0;
        }

        boolean isGuard(RegisterDef register) {
            return switch (register.writeDevice) {
                case PEG, BUS_GUARD, GRAM_GUARD -> true;
                default -> false;
            };
        }

        private RegisterDef guardLock(RegisterDef register) {
            RegisterDef lock = register.guardLockBinding;
            if (lock == null) {
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

        private BusGuard bindBusGuard(String name, GuardCapture capture) {
            RegisterDef read = registersByName.get(name);
            RegisterDef write = read == null ? null : register(read.address + 8, 4);
            return new BusGuard(name, read, read == null ? null : register(read.address + 4, 4),
                write, write == null ? null : register(write.address + 4, 4), capture);
        }

        private RegisterDef guardProtection(BusGuard guard, boolean write, String owner, String relation) {
            RegisterDef protection = write ? guard.write : guard.read;
            if (protection != null) return protection;
            // Preserve the original fault at access time for absent metadata.
            RegisterDef read = requiredRegister(owner, relation, guard.name);
            return write ? register(read.address + 8, 4) : read;
        }

        private RegisterDef guardSpid(BusGuard guard, RegisterDef protection, boolean write) {
            RegisterDef spid = write ? guard.writeSpid : guard.readSpid;
            return spid != null ? spid : register(protection.address + 4, 4);
        }

        void requireBusGuard(PcodeThread<byte[]> thread, BusGuard guard,
                             long address, int size, CpuAccess access) {
            boolean write = access == CpuAccess.WRITE;
            RegisterDef protection = guardProtection(guard, write, "P1M-E", "read guard");
            RegisterDef spid = guardSpid(guard, protection, write);
            // Table31.147: CPU is PEID1. PEID4 denotes DMA/DTS/FlexRay,
            // not a CPU privilege mode; this path never impersonates a master.
            if ((registerValue(protection) & (1L << 18)) == 0
                    || (registerValue(spid) & (1L << cpuSpid(thread))) == 0) {
                segError(thread, address, write ? 0x200L : 0x10L);
                if (write) {
                    discardBusStore = true;
                    return;
                }
                throw fault("unsupported-bus-guard-read", thread, address, size, access.name,
                    protection.evidence,
                    protection.name + " blocks access; error-response read data is unspecified");
            }
        }

        private long guardValue(RegisterDef register, boolean probe) {
            if (!probe) return registerValue(register);
            if (register == null || missingResetInput(register)) return -1;
            return deviceState.inspectInitializedDevice(register, bigEndian);
        }

        private boolean gramWriteAllowed(PcodeThread<byte[]> thread, long address, int size,
                boolean probe) {
            int spid = cpuSpid(thread);
            // Table31.153: every matching enabled region must permit every lane.
            for (RegisterDef[] guard : gramGuards) {
                long protection = guardValue(guard[0], probe);
                if (protection < 0) return false;
                if ((protection & 0x40000000L) == 0) continue;
                long valid = guardValue(guard[3], probe);
                long base = guardValue(guard[2], probe);
                long allowed = guardValue(guard[1], probe);
                if ((valid | base | allowed) < 0) return false;
                if ((allowed & (1L << spid)) != 0) continue;
                for (int lane = 0; lane < size; lane++) {
                    if (((address + lane) & valid) == (base & valid)) return false;
                }
            }
            return true;
        }

        // True means the entire mapped region is guard-free for this kind of access.
        boolean requireGuards(PcodeThread<byte[]> thread, long address, int size, CpuAccess access,
                              RegionDef region, RegisterDef target) {
            if (region != null && "global_ram".equals(region.name) && access == CpuAccess.WRITE) {
                if (!gramWriteAllowed(thread, address, size, false)) {
                    segError(thread, address, 0x10L);
                    discardBusStore = true;
                }
                return false;
            }
            if (region != null) {
                if ("dataflash".equals(region.name)) {
                    requireBusGuard(thread, dataFlashGuard, address, size, access);
                    return false;
                }
                return true;
            }
            if (target == null) return false; // Preserve the precise unmapped/width boundary.
            BusGuard guard = peripheralGuards[target.bindingIndex];
            if (guard != null) requireBusGuard(thread, guard, address, size, access);
            return false;
        }

        long segFlagValue() {
            return deviceRegisterInitialized(segFlagRegister)
                ? registerValue(segFlagRegister) & 0x354L : segFlags;
        }

        long enabledSegFlags() {
            return segFlagValue() & registerValue(registersByName.get("SEGCONT"));
        }

        void setSegFlags(long flags) {
            segFlags = flags & 0x354L;
            RegisterDef register = segFlagRegister;
            if (deviceRegisterInitialized(register)) {
                long reserved = registerValue(register) & ~0x354L;
                setRegisterValue(register, reserved | segFlags);
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
            invalidateBatchProof();
            thread.overrideCounter(memorySpace.getAddress(handler));
            JsonObject event = new JsonObject();
            event.addProperty("kind", "syserr-enter");
            event.addProperty("cause", hex32(cause));
            event.addProperty("return_pc", hex32(returnPc));
            event.addProperty("handler", hex32(handler));
            event.addProperty("evidence", "manual:R01US0123EJ0140 Tables4-1,4-4; R01UH0585EJ0120 Table3.80");
            trace.deviceEvents.add(event);
        }

        private RegisterDef requireAccessProtection(PcodeThread<byte[]> thread, long address, int size,
                CpuAccess access, RegionDef region) {
            int mode = protectionMode(thread);
            if (descriptorMpuEnabled(mode)) requireMpu(thread, address, size, access, mode, null);
            if (peripheralFile) return null;
            RegisterDef target = region == null ? register(address, size) : null;
            requireGuards(thread, address, size, access, region, target);
            if (discardBusStore && access == CpuAccess.WRITE) return null;
            if ((mode & CPU_USER_MODE) != 0) requireUserIpg(thread, address, size, access.name, region);
            return target;
        }

        private static boolean userIpgExempt(RegionDef region) {
            return region != null &&
                (region.name.startsWith("codeflash") || "local_ram".equals(region.alias_group));
        }

        private boolean userIpgAllows(RegionDef region) {
            long value = guardValue(ipgEnableRegister, true);
            return value >= 0 && ((value & 1) == 0 || userIpgExempt(region));
        }

        void requireUserIpg(PcodeThread<byte[]> thread, long address, int size, String access,
                            RegionDef region) {
            RegisterDef ipg = ipgEnableRegister;
            if (ipg == null) ipg = requiredRegister("P1M-E", "IPG enable", "IPGENUM");
            if ((registerValue(ipg) & 1) == 0 || userIpgExempt(region)) return;
            throw fault("unsupported-ipg-user-access", thread, address, size, access,
                ipg.evidence, "enabled IPG user-mode peripheral protection requires its group/violation model");
        }

        private void requireIpgRegisterPrivilege(PcodeThread<byte[]> thread, RegisterDef register, String access) {
            if (userMode(thread)) {
                throw fault("privileged-register-access", thread, register.address,
                    register.size, access, register.evidence, "IPG configuration requires supervisor mode");
            }
        }


        long requireExecute(PcodeThread<byte[]> thread, long address, int size) {
            return requireExecute(thread, address, size, protectionMode(thread), null);
        }

        long requireExecute(PcodeThread<byte[]> thread, long address, int size,
                int mode, MpuWindow window) {
            long mpuEnd = requireMpu(thread, address, size, CpuAccess.EXECUTE, mode, window);
            RegionDef region = region(address, size);
            boolean guardFree = peripheralFile || requireGuards(thread, address, size, CpuAccess.EXECUTE,
                region, region == null ? register(address, size) : null);
            if ((mode & CPU_USER_MODE) != 0 && !peripheralFile)
                requireUserIpg(thread, address, size, "execute", region);
            if (region == null || !region.executable) {
                throw fault("execute-unmapped", thread, address, size, "execute",
                    region == null ? "unknown" : region.evidence,
                    "instruction fetch outside an executable P1M-E region");
            }
            // IPG checks select whole regions. Do not reuse a size-specific bus-guard result.
            return guardFree ? Math.min(mpuEnd, region.end_exclusive) : 0;
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
                if ((previous & 1) == 0) setRegisterValue(information, context);
                setRegisterValue(status, previous | 1 | ((previous & 1) != 0 ? 2 : 0));
                latchEcmError(thread, source);
            }
        }

        boolean dmaBusGuard(PcodeThread<byte[]> thread, BusGuard guard, int spid, boolean write) {
            RegisterDef protection = guardProtection(guard, write, "DMAC", "bus guard");
            RegisterDef identities = guardSpid(guard, protection, write);
            // Tables31.159,31.166: the DMAC master is PEID4, independent
            // of both the CPU MPU and the channel owner's assigned PEID.
            if ((registerValue(protection) & (1L << 21)) != 0
                    && (registerValue(identities) & (1L << spid)) != 0) return true;
            guard.capture.record(thread, ((long) spid << 16) | 0x8000 | (write ? 1 : 0));
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
                    || dmaBusGuard(thread, dataFlashGuard, spid, write);
            }
            RegisterDef target = register(address, size);
            // Unknown peripheral behavior remains a precise model fault below;
            // it is not converted into a fabricated hardware transfer error.
            BusGuard guard = target == null ? null : peripheralGuards[target.bindingIndex];
            return guard == null || dmaBusGuard(thread, guard, spid, write);
        }

        private long readInputBits(RegisterDef register, long address, int size) {
            int lane = Math.toIntExact(address - register.address);
            int shift = 8 * (bigEndian ? register.size - lane - size : lane);
            return readInputResponses.get(register.name) >>> shift;
        }

        byte[] readInputLanes(RegisterDef register, long address, int size) {
            return bytes(readInputBits(register, address, size), size, bigEndian);
        }

        long readInputNumber(RegisterDef register, long address, int size) {
            if (size <= 0 || size > Long.BYTES)
                return Utils.bytesToLong(readInputLanes(register, address, size), size, bigEndian);
            return readInputBits(register, address, size) & (-1L >>> (Byte.SIZE * (Long.BYTES - size)));
        }

        byte[] dmaRead(PcodeThread<byte[]> thread, Dma.Channel channel, long address, int size) {
            String previous = trace.busInitiator;
            trace.busInitiator = channel.initiator;
            try {
                if (!dmaAccessAllowed(thread, channel, address, size, false)) return null;
                RegisterDef register = beforeRead(thread, address, size, false);
                if (register != null && register.read_input) return readInputLanes(register, address, size);
                byte[] result;
                if (size <= Long.BYTES && deviceState != null) {
                    long value = deviceState.readBusBacking(register, address, size, bigEndian, Reason.INSPECT);
                    if (channel.transferBuffer == null || channel.transferBuffer.length != size)
                        channel.transferBuffer = new byte[size];
                    result = channel.transferBuffer;
                    P1MEJitMachine.writeNumber(result, 0, size, bigEndian, value);
                }
                else result = memory(thread, address, size);
                completeBusRead(thread, register, address, size);
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
                return storeBus(thread, address, value.length, 0, value, false);
            } finally {
                trace.busInitiator = previous;
            }
        }

        long ecmLatchedStatus(RegisterDef status) {
            // Internal latches can inspect backing bits before the external pin is known.
            long value = deviceState != null && status.size <= Long.BYTES
                ? deviceState.inspectDevice(status, bigEndian) & 0xffffffffL
                : unsigned(emulator.getSharedState().getVar(
                    memorySpace, status.address, status.size, true, Reason.INSPECT));
            return missingResetInput(status) ? value & status.reset_mask : value;
        }

        void latchEcmError(PcodeThread<byte[]> thread, int source) {
            int index = source / 32;
            long bit = 1L << (source % 32);
            for (int route = 1; route < ecmNotification.length; route++) {
                RegisterDef configuration = ecmNotification[route][index];
                if ((registerValue(configuration) & bit) != 0)
                    throw fault("unsupported-ecm-notification", thread, configuration.address,
                        configuration.size, "device", configuration.evidence,
                        "enabled FENMI, internal reset or delay-timer route requires its execution model");
            }
            boolean newlyLatched = false;
            for (int domain = 0; domain < 2; domain++) {
                RegisterDef status = ecmStatus[domain][index];
                boolean missing = missingResetInput(status);
                long previous = ecmLatchedStatus(status);
                newlyLatched |= (previous & bit) == 0;
                setRegisterValue(status, previous | bit);
                // Internal errors do not identify the external ERROROUT pin.
                if (missing) updateRegisterState(status, 0, MISSING_RESET_INPUT);
            }
            refreshEcmFeedback();
            if (newlyLatched && (registerValue(ecmNotification[0][index]) & bit) != 0)
                requestInterrupt(thread, 8);
        }

        RegisterDef beforeRead(PcodeThread<byte[]> thread, long address, int size) {
            return beforeRead(thread, address, size, true);
        }

        RegisterDef beforeRead(PcodeThread<byte[]> thread, long address, int size, boolean cpu) {
            requireAlignment(thread, address, size, "read");
            RegionDef region = region(address, size);
            RegisterDef register = cpu ? requireAccessProtection(thread, address, size, CpuAccess.READ, region)
                : region == null && !peripheralFile ? register(address, size) : null;
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
                traceBusRead(thread, address, size, region.evidence);
                return null;
            }
            if (peripheralFile) {
                invalidateClockHorizon();
                // Scenario checks compare these bytes. Keeping them out of the
                // access trace reserves its capacity for RAM traffic.
                scriptPeripheralPoll(thread, address, size);
                return null;
            }
            if (register == null) {
                throw fault("unmapped-read", thread, address, size, "read", "unknown",
                    "no SystemRDL memory region or register covers this read");
            }
            boolean missing = missingResetInput(register);
            boolean widthAllowed = register.allowsOwnedBusAccess(address, size);
            int effects = register.busReadEffects;
            if (register.passiveBusRead && widthAllowed && !missing && size <= register.size
                    && (effects == 0 || csihBindings[register.bindingIndex] != null)) {
                traceBusRead(thread, address, size, register.evidence);
                return register;
            }
            finishBusRead(thread, register, address, size, effects, widthAllowed, missing);
            return register;
        }

        private void finishBusRead(PcodeThread<byte[]> thread, RegisterDef register, long address, int size,
                int effects, boolean widthAllowed, boolean missing) {
            // Consuming RSENT's receive buffer can promote a frame and request DMA.
            if ((effects & READ_RSENT) != 0) invalidateClockHorizon();
            if ((effects & READ_PRIVILEGED) != 0) requireIpgRegisterPrivilege(thread, register, "read");
            if (!widthAllowed) {
                throw fault("mmio-width", thread, address, size, "read",
                    register.evidence, "illegal access width/alignment for register " + register.name);
            }
            if (missing) {
                throw fault("missing-reset-input", thread, address, size, "read",
                    register.evidence, "reset invalidated opaque hardware result "
                        + register.name + "; supply an explicit post-reset scenario input");
            }
            if ((effects & READ_FACI_COMMAND) != 0
                    && (registerValue(requiredRegister(register.name, "control", register.control_register)) & 0x81) != 0x80)
                throw fault("read-prohibited", thread, address, size, "read", register.evidence,
                    "command-area read side effects are supported only in DataFlash P/E mode");
            if (register.read_value != null) {
                setRegisterValue(register.nameBinding, register.read_value);
            }
            else if (register.read_input) {
                if (readInputResponses == null || !readInputResponses.containsKey(register.name)) {
                    throw fault("missing-read-input", thread, address, size, "read",
                        register.evidence, "read data is unspecified for write-only command "
                            + register.name + "; supply an explicit register-input bus response");
                }
            }
            else if (!register.permitsBusRead()) {
                throw fault("read-prohibited", thread, address, size, "read",
                    register.evidence, "register is not software-readable: " + register.name);
            }
            if ((effects & ~READ_PRIVILEGED) != 0)
                applyBusReadEffects(thread, register, effects & ~READ_PRIVILEGED);
            if (size > register.size) {
                // Only a width explicitly declared in RDL reaches this point.
                // Preserve the native register/physical SFR width and normalize
                // the containing transaction's reserved lanes, not all MMIO holes.
                setMemory(address, bytes(registerValue(register), size, language.isBigEndian()));
            }
            traceBusRead(thread, address, size, register.evidence);
        }

        private void traceBusRead(PcodeThread<byte[]> thread, long address, int size, String evidence) {
            if (trace.retainsRead()) trace.addBusAccess("read", pc(thread), address, size, evidence);
        }

        private void traceBusWrite(PcodeThread<byte[]> thread, long address, int size, String evidence) {
            if (trace.markBusWrite(address, size)) trace.addBusAccess("write", pc(thread), address, size, evidence);
        }

        private void applyBusReadEffects(PcodeThread<byte[]> thread, RegisterDef register, int effects) {
            // A register can carry both a behavior and a trigger. Apply every
            // bound action in the same order, not just the most specific one.
            for (; effects != 0; effects &= effects - 1) {
                int effect = Integer.lowestOneBit(effects);
                switch (effect) {
                    case READ_FACI_COMMAND -> {
                        // R01UH0615EJ0120 section6.3.14.1 and Table8.1: reads cause
                        // command lock, without terminating the command in progress (8.3).
                        RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                        RegisterDef access = requiredRegister(register.name, "access-status", register.access_register);
                        setRegisterValue(status, registerValue(status) | 0x4000);
                        setRegisterValue(access, registerValue(access) | FASTAT_CMDLK);
                        // A read breaks an incomplete command-issuance sequence so
                        // the subsequent forced stop is a command, not program data.
                        faciPendingCommand = 0;
                        faciProgramStage = 0;
                    }
                    case READ_CSIH_BIND -> csih(register);
                    case READ_CSIH_RX, READ_CSIH_TX -> csih(register).read(thread, register, effect == READ_CSIH_RX);
                    case READ_ADC, READ_ADC_SELECTOR -> adc.beforeRead(effect == READ_ADC_SELECTOR);
                    case READ_TAUJ -> tauj.read(thread, register);
                    case READ_TAUD -> taud.read(register);
                    case READ_TSG -> tsg.read(thread, register);
                    case READ_RSENT -> rsent.beforeRead(thread, register);
                    case READ_FACI_STATUS -> faciReadErrors |= registerValue(register) & FASTAT_ACCESS_ERROR_MASK;
                    case READ_PORT_PIN -> refreshPortAlias(portBindings.pinAliases[register.bindingIndex], 0);
                    case READ_PORT_MASKED -> {
                        RegisterDef target = maskedPortTarget(register);
                        setRegisterValue(register, registerValue(target));
                    }
                    case READ_CVM, READ_PORT_INPUT ->
                        setRegisterValue(register.nameBinding, registerValue(register) & register.active_mask);
                    case READ_MODE_LATCH -> {
                        long latched = registerValue(register);
                        setRegisterValue(register.nameBinding, (latched & 1) == 0 ? 0 : latched & register.active_mask);
                    }
                    case READ_ECMPS -> setRegisterValue(register.nameBinding, registerValue(register) & 1);
                    case READ_DCRA_SEED -> {
                        RegisterDef control = requiredRegister(register.name, "mode", register.mode_register);
                        long mode = registerValue(control);
                        if (mode != 0 && !("DCRA0CTL".equals(control.name) && mode == 0x22)) {
                            throw fault("unsupported-dcra-mode", thread, control.address,
                                control.size, "read", control.evidence,
                                "supported DCRA modes are Ethernet/32-bit and DCRA0 SAEJ1850/8-bit");
                        }
                    }
                    default -> throw new AssertionError("unknown bus-read effect: " + effect);
                }
            }
        }

        RegisterDef beforeWrite(PcodeThread<byte[]> thread, long address, int size, long value,
                boolean cpu, RegionDef region) {
            discardBusStore = false;
            requireAlignment(thread, address, size, "write");
            RegisterDef register = cpu ? requireAccessProtection(thread, address, size, CpuAccess.WRITE, region)
                : region == null && !peripheralFile ? register(address, size) : null;
            if (discardBusStore) return null;
            if (region != null) {
                if ("pbg0_unimplemented_channels8_9".equals(region.name)) {
                    segError(thread, address, 0x200L);
                    discardBusStore = true;
                    traceBusWrite(thread, address, size, region.evidence);
                    return null;
                }
                if (!region.access.contains("w") || region.name.startsWith("codeflash")
                        || region.name.equals("dataflash")) {
                    // The explicit peripheral-file exploration mode retains its
                    // stub-write experiment; strict device execution never patches ROM.
                    if (peripheralFile && region.name.startsWith("codeflash")
                            && size == 2 && (address & 1) == 0
                            && unsigned(memory(thread, address, 2)) == 0x7fL) {
                        traceBusWrite(thread, address, size, region.evidence);
                        return null;
                    }
                    throw fault("write-prohibited", thread, address, size, "write",
                        region.evidence, "direct write prohibited for region: " + region.name);
                }
                traceBusWrite(thread, address, size, region.evidence);
                return null;
            }
            if (peripheralFile) {
                invalidateClockHorizon();
                return null;
            }
            if (register == null) {
                throw fault("unmapped-write", thread, address, size, "write", "unknown",
                    "no SystemRDL memory region or register covers this write");
            }
            if (register.changesClockSchedule) invalidateClockHorizon();
            if (size > register.size || !register.allowsOwnedBusAccess(address, size)) {
                throw fault("mmio-width", thread, address, size, "write",
                    register.evidence, "illegal access width/alignment for register " + register.name);
            }
            WriteDevice device = register.writeDevice;
            WriteTrigger trigger = register.writeTrigger;
            if (device == WriteDevice.PDMA && !dma.authorizeCpuWrite(thread, register)) {
                discardBusStore = true;
                return null;
            }
            if (!register.busWritable && !register.access.contains("w")) {
                throw fault("write-prohibited", thread, address, size, "write",
                    register.evidence, "register is not software-writable: " + register.name);
            }
            if (device == WriteDevice.SEG) {
                if (userMode(thread)) {
                    segError(thread, address, 0x10L);
                    discardBusStore = true;
                    return null;
                }
                if (!"SEGADDR".equals(register.name)) {
                    if ((value & ~register.writable_mask) != 0) {
                        throw fault("prohibited-register-reserved-bits", thread, address, size,
                            "write", register.evidence, "SEG reserved bits must be written as zero");
                    }
                    registerBeforeWrite = "SEGFLAG".equals(register.name)
                            && !deviceRegisterInitialized(segFlagRegister)
                        ? segFlagValue() : registerValue(register);
                }
                else if (enabledSegFlags() != 0) {
                    discardBusStore = true;
                    return null;
                }
            }
            if ((trigger == WriteTrigger.BANKED_ECC_CLEAR || trigger == WriteTrigger.ECC_NOTIFICATION)
                    && ((value << (8 * (address - register.address)))
                        & ~register.writable_mask) != 0) {
                throw fault("prohibited-register-reserved-bits", thread, address, size,
                    "write", register.evidence,
                    "reserved ECC clear bits must be written as zero: " + register.name);
            }
            if (isGuard(register)) {
                registerBeforeWrite = registerValue(register);
                RegisterDef lock = guardLock(register);
                long lockMask = device == WriteDevice.PEG ? 0x10L : 0x80000000L;
                guardWriteIgnored = (registerValue(lock) & lockMask) != 0;
                if (!guardWriteIgnored) {
                    long laneMask = ((1L << (8 * size)) - 1) << (8 * (address - register.address));
                    long incoming = value << (8 * (address - register.address));
                    if (((incoming ^ register.reset) & laneMask & ~register.writable_mask) != 0) {
                        throw fault("prohibited-register-reserved-bits", thread, address, size,
                            "write", register.evidence,
                            "guard reserved bits must retain their reset value: " + register.name);
                    }
                }
            }
            if (device == WriteDevice.PDMA) dma.validateWrite(thread, register, value);
            if (trigger == WriteTrigger.GUARD_ERROR_CLEAR
                    && ((value << (8 * (address - register.address))) & ~register.writable_mask) != 0)
                throw fault("prohibited-register-reserved-bits", thread, address, size,
                    "write", register.evidence, "guard clear reserved bits must be zero");
            switch (device) {
                case CSIH -> {
                    if (trigger != WriteTrigger.DMA_SELECT) csih(register).validateWrite(thread, register, value);
                    else if ((value & ~register.writable_mask) != 0)
                        throw fault("prohibited-csih-register", thread, address, size, "write",
                            register.evidence, "SELCSIHDMA reserved bits must be zero");
                    registerBeforeWrite = register.reset == null ? 0 : registerValue(register);
                }
                case ADC -> {
                    adc.validateWrite(thread, register, value);
                    registerBeforeWrite = registerValue(register);
                }
                case RSENT -> rsent.validateWrite(thread, register, value);
                case TAUD -> registerBeforeWrite = registerValue(register);
                default -> { }
            }
            if (trigger == WriteTrigger.DCRA_CONTROL || trigger == WriteTrigger.CLOCK_SELECTOR
                    || trigger == WriteTrigger.PDMA_COMPARATOR)
                registerBeforeWrite = registerValue(register);
            if (register.validateBusWrite) validateDeviceWrite(thread, register, size, value);
            if (device == WriteDevice.ECM) {
                registerBeforeWrite = register.reset == null ? 0 : registerValue(register);
            }
            if (device == WriteDevice.CVM && register.permitsBusRead()) {
                registerBeforeWrite = registerValue(register);
            }
            if (trigger == WriteTrigger.NOISE_CLOCK_SELECTOR) {
                registerBeforeWrite = registerValue(register);
            }
            if (device == WriteDevice.PERIPHERAL_ECC || register.snapshotWriteBacking) {
                // Backing snapshots do not resolve unknown reset inputs.
                registerBeforeWrite = inspectBusBacking(thread, register);
            }
            traceBusWrite(thread, address, size, register.evidence);
            return register;
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
            RegisterDef status = registersByName.get("RESF");
            setRegisterValue(status, value);
            if (resetFactorKnownMask != 0xffffffffL) {
                updateRegisterState(status, DEVICE_REGISTER_INITIALIZED, MISSING_RESET_INPUT);
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

        // A replayed RESF observation was taken at the reset of its own scenario.
        // Later resets keep the flags the controller derived and the firmware
        // cleared; the row resolves only what the new reset left unknown.
        void resolveReplayedResetFactors(long value) {
            long known = resetFactorKnownMask;
            validateResetFactorInput(
                (resetFactorValue() & known) | (value & (~known & 0xffffffffL)));
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
            setRegisterValue(command.nameBinding, 0);
        }

        void applyReset(String resetClass) {
            if (resetClass == null || resetClass.equals("none")) return;
            invalidateClockHorizon();
            if (registersByName.get("FSTATR").reset_classes.contains(resetClass)) resetFaci();
            for (Csih controller : csihControllers.values()) controller.reset();
            dma.reset();
            adc.reset();
            rsent.reset();
            if (icusStartupStub != null) icusStartupStub.reset();
            RegisterDef rscfdStatus = registersByName.get("GSTS");
            if (rscfdStatus != null && rscfdStatus.reset_classes.contains(resetClass)) {
                rscfdRamInitDeadline = Math.addExact(
                    hsbCycles, RSCFD_RAM_INITIALIZATION_CYCLES);
            }
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
                    setRegisterValue(register.nameBinding, register.reset);
                }
                else if (register.reset != null
                        && deviceRegisterInitialized(register)) {
                    long retained = registerValue(register) & ~register.reset_mask;
                    setRegisterValue(register.nameBinding, retained | (register.reset & register.reset_mask));
                }
                else {
                    updateRegisterState(register, DEVICE_REGISTER_INITIALIZED, MISSING_RESET_INPUT);
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
                        setRegisterValue(register.nameBinding, register.skipped_value);
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
                            && deviceRegisterInitialized(register)) {
                        setRegisterValue(register.nameBinding, registerValue(register) | (1L << 27));
                    }
                }
            }
            applyResetFactors(resetClass);
            refreshEcmFeedback();
        }

        long unsigned(byte[] value) {
            return Utils.bytesToLong(value, value.length, bigEndian) & 0xffffffffL;
        }

        byte[] memory(long address, int size) {
            if (missingResetInputCount != 0) {
                RegisterDef register = register(address, size);
                if (register != null && missingResetInput(register)) {
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

        private long inspectBusBacking(PcodeThread<byte[]> thread, RegisterDef register) {
            if (deviceState != null && register.size > 0 && register.size <= Long.BYTES)
                return deviceState.inspectDevice(register, bigEndian) & 0xffff_ffffL;
            return unsigned(memory(thread, register.address, register.size));
        }

        private RegisterDef[] bindRegisterNames(String[] names) {
            RegisterDef[] result = new RegisterDef[names.length];
            for (int i = 0; i < names.length; i++) result[i] = registersByName.get(names[i]);
            return result;
        }

        private RegisterDef[][] bindRegisterRows(String[][] names) {
            RegisterDef[][] result = new RegisterDef[names.length][];
            for (int i = 0; i < names.length; i++) result[i] = bindRegisterNames(names[i]);
            return result;
        }

        RegisterDef requiredRegister(String owner, String relation, String name) {
            RegisterDef register = name == null ? null : registersByName.get(name);
            if (register == null) {
                throw new IllegalStateException(owner + " lacks " + relation + " register metadata");
            }
            return register;
        }

        void validateDeviceWrite(PcodeThread<byte[]> thread, RegisterDef register,
                                 int size, long value) {
            WriteDevice device = register.writeDevice;
            WriteTrigger trigger = register.writeTrigger;
            if (device == WriteDevice.IPG) requireIpgRegisterPrivilege(thread, register, "write");
            // Timer/PIC handlers own their entire validation, even if a trigger is also present.
            switch (device) {
                case TAUJ -> { tauj.validate(thread, register, value); return; }
                case TAUD, PIC_TAUD -> { taud.validate(thread, register, value); return; }
                case TSG, PIC_TSG -> { tsg.validate(thread, register, value); return; }
                case PIC1_START -> { pic1.validate(thread, register, value); return; }
                default -> { }
            }
            if (trigger == WriteTrigger.PDMA_COMPARATOR) {
                long incoming = value;
                if ((incoming & register.protection_mask) == register.protection_value) {
                    long selection = incoming & register.writable_mask;
                    if (selection != 0 && selection != 0x3fff7f7fL) {
                        throw fault("unsupported-pdma-comparator-selection", thread,
                            register.address, size, "write", register.evidence,
                            "only the documented mismatch-injection pattern and its cleared state are modeled");
                    }
                    if (selection != 0
                            && ((registerValue(ecmNotification[1][0])
                                | registerValue(ecmNotification[2][0])
                                | registerValue(ecmNotification[3][0])) & 4) != 0) {
                        throw fault("unsupported-ecm-notification", thread,
                            register.address, size, "write", register.evidence,
                            "source2 FENMI, internal reset or delay-timer routing requires the corresponding execution model");
                    }
                }
            }
            if (device == WriteDevice.PERIPHERAL_ECC) {
                long incoming = value;
                long readOnly = trigger == WriteTrigger.PERIPHERAL_ECC_CONTROL
                    ? 0x30807L : 0;
                if ((incoming & ~(register.writable_mask | readOnly)) != 0) {
                    throw fault("prohibited-register-reserved-bits", thread,
                        register.address, size, "write", register.evidence,
                        "reserved peripheral ECC bits must be written as zero");
                }
                if (trigger == WriteTrigger.PERIPHERAL_ECC_TEST) {
                    long mode = (incoming & 0xc000L) == 0x8000L
                        ? incoming & 0x80L : registerValue(register) & 0x80L;
                    if (mode != 0) {
                        throw fault("unsupported-peripheral-ecc-test", thread,
                            register.address, size, "write", register.evidence,
                            "active test mode requires ECC encoder/decoder and peripheral RAM substitution");
                    }
                }
            }
            if (device == WriteDevice.NOISE_FILTER) {
                long incoming = value;
                if ((incoming & ~register.writable_mask) != 0) {
                    throw fault("prohibited-register-reserved-bits", thread, register.address,
                        size, "write", register.evidence,
                        "noise-filter reserved bits must remain at reset: " + register.name);
                }
                if (trigger == WriteTrigger.NOISE_FILTER_ENABLE && incoming != 0) {
                    throw fault("unsupported-noise-filter-operation", thread, register.address,
                        size, "write", register.evidence,
                        "enabled filtering requires external signal and sampling-clock behavior");
                }
                if (trigger == WriteTrigger.NOISE_CLOCK_SELECTOR
                        && !register.allowed_values.contains(incoming)) {
                    throw fault("prohibited-clock-source", thread, register.address,
                        size, "write", register.evidence,
                        "DNF sampling source code is prohibited: " + incoming);
                }
                if (register.enable_register != null) {
                    RegisterDef enable = requiredRegister(register.name, "enable", register.enable_register);
                    if (registerValue(enable) != 0) {
                        throw fault("prohibited-noise-filter-enabled", thread, register.address,
                            size, "write", register.evidence,
                            "configuration may change only while the related filter is disabled");
                    }
                }
                if (trigger == WriteTrigger.NOISE_CLOCK_SELECTOR) {
                    for (String name : register.capture_registers) {
                        RegisterDef enable = requiredRegister(register.name, "enable", name);
                        if (registerValue(enable) != 0) {
                            throw fault("prohibited-noise-filter-enabled", thread, register.address,
                                size, "write", register.evidence,
                                "sampling source may change only while all related filters are disabled");
                        }
                    }
                }
            }
            if ((device == WriteDevice.IPG || device == WriteDevice.GRAM_BUFFER)
                    && (value & ~register.writable_mask) != 0) {
                throw fault("prohibited-register-reserved-bits", thread, register.address,
                    size, "write", register.evidence,
                    "reserved bits must be written as zero: " + register.name);
            }
            if (trigger == WriteTrigger.BIST_CONTROL
                    && (value & ~register.active_mask) != 0) {
                throw fault("prohibited-bist-reserved-bits", thread, register.address,
                    size, "write", register.evidence,
                    "BSEQ0CTL reserved bits must be zero");
            }
            if (trigger == WriteTrigger.CLOCK_DIVIDER || trigger == WriteTrigger.CLOCK_SELECTOR) {
                long incoming = value;
                if ((incoming & ~register.writable_mask) != 0) {
                    throw fault("prohibited-clock-reserved-bits", thread, register.address,
                        size, "write", register.evidence,
                        "reserved clock register bits must be written as zero: " + register.name);
                }
                if (trigger == WriteTrigger.CLOCK_DIVIDER) {
                    RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                    if ((registerValue(status) & register.sync_mask) != register.sync_mask) {
                        throw fault("prohibited-clock-divider-unsynchronized", thread, register.address,
                            size, "write", register.evidence,
                            "divider must not be written while SYNC is zero");
                    }
                }
                else {
                    if (!register.allowed_values.contains(incoming)) {
                        throw fault("prohibited-clock-source", thread, register.address,
                            size, "write", register.evidence,
                            "clock source ID is prohibited: " + incoming);
                    }
                    RegisterDef divider = requiredRegister(register.name, "control", register.control_register);
                    RegisterDef status = requiredRegister(
                        register.name, "secondary-status", register.secondary_status_register);
                    if (incoming != registerValue(register) && (registerValue(divider) != 0
                            || registerValue(status) != register.completion_value)) {
                        throw fault("prohibited-clock-selector-running", thread, register.address,
                            size, "write", register.evidence,
                            "clock source may change only with divider zero and stopped synchronized status");
                    }
                }
            }
            if (device == WriteDevice.FLMD) {
                long incoming = value;
                boolean valid = trigger == WriteTrigger.FLMD_COMMAND
                    ? flmdStage == 0 && incoming == 0xa5
                    : trigger == WriteTrigger.FLMD_CONTROL
                        && (flmdStage == 1 && incoming <= 1
                            || flmdStage == 2 && incoming == (flmdDesired ^ 0xffffffffL)
                            || flmdStage == 3 && incoming == flmdDesired);
                if (!valid) {
                    throw fault("unsupported-flmd-sequence", thread, register.address,
                        size, "write", register.evidence,
                        "only uninterrupted A5/value/full-word-inverse/value writes are modeled; malformed-sequence error timing is not modeled");
                }
            }
            if (device == WriteDevice.DCRA) {
                RegisterDef control = trigger == WriteTrigger.DCRA_CONTROL ? register
                    : requiredRegister(register.name, "mode", register.mode_register);
                long mode = control == register ? value : registerValue(control);
                if (mode != 0 && !("DCRA0CTL".equals(control.name) && mode == 0x22)) {
                    throw fault("unsupported-dcra-mode", thread, control.address,
                        control.size, "write", control.evidence,
                        "supported DCRA modes are Ethernet/32-bit and DCRA0 SAEJ1850/8-bit; reserved bits must be zero");
                }
                if (trigger == WriteTrigger.DCRA_INPUT) {
                    if (!dcraSeeded.contains(control.name)) {
                        throw fault("uninitialized-dcra-seed", thread, register.address,
                            size, "write", register.evidence,
                            "DCRAnCOUT must be explicitly seeded before the first input word");
                    }
                    RegisterDef output = requiredRegister(register.name, "status", register.status_register);
                    memory(thread, output.address, output.size);
                }
            }
            switch (trigger) {
                case FACI_COMMAND -> validateFaciWrite(thread, register, size, value);
                case FACI_ENABLE -> {
                    if ((registerValue(registersByName.get("FSTATR")) & FSTATR_FRDY) == 0
                            && (value & 1) != registerValue(register))
                        throw fault("prohibited-faci-enable-change", thread, register.address, size,
                            "write", register.evidence, "FHVE enables must not change during command processing");
                }
                case FACI_ADDRESS -> {
                    RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                    memory(thread, status.address, status.size);
                }
                case FACI_DATAFLASH_MODE -> {
                    RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                    long previous = unsigned(memory(thread, register.address, register.size));
                    if ((unsigned(memory(thread, status.address, status.size)) & FSTATR_FRDY) != 0
                            && (previous != 0 && previous != 0x80
                                || (value >>> 8) == 0xaa
                                    && (value & 0xff) != 0 && (value & 0xff) != 0x80)) {
                        throw fault("unsupported-faci-mode", thread, register.address,
                            size, "write", register.evidence,
                            "mode transitions are bounded to read/DataFlash P/E; CodeFlash/FWE and illegal-mode errors are not modeled");
                    }
                }
                case FACI_NORMAL_EMULATION -> {
                    if (value != 0 || unsigned(memory(thread, register.address, register.size)) != 0)
                        throw fault("unsupported-faci-emulation", thread, register.address,
                            size, "write", register.evidence,
                            "only unchanged normal FLEMU mode is modeled; OCD write permission is not inferred");
                }
                case DATAFLASH_READ_CYCLE -> {
                    if ((value & 0xf) < 3)
                        throw fault("prohibited-dataflash-read-cycle", thread, register.address,
                            size, "write", register.evidence,
                            "EEPRDCYCL codes0..2 are prohibited; no timing behavior is synthesized");
                }
                case ICUS_COMMAND -> {
                    if (icusStartupStub != null && icusStartupStub.handles(value)) {
                        icusStartupStub.validateCommand(thread, register, value);
                    }
                    // Exact F33 8A8E4 issues (slot<<16)|7 for slots0..14;
                    // 8ACA8 issues the bare abort word3F. Accept writes only:
                    // neither operation has a simulated hardware reply.
                    else if ((value & 0xffff) != 5
                            && !((value & 0xffff) == 7 && (value >>> 16) < 15)
                            && value != 0x3f) {
                        throw fault("unsupported-icus-command", thread, register.address,
                            size, "write", register.evidence,
                            String.format("ICU-S command 0x%04X has no recovered state transition",
                                value & 0xffff));
                    }
                }
                case ICUS_CONTROL -> {
                    if (icusStartupStub != null) icusStartupStub.validateAck(thread, register, value);
                }
                case RSCFD_TRANSMIT -> {
                    if ((value & 1) == 0) return;
                    if (register.payload_address == null) {
                        throw new IllegalStateException(register.name + " lacks payload_address metadata");
                    }
                    long base = register.payload_address;
                    memory(thread, base, 4);
                    memory(thread, base + 4, 4);
                    memory(thread, base + 12, 4);
                    memory(thread, base + 16, 4);
                }
                default -> { }
            }
        }

        private boolean missingResetInput(RegisterDef register) {
            return (registerState[register.bindingIndex] & MISSING_RESET_INPUT) != 0;
        }

        private boolean deviceRegisterInitialized(RegisterDef register) {
            return register != null
                && (registerState[register.bindingIndex] & DEVICE_REGISTER_INITIALIZED) != 0;
        }

        private void updateRegisterState(RegisterDef register, int clear, int set) {
            int index = register.bindingIndex;
            int previous = registerState[index];
            int next = (previous & ~clear) | set;
            if (next == previous) return;
            registerState[index] = (byte) next;
            missingResetInputCount += (next & MISSING_RESET_INPUT) - (previous & MISSING_RESET_INPUT);
            if (((next ^ previous) & MISSING_RESET_INPUT) != 0 && dmaWordIndex != null)
                deviceState.invalidateDeviceWord(register);
        }

        private void resolveRegisterInput(RegisterDef register) {
            updateRegisterState(register, MISSING_RESET_INPUT,
                register.reset_mask != null ? DEVICE_REGISTER_INITIALIZED : 0);
        }

        void setRegisterValue(String name, long value) {
            RegisterDef register = registersByName.get(name);
            if (register == null) throw new IllegalStateException("machine model lacks register " + name);
            setRegisterValue(register, value);
        }

        void setRegisterValue(RegisterDef register, long value) {
            if (register.size <= Long.BYTES
                    && deviceState != null && deviceState.writeDevice(register, value, bigEndian)) {
                int pending = register.pendingBinding;
                if (pending >= 0 && !missingResetInput(register))
                    updatePendingInterrupt(pending, register, value, true);
                else if (pending != -1) refreshPendingInterrupts(register.address, register.size, true);
            }
            else setMemory(register.address, bytes(value, register.size, bigEndian));
            resolveRegisterInput(register);
        }

        void registerWriteEvent(PcodeThread<byte[]> thread, RegisterDef register, long value) {
            if (trace.deviceEvents.omitsEventPayload(JsonRows.REGISTER_WRITE.name)) return;
            trace.deviceEvents.addRegisterWrite(pc(thread), register, value, trace.busInitiator);
        }

        RegisterDef rscfdTransmitResultSummary(long buffer) {
            if (buffer < 0 || buffer > 47) {
                throw new IllegalStateException("RSCFD transmit buffer is outside buffers0..47");
            }
            return requiredRegister("RSCFD", "transmit-complete-status",
                "CFDTMTCSTS" + (buffer / 32));
        }

        // R01UH0585EJ0120 section 17.4.11.7 Table 17.153: TMIEp is bit p % 32 of TMIEC(p / 32).
        RegisterDef rscfdTransmitInterruptEnable(long buffer) {
            if (buffer < 0 || buffer > 47) {
                throw new IllegalStateException("RSCFD transmit buffer is outside 0..47");
            }
            return requiredRegister("RSCFD", "transmit-interrupt-enable", "TMIEC" + (buffer / 32));
        }

        void setRscfdTransmitRequest(long buffer, boolean present) {
            RegisterDef status = requiredRegister(
                "RSCFD", "transmit-request-status", "CFDTMTRSTS" + (buffer / 32));
            long bit = 1L << (buffer & 31);
            setRegisterValue(status.nameBinding,
                present ? registerValue(status) | bit : registerValue(status) & ~bit);
        }

        void setRscfdTransmitAbortRequest(long buffer, boolean present) {
            RegisterDef status = requiredRegister(
                "RSCFD", "transmit-abort-status", "CFDTMTARSTS" + (buffer / 32));
            long bit = 1L << (buffer & 31);
            setRegisterValue(status.nameBinding,
                present ? registerValue(status) | bit : registerValue(status) & ~bit);
        }

        long rscfdTransmitBuffer(RegisterDef register) {
            if (register.payload_address == null) {
                throw new IllegalStateException(register.name + " lacks RSCFD payload metadata");
            }
            long bufferOffset = register.payload_address - RSCFD_TX_RAM_BASE;
            if (bufferOffset < 0 || bufferOffset % RSCFD_TX_RECORD_SIZE != 0) {
                throw new IllegalStateException(
                    register.name + " has an invalid RSCFD payload address");
            }
            return bufferOffset / RSCFD_TX_RECORD_SIZE;
        }


        void setRscfdTransmitResult(long buffer, boolean present) {
            long channel = buffer / 16;
            RegisterDef summary = rscfdTransmitResultSummary(buffer);
            long summaryBit = 1L << (buffer & 31);
            long next = present
                ? registerValue(summary) | summaryBit
                : registerValue(summary) & ~summaryBit;
            setRegisterValue(summary.nameBinding, next);
            long enabled = registerValue(rscfdTransmitInterruptEnable(buffer))
                >>> ((buffer / 16 & 1) * 16);
            long channelResults = next >>> ((buffer / 16 & 1) * 16);
            if (channel == 1 && (channelResults & enabled) == 0) {
                RegisterDef eic = interruptRegisters.get(188);
                if (eic != null) {
                    setRegisterValue(eic.nameBinding, registerValue(eic) & ~0x1000L);
                }
            }
        }

        void handleRscfdTransmitStatusWrite(RegisterDef register) {
            long channel;
            long channelBase;
            if (register.address >= 0xFFD202D0L && register.address < 0xFFD202D4L) {
                channel = 0;
                channelBase = 0xFFD202D0L;
            }
            else if (register.address >= 0xFFD202E0L && register.address < 0xFFD202F0L) {
                channel = 1;
                channelBase = 0xFFD202E0L;
            }
            else if (register.address == 0xFFD202F0L) {
                channel = 2;
                channelBase = 0xFFD202F0L;
            }
            else {
                throw new IllegalStateException(
                    register.name + " is outside modeled RSCFD transmit-status banks");
            }
            for (int offset = 0; offset < register.size; offset++) {
                long resource = register.address + offset - channelBase;
                long result = unsigned(memory(register.address + offset, 1)) & 6;
                setRscfdTransmitResult(channel * 16 + resource, result != 0);
            }
        }

        void resetRscfdControllerState() {
            pendingRscfdTransmits.clear();
            for (ReceiveFifo fifo : receiveFifos.values()) {
                fifo.messages.clear();
                setRegisterValue(fifo.status.nameBinding, 1);
                refreshReceiveFifo(fifo);
            }
            for (RegisterDef register : registers) {
                if ("rscfd-transmit-status".equals(register.trigger)) {
                    setRegisterValue(register.nameBinding, 0);
                }
            }
        }

        void handleRscfdModeWrite(RegisterDef register, long value) {
            RegisterDef status =
                requiredRegister(register.name, "status", register.status_register);
            long mode = value & 3;
            long state = switch ((int) mode) {
                case 0 -> 0;
                case 1 -> 1;
                case 2 -> 2;
                default -> throw new IllegalStateException(
                    register.name + " requests reserved RSCFD mode 3");
            };
            if ((value & 4) != 0) state |= 4;
            setRegisterValue(status.nameBinding, (registerValue(status) & ~0xfL) | state);
            if ("rscfd-global-control".equals(register.trigger) && mode == 1) {
                // Tables 17.107-17.108: entering global reset initializes the
                // controller RAM/FIFO state; GRAMINIT is complete at this
                // functional (non-cycle-accurate) write boundary.
                resetRscfdControllerState();
            }
        }


        void handleRscfdWrite(PcodeThread<byte[]> thread, RegisterDef register, long command,
                              long registerBeforeWrite) {
            long buffer = rscfdTransmitBuffer(register);
            if ((command & 2) != 0) {
                if (pendingRscfdTransmits.containsKey(buffer)) {
                    setRegisterValue(register.nameBinding, registerBeforeWrite | 2);
                    setRscfdTransmitAbortRequest(buffer, true);
                }
                else {
                    setRegisterValue(register.nameBinding, registerBeforeWrite);
                }
                return;
            }
            if ((command & 1) == 0) {
                setRegisterValue(register.nameBinding, registerBeforeWrite);
                return;
            }
            if (register.completion_value == null) {
                throw new IllegalStateException(register.name + " lacks RSCFD trigger metadata");
            }
            RegisterDef previous = pendingRscfdTransmits.putIfAbsent(buffer, register);
            if (previous != null) {
                throw new IllegalStateException(
                    register.name + " requested while " + previous.name + " is still transmitting");
            }
            setRscfdTransmitRequest(buffer, true);
            long base = register.payload_address;
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
            });
        }

        void completeRscfdTransmit(PcodeThread<byte[]> thread, ExternalEvent input) {
            if (input.buffer == null || input.buffer < 0 || input.buffer >= 48) {
                throw new IllegalArgumentException(
                    "can-tx-complete requires an RSCFD buffer in range 0..47");
            }
            long buffer = Integer.toUnsignedLong(input.buffer);
            RegisterDef control = pendingRscfdTransmits.remove(buffer);
            if (control == null) {
                if (!input.tolerate_no_pending) {
                    throw new IllegalArgumentException(
                        "can-tx-complete buffer " + buffer + " has no pending transmission");
                }
                JsonObject ignored = new JsonObject();
                ignored.addProperty("kind", "can-tx-complete-ignored");
                ignored.addProperty("scheduler_tick", trace.instructions);
                ignored.addProperty("controller", "RSCFD");
                ignored.addProperty("buffer", buffer);
                ignored.addProperty("evidence", input.evidence);
                trace.deviceEvents.add(ignored);
                return;
            }
            RegisterDef status = requiredRegister(
                control.name, "completion-status", control.status_register);
            long statusOffset = status.size == 1 ? 0 : buffer & 15;
            if (statusOffset >= status.size) {
                throw new IllegalStateException(
                    control.name + " completion status lies outside " + status.name);
            }
            boolean abortRequested = (registerValue(control) & 2) != 0;
            long result = abortRequested ? 6 : control.completion_value;
            setMemory(status.address + statusOffset,
                bytes(result, 1, language.isBigEndian()));
            setRscfdTransmitResult(buffer, true);
            setRscfdTransmitRequest(buffer, false);
            setRscfdTransmitAbortRequest(buffer, false);
            setRegisterValue(control.nameBinding, 0);

            long enabled = registerValue(rscfdTransmitInterruptEnable(buffer));
            boolean interrupt = (enabled & (1L << (buffer & 31))) != 0;
            if (interrupt) {
                long channel = buffer / 16;
                if (channel != 1) {
                    throw new IllegalStateException(
                        "RSCFD transmit interrupt routing is not modeled for channel " + channel);
                }
                requestInterrupt(thread, 188, input.firmware_control);
            }
            JsonObject event = new JsonObject();
            event.addProperty("kind", "can-tx-complete");
            event.addProperty("scheduler_tick", trace.instructions);
            event.addProperty("controller", "RSCFD");
            event.addProperty("buffer", buffer);
            event.addProperty("interrupt", interrupt);
            event.addProperty("evidence", input.evidence);
            trace.deviceEvents.add(event);
        }

        long registerValue(RegisterDef register) {
            if (deviceState != null && !missingResetInput(register) && register.size <= Long.BYTES) {
                return deviceState.inspectDevice(register, bigEndian) & 0xffff_ffffL;
            }
            return unsigned(memory(register.address, register.size));
        }

        void refreshReceiveFifo(ReceiveFifo fifo) {
            long control = registerValue(fifo.control);
            int depth = FIFO_DEPTHS[(int) (control >>> 8) & 7];
            int count = fifo.messages.size();
            long status = registerValue(fifo.status) & 0x1c;
            status |= ((long) count << 8) | (count == 0 ? 1 : 0)
                | (depth != 0 && count == depth ? 2 : 0);
            setRegisterValue(fifo.status.nameBinding, status);
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
            setRegisterValue(fifo.interrupt.nameBinding, (old & ~0x1000L) | (requested ? 0x1000 : 0));
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
                setRegisterValue(fifo.status.nameBinding, registerValue(fifo.status) | 4);
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
                P1MEJitMachine.writeNumber(window, 0, 4, false,
                    parseUnsigned(input.can_id) | (input.extended ? 0x80000000L : 0));
                P1MEJitMachine.writeNumber(window, 4, 4, false,
                    ((long) dlc << 28) | ((long) input.label << 16) | input.timestamp);
                window[8] = (byte) (input.fd ? 4 : 0);
                System.arraycopy(payload, 0, window, 12, Math.min(payload.length, capacity));
                fifo.messages.add(window);
                if ((control & 0x1000) != 0 || fifo.messages.size() * 8 >= depth * thresholdEighths) {
                    setRegisterValue(fifo.status.nameBinding, registerValue(fifo.status) | 8);
                }
                refreshReceiveFifo(fifo);
            }
            String kind = discarded == null ? "can-rx" : "can-rx-discard";
            if (trace.deviceEvents.omitsEventPayload(kind)) return;
            JsonObject event = GSON.toJsonTree(input).getAsJsonObject();
            event.addProperty("kind", kind);
            if (discarded != null) event.addProperty("reason", discarded);
            event.addProperty("scheduler_tick", trace.instructions);
            trace.deviceEvents.add(event);
        }

        void handleReceiveWrite(PcodeThread<byte[]> thread, RegisterDef register, int size, long value) {
            ReceiveFifo fifo = receiveFifos.get(register.fifo_index);
            if (register == fifo.status) {
                // CFMC/CFEMP/CFFLL are read-only; the three sticky flags clear by writing zero.
                setRegisterValue(register.nameBinding, registerBeforeWrite & (registerValue(register) | ~0x1cL));
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
                if ((value & 0xff) != 0xff || (registerValue(fifo.control) & 1) == 0
                        || fifo.messages.isEmpty()) {
                    throw fault("invalid-fifo-pop", thread, register.address, size,
                        "write", "manual", "receive FIFO pop requires CFE=1, unread data, and CFPC=0xFF");
                }
                fifo.messages.remove();
                refreshReceiveFifo(fifo);
                if (trace.deviceEvents.omitsEventPayload("can-rx-pop")) return;
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

        void retireClock(PcodeThread<byte[]> thread) {
            long cycles = hsbCyclesPerInstruction;
            if (cycles == 0) return;
            if (cycles > 0 && cycles <= quietRemaining()) {
                hsbCycles += cycles;
                return;
            }
            if (cycles > 0 && quietUntil != 0 && quietUntil != Long.MAX_VALUE
                    && cycles == quietUntil - hsbCycles) {
                int events = quietClockEvents;
                invalidateClockHorizon();
                invalidateBatchProof();
                advanceClockSpan(thread, cycles, events);
                return;
            }
            invalidateClockHorizon();
            advanceClock(thread, cycles, true);
        }

        private long quietRemaining() {
            return quietUntil > hsbCycles ? quietUntil - hsbCycles - 1 : 0;
        }

        private void invalidateClockHorizon() {
            quietUntil = 0;
        }

        private static long timerDeadline(long tick, long remaining) {
            return remaining == Long.MAX_VALUE ? NO_CLOCK_EDGE : tick + remaining;
        }

        private long taudCyclesUntilEvent() {
            if (taudClockDue == 0) {
                long remaining = taud.cyclesUntilEvent();
                // A fault can leave another unit's emitted edges pending.
                if (taud.units[0].emitted != 0 || taud.units[1].emitted != 0) return remaining;
                taudClockDue = timerDeadline(taudClockTick, remaining);
            }
            return taudClockDue == NO_CLOCK_EDGE ? Long.MAX_VALUE : taudClockDue - hsbCycles;
        }

        private long taujCyclesUntilEvent() {
            if (taujClockDue == 0)
                taujClockDue = timerDeadline(taujClockTick, tauj.cyclesUntilEvent());
            return taujClockDue == NO_CLOCK_EDGE ? Long.MAX_VALUE : taujClockDue - hsbCycles;
        }

        private long rsentCyclesUntilEvent() {
            if (rsentClockDue < 0) rsentClockDue = rsent.nextEventTick();
            // After an earlier clock stage faults, RSENT's local time can be
            // behind HSB even when it has caught up with every committed span.
            return rsentClockDue == Long.MAX_VALUE ? Long.MAX_VALUE
                : Math.max(0, rsentClockDue - rsent.now - (hsbCycles - rsentClockTick));
        }

        private void syncTaudClock(long tick) {
            long span = tick - taudClockTick;
            if (span == 0) return;
            for (Taud.Unit unit : taud.units) unit.advance(span);
            taudClockTick = tick;
        }

        private void syncTaujClock(long tick) {
            long span = tick - taujClockTick;
            if (span == 0) return;
            for (Tauj.Unit unit : tauj.units) unit.move(span);
            taujClockTick = tick;
        }

        private void syncRsentClock(long tick) {
            long span = tick - rsentClockTick;
            if (span == 0) return;
            rsent.moveClock(span);
            rsentClockTick = tick;
        }

        private void drainDeviceClocks() {
            adc.syncClock();
            tsg.syncClock(hsbCycles);
            syncTaudClock(hsbCycles);
            syncTaujClock(hsbCycles);
            syncRsentClock(hsbCycles);
        }

        private void rebaseDeviceClocks() {
            taudClockTick = taujClockTick = rsentClockTick = hsbCycles;
            taudClockDue = taujClockDue = 0;
            rsentClockDue = -1;
        }

        private void advanceClock(PcodeThread<byte[]> thread, long cycles, boolean fromRetirement) {
            if (cycles < 0) throw new IllegalArgumentException("negative CLK_HSB advance");
            while (cycles != 0) {
                long adcDeadline = adc.cyclesUntilEvent();
                long rsentDeadline = rsentCyclesUntilEvent();
                long next = nextBusClockEdge(adcDeadline, rsentDeadline);
                // A one-tick external advance cannot cross a timer edge. Retirement
                // also needs the next edge to bound subsequent instructions.
                long tsgDeadline = 0; // Unprobed; defer the lookup to its ordered stage.
                if (next > 1 && (fromRetirement || cycles > 1)) {
                    long timer = Math.min(taujCyclesUntilEvent(), taudCyclesUntilEvent());
                    tsgDeadline = tsg.cyclesUntilEvent(hsbCycles);
                    next = Math.min(next, Math.min(timer, tsgDeadline));
                }
                if (fromRetirement && cycles < next && taudClockDue != 0 && taujClockDue != 0
                        && !taud.picDirty && !tsg.picDirty && !tsg.picRoutingDeferred) {
                    long bound = Math.min(next, Long.MAX_VALUE - hsbCycles);
                    if (cycles < bound) {
                        setClockHorizon(bound, adcDeadline, rsentDeadline, tsgDeadline);
                        hsbCycles += cycles;
                        return;
                    }
                }
                long span = Math.min(cycles, next);
                if (span <= 0) throw new IllegalStateException("non-advancing peripheral clock");
                if (fromRetirement && span == next) invalidateBatchProof();
                advanceClockSpan(thread, span, clockEventMask(span, adcDeadline, rsentDeadline, tsgDeadline));
                cycles -= span;
            }
        }

        private static int clockEventMask(long span, long adcDeadline, long rsentDeadline, long tsgDeadline) {
            return (span == adcDeadline && adcDeadline != Long.MAX_VALUE ? QUIET_ADC_DUE : 0)
                | (span == rsentDeadline ? QUIET_RSENT_DUE : 0)
                | (tsgDeadline != 0 ? QUIET_TSG_KNOWN | (span >= tsgDeadline ? QUIET_TSG_DUE : 0) : 0);
        }

        private void advanceClockSpan(PcodeThread<byte[]> thread, long span, int events) {
            long start = hsbCycles;
            hsbCycles = Math.addExact(start, span);
            tsg.deferPicRouting();
            int stage = 0;
            try {
                // Commit ADC results before coincident triggers. Keep the
                // original span for edge delivery (including TAUJ trace rows).
                if ((events & QUIET_ADC_DUE) != 0) adc.advanceAtDeadline(thread);
                stage = 1;
                // A DMA beat can determine the next span without probing the
                // timers. Fill any missing slot here, in its ordered stage.
                if (taudClockDue == 0) taudCyclesUntilEvent();
                if (taudClockDue == 0 || taudClockDue == hsbCycles) {
                    syncTaudClock(start);
                    taudClockTick = hsbCycles;
                    taudClockDue = 0;
                    taud.advanceSpan(thread, span);
                }
                stage = 2;
                if (taujClockDue == 0) taujCyclesUntilEvent();
                if (taujClockDue == 0 || taujClockDue == hsbCycles) {
                    syncTaujClock(start);
                    taujClockTick = hsbCycles;
                    taujClockDue = 0;
                    tauj.advanceSpan(thread, span);
                }
                stage = 3;
                boolean tsgEvent = (events & QUIET_TSG_KNOWN) != 0
                    ? (events & QUIET_TSG_DUE) != 0 : span >= tsg.cyclesUntilEvent(start);
                if (tsgEvent) tsg.advanceSpan(thread, start, span);
                stage = 4;
                // At saturation, RSENT must process its final edge before later devices.
                boolean rsentEvent = (events & QUIET_RSENT_DUE) != 0;
                if (rsentEvent || hsbCycles == Long.MAX_VALUE) {
                    syncRsentClock(start);
                    rsentClockTick = hsbCycles;
                    rsentClockDue = -1;
                    rsent.advanceSpan(thread, span, rsentEvent);
                }
            }
            catch (RuntimeException | Error failure) {
                // Earlier stages reached this edge; later stages reached only
                // its start. Commit any skipped quiet work, not the missed span.
                adc.syncClock();
                syncTaudClock(stage >= 1 ? hsbCycles : start);
                syncTaujClock(stage >= 2 ? hsbCycles : start);
                syncRsentClock(stage >= 4 ? hsbCycles : start);
                if (stage < 4) tsg.recoverClock(start);
                rebaseDeviceClocks();
                throw failure;
            }
            finishPicRouting(thread);
            if (hsbCycles == faciDeadline) completeFaciOperation();
            if (hsbCycles == rscfdRamInitDeadline) {
                RegisterDef status = requiredRegister("RSCFD", "status", "GSTS");
                setRegisterValue(status.nameBinding, registerValue(status) & ~8L);
                rscfdRamInitDeadline = Long.MAX_VALUE;
            }
            if (icusStartupStub != null && icusStartupStub.deadline != Long.MAX_VALUE
                    && hsbCycles == icusStartupStub.deadline)
                icusStartupStub.complete();
            if (dma.nextService <= hsbCycles) dma.advanceClock(thread);
        }

        Csih csih(RegisterDef register) {
            Csih bound = csihBindings[register.bindingIndex];
            if (bound != null) return bound;
            String prefix = register.name.substring(0, 5);
            return csihControllers.computeIfAbsent(prefix, Csih::new);
        }

        // Section14 word-level wire boundary: no synthetic baud clock or ASIC.
        // FIFO shares 128 entries; dual buffer has separate 64-entry banks.
        final class Csih {
            private enum Word { CTL0, CTL1, CTL2, MCTL0, MCTL1, MCTL2, MRWP0,
                STR0, STCR0, TX0W, TX0H, RX0W, RX0H }

            final String prefix;
            private Integer unit;
            final RegisterDef control;
            final Map<String, RegisterDef> bank = new HashMap<>();
            final RegisterDef[] configurations = new RegisterDef[8];
            final RegisterDef[] baudRates = new RegisterDef[4];
            private final RegisterDef[] words;
            private final RegisterDef dmaSelector;
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
            final WireInputs relativeInputs = new WireInputs();

            Csih(String prefix) {
                this.prefix = prefix;
                control = requiredRegister(prefix, "control", prefix + "CTL0");
                if (!control.name.equals(control.control_register) || control.interrupt_channel_base == null)
                    throw new IllegalStateException(prefix + " lacks CSIH controller/IRQ metadata");
                for (RegisterDef register : registers) {
                    if (register.writeDevice != WriteDevice.CSIH || !register.name.startsWith(prefix)) continue;
                    String suffix = register.csihSuffix = register.name.substring(prefix.length());
                    bank.put(suffix, register);
                    register.csihWriteWord = switch (suffix) {
                        case "CTL0" -> Word.CTL0;
                        case "MCTL0" -> Word.MCTL0;
                        case "MCTL1" -> Word.MCTL1;
                        case "MCTL2" -> Word.MCTL2;
                        case "MRWP0" -> Word.MRWP0;
                        case "STCR0" -> Word.STCR0;
                        default -> null;
                    };
                    csihBindings[register.bindingIndex] = this;
                }
                for (int index = 0; index < configurations.length; index++) configurations[index] = reg("CFG" + index);
                for (int index = 0; index < baudRates.length; index++) baudRates[index] = reg("BRS" + index);
                Word[] slots = Word.values();
                words = new RegisterDef[slots.length];
                for (Word slot : slots) words[slot.ordinal()] = bank.get(slot.name());
                dmaSelector = registersByName.get("SELCSIHDMA");
            }
            RegisterDef reg(String suffix) {
                RegisterDef register = bank.get(suffix);
                if (register == null) throw new IllegalStateException(prefix + " lacks " + suffix + " metadata");
                return register;
            }
            RegisterDef reg(Word slot) {
                RegisterDef register = words[slot.ordinal()];
                return register != null ? register : reg(slot.name());
            }
            long cfg(int index) { return registerValue(configurations[index]); }
            long get(String suffix) { return registerValue(reg(suffix)); }
            long get(Word slot) { return registerValue(reg(slot)); }
            void put(Word slot, long value) { setRegisterValue(reg(slot), value); }
            int mode(long controlValue) {
                return (controlValue & 1) != 0 ? -1 : (int) (get(Word.MCTL0) >> 8) & 3;
            }
            int mode() { return mode(get(Word.CTL0)); }
            static int capacity(int mode) { return mode == 1 ? 64 : 128; }
            int pointer(Word slot, int shift) { return (int) (get(slot) >> shift) & 127; }
            void pointer(Word slot, int shift, int value) {
                put(slot, (get(slot) & ~(127L << shift)) | ((long) value << shift));
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
                put(Word.MRWP0, 0);
                put(Word.MCTL2, 0);
                frame.clear();
                status();
            }
            void status() {
                long flags = get(Word.STR0) & 0xC10BL;
                if (active || queued != 0 || bufferStarted) flags |= 0x80;
                if (mode() == 0) {
                    flags |= (long) queued << 16 | (long) received << 24;
                    if (queued + received == 0) flags |= 0x10;
                    if (queued + received >= 128) flags |= 0x20;
                } else flags |= 0x10;
                put(Word.STR0, flags);
            }
            RuntimeException boundary(PcodeThread<byte[]> thread, RegisterDef register, String detail) {
                return fault("unsupported-csih-operation", thread, register.address, register.size,
                    "device", register.evidence, prefix + ": " + detail);
            }
            long mask(RegisterDef register) {
                if (register.writable_mask != null) return register.writable_mask;
                if (register.csihSuffix.startsWith("CFG")) return 0xFF0FFFFFL;
                if (register.csihSuffix.startsWith("BRS")) return 0xFFFL;
                throw new IllegalStateException("CSIH writable mask missing: " + register.name);
            }
            void validateWrite(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                if ((value & ~mask(register)) != 0)
                    throw boundary(thread, register, "reserved bits must be zero");
                Word word = register.csihWriteWord;
                WriteTrigger trigger = register.writeTrigger;
                if (word == Word.MCTL0 && (value & 0x300) == 0x300)
                    throw boundary(thread, register, "MMS=11 is prohibited");
                if (trigger != WriteTrigger.TX && trigger != WriteTrigger.TX_HALF
                        && word != Word.CTL0 && word != Word.STCR0 && word != Word.MRWP0
                        && word != Word.MCTL1 && word != Word.MCTL2
                        && (get(Word.CTL0) & 0x80) != 0 && value != get(register.csihSuffix))
                    throw boundary(thread, register, "configuration changes require PWR=0");
                if (word == Word.CTL0 && active && (value & 0x80) != 0
                        && ((value ^ get(Word.CTL0)) & 0x61) != 0)
                    throw boundary(thread, register, "TXE/RXE/MBS changes during active transfer");
                if (word == Word.MRWP0 && mode() == 1
                        && ((value & 127) >= 64 || ((value >> 16) & 127) >= 64))
                    throw boundary(thread, register, "dual-buffer pointer exceeds 63");
                if (word == Word.MCTL2) {
                    if (active && (value & 0xFF007F) != get(Word.MCTL2))
                        throw boundary(thread, register, "ND/SOP must not change during a buffer transfer");
                    int mode = mode();
                    int capacity = capacity(mode);
                    if (mode > 0 && (((value >> 16) & 255) > capacity || (value & 127) >= capacity))
                        throw boundary(thread, register, "buffer count/start exceeds implemented bank");
                    if ((value & 0x80000000L) != 0 && (mode <= 0 || active))
                        throw boundary(thread, register, "BTST requires idle dual/transmit-only buffer mode");
                }
                if (trigger == WriteTrigger.TX_HALF && !txHeaderKnown)
                    throw boundary(thread, register, "TX0H requires an earlier TX0W header");
                if (trigger == WriteTrigger.TX && (value & 0xFF0000) == 0xFF0000)
                    throw boundary(thread, register, "all chip selects inactive is prohibited");
            }
            void write(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                Word word = register.csihWriteWord;
                WriteTrigger trigger = register.writeTrigger;
                if (word == Word.CTL0) {
                    put(Word.CTL0, value & ~2L);
                    if ((registerBeforeWrite & 0x80) != 0 && (value & 0x80) == 0) {
                        clearPointers();
                    }
                    if (((registerBeforeWrite ^ value) & 0x80) != 0) put(Word.STR0, get(Word.STR0) & ~0xC00BL);
                    if (start(thread)) return;
                } else if (word == Word.STCR0) {
                    put(Word.STR0, get(Word.STR0) & ~(value & 0xC00B));
                    if ((value & 0x100) != 0) clearPointers();
                    put(Word.STCR0, 0);
                } else if (word == Word.MCTL2) {
                    put(Word.MCTL2, value & 0xFF007F);
                    if ((value & 0x80000000L) != 0) {
                        bufferStarted = ((value >> 16) & 255) != 0;
                        if (start(thread)) return;
                    }
                } else if (trigger == WriteTrigger.TX || trigger == WriteTrigger.TX_HALF) {
                    if (trigger == WriteTrigger.TX) {
                        txHeaderKnown = true;
                        txHeader = value & 0xFFFF0000L;
                    } else value |= txHeader;
                    int mode = mode();
                    if (mode == 0 && queued + received >= 128) {
                        put(Word.STR0, get(Word.STR0) | 0x4000);
                        interrupt(thread, 0, value);
                    } else if (mode == -1 && queued >= 2) {
                        throw boundary(thread, register, "direct shift/data register already occupied");
                    } else {
                        int index = mode == -1 ? queued : pointer(Word.MRWP0, 0);
                        tx[index] = value;
                        txValid[index] = true;
                        put(Word.TX0W, value);
                        put(Word.TX0H, value & 0xFFFF);
                        if (mode <= 0) queued++;
                        if (mode != -1) pointer(Word.MRWP0, 0, (index + 1) % capacity(mode));
                        if (start(thread)) return;
                    }
                }
                status();
            }
            // A successful start publishes the new status before enqueueing the launch.
            boolean start(PcodeThread<byte[]> thread) {
                if (active) return false;
                long controlValue = get(Word.CTL0);
                if ((controlValue & 0x80) == 0 || (controlValue & 0x60) == 0) return false;
                // Direct mode does not inspect MCTL0 until after CTL1.
                boolean direct = (controlValue & 1) != 0;
                long memoryControl = direct ? 0 : get(Word.MCTL0);
                int mode = direct ? -1 : (int) (memoryControl >> 8) & 3;
                if (mode <= 0 ? queued == 0 : !bufferStarted) return false;
                if (mode == 3)
                    throw boundary(thread, reg(Word.MCTL0), "MMS=11 is prohibited");
                if ((get(Word.CTL1) & 0x4006BL) != 0)
                    throw boundary(thread, reg(Word.CTL1), "job, priority, data-consistency, loopback, handshake and slave-select pin modes are not modeled");
                if (((direct ? get(Word.MCTL0) : memoryControl) & 31) != 0)
                    throw boundary(thread, reg(Word.MCTL0), "FIFO timeout needs serial-clock elapsed-time input");
                if ((controlValue & 0x60) == 0x20)
                    throw boundary(thread, control, "receive-only clock generation requires explicit pin/clock mode");
                int index = direct ? 0 : pointer(Word.MCTL2, 0);
                if (!txValid[index]) throw boundary(thread, reg(Word.TX0W), "transfer reads unwritten transmit buffer entry " + index);
                long transmitWord = tx[index];
                int selectedLines = selectedLines(transmitWord);
                int selected = selected(selectedLines);
                long configuration = cfg(selected);
                // Section14.5.3.1: RCB priority applies only to simultaneous CS lines.
                boolean broadcast = (selectedLines & (selectedLines - 1)) != 0;
                if (broadcast && (configuration & 0x80000) != 0)
                    throw boundary(thread, reg(Word.TX0W), "broadcast has no dominant chip-select configuration");
                for (int cs = 0; cs < 8; cs++) {
                    // Still inspect unselected entries in their original order.
                    long other = cs == selected ? configuration : cfg(cs);
                    if ((selectedLines & (1 << cs)) != 0 && (other & 0x80000) == 0
                            && other != configuration)
                        throw boundary(thread, reg(Word.TX0W), "dominant broadcast configurations disagree");
                }
                if ((get(Word.CTL2) & 0xE000) != 0xE000
                        && registerValue(baudRates[(int) (configuration >> 30) & 3]) == 0) return false;
                if (!frame.isEmpty() && (frame.get(0) & 0xFF0000) != (transmitWord & 0xFF0000))
                    throw boundary(thread, reg(Word.TX0W), "EDL continuation changes chip select");
                activeWord = transmitWord;
                active = true;
                launched = false;
                status();
                int epoch = generation;
                scheduleNextTick(() -> {
                    if (epoch != generation || !active) return;
                    launched = true;
                    long word = activeWord;
                    long configurationAtLaunch = cfg(selected(selectedLines(word)));
                    int bits = dataBits(word, configurationAtLaunch);
                    long wordOrdinal = ++transmittedWords;
                    if (!trace.deviceEvents.omitsEventPayload(JsonRows.CSIH_TX.name)) {
                        trace.deviceEvents.addCsihTx(unit(), trace.instructions, activeWord, bits,
                            (configurationAtLaunch & 0x40000) != 0, wordOrdinal);
                    }
                    WireInput wire = relativeInputs.take(wordOrdinal);
                    if (wire != null) {
                        ExternalEvent input = wire.payload;
                        long tick = Math.addExact(trace.instructions, input.delay_instructions);
                        externalEvents.add(new ScheduledEvent(tick, wire.ordinal, () -> {
                            // An aborted transfer cannot consume a later word's input.
                            if (epoch != generation || wordOrdinal != transmittedWords
                                    || !active || !launched) return;
                            complete(thread, input);
                        }));
                    }
                    int launchMode = mode();
                    boolean early = launchMode == -1 || launchMode == 2;
                    boolean request = launchMode == -1 || ((get(Word.MCTL2) >> 16) & 255) == 1;
                    if (early && request && (get(Word.CTL1) & 0x10000) != 0) interrupt(thread, 2, activeWord);
                });
                return true;
            }
            int dataBits(long word) {
                return dataBits(word, cfg(selected(selectedLines(word))));
            }
            int dataBits(long word, long configuration) {
                int bits = (int) (configuration >> 24) & 15;
                return bits == 0 || ((get(Word.CTL1) & 0x80) != 0 && (word & 0x20000000L) != 0) ? 16 : bits;
            }
            static int selectedLines(long word) { return (int) (~word >> 16) & 255; }
            int selected(int lines) {
                int first = Integer.numberOfTrailingZeros(lines);
                // One asserted line wins even when recessive; the caller still reads its CFG.
                if ((lines & (lines - 1)) == 0) return first;
                for (int remaining = lines; remaining != 0; remaining &= remaining - 1) {
                    int cs = Integer.numberOfTrailingZeros(remaining);
                    if ((cfg(cs) & 0x80000) == 0) return cs;
                }
                return first;
            }
            int unit() {
                if (unit == null) unit = Integer.parseInt(prefix.substring(4));
                return unit;
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
                        int select = (int) registerValue(dmaSelector != null ? dmaSelector
                            : requiredRegister(prefix, "DMA selector", "SELCSIHDMA"));
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
                long controlValue = get(Word.CTL0);
                boolean receive = (controlValue & 0x20) != 0;
                if (receive != (input.value != null))
                    throw boundary(thread, control, "RXE requires explicit wire value; TX-only completion omits value");
                long word = activeWord;
                int memoryMode = mode(controlValue);
                int index = memoryMode == -1 ? 0 : pointer(Word.MCTL2, 0);
                if (receive) {
                    long receivedWord = (word & 0xFF0000) | (parseUnsigned(input.value) & ((1L << dataBits(word)) - 1));
                    if (memoryMode == 1 || memoryMode == 0) {
                        if (memoryMode == 0) tx[index] = receivedWord;
                        rx[index] = receivedWord;
                        rxValid[index] = true;
                        if (memoryMode == 0) received++;
                    } else {
                        if (directRxUnread) {
                            put(Word.STR0, get(Word.STR0) | 1);
                            interrupt(thread, 0, word);
                        }
                        rx[0] = receivedWord;
                        rxValid[0] = directRxUnread = true;
                    }
                    put(Word.RX0W, receivedWord);
                    put(Word.RX0H, receivedWord & 0xFFFF);
                }
                active = launched = false;
                if (memoryMode <= 0) {
                    queued--;
                    if (memoryMode == -1 && queued != 0) { tx[0] = tx[1]; txValid[0] = txValid[1]; }
                } else {
                    int remaining = (int) (get(Word.MCTL2) >> 16) & 255;
                    put(Word.MCTL2, ((long) (remaining - 1) << 16) | ((index + 1) % capacity(memoryMode)));
                    bufferStarted = remaining > 1;
                }
                if (memoryMode == 0) pointer(Word.MCTL2, 0, (index + 1) % 128);
                boolean last = memoryMode <= 0 ? queued == 0 : !bufferStarted;
                if (receive && (memoryMode == 0 ? received == 128 - (get(Word.MCTL1) & 127)
                        : memoryMode != 1 || last)) interrupt(thread, 1, word);
                boolean communicate = switch (memoryMode) {
                    case 0 -> queued == ((get(Word.MCTL1) >> 16) & 127);
                    case -1 -> (get(Word.CTL1) & 0x10000) == 0;
                    case 2 -> last && (get(Word.CTL1) & 0x10000) == 0;
                    default -> last;
                };
                if (communicate) interrupt(thread, 2, word);
                frame.add(word);
                boolean continued = (get(Word.CTL1) & 0x80) != 0 && (word & 0x20000000L) != 0;
                if (!continued) {
                    if (!trace.deviceEvents.omitsEventPayload(JsonRows.CSIH_FRAME.name)) {
                        trace.deviceEvents.addCsihFrame(unit(), trace.instructions, frame);
                    }
                    frame.clear();
                }
                if (!trace.deviceEvents.omitsEventPayload(JsonRows.CSIH_WORD.name)) {
                    trace.deviceEvents.addCsihWord(unit(), trace.instructions,
                        receive ? input.value : null, input.evidence);
                }
                status();
                start(thread);
            }
            void read(PcodeThread<byte[]> thread, RegisterDef register, boolean receive) {
                int mode = mode();
                if (receive) {
                    int index = mode == -1 || mode == 2 ? 0 : pointer(Word.MRWP0, 16);
                    if (!rxValid[index] || (mode == 0 && received == 0))
                        throw boundary(thread, register, "receive data is not supplied at buffer entry " + index);
                    setRegisterValue(register.nameBinding, register.size == 2 ? rx[index] & 0xFFFF : rx[index]);
                    directRxUnread = false;
                    if (mode == 0) received--;
                    if (mode == 0 || mode == 1) pointer(Word.MRWP0, 16, (index + 1) % capacity(mode));
                    status();
                } else {
                    if (mode == -1) {
                        if (!txHeaderKnown) throw boundary(thread, register, "direct transmit register is unwritten");
                        return;
                    }
                    int index = pointer(Word.MRWP0, 0);
                    if (!txValid[index]) throw boundary(thread, register, "transmit buffer entry is unwritten");
                    setRegisterValue(register.nameBinding, register.size == 2 ? tx[index] & 0xFFFF : tx[index]);
                    pointer(Word.MRWP0, 0, (index + 1) % capacity(mode));
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
            long clockTick, clockHorizon = Long.MAX_VALUE;

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
            boolean isTimer(RegisterDef register) { return register.writeDevice == WriteDevice.TSG; }
            void reset() {
                for (Unit u : units) u.reset();
                picTsgSources = picOtherSources = nextSources = 0;
                picRoutingDeferred = picDirty = false;
                clockTick = hsbCycles;
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
                clockTick = hsbCycles;
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
                syncClock(hsbCycles);
                if (u.offset(register) == 0x014) throw unsupported(thread, register,
                    "STR1 includes output/input pattern observations; no pin feedback is synthesized");
                u.materialize(register);
            }
            void write(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                if (isTimer(register)) {
                    syncClock(hsbCycles);
                    unit(register).write(thread, register, value);
                    // Preserve the refresh on a write after a partial edge fault.
                    if (units[0].clockDue == 0 || units[1].clockDue == 0) clockHorizonDirty = true;
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
            long cyclesUntilEvent(long tick) {
                if (clockHorizonDirty) {
                    clockHorizon = picTsgSources != 0 ? 1
                        : Math.min(units[0].remaining(clockTick), units[1].remaining(clockTick));
                    clockHorizonDirty = false;
                }
                return clockHorizon == Long.MAX_VALUE ? Long.MAX_VALUE
                    : clockHorizon - (tick - clockTick);
            }
            void syncClock(long tick) {
                // No compare, pulse fall, or counter turn occurs during this
                // span. The counters do not have to move at another device's edge.
                long span = tick - clockTick;
                if (span == 0) return;
                if (units[0].enabled) units[0].moveQuiet(span);
                if (units[1].enabled) units[1].moveQuiet(span);
                if (clockHorizon != Long.MAX_VALUE) clockHorizon -= span;
                clockTick = tick;
            }
            void recoverClock(long start) {
                // An earlier stage may have faulted before we saw this span;
                // or one TSG unit may have faulted before the other ran its edge.
                // Keep the counters/horizon the ordered stages left behind.
                if (clockTick != hsbCycles) syncClock(start);
                clockTick = hsbCycles;
                units[0].clockDue = units[1].clockDue = 0;
            }
            void advanceSpan(PcodeThread<byte[]> thread, long start, long span) {
                syncClock(start);
                Unit first = units[0], second = units[1];
                boolean firstDue = first.remaining(start) <= span;
                boolean secondDue = second.remaining(start) <= span;
                if (span > 1) {
                    first.moveQuiet(span - 1);
                    second.moveQuiet(span - 1);
                }
                clockTick = hsbCycles;
                nextSources = 0;
                // Commit every timer's clock edge before DMA can write any timer's shadow bank.
                first.advanceEdge(thread, firstDue);
                second.advanceEdge(thread, secondDue);
                if (first.interrupts != 0) first.deliver(thread);
                if (second.interrupts != 0) second.deliver(thread);
                if (picTsgSources != nextSources) {
                    picTsgSources = nextSources;
                    picSourcesChanged(thread);
                }
                clockHorizonDirty = true;
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
                long clockDue;
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
                    setRegisterValue(r.nameBinding, value);
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
                    clockDue = 0;
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
                    if (enabled && pending && reloadable(o) && value != v(o))
                        throw fault("prohibited-tsg-reload-write", thread, register.address,
                            register.size, "write", register.source_ref,
                            "changed reload value while RSF=1 (section25.4.1.3)");
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
                            else if (o == 0x034) {
                                enabled = false;
                                clockDue = NO_CLOCK_EDGE;
                                clockHorizonDirty = true;
                                publishStatus();
                            }
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
                    syncClock(hsbCycles);
                    clockDue = 0;
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
                long remaining(long tick) {
                    if (clockDue == 0) clockDue = timerDeadline(tick, cyclesUntilEvent());
                    return clockDue == NO_CLOCK_EDGE ? Long.MAX_VALUE : clockDue - tick;
                }
                void advanceEdge(PcodeThread<byte[]> thread, boolean due) {
                    if (due) {
                        clockDue = 0;
                        edge(thread);
                    } else {
                        interrupts = 0;
                        moveQuiet(1);
                    }
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
                    for (int mask = interrupts; mask != 0; mask &= mask - 1) {
                        int m = Integer.numberOfTrailingZeros(mask);
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
                syncTaudClock(hsbCycles);
                taudClockDue = 0;
                for (Unit u : units) u.reset();
                for (int n = 0; n < 2; n++) for (int g = 0; g < 5; g++)
                    adcMasks[n][g] = (int)registerValue(adcEnable[n][g]);
                picDirty = true;
            }
            void read(RegisterDef r) {
                Unit u = unit(r); int o = u.offset(r);
                if (o >= 0x80 && o < 0xc0) {
                    syncTaudClock(hsbCycles);
                    setRegisterValue(r.nameBinding, u.counters[(o - 0x80) / 4]);
                }
            }
            void flush() {
                for (Unit u : units) for (int c = 0; c < 16; c++)
                    setRegisterValue(u.count[c].nameBinding, u.counters[c]);
            }
            void validate(PcodeThread<byte[]> t, RegisterDef r, long v) {
                long mask = r.writable_mask == null ? 0xffffL : r.writable_mask;
                if ((v & ~mask) != 0) throw unsupported(t, r, "reserved bits must retain reset value");
                if (r.writeDevice == WriteDevice.TAUD) unit(r).validate(t, r, v);
            }
            void write(PcodeThread<byte[]> t, RegisterDef r, long v) {
                if (r.writeDevice == WriteDevice.TAUD) {
                    syncTaudClock(hsbCycles);
                    taudClockDue = 0;
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
                syncTaudClock(hsbCycles);
                taudClockDue = 0;
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
                invalidateClockHorizon();
                syncTaudClock(hsbCycles);
                taudClockDue = 0;
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
            void advanceSpan(PcodeThread<byte[]> t, long span) {
                for (Unit u : units) u.advance(span);
                finishEdges(t);
            }
            void finishEdges(PcodeThread<byte[]> t) {
                // Channel dependency graph points only downward: no recursion or arbitrary cutoff.
                for (Unit u : units) {
                    int held = u.signals | u.priorSignals;
                    if ((u.emitted | held) == 0) continue;
                    int raised = 0;
                    for (int pending = u.emitted & ~held; pending != 0; pending = u.emitted & ~(held | raised)) {
                        int c = Integer.numberOfTrailingZeros(pending);
                        raised |= 1 << c;
                        u.cascade(c);
                    }
                    if ((u.signals | u.emitted) != held) picDirty = true;
                    u.signals |= u.emitted;
                    u.emitted = 0;
                    u.priorSignals = 0;
                    for (int mask = raised; mask != 0; mask &= mask - 1) {
                        int c = Integer.numberOfTrailingZeros(mask);
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
                final int[] clockChannels = new int[4];
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
                    Arrays.fill(phase, 0);
                    Arrays.fill(clockChannels, 0);
                    Arrays.fill(running, false); Arrays.fill(overflow, false);
                    Arrays.fill(known, false); Arrays.fill(sampled, false); Arrays.fill(driven, false);
                    signals = emitted = priorSignals = 0;
                    enabledMask = (int)registerValue(enable);
                    tpsValue = (int)registerValue(tps); brsValue = (int)registerValue(brs); updateDivisors();
                    for (int c = 0; c < 16; c++) {
                        modes[c] = (int)registerValue(mode[c]); edges[c] = (int)registerValue(user[c]) & 3;
                        reloads[c] = (int)registerValue(data[c]); counters[c] = (int)registerValue(count[c]);
                        if (enabled(c)) clockChannels[cks(c)] |= 1 << c;
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
                    enabledMask |= mask; setRegisterValue(enable.nameBinding, enabledMask);
                    for (int c = 0; c < 16; c++) if ((mask & (1 << c)) != 0) {
                        clockChannels[cks(c)] |= 1 << c;
                        running[c] = false; overflow[c] = false;
                        if (kind(c) == 4 || sts(c) == 0 || (kind(c) == 0 && sts(c) == 1)) restart(c);
                    }
                }
                void write(PcodeThread<byte[]> t, RegisterDef r, int v) {
                    int o = offset(r);
                    if (o < 0x40) {
                        int c = o / 4;
                        if (capture(c)) setRegisterValue(r.nameBinding, registerBeforeWrite);
                        else reloads[c] = v;
                    }
                    else if (o >= 0xc0 && o < 0x100) edges[(o - 0xc0) / 4] = v & 3;
                    else if (o == 0x58) setRegisterValue(r.nameBinding,
                        (registerBeforeWrite & registerValue(outputEnable)) | (v & ~registerValue(outputEnable)));
                    else if (o == 0x1c4) { start(v); setRegisterValue(r.nameBinding, 0); }
                    else if (o == 0x1c8) {
                        enabledMask &= ~v; setRegisterValue(enable.nameBinding, enabledMask);
                        for (int c = 0; c < 16; c++) if ((v & (1 << c)) != 0) {
                            clockChannels[cks(c)] &= ~(1 << c);
                            running[c] = false;
                        }
                        setRegisterValue(r.nameBinding, 0);
                    } else if (o >= 0x180 && o < 0x1c0) {
                        int c = (o - 0x180) / 4;
                        if ((v & 1) != 0) setRegisterValue(status[c].nameBinding, registerValue(status[c]) & ~1L);
                        setRegisterValue(r.nameBinding, 0);
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
                    else if (o == 0x44) setRegisterValue(r.nameBinding, 0);
                }
                void emit(int c) {
                    emitted |= 1 << c;
                    if ((registerValue(outputEnable) & (1 << c)) != 0 && !capture(c))
                        setRegisterValue(output.nameBinding, registerValue(output) ^ (1 << c));
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
                    for (int mask = enabledMask & (-1 << (source + 1)); mask != 0; mask &= mask - 1) {
                        int c = Integer.numberOfTrailingZeros(mask);
                        int p = master(c);
                        if ((sts(c) == 4 && p == source) || (sts(c) == 5 && c == source + 1)) {
                            if (kind(c) != 8 || !running[c] || (m(c) & 1) != 0) restart(c);
                        } else if (ccs(c) == 3 && p == source && running[c]) down(c, 1);
                    }
                }
                void captureValue(int c) {
                    int cos = (m(c) >>> 6) & 3;
                    if ((cos & 2) == 0 || !overflow[c]) setRegisterValue(data[c].nameBinding, counters[c]);
                    if (cos == 0) setRegisterValue(status[c].nameBinding, overflow[c] ? 1 : 0);
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
                    if (signals != 0) return 1;
                    long next = Long.MAX_VALUE;
                    for (int mask = enabledMask; mask != 0; mask &= mask - 1) {
                        int c = Integer.numberOfTrailingZeros(mask);
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
                    // All prescalers run even when no channel selects them.
                    int dueChannels = 0;
                    for (int ck = 0; ck < 4; ck++) {
                        long div = divisor(ck);
                        if (div == 1) {
                            if (span != 1 && clockChannels[ck] != 0) ticks[ck] = span;
                        } else if (span == 1) {
                            if (++phase[ck] < div) continue;
                            phase[ck] = 0;
                        } else {
                            long mask = div - 1;
                            boolean binary = (div & mask) == 0;
                            long rest = (binary ? span & mask : span % div) + phase[ck];
                            boolean wraps = rest >= div;
                            phase[ck] = wraps ? rest - div : rest;
                            if (clockChannels[ck] == 0) continue;
                            long whole = binary ? span >>> Long.numberOfTrailingZeros(div) : span / div;
                            long amount = whole + (wraps ? 1 : 0);
                            if (amount == 0) continue;
                            ticks[ck] = amount;
                        }
                        dueChannels |= clockChannels[ck];
                    }
                    for (int mask = dueChannels; mask != 0; mask &= mask - 1) {
                        int c = Integer.numberOfTrailingZeros(mask);
                        long amount = span == 1 ? 1 : ticks[cks(c)];
                        if (inputEdge(c)) continue;
                        if (!running[c] || ccs(c) != 0) continue;
                        if (!capture(c)) down(c, amount);
                        else {
                            long sum = counters[c] + amount;
                            if (sum >= 0x10000) {
                                overflow[c] = true;
                                int cos = (m(c) >>> 6) & 3;
                                if ((cos & 1) != 0) setRegisterValue(status[c].nameBinding, registerValue(status[c]) | 1);
                                if ((cos & 2) != 0) setRegisterValue(data[c].nameBinding, 0xffff);
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
            void reset() {
                syncTaujClock(hsbCycles);
                taujClockDue = 0;
                for (Unit u : units) u.reset();
            }
            // Once after explicit scenario register seeding, not on ordinary clock advancement.
            void loadRegisters() {
                syncTaujClock(hsbCycles);
                taujClockDue = 0;
                for (Unit u : units) u.loadRegisters();
            }
            void read(PcodeThread<byte[]> thread, RegisterDef register) {
                Unit u = unit(register);
                int offset = (int) (register.address - u.base);
                if (offset >= 0x10 && offset <= 0x1c) {
                    syncTaujClock(hsbCycles);
                    u.materialize((offset - 0x10) >>> 2);
                }
            }
            void flush() { for (Unit u : units) u.flush(); }
            void validate(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                if ((value & ~register.writable_mask) != 0)
                    throw fault("reserved-tauj-bits", thread, register.address, register.size,
                        "write", register.source_ref, "reserved bits must have their reset value");
                unit(register).validate(thread, register, value);
            }
            void write(PcodeThread<byte[]> thread, RegisterDef register, long value) {
                syncTaujClock(hsbCycles);
                taujClockDue = 0;
                unit(register).write(thread, register, value);
            }
            void validateSimultaneousStart(PcodeThread<byte[]> thread, long sser2) {
                for (int n = 0; n < 2; n++) units[n].validateStart(thread, (int) (sser2 >>> (4 * n)) & 15);
            }
            void simultaneousStart(PcodeThread<byte[]> thread, long sser2) {
                validateSimultaneousStart(thread, sser2);
                syncTaujClock(hsbCycles);
                taujClockDue = 0;
                for (int n = 0; n < 2; n++) units[n].start((int) (sser2 >>> (4 * n)) & 15);
            }
            long cyclesUntilEvent() {
                long result = Long.MAX_VALUE;
                for (Unit u : units) result = Math.min(result, u.cyclesUntilEvent());
                return result;
            }
            void advanceSpan(PcodeThread<byte[]> thread, long span) {
                // Commit every counter/reload before delivering requests.
                for (Unit u : units) u.move(span);
                for (Unit u : units) u.deliver(thread, span);
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
                final boolean[] pending = new boolean[4];
                long rootPhase;
                int baudFactor, brgPhase, dirtyCounters, irqHigh, requestMask, startMask, underflowMask;

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
                    setRegisterValue(r.nameBinding, value);
                }
                void count(int c, long value) {
                    if (state[4 + c] == value) return;
                    state[4 + c] = value;
                    dirtyCounters |= 1 << c;
                }
                void materialize(int c) {
                    if ((dirtyCounters & (1 << c)) == 0) return;
                    setRegisterValue(counter[c].nameBinding, state[4 + c]);
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
                    if (cycles == 1) return phase(ck) == divisor - 1 ? 1 : 0;
                    return cycles / divisor + (cycles % divisor + phase(ck)) / divisor;
                }
                void reset() {
                    rootPhase = 0;
                    brgPhase = irqHigh = requestMask = startMask = underflowMask = 0;
                    Arrays.fill(pending, false);
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
                        irqHigh &= ~mask;
                        for (int c = 0; c < 4; c++) if ((mask & (1 << c)) != 0) pending[c] = false;
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
                    if (irqHigh != 0) return 1;
                    long result = Long.MAX_VALUE;
                    for (int mask = enabled(); mask != 0; mask &= mask - 1) {
                        int c = Integer.numberOfTrailingZeros(mask);
                        int ck = clock(c);
                        long counts = pending[c] ? 1 : state[4 + c] + 1;
                        // Maximum = 2^32 * (32768*256) < Long.MAX_VALUE.
                        result = Math.min(result, counts * div[ck] - phase(ck));
                    }
                    return result;
                }
                void move(long cycles) {
                    startMask = underflowMask = 0;
                    int pulses = 0;
                    for (int mask = enabled(); mask != 0; mask &= mask - 1) {
                        int c = Integer.numberOfTrailingZeros(mask), bit = 1 << c;
                        long countTicks = ticks(clock(c), cycles);
                        if (countTicks == 0) continue;
                        if (pending[c]) {
                            if (countTicks != 1) throw new IllegalStateException("TAUJ start edge was skipped");
                            pending[c] = false;
                            count(c, v(data[c]));
                            startMask |= bit;
                            if ((v(mode[c]) & 1) != 0) pulses |= bit;
                        } else {
                            long current = state[4 + c];
                            if (countTicks <= current) count(c, current - countTicks);
                            else {
                                if (countTicks != current + 1)
                                    throw new IllegalStateException("TAUJ underflow edge was skipped");
                                count(c, v(data[c]));
                                underflowMask |= bit;
                                pulses |= bit;
                            }
                        }
                    }
                    // Pulses last one HSB clock. Adjacent pulses remain high,
                    // notably CDR=0/divisor=1 (manual Figure24.17).
                    requestMask = cycles == 1 ? pulses & ~irqHigh : pulses;
                    irqHigh = pulses;
                    if (pulses != 0) {
                        long flip = pulses & v(toe);
                        if (flip != 0) put(to, v(to) ^ flip);
                    }
                    if (baudFactor != 1) {
                        long mask = pre[3] - 1;
                        if (cycles == 1) {
                            if ((rootPhase & mask) == mask && ++brgPhase == baudFactor) brgPhase = 0;
                        } else {
                            int shift = Long.numberOfTrailingZeros(pre[3]);
                            long preTicks = (cycles >>> shift)
                                + (((cycles & mask) + (rootPhase & mask)) >>> shift);
                            brgPhase = (int) ((brgPhase + preTicks % baudFactor) % baudFactor);
                        }
                    }
                    rootPhase = (rootPhase + (cycles & 32767)) & 32767;
                }
                void deliver(PcodeThread<byte[]> thread, long span) {
                    int events = startMask | underflowMask;
                    for (int mask = events | requestMask; mask != 0; mask &= mask - 1) {
                        int c = Integer.numberOfTrailingZeros(mask);
                        if ((events & (1 << c)) != 0 && !trace.deviceEvents.omitsEventPayload("tauj-clock")) {
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
                setRegisterValue(start.nameBinding, 0);
            }
        }

        final class Adc {
            static final long NEVER = Long.MAX_VALUE;
            static final long FIRST_ADDRESS = 0xfff91000L, END_ADDRESS = FIRST_ADDRESS + 0x2000;
            final Unit[] units;
            final boolean fullPinPackage;
            final RegisterDef selector = requiredRegister("ADCG", "clock", "CKSC8C");
            final RegisterDef selectorStatus = requiredRegister("ADCG", "clock status", "CKSC8S");
            long now;
            long hsbRemainder;
            private long clockTick, clockDue;
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
                long auxiliaryDeadline = NEVER;
                boolean auxiliaryDeadlineDirty;
                boolean errorLine;

                Unit(int number) {
                    this.number = number;
                    base = FIRST_ADDRESS + number * 0x1000L;
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
                void put(int offset, long value) { setRegisterValue(reg(offset).nameBinding, value); }
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
                    setConversionDeadline(NEVER);
                    Arrays.fill(active, false);
                    Arrays.fill(timerDue, NEVER);
                    Arrays.fill(irqDue, NEVER);
                    auxiliaryDeadline = NEVER;
                    auxiliaryDeadlineDirty = false;
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
                            setConversionDeadline(NEVER);
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
                    setConversionDeadline(Math.addExact(now, sampleCycles()));
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
                    setConversionDeadline(Math.addExact(now, 22));
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
                        setConversionDeadline(Math.addExact(now, sampleCycles()));
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
                    if (output) setIrqDeadline(group, Math.addExact(now, 6 / clockDivisor()));
                    if (endOfCycle) {
                        if (!continuous && --cyclesLeft[group] == 0) {
                            active[group] = false;
                            status(group);
                        } else pointer[group] = (int) get(sg(group) + 0x14);
                    } else pointer[group]++;
                    current = -1;
                    setConversionDeadline(NEVER);
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
                    setConversionDeadline(NEVER);
                    request(thread, group);
                }
                void startTimer(PcodeThread<byte[]> thread, int group) {
                    if (timerDue[group] != NEVER) return;
                    setTimerDeadline(group, Math.addExact(now, get(sg(group) + 0x28)));
                    status(group);
                    // ADTIP=0 emits its first trigger simultaneously with start.
                    if (timerDue[group] == now) timer(thread, group);
                }
                void timer(PcodeThread<byte[]> thread, int group) {
                    setTimerDeadline(group, Math.addExact(now, get(sg(group) + 0x2c) + 1));
                    if ((get(sg(group) + 0x10) & 3) >= 2) request(thread, group);
                }
                void setConversionDeadline(long due) {
                    conversionDue = due;
                    clockDue = 0;
                }
                void setTimerDeadline(int group, long due) {
                    timerDue[group] = due;
                    auxiliaryDeadlineDirty = true;
                    clockDue = 0;
                }
                void setIrqDeadline(int group, long due) {
                    irqDue[group] = due;
                    auxiliaryDeadlineDirty = true;
                    clockDue = 0;
                }
                long nextDeadline() {
                    if (auxiliaryDeadlineDirty) {
                        long next = NEVER;
                        for (int group = 0; group < 5; group++)
                            next = Math.min(next, Math.min(timerDue[group], irqDue[group]));
                        auxiliaryDeadline = next;
                        auxiliaryDeadlineDirty = false;
                    }
                    return Math.min(conversionDue, auxiliaryDeadline);
                }
                void advance(PcodeThread<byte[]> thread) {
                    // Stable ordering for coincident timer/results: result commits before a new edge.
                    boolean auxiliaryDue = auxiliaryDeadline == now;
                    if (conversionDue == now) {
                        if (phase == 1) sample(thread); else result(thread);
                    }
                    if (!auxiliaryDue) return;
                    for (int group = 0; group < 5; group++) {
                        if (timerDue[group] == now) timer(thread, group);
                        if (irqDue[group] == now) {
                            setIrqDeadline(group, NEVER);
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
                        if (sub == 12 && (value & 1) != 0) { setTimerDeadline(group, NEVER); status(group); }
                    }
                    if (!reg(offset).access.contains("r")) put(offset, 0);
                }
            }

            void initializeClock() {
                long control = registerValue(selector);
                if (control != 2 && control != 4)
                    throw new IllegalArgumentException("CKSC8C requires 2 or 4");
                syncClock();
                clockDue = 0;
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
            void syncClock() {
                long span = hsbCycles - clockTick;
                if (span == 0) return;
                // The ADC advances at no more than half the HSB rate, and
                // the remainder never exceeds the already elapsed HSB time.
                long total = Math.addExact(hsbRemainder, span);
                long cycles = total >>> clockDivisor();
                hsbRemainder = total & (clockSelection - 1);
                now = Math.addExact(now, cycles);
                clockTick = hsbCycles;
            }
            void advanceAtDeadline(PcodeThread<byte[]> thread) {
                syncClock();
                clockDue = 0;
                for (;;) {
                    boolean first = units[0].nextDeadline() == now;
                    boolean second = units[1].nextDeadline() == now;
                    if (!first && !second) return;
                    if (first) units[0].advance(thread);
                    if (second) units[1].advance(thread);
                }
            }
            void hardwareTrigger(PcodeThread<byte[]> thread, int unit, int group) {
                if (unit < 0 || unit > 1 || group < 0 || group > 4) throw new IllegalArgumentException("invalid ADC hardware trigger");
                Unit adc = units[unit];
                int mode = (int) adc.get(adc.sg(group) + 0x10) & 3;
                if (group >= 3 && mode == 3) { syncClock(); adc.startTimer(thread, group); return; }
                if (mode != 1) return;
                syncClock();
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
                syncClock();
                for (Unit adc : units) for (int group = timerStart ? 3 : 0; group < 5; group++) {
                    long control = adc.get(adc.sg(group) + 0x10);
                    if ((control & (timerStart ? 0x80 : 0x40)) == 0) continue;
                    if (timerStart) adc.startTimer(thread, group); else adc.request(thread, group);
                }
            }
            long cyclesUntilEvent() {
                if (clockDue != 0)
                    return clockDue == NO_CLOCK_EDGE ? NEVER : clockDue - hsbCycles;
                syncClock();
                long next = Math.min(units[0].nextDeadline(), units[1].nextDeadline());
                long remaining = next == NEVER ? NEVER
                    : Math.subtractExact(Math.multiplyExact(next - now, 2L * clockDivisor()), hsbRemainder);
                if (remaining > 0) clockDue = timerDeadline(hsbCycles, remaining);
                return remaining;
            }
            void reset() {
                syncClock();
                clockDue = 0;
                for (Unit adc : units) adc.reset();
                hsbRemainder = 0;
                clockSelection = 2;
                // Keep monotonic named-domain time; reset invalidates all live deadlines.
            }
            void beforeRead(boolean reflectSelector) {
                // Results and busy flags are committed only by named clock progress, not polling.
                syncClock();
                if (reflectSelector)
                    setRegisterValue(selectorStatus, clockSelection | 1);
            }
            void readCompleted(PcodeThread<byte[]> thread, long address, int size) {
                long relative = address - units[0].base;
                long unit = relative >>> 12;
                if (unit >= units.length) return;
                int offset = (int) relative & 0xfff;
                Unit adc = units[(int) unit];
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
                syncClock();
                if ("adc-clock".equals(register.behavior)) {
                    if (value != registerBeforeWrite) hsbRemainder %= 2; // Preserve HSB-to-LSB half-cycle phase.
                    clockDue = 0;
                    clockSelection = (int) value;
                    setRegisterValue(selectorStatus, value | 1);
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
                syncClock();
                if (trace.deviceEvents.omitsEventPayload("external-adc-sample")) return;
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
            static final long FIRST_ADDRESS = 0xffe05000L;
            static final long FIRST_RX_DATA = FIRST_ADDRESS + 4 * FRXD, SECOND_RX_DATA = FIRST_RX_DATA + 0x1000;
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
                final WireInputs relativeInputs = new WireInputs();
                int generation;
                int[] pulses;
                int phase, statusNibble, crc, packed;
                long calibration, messageSamples, capturedTimestamp;
                String inputEvidence;
                Unit(int number) {
                    this.number=number;
                    base=FIRST_ADDRESS+number*0x1000L;
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
                    setRegisterValue(regs[index].nameBinding,v[index]);
                }
                void driveStatus(boolean asserted) {
                    // Table6.11: this source is a level, unlike the receive IRQ.
                    // Follow existing CAN level-source convention; preserve EIMK/EIP/EITB.
                    long old=registerValue(statusInterrupt);
                    long next=(old&~0x1000L)|(asserted ? 0x1000L : 0);
                    if(next!=old) setRegisterValue(statusInterrupt.nameBinding,next);
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
                    WireInput wire = relativeInputs.take(spcSequence);
                    if (wire != null) {
                        ExternalEvent input = wire.payload;
                        if (input.delay_hsb_cycles < spcDue - now)
                            throw new IllegalArgumentException("RSENT response overlaps its SPC output pulse");
                        int epoch = generation;
                        long sequence = spcSequence;
                        wireEvents.add(new ScheduledEvent(Math.addExact(now, input.delay_hsb_cycles),
                            wire.ordinal, () -> {
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
                if (trace.deviceEvents.omitsEventPayload(kind)) return;
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
                syncRsentClock(hsbCycles);
                rsentClockDue = -1;
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
                if(i==TSC) {
                    syncRsentClock(hsbCycles);
                    u.put(TSC,u.v[TSC]);
                }
            }
            void readCompleted(PcodeThread<byte[]> thread,long address,int size) {
                if(size!=4) return;
                if(address==FIRST_RX_DATA) units[0].promote(thread);
                else if(address==SECOND_RX_DATA) units[1].promote(thread);
            }
            boolean receive(PcodeThread<byte[]> thread,int number,int[] pulseSamples,String source) {
                syncRsentClock(hsbCycles);
                rsentClockDue = -1;
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
            long nextEventTick() {
                ScheduledEvent wire = wireEvents.peek();
                long due = wire == null ? NEVER : wire.tick;
                for(Unit u:units) due=Math.min(due,Math.min(u.spcDue,u.pulseDue));
                return due;
            }
            void moveClock(long span) {
                long end = Math.addExact(now, span);
                for (Unit u : units) if (u.running()) {
                    long divisor = u.timestampDivisor();
                    if (span == 1) {
                        long rem = u.timestampRemainder + 1;
                        if (rem == divisor) {
                            u.v[TSC] = (u.v[TSC] + 1) & 0xffffffffL;
                            rem = 0;
                        }
                        u.timestampRemainder = rem;
                    } else {
                        long ticks = span / divisor;
                        long rem = u.timestampRemainder + span % divisor;
                        boolean wraps = rem >= divisor;
                        u.v[TSC] = (u.v[TSC] + ticks + (wraps ? 1 : 0)) & 0xffffffffL;
                        u.timestampRemainder = wraps ? rem - divisor : rem;
                    }
                }
                now = end;
            }
            void advanceSpan(PcodeThread<byte[]> thread, long span, boolean atEvent) {
                moveClock(span);
                if (!atEvent && now != NEVER) return;
                long next;
                do {
                    for (Unit u : units) {
                        if (u.spcDue == now) {
                            u.spcDue = NEVER;
                            event("rsent-spc-end", u, "trigger waveform complete; response still outstanding");
                        }
                        if (u.pulseDue == now) u.pulseBoundary(thread);
                    }
                    while (!wireEvents.isEmpty() && wireEvents.peek().tick <= now)
                        wireEvents.remove().action.run();
                } while ((next = nextEventTick()) != NEVER && next <= now);
            }
            void flush() { for(Unit u:units) u.put(TSC,u.v[TSC]); }
            void reset() {
                // Keep monotonic HSB time, invalidate every live deadline and frame.
                syncRsentClock(hsbCycles);
                rsentClockDue = -1;
                masterSelect=0; setRegisterValue(selector.nameBinding,0);
                for(Unit u:units) u.resetUnit();
            }
            void loadInitialState(PcodeThread<byte[]> thread) {
                // Call ONCE after reset plus scenario register initialization. Do not call on every read.
                syncRsentClock(hsbCycles);
                rsentClockDue = -1;
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
            private static final long CHANNEL_BASE = 0xffff8400L;
            private static final int CHANNEL_MASK = 0xffff;
            private static final int SELECTORS = 128; // DTFR.REQSEL is seven bits.
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

            WordIndex watchWords(P1MEJitMachine.MachineState state) {
                RegisterDef[][] groups = new RegisterDef[channels.length * 2][];
                for (Channel channel : channels) {
                    int n = channel.number;
                    long base = CHANNEL_BASE + n * 64L;
                    RegisterDef[] bank = channel.bank;
                    if (bank[DTCT].address != base + DTCT * 4L ||
                            bank[DCST].address != base + DCST * 4L ||
                            bank[DCEN].address != base + DCEN * 4L ||
                            bank[DTFR].address != base + DTFR * 4L ||
                            bank[DTFRRQ].address != base + DTFRRQ * 4L ||
                            bank[DTFRRQ].size != Integer.BYTES) return null;
                    groups[n] = new RegisterDef[] {bank[DTCT], bank[DCST], bank[DCEN]};
                    groups[n + channels.length] = new RegisterDef[] {bank[DTFR]};
                }
                var words = state.watchDeviceWords(groups);
                return words == null ? null : new WordIndex(state, words);
            }

            // Derived only from fully populated physical words. An unavailable
            // input never performs an inspect callback here; callers use the
            // original ordered scans when the relevant mask is incomplete.
            final class WordIndex {
                final P1MEJitMachine.MachineState state;
                final P1MEJitMachine.DeviceWordIndex words;
                final boolean bigEndian = language.isBigEndian();
                final int[] selectors = new int[channels.length];
                final int[] requestChannels = new int[SELECTORS];
                int arbitrationKnown, ready, enabled, selectorsKnown;

                WordIndex(P1MEJitMachine.MachineState state, P1MEJitMachine.DeviceWordIndex words) {
                    this.state = state;
                    this.words = words;
                    Arrays.fill(selectors, -1);
                }

                private long inspect(RegisterDef register) {
                    return missingResetInput(register) ? -1
                        : state.inspectInitializedDevice(register, bigEndian);
                }

                long readiness(int mask) {
                    int dirty = (int) words.takeDirty(mask);
                    arbitrationKnown &= ~dirty;
                    enabled &= ~dirty;
                    ready &= ~dirty;
                    while (dirty != 0) {
                        int n = Integer.numberOfTrailingZeros(dirty);
                        int bit = 1 << n;
                        dirty ^= bit;
                        RegisterDef[] bank = channels[n].bank;
                        long configuration = inspect(bank[DTCT]);
                        long status = inspect(bank[DCST]);
                        long enable = inspect(bank[DCEN]);
                        if ((configuration | status | enable) < 0) continue;
                        arbitrationKnown |= bit;
                        if (!channelEnabled(configuration, status, enable)) continue;
                        enabled |= bit;
                        if (channelRequested(configuration, status)) ready |= bit;
                    }
                    return (arbitrationKnown & mask) == mask ? ((long) enabled << 16) | ready : -1;
                }

                int requesting(int source) {
                    if (source < 0 || source >= requestChannels.length) return -1;
                    int dirty = (int) (words.takeDirty((long) CHANNEL_MASK << 16) >>> 16);
                    selectorsKnown &= ~dirty;
                    while (dirty != 0) {
                        int n = Integer.numberOfTrailingZeros(dirty);
                        int bit = 1 << n;
                        dirty ^= bit;
                        int oldSource = selectors[n];
                        if (oldSource >= 0) requestChannels[oldSource] &= ~bit;
                        selectors[n] = -1;
                        long word = inspect(channels[n].bank[DTFR]);
                        if (word < 0) continue;
                        selectorsKnown |= bit;
                        int newSource = (int) (word >>> 1);
                        if (newSource >= requestChannels.length) continue;
                        selectors[n] = newSource;
                        requestChannels[newSource] |= bit;
                    }
                    return selectorsKnown == CHANNEL_MASK ? requestChannels[source] : -1;
                }
            }

            private static boolean channelEnabled(long configuration, long status, long enable) {
                return (enable & 1) != 0
                    && ((configuration & 0x2000) != 0 || (status & 0x10) == 0)
                    && ((configuration & 0x08000000L) == 0 || (status & 0x80) == 0);
            }

            private static boolean channelRequested(long configuration, long status) {
                return (status & ((configuration & 0x04000000L) != 0 ? 2 : 1)) != 0;
            }

            final class Channel {
                final int number;
                final String initiator;
                final RegisterDef[] bank = new RegisterDef[15];
                final RegisterDef master;
                long source, destination, count, control;
                int size;
                byte[] data, transferBuffer;
                boolean readDone;

                Channel(int number) {
                    this.number = number;
                    initiator = "DMAC" + (number / 8) + "." + (number % 8);
                    for (int n = 0; n < bank.length; n++) {
                        bank[n] = register(CHANNEL_BASE + number * 64L + n * 4L, 4);
                        if (bank[n] == null)
                            throw new IllegalStateException("DMAC channel register missing: " + number + "/" + n);
                    }
                    master = requiredRegister(initiator, "master configuration",
                        "DM" + (number / 8) + (number % 8) + "CM");
                }

                long get(int index) { return registerValue(bank[index]); }
                void put(int index, long value) { setRegisterValue(bank[index], value); }
                int spid() { return Math.max(2, (int) (registerValue(master) >>> 2) & 31); }

                private boolean hardwareRequested(long configuration) {
                    return (configuration & 0x04000000L) != 0 && (get(DTFR) & get(DTFRRQ) & 1) != 0;
                }

                private void updateRequestStatus(long status, boolean requested) {
                    put(DCST, (status & ~2L) | (requested ? 2 : 0));
                }

                void refreshRequest() {
                    boolean requested = hardwareRequested(get(DTCT));
                    updateRequestStatus(get(DCST), requested);
                }

                boolean enabled() {
                    long configuration = get(DTCT), status = get(DCST);
                    return channelEnabled(configuration, status, get(DCEN));
                }

                boolean ready() {
                    long configuration = get(DTCT), status = get(DCST);
                    return channelEnabled(configuration, status, get(DCEN))
                        && channelRequested(configuration, status);
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
                    // Publish BUSY before inspecting the hardware request inputs.
                    updateRequestStatus(status, hardwareRequested(control));
                    setRegisterValue(cycles, registerValue(cycles) | (1L << number));
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
                        setRegisterValue(errors, registerValue(errors) | (1L << number));
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
                    long compare = get(DTCC);
                    boolean match = compare != 0 && (count & 0xffff) == compare;
                    if (last) {
                        status |= 0x10;
                        if ((control & 0x2000) == 0) put(DCEN, 0);
                    }
                    if (match) status |= 0x20;
                    put(DCST, status);
                    setRegisterValue(cycles, registerValue(cycles) & ~(1L << number));
                    if ((last && (control & 0x4000) != 0) || (match && (control & 0x8000) != 0))
                        requestInterrupt(thread, 16 + number);
                    int chain = (int) (control >>> 16) & 3;
                    if (chain == 3 || (chain == 1 && last)) {
                        Channel next = channels[(number & 8) | ((int) (control >>> 18) & 7)];
                        // Section7.5.4: chain compares PEID and UM, not SPID.
                        if (((registerValue(master) ^ registerValue(next.master)) & 0xe002) == 0)
                            next.put(DCST, next.get(DCST) | 1);
                    }
                    trace.deviceEvents.addDmaTransfer(number, source, destination, size,
                        remaining, error, trace.instructions, hsbCycles);
                }
            }

            long nextAddress(long address, int mode, int size) {
                return (address + (mode == 0 ? size : mode == 1 ? -size : 0)) & 0xffffffffL;
            }

            Channel channel(RegisterDef register) {
                if (register.address >= CHANNEL_BASE && register.address < CHANNEL_BASE + channels.length * 64L)
                    return channels[(int) ((register.address - CHANNEL_BASE) >>> 6)];
                return null;
            }

            void reset() {
                if (dmaWordIndex != null) dmaWordIndex.words.invalidateAll();
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
                if (active[0] != null || active[1] != null) {
                    nextService = Math.addExact(hsbCycles, 1);
                    return;
                }
                if ((registerValue(suspension) & 1) != 0) return;
                if (dmaWordIndex != null) {
                    long readiness = dmaWordIndex.readiness(CHANNEL_MASK);
                    if (readiness >= 0) {
                        for (Channel owner : blockOwner) {
                            if (owner == null || (readiness & (1L << (16 + owner.number))) == 0) continue;
                            nextService = Math.addExact(hsbCycles, 1);
                            return;
                        }
                        if ((readiness & CHANNEL_MASK) != 0)
                            nextService = Math.addExact(hsbCycles, 1);
                        return;
                    }
                }
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

            private Channel select(int group) {
                Channel owner = blockOwner[group];
                int first = group * 8;
                if (dmaWordIndex != null) {
                    int mask = 0xff << first;
                    long readiness = dmaWordIndex.readiness(mask);
                    if (readiness >= 0) {
                        if (owner != null && (readiness & (1L << (16 + owner.number))) != 0)
                            return owner;
                        int candidates = (int) readiness & mask;
                        if (candidates != 0) return channels[Integer.numberOfTrailingZeros(candidates)];
                        return null;
                    }
                }
                if (owner != null && owner.enabled()) return owner;
                for (int n = first; n < first + 8; n++) {
                    if (channels[n].ready()) return channels[n];
                }
                return null;
            }

            void advanceClock(PcodeThread<byte[]> thread) {
                this.thread = thread;
                nextService = Long.MAX_VALUE;
                if ((registerValue(suspension) & 1) == 0) {
                    for (int group = 0; group < active.length; group++) {
                        if (active[group] != null) continue;
                        Channel selected = select(group);
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
                if (dmaWordIndex != null) {
                    int candidates = dmaWordIndex.requesting(source);
                    if (candidates >= 0) {
                        if (candidates == 0) return;
                        do {
                            int n = Integer.numberOfTrailingZeros(candidates);
                            candidates ^= 1 << n;
                            latchRequest(channels[n]);
                        } while (candidates != 0);
                        schedule(thread);
                        return;
                    }
                }
                boolean selected = false;
                for (Channel channel : channels) {
                    if ((channel.get(DTFR) >>> 1) != source) continue;
                    latchRequest(channel);
                    selected = true;
                }
                if (selected) schedule(thread);
            }

            private void latchRequest(Channel channel) {
                // The selector/hold circuit runs even when REQEN or DTE
                // is zero (Section7.4.3). A second edge latches OVF.
                long request = channel.get(DTFRRQ);
                channel.put(DTFRRQ, request | 1 | ((request & 1) != 0 ? 2 : 0));
                channel.refreshRequest();
            }

            boolean authorizeCpuWrite(PcodeThread<byte[]> thread, RegisterDef register) {
                if (register.address < 0xffff8000L || register.address >= 0xffff8800L
                        || !userMode(thread)) return true;
                Channel channel = channel(register);
                // Table7.12: only CPU1 supervisor is the special master.
                // General masters cannot change common configuration.
                if (channel == null) return false;
                long identity = registerValue(channel.master);
                int spid = cpuSpid(thread);
                if ((identity & 0xe002) == 0x2002 && channel.spid() == spid) return true;
                RegisterDef captured = violations[channel.number / 8];
                if ((registerValue(captured) & 1) == 0)
                    setRegisterValue(captured,
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
                            setRegisterValue(errors, registerValue(errors) & ~(1L << channel.number));
                    } else if (index == DTFRRQC) channel.put(DTFRRQ, channel.get(DTFRRQ) & ~value);
                    channel.refreshRequest();
                } else if ("CMVC".equals(register.name)) {
                    for (int n = 0; n < violations.length; n++)
                        if ((value & (1L << n)) != 0)
                            setRegisterValue(violations[n], registerValue(violations[n]) & ~1L);
                }
                if (register.read_value != null) setRegisterValue(register.nameBinding, register.read_value);
                schedule(thread);
            }
        }

        final class EventSocket implements Closeable {

            final ServerSocket server;
            final Socket socket;
            final BufferedReader input;
            final PrintWriter output;
            final PcodeThread<byte[]> thread;
            final long readyAddress;
            final long readyArrivalAddress;
            final long readyArrivalCount;
            long readyArrivals;
            boolean ready;
            // An eight-byte classic frame holds the bus for 108 bit times plus the
            // 3-bit intermission. Classic CAN runs at at most 1 Mbit/s and the model
            // spends one 80 MHz cycle per instruction, so no completion and no
            // neighbouring frame can be observed sooner than this many instructions.
            private static final long CAN_FRAME_INSTRUCTIONS = 8_880;
            final ArrayDeque<JsonObject> pendingCanTransmits = new ArrayDeque<>();
            long busFreeAt;
            record SocketLine(String line, IOException failure) {}
            final ConcurrentLinkedQueue<SocketLine> inputLines = new ConcurrentLinkedQueue<>();
            final Thread inputThread;
            final boolean holdWhenReady;
            // A requested hold parks the thread at a later foreground arrival, so
            // the host samples memory at the same instruction as a scenario trial.
            long holdArrivals = -1;

            EventSocket(EventSocketConfig config, PcodeThread<byte[]> thread) throws IOException {
                this.thread = thread;
                InetAddress host = InetAddress.getByName(config.host);
                if (!host.isLoopbackAddress())
                    throw new IllegalArgumentException("event_socket host must be loopback");
                server = new ServerSocket(config.port, 1, host);
                socket = server.accept();
                socket.setSoTimeout(0);
                input = new BufferedReader(new InputStreamReader(
                    socket.getInputStream(), StandardCharsets.UTF_8));
                output = new PrintWriter(socket.getOutputStream(), true, StandardCharsets.UTF_8);
                holdWhenReady = config.hold_when_ready;
                inputThread = new Thread(() -> {
                    try {
                        while (true) {
                            String line = input.readLine();
                            inputLines.add(new SocketLine(line, null));
                            if (line == null) return;
                        }
                    }
                    catch (IOException exception) {
                        inputLines.add(new SocketLine(null, exception));
                    }
                }, "p1me-event-socket-reader");
                inputThread.setDaemon(true);
                inputThread.start();
                readyAddress = config.ready_address == null
                    ? -1 : parseUnsigned(config.ready_address);
                readyArrivalAddress = config.ready_after_arrivals == null
                    ? -1 : parseUnsigned(config.ready_after_arrivals.address);
                readyArrivalCount = config.ready_after_arrivals == null
                    ? -1 : config.ready_after_arrivals.count;
                trace.memoryAccesses.discard = true;
                trace.deviceEvents.listener = this::publish;
                trace.deviceEvents.discard = true;
                if (readyAddress < 0 && readyArrivalAddress < 0) publishReady();
            }

            void publishReady() {
                JsonObject row = new JsonObject();
                row.addProperty("kind", "machine-ready");
                row.addProperty("held", holdWhenReady);
                row.addProperty("instruction", trace.instructions);
                output.println(new Gson().toJson(row));
                ready = true;
            }

            void poll(PcodeThread<byte[]> thread) {
                long pc = thread.getCounter().getOffset();
                if (!ready && (pc == readyAddress || (pc == readyArrivalAddress
                        && ++readyArrivals == readyArrivalCount))) {
                    publishReady();
                    if (holdWhenReady) hold(thread);
                }
                else if (ready && pc == readyArrivalAddress) {
                    JsonObject row = new JsonObject();
                    row.addProperty("kind", "instruction-arrival");
                    row.addProperty("address", hex32(pc));
                    row.addProperty("instruction", trace.instructions);
                    output.println(new Gson().toJson(row));
                    if (holdArrivals > 0 && --holdArrivals == 0) hold(thread);
                }
                SocketLine next;
                while ((next = inputLines.poll()) != null) serve(socketLine(next), thread);
            }

            String socketLine(SocketLine next) {
                if (next.failure() != null)
                    throw new IllegalStateException("event socket read failed", next.failure());
                return next.line();
            }

            void hold(PcodeThread<byte[]> thread) {
                JsonObject held = new JsonObject();
                held.addProperty("kind", "machine-held");
                held.addProperty("instruction", trace.instructions);
                output.println(new Gson().toJson(held));
                while (true) {
                    SocketLine next = inputLines.poll();
                    if (next != null && !serve(socketLine(next), thread)) return;
                    java.util.concurrent.locks.LockSupport.parkNanos(100_000L);
                }
            }

            /** Handles one host line; returns false when a resume ends a hold. */
            boolean serve(String line, PcodeThread<byte[]> thread) {
                if (line == null) throw new MachineHalt("event-socket-closed");
                JsonObject row = GSON.fromJson(line, JsonObject.class);
                String kind = row.get("kind").getAsString();
                if ("stop".equals(kind)) throw new MachineHalt("event-socket-stop");
                if ("memory-read".equals(kind)) {
                    long address = parseUnsigned(row.get("address").getAsString());
                    int size = row.get("size").getAsInt();
                    if (size <= 0 || size > 0x10000)
                        throw new IllegalArgumentException("event_socket memory-read size must be 1..65536");
                    JsonObject response = new JsonObject();
                    response.addProperty("kind", "memory-read");
                    response.addProperty("request_id", row.get("request_id").getAsString());
                    response.addProperty("address", hex32(address));
                    response.addProperty("size", size);
                    response.addProperty("data_hex", byteHex(memory(thread, address, size)));
                    response.addProperty("instruction", trace.instructions);
                    output.println(new Gson().toJson(response));
                    return true;
                }
                if ("resume".equals(kind)) {
                    JsonObject response = new JsonObject();
                    response.addProperty("kind", "resumed");
                    response.addProperty("request_id", row.get("request_id").getAsString());
                    output.println(new Gson().toJson(response));
                    return false;
                }
                if ("hold-at-arrival".equals(kind)) {
                    long arrivals = row.get("arrivals").getAsLong();
                    if (arrivals < 1)
                        throw new IllegalArgumentException("event_socket hold-at-arrival count must be positive");
                    holdArrivals = arrivals;
                    JsonObject response = new JsonObject();
                    response.addProperty("kind", "hold-armed");
                    response.addProperty("request_id", row.get("request_id").getAsString());
                    response.addProperty("instruction", trace.instructions);
                    output.println(new Gson().toJson(response));
                    return true;
                }
                if ("reset-assert".equals(kind)) {
                    ready = false;
                    readyArrivals = 0;
                    holdArrivals = -1;
                    pendingCanTransmits.clear();
                    busFreeAt = 0;
                    ExternalEvent event = GSON.fromJson(row, ExternalEvent.class);
                    if (event.evidence == null || event.evidence.isBlank())
                        event.evidence = "loopback event socket";
                    applyExternalEvent(thread, event);
                    JsonObject response = new JsonObject();
                    response.addProperty("kind", "reset-asserted");
                    response.addProperty("request_id", row.get("request_id").getAsString());
                    response.addProperty("reset_class", event.reset_class);
                    response.addProperty("instruction", trace.instructions);
                    output.println(new Gson().toJson(response));
                    return true;
                }
                if (!Set.of("can-rx", "clock", "interrupt").contains(kind))
                    throw new IllegalArgumentException(
                        "event_socket accepts can-rx, clock, interrupt, memory-read, hold-at-arrival, resume, reset-assert, or stop");
                ExternalEvent event = GSON.fromJson(row, ExternalEvent.class);
                if (event.evidence == null || event.evidence.isBlank())
                    event.evidence = "loopback event socket";
                if ("can-rx".equals(kind)) {
                    event.socket_poll_instruction = trace.instructions;
                    busFreeAt = Math.max(trace.instructions, busFreeAt) + CAN_FRAME_INSTRUCTIONS;
                    long arrival = busFreeAt;
                    externalEvents.add(new ScheduledEvent(
                        arrival, nextEventOrdinal++, () -> applyExternalEvent(thread, event)));
                    return true;
                }
                applyExternalEvent(thread, event);
                return true;
            }

            void publish(JsonObject row) {
                String kind = row.get("kind").getAsString();
                if ("can-rx".equals(kind) || "can-rx-discard".equals(kind)
                        || "can-rx-pop".equals(kind)) {
                    output.println(new Gson().toJson(row));
                    return;
                }
                if ("interrupt-return".equals(kind)) {
                    output.println(new Gson().toJson(row));
                    if (row.has("channel") && row.get("channel").getAsInt() == 188) {
                        while (!pendingCanTransmits.isEmpty())
                            output.println(new Gson().toJson(pendingCanTransmits.remove()));
                    }
                    return;
                }
                if (!"can-tx".equals(kind)) return;
                int buffer = row.get("buffer").getAsInt();
                busFreeAt = Math.max(trace.instructions, busFreeAt) + CAN_FRAME_INSTRUCTIONS;
                long completion = busFreeAt;
                scheduleAt(completion, () -> {
                    ExternalEvent event = new ExternalEvent();
                    event.kind = "can-tx-complete";
                    event.buffer = buffer;
                    event.firmware_control = "0x8048";
                    event.evidence = "loopback event socket: eight-byte classic frame off the bus";
                    boolean interrupt = (registerValue(rscfdTransmitInterruptEnable(buffer))
                        & (1L << (buffer & 31))) != 0;
                    completeRscfdTransmit(thread, event);
                    row.addProperty("completed_instruction", trace.instructions);
                    if (interrupt) pendingCanTransmits.add(row);
                    else output.println(new Gson().toJson(row));
                });
            }

            @Override
            public void close() throws IOException {
                trace.deviceEvents.listener = null;
                socket.close();
                server.close();
            }
        }

        enum EventOrigin { SCENARIO, TRIAL, RESET }

        void configureExternalEvents(PcodeThread<byte[]> thread, List<ExternalEvent> inputs,
                long baseInstruction, EventOrigin origin) {
            for (ExternalEvent input : inputs) {
                long ordinal = nextEventOrdinal++;
                if (input.after_reset_instructions != null) {
                    if (origin == EventOrigin.RESET && baseInstruction != 0)
                        throw new IllegalArgumentException(
                            "reset-relative event is unsupported inside a reset replay fragment");
                    resetRelativeEvents.add(input);
                }
                else if ("memory-write".equals(input.kind) && input.after_instructions == 0
                        && (origin != EventOrigin.TRIAL || baseInstruction == 0)) {
                    // A tick-zero overlay is initial machine state. Apply it
                    // before the thread begins decoding so a checkpoint at zero
                    // captures it without invalidating an active decode.
                    applyExternalEvent(thread, input);
                }
                else if (input.after_transmit_words != null) {
                    Csih controller = csih(requiredRegister(
                        "csih-word", "controller", "CSIH" + input.unit + "CTL0"));
                    long base = origin == EventOrigin.SCENARIO ? 0 : controller.transmittedWords;
                    controller.relativeInputs.add(Math.addExact(base, input.after_transmit_words), ordinal, input);
                }
                else if (input.after_spc_triggers != null) {
                    Rsent.Unit receiver = rsent.unit(input.unit);
                    long base = origin == EventOrigin.SCENARIO ? 0 : receiver.spcSequence;
                    receiver.relativeInputs.add(Math.addExact(base, input.after_spc_triggers), ordinal, input);
                }
                else {
                    long tick = Math.addExact(baseInstruction, input.after_instructions);
                    externalEvents.add(new ScheduledEvent(
                        tick, ordinal, () -> applyExternalEvent(thread, input)));
                }
            }
        }


        void replayAfterReset(PcodeThread<byte[]> thread) {
            if (resetReplay != null) {
                for (MemoryInit init : resetReplay.memory) {
                    long address = parseUnsigned(init.address);
                    byte[] value;
                    if (init.hex != null) {
                        value = parseHex(init.hex);
                    }
                    else {
                        value = new byte[init.size];
                        Arrays.fill(value, (byte) (init.fill & 0xff));
                    }
                    initializeMemory(address, value, init.evidence);
                }
                if (resetReplay.hsb_cycles_per_instruction != null)
                    hsbCyclesPerInstruction = resetReplay.hsb_cycles_per_instruction;
                initializeDataFlashCells(resetReplay.dataflash_cells);
                if (resetReplay.icus_startup_stub != null)
                    icusStartupStub = new IcusStartupStub(resetReplay.icus_startup_stub);
                dma.masterRewriteAssumption = resetReplay.dma_master_rewrite_assumption;
                configureExternalEvents(
                    thread, resetReplay.events, trace.instructions, EventOrigin.RESET);
            }
            for (ExternalEvent input : resetRelativeEvents) {
                long ordinal = nextEventOrdinal++;
                long tick = Math.addExact(trace.instructions, input.after_reset_instructions);
                if ("memory-write".equals(input.kind) && input.after_reset_instructions == 0) {
                    applyExternalEvent(thread, input);
                }
                else {
                    externalEvents.add(new ScheduledEvent(
                        tick, ordinal, () -> applyExternalEvent(thread, input)));
                }
            }
        }

        void dispatchExternalEvents() {
            ScheduledEvent next = externalEvents.peek();
            if (next == null || next.tick > trace.instructions) return;
            invalidateBatchProof();
            // Wire-relative CSIH completions also enter here, not via applyExternalEvent.
            invalidateClockHorizon();
            do {
                externalEvents.remove().action.run();
                next = externalEvents.peek();
            } while (next != null && next.tick <= trace.instructions);
        }

        void applyExternalEvent(PcodeThread<byte[]> thread, ExternalEvent input) {
            invalidateBatchProof();
            invalidateClockHorizon();
            switch (input.kind) {
                case "clock": advanceClock(thread, input.p_bus_cycles, false); break;
                case "adc-sample": adc.input(input); break;
                case "rsent-frame":
                    rsent.receive(thread, input.unit, input.pulse_samples, input.evidence);
                    break;
                case "can-rx": receiveFrame(thread, input); break;
                case "can-tx-complete": completeRscfdTransmit(thread, input); break;
                case "csih-word":
                    csih(requiredRegister("csih-word", "controller", "CSIH" + input.unit + "CTL0"))
                        .complete(thread, input);
                    break;
                case "interrupt":
                    requestInterrupt(thread, input.channel, input.firmware_control);
                    break;
                case "memory-write": externalMemoryWrite(input); break;
                case "register-input": externalRegisterInput(input); break;
                case "ecm-pin-drive": externalEcmPinDrive(input); break;
                case "peripheral-reset": externalPeripheralReset(input); break;
                case "reset-assert": externalResetAssert(thread, input); break;
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

        void validateFaciWrite(PcodeThread<byte[]> thread, RegisterDef register, int size, long value) {
            boolean program = faciPendingCommand == 0xe8;
            boolean data = program && (faciProgramStage == 1 || faciProgramStage == 2);
            if (size != (data ? 2 : 1))
                throw fault("unsupported-faci-width", thread, register.address, size,
                    "write", register.evidence, "FACI commands/count require byte writes; each program word requires a halfword");
            int command = (int) (value >>> (bigEndian ? (size - 1) * 8 : 0)) & 0xff;
            if (!data) {
                boolean valid = program && faciProgramStage == 0 ? command == 2
                    : faciPendingCommand != 0 ? command == 0xd0
                    : command == 0x50 || command == 0xb3 || command == 0x71
                        || command == 0x20 || command == 0xe8;
                if (!valid)
                    throw fault(faciPendingCommand == 0 ? "unsupported-faci-command" : "unsupported-faci-sequence",
                        thread, register.address, size, "write", register.evidence,
                        "supported sequences: 50; B3; 71,D0; 20,D0; E8,02,two halfwords,D0");
            }
            boolean stop = !data && command == 0xb3;
            RegisterDef status = requiredRegister(register.name, "status", register.status_register);
            long statusValue = unsigned(memory(thread, status.address, status.size));
            boolean prematureClear = !data && command == 0x50 && faciOperation == 0xb3
                && (statusValue & FSTATR_FRDY) == 0
                && (registerValue(requiredRegister(register.name, "control", register.control_register)) & 0x81) == 0x80;
            if (!stop && !prematureClear && (statusValue & FSTATR_FRDY) == 0 && !program)
                throw fault("faci-not-ready", thread, register.address, size, "write",
                    register.evidence, "new FACI commands require FSTATR.FRDY=1");
            RegisterDef access = requiredRegister(register.name, "access-status", register.access_register);
            RegisterDef history = requiredRegister(register.name, "history", register.history_register);
            long accessValue = unsigned(memory(thread, access.address, access.size));
            memory(thread, history.address, history.size);
            RegisterDef control = requiredRegister(register.name, "control", register.control_register);
            long controlValue = unsigned(memory(thread, control.address, control.size)) & 0x81;
            if (!data && (command == 0x50 || stop)) {
                if (controlValue != 1 && controlValue != 0x80)
                    throw fault("unsupported-faci-mode", thread, register.address, size,
                        "write", register.evidence, "status clear/forced stop requires CodeFlash or DataFlash P/E mode");
                if (stop) {
                    RegisterDef emulation = requiredRegister(register.name, "emulation", register.emulation_register);
                    if (unsigned(memory(thread, emulation.address, emulation.size)) != 0)
                        throw fault("unsupported-faci-emulation", thread, register.address, size,
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
                throw fault("unsupported-faci-mode", thread, register.address, size, "write",
                    register.evidence, "submission requires both FHVE enables, unlocked DataFlash P/E and normal mode");
            if (program || command == 0xe8) {
                RegisterDef ecc = requiredRegister(register.name, "ECC mode", "FECCTMD");
                RegisterDef clock = requiredRegister(register.name, "clock", "FPCKAR");
                if ((unsigned(memory(thread, ecc.address, ecc.size)) & 0xff) != 0x30
                        || unsigned(memory(thread, clock.address, clock.size)) != 40)
                    throw fault("unsupported-faci-mode", thread, register.address, size, "write",
                        register.evidence, "programming requires normal ECC encoding/verification and FPCKAR=40MHz");
                if (!data && (command == 0xe8 || command == 0xd0)) faciTarget(register, thread, 0xe8);
                faciCycles(1700);
                return;
            }
            if (command == 0x20 || faciPendingCommand == 0x20) {
                faciTarget(register, thread, 0x20); // FEADDR is not used for block erase (Table4.6).
                RegisterDef clock = requiredRegister(register.name, "clock", "FPCKAR");
                if (unsigned(memory(thread, clock.address, clock.size)) != 40)
                    throw fault("unsupported-faci-mode", thread, register.address, size, "write",
                        register.evidence, "erase timing requires FPCKAR=40MHz");
                faciCycles(10000);
                return;
            }
            if (command == 0x71) return;
            RegisterDef start = requiredRegister(register.name, "start-address", register.start_address_register);
            RegisterDef end = requiredRegister(register.name, "end-address", register.end_address_register);
            long first = unsigned(memory(thread, start.address, start.size));
            long last = unsigned(memory(thread, end.address, end.size));
            if (dataFlash == null) throw new IllegalStateException("FACI blank check lacks DataFlash region");
            int decrement = (int)(registerValue(mode) & 1);
            long[] result = new long[4];
            P1MEFaci.blankCheck(dataFlashCells, first, last, dataFlash.size, decrement, result);
            if (result[0] == 1)
                throw fault("unsupported-faci-range", thread, register.address, size, "write",
                    register.evidence, "blank-check range must be ordered and contained in the registered DataFlash region");
            faciBlankFirst = result[1];
            if (result[0] == 2)
                throw fault("missing-dataflash-cell-state", thread, dataFlash.start + result[3], 4,
                    "device", "scenario", "blank checking requires known erased/programmed cells; interrupted cells require erase");
            faciBlankCycles = faciCycles(result[2]);
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

        void handleFaciWrite(PcodeThread<byte[]> thread, RegisterDef register, int size, long value) {
            int command = (int) (value >>> (bigEndian ? (size - 1) * 8 : 0)) & 0xff;
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
                    P1MEJitMachine.writeNumber(faciProgramData, (faciProgramStage - 1) * 2, 2, bigEndian, value);
                    faciProgramStage++;
                    sequence.add(value);
                    faciTransition(thread, register, command, "program-data-buffered", sequence);
                    return;
                }
            }
            RegisterDef statusRegister = requiredRegister(register.name, "status", register.status_register);
            RegisterDef accessRegister = requiredRegister(register.name, "access-status", register.access_register);
            RegisterDef historyRegister = requiredRegister(register.name, "history", register.history_register);
            long status = unsigned(memory(statusRegister.address, statusRegister.size));
            long history = unsigned(memory(historyRegister.address, historyRegister.size));
            if (command == 0x50 && faciOperation == 0xb3 && (status & FSTATR_FRDY) == 0) {
                // Tables6.4/8.1: premature status clear locks, but neither
                // completes nor restarts forced stop. Keep its original deadline.
                setRegisterValue(statusRegister.nameBinding, status | 0x4000);
                setRegisterValue(accessRegister.nameBinding, registerValue(accessRegister) | FASTAT_CMDLK);
                setRegisterValue(historyRegister.nameBinding, (command << 8) | ((history >>> 8) & 0xff));
                sequence.add(command);
                faciTransition(thread, register, command, "status-clear-rejected-busy", sequence);
                return;
            }
            if (command == 0x71 || command == 0x20 || command == 0xe8) {
                faciPendingCommand = command;
                if (command == 0xe8) {
                    faciProgramStage = 0;
                    faciTargetOffset = faciTarget(register, thread, command);
                    faciTargetSize = 4;
                    Arrays.fill(faciProgramData, (byte)0);
                    // Table4.7: Program clears FRDY at the FIRST access, unlike erase/blank check.
                    setRegisterValue(statusRegister.nameBinding, status & ~FSTATR_FRDY);
                    setRegisterValue(historyRegister.nameBinding, (command << 8) | ((history >>> 8) & 0xff));
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
                    setRegisterValue(historyRegister.nameBinding, 0xd000 | faciPendingCommand);
                }
                if (faciOperation == 0x20) {
                    faciTargetOffset = faciTarget(register, thread, 0x20);
                    faciTargetSize = 64;
                }
                setRegisterValue(statusRegister.nameBinding, status & ~FSTATR_FRDY);
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
                setRegisterValue(historyRegister.nameBinding, (command << 8) | ((history >>> 8) & 0xff));
                setRegisterValue(statusRegister.nameBinding, nextStatus);
                setRegisterValue(accessRegister.nameBinding, nextAccessStatus);
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
            long[] result = new long[5];
            P1MEFaci.complete(previousStatus, access, faciOperation, faciBlankFirst, result);
            long status = result[0];
            access = result[1];
            if (result[2] >= 0) {
                setRegisterValue("FBCSTAT", result[2]);
                if (result[3] >= 0) setRegisterValue("FPSADDR", result[3]);
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
            if (result[4] != 0) requestInterrupt(executionThread, 379);
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

        void handleIcusWrite(PcodeThread<byte[]> thread, RegisterDef register, long word) {
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
            // Command7 and abort admission preserve every explicit hardware
            // input. BUSY, STS2, errors and output are supplied by the scenario;
            // a command write cannot create a completion or clear a reply.
            if ((word & 0xffff) == 7 || word == 0x3f) return;
            RegisterDef status = requiredRegister(register.name, "status", register.status_register);
            RegisterDef secondary = requiredRegister(
                register.name, "secondary-status", register.secondary_status_register);
            setRegisterValue(status.nameBinding, 0);
            setRegisterValue(secondary.nameBinding, 0);
        }

        void handleDcraInput(RegisterDef register, long value) {
            RegisterDef output = requiredRegister(register.name, "status", register.status_register);
            RegisterDef control = requiredRegister(register.name, "mode", register.mode_register);
            if (registerValue(control) == 0x22) {
                // Tables33.8-33.9: raw CRC8 XOR FF on read, MSB-first 0x1D.
                long previous = registerValue(output);
                int crc = (int) ((previous ^ 0xFF) ^ value) & 0xFF;
                for (int bit = 0; bit < 8; bit++)
                    crc = ((crc << 1) ^ ((crc & 0x80) != 0 ? 0x1D : 0)) & 0xFF;
                // Only low8 are defined in this mode; high lanes keep explicit seed data.
                setRegisterValue(output.nameBinding, (previous & 0xFFFFFF00L) | (crc ^ 0xFF));
                return;
            }
            // R01UH0585EJ0120 pp2845–2846,2850–2851: LSB first, reflected
            // 04C11DB7 polynomial; COUT reads expose internal state XOR FFFFFFFF.
            int crc = ~(int) registerValue(output) ^ (int) value;
            for (int bit = 0; bit < 32; bit++) {
                crc = (crc >>> 1) ^ ((crc & 1) != 0 ? 0xedb88320 : 0);
            }
            setRegisterValue(output.nameBinding, Integer.toUnsignedLong(~crc));
        }

        int ecmDomain(RegisterDef register) {
            if (register.address < 0xffd61000L) return 0;
            if (register.address < 0xffd62000L) return 1;
            return 2;
        }

        PortBindings bindPortAliases() {
            int count = registers.size();
            PortPinAlias[] pinAliases = new PortPinAlias[count];
            PortPinAlias[][] dependents = new PortPinAlias[count][];
            RegisterDef[] maskedTargets = new RegisterDef[count];
            Map<String, PortPinField[]> groups = new HashMap<>();
            Map<RegisterDef, List<PortPinAlias>> dependentsBySource = new HashMap<>();
            // Retain the catalog's original alias write order, not the address lookup order.
            for (List<RegisterDef> definitions : List.of(spec.manual.registers,
                    spec.target_derived.registers)) {
                for (RegisterDef alias : definitions) {
                    if (alias.writeTrigger == WriteTrigger.PORT_MASKED_ALIAS) {
                        if (alias.control_register != null)
                            maskedTargets[alias.bindingIndex] = registersByName.get(alias.control_register);
                    }
                    if (!"port-pin-alias".equals(alias.trigger)) continue;
                    int separator = alias.name.indexOf('_');
                    String prefix = alias.name.startsWith("J") ? "J" : "";
                    String group = alias.name.substring(separator - 1, separator);
                    long pin = 1L << Integer.parseInt(alias.name.substring(separator + 1));
                    PortPinField[] columns = groups.computeIfAbsent(prefix + group,
                        ignored -> bindPortColumns(prefix, group));
                    List<PortPinField> fields = new ArrayList<>();
                    int overwrittenColumns = 0;
                    for (PortPinField field : columns) {
                        if ((field.pins & pin) != 0) fields.add(field);
                        RegisterDef source = field.source;
                        if (alias.address < source.address + source.size
                                && source.address < alias.address + alias.size)
                            overwrittenColumns |= field.aliasMask;
                    }
                    PortPinAlias plan = new PortPinAlias(alias, pin,
                        fields.toArray(PortPinField[]::new), overwrittenColumns);
                    pinAliases[alias.bindingIndex] = plan;
                    for (PortPinField field : plan.fields)
                        dependentsBySource.computeIfAbsent(field.source, ignored -> new ArrayList<>()).add(plan);
                }
            }
            dependentsBySource.forEach((source, pins) ->
                dependents[source.bindingIndex] = pins.toArray(PortPinAlias[]::new));
            return new PortBindings(pinAliases, dependents, maskedTargets);
        }

        private PortPinField[] bindPortColumns(String prefix, String group) {
            List<PortPinField> columns = new ArrayList<>();
            for (int index = 0; index < PORT_PIN_BITS.length; index++) {
                RegisterDef source = registersByName.get(prefix + PORT_PIN_REGISTERS[index] + group);
                if (source == null) continue; // Table2.42 omits several JP group functions.
                long pins = "port-input".equals(source.behavior) ? source.active_mask : source.writable_mask;
                columns.add(new PortPinField(source, index, 1 << PORT_PIN_BITS[index], pins));
            }
            return columns.toArray(PortPinField[]::new);
        }

        private RegisterDef maskedPortTarget(RegisterDef alias) {
            RegisterDef target = portBindings.maskedTargets[alias.bindingIndex];
            // Missing control metadata is checked on use, not during model binding.
            if (target == null)
                throw new IllegalStateException(alias.name + " lacks control register metadata");
            return target;
        }

        private int refreshPortAlias(PortPinAlias alias, int sampled) {
            long value = alias.register.reset;
            for (PortPinField field : alias.fields) {
                int mask = field.aliasMask;
                if ((sampled & mask) == 0) {
                    portColumnValues[field.column] = registerValue(field.source);
                    sampled |= mask;
                }
                value = (value & ~mask) | ((portColumnValues[field.column] & alias.pinMask) != 0
                    ? mask : 0);
            }
            setRegisterValue(alias.register, value);
            return sampled & ~alias.overwrittenColumns;
        }

        void refreshPortDependents(RegisterDef source) {
            PortPinAlias[] dependents = portBindings.dependents[source.bindingIndex];
            if (dependents == null) return;
            // Sample each column at its first use, and publish one alias at a time.
            // Undefined inputs can fault after earlier aliases have already been written.
            int sampled = 0;
            for (PortPinAlias alias : dependents) sampled = refreshPortAlias(alias, sampled);
        }

        void handlePortWrite(RegisterDef register, long value) {
            PortPinAlias alias = portBindings.pinAliases[register.bindingIndex];
            if (alias != null) {
                for (PortPinField field : alias.fields) {
                    if ((register.writable_mask & field.aliasMask) == 0) continue;
                    long bit = (value & field.aliasMask) != 0 ? alias.pinMask : 0;
                    setRegisterValue(field.source,
                        (registerValue(field.source) & ~alias.pinMask) | bit);
                }
                refreshPortAlias(alias, 0);
            }
            else if (register.writeTrigger == WriteTrigger.PORT_MASKED_ALIAS) {
                RegisterDef target = maskedPortTarget(register);
                long enabled = (value >>> 16) & target.writable_mask;
                long next = (registerValue(target) & ~enabled) | (value & enabled);
                setRegisterValue(target, next);
                setRegisterValue(register, next);
                refreshPortDependents(target);
            }
            else {
                setRegisterValue(register,
                    (register.reset & ~register.writable_mask) | (value & register.writable_mask));
                refreshPortDependents(register);
            }
        }

        boolean ecmHasUnmaskedErrors(int domain) {
            for (int index = 0; index < 3; index++) {
                RegisterDef status = ecmStatus[domain][index];
                long errors = ecmLatchedStatus(status);
                long mask = registerValue(ecmErrorMask[index]);
                if ((errors & ~mask & (index == 2 ? 0x7fffffffL : 0xffffffffL)) != 0)
                    return true;
            }
            return false;
        }

        boolean checkerOutputLoopback() {
            // P3_11, fifth alternative output: PFCAE/PFCE/PFC = 1/0/0.
            // R01UH0585EJ0120 Tables2.18,2.46 and section2.3.4.3.
            return (registerValue(checkerPmc) & 0x800) != 0
                && (registerValue(checkerPm) & 0x800) == 0
                && (registerValue(checkerPipc) & 0x800) == 0
                && (registerValue(checkerPfcae) & 0x800) != 0
                && (registerValue(checkerPfce) & 0x800) == 0
                && (registerValue(checkerPfc) & 0x800) == 0
                && (registerValue(checkerPbdc) & 0x800) != 0
                && (registerValue(checkerPibc) & 0x800) == 0;
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
                RegisterDef status = ecmStatus[domain][2];
                long latched = ecmLatchedStatus(status);
                if (fieldBistExecuted && missingResetInput(status))
                    latched |= 1L << 27;
                // PINV applies to alternate outputs before their pin-level
                // loopback (Table2.24). Camry inverts P3_11 during boot.
                boolean outputHigh = !ecmOutputLow[domain];
                if (domain == 1 && (registerValue(checkerPinv) & 0x800) != 0)
                    outputHigh = !outputHigh;
                boolean high = !"low".equals(drive) && outputHigh;
                setRegisterValue(status,
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
                setRegisterValue(register.nameBinding, registerBeforeWrite);
                return;
            }
            long selection = value & register.writable_mask;
            setRegisterValue(register.nameBinding, selection);
            if (selection == 0) return; // Removing injection does not clear latched error status.
            RegisterDef masterStatus = ecmStatus[0][0], checkerStatus = ecmStatus[1][0];
            long master = registerValue(masterStatus);
            long checker = registerValue(checkerStatus);
            setRegisterValue(masterStatus, master | 4);
            setRegisterValue(checkerStatus, checker | 4);
            refreshEcmFeedback();
            // Table32.5 emits a pulse when enabled error-source status is set.
            if ((master & checker & 4) == 0
                    && (registerValue(ecmNotification[0][0]) & 4) != 0)
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
                boolean knownIndex = index >= 0 && index < ecmStatus[0].length;
                RegisterDef master = knownIndex ? ecmStatus[0][index]
                    : registersByName.get("ECMMESSTR" + index);
                RegisterDef checker = knownIndex ? ecmStatus[1][index]
                    : registersByName.get("ECMCESSTR" + index);
                long masterValue = registerValue(master);
                long checkerValue = registerValue(checker);
                setRegisterValue(master.nameBinding, masterValue & ~clear);
                setRegisterValue(checker.nameBinding, checkerValue & ~clear);
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
                RegisterDef status = ecmStatus[ecmDomain(register) == 0 ? 0 : 1][2];
                long status2 = registerValue(status);
                boolean set = "ecm-output-set".equals(register.trigger);
                if (set) {
                    setRegisterValue(status, status2 | 0x40000000L);
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
            if (register.access.contains("r")) setRegisterValue(register.nameBinding, value);
            if (register.name.startsWith("ECMEMK")) refreshEcmFeedback();
        }

        void handleEcmWrite(PcodeThread<byte[]> thread, RegisterDef register, long value) {
            int domain = ecmDomain(register);
            boolean command = "ecm-command".equals(register.trigger);
            boolean unprotected = register.name.equals("ECMPEM")
                || register.name.equals("ECMEPCTL");
            // The p-code store already occurred. Neither an intermediate
            // protocol word nor a failed write may change the effective register.
            if (!command) setRegisterValue(register.nameBinding, registerBeforeWrite);
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
                setRegisterValue(register.nameBinding, value & register.writable_mask);
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
                    setRegisterValue(enable.nameBinding,
                        (registerValue(enable) & ~register.writable_mask)
                            | (value & register.writable_mask));
                    cvmEnableWritten = true;
                }
                setRegisterValue(register.nameBinding, 0);
            }
            else if ("cvm-factor-clear".equals(register.trigger)) {
                RegisterDef factors = requiredRegister(register.name, "status", register.status_register);
                setRegisterValue(factors.nameBinding, registerValue(factors) & ~(value & register.writable_mask));
                setRegisterValue(register.nameBinding, 0);
            }
            else {
                setRegisterValue(register.nameBinding,
                    (registerBeforeWrite & ~register.writable_mask) | (value & register.writable_mask));
            }
        }

        void resetPeripheralEccControl(RegisterDef register) {
            // Table31.79 defines every reset bit except the live RAM-output
            // ECEMF input. Store known bits for internal RMW, not a CPU-readable
            // assertion that ECEMF is zero or retained across reset.
            setMemory(register.address, bytes(register.reset & register.reset_mask,
                register.size, language.isBigEndian()));
            updateRegisterState(register, DEVICE_REGISTER_INITIALIZED, MISSING_RESET_INPUT);
        }

        void handlePeripheralEccWrite(RegisterDef register, long value) {
            if ("peripheral-ecc-test".equals(register.trigger)) {
                // Validation excludes effective ECTMCE=1. Table31.80 clears
                // all test-control bits in normal mode; ETMA always reads zero.
                setRegisterValue(register.nameBinding, 0);
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
            if (deviceRegisterInitialized(register)) {
                setRegisterValue(register.nameBinding, next);
            }
            else {
                // Clearing latched flags cannot resolve the live ECEMF input.
                setMemory(register.address, bytes(next, register.size, language.isBigEndian()));
            }
        }

        void handleBankedEccClear(RegisterDef command, long selected) {
            setRegisterValue(command.nameBinding, 0);
            if (selected == 0) return;
            RegisterDef status = requiredRegister(command.name, "status", command.status_register);
            RegisterDef overflow = command.secondary_status_register == null ? null
                : requiredRegister(command.name, "secondary-status", command.secondary_status_register);
            long statusValue = registerValue(status);
            // A clear determines only selected functional bits, never undefined
            // reset bits (ITOVFSTR bit 4, Table31.71). Keep the whole-word input
            // prerequisite until a scenario supplies those bits.
            boolean unknownOverflow = overflow != null && overflow.reset_mask != null
                && !deviceRegisterInitialized(overflow);
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
                    setRegisterValue(capture.nameBinding, 0);
                }
            }
            setRegisterValue(status.nameBinding, statusValue);
            if (unknownOverflow) {
                setMemory(overflow.address, bytes(overflowValue, overflow.size, language.isBigEndian()));
                updateRegisterState(overflow, 0, MISSING_RESET_INPUT);
            }
            else if (overflow != null) {
                setRegisterValue(overflow.nameBinding, overflowValue);
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
        Map<RegionDef, byte[]> resetMemoryBefore() {
            Map<RegionDef, byte[]> before = new LinkedHashMap<>();
            for (RegionDef region : regions) {
                if (!region.name.toLowerCase().contains("ram")) continue;
                try {
                    before.put(region, emulator.getSharedState().getVar(
                        memorySpace, region.start, region.size, true, Reason.INSPECT));
                }
                catch (RuntimeException unavailable) {
                    before.put(region, null);
                }
            }
            return before;
        }

        JsonArray resetMemoryChanges(Map<RegionDef, byte[]> before) {
            JsonArray rows = new JsonArray();
            for (Map.Entry<RegionDef, byte[]> entry : before.entrySet()) {
                RegionDef region = entry.getKey();
                byte[] prior = entry.getValue();
                byte[] after;
                try {
                    after = emulator.getSharedState().getVar(
                        memorySpace, region.start, region.size, true, Reason.INSPECT);
                }
                catch (RuntimeException unavailable) {
                    after = null;
                }
                if (prior == null || after == null) {
                    if (prior == after) continue;
                    JsonObject row = new JsonObject();
                    row.addProperty("region", region.name);
                    row.addProperty("address", hex32(region.start));
                    row.addProperty("size", region.size);
                    row.addProperty("initialized_before", prior != null);
                    row.addProperty("initialized_after", after != null);
                    rows.add(row);
                    continue;
                }
                int first = 0;
                while (first < prior.length) {
                    while (first < prior.length && prior[first] == after[first]) first++;
                    if (first == prior.length) break;
                    int last = first + 1;
                    while (last < prior.length && prior[last] != after[last]) last++;
                    JsonObject row = new JsonObject();
                    row.addProperty("region", region.name);
                    row.addProperty("address", hex32(region.start + first));
                    row.addProperty("size", last - first);
                    rows.add(row);
                    first = last;
                }
            }
            return rows;
        }

        void clearResetQueues() {
            scheduledEvents.clear();
            nextScheduledTick = Long.MAX_VALUE;
            pendingRscfdTransmits.clear();
            for (ReceiveFifo fifo : receiveFifos.values()) fifo.messages.clear();
            pendingInterrupts.clear();
            Arrays.fill(pendingPriorities, (byte) -1);
            for (BitSet channels : channelsByPriority) channels.clear();
            activeInterruptChannels.clear();
            for (Csih controller : csihControllers.values()) controller.relativeInputs.clear();
            for (Rsent.Unit receiver : rsent.units) receiver.relativeInputs.clear();
            pendingPriorityMask = 0;
        }

        void externalResetAssert(PcodeThread<byte[]> thread, ExternalEvent input) {
            Map<RegionDef, byte[]> before = resetMemoryBefore();
            clearResetQueues();
            applyReset(input.reset_class);
            initializeProcessorReset(thread);
            thread.overrideCounter(memorySpace.getAddress(0));
            thread.overrideContextWithDefault();
            thread.setSuspended(false);
            replayAfterReset(thread);
            JsonObject event = new JsonObject();
            event.addProperty("kind", "reset-assert");
            event.addProperty("reset_class", input.reset_class);
            event.addProperty("reset_cause_register", "RESF");
            event.addProperty("reset_cause_value", hex32(resetFactorValue()));
            event.addProperty("instruction", trace.instructions);
            event.add("changed_memory_ranges", resetMemoryChanges(before));
            event.addProperty("internal_scheduled_events", "discarded");
            event.addProperty("can_controller_queues", "discarded");
            event.addProperty("future_external_events", "retained");
            if (resetReplay != null) {
                event.addProperty("replayed_scenario", resetReplay.scenario);
                event.addProperty("replayed_memory_rows", resetReplay.memory.size());
                event.addProperty("replayed_event_rows", resetReplay.events.size());
            }
            event.addProperty("evidence", input.evidence);
            trace.deviceEvents.add(event);
        }

        void handleRegisterWrite(PcodeThread<byte[]> thread, RegisterDef register,
                long address, int size, long value) {
            WriteDevice device = register.writeDevice;
            WriteTrigger trigger = register.writeTrigger;
            switch (device) {
                case TAUJ -> { tauj.write(thread, register, value); return; }
                case TAUD, PIC_TAUD -> {
                    tsg.deferPicRouting();
                    taud.write(thread, register, value);
                    finishPicRouting(thread);
                    return;
                }
                case TSG, PIC_TSG -> { tsg.write(thread, register, value); return; }
                case PIC1_START -> {
                    tsg.deferPicRouting();
                    pic1.write(thread, register, value);
                    finishPicRouting(thread);
                    return;
                }
                case PDMA -> { dma.write(thread, register, value); return; }
                case ADC -> { adc.handleWrite(thread, register, value); return; }
                case RSENT -> { rsent.handleWrite(thread, register, value); return; }
                default -> { }
            }
            // These triggers take precedence over the remaining device handlers.
            switch (trigger) {
                case GUARD_ERROR_CLEAR -> {
                    RegisterDef status = requiredRegister(register.name, "error status", register.status_register);
                    long clear = value << (8 * (address - register.address));
                    setRegisterValue(status, registerValue(status) & ~clear);
                    setRegisterValue(register.nameBinding, 0);
                    return;
                }
                case PDMA_COMPARATOR -> { handlePdmaComparatorWrite(thread, register, value); return; }
                case RESET_FACTOR_CLEAR -> { clearResetFactors(value); return; }
                default -> { }
            }
            switch (device) {
                case CSIH -> {
                    if (trigger != WriteTrigger.DMA_SELECT) csih(register).write(thread, register, value);
                    return;
                }
                case SEG -> {
                    if ("SEGFLAG".equals(register.name)) {
                        if (deviceRegisterInitialized(segFlagRegister)) {
                            setRegisterValue(segFlagRegister,
                                (registerBeforeWrite & ~0x354L) | (value & 0x354L));
                        }
                        setSegFlags(value);
                        if ((registerBeforeWrite & ~value & 0x354L) != 0)
                            segNotificationPending = enabledSegFlags() != 0;
                    }
                    else if ("SEGCONT".equals(register.name)) {
                        segNotificationPending = enabledSegFlags() != 0;
                    }
                    return;
                }
                case PEG, BUS_GUARD, GRAM_GUARD -> {
                    if (guardWriteIgnored) {
                        setRegisterValue(register.nameBinding, registerBeforeWrite);
                    }
                    else {
                        setRegisterValue(register.nameBinding,
                            (registerBeforeWrite & ~register.writable_mask)
                                | (registerValue(register) & register.writable_mask));
                        if (trigger == WriteTrigger.PEG_MASK) {
                            RegisterDef base = guardLock(register);
                            setRegisterValue(base.nameBinding, registerValue(base) & ~1L);
                        }
                    }
                    return;
                }
                case PERIPHERAL_ECC -> { handlePeripheralEccWrite(register, value); return; }
                case CVM -> { handleCvmWrite(register, value); return; }
                case ECM -> { handleEcmWrite(thread, register, value); return; }
                case PORT_CONFIG -> {
                    handlePortWrite(register, value);
                    refreshEcmFeedback();
                    return;
                }
                case NOISE_FILTER -> {
                    if (trigger == WriteTrigger.NOISE_CLOCK_SELECTOR && value != registerBeforeWrite) {
                        RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                        // Do not turn a requested source into an asserted CLKACT.
                        // Its actual activity must be supplied as a new external input.
                        setRegisterValue(status, value);
                        updateRegisterState(status, 0, MISSING_RESET_INPUT);
                    }
                    return;
                }
                case INTC_EIC -> {
                    if (register.reset != null) {
                        boolean level = (register.reset & 0x8000) != 0;
                        long writable = level ? 0xcfL : 0x10cfL;
                        // Table6.4: EICT and reserved bits read their reset value.
                        // Level EIRF follows its source, not the software write.
                        setRegisterValue(register.nameBinding, (register.reset & 0x8000L)
                            | (level ? registerBeforeWrite & 0x1000L : 0)
                            | (registerValue(register) & writable));
                    } else {
                        // Firmware-only EICs can be reprogrammed before or after an explicit
                        // request. A CPU store to these words is not itself a request source.
                        refreshPendingInterrupts(address, size, false);
                    }
                }
                default -> { }
            }
            if (register.fifoBusWrite) handleReceiveWrite(thread, register, size, value);
            switch (trigger) {
                case NONE: break;
                case CLOCK_DIVIDER: {
                    RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                    // Functional completion at the write boundary, not oscillator startup,
                    // waveform frequency qualification, or cycle-accurate synchronization.
                    setRegisterValue(status, register.completion_value
                        | (value == 0 ? 0 : register.active_mask));
                    break;
                }
                case CLOCK_SELECTOR: {
                    if (registerBeforeWrite != value) {
                        RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                        setRegisterValue(status, value);
                    }
                    break;
                }
                case FLMD_COMMAND:
                    flmdStage = 1;
                    break;
                case FLMD_CONTROL:
                    if (flmdStage == 3) {
                        flmdStage = 0;
                        RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                        setRegisterValue(status, 0);
                    }
                    else {
                        if (flmdStage == 1) flmdDesired = value;
                        flmdStage++;
                        setRegisterValue(register.nameBinding, registerBeforeWrite);
                    }
                    break;
                case BIST_CONTROL:
                    break; // Validated HWBISTEXE storage affects the next applicable reset only.
                case DCRA_CONTROL:
                    if (registerBeforeWrite != value) dcraSeeded.remove(register.name);
                    break;
                case DCRA_SEED:
                    // Writes initialize raw state; reads apply the hardware's final XOR.
                    RegisterDef crcControl = requiredRegister(register.name, "mode", register.mode_register);
                    setRegisterValue(register.nameBinding, value
                        ^ (registerValue(crcControl) == 0x22 ? 0xFF : 0xFFFFFFFFL));
                    dcraSeeded.add(crcControl.name);
                    break;
                case DCRA_INPUT: handleDcraInput(register, value); break;
                case RSCFD_TRANSMIT:
                    handleRscfdWrite(thread, register, value, registerBeforeWrite);
                    break;
                case RSCFD_TRANSMIT_STATUS: handleRscfdTransmitStatusWrite(register); break;
                case RSCFD_GLOBAL_CONTROL:
                case RSCFD_CHANNEL_CONTROL:
                    handleRscfdModeWrite(register, registerValue(register));
                    break;
                case RSCFD_FD_COUNTER_CLEAR: {
                    // Section17.2.2: classical mode maps this address to a rule word.
                    if ((registerValue(registersByName.get("GRMCFG")) & 1) == 0) break;
                    // Table17.103: requests clear only their counter and always read zero.
                    long request = registerValue(register);
                    RegisterDef status = requiredRegister(register.name, "status", register.status_register);
                    long clear = ((request & 2) != 0 ? 0xff000000L : 0)
                        | ((request & 1) != 0 ? 0x00ff0000L : 0);
                    setRegisterValue(status, registerValue(status) & ~clear);
                    setRegisterValue(register.nameBinding, 0);
                    break;
                }
                case RSCFD_FD_STATUS:
                    if ((registerValue(registersByName.get("GRMCFG")) & 1) == 0) break;
                    // Table17.104: only flags9:7 are W0C; counters/result are read-only.
                    setRegisterValue(register.nameBinding, registerBeforeWrite
                        & ~(register.writable_mask & ~registerValue(register)));
                    break;
                case FACI_COMMAND: handleFaciWrite(thread, register, size, value); break;
                case FACI_ACCESS_STATUS: {
                    long next = registerBeforeWrite
                        & ~(faciReadErrors & ~value & FASTAT_ACCESS_ERROR_MASK);
                    setRegisterValue(register.nameBinding, next);
                    faciReadErrors &= next;
                    break;
                }
                case FACI_SETUP_INITIALIZE:
                case FACI_AREA_SELECTOR:
                case FACI_CLOCK_NOTIFY: {
                    boolean setup = trigger == WriteTrigger.FACI_SETUP_INITIALIZE;
                    long incoming = value;
                    long next = registerBeforeWrite;
                    if ((registerValue(registersByName.get("FSTATR")) & FSTATR_FRDY) != 0
                            && (incoming & register.protection_mask) == register.protection_value) {
                        next = incoming & register.writable_mask;
                        if (setup && next != 0) {
                            for (String name : FACI_SETUP_REGISTERS)
                                setRegisterValue(name, 0);
                        }
                    }
                    setRegisterValue(register.nameBinding, next);
                    break;
                }
                case FACI_ADDRESS:
                    RegisterDef addressStatus = requiredRegister(register.name, "status", register.status_register);
                    setRegisterValue(register.nameBinding, (registerValue(addressStatus) & FSTATR_FRDY) != 0
                        ? value & ~3L : registerBeforeWrite);
                    break;
                case FACI_DATAFLASH_MODE: {
                    RegisterDef modeStatus = requiredRegister(register.name, "status", register.status_register);
                    long incoming = value;
                    long next = registerBeforeWrite;
                    if ((registerValue(modeStatus) & FSTATR_FRDY) != 0) {
                        next = (incoming >>> 8) == 0xaa && registerBeforeWrite == 0
                            ? incoming & 0x80 : 0;
                    }
                    setRegisterValue(register.nameBinding, next);
                    break;
                }
                case FACI_NORMAL_EMULATION:
                    break; // Validated zero-to-zero write; no OCD-mode behavior is inferred.
                case FACI_ENABLE:
                    setRegisterValue(register.nameBinding, value & 1);
                    break;
                case BANKED_ECC_CLEAR:
                    handleBankedEccClear(register,
                        value << (8 * (address - register.address)));
                    break;
                case ECC_NOTIFICATION:
                    // The validated byte lanes already updated the ordinary enable latches.
                    break;
                case DATAFLASH_READ_CYCLE:
                    setRegisterValue(register.nameBinding, value & 0xf);
                    break;
                case ECC_PROTECTED_CONTROL: {
                    long incoming = value;
                    long writable = register.writable_mask;
                    long protectionMask = register.protection_mask == null
                        ? 0xc000L : register.protection_mask;
                    long protectionValue = register.protection_value == null
                        ? 0x4000L : register.protection_value;
                    // Narrow writes must include the key and the data in the same access.
                    long next = address == register.address
                            && (incoming & protectionMask) == protectionValue
                        ? incoming & writable : registerBeforeWrite;
                    setRegisterValue(register.nameBinding, next & writable);
                    break;
                }
                case ICUS_COMMAND: handleIcusWrite(thread, register, value); break;
                case ICUS_CONTROL:
                    if (icusStartupStub != null) icusStartupStub.acknowledge();
                    break;
                default: throw new IllegalStateException(
                    "unknown machine-model trigger: " + register.trigger);
            }
        }

        boolean storeBus(PcodeThread<byte[]> thread, long address, int size, long number, byte[] raw, boolean cpu) {
            RegionDef region = region(address, size);
            if (raw != null && (size <= Long.BYTES || region == null || !region.directPageWrites))
                number = Utils.bytesToLong(raw, size, bigEndian);
            long word = number & Utils.calc_mask(Math.min(size, Integer.BYTES));
            RegisterDef register = beforeWrite(thread, address, size, word, cpu, region);
            if (discardBusStore) {
                discardBusStore = false;
                return false;
            }
            writeBusBacking(register, address, size, number, raw);
            if (!cpu) refreshPendingInterrupts(address, size, true);
            if (region != null && region.alias_group != null) {
                List<RegionDef> group = aliases.get(region.alias_group);
                if (group != null) {
                    for (RegionDef alias : group) {
                        if (alias == region) continue;
                        long other = alias.start + (address - region.start);
                        writeBusBacking(null, other, size, number, raw);
                        refreshPendingInterrupts(other, size, true);
                        trace.aliasWrite(address, other, size);
                    }
                }
            }
            if (peripheralFile) refreshPendingInterrupts(address, size, true);
            else if (region == null || !region.directPageWrites) {
                // Region overlays keep their original post-write SFR lookup.
                RegisterDef target = region == null ? register : register(address, size);
                if (target != null) {
                    registerWriteEvent(thread, target, word);
                    if (target.completesBusWrite) handleRegisterWrite(thread, target, address, size, word);
                }
            }
            return true;
        }

        private void writeBusBacking(RegisterDef register, long address, int size, long number, byte[] raw) {
            if (deviceState != null && size > 0 && size <= Long.BYTES) {
                if (register != null && register.address == address && register.size == size
                        && deviceState.writeDevice(register, number, bigEndian)) return;
                if (deviceState.writeMemoryNumberIfInitialized(address, size, number, bigEndian)) return;
            }
            emulator.getSharedState().setVar(memorySpace, address, size, true,
                raw != null ? raw : bytes(number, size, bigEndian));
        }


        void initializeResetRegisters() {
            invalidateClockHorizon();
            dcraSeeded.clear();
            segFlags = 0;
            segNotificationPending = false;
            flmdStage = 0;
            cvmEnableWritten = false;
            resetFaci();
            // Table10.3: no reset defines the CVMOUT pin level.
            RegisterDef cvmMonitor = registersByName.get("CVMMON");
            if (cvmMonitor != null) updateRegisterState(cvmMonitor, 0, MISSING_RESET_INPUT);
            for (RegisterDef register : registers) {
                if ("peripheral-ecc-control".equals(register.trigger)) {
                    resetPeripheralEccControl(register);
                    continue;
                }
                // Partial reset values do not determine a readable whole word.
                if (register.reset_mask != null) {
                    updateRegisterState(register, 0, MISSING_RESET_INPUT);
                    if ("reset-factors".equals(register.trigger)
                            || "ecm-bist-status".equals(register.trigger)) {
                        // Backing bits for controller-side RMW only. The
                        // separate knowledge mask still forbids unresolved CPU reads.
                        setMemory(register.address, bytes(register.reset & register.reset_mask,
                            register.size, language.isBigEndian()));
                    }
                    continue;
                }
                if (register.read_input && register.reset == null) {
                    // Internal command backing only. Reads still require a
                    // separate explicit bus response; this is no reset value.
                    setMemory(register.address, new byte[register.size]);
                    continue;
                }
                if (register.reset == null) continue;
                setRegisterValue(register.nameBinding, register.reset);
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

        // Model writes index EIRF. Raw writes to firmware-only EICs update arbitration
        // only for already indexed requests; an untouched lane may still be undefined.
        void refreshPendingInterrupts(long address, int size, boolean indexRequests) {
            if (interruptRegistersByAddress.length == 0 || size == 0) return;
            RegisterDef last = interruptRegistersByAddress[interruptRegistersByAddress.length - 1];
            long end = address + size;
            if (end <= interruptRegistersByAddress[0].address
                    || address >= last.address + last.size) return;
            int low = 0;
            int high = interruptRegistersByAddress.length;
            while (low < high) {
                int middle = (low + high) >>> 1;
                RegisterDef eic = interruptRegistersByAddress[middle];
                if (eic.address + eic.size <= address) low = middle + 1;
                else high = middle;
            }
            for (int index = low; index < interruptRegistersByAddress.length; index++) {
                RegisterDef eic = interruptRegistersByAddress[index];
                if (eic.address >= end) break;
                if (!indexRequests && !pendingInterrupts.get(index)) continue;
                updatePendingInterrupt(index, eic, registerValue(eic), indexRequests);
            }
        }

        private void updatePendingInterrupt(int index, RegisterDef eic, long control, boolean indexRequests) {
            int previous = pendingPriorities[index];
            int priority = (control & 0x1080) == 0x1000 ? (int) control & 15 : -1;
            if (previous != priority) {
                int channel = eic.interrupt_channel;
                if (previous >= 0) {
                    channelsByPriority[previous].clear(channel);
                    if (channelsByPriority[previous].isEmpty()) pendingPriorityMask &= ~(1 << previous);
                }
                if (priority >= 0) {
                    channelsByPriority[priority].set(channel);
                    pendingPriorityMask |= 1 << priority;
                }
                pendingPriorities[index] = (byte) priority;
            }
            if (indexRequests) pendingInterrupts.set(index, (control & 0x1000) != 0);
        }

        void setMemory(long address, byte[] value) {
            emulator.getSharedState().setVar(memorySpace, address, value.length, true, value);
            refreshPendingInterrupts(address, value.length, true);
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
            if ("faci".equals(register.behavior) && !register.read_input && (register.trigger != null
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
            if ("RESF".equals(register.name)) {
                if (input.replayedAfterReset) resolveReplayedResetFactors(value);
                else validateResetFactorInput(value);
            }
            if (register.read_input) {
                if (readInputResponses == null) readInputResponses = new HashMap<>();
                readInputResponses.put(register.name, value);
            }
            else {
                setRegisterValue(register.nameBinding, value);
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
                resolveRegisterInput(register);
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
        Integer interruptReturnChannel;

        Callbacks(SleighLanguage language, Model model) {
            this.language = language;
            this.model = model;
        }
        static final Set<String> FLAG_ARITHMETIC = Set.of(
            "add", "addi", "sub", "subr", "satadd", "satsub", "satsubr",
            "shl", "shr", "sar", "and", "or", "xor", "not", "mul", "mulu",
            "div", "divu", "mac", "macu"
        );
        static final class InstructionObservation {
            static final Register[] NO_REGISTERS = new Register[0];
            static final int DERIVE_NONE = 0, DERIVE_SHIFT = 1, DERIVE_ADD = 2;

            final Instruction instruction;
            final PcodeProgram decodedProgram;
            final long pc;
            final String mnemonic;
            final String compareMnemonic;
            final boolean conditional;
            final boolean computed;
            final boolean readsIcctrl;
            final boolean writesIcctrl;
            final boolean writesIspr;
            final boolean returnFromInterrupt, ordinaryRetirement;
            final int compareWidth;
            final OperandValue penultimateValue;
            final OperandValue lastValue;
            final Register[] addressRegisters;
            final AddressDerivation[] addressDerivations;
            final Register destination;
            final int derivation;
            private static final AddressDerivation[] NO_DERIVATIONS = new AddressDerivation[0];
            private AddressDerivation[] resultDerivations;

            InstructionObservation(Callbacks callbacks, Instruction instruction, PcodeProgram decodedProgram,
                    boolean comparisons, boolean indices, boolean peripheralFile) {
                this.instruction = instruction;
                this.decodedProgram = decodedProgram;
                pc = instruction.getAddress().getOffset();
                mnemonic = instruction.getMnemonicString();
                String lower = comparisons || indices ? mnemonic.toLowerCase() : mnemonic;
                int last = instruction.getNumOperands() - 1;
                boolean compare = comparisons && last >= 1 && (lower.equals("cmp")
                    || lower.equals("tst") || lower.equals("cmpf.s") || lower.equals("cmpf.d")
                    || FLAG_ARITHMETIC.contains(lower));
                var flow = comparisons || indices ? instruction.getFlowType() : null;
                conditional = comparisons && flow.isConditional();
                computed = indices && flow.isComputed();
                compareMnemonic = compare ? lower : null;
                derivation = !indices || last < 1 ? DERIVE_NONE
                    : lower.equals("shl") && last == 1 ? DERIVE_SHIFT
                    : lower.equals("add") ? DERIVE_ADD : DERIVE_NONE;

                Register[] addresses = indices && last >= 0 ? new Register[last + 1] : NO_REGISTERS;
                addressDerivations = addresses.length == 0 ? NO_DERIVATIONS
                    : new AddressDerivation[addresses.length];
                OperandValue left = null;
                OperandValue right = null;
                boolean stsr = peripheralFile && mnemonic.equals("stsr");
                boolean icctrlRead = false;
                if (indices || compare || stsr) {
                    for (int index = 0; index <= last; index++) {
                        Register address = indices || (stsr && !icctrlRead)
                            ? instruction.getRegister(index) : null;
                        if (stsr && address != null && "ICCTRL".equals(address.getName())) {
                            icctrlRead = true;
                        }
                        boolean needLeft = index == last - 1 && (compare || derivation != DERIVE_NONE);
                        boolean needRight = index == last && compare;
                        boolean needValue = needLeft || needRight;
                        OperandValue value = null;
                        // Index probes prefer the direct register. Operand values
                        // instead use the first displayed scalar or register.
                        if (needValue || (indices && address == null)) {
                            for (Object object : instruction.getOpObjects(index)) {
                                if (object instanceof Register register) {
                                    if (address == null) address = register;
                                    if (value == null && needValue) {
                                        value = new OperandValue(register, 0, register.getBitLength());
                                    }
                                }
                                else if (value == null && needValue && object instanceof Scalar scalar) {
                                    value = new OperandValue(null, scalar.getUnsignedValue(),
                                        scalar.bitLength());
                                }
                                if ((!indices || address != null) && (!needValue || value != null)) break;
                            }
                        }
                        if (indices) {
                            addresses[index] = address;
                            if (address != null) addressDerivations[index] = callbacks.derivationSlot(address);
                        }
                        if (needLeft) left = value;
                        if (needRight) right = value;
                    }
                }
                readsIcctrl = icctrlRead;
                Register system = mnemonic.equals("ldsr") ? instruction.getRegister(1) : null;
                writesIcctrl = !peripheralFile && system != null && "ICCTRL".equals(system.getName());
                writesIspr = system != null && "ISPR".equals(system.getName());
                returnFromInterrupt = mnemonic.equals("eiret");
                ordinaryRetirement = !writesIcctrl && !writesIspr && !returnFromInterrupt &&
                    switch (mnemonic) {
                        case "synce", "syncm", "syncp", "synci", "prepare", "jarl" -> false;
                        default -> true;
                    };
                penultimateValue = left;
                lastValue = right;
                compareWidth = !compare || left == null || right == null ? 0
                    : lower.equals("cmpf.d") ? 64 : lower.equals("cmpf.s") ? 32
                    : Math.max(left.width(), right.width());
                addressRegisters = addresses;
                destination = indices && last >= 0 ? addresses[last] : null;
            }

            AddressDerivation[] resultDerivations(Callbacks callbacks) {
                if (resultDerivations != null) return resultDerivations;
                List<Register> registers = new ArrayList<>();
                if (decodedProgram != null) {
                    // Match Sleigh's register results using the plan's unmodified
                    // p-code. STORE contributes an Address, never a Register.
                    for (var op : decodedProgram.getCode()) {
                        var output = op.getOutput();
                        if (op.getOpcode() == ghidra.program.model.pcode.PcodeOp.STORE
                                || output == null || !(output.isRegister() || output.isAddress())) {
                            continue;
                        }
                        Register register = callbacks.language.getRegister(output.getAddress(), output.getSize());
                        if (register != null && !registers.contains(register)) registers.add(register);
                    }
                }
                else {
                    for (Object object : instruction.getResultObjects()) {
                        if (object instanceof Register register) registers.add(register);
                    }
                }
                if (registers.isEmpty()) return resultDerivations = NO_DERIVATIONS;
                var resolved = new AddressDerivation[registers.size()];
                for (int i = 0; i < resolved.length; i++) {
                    resolved[i] = callbacks.derivationSlot(registers.get(i));
                }
                return resultDerivations = resolved;
            }
        }

        record OperandValue(Register register, long scalar, int width) {}
        record PendingCompare(InstructionObservation instruction, long left, long right) {}
        // Decoded observations for the same register share a slot.
        static final class AddressDerivation {
            long base;
            long index;
            int scale; // Zero denotes an inactive slot; every real scale is positive.

            boolean matches(long effective) {
                return scale != 0 && index != 0 && ((base + index * scale) & 0xffffffffL) == effective;
            }
        }

        record SavedDerivation(AddressDerivation slot, long base, long index, int scale) {}
        private final Map<String, AddressDerivation> addressDerivations = new HashMap<>();
        private int activeDerivations;
        final long[] inspected = new long[2];
        InstructionObservation currentObservation;
        InstructionObservation pendingComparison;
        long pendingLeft;
        long pendingRight;

        InstructionObservation decodeObservation(Instruction instruction, PcodeProgram decodedProgram) {
            return new InstructionObservation(this, instruction, decodedProgram,
                model.compareOperands, model.inputDerivedTableIndices, model.peripheralFile);
        }

        private AddressDerivation derivationSlot(Register register) {
            return addressDerivations.computeIfAbsent(register.getName(), name -> new AddressDerivation());
        }

        private void setDerivation(AddressDerivation slot, long base, long index, int scale) {
            if (slot.scale == 0) activeDerivations++;
            slot.base = base;
            slot.index = index;
            slot.scale = scale;
        }

        List<SavedDerivation> checkpointDerivations() {
            var saved = new ArrayList<SavedDerivation>(activeDerivations);
            for (AddressDerivation slot : addressDerivations.values()) {
                if (slot.scale != 0) saved.add(new SavedDerivation(slot, slot.base, slot.index, slot.scale));
            }
            return saved;
        }

        void restoreDerivations(List<SavedDerivation> saved) {
            for (AddressDerivation slot : addressDerivations.values()) slot.scale = 0;
            activeDerivations = 0;
            for (SavedDerivation row : saved) setDerivation(row.slot, row.base, row.index, row.scale);
        }

        PendingCompare checkpointCompare() {
            return pendingComparison == null ? null
                : new PendingCompare(pendingComparison, pendingLeft, pendingRight);
        }

        void restoreCompare(PendingCompare pending) {
            pendingComparison = pending == null ? null : pending.instruction();
            if (pending != null) {
                pendingLeft = pending.left();
                pendingRight = pending.right();
            }
        }

        boolean inspectRegister(PcodeThread<byte[]> thread, Register register, int slot) {
            if (thread instanceof P1MEJitMachine.MachineThread jit) {
                return jit.readObservedRegister(register, inspected, slot);
            }
            try {
                byte[] value = thread.getState().getVar(register, Reason.INSPECT);
                inspected[slot] = Utils.bytesToLong(value, value.length, language.isBigEndian());
                return true;
            }
            catch (RuntimeException unavailable) {
                return false;
            }
        }

        boolean inspectOperand(PcodeThread<byte[]> thread, OperandValue operand, int slot) {
            if (operand == null) return false;
            if (operand.register() != null) return inspectRegister(thread, operand.register(), slot);
            inspected[slot] = operand.scalar();
            return true;
        }

        boolean noteCompare(PcodeThread<byte[]> thread, InstructionObservation observation) {
            if (observation.compareWidth == 0
                    || !inspectOperand(thread, observation.penultimateValue, 0)
                    || !inspectOperand(thread, observation.lastValue, 1)) return false;
            pendingComparison = observation;
            pendingLeft = inspected[0];
            pendingRight = inspected[1];
            return true;
        }

        void consumeCompare(InstructionObservation branch) {
            InstructionObservation compare = pendingComparison;
            if (compare == null || !branch.conditional) return;
            model.trace.compare(compare.pc, branch.pc, compare.compareMnemonic, compare.compareWidth,
                pendingLeft, pendingRight);
            pendingComparison = null;
        }

        void updateAddressDerivations(PcodeThread<byte[]> thread, InstructionObservation observation,
                boolean compared) {
            Register destination = observation.destination;
            if (destination == null) return;
            AddressDerivation[] slots = observation.addressDerivations;
            AddressDerivation destinationSlot = slots[slots.length - 1];
            boolean reuseDestination = compared && observation.lastValue.register() == destination;
            if (observation.derivation == InstructionObservation.DERIVE_SHIFT) {
                if ((reuseDestination || inspectRegister(thread, destination, 1)) && inspected[1] != 0
                        && (compared || inspectOperand(thread, observation.penultimateValue, 0))
                        && inspected[0] >= 0 && inspected[0] < 31) {
                    setDerivation(destinationSlot, 0, inspected[1], 1 << (int) inspected[0]);
                    return;
                }
            }
            else if (observation.derivation == InstructionObservation.DERIVE_ADD) {
                AddressDerivation source = slots[slots.length - 2];
                if (source != null && (compared || inspectOperand(thread, observation.penultimateValue, 0))
                        && inspected[0] != 0 && (reuseDestination || inspectRegister(thread, destination, 1))) {
                    long sourceValue = inspected[0];
                    long base = inspected[1];
                    if (destinationSlot.scale != 0) {
                        setDerivation(destinationSlot, (sourceValue + destinationSlot.base) & 0xffffffffL,
                            destinationSlot.index, destinationSlot.scale);
                    }
                    else if (source.scale != 0) {
                        setDerivation(destinationSlot, (base + source.base) & 0xffffffffL,
                            source.index, source.scale);
                    }
                    else {
                        setDerivation(destinationSlot, base, sourceValue, 1);
                    }
                    return;
                }
            }
            if (activeDerivations == 0) return;
            for (AddressDerivation result : observation.resultDerivations(this)) {
                if (result.scale != 0) {
                    result.scale = 0;
                    activeDerivations--;
                }
            }
        }

        void recordIndex(long pc, AddressDerivation derivation, long effective, int width, String access) {
            model.trace.tableIndex(pc, derivation.base, derivation.index, derivation.scale,
                effective, width, access);
        }

        private void noteIndex(long effective, int size, String access) {
            if (activeDerivations == 0) return;
            InstructionObservation observation = currentObservation;
            if (observation == null) return;
            for (AddressDerivation derivation : observation.addressDerivations) {
                if (derivation == null || !derivation.matches(effective)) continue;
                recordIndex(observation.pc, derivation, effective, size * 8, access);
                return;
            }
        }

        void noteIndirectBranch(PcodeThread<byte[]> thread, InstructionObservation observation) {
            if (!observation.computed || activeDerivations == 0) return;
            for (int i = 0; i < observation.addressDerivations.length; i++) {
                AddressDerivation derivation = observation.addressDerivations[i];
                if (derivation == null || derivation.scale == 0 || derivation.index == 0
                        || !inspectRegister(thread, observation.addressRegisters[i], 0)
                        || !derivation.matches(inspected[0])) {
                    continue;
                }
                recordIndex(observation.pc, derivation, inspected[0], 32, "branch");
                return;
            }
        }

        long offset(byte[] value) {
            return Utils.bytesToLong(value, value.length, language.isBigEndian()) & 0xffffffffL;
        }

        @Override
        public void beforeDecodeInstruction(PcodeThread<byte[]> thread, Address counter,
                                            RegisterValue context) {
            authorizeInstructionStart(thread, counter);
        }

        long authorizeInstructionStart(PcodeThread<byte[]> thread, Address counter) {
            return model.requireExecute(thread, counter.getOffset(), 1);
        }

        @Override
        public void beforeExecuteInstruction(PcodeThread<byte[]> thread,
                                             Instruction instruction, PcodeProgram program) {
            beforeExecuteInstruction(thread, instruction, null, 0);
        }

        void beforeExecuteInstruction(PcodeThread<byte[]> thread, Instruction instruction,
                                      Address fetchStart, long fetchEnd) {
            Address address = instruction.getAddress();
            long pc = address.getOffset();
            int size = instruction.getLength();
            model.trace.enterInstruction(pc, size);
            if (size <= 0 || Long.compareUnsigned(pc + size, fetchEnd) > 0
                    || !address.equals(fetchStart)) {
                model.requireExecute(thread, pc, size);
            }
            P1MEJitMachine.MachineThread jit = thread instanceof P1MEJitMachine.MachineThread machineThread
                ? machineThread : null;
            if (jit == null || !jit.hasVerifiedInstructionBytes(instruction)) {
                thread.getState().getVar(model.memorySpace, pc, size, true, Reason.EXECUTE_READ);
            }
            // Authorization and bytes for this boundary were observed normally.
            // A clock or scheduler action later in the instruction sets the barrier again.
            model.idleBatchBarrier = false;
            InstructionObservation observation = jit == null ? null : jit.currentObservation(instruction);
            if (observation == null) observation = decodeObservation(instruction, null);
            currentObservation = observation;
            if (model.trace.recordsInstructionMetadata()
                    && (model.compareOperands || model.inputDerivedTableIndices)) {
                consumeCompare(observation);
                noteIndirectBranch(thread, observation);
                boolean compared = noteCompare(thread, observation);
                if (model.inputDerivedTableIndices)
                    updateAddressDerivations(thread, observation, compared);
            }
            if (observation.readsIcctrl) model.scriptIcctrl(thread);
            interruptReturn = observation.returnFromInterrupt;
            interruptReturnChannel = interruptReturn
                ? model.activeInterruptChannels.peekLast() : null;
            automaticPriorityReturn = interruptReturn
                && (model.processorRegister(thread, "PSW") & 0x40) == 0
                && (model.processorRegister(thread, "INTCFG") & 1) == 0;
            icctrlWrite = observation.writesIcctrl;
            protectedIsprWrite = observation.writesIspr
                && (model.processorRegister(thread, "INTCFG") & 1) == 0;
            if (automaticPriorityReturn || protectedIsprWrite) {
                isprBeforeInstruction = model.processorRegister(thread, "ISPR");
            }
        }

        // CPU data transactions only. Concrete-offset access is the backing path for
        // fetch, inspection, device updates, and the transfer after authorization.
        private RegisterDef beginBusRead(PcodeThread<byte[]> thread, long address, int size) {
            noteIndex(address, size, "load");
            return model.beforeRead(thread, address, size);
        }

        private void endBusRead(PcodeThread<byte[]> thread, RegisterDef register, long address, int size) {
            model.completeBusRead(thread, register, address, size);
            // EIC request bits change on modeled edges or writes. A completed byte
            // test can be repeated only before the next such boundary.
            if (register != null && size == 1 && register.plainEicRead
                    && currentObservation != null && "tst1".equals(currentObservation.mnemonic)) {
                model.pollTest = currentObservation.instruction;
                model.pollReadTick = model.trace.instructions;
                model.pollReadAddress = address;
            }
        }

        long readBusNumber(long address, int size) {
            PcodeThread<byte[]> thread = model.executionThread;
            RegisterDef register = beginBusRead(thread, address, size);
            boolean bigEndian = model.bigEndian;
            long value = register != null && register.read_input
                ? model.readInputNumber(register, address, size)
                : model.deviceState.readBusBacking(register, address, size, bigEndian, Reason.EXECUTE_READ);
            endBusRead(thread, register, address, size);
            return value;
        }

        byte[] readBus(long address, int size) {
            PcodeThread<byte[]> thread = model.executionThread;
            RegisterDef register = beginBusRead(thread, address, size);
            byte[] result = register != null && register.read_input
                ? model.readInputLanes(register, address, size)
                : model.emulator.getSharedState().getVar(model.memorySpace, address, size,
                    true, Reason.EXECUTE_READ);
            endBusRead(thread, register, address, size);
            return result;
        }

        void writeBusNumber(long address, int size, long value) {
            noteIndex(address, size, "store");
            model.storeBus(model.executionThread, address, size, value, null, true);
        }

        void writeBus(long address, byte[] value) {
            noteIndex(address, value.length, "store");
            model.storeBus(model.executionThread, address, value.length, 0, value, true);
        }

        @Override
        public void afterExecuteInstruction(PcodeThread<byte[]> thread, Instruction instruction) {
            InstructionObservation observation = currentObservation;
            boolean sameInstruction = observation != null && observation.instruction == instruction;
            long pc = sameInstruction ? observation.pc : instruction.getAddress().getOffset();
            boolean boundedCall = (!sameInstruction || !observation.ordinaryRetirement) &&
                finishObservedInstruction(thread, instruction, observation, sameInstruction, pc);
            model.trace.instructions++;
            model.trace.recordExecutedPc(pc);
            if (boundedCall) model.noteBoundedCall(thread);
            model.trace.noteRecentPc(pc);
            model.lastRetiredPc = pc;
            model.retireClock(thread);
            model.dispatchDueEvents();
            model.deliverSystemError(thread);
            currentObservation = null;
        }

        private boolean finishObservedInstruction(PcodeThread<byte[]> thread, Instruction instruction,
                InstructionObservation observation, boolean sameInstruction, long pc) {
            if (automaticPriorityReturn) {
                model.processorRegister(thread, "ISPR", isprBeforeInstruction & (isprBeforeInstruction - 1));
            }
            else if (protectedIsprWrite) {
                model.processorRegister(thread, "ISPR", isprBeforeInstruction);
            }
            if (interruptReturn) {
                if (interruptReturnChannel != null) {
                    int enteredChannel = model.activeInterruptChannels.removeLast();
                    if (enteredChannel != interruptReturnChannel) {
                        throw new IllegalStateException(
                            "interrupt-return stack changed before eiret retirement");
                    }
                }
                if (!model.trace.deviceEvents.omitsEventPayload("interrupt-return")) {
                    JsonObject event = new JsonObject();
                    event.addProperty("kind", "interrupt-return");
                    event.addProperty("pc", hex32(pc));
                    if (interruptReturnChannel != null)
                        event.addProperty("channel", interruptReturnChannel);
                    event.addProperty("return_pc", hex32(model.pc(thread)));
                    event.addProperty("scheduler_tick", model.trace.instructions + 1);
                    model.trace.deviceEvents.add(event);
                }
            }
            String mnemonic = sameInstruction ? observation.mnemonic : instruction.getMnemonicString();
            switch (mnemonic) {
                case "synce" -> model.trace.sync("SYNCE");
                case "syncm" -> model.trace.sync("SYNCM");
                case "syncp" -> model.trace.sync("SYNCP");
                case "synci" -> model.trace.sync("SYNCI");
                default -> { }
            }
            if ("prepare".equals(mnemonic)) {
                model.clearPreparedFrame(thread, instruction);
            }
            if (icctrlWrite) model.completeInstructionCacheClear(thread);
            return "jarl".equals(mnemonic);
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
        String digits = "0123456789ABCDEF";
        byte[] text = new byte[10];
        text[0] = '0';
        text[1] = 'x';
        for (int index = 9; index >= 2; index--, value >>>= 4) {
            text[index] = (byte) digits.charAt((int) value & 15);
        }
        return new String(text, StandardCharsets.ISO_8859_1);
    }

    static byte[] bytes(long value, int size, boolean bigEndian) {
        return Utils.longToBytes(value, size, bigEndian);
    }

    static byte[] parseHex(String value) {
        String text = value.replace(" ", "").replace("_", "");
        if ((text.length() & 1) != 0) throw new IllegalArgumentException("odd-length hex bytes");
        byte[] out = new byte[text.length() / 2];
        for (int i = 0; i < out.length; i++) {
            out[i] = (byte) Integer.parseInt(text, i * 2, i * 2 + 2, 16);
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
                SleighLanguage language = model.language;
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
            int length = entryInstructionLength(model.language, codeflash, imageBase, resolved);
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
        int entryLength = entryInstructionLength(model.language, codeflash, imageBase, resolved);
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

    private int entryInstructionLength(SleighLanguage language, byte[] codeflash, long imageBase,
            long resolved) throws Exception {
        Address address = language.getDefaultSpace().getAddress(resolved);
        try {
            Instruction instruction = currentProgram.getListing().getInstructionAt(address);
            if (instruction != null) return instruction.getLength();
        }
        catch (DomainObjectException unavailable) {
            // Decode from the verified flash image instead.
        }

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

    private record CheckResults(JsonArray rows, boolean passed) {}

    private CheckResults evaluateChecks(Model model, PcodeThread<byte[]> thread,
                                            SleighLanguage language, List<CheckDef> checks) {
        JsonArray results = new JsonArray(checks.size());
        boolean allPassed = true;
        for (CheckDef check : checks) {
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
            allPassed &= passed;
        }
        return new CheckResults(results, allPassed);
    }

    private JsonObject reportBase(
            RunContract contract, Scenario scenario, Trace trace, JsonObject resolution) {
        JsonObject report = new JsonObject();
        report.addProperty("schema", "rh850-p1me-machine-report-v2");
        report.addProperty("target", contract.target.name);
        report.addProperty("mcu", contract.target.mcu);
        report.addProperty("scenario", scenario.name);
        report.addProperty("engine", scenario.engine.equals("jit")
            ? "Ghidra JitPcodeEmulator" : "Ghidra PcodeEmulator");
        report.addProperty("codeflash_sha256", contract.target.codeflash.sha256);
        report.addProperty("model_sha256", contract.model_sha256);
        report.addProperty("executable_overlays", false);
        report.addProperty("stubbed_execution", scenario.stubbed());
        report.add("entry_resolution", resolution);
        JsonObject resolvedContract = new JsonObject();
        resolvedContract.add("entry", resolution.deepCopy());
        if (scenario.source != null)
            resolvedContract.add("source", scenario.source.deepCopy());
        resolvedContract.add("stop_addresses", GSON.toJsonTree(scenario.stop_addresses));
        resolvedContract.addProperty("max_instructions", scenario.max_instructions);
        resolvedContract.addProperty("hsb_cycles_per_instruction", scenario.hsb_cycles_per_instruction);
        resolvedContract.addProperty("expected_termination", scenario.expected_termination);
        resolvedContract.addProperty("reset", scenario.reset);
        if (scenario.instruction_trace_start_step != null)
            resolvedContract.addProperty(
                "instruction_trace_start_step", scenario.instruction_trace_start_step);
        resolvedContract.addProperty("compare_operands", scenario.compare_operands);
        resolvedContract.addProperty(
            "input_derived_table_indices", scenario.input_derived_table_indices);
        if (scenario.icus_startup_stub != null)
            resolvedContract.add("icus_startup_stub", GSON.toJsonTree(scenario.icus_startup_stub));
        if (scenario.dma_master_rewrite_assumption != null)
            resolvedContract.addProperty("dma_master_rewrite_assumption", scenario.dma_master_rewrite_assumption);
        report.add("resolved_run_contract", resolvedContract);
        report.addProperty("instruction_count", trace.instructions);
        report.addProperty("unique_instruction_addresses", trace.executed.size());
        report.add("recent_pcs", trace.recentPcs());
        report.add("sync_counts", GSON.toJsonTree(trace.syncCounts));
        report.addProperty("trace_lost_address", trace.traceLostAddress);
        report.add("compare_operands", com.google.gson.JsonNull.INSTANCE);
        report.add("input_derived_table_indices", com.google.gson.JsonNull.INSTANCE);
        if (trace.instructionTraceEnabled) {
            report.addProperty("instruction_trace_semantics",
                "entered instructions in callback order; instruction is the absolute retired count "
                + "before entry (terminal fault/halt may not retire); instruction_trace_start_step "
                + "defers recording through the named step; modeled shortcuts do not retire or "
                + "synthesize instructions and appear separately in instruction_trace_shortcuts");
        }
        return report;
    }

    static final class MemoryStateSnapshot {
        private final Map<AddressSpace, SemisparseByteArray> spaces;
        final long pageCount;
        final long initializedBytes;
        final long initializedRanges;

        private MemoryStateSnapshot(Map<AddressSpace, SemisparseByteArray> spaces,
                long pageCount, long initializedBytes, long initializedRanges) {
            this.spaces = spaces;
            this.pageCount = pageCount;
            this.initializedBytes = initializedBytes;
            this.initializedRanges = initializedRanges;
        }

        static MemoryStateSnapshot capture(
                Map<AddressSpace, ? extends BytesPcodeExecutorStateSpace> liveSpaces) {
            Map<AddressSpace, SemisparseByteArray> snapshots = new LinkedHashMap<>();
            long pages = 0;
            long initialized = 0;
            long ranges = 0;
            for (var entry : liveSpaces.entrySet()) {
                var data = InitializedBytes.backingOf(entry.getValue()).fork();
                snapshots.put(entry.getKey(), data);
                long previousPage = -1;
                for (var span : data.getInitialized().spans()) {
                    initialized = Math.addExact(initialized, span.length());
                    ranges++;
                    long first = Long.divideUnsigned(span.min(), SemisparseByteArray.BLOCK_SIZE);
                    long last = Long.divideUnsigned(span.max(), SemisparseByteArray.BLOCK_SIZE);
                    // Spans are ordered but can share a page; count each initialized page once.
                    pages = Math.addExact(pages, last - Math.max(first, previousPage + 1) + 1);
                    previousPage = last;
                }
            }
            return new MemoryStateSnapshot(snapshots, pages, initialized, ranges);
        }

        boolean hasSameDefinedBytes(Map<AddressSpace, ? extends BytesPcodeExecutorStateSpace> live) {
            if (!spaces.keySet().equals(live.keySet())) return false;
            for (var entry : spaces.entrySet()) {
                var saved = entry.getValue().getInitialized().spans().iterator();
                var current = InitializedBytes.backingOf(live.get(entry.getKey()))
                    .getInitialized().spans().iterator();
                while (saved.hasNext() && current.hasNext()) {
                    var a = saved.next();
                    var b = current.next();
                    if (a.min() != b.min() || a.max() != b.max()) return false;
                }
                if (saved.hasNext() || current.hasNext()) return false;
            }
            return true;
        }

        boolean copyIntoBoundPages(Map<AddressSpace, ? extends BytesPcodeExecutorStateSpace> live,
                AddressSpace fetchSpace, BitSet decodedPages) {
            boolean codeChanged = false;
            int size = SemisparseByteArray.BLOCK_SIZE;
            long mask = -((long) size);
            for (var entry : spaces.entrySet()) {
                var source = entry.getValue();
                var target = InitializedBytes.backingOf(live.get(entry.getKey()));
                long copied = -1;
                for (var span : source.getInitialized().spans()) {
                    long last = span.max() & mask;
                    for (long base = span.min() & mask;; base += size) {
                        if (base != copied) {
                            byte[] saved = source.getDirect(base);
                            if (entry.getKey() == fetchSpace && !codeChanged &&
                                    Long.compareUnsigned(base / size, Integer.MAX_VALUE) <= 0 &&
                                    decodedPages.get((int) (base / size))) {
                                var current = target.getDirectPage(base);
                                codeChanged = !Arrays.equals(current.array(), current.offset(), current.offset() + size,
                                    saved, 0, size);
                            }
                            target.copyDirectPage(base, saved);
                            copied = base;
                        }
                        if (base == last) break;
                    }
                }
            }
            return codeChanged;
        }

        void restore(Map<AddressSpace, ? extends BytesPcodeExecutorStateSpace> liveSpaces,
                java.util.function.Function<AddressSpace, ? extends BytesPcodeExecutorStateSpace> getOrCreateSpace) {
            liveSpaces.keySet().retainAll(spaces.keySet());
            for (var entry : spaces.entrySet()) {
                var bytes = InitializedBytes.backingOf(getOrCreateSpace.apply(entry.getKey()));
                // Retain the space object, not its pages. JIT entries must rebind after restore.
                bytes.clear();
                bytes.putAll(entry.getValue());
            }
        }
    }

    // Each upstream piece fixes its own space superclass and exposes the bytes only to subclasses.
    interface InitializedBytes {
        SemisparseByteArray backing();

        static SemisparseByteArray backingOf(BytesPcodeExecutorStateSpace space) {
            return ((InitializedBytes) space).backing();
        }

        static boolean covers(SemisparseByteArray bytes, AddressSpace space, long offset, int size) {
            long end = offset + size - 1L;
            return size > 0 && Long.compareUnsigned(offset, end) <= 0
                && Long.compareUnsigned(end, space.getMaxAddress().getOffset()) <= 0
                && bytes.isInitialized(offset, end);
        }
    }

    static final class InitializedBytesSpace extends BytesPcodeExecutorStateSpace
            implements InitializedBytes {
        InitializedBytesSpace(Language language, AddressSpace space,
                BytesPcodeExecutorStatePiece piece) {
            super(language, space, piece);
        }

        @Override
        public SemisparseByteArray backing() {
            return bytes;
        }

        @Override
        public byte[] read(long offset, int size, Reason reason, PcodeStateCallbacks cb) {
            // Partial, empty and wrapping ranges retain Ghidra's callbacks and faults.
            if (InitializedBytes.covers(bytes, space, offset, size))
                return readBytes(offset, size, reason);
            return super.read(offset, size, reason, cb);
        }
    }

    static final class InitializedBytesPiece extends BytesPcodeExecutorStatePiece {
        InitializedBytesPiece(Language language, PcodeStateCallbacks callbacks) {
            super(language, callbacks);
        }

        @Override
        protected BytesPcodeExecutorStateSpace newSpace(AddressSpace space) {
            return new InitializedBytesSpace(language, space, this);
        }

        MemoryStateSnapshot checkpoint() {
            return MemoryStateSnapshot.capture(spaceMap);
        }

        void restore(MemoryStateSnapshot checkpoint) {
            checkpoint.restore(spaceMap, space -> getForSpace(space, true));
        }
    }

    interface CheckpointableBytesState {
        MemoryStateSnapshot checkpoint();
        void restore(MemoryStateSnapshot checkpoint);
    }

    static final class InitializedBytesState extends BytesPcodeExecutorState
            implements CheckpointableBytesState {
        private final InitializedBytesPiece initializedPiece;
        private final Callbacks bus;

        InitializedBytesState(Language language, Callbacks callbacks, PcodeThread<byte[]> thread) {
            this(new InitializedBytesPiece(language, callbacks.wrapFor(thread)),
                thread == null ? callbacks : null);
        }

        private InitializedBytesState(InitializedBytesPiece piece, Callbacks bus) {
            super(piece);
            this.initializedPiece = piece;
            this.bus = bus;
        }

        @Override
        public byte[] getVar(AddressSpace space, byte[] offset, int size, boolean quantize, Reason reason) {
            if (bus != null && reason == Reason.EXECUTE_READ && space.equals(bus.model.memorySpace))
                return bus.readBus(bus.offset(offset), size);
            return super.getVar(space, offset, size, quantize, reason);
        }

        @Override
        public void setVar(AddressSpace space, byte[] offset, int size, boolean quantize,
                byte[] value) {
            if (bus != null && space.equals(bus.model.memorySpace)) {
                bus.writeBus(bus.offset(offset), value.length == size ? value : Arrays.copyOf(value, size));
                return;
            }
            super.setVar(space, offset, size, quantize, value);
        }

        @Override
        public MemoryStateSnapshot checkpoint() {
            return initializedPiece.checkpoint();
        }

        @Override
        public void restore(MemoryStateSnapshot checkpoint) {
            initializedPiece.restore(checkpoint);
        }
    }

    static final class ModelGraphCheckpoint {
        private static final Set<String> MODEL_UNCAPTURED = Set.of(
            "language", "spec", "trace", "executionThread", "regions", "registers",
            "regionCache", "registerPages", "registerPageBase", "mpu", "mpuHints",
            "registersByName", "interruptRegisters", "interruptRegistersByAddress",
            "portBindings", "portColumnValues", "gramGuards", "peripheralGuards",
            "aliases", "emulator", "memorySpace",
            "deviceState", "dmaWordIndex", // Derived from backing storage; both restore paths invalidate it.
            // Capture commits all ticks. Restore only needs to rebase derived timing.
            "quietUntil", "quietClockEvents",
            "taudClockTick", "taujClockTick", "rsentClockTick",
            "taudClockDue", "taujClockDue", "rsentClockDue"
        );
        final List<Runnable> restoreOperations = new ArrayList<>();
        final IdentityHashMap<Object, Boolean> visited = new IdentityHashMap<>();
        int mutableFieldCount;

        ModelGraphCheckpoint(Model model) {
            captureObject(model, "Model");
        }

        private boolean immutable(Object value) {
            Class<?> type = value.getClass();
            if (type.isEnum() || type.isRecord() || value instanceof String
                    || value instanceof Number || value instanceof Boolean
                    || value instanceof Character || value instanceof Class
                    || value instanceof Runnable || value instanceof Comparator
                    || value instanceof JsonElement || value instanceof Address
                    || value instanceof AddressSpace || value instanceof Register
                    || value instanceof RegisterValue || value instanceof SleighLanguage
                    || value instanceof PcodeExecutor<?> || value instanceof PcodeProgram
                    || value instanceof PcodeThread<?> || value instanceof PcodeEmulator
                    || value instanceof MachineSpec || value instanceof RegionDef
                    || value instanceof RegisterDef || value instanceof ExternalEvent) {
                return true;
            }
            Package pkg = type.getPackage();
            String name = pkg == null ? "" : pkg.getName();
            return name.startsWith("java.time.") || name.startsWith("java.math.");
        }

        @SuppressWarnings({"rawtypes", "unchecked"})
        private void captureObject(Object value, String path) {
            if (value == null || immutable(value) || visited.put(value, Boolean.TRUE) != null) return;
            Class<?> type = value.getClass();
            if (type.isArray()) {
                int length = Array.getLength(value);
                Object copy = Array.newInstance(type.getComponentType(), length);
                System.arraycopy(value, 0, copy, 0, length);
                restoreOperations.add(() -> System.arraycopy(copy, 0, value, 0, length));
                if (!type.getComponentType().isPrimitive()) {
                    for (int index = 0; index < length; index++)
                        captureObject(Array.get(value, index), path + "[" + index + "]");
                }
                return;
            }
            if (value instanceof BitSet bits) {
                BitSet copy = (BitSet) bits.clone();
                restoreOperations.add(() -> {
                    bits.clear();
                    bits.or(copy);
                });
                return;
            }
            if (value instanceof Map map) {
                Map copy = new LinkedHashMap(map);
                restoreOperations.add(() -> {
                    map.clear();
                    map.putAll(copy);
                });
                for (Object entryObject : copy.entrySet()) {
                    Map.Entry entry = (Map.Entry) entryObject;
                    captureObject(entry.getKey(), path + ".key");
                    captureObject(entry.getValue(), path + ".value");
                }
                return;
            }
            if (value instanceof Collection collection) {
                List copy = new ArrayList(collection);
                restoreOperations.add(() -> {
                    collection.clear();
                    collection.addAll(copy);
                });
                for (Object item : copy) captureObject(item, path + "[]");
                return;
            }
            if (!type.getName().startsWith(RunP1MEMachine.class.getName() + "$")) {
                throw new IllegalStateException(
                    "checkpoint cannot capture " + path + " of type " + type.getName());
            }
            for (Class<?> current = type; current != Object.class; current = current.getSuperclass()) {
                for (Field field : current.getDeclaredFields()) {
                    if (Modifier.isStatic(field.getModifiers()) || field.isSynthetic()) continue;
                    if (value instanceof Model && MODEL_UNCAPTURED.contains(field.getName())) continue;
                    try {
                        field.setAccessible(true);
                        Object fieldValue = field.get(value);
                        if (!Modifier.isFinal(field.getModifiers())) {
                            Object saved = fieldValue;
                            restoreOperations.add(() -> {
                                try {
                                    field.set(value, saved);
                                }
                                catch (IllegalAccessException exception) {
                                    throw new IllegalStateException(
                                        "cannot restore " + path + "." + field.getName(), exception);
                                }
                            });
                            mutableFieldCount++;
                        }
                        captureObject(fieldValue, path + "." + field.getName());
                    }
                    catch (IllegalAccessException exception) {
                        throw new IllegalStateException(
                            "cannot capture " + path + "." + field.getName(), exception);
                    }
                }
            }
        }

        void restore() {
            for (Runnable operation : restoreOperations) operation.run();
        }
    }

    static final class MachineCheckpoint {
        final ModelGraphCheckpoint model;
        final MemoryStateSnapshot sharedMemory;
        final MemoryStateSnapshot localMemory;
        final Trace.Checkpoint trace;
        final Address counter;
        final RegisterValue context;
        final boolean suspended;
        final long captureNanoseconds;
        final Callbacks.PendingCompare pendingCompare;
        final List<Callbacks.SavedDerivation> addressDerivations;

        MachineCheckpoint(Model machine, Callbacks callbacks, PcodeThread<byte[]> thread) throws IOException {
            if (thread.getFrame() != null)
                throw new IllegalStateException("checkpoint requires an instruction boundary");
            long started = System.nanoTime();
            machine.drainDeviceClocks();
            machine.invalidateClockHorizon();
            model = new ModelGraphCheckpoint(machine);
            CheckpointableBytesState shared =
                (CheckpointableBytesState) thread.getState().getSharedState();
            CheckpointableBytesState local =
                (CheckpointableBytesState) thread.getState().getLocalState();
            sharedMemory = shared.checkpoint();
            localMemory = local.checkpoint();
            trace = machine.trace.checkpoint();
            counter = thread.getCounter();
            context = thread.getContext();
            suspended = thread.isSuspended();
            pendingCompare = callbacks.checkpointCompare();
            addressDerivations = callbacks.checkpointDerivations();
            captureNanoseconds = System.nanoTime() - started;
        }

        long pageCount() {
            return sharedMemory.pageCount + localMemory.pageCount;
        }

        long initializedBytes() {
            return sharedMemory.initializedBytes + localMemory.initializedBytes;
        }

        long initializedRanges() {
            return sharedMemory.initializedRanges + localMemory.initializedRanges;
        }

        long restore(Model machine, Callbacks callbacks, PcodeThread<byte[]> thread) throws IOException {
            long started = System.nanoTime();
            model.restore();
            machine.invalidateClockHorizon();
            machine.rebaseDeviceClocks();
            var shared = (CheckpointableBytesState) thread.getState().getSharedState();
            var local = (CheckpointableBytesState) thread.getState().getLocalState();
            if (!(shared instanceof P1MEJitMachine.MachineState jitShared &&
                    local instanceof P1MEJitMachine.MachineState jitLocal &&
                    jitShared.restoreBoundPair(sharedMemory, jitLocal, localMemory))) {
                shared.restore(sharedMemory);
                local.restore(localMemory);
            }
            machine.trace.restore(trace);
            callbacks.restoreCompare(pendingCompare);
            callbacks.restoreDerivations(addressDerivations);
            if (thread.getFrame() != null) thread.dropInstruction();
            thread.overrideCounter(counter);
            if (context != null) thread.overrideContext(context);
            thread.setSuspended(suspended);
            return System.nanoTime() - started;
        }
    }


    private void addSymbolCacheProbe(JsonObject report) {
        if (!Boolean.getBoolean("p1me.symbolCacheProbe")) return;
        // Test-only, isolated-process census. A 12.2 JIT compilation creates one
        // JitDataFlowUseropLibrary per passage. No completed compiler graph may
        // remain as a global SymbolsCache key, including after scenario failure.
        System.gc();
        System.runFinalization();
        System.gc();
        int roots = 0;
        synchronized (PcodeUseropLibrary.SYMBOL_CACHE) {
            for (PcodeUseropLibrary<?> library : PcodeUseropLibrary.SYMBOL_CACHE.keySet()) {
                if (library.getClass().getName().equals(
                        "ghidra.pcode.emu.jit.analysis.JitDataFlowUseropLibrary")) roots++;
            }
        }
        report.addProperty("daemon_jit_dataflow_symbol_cache_roots", roots);
        var symbolsCacheSource = PcodeUseropLibrary.class.getClassLoader()
            .getResource("ghidra/pcode/exec/SymbolsCache.class");
        report.addProperty("daemon_symbols_cache_source",
            symbolsCacheSource == null ? "" : symbolsCacheSource.toExternalForm());
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
        model.compareOperands = scenario.compare_operands;
        model.inputDerivedTableIndices = scenario.input_derived_table_indices;
        Callbacks callbacks = new Callbacks(language, model);
        PcodeMachine<byte[]> emulator = scenario.engine.equals("jit")
            ? new P1MEJitMachine(language, callbacks) : new PcodeEmulator(language, callbacks) {
            @Override
            protected PcodeExecutorState<byte[]> createSharedState() {
                return new InitializedBytesState(language, callbacks, null);
            }
            @Override
            protected PcodeExecutorState<byte[]> createLocalState(PcodeThread<byte[]> thread) {
                return new InitializedBytesState(language, callbacks, thread);
            }
            @Override
            protected PcodeUseropLibrary<byte[]> createUseropLibrary() {
                return new Rh850Userops();
            }
        };
        JsonObject report = null;
        try {
            report = executeScenario(
                contract, language, scenario, codeflash, dataflash, trace,
                model, callbacks, emulator);
            return report;
        }
        finally {
            Runtime runtime = Runtime.getRuntime();
            long heapBeforeRelease = runtime.totalMemory() - runtime.freeMemory();
            if (report != null)
                report.addProperty("daemon_heap_bytes_before_release", heapBeforeRelease);
            if (emulator instanceof P1MEJitMachine jit) jit.release();
            model.executionThread = null;
            model.emulator = null;
            model.deviceState = null;
            model.eventSocket = null;
        }
    }

    private void finishHeapRelease(JsonObject report, long heapAtScenarioStart) {
        Runtime runtime = Runtime.getRuntime();
        long releasedHeap = runtime.totalMemory() - runtime.freeMemory();
        long heapBeforeRelease = report.has("daemon_heap_bytes_before_release")
            ? report.get("daemon_heap_bytes_before_release").getAsLong() : releasedHeap;
        boolean fullCollection = heapBeforeRelease >= runtime.maxMemory() / 2
            && heapBeforeRelease - heapAtScenarioStart >= runtime.maxMemory() / 8;
        if (fullCollection) System.gc();
        long heapAfterRelease = runtime.totalMemory() - runtime.freeMemory();
        report.addProperty("daemon_heap_bytes_before_release", heapBeforeRelease);
        report.addProperty("daemon_heap_bytes_after_release", heapAfterRelease);
        report.addProperty("daemon_full_collection", fullCollection);
        report.addProperty("daemon_heap_bytes_reclaimed",
            Math.max(0, heapBeforeRelease - heapAfterRelease));
    }

    static final class ExecutionResult {
        MachineFault fault;
        MachineHalt halt;
        boolean stopAfterArrivals;
        Map<Long, Long> arrivalCounts = Map.of();
    }

    static final class StepBatchResult {
        final JsonObject report;
        final boolean passed;
        final String finalTermination;

        StepBatchResult(JsonObject report, boolean passed, String finalTermination) {
            this.report = report;
            this.passed = passed;
            this.finalTermination = finalTermination;
        }
    }
    static final class ArrivalCounter {
        final long[] addresses, limits, counts;

        ArrivalCounter(List<StopArrival> rows) {
            int n = rows.size();
            addresses = new long[n];
            limits = new long[n];
            counts = new long[n];
            for (int i = 0; i < n; i++) {
                StopArrival row = rows.get(i);
                long address = parseUnsigned(row.address);
                for (int j = 0; j < i; j++) if (addresses[j] == address)
                    throw new IllegalArgumentException("duplicate stop_after_arrivals address");
                if (row.count <= 0) throw new IllegalArgumentException("arrival count must be positive");
                addresses[i] = address;
                limits[i] = row.count;
            }
        }

        boolean arrive(long address) {
            for (int i = 0; i < addresses.length; i++) if (addresses[i] == address) {
                counts[i] = Math.incrementExact(counts[i]);
                return counts[i] >= limits[i];
            }
            return false;
        }

        Map<Long, Long> snapshot() {
            Map<Long, Long> result = new LinkedHashMap<>();
            for (int i = 0; i < addresses.length; i++) result.put(addresses[i], counts[i]);
            return result;
        }
    }


    private ExecutionResult runUntil(
            Model model, PcodeThread<byte[]> thread, long instructionLimit,
            Set<Long> stops) throws Exception {
        return runUntil(model, thread, instructionLimit, stops, null);
    }

    private ExecutionResult runUntil(
            Model model, PcodeThread<byte[]> thread, long instructionLimit,
            Set<Long> stops, ArrivalCounter arrivals) throws Exception {
        ExecutionResult result = new ExecutionResult();
        var stopIndex = P1MEJitMachine.StopIndex.of(stops);
        if (arrivals != null && arrivals.addresses.length == 0) arrivals = null;
        var batchStops = stopIndex;
        boolean batchArrivals = arrivals != null && model.trace.canDeferNativeBus();
        if (batchArrivals) {
            var boundaries = new java.util.HashSet<Long>(stops);
            for (long address : arrivals.addresses) boundaries.add(address);
            batchStops = P1MEJitMachine.StopIndex.of(boundaries);
        }
        P1MEJitMachine.MachineThread jit =
            thread instanceof P1MEJitMachine.MachineThread machineThread ? machineThread : null;
        P1MEJitMachine.PolledBitLoop pollLoop = null;
        try {
            while (true) {
                long pc = thread.getCounter().getOffset();
                if (arrivals != null && arrivals.arrive(pc)) {
                    result.stopAfterArrivals = true;
                    break;
                }
                if (model.trace.instructions >= instructionLimit || stopIndex.contains(pc)) break;
                if (pollLoop != null && pc != pollLoop.testPc() && pc != pollLoop.branchPc())
                    pollLoop = null;
                monitor.checkCancelled();
                if (model.eventSocket != null) model.eventSocket.poll(thread);
                if (!model.boundedEdges.isEmpty() && model.returnBoundedCallee(thread)) continue;
                model.dispatchDueEvents();
                model.dispatchExternalEvents();
                model.deliverInterrupt(thread);
                model.completeCountedDelay(thread);
                // Count arrivals at the scheduler boundary. Retire just one instruction
                // at a watched PC so a self-branch counts as another arrival.
                if (jit != null && (arrivals == null ||
                        batchArrivals && !batchStops.contains(thread.getCounter().getOffset()))) {
                    if (model.eventSocket == null) {
                        if (model.pollTest != null) {
                            long elapsed = model.trace.instructions - model.pollReadTick;
                            if (elapsed != 1) {
                                Instruction test = model.pollTest;
                                model.pollTest = null;
                                pollLoop = elapsed == 2 && !model.peripheralFile && model.boundedEdges.isEmpty()
                                    ? jit.decodedPolledBitLoop(pollLoop, test, model.lastRetiredPc) : null;
                                if (pollLoop != null &&
                                        model.repeatPoll(jit, instructionLimit, batchStops, pollLoop)) continue;
                            }
                        }
                        // A clock edge discards the value witness, not the decoded
                        // pair. Step one real instruction after the scheduler; a
                        // branch after an edge-ending test still sees that test's Z.
                        if (pollLoop != null && jit.stepPollBoundary(pollLoop, model.lastRetiredPc)) continue;
                        pollLoop = null;
                        if (model.pollTest != null) {
                            thread.stepInstruction();
                            continue;
                        }
                    }
                    long batchLimit = model.idleBatchLimit(
                        instructionLimit, thread.getCounter().getOffset());
                    if (batchLimit != 0) {
                        long batchPc = thread.getCounter().getOffset();
                        long batched = jit.batchIdle(batchLimit);
                        if (batched != 0) {
                            if (batched != batchLimit)
                                throw new IllegalStateException("partial idle batch retirement");
                            model.retireIdleBatch(batchPc, batched);
                            continue;
                        }
                    }
                    int instructionBatchLimit = model.instructionBatchLimit(instructionLimit);
                    if (instructionBatchLimit >= 2) {
                        jit.stepOrBatch(instructionBatchLimit, batchStops);
                        continue;
                    }
                }
                thread.stepInstruction();
            }
        }
        catch (RuntimeException exception) {
            result.fault = cause(exception, MachineFault.class);
            result.halt = cause(exception, MachineHalt.class);
            if (exception instanceof IllegalArgumentException) throw exception;
            if (result.fault == null && result.halt == null) {
                throw new IllegalStateException(
                    exception.getMessage() + " at pc=" + hex32(thread.getCounter().getOffset())
                    + " frame_active=" + (thread.getFrame() != null), exception);
            }
        }
        finally {
            model.pollTest = null;
            model.drainDeviceClocks();
        }
        if (arrivals != null) result.arrivalCounts = arrivals.snapshot();
        return result;
    }


    private static String byteHex(byte[] value) {
        return java.util.HexFormat.of().formatHex(value);
    }

    private static final class RegisterRows {
        private Register[] order;
        private byte[][] previous;
        private JsonArray rows;
        private P1MEJitMachine.MachineThread.RegisterImage image;

        private static JsonObject row(Register reg, byte[] value) {
            JsonObject row = new JsonObject();
            row.addProperty("name", reg.getName());
            row.addProperty("address", hex32(reg.getAddress().getOffset()));
            row.addProperty("size", value.length);
            row.addProperty("value_hex", byteHex(value));
            return row;
        }

        JsonArray capture(PcodeThread<byte[]> thread) {
            Map<Register, byte[]> values = null;
            if (image == null || !image.current()) {
                values = thread.getState().getRegisterValues();
                if (order == null || order.length != values.size() ||
                        !Arrays.stream(order).allMatch(values::containsKey)) {
                    order = values.keySet().toArray(Register[]::new);
                    Arrays.sort(order, Comparator.comparing(Register::getName)
                        .thenComparingLong(reg -> reg.getAddress().getOffset()));
                    previous = new byte[order.length][];
                    rows = null;
                }
                if (thread instanceof P1MEJitMachine.MachineThread jit) image = jit.bindRegisterImage(order);
            }
            JsonArray changed = rows == null ? new JsonArray(order.length) : null;
            for (int i = 0; i < order.length; i++) {
                Register reg = order[i];
                byte[] live = image == null ? values.get(reg) : image.bytes[i];
                int offset = image == null ? 0 : image.offsets[i];
                int size = image == null ? live.length : reg.getNumBytes();
                byte[] old = previous[i];
                if (old != null && old.length == size && Arrays.equals(old, 0, size, live, offset, offset + size)) continue;
                if (old == null || old.length != size) previous[i] = old = new byte[size];
                System.arraycopy(live, offset, old, 0, size);
                if (rows == null) changed.add(row(reg, old));
                else {
                    if (changed == null) {
                        changed = new JsonArray(order.length);
                        changed.addAll(rows);
                    }
                    changed.set(i, row(reg, old));
                }
            }
            if (changed != null) rows = changed;
            return rows;
        }
    }

    private static void flushPeripheralSnapshots(Model model) {
        model.drainDeviceClocks();
        model.taud.flush();
        model.tauj.flush();
        model.tsg.flushSnapshot();
        model.rsent.flush();
    }

    private StepBatchResult executeSteps(
            Model model, Callbacks callbacks, PcodeThread<byte[]> thread,
            SleighLanguage language, Scenario scenario) throws Exception {
        var registerRows = new RegisterRows();
        Map<String, MachineCheckpoint> checkpoints = new LinkedHashMap<>();
        JsonArray checkpointRows = new JsonArray();
        JsonArray trialRows = new JsonArray();
        long segmentStarted = System.nanoTime();
        long pendingRestoreNanoseconds = 0;
        boolean restored = false;
        boolean allPassed = true;
        String finalTermination = "incomplete";

        // A capture-disabled suffix below the row cap cannot ask whether a later unrecorded
        // address was previously written. A restore rechecks the cap from its own snapshot.
        int lastCapture = -1;
        for (int i = 0; i < scenario.steps.size(); i++) {
            var step = scenario.steps.get(i);
            if (("trial".equals(step.kind) && !Boolean.FALSE.equals(step.capture_rows)) ||
                    ("checkpoint".equals(step.kind) && step.after_instructions != null)) lastCapture = i;
        }
        int stepIndex = -1;
        for (ScenarioStep step : scenario.steps) {
            stepIndex++;
            switch (step.kind) {
                case "checkpoint": {
                    if (step.after_instructions != null) {
                        long checkpointInstruction = step.after_instructions;
                        if (checkpointInstruction > scenario.max_instructions) {
                            throw new IllegalArgumentException(
                                "checkpoint instruction boundary exceeds scenario budget");
                        }
                        ExecutionResult prefix = runUntil(
                            model, thread, checkpointInstruction, Set.of());
                        if (prefix.fault != null || prefix.halt != null
                                || model.trace.instructions != checkpointInstruction) {
                            throw new IllegalStateException(
                                "checkpoint prefix did not reach instruction " + checkpointInstruction);
                        }
                        // Events at the reached boundary are part of the prefix. In
                        // particular, tick-zero snapshot overlays must be installed
                        // before the checkpoint is captured.
                        model.dispatchDueEvents();
                        model.dispatchExternalEvents();
                    }
                    long prefixNanoseconds = System.nanoTime() - segmentStarted;
                    MachineCheckpoint checkpoint = new MachineCheckpoint(model, callbacks, thread);
                    if (checkpoints.put(step.name, checkpoint) != null)
                        throw new IllegalArgumentException("duplicate checkpoint " + step.name);
                    JsonObject row = new JsonObject();
                    row.addProperty("name", step.name);
                    row.addProperty("instruction", model.trace.instructions);
                    row.addProperty("prefix_nanoseconds", prefixNanoseconds);
                    row.addProperty("capture_nanoseconds", checkpoint.captureNanoseconds);
                    row.addProperty("memory_pages", checkpoint.pageCount());
                    row.addProperty("memory_page_bytes",
                        Math.multiplyExact(checkpoint.pageCount(), SemisparseByteArray.BLOCK_SIZE));
                    row.addProperty("initialized_bytes", checkpoint.initializedBytes());
                    row.addProperty("initialized_ranges", checkpoint.initializedRanges());
                    row.addProperty("mutable_model_fields",
                        checkpoint.model.mutableFieldCount);
                    checkpointRows.add(row);
                    segmentStarted = System.nanoTime();
                    restored = false;
                    pendingRestoreNanoseconds = 0;
                    break;
                }
                case "restore": {
                    MachineCheckpoint checkpoint = checkpoints.get(step.checkpoint);
                    if (checkpoint == null)
                        throw new IllegalArgumentException("unknown checkpoint " + step.checkpoint);
                    pendingRestoreNanoseconds = checkpoint.restore(model, callbacks, thread);
                    restored = true;
                    segmentStarted = System.nanoTime();
                    break;
                }
                case "trial": {
                    long startInstruction = model.trace.instructions;
                    List<String> eventKinds = step.capture_event_kinds;
                    boolean captureRows = step.capture_rows == null || step.capture_rows;
                    model.configureExternalEvents(thread, step.events, startInstruction, Model.EventOrigin.TRIAL);
                    Set<Long> trialStops = new HashSet<>();
                    for (String value : step.stop_addresses)
                        trialStops.add(parseUnsigned(value));
                    ArrivalCounter arrivals = new ArrivalCounter(step.stop_after_arrivals);
                    if (eventKinds == null) step.capture_rows = captureRows;
                    model.trace.beginTrial(captureRows, eventKinds);
                    model.trace.unobservedWrites = stepIndex > lastCapture && !captureRows && eventKinds == null &&
                        model.trace.memoryAccesses.size() < Trace.MAX_MEMORY_ROWS && model.eventSocket == null;
                    P1MEJitMachine.MachineThread jit = thread instanceof P1MEJitMachine.MachineThread t ? t : null;
                    long compiledAtStart = jit == null ? 0 : jit.compiledInstructions;
                    long idleAtStart = jit == null ? 0 : jit.idleInstructions;
                    long templateAtStart = jit == null ? 0 : jit.templateInstructions;
                    long trialStarted = System.nanoTime();
                    ExecutionResult result = runUntil(
                        model, thread,
                        Math.addExact(startInstruction, step.max_instructions),
                        trialStops, arrivals);
                    if (thread.getFrame() != null) thread.dropInstruction();
                    flushPeripheralSnapshots(model);
                    CheckResults checks =
                        evaluateChecks(model, thread, language, step.checks);
                    model.trace.unobservedWrites = false;
                    JsonObject eventKindCounts = model.trace.endTrial();
                    long trialNanoseconds = System.nanoTime() - trialStarted;
                    long finalPc = thread.getCounter().getOffset();
                    boolean atStop = trialStops.contains(finalPc);
                    String termination = result.fault != null ? "unexpected-fault"
                        : result.halt != null ? "halt"
                        : result.stopAfterArrivals ? "stop-after-arrivals"
                        : atStop ? "stop-address"
                        : model.trace.instructions >= startInstruction + step.max_instructions
                            ? "instruction-budget" : "incomplete";
                    boolean passed = result.fault == null
                        && !"incomplete".equals(termination) && checks.passed;
                    allPassed &= passed;
                    finalTermination = termination;

                    JsonObject row = new JsonObject();
                    row.addProperty("name", step.name);
                    row.addProperty("start", restored ? "restore" : "checkpoint");
                    row.addProperty("start_instruction", startInstruction);
                    row.addProperty("instruction_count",
                        model.trace.instructions - startInstruction);
                    if (jit != null) {
                        row.addProperty("jit_compiled_instructions", jit.compiledInstructions - compiledAtStart);
                        row.addProperty("jit_idle_instructions", jit.idleInstructions - idleAtStart);
                        row.addProperty("jit_template_instructions", jit.templateInstructions - templateAtStart);
                    }
                    row.addProperty("final_pc", hex32(finalPc));
                    row.addProperty("termination_reason", termination);
                    row.addProperty("restore_nanoseconds", pendingRestoreNanoseconds);
                    row.addProperty("execution_nanoseconds", trialNanoseconds);
                    if (trialNanoseconds > 0) {
                        row.addProperty("instructions_per_second",
                            (model.trace.instructions - startInstruction) * 1_000_000_000.0
                                / trialNanoseconds);
                    }
                    row.addProperty("passed", passed);
                    if (eventKinds == null) row.addProperty("capture_rows", captureRows);
                    else {
                        row.add("capture_event_kinds", GSON.toJsonTree(eventKinds));
                        row.add("event_kind_counts", eventKindCounts);
                    }
                    if (result.fault != null) row.add("fault", result.fault.toJson());
                    if (result.halt != null) row.addProperty("halt", result.halt.operation);
                    row.add("checks", checks.rows);
                    row.add("register_rows", registerRows.capture(thread));
                    JsonArray arrivalRows = new JsonArray();
                    for (StopArrival requested : step.stop_after_arrivals) {
                        long address = parseUnsigned(requested.address);
                        JsonObject arrival = new JsonObject();
                        arrival.addProperty("address", hex32(address));
                        arrival.addProperty("count", requested.count);
                        arrival.addProperty(
                            "arrivals", result.arrivalCounts.getOrDefault(address, 0L));
                        arrivalRows.add(arrival);
                    }
                    row.add("stop_after_arrivals", arrivalRows);
                    if (model.trace.instructionTraceEnabled)
                        row.add("instruction_trace", com.google.gson.JsonNull.INSTANCE);
                    row.add("compare_operands", com.google.gson.JsonNull.INSTANCE);
                    row.add("input_derived_table_indices", com.google.gson.JsonNull.INSTANCE);
                    trialRows.add(row);
                    restored = false;
                    pendingRestoreNanoseconds = 0;
                    long finished = System.nanoTime();
                    row.addProperty("step_wall_nanoseconds", finished - segmentStarted);
                    segmentStarted = finished;
                    break;
                }
                default:
                    throw new IllegalArgumentException("unsupported scenario step " + step.kind);
            }
            if (step.name != null
                    && step.name.equals(scenario.instruction_trace_start_step))
                model.trace.startInstructionRecording();
        }

        JsonObject report = new JsonObject();
        report.add("checkpoints", checkpointRows);
        report.add("trials", trialRows);
        report.addProperty("all_trials_passed", allPassed);
        report.add("uncaptured_components", new JsonArray());
        return new StepBatchResult(report, allPassed, finalTermination);
    }

    private JsonArray writeSnapshotOutputs(
            Model model, PcodeThread<byte[]> thread, Scenario scenario) throws Exception {
        JsonArray rows = new JsonArray();
        for (SnapshotOutput output : scenario.snapshot_outputs) {
            long address = parseUnsigned(output.address);
            byte[] value = model.memory(thread, address, output.size);
            Path path = Path.of(output.path);
            Path parent = path.getParent();
            if (parent != null) Files.createDirectories(parent);
            Files.write(path, value);
            JsonObject row = new JsonObject();
            row.addProperty("path", path.toString());
            row.addProperty("address", hex32(address));
            row.addProperty("size", value.length);
            row.addProperty("sha256", sha256(value));
            row.addProperty("evidence", output.evidence);
            rows.add(row);
        }
        return rows;
    }


    private JsonObject executeScenario(
            RunContract contract, SleighLanguage language, Scenario scenario,
            byte[] codeflash, byte[] dataflash, Trace trace, Model model,
            Callbacks callbacks, PcodeMachine<byte[]> emulator) throws Exception {
        model.attach(emulator);
        if (scenario.instruction_trace_start_step != null)
            trace.deferInstructionRecording();
        if (scenario.icus_startup_stub != null)
            model.icusStartupStub = model.new IcusStartupStub(scenario.icus_startup_stub);
        model.dma.masterRewriteAssumption = scenario.dma_master_rewrite_assumption;
        model.resetReplay = scenario.reset_replay;
            if (model.resetReplay != null)
                for (ExternalEvent input : model.resetReplay.events) input.replayedAfterReset = true;
        PcodeThread<byte[]> thread = emulator.newThread("PE1");
        model.executionThread = thread;
        model.initializeProcessorReset(thread);
        model.bindMpu(thread);
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

        model.configureExternalEvents(thread, scenario.events, 0, Model.EventOrigin.SCENARIO);
        if (scenario.event_socket != null)
            model.eventSocket = model.new EventSocket(scenario.event_socket, thread);
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
        StepBatchResult batch = null;
        try {
            if (scenario.steps.isEmpty()) {
                ExecutionResult result =
                    runUntil(model, thread, scenario.max_instructions, stops);
                fault = result.fault;
                halt = result.halt;
            }
            else {
                batch = executeSteps(model, callbacks, thread, language, scenario);
            }
        }
        finally {
            if (model.eventSocket != null) model.eventSocket.close();
        }

        JsonObject report = reportBase(contract, scenario, trace, resolved.proof);
        if (thread instanceof P1MEJitMachine.MachineThread jit) {
            report.addProperty("jit_compiled_instructions", jit.compiledInstructions);
            report.addProperty("jit_idle_instructions", jit.idleInstructions);
            report.addProperty("jit_template_instructions", jit.templateInstructions);
            report.addProperty("jit_native_proof", jit.nativeDiagnostic());
        }
        long finalPc = thread.getCounter().getOffset();
        report.addProperty("final_pc", hex32(finalPc));
        if (fault != null) report.add("fault", fault.toJson());
        if (halt != null) report.addProperty("halt", halt.operation);
        if (batch != null) report.add("checkpointing", batch.report);
        if (batch == null) flushPeripheralSnapshots(model);
        report.add("snapshot_outputs", writeSnapshotOutputs(model, thread, scenario));

        CheckResults checks = evaluateChecks(model, thread, language, scenario.checks);
        report.add("checks", checks.rows);
        boolean passed;
        String termination;
        if (scenario.expected_fault != null) {
            ExpectedFault expected = scenario.expected_fault;
            boolean expectedFault = fault != null
                && (expected.kind == null || expected.kind.equals(fault.kind))
                && (expected.address == null || parseUnsigned(expected.address) == fault.address)
                && (expected.access == null || expected.access.equals(fault.access));
            passed = expectedFault && checks.passed;
            termination = expectedFault ? "expected-fault"
                : fault != null ? "unexpected-fault" : "missing-expected-fault";
        }
        else {
            boolean atStop = stops.contains(finalPc);
            boolean completed = batch != null || halt != null || atStop;
            termination = fault != null ? "unexpected-fault"
                : batch != null ? batch.finalTermination
                : halt != null ? "halt"
                : atStop ? "stop-address"
                : trace.instructions >= scenario.max_instructions ? "instruction-budget"
                : "incomplete";
            boolean expectedTermination = scenario.expected_termination == null
                ? completed : scenario.expected_termination.equals(termination);
            passed = fault == null && expectedTermination && checks.passed
                && (batch == null || batch.passed);
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
            "icus_startup_stub", "dma_master_rewrite_assumption", "source", "steps",
            "compare_operands", "input_derived_table_indices", "reset_replay",
            "event_socket", "snapshot_outputs", "engine", "instruction_trace_start_step"),
            "scenario");
        if (scenarioJson.has("engine") &&
                !Set.of("plain", "jit").contains(scenarioJson.get("engine").getAsString()))
            throw new IllegalArgumentException("scenario engine must be plain or jit");
        JsonElement source = scenarioJson.get("source");
        if (source != null && !source.isJsonObject())
            throw new IllegalArgumentException("scenario source must be an object");
        JsonArray steps = scenarioJson.getAsJsonArray("steps");
        JsonElement traceStart = scenarioJson.get("instruction_trace_start_step");
        String traceStartStep = null;
        if (traceStart != null) {
            if (traceStart.isJsonNull() || !traceStart.isJsonPrimitive()
                    || !traceStart.getAsJsonPrimitive().isString()
                    || traceStart.getAsString().isBlank())
                throw new IllegalArgumentException(
                    "scenario instruction_trace_start_step must be a nonempty step name");
            traceStartStep = traceStart.getAsString();
        }
        JsonElement eventSocket = scenarioJson.get("event_socket");
        if (eventSocket != null && !eventSocket.isJsonNull()) {
            requireKeys(
                eventSocket.getAsJsonObject(),
                Set.of("host", "port", "ready_address", "ready_after_arrivals", "hold_when_ready"),
                "event_socket");
            if (steps.size() != 0)
                throw new IllegalArgumentException("event_socket does not compose with steps");
        }
        int traceStartMatches = 0;
        for (JsonElement element : steps) {
            JsonObject step = element.getAsJsonObject();
            String kind = step.get("kind").getAsString();
            switch (kind) {
                case "checkpoint":
                    requireKeys(step, Set.of("kind", "name", "after_instructions"),
                        "checkpoint step");
                    break;
                case "restore":
                    requireKeys(step, Set.of("kind", "checkpoint"), "restore step");
                    break;
                case "trial": {
                    requireKeys(step, Set.of("kind", "name", "max_instructions",
                        "stop_addresses", "stop_after_arrivals", "events", "checks",
                        "capture_rows", "capture_event_kinds"), "trial step");
                    JsonElement eventKinds = step.get("capture_event_kinds");
                    if (eventKinds != null) {
                        if (step.has("capture_rows"))
                            throw new IllegalArgumentException(
                                "trial capture_event_kinds and capture_rows are mutually exclusive");
                        if (!eventKinds.isJsonArray())
                            throw new IllegalArgumentException(
                                "trial capture_event_kinds must be a list");
                        Set<String> seen = new HashSet<>();
                        for (JsonElement selected : eventKinds.getAsJsonArray()) {
                            if (!selected.isJsonPrimitive()
                                    || !selected.getAsJsonPrimitive().isString()
                                    || selected.getAsString().isEmpty()
                                    || !seen.add(selected.getAsString()))
                                throw new IllegalArgumentException(
                                    "trial capture_event_kinds must contain unique nonempty strings");
                        }
                    }
                    break;
                }
                default:
                    throw new IllegalArgumentException("unsupported scenario step: " + kind);
            }
            if (traceStartStep != null && step.has("name")
                    && traceStartStep.equals(step.get("name").getAsString()))
                traceStartMatches++;
        }
        if (traceStartStep != null && traceStartMatches != 1)
            throw new IllegalArgumentException(
                "scenario instruction_trace_start_step must name exactly one checkpoint or trial step");
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

    private static final class ScenarioReportOutput {
        String report;
        String instruction_spool;
        String drcov_path;
    }

    private static final class ReportFile implements Closeable {
        final FileChannel channel;
        final BufferedWriter output;
        final JsonWriter writer;

        ReportFile(Path path) throws IOException {
            channel = FileChannel.open(path, StandardOpenOption.WRITE, StandardOpenOption.CREATE,
                StandardOpenOption.TRUNCATE_EXISTING);
            output = new BufferedWriter(Channels.newWriter(channel, StandardCharsets.UTF_8), 65536);
            writer = new JsonWriter(output);
        }

        void finish() throws IOException {
            writer.flush();
            output.write('\n');
        }

        @Override
        public void close() throws IOException {
            writer.close();
        }
    }

    private void writeObservationField(JsonWriter writer, FileChannel output, Trace trace,
            int trial, Map.Entry<String, JsonElement> field) throws Exception {
        writer.name(field.getKey());
        switch (field.getKey()) {
            case "compare_operands" -> trace.writeCompareOperands(writer, output, trial);
            case "input_derived_table_indices" -> trace.writeTableIndices(writer, output, trial);
            case "instruction_trace" -> trace.writeInstructionTrace(writer, trial);
            default -> GSON.toJson(field.getValue(), writer);
        }
    }

    private void writeCheckpointReport(JsonWriter writer, FileChannel output,
            JsonObject checkpointing, Trace trace) throws Exception {
        writer.beginObject();
        for (var field : checkpointing.entrySet()) {
            writer.name(field.getKey());
            if (!"trials".equals(field.getKey())) {
                GSON.toJson(field.getValue(), writer);
                continue;
            }
            writer.beginArray();
            int index = 0;
            for (JsonElement trial : field.getValue().getAsJsonArray()) {
                writer.beginObject();
                for (var item : trial.getAsJsonObject().entrySet())
                    writeObservationField(writer, output, trace, index, item);
                writer.name("memory_rows");
                trace.memoryAccesses.writeTo(writer, output, index);
                writer.name("event_rows");
                trace.deviceEvents.writeTo(writer, output, index++);
                writer.endObject();
            }
            writer.endArray();
        }
        writer.endObject();
    }

    private void writeScenarioReport(JsonWriter writer, FileChannel output, JsonObject report,
            Scenario scenario, Trace trace, String drcovPath) throws Exception {
        writer.beginObject();
        for (var field : report.entrySet()) {
            if ("checkpointing".equals(field.getKey())) {
                writer.name(field.getKey());
                writeCheckpointReport(writer, output, field.getValue().getAsJsonObject(), trace);
            }
            else if ("resolved_run_contract".equals(field.getKey())) {
                writer.name(field.getKey()).beginObject();
                for (var entry : field.getValue().getAsJsonObject().entrySet())
                    GSON.toJson(entry.getValue(), writer.name(entry.getKey()));
                GSON.toJson(scenario.events, List.class, writer.name("events"));
                GSON.toJson(scenario.steps, List.class, writer.name("steps"));
                writer.endObject();
            }
            else writeObservationField(writer, output, trace, -1, field);
        }
        if (!isRunnerError(report)) {
            writer.name("memory_accesses");
            trace.memoryAccesses.writeTo(writer, output, -1);
            writer.name("device_events");
            trace.deviceEvents.writeTo(writer, output, -1);
            if (trace.instructionTraceEnabled) {
                writer.name("instruction_trace_shortcuts");
                GSON.toJson(trace.instructionShortcuts, List.class, writer);
                writer.name("instruction_trace");
                trace.writeInstructionTrace(writer, -1);
            }
        }
        if (drcovPath != null) writer.name("drcov_path").value(drcovPath);
        writer.endObject();
    }

    private static boolean isRunnerError(JsonObject report) {
        return "runner-error".equals(report.get("termination_reason").getAsString());
    }

    private void writeInstructionSpool(Path path, Trace trace) throws IOException {
        // Feed Python's drcov writer without decoding the JSON instruction trace.
        trace.instructionRows.writeCompact(path);
    }

    private void writeVerdict(JsonWriter writer, JsonObject report, boolean passed,
            ScenarioReportOutput paths) throws IOException {
        writer.beginObject();
        writer.name("passed").value(passed);
        writer.name("report_path").value(paths.report);
        if (paths.drcov_path != null) writer.name("drcov_path").value(paths.drcov_path);
        if (!passed) {
            for (String key : List.of("scenario", "termination_reason", "error", "fault", "recent_pcs")) {
                if (report.has(key)) GSON.toJson(report.get(key), writer.name(key));
            }
            if (report.has("checks")) {
                for (JsonElement row : report.getAsJsonArray("checks")) {
                    if (!row.getAsJsonObject().get("passed").getAsBoolean()) {
                        writer.name("checks").beginArray();
                        GSON.toJson(row, writer);
                        writer.endArray();
                        break;
                    }
                }
            }
        }
        writer.endObject();
    }


    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String usage = "expected contract JSON and report JSON paths [--instruction-trace]"
            + " [--report-outputs <staging-plan-json>]";
        if (args.length < 2) throw new IllegalArgumentException(usage);
        boolean instructionTraceEnabled = false;
        Path reportOutputsPath = null;
        for (int i = 2; i < args.length; i++) {
            if ("--instruction-trace".equals(args[i]) && !instructionTraceEnabled)
                instructionTraceEnabled = true;
            else if ("--report-outputs".equals(args[i]) && reportOutputsPath == null
                    && i + 1 < args.length)
                reportOutputsPath = Path.of(args[++i]);
            else throw new IllegalArgumentException(usage);
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
        ScenarioReportOutput[] reportOutputs = null;
        if (reportOutputsPath != null) {
            reportOutputs = GSON.fromJson(Files.readString(reportOutputsPath), ScenarioReportOutput[].class);
            if (reportOutputs == null || reportOutputs.length != contract.scenarios.size())
                throw new IllegalArgumentException("staging plan report count drifted");
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

        if (currentProgram == null) {
            throw new IllegalStateException("P1M-E machine requires the target program");
        }
        SleighLanguage language = (SleighLanguage) currentProgram.getLanguage();
        if (!language.getLanguageID().getIdAsString().equals(contract.target.processor)) {
            throw new IllegalArgumentException("processor mismatch: " + language.getLanguageID());
        }
        byte[] codeflash = loadImage(contract.target.codeflash, "CodeFlash");
        byte[] dataflash = contract.target.dataflash == null
            ? null : loadImage(contract.target.dataflash, "DataFlash");
        Runtime runtime = Runtime.getRuntime();

        boolean passed = true;
        Files.createDirectories(reportPath.getParent());
        Path partialReport = Files.createTempFile(reportPath.getParent(), ".p1me-batch-", ".json");
        try {
            try (ReportFile batch = new ReportFile(partialReport)) {
                JsonWriter writer = batch.writer;
                if (reportOutputs == null) writer.setIndent("  ");
                writer.beginObject();
                writer.name("schema").value(reportOutputs == null
                    ? "rh850-p1me-machine-batch-report-v1"
                    : "rh850-p1me-machine-report-manifest-v1");
                writer.name("target").value(contract.target.name);
                writer.name("mcu").value(contract.target.mcu);
                writer.name("reports").beginArray();
                for (int index = 0; index < contract.scenarios.size(); index++) {
                    Scenario scenario = contract.scenarios.get(index);
                    monitor.checkCancelled();
                    try (Trace trace = new Trace(instructionTraceEnabled, reportPath.getParent())) {
                        JsonObject report;
                        long heapAtScenarioStart =
                            runtime.totalMemory() - runtime.freeMemory();
                        try {
                            report = runScenario(
                                contract, machineSpec, language, scenario, codeflash, dataflash, trace);
                        }
                        catch (CancelledException exc) {
                            throw exc;
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
                        finishHeapRelease(report, heapAtScenarioStart);
                        addSymbolCacheProbe(report);
                        boolean scenarioPassed = report.get("passed").getAsBoolean();
                        passed &= scenarioPassed;
                        if (reportOutputs == null) {
                            writeScenarioReport(writer, batch.channel, report, scenario, trace, null);
                        }
                        else {
                            ScenarioReportOutput paths = reportOutputs[index];
                            Path finalReport = Path.of(paths.report);
                            Path reportParent = finalReport.toAbsolutePath().getParent();
                            Files.createDirectories(reportParent);
                            Path stagedPath = Files.createTempFile(
                                reportParent, ".p1me-trial-", ".json");
                            try {
                                try (ReportFile staged = new ReportFile(stagedPath)) {
                                    writeScenarioReport(staged.writer, staged.channel, report,
                                        scenario, trace, paths.drcov_path);
                                    staged.finish();
                                }
                                Files.move(stagedPath, finalReport,
                                    java.nio.file.StandardCopyOption.REPLACE_EXISTING);
                            } finally {
                                Files.deleteIfExists(stagedPath);
                            }
                            if (paths.instruction_spool != null) {
                                writeInstructionSpool(Path.of(paths.instruction_spool), trace);
                            }
                            writeVerdict(writer, report, scenarioPassed, paths);
                        }
                    }
                    // Report serialization can allocate after finishHeapRelease, and the trace
                    // itself remains reachable until this point. Collect only under real pressure,
                    // after both the emulator and every per-scenario spool have been released.
                    if (runtime.totalMemory() - runtime.freeMemory() >= runtime.maxMemory() / 2)
                        System.gc();
                }
                writer.endArray();
                writer.name("passed").value(passed);
                writer.endObject();
                batch.finish();
            }
            Files.move(partialReport, reportPath, java.nio.file.StandardCopyOption.REPLACE_EXISTING);
        }
        finally {
            Files.deleteIfExists(partialReport);
        }
        println("P1ME_MACHINE_REPORT=" + reportPath);
        println("P1ME_MACHINE_RESULT=" + (passed ? "PASS" : "FAIL"));
        if (!passed) throw new IllegalStateException("P1M-E machine batch failed; see " + reportPath);
    }
}
