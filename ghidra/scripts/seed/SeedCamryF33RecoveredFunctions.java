//@author kaikozlov
//@category Seed
// Seed exact-F33 entries and apply target-native, execution-backed semantic types.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.data.*;
import ghidra.program.model.symbol.SourceType;
import java.io.*;
public class SeedCamryF33RecoveredFunctions extends GhidraScript {
  private void ensure(long v) throws Exception { Address a=toAddr(v); Listing l=currentProgram.getListing(); Instruction c=l.getInstructionContaining(a); if(c!=null&&!c.getMinAddress().equals(a)) l.clearCodeUnits(c.getMinAddress(),c.getMaxAddress(),false); CodeUnit u=l.getCodeUnitContaining(a); if(u!=null&&!(u instanceof Instruction)) l.clearCodeUnits(u.getMinAddress(),u.getMaxAddress(),false); if(l.getInstructionAt(a)==null&&!disassemble(a)) throw new IllegalStateException("disassembly failed "+a); Function f=currentProgram.getFunctionManager().getFunctionAt(a); if(f==null) f=createFunction(a,null); if(f==null) throw new IllegalStateException("function creation failed "+a); }
  private void annotateMemoryPrimitives() throws Exception {
    DataType pointer = new PointerDataType(VoidDataType.dataType, 4);
    Function copy = getFunctionAt(toAddr(0x89F2EL));
    Function zero = getFunctionAt(toAddr(0x8A134L));
    if (copy == null || zero == null) {
      throw new IllegalStateException("missing exact-F33 memory primitives");
    }
    copy.setName("f33_memcpy_forward", SourceType.USER_DEFINED);
    copy.setReturnType(pointer, SourceType.USER_DEFINED);
    copy.replaceParameters(Function.FunctionUpdateType.DYNAMIC_STORAGE_FORMAL_PARAMS,
        true, SourceType.USER_DEFINED,
        new ParameterImpl("destination", pointer, currentProgram),
        new ParameterImpl("source", pointer, currentProgram),
        new ParameterImpl("byte_count", UnsignedIntegerDataType.dataType, currentProgram));
    copy.setComment("Forward byte-counted copy; returns the original destination. "
        + "Uses word transfers only when both pointers are four-byte aligned, "
        + "otherwise byte transfers. Not an overlap-safe memmove contract. "
        + "Exact CodeFlash execution covers zero length, alignment combinations, "
        + "bulk/tail boundaries, source preservation and destination canaries.");
    zero.setName("f33_memzero", SourceType.USER_DEFINED);
    zero.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
    zero.replaceParameters(Function.FunctionUpdateType.DYNAMIC_STORAGE_FORMAL_PARAMS,
        true, SourceType.USER_DEFINED,
        new ParameterImpl("destination", pointer, currentProgram),
        new ParameterImpl("byte_count", UnsignedIntegerDataType.dataType, currentProgram));
    zero.setComment("Zero exactly byte_count bytes. For counts above three, "
        + "byte-align the destination before word stores; use 128/64/32/16-byte "
        + "blocks then word/byte tails. Zero count performs no destination write. "
        + "Exact CodeFlash execution checks all alignments and bulk/tail boundaries.");
  }
  private void annotateBootAndFreshness() throws Exception {
    Function relocate = getFunctionAt(toAddr(0x35E4L));
    Function commit = getFunctionAt(toAddr(0x90D6AL));
    if (relocate == null || commit == null) {
      throw new IllegalStateException("missing exact-F33 relocation/freshness functions");
    }
    relocate.setName("f33_boot_copy_flash_driver_to_ram", SourceType.USER_DEFINED);
    relocate.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
    relocate.replaceParameters(Function.FunctionUpdateType.DYNAMIC_STORAGE_FORMAL_PARAMS,
        true, SourceType.USER_DEFINED);
    relocate.setComment("Boot-phase relocation: copies 0xCB words from CodeFlash "
        + "0x8370..0x869B into RAM 0xFEBF1000..0xFEBF132B, reads the last word "
        + "back, then executes SYNCM and SYNCI. Exact CodeFlash execution checks "
        + "the complete copied span and both canaries. The callback at "
        + "0xFEBF12B8 corresponds to ROM 0x8628 in this phase; application "
        + "crypto subsequently reuses the same RAM. This is not permanent RAM code.");
    commit.setName("f33_freshness_commit_pending", SourceType.USER_DEFINED);
    commit.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
    commit.replaceParameters(Function.FunctionUpdateType.DYNAMIC_STORAGE_FORMAL_PARAMS,
        true, SourceType.USER_DEFINED,
        new ParameterImpl("slot", UnsignedShortDataType.dataType, currentProgram),
        new ParameterImpl("verification_result", ByteDataType.dataType, currentProgram));
    commit.setComment("For unsigned slot < 2 and low-byte verification_result == 1, "
        + "copy 12 bytes from 0xFEBE55F4 + slot*12 (pending) to "
        + "0xFEBE55DC + slot*12 (committed), inside the ordinary critical section. "
        + "Other inputs perform no history copy. This is pending-to-committed, "
        + "not rollback, and does not dequeue a secured PDU. Exact CodeFlash "
        + "execution checks both slots, rejected inputs, and low-byte truncation.");
  }
  private Function semanticFunction(long entry, String name, DataType result,
      Parameter... parameters) throws Exception {
    Function function = getFunctionAt(toAddr(entry));
    if (function == null) throw new IllegalStateException("missing exact-F33 function " + toAddr(entry));
    function.setName(name, SourceType.USER_DEFINED);
    function.setReturnType(result, SourceType.USER_DEFINED);
    function.replaceParameters(Function.FunctionUpdateType.DYNAMIC_STORAGE_FORMAL_PARAMS,
        true, SourceType.USER_DEFINED, parameters);
    return function;
  }
  private DataType resolve(StructureDataType draft) {
    return currentProgram.getDataTypeManager().addDataType(
        draft, DataTypeConflictHandler.REPLACE_HANDLER);
  }
  private void annotateFreshnessLayouts() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    StructureDataType slot = new StructureDataType(category, "F33FreshnessSlot", 0);
    slot.setPackingEnabled(true);
    slot.add(u16, "selector", "Zero in the ordinary wrapper; OEM field name not recovered.");
    slot.add(ShortDataType.dataType, "slot", "Signed index; the ordinary wrapper admits 0 or 1.");
    DataType slotPointer = new PointerDataType(resolve(slot), 4);

    StructureDataType wire = new StructureDataType(category, "F33FreshnessWire", 0);
    wire.setPackingEnabled(true);
    wire.add(u32, "trip", "16 wire bits in full format; zero in truncated format.");
    wire.add(u32, "reset", "20 wire bits in full format; zero in truncated format.");
    wire.add(u16, "message", "8 wire bits in full format, 2 in truncated format.");
    wire.add(u8, "reset_low2", "Two received reset-low bits.");
    wire.add(u8, "bit_length", "4 or 46 bits; this is not a byte count.");
    DataType wirePointer = new PointerDataType(resolve(wire), 4);

    StructureDataType history = new StructureDataType(category, "F33FreshnessHistory", 0);
    history.setPackingEnabled(true);
    history.add(u32, "trip", "Reconstructed trip counter.");
    history.add(u32, "reset", "Reconstructed reset counter.");
    history.add(u16, "message", "Reconstructed message; 0xFF is the outer wrapper's sentinel.");
    history.add(new ArrayDataType(u8, 2, 1), "opaque_0a",
        "Not written by reconstruction; copied by the 12-byte commit. Not wire flags.");
    DataType historyPointer = new PointerDataType(resolve(history), 4);

    StructureDataType search = new StructureDataType(category, "F33FreshnessSearch", 0);
    search.setPackingEnabled(true);
    search.add(u32, "message_bit_width", "Derived from parsed bit_length, capped at eight.");
    search.add(u32, "reset_low_bit_width", "Two for supported formats; bit_length 0 or 1 is retained.");
    search.add(u32, "reset_candidate", "Selected reset; unspecified when search fails.");
    search.add(u16, "skip_matches", "Matching candidates to skip, not updated in place.");
    search.add(u16, "candidate_index", "0..4: current,-1,+1,-2,+2; 5 means exhausted.");
    search.add(u8, "advance_message", "One requests the next message congruence interval.");
    search.add(new ArrayDataType(u8, 3, 1), "opaque_11", "No recovered field semantics.");
    DataType searchPointer = new PointerDataType(resolve(search), 4);
    DataType bytes = new PointerDataType(u8, 4);
    DataType bitCapacity = new PointerDataType(u32, 4);

    semanticFunction(0x90566L, "f33_freshness_encode_wire", VoidDataType.dataType,
        new ParameterImpl("freshness", wirePointer, currentProgram),
        new ParameterImpl("wire", bytes, currentProgram),
        new ParameterImpl("bit_capacity", bitCapacity, currentProgram))
        .setComment("Encode 4 bits into one high-nibble byte, or 46 bits into six "
            + "MSB-first bytes. Admission compares only the low byte of *bit_capacity. "
            + "Insufficient capacity leaves both output and capacity unchanged; "
            + "unsupported format writes capacity zero without writing wire bytes. "
            + "Supported output reports the encoded bit length; unused low wire bits are zero.");
    semanticFunction(0x90736L, "f33_freshness_decode_wire", VoidDataType.dataType,
        new ParameterImpl("wire", bytes, currentProgram),
        new ParameterImpl("bit_length", u32, currentProgram),
        new ParameterImpl("freshness", wirePointer, currentProgram))
        .setComment("Accept exact bit lengths 4 and 46, reading one and six bytes "
            + "respectively. Decode into the 12-byte F33FreshnessWire layout. "
            + "Unsupported lengths zero the entire output without reading wire. "
            + "Truncated low nibble and full-format low two wire bits are ignored.");
    Function selectReset = semanticFunction(0x909CAL, "f33_freshness_select_reset_candidate", u32,
        new ParameterImpl("unused_slot", slotPointer, currentProgram),
        new ParameterImpl("received", wirePointer, currentProgram),
        new ParameterImpl("search", searchPointer, currentProgram));
    selectReset.setInline(true);
    selectReset.setComment("Reload current reset FEBE55C4 on each attempt; search current, "
        + "-1,+1,-2,+2 without crossing 0..0xFFFFF. Match the configured low-bit "
        + "mask and skip the requested number of matches. Return 1 for a selected "
        + "candidate, 0 when exhausted. With two low bits, -2 and +2 can both "
        + "match; skip_matches selects between them. Candidate value is not valid on failure. "
        + "Inline the real p-code: 909CA..90A47 preserves r6-r9, and the sole caller "
        + "at 90B76 forwards them to 90A48 at 90B7E without reloading. The generic "
        + "caller-saved ABI would otherwise invent undefined arguments. This does "
        + "not change the ordinary calling convention or replace the function's effects.");
    semanticFunction(0x90A48L, "f33_freshness_reconstruct_ordinary", u32,
        new ParameterImpl("slot", slotPointer, currentProgram),
        new ParameterImpl("received", wirePointer, currentProgram),
        new ParameterImpl("search", searchPointer, currentProgram),
        new ParameterImpl("reconstructed", historyPointer, currentProgram))
        .setComment("Read trip FEBE55C0, then snapshot the selected committed history "
            + "inside the ordinary critical section. A newer trip/reset seeds message "
            + "from received low bits; no fixed first-in-epoch 0/1 rule exists. "
            + "Same epoch rebuilds message congruence, optionally advancing one interval. "
            + "Reset ceiling or message advance overflow yields message 0xFF with return 0; "
            + "the outer wrapper interprets that sentinel. Older epochs return 0x23 "
            + "while candidate_index < 4, otherwise 0x22, without writing output. "
            + "Successful reconstruction writes ten bytes and preserves the opaque tail.");
    semanticFunction(0x90B1CL, "f33_freshness_reconstruct_candidate", u32,
        new ParameterImpl("slot", slotPointer, currentProgram),
        new ParameterImpl("received", wirePointer, currentProgram),
        new ParameterImpl("skip_matches", u16, currentProgram),
        new ParameterImpl("reconstructed", historyPointer, currentProgram))
        .setComment("Compose reset candidate selection and ordinary message reconstruction. "
            + "Derive message width from received bit_length (minus two, clamped to 0..8); "
            + "reset-low width is two except bit_length 0 or 1 is retained. This helper "
            + "does not independently reject unsupported formats. Advance when received "
            + "low bits do not exceed committed low bits. "
            + "No reset candidate returns 0x22 without writing output. The matching ordinal "
            + "can move an ambiguous -2 candidate returning 0x23 to the admissible +2 candidate. "
            + "The fourth argument is the output pointer in r9; it is not an implicit global.");
  }
  private void semanticData(long entry, DataType type, String name, String comment)
      throws Exception {
    Address start = toAddr(entry);
    Listing listing = currentProgram.getListing();
    Data existing = listing.getDefinedDataAt(start);
    if (existing == null || existing.getLength() != type.getLength()
        || !existing.getDataType().isEquivalent(type)) {
      listing.clearCodeUnits(start, start.add(type.getLength() - 1L), false);
      createData(start, type);
    }
    createLabel(start, name, true);
    listing.setComment(start, CodeUnit.PLATE_COMMENT, comment);
  }
  private void annotateBootDispatchAndCurves() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType s16 = ShortDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    StructureDataType point = new StructureDataType(category, "F33CurvePointS16U16", 0);
    point.setPackingEnabled(true);
    point.add(s16, "x", "Signed comparison axis; physical units not recovered.");
    point.add(u16, "y", "Unsigned ordinate; physical units not recovered.");
    DataType pointType = resolve(point);
    StructureDataType curve = new StructureDataType(category, "F33Curve16", 0);
    curve.setPackingEnabled(true);
    curve.add(new ArrayDataType(pointType, 16, 4), "points",
        "Sixteen points consumed by C29B2. Point 15 supplies the upper clamp.");
    curve.add(Undefined4DataType.dataType, "opaque_40",
        "Four-byte row tail; not read by C29B2. Row stride is 0x44.");
    DataType curveType = resolve(curve);
    DataType rows = new ArrayDataType(curveType, 2, 0x44);
    semanticData(0x18100L, rows, "f33_curve_bank0_initial_rows",
        "First two rows selected by C28AE/C28FC through B144C when "
        + "(byte FEBEAC3C & 1) == 0. The x value 101 at 18108 was "
        + "misclassified as JMP TP code, creating a false reference to 869C.");
    semanticData(0x10100L, rows, "f33_curve_bank1_initial_rows",
        "Alternate first two rows, selected through B1450 when "
        + "(byte FEBEAC3C & 1) == 1. This is a CodeFlash calibration selection, "
        + "not an image-address offset.");
    semanticData(0xB144CL,
        new ArrayDataType(new PointerDataType(UnsignedCharDataType.dataType, 4), 2, 4),
        "f33_calibration_bank_bases",
        "Byte-addressed bases 18100 and 10100, indexed by FEBEAC3C & 1. "
        + "Consumers use several table formats; the whole banks are not F33Curve16 arrays.");
    semanticFunction(0xC29B2L, "f33_curve16_interpolate_with_slope", u32,
        new ParameterImpl("curve", new PointerDataType(curveType, 4), currentProgram),
        new ParameterImpl("x", s16, currentProgram),
        new ParameterImpl("slope_q9", new PointerDataType(s16, 4), currentProgram))
        .setComment("Fixed decision tree selects among sixteen signed-x/unsigned-y points. "
            + "At or above x[15], return y[15]; below x[0], extrapolate segment zero "
            + "rather than clamp. Otherwise interpolate and retain the low sixteen "
            + "result bits; the value denominator is narrowed to signed16. "
            + "The second output blends maxima of adjacent quantized Q8 segment "
            + "slopes, rescales to Q9 and narrows to signed16 without saturation. "
            + "Zero-width slope segments use the signed fallback at AF88C (7800); "
            + "native 32-bit multiplication, shifts and DIVQ govern arithmetic. "
            + "Execution covers every real-row knot, negative extrapolation, upper "
            + "clamping, and duplicate-x slope fallbacks; not every malformed table.");

    FunctionDefinitionDataType callback =
        new FunctionDefinitionDataType(category, "F33BootInterruptCallback");
    callback.setReturnType(VoidDataType.dataType);
    StructureDataType dispatch = new StructureDataType(category, "F33BootInterruptEntry", 0);
    dispatch.setPackingEnabled(true);
    dispatch.add(u32, "eiic", "Exact EIIC match; FFFFFFFF is the terminating default.");
    dispatch.add(new PointerDataType(callback, 4), "handler", "No ordinary C arguments.");
    currentProgram.getFunctionManager().removeFunction(toAddr(0x869CL));
    semanticData(0x869CL, new ArrayDataType(resolve(dispatch), 8, 8),
        "f33_boot_interrupt_dispatch",
        "Consumed by 748 through TP=869C. Seven causes and one FFFFFFFF sentinel. "
        + "The subsequent pair at 86DC is not traversed, even for cause 27F; "
        + "its consumer is not identified. This replaces a false data-as-code function.");
    semanticFunction(0x100L, "f33_boot_eiint_vector", VoidDataType.dataType)
        .setComment("Hardware EIINT entry: SYNCP then branch to 10C. Not a normal C call.");
    semanticFunction(0x10CL, "f33_boot_eiint_context", VoidDataType.dataType)
        .setComment("Save r6, EIPC and EIPSW; read EIIC into r6, enable interrupts, "
            + "save r1..lp and call 748. Restore registers, disable interrupts, "
            + "restore EIPSW/EIPC/r6, then EIRET. Exact execution with FPEC=0 "
            + "and boot state1 preserves all 31 GPRs, restores PSW and clears ISPR. "
            + "This does not establish physical interrupt timing or the pending-FPI path.");
    semanticFunction(0x748L, "f33_boot_dispatch_eiic", VoidDataType.dataType,
        new ParameterImpl("eiic", u32, currentProgram))
        .setComment("Traverse eight-byte records from TP; call the first handler "
            + "whose cause equals eiic or FFFFFFFF. The sentinel terminates the "
            + "search, not the end of the surrounding data region. Executed matches "
            + "1087/10C1 and defaults 27F/FFFFFFFF against the exact image.");
    semanticFunction(0x1E44L, "f33_boot_tauj0_ch2_callback", VoidDataType.dataType)
        .setComment("Dispatch entry for EIIC 1087: TAUJ0 channel2 per P1M-E "
            + "R01UH0585EJ0120 interrupt table, page284. Calls 1CE8, then 1E04, "
            + "then 14A2; state byte FEBF2904 == 2 enters services, state1 returns. "
            + "The full state1 interrupt return was executed without replacing callees.");
  }
  @Override public void run() throws Exception {
    String[] args = getScriptArgs();
    if (args.length != 1) throw new IllegalArgumentException("expected function_seeds.csv path");
    File file = new File(args[0]);
    if (!file.isFile()) throw new IllegalStateException("missing seed file " + file);
    int count = 0;
    try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
      if (!"address,provenance,note".equals(reader.readLine())) {
        throw new IllegalStateException("seed CSV header drift");
      }
      String line;
      while ((line = reader.readLine()) != null) {
        if (line.isBlank()) continue;
        String[] fields = line.split(",", 3);
        if (fields.length != 3 || fields[1].isBlank()) {
          throw new IllegalStateException("invalid seed row: " + line);
        }
        ensure(Long.parseLong(fields[0].replace("0x", ""), 16));
        count++;
      }
    }
    annotateMemoryPrimitives();
    annotateBootAndFreshness();
    annotateFreshnessLayouts();
    annotateBootDispatchAndCurves();
    println("SeedCamryF33RecoveredFunctions: seeded " + count
        + " evidence-backed entries and applied exact-F33 semantic prototypes");
  }
}
