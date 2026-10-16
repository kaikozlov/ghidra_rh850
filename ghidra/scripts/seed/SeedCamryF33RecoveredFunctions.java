//@author kaikozlov
//@category Seed
// Seed exact-F33 entries and apply target-native, execution-backed semantic types.
import ghidra.app.script.GhidraScript;
import ghidra.program.database.SpecExtension;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
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
  private void annotateRedundantStatePrimitives() throws Exception {
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType bytes = new PointerDataType(u8, 4);
    DataType halfwords = new PointerDataType(u16, 4);
    DataType words = new PointerDataType(u32, 4);
    semanticFunction(0x66E2EL, "f33_copy_whole_words", VoidDataType.dataType,
        new ParameterImpl("destination", words, currentProgram),
        new ParameterImpl("source", words, currentProgram),
        new ParameterImpl("byte_count", u16, currentProgram))
        .setComment("Copy floor(low16(byte_count)/4) words forward. Ignore trailing "
            + "bytes; no pointer or alignment validation. Forward overlap propagates "
            + "earlier stores, unlike memmove. No return-value contract.");
    semanticFunction(0x66E50L, "f33_update_whole_words", u32,
        new ParameterImpl("destination", words, currentProgram),
        new ParameterImpl("source", words, currentProgram),
        new ParameterImpl("byte_count", u16, currentProgram))
        .setComment("Same forward whole-word extent as66E2E, but write only differing "
            + "words. Return zero if none differ, otherwise one; the result remains "
            + "one even when a later word already matches. Ignore trailing bytes.");
    semanticFunction(0x701C4L, "f33_priority_mask_enter", u32,
        new ParameterImpl("requested_mask", u32, currentProgram))
        .setComment("Return the previous full PMR. Write requested_mask only when "
            + "signed32(previous PMR) < signed32(requested_mask). Preserve incoming "
            + "PSW.ID around the write; SYNCP follows a write. This is not a bitwise "
            + "mask union or unconditional interrupt disable. Execution seeds "
            + "FPEC=0; pending-FPI and physical interrupt timing remain outside proof.");
    semanticFunction(0x701EAL, "f33_priority_mask_restore", VoidDataType.dataType,
        new ParameterImpl("saved_mask", u32, currentProgram))
        .setComment("Unconditionally write saved_mask to PMR, preserving incoming "
            + "PSW.ID around the write, then SYNCP. No return-value contract. "
            + "Executed with ID both clear and set, FPEC=0; no concurrent interrupt "
            + "or physical timing claim.");
    semanticFunction(0x70736L, "f33_vote_redundant_u8", s32,
        new ParameterImpl("raw", bytes, currentProgram),
        new ParameterImpl("xor55", bytes, currentProgram),
        new ParameterImpl("xorAA", bytes, currentProgram),
        new ParameterImpl("output", bytes, currentProgram))
        .setComment("Reject any NULL pointer or output==raw with -1 and no write. "
            + "Read three bytes under the FFC0 priority-mask pair, then normalize "
            + "the encoded copies with55/AA. All agree: return0 and raw. Raw agrees "
            + "with either encoded copy: return-11 and raw. Only encoded copies "
            + "agree: return-12 and that value. All differ: return-13 but still "
            + "write raw. Output may alias either encoded input; no input repair.");
    semanticFunction(0x66C24L, "f33_read_repair_redundant_u8", u32,
        new ParameterImpl("raw", bytes, currentProgram),
        new ParameterImpl("xor55", bytes, currentProgram),
        new ParameterImpl("xorAA", bytes, currentProgram),
        new ParameterImpl("fallback", u8, currentProgram))
        .setComment("Vote through70736. Status0 returns the agreed value without "
            + "repair; -11/-12 republish the voted value to all three cells. Other "
            + "nonzero statuses republish low8(fallback). The publisher rejects "
            + "NULL pointers without partial stores, so invalid-pointer cases "
            + "return fallback without repair. Final LD.BU zero-extends the byte "
            + "to the full r10 return register.");
    semanticFunction(0x70A0AL, "f33_publish_redundant_u8", s32,
        new ParameterImpl("value", u8, currentProgram),
        new ParameterImpl("raw", bytes, currentProgram),
        new ParameterImpl("xor55", bytes, currentProgram),
        new ParameterImpl("xorAA", bytes, currentProgram))
        .setComment("Any NULL destination returns-1 before all stores. Otherwise "
            + "publish low8(value), value^55, value^AA in that order under the "
            + "FFC0 priority-mask pair and return0. No alias rejection; the three "
            + "stores are not asserted atomic against every interrupt source.");
    semanticFunction(0x70A4EL, "f33_publish_redundant_u16", s32,
        new ParameterImpl("value", u16, currentProgram),
        new ParameterImpl("raw", halfwords, currentProgram),
        new ParameterImpl("xor5555", halfwords, currentProgram),
        new ParameterImpl("xorAAAA", halfwords, currentProgram))
        .setComment("Any NULL destination returns-1 without partial stores. Otherwise "
            + "publish low16(value), value^5555, value^AAAA in that order under the "
            + "FFC0 priority-mask pair and return0. No alias rejection or local "
            + "alignment validation; no claim of global interrupt exclusion.");
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
    semanticFunction(0x3614L, "f33_boot_cache_set_enabled", VoidDataType.dataType,
        new ParameterImpl("enabled", UnsignedCharDataType.dataType, currentProgram))
        .setComment("Low-byte zero disables the data buffer and instruction cache "
            + "before requesting both clears; nonzero clears first, then enables both. "
            + "G3M CDBCR.CDBCLR reads zero; ICCTRL.ICHCLR remains hardware-dependent "
            + "until completion. Final ICCTRL read, SYNCI and return are real code. "
            + "Processor fixtures supply an explicit completion event; no cache "
            + "contents, physical latency or guaranteed completion are inferred.");
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
  private void annotateNvmDescriptors() throws Exception {
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    StructureDataType descriptor =
        new StructureDataType(new CategoryPath("/CamryF33"), "F33NvmDescriptor", 0);
    descriptor.setPackingEnabled(true);
    descriptor.add(u16, "page", "64-byte DataFlash page; descriptor zero contains FFFF.");
    descriptor.add(u16, "payload_bytes", "Unsigned payload length; not the allocation size.");
    descriptor.add(u8, "option", "All registered descriptors contain zero; nonzero changes allocation overhead.");
    descriptor.add(u8, "opaque_05", "No field semantics recovered.");
    int count = currentProgram.getMemory().getShort(toAddr(0x27928L)) & 0xFFFF;
    semanticData(0x27634L, new ArrayDataType(resolve(descriptor), count, 6),
        "f33_nvm_descriptors",
        "Count at27928 is123. Record0 has sentinel pageFFFF; records1..122 include "
        + "multi-page allocations. A length-based table start at27636 wrongly "
        + "pairs each length with the next record's page. No logical copy grouping "
        + "or XOR mask is encoded by a simple handle/3 calculation.");
    semanticData(0x27928L, u16, "f33_nvm_descriptor_count",
        "Unsigned upper bound used by77982 and other record requests.");
    semanticFunction(0x74884L, "f33_nvm_payload_length", u32,
        new ParameterImpl("handle", u16, currentProgram))
        .setComment("Return descriptor payload_bytes, zero-extended to r10. "
            + "No local handle bound check. The field is at27636+6*handle.");
    semanticFunction(0x74892L, "f33_nvm_base_offset", u32,
        new ParameterImpl("handle", u16, currentProgram))
        .setComment("Return descriptor page shifted left six, using27634+6*handle. "
            + "No local bound or sentinel rejection; handle0 returns003FFFC0.");
    semanticFunction(0x748A2L, "f33_nvm_descriptor_option", u32,
        new ParameterImpl("handle", u16, currentProgram))
        .setComment("Return unsigned byte27638+6*handle. The registered123 "
            + "descriptors all contain zero. No local handle bound check.");
    semanticFunction(0x748B0L, "f33_nvm_allocation_pages", u32,
        new ParameterImpl("handle", u16, currentProgram))
        .setComment("Let n=payload length and b=descriptor option. Return "
            + "(n + (n>32 ? 4:0) + (b!=0 ? 12:4) + 64) >> 6. "
            + "This includes record overhead and differs from payload page count. "
            + "Exact execution covers all nine registered length classes. "
            + "This helper and74884/74892/748A2 preserve r7/r8 throughout: "
            + "inline their real p-code so748E4 retains its second and third arguments.");
    getFunctionAt(toAddr(0x74884L)).setInline(true);
    getFunctionAt(toAddr(0x74892L)).setInline(true);
    getFunctionAt(toAddr(0x748A2L)).setInline(true);
    getFunctionAt(toAddr(0x748B0L)).setInline(true);
    semanticFunction(0x748E4L, "f33_nvm_record_offset", u32,
        new ParameterImpl("handle", u16, currentProgram),
        new ParameterImpl("allocation_index", u16, currentProgram),
        new ParameterImpl("byte_offset", u32, currentProgram))
        .setComment("Return base_offset + allocation_index*allocation_pages*64 "
            + "+ byte_offset with native32-bit arithmetic. First two inputs are "
            + "truncated to16 bits. Helpers preserve the forwarded r7/r8 values; "
            + "they are not undefined extra outputs. Executed for all123 "
            + "descriptor indices plus explicit low16 truncation.");
    semanticFunction(0x77314L, "f33_nvm_payload_page_count", u32,
        new ParameterImpl("handle", u16, currentProgram))
        .setComment("For payload length n return (((n + (n & 3)) & FFFF) + 60) >> 6. "
            + "Keep literal narrowing/rounding; do not substitute a generic ceil "
            + "for arbitrary lengths. Registered lengths are multiples of eight. "
            + "A64-byte payload returns1 here but allocation_pages returns2.");
    semanticFunction(0x778FEL, "f33_nvm_trailer_offset", u32,
        new ParameterImpl("handle", u16, currentProgram))
        .setComment("Return allocation_pages*64 - 4. 77AA8 reads the commit marker "
            + "there and comparesAAAAAAAA; the trailer is not always at byte60 "
            + "of the first page. Executed for every registered length class.");
  }
  private void annotateNvmLogicalRequests() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType pointer = new PointerDataType(VoidDataType.dataType, 4);
    StructureDataType descriptor =
        new StructureDataType(category, "F33NvmLogicalDescriptor", 0);
    descriptor.setPackingEnabled(true);
    descriptor.add(u8, "opaque_00", "Not interpreted here.");
    descriptor.add(u8, "queue_key", "73328 reads this byte; normal queue index is3+key. No execution-priority claim.");
    descriptor.add(Undefined2DataType.dataType, "opaque_02", "Not interpreted here.");
    descriptor.add(u8, "buffer_mode", "All 124 registered rows contain1. Selectors use mode4 for scratch storage.");
    descriptor.add(Undefined1DataType.dataType, "opaque_05", "Not interpreted here.");
    descriptor.add(u16, "payload_bytes", "Length passed by the logical read callback.");
    descriptor.add(u16, "storage_handle", "Explicit mapping consumed by73CA4; not implicit handle-minus-one.");
    descriptor.add(Undefined2DataType.dataType, "opaque_0a", "Not interpreted here.");
    descriptor.add(pointer, "default_buffer", "All registered rows containNULL; explicit overrides take precedence.");
    int count = currentProgram.getMemory().getShort(toAddr(0x26C08L)) & 0xFFFF;
    semanticData(0x26C0CL, new ArrayDataType(resolve(descriptor), count, 16),
        "f33_nvm_logical_descriptors",
        "124 logical rows, distinct from123 six-byte physical descriptors at27634. "
        + "Storage mapping: logical0->1,1->FFFE,2->1,...,123->122. "
        + "Do not treat FFFE as an admitted physical handle or infer copy grouping.");
    semanticData(0x26C08L, u16, "f33_nvm_logical_descriptor_count",
        "Logical descriptor count; the leaf selectors do not enforce this bound.");
    StructureDataType request =
        new StructureDataType(category, "F33NvmOperation", 0);
    request.setPackingEnabled(true);
    request.add(u32, "operation", "Published operation selector; admission does not validate it.");
    request.add(u16, "logical_handle", "Logical descriptor index, not the physical storage handle.");
    request.add(Undefined2DataType.dataType, "padding_06", "Not copied or initialized by73ADC/73AB0.");
    request.add(pointer, "buffer_08", "Read operation callback consumes this destination pointer.");
    request.add(pointer, "buffer_0c", "Write operation callback consumes this source pointer.");
    DataType requestType = resolve(request);
    semanticData(0xFEBF6AECL, requestType, "f33_nvm_pending_operation",
        "Single operation record. State byteFEBF6B00==2 rejects a new publication "
        + "before reading its input; this is not a multi-entry queue.");
    semanticData(0xFEBF6AFCL, u16, "f33_nvm_operation_phase",
        "Publication and initialization set1; dispatch consumes this phase.");
    semanticData(0xFEBF6AFEL, u16, "f33_nvm_operation_step",
        "Initialization setsFFFF. Publication leaves this field unchanged.");
    semanticData(0xFEBF6B00L, u8, "f33_nvm_operation_state",
        "Initialization sets0; publication rejects2, otherwise copies the record and sets2.");
    semanticData(0xFEBF6B08L, pointer, "f33_nvm_read_buffer_override",
        "Set by745E4 and consumed by74614; distinct from the write override.");
    semanticData(0xFEBF6B0CL, pointer, "f33_nvm_write_buffer_override",
        "Set by746AA and consumed by746DE.");
    semanticData(0xFEBF6B14L, u8, "f33_nvm_buffer_retry",
        "Cleared by745DA before either override setter; broader retry policy not reconstructed here.");
    semanticFunction(0x73CA4L, "f33_nvm_storage_handle", u32,
        new ParameterImpl("logical_handle", u16, currentProgram))
        .setComment("Return unsigned16 field+8 from26C0C+16*low16(handle), "
            + "zero-extended to r10. No local bound check; r7 is not read. "
            + "All124 rows and high-bit truncation executed against exact CodeFlash.");
    semanticFunction(0x745DAL, "f33_nvm_reset_buffer_retry", VoidDataType.dataType)
        .setComment("Clear byteFEBF6B14; onlyr11 is clobbered. Preserve r6/r7 "
            + "through the real p-code so the override setters retain their inputs.");
    getFunctionAt(toAddr(0x745DAL)).setInline(true);
    semanticFunction(0x745E4L, "f33_nvm_set_read_buffer", VoidDataType.dataType,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("buffer", pointer, currentProgram))
        .setComment("Clear buffer retry, then store buffer atFEBF6B08. "
            + "NULL with descriptor mode2 calls71CE0(handle,0); registered mode1 "
            + "does not take that callback. No local handle bound check.");
    semanticFunction(0x746AAL, "f33_nvm_set_write_buffer", VoidDataType.dataType,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("buffer", pointer, currentProgram))
        .setComment("Clear buffer retry, then store buffer atFEBF6B0C. "
            + "NULL with descriptor mode2 calls71CE0(handle,77); registered mode1 "
            + "does not take that callback. No local handle bound check.");
    semanticFunction(0x74614L, "f33_nvm_read_buffer", pointer,
        new ParameterImpl("logical_handle", u16, currentProgram))
        .setComment("Read descriptor mode, then prefer nonNULL overrideFEBF6B08. "
            + "Without override useFEBF6B10 for mode4, otherwise descriptor+C. "
            + "All registered rows are mode1 withNULL defaults; no bound check.");
    semanticFunction(0x746DEL, "f33_nvm_write_buffer", pointer,
        new ParameterImpl("logical_handle", u16, currentProgram))
        .setComment("Same selection using overrideFEBF6B0C, notFEBF6B08. "
            + "Both selectors executed for all124 rows withNULL/nonNULL overrides. "
            + "Unregistered mode4 is instruction-derived, not an executed configuration.");
    semanticFunction(0x73AB0L, "f33_nvm_initialize_operation", VoidDataType.dataType)
        .setComment("Set operationFFFFFFFF, handleFFFF, both pointersNULL, "
            + "phase1, stepFFFF and state0. Leave record padding unchanged.");
    semanticFunction(0x73ADCL, "f33_nvm_copy_operation", VoidDataType.dataType,
        new ParameterImpl("request", new PointerDataType(requestType, 4), currentProgram))
        .setComment("Copy only fields+0,+4,+8,+C intoFEBF6AEC. "
            + "Do not copy the two padding bytes or adjacent dispatch state.");
    semanticFunction(0x73AFCL, "f33_nvm_submit_operation", u32,
        new ParameterImpl("request", new PointerDataType(requestType, 4), currentProgram))
        .setComment("State2 returns1 without reading request. Otherwise copy "
            + "the four operation fields, set state2 and phase1, return0. "
            + "No operation/handle/pointer validation, interrupt mask or flash "
            + "execution at this layer. Step and padding remain unchanged.");
  }
  private void annotatePwmCompareStaging() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    StructureDataType halfwords =
        new StructureDataType(category, "F33PwmHalfwordStage", 0);
    halfwords.setPackingEnabled(true);
    halfwords.add(u16, "port_mask", "Consumed by61DFA;61C90 does not write this field.");
    halfwords.add(u16, "u", "61E72 writes this value toTSG3nCMPUE.");
    halfwords.add(u16, "v", "61E72 writes this value toTSG3nCMPVE.");
    halfwords.add(u16, "w", "61E72 writes this value toTSG3nCMPWE.");
    semanticData(0xFEBE38A0L, new ArrayDataType(resolve(halfwords), 2, 8),
        "f33_pwm_halfword_stages",
        "Two software slots.315D0 maps slots0/1 toTSG3 units1/0. "
        + "The compare register identities do not establish output polarity or motor timing.");
    StructureDataType words =
        new StructureDataType(category, "F33PwmWordStage", 0);
    words.setPackingEnabled(true);
    words.add(u32, "w", "Zero-extended quantized third input; reverse lane order.");
    words.add(u32, "v", "Zero-extended quantized second input.");
    words.add(u32, "u", "Zero-extended quantized first input.");
    semanticData(0xFEBE38B0L, new ArrayDataType(resolve(words), 2, 12),
        "f33_pwm_word_stages",
        "Initialized alongside halfword stages by61AEA, written by61D38. "
        + "This annotation does not establish a hardware transfer consumer.");
    semanticData(0x3166CL, u16, "f33_pwm_compare_span",
        "Unsigned calibration4000 used by61C90/61D38; no clock-frequency claim.");
    semanticData(0x3166EL, u16, "f33_pwm_compare_offset",
        "Unsigned calibration80 used by61C90/61D38; distinct from31670/31672.");
    semanticFunction(0x61AEAL, "f33_pwm_initialize_compare_stages", VoidDataType.dataType,
        new ParameterImpl("compare", u16, currentProgram))
        .setComment("For both slots copy low16(compare) to all three halfwords "
            + "and zero-extend it into all three word lanes. Load port masks "
            + "from31612+8*slot. No quantization or peripheral access here.");
    semanticFunction(0x61C90L, "f33_pwm_stage_halfword_compares", VoidDataType.dataType,
        new ParameterImpl("slot", u32, currentProgram),
        new ParameterImpl("u_code", u16, currentProgram),
        new ParameterImpl("v_code", u16, currentProgram),
        new ParameterImpl("w_code", u16, currentProgram))
        .setComment("Quantize each low16 input p: p==0 ->span+2*offset; "
            + "0<p<8000 ->offset+(((8000-p)*span)>>15); p>=8000 ->0. "
            + "Store low16 results atFEBE38A0+8*full32(slot)+2/+4/+6, "
            + "preserving the port mask. Native MULU/SHR; no local index bound. "
            + "This is compare staging, not a signed formula or physical duty claim.");
    semanticFunction(0x61D38L, "f33_pwm_stage_word_compares", VoidDataType.dataType,
        new ParameterImpl("slot", ShortDataType.dataType, currentProgram),
        new ParameterImpl("u_code", u16, currentProgram),
        new ParameterImpl("v_code", u16, currentProgram),
        new ParameterImpl("w_code", u16, currentProgram))
        .setComment("Same unsigned-input quantizer as61C90, but zero-extend each "
            + "low16 result to a word and store in W/V/U order at "
            + "FEBE38B0+12*signed16(slot). MULHI truncates/sign-extends the slot; "
            + "unlike61C90 it does not use the full32-bit index. No local bounds. "
            + "Execution includes high-bit truncation and slotFFFF writing before "
            + "the declared two-slot array; not evidence that callers use that slot.");
  }
  private void annotateNvmRecordIntegrity() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType bytes = new PointerDataType(u8, 4);
    StructureDataType record =
        new StructureDataType(category, "F33NvmRecordContext", 0);
    record.setPackingEnabled(true);
    record.add(u16, "storage_handle", "First two on-flash header bytes.");
    record.add(u16, "checksum16", "Header checksum used for payload lengths<=32.");
    record.add(bytes, "source_buffer", "Source consumed by773FE and the write preparation path.");
    record.add(bytes, "destination_buffer", "Destination set by772D8 and used by772C0.");
    record.add(u32, "checksum32", "Large-record checksum read from immediately after the payload; not a pointer.");
    DataType recordType = resolve(record);
    DataType recordPointer = new PointerDataType(recordType, 4);
    semanticData(0xFEBF6B80L, recordType, "f33_nvm_record_context",
        "Metadata and buffer pointers, not an inline payload. The +C word "
        + "is a checksum, distinct from the source pointer at+C inF33NvmOperation.");
    StructureDataType commit =
        new StructureDataType(category, "F33NvmCommitContext", 0);
    commit.setPackingEnabled(true);
    commit.add(recordPointer, "record", "Set by778C6.");
    commit.add(u32, "marker", "77AA8 reads the final-allocation word here and requiresAAAAAAAA.");
    semanticData(0xFEBF6B78L, resolve(commit), "f33_nvm_commit_context",
        "Accepted marker contributes680 to the running byte sum.");
    semanticData(0xFEBF6C28L, u32, "f33_nvm_checksum_accumulator",
        "Running unsigned byte sum. Header contributes only its two handle bytes; "
        + "the accepted marker contributes fourAA bytes. Small/large verification "
        + "addsC000/C0000000 respectively.");
    semanticData(0xFEBF6C46L, u16, "f33_nvm_payload_chunks_remaining",
        "Decremented only after an accepted payload copy by7771A.");
    Function bind = semanticFunction(0x778C6L, "f33_nvm_bind_record_context", VoidDataType.dataType,
        new ParameterImpl("context", new PointerDataType(resolve(commit), 4), currentProgram),
        new ParameterImpl("record", recordPointer, currentProgram));
    bind.setComment("Store r7 at context+0; preserve r6/r7/r10. Inline the real "
        + "six-byte body so77B12 retains the record pointer for772D8.");
    bind.setInline(true);
    Function destination = semanticFunction(0x772D8L, "f33_nvm_set_read_destination", VoidDataType.dataType,
        new ParameterImpl("context", recordPointer, currentProgram),
        new ParameterImpl("destination", bytes, currentProgram));
    destination.setComment("Store r7 at record-context+8; preserve r6/r7/r10. "
        + "No destination bound or alignment validation.");
    destination.setInline(true);
    semanticFunction(0x77356L, "f33_nvm_sum_bytes", u32,
        new ParameterImpl("byte_count", u16, currentProgram),
        new ParameterImpl("source", bytes, currentProgram))
        .setComment("Sum exactly low16(byte_count) unsigned bytes into full32-bit "
            + "r10. Zero count does not read source; unaligned byte input is valid. "
            + "This is an additive sum, not a CRC. The prior inferredvoid prototype "
            + "incorrectly hid the source reads and result in standalone C.");
    semanticFunction(0x77330L, "f33_nvm_payload_chunk_length", u32,
        new ParameterImpl("handle", u16, currentProgram),
        new ParameterImpl("payload_offset", u16, currentProgram))
        .setComment("Let r=min(low16(payload_length-payload_offset),64). Return "
            + "low16(r+(r&3)), zero-extended. This is not generic round-up-to-four: "
            + "length64/offset1 returns66, while offset past length wraps before "
            + "clipping. Registered payloads and ordinary chunk offsets are aligned.");
    semanticFunction(0x772A8L, "f33_nvm_header_checksum", u32,
        new ParameterImpl("context", recordPointer, currentProgram))
        .setComment("Load context+2 as unsigned16 and zero-extend to r10.");
    semanticFunction(0x772DEL, "f33_nvm_tail_checksum", u32,
        new ParameterImpl("context", recordPointer, currentProgram))
        .setComment("Load full32-bit checksum from context+C; not a pointer read.");
    semanticFunction(0x74830L, "f33_copy_bytes_forward", VoidDataType.dataType,
        new ParameterImpl("destination", bytes, currentProgram),
        new ParameterImpl("source", bytes, currentProgram),
        new ParameterImpl("byte_count", u32, currentProgram))
        .setComment("Forward byte loop with full32-bit count. No validation, "
            + "overlap-safe memmove guarantee or return-value contract.");
    semanticFunction(0x772C0L, "f33_nvm_copy_payload_chunk", VoidDataType.dataType,
        new ParameterImpl("context", recordPointer, currentProgram),
        new ParameterImpl("payload_offset", u16, currentProgram),
        new ParameterImpl("byte_count", u16, currentProgram),
        new ParameterImpl("source", bytes, currentProgram))
        .setComment("Copy low16(byte_count) bytes into context.destination_buffer "
            + "+low16(payload_offset), through the real74830 byte loop. "
            + "No local destination bound or checksum validation.");
    semanticFunction(0x7771AL, "f33_nvm_read_payload_chunk", u32,
        new ParameterImpl("handle", u16, currentProgram),
        new ParameterImpl("record_offset", u32, currentProgram),
        new ParameterImpl("read_option", u8, currentProgram))
        .setComment("Read the next payload chunk through776FA. On success add its "
            + "unsigned byte sum. For lengths<=32 addC000 and compare low16 "
            + "against context.checksum16 before copying; mismatch returnsFFFC "
            + "without destination write or remaining-count decrement. Larger "
            + "payloads copy before the later777CA checksum check. Native proof "
            + "includes post-read7775E boundaries and a complete captured16-byte "
            + "read through77B12 with explicit ICU-S/ECC/blank-check inputs. "
            + "Full multi-chunk acquisition and application restoration remain separate.");
    semanticFunction(0x777CAL, "f33_nvm_read_payload_checksum", u32,
        new ParameterImpl("handle", u16, currentProgram),
        new ParameterImpl("record_offset", u32, currentProgram),
        new ParameterImpl("read_option", u8, currentProgram))
        .setComment("Read four bytes at record_offset+payload_length+4 into "
            + "context.checksum32. Success addsC0000000 to the accumulator and "
            + "compares the full word; mismatch returnsFFFC. No rollback of "
            + "earlier destination copies. Native proof starts at post-read777FC; "
            + "not an end-to-end hardware read or application restoration proof.");
    semanticFunction(0x77B12L, "f33_nvm_begin_record_read", VoidDataType.dataType,
        new ParameterImpl("handle", u16, currentProgram),
        new ParameterImpl("destination", bytes, currentProgram),
        new ParameterImpl("read_option", u8, currentProgram))
        .setComment("Reject low16(handle)>=123 or NULL destination before setup. "
            + "Bind the contexts, set remaining chunks/base, then read marker with "
            + "option1 regardless of caller option. Admit header and first payload "
            + "chunk; return pending if chunks remain. Otherwise check the large "
            + "checksum when length>32 and publish status through77640. Entry does "
            + "not reset the checksum accumulator. Complete captured16-byte record "
            + "execution covers explicit blank/nonblank hardware results, destination "
            + "canaries and completion cleanup; full multi-chunk and application "
            + "request/notification closure remain separate.");
  }
  private void annotateApplicationRecords() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType words = new PointerDataType(u32, 4);
    int count = currentProgram.getMemory().getShort(toAddr(0x2AD72L)) & 0xFFFF;
    StructureDataType descriptor =
        new StructureDataType(category, "F33NvmFamily1RamDescriptor", 0);
    descriptor.setPackingEnabled(true);
    descriptor.add(u16, "payload_bytes", "Whole-word copy and checksum length.");
    descriptor.add(u16, "first_logical_handle",
        "Three copies use this handle,+4,+8; FFFF disables the registered object.");
    descriptor.add(words, "buffer", "Application RAM object, not a DataFlash address.");
    semanticData(0x2AF0CL, new ArrayDataType(resolve(descriptor), count, 8),
        "f33_nvm_family1_ram_descriptors",
        "Sixteen eight-byte rows selected by family byte1 at66DFC. "
        + "Object0 has16 bytes atFEBEF468. Do not infer copy grouping from row order.");
    semanticData(0x2AD72L, u16, "f33_nvm_family1_object_count",
        "Getter68144 enforces this bound; checksum leaves67B12/67C8C do not.");
    semanticData(0xFEBF0328L, new ArrayDataType(u8, count, 1),
        "f33_nvm_family1_status", "Primary status bytes; not boolean validity flags.");
    semanticData(0xFEBF1088L, new ArrayDataType(u8, count, 1),
        "f33_app_nvm_family1_status_xor55",
        "Application-phase XOR55 replicas. This RAM has a different boot-relocation role.");
    semanticData(0xFEBF10ACL, new ArrayDataType(u8, count, 1),
        "f33_app_nvm_family1_status_xorAA",
        "Application-phase XORAA replicas. This RAM has a different boot-relocation role.");
    semanticData(0xFEBF0428L, new ArrayDataType(u16, count, 2),
        "f33_nvm_family1_checksum_seeds",
        "Low16(A55A - sum(word + (word>>16))); distinct from physical-record checksums.");
    int family0Count = currentProgram.getMemory().getShort(toAddr(0x2AD70L)) & 0xFFFF;
    StructureDataType family0Descriptor =
        new StructureDataType(category, "F33NvmFamily0RamDescriptor", 0);
    family0Descriptor.setPackingEnabled(true);
    family0Descriptor.add(u16, "payload_bytes", "Application payload; excludes sequence envelope.");
    family0Descriptor.add(u16, "logical_count", "Inclusive first through first+count-1 member range.");
    family0Descriptor.add(u16, "first_logical_handle", "FFFF disables this registered object.");
    family0Descriptor.add(u16, "opaque_06", "Not interpreted by the publication contract.");
    family0Descriptor.add(new PointerDataType(u8, 4), "buffer", "Byte-addressed application RAM mirror.");
    semanticData(0x2AD8CL, new ArrayDataType(resolve(family0Descriptor), family0Count, 12),
        "f33_nvm_family0_ram_descriptors",
        "32 registered rows. Payload8..240 bytes and logical counts0/2/6; "
        + "registered per-object probe costs are at most12, below budget18.");
    semanticData(0x2AD70L, u16, "f33_nvm_family0_object_count",
        "Registered32; completion getter and classification enforce this bound.");
    semanticData(0xFEBF0308L, new ArrayDataType(u8, family0Count, 1),
        "f33_nvm_family0_status", "Application status, distinct from lower completion0338.");
    semanticData(0xFEBF0338L, new ArrayDataType(u8, family0Count, 1),
        "f33_nvm_family0_completion",
        "FF admits callbacks; final read/write handling publishes5A/A5, not public status10/30/31.");
    semanticData(0xFEBF0368L, new ArrayDataType(u16, family0Count, 2),
        "f33_nvm_family0_selected_logical_handles",
        "FFFF means no selection. Read publication selects its member; successful expected write advances it.");
    semanticData(0xFEBF03A8L, new ArrayDataType(u32, family0Count, 4),
        "f33_nvm_family0_sequences",
        "Read selection stores accepted sequence; write arming increments before completion, even if enqueue rejects.");
    semanticData(0xFEBF0708L, new ArrayDataType(u8, 1024, 1),
        "f33_nvm_family0_write_record",
        "Shared sequence/payload/padding/inverse-sequence envelope, initialized separately from application mirrors.");
    semanticData(0xFEBF0C88L, new ArrayDataType(u8, 1024, 1),
        "f33_nvm_family0_read_record",
        "Shared read staging.68B2E always reads its sequence header here, even though payload/trailer use r8.");
    semanticFunction(0x67B12L, "f33_nvm_check_family1_checksum", s32,
        new ParameterImpl("object", u16, currentProgram))
        .setComment("No local object bound. Read floor(payload_bytes/4) live RAM words "
            + "and sum word+(word>>16) with32-bit wrap. Return1 iff low16(sum+seed)"
            + "==A55A, otherwise full32 FFFFFFFF. No repair or publication.");
    semanticFunction(0x67C8CL, "f33_nvm_publish_family1_checksum", VoidDataType.dataType,
        new ParameterImpl("object", u16, currentProgram))
        .setComment("No local object bound. Fold the same live RAM words as67B12 "
            + "and store only low16(A55A-sum) in the selected seed. No status change.");
    semanticFunction(0x68144L, "f33_nvm_get_family1_record", u32,
        new ParameterImpl("object", u16, currentProgram),
        new ParameterImpl("destination", words, currentProgram))
        .setComment("Out-of-bound object returnsFF without a copy. Otherwise copy "
            + "whole words BEFORE voting/repairing status with fallback12. Forward "
            + "every voted status unchanged except10 with a failing live-source "
            + "checksum returns12. Checksum failure does not rewrite stored status "
            + "or undo the copy. Forward-copy aliasing can change the checked source.");
    semanticFunction(0x66DFCL, "f33_nvm_get_record", u32,
        new ParameterImpl("selector", u32, currentProgram),
        new ParameterImpl("destination", words, currentProgram))
        .setComment("Decode only selector bits8..15 and pass low8 object plus "
            + "the unchanged destination to67948/68144/67208 for families0/1/2. "
            + "Forward the callee result; other families returnFF without data access. "
            + "Upper16 selector bits are ignored. Families0/1 copy RAM; family2 validates and copies ROM. Not a physical NvM read.");
    DataType quad = new ArrayDataType(u16, 4, 2);
    StructureDataType record =
        new StructureDataType(category, "F33LearnedQuadRecord", 0);
    record.setPackingEnabled(true);
    record.add(u32, "marker", "3584A requires A55A5AA5, not AA5A5AA5.");
    record.add(quad, "values", "Four raw unsigned halfwords; physical units not recovered.");
    record.add(u32, "opaque_tail", "Included in the application checksum; not published by355F6.");
    semanticData(0xFEBEF468L, resolve(record), "f33_learned_quad_record",
        "Family1 object0;16-byte RAM record. Physical-copy consensus and status "
        + "publication are separate prerequisites, not implied by this layout.");
    semanticData(0xFEBE6AE6L, quad, "f33_learned_quad",
        "355F6 publishes all four values before3584A performs range validation. "
        + "A failed range check does not roll this publication back.");
    StructureDataType bounds =
        new StructureDataType(category, "F33LearnedQuadBounds", 0);
    bounds.setPackingEnabled(true);
    bounds.add(s32, "pair1_upper", "Inclusive signed bound for values0 and1.");
    bounds.add(s32, "pair1_lower", "Inclusive signed bound for values0 and1.");
    bounds.add(s32, "pair2_upper", "Inclusive signed bound for values2 and3.");
    bounds.add(s32, "pair2_lower", "Inclusive signed bound for values2 and3.");
    DataType boundsType = resolve(bounds);
    semanticData(0xAEF5CL, boundsType, "f33_learned_quad_rom_bounds",
        "Exact target constants: +200000,-200000,+200000,-200000 hex. "
        + "BF3AA copies these four words into the application snapshot.");
    semanticData(0xFEBEE8E8L, boundsType, "f33_learned_quad_runtime_bounds",
        "BF3AA copies the ROM bounds; BF97A also writes the same initial values. "
        + "35640 consumes signed32 values here; no physical-unit inference.");
    semanticFunction(0xB73BAL, "f33_scale_u16_delta_s16_x4", s32,
        new ParameterImpl("value", u16, currentProgram),
        new ParameterImpl("origin", u16, currentProgram),
        new ParameterImpl("gain", ShortDataType.dataType, currentProgram))
        .setComment("Return low32((uint16(value)-uint16(origin))*int16(gain)*4). "
            + "MUL discards the high word, then SHL2 wraps. FDEBC is the real "
            + "tail-jump thunk. No saturation or physical-unit contract.");
    semanticFunction(0x355F6L, "f33_publish_learned_quad", VoidDataType.dataType)
        .setComment("Initialize a16-byte local from210D0; get selector100 again. "
            + "Only result10 publishes record offsets4/6/8/A toFEBE6AE6..6AEC. "
            + "Other results preserve published values; there is no zero fallback. "
            + "This helper does not test the marker or ranges.");
    semanticFunction(0x35640L, "f33_check_learned_quad_bounds", u32)
        .setComment("Convert each unsigned halfword with origin800 and gain-9CD "
            + "through FDEBC/B73BA: (2048-value)*10036. Signed32 inclusive bounds "
            + "use pair1 for values0/1 and pair2 for2/3. Return5A for any violation, "
            + "otherwise0; no published-state writes.");
    semanticFunction(0x3584AL, "f33_restore_learned_quad", u32)
        .setComment("Get selector100; require result10 and markerA55A5AA5. Then "
            + "355F6 performs a SECOND get and conditional publication, followed "
            + "by35640. ReturnA55A5AA5 iff validation returns0, otherwise5AA5A55A. "
            + "Marker/status rejection precedes publication; range rejection follows "
            + "it without rollback. No single-snapshot or asynchronous completion claim.");
  }
  private void annotateApplicationCompletion() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    int logicalCount = currentProgram.getMemory().getShort(toAddr(0x26C08L)) & 0xFFFF;
    int objectCount = currentProgram.getMemory().getShort(toAddr(0x2AD72L)) & 0xFFFF;
    int requestCount = currentProgram.getMemory().getByte(toAddr(0x2AD8BL)) & 0xFF;
    StructureDataType route = new StructureDataType(category, "F33NvmApplicationRoute", 0);
    route.setPackingEnabled(true);
    route.add(u8, "object", "Low byte; interpreted within the selected family.");
    route.add(u8, "family", "68E9E handles only families0 and1.");
    semanticData(0x2B010L, new ArrayDataType(resolve(route), logicalCount, 2),
        "f33_nvm_logical_application_routes",
        "Logical-indexed routing, not a physical-handle table. Entries0/1 areFFFF. "
        + "Enabled family1 descriptors map base/base+4/base+8 to the same object.");
    StructureDataType result = new StructureDataType(category, "F33NvmLogicalResultCell", 0);
    result.setPackingEnabled(true);
    result.add(u8, "result", "71D0A stores only this byte before notification.");
    result.add(u8, "write_inhibit", "743F8 rejects exactly1; other values pass.71CA0 initializes2 in this target.");
    semanticData(0xFEBF6000L, new ArrayDataType(resolve(result), logicalCount, 2),
        "f33_nvm_logical_results", "Byte result in a two-byte cell; not a halfword store.");
    StructureDataType stage = new StructureDataType(category, "F33NvmCopyStage", 0);
    stage.setPackingEnabled(true);
    DataType lane = new ArrayDataType(u8, 32, 1);
    stage.add(lane, "raw", "Raw payload; read consensus may repair this lane.");
    stage.add(lane, "xor55", "Decode each payload byte with55.");
    stage.add(lane, "xorAA", "Decode each payload byte withAA.");
    semanticData(0xFEBF0B08L, new ArrayDataType(resolve(stage), 4, 96),
        "f33_nvm_family1_read_stages",
        "Slot=object&3. Payload lengths8/16/32 leave lane padding untouched. "
        + "Shared-slot execution ordering is a separate queue/scheduler question.");
    semanticData(0xFEBF06A8L, resolve(stage), "f33_nvm_family1_write_stage",
        "One shared raw/55/AA snapshot.6869E copies the live source in three passes, "
        + "then encodes the latter lanes; bytes after payload length remain untouched.");
    semanticData(0xFEBF0358L, new ArrayDataType(u8, objectCount, 1),
        "f33_nvm_family1_completion",
        "FF admits the application callback; terminal read/write handlers publish5A/A5. "
        + "Distinct from the redundant application-status bytes atFEBF0328.");
    semanticData(0xFEBF0691L, u8, "f33_nvm_family1_busy",
        "68E9E clears this on leaf return5A, including failed read/write completion. "
        + "Its current value is not an admission gate in68E9E.");
    semanticData(0xFEBF0694L, u8, "f33_nvm_copy_read_retry",
        "Shared by family0 and family1 read callbacks. Success clears it; nonzero "
        + "result retries below2, consuming an attempt even if73FE8 rejects submission.");
    semanticData(0xFEBF0698L, new ArrayDataType(u32, 4, 4),
        "f33_nvm_family1_copy_failure_masks",
        "One word per shared slot. Read voting tests5A bits in each copy byte; "
        + "write completion tests the ENTIRE word for zero. Copy0 resets the word.");
    StructureDataType request = new StructureDataType(category, "F33NvmRequestCell", 0);
    request.setPackingEnabled(true);
    request.add(u8, "state", "11 read;22 write;33 write unless completion5A. Membership ignores it.");
    request.add(u8, "opaque_01", "Preserved by dequeue and initialization.");
    request.add(u16, "object", "FFFF marks an empty object field; membership scans all rows.");
    semanticData(0xFEBF058CL, new ArrayDataType(resolve(request), requestCount, 4),
        "f33_nvm_family1_request_cells",
        "49 four-byte cells at058C, not048C.67AE6 ignores state and queue indices.");
    int family0RequestCount = currentProgram.getMemory().getByte(toAddr(0x2AD8AL)) & 0xFF;
    semanticData(0xFEBF0488L, new ArrayDataType(resolve(request), family0RequestCount, 4),
        "f33_nvm_family0_request_cells",
        "65 four-byte cells.673DE scans every object field regardless of state or indices.");
    semanticData(0x2AD8AL, u8, "f33_nvm_family0_request_cell_count",
        "Registered count65; shared by index advancement, recovery and membership.");
    semanticData(0x2AD8BL, u8, "f33_nvm_family1_request_cell_count",
        "Registered count49; consumed by the full membership scan.");
    semanticData(0xFEBF0689L, u8, "f33_nvm_family1_phase",
        "67CCA handles11/22/33; completion cleanup stores0.");
    semanticData(0xFEBF068AL, u8, "f33_nvm_family1_write_retry",
        "Whole-write retry in phase33; distinct from the per-copy read counter0694.");
    semanticData(0xFEBF068CL, u16, "f33_nvm_family1_active_object",
        "67CCA snapshots this object; cleanup storesFFFF. Retry returns before cleanup.");
    StructureDataType pair = new StructureDataType(category, "F33U32ValueKey", 0);
    pair.setPackingEnabled(true);
    pair.add(u32, "value", "Full-width result, not necessarily a byte event.");
    pair.add(u32, "key", "Exact full32-bit comparison.");
    DataType pairType = resolve(pair);
    StructureDataType lookup = new StructureDataType(category, "F33U32LookupTable", 0);
    lookup.setPackingEnabled(true);
    lookup.add(u32, "count", "Unsigned row count; no sentinel.");
    lookup.add(new PointerDataType(pairType, 4), "rows", "Value/key pairs, eight-byte stride.");
    DataType lookupType = resolve(lookup);
    int eventCount = currentProgram.getMemory().getInt(toAddr(0x275CCL));
    long eventRows = currentProgram.getMemory().getInt(toAddr(0x275D0L)) & 0xFFFFFFFFL;
    semanticData(0x275CCL, lookupType, "f33_nvm_operation_event_lookup",
        "Nine registered pairs; A1A62093->6 and22AA8A36->7. Other event meanings "
        + "are not inferred from their numeric values.");
    semanticData(eventRows, new ArrayDataType(pairType, eventCount, 8),
        "f33_nvm_operation_event_rows", "Consumed through the counted lookup header.");
    FunctionDefinitionDataType callback =
        new FunctionDefinitionDataType(category, "F33NvmApplicationResultCallback");
    callback.setReturnType(u32);
    callback.setArguments(
        new ParameterDefinitionImpl("event", u8, null),
        new ParameterDefinitionImpl("logical_handle", u16, null),
        new ParameterDefinitionImpl("result", u8, null));
    semanticData(0x26BFCL, new PointerDataType(callback, 4),
        "f33_nvm_application_result_callback", "Registered target68E9E; caller ignores its result.");
    FunctionDefinitionDataType zeroCallback =
        new FunctionDefinitionDataType(category, "F33NvmZeroHandleResultCallback");
    zeroCallback.setReturnType(VoidDataType.dataType);
    zeroCallback.setArguments(
        new ParameterDefinitionImpl("event", u8, null),
        new ParameterDefinitionImpl("result", u8, null));
    semanticData(0x26BF8L, new PointerDataType(zeroCallback, 4),
        "f33_nvm_zero_handle_result_callback",
        "NULL in this exact target. The caller has two arguments and consumes no return value.");
    semanticFunction(0x73A86L, "f33_lookup_u32_value_by_key", u32,
        new ParameterImpl("key", u32, currentProgram),
        new ParameterImpl("fallback", u32, currentProgram),
        new ParameterImpl("table", new PointerDataType(lookupType, 4), currentProgram))
        .setComment("Linear unsigned-count scan of eight-byte value/key pairs. "
            + "Return the FIRST full32-bit key match, otherwise full32 fallback. "
            + "Count0 does not read the row pointer. No pointer or extent validation.");
    semanticFunction(0x68A50L, "f33_nvm_get_family1_completion", u32,
        new ParameterImpl("object", u16, currentProgram))
        .setComment("Bound low16 object by the registered count16. Return the "
            + "selected byte zero-extended, orA5 without an array read when out of bounds.");
    semanticFunction(0x68CCAL, "f33_nvm_handle_family1_read_result", u32,
        new ParameterImpl("result", u8, currentProgram),
        new ParameterImpl("logical_handle", u16, currentProgram))
        .setComment("Map low16 logical to low8 object, slot=object&3. Copy0 resets "
            + "the mask; success clears shared retry. Nonzero result retries while "
            + "counter<2 and ignores submission result; exhaustion marks that copy "
            + "with5A and clears retry. Only copy2 without retry votes all payload "
            + "bytes using trusted raw/AA,raw/55,then55/AA pairs. Encoded agreement "
            + "repairs raw staging even when another byte fails. Publish destination "
            + "only if every byte passes; completion5A/A5 distinguishes success/failure. "
            + "Return5A for either completed vote, otherwise0. No local handle/object "
            + "bound. Unmatched copy handle sets mask005A5A5A without reading retry.");
    semanticFunction(0x68E16L, "f33_nvm_handle_family1_write_result", u32,
        new ParameterImpl("result", u8, currentProgram),
        new ParameterImpl("logical_handle", u16, currentProgram))
        .setComment("Unchecked route object and family1 descriptor; slot=object&3. "
            + "Copy0 resets the entire mask without reading it. Nonzero result ORs5A "
            + "into that copy byte; success does not clear prior failures. Copy2 "
            + "publishes5A iff the FULL32 mask is zero, otherwiseA5, and returns5A "
            + "in both cases. Earlier copies return0. Unmatched handle sets005A5A5A "
            + "and returns0. No read retry, data copy or physical-programming proof.");
    semanticFunction(0x68E9EL, "f33_nvm_route_application_result", u32,
        new ParameterImpl("event", u8, currentProgram),
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("result", u8, currentProgram))
        .setComment("Decode family/object from2B010. Require family completionFF "
            + "and nonFFFF first handle; event6/7 selects read/write result handler. "
            + "Leaf return5A clears that family's busy byte even on failure. Always "
            + "return0. Native read/write handlers for both families; completion "
            + "publication is not evidence of physical flash commitment.");
    semanticFunction(0x71D0AL, "f33_nvm_publish_logical_result", VoidDataType.dataType,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("operation", u32, currentProgram),
        new ParameterImpl("result", u8, currentProgram))
        .setComment("Store only result low8 atFEBF6000+2*low16(handle), preserving "
            + "the other byte; then route the same handle/operation/result. No local bound.");
    semanticFunction(0x71E08L, "f33_nvm_route_logical_result", VoidDataType.dataType,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("operation", u32, currentProgram),
        new ParameterImpl("result", u8, currentProgram))
        .setComment("Low16 handle0 calls the two-argument zero-handle notifier; "
            + "otherwise preserve all three arguments for the logical notifier.");
    semanticFunction(0x71DBAL, "f33_nvm_notify_logical_result", VoidDataType.dataType,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("operation", u32, currentProgram),
        new ParameterImpl("result", u8, currentProgram))
        .setComment("Descriptor+A bit5 optionally calls747DC, whose exact body is "
            + "JMP LP; all124 registered rows clear that bit. Result2 suppresses "
            + "application notification. Otherwise nonNULL26BFC receives low8 "
            + "lookup(operation,FF), low16 handle, low8 result. No local handle bound.");
    semanticFunction(0x71D8CL, "f33_nvm_notify_zero_handle_result", VoidDataType.dataType,
        new ParameterImpl("operation", u32, currentProgram),
        new ParameterImpl("result", u8, currentProgram))
        .setComment("Perform the event lookup even before checking result2 or "
            + "callbackNULL. Conditional callback takes event/result only. Registered "
            + "26BF8 isNULL, so this exact target emits no zero-handle application callback.");
    semanticFunction(0x67AE6L, "f33_nvm_family1_has_request_cell", u32,
        new ParameterImpl("object", u16, currentProgram))
        .setComment("Scan all49 cell object halfwords atFEBF058E+4*i for low16 object; "
            + "return1 on first match else0. Ignore state bytes, producer/consumer "
            + "indices and empty-sentinel meaning; no local object bound.");
    semanticFunction(0x67CCAL, "f33_nvm_handle_family1_completion", VoidDataType.dataType)
        .setComment("Snapshot phase/object and queue indices. Phase11 sets0688=A5. "
            + "Valid phase22/33 completion5A publishes checksum seed then status10. "
            + "Phase22 failure calls68A6C: zero->30, every other result->11; no "
            + "checksum publication. Phase33 failure increments retry below2, calls "
            + "6869E and returns before cleanup regardless rearm result; exhaustion "
            + "selects31. A matching request cell overrides status to20 after any seed "
            + "publication. Publish all status planes; clear phase, preserve recovered "
            + "producer index, set active objectFFFF. Invalid phase/object only cleans "
            + "up. Native real classifier/cancellation and accepted whole-write retry; "
            + "explicit FACI events are not physical blankness or programming proof.");
    semanticFunction(0x6869EL, "f33_nvm_submit_family1_write_copies", u32,
        new ParameterImpl("object", u16, currentProgram))
        .setComment("Read descriptor before busy0/nonFFFF gate; no local object bound. "
            + "Copy payload bytes from live RAM in three separate passes to06A8/06C8/"
            + "06E8, then XOR latter lanes55/AA; no atomic-snapshot claim. Submit "
            + "base/+4/+8 via74014, ignoring each return. Set busyFF, selected slot "
            + "mask005A5A5A and completionFF; return0 even with all writes rejected. "
            + "Rejected local gate returnsFF without staging changes. Native lengths "
            + "16/32, high object bits, busy/disabled rejection, partial/all inhibition "
            + "and composed phase33 retry. Queued is not flash committed.");
  }
  private void annotateNvmQueues() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType pointer = new PointerDataType(VoidDataType.dataType, 4);
    DataType operation = getDataAt(toAddr(0xFEBF6AECL)).getDataType();
    DataType operationPointer = new PointerDataType(operation, 4);
    StructureDataType slot = new StructureDataType(category, "F33NvmQueueSlot", 0);
    slot.setPackingEnabled(true);
    slot.add(u32, "operation", "9DA70AE7 denotes a free slot.");
    slot.add(pointer, "read_buffer", "Copied from operation+8; not dereferenced by enqueue.");
    slot.add(pointer, "write_buffer", "Copied from operation+C; not dereferenced by enqueue.");
    slot.add(u16, "logical_handle", "FFFF in a free slot.");
    slot.add(u16, "next", "FFFF terminates the singly linked chain.");
    DataType slotType = resolve(slot);
    StructureDataType header = new StructureDataType(category, "F33NvmQueueHeader", 0);
    header.setPackingEnabled(true);
    header.add(u16, "head", "Both head/tailFFFF denotes empty.");
    header.add(u16, "tail", "Exactly one sentinel is inconsistent.");
    DataType headerType = resolve(header);
    semanticData(0xFEBF6128L, new ArrayDataType(slotType, 123, 16),
        "f33_nvm_queue_slots", "123 slots, not124. Cold free pool0 contains122; pool1 contains0..121.");
    semanticData(0xFEBF68D8L, operation, "f33_nvm_zero_handle_operation",
        "Separate operation-layout record, NOT a queue-slot layout. Padding+6 is preserved.");
    semanticData(0xFEBF68E8L, new ArrayDataType(headerType, 127, 4),
        "f33_nvm_queue_headers", "Free pools0/1, reserved queue2, normal queues3+descriptor.queue_key.");
    semanticData(0xFEBF6AE4L, u16, "f33_nvm_reserved_free_count", "Cold value1.");
    semanticData(0xFEBF6AE6L, u16, "f33_nvm_normal_free_count", "Cold value122.");
    semanticData(0xFEBF6AE8L, u16, "f33_nvm_reserved_used_count", "Cold value0.");
    semanticData(0xFEBF6AEAL, u16, "f33_nvm_normal_used_count", "Cold value0.");
    semanticData(0xFEBF6126L, u16, "f33_nvm_reset_notification_exclusion",
        "73078 suppresses result6 for this logical handle.73F0A does not initialize this field.");
    semanticFunction(0x71CA0L, "f33_nvm_initialize_logical_cells", VoidDataType.dataType)
        .setComment("Initialize124 result bytes0. Set write-inhibit1 iff descriptor+A bit11 "
            + "is clear and bit4 set, otherwise2; all registered flags0 yield2. Clear scan halfword60F8.");
    semanticFunction(0x71CF8L, "f33_nvm_get_write_inhibit", u32,
        new ParameterImpl("logical_handle", u16, currentProgram))
        .setComment("Zero-extend byte6001+2*low16(handle); no local bound.");
    semanticFunction(0x71D28L, "f33_nvm_read_logical_result", u32,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("output", new PointerDataType(u8, 4), currentProgram))
        .setComment("Store result byte6000+2*low16(handle) through output; return0. No bound/null check.");
    semanticFunction(0x73078L, "f33_nvm_notify_reset_result", VoidDataType.dataType,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("operation", u32, currentProgram))
        .setComment("Publish logical result6 unless low16 handle equalsFEBF6126. Result6 is not event6.");
    semanticFunction(0x730A2L, "f33_nvm_clear_queue_headers", VoidDataType.dataType)
        .setComment("Set head/tailFFFF in all127 headers; do not inspect slots.");
    semanticFunction(0x730C0L, "f33_nvm_queue_index", u32,
        new ParameterImpl("base", u32, currentProgram),
        new ParameterImpl("offset", u32, currentProgram))
        .setComment("Return low16(base+offset), zero-extended. No queue bounds check.");
    semanticFunction(0x730C8L, "f33_nvm_reset_slot_range_notifying", VoidDataType.dataType,
        new ParameterImpl("queue", u16, currentProgram),
        new ParameterImpl("first", u16, currentProgram),
        new ParameterImpl("last", u16, currentProgram))
        .setComment("Relink inclusive range. For nonfree old markers, logical2..123 calls "
            + "73078 before clearing; invalid logical calls72130 then still clears. "
            + "Final nextFFFF. No queue/range validation; not proof of a warm-boot entry.");
    semanticFunction(0x7314EL, "f33_nvm_reset_slot_range", VoidDataType.dataType,
        new ParameterImpl("queue", u16, currentProgram),
        new ParameterImpl("first", u16, currentProgram),
        new ParameterImpl("last", u16, currentProgram))
        .setComment("Set header and inclusive unsigned16 range to free marker, NULL buffers, "
            + "logicalFFFF, ascending next; last.nextFFFF. Preserve r10:7319A carries "
            + "pool1 across this call. Inline actual p-code, not an invented return value. "
            + "No range validation; lastFFFF wraps the loop.");
    getFunctionAt(toAddr(0x7314EL)).setInline(true);
    semanticFunction(0x7319AL, "f33_nvm_reset_pooled_queues", VoidDataType.dataType,
        new ParameterImpl("notify", u8, currentProgram))
        .setComment("Clear127 headers; reset pool0 slot122 and pool1 slots0..121. "
            + "Exactly notify==1 selects old-operation notifications. Set free counts1/122 "
            + "and used counts0/0. Does not initialize the notification-exclusion handle.");
    semanticFunction(0x73212L, "f33_nvm_reset_zero_handle_operation", VoidDataType.dataType,
        new ParameterImpl("notify", u8, currentProgram))
        .setComment("When notify==1 and marker nonfree, call73078(handle0,old marker). "
            + "Then marker9DA70AE7, logicalFFFF, NULL buffers; preserve padding+6.");
    semanticFunction(0x7324CL, "f33_nvm_initialize_queues", VoidDataType.dataType)
        .setComment("Reset pooled queues and dedicated logical-zero record without old-operation notifications.");
    semanticFunction(0x73260L, "f33_nvm_reset_queues_notifying", VoidDataType.dataType)
        .setComment("Reset pooled queues and logical-zero record with notify mode1. "
            + "Native proof includes retained request, exclusion and invalid retained logical.");
    semanticFunction(0x732C0L, "f33_nvm_check_queue_empty", u32,
        new ParameterImpl("header", new PointerDataType(headerType, 4), currentProgram),
        new ParameterImpl("empty", new PointerDataType(u8, 4), currentProgram))
        .setComment("Both sentinels:empty1/return0; neither:empty0/return0. Exactly one "
            + "sentinel calls72130, returns1 and leaves output unchanged.");
    semanticFunction(0x732F6L, "f33_nvm_check_slot_partition", u32,
        new ParameterImpl("index", u16, currentProgram),
        new ParameterImpl("queue", u16, currentProgram))
        .setComment("Queues0/2 accept only122; all other queue values accept0..121. "
            + "Invalid slot calls72130 and returns1, else0. Does not bound queue itself.");
    semanticFunction(0x73328L, "f33_nvm_queue_key", u32,
        new ParameterImpl("logical_handle", u16, currentProgram))
        .setComment("Zero-extend descriptor BYTE+1; no local handle bound or priority semantics.");
    semanticFunction(0x734EEL, "f33_nvm_uses_reserved_queue", u32,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("operation", u32, currentProgram))
        .setComment("True only for queue_key0 and marker22AA8A36 or1C646989. "
            + "Every registered descriptor has nonzero key, so all use the normal pool.");
    semanticFunction(0x73552L, "f33_nvm_unlink_queue_slot", VoidDataType.dataType,
        new ParameterImpl("header", new PointerDataType(headerType, 4), currentProgram),
        new ParameterImpl("index", u16, currentProgram),
        new ParameterImpl("previous", u16, currentProgram))
        .setComment("PreviousFFFF replaces head with next, otherwise previous.next=next. "
            + "If nextFFFF, update tail to previous or the new empty head. No checks, "
            + "slot clearing or count update. Preserve r10 used by7358C; inline real p-code.");
    getFunctionAt(toAddr(0x73552L)).setInline(true);
    semanticFunction(0x7358CL, "f33_nvm_pop_queue_head", u32,
        new ParameterImpl("queue", u16, currentProgram),
        new ParameterImpl("index", new PointerDataType(u16, 4), currentProgram))
        .setComment("Validate header consistency, nonempty and head partition, then unlink "
            + "head and store index; return0. Rejection returns1 without output assignment. "
            + "No marker check, slot clearing, counter update or queue bound.");
    semanticFunction(0x735E6L, "f33_nvm_append_queue_slot", u32,
        new ParameterImpl("queue", u16, currentProgram),
        new ParameterImpl("index", u16, currentProgram))
        .setComment("Empty tail sets head; otherwise validate old tail partition and link "
            + "its next. Set tail=index and new nextFFFF. Return0 or1 on old-tail failure. "
            + "Does not validate new index or head/tail consistency.");
    semanticFunction(0x73640L, "f33_nvm_copy_operation_to_slot", VoidDataType.dataType,
        new ParameterImpl("slot", new PointerDataType(slotType, 4), currentProgram),
        new ParameterImpl("operation", operationPointer, currentProgram))
        .setComment("Copy operation+0/+4/+8/+C into slot+0/+C/+4/+8; preserve slot.next. "
            + "Preserve r10, carrying append success through7365C; inline actual p-code.");
    getFunctionAt(toAddr(0x73640L)).setInline(true);
    semanticFunction(0x7365CL, "f33_nvm_append_operation", u32,
        new ParameterImpl("queue", u16, currentProgram),
        new ParameterImpl("index", u16, currentProgram),
        new ParameterImpl("operation", operationPointer, currentProgram))
        .setComment("Append index, then copy operation only on success. Return append status.");
    semanticFunction(0x73686L, "f33_nvm_enqueue_pooled_operation", u32,
        new ParameterImpl("operation", operationPointer, currentProgram))
        .setComment("Select free pool0/1 and queue2/3+key. Pop before checking free marker "
            + "and appending destination; failures after pop do NOT roll back. Only "
            + "successful append decrements free/increments used. Empty pool with count0 "
            + "sets service3 state2; other inconsistencies call72130. Return0/1. "
            + "No local logical bound or payload dereference.");
    semanticFunction(0x73F0AL, "f33_nvm_initialize_logical_module", VoidDataType.dataType)
        .setComment("Actual full initializer executes5772 instructions under explicit "
            + "RAM preconditions. Initialize logical cells, buffer overrides, abortF0, "
            + "pending/active records and queues. Preserve service-state bytes,6126,6B14 "
            + "and padding.7477A clears the same6B18 word once in this target. "
            + "No implied blanket zeroing or reset-path completion.");
    semanticFunction(0x741ECL, "f33_nvm_check_logical_handle", u32,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("api", u8, currentProgram),
        new ParameterImpl("allow_zero", u8, currentProgram))
        .setComment("Accept2..123, additionally0 iff allow_zero==1. Otherwise call "
            + "71D88(14,0,api,A), whose exact body returns0, then return1. No init gate.");
    semanticFunction(0x7423AL, "f33_nvm_check_not_pending", u32,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("api", u8, currentProgram))
        .setComment("Reject exactly logical result2 with return1; other byte values return0.");
    semanticFunction(0x74388L, "f33_nvm_check_buffer_argument", u32,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("buffer", pointer, currentProgram),
        new ParameterImpl("api", u8, currentProgram))
        .setComment("NonNULL passes without descriptor or pointee access. NULL passes "
            + "only modes2/4; registered mode1 rejects it. No alignment/extent validation.");
    semanticFunction(0x743BCL, "f33_nvm_check_read_request", u32,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("buffer", pointer, currentProgram))
        .setComment("Check handle with api6/allow_zero0. If valid, evaluate BOTH pending "
            + "and buffer checks, even when pending; return0 iff both pass, else1.");
    semanticFunction(0x743F8L, "f33_nvm_check_write_inhibit", u32,
        new ParameterImpl("logical_handle", u16, currentProgram))
        .setComment("Set service6 state1, reject exactly write_inhibit1 and set state2. "
            + "Call ordinary service notifier; target747DE is JMP LP. No mutex or "
            + "flash protection claim. Values0/2/FF pass.");
    semanticFunction(0x74422L, "f33_nvm_check_write_request", u32,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("buffer", pointer, currentProgram))
        .setComment("Api7 handle check, then pending and buffer checks; only when both "
            + "pass evaluate write-inhibit. Return0 iff all pass.");
    semanticFunction(0x73FE8L, "f33_nvm_enqueue_read", u32,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("destination", pointer, currentProgram))
        .setComment("Validate then72E2E(A1A62093,handle,destination,NULL). Return0 "
            + "means queued, NOT data acquired or completion. Payload need not be "
            + "initialized/aligned at this layer; successful result becomes pending2.");
    semanticFunction(0x74014L, "f33_nvm_enqueue_write", u32,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("source", pointer, currentProgram))
        .setComment("Validate then72E2E(22AA8A36,handle,NULL,source). Return0 means "
            + "queued, not flash committed. Source is not dereferenced here.");
  }
  private void annotateNvmStartup() throws Exception {
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    semanticFunction(0x632B2L, "f33_clear_application_ram_4k", VoidDataType.dataType)
        .setComment("Zero1024 words atFEBE7000..FEBE7FFF; preserve adjacent words. "
            + "Actual5122-instruction call, distinct from the boot96KiB LocalRAM clear.");
    semanticFunction(0x679B8L, "f33_nvm_initialize_family1_application", VoidDataType.dataType)
        .setComment("For49 request cells write stateFF/objectFFFF, preserving byte+1. "
            + "For16 objects zero checksum seed, publish status0/55/AA and clear "
            + "floor(payload_bytes/4) words through the application descriptor. "
            + "Includes disabled descriptors' buffers. Clear0686..068A and068E, "
            + "set active object068C=FFFF; preserve068B and unrelated completion/staging. "
            + "Native full call2115 instructions; no flash acquisition.");
    semanticFunction(0x681F8L, "f33_nvm_initialize_acquisition", VoidDataType.dataType)
        .setComment("Clear family0/1 completion; set family0 objectsFFFF/counters0; clear "
            + "0690..0694, four failure masks, write staging, four read stages and "
            + "both1024-byte buffers0708/0C88. Then call79B1E,73F0A,764E2; "
            + "no lower initialization result is propagated. Native19535 instructions "
            + "with explicit ICU-S zero and externally completed FACI forced stop. "
            + "ICU-S bit0 rejection still returns after RAM initialization, preserving "
            + "prior6CB0/6CB2/6CB3 and setting6CB1=1. Not acquired application data.");
    semanticFunction(0x68324L, "f33_nvm_submit_bulk_reads", u32)
        .setComment("For family1 completion!=5A and nonFFFF first handle, submit "
            + "base/base+4/base+8 to slot(object&3) raw/55/AA destinations, ignoring "
            + "each enqueue result, then set completionFF. No family busy gate or "
            + "payload access. Family0 noncomplete/nonFFFF descriptors enqueue each "
            + "inclusive first..low16(first+count-1) handle to shared0C88, ignoring "
            + "admission results, then set objectFFFF/counter0 and completionFF. "
            + "ReturnFF if any eligible object attempted, otherwise0. Native all "
            + "registered families enqueue89 requests, leave33 free slots and preserve "
            + "staging; pending-copy rejection and already-complete arrays also checked. "
            + "No local overflow/range guard; malformed count can wrap the handle loop.");
    semanticFunction(0x68626L, "f33_nvm_submit_family1_read_copies", u32,
        new ParameterImpl("object", u16, currentProgram))
        .setComment("Read descriptor before gating on busy0 and first handle!=FFFF; "
            + "no local object bound. Submit three copies through73FE8, ignore their "
            + "return values, set busyFF and slot failure mask005A5A5A, return0. "
            + "Rejected gate returnsFF. Preserve completion byte and staging; this "
            + "is submission, not acquired data or completed restoration.");
    semanticFunction(0x78CE6L, "f33_faci_force_stop_and_poll", u32)
        .setComment("If FSTATR.ILGLERR and FASTAT!=10, write FASTAT10. IssueB3, "
            + "then793F0(FSTATR,8000,8000,E5); return0 for poll0/1, else8. "
            + "Actual mask precedence makes poll1 unreachable for these identical masks. "
            + "No P/E entry/exit or automatic completion; native timeout1859 instructions "
            + "and explicit hypothetical completion111 instructions.");
    semanticFunction(0x7936EL, "f33_nvm_initialize_dataflash_read_controls", VoidDataType.dataType)
        .setComment("Write EEPRDCYCL=F, DFECCCTL=4000, DFERRINT=0, DFTSTCTL=4000. "
            + "Manual PROT01 keys are not retained: normal ECC enabled, ECC test "
            + "disabled, notification enables cleared. Eight native instructions "
            + "from nonzero control state; no physical timing or ECM delivery proof.");
    semanticFunction(0x793F0L, "f33_poll_word_masks", u32,
        new ParameterImpl("word", new PointerDataType(u32, 4), currentProgram),
        new ParameterImpl("first_mask", u32, currentProgram),
        new ParameterImpl("second_mask", u32, currentProgram),
        new ParameterImpl("attempts", u32, currentProgram))
        .setComment("Read one full word each iteration. First-mask intersection returns0; "
            + "otherwise second-mask intersection returns1. If neither, decrement the "
            + "32-bit attempt count and return2 when it reaches0. Zero count does not "
            + "skip the first read; absent a match it wraps. Not masked equality, elapsed "
            + "time, or a second independent read. Native precedence/second/exhaustion/zero "
            + "cases plus the real forced-stop polling loop.");
  }
  private void annotateNvmPhysicalResults() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    StructureDataType classes = new StructureDataType(category, "F33NvmPhysicalResultClass", 0);
    classes.setPackingEnabled(true);
    classes.add(u32, "raw_result", "Exact full32 comparison; FFFF0000 is not0000FFFF.");
    classes.add(u8, "mode1_class", "Selected when completion mode6C4B equals1.");
    classes.add(u8, "other_class", "Selected otherwise; only mode2 is subsequently dispatched.");
    classes.add(Undefined2DataType.dataType, "opaque_06", "Not read by77D66.");
    semanticData(0x27C38L, new ArrayDataType(resolve(classes), 8, 8),
        "f33_nvm_physical_result_classes", "Eight full32 result/class pairs; unmatched result classFD. "
        + "These classes are not operation-notification events.");
    StructureDataType masks = new StructureDataType(category, "F33NvmDiagnosticMaskMap", 0);
    masks.setPackingEnabled(true);
    masks.add(u32, "source_mask", "Any intersecting input bit selects this row.");
    masks.add(u32, "destination_mask", "OR into the full32 result; not first-match lookup.");
    semanticData(0x27CE4L, new ArrayDataType(resolve(masks), 17, 8),
        "f33_nvm_diagnostic_mask_map", "Seventeen rows consumed by79826. Input8000 maps80000000; "
        + "input01000000 reaches the final row and maps00020000. Unmapped bits contribute nothing.");
    semanticData(0xFEBF6B73L, u8, "f33_nvm_physical_attempt_flags",
        "7697E sets bit0 when completion raw result is not1; other bits retain independent writers.");
    semanticData(0xFEBF6B76L, u8, "f33_nvm_physical_result_state",
        "76554 accepts0/1/2/4 unconditionally and3 only from2; others ignored. Not an OEM enum.");
    semanticData(0xFEBF6C10L, u32, "f33_nvm_completion_raw_result",
        "77D66 compares full32 before cleanup; distinct from callback-published result6C1C.");
    semanticData(0xFEBF6C3CL, u16, "f33_nvm_completion_storage_handle",
        "77D66 dispatches only below123; reset storesFFFF.");
    semanticData(0xFEBF6C4BL, u8, "f33_nvm_completion_mode",
        "Only1/2 dispatch the result class; do not infer read/write direction solely from the number.");
    semanticData(0xFEBF6C4CL, u8, "f33_nvm_completion_side_status",
        "77D46 maps1->source mask2 and2->source mask1 before the mode/handle dispatch gate.");
    semanticData(0xFEBF6CC0L, u32, "f33_nvm_service_diagnostic_mask",
        "Sticky OR of translated bits for service6..8,C/D,16..18.");
    semanticData(0xFEBF6CC8L, u32, "f33_nvm_service_cd_diagnostic_mask",
        "Additional sticky OR only for serviceC/D; not overwritten by the general accumulator.");
    semanticData(0xFEBF6CCCL, u8, "f33_nvm_diagnostic_service",
        "Byte selector consumed by7971C; unrelated to application family or physical result class.");
    semanticFunction(0x76554L, "f33_nvm_set_physical_result_state", VoidDataType.dataType,
        new ParameterImpl("state", u8, currentProgram))
        .setComment("Low8 input0/1/2/4 stores unconditionally;3 stores only if old6B76==2. "
            + "All other values preserve the byte. Native guarded, unguarded, high-bit and ignored cases.");
    semanticFunction(0x76722L, "f33_nvm_publish_physical_class", VoidDataType.dataType,
        new ParameterImpl("result_class", u8, currentProgram))
        .setComment("Low8 class0 sets6B76=0 and calls76ACE. Class83 sets4; other nonzero "
            + "classes set1, report the class and call76ADA. Their73CA0/73CA2 targets are "
            + "JMPLP leaves, not logical publication. Extra r7/r8/r9 prepared by77D66 "
            + "are not consumed in this implementation.");
    semanticFunction(0x7697EL, "f33_nvm_mark_physical_attempt_error", VoidDataType.dataType)
        .setComment("SET1 bit0 of6B73; preserve other bits. Invoked before completion dispatch gates.");
    semanticFunction(0x769F6L, "f33_nvm_report_class_byte", VoidDataType.dataType,
        new ParameterImpl("result_class", u8, currentProgram))
        .setComment("Zero-extend low8 then forward to76A3A; no independent event or callback semantics.");
    semanticFunction(0x76A1CL, "f33_nvm_accumulate_side_status", VoidDataType.dataType,
        new ParameterImpl("status", u32, currentProgram))
        .setComment("Full32 input0->source mask1,1->2,other->8000; call7971C. "
            + "Unlike the class mapper this input is not truncated to a byte.");
    semanticFunction(0x76A3AL, "f33_nvm_accumulate_result_class", VoidDataType.dataType,
        new ParameterImpl("result_class", u8, currentProgram))
        .setComment("Low8 classes21/22/FD->source mask8,7F->4,81->20,83->40,FF->10, "
            + "other->8000. Then actual7971C translation and service-specific sticky OR. "
            + "Class0 is not special here;76722 skips this mapper for class0.");
    semanticFunction(0x76AC0L, "f33_nvm_report_physical_class", VoidDataType.dataType,
        new ParameterImpl("result_class", u8, currentProgram))
        .setComment("Zero-extend low8 and forward through769F6 to the class-mask mapper.");
    semanticFunction(0x77BECL, "f33_nvm_reset_completion_context", VoidDataType.dataType)
        .setComment("Zero6C4C,6C10,6C4B; set6C3C=FFFF; store identity(0) into6C14/6C18. "
            + "Preserve published result6C1C, selector6C4A and unrelated fields. "
            + "Native whole-context canaries verify cleanup after both dispatched and rejected results.");
    semanticFunction(0x77D2EL, "f33_nvm_mark_non_success_result", VoidDataType.dataType)
        .setComment("Full32 completion result6C10!=1 sets6B73.bit0 through7697E; no other gate.");
    semanticFunction(0x77D46L, "f33_nvm_report_completion_side_status", VoidDataType.dataType)
        .setComment("Side byte6C4C==1 calls76A1C(1);==2 calls76A1C(0); others do nothing. "
            + "77D66 calls this before validating completion mode/handle.");
    semanticFunction(0x77D66L, "f33_nvm_finish_physical_result", VoidDataType.dataType)
        .setComment("Mark non1 result, scan8 full32 rows at27C38, default classFD; report "
            + "side status before dispatch gates. Modes1/2 and storage handle<123 call76722. "
            + "Mode1 loads6C14 into r7; mode2 loads6C18; no pointee is read by the consumer. "
            + "Always zero6C20 and reset completion context, even on invalid mode/handle. "
            + "Native both columns, unknown fullword, last/invalid handle, side effects and preserved gaps.");
    semanticFunction(0x7971CL, "f33_nvm_accumulate_diagnostic_mask", VoidDataType.dataType,
        new ParameterImpl("source_mask", u32, currentProgram))
        .setComment("Translate through79826 first. Service byte6CCC in6..8 or16..18 "
            + "ORs6CC0; C/D OR both6CC0 and6CC8; other services leave both unchanged. "
            + "Preserve existing mask bits; neither mask is a logical/application completion code.");
    semanticFunction(0x79826L, "f33_nvm_translate_diagnostic_mask", u32,
        new ParameterImpl("source_mask", u32, currentProgram))
        .setComment("Scan all17 {input_mask,output_mask} rows at27CE4. If input intersects "
            + "the row mask, OR its output into r10, initially0. Full32 input/output; "
            + "unmapped bits ignored. Missing input/return types previously hid the work "
            + "as an empty loop in C; actual native composite/high-output/unmapped cases verify it.");
  }
  private void annotateNvmPageClassification() throws Exception {
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType pageOut = new PointerDataType(u16, 4);
    StructureDataType resultMap = new StructureDataType(
        new CategoryPath("/CamryF33"), "F33NvmByteResultMap", 0);
    resultMap.setPackingEnabled(true);
    resultMap.add(u8, "key", "Compare the zero-extended low8 input.");
    resultMap.add(Undefined3DataType.dataType, "opaque_01", "Not read by74912.");
    resultMap.add(u32, "result", "Full32 return; FFFF0000 differs from0000FFFF.");
    DataType mapType = resolve(resultMap);
    semanticData(0x27934L, new ArrayDataType(mapType, 11, 8),
        "f33_nvm_saved_driver_result_map", "74932 translates saved byte6B21; key5->FFFF0000.");
    semanticData(0x2798CL, new ArrayDataType(mapType, 11, 8),
        "f33_nvm_read_driver_result_map", "7494C translates its low8 input; key5->1. "
        + "Distinct namespace from saved driver status, despite shared lookup mechanics.");
    semanticData(0x27CC8L, u16, "f33_nvm_region_first_page",
        "Registered direct-operation region starts at page0. Read and erase consumers have distinct bounds checks.");
    semanticData(0x27CCAL, u16, "f33_nvm_region_page_count",
        "Registered480 pages, byte region0..77FF; not the complete physical DataFlash capacity.");
    semanticData(0xFEBF0693L, u8, "f33_nvm_direct_operation_request",
        "Exact5A requests direct-operation mode through79D46/79CE2 for both page classification and span erasure.");
    semanticData(0xFEBF6B22L, u8, "f33_nvm_driver_block_latch",
        "Any nonzero value blocks74A36; separate from lower status6CB1==80.");
    semanticData(0xFEBF6B23L, u8, "f33_nvm_driver_phase",
        "74A5A admits only zero after the block-latch/lower-status checks.");
    semanticData(0xFEBF6B72L, u8, "f33_nvm_secondary_result_state",
        "7680C stores0/1/4/6 unconditionally;5 only from1. Other low8 values ignored.");
    semanticData(0xFEBF6CDCL, u8, "f33_nvm_direct_operation_mode",
        "79CE2 stores55 for request0693==5A. Exit cancels before storing0. Shared by classification and erasure; "
        + "not a read-only guarantee or the returned busy indication from79C9E.");
    semanticFunction(0x68A6CL, "f33_nvm_classify_family1_pages", u32,
        new ParameterImpl("object", u16, currentProgram))
        .setComment("Reject object>=16 or descriptor first_handleFFFF withFF before changing "
            + "probe mode. Set0693=5A and reconcile; translate logical base/+4/+8 through747E0 "
            + "and classify64 bytes at page<<6. Continue only on class2; all three2->5A, "
            + "first3->0, mapping failure/other classes->FF. Clear0693 and reconcile on every "
            + "admitted exit. That exit invokes real physical cancellation, can issue B3, "
            + "and sets logical phase8 if operation state2. No application payload publication; "
            + "0 is not checksum/ECC integrity proof. Native first/last nonblank and all-blank "
            + "cases use explicit FACI completion and a separate cancellation completion.");
    semanticFunction(0x747E0L, "f33_nvm_get_logical_storage_page", u32,
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("page_out", pageOut, currentProgram))
        .setComment("Accept low16 logical2..123, load logical descriptor+8 storage handle, "
            + "then784E2 writes its page through the unchanged r7 pointer. Return0; invalid "
            + "logical returns1 without touching output. Explicit output contract repairs "
            + "the formerly missing pointer argument in C.");
    semanticFunction(0x784E2L, "f33_nvm_get_storage_page", u32,
        new ParameterImpl("storage_handle", u16, currentProgram),
        new ParameterImpl("page_out", pageOut, currentProgram))
        .setComment("Unchecked low16 storage index into six-byte descriptors at27634; "
            + "write row.page as one halfword through r7 and return0. Caller747E0 supplies "
            + "the logical namespace admission; do not conflate logical and storage handles.");
    semanticFunction(0x795D4L, "f33_nvm_probe_range_rejected", u32,
        new ParameterImpl("byte_offset", u32, currentProgram),
        new ParameterImpl("byte_count", u32, currentProgram))
        .setComment("Return1 unless first_page!=FFFF and unsigned offset is within "
            + "[first_page*64,(first_page+page_count)*64-1] and count fits the remaining span. "
            + "Exact region0..77FF. Zero length is allowed only with an in-region start; "
            + "no alignment check or64-byte local-buffer bound is imposed here.");
    semanticFunction(0x79594L, "f33_nvm_classify_storage_range", u32,
        new ParameterImpl("ignored_selector", u32, currentProgram),
        new ParameterImpl("byte_offset", u32, currentProgram),
        new ParameterImpl("byte_count", u32, currentProgram))
        .setComment("First ABI input unused. Return4 if6CDC==0 or795D4 rejects. Otherwise "
            + "call76930 and preserve only2/3/6/9; map other results to4. This performs "
            + "synchronous classification, not a queue submission.");
    semanticFunction(0x76930L, "f33_nvm_probe_storage_range", u32,
        new ParameterImpl("byte_offset", u32, currentProgram),
        new ParameterImpl("byte_count", u16, currentProgram))
        .setComment("Enter paired-call guard79AAA; nonzero6CD0 returns9 without reading. "
            + "Otherwise call74D78(offset,low16 count,64-byte local buffer,1): result1->3, "
            + "3->2,FFFF0000->6,other->4. Always79ABE before return. 68A6C passes64; "
            + "the surrounding region check is not a local-buffer-size check.");
    semanticFunction(0x74A36L, "f33_nvm_sync_access_blocked", u32)
        .setComment("Return1 if6B22!=0; otherwise return whether lower status6CB1 equals80. "
            + "The first branch does not read6CB1.");
    semanticFunction(0x74A5AL, "f33_nvm_sync_admission_result", u32)
        .setComment("74A36 true->FFFF0000; otherwise6B23==0->1, nonzero->0000FFF9. "
            + "These are full32 results, not pointers.");
    semanticFunction(0x74D78L, "f33_nvm_read_with_optional_blank_check", u32,
        new ParameterImpl("byte_offset", u32, currentProgram),
        new ParameterImpl("byte_count", u16, currentProgram),
        new ParameterImpl("destination", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("blank_option", u8, currentProgram))
        .setComment("Only admission result1 proceeds; any other result collapses toFFFF0000. "
            + "Then set6B20/6B21=FF. Exact low8 option1 calls74D0C; only its result4 proceeds "
            + "to74D40 read, other results return without copy. Other option bytes read directly. "
            + "Low16 count; native option2/high-bit truncation, blank no-copy, and both rejection gates.");
    semanticFunction(0x74D0CL, "f33_nvm_map_blank_check_result", u32,
        new ParameterImpl("byte_offset", u32, currentProgram),
        new ParameterImpl("byte_count", u16, currentProgram))
        .setComment("Actual7892A blank check: result2->3,7->4; other results translate "
            + "through7494C and pass74CD2 classification to74CE8 for side effects. "
            + "Result4 here means continue into the reader, not a completed read.");
    semanticFunction(0x74912L, "f33_nvm_lookup_byte_result", u32,
        new ParameterImpl("key", u8, currentProgram),
        new ParameterImpl("rows", new PointerDataType(mapType, 4), currentProgram),
        new ParameterImpl("row_count", u32, currentProgram))
        .setComment("Scan row_count eight-byte entries in order; first low8 key match "
            + "returns full32 row+4. Exhaustion, including count0, returnsFFFFFFFF.");
    semanticFunction(0x74932L, "f33_nvm_translate_saved_driver_result", u32)
        .setComment("Translate saved byte6B21 through11 rows at27934 and preserve74912's "
            + "full32 return. KeyFF->0; key5->FFFF0000, unlike direct read-result key5.");
    semanticFunction(0x7494CL, "f33_nvm_translate_read_driver_result", u32,
        new ParameterImpl("driver_result", u8, currentProgram))
        .setComment("Translate low8 input through11 rows at2798C and preserve74912's full32 "
            + "return. Key5->1; keyC reaches the final row; unknown keyA->FFFFFFFF.");
    semanticFunction(0x79CE2L, "f33_nvm_refresh_direct_probe_mode", u32)
        .setComment("Request0693 exactly5A stores/returns55. Otherwise, if old6CDC!=0, "
            + "call741D0->72248->73C4A->7664E before storing/returning0. This exit can "
            + "perform real cancellation/B3; it is not a pure flag refresh.");
    semanticFunction(0x79C9EL, "f33_nvm_reconcile_probe_mode", u32)
        .setComment("Sample79AF0 (including its redundant-state check), then refresh79CE2. "
            + "If sampled6CD0!=0 return55 even when stored6CDC becomes0; otherwise return "
            + "the refreshed mode. Native exact5A/non5A and interference-with-cancellation cases.");
    semanticFunction(0x79CB8L, "f33_nvm_poll_probe_mode", u32)
        .setComment("Preserve79C9E's return through the real call. 68A6C invokes this at68AA0 "
            + "and68B24, around the whole classifier, not around each of its three page probes.");
    semanticFunction(0x73C4AL, "f33_nvm_cancel_logical_operation", VoidDataType.dataType)
        .setComment("Call physical cancellation7664E first; then if6B00==2 set6AFC=8. "
            + "72248 calls this before inspecting its own module marker. Native classifier "
            + "mode exit exercises the active and inactive logical-operation cases.");
    semanticFunction(0x7664EL, "f33_nvm_cancel_physical_operation", VoidDataType.dataType)
        .setComment("Reset completion context77C32 and both registered banks782DE. Enter "
            + "79AAA, clear6B77; if6CD0==0 call74E94 (actual lower cancellation) then set6B77=1, "
            + "ignoring74E94's result. Leave79ABE; request primary state3 and secondary state5, "
            + "then76ADA's no-op hook. Native explicit B3 completion and interference skip; "
            + "B3 timeout reaches command-area halfword reads not yet modeled.");
    semanticFunction(0x7680CL, "f33_nvm_set_secondary_result_state", VoidDataType.dataType,
        new ParameterImpl("state", u8, currentProgram))
        .setComment("Low8 states0/1/4/6 store6B72 unconditionally;5 only from old1; "
            + "others preserve it. Native guarded accept/reject, high input bits,6 and unknown2.");
  }
  private void annotateNvmAcquisition() throws Exception {
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType bytes = new PointerDataType(u8, 4);
    semanticData(0x2AD76L, u16, "f33_nvm_classification_budget",
        "18 charged64-byte chunks per acquisition pass; shared across family0 then family1.");
    semanticData(0x2AD78L, u16, "f33_nvm_acquisition_service_steps",
        "18 real79C60 calls per nonzero initial-read token.");
    semanticData(0x2AD7AL, u16, "f33_nvm_initial_acquisition_limit",
        "88 calls at most; exhaustion clears0673 without guaranteeing completion.");
    semanticData(0xFEBF0670L, u8, "f33_nvm_work_hold",
        "66C5C repairs this triplet with fallback0; decoded5A suppresses work selection/progression.");
    semanticData(0xFEBF10A8L, u8, "f33_nvm_work_hold_xor55",
        "Application-phase encoded replica of0670.");
    semanticData(0xFEBF10CCL, u8, "f33_nvm_work_hold_xorAA",
        "Application-phase encoded replica of0670.");
    semanticData(0xFEBF0673L, u8, "f33_nvm_acquisition_phase",
        "66B16 handles0/33/55/AA/CC. Recognized nonzero entry returns busy1 even when this call clears phase.");
    semanticData(0xFEBF0676L, u16, "f33_nvm_family0_scan_cursor",
        "675A4 resumes object-status classification at this registered-object index.");
    semanticData(0xFEBF0678L, u16, "f33_nvm_family0_probe_offset",
        "Partial-object offset. Full-object path clears it; registered max cost12 makes the split path unreachable under budget18.");
    semanticData(0xFEBF067DL, u8, "f33_nvm_family0_classification_latch",
        "675A4 sets5A on68946 result0, including a blocked probe; not proof of nonblank or valid payload.");
    semanticData(0xFEBF0680L, u8, "f33_nvm_family0_phase",
        "Snapshot by66C5C before hold decoding and acquisition progression.");
    semanticData(0xFEBF068EL, u16, "f33_nvm_family1_scan_cursor",
        "67D96 resumes status classification; completion reaches registered count16.");
    semanticData(0xFEBF0690L, u8, "f33_nvm_family0_busy",
        "Read/write arming requires0 and setsFF independently of enqueue success; completed callback clears it.");
    semanticData(0xFEBF0692L, u8, "f33_nvm_initial_read_token",
        "5A arms bulk submission; exactFF completion bytes retain a nonzero token. Not an all-success predicate.");

    semanticFunction(0x68B2EL, "f33_nvm_handle_family0_read_result", u32,
        new ParameterImpl("result", u8, currentProgram),
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("record", bytes, currentProgram))
        .setComment("Resolve unchecked route object/descriptor. Nonzero result retries "
            + "below2 via real73FE8, increments shared0694 regardless enqueue result, "
            + "returns0 before finalization; exhaustion clears retry and skips copy. "
            + "Success clears retry, reads sequence at fixed0C88, inverse trailer at "
            + "record+3C for payload<=56, else record+low16(payload+4); accept inverse match and no selection "
            + "or unsigned sequence delta<=C0000000. Copy exactly payload bytes from "
            + "record+4 immediately, then update sequence/selection. At handle>=low16"
            + "(first+count-1), completion is5A iff any selection exists elseA5, and "
            + "return5A for either outcome; otherwise0. Native early/long publication, "
            + "bad inverse, delta boundary and retry rejection/exhaustion through68E9E.");
    semanticFunction(0x68C5EL, "f33_nvm_handle_family0_write_result", u32,
        new ParameterImpl("result", u8, currentProgram),
        new ParameterImpl("logical_handle", u16, currentProgram))
        .setComment("Unchecked route object/descriptor. Expected member is low16"
            + "(selection+1), wrapping to first on oldFFFF or past descriptor end. "
            + "Only result0 and exact expected handle update selection and completion5A; "
            + "otherwise completionA5. Always return5A, causing router busy release "
            + "even on failure. No third argument, sequence/payload update or local retry.");
    semanticFunction(0x684D0L, "f33_nvm_arm_family0_read", u32,
        new ParameterImpl("object", u16, currentProgram))
        .setComment("Read descriptor before busy0/first!=FFFF gate; no local object "
            + "bound. Enqueue inclusive first..low16(first+count-1) reads to shared0C88, "
            + "ignore every return, then selectionFFFF/sequence0/completionFF/busyFF. "
            + "Return0 on local admission even if all reads reject, elseFF. "
            + "Malformed ranges may wrap; registered ranges are bounded.");
    semanticFunction(0x6853EL, "f33_nvm_arm_family0_write", u32,
        new ParameterImpl("object", u16, currentProgram))
        .setComment("Busy0 and nonFFFF descriptor admit; no local object bound. Choose "
            + "selected successor/wrap, increment sequence modulo32, write LE sequence "
            + "header at0708, payload at+4, zero short padding through+3B, inverse "
            + "sequence at+3C for payload<=56, else+low16(payload+4). Real74014 result is ignored; "
            + "save incremented sequence and completion/busyFF, return0. Selection "
            + "changes only on completion. Native rejected enqueue still builds the "
            + "exact envelope and wraps sequence; rejection of local gate returnsFF.");
    semanticFunction(0x6892AL, "f33_nvm_get_family0_completion", u32,
        new ParameterImpl("object", u16, currentProgram))
        .setComment("Bound low16 object by registered32; return zero-extended0338 byte, "
            + "orA5 without reading completion RAM when out of range.");
    semanticFunction(0x68946L, "f33_nvm_classify_family0_chunks", u32,
        new ParameterImpl("object", u16, currentProgram),
        new ParameterImpl("chunk_offset", u16, currentProgram),
        new ParameterImpl("chunk_count", u16, currentProgram))
        .setComment("Reject invalid/disabled object or last-member page-map error withFF "
            + "before mode changes. Otherwise base=(low16(mapped_last_page+offset)<<6); "
            + "set0693=5A/reconcile once, probe count64-byte chunks in ascending order. "
            + "Continue only on class2; every other class yields0, including driver "
            + "errors, unlike68A6C. All2 or count0 yields5A. Clear/reconcile once, "
            + "including real cancellation. Native blank/nonblank, blocked, zero-count "
            + "and invalid-object paths; explicit FACI inputs do not prove blankness.");
    semanticFunction(0x689DEL, "f33_nvm_family0_chunk_cost", u32,
        new ParameterImpl("payload_bytes", u16, currentProgram))
        .setComment("Return max(2,(low16(payload_bytes+20)+63)>>6). Truncate before "
            + "rounding, not after. Native108->2,109->3,FFEC->2 with high input bits. "
            + "Multiply by descriptor logical_count for full-object scan charge.");
    semanticFunction(0x675A4L, "f33_nvm_classify_family0_pass", u32,
        new ParameterImpl("charged_out", new PointerDataType(u16, 4), currentProgram))
        .setComment("Resume0676 with fresh charge0. Completion5A publishes status10 "
            + "without charge or payload access. Otherwise cost=low16(count*689DE"
            + "(payload)); admit full object while cost+charge<=ROM18, charge before "
            + "68946. Result0 publishes30 and latches067D=5A, including blocked reads; "
            + "other full-object results publish11. Stop before exceeding budget. "
            + "Generic split branch requires fresh charge0 and object cost>18; all32 "
            + "registered costs<=12 make it unreachable here. Store cursor/offset and "
            + "halfword charge; return5A iff cursor>=32. Native disabled charge4, "
            + "blocked valid-object charge6 and free completed-object publication.");
    semanticFunction(0x67D96L, "f33_nvm_classify_family1_pass", u32,
        new ParameterImpl("already_charged", u16, currentProgram))
        .setComment("Resume068E. Completion5A publishes live-RAM checksum/status10 "
            + "without charge. Otherwise add3 modulo16; stop if aboveROM18, else "
            + "call68A6C and choose30 only for result0,11 for every nonzero result. "
            + "Publish all three planes, advance cursor, store068E; return5A iff "
            + "cursor>=16. No pending-cell override. Native exact/over-budget, "
            + "disabled and real last-object blank/nonblank classification.");
    semanticFunction(0x6842CL, "f33_nvm_retain_token_while_reads_pending", u32,
        new ParameterImpl("token", u8, currentProgram))
        .setComment("Scan registered16 family1 bytes then32 family0 bytes. Any exactFF "
            + "retains low8 token; noFF returns0. Early exit on pending family1 "
            + "avoids family0 reads. NonFF failure values do not retain the token.");
    semanticFunction(0x68488L, "f33_nvm_step_initial_read_acquisition", u32)
        .setComment("Token0692==5A invokes68324 and replaces the local token with its "
            + "result. Every nonzero token executes exactlyROM18 real79C60 calls, "
            + "then6842C; store/return resulting token. Native no-work/completed and "
            + "pending cases use the real uninitialized-service gate. Initialized "
            + "driver scheduling remains outside these native proofs.");
    semanticFunction(0x684C6L, "f33_nvm_arm_initial_read_acquisition", VoidDataType.dataType)
        .setComment("Store only5A to0692; does not submit or complete any request.");
    semanticFunction(0x66B16L, "f33_nvm_step_acquisition_pass", u32)
        .setComment("State0673:0 idle;33 calls68488 and advances55 only on0, returning "
            + "without classification that call.55 runs675A4 and, on completion, "
            + "advancesAA and forwards its charge to67D96 in the same call. EntryAA "
            + "uses fresh charge0. Completed67D96 or entryCC calls670C4 and clears "
            + "state. Recognized nonzero entry always returns1, including finalization; "
            + "invalid state clears/returns0. Native finalization includes actual ROM "
            + "CRC failures in groups1/3 and still clears state/returns1. Complete "
            + "initialized physical acquisition remains outside these proofs.");
    semanticFunction(0x66B96L, "f33_nvm_run_bounded_initial_acquisition", VoidDataType.dataType)
        .setComment("Set0673=33 and arm0692=5A. Call66B16 at mostROM88 times, stopping "
            + "early on0; always clear0673 afterward. Native88-tick exhaustion leaves "
            + "three pending reads in distinct logical queues,0692FF and no dequeue "
            + "under real service-state0 rejection. Not successful acquisition.");
    semanticFunction(0x66C5CL, "f33_nvm_select_acquisition_work", u32,
        new ParameterImpl("current_work", u8, currentProgram))
        .setComment("Snapshot family phases before repairing0670/10A8/10CC with "
            + "fallback0. Decoded5A returns0. Idle acquisition with an active phase "
            + "selects2 for family1 before1 for family0. Otherwise step66B16; busy "
            + "preserves current work. On idle completion,67B58==1 selects2, else "
            + "6740A==1 selects1, else preserve work. Native hold repair/fallback "
            + "and phase priority; request selectors have separate native edge proofs.");
    semanticFunction(0x679B2L, "f33_nvm_get_family0_phase", u32)
        .setComment("Return zero-extended byte0680; snapshot precedes hold decoding.");
    semanticFunction(0x681F2L, "f33_nvm_get_family1_phase", u32)
        .setComment("Return zero-extended byte0689; snapshot precedes hold decoding.");
    semanticFunction(0x79C60L, "f33_nvm_service_acquisition_driver", VoidDataType.dataType)
        .setComment("Real wrapper of74164, not a replacement readiness callback. "
            + "Native polling/budget cases exercise its service-state rejection; "
            + "74164 also has initialized scheduler/terminal-state proofs, not a "
            + "whole physical-acquisition proof.");
    semanticFunction(0x74164L, "f33_nvm_service_logical_and_physical_driver", VoidDataType.dataType)
        .setComment("Return if79470(14) or72148 rejects. Otherwise79A50,79C9E; only "
            + "mode result0 invokes73B2C(1),72EEA. Then79C4C(mode_result!=0),79A94. "
            + "Native uninitialized exit, initialized quiet scan/wrap, mode blocking "
            + "and explicit terminal phases8/10/20. Queued work is bounded at726C4; "
            + "deferred notification at7990E. No physical flash progress claim.");
    semanticFunction(0x72148L, "f33_nvm_service_uninitialized", u32)
        .setComment("Return full32 boolean(6102!=F0). Native service-state0 rejects "
            + "scheduler progress; queue admission itself is a different contract.");
    semanticFunction(0x79470L, "f33_nvm_driver_gate_rejected", u32,
        new ParameterImpl("ignored_service", u16, currentProgram))
        .setComment("Mask input16, call79D2E and normalize nonzero to1. Exact target "
            + "hook always returns0, so this is not an additional live readiness check.");
    semanticFunction(0x79D2EL, "f33_nvm_driver_gate_hook", u32)
        .setComment("Exact MOV0,r10;JMPLP. No argument reads or hardware access.");
  }
  private void annotateNvmRequestSelection() throws Exception {
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType byteOut = new PointerDataType(u8, 4);
    semanticData(0xFEBF067AL, u8, "f33_nvm_family0_request_producer", "Byte index into65 cells.");
    semanticData(0xFEBF067BL, u8, "f33_nvm_family0_request_consumer", "Advanced even for invalid consumed objects/kinds.");
    semanticData(0xFEBF067EL, u8, "f33_nvm_family0_span_request", "Exact5A selects the mapped-span branch.");
    semanticData(0xFEBF0680L, u8, "f33_nvm_family0_phase", "Selector stores11/22/33; not an OEM enum.");
    semanticData(0xFEBF0682L, u16, "f33_nvm_family0_active_object", "Set only for valid read/write selection.");
    semanticData(0xFEBF0686L, u8, "f33_nvm_family1_request_producer", "Byte index into49 cells.");
    semanticData(0xFEBF0687L, u8, "f33_nvm_family1_request_consumer", "Advanced even for invalid consumed objects/kinds.");
    semanticData(0xFEBF0688L, u8, "f33_nvm_family1_span_request", "Exact5A selects the mapped-span branch.");
    for (long entry : new long[] {0x67350L, 0x67A58L}) {
      String family = entry == 0x67350L ? "0" : "1";
      semanticFunction(entry, "f33_nvm_recover_family" + family + "_request_indices", VoidDataType.dataType,
          new ParameterImpl("producer_out", byteOut, currentProgram),
          new ParameterImpl("consumer_out", byteOut, currentProgram))
          .setComment("If both stored byte indices are below the registered cell "
              + "count, copy them without reading cells. Otherwise start both at0 "
              + "and scan adjacent object halfwords from row1: last occupied-to-empty "
              + "transition selects producer; last empty-to-occupied selects consumer. "
              + "ObjectFFFF alone denotes empty; state is ignored. Store recovered "
              + "indices globally and through outputs. No cell repair or explicit "
              + "last-to-first comparison; all-empty/all-full recover0/0.");
    }
    for (long entry : new long[] {0x673C2L, 0x67ACAL}) {
      String family = entry == 0x673C2L ? "0" : "1";
      semanticFunction(entry, "f33_nvm_advance_family" + family + "_request_index", u32,
          new ParameterImpl("index", u8, currentProgram))
          .setComment("Return low8(index)+1 when index<count-1, otherwise0. Counts "
              + "are65/49 in the registered target. No global index store.");
    }
    semanticFunction(0x673DEL, "f33_nvm_family0_has_request_cell", u32,
        new ParameterImpl("object", u16, currentProgram))
        .setComment("Scan all65 object halfwords at048A+4*i for low16 object; "
            + "return1 on first match else0. Ignore state, queue indices and empty "
            + "sentinel meaning. Native duplicate outside the active interval overrides "
            + "the selector's status even when that cell's state isFF.");
    semanticFunction(0x6740AL, "f33_nvm_select_family0_request", u32)
        .setComment("Recover indices first. Span flag5A calls687DE, ignores return "
            + "and selects phase11/return1 without dequeue. Empty ring returns0. "
            + "Otherwise clear state/object but preserve+1, then advance consumer "
            + "BEFORE object/kind validation. Kind11 calls684D0, selects phase22; "
            + "22 always calls6853E,33 only when completion!=5A; both select phase33. "
            + "Ignore arm return; set active object/status21 and return1. Unknown "
            + "kind publishes32/returns0 without changing phase/active. Any matching "
            + "remaining cell overrides status20. Invalid object only consumes cell. "
            + "Bulk dispatch beyond the computed-span boundary is not proved.");
    semanticFunction(0x67B58L, "f33_nvm_select_family1_request", u32)
        .setComment("Same consume-before-validation and11/22/33 selection contract "
            + "as family0, using68626/6869E and redundant status publication; write "
            + "selection additionally clears068A. Span flag5A selects phase11 "
            + "regardless6889A result. Empty ring scans repaired status triplets "
            + "with fallback12; first status10 with failing live checksum calls68626 "
            + "then stops, but still returns0 and preserves phase/active/completion. "
            + "Native empty-ring failure queues three actual reads while leaving "
            + "prior completion5A; caller reachability/restoration is not inferred.");
    semanticFunction(0x687DEL, "f33_nvm_dispatch_family0_page_span", u32)
        .setComment("Busy nonzero returnsFF. Otherwise map every enabled object's "
            + "logical members; retain minimum/maximum pages and logical owner of "
            + "the first strictly greatest page. Add that owner's chunk cost to "
            + "the maximum; call6879C(min,low16(max+cost-min)). Return its result; "
            + "zero sets busyA5. Exact table computes page10C/count164. Native "
            + "admitted proof stops BEFORE6879C; no completed range operation.");
    semanticFunction(0x6889AL, "f33_nvm_dispatch_family1_page_span", u32)
        .setComment("Busy nonzero returnsFF. Map enabled base/+4/+8 handles, "
            + "accumulating min/max successful pages. Call6879C(min,max+1-min); "
            + "zero result sets busyA5. Exact table computes page1B0/count48. "
            + "Native admitted proof stops BEFORE6879C; no physical operation claim.");
  }
  private void annotateRomGroupIntegrity() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType words = new PointerDataType(u32, 4);
    int count = currentProgram.getMemory().getShort(toAddr(0x2AD74L)) & 0xFFFF;
    StructureDataType descriptor = new StructureDataType(category, "F33NvmFamily2Descriptor", 0);
    descriptor.setPackingEnabled(true);
    descriptor.add(u16, "payload_bytes", "67090 includes four additional bytes, with16-bit length wrap.");
    descriptor.add(u16, "opaque_02", "Not interpreted by the CRC consumer.");
    descriptor.add(words, "ram_buffer", "RAM destination used by other group consumers; NOT CRC source.");
    descriptor.add(words, "rom_record", "CodeFlash source consumed by67090, including its trailing word.");
    semanticData(0x2AF8CL, new ArrayDataType(resolve(descriptor), count, 12),
        "f33_nvm_family2_descriptors", "Eleven12-byte records. Groups1/3 point to zero-filled ROM records.");
    semanticData(0x2AD74L, u16, "f33_nvm_family2_object_count", "Registered count11.");
    semanticData(0xFEBF0650L, new ArrayDataType(u8, count, 1),
        "f33_nvm_family2_status", "670C4 bypasses ROM CRC for repaired10;67176 also publishes10 after a RAM update.");
    semanticData(0xFEBF1098L, new ArrayDataType(u8, count, 1),
        "f33_nvm_family2_status_xor55", "Redundant status plane, not CRC bytes.");
    semanticData(0xFEBF10BCL, new ArrayDataType(u8, count, 1),
        "f33_nvm_family2_status_xorAA", "Redundant status plane, not CRC bytes.");
    semanticFunction(0x67060L, "f33_dcra1_crc_raw_words", u32,
        new ParameterImpl("source", words, currentProgram),
        new ParameterImpl("byte_count", u32, currentProgram),
        new ParameterImpl("raw_seed", u32, currentProgram))
        .setComment("Write CTL00 and COUT raw seed; feed exactly byte_count>>2 "
            + "source words to CIN. Return complement of COUT read. Manual "
            + "R01UH0585EJ0120 pp2844-2852 specifies reflected Ethernet CRC and "
            + "COUT read XOR FFFFFFFF, so firmware returns RAW state, not ordinary "
            + "CRC32. Trailing bytes ignored; count<4 reads no source and returns seed. "
            + "Native real register sequence uses bounded CTL00 hardware model.");
    semanticFunction(0x67090L, "f33_nvm_check_family2_rom_crc", u32,
        new ParameterImpl("group", u16, currentProgram))
        .setComment("Unchecked low16 group indexes12-byte2AF8C descriptor. Feed "
            + "ROM pointer+8 and low16(payload+4) to67060 with raw seedFFFFFFFF. "
            + "Return10 iff raw residue0, otherwise30. Immutable groups1/3 are "
            + "entirely zero-filled and produce842A3990/F02A6472, not valid residues; "
            + "other nine registered records produce0. Not a live RAM checksum.");
    semanticFunction(0x670C4L, "f33_nvm_refresh_family2_status", VoidDataType.dataType)
        .setComment("For11 groups, repair status triplet with fallback30. Exact10 "
            + "bypasses CRC; other values call67090, retry exactly once only on "
            + "non10, then publish last status across all planes. Real all-recompute "
            + "sweep publishes10,30,10,30,10,10,10,10,10,10,10 with399 CIN writes. "
            + "Status10 bypass can preserve prior10 even for the zero-filled groups.");
  }
  private void annotateInitializedNvmService() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType operation = getDataAt(toAddr(0xFEBF6AECL)).getDataType();
    semanticData(0xFEBF6104L, operation, "f33_nvm_scheduler_operation",
        "Same16-byte logical-operation layout; marker9DA70AE7 means idle. Padding+6 is not copied by721C6.");
    semanticData(0xFEBF6124L, u8, "f33_nvm_scheduler_phase",
        "721C6 classifies active phases08/10/20 as terminal status2; other active phases status1.");
    semanticData(0xFEBF6B04L, new PointerDataType(VoidDataType.dataType, 4),
        "f33_nvm_selected_service_poll",
        "73EEE selects767EA for nonzero low8,766F4 for zero. Callback ABI not inferred here.");
    StructureDataType guards = new StructureDataType(category, "F33NvmServiceGuards", 0);
    guards.setPackingEnabled(true);
    guards.add(u8, "service", "79A50 clears;79A94 sets1.");
    guards.add(u8, "paired_call", "79AAA clears;79ABE sets1.");
    guards.add(u8, "deferred", "79A32 consumes asFF only when both preceding bytes equal1.");
    semanticData(0xFEBF6CCDL, resolve(guards), "f33_nvm_service_guards",
        "Recovered byte comparisons, not an inferred mutex or interrupt mask.");
    semanticData(0xFEBF6CDAL, u8, "f33_nvm_service_mode_nonzero",
        "74164 writes mode_result!=0 after conditional scheduling; not the cause of its admission gate.");
    semanticFunction(0x79A32L, "f33_nvm_consume_deferred_guard", VoidDataType.dataType)
        .setComment("Only when6CCD==1 AND6CCE==1, set6CCF=FF; otherwise preserve it.");
    semanticFunction(0x79A50L, "f33_nvm_enter_service_guard", VoidDataType.dataType)
        .setComment("Call79A32 BEFORE storing6CCD=0. No lock or interrupt semantics inferred.");
    semanticFunction(0x79A64L, "f33_nvm_finish_deferred_guard", VoidDataType.dataType)
        .setComment("Only when6CCD==1 AND6CCE==1: call7990E if6CCF==0, then storeFF. "
            + "Native non-notifying branches and exact7990E entry; its body is a "
            + "separate dependency, not a substituted callback.");
    semanticFunction(0x79A94L, "f33_nvm_leave_service_guard", VoidDataType.dataType)
        .setComment("Store6CCD=1 then call79A64. Deferred7990E branch remains bounded at entry.");
    semanticFunction(0x79C4CL, "f33_nvm_store_service_mode_nonzero", VoidDataType.dataType,
        new ParameterImpl("value", u8, currentProgram))
        .setComment("Only store low8 to6CDA. This is NOT a driver pump.");
    semanticFunction(0x73EEEL, "f33_nvm_set_service_poll", VoidDataType.dataType,
        new ParameterImpl("full_service", u8, currentProgram))
        .setComment("Store767EA at6B04 for nonzero low8, otherwise766F4. Does not call the pointer.");
    semanticFunction(0x73B2CL, "f33_nvm_select_service_poll", VoidDataType.dataType,
        new ParameterImpl("full_service", u8, currentProgram))
        .setComment("Zero-extend low8 and call73EEE. Initialized74164 selects the nonzero branch.");
    semanticFunction(0x721C6L, "f33_nvm_snapshot_scheduler_operation", u32,
        new ParameterImpl("output", new PointerDataType(operation, 4), currentProgram))
        .setComment("Marker9DA70AE7 returns0 without output writes or remaining record reads. "
            + "Otherwise return2 for phases08/10/20,1 for other phases; copy marker, "
            + "logical handle and two pointers, preserving output padding+6. SETF "
            + "and MOV establish full32 return. Native idle and terminal compositions.");
    semanticFunction(0x72EEAL, "f33_nvm_service_scheduler", VoidDataType.dataType)
        .setComment("Snapshot via721C6. Idle:73C76==1 calls72E70, otherwise abort72130 "
            + "(lower operation state2). Active status1 calls72ED4; status2 skips it. "
            + "Always finish723D6. Native quiet scans, ascending-header admission "
            + "bounded before726C4, phase08 queue retention and explicit10/20 "
            + "terminal dequeue/recycle/result1/6. These terminal inputs do not prove "
            + "physical programming reached those phases.");
  }
  private void annotateApplicationRecordApis() throws Exception {
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType words = new PointerDataType(u32, 4);
    int count = currentProgram.getMemory().getShort(toAddr(0x2AD74L)) & 0xFFFF;
    semanticData(0xFEBF065BL, new ArrayDataType(u8, count, 1),
        "f33_nvm_family2_setter_flags", "66FFE clears and67176 writes5A. No reader recovered; not a proven persistence flag.");
    semanticFunction(0x66D1AL, "f33_nvm_request_record_refresh", u32,
        new ParameterImpl("selector", u32, currentProgram))
        .setComment("Repair gate0671/10A9/10CD with fallback0; exact5A rejects. Decode family bits8..15 and low8 "
            + "object, ignoring high16. Families0/1 enqueue read-kind11; family2 synchronously refreshes ROM "
            + "status. Return acceptance, not persistence or CRC success.");
    semanticFunction(0x66D6EL, "f33_nvm_set_record", u32,
        new ParameterImpl("selector", u32, currentProgram),
        new ParameterImpl("source", words, currentProgram))
        .setComment("Repair gate0672/10AA/10CE with fallback0; exact5A rejects before source access. Dispatch "
            + "family0/1 RAM update and request admission, or family2 RAM-only update. Unsupported families "
            + "return0; high16 selector bits ignored.");
    semanticFunction(0x66DCAL, "f33_nvm_get_record_status", u32,
        new ParameterImpl("selector", u32, currentProgram))
        .setComment("Dispatch low8 object by selector bits8..15. Family0 reads raw status; family1 votes with "
            + "fallback12; family2 votes with fallback10. Unknown families returnFF; no physical flash read.");
    semanticFunction(0x6768AL, "f33_nvm_family0_request_full", u32,
        new ParameterImpl("producer", u32, currentProgram),
        new ParameterImpl("consumer", u32, currentProgram))
        .setComment("Truncate both indices to low8. Return producer+1==(consumer==0?ROM cell_count65:consumer). No "
            + "cell inspection; reserves one cell.");
    semanticFunction(0x676A4L, "f33_nvm_previous_family0_request", u32,
        new ParameterImpl("index", u32, currentProgram))
        .setComment("Return zero-extended low8 predecessor, with zero wrapping to ROM cell_count65 minus1. No "
            + "general index validation.");
    semanticFunction(0x676BAL, "f33_nvm_enqueue_family0_read", u32,
        new ParameterImpl("object", u32, currentProgram))
        .setComment("Low16 object. Recover indices before full and object<32 gates. Full rejects before duplicate "
            + "detection. Only matching kind11 at predecessor(producer) suppresses insertion, even on an "
            + "empty ring. Otherwise publish status20, kind11/object, and advance producer. Always republish "
            + "producer; recovery may change both indices. Disabled descriptors are not checked.");
    semanticFunction(0x6773AL, "f33_nvm_set_family0_record", u32,
        new ParameterImpl("object", u32, currentProgram),
        new ParameterImpl("source", words, currentProgram))
        .setComment("Recover indices before full/object bounds. Scan consumer through producer inclusively for "
            + "first matching kind22/33; kind11 does not coalesce. Compare/copy payload before queue "
            + "mutation. Changed payload or prior22 selects22, otherwise33. Tail duplicate changes only kind; "
            + "earlier duplicate compacts object/kind, preserving slot opaque bytes, then moves to tail. "
            + "Other admissions publish20. No disabled/busy/completion gate or normal rejection after copy.");
    semanticFunction(0x6792CL, "f33_nvm_get_family0_status", u32,
        new ParameterImpl("object", u32, currentProgram))
        .setComment("Return raw status byte for low16 object<32, otherwiseFF. No mutation or persistence "
            + "inspection.");
    semanticFunction(0x67948L, "f33_nvm_get_family0_record", u32,
        new ParameterImpl("object", u32, currentProgram),
        new ParameterImpl("destination", words, currentProgram))
        .setComment("Low16 object>=32 returnsFF before data access. Otherwise copy descriptor-sized whole words "
            + "from live RAM, then return raw status. No status-before-copy gate, disabled check or physical "
            + "read.");
    semanticFunction(0x67E18L, "f33_nvm_family1_request_full", u32,
        new ParameterImpl("producer", u32, currentProgram),
        new ParameterImpl("consumer", u32, currentProgram))
        .setComment("Truncate both indices to low8. Return producer+1==(consumer==0?ROM cell_count49:consumer). No "
            + "cell inspection; reserves one cell.");
    semanticFunction(0x67E32L, "f33_nvm_previous_family1_request", u32,
        new ParameterImpl("index", u32, currentProgram))
        .setComment("Return zero-extended low8 predecessor, with zero wrapping to ROM cell_count49 minus1. No "
            + "general index validation.");
    semanticFunction(0x67E48L, "f33_nvm_enqueue_family1_read", u32,
        new ParameterImpl("object", u32, currentProgram))
        .setComment("Recover indices before full and low16 object<16 gates. Immediate predecessor kind11/object "
            + "duplicate returns1 without status publication, even for empty indices. Otherwise store "
            + "kind/object, advance producer and publish20/75/8A. Recovery can change both globals before "
            + "rejection; this routine finally republishes producer. No descriptor, completion or busy gate.");
    semanticFunction(0x67EDEL, "f33_nvm_set_family1_record", u32,
        new ParameterImpl("object", u32, currentProgram),
        new ParameterImpl("source", words, currentProgram))
        .setComment("Reject low16 object>=16 before repair/recovery. Vote status with fallback12, recover indices, "
            + "then reject full or voted21 before source/descriptor-content reads. Inclusive write-kind scan "
            + "and changed-word copy precede placement as in family0. Tail duplicate republishes original "
            + "voted status; other admissions publish20. Opaque bytes stay at physical slots. No checksum, "
            + "completion, disabled-descriptor or busy gate; no normal rejection after copy.");
    semanticFunction(0x6810CL, "f33_nvm_get_family1_status", u32,
        new ParameterImpl("object", u32, currentProgram))
        .setComment("Low16 object>=16 returnsFF before repair. Otherwise vote/repair0328/1088/10AC with fallback12. "
            + "No checksum or physical read.");
    semanticFunction(0x66FFEL, "f33_nvm_initialize_family2_ram", VoidDataType.dataType)
        .setComment("For each registered family2 descriptor, clear setter flag, publish00/55/AA status and zero "
            + "payload whole words in RAM. Preserve gaps and trailing bytes. No ROM-default copy or CRC "
            + "computation.");
    semanticFunction(0x6712CL, "f33_nvm_refresh_family2_record_status", u32,
        new ParameterImpl("object", u32, currentProgram))
        .setComment("Low16 object bound first. Validate immutable ROM, retry once on non10, and publish final "
            + "status. Return1 for an in-range request even when status30; invalid returns0. RAM payload and "
            + "setter flag unchanged.");
    semanticFunction(0x67176L, "f33_nvm_set_family2_record", u32,
        new ParameterImpl("object", u32, currentProgram),
        new ParameterImpl("source", words, currentProgram))
        .setComment("Low16 object bound before source. Copy payload whole words into descriptor RAM, set flag5A and "
            + "publish10/45/BA. Return1, invalid0. No ROM CRC or flash programming; no flag reader recovered.");
    semanticFunction(0x671D0L, "f33_nvm_get_family2_status", u32,
        new ParameterImpl("object", u32, currentProgram))
        .setComment("Low16 object>=11 returnsFF. Otherwise vote/repair0650/1098/10BC with fallback10, without CRC. "
            + "Cached10 is not proof of ROM validity or persistence.");
    semanticFunction(0x67208L, "f33_nvm_get_family2_rom_record", u32,
        new ParameterImpl("object", u32, currentProgram),
        new ParameterImpl("destination", words, currentProgram))
        .setComment("Low16 object bound before CRC/destination. Validate ROM, retry once on non10 and publish "
            + "result. Copy ROM payload, excluding trailer, only on10. Return10/30 or invalidFF. Neither RAM "
            + "payload nor setter flag supplies this getter.");
    semanticFunction(0x32454L, "f33_publish_family2_group8_halfword", VoidDataType.dataType,
        new ParameterImpl("index", u32, currentProgram))
        .setComment("Get selector0208 into an eight-byte stack record. Success10 selects halfword at "
            + "record+4+2*low8(index); otherwise use FEBE66CE+2*index. Publish to FEBE68AA+2*index. No local "
            + "index bound. Native index0 proves ROM source despite conflicting setter-like RAM; OEM meaning "
            + "unnamed.");
    semanticFunction(0x67276L, "f33_select_flmd0_internal_pulldown", VoidDataType.dataType)
        .setComment("If FLMDCNT.bit0 is clear, return. Otherwise enter PMRFFFF, attempt at most three "
            + "A5/0/FFFFFFFF/0 protected sequences, read back control, SYNCP and inspect FLMDPS.bit0; restore "
            + "prior PMR. No final success result. Manual pp2869-2874 identifies internal pull control, not "
            + "actual pin level or persistence.");
  }
  private void annotateNvmDirectOperations() throws Exception {
    DataType u32 = UnsignedIntegerDataType.dataType;
    semanticFunction(0x6879CL, "f33_nvm_begin_page_erase_span", u32,
        new ParameterImpl("first_page", u32, currentProgram),
        new ParameterImpl("page_count", u32, currentProgram))
        .setComment("Truncate page/count independently to16 bits and shift by6. Set direct-operation request5A and "
            + "reconcile. Call794DA; return0 and retain mode only for result7. Otherwise clear request, "
            + "perform real cancellation/reconciliation and returnFF. Native admitted path is bounded before "
            + "opcode20, not erased data.");
    semanticFunction(0x794DAL, "f33_nvm_request_erase_span", u32,
        new ParameterImpl("unused_selector", u32, currentProgram),
        new ParameterImpl("byte_offset", u32, currentProgram),
        new ParameterImpl("byte_count", u32, currentProgram))
        .setComment("Require nonzero direct-operation classification. Compute low16((byte_count+63 mod2^32)>>6), "
            + "check79608, then guarded76872 admission. Preserve7 and9, normalize other outcomes to8. R6 is "
            + "unused. Bounds use wrapped page arithmetic, not a generic nonzero-length test.");
    semanticFunction(0x79608L, "f33_nvm_erase_span_outside_region", u32,
        new ParameterImpl("byte_offset", u32, currentProgram),
        new ParameterImpl("page_count", u32, currentProgram))
        .setComment("Return1 unless registered first_page!=FFFF, low16(byte_offset>>6)>=first_page, and "
            + "low16(page+page_count-1)<=low16(first_page+region_count-1). Exact region0/480 pages. No "
            + "alignment or independent nonzero-count check; wrapped arithmetic is intentional "
            + "reconstruction, not strengthened validation.");
    semanticFunction(0x76872L, "f33_nvm_guarded_erase_admission", u32,
        new ParameterImpl("byte_offset", u32, currentProgram),
        new ParameterImpl("page_count", u32, currentProgram))
        .setComment("Enter actual paired guards. Mirrored interference returns9; otherwise start reverse-block "
            + "driver with low16 count and callback selector0B. Driver2 publishes secondary pending1 and "
            + "returns7; other driver results return8. Always leave guard. Successful command submission "
            + "remains a hardware dependency.");
    semanticFunction(0x74B76L, "f33_nvm_start_reverse_erase", u32,
        new ParameterImpl("byte_offset", u32, currentProgram),
        new ParameterImpl("page_count", u32, currentProgram),
        new ParameterImpl("callback_selector", u32, currentProgram))
        .setComment("Store end cursor=offset+64*low16(count) before lower admission. Submit previous block. Only "
            + "result2 publishes active1, remaining count and low8 callback selector; preserve driver result "
            + "in R10. No completed erase proof.");
    semanticFunction(0x74A8CL, "f33_nvm_submit_previous_erase_block", u32)
        .setComment("Require74A5A result1, reset diagnostics, decrement cursor by64 BEFORE7867A(cursor,64). Driver0 "
            + "installs completion callback and returns2; failure translates saved driver status. Native "
            + "exact-family paths reach first opcode20 boundary with decreasing addresses.");
    semanticFunction(0x7951CL, "f33_nvm_poll_direct_operation", VoidDataType.dataType)
        .setComment("Dispatch guarded lower polling only when direct-operation classification6CDC is nonzero. Does "
            + "not itself normalize result or release application ownership.");
    semanticFunction(0x768AEL, "f33_nvm_guarded_direct_poll", VoidDataType.dataType)
        .setComment("Enter paired guards. If mirrored interference is clear, execute79388,781BE,74E46(1); publish "
            + "the interference predicate through79C56 and leave guard. Physical sequencer completion remains "
            + "separately bounded.");
    semanticFunction(0x768DEL, "f33_nvm_get_secondary_result", u32)
        .setComment("Zero-extend byte6B72 to full32 R10; no mutation.");
    semanticFunction(0x79530L, "f33_nvm_get_direct_operation_result", u32)
        .setComment("Read actual secondary result; preserve0,1,5,6 and normalize every other byte to4. Result1 is "
            + "pending, not terminal success.");
    semanticFunction(0x769D4L, "f33_nvm_publish_erase_driver_result", VoidDataType.dataType,
        new ParameterImpl("driver_result", u32, currentProgram))
        .setComment("ROM callback selector0B at27A10. Driver1 publishes secondary0, full32 FFFF0000 publishes6, all "
            + "other values publish4 through7680C. Synthetic terminal-input execution is not physical erase "
            + "completion.");
    semanticFunction(0x682D6L, "f33_nvm_service_and_release_erase_span", VoidDataType.dataType)
        .setComment("Always call74114 first. If either family busy byte equalsA5, poll and normalize result. Retain "
            + "both flags and direct-operation request only for result1; any other result clears both busy "
            + "bytes and request, then performs real mode-exit cancellation/reconciliation.");
    semanticFunction(0x74114L, "f33_nvm_service_application_cycle", VoidDataType.dataType)
        .setComment("Require service14 and initialized-service gates. Enter service guards and classify direct "
            + "mode. Mode0 selects callback766F4, services scheduler and74790; active direct mode skips "
            + "ordinary scheduling. Publish classification predicate via79C42 and finish guards. Lower "
            + "hardware completion is not inferred.");
    semanticFunction(0x66CF6L, "f33_nvm_application_cycle", VoidDataType.dataType)
        .setComment("Select work from current0674 through66C5C; service logical/range work via682D6; "
            + "finish the selected application phase through66CC4 and publish its low8 result to0674; "
            + "then maintain the FLMD0 internal pull-down. Composed initialized-idle execution advances "
            + "the logical scan, selects callback766F4 and leaves application ownership idle. "
            + "Active flash sequencing remains a separate dependency.");
  }
  private void annotateControlPipeline() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType halfwords = new PointerDataType(u16, 4);
    semanticFunction(0xD02DAL, "f33_filter_command_slew", v)
        .setComment("ROM B1338==1 enables retained CC30/34/38/3C recurrence. Nonzero CC9C selects filtered output, "
            + "otherwise CC4C bypasses to CC4E. Difference shift uses low5 CC9E with minimum nonzero step +/-1; "
            + "selected filtered output saturates to +/-32767. Always retain published CC4E in CC3C. Invocation "
            + "recurrence, not a wall-time rate.");
    semanticFunction(0xD039EL, "f33_compose_command_sources", v)
        .setComment("Select delayed AC10 history CC5A only when AC28==1, otherwise current CC60. Apply "
            + "complement-checked base and local-addend gains from CB9C8/CB9AE, narrowing each gained term to "
            + "signed16. Add local C81A term only when C797==0; clamp the sum to ROM B1334 and publish CC50. "
            + "Therefore CC62 is not universally before or after the earlier slew path.");
    semanticFunction(0xD042CL, "f33_scale_clamp_gate_command", v)
        .setComment("Signed16 CC50 times unsigned16 AC5A, signed division by1024, then signed16 narrowing BEFORE "
            + "amplitude clamp. Publish CC62 and reuse the register value, not a RAM reload. Clamp against signed "
            + "AC4C into CC54; publish CC66 only when AC29!=0 and AC2A==0, else zero. Copy AC4C to CC68. No "
            + "history or slew recurrence here.");
    semanticFunction(0xD047CL, "f33_select_final_command", v)
        .setComment("Normally select CC66. Nonzero CC98 selects signed32 CC94 clamped to +/-22170 instead. Publish "
            + "CC64. Internal override selection can differ from both the diagnostic CC62 and normal gated CC66 "
            + "values.");
    semanticFunction(0xD0AAEL, "f33_publish_command_snapshot", v)
        .setComment("Sequentially publish selected CC64 to AC54, normal gated CC66 to AC76, and pre-final-clamp/gate "
            + "CC62 to AC56. Also copy CC60/CC68 and independent C128/C172 snapshots; publish override indication "
            + "and AC3F=5A. Sequential RAM stores are not an all-reader atomic transaction.");
    semanticFunction(0x35C4CL, "f33_sample_motor_command", v)
        .setComment("Normally publish diagnostic6AF6=EE40A, pre-override6AF8=EE410 and motor6AF4=-EE40C. In mode "
            + "family0500, E780==5A selects clamped EB10 first; otherwise EE406==5A selects clamped EE416. Exact "
            + "ROM30F1C/31914 are zero, so their forced branch is inactive. Command publication and current "
            + "conversion use separate interrupt contexts.");
    semanticFunction(0x38396L, "f33_interpolate_current_curve", s32,
        new ParameterImpl("first_component", s16, currentProgram))
        .setComment("Use signed first component to select/blend five ROM curves over -12800,-10240,-7237,-3840,0. Each "
            + "curve indexes saturating_abs(6E0A) with128-count spacing and unsigned ordinates; inter-curve "
            + "weight is scaled1024. Publish bank/weight/ordinate state and return magnitude in R10. Caller384D8 "
            + "applies command sign.");
    semanticFunction(0x38162L, "f33_calculate_sixfold_current_correction", v)
        .setComment("Use current-pair squared magnitude and a separate abs(5F36) map, quadrant-aware angle70BE0 and "
            + "trig70E32. Sixfold wrapped phase produces corrections clamped to +/-1280;71EC low2bits suppress "
            + "them. Publish6DA6/8=0 and6DAA/C corrections. This is not the complete downstream motor transform.");
    semanticFunction(0x36144L, "f33_transform_measured_phase_currents", v)
        .setComment("Transform two conditioned phase-current banks using measured-frame coefficient pairs7D4E/50 "
            + "and7D5A/5C. Keep32-bit results6B3C/40/44/48 plus saturated halfword mirrors6B34..3A. ADC/DMA "
            + "freshness and physical phase identity are separate dependencies.");
    semanticFunction(0x37E48L, "f33_compose_current_feedback", v)
        .setComment("Exclude bank0 for71EC.bit0 and bank1 forbit1, then form common/difference feedback. Preserve "
            + "unsaturated32-bit second-axis sum6D78 separately from saturated6D72; the common regulator "
            + "consumes6D78. Acquisition-status8B28&40004 takes the reset branch.");
    semanticFunction(0x5E202L, "f33_run_current_control_and_stage_output", v,
        new ParameterImpl("workmask", u32, currentProgram),
        new ParameterImpl("state", u16, currentProgram))
        .setComment("With workmask bit1, state>=0200 runs current conversion, feedback regulation, limiting, transforms "
            + "and slot0 publication. Independently state>=0101 runs arbitration/history and compare staging, "
            + "so0101..01FF can stage existing values without recomputing control.57FD2 always publishes "
            + "snapshots. Software compare staging is separate from acquisition and hardware commit.");
    semanticFunction(0x38E52L, "f33_scale_first_phase_codes", v,
        new ParameterImpl("scale", s32, currentProgram),
        new ParameterImpl("triplet", halfwords, currentProgram))
        .setComment("Scale first regulated phase triplet by shared scale/1024 with modulation-dependent output-code "
            + "bounds; write three halfwords through R7. R6 remains the scale input used by subsequent38EE2.");
    semanticFunction(0x38EE2L, "f33_scale_second_phase_codes", v,
        new ParameterImpl("scale", s32, currentProgram),
        new ParameterImpl("triplet", halfwords, currentProgram))
        .setComment("Second-bank counterpart of38E52. Real ABI consumes scale in R6 and destination in R7; caller38F72 "
            + "reuses retained R6 and supplies SP for this triplet, SP+6 for the first.");
    semanticFunction(0x38F72L, "f33_publish_current_output_slot", v)
        .setComment("Run both real phase-code scaling helpers with ROM31E38, publish the paired triplets "
            + "through57BCA(2,0,...) and enable slot0 through57C48(0). Arbitration, staging and later hardware "
            + "commit remain distinct operations.");
    semanticFunction(0x57A5AL, "f33_select_phase_output_slots", v)
        .setComment("Scan slots0..4 and choose the highest enabled slot for each bank. Publish selected "
            + "index/complement and triplets8BEE..8BF8. Optional code clamp uses [8000-L,L], L bounded4000..8000. "
            + "Selected indices are not boolean bridge-disable flags; slot4 can outrank mode-owned slot3.");
    semanticFunction(0x66786L, "f33_fast_control_cycle", v)
        .setComment("Commit PREVIOUS compare stage through61E72, then6289C, acquire/publish snapshots66824, and "
            + "dispatch next application work588E8. New controller output is staged for a later cycle. No ADC "
            + "freshness, timer-latch, electrical or mechanical proof.");
    // Inline real leaf p-code so the shared R6 scale survives the first call.
    getFunctionAt(toAddr(0x38E52L)).setInline(true);
    getFunctionAt(toAddr(0x38EE2L)).setInline(true);
    semanticData(0xB1330L, s32, "f33_command_sum_margin",
        "Scalar5120 added to B132C before D0284 input limiting, not a CodeFlash pointer.");
    semanticData(0x31CF0L, s16, "f33_first_current_curve_upper_bound", "Signed scalar0.");
    semanticData(0x31CF2L, s16, "f33_first_current_curve_lower_bound", "Signed scalar-25600, not a pointer.");
    semanticData(0x31B86L, s16, "f33_current_correction_coefficient_a", "Signed scalar1019.");
    semanticData(0x31B8CL, s16, "f33_current_correction_coefficient_b", "Signed scalar-1019.");
    semanticData(0x31B96L, s16, "f33_current_correction_phase_slope", "Signed scalar-853.");
    getFunctionAt(toAddr(0x37228L)).setComment("Common first-axis regulator: error=sat(6D80-6D70), accumulator6C8C. "
        + "Prior saturation gates integration, not proportional error difference. First-invalid correction "
        + "requires ENTIRE previous6C84==0: bit0 selects(common-old differential)/2 before bit1's plus case. "
        + "Symmetric saturation precedes division. Publish corrected6C88, then update before370E6; "
        + "the reset branch does not clear6C84/6C88.");
    getFunctionAt(toAddr(0x36F26L)).setComment("Retained output scaling follows a projected bank-axis product "
        + "and a separate scale accumulator. Unconditionally load unsigned7DA6/7DA8 before admission. "
        + "A zero filtered estimate selects target128; actual fractional recurrence still runs. "
        + "Staged scale128 forwards nonzero bank axes without implying fresh acquisition or PWM duty.");
    getFunctionAt(toAddr(0x370E6L)).setComment("Differential first-axis regulator: error=sat(6D82-6D74), accumulator6C78. Prior output-direction flags gate integration; both nonzero selected slot indices or8B28&40004 reset state. Additional accumulator clamp uses ROM31A3C. Selected slot indices are not physical-disable booleans.");
    getFunctionAt(toAddr(0x3777EL)).setComment("Common second-axis regulator aggregate375C2/375E6/3762E: error uses unsaturated32-bit feedback6D78, not halfword6D72. Persistent accumulator6CCC, directional anti-windup and first channel-invalid transition adjustment; additional clamp31A68.");
    getFunctionAt(toAddr(0x37538L)).setComment("Differential second-axis regulator aggregate373E6/37418/37460: error=sat(6D7E-6D76), accumulator6CA0, directional anti-windup and additional clamp31A58. Reset follows selected arbitration indices and acquisition status, not a generic diagnostic inhibit.");
    getFunctionAt(toAddr(0x38A58L)).setComment("Reference-derived first-bank phase transform used by compensation36750, not the final regulated output transform. Combine main/correction current pairs, halve when71EC low2bits clear, use output-frame coefficients7D54/56 and saturate triplet6E58/5A/5C.");
    getFunctionAt(toAddr(0x38B6AL)).setComment("Second-bank reference-derived phase compensation transform, paired with38A58. Its triplet is distinct from the regulated output of38D6C.");
    getFunctionAt(toAddr(0x38C7CL)).setComment("Transform limited first-bank regulated axis commands to phase triplet6E68/6A/6C using output-frame coefficients; signed saturation +/-32767. Compensation and modulation offset/clipping follow.");
    getFunctionAt(toAddr(0x38D6CL)).setComment("Second-bank regulated axis-to-phase transform, publishing6E70/72/74. Not the same interface as measured-frame feedback coefficients or reference compensation.");
  }
  private void annotateSensingPipeline() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    semanticFunction(0x6091EL, "f33_read_transfer_descriptor_head", u32,
        new ParameterImpl("channel", u8, currentProgram))
        .setComment("Read u32 at FFFF8404+64*low8(channel). R6-scaled signed displacement, NOT GP-relative "
            + "FEBE3C00. No local channel bound; physical descriptor-block identity remains separate.");
    semanticFunction(0x60940L, "f33_count_transfer_entries", u16,
        new ParameterImpl("channel", u8, currentProgram))
        .setComment("Channels<16 combine low/high halfwords of descriptor+08/+18 using low16 arithmetic; "
            + "otherwise return0. BaseFFFF8400 is independent of GP. A count does not establish sample age.");
    semanticFunction(0x668E2L, "f33_consume_rsent_sensor_slots", v)
        .setComment("On odd5F28 consume two slot records through62B32 and publish5F02..5F10; increment5F28 "
            + "on every call. Software one-of-two cadence, not proof that hardware supplied a new frame.");
    semanticFunction(0x4845EL, "f33_select_torque_pair_differences", s16,
        new ParameterImpl("first_pair", s16, currentProgram),
        new ParameterImpl("second_pair", s16, currentProgram))
        .setComment("R6/R7 are the saturated A-B and C-D differences, BEFORE their /2 diagnostic mirrors. "
            + "7CB7 selects (first-second)/2, negated second, or first. Nonzero71EC bits5/6 override: "
            + "bit5 selects negated second, otherwise first. Publish the effective selector at7DE8.");
    semanticFunction(0x4849AL, "f33_bound_torque_tracking_step", s16,
        new ParameterImpl("value", s16, currentProgram),
        new ParameterImpl("previous", s16, currentProgram))
        .setComment("FIRST clamp previous to+/-5120, then bound value within that center+/-u16[30E50]. "
            + "Exact window is5120. This is not an unbounded previous-value-centered slew limiter.");
    semanticFunction(0x484D2L, "f33_clamp_decoded_torque", s16,
        new ParameterImpl("value", s16, currentProgram))
        .setComment("Clamp signed16 input to+/-s16[30E52], exact2109 raw counts, and return in R10.");
    semanticFunction(0x484F0L, "f33_decode_torque_sensor_channels", v)
        .setComment("Only on8A1C==5A: subtract four zero points from unsigned raw channels, apply signed "
            + "ROM gains/div2048, publish channel/pair mirrors, select from the full pair differences, bound the tracking center/step "
            + "and independently amplitude-clamp into7DEA. Alternate software cadence retains state.");
    semanticFunction(0x48684L, "f33_publish_selected_torque_feedback", v)
        .setComment("On8A1C==5A publish7E0C from6870 if686C==5A, otherwise7DEA; else hold. "
            + "The selection byte alone is not a physical sensor-health classification.");
    semanticFunction(0x486D0L, "f33_condition_measured_phase_currents", v)
        .setComment("Two triples: reconcile offset references, learn only when -768<6D7C<768 and each history "
            + "is>=2294; this is separate from reconstruction when any history>30474. Select signed gains "
            + "by difference sign, saturate wide product before /16384, clamp+/-32767, retain raw mirrors. "
            + "Replace the selected phase by minus the other two; ties favor phase1 over0, then phase2.");
    semanticFunction(0x47D62L, "f33_select_electrical_angle_sample", u16,
        new ParameterImpl("channel", u8, currentProgram))
        .setComment("Channel1 selects8250, all others824C. Store7D90 and RETURN the selected halfword inR10. "
            + "The real leaf preserves caller R7, reused as the correction-table bank.");
    // Preserve the actual R7 bank across this leaf, not an invented extra return or ABI shim.
    getFunctionAt(toAddr(0x47D62L)).setInline(true);
    semanticFunction(0x47DA2L, "f33_correct_electrical_angle_sample", s16,
        new ParameterImpl("enabled", u8, currentProgram),
        new ParameterImpl("bank", u8, currentProgram),
        new ParameterImpl("phase", s16, currentProgram))
        .setComment("When enabled==5A subtract signed-byte circular interpolation at A0C0+256*bank. "
            + "Index255 wraps to0; signed division256 truncates toward zero. Return narrowed signed16 phase.");
    semanticFunction(0x47DF8L, "f33_accumulate_electrical_angle", s32,
        new ParameterImpl("previous", s32, currentProgram),
        new ParameterImpl("phase", s16, currentProgram))
        .setComment("Wrap signed low-half delta into[-32768,32768), preserve the new phase low16, and adjust "
            + "the coarse accumulator by06660000 around+/-03330000. Software counts, not established turns.");
    semanticFunction(0x47E4CL, "f33_update_electrical_angle_feedback", v)
        .setComment("Select by71EC.bit7, correct using6A7B and the retained channel bank, accumulate into7DA0 "
            + "and publish7D92. Normally copy to7D78/7D94;7566==5A substitutes7576/7578 only in publication. "
            + "Feeds rotating-frame coefficients; physical sensor mount is not inferred.");
  }
  private void annotateRateObserver() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    StructureDataType sample =
        new StructureDataType(new CategoryPath("/CamryF33"), "F33RateObserverSample", 0);
    sample.setPackingEnabled(true);
    sample.add(u8, "state", "Candidate state or retained C08E.");
    sample.add(u8, "qualification", "Candidate C0B6 or retained C08F; not a new-sample guarantee.");
    sample.add(new ArrayDataType(u8, 2, 1), "reserved", "Unwritten padding.");
    sample.add(s32, "rate", "Signed rate at offset4; zero on a failed sample gate with nonzero divisor.");
    semanticFunction(0xC452EL, "f33_sample_rate_observer", v,
        new ParameterImpl("sample", new PointerDataType(resolve(sample), 4), currentProgram))
        .setComment("Require AD3C!=0/3,BFB9==5A,BFC5==0 and C0B4>=selected threshold1. Delta is low32 "
            + "ABA4-(ABA0<<7)-(ABA8<<7); rate=(delta/8)/((u16AC12<<4)/1024). Failed gate zeroes delta "
            + "but RETAINS state/qualification. A zero divisor alone holds oldC084. Output layout is8 bytes.");
    semanticFunction(0xC45C0L, "f33_commit_rate_observer", v)
        .setComment("Always run C330C source snapshot/qualification prework. Only AC07==5A samples and "
            + "commits C08F,then C08E,then C084 under PMRFFC0. Closed outer gate holds publication.");
    semanticFunction(0xC3F56L, "f33_reset_rate_observer", v)
        .setComment("Reset external-source acquisition throughC2E14, then C084,C06C,C08E/F and C090/91. "
            + "Sibling estimator, acquisition verdicts and cross-rate interface have separate reset owners.");
    semanticFunction(0xC492CL, "f33_qualify_rate_observer_acquisition", v)
        .setComment("Build56-byte published-source/reference snapshot; acknowledgementsC08D/C08C clear "
            + "requestsC091/C090 but themselves hold. ConsistencyC4640 then routingC489C may reassert a "
            + "request in the same invocation. Distinct from C45C0 rate sampling and physical freshness.");
    semanticFunction(0xC4BCEL, "f33_update_rate_observer_deadband", v)
        .setComment("Initialize band until state11/22 latches initialization; select32 for11/other,0 for22, "
            + "adapt one count per invocation, retain direction-dependent active band, then publish "
            + "deadband excessC0CC and stateC0D0 under PMR. Invalid state reinitializes on each call.");
    semanticFunction(0xC71D0L, "f33_update_observer_dependent_assist_bound", v)
        .setComment("C08F==0 targets gain0 with coefficient16384; otherwise target1024 with286 unless the "
            + "completion latch still requires clearing. Retained accumulator divisor16384. "
            + "C37E=1792+3328*C37C/1024: qualification loss reduces the bound, NOT to zero.");
    semanticFunction(0xC7286L, "f33_map_observer_rate_to_assist_bound", v)
        .setComment("Clamp C084 symmetrically to+/-32767, map its magnitude through B0126 and publish "
            + "C378. This is an assist amplitude bound, not a phase counter or sample-age flag.");
    semanticFunction(0xC72C0L, "f33_compose_observer_dependent_assist", v)
        .setComment("Sum signed16 C894,C4A0,C3EA,C524,C2E2 into s32C330; clamp toC378 intoC334, then "
            + "to min(C37E,C37A), narrow intoC3A0. D0162 consumes this term intoCC2C: no direct C084 "
            + "read in the command slice does NOT mean independence from the observer.");
    semanticFunction(0xD0C16L, "f33_publish_rate_observer_interface", v)
        .setComment("Copy external-source qualifierBFC5 toAC08; under PMRFFC0 publish C084->AC1C and "
            + "C08E->AC09. Do not conflate this interface snapshot with the direct nested-assist consumers.");
  }
  private void annotateEstimatorAcquisition() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    semanticFunction(0xC3498L, "f33_estimator_reference_correction", s32)
        .setComment("Return signed correction in R10, also storeBFD0; former void inference lost it. "
            + "BFC8=low32(BF7C-BF70); normalize its abs32 with low32 left shift10, unsigned division "
            + "byAE38 and capFFFF (zero coefficient gives input0). MapAF5CE; low32 multiply byAE38, "
            + "signed divide1024 intoBFCC, then negate when BFC8>=0. Preserve wrap and division order.");
    semanticFunction(0xC34F8L, "f33_acquire_external_estimator_reference", v)
        .setComment("Require BFF1/BFB7==5A, BFC5/BFC4==0, wrapped abs16(BF9C)<160 and abs16(BF98)<512. "
            + "D095E returns -32768 for INT16_MIN, so that raw value passes both signed comparisons. "
            + "Increment u16BFE8; only count>10 withC0DE==5A publishes. Elapsed count pins10 even if "
            + "C0DE rejects; failed outer gate resets0. BFD4=correction+BF78-BF84-BF7C+BFD8+BF70 "
            + "with low32 arithmetic; under PMRFFC0 publish inverseBFE4,validBFF0=5A,markerBFF2=A5.");
    semanticFunction(0xC35C4L, "f33_select_external_reference_acquisition", v)
        .setComment("Clear model windowBFEA and accumulatorsBFDC/BFE0 before the external-reference "
            + "warmup/commit. Accepted sample and committed estimator reference are distinct states.");
    semanticFunction(0xC35DCL, "f33_accumulate_model_estimator_reference", v)
        .setComment("BFC5!=0 clears model accumulators/count. Otherwise failed C045/C044/C042==5A, "
            + "AD18==11 orADF4>=3840 gate HOLDS them. Qualified passes accumulate signed BF78/2000 "
            + "and BF78%2000. At incremented u16count>=2000 publish quotient-sum+remainder-sum/2000 "
            + "and inverse/markers under PMRFFC0, then CLEAR accumulators/count. Counts are invocations.");
    semanticFunction(0xC368CL, "f33_select_model_reference_acquisition", v)
        .setComment("Invalidate accepted-external markerBFF1, warmupBFE8, source markerBFFA and countBFF8 "
            + "before model accumulation. A failed model qualifier can still retain its prior window.");
    semanticFunction(0xC36A8L, "f33_latch_estimator_external_sample", v)
        .setComment("CopyBFF4->BFD8 and setBFF1=5A. AD3C==1 orAD3E==2 selects external acquisition; "
            + "otherwise AD3E==1 selects model acquisition, which clears the accepted marker again. "
            + "Other combinations retain the sample without invoking either acquisition channel.");
    semanticFunction(0xC36DEL, "f33_update_estimator_source_limits", v)
        .setComment("Without BFF0==5A retain BFEC/BFEE. With valid reference and BFFA==5A map BFF8 "
            + "through AF570[BFB8] into both. Otherwise selectAF582 or mode2AF584; BOTH exact defaults "
            + "are8000 (little-endian401F), not320/500. No local BFB8 bounds check.");
    semanticFunction(0xC3740L, "f33_select_estimator_acquisition_source", v)
        .setComment("BFB6!=5A clears accepted marker, both acquisition counters and model accumulators. "
            + "Otherwise AD3C==0/3 holds state; every other byte admits selection. Mode2 choosesAF7D0, "
            + "othersAF7CE (both1). BFFA/BFAF==5A and BFF8>=threshold accept the external sample; "
            + "otherwise select model accumulation. Finally update source limits.");
    semanticFunction(0xC331CL, "f33_publish_raw_estimator_state", v)
        .setComment("Snapshot inputs before PMRFFC0, then publish BFD4->ABA0, BFD8->BF88, C074->BF8C, "
            + "C080->BF90, BF50->BF94 plus acquisition/mode/status bytes and BFEC/BFEE limits. "
            + "ABA0 is the acquired reference, not accepted sampleBFD8; publication is not hardware freshness.");
    semanticFunction(0xC33E6L, "f33_clear_published_estimator_state", v)
        .setComment("Under PMRFFC0 clear ABA0, published BF88..BF94, BF B9..C3 status bytes and BFAA/BFAC "
            + "limits. Does not itself clear the underlying BFD4 acquisition reference.");
    semanticFunction(0xC32AAL, "f33_refresh_observer_source_term", v)
        .setComment("Publish ABA4=low32(-AC18) and BFC4=AC02 before observer sampling.");
    semanticFunction(0xBC9E8L, "f33_scale_observer_source_term", v)
        .setComment("Invoke D1272(AF8C,45,4,&result) and publish result atAC18. The later C32AA negate "
            + "is a separate update; no physical-source identity is inferred from this scaling.");
    semanticFunction(0xC2E14L, "f33_clear_observer_source_term", v)
        .setComment("Clear ABA4,BFC4,BF6D,BF6E,BFC5; not a whole raw-estimator reset.");
    semanticFunction(0xC3F7AL, "f33_apply_estimator_center_reseed", v)
        .setComment("When C091==5A setC080=C0B0,C078=low32(C0B0<<11),C08D=5A; otherwise clearC08D. "
            + "The requestC091 remains set until its separate consumer acknowledges it.");
    semanticFunction(0xC3FA0L, "f33_apply_estimator_acquisition_reset", v)
        .setComment("C090==5A clears reference/inverse validity, acquisition windows, model qualifiers, "
            + "limits, difference tracker and center; setsC08C=5A. Does not clear requestC090 or "
            + "accepted sampleBFD8. Without request only clear acknowledgementC08C.");
    semanticFunction(0xC43E0L, "f33_run_estimator_acquisition_or_tracking", v)
        .setComment("Refresh qualifiers; BFF0==5A selects established-reference difference trackingC419C, "
            + "otherwise source acquisitionC3740. Then update external-source projectionC4358. "
            + "Reference acquisition is not repeated on every established tracking pass.");
    semanticFunction(0xC4358L, "f33_update_estimator_source_projection", v)
        .setComment("AD3C==0/3 or mode2+AD3E1+AD250+AD271 clearsBFF1/C068/BFFA but retainsC07C. "
            + "Otherwise acceptedBFF1==5A projectsC07C=low32(C080+BFD8); absent acceptance invokes "
            + "C424C prediction. Projection usesBFD8, notBFD4.");
    semanticFunction(0xC44E2L, "f33_run_raw_estimator_cycle", v)
        .setComment("Always apply reseed/reset and source/secondary-tracker preworkC4046. AD13==5A "
            + "seeds BFF8/BFFA fromAE0E/AD31 once whileC070==0, then acquisition/tracking, source-band "
            + "selection, center following and publication. Otherwise clear only published copiesC33E6.");
    semanticData(0xAF580L, u16, "f33_estimator_reference_window",
        "Unsigned16 divisor/count threshold2000; not a fused32-bit scalar with following calibration.");
    semanticData(0xAF582L, u16, "f33_estimator_source_limit_default", "Exact default8000.");
    semanticData(0xAF584L, u16, "f33_estimator_source_limit_mode2", "Exact mode2 default8000.");
  }
  private void annotateEstimatorQualifiers() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType bytes = new PointerDataType(u8, 4);
    DataType halves = new PointerDataType(u16, 4);
    semanticFunction(0x49E98L, "f33_get_grouped_status_byte", u8,
        new ParameterImpl("selector", u32, currentProgram))
        .setComment("Low8 selector<30 reads290DA+8*selector: values1/2 select7F51/7F52; "
            + "other rows or out-of-range selectors return7F50. These are staged status bytes, not event IDs.");
    semanticFunction(0xBDB76L, "f33_get_application_grouped_status", u8,
        new ParameterImpl("selector", u32, currentProgram))
        .setComment("Narrow selector to low8 and forward through the real49E98 thunk. Preserve the "
            + "returned byte; the former void inference lost consequential estimator/supervisor dataflow.");
    semanticFunction(0xC405EL, "f33_refresh_estimator_tracking_qualifiers", v)
        .setComment("Refresh threshold maps, source stabilityC042, paired-source qualificationC044, "
            + "then compositeC045. C43E0 consumes these newly produced bytes before acquisition/tracking.");
    semanticFunction(0xC3908L, "f33_refresh_estimator_qualifier_thresholds", v)
        .setComment("Always refresh five C0B4-indexed scalesC00C..14; exact maps are flat1024. Only "
            + "AD18==11 refreshes axisADF6 maps and composite thresholdsC016..28. AD3F==2 selects "
            + "separate but numerically identical curves:584,218,102,384,40. Other AD18 holds those thresholds.");
    semanticFunction(0xC3A50L, "f33_update_estimator_source_mode_gate", v)
        .setComment("C02E is5A except when AD3F==2 and eitherAD5C!=2 or abs32(s16AE40)>=unsignedC028. "
            + "The signed16 input is widened before abs32, not passed through wrapping abs16.");
    semanticFunction(0xC3A84L, "f33_advance_estimator_stability_window", v,
        new ParameterImpl("count", halves, currentProgram),
        new ParameterImpl("qualified", bytes, currentProgram))
        .setComment("Count0 reseeds max/minC000/C004 toBF78; otherwise extend extrema. Wrapped spread "
            + "must be strictly below80*AE38/1024. Incremented u16 count>10 pins10 and publishes5A; "
            + "earlier admitted counts retain oldC042. Failed spread clears count/status.");
    semanticFunction(0xC3B00L, "f33_qualify_estimator_source_stability", v)
        .setComment("Refresh source-mode gate even if outer AD3F0/3, BFC5!=0 orAC02!=0 rejects. Admitted "
            + "path clamps low32(BF74+s16BF98) symmetrically16, updatesC034 by input-oldC03C, then "
            + "low32 shift10 /8672 and narrowing toC03C. Wrapped abs16(output)<signedC026, "
            + "abs16(BF9C)<160 andC02E5A admit the extrema window; rejection clearsC03E/C042.");
    semanticFunction(0xC3BD4L, "f33_update_estimator_group_release", v)
        .setComment("Real grouped status selector12hex nonzero resetsC02A and inhibitsC02F5A. Zero "
            + "increments u16 count; reaching inclusive40 pins40 and clears inhibition in that invocation.");
    semanticFunction(0xC3C12L, "f33_advance_estimator_pair_window", v,
        new ParameterImpl("count", halves, currentProgram),
        new ParameterImpl("qualified", bytes, currentProgram))
        .setComment("Mean of four unsignedBFA2/4/6/8 samples must be nonzero. Either normalized "
            + "cross-pair difference >=7 percent rejects and setsC0435A. Require pair difference<C024, "
            + "abs32(BF80)<C020, abs32(s16BFA0)<signedC022 andBFB0/BFB15A. Incremented count>10 "
            + "pins10/publishes5A; earlier admission retainsC044. Rejection clears count/status.");
    semanticFunction(0xC3D04L, "f33_qualify_estimator_paired_sources", v)
        .setComment("Always update grouped release. BFB25A andC02F0 admit paired window; otherwise "
            + "clearC040/C044 but leave pair-mismatchC043 unchanged because the window did not run.");
    semanticFunction(0xC3D4CL, "f33_estimator_base_source_constraint", u32)
        .setComment("Return5A only for BFB3/BFB4/BF46 zero and wrapped abs16(AE06/AE04)<=1; otherwise0.");
    semanticFunction(0xC3DA0L, "f33_estimator_mode2_constraint_a", u32)
        .setComment("AD3C other than2 returns5A. Mode2 requires wrapped abs16(AE4C/AE50)<=1 "
            + "andAD34/AD35 zero.");
    semanticFunction(0xC3DF2L, "f33_estimator_mode2_constraint_b", u32)
        .setComment("AD3F other than2 returns5A. Mode2 requires wrapped abs16(AE4E/AE52)<=1 "
            + "andAD34/AD35 zero.");
    semanticFunction(0xC3E44L, "f33_qualify_estimator_source_constraints", v)
        .setComment("Always compute/store three source constraintsC030..32. C0455A additionally "
            + "requires both AD3C/AD3F outside0/3, AD1811, BFB25A, BFB50 and absolute paired mean "
            + "minusADF6 strictly below1280. This is not the same gate as either consecutive window.");
    semanticData(0xAF614L, s32, "f33_estimator_stability_filter_divisor", "Exact8672 after low32 shift10.");
    semanticData(0xAF618L, s32, "f33_estimator_stability_spread_scale", "Exact80; scale byAE38/1024.");
    semanticData(0xAF61CL, s16, "f33_estimator_stability_amplitude_limit", "Exact160; strict signed comparison.");
    semanticData(0xAF61EL, u16, "f33_estimator_stability_window", "Exact10; incremented count must exceed.");
    semanticData(0xAF620L, u16, "f33_estimator_group_release_window", "Exact40; inclusive release.");
    semanticData(0xAF622L, u16, "f33_estimator_pair_percent_limit", "Exact7; equality rejects.");
    semanticData(0xAF624L, u16, "f33_estimator_pair_window", "Exact10; incremented count must exceed.");
    semanticData(0xAF626L, new ArrayDataType(s16, 6, 2), "f33_estimator_source_amplitude_limits",
        "Six signed bounds, each1. Shared wrapping abs16 preserves INT16_MIN behavior.");
    semanticData(0xAF632L, u16, "f33_estimator_pair_axis_margin", "Exact1280; strict absolute-difference gate.");
  }
  private void annotateRetainedEstimatorQualification() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType bytes = new PointerDataType(u8, 4);
    semanticFunction(0xC45FEL, "f33_initialize_retained_estimator_qualification", v)
        .setComment("Full initialization clears residuals/bounds/counters, correctionABA8, reseed centerC0B0 "
            + "and sticky plausibilityC0AE. Ordinary failure resetC4714 does not clear that latch.");
    semanticFunction(0xC4640L, "f33_check_retained_estimator_consistency", v,
        new ParameterImpl("snapshot", bytes, currentProgram))
        .setComment("Separate evaluation admissionC0AD and passC0AC. Inadmission clearsAD but holdsAC. "
            + "Admitted residuals are sample+difference-feedforward and sample+center-feedforward; "
            + "wrapped abs32 must be strictly below signed low32(480/160*AC12)/1024. Bounds refresh "
            + "after outer mode admission; residuals only after all source/count gates.");
    semanticFunction(0xC4714L, "f33_clear_retained_estimator_and_request_reset", v)
        .setComment("Clear candidate/publication qualification, counters, correctionABA8 and centerC0B0; "
            + "assertC090. Do not execute raw-estimator reset, clear stickyC0AE or overwrite rateC084.");
    semanticFunction(0xC475AL, "f33_count_retained_estimator_failure", v)
        .setComment("Exclusive u16C0A8 failure counter reaches2 inclusively then callsC4714. Narrow "
            + "increment before comparison; pre-existingFFFF wraps rather than saturating.");
    semanticFunction(0xC478CL, "f33_accept_consistent_estimator_center", v,
        new ParameterImpl("snapshot", bytes, currentProgram))
        .setComment("ExclusiveC0A4 reaches3 inclusively: qualifyC0B6, adopt primary class/count, and "
            + "copy published centerBF90 to BOTH correctionABA8 and reseed centerC0B0.");
    semanticFunction(0xC47D8L, "f33_request_secondary_estimator_reseed", v,
        new ParameterImpl("snapshot", bytes, currentProgram))
        .setComment("ExclusiveC0A6 reaches3 inclusively: adopt secondary class/count and assertC091. "
            + "Hold correctionABA8, reseed centerC0B0 and retained qualificationC0B6.");
    semanticFunction(0xC4816L, "f33_accept_unqualified_estimator_center", v,
        new ParameterImpl("snapshot", bytes, currentProgram))
        .setComment("ExclusiveC0AA reaches3 inclusively: adopt primary class/count, clear qualification "
            + "and copyBF90 toABA8 only; retain reseed centerC0B0.");
    semanticFunction(0xC485AL, "f33_route_retained_estimator_qualification", v,
        new ParameterImpl("snapshot", bytes, currentProgram))
        .setComment("Admission/pass both5A select primary consistency; else retained qualification5A "
            + "selects secondary reseed; else inadmission selects unqualified primary; otherwise failure. "
            + "Exactly one branch runs and clears the other three consecutive counters.");
    semanticFunction(0xC489CL, "f33_validate_and_route_retained_estimator", v,
        new ParameterImpl("snapshot", bytes, currentProgram))
        .setComment("Suppression/mode predicates and bitwise reference/marker complements precede "
            + "widened abs(s16C172)<12000 and stickyC0AE==0. Structural rejection preserves latch; "
            + "plausibility/latch failure sets5A. Rejection counts failure, not immediate raw reset.");
    semanticFunction(0xC424CL, "f33_predict_estimator_source_sample", v,
        new ParameterImpl("warmup", new PointerDataType(u16, 4), currentProgram),
        new ParameterImpl("accepted", bytes, currentProgram),
        new ParameterImpl("projection", new PointerDataType(s32, 4), currentProgram))
        .setComment("Source markers, wrapped abs16 amplitudes<160/512 and unsigned abs32 difference "
            + "<low32(24000*AE38)>>10 admit warmup. Incremented u16 count>10 pins10; C0DE5A additionally "
            + "commits BFD8=BF7C-(BF78-BFD4-BF70), projection=C080+BFD8 and acceptance5A. "
            + "Rejection clears warmup but holds acceptance/output.");
    semanticFunction(0xC4BF2L, "f33_initialize_secondary_estimator_stability", v)
        .setComment("Clear observationsC0D4/C0D8, counterC0DD and markerC0DE; seed tokenC0DC fromAD5B.");
    semanticFunction(0xC4C0CL, "f33_qualify_secondary_estimator_change", v,
        new ParameterImpl("change", s32, currentProgram),
        new ParameterImpl("count", bytes, currentProgram),
        new ParameterImpl("qualified", bytes, currentProgram))
        .setComment("Require signed change<signed low32(43*AE38)/1024. Increment below2 and assert5A "
            + "on reaching2; equality/large change clears count/status. Invocation count, not elapsed time.");
    semanticFunction(0xC4C56L, "f33_update_secondary_estimator_stability", v)
        .setComment("Admitted source with changedAD5B token evaluates BF84+BF7C-BF70 versusC0D8. "
            + "Changed token updates both observations even on rejection; unchanged token holds. Closed "
            + "admission clearsC0D8/count/marker but retainsC0D4. Always retain current token.");
    semanticFunction(0xC37D4L, "f33_publish_retained_estimator_projection", v)
        .setComment("Conditionally copyC07C/countC0B4 toAF04/AE0E using observer state, acceptance and "
            + "prior snapshotBFFA/BFF8. Some BFFA5A branches hold values while publishingACEC5A; "
            + "qualification is not freshness. Observed reset first clearsC07C/BFFA.");
    semanticFunction(0xC37BAL, "f33_snapshot_retained_estimator_projection", v)
        .setComment("Snapshot AF04/AE0E/ACEC intoBFF4/BFF8/BFFA for separate publication retention gates.");
  }
  private void annotateEstablishedTracking() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType words = new PointerDataType(s32, 4);
    semanticFunction(0xD095EL, "f33_abs_s16_wrapping", s16,
        new ParameterImpl("value", s16, currentProgram))
        .setComment("SXH input, negate nonpositive input, then SXH R10 again. INT16_MIN remains-32768; "
            + "the physical R10 result is sign-extended32. Signed16 return makes the narrowing explicit "
            + "in C rather than falsely returning+32768. Not a saturating absolute value.");
    semanticFunction(0xD0970L, "f33_abs_s32_wrapping", s32,
        new ParameterImpl("value", s32, currentProgram))
        .setComment("Return positive input unchanged, otherwise low32 negation. INT32_MIN remains "
            + "negative. C unary-minus spelling does not establish a nonnegative result over all32-bit inputs.");
    semanticFunction(0xC419CL, "f33_track_established_estimator_difference", v)
        .setComment("With BFC5==0, first copyC0B4->BFEE. QualifiersC045/C044/C042=5A, AD18=11 and "
            + "unsignedADF4>=3840 publishC074=low32(BF78-BFD4) and increment u16C064. Only count>100 "
            + "runs bounded filter/source-count update, then pins100. Failed qualification resets warmup "
            + "but holds C04C/C078/C074; BFC5!=0 instead clears filter/accumulator and warmup.");
    semanticFunction(0xC4076L, "f33_filter_established_estimator_difference", v,
        new ParameterImpl("difference", s32, currentProgram),
        new ParameterImpl("filtered_difference", words, currentProgram),
        new ParameterImpl("new_accumulator", words, currentProgram))
        .setComment("Clip difference around C080 by AE38/1024. StateC08E selects curveAF77E/AF792/AF7A6 "
            + "atADF6; gain=8192/curve, or8192 when zero. Clamp low32 error*low16(gain) to +/-8*AE38; "
            + "add signed increment/4 to GLOBAL C078, publish accumulator/2048 through output pointer. "
            + "Arithmetic is low32, not a saturating integral; third pointer is output-only.");
    semanticFunction(0xC4144L, "f33_advance_estimator_source_count", v,
        new ParameterImpl("candidate", s32, currentProgram),
        new ParameterImpl("previous", s32, currentProgram))
        .setComment("Start from C0B4, not oldBFEC. Below curve ceiling60000, increment if candidate "
            + "changed or wrapped abs32(candidate-C080)<AE38/1024. Otherwise retain the input count, "
            + "even above the ceiling. Publish BFEC and diagnostic ceilingC066.");
    semanticFunction(0xC4404L, "f33_classify_estimator_source_band", v)
        .setComment("Always snapshotC08E->C08A. Modes0/3 selectC06E0. Other mode bytes classify "
            + "unsignedBFEC with exact lower1 and upper10880: below lower0, below upper11, otherwise22. "
            + "Mode2 has separate calibration cells but the same exact thresholds.");
    semanticFunction(0xC4464L, "f33_follow_estimator_center", v)
        .setComment("BFC5==0 andBFF0==5A compute low32 residualBF78-BFD4-C080. First C06F0 call latches "
            + "C06E->C08B andC06F5A without adopting the filter. Later calls adoptC04C and current band "
            + "only when wrapped abs32(residual)<=480*AE38/1024. Closed gate clears center only, "
            + "retaining C06F/C08B/C05C. This is separate from AD13's outer publication gate.");
    semanticData(0xAF760L, s32, "f33_estimator_tracking_band_scale", "Exact1, normalized byAE38/1024.");
    semanticData(0xAF764L, s32, "f33_estimator_tracking_step_scale", "Exact8192, normalized byAE38/1024.");
    semanticData(0xAF76CL, s32, "f33_estimator_center_adoption_scale", "Exact480; inclusive residual gate.");
    semanticData(0xAF772L, u16, "f33_estimator_tracking_warmup", "Exact100; incremented count must exceed it.");
    semanticData(0xAF77AL, u16, "f33_estimator_upper_band_default", "Exact10880.");
    semanticData(0xAF77CL, u16, "f33_estimator_upper_band_mode2", "Exact10880.");
    semanticData(0xAF7CEL, u16, "f33_estimator_lower_band_default", "Exact1.");
    semanticData(0xAF7D0L, u16, "f33_estimator_lower_band_mode2", "Exact1.");
  }
  private void annotateThermalModels() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
    StructureDataType following = new StructureDataType(category, "F33FractionalFollowing16", 0);
    following.add(s16, "previous", "Prior quantized output.");
    following.add(s16, "target", "Current target.");
    following.add(s32, "accumulator", "Retained signed16.16 accumulator; low32 arithmetic.");
    semanticFunction(0x6A63EL, "f33_follow_s16_fractional", v,
        new ParameterImpl("state", new PointerDataType(resolve(following), 4), currentProgram),
        new ParameterImpl("coefficient", u32, currentProgram),
        new ParameterImpl("output", new PointerDataType(s16, 4), currentProgram),
        new ParameterImpl("new_accumulator", new PointerDataType(s32, 4), currentProgram))
        .setComment("Use coefficient1..65535, otherwise65536. Compute low32 accumulator + "
            + "coefficient*(target-previous); publish signed division by65536 narrowed16, not SAR rounding.");
    semanticFunction(0x39420L, "f33_scale_thermal_divisor", u32,
        new ParameterImpl("base", u32, currentProgram),
        new ParameterImpl("scale", u32, currentProgram))
        .setComment("Unsigned low16 product >>10, cappedFFFF; high input bits ignored.");
    semanticFunction(0x3943AL, "f33_update_nonnegative_thermal_pole", s32,
        new ParameterImpl("previous", s32, currentProgram),
        new ParameterImpl("drive", s32, currentProgram),
        new ParameterImpl("divisor", u32, currentProgram))
        .setComment("Saturate drive-previous to +/-7FFFFFFF, divide by low16 divisor if nonzero, "
            + "saturating-add previous, then floor0. Zero divisor uses the whole error, not hold.");
    semanticFunction(0x3949AL, "f33_scale_thermal_contribution", s32,
        new ParameterImpl("state", s32, currentProgram),
        new ParameterImpl("gain", s16, currentProgram),
        new ParameterImpl("upper", s16, currentProgram),
        new ParameterImpl("lower", s16, currentProgram))
        .setComment("Signed state/128, symmetric saturating32 multiply by gain, signed /4096, then "
            + "upper/lower clamp and sign-extended16 result. Preserve both truncation stages.");
    semanticFunction(0x3A670L, "f33_update_motor_thermal_estimate", v)
        .setComment("Only uninitialized6F80==0 requires7DCC/7BF6 both5A and restore3A5D4. Nonzero marker "
            + "continues both branches without rechecking validity; publish signed maximum at6F82. "
            + "Temperature estimation and later current-limit mapping are separate operations.");
    semanticFunction(0x3A718L, "f33_update_motor_thermal_branch0", s32,
        new ParameterImpl("upper", s16, currentProgram),
        new ParameterImpl("lower", s16, currentProgram))
        .setComment("Drive70B4 updates poles6F94/6F98. Divisors1000/250 use flat1024 gain map unless "
            + "sat_abs16(64E2)>32 AND drive>1638400, selecting1536 scale and divisors1500/375. "
            + "Contributions use gains5/38, bias384; clamp then offset/follow selector6. Real signedR10 "
            + "adjusted estimate is both stored6F8C and consumed by the parent maximum.");
    semanticFunction(0x3A85AL, "f33_update_motor_thermal_branch1", s32,
        new ParameterImpl("upper", s16, currentProgram),
        new ParameterImpl("lower", s16, currentProgram))
        .setComment("Drive70B8 and poles6FA4/6FA8; same exact numerical coefficients as branch0, "
            + "separate speed-axis6694 and selector7. Return/store adjusted6F9C, not void.");
    semanticFunction(0x3AE10L, "f33_update_ecu_source3_thermal_estimate", v)
        .setComment("Uninitialized6FE0 requires7DCC/7BF6 both5A and restore3AD72. Otherwise update "
            + "both branches and publish signed maximum6FE2; source3 is a structural code, not an OEM component.");
    semanticFunction(0x3AEB8L, "f33_update_ecu_source3_thermal_branch0", s32,
        new ParameterImpl("upper", s16, currentProgram),
        new ParameterImpl("lower", s16, currentProgram))
        .setComment("Drive6EF4 updates6FF4/6FF8. Exact divisors1/1 and contribution gains/bias0 still "
            + "evolve poles, while raw thermal contribution is0. Selector4 offset/following remains active; "
            + "return adjusted6FEC. Do not infer an entirely disabled thermal path.");
    semanticFunction(0x3AFD0L, "f33_update_ecu_source3_thermal_branch1", s32,
        new ParameterImpl("upper", s16, currentProgram),
        new ParameterImpl("lower", s16, currentProgram))
        .setComment("Drive6EF8 updates7004/7008; exact zero contribution gains/bias and divisors1/1 "
            + "as branch0. Selector5 supplies adjusted6FFC, returned in signedR10.");
    semanticFunction(0x3A9AEL, "f33_publish_motor_thermal_limit_maps", v)
        .setComment("Map signed6F82 through2B4E4/2B500 into6FAC/6FAE. Exact curves are flat22170/14965 "
            + "before signed-axis7FFF terminators, at or above arbitration nominals22170/11085.");
    semanticFunction(0x3B0FAL, "f33_publish_ecu_source3_thermal_limit_maps", v)
        .setComment("Map signed6FE2 through2B554/2B570 into700C/700E; exact flat22170/14965 curves. "
            + "This source alone does not lower either arbitration nominal.");
    semanticFunction(0x3B960L, "f33_apply_thermal_offset_and_following", s32,
        new ParameterImpl("selector", u32, currentProgram),
        new ParameterImpl("raw_estimate", s16, currentProgram),
        new ParameterImpl("previous", s16, currentProgram))
        .setComment("Low8 selector indexes two-byte21258 rows without local bounds check. Use7014 "
            + "offset bank unless both7BF8 masks22/2200 are nonzero, then7074. Saturating16 add and "
            + "clamp[-6400,32000]. First selector use bypasses following; initialized modes7058=1/3 "
            + "follow only for saturated absolute change>=128, otherwise set separate completion flags.");
    semanticFunction(0x3B8E4L, "f33_follow_thermal_offset_target", s32,
        new ParameterImpl("selector", u32, currentProgram),
        new ParameterImpl("target", s16, currentProgram),
        new ParameterImpl("previous", s16, currentProgram),
        new ParameterImpl("bias", s16, currentProgram))
        .setComment("Reseed selector accumulator7090 from previous<<16 when its signed /65536 "
            + "narrowed16 disagrees. Apply fractional follower with exact coefficient800; add bias "
            + "to accumulator/output, cap output at32000 and return signed16. Exact mode1/3 biases are0.");
    semanticFunction(0x3A5D4L, "f33_restore_motor_thermal_model", v)
        .setComment("Seed56-byte local from211E8 then get application record6. Status!=10 or markerA55A "
            + "uses ROM terms307/2893 per branch. Otherwise use saved terms unless at least one7BF8 byte "
            + "is zero, marker==0 and selected signed source difference>32000. Marker is passed in realR6 "
            + "to3A56E. Restore chooses live poles; it does not erase the record or prove durability.");
    semanticFunction(0x3AD72L, "f33_restore_ecu_source3_thermal_model", v)
        .setComment("Seed56-byte local from21220 then get record6; use fields24/26/28/2A and marker32 "
            + "(hex offsets). Status!=10 or markerA55A uses zero ROM terms. Otherwise conditional zero "
            + "requires an absent7BF8 byte and3AD0C(marker)==5A: marker0 and selected difference>32000.");
    semanticFunction(0x3B684L, "f33_stage_dual_thermal_squared_inputs", s32,
        new ParameterImpl("upper", s16, currentProgram),
        new ParameterImpl("lower", s16, currentProgram))
        .setComment("Low32 sums66E6^2+66E8^2 and66EA^2+66EC^2 pass unsigned bounds and publish70B4/70B8. "
            + "Their bounded sum also drives independent70BC/70C0 poles and a separate returned estimate. "
            + "These staged squared-input drives are not measurements of power in watts.");
    semanticFunction(0x397E6L, "f33_stage_ecu_thermal_squared_inputs", v)
        .setComment("Low32 squares of32-bit6EFC and signed16 6EEC/6EEE, then signed calibration bounds, "
            + "publish6EF0/6EF4/6EF8. Do not replace low32 multiplication by an unbounded mathematical square.");
    semanticData(0x21258L, new ArrayDataType(u8, 16, 1), "f33_thermal_offset_source_pairs",
        "Eight normal/alternate index pairs: selectors0/1/4..7 use0; selector2 uses1; selector3 uses2.");
  }
  private void annotateRemainingEcuThermalModels() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    semanticFunction(0x39D26L, "f33_update_ecu_source2_thermal_estimate", v)
        .setComment("Only zero6F34 requires7DCC/7BF6 both5A and record6 restoration. Initialized model "
            + "continues without those validity gates. First6764&3!=0 with6F35==0 rebases both pole pairs "
            + "and latches alternate gains5A; clearing6764 does not revert it. Publish signed branch maximum6F36.");
    semanticFunction(0x39DA8L, "f33_update_ecu_source2_thermal_branch0", s32,
        new ParameterImpl("upper", s16, currentProgram),
        new ParameterImpl("lower", s16, currentProgram),
        new ParameterImpl("alternate_gains", u8, currentProgram))
        .setComment("Drive70B4 and poles6F4C/6F50; gains23/10 or54/6, bias512. Base divisors13/5000 "
            + "scale1536 only when sat_abs16(64E2)>32 AND signed drive>1638400; otherwise unsigned "
            + "speed map is flat1024. Selector0 offset/following returns signedR10 and stores6F40.");
    semanticFunction(0x3A00AL, "f33_update_ecu_source2_thermal_branch1", s32,
        new ParameterImpl("upper", s16, currentProgram),
        new ParameterImpl("lower", s16, currentProgram),
        new ParameterImpl("alternate_gains", u8, currentProgram))
        .setComment("Independent drive70B8/poles6F60/6F64, same exact coefficients as branch0, "
            + "speed axis6694 and selector1 offset/following. Return/store adjusted6F54.");
    semanticFunction(0x39F3CL, "f33_rebase_ecu_source2_thermal_branch0", v)
        .setComment("Convert each old pole by signed /2048, multiply old gain23/10, divide new54/6, "
            + "then symmetric saturating32 multiply2048. Preserve staged truncation; not exact real-valued rescaling.");
    semanticFunction(0x3A19EL, "f33_rebase_ecu_source2_thermal_branch1", v)
        .setComment("Same staged conversion for6F60/6F64 before first alternate-gain model update.");
    semanticFunction(0x39B6AL, "f33_update_ecu_source4_thermal_estimate", v)
        .setComment("Only zero6F10 requires7DCC/7BF6 both5A and39A1C restoration. Then calculate "
            + "adjusted estimate and store real signedR10 low16 at6F12; nonzero marker bypasses initialization gates.");
    semanticFunction(0x39A94L, "f33_calculate_ecu_source4_thermal_estimate", s32)
        .setComment("Drive70B0 updates two poles with exact divisors1/1. High-load scale1536 truncates "
            + "these divisors back to1. Gains0/0 leave raw bias1536; selector2 adds offset source index1 "
            + "and optional following. Return adjusted estimate inR10, not void.");
    semanticFunction(0x3933AL, "f33_update_ecu_source5_thermal_estimate", v)
        .setComment("Only zero6EAC requires7DCC/7BF6 both5A and390FE restoration. Store calculated "
            + "signedR10 low16 at6EAE; initialized updates do not require fresh admission bytes.");
    semanticFunction(0x391E6L, "f33_calculate_ecu_source5_thermal_estimate", s32)
        .setComment("Six poles6EC0..6ED4: first three use6EF0, last three70B0. Divisors200/420/1/1/1/1, "
            + "gains13/100/0/0/0/0 and bias0. Clamp summed contributions then selector3 offset/following "
            + "using source index2. Return adjusted signedR10; zero-gain poles still evolve.");
    semanticFunction(0x3A27EL, "f33_publish_ecu_source2_thermal_limit_maps", v)
        .setComment("Signed6F36 selects nonflat2B3C4/2B3E0 curves into6F68/6F6A. Bank0 reaches5542 "
            + "at18560; bank1 reaches0 at19376. Signed-axis7FFF terminates; FFFF ordinate is not an endpoint.");
    semanticFunction(0x39BC4L, "f33_publish_ecu_source4_thermal_limit_maps", v)
        .setComment("Signed6F12 selects2B32C/2B348 into6F30/6F32. Bank0 reaches5542 at16512 and "
            + "bank1 reaches0 at16628. Zero pole gains do not disable this offset-driven derating path.");
    semanticFunction(0x393A4L, "f33_publish_ecu_source5_thermal_limit_maps", v)
        .setComment("Signed6EAE selects2B2B8/2B2D4 into6EE0/6EE2. Bank0 reaches5542 at18560, "
            + "bank1 reaches0 at15216. Distinct from flat motor/source3 maps and the signed current floor.");
    semanticFunction(0x39C78L, "f33_restore_ecu_source2_thermal_model", v)
        .setComment("Record6 terms08/0A/0C/0E, marker32. Exact status10 and marker!=A55A admit saved "
            + "terms, conditionally zeroed for marker0/selected difference>32000 with a zero7BF8 byte. "
            + "Rejected record uses3390/222 per branch. 6764&3 chooses initial gains and6F35; seed poles "
            + "from contribution*4096/gain then saturating multiply128.");
    semanticFunction(0x39A1CL, "f33_restore_ecu_source4_thermal_model", v)
        .setComment("Record6 terms10/12 and common marker32/conditional-zero contract. Rejection uses "
            + "zero defaults. Exact gains0/0 seed both poles0 even with nonzero saved contributions.");
    semanticFunction(0x390FEL, "f33_restore_ecu_source5_thermal_model", v)
        .setComment("Record6 terms18..22 and marker32; same exact-status and conditional-zero contract. "
            + "Rejected record uses539/3803/0/0/0/0. Seed via signed contribution*4096/gain followed by "
            + "saturating multiply128; zero gain seeds0. Does not rewrite the retained record.");
    semanticFunction(0x39C12L, "f33_should_zero_ecu_source2_thermal_seed", u32,
        new ParameterImpl("record_marker", u16, currentProgram))
        .setComment("Return5A only for marker0 and selected signed difference>32000. 7BF8 low0/high "
            + "nonzero selects7DD0-7DCE; low nonzero/high0 selects7DD8-7DD6; otherwise use minimum. "
            + "Update selected6F38/6F3C histories; retain an unselected history.");
    semanticFunction(0x39930L, "f33_should_zero_ecu_source4_thermal_seed", u32,
        new ParameterImpl("record_marker", u16, currentProgram))
        .setComment("Same strict32000/marker0/source-byte selection; selected difference histories6F28/6F2C.");
    semanticFunction(0x3906EL, "f33_should_zero_ecu_source5_thermal_seed", u32,
        new ParameterImpl("record_marker", u16, currentProgram))
        .setComment("Same strict32000/marker0/source-byte selection; histories6ED8/6EDC. Caller39126 "
            + "loads record+32 intoR6 and preserves it through the39152 call; no invented NvM return argument.");
    semanticFunction(0x3A56EL, "f33_should_zero_motor_thermal_seed", u32,
        new ParameterImpl("record_marker", u16, currentProgram))
        .setComment("Same strict32000/marker0/source-byte selection; selected histories6F84/6F88.");
    semanticFunction(0x3AD0CL, "f33_should_zero_ecu_source3_thermal_seed", u32,
        new ParameterImpl("record_marker", u16, currentProgram))
        .setComment("Same strict32000/marker0/source-byte selection; selected histories6FE4/6FE8.");
    DataType point = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33CurvePointS16U16");
    DataType currentCurve = new ArrayDataType(point, 7, 4);
    semanticData(0x2B3C4L, currentCurve, "f33_ecu_source2_current_curve_bank0", "Signed-axis7FFF sentinel; final real ordinate5542.");
    semanticData(0x2B3E0L, currentCurve, "f33_ecu_source2_current_curve_bank1", "Nonflat current limit reaches0 at19376.");
    semanticData(0x2B32CL, currentCurve, "f33_ecu_source4_current_curve_bank0", "Nonflat current limit reaches5542 at16512.");
    semanticData(0x2B348L, currentCurve, "f33_ecu_source4_current_curve_bank1", "Nonflat current limit reaches0 at16628.");
    semanticData(0x2B2B8L, currentCurve, "f33_ecu_source5_current_curve_bank0", "Nonflat current limit reaches5542 at18560.");
    semanticData(0x2B2D4L, currentCurve, "f33_ecu_source5_current_curve_bank1", "Nonflat current limit reaches0 at15216.");
    StructureDataType record = new StructureDataType(new CategoryPath("/CamryF33"), "F33ThermalHistoryRecord", 0);
    record.setPackingEnabled(true);
    record.add(new ArrayDataType(s16, 4, 2), "motor_terms", "Two restored contributions per branch, not raw poles.");
    record.add(new ArrayDataType(s16, 4, 2), "source2_terms", "Two restored contributions per branch.");
    record.add(new ArrayDataType(s16, 2, 2), "source4_terms", "Exact zero gains discard these when seeding poles.");
    record.add(new ArrayDataType(s16, 2, 2), "offset_terms", "707C then707A; restored in reverse argument order by3B60C.");
    record.add(new ArrayDataType(s16, 6, 2), "source5_terms", "Six contributions; four have exact zero gains.");
    record.add(new ArrayDataType(s16, 4, 2), "source3_terms", "Four exact zero-gain contributions.");
    record.add(u32, "writer_zero", "All three record6 writers publish zero.");
    record.add(u16, "ancillary_snapshot", "Normal writer captures E8AC; clear/invalidate use7F80. Physical identity unresolved.");
    record.add(u16, "marker", "A55A rejects; zero permits conditional zero seeding; other accepted markers retain terms.");
    record.add(new ArrayDataType(s16, 2, 2), "drive_epoch_maxima", "Current run maximum merged with the two restored maxima; marker admission differs from model terms.");
    semanticData(0xFEBEF4D0L, resolve(record), "f33_thermal_history_record",
        "Family0 object6 live RAM mirror, not physical flash. All restore consumers copy before exact status10 admission.");
  }
  private void annotateThermalHistoryLifecycle() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    semanticFunction(0x3A9EAL, "f33_check_thermal_raw_estimate_margin", u32)
        .setComment("Return real R10 A5 iff minimum of five bank0 maps>=21248. Map raw model maxima "
            + "plus common10880 and margins803/3370/0/0/983 after symmetric32767 saturation. "
            + "Publish adjusted inputs6FB4..6FBC, maps6FBE..6FC6, minimum6FC8 and status6FB1.");
    semanticFunction(0x3AB78L, "f33_check_thermal_contribution_count", u32)
        .setComment("Map maximum individual contribution of each model, then require maximum map "
            + "output strictly below unsigned688C/2. Maps2FB64..2FBC7: motor/source3 flat125; "
            + "source2/4/5 step125 to65534 at1229. Counter251 rejects equality,252 admits flat125. "
            + "Publish maxima6FCA..6FD2, maps6FD4..6FDC, maximum6FDE and real R10/status6FB2.");
    semanticFunction(0x3ACC4L, "f33_update_thermal_history_qualification", v)
        .setComment("Snapshot6764 before both tests. Publish6FB0=A5 only when both returnA5 and "
            + "the entire saved word is zero, otherwise5A. No physical temperature/time claim.");
    semanticFunction(0x3206CL, "f33_initialize_thermal_shutdown_counter", v)
        .setComment("Clear688C; map30E78 at constant input0 to set688E=15000 invocations.");
    semanticFunction(0x32090L, "f33_step_thermal_shutdown_request", v)
        .setComment("Increment688C while below688E and previous6FB0!=A5; otherwise request event27. "
            + "Schedulers call this before the current thermal qualification publication.");
    semanticFunction(0x39512L, "f33_publish_thermal_history_record", v)
        .setComment("Nonzero7071 admits56-byte family0 record6. Marker5AA5 if7BF8!=0, otherwise "
            + "FFFF iff6FB0A5, else0. Cache6F00/02 into6EE6/8. Ignore setter acceptance and arm6EE4=1.");
    semanticFunction(0x395F0L, "f33_reset_thermal_models_and_history_record", v)
        .setComment("Clear model contributions/poles, offset poles and drive maxima, not every "
            + "published limit or initialization marker. Publish zero terms, ancillary7F80 and marker0; "
            + "clear6EE6/8, ignore setter acceptance and arm6EE4=1.");
    semanticFunction(0x3967CL, "f33_invalidate_thermal_history_record", v)
        .setComment("Publish ROM default terms, ancillary7F80 and rejecting markerA55A while retaining "
            + "cached6EE6/8 maxima. Ignore setter acceptance; unlike normal/clear publication do not arm6EE4.");
    semanticFunction(0x393F0L, "f33_poll_thermal_history_record_status", v)
        .setComment("Only tracker6EE4==1 polls object6: exact10 becomesFF, high-nibble30 becomesFE, "
            + "all other statuses retain1. No transaction identity ties this poll to accepted publication.");
    semanticFunction(0x483ECL, "f33_publish_thermal_reference_record", v)
        .setComment("Require7DCC5A; publish signed7DCE/7DD6 plus zero word to family0 record5. "
            + "Set7DE4=1 before setter; acceptance ignored. Independent from record6's7071 gate.");
    semanticFunction(0xB2CC2L, "f33_snapshot_retained_control_records", v)
        .setComment("Compose record5, record6 and gated estimator record8 publications. Called by "
            + "B2CFE on mode0701/event27 before B1620(0702), not itself an AEB00 family hook. "
            + "Separate admission/queues/trackers, not an atomic or durable snapshot.");
    semanticFunction(0x35114L, "f33_service_clear_thermal_history", s32)
        .setComment("Phase0 resets squared drive and models, publishes records6/5, sets phase5A, returns-1. "
            + "Phase5A waits while either tracker==1, then clears phase and returns0 only if bothFF, else-6.");
    semanticFunction(0x3B55AL, "f33_should_zero_restored_thermal_offset", u32,
        new ParameterImpl("record_marker", s16, currentProgram))
        .setComment("Select signed absolute reference7DCE/7DD6 by7BF8 byte availability, otherwise "
            + "their maximum. Return5A only for selected<14720 AND marker0; not a reference delta. "
            + "Always snapshot references into707E/7080; real marker arrives in R6.");
    semanticFunction(0x3B5A8L, "f33_seed_thermal_offset_pole", s32,
        new ParameterImpl("contribution", s16, currentProgram),
        new ParameterImpl("gain", s16, currentProgram))
        .setComment("Gain0 returns0; otherwise signed contribution*4096/gain, then saturating multiply128.");
    semanticFunction(0x3B60CL, "f33_restore_thermal_offset_terms", v)
        .setComment("Copy record6 before exact status10/marker!=A55A admission. Zero-byte7BF8 and "
            + "marker!=5AA5 permit3B55A conditional zero. Restore+16 then+14 through gains100/25; "
            + "rejection uses exact zero defaults. Seed baseline outputs7074/76/78 to14720.");
    semanticFunction(0x3985CL, "f33_restore_thermal_drive_epoch_maxima", v)
        .setComment("Copy record6, accept tail+34/+36 on exact status10 WITHOUT checking markerA55A. "
            + "Otherwise clear both restored maxima6F06/08. Separate from model-term validity.");
    semanticFunction(0x398A0L, "f33_update_thermal_drive_epoch_maxima", v)
        .setComment("Filter70B0 with divisor30000/gain25, clamp contribution0..32767 and retain run "
            + "maximum6F04. Merge that one maximum with restored6F06/08 into6F00/02; ties permitted. "
            + "Do not feed current outputs back into the restored pair.");
    semanticData(0xFEBE6FB0L, new ArrayDataType(u8, 3, 1), "f33_thermal_history_qualification",
        "Combined/raw-estimate/contribution-count results. A5 qualified;5A not qualified.");
    semanticData(0xFEBE688CL, u16, "f33_thermal_shutdown_count", "Invocation count, not a wall-clock unit.");
    semanticData(0xFEBE688EL, u16, "f33_thermal_shutdown_count_limit", "Initialized15000 from30E78 at input0.");
  }
  private void annotateThermalArbitration() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType byteOut = new PointerDataType(u8, 4);
    Function choose = semanticFunction(0x3A2D2L, "f33_choose_thermal_limit_source", u32,
        new ParameterImpl("current", u16, currentProgram),
        new ParameterImpl("candidate", u16, currentProgram),
        new ParameterImpl("source", byteOut, currentProgram),
        new ParameterImpl("candidate_source", u8, currentProgram));
    choose.setInline(true);
    choose.setComment("With nonnull source, candidate<=current replaces both limit and source; ties choose "
        + "the later candidate. Null source retains current. Real leaf preserves R8 across the selector's "
        + "successive calls; inline its actual effects rather than inventing pointer arguments.");
    semanticFunction(0x3A2E8L, "f33_select_ecu_thermal_limit", u32,
        new ParameterImpl("source", byteOut, currentProgram),
        new ParameterImpl("bank", u8, currentProgram))
        .setComment("Reduce sources2,4,5,3 in that order, with later equal minima winning. Bank0 reads "
            + "6F68/6F30/6EE0/700C; nonzero bank reads their +2 partners. Null source returns nominal "
            + "22170 or11085 without reading the limits.");
    semanticFunction(0x3A35EL, "f33_select_ecu_thermal_diagnostic", s32,
        new ParameterImpl("limit", u16, currentProgram),
        new ParameterImpl("source", u8, currentProgram),
        new ParameterImpl("active_source", byteOut, currentProgram),
        new ParameterImpl("bank", u8, currentProgram))
        .setComment("Only limit below bank nominal22170/11085 and source2/3/4/5 publishes its source "
            + "and signed temperature6F36/6FE2/6F12/6EAE. Otherwise publish source0 and return0; "
            + "null output returns0 without a write. Not selection of the globally strongest motor limit.");
    semanticFunction(0x3A3B0L, "f33_select_motor_thermal_diagnostic", v,
        new ParameterImpl("limit", u16, currentProgram),
        new ParameterImpl("nominal", u16, currentProgram),
        new ParameterImpl("active", byteOut, currentProgram),
        new ParameterImpl("temperature", new PointerDataType(s16, 4), currentProgram))
        .setComment("Limit strictly below nominal publishes active1 and signed6F82; equality or above "
            + "publishes active0/temperature0. Both output pointers are required.");
    semanticFunction(0x3A3CEL, "f33_select_smaller_magnitude_s16", s32,
        new ParameterImpl("first", s16, currentProgram),
        new ParameterImpl("second", s16, currentProgram))
        .setComment("Rank by saturated absolute magnitude (-32768 ranks32767), retain original signed "
            + "value and choose first on equality. Return is full sign-extended R10.");
    semanticFunction(0x3A406L, "f33_map_thermal_current_floor", v,
        new ParameterImpl("current_limit", u16, currentProgram))
        .setComment("Map four signed temperature states and unsigned effective limit; retain the smallest "
            + "absolute output at6F7E. All five exact maps are flat -22170 before their sentinels. "
            + "37FD2 applies this as a signed floor in its ordinary current-component branch.");
    semanticFunction(0x3A4A0L, "f33_arbitrate_thermal_current_limits", v)
        .setComment("Compute both ECU minima, combine each with its motor limit6FAC/6FAE, and choose "
            + "bank0 iff6764&3==0. Publish effective limit to owner0 viaBB736, but publish ECU and motor "
            + "diagnostic activity/temperatures independently at6F6C..6F7C. No new-sample or heating proof.");
    semanticFunction(0xBB736L, "f33_set_current_limit_request", v,
        new ParameterImpl("owner", u32, currentProgram),
        new ParameterImpl("limit", u16, currentProgram))
        .setComment("For low8(owner)<10 replace BD34[owner] only. Request publication is distinct from "
            + "later masked reductions and current-control consumption.");
    semanticFunction(0x482BEL, "f33_filter_thermistor_channel0", v)
        .setComment("Filter unsigned6492 into7DD2/7DDC; mismatch of accumulator high16 and previous "
            + "output reseeds from the input before6A678. Map via31808 into signed7DCE.");
    semanticFunction(0x48326L, "f33_filter_thermistor_channel1", v)
        .setComment("Companion6498 ->7DD4/7DE0 -> signed7DD6, with the same coherence repair and ROM map. "
            + "This is software conditioning of staged inputs, not hardware sample-freshness proof.");
    semanticFunction(0x4838EL, "f33_update_thermistor_channels", v)
        .setComment("Run both channel filters; publish signed max(7DCE,7DD6) at7DDA and mark7DCC=5A. "
            + "Exact RDBI1063/1069 aliases expose this same publication, not two independent values.");
    semanticFunction(0x4DB3EL, "f33_rdbi_1034_callback", u32,
        new ParameterImpl("output", byteOut, currentProgram))
        .setComment("RDBI1034/1039 aliases: scale unsigned66BA by100/256, cap2500, encode BE16, return0. "
            + "Current EMPS_P5 names these battery voltage, with wire units0.01V.");
    semanticFunction(0x4DC9AL, "f33_rdbi_1063_callback", u32,
        new ParameterImpl("output", byteOut, currentProgram))
        .setComment("RDBI1063/1069 aliases: signed7DDA*10/128, narrow16, clamp[-500,2000], encodeBE16. "
            + "Current EMPS_P5 names thermistor temperature with wire units0.1degC.");
    semanticFunction(0x4E86AL, "f33_rdbi_1c06_callback", u32,
        new ParameterImpl("output", byteOut, currentProgram))
        .setComment("ECU overheat-prevention estimate:6F6C==0 emits7FFF sentinel, not zero degrees. "
            + "Otherwise scale signed6F7A*10/128 and clamp[-500,2000]; encodeBE16 and return0.");
    semanticFunction(0x4E8B8L, "f33_rdbi_1c07_callback", u32,
        new ParameterImpl("output", byteOut, currentProgram))
        .setComment("Motor overheat-prevention estimate:6F6D==0 emits7FFF sentinel; otherwise scale "
            + "signed6F7C*10/128 and clamp[-500,2000]. Diagnostic visibility is not the global limit winner.");
    semanticFunction(0xBB74AL, "f33_reduce_thermal_current_requests", u32)
        .setComment("Return min(22170, enabled BD34 owners). AF0CC=1 selects only owner0. Full R10 "
            + "return is consumed byBB88C; the former void inference lost this value.");
    semanticFunction(0xBB786L, "f33_reduce_other_current_requests", u32)
        .setComment("Return min(22170, BD34 owners excluded by AF0CC). Exact mask1 selects owners1..9, "
            + "including the retained thermal-release owner7.");
    semanticFunction(0xBB7C2L, "f33_reduce_service_current_requests", u32)
        .setComment("Return min(22170, BD34 owners whose AECD4 bit is clear). Exact mask21 excludes "
            + "owners0/5, not the retained thermal-release owner7.");
    semanticFunction(0xBB7FAL, "f33_publish_other_current_limit", v)
        .setComment("Use service reduction only for family0500,B37C==5A,B20E!=11/22; otherwise normal "
            + "nonthermal reduction. AF3C=3 at22170,0 atzero,1 otherwise. Under PMRFF80 publish limitAF40, "
            + "signed min(owner6,owner9) atAF42 and B37C atAF3D; publish route markerAF3E afterward.");
    semanticFunction(0xBB88CL, "f33_update_thermal_release_envelope", v)
        .setComment("Target is owner0 reduction. Drops apply immediately; rises hold if abs_sat(B054)<=256 "
            + "and previous output<=11085. Otherwise mode2 for BEE2<512 and BEF0==11 uses coefficient115828; "
            + "mode1 uses4666. Mode change resets counter/base to0/old output. Increment saturating counter; "
            + "candidate=base+floor(n*n*coefficient/65536), capped to target, with high-product overflow "
            + "also selecting target. Publish owner7 and BD48/4A/4C/4E; counts are invocations, not time.");
    semanticFunction(0xC1DE0L, "f33_snapshot_health_and_service_inputs", v)
        .setComment("Copy status, observer, analog and all ten BD34 current-limit owner cells into the "
            + "health/service snapshot, including B010[0..9]. B84B8 checks every owner except5 against22170. "
            + "This sequential snapshot is not an atomic hardware sample or instantaneous owner publication.");
    semanticData(0xAF0CCL, u32, "f33_thermal_current_owner_mask",
        "Mask1 selects thermal owner0; complement selects owners1..9.");
    semanticData(0xAECD4L, u32, "f33_service_current_owner_exclusions",
        "Mask21 excludes owner0 and owner5 in the special service reduction.");
    semanticData(0xAF0D8L, u32, "f33_thermal_release_coefficient_mode2",
        "Unsigned scalar115828 for the n-squared release envelope, not a CodeFlash pointer.");
    semanticData(0xAF0DCL, u32, "f33_thermal_release_coefficient_mode1",
        "Unsigned scalar4666 for the n-squared release envelope.");
  }
  private void annotateFaultActions() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType words = new PointerDataType(u16, 4);
    semanticFunction(0x3C008L, "f33_aggregate_fault_actions", v)
        .setComment("Select 24 current7200 or retained7320 records by71CC markers5A/A5, stride12. "
            + "Only words0/4 require their separate complements; words1/2/3 are ORed independently. "
            + "Qualify aggregate word4, optionally OR7440..7446 when71EC.bit15, dispatch four action "
            + "words, then mirror all five at71F4..71FC. Source stripping affects later aggregation.");
    semanticFunction(0x3C19CL, "f33_merge_fault_action_record", v,
        new ParameterImpl("actions", words, currentProgram),
        new ParameterImpl("slot", u32, currentProgram))
        .setComment("For low8(slot)<24, mutate the five-word input when its word4 overlaps71EC: "
            + "clear word0 bits12, word1 bits70 and word2 bitsC00 (hex masks). OR into current record "
            + "at7200+12*slot; AND corresponding word0/4 complements with inverse input. Does not mark "
            + "the record current. The sixth halfword in the stride is not part of this contract.");
    semanticFunction(0x3C7FEL, "f33_encode_fault_action_kind", v,
        new ParameterImpl("slot", u8, currentProgram),
        new ParameterImpl("kind", u8, currentProgram))
        .setComment("Build five action words, suppress the entire template if word4 intersects ROM317DC, "
            + "then merge into the slot. Word3 is ancillary action flags; word4 is qualification class. "
            + "Kind32(hex) sets word3.bit15, not the qualifier bit15. Kinds are not DTC identities.");
    semanticFunction(0x3BFCEL, "f33_qualify_fault_action_aggregate", v,
        new ParameterImpl("actions", words, currentProgram))
        .setComment("Optionally OR317D8 into local word4 only when317D4==5A (exact byte0 disables). "
            + "Classify word4, advance retained qualification, then maintain current records and overrides "
            + "from the original action words. Does not replace the caller's aggregate words.");
    semanticFunction(0x3BE88L, "f33_classify_fault_qualification", v,
        new ParameterImpl("classes", u32, currentProgram))
        .setComment("Classify low16 mask into71EE: zero->0, one bit->that bit, multiple bits->8000. "
            + "These internal classes are not diagnostic event IDs or OEM fault names.");
    semanticFunction(0x3BEBAL, "f33_vote_fault_qualification", u32)
        .setComment("Vote71EC with XOR5555/XORAAAA copies7108/710A using707AC; ignore voter status "
            + "and return the voted unsigned16 value in full R10.");
    semanticFunction(0x3BEDAL, "f33_update_fault_qualification", v)
        .setComment("Candidate71EE intersecting317DA=3E1C becomes8000. Nonzero candidate disjoint from "
            + "nonzero prior vote also becomes8000, then OR prior. Zero candidate retains prior except "
            + "clears4000 if prior bit15 is clear. Publish redundant qualification/limit;71E4=5A only "
            + "for prior0 -> new nonzero.");
    semanticFunction(0x3BDC6L, "f33_publish_fault_qualification_limit", v,
        new ParameterImpl("classes", u16, currentProgram))
        .setComment("Under PMRFFC0 publish71EC and XOR copies7108/710A, plus minimum enabled317E0 "
            + "entry at71F2 (default22170). Bits0/1 select14965, bits2..8 select11085, remaining bits "
            + "select22170. This is an amplitude bound, not a command or an age counter.");
    semanticFunction(0x3BF3AL, "f33_maintain_qualified_fault_actions", v,
        new ParameterImpl("mode_actions", u16, currentProgram),
        new ParameterImpl("status_actions", u16, currentProgram),
        new ParameterImpl("output_actions", u16, currentProgram))
        .setComment("On first nonzero qualification71E4==5A, strip masks12/70/C00 from current records "
            + "whose word4 intersects71EC, repairing word0 complements. Retained records are untouched. "
            + "With71EC.bit15, accumulate those masks in7440/42/44 and retain7446; otherwise clear overrides.");
    semanticFunction(0x3C290L, "f33_route_fault_status_actions", v,
        new ParameterImpl("actions", u32, currentProgram))
        .setComment("Bits2/1/0 or bit15-qualified6/5/4 select status4/3/2 viaBACF8. Active status "
            + "increments71F0 while <=317DE=50, so the retained ceiling is51. No action publishes "
            + "(counter<=50), then resets the counter only if unsignedEB9A>22169.");
    semanticFunction(0x3C470L, "f33_route_fault_output_actions", v,
        new ParameterImpl("actions", u32, currentProgram))
        .setComment("Route output action combinations through5737A owner2/5/6 and channel/validity "
            + "owners2/3/4. Some combinations awaitEB9A==0 orEB9C<=11085;71EC selects qualifier and "
            + "channel retention. These bitmask owners are distinct from the BD34 current-limit slots.");
    semanticFunction(0x3C6A8L, "f33_route_fault_ancillary_actions", v,
        new ParameterImpl("actions", u32, currentProgram))
        .setComment("Word3 routes event15, software substitutions, paired channel selections and "
            + "owner-specific validity actions. Bit15 publishes the4C5E8 flag for0351; it does not "
            + "set71EC.bit15. Request writes do not themselves prove hardware response.");
    semanticData(0x317E0L, new ArrayDataType(u16, 16, 2), "f33_fault_class_amplitude_limits",
        "Minimum active class limit published at71F2; bits0/1=14965,2..8=11085,9..15=22170.");
  }
  private void annotateDiagnosticEventLifecycle() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType bytes = new PointerDataType(u8, 4);
    CategoryPath category = new CategoryPath("/CamryF33");
    StructureDataType application = new StructureDataType(category, "F33DiagnosticApplicationSample", 0);
    application.add(new ArrayDataType(u8, 56, 1), "raw", "Software-source projection; not a hardware sample.");
    DataType applicationOut = new PointerDataType(resolve(application), 4);
    StructureDataType capture = new StructureDataType(category, "F33DiagnosticCapture", 0);
    capture.setPackingEnabled(true);
    capture.add(new ArrayDataType(u8, 72, 1), "profile_prefix", "Selected source profile.");
    capture.add(new ArrayDataType(u8, 72, 1), "supplemental", "Retained85AC copy or zero-filled.");
    capture.add(u16, "event", "Internal event index, not packed DTC.");
    capture.add(u16, "event_copy", "Duplicate event index, not an inverse.");
    capture.add(new ArrayDataType(u8, 36, 1), "extended_prefix", "Profile-dependent software fields.");
    capture.add(u16, "selected_sample", "Kind4 AC56; kind10 AFA4; default B02C.");
    capture.add(new ArrayDataType(u8, 30, 1), "extended_middle", "Profile-dependent software fields.");
    capture.add(ShortDataType.dataType, "ecu_thermal_estimate", "Signed6F7A publication.");
    capture.add(ShortDataType.dataType, "motor_thermal_estimate", "Signed6F7C publication.");
    capture.add(u8, "ecu_thermal_source", "6F6C source, independent of global limiting winner.");
    capture.add(u8, "motor_thermal_active", "6F6D activity.");
    capture.add(new ArrayDataType(u8, 18, 1), "extended_tail", "Software fields through offsetEF.");
    DataType captureType = resolve(capture);
    DataType captureOut = new PointerDataType(captureType, 4);
    semanticFunction(0x52784L, "f33_get_diagnostic_event_state", u32,
        new ParameterImpl("event", u32, currentProgram))
        .setComment("Low16 event1..17F(hex) returns bits0/1/2 from6090/60C0/60F0 bitmaps; otherwise0. "
            + "These three internal generations are not by themselves the UDS eight-bit status byte.");
    semanticFunction(0x51C66L, "f33_report_diagnostic_event_failure", v,
        new ParameterImpl("event", u32, currentProgram),
        new ParameterImpl("capture_kind", u16, currentProgram))
        .setComment("Low16 event1..17F, excluding lifecycle82D4 states1/2/4/6. Snapshot old82D5, then "
            + "set it5A if event descriptor byte4.bit7. Only entry current-bit0 clear invokes bitmap "
            + "failure, capture and classifier assertion; statistics path can run separately. The "
            + "second argument selects capture profile4/10/default, not an occurrence count.");
    semanticFunction(0x51D5EL, "f33_report_diagnostic_event_pass", v,
        new ParameterImpl("event", u32, currentProgram))
        .setComment("Same event/lifecycle admission as failure. Read ENTRY current bit, invoke bitmap "
            + "pass, then release the descriptor's classifier when entry bit was set. Thus5F85==AA "
            + "can inhibit bitmap mutation without inhibiting classifier decrement.");
    semanticFunction(0x522E4L, "f33_mark_diagnostic_event_failed", v,
        new ParameterImpl("event", u32, currentProgram),
        new ParameterImpl("prior_qualification", u8, currentProgram))
        .setComment("Unless5F85==AA, atomically set all three event bitmap bits on a new current failure; "
            + "dirty5F81/82 and5F84.bit1. Descriptor flags and packedDTC determine bounded pending-code "
            + "counter updates and6028/602A requests. No local event bounds check; caller owns admission.");
    semanticFunction(0x523E2L, "f33_mark_diagnostic_event_passed", v,
        new ParameterImpl("event", u32, currentProgram))
        .setComment("Unless5F85==AA, ordinary pass clears only current6090 bit and dirties5F81. "
            + "Exact exception list0E/51/BE/FF/20/120 clears all three bits even if only retained bits "
            + "were set, dirties5F81/82 and5F84.bit5. Does not itself clear captures or classifier latches.");
    semanticFunction(0x50FC8L, "f33_assert_diagnostic_classifier", v,
        new ParameterImpl("classification", u8, currentProgram))
        .setComment("Descriptor class2/4/8/0F/10/20/40/80/F0 selects its16-bit counter and class-specific "
            + "latches. Counter increments wrap16; not saturating. Unknown classes make no update.");
    semanticFunction(0x514BCL, "f33_release_diagnostic_classifier", v,
        new ParameterImpl("classification", u8, currentProgram))
        .setComment("Decrement the selected class counter only if nonzero. Existing class/aging flags "
            + "are not cleared here; classifier aging/projection remains a separate operation.");
    semanticFunction(0x51BB6L, "f33_gate_diagnostic_event_capture", v,
        new ParameterImpl("event", u32, currentProgram),
        new ParameterImpl("capture_kind", u16, currentProgram),
        new ParameterImpl("prior_qualification", u8, currentProgram))
        .setComment("Descriptor byte0 must intersect2, or6 when prior qualification==5A. Forward "
            + "capture kind and boolean prior qualification to52E18; event validity belongs to caller.");
    semanticFunction(0x51BE8L, "f33_update_diagnostic_event_statistics", v,
        new ParameterImpl("event", u32, currentProgram),
        new ParameterImpl("prior_qualification", u8, currentProgram))
        .setComment("Only prior qualification0 admits descriptor byte4 classes81/82/86..8C. Increment "
            + "their selected5470C/54632 counter up toFFFF. This can run even when current event already "
            + "failed, independently of first-failure bitmap/capture/classifier work.");
    semanticFunction(0x52E18L, "f33_capture_diagnostic_event", v,
        new ParameterImpl("event", u16, currentProgram),
        new ParameterImpl("capture_kind", u16, currentProgram),
        new ParameterImpl("qualified", u8, currentProgram))
        .setComment("Construct240-byte profile4/10/default record, fill supplemental72 bytes from85AC "
            + "or zeros when qualified==1, and write duplicate event words at90/92. Only then check "
            + "6150==AA storage inhibit. Under PMRFF00, unqualified first capture fills82DC once; "
            + "615A==5A and nonzero packedDTC distinct from both prior records also fills83CC. "
            + "Qualified capture fills84BC. Update occupancy/dirty flags and consume615A on replacement.");
    Function copy = semanticFunction(0x52A8AL, "f33_copy_diagnostic_capture", v,
        new ParameterImpl("destination", captureOut, currentProgram),
        new ParameterImpl("source", captureOut, currentProgram));
    String convention = "__f33_capture_copy";
    String prototype = "<prototype name=\"__f33_capture_copy\" extrapop=\"0\" stackshift=\"0\">"
        + "<input><pentry minsize=\"4\" maxsize=\"4\"><register name=\"r6\"/></pentry>"
        + "<pentry minsize=\"4\" maxsize=\"4\"><register name=\"r7\"/></pentry></input><output/>"
        + "<unaffected><register name=\"r2\"/><register name=\"sp\"/><register name=\"gp\"/>"
        + "<register name=\"tp\"/><register name=\"r6\"/><register name=\"r7\"/>"
        + "<register name=\"r8\"/><register name=\"r9\"/><register name=\"r10\"/>"
        + "<register name=\"r11\"/><register name=\"r12\"/><register name=\"r13\"/>"
        + "<register name=\"r14\"/><register name=\"r15\"/><register name=\"r16\"/>"
        + "<register name=\"r17\"/><register name=\"r18\"/><register name=\"r20\"/>"
        + "<register name=\"r21\"/><register name=\"r22\"/><register name=\"r23\"/>"
        + "<register name=\"r24\"/><register name=\"r25\"/><register name=\"r26\"/>"
        + "<register name=\"r27\"/><register name=\"r28\"/><register name=\"r29\"/></unaffected>"
        + "<killedbycall><register name=\"r1\"/><register name=\"r19\"/><register name=\"ep\"/>"
        + "<register name=\"lp\"/></killedbycall></prototype>";
    if (!prototype.equals(currentProgram.getOptions(SpecExtension.SPEC_EXTENSION)
        .getString("prototype_" + convention, null))) {
      new SpecExtension(currentProgram).addReplaceCompilerSpecExtension(prototype, monitor);
    }
    copy.setCallingConvention(convention);
    copy.setInline(false);
    copy.setComment("Copy60 words forward. Exact leaf changes only R1/R19/EP and flags; call also "
        + "changes LP. Its target-local convention preserves R10 carrying saved PMR in52E18. "
        + "Do not invent a mask return or rely on repeated-loop inlining, which fails at later calls.");
    semanticFunction(0x52A76L, "f33_clear_diagnostic_supplement", v,
        new ParameterImpl("destination", bytes, currentProgram))
        .setComment("Clear18 words (72 bytes); used only for the supplemental region, not the whole capture.");
    semanticFunction(0x52DFCL, "f33_copy_diagnostic_supplement", v,
        new ParameterImpl("destination", bytes, currentProgram),
        new ParameterImpl("source", bytes, currentProgram))
        .setComment("Copy18 words (72 bytes) forward; the retained85AC supplement is distinct from current profile data.");
    semanticFunction(0x53DB8L, "f33_build_diagnostic_capture_kind10", v,
        new ParameterImpl("output", captureOut, currentProgram))
        .setComment("Populate profile/extended fields from staged software sources and kind10 application "
            + "sample. Preserve supplemental/event regions for52E18. Thermal D8/DA/DC/DD fields copy "
            + "6F7A/6F7C/6F6C/6F6D; selected sampleB8 comes fromAFA4.");
    semanticFunction(0x53FFEL, "f33_build_diagnostic_capture_kind4", v,
        new ParameterImpl("output", captureOut, currentProgram))
        .setComment("Kind4 staged source bank; selected sampleB8 comes fromAC56. Same240-byte layout "
            + "and thermal publication fields, but not the same acquisition generation as kind10.");
    semanticFunction(0x54244L, "f33_build_diagnostic_capture_default", v,
        new ParameterImpl("output", captureOut, currentProgram))
        .setComment("Default staged source bank with application selector50; selected sampleB8 comes "
            + "fromB02C and limit/positive flag useAFD0 rather thanAF40. No hardware-freshness claim.");
    semanticFunction(0xBDF84L, "f33_snapshot_diagnostic_application", v,
        new ParameterImpl("output", applicationOut, currentProgram),
        new ParameterImpl("capture_kind", u16, currentProgram))
        .setComment("Forward real R6 output pointer to profile4/10/default snapshot. Each writes56 bytes; "
            + "the output buffer is not an unused integer argument.");
    semanticFunction(0xBDFACL, "f33_snapshot_diagnostic_application_kind10", v,
        new ParameterImpl("output", applicationOut, currentProgram))
        .setComment("56-byte staged application projection; signedAF40 supplies limit and positive flag, "
            + "AFA4 supplies selected sample. Trailing padding is explicitly zeroed.");
    semanticFunction(0xBE070L, "f33_snapshot_diagnostic_application_kind4", v,
        new ParameterImpl("output", applicationOut, currentProgram))
        .setComment("Same application layout as kind10 but selected sample comes fromAC56.");
    semanticFunction(0xBE134L, "f33_snapshot_diagnostic_application_default", v,
        new ParameterImpl("output", applicationOut, currentProgram))
        .setComment("Same application layout with signedAFD0 limit/positive flag and B02C sample.");
    semanticFunction(0x3210AL, "f33_publish_record_coherence_fault", v)
        .setComment("Only while6899==0: report event12E with capture kind10, retain slot23, merge action "
            + "kind1, mark current and latch6899=5A. Diagnostic admission failure does not suppress the "
            + "fault record or cause a later retry. Exact event maps to packed45D604/C05D604.");
    semanticFunction(0x3C116L, "f33_retain_and_clear_fault_record", v,
        new ParameterImpl("slot", u32, currentProgram))
        .setComment("Low8 slot<24: copy five current halfwords and two complements to retained storage, "
            + "markA5, clear five current words and set complementsFFFF. Stride-tail halfwords untouched.");
    semanticFunction(0x3C108L, "f33_select_retained_fault_record", v,
        new ParameterImpl("slot", u32, currentProgram))
        .setComment("StoreA5 to71CC[low8(slot)]; no local bounds check.");
    semanticFunction(0x3C184L, "f33_select_current_fault_record", v,
        new ParameterImpl("slot", u32, currentProgram))
        .setComment("Store5A to71CC[low8(slot)] only for slot<24.");
    semanticData(0xFEBE82DCL, new ArrayDataType(captureType, 3, 240), "f33_diagnostic_capture_slots",
        "First unqualified, distinct-code unqualified and qualified240-byte records. RAM publication is not durable persistence.");
  }
  private void annotateDiagnosticAgingAndClear() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType bytes = new PointerDataType(u8, 4);
    DataType halves = new PointerDataType(u16, 4);
    semanticFunction(0x510E0L, "f33_update_classifier_status_latch", u8)
        .setComment("Return/store actual R10 byte82B4. Zero latch asserts5A only for7F515A; nonzero "
            + "latch clears only when7F51 andE827 are both zero. Caller512E4 uses nonzero, not equality5A.");
    semanticFunction(0x5110AL, "f33_age_classifier_flag_group", v,
        new ParameterImpl("flags", bytes, currentProgram),
        new ParameterImpl("activity", bytes, currentProgram),
        new ParameterImpl("age", halves, currentProgram),
        new ParameterImpl("threshold", u16, currentProgram))
        .setComment("Snapshot unsignedE8B0 before PMRFF00. Consume activity5A and reset age, then "
            + "increment while age<=threshold. Clear whole flag group only for age>threshold andE8B0>=22170. "
            + "Consumed activity leaves age1; already-over-threshold age holds. No class-counter decrement.");
    semanticFunction(0x5116CL, "f33_age_classifier_retained_flags", v)
        .setComment("Same activity/strict age contract for82A5/82A8/82CE with exact600, but noE8B0 gate. "
            + "PMRFF00 protects updates; histories and active class counts are untouched.");
    semanticFunction(0x511B6L, "f33_age_classifier_groups", v)
        .setComment("Snapshot flagsA4/A5, then age nonzero groups in A3,A5,A4 order. Exact thresholds "
            + "200/600/200 are invocation counts, not elapsed time or event-bitmap aging.");
    semanticFunction(0x51208L, "f33_classifier_selector3_predicate", u32)
        .setComment("Return5A for zero6AF0, E8533/4, E854FF, E85511, sentinel33333333 inE91C/E924/E92C "
            + "or62E12 resultA55AA55A; otherwise0. Structural classifier priority, not a recovered OEM fault name.");
    semanticFunction(0x51266L, "f33_update_classifier_status22_edges", u32)
        .setComment("Each E857/8/9==22 asserts its82B1/2/3 latch; rising edges set82A4.bit5 and "
            + "activity82A75A. Other values clear that latch. Return5A while any source equals22.");
    semanticFunction(0x512E4L, "f33_update_diagnostic_classifier_output", v)
        .setComment("Update bank predicate, snapshot active counts, update status latch, then age flags. "
            + "Select using pre-aging counts and post-aging flags plus application predicates; publish "
            + "selector82A0 and its five-byte2A19C row. Cleared age flags do not imply cleared active counts "
            + "or event histories. Stateful selectors1/2 have separate counters82B6/82B8.");
    semanticFunction(0x51592L, "f33_reset_classifier_counts_and_flags", v)
        .setComment("Clear nine active counters and82A3/A4/A5 flags, reload ages200/200/600. "
            + "Do not clear activity82A6/A7/A8 or describe this as resetting every classifier field.");
    semanticFunction(0x4D63EL, "f33_diagnostic_clear_request_callback", u16)
        .setComment("Idle81B2 publishes1410 and requests operation1, returning pending4. Matching "
            + "family14 with low10 stays pending; terminal low0 returns0 and other terminal lows return6, "
            + "clearing81B2. Other families return6 without stealing their state. RAM reset is not durable completion.");
    semanticFunction(0x51714L, "f33_request_diagnostic_clear", u32)
        .setComment("Idle lifecycle82D4: set1, reset RAM state, then set high bit to81. Other states "
            + "except81 deduplicate request1 in four queue bytes82D8..DB and insert at normalized "
            + "circular index82D6. Return0, not a persistence acknowledgement or queue-full status.");
    semanticFunction(0x516DCL, "f33_clear_diagnostic_ram_generation", v)
        .setComment("If E856==11, save six current exceptional event IDs around bitmap reset, capture "
            + "maintenance and classifier reset, then restore them. Otherwise run the same reset without "
            + "preservation. Second retained history60F0 is not cleared by this operation.");
    semanticFunction(0x51674L, "f33_snapshot_preserved_current_events", v,
        new ParameterImpl("events", halves, currentProgram))
        .setComment("Write six halfwords: ROM2FC44 event ID when its entry current bit is set, otherwise0. "
            + "Retained-only exceptions do not qualify; the real buffer is12 bytes, not six byte flags.");
    semanticFunction(0x516A6L, "f33_restore_preserved_current_events", v,
        new ParameterImpl("events", halves, currentProgram))
        .setComment("Read six saved IDs/zero slots;525E0 restores valid events into three histories. "
            + "Pass descriptor byte1 in realR6 to classifier assertion when nonzero. Exact preserved-event "
            + "classes1/0 do not rebuild class2 counters; class1 has no50FC8 handler.");
    semanticFunction(0x5255AL, "f33_clear_current_and_first_event_history", v)
        .setComment("Phase5F85AA, clear12 words each6090/60C0/6120, rebuild descriptor bitmap, "
            + "set dirty5F81/82 and5F84.bit3, then phaseA5. Preserve second retained60F0.");
    semanticFunction(0x525A0L, "f33_clear_second_event_history", v)
        .setComment("Distinct operation: phase5F85AA, clear60F0, eight-byte banks5F71/5F79 and6028/602A, "
            + "set dirty5F84.bit4 and phaseA5. InitialAA store is instruction-visible despite C folding.");
    semanticFunction(0x51E46L, "f33_rebuild_event_descriptor_bitmap", v)
        .setComment("Rows0..17F inclusive: set6120 bit when descriptor byte2 OR byte5 is zero. "
            + "Includes row0; does not simply copy an existing failure history.");
    semanticFunction(0x52FCCL, "f33_mark_capture_slots_for_clear", v)
        .setComment("For occupied slots, marker44 drops occupancy and copies240-byte ROM defaults. "
            + "Other markers retain occupancy/data except event halfword90=0 and markerB7=22. "
            + "Set corresponding dirty bit2 and global phaseA5; if no slot is occupied, restore entry6150 phase. "
            + "Always set615A5A and clear6166. Retained supplement85AC is not erased.");
    semanticData(0x30E40L, u16, "f33_classifier_primary_age_threshold", "Exact200 invocations; strict expiry.");
    semanticData(0x30E42L, u16, "f33_classifier_secondary_age_threshold", "Exact200 invocations; strict expiry.");
    semanticData(0x30E44L, u16, "f33_classifier_retained_age_threshold", "Exact600 invocations; strict expiry.");
    semanticData(0x30E46L, u16, "f33_classifier_age_release_threshold", "Exact22170; unsignedE8B0 inclusive gate.");
  }
  private void annotateDiagnosticTransactions() throws Exception {
    DataType v = VoidDataType.dataType;
    semanticFunction(0x52186L, "f33_stage_diagnostic_history_record", v)
        .setComment("PMRFF00-protected160-byte object0 serialization: eight bytes each5F71/5F79 then "
            + "48 bytes each60C0/60F0/6120. Current bitmap6090 is excluded. Real66D6E acceptance is "
            + "ignored; RAM mirror/queue publication is not durable storage.");
    semanticFunction(0x521F2L, "f33_stage_diagnostic_invocation_record", v)
        .setComment("PMRFF00-protected object10 serialization:6028/602A halfwords plus zero word. "
            + "Submit real66D6E and restore mask without propagating acceptance.");
    semanticFunction(0x52222L, "f33_publish_dirty_diagnostic_records", v)
        .setComment("Snapshot5F84; permissionE8215A or dirty bits3/4 admit. Remove captured bits under "
            + "PMR, then separately snapshot payloads. MasksBA/52 select objects0/10; bit3 arms object0, "
            + "bit4 arms both completion trackers, irrespective of set-record acceptance.");
    semanticFunction(0x52108L, "f33_poll_diagnostic_record_completion", v)
        .setComment("Trackers5F83/86 equal1 inspect real software status: high20 stays1, high10 becomes2, "
            + "other becomes3. Wait for every armed peer; then phase5F85=55 if either failed, else0, "
            + "and clear trackers. Low nibble is ignored; no local timeout/retry or physical read.");
    semanticFunction(0x52296L, "f33_service_diagnostic_record_transaction", v)
        .setComment("Rebuild one pending derived bank, refresh derived presence, poll previous submissions "
            + "BEFORE publishing new dirty records. Completion later in the scheduler may start a new "
            + "dirty generation that cannot be serialized retroactively.");
    semanticFunction(0x51632L, "f33_repair_diagnostic_queue_consumer", v)
        .setComment("Only consumer82D7>=4 triggers bounded four-cell search beginning at producer82D6. "
            + "A valid consumer pointing to an empty slot is not rescanned.");
    semanticFunction(0x51A12L, "f33_dispatch_next_diagnostic_request", v)
        .setComment("Repair consumer, clear lifecycle82D4, then skip unsupported nonzero entries and "
            + "dispatch at most one of1/2/4/5/6. Clear consumed slot and advance circular consumer; "
            + "stop at empty slot or after four unsupported entries. Opcode3 is not recognized.");
    semanticFunction(0x51A98L, "f33_complete_diagnostic_request_and_dispatch", v)
        .setComment("Active lifecycle waits while ANY phase5F85/6150/8608/89C4 isAA/A5. Terminal "
            + "lifecycle-specific acknowledgement precedes bounded queue dispatch; phase55 is failure, "
            + "not hold. A dispatched request can immediately restore busy phase and dirty state.");
    semanticFunction(0x51B9EL, "f33_service_diagnostic_request_lifecycle", v)
        .setComment("Nonzero82D4 invokes completion/dispatch, then independently run51B64 mode-gated "
            + "callbacks. Those E85611/E85B0-or22 callbacks are not persistence acknowledgement.");
    semanticFunction(0x52B3CL, "f33_poll_diagnostic_capture_completion", v)
        .setComment("Objects1/2/3 use trackers6157..59: high20 pending, high10 success, other failure. "
            + "Only after no tracker1 remains clear trackers and publish aggregate6150=0/55.");
    semanticFunction(0x52BECL, "f33_publish_dirty_diagnostic_captures", v)
        .setComment("Permission5A or aggregate dirtybit2 admits publication. Captured masks&6 submit "
            + "240-byte objects1/2/3; bit2 arms trackers. Consume captured masks and ignore submission "
            + "acceptance; do not infer physical completion from armed software trackers.");
  }
  private void annotateAssistComposition() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    semanticFunction(0xC2B64L, "f33_update_signed_speed_torque_assist", v)
        .setComment("Select adjacent speed/torque curves throughC28FC, evaluate abs(C128), blend with C1A6/1024, "
            + "clamp magnitude to0..29125, then restore torque sign using AF888=1024/AF88A=-1024. "
            + "BF3C is signed32 assistance, not the nonnegative intermediate. Publish both curve slopes.");
    semanticFunction(0xC4DF2L, "f33_condition_assist_torque", v)
        .setComment("Clamp C150 to+/-2109, then advance retained two-stage recurrence. C12A==1 seeds "
            + "stage1 with low32(input*408474)/1024 and blend1024, but does not clear stage2 history. "
            + "Ordinary stage1 preserves low32 accumulator/shift arithmetic before signed division408474.");
    semanticFunction(0xC8678L, "f33_update_torque_rate_assist_compensation", v)
        .setComment("Map signed torque rateC266 and multiply by a narrowed factor from assistance slopeBF40 "
            + "and adjacent speed maps. Publish bounded signed32 C4C0. Preserve low32 products and the real "
            + "left-shift10 followed by signed division1024; these are not algebraic identities under wrap.");
    semanticFunction(0xD0162L, "f33_aggregate_internal_assist_terms", v)
        .setComment("Sum signed32 CC24/C39C and signed16 C3A0/C41E/C53A/C5A8, clamp to+/-5120, publish CC2C. "
            + "Nested rate, bounded-memory and moving-state terms retain separate attenuation/history. "
            + "ROM B1328 makes CC24 zero; B1371 disables C5A8 in this image.");
    semanticFunction(0xD0218L, "f33_aggregate_assist_command", v)
        .setComment("Publish signed32 CC48 without whole-sum saturation. AC2B==5A selects C4C0+C3BA+BF3C; "
            + "otherwise C7BF==1 selects C4C0+BF3C; ordinary branch adds C43C,CC2C,CBE8 and "
            + "clamp(s32(CB38)+s32(C5EE),+/-12002). Selection does not reset skipped producers.");
    semanticFunction(0xD0AF6L, "f33_run_assist_command_slice", v)
        .setComment("Capture AC31 once. Non5A skips selected producers while torque conditioning, base assistance "
            + "and other retained filters still advance. D0162 precedes fresh C266/C3BA/C4C0; D0218 sees those "
            + "new direct terms but the earlier nested aggregate. Finish through command clamp/gate/publication.");
    semanticFunction(0xCF33CL, "f33_update_angle_controller_output_envelope", v)
        .setComment("Select envelope mode, evolve retained0..256 gain, vote target and prior output, scale, slew "
            + "and saturate into CB38 plus duplicate publications. Never-active mode7 selects zero; after prior "
            + "activation the envelope may finish fading. Not an always-active ordinary return controller.");
    semanticFunction(0xCFD56L, "f33_update_windowed_excitation", v)
        .setComment("Run waveform and bounded AC24-memory terms only when CBEB and CBFE are nonzero. Mode "
            + "transition resets phase; window controls publication. Disable after activity resets retained "
            + "blocks, while already-idle disable publishes zero. OEM request identity remains unassigned.");
    semanticFunction(0xC51ACL, "f33_scale_torque_memory_correction", s16,
        new ParameterImpl("value", s16, currentProgram))
        .setComment("Unsigned C134 gain times signed16 R6, signed division1024, then SXH R10. Return and store "
            + "the same narrowed result in C136; not void.");
    semanticFunction(0xC7D5CL, "f33_scale_rate_assist_term", s16,
        new ParameterImpl("value", s16, currentProgram))
        .setComment("Unsigned C42C gain times signed16 R6, divide1024, SXH R10, store C42E and return it.");
    semanticFunction(0xC6D5EL, "f33_apply_internal_assist_attenuation", s32,
        new ParameterImpl("value", s32, currentProgram))
        .setComment("Apply C2F4 then C2F6 through separate low32 products and signed divisions1024. "
            + "Publish C2E4/C2E8 and return the second signed32 result in R10.");
  }
  private void annotateAssistConditioning() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    StructureDataType gain = new StructureDataType(new CategoryPath("/CamryF33"), "F33GainSlewState", 0);
    gain.setPackingEnabled(true);
    gain.add(u16, "down_target", "Selected only when direction2 and current>=this target.");
    gain.add(u16, "down_step", "Unsigned bounded downward step.");
    gain.add(u16, "up_target", "Default/upward target.");
    gain.add(u16, "up_step", "Unsigned bounded upward step.");
    gain.add(u16, "current", "Retained gain, updated by CE8DA.");
    gain.add(u8, "direction", "2 permits downward path; otherwise use upward/default path.");
    gain.add(u8, "padding", "Not consumed.");
    DataType gainPointer = new PointerDataType(resolve(gain), 4);
    semanticFunction(0xCE8DAL, "f33_step_retained_unsigned_gain", v,
        new ParameterImpl("state", gainPointer, currentProgram))
        .setComment("Generic retained unsigned gain step used by eight producers. Direction2 and "
            + "current>=down_target select bounded subtraction; otherwise step toward up_target. "
            + "Write only current at+8; not a torque-specific policy or elapsed-time controller.");
    Function prepare = semanticFunction(0xC5106L, "f33_prepare_torque_memory_gain_parameters", v,
        new ParameterImpl("state", gainPointer, currentProgram),
        new ParameterImpl("mode", u32, currentProgram));
    prepare.setComment("Low8 mode<7 selects16-byte D2FB8 row in bankAC3C&1: three dereferenced "
        + "halfword pointers plus inline up_target. Otherwise retain parameters and select direction1. "
        + "Real leaf preserves R6 for following CE8DA; inline its actual p-code, not an invented return.");
    prepare.setInline(true);
    long[][] otherPreparations = {
        {0xC660EL, 0xC2A4L}, {0xC6C24L, 0xC2F4L}, {0xC79BAL, 0xC3F4L},
        {0xC7CB6L, 0xC42CL}, {0xC7D76L, 0xC438L}, {0xC88B0L, 0xC4DCL}, {0xC8FFAL, 0xC544L}
    };
    for (long[] row : otherPreparations) {
      Function sibling = semanticFunction(row[0], "f33_prepare_gain_parameters_" + Long.toHexString(row[1]), v,
          new ParameterImpl("state", gainPointer, currentProgram),
          new ParameterImpl("mode", u32, currentProgram));
      sibling.setInline(true);
      sibling.setComment("Same12-byte state and preserved R6 as C5106, feeding CE8DA. Exact94-byte body "
          + "differs only in ROM pointer/global displacements; calibration values remain producer-local. "
          + "Inline real p-code so the shared helper's typed argument remains connected in every caller.");
    }
    StructureDataType calibration = new StructureDataType(new CategoryPath("/CamryF33"), "F33GainSlewCalibration", 0);
    calibration.setPackingEnabled(true);
    DataType halfwordPointer = new PointerDataType(u16, 4);
    calibration.add(halfwordPointer, "down_target", "Dereferenced by C5106.");
    calibration.add(halfwordPointer, "down_step", "Dereferenced by C5106.");
    calibration.add(u16, "up_target", "Inline value, not a pointer.");
    calibration.add(u16, "opaque_0a", "Not consumed by C5106.");
    calibration.add(halfwordPointer, "up_step", "Dereferenced by C5106.");
    semanticData(0xD2FB8L, new ArrayDataType(resolve(calibration), 14, 16),
        "f33_torque_memory_gain_calibrations",
        "Both banks/all seven modes resolve targets1024 and down_step0. Up_step0 in bank0,3 in bank1.");
    semanticFunction(0xC4CF0L, "f33_initialize_assist_torque_conditioner", v)
        .setComment("Initialize both retained recurrences, denominators408474/6347, outputs/history "
            + "and selector/repair latches. This reset is distinct from a later C12A reseed.");
    semanticFunction(0xC4D68L, "f33_update_retained_assist_torque_output", v)
        .setComment("Denominator1024 for C12A==1, otherwise6347 when unsigned AC4A<=512 or4607. "
            + "Rescale old accumulator using low32(newD<<10)/oldD, then add C108-oldC112. "
            + "Narrow low32(newAccumulator<<10)/newD into C112/C128; history is not independently cleared.");
    semanticFunction(0xC4E94L, "f33_update_torque_conditioner_slope_blend", v)
        .setComment("Produce C114 from previous BF40 before current base surface/slope publication. "
            + "Caller AC31 admission can retain this coefficient while torque recurrences advance.");
    semanticFunction(0xC4F04L, "f33_update_torque_conditioner_reseed_selector", v)
        .setComment("Threshold is unsigned AC84 only for ADFA.high0500 and AC41==5A, otherwise signed AC4C. "
            + "Previous command/base-assist magnitudes and low-nine AC50 bits gate entry/retention. "
            + "Entry also tests input/output magnitude difference and command-rate residual. "
            + "All four exact margins0 admit equality; common failure clears retained C12A.");
    semanticFunction(0xC4FDAL, "f33_repair_assist_torque_conditioner_state", v)
        .setComment("Strict consistency band(-384,384); equality repairs. Indications1/2 repair first "
            + "accumulator/model,4/8 repair second accumulator/output,10 initializes zero second denominator. "
            + "Second-stage differences SXH before comparison. Publish C11E and OR into sticky C120; do not write C128.");
    semanticFunction(0xC50E8L, "f33_initialize_torque_memory_gain", v)
        .setComment("Initialize C12C/C12E/C130/C132/C134 to1024. Combined with all exact D2FB8 rows, "
            + "this makes C134 invariant1024 from initialized state.");
    semanticFunction(0xC5164L, "f33_update_torque_memory_gain", v)
        .setComment("ModeCB00 only when CAB7==1, otherwise7. Prepare stack state, run real CE8DA "
            + "with preserved R6, then publish parameter tuple and C134. Not evidence of varying initialized gain.");
    semanticFunction(0xC51C6L, "f33_initialize_torque_memory_correction", v)
        .setComment("Reset bounded-memory correction state separately from torque recurrence initialization.");
    semanticFunction(0xC51F0L, "f33_update_torque_memory_band_amplitude", v)
        .setComment("Selector-strided torque-magnitude curve supplies C14A; diagnostic AC2B==5A requests zero band.");
    semanticFunction(0xC523CL, "f33_update_torque_memory_correction", v)
        .setComment("First use seeds signed32 offset=-AC90; in-band motion retains it and excursions move "
            + "the band boundary. Scalar low32(1440*u16(AC5E))/262144; zero scalar gives zero raw correction. "
            + "Speed gain then SXH, retained gain then SXH, and final+/-256 clamp publish C146.");
    semanticFunction(0xC52FAL, "f33_publish_bounded_assist_torque_input", v)
        .setComment("SXH(AC44+C146) BEFORE +/-2109 clamp into C150; not wide saturating addition.");
    semanticFunction(0xC5326L, "f33_update_torque_memory_speed_gain", v)
        .setComment("Unsigned ADF6 selects selector-strided speed curve into C148. Separate slow-domain "
            + "caller requires captured ACBC&8; base assist may consume retained gain.");
    semanticFunction(0xC5360L, "f33_initialize_assist_surface_selection", v)
        .setComment("Initialize retained source-transition qualification and source/selector publications.");
    semanticFunction(0xC5372L, "f33_qualify_assist_surface_transition", v)
        .setComment("Separate AD18/AD5F source snapshots and six signed wrapped-magnitude gates qualify "
            + "source mismatch. Exact B1172=0 makes every admitted invocation immediately set C154=5A "
            + "and clear C152; no nonzero debounce. Rejection clears both. Signed-minimum wrap is not saturation.");
    semanticFunction(0xC54A2L, "f33_update_retained_assist_surface_source", v)
        .setComment("Priority diagnostic66, AC94 magic override11, then five complement markers/AC50 "
            + "admission. Admitted but unqualified holds C158; qualified selects55 or77/44/88/0. "
            + "Failed marker/status admission clears source without waiting.");
    semanticFunction(0xC5554L, "f33_publish_assist_surface_selector", v)
        .setComment("Regenerate C156 from C158:77->1,44->2,88->3,otherwise0. Calibration source, not a command.");
    semanticFunction(0xC6182L, "f33_update_assist_torque_input_delta", v)
        .setComment("First use or C12A==1 suppresses delta but still updates previous C150. Otherwise "
            + "use full signed32 difference, low32 multiply1250/div16 and saturation+/-32767; "
            + "separately stored C250 is narrowed. Caller can retain this state on non5A generation.");
  }
  private void annotatePairedMonitorActions() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    semanticFunction(0x427F2L, "f33_publish_channel_monitor_actions_a", v)
        .setComment("Rebuild fault slot2 from14 statuses7818..7825: retain old five words, clear current, "
            + "merge pending/confirmed templates, then select current. Qualification71EC.bit0 and "
            + "diagnostic reporting admission are separate. Aggregate status10 has no diagnostic callbacks "
            + "and is excluded from the third summary and both channel caches.");
    semanticFunction(0x437B4L, "f33_publish_channel_monitor_actions_b", v)
        .setComment("Parallel slot3 reduction from7928..7935 with71EC.bit1 and distinct action kinds. "
            + "Phase status11 can coexist with aggregate status22, producing ancillary action without "
            + "phase confirmation; aggregate10 is excluded from third summary and channel caches.");
    semanticFunction(0x42A38L, "f33_set_channel_monitor_status_a", v,
        new ParameterImpl("index", u32, currentProgram), new ParameterImpl("status", u8, currentProgram))
        .setComment("Bound unsigned index<14 before storing one status byte at7818+index.");
    semanticFunction(0x439FAL, "f33_set_channel_monitor_status_b", v,
        new ParameterImpl("index", u32, currentProgram), new ParameterImpl("status", u8, currentProgram))
        .setComment("Bound unsigned index<14 before storing one status byte at7928+index.");
    semanticFunction(0x425F6L, "f33_step_channel_phase_monitors_a", v)
        .setComment("Three conditioned phase/comparison predicates run retained window qualification "
            + "with strict count>25 confirmation; separately aggregate any phase failure count>=1 "
            + "with zero confirmation limits. Event38/39/3A reporting does not gate action status.");
    semanticFunction(0x435B8L, "f33_step_channel_phase_monitors_b", v)
        .setComment("Parallel phase qualification and immediate aggregate counter monitor; diagnostic "
            + "events1B/1C/1D are separate from slot3 action kinds.");
    semanticFunction(0x4270EL, "f33_classify_channel_phase_sample_a", u32)
        .setComment("Failure22: sat_abs16(sample)>19968 or source62E4==0/comparison<-19968, "
            + "with unsigned7DA6<=4298 and signed62DC>-32768. Neutral33 on unadmitted abnormality, otherwise11.");
    semanticFunction(0x436D0L, "f33_classify_channel_phase_sample_b", u32)
        .setComment("Matching sample/comparison classifier with source62E5 and unsigned7DA8 admission.");
    semanticFunction(0x42D04L, "f33_classify_channel_sample_sum_a", u32)
        .setComment("Gate8B28&40004 clear and EB88==5A or all phase magnitudes<19968. "
            + "Admitted abs(sum)>4302 plus6368==5A fails22; <=4302 with valid5A and7B30FFFF passes11. "
            + "Other admitted cases33; failed admission44.");
    semanticFunction(0x43CC8L, "f33_classify_channel_sample_sum_b", u32)
        .setComment("Parallel sum classifier with6369 validity and7B32FFFF pass marker; same exact thresholds.");
    semanticFunction(0x42506L, "f33_step_channel_difference_latch_a", v)
        .setComment("Separate snapshot producer: abs(unsigned-sample difference sum)>21103 and "
            + "gate<=4298 accumulate failure through15, then next invocation publishes5A. "
            + "Healthy count reaches25 before next invocation clears failure/publishesA5; qualification freezes state.");
    semanticFunction(0x434C8L, "f33_step_channel_difference_latch_b", v)
        .setComment("Parallel delayed snapshot latch; retain failure high-water count. Later5CA3A "
            + "snapshot and4337A consumption are separate generations.");
    semanticFunction(0x42486L, "f33_sum_channel_snapshot_differences_a", s32)
        .setComment("Sum three unsigned sample differences from8238..823C versus822C..8230. "
            + "Exact31E5E==5A selects retained members refreshed by EAC1 and individual validity.");
    semanticFunction(0x43448L, "f33_sum_channel_snapshot_differences_b", s32)
        .setComment("Parallel sum from823E..8242 versus8232..8236 with31E66==5A and independent validity.");
    semanticFunction(0x41F74L, "f33_classify_channel_negative_pair_a", u32)
        .setComment("ROM28508 predicate: both signed comparison members<-19968 return22, otherwise11.");
    semanticFunction(0x42F32L, "f33_classify_channel_negative_pair_b", u32)
        .setComment("Parallel ROM2867C predicate; same strict signed bounds.");
    semanticFunction(0x422B8L, "f33_classify_channel_residual_a", u32)
        .setComment("ROM2853C callback; zero companion status and8B28&40004 admit residual/reference "
            + "windows. Failure uses abs(reference)<2895, abs(filtered)>6103, bounded abs(629E) "
            + "and unsigned minimum7DA6. Pass separately requires EB88==0 and7B34FFFF; verify CMP/branches, "
            + "not the decompiler's misleading overflow-expression precedence.");
    semanticFunction(0x43276L, "f33_classify_channel_residual_b", u32)
        .setComment("Parallel ROM286B0 residual classifier with7DA8 gate and7B36FFFF pass marker. "
            + "Unsigned minimum remains an independent conjunct of the pass branch.");
    semanticFunction(0x427C2L, "f33_classify_channel_phase_failure_count_a", u32)
        .setComment("Any retained phase failure counter>=exact byte threshold1 returns22, otherwise11. "
            + "ROM285A4 has no reporting callbacks; can confirm before an individual phase.");
    semanticFunction(0x43784L, "f33_classify_channel_phase_failure_count_b", u32)
        .setComment("Parallel immediate aggregate predicate at ROM28718; not itself a diagnostic event.");
    semanticFunction(0x42BEEL, "f33_classify_channel_raw_lower_bound_a", u32)
        .setComment("Low16 8B28 must clear. Any raw6238/3A/3C<10224 with its636C/D/E validity5A "
            + "fails22; all>=10224 and all valid pass11. Otherwise33; closed gate44.");
    semanticFunction(0x43BB0L, "f33_classify_channel_raw_lower_bound_b", u32)
        .setComment("Parallel623E/6240/6242 with636F/70/71 validity and high16 8B28 gate.");
  }
  private void annotateSharedMonitorComposition() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    StructureDataType state = new StructureDataType(new CategoryPath("/CamryF33"), "F33EscalatingMonitorState", 0);
    state.setPackingEnabled(true);
    state.add(u32, "packed_status", "Lower confirmed/pending status and upper transition publication.");
    for (String field : new String[]{"passing_count", "failing_count", "failing_high_water", "recovery_count", "elapsed_count"})
      state.add(u16, field, null);
    DataType stateType = resolve(state);
    DataType statePointer = new PointerDataType(stateType, 4);
    DataType halfwords = new PointerDataType(u16, 4);
    DataType words = new PointerDataType(u32, 4);
    semanticFunction(0x6BDB4L, "f33_step_escalating_monitor", u32,
        new ParameterImpl("state", statePointer, currentProgram),
        new ParameterImpl("calibration", halfwords, currentProgram),
        new ParameterImpl("callbacks", words, currentProgram))
        .setComment("Fourteen-byte retained state, eight-u16 calibration and17-slot callback vector. "
            + "Saturating counters, strict confirmation thresholds, recovery/elapsed escalation. "
            + "Packed result is written to state, NOT returned: normal API return is11.");
    semanticFunction(0x6BA64L, "f33_retain_disabled_escalating_monitor", v,
        new ParameterImpl("state", statePointer, currentProgram),
        new ParameterImpl("calibration", halfwords, currentProgram))
        .setComment("Reclassify from counters; retain confirmed22/escalated44 and confirmed pass2200, "
            + "discard pending paths. Failure high-water survives.");
    semanticFunction(0x6FF1CL, "f33_force_monitor_escalation", v,
        new ParameterImpl("state", statePointer, currentProgram),
        new ParameterImpl("calibration", halfwords, currentProgram),
        new ParameterImpl("callbacks", words, currentProgram))
        .setComment("Require finite fail/elapsed thresholds. Execute transition callbacks, publish44, "
            + "seed failure/elapsed to threshold+1, clear passing/recovery, preserve failure high-water.");
    long[] stateAddresses = {0x7C00L,0x7C1CL,0x7C74L,0x7C90L,0x7CF0L,0x7D04L,0x7CC8L,0x7CDCL,0x7D18L,0x7D2CL};
    for (int i = 0; i < stateAddresses.length; i++)
      semanticData(0xFEBE0000L + stateAddresses[i], stateType, "f33_shared_snapshot_monitor_" + i,
          "Slot0 retained state; snapshot-change detection and qualification are separate generations.");
    semanticFunction(0x47116L, "f33_publish_shared_snapshot_monitor_actions", v)
        .setComment("Rebuild slot0. Groups{0,2,8}/{1,3,9} select7CB7 with groupB priority. "
            + "Kinds05/10/11/2F/30; qualification can force escalation. Upper pending transitions "
            + "also affect686D selected-source hold without changing confirmed group selection.");
    semanticFunction(0x44928L, "f33_publish_shared_condition_monitor_actions", v)
        .setComment("Rebuild slot1 from nine statuses. Current classifier36066(2,643E)==1 OR earlier "
            + "snapshot63DC==1 selects kind0B for common confirmed fault, otherwise17. "
            + "Inverse monitors7/8 affect actions/summary but are excluded from both channel caches.");
    semanticFunction(0x473D6L, "f33_publish_shared_snapshot_monitor_status", v,
        new ParameterImpl("index", u32, currentProgram), new ParameterImpl("packed", u32, currentProgram))
        .setComment("Unsigned index<11: low byte to7CAC[index], bits16..23 to7CB9[index].");
    semanticFunction(0x44B0CL, "f33_publish_shared_condition_monitor_status", v,
        new ParameterImpl("index", u32, currentProgram), new ParameterImpl("packed", u32, currentProgram))
        .setComment("Unsigned index<9: publish only low status byte at79DC[index].");
    long[] predicateAddresses = {0x43FB2L,0x44064L,0x44654L,0x44702L,0x447C4L,0x448B2L,
        0x4611CL,0x461BAL,0x463F2L,0x46490L,0x46AA6L,0x46AC6L,0x46C58L,0x46F62L,
        0x47470L,0x4749CL,0x47538L,0x47564L,0x47606L,0x4770CL,0x4782AL,0x47860L,0x479C6L,0x479FCL};
    String[] predicateNames = {"inverse_gate_a","inverse_gate_b","direct_source_a","direct_source_b",
        "paired_shared_gate_a","paired_shared_gate_b","snapshot_status_a","snapshot_status_recovery_a",
        "snapshot_status_b","snapshot_status_recovery_b","selected_source_hold","selected_source_hold_recovery",
        "snapshot_sample_bounds_recovery_a","snapshot_sample_bounds_recovery_b",
        "snapshot_bit3_a","snapshot_bit3_recovery_a","snapshot_bit3_b","snapshot_bit3_recovery_b",
        "snapshot_low_gate_a","snapshot_low_gate_b","snapshot_bit2_a","snapshot_bit2_recovery_a",
        "snapshot_bit2_b","snapshot_bit2_recovery_b"};
    for (int i = 0; i < predicateAddresses.length; i++)
      semanticFunction(predicateAddresses[i], "f33_classify_" + predicateNames[i], u32)
          .setComment("Exact slot0/1 callback predicate. Return11/22/33/44 protocol; software source, "
              + "qualification and retained-snapshot conditions are not physical freshness guarantees.");
    long[] retained = {0x462D8L,0x465AEL,0x46D92L,0x4709CL,0x478CEL,0x47A6AL};
    String[] retainedNames = {"status_a","status_b","sample_bounds_a","sample_bounds_b","bit2_a","bit2_b"};
    for (int i = 0; i < retained.length; i++)
      semanticFunction(retained[i], "f33_request_shared_monitor_escalation_" + retainedNames[i], v)
          .setComment("Slot0 callback in the retained/escalation family; action and diagnostic reporting "
              + "remain independent. See exact callback vector and shared-monitor composition report.");
    semanticData(0xFEBE7CACL, new ArrayDataType(u8, 11, 1), "f33_shared_snapshot_status", "Slot0 lower statuses.");
    semanticData(0xFEBE7CB9L, new ArrayDataType(u8, 11, 1), "f33_shared_snapshot_transition", "Slot0 upper transition bytes.");
    semanticData(0xFEBE79DCL, new ArrayDataType(u8, 9, 1), "f33_shared_condition_status", "Slot1 statuses, including inverse7/8.");
  }
  private void annotateCommunicationStatusComposition() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    semanticFunction(0x49888L, "f33_update_application_receive_statuses", v)
        .setComment("Rebuild30 status bytes: raw-marker-nonzero bit0 plus confirmed-timeout bit1. "
            + "Admission can preserve old state; status generation is not a timestamp.");
    semanticFunction(0x498E0L, "f33_get_application_receive_status", u8,
        new ParameterImpl("selector", u32, currentProgram))
        .setComment("Read7F0E[selector] for selector<30, otherwise return1.");
    semanticFunction(0x49708L, "f33_classify_receive_monitor_admission", u8,
        new ParameterImpl("channel", u32, currentProgram), new ParameterImpl("group", u32, currentProgram),
        new ParameterImpl("selector", u32, currentProgram))
        .setComment("Channel1/2, grouped status, group enable/bypass11 and E82A gates. "
            + "Separate return2 retains prior monitor state instead of declaring healthy.");
    for (long address : new long[]{0x4975CL,0x497A8L})
      semanticFunction(address, address == 0x4975CL ? "f33_advance_receive_timeout" : "f33_retain_receive_timeout", u32,
          new ParameterImpl("selector", u32, currentProgram))
          .setComment("Raw marker5A drives strict counter>threshold timeout; other marker clears. "
              + "Confirmed timeout retention is distinct from raw invalidity.");
    semanticFunction(0x3CC36L, "f33_publish_receive_fault_bank", v,
        new ParameterImpl("bank", u8, currentProgram), new ParameterImpl("status", u8, currentProgram))
        .setComment("R6 bank/R7 status: zero publishes0 and healthy edge; invalid-only publishes22; "
            + "original bit1 set publishes44 and first-failure edge. Local latch updates despite Dem inhibition.");
    semanticFunction(0x3CCBEL, "f33_update_configured_receive_fault_banks", v)
        .setComment("Six280A4 rows join monitor bank, status selector and diagnostic event. "
            + "All exact-image mode bytesA5 admit publication. Preserve real R7 status dataflow3CCD6..3CCF4.");
    semanticFunction(0x3CE40L, "f33_update_communication_qualification_monitors", v)
        .setComment("Compose six receive rows, bus-status adapters and internal7F68 summary. "
            + "7F68 modes1/2 retain the previous summary; mode3 publishes44.");
    semanticFunction(0x3CEDAL, "f33_publish_selected_source_fault_edges", v)
        .setComment("Application selected-source diagnostic adapters; not a CAN frame decoder.");
    semanticFunction(0x3D0A0L, "f33_publish_source_family_fault_edges", v)
        .setComment("Application source-family diagnostic edges remain distinct from action selection.");
    semanticFunction(0x3D31CL, "f33_set_communication_monitor_status", v,
        new ParameterImpl("index", u32, currentProgram), new ParameterImpl("status", u8, currentProgram));
    semanticFunction(0x3D348L, "f33_compose_communication_status_fault_actions", v)
        .setComment("Rebuild slot16/kind16 from communication, receive-qualification and service-status "
            + "sources. Optional E824/7BBA gate affects7489 mask22, not44. Cache7475 is exact7486==22.");
    semanticFunction(0x3D436L, "f33_update_received_content_monitor_a", v)
        .setComment("Thresholds pass0/fail20, eventDE confirmed failure; callback vector has no ordinary pass reporter.");
    semanticFunction(0x3D4D0L, "f33_update_received_content_monitor_b", v)
        .setComment("Parallel content monitor with eventDF; not a raw timeout predicate.");
    semanticFunction(0x3D472L, "f33_classify_received_content_a", u32)
        .setComment("Return44 unless7F68==0 and8052==0, then22 iff804D==1, otherwise11.");
    semanticFunction(0x3D50CL, "f33_classify_received_content_b", u32)
        .setComment("Return44 unless7F68==0 and8052==0, then22 iff804E==1, otherwise11.");
    semanticFunction(0x3D6A6L, "f33_publish_local_status_link_fault", v)
        .setComment("8294.bit0 publishes local index0=22 and reportsEC; healthy publishes0 without ordinary pass.");
    semanticFunction(0x3D6D2L, "f33_compose_local_status_fault_actions", v)
        .setComment("Slot12 ORs only74A8/74A9/74AD. Complete22 selects kind17; ANY nonzero "
            + "publishes615B11 and prevents healthy diagnostic-cache refresh, even preconfirmation11.");
    semanticFunction(0x3D724L, "f33_set_local_status_monitor_status", v,
        new ParameterImpl("index", u32, currentProgram), new ParameterImpl("status", u8, currentProgram));
    semanticFunction(0x3D756L, "f33_update_qualified_local_status_monitor", v)
        .setComment("Index5, thresholds40/40; F3 failure callback, healthy-observed51E2C on pass confirmation.");
    semanticFunction(0x3D790L, "f33_classify_qualified_local_status", u32)
        .setComment("8278 fails22/passes11 only with qualification. Channel state2 counts67A0 "
            + "to5 before switching65F1 admission to65F6/7; closed gate44.");
    semanticFunction(0x3D83AL, "f33_update_paired_local_status_monitor", v)
        .setComment("Paired827D/827E monitor index4; any low status produces74C8 inhibition of individual predicates.");
    semanticFunction(0x3D916L, "f33_update_individual_local_status_a", v);
    semanticFunction(0x3D9C8L, "f33_update_individual_local_status_b", v);
    semanticFunction(0x3D892L, "f33_classify_paired_local_status", u32)
        .setComment("Failure only when both827D and827E equal5A.");
    semanticFunction(0x3D8B2L, "f33_classify_paired_local_status_recovery", u32)
        .setComment("Confirmed-state paired predicate; both827D/827E5A is failure.");
    semanticFunction(0x3D95EL, "f33_classify_individual_local_status_a", u32)
        .setComment("Return44 while74C8==5A; otherwise classify827E as22/11.");
    semanticFunction(0x3DA10L, "f33_classify_individual_local_status_b", u32)
        .setComment("Return44 while74C8==5A; otherwise classify827D as22/11.");
    semanticFunction(0x61404L, "f33_update_local_status_packet", v)
        .setComment("389E5A admits local four-halfword MMIO read, CRC and6000 header check. "
            + "At25 failed admitted updates latch3840; healthy publication does not clear an already latched fault. "
            + "Hardware packet availability remains an explicit boundary.");
    semanticFunction(0x615F0L, "f33_update_local_status_bit_latch", v)
        .setComment("Count published3838.bit10; exact BYTE315CA==20 latches3846. "
            + "Removing bit resets byte counter, not latch;61526 initializes it.");
    semanticData(0xFEBE7F0EL, new ArrayDataType(u8, 30, 1), "f33_application_receive_status",
        "Bit0 raw marker nonzero; bit1 confirmed timeout. Thirty status selectors, not CAN IDs.");
  }
  private void annotateAngleControllerComposition() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    semanticFunction(0xCEFFCL, "f33_select_angle_controller_mode", v)
        .setComment("DefaultCB00=7. RequireACBD0/CAFF1; ADB0 values1/4/11/10/19/18 map modes0..5.");
    semanticFunction(0xCD032L, "f33_update_selected_angle_target", v)
        .setComment("Compose interpolation and bounds; mode7 still produces target, with32766 limit overrides.");
    semanticFunction(0xCCF0EL, "f33_interpolate_selected_angle_target", v)
        .setComment("Signed32 AE90 doubled/clamped32767, then six-generation retained interpolation; "
            + "generations1..5 add delta/6 and generation6 selects complete target.");
    semanticFunction(0xCCFB2L, "f33_bound_selected_angle_target", v)
        .setComment("Bound target around prior selected value and magnitude, publishC8B8/C9A0/C9CC. "
            + "Ordinary limits are bank/mode dependent; mode7 bypasses slew with32766 limits.");
    semanticFunction(0xCEB7AL, "f33_update_angle_feedback_offset_and_publication", v)
        .setComment("Compose qualified offset capture and corrected feedback; lost qualification may hold last feedback.");
    semanticFunction(0xCEADAL, "f33_publish_offset_corrected_angle_feedback", v)
        .setComment("Saturate2*AE5E-voted(CABC/CAC0/CAC4) to signed16 including-32768; publishCAD2/4/6 when qualified.");
    semanticFunction(0xCD128L, "f33_update_angle_error_and_derivative", v)
        .setComment("Scale voted target/feedback2934/1024; error clamp18000. Separate bounded "
            + "error filterCA32 and retained derivative stateC910; derivative publication capped1600.");
    semanticFunction(0xCD094L, "f33_filter_angle_controller_measured_rate", v)
        .setComment("ClampC172 to4279 then retained69/256 filter; publishCA36/82/90, save old stateCA0E.");
    semanticFunction(0xCDFD4L, "f33_compose_angle_controller_terms", v)
        .setComment("Target-driven feedforward, error-driven P/I/D feedback, and direction/persistence attenuation.");
    semanticFunction(0xCD2A0L, "f33_update_angle_target_rate_feedforward", s32)
        .setComment("Bounded-difference target memory and retained rate filter; real R10 return consumed byCD538.");
    semanticFunction(0xCD382L, "f33_map_angle_target_feedforward", s32)
        .setComment("Mapped target shaping with real R10 return, not void despite original auto signature.");
    semanticFunction(0xCD45CL, "f33_calculate_angle_target_feedforward", s32)
        .setComment("Alternate speed/target formula, real R10 contribution returned toCD538 composition.");
    semanticFunction(0xCDA20L, "f33_update_angle_error_integral", v)
        .setComment("Mode0 clears. Otherwise ADBB1 or previousCA9B direction can block integration; "
            + "blocked update retains rawC91C. Allowed saturated addition uses voted bounded state. "
            + "Bank0 bound786432, bank1 bound589824.");
    semanticFunction(0xCDC48L, "f33_compose_filtered_angle_error_feedback", v)
        .setComment("P+integral/512+D clamps128000 then retained filtering. Exact second-stage "
            + "limits differ materially: inspected bank0 rows zero, bank1 mode-specific nonzero.");
    semanticFunction(0xCE144L, "f33_compose_angle_controller_prelimit_output", v)
        .setComment("Measured-rate term plus scaled feedforward/feedback. Nonzero active modes "
            + "retain output and suppress following limiting update while unsignedAE02<128.");
    semanticFunction(0xCE26EL, "f33_reset_angle_controller_control_state", v)
        .setComment("Mode7 clears controller error/PID/filter/composite states, seedsC950 from10*selected "
            + "target, but does NOT clear finalCB38 slew history or envelope accumulatorCB04.");
    semanticFunction(0xCE594L, "f33_limit_angle_controller_output", v)
        .setComment("ADBD scaling or special offsets, previous-output slew then absolute clamp. "
            + "Equality admitted; publishCAAC/CAAD/CA9B and retained center. Mode0 center is zero.");
    semanticFunction(0xCE6F4L, "f33_shape_angle_controller_target", v)
        .setComment("VoteCA46/7C/8A and apply sign-selected curve/1024 intoCA2E/80/8E.");
    semanticFunction(0xCCEB4L, "f33_publish_angle_controller_target_triplicate", v)
        .setComment("Retained gain, inner slew and magnitude clamp publish one target redundantly "
            + "toCAA6/8/A, not three independent producers. Exact inner limits65280/12800.");
    semanticFunction(0xCF148L, "f33_update_angle_controller_retained_envelope", v)
        .setComment("Unsigned accumulator rescaled when denominator changes; denominator floor1. "
            + "Mode11 rises,22/33 decay. Inclusive snap boundaries256-H/H. Consistent retained state "
            + "supports0..256; arbitrary corrupt accumulator is not universally clamped.");
    semanticFunction(0xCF22CL, "f33_vote_angle_target_and_update_fade_latch", v)
        .setComment("VoteCAA6/8/A. Non7 setsCB36=2; never-active mode7 suppresses target. "
            + "At gain0 clear activity but still admit that invocation's prior-active voted target.");
    semanticFunction(0xCF2B2L, "f33_slew_and_clamp_angle_controller_contribution", v)
        .setComment("Scale target*gain/256, slew from votedCB38/30/32, then absolute clamp and "
            + "triplicate publication. Zero gain/activity does not immediately erase output history.");
    semanticData(0xFEBECAA6L, new ArrayDataType(s16, 3, 2), "f33_angle_controller_target_triplicate",
        "One calculated target, three redundant publications.");
    semanticData(0xFEBECB04L, u32, "f33_angle_controller_envelope_accumulator", "Unsigned retained gain accumulator.");
    semanticData(0xFEBECB20L, new ArrayDataType(u16, 8, 2), "f33_angle_controller_envelope_parameters",
        "Gain,rise,fall,fast,snap,old denominator,final slew,final absolute. Mode7 retains coefficients.");
  }
  private void annotateCompensationPublication() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    semanticFunction(0xC7C78L, "f33_initialize_three_term_compensation", v)
        .setComment("Clear C420/C43C and initialize both retained gain families to1024.");
    semanticFunction(0xC7E36L, "f33_bound_three_term_compensation", v)
        .setComment("Sum fresh nonlinear torqueC44C with separately published C45A/C472; retain raw signed32 C420, bound by unsigned AC6C and publish signed16 C43C.");
    semanticFunction(0xC7E62L, "f33_initialize_nonlinear_torque_compensation", v)
        .setComment("Clear speed gain, curve products, bounded term and separate slope contribution.");
    semanticFunction(0xC7E88L, "f33_update_nonlinear_torque_speed_gain", v)
        .setComment("Unsigned ADF6 through AFB8E: gain1024 through7680, interpolate to614 at12800, then retain614.");
    semanticFunction(0xC7EA2L, "f33_update_nonlinear_torque_compensation", v)
        .setComment("Unsigned wrapping magnitude of C128 selects32-wide interpolation below index127; otherwise4876. Restore sign, narrow after C43E/1024 and AC6E/1024 products, bound10240 into C44C.");
    semanticFunction(0xC7F44L, "f33_update_nonlinear_torque_slope", v)
        .setComment("Use AFDA8 indexed by abs(C128)>>5, else2713. Narrow speed-scaled slope; AC2B5A publishes C44E zero, otherwise scale by AC6E/1024.");
    semanticFunction(0xC7FA0L, "f33_initialize_angle_rate_compensation", v)
        .setComment("Clear C450..C45A angle-rate compensation publications.");
    semanticFunction(0xC7FBAL, "f33_update_angle_rate_compensation_speed_gain", v)
        .setComment("Unsigned ADF6 through AFFC4: gain1024 through7680, interpolate tozero at12800, then zero.");
    semanticFunction(0xC7FD4L, "f33_update_angle_rate_compensation", v)
        .setComment("Signed sentinel lookup of wrapping abs(C172): zero through480, rise to384 at1280. Restore sign; narrow C450/1024 and AE4A/1024 products; bound768 into C45A.");
    semanticFunction(0xC8042L, "f33_initialize_directional_rate_compensation", v)
        .setComment("Clear counters/latch, map products, retained accumulatorC45C/filterC46C and independently published C472.");
    semanticFunction(0xC8070L, "f33_qualify_opposed_rate_direction", v)
        .setComment("ADF2>0 and C18A<-80 qualify direction1; ADF2<0 and C18A>80 direction2. Increment while count<=3; strict>3 latches. Counts may reset while latch persists until the rate sign releases it.");
    semanticFunction(0xC810AL, "f33_update_directional_rate_speed_gain", v)
        .setComment("Unsigned ADF6 lookup at AFFFE. All ordinary ordinates are zero in this exact image.");
    semanticFunction(0xC8124L, "f33_filter_directional_rate_compensation", v)
        .setComment("Gate signed mapped C18A with retained direction and speed gain, AE4A and optional CDF4/CDEC suppression, then C42C scaling. Suppression zeros input, not history. Update A=A+input-oldY; Y=s16(s32(A<<10)/5100). Exact AFFE6 ordinates are zero.");
    semanticFunction(0xC81CEL, "f33_publish_directional_rate_compensation", v)
        .setComment("Bound retained C46C to768 into C472. D0C44 invokes on captured CCA0==1, separately from foreground filter updates.");
    semanticFunction(0xD0C44L, "f33_run_observer_publication_slice", v)
        .setComment("Capture CCA0/CCA1. Alternate observer acquisition and C472 publication use old CCA0==1; increment modulo2/modulo10 afterward. This is software generation ordering, not a clock or jitter measurement.");
    semanticFunction(0xC2C32L, "f33_publish_combined_assist_slope", v)
        .setComment("Interpolate prior base-curve slopes BF34/BF36 with C1A6, add nonlinear slopeC44E, then clamp by AF88C into signed16 BF40.");
    semanticFunction(0xC6274L, "f33_repair_torque_rate_filter_state", v)
        .setComment("Two stages independently compare current/mirror outputs and accumulator residuals. Strict mirror windows; residual equality repairs accumulator. Publish per-cycle and latched repair bits before filtering.");
    semanticFunction(0xC61EAL, "f33_filter_torque_rate_compensation_input", v)
        .setComment("Cascade retained accumulators with AF860/AF864, preserving low32 shifts and signed division. Publish mirrors and bound second output by AF868 into C266.");
    semanticFunction(0xC73EEL, "f33_map_first_model_derivative_compensation", v)
        .setComment("Signed C23C lookup at B11D2 times bank-specific combined-slope map and retained C3B0 gain; publish signed32 C3A4.");
    semanticFunction(0xC7450L, "f33_map_second_model_derivative_compensation", v)
        .setComment("Signed C23E lookup at B11E6, narrow its C3B2-scaled product before B11AE slope scaling; publish signed32 ABB0.");
    semanticFunction(0xC74ACL, "f33_publish_model_derivative_compensation", v)
        .setComment("Add ABB0+C3A4, retain C3AC, then real low32 shift10/signed division1024 into C3A8 before B11AC bound into C3BA. Shift/division cannot be cancelled under wrap.");
    semanticFunction(0xC6F58L, "f33_sum_nonlinear_and_moving_assist", v)
        .setComment("Publish C358=C348+C5F0 with machine signed32 arithmetic.");
    semanticFunction(0xC6F68L, "f33_bound_nonlinear_and_moving_assist", v)
        .setComment("Bound C358 to exact B00E8=5120 and publish signed32 C39C for the nested assist aggregate.");
    semanticFunction(0xD0768L, "f33_interpolate_signed_sentinel_curve", s32,
        new ParameterImpl("points", new PointerDataType(s16, 4), currentProgram),
        new ParameterImpl("input", s16, currentProgram))
        .setComment("Signed16 axis and ordinate pairs; 7FFF axis sentinel returns previous ordinate. Endpoint hold or signed32 linear interpolation with sign-extended16 result; no table-order/extent validation.");
    semanticFunction(0xD0844L, "f33_interpolate_unsigned_axis_sentinel_curve", s32,
        new ParameterImpl("points", new PointerDataType(u16, 4), currentProgram),
        new ParameterImpl("input", u16, currentProgram))
        .setComment("Unsigned16 axis, signed16 ordinate pairs; FFFF axis sentinel. Endpoint hold or signed32 interpolation and sign-extended16 result. SXH and ZXH input contracts differ from D0768.");
    semanticData(0xAFFD8L, s32, "f33_directional_rate_filter_denominator",
        "Exact5100; scalar denominator, not a code pointer.");
    semanticData(0xB00E8L, s32, "f33_nonlinear_moving_assist_limit",
        "Exact5120 signed32 nested-term magnitude bound, not a pointer.");
    semanticData(0xB1324L, s32, "f33_nested_assist_sum_limit",
        "Exact5120 signed32 aggregate bound, not a pointer.");
  }
  private void annotateTxPublication() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType bytes = new PointerDataType(u8, 4);
    DataType halfwords = new PointerDataType(u16, 4);
    StructureDataType info = new StructureDataType(category, "F33PduInfo", 0);
    info.setPackingEnabled(true);
    info.add(bytes, "data", "Application or queued payload pointer.");
    info.add(u16, "length", "Byte extent.");
    info.add(u16, "opaque_06", "Not read by the recovered TX paths.");
    DataType infoPointer = new PointerDataType(resolve(info), 4);
    StructureDataType record = new StructureDataType(category, "F33CanIfTxRecord", 0);
    record.setPackingEnabled(true);
    record.add(u32, "raw_id", "Includes protocol/format flags.");
    record.add(u16, "source_pdu", "Decoded source namespace.");
    record.add(u8, "class_flags", "Queue/callback class, not an on-wire byte.");
    record.add(u8, "length", "Payload byte extent.");
    record.add(bytes, "data", "Copied before ordinary controller admission.");
    DataType recordPointer = new PointerDataType(resolve(record), 4);
    StructureDataType queue = new StructureDataType(category, "F33CanQueueDescriptor", 0);
    queue.setPackingEnabled(true);
    queue.add(u16, "capacity_words", "Includes end allowance.");
    queue.add(u8, "opaque_02", "Unassigned descriptor byte.");
    queue.add(u8, "completion_policy", "Zero permits immediate next scheduling.");
    queue.add(u8, "hardware_group", "Retained hardware-state selector.");
    queue.add(u8, "opaque_05", "Unassigned descriptor byte.");
    queue.add(u16, "driver_handle", "Handle in the lower driver namespace.");
    queue.add(u16, "queue_index", "Selects cursor triple and buffer.");
    DataType queueType = resolve(queue);
    DataType queuePointer = new PointerDataType(queueType, 4);
    StructureDataType driver = new StructureDataType(category, "F33CanDriverPdu", 0);
    driver.setPackingEnabled(true);
    driver.add(u16, "confirmation_handle", "Software completion routing.");
    driver.add(u8, "length", "Payload byte extent.");
    driver.add(u8, "opaque_03", "Not assigned an OEM meaning.");
    driver.add(u32, "raw_id", "Bit30 selects the FD route.");
    driver.add(bytes, "data", "Retained queue payload, not live COM storage.");
    DataType driverPointer = new PointerDataType(resolve(driver), 4);
    StructureDataType slot = new StructureDataType(category, "F33SecOcQueueSlot", 0);
    slot.setPackingEnabled(true);
    slot.add(u16, "length", "Application extent excluding reserved trailer.");
    slot.add(u16, "next", "Queue linkage.");
    slot.add(u16, "next_inverse", "Complemented linkage.");
    slot.add(u16, "opaque_06", "Unassigned slot field.");
    semanticFunction(0x7E13AL, "f33_service_com_tx_publication", v)
        .setComment("Apply group transitions, service countdowns, then bounded dispatch. Exact21C5E allows one attempt per group per invocation.");
    semanticFunction(0x7D8AEL, "f33_apply_com_tx_group_transition", v,
        new ParameterImpl("group", u8, currentProgram))
        .setComment("Enable/disable clears pending classes and updates flags/countdowns; neither transition copies or clears live COM payload.");
    semanticFunction(0x7DB0CL, "f33_service_com_tx_countdowns", v)
        .setComment("Advance periodic and minimum-delay countdowns; due requests enter pending bitmaps separately from payload generation.");
    semanticFunction(0x7DCA0L, "f33_select_admissible_com_tx", s32,
        new ParameterImpl("group", u8, currentProgram),
        new ParameterImpl("selected_pdu", halfwords, currentProgram))
        .setComment("Select admitted event before periodic request, zero minimum delay, active group and valid clear inhibit pair. Return2 event,1 periodic,-20 none.");
    semanticFunction(0x7DF14L, "f33_dispatch_one_com_tx", s32,
        new ParameterImpl("group", u8, currentProgram))
        .setComment("Sample live COM after admission. Lower return2 maps to-19 and retains pending; other lower failures and success consume both pending classes. Exact normal descriptors bypass optional COM scratch/callout.");
    semanticFunction(0x81A7EL, "f33_route_com_tx", u32,
        new ParameterImpl("pdu", u16, currentProgram),
        new ParameterImpl("info", infoPointer, currentProgram))
        .setComment("Map route namespace and forward R7 descriptor unchanged to the configured upper TX dispatcher.");
    semanticFunction(0x81AB2L, "f33_dispatch_upper_tx_route", u32,
        new ParameterImpl("pdu", u16, currentProgram),
        new ParameterImpl("info", infoPointer, currentProgram))
        .setComment("Route classic traffic to CanIf and protected PDU0 to SecOC; R7 descriptor is a real preserved argument.");
    semanticFunction(0x7FEF8L, "f33_canif_transmit", u32,
        new ParameterImpl("source_pdu", u16, currentProgram),
        new ParameterImpl("info", infoPointer, currentProgram))
        .setComment("Decode source namespace and construct transmit record. Real R10 return defaults1 and propagates7FD46 status; not void.");
    semanticFunction(0x7FD46L, "f33_snapshot_and_enqueue_can_tx", u32,
        new ParameterImpl("controller", u8, currentProgram),
        new ParameterImpl("route", u16, currentProgram),
        new ParameterImpl("record", recordPointer, currentProgram))
        .setComment("Normal class first copies up to64 bytes into4FB2 and calls811BE, before controller/route/capacity admission. Queue-full2 preserves old queue but scratch already contains newer data.");
    semanticFunction(0x7FC0EL, "f33_enqueue_large_can_tx", u32,
        new ParameterImpl("record", recordPointer, currentProgram),
        new ParameterImpl("queue_index", u16, currentProgram),
        new ParameterImpl("capacity_words", u16, currentProgram))
        .setComment("Large-record queue path with retained cursor/capacity accounting; queue admission is not physical transmission.");
    semanticFunction(0x8ED8EL, "f33_secoc_transmit", u32,
        new ParameterImpl("source_pdu", u16, currentProgram),
        new ParameterImpl("info", infoPointer, currentProgram))
        .setComment("Require54F4FE01, nonnull descriptor/data, mapped source0 and exact allowed length4..32 before protected claim.");
    semanticFunction(0x8FABAL, "f33_claim_secoc_tx_snapshot", u32,
        new ParameterImpl("profile", u16, currentProgram),
        new ParameterImpl("info", infoPointer, currentProgram))
        .setComment("Require5568E1/55695A; claimD2/A5 and increment generation before copy. Subtract four reserved bytes. Occupied rejection21 preserves prior snapshot/head/count but COM consumes this request.");
    semanticFunction(0x8025AL, "f33_service_can_tx_queues", v,
        new ParameterImpl("controller", u8, currentProgram))
        .setComment("Scan retained queues and attempt hardware admission; separate from COM publication and queue-copy generation.");
    semanticFunction(0x8015CL, "f33_attempt_queued_can_tx", v,
        new ParameterImpl("controller", u8, currentProgram),
        new ParameterImpl("route_index", u8, currentProgram),
        new ParameterImpl("descriptor", queuePointer, currentProgram),
        new ParameterImpl("cursors", halfwords, currentProgram))
        .setComment("Validate retained record/inverse and bounds, pass queued payload to85112. Rejection marks3C without consuming occupancy; admission marks hardware group and queue5A.");
    semanticFunction(0x8043CL, "f33_complete_queued_can_tx", v,
        new ParameterImpl("controller_route", u16, currentProgram))
        .setComment("Queue state5A advances read cursor and subtracts occupied words; state3C does not consume the queued record.");
    semanticFunction(0x85112L, "f33_driver_admit_can_tx", u32,
        new ParameterImpl("driver_handle", u16, currentProgram),
        new ParameterImpl("pdu", driverPointer, currentProgram))
        .setComment("Require physical-channel initialization sentinel; choose classic853AA or FD8549E by raw-ID bit30. Subsequent CFDTMC request store is not proof of bus delivery.");
    semanticFunction(0x815A0L, "f33_route_secured_lower_tx", u32,
        new ParameterImpl("pdu", u16, currentProgram),
        new ParameterImpl("info", infoPointer, currentProgram))
        .setComment("Forward secured lower TX with preserved descriptor R7; no omitted argument in the actual ABI.");
    semanticFunction(0x901D2L, "f33_secoc_lower_tx", u32,
        new ParameterImpl("pdu", u16, currentProgram),
        new ParameterImpl("info", infoPointer, currentProgram))
        .setComment("Protected lower-route forwarding preserves R7 descriptor; application snapshot admission remains distinct from MAC/lower transmission completion.");
    semanticData(0x21ACCL, new ArrayDataType(queueType, 5, 10), "f33_can_queue_descriptors",
        "Five10-byte queue/hardware descriptors; software queue admission is separate from driver admission.");
    semanticData(0xFEBE48DAL, new ArrayDataType(u16, 15, 2), "f33_can_tx_queue_cursors",
        "Five triples: write cursor, read cursor, occupied words.");
    semanticData(0xFEBE493EL, new ArrayDataType(u8, 5, 1), "f33_com_tx_pdu_flags", "Normal COM TX PDU flags.");
    semanticData(0xFEBE496EL, new ArrayDataType(u16, 5, 2), "f33_com_tx_periodic_countdowns", "Separate from payload generation.");
    semanticData(0xFEBE4978L, new ArrayDataType(u16, 5, 2), "f33_com_tx_minimum_delay_countdowns", "Zero required for dispatch admission.");
    semanticData(0xFEBE4A34L, new ArrayDataType(u8, 2, 1), "f33_com_tx_inhibit_pair", "Bitmap and inverse; inconsistent pair rejects admission.");
    semanticData(0xFEBE4A39L, new ArrayDataType(u8, 6, 1), "f33_com_tx_pending_and_group_state",
        "Periodic/event pending, desired/current group mask, event/periodic admission enables.");
    semanticData(0xFEBE5458L, resolve(slot), "f33_secoc_tx_queue_slot", "Initialized after application copy, before head publication.");
    semanticData(0xFEBE5460L, new ArrayDataType(u16, 2, 2), "f33_secoc_tx_queue_head_pair", "Head and inverse.");
    semanticData(0xFEBE5488L, new ArrayDataType(u8, 32, 1), "f33_secoc_tx_application_snapshot", "Ordinary32-byte COM input copies28 application bytes here.");
  }
  private void annotatePairedSourceMonitorComposition() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    semanticFunction(0x3DDAEL, "f33_step_paired_source_counter_monitor_a", v)
        .setComment("Own qualification bit7 clear admits primary A; exact pass/fail25, strict26 confirmation. Disable clears cause bytes but retains confirmed state.");
    semanticFunction(0x3DF4EL, "f33_step_paired_source_counter_monitor_b", v)
        .setComment("Parallel primary B gated by bit8, with separate counter snapshots and retained state.");
    semanticFunction(0x3E3FAL, "f33_step_paired_source_mask_monitor_a", v)
        .setComment("Own bit7 admission and primary status exactlyzero precede maskA monitor; pass/fail25 with windows500.");
    semanticFunction(0x3E4CCL, "f33_step_paired_source_mask_monitor_b", v)
        .setComment("Parallel maskB monitor under own bit8; staged mask and counter snapshots need not share an acquisition generation.");
    semanticFunction(0x3DA8AL, "f33_step_paired_source_difference_monitors_a", v)
        .setComment("Step delayed-difference indices6/7 without wrapper qualification disable. Qualification can permit failure while preventing pass.");
    semanticFunction(0x3DC16L, "f33_step_paired_source_difference_monitors_b", v)
        .setComment("Parallel delayed-difference indices8/9, with independent retained windows and diagnostic reporting admission.");
    semanticFunction(0x3E172L, "f33_accumulate_paired_source_difference_counts", v)
        .setComment("Classify signed wrapped differences and retained failures; increment wrapping counters754F..7552. Later snapshot/recomparison, not direct per-cycle fail status.");
    semanticFunction(0x3E1EAL, "f33_publish_paired_source_difference_changes", v)
        .setComment("Compare642C..642F against7555..7558, publish changed bits1/2/10/20 at7554 and refresh comparison snapshots.");
    semanticFunction(0x3E0C2L, "f33_classify_paired_source_sample_differences", u32)
        .setComment("Signed16-wrapped824C-824E,824C-8250,8250-8252 outside inclusive[-1274,1274] set bits0/1/2; equality does not fail.");
    semanticFunction(0x3E112L, "f33_classify_paired_source_difference_first", u32,
        new ParameterImpl("mask", u32, currentProgram))
        .setComment("Combine raw difference mask with confirmed first-group statuses.");
    semanticFunction(0x3E132L, "f33_classify_paired_source_difference_middle", u32,
        new ParameterImpl("mask", u32, currentProgram))
        .setComment("Combine middle raw difference and retained paired monitor confirmations.");
    semanticFunction(0x3E152L, "f33_classify_paired_source_difference_last", u32,
        new ParameterImpl("mask", u32, currentProgram))
        .setComment("Combine last raw difference and retained paired monitor confirmations.");
    semanticFunction(0x3E3C4L, "f33_publish_paired_source_monitor_status", v,
        new ParameterImpl("index", u32, currentProgram),
        new ParameterImpl("packed", u32, currentProgram))
        .setComment("Unsigned low8 index<10: low status byte to755C[index], bits16..23 to756A[index]. Normal producer census covers0/1/2/3/6/7/8/9.");
    semanticFunction(0x3E230L, "f33_publish_paired_source_monitor_actions", v)
        .setComment("Rebuild slot4 from groups0/2/6/7 and1/3/8/9; confirmed22 selects kinds35/36. Transition11 plus exact lower OR11 holds7576/7578; otherwise refresh6292/6298. Diagnostic admission does not gate action/caches.");
    semanticFunction(0x3DE00L, "f33_classify_paired_source_counter_changes_a", u32)
        .setComment("Compare four wrapping counter snapshots; actual invocation refreshes them even on44, but confirmed retained failure bypasses predicate.");
    semanticFunction(0x3DFA0L, "f33_classify_paired_source_counter_changes_b", u32)
        .setComment("Compare four wrapping counter snapshots; actual invocation refreshes them even on44, but confirmed retained failure bypasses predicate.");
    semanticFunction(0x3E442L, "f33_classify_paired_source_status_masks_a", u32)
        .setComment("Admission and own primary status exactlyzero required; either staged mask intersecting05A0 fails.");
    semanticFunction(0x3E514L, "f33_classify_paired_source_status_masks_b", u32)
        .setComment("Admission and own primary status exactlyzero required; either staged mask intersecting05A0 fails.");
    semanticFunction(0x3DAEAL, "f33_classify_paired_source_delayed_difference_aa", u32)
        .setComment("Changed bit fails under admission and primary-zero; pass requires whole7554 zero, ownFFFF marker and own qualification bit clear, otherwise33.");
    semanticFunction(0x3DB68L, "f33_classify_paired_source_delayed_difference_ab", u32)
        .setComment("Changed bit fails under admission and primary-zero; pass requires whole7554 zero, ownFFFF marker and own qualification bit clear, otherwise33.");
    semanticFunction(0x3DC76L, "f33_classify_paired_source_delayed_difference_ba", u32)
        .setComment("Changed bit fails under admission and primary-zero; pass requires whole7554 zero, ownFFFF marker and own qualification bit clear, otherwise33.");
    semanticFunction(0x3DCF4L, "f33_classify_paired_source_delayed_difference_bb", u32)
        .setComment("Changed bit fails under admission and primary-zero; pass requires whole7554 zero, ownFFFF marker and own qualification bit clear, otherwise33.");
    semanticData(0xFEBE755CL, new ArrayDataType(u8, 10, 1), "f33_paired_source_monitor_status", "Slot4 lower statuses;4/5 excluded from reduction.");
    semanticData(0xFEBE756AL, new ArrayDataType(u8, 10, 1), "f33_paired_source_monitor_transition", "Upper packed transition bytes.");
  }
  private void annotateDiagnosticServiceAdmission() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType bytes = new PointerDataType(u8, 4);
    DataType halfwords = new PointerDataType(u16, 4);
    DataType infoPointer = new PointerDataType(
        currentProgram.getDataTypeManager().getDataType("/CamryF33/F33PduInfo"), 4);
    StructureDataType message = new StructureDataType(category, "F33DcmMessageContext", 0);
    message.setPackingEnabled(true);
    message.add(bytes, "request", "Advanced after admitted SID/subfunction prefixes.");
    message.add(u32, "request_length", "Remaining request bytes.");
    message.add(bytes, "response", "Advanced past separately counted prefixes.");
    message.add(u32, "response_length", "Response body length, excluding retained prefix count.");
    message.add(u8, "addressing_kind", "Low bit supplied to application gate;1 selects functional response suppression.");
    message.add(u8, "suppress_positive", "Captured subfunction bit7.");
    message.add(u16, "opaque_12", "Not interpreted here.");
    message.add(u32, "response_capacity", "Remaining response capacity after prefix reservation.");
    message.add(u8, "service_id", "Original request SID retained by91566.");
    message.add(u8, "opaque_19", "Not interpreted here.");
    message.add(u16, "service_list_selector", "Selector2/3/4; not a CAN channel identity.");
    DataType messageType = resolve(message);
    DataType messagePointer = new PointerDataType(messageType, 4);
    FunctionDefinitionDataType callback = new FunctionDefinitionDataType(category, "F33DcmServiceCallback");
    callback.setReturnType(v);
    callback.setArguments(new ParameterDefinitionImpl("operation", u8, null),
        new ParameterDefinitionImpl("message", messagePointer, null));
    DataType callbackPointer = new PointerDataType(callback, 4);
    StructureDataType subfunction = new StructureDataType(category, "F33DcmSubfunction", 0);
    subfunction.setPackingEnabled(true);
    subfunction.add(callbackPointer, "callback", "Fixed operation callback or null.");
    subfunction.add(bytes, "security", "Null list independently admits security check.");
    subfunction.add(bytes, "sessions", "Allowed session bytes.");
    subfunction.add(u8, "subfunction", "Compared with request byte1 masked7F.");
    subfunction.add(u8, "security_count", "Non-null zero-count list rejects.");
    subfunction.add(u8, "session_count", "Session list extent.");
    subfunction.add(u8, "opaque_0f", "Not interpreted here.");
    DataType subfunctionPointer = new PointerDataType(resolve(subfunction), 4);
    StructureDataType service = new StructureDataType(category, "F33DcmService", 0);
    service.setPackingEnabled(true);
    service.add(callbackPointer, "callback", "Direct service callback or null.");
    service.add(bytes, "security", "Exact configured service lists are null.");
    service.add(bytes, "sessions", "Allowed sessions, distinct from application traffic gate.");
    service.add(subfunctionPointer, "subfunctions", "Fixed16-byte records.");
    service.add(u8, "sid", "Request service identifier.");
    service.add(u8, "has_subfunctions", "Exact1 selects generic subfunction dispatch except SID31.");
    service.add(u8, "security_count", "Security list extent.");
    service.add(u8, "session_count", "Session list extent.");
    service.add(u8, "subfunction_count", "Subfunction table extent.");
    service.add(new ArrayDataType(u8, 3, 1), "opaque_15", "Not interpreted here.");
    DataType serviceType = resolve(service);
    DataType servicePointer = new PointerDataType(serviceType, 4);
    StructureDataType serviceList = new StructureDataType(category, "F33DcmServiceList", 0);
    serviceList.setPackingEnabled(true);
    serviceList.add(u16, "selector", "Matched by913F0; unknown falls back to row0.");
    serviceList.add(u8, "count", "Number of halfword indices.");
    serviceList.add(u8, "opaque_03", "Not interpreted here.");
    serviceList.add(halfwords, "indices", "Indices into the shared23-row service table.");
    DataType serviceListType = resolve(serviceList);
    StructureDataType selection = new StructureDataType(category, "F33DcmServiceSelection", 0);
    selection.add(new PointerDataType(serviceListType, 4), "list", "Input service list.");
    selection.add(servicePointer, "service", "Output selected row, even on policy rejection.");
    DataType selectionPointer = new PointerDataType(resolve(selection), 4);
    StructureDataType subSelection = new StructureDataType(category, "F33DcmSubfunctionSelection", 0);
    subSelection.add(servicePointer, "service", "Input service row.");
    subSelection.add(subfunctionPointer, "subfunction", "Output selected row; second stack word is not an unrelated local.");
    DataType subSelectionPointer = new PointerDataType(resolve(subSelection), 4);
    StructureDataType route = new StructureDataType(category, "F33DcmRequestRoute", 0);
    route.add(u8, "addressing_kind", "Copied into message context.");
    route.add(u8, "opaque_01", "Not interpreted here.");
    route.add(u16, "service_list_selector", "Logical selector2/3/4, not a CAN bus.");
    DataType routePointer = new PointerDataType(resolve(route), 4);
    semanticFunction(0x4D17AL, "f33_check_diagnostic_application_admission", u32,
        new ParameterImpl("addressing_kind", u8, currentProgram))
        .setComment("Always publish addressing kind819A. Return0 only for81CC=5A,81AC=5A and7F97!=5A; otherwise1. Does not test delayed COM inhibit7F96.");
    semanticFunction(0x8B0FCL, "f33_check_diagnostic_addressing_admission", u32,
        new ParameterImpl("addressing_flags", u8, currentProgram))
        .setComment("Pass bit0 to4D17A and preserve its consequential full R10 result; not void.");
    semanticFunction(0x90EFEL, "f33_dcm_application_policy_hook", u32,
        new ParameterImpl("service_id", u8, currentProgram),
        new ParameterImpl("request", bytes, currentProgram),
        new ParameterImpl("request_length", u16, currentProgram),
        new ParameterImpl("addressing_flags", u8, currentProgram),
        new ParameterImpl("service_list_selector", u16, currentProgram),
        new ParameterImpl("negative_response", bytes, currentProgram))
        .setComment("Configured second policy hook uses fourth argument R9 only; map nonzero8B0FC result to8, otherwise0. Return8 selects silent-drop disposition, not a fabricated NRC.");
    semanticFunction(0x90F18L, "f33_dcm_check_session_list", u32,
        new ParameterImpl("allowed", bytes, currentProgram),
        new ParameterImpl("count", u8, currentProgram))
        .setComment("Null list allows; nonnull list requires current595C session in count bytes. Nonnull zero-count rejects. Return0 allowed,1 rejected.");
    semanticFunction(0x90F58L, "f33_dcm_check_security_list", u32,
        new ParameterImpl("allowed", bytes, currentProgram),
        new ParameterImpl("count", u8, currentProgram))
        .setComment("Null list allows; otherwise match current security getter result against count bytes. Nonnull zero-count rejects. Separate from application/group admission.");
    semanticFunction(0x90F98L, "f33_dcm_resolve_service", u32,
        new ParameterImpl("message", messagePointer, currentProgram),
        new ParameterImpl("selection", selectionPointer, currentProgram),
        new ParameterImpl("has_subfunction", bytes, currentProgram),
        new ParameterImpl("negative_response", bytes, currentProgram))
        .setComment("Search service-list u16 indices into24-byte rows; no own zero-request-length guard. Store selected row before session/security checks. NRC11 absent,7F session rejection,33 security rejection. Subfunction flag only when configured byte1 and SID!=31.");
    semanticFunction(0x9105AL, "f33_dcm_resolve_subfunction", u32,
        new ParameterImpl("message", messagePointer, currentProgram),
        new ParameterImpl("selection", subSelectionPointer, currentProgram),
        new ParameterImpl("negative_response", bytes, currentProgram))
        .setComment("Select request byte1 masked7F among16-byte rows. Actual load precedes length>=2 check. NRC13 short,12 absent,7E session rejection,33 security rejection; selected pointer published before policy checks.");
    semanticFunction(0x910FAL, "f33_dcm_invoke_request_policy", u32,
        new ParameterImpl("service_id", u8, currentProgram),
        new ParameterImpl("message", messagePointer, currentProgram),
        new ParameterImpl("stage", u32, currentProgram),
        new ParameterImpl("negative_response", bytes, currentProgram))
        .setComment("Stage bit1 selects hook family; bit0 selects post-SID request and adds address flag10. Clamp byte extent toFFFF. Exact first hook disabled, second enabled. Preserve nonzero callback result; only result1 is an NRC path in the service entry.");
    semanticFunction(0x913C2L, "f33_dcm_initialize_message_context", v,
        new ParameterImpl("service_list_selector", u16, currentProgram),
        new ParameterImpl("addressing_kind", u8, currentProgram),
        new ParameterImpl("request", infoPointer, currentProgram),
        new ParameterImpl("response", infoPointer, currentProgram))
        .setComment("Initialize28-byte5630 context from two eight-byte PduInfo descriptors. Request and response extents read as unsigned16; response length and suppression reset.");
    semanticFunction(0x913F0L, "f33_dcm_select_service_list", u32,
        new ParameterImpl("selector", u16, currentProgram))
        .setComment("Exact selectors2/3/4 select rows0/1/2 at25C0C. Unknown selector falls back to row0; not a CAN-bus identity claim.");
    semanticFunction(0x91410L, "f33_dcm_dispatch_direct_service", v,
        new ParameterImpl("message", messagePointer, currentProgram),
        new ParameterImpl("service", servicePointer, currentProgram))
        .setComment("Write positive SID prefix; advance request and response pointers and reduce capacities before callback. Set header count1. Null callback selects disposition3, not an implicit worker.");
    semanticFunction(0x91466L, "f33_dcm_dispatch_subfunction_service", v,
        new ParameterImpl("message", messagePointer, currentProgram),
        new ParameterImpl("service", servicePointer, currentProgram))
        .setComment("Resolve typed service/subfunction pair, then both post-SID policy stages. Preserve bit7 as suppress-positive flag and clear it in request; copy subfunction prefix. Set header count2 and active callback before operation0. Failed policy never invokes action.");
    semanticFunction(0x91566L, "f33_dcm_begin_service_request", v,
        new ParameterImpl("route", routePointer, currentProgram),
        new ParameterImpl("request", infoPointer, currentProgram),
        new ParameterImpl("response", infoPointer, currentProgram))
        .setComment("Initialize context; run first policy, service/session/security resolution, then second policy before direct/subfunction dispatch. Result1 stages NRC; other nonzero policy results choose silent disposition3. Session denial precedes application addressing publication.");
    semanticFunction(0x9139EL, "f33_dcm_clear_active_service", v)
        .setComment("Clear retained service ID562C, callback5628 and header count562D, then reset negative-response state.");
    semanticFunction(0x9165EL, "f33_dcm_cancel_active_service", v)
        .setComment("If active callback exists, clear negative-response state and call operation2 with5630; then finish local cleanup and clear active service. Does not itself prove downstream control/persistence cancellation.");
    semanticFunction(0x916ACL, "f33_dcm_notify_active_service_operation_three", v)
        .setComment("Invoke active callback with operation3 and5630 when nonnull; no inferred completion or physical result.");
    semanticFunction(0x91688L, "f33_dcm_get_message_context", messagePointer)
        .setComment("Return the retained28-byte message context5630; not an opaque scalar.");
    semanticFunction(0x91AE0L, "f33_dcm_get_security_level", u32,
        new ParameterImpl("level", bytes, currentProgram))
        .setComment("Null output returns0 without a read; otherwise return9240E status and its byte output.");
    semanticFunction(0x91AF4L, "f33_dcm_get_session", u32,
        new ParameterImpl("session", bytes, currentProgram))
        .setComment("Null output returns0 without a read; otherwise return924FC status and its byte output.");
    semanticFunction(0x924FCL, "f33_dcm_read_session_snapshot", u32,
        new ParameterImpl("session", bytes, currentProgram))
        .setComment("Copy current595C under the recovered critical section and return0; session membership is checked by callers.");
    semanticFunction(0x4A456L, "f33_update_application_communication_inhibits", v)
        .setComment("Condition E86D=5A and(7F95=0 or E860!=0) and7F94=1 immediately sets7F96/97=5A and clears7F98. On release clear7F97 immediately; only clear7F96 once invocation counter reaches ROM317B8.");
    semanticFunction(0x4CFA8L, "f33_refresh_mode_diagnostic_admission", v)
        .setComment("Publish81AC from captured E826, published E8CC and4CF66. Specified transitions clear diagnostic service/security state and event88; retained prior E826/7F97 detect transitions. Not atomic with foreground DCM.");
    semanticFunction(0x509A4L, "f33_refresh_diagnostic_application_availability", v)
        .setComment("E826=33/11 or7BBA=5A clears81CC; otherwise5A. Separate crypto availability81CD additionally requires7F97!=5A, with transition cleanup5704E. The two publications are not interchangeable.");
    semanticData(0x25C54L, new ArrayDataType(serviceType, 23, 24), "f33_dcm_service_rows",
        "Shared23-row bank; selector2 exposes17 entries, selector3 six, selector4 five. Not17 globally unique rows.");
    semanticData(0x25C0CL, new ArrayDataType(serviceListType, 3, 8), "f33_dcm_service_lists",
        "Selectors2/3/4 index shared descriptors; fallback is selector2 row.");
    semanticData(0xFEBE5630L, messageType, "f33_dcm_message_context",
        "Mutable request/response cursors and retained routing; not an immutable whole-transaction snapshot.");
    semanticData(0xFEBE5628L, callbackPointer, "f33_dcm_active_service_callback",
        "Installed before operation0; operation2/3 notifications use the same retained message context.");
  }
  private void annotateDiagnosticWritesAndRoutines() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType bytes = new PointerDataType(u8, 4);
    DataType halves = new PointerDataType(u16, 4);
    DataType pointer = new PointerDataType(v, 4);
    DataType messagePointer = new PointerDataType(
        currentProgram.getDataTypeManager().getDataType("/CamryF33/F33DcmMessageContext"), 4);
    semanticFunction(0x4D118L, "f33_diag_translate_application_request_status", u32,
        new ParameterImpl("application_status", s32, currentProgram))
        .setComment("0\u21920,-12\u21924,-7\u21928,-6\u21925,-1\u21922,other\u21929;negativeapplicationstatusesmuststay32-bit.");
    semanticFunction(0x4D36EL, "f33_select_available_did_metadata", u32,
        new ParameterImpl("did", u16, currentProgram))
        .setComment("Scans242 records2927C stride16 kind0, optional gate result5A, storesindex81B8; returns0/3.");
    semanticFunction(0x4D47EL, "f33_did_metadata_always_available", u32)
        .setComment("4D47E movea5A,r0,r10;4D482jmplp;usedmetadata2013/14.");
    semanticFunction(0x4D492L, "f33_get_selected_did_payload_length", v,
        new ParameterImpl("length", halves, currentProgram))
        .setComment("Metadata index81B8, readsu16record+2, writes0 if out of range.");
    semanticFunction(0x4FD2EL, "f33_start_pending_write_mode_request", v)
        .setComment("81AF11 ->35AA2,B9320(11),12;21->B9320(22),22. Invokedwhile81B2=2E10.");
    semanticFunction(0x4FD68L, "f33_finish_pending_write_mode_request", v)
        .setComment("81AF12->clear;22->5199E(operation6diagnosticqueue),clear;otherunchanged.");
    semanticFunction(0x4FD88L, "f33_write_0204_precondition", u32)
        .setComment("UnsignedE892>ROM318AE512 =>5 else0;LDHU/CMP/CMOVH4FD88..4FD9A.");
    semanticFunction(0x4FD9CL, "f33_write_0204_stage_mode_persistence", u32,
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("unused_length", u16, currentProgram))
        .setComment("4FDA0 tst1bit7,1[r6];81AF=11/21,81B2=2E10,r10=2. Byte0 ignored.");
    semanticFunction(0x4FDB8L, "f33_write_2001_precondition", u32)
        .setComment("Exact20-byte identity to4FD88.");
    semanticFunction(0x4FDCCL, "f33_write_2001_request_record101_reset", u32,
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("unused_length", u16, currentProgram))
        .setComment("ExactAEBA8 allzero limitsB5A74 acceptedbyte1. B5EBA ignoresbyte,setsB25511/returns1;callbackstatus2,owner2E10;invalid4,clearowner.");
    semanticFunction(0x4FE02L, "f33_write_2002_precondition", u32)
        .setComment("Exact20-byte identity to4FD88.");
    semanticFunction(0x4FE16L, "f33_write_2002_stage_record102_mode", u32,
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("unused_length", u16, currentProgram))
        .setComment("Byte0/1->55AAAA55/AA5555AA B7092;2/pending. Other4 clearsowner only.");
    semanticFunction(0x4FE5EL, "f33_write_2005_precondition", u32)
        .setComment("Exact20-byte identity to4FD88.");
    semanticFunction(0x4FE72L, "f33_write_2005_stage_record103_slot3", u32,
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("unused_length", u16, currentProgram))
        .setComment("Byte readtor7,selector3r6 at4FE78..7C; B69A8 staging,2E10,status2.");
    semanticFunction(0x4FE8EL, "f33_write_2006_precondition", u32)
        .setComment("Exact20-byte identity to4FD88.");
    semanticFunction(0x4FEA2L, "f33_write_2006_stage_record103_slot4", u32,
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("unused_length", u16, currentProgram))
        .setComment("Byte readtor7,selector4;B69A8 staging,2E10,status2.");
    semanticFunction(0x4FEBEL, "f33_write_2007_precondition", u32)
        .setComment("Exact20-byte identity to4FD88.");
    semanticFunction(0x4FED2L, "f33_write_2007_stage_record103_slot5", u32,
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("unused_length", u16, currentProgram))
        .setComment("Byte readtor7,selector5;B69A8 staging,2E10,status2.");
    semanticFunction(0x4FEEEL, "f33_write_2008_precondition", u32)
        .setComment("Exact20-byte identity to4FD88.");
    semanticFunction(0x4FF02L, "f33_write_2008_stage_record103_slot6", u32,
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("unused_length", u16, currentProgram))
        .setComment("Byte readtor7,selector6;B69A8 staging,2E10,status2.");
    semanticFunction(0x4FF1EL, "f33_write_2009_precondition", u32)
        .setComment("Exact20-byte identity to4FD88.");
    semanticFunction(0x4FF32L, "f33_write_2009_stage_record103_slot7", u32,
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("unused_length", u16, currentProgram))
        .setComment("Byte readtor7,selector7;B69A8 staging,2E10,status2.");
    semanticFunction(0x4FF56L, "f33_write_200d_precondition", u32)
        .setComment("Exact20-byte identity to4FD88.");
    semanticFunction(0x4FF6AL, "f33_write_200d_stage_record103_slot8", u32,
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("unused_length", u16, currentProgram))
        .setComment("Byte readtor7,selector8;B69A8 staging,2E10,status2.");
    semanticFunction(0x4FF86L, "f33_write_2010_precondition", u32)
        .setComment("Exact20-byte identity to4FD88.");
    semanticFunction(0x4FF9AL, "f33_write_2010_stage_mode_pair", u32,
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("unused_length", u16, currentProgram))
        .setComment("4FFB0 subtract1,4FFB4 cmp1,4FFB6 unsignedbh accepts1 AND2 aliases;0 alternatepair. B8FB2 returns0.4FFCA4D118 returns0/4;4FFD8 storedoesnotclobberr10. NOTvoid.");
    semanticFunction(0x4FFE0L, "f33_write_2012_precondition", u32)
        .setComment("00527f00=mov0,r10;jmplp, unconditional.");
    semanticFunction(0x4FFE4L, "f33_write_2012_latch_availability_override", u32,
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("unused_length", u16, currentProgram))
        .setComment("Byte1->B41A4/latchB18F5A,status0;else4. Doesnotclear81B2.");
    semanticFunction(0x4FFFEL, "f33_write_2013_precondition", u32)
        .setComment("GNU exact40bytes:80A5!=0 OR80A0!=0 ORu16E892>512=>5 else0. a497a5c8 displacementc8a5 loads80A5, NOT80A4. Seeded from the exact callback pointer.");
    semanticFunction(0x50026L, "f33_write_2013_service_numeric_target", u32,
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("unused_length", u16, currentProgram))
        .setComment("5002C/2E loads,50030 shl8,50032or;B8A4C fullu16setterB418;owner0/status0.");
    semanticFunction(0x50042L, "f33_write_2014_precondition", u32)
        .setComment("Exact40-byte identity4FFFE, GNU decoded50042..50068;receive-status80A5 separate fromgeneration80A4.");
    semanticFunction(0x5006AL, "f33_write_2014_service_qualification_mode", u32,
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("unused_length", u16, currentProgram))
        .setComment("0/1->B3D2 0/5A throughB85A2;invalid4 no setter. All clear81B2.");
    semanticFunction(0x500A2L, "f33_diag_routine_1001_admit", u32)
        .setComment("Raw500A2..AC819A==1?5:0;nooperationinputconsumed.");
    semanticFunction(0x500AEL, "f33_diag_routine_1001_family_capabilities", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("unused_input", bytes, currentProgram),
        new ParameterImpl("unused_input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("start:4D222(out,32) builds high-byte family support bitmap using low-byte-zero RID entries;outlen32,result2. results:byte,outlen1;other=>7. No asynchronous application service. Raw500AE..50886: R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions. Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32.");
    semanticFunction(0x500F8L, "f33_diag_routine_1000_admit", u32)
        .setComment("819A==1?5:0.");
    semanticFunction(0x50104L, "f33_diag_routine_1000_capabilities", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("unused_input", bytes, currentProgram),
        new ParameterImpl("unused_input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("start:4D308(1000,out,32) builds10xx RID support bitmap from26918;outlen=32;result=2 immediately. results:copy result byte,outlen1. Other direct control=>7. No asynchronous application service. Raw500AE..50886: R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions. Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32.");
    semanticFunction(0x50152L, "f33_diag_routine_1002_admit", u32,
        new ParameterImpl("control_type", u8, currentProgram))
        .setComment("819A==1=>5. start requires unsignedE892<=CodeFlash318AE (0200);already running=>8;results accepted;other=>7. Proof50164..72. Raw50152..5081E zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows.");
    semanticFunction(0x5018EL, "f33_diag_routine_1002_normalize_lifecycle", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("unused_input", bytes, currentProgram),
        new ParameterImpl("unused_input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("start:35AA2 conditionally requests internal6AE2=22 normalization (only when6AF0 neitherFFFFFFFF norA55A5AA5 and6ADD neither88 nor11 and6AE2!=11), thenB9320(44) writesAF47, unconditionally marks result1,outlen0. ScheduledB9212 consumes44: ifAF46!=5A andB8D9C(1)==5A thenB8DDA(1) restarts lifecycle groupB439;setsAF46=5A,AF44 active,consumesAF47 and reports selector2 success. This is normalization acknowledgement, NOT lower group convergence. A rejected lower restart still sets normalization flag and acknowledges. Later normalizer request88 clearsAF46. Result3 returns byte,len1. Raw500AE..50886: R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions. Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32.");
    semanticFunction(0x501D0L, "f33_diag_routine_1004_admit", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("input", bytes, currentProgram))
        .setComment("Raw501D0..50212;819Ainhibit,startFFFFpayload,819E==1duplicate;noinputlengthconsumed.");
    semanticFunction(0x50214L, "f33_diag_routine_1004_request_history_rewrite", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("unused_input", bytes, currentProgram),
        new ParameterImpl("unused_input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("start calls518E0 operation5 producer, translates return through4D118,marks result1 on0,len0. Idle producer immediately5551A history initialization then lifecycle85;busy producer deduplicates5/6 in four slots or writes producer slot (no full acknowledgement). Parent-owned5F91C/5F972 scheduler and51A98 later apply global AA/A5 hold, then85 needs89C4==0 for selector3 success,otherwise failure20;dispatcher51A12 may start queued request afterwards. No persistent success is implied by immediate callback return0. Raw500AE..50886: R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions. Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32.");
    semanticFunction(0x50258L, "f33_diag_routine_1007_admit", u32,
        new ParameterImpl("control_type", u8, currentProgram))
        .setComment("start requiresB8D9C(0)==5A,then result!=1;failure5 or duplicate8. No819A or speed gate. Results always admitted;other=>7. Raw50152..5081E zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows.");
    semanticFunction(0x5028EL, "f33_diag_routine_1007_restart_lifecycle_group0", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("unused_input", bytes, currentProgram),
        new ParameterImpl("unused_input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("startB8DDA(0) initializes B438=11,counterB440=0 (with shared dependent reinitializers whenB439!=11),result1,len0. B8D9C(0) checksB439 andB43A, notB438. B8B38 waits five status wordsB2D4/B26C/B324/B490/B352 high bytes88;all low bytes22=>group22 and selector4 success;otherwisegroup44 andfail20. Waiting timeout setsB43C=5A but does not directly acknowledge. Control type3 returns result byte,len1. Raw500AE..50886: R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions. Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32.");
    semanticFunction(0x502CAL, "f33_diag_routine_1008_admit", u32,
        new ParameterImpl("control_type", u8, currentProgram))
        .setComment("startB8D9C(2)==5A,then result!=1;failure5/duplicate8. Kind2 checksB438/B439,notB43A. No819A/speed gate;results admitted. Raw50152..5081E zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows.");
    semanticFunction(0x50300L, "f33_diag_routine_1008_restart_lifecycle_group2", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("unused_input", bytes, currentProgram),
        new ParameterImpl("unused_input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("startB8E52 restarts five dependencies,setsB43A=11,counterB442=0,result1,len0. B8CCE waits B2CE/B25C/B302/B462/B334;all22=>selector5 success andgroup22;all no longer11 but not all22=>failure20 andgroup44;otherwise waits withB43D timeout flag. Results byte,len1. Raw500AE..50886: R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions. Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32.");
    semanticFunction(0x5033AL, "f33_diag_routine_1009_admit", u32,
        new ParameterImpl("control_type", u8, currentProgram))
        .setComment("819A!=1;start result!=1 else8;results admitted;other7. No additional feature/E958 gate in THIS F33 raw precondition! Do not transfer Sienna semantics. Raw50152..5081E zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows.");
    semanticFunction(0x50366L, "f33_diag_routine_1009_reset_record103", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("unused_input", bytes, currentProgram),
        new ParameterImpl("unused_input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("startB69C6 resets B6990/B692A and setsB2C9=11,result1,len0. B6658 waitsB2C8/B2CA not22,thenB65CA queues selector103 with first8 zero,last8 FF;state22 pollsFF0C4(103):exact10 success=>B2C9=44,selector6 success plus reinit;high20 remains pending;other=>state88 and selector6 fail20. Results byte,len1. Admission, RAM reset and asynchronous selector103 persistence are distinct. Raw500AE..50886: R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions. Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32.");
    semanticFunction(0x503A0L, "f33_diag_routine_1100_admit", u32)
        .setComment("Raw503A0..AA819A==1?5:0.");
    semanticFunction(0x503ACL, "f33_diag_routine_1100_capabilities", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("unused_input", bytes, currentProgram),
        new ParameterImpl("unused_input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("start4D308(1100,out,32) builds11xx RID support bitmap,result2,outlen32;results byte,len1;other7. Raw500AE..50886: R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions. Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32.");
    semanticFunction(0x503FAL, "f33_diag_routine_1103_admit", u32,
        new ParameterImpl("control_type", u8, currentProgram))
        .setComment("819A!=1;start35A06()==1 and81A6!=1,then81A3!=1;5 vs8.35A06 raw gatesE81A==1,66B8>=30E32,E892<=30E34,80A5/80A0==0,saturatingabs66A8<512,clear6764&81FF. Results allowed;other7. Raw50152..5081E zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows.");
    semanticFunction(0x5043EL, "f33_diag_routine_1103_request_service1", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("unused_input", bytes, currentProgram),
        new ParameterImpl("unused_input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("start35A96 sets6AE2=11 andreturns2;callback converts to0,result1,len0.357C0 later requestsB3224(1),sets6ADD=88 on queued-1 or reportsselector8 failure. Existing family0500\u21920522 acquisition, selector100 learned quad+marker and service cleanup ownership in \u00a777.24 applies. This is not direct physical acquisition or immediate persistence. Results byte,len1. Raw500AE..50886: R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions. Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32.");
    semanticFunction(0x5047EL, "f33_diag_routine_1106_admit", u32,
        new ParameterImpl("control_type", u8, currentProgram))
        .setComment("819A!=1;start unsignedE892<=0200,thenresult!=1 else8;results allowed;other7. Raw50152..5081E zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows.");
    semanticFunction(0x504BCL, "f33_diag_routine_1106_restart_lifecycle_groups", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("unused_input", bytes, currentProgram),
        new ParameterImpl("unused_input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("startB524A invokesB5EC6/B707A/B8FA8 andsetsB214=11,result1,len0. B51BE succeeds onlyB311/B471/B256 all44\u2192group22 andselector9 success;when none remain11/22 but notall44\u2192group44 andfail20;otherwise waits. No local callback persistence/done assumption. Results byte,len1. Raw500AE..50886: R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions. Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32.");
    semanticFunction(0x504F6L, "f33_diag_routine_1108_admit", u32,
        new ParameterImpl("control_type", u8, currentProgram))
        .setComment("819A!=1;start result!=1 else8;no local speed gate;results allowed;other7. Raw50152..5081E zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows.");
    semanticFunction(0x50524L, "f33_diag_routine_1108_request_checkpoint_reset", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("unused_input", bytes, currentProgram),
        new ParameterImpl("unused_input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("start517DC operation2 producer and4D118;on0 result1,len0. Idle51788 performs multi-owner diagnostic reset/preservation then lifecycle82;busy deduplicates2/6 or writes producer slot,no capacity acknowledgement. Existing diagnostic scheduler51A98 requires all four persistence phaseszero for82 success;AA/A5 anygroup holds;other terminal phase yieldsfail20. Aggregateoperation86 canack both selector3/A via4D0E8. Results byte,len1. Raw500AE..50886: R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions. Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32.");
    semanticFunction(0x50568L, "f33_diag_routine_1109_admit", u32,
        new ParameterImpl("control_type", u8, currentProgram))
        .setComment("819A!=1;startE892<=0200,81A3!=1,80A0==0,80A5==0,E81E==0,E884!=5A,E88A!=5A,then ownresult!=1 (8);otherwise5. Results allowed;other7. Proof5057A..5C8. Raw50152..5081E zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows.");
    semanticFunction(0x505D8L, "f33_diag_routine_1109_request_record100_reset", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("unused_input", bytes, currentProgram),
        new ParameterImpl("unused_input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("startB90CA(22,1),4D118:pending-1 maps2 then callback0+result1;immediate0 givesresult2;other errors propagate. B90CA rejects modefamily0100/0900;nonzero publishedF208 triggers3599E to queue redundant selector100 defaultquad0800+marker0 when6AF0!=0 andsetsB495=5A,B497=5A,B498=1. If marker already0 returns0 (no required update). B906A waits publishedF00F==11,44 terminalsuccess;otherterminalfails;B8FEE reportsselectorB andclearsrequesterbit. Callback acceptance, redundant application record submission, lower NvMsoftwarecompletion and physical durability differ. Raw500AE..50886: R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions. Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32.");
    semanticFunction(0x5062CL, "f33_diag_routine_110a_admit", u32,
        new ParameterImpl("control_type", u8, currentProgram))
        .setComment("819A!=1. startB84B8(kind1) qualified,81A6!=1,E884/E88A!=5A,ownresult!=1 (8). stopresult!=0 else8;results accepted;other7. Kind1 is retainedR6 at50646,not absentargument. Raw50152..5081E zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows.");
    semanticFunction(0x50698L, "f33_diag_routine_110a_control_service2", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("unused_input", bytes, currentProgram),
        new ParameterImpl("unused_input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("startB3224(2),4D118;queued=>callback0,B85D0 clearsstoplatch,result1,len0. stop whenrunning1 callsB85BC (B3DD=5A,B3CB=0) but leavesresult1;when terminal nonzero clearsresult0;len0. Existing family0520 kind1 engine, B303E completion and forcedexitB3194 apply. Results byte,len1. Raw500AE..50886: R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions. Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32.");
    semanticFunction(0x50702L, "f33_diag_routine_110b_admit_noop", u32)
        .setComment("Raw50702mov0,R10;50704jmpLP.");
    semanticFunction(0x50706L, "f33_diag_routine_110b_action_noop", u32)
        .setComment("Raw50706mov0,R10;50708jmpLP;NOoutputlengthor81A8resultaccess.");
    semanticFunction(0x5070AL, "f33_diag_routine_110c_admit", u32,
        new ParameterImpl("control_type", u8, currentProgram))
        .setComment("819A!=1;startB84B8(kind2),81A6!=1,E884/E88A!=5A,andE889!=0;ownresult!=1 else8. E889 is published ID2 completionB3CA,not generic NvM validity. No stop support. Raw50152..5081E zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows.");
    semanticFunction(0x5076AL, "f33_diag_routine_110c_request_service3", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("unused_input", bytes, currentProgram),
        new ParameterImpl("unused_input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("startB3224(3),4D118 queued=>callback0,result1,len0. Existing0520 kind2 preserves center/extrema andresumestracking;B303E emitsselectorE;forcedexit fails (no stop latch). Results byte,len1. Raw500AE..50886: R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions. Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32.");
    semanticFunction(0x507B2L, "f33_diag_routine_110d_admit", u32,
        new ParameterImpl("control_type", u8, currentProgram))
        .setComment("819A!=1;startB84B8(kind3),81A6!=1,E884/E88A!=5A,ownresult!=1 else8. stopresult!=0 else8;results allowed. Raw50152..5081E zxbR6andfullR10return0/5/7/8;gate details in companion recovery rows.");
    semanticFunction(0x50820L, "f33_diag_routine_110d_control_service4", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("unused_input", bytes, currentProgram),
        new ParameterImpl("unused_input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("startB3224(4),4D118 queued=>callback0,B85CA clearsstoplatch,result1,len0. stoprunning1 callsB85AE settingB3DC=5A,B3CB=0,doesnotterminallycompleteresult;terminalnonzero clearsresult0. Existing0520kind3 andB303E/forcedexit cleanup apply. Results byte,len1. Raw500AE..50886: R6zxbcontrols1/2/3;R9output;fifthargumentatentrySP+0pointsu16length(st.h);return32-bitR10;inputargumentsunusedbytheseactions. Result requestsproduce1byte;starts/stops0exceptcapabilitystarts32.");
    semanticFunction(0x5088AL, "f33_diag_routine_clear_nonrunning_results", v,
        new ParameterImpl("preserve_selector2", u8, currentProgram))
        .setComment("Alwayspreservesrunning1;argument5Aadditionallypreservesindex2.4D582calls0.");
    semanticFunction(0x508CCL, "f33_diag_routine_publish_terminal_result", v,
        new ParameterImpl("result_selector", u8, currentProgram),
        new ParameterImpl("completion_status", u8, currentProgram))
        .setComment("Onlyselector<16andcurrentresult1;status10noop,0\u21922,30\u21920,other\u21923.8-bitselector/statusmasking;no meaningfulreturn.");
    semanticFunction(0x8B396L, "f33_reset_write_did_transaction", v)
        .setComment("Clearsindex3B1E/completion3B20/lifecycle3B21/actionstatus3B25; sidestatus1,opaqueFF.");
    semanticFunction(0x8B400L, "f33_dcm_probe_did_metadata", u32,
        new ParameterImpl("did", u16, currentProgram))
        .setComment("Transparent call4D36E; r10 result consumed951DA/9521E despite former void.");
    semanticFunction(0x8B40EL, "f33_dcm_selected_did_payload_length", v,
        new ParameterImpl("length", halves, currentProgram))
        .setComment("Transparent call4D492; pointerr6 must be preserved in ABI.");
    semanticFunction(0x8B572L, "f33_write_did_precondition_phase", u32,
        new ParameterImpl("matched_index", halves, currentProgram),
        new ParameterImpl("did", u16, currentProgram))
        .setComment("Lifecycle3B21=0/1 andlowerstatus merge; consumes8E4BC status, emitsbyte-normalized meaningfulr10.");
    semanticFunction(0x8B632L, "f33_write_did_payload_phase", u32,
        new ParameterImpl("matched_index", u16, currentProgram),
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("length", u16, currentProgram))
        .setComment("8B66C cmp8,66E unsigned guard for7-byte staging; originalpointer/length still passed8E506 at6E0..6E8.8B6FC merge result survives stores through71C and consumedcaller758. NOTvoid.");
    semanticFunction(0x8B720L, "f33_write_did_request_adapter", u32,
        new ParameterImpl("did", u16, currentProgram),
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("length", u16, currentProgram),
        new ParameterImpl("nrc", bytes, currentProgram))
        .setComment("8B742 prephase;746/754/758 r10 dataflow.2->adapter10 andcompletionFF,else8E6EC translatesNRC.");
    semanticFunction(0x8B7B8L, "f33_diag_reset_routine_class_state", v)
        .setComment("Resets3B2C..35 andbuffers3B36[32],3B56[49],3B87[68];noapplicationservicecancelorresultpublication. Configuredwrapperoperation/status>=2\u21928B83C\u2192thisreset,distinctfromcontrol-type2stop.");
    semanticFunction(0x8B858L, "f33_diag_routine_crypto_admit", u32)
        .setComment("8B85Ccalls8B854whichmov0,R10;jmpLP.");
    semanticFunction(0x8B864L, "f33_diag_routine_100e_activate_fixed_crypto_bank0", u32)
        .setComment("6A028activatesonly5096==0;callbackreturns0,nooutput/lengthaccess.");
    semanticFunction(0x8B872L, "f33_diag_routine_100f_activate_fixed_crypto_bank1", u32)
        .setComment("6A0AEactivatesonly509B==0;callbackreturns0;fixed16bytecommand5boundarymaintained.");
    semanticFunction(0x8BC86L, "f33_diag_routine_begin_admission", u32,
        new ParameterImpl("rid", u16, currentProgram),
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("callback_index", halves, currentProgram),
        new ParameterImpl("encoded_input", bytes, currentProgram),
        new ParameterImpl("input_length", u16, currentProgram))
        .setComment("Stages7bytes sideevent88000010,selectsprecondition via8E562,persists3B30..33;pendingstatus2 retained.");
    semanticFunction(0x8BD7CL, "f33_diag_routine_run_action_phase", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("callback_index", u16, currentProgram),
        new ParameterImpl("encoded_input", bytes, currentProgram),
        new ParameterImpl("input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("Sideevent88000011,8E5BCcall8BE1A/8BE8E,captures32maxoutputorresultbyte,merges8E602,clearsstateonterminal.");
    semanticFunction(0x8BF60L, "f33_diag_routine_application_class", u32,
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("configured_index", u16, currentProgram),
        new ParameterImpl("encoded_input", u32, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("unused_length", halves, currentProgram),
        new ParameterImpl("nrc", bytes, currentProgram))
        .setComment("8BC86\u21928BD7C;2-byteinputfromu32high/low;constantlength7;selectedindex3B2C;pending2mapsreturn10;8E6ECmapsotherreturns. Fifthargumentunused.");
    semanticFunction(0x8E4BCL, "f33_find_write_did_and_check_precondition", u32,
        new ParameterImpl("matched_index", halves, currentProgram),
        new ParameterImpl("did", u16, currentProgram))
        .setComment("8E4C0 savesdid,4C2 indexptr;13-entry table25640. Fullr10 cmp3 at4F0 re-enters SAME index at4CA via4F2; increments only4F6. Storesu16 index4FE.");
    semanticFunction(0x8E506L, "f33_dispatch_or_poll_write_did_action", u32,
        new ParameterImpl("completion_status", u8, currentProgram),
        new ParameterImpl("matched_index", u16, currentProgram),
        new ParameterImpl("payload", bytes, currentProgram),
        new ParameterImpl("length", u16, currentProgram))
        .setComment("8E50A..510 savesargs;3B25==2 bypassescallback, usescompletion withFF->2;elseboundedfixedcallback. Storeslateststatus8B7AE.");
    semanticFunction(0x8E562L, "f33_diag_routine_select_precondition", u32,
        new ParameterImpl("callback_index", halves, currentProgram),
        new ParameterImpl("rid", u16, currentProgram),
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("input", bytes, currentProgram),
        new ParameterImpl("input_length", u16, currentProgram))
        .setComment("8E566/56C retainu16RID;56E zxbcontrol;594 ld.hu original fifthargument;5A0 indirectcall row+4;5A4/A6 fullR10==3 re-enters sameindex;5AA only mismatch/null increments;5B4 writesu16index.");
    semanticFunction(0x8E5BCL, "f33_diag_routine_dispatch_action", u32,
        new ParameterImpl("callback_index", u16, currentProgram),
        new ParameterImpl("control_type", u8, currentProgram),
        new ParameterImpl("input", bytes, currentProgram),
        new ParameterImpl("input_length", u16, currentProgram),
        new ParameterImpl("output", bytes, currentProgram),
        new ParameterImpl("output_length", halves, currentProgram))
        .setComment("8E5C0/C2/C4 zxh/zxb/zxh;5C8 bounds19;5D6+5F6 row+8;5E2+5EC loadoriginalstackarg6/5 andshuffle5argcallback;5FA indirectcall.");
    semanticFunction(0x8E602L, "f33_merge_two_diagnostic_statuses", u32,
        new ParameterImpl("application_status", u8, currentProgram),
        new ParameterImpl("lower_status", u8, currentProgram),
        new ParameterImpl("success_status", u8, currentProgram),
        new ParameterImpl("pending_status", u8, currentProgram))
        .setComment("ZXB R6/R7/R8/R9 at8E602..608; choose pending if either input is pending, otherwise local failure or nonzero side result after local success. MOV R9,R10 at8E620 and JMP LP guarantee full zero-extended32 result0..255.");
    semanticFunction(0x8E624L, "f33_diag_routine_local_dispatch_enabled", u32)
        .setComment("Exactfunctionreturns5Aunconditionally;nominalside-statusargumentisignored. No status-dependent admission inferred.");
    semanticFunction(0x8E6ECL, "f33_diagnostic_status_to_nrc", u32,
        new ParameterImpl("status", u8, currentProgram),
        new ParameterImpl("nrc", bytes, currentProgram))
        .setComment("status0 =>0,NRC0;other =>1 andconfigured byte mapping, no pending scheduling itself.");
    semanticFunction(0x94288L, "f33_dcm_resolve_did_group", u32,
        new ParameterImpl("did", u16, currentProgram),
        new ParameterImpl("table_kind", u8, currentProgram),
        new ParameterImpl("group", halves, currentProgram),
        new ParameterImpl("capabilities", bytes, currentProgram))
        .setComment("Writes capability0 then invokes94148 forkind1 or941EC; actual resolver r10 is consumed9586C. Existing void prototype is wrong.");
    semanticFunction(0x95978L, "f33_dcm_write_did_service", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", messagePointer, currentProgram))
        .setComment("0 starts9586C,2 cancels958F4; all paths meaningful r10.");
    semanticFunction(0x972F2L, "f33_diag_routine_control_type_supported", u32,
        new ParameterImpl("configured_index", u16, currentProgram),
        new ParameterImpl("control_type", u8, currentProgram))
        .setComment("269B9+15*index offsets4/9/1 forcontrols1/2/3;0supported,1rejected;indexbound26492.");
    semanticFunction(0xB41A4L, "f33_latch_availability_override", v)
        .setComment("DirectB18F5A;noNvMrequest.");
    semanticFunction(0xB51BEL, "f33_monitor_routine_1106_lifecycle_groups", v)
        .setComment("B214=11waitsB311/B471/B256;all44success,otherterminalfail;selector9.");
    semanticFunction(0xB5EBAL, "f33_request_record101_reset_write", u32)
        .setComment("B5EBA..C4 onlystoresB255=11 andreturns1;incomingr6payloadunused.");
    semanticFunction(0xB6658L, "f33_monitor_routine_1009_record103_reset", v)
        .setComment("B2C9states11\u219222\u219244/88;B65CAqueues103;FF0C4status10success/high20pending;selector6.");
    semanticFunction(0xB66D2L, "f33_submit_staged_record103_byte_write", v)
        .setComment("Copieslive8bytes,selector1..8 replacesone,magicA55A5AA5,FF09C103;sharedstagingnotqueue.");
    semanticFunction(0xB674EL, "f33_service_record103_byte_write", v)
        .setComment("11->22 request whenpeerstatesnot22;pollrecord103;10->44reload/ack,20xwait,other88ackfailure.");
    semanticFunction(0xB69A8L, "f33_stage_record103_byte_write", v,
        new ParameterImpl("selector", u8, currentProgram),
        new ParameterImpl("value", u8, currentProgram))
        .setComment("B69BEB69C0 stores incomingr6 selectoratB2CC,r7 valueB2CB. B6990/B692A preserveboth registers. Corpus void(void) losesABI.");
    semanticFunction(0xB7092L, "f33_stage_record102_mode_write", v,
        new ParameterImpl("encoded_mode", u32, currentProgram))
        .setComment("Resetsqualification,B31211,B31Cencodedmode,doesnotwriteliveB314.");
    semanticFunction(0xB85A2L, "f33_set_service_qualification_mode", v,
        new ParameterImpl("mode", u8, currentProgram))
        .setComment("DirectbyteB3D2;B7CD0/B8474thresholdselection.");
    semanticFunction(0xB8A4CL, "f33_set_service_numeric_target", v,
        new ParameterImpl("target", u16, currentProgram))
        .setComment("Directu16storeB418,consumedB89E0 onlywhenB40C5A.");
    semanticFunction(0xB8B38L, "f33_monitor_routine_1007_lifecycle_group", v)
        .setComment("B438=11waitsfive88xxstatuses;all8822success,otherterminalfail;selector4.");
    semanticFunction(0xB8CCEL, "f33_monitor_routine_1008_lifecycle_group", v)
        .setComment("B43A=11waitsfivegroupbytes;all22success,othernon11terminalfail;selector5.");
    semanticFunction(0xB8FB2L, "f33_stage_encoded_mode_pair", u32,
        new ParameterImpl("first", u32, currentProgram),
        new ParameterImpl("second", u32, currentProgram))
        .setComment("B47244,B480/B484=pair,r10=0. No recoveredreader ofstagedpair;NOTliveB474/B478.");
    semanticFunction(0xB906AL, "f33_monitor_pending_learned_record_updates", v)
        .setComment("B494/B495requestflags,publishedF011/F00Fstates;callsB8FEE11successor22fail;selectorBrequesterbit1handledthere.");
    semanticFunction(0xB9212L, "f33_consume_lifecycle_normalization_request", v)
        .setComment("AF47request44conditionallyrestartsB439,alwayssetsAF46=5Aandacknowledgesselector2thenconsumesrequest;notgroupcompletion.");
    semanticFunction(0xFE09CL, "f33_stage_encoded_mode_pair_thunk", u32,
        new ParameterImpl("first", u32, currentProgram),
        new ParameterImpl("second", u32, currentProgram))
        .setComment("TransparentthunktoB8FB2;return0used4FF9A.");
    semanticFunction(0xFE0C4L, "f33_record103_byte_write_thunk", v,
        new ParameterImpl("selector", u8, currentProgram),
        new ParameterImpl("value", u8, currentProgram))
        .setComment("Transparent CodeFlashthunk->B69A8, actualselectors3..8 fromconfiguredwritecallbacks.");
    semanticFunction(0xFE1B4L, "f33_set_service_qualification_mode_thunk", v,
        new ParameterImpl("mode", u8, currentProgram))
        .setComment("TransparentthunkB85A2 from5006A.");
    semanticFunction(0xFE1C8L, "f33_set_service_numeric_target_thunk", v,
        new ParameterImpl("target", u16, currentProgram))
        .setComment("TransparentthunkB8A4C from50026.");
    FunctionDefinitionDataType writeDidPrecondition = new FunctionDefinitionDataType(category, "F33WriteDidPrecondition");
    writeDidPrecondition.setReturnType(u32);
    FunctionDefinitionDataType writeDidAction = new FunctionDefinitionDataType(category, "F33WriteDidAction");
    writeDidAction.setReturnType(u32);
    writeDidAction.setArguments(new ParameterDefinitionImpl("payload", bytes, null),
        new ParameterDefinitionImpl("length", u16, null));
    StructureDataType writeDid = new StructureDataType(category, "F33WriteDidCallbacks", 0);
    writeDid.setPackingEnabled(true);
    writeDid.add(u16, "identifier", "Configured diagnostic identifier.");
    writeDid.add(u16, "opaque_02", "Zero in the exact registered table.");
    writeDid.add(new PointerDataType(writeDidPrecondition, 4), "precondition", "Fixed callback or null; return3 retries same matched row.");
    writeDid.add(new PointerDataType(writeDidAction, 4), "action", "Fixed callback or null; admission is separate from completion.");
    semanticData(0x25640L, new ArrayDataType(resolve(writeDid), 13, 12), "f33_write_did_callbacks",
        "Exact configured application callback records; no inferred OEM service names.");
    FunctionDefinitionDataType routinePrecondition = new FunctionDefinitionDataType(category, "F33RoutinePrecondition");
    routinePrecondition.setReturnType(u32);
    routinePrecondition.setArguments(new ParameterDefinitionImpl("control_type", u8, null),
        new ParameterDefinitionImpl("input", bytes, null),
        new ParameterDefinitionImpl("input_length", u16, null));
    FunctionDefinitionDataType routineAction = new FunctionDefinitionDataType(category, "F33RoutineAction");
    routineAction.setReturnType(u32);
    routineAction.setArguments(new ParameterDefinitionImpl("control_type", u8, null),
        new ParameterDefinitionImpl("input", bytes, null),
        new ParameterDefinitionImpl("input_length", u16, null),
        new ParameterDefinitionImpl("output", bytes, null),
        new ParameterDefinitionImpl("output_length", halves, null));
    StructureDataType routine = new StructureDataType(category, "F33RoutineCallbacks", 0);
    routine.setPackingEnabled(true);
    routine.add(u16, "identifier", "Configured diagnostic identifier.");
    routine.add(u16, "opaque_02", "Zero in the exact registered table.");
    routine.add(new PointerDataType(routinePrecondition, 4), "precondition", "Fixed callback or null; return3 retries same matched row.");
    routine.add(new PointerDataType(routineAction, 4), "action", "Fixed callback or null; admission is separate from completion.");
    semanticData(0x256DCL, new ArrayDataType(resolve(routine), 19, 12), "f33_routine_callbacks",
        "Exact configured application callback records; no inferred OEM service names.");
    // Real leaves preserve the staged write's incoming R6/R7; a generic call
    // model otherwise invents extraout values. The local-enable leaf is exact5A.
    getFunctionAt(toAddr(0xB6990L)).setInline(true);
    getFunctionAt(toAddr(0xB692AL)).setInline(true);
    getFunctionAt(toAddr(0x8E624L)).setInline(true);
  }
  private void annotateServiceLifecycle() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType samplePointer = new PointerDataType(s16, 4);
    semanticFunction(0xB3224L, "f33_queue_application_service", s32,
        new ParameterImpl("service_id", u8, currentProgram))
        .setComment("IDs1..4 require live mode<0600. Return -1 queued,-7 duplicate,-6 rejected. IDs2/3 set B3D1, "
            + "ID4 sets B3D7, and all three cancel event4 BEFORE duplicate detection. ID1 requests event6 only "
            + "when published learned markerF208 is nonzero; acceptance is not guaranteed immediate mode entry.");
    semanticFunction(0xB84B8L, "f33_qualify_service_admission", u32,
        new ParameterImpl("kind", u8, currentProgram))
        .setComment("Return0/5A from exact raw-unit input/status/mode/limit gates. Kinds1/2 additionally apply "
            + "B8474 hysteresis. Diagnostic5062C passes kind1 in retained R6;5070A/507B2 pass2/3. "
            + "No inferred physical stationary condition or engineering-unit interpretation.");
    semanticFunction(0xB309CL, "f33_advance_service_family", v)
        .setComment("Family0500 selects events2A/2C/2E into0512/0522/0520. Submodes independently qualify "
            + "completion events and return0500. Accepted queue, selected submode, convergence, persistence "
            + "and diagnostic result are separate states.");
    semanticFunction(0xB3194L, "f33_report_pending_service_aborts", v)
        .setComment("For pending IDs1/3 report failure; IDs2/4 report cancellation only with their stop latch5A, "
            + "otherwise failure. Clear ID1 internal88 state. Does NOT clear pending bitsB10E.");
    semanticFunction(0xB3204L, "f33_exit_service_family", v)
        .setComment("Report pending aborts, clean engine/output state, clear admission latches, conditionally "
            + "restore output masks. Pending bitsB10E survive; do not describe this as dequeue-all.");
    semanticFunction(0xB83F8L, "f33_initialize_service_engine", v,
        new ParameterImpl("kind", u8, currentProgram))
        .setComment("Initialize0520 engine kind1/2/3. Kind2 preserves extrema and selector106. Kinds1/3 reset "
            + "extrema and immediately queue selector106=0. Set phase1, reset qualification and request masks.");
    semanticFunction(0xB7D38L, "f33_qualify_service_progress", u8,
        new ParameterImpl("done", u8, currentProgram),
        new ParameterImpl("cancel", u8, currentProgram))
        .setComment("Cancellation precedes done; publish B3CB=0/2. Otherwise runtime predicates select "
            + "continuing1 or failed3. Return5A for terminal,0 for continuing. Counts are not milliseconds.");
    semanticFunction(0xB7F2EL, "f33_queue_service_center_and_check_geometry", u32)
        .setComment("Queue learned selector106 scalar BEFORE B78F8 geometry establishment. Preserve its R10 "
            + "status across the B3F0 store and return it;5A signals invalid B138>>3 geometry. Diagnostic "
            + "completion does not await the separate selector106 persistence poll.");
    semanticFunction(0xB80A2L, "f33_advance_service_excursion_phase", u8,
        new ParameterImpl("phase", u8, currentProgram))
        .setComment("Dispatch the kind1 initial excursion phases and return the selected child phase in R10; "
            + "not void. Phase number alone is not a completion indication.");
    // Each phase worker retains its input when its transition condition is not met.
    // Formal child arguments are needed as well as the dispatcher's scalar return.
    for (long entry : new long[] {
        0xB7DBAL, 0xB7E44L, 0xB7EB2L, 0xB7EDCL,
        0xB7F8AL, 0xB7FF4L, 0xB8040L, 0xB8070L}) {
      semanticFunction(entry, getFunctionAt(toAddr(entry)).getName(), u8,
          new ParameterImpl("phase", u8, currentProgram));
    }
    semanticFunction(0xB7E82L, "f33_update_service_minimum_excursion", u8,
        new ParameterImpl("qualification", u8, currentProgram))
        .setComment("Update minimum of -AFE8 while not qualified, call B7E66, retain and return B3C8 status.");
    semanticFunction(0xB7EFEL, "f33_update_service_maximum_excursion", u8,
        new ParameterImpl("qualification", u8, currentProgram))
        .setComment("Update maximum of -AFE8 while not qualified, call B7E66, retain and return B3C9 status.");
    semanticFunction(0xB8690L, "f33_select_service_kind1_sample", u32,
        new ParameterImpl("sample", samplePointer, currentProgram))
        .setComment("Write the phase-selected signed halfword through R6; return0/5A enable in full R10. "
            + "Real leaf preserves caller R19=0, used as the secondary publication flag.");
    semanticFunction(0xB86E8L, "f33_select_service_kind2_sample", u32,
        new ParameterImpl("sample", samplePointer, currentProgram))
        .setComment("Phase0A selects B3A6 and returns5A; otherwise write zero and return0. R6 is a real output pointer.");
    semanticFunction(0xB8704L, "f33_select_service_kind3_sample", u32,
        new ParameterImpl("sample", samplePointer, currentProgram))
        .setComment("Select AC56 or directed ROM samples in phases0C..0F; write through R6 and return0/5A.");
    semanticFunction(0xB8774L, "f33_publish_service_engine_substitution", v)
        .setComment("Select sample by engine kind, derive bound, publish B3FC enable/B3FD secondary flag/"
            + "B3FE sample/B400 bound. BF33E snapshots these for family0500 motor substitution. No physical actuation claim.");
    // Preserve actual leaf register effects, including R19, without replacement callees.
    getFunctionAt(toAddr(0xB8690L)).setInline(true);
    getFunctionAt(toAddr(0xB86E8L)).setInline(true);
    getFunctionAt(toAddr(0xB8704L)).setInline(true);
  }
  private void annotateApplicationLifecycle() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType halfwords = new PointerDataType(u16, 4);
    semanticFunction(0x667E6L, "f33_foreground_subsystem_cycle", v)
        .setComment("Exact order69CA2,7A254,988C2,69E7C,58B5E,66512.7A254 contains RX drain then SecOC6A410;988C2 is "
            + "DCM, not SecOC. Application work follows DCM and precedes the enclosing foreground NvM66CF6 "
            + "service.");
    semanticFunction(0x988C2L, "f33_dcm_foreground_cycle", v)
        .setComment("Only when5E50==A5 run DCM worker91FBE, timers98AE4 and event queue98946 in that order. SecOC "
            + "processing belongs upstream inside7A254. Timer expiry uses remaining<quantum, and the queue worker "
            + "snapshots its entry event count.");
    semanticFunction(0x58B5EL, "f33_dispatch_foreground_mode_generation", v)
        .setComment("Use published modeE8CC and local8C06/inverse8C12. Valid changed mode takes transition workers; "
            + "broken inverse repairs from snapshot and takes steady workers, not automatic failsafe. "
            + "Mask=(~n&(n+2)&3E)|1, n+=2 modulo256. Central mode work can change live mode while remaining "
            + "dispatchers still receive the previously captured mode.");
    semanticFunction(0x65984L, "f33_apply_mpu_attribute_profile", v,
        new ParameterImpl("selector", u8, currentProgram))
        .setComment("Load MPAT0..15 from31708+64*low8(selector), then SYNCI/SYNCP. No index validation and no "
            + "region-bound writes. Assembly system-register effects are authoritative; decompiler formerly "
            + "exposed only the incidental last load in R10 as a false getter result.");
    semanticFunction(0xB1546L, "f33_reconcile_mode_requests", v)
        .setComment("Reconcile request and cancellation bitmaps for IDs0..49 into status slotsB0A8. Materialize "
            + "requested/not-cancelled slots throughB1BFE; acknowledged5AA5 causes request cancellation but "
            + "clears only on a later reconciliation. Cancelled pendingA55A is NOT revoked. Native mixed-state "
            + "pass covers both bitmap words and the domain boundary.");
    semanticFunction(0xB1BFEL, "f33_materialize_mode_request", u32,
        new ParameterImpl("request_id", u32, currentProgram))
        .setComment("Index by low8(request_id), without a local bounds check. Preserve acknowledged5AA5, otherwise "
            + "publish pendingA55A. Return the zero-extended status in full R10; this return is consumed byB1546 "
            + "and is not void.");
    semanticFunction(0xB1C1AL, "f33_clear_acknowledged_mode_request", v,
        new ParameterImpl("request_id", u32, currentProgram))
        .setComment("Index low8(request_id), without a local bounds check. Clear only5AA5; preserve pendingA55A and "
            + "every other value. Cancellation after materialization therefore does not revoke an unaccepted "
            + "request.");
    semanticFunction(0x3C232L, "f33_route_fault_action_mode_request", v,
        new ParameterImpl("actions", u32, currentProgram))
        .setComment("Hard action bit0 or gatedbit1 latchesB190 and requests event0 only when publishedEB9A==0. "
            + "Otherwise soft bit3 or gatedbit4 waits for8AC8/8ACB==0.71EC.bit15 qualifies bits1/4. A "
            + "still-present fault waiting for zero does not cancel; no action cancels event0. R6 action-mask "
            + "input; no DTC identity or universal shutdown inference.");
    CategoryPath category = new CategoryPath("/CamryF33");
    FunctionDefinitionDataType callback = new FunctionDefinitionDataType(category, "F33ModeFamilyHook");
    callback.setReturnType(v);
    StructureDataType hooks = new StructureDataType(category, "F33ModeFamilyHooks", 0);
    hooks.setPackingEnabled(true);
    hooks.add(new PointerDataType(callback, 4), "entry", "Called before publishing new live mode.");
    hooks.add(new PointerDataType(callback, 4), "exit", "Old-family exit precedes new-family entry.");
    semanticData(0xAEB00L, new ArrayDataType(resolve(hooks), 10, 8), "f33_mode_family_hooks",
        "Index is mode high byte. Entry/exit pairs for0000..0900; legitimate callers select0100..0900.");
    getFunctionAt(toAddr(0x66062L)).setComment("Foreground polls and clears EIC136.bit12; a flag is not a counted backlog. Optional31910==5A hooks bracket bookkeeping, alternate-context physical NvM pump,667E6 subsystem cycle and alternate-context66CF6 application NvM cycle. Increment39DB after completion. Relative order is exact; execution time and missed-tick behavior are not a periodic-job guarantee.");
    getFunctionAt(toAddr(0x71378L)).setComment("NONORDINARY PAIRED ABI: PUSHSP r1..ep saves120 bytes on original stack; r2 retains saved-frame SP, SP becomes FEBE2800, r20 preserves continuation, profile selectorROM31684=1 goes to65984. No PSW save or independent interrupt disable. Pair with71398; do not model as an ordinary leaf wrapper.");
    getFunctionAt(toAddr(0x71398L)).setComment("PAIRED ABI exit: apply profileROM31683=0, restore SP from r2, restore r1..ep and return through preserved continuation. LP is outside the saved register range. Exact assembly, not ordinary C stack effects, defines this contract.");
    getFunctionAt(toAddr(0x65AC0L)).setComment("Assembly MPAT0..15 save with persistent SP delta-64. Used in timer interrupt frames; not a normal stack-neutral leaf.");
    getFunctionAt(toAddr(0x65B4AL)).setComment("Assembly MPAT0..15 restore with persistent SP delta+64, paired with65AC0. Restores the interrupted MPU profile, including foreground profile1.");
    getFunctionAt(toAddr(0xB4FFCL)).setComment("Vote qualified health stateB20E/B20C/B20D; unrecoverable vote starts at0. States0/33 may select11,0 may select33,33 may clear,11 may select22 and latchB20F. Route the new state throughB4F8A BEFORE publishing it. Physical analog-channel identities and OEM state names remain bounded.");
    getFunctionAt(toAddr(0xB4F8AL)).setComment("Health-state event routing:11 requests event1 with zero-output gates in families0400/0500;22 requests1 only in those families and2 in0700/0800. Exact0522 also checksAFCE!=11. No event1 cancellation here; do not infer universal immediate shutdown.");
    semanticFunction(0x56B06L, "f33_set_channel_owner_request", v,
        new ParameterImpl("owner", u8, currentProgram),
        new ParameterImpl("request_mask", u32, currentProgram))
        .setComment("Replace one of five owner masks when low8(owner)<5. Clearing one owner does not clear other owners.");
    semanticFunction(0x569DAL, "f33_apply_channel_request_mask", v,
        new ParameterImpl("request_mask", u32, currentProgram))
        .setComment("Consume full R6. Bits1/17 select the requested rather than reference level for channels0/1. "
            + "Both bits set, or the entire mask zero, also performs an early paired write before the per-channel "
            + "writes. Preserve those repeated effects and their order; no physical channel identity is assigned.");
    semanticFunction(0x56A26L, "f33_read_channel_mismatch_mask", u32)
        .setComment("Return bit1/17 when the corresponding GPIO input differs from its ROM reference level. "
            + "This is readback, not a copy of the requested mask or proof of actuator response.");
    semanticFunction(0x56AD2L, "f33_update_channel_requests", v)
        .setComment("OR-reduce five owner masks, apply the combined mask through569DA, then read GPIO mismatch "
            + "through56A26 and qualify both channels through56A48/56A8C. Exact ROM318F8/F9 thresholds are zero: "
            + "qualification directly selects state2 for matching reference, state0 otherwise. The formal R6 "
            + "contract on569DA preserves the real OR-reduction in recovered C.");
    semanticFunction(0x62050L, "f33_write_channel_reference_level", v,
        new ParameterImpl("channel", u32, currentProgram))
        .setComment("Descriptor-driven masked port write using reference_level; no local index validation.");
    semanticFunction(0x62082L, "f33_write_channel_requested_level", v,
        new ParameterImpl("channel", u32, currentProgram))
        .setComment("Descriptor-driven masked port write using requested_level; no local index validation.");
    semanticFunction(0x620B4L, "f33_read_channel_input_level", u32,
        new ParameterImpl("channel", u32, currentProgram))
        .setComment("Read the descriptor-selected halfword port input, isolate its bit, return zero-extended level. "
            + "No local index validation; the two reviewed wrappers pass0/1.");
    semanticFunction(0x66AB0L, "f33_channel0_matches_reference", u32)
        .setComment("Return full-width0/1 for input channel0 equal to ROM31302 reference level1.");
    semanticFunction(0x66AE8L, "f33_channel1_matches_reference", u32)
        .setComment("Return full-width0/1 for input channel1 equal to ROM3130A reference level1.");
    StructureDataType port = new StructureDataType(category, "F33ChannelPortDescriptor", 0);
    port.setPackingEnabled(true);
    port.add(u32, "output_selector", "Output bit in low4; output port in bits8..15.");
    port.add(u8, "input_port", "Input register stride is0x40 bytes.");
    port.add(u8, "input_bit", "Bit selected from a halfword port read.");
    port.add(u8, "reference_level", "Compared against input and selected by a clear request bit.");
    port.add(u8, "requested_level", "Selected by an asserted request bit.");
    semanticData(0x312FCL, new ArrayDataType(resolve(port), 2, 8), "f33_channel_ports",
        "Two rows consumed by channel wrappers: port0/bit10 and port3/bit5, reference1/requested0. "
            + "OEM pin roles and physical response remain unassigned.");
    StructureDataType channels = new StructureDataType(category, "F33ChannelRequestState", 0);
    channels.setPackingEnabled(true);
    channels.add(u8, "channel0_state", "0=mismatch,1=qualifying mismatch,2=match,3=qualifying match.");
    channels.add(u8, "channel0_match_calls", "Consecutive matching invocations; not elapsed time.");
    channels.add(u8, "channel0_mismatch_calls", "Consecutive mismatching invocations.");
    channels.add(u8, "channel1_state", "Same software qualification encoding as channel0.");
    channels.add(u8, "channel1_match_calls", "Consecutive matching invocations.");
    channels.add(u8, "channel1_mismatch_calls", "Consecutive mismatching invocations.");
    channels.add(new ArrayDataType(u8, 2, 1), "opaque_06", "Not interpreted by this reconstruction.");
    channels.add(new ArrayDataType(u32, 5, 4), "owner_requests", "OR-reduced before output writes.");
    channels.add(u32, "observed_mismatch", "Readback bits1/17, separate from owner requests.");
    semanticData(0xFEBE8A68L, resolve(channels), "f33_channel_request_state",
        "Software request, GPIO observation and qualification are distinct phases. ROM thresholds are zero in this image.");
  }
  private void annotateDataFlashReads() throws Exception {
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType words = new PointerDataType(u32, 4);
    Function load8 = semanticFunction(0x78AD4L, "f33_load_u8", u32,
        new ParameterImpl("source", new PointerDataType(u8, 4), currentProgram));
    load8.setComment("MOV r6,EP; SLD.BU [EP],r10; JMP LP. Zero-extend to full32 "
        + "r10; preserve r6/r7/r8. Inline real p-code, not a replacement helper.");
    load8.setInline(true);
    Function load16 = semanticFunction(0x78ADAL, "f33_load_u16", u32,
        new ParameterImpl("source", new PointerDataType(u16, 4), currentProgram));
    load16.setComment("MOV r6,EP; SLD.HU [EP],r10; JMP LP. Zero-extend to full32 "
        + "r10; preserve r6/r7/r8. Keep FACI pointer dataflow across actual calls.");
    load16.setInline(true);
    Function load = semanticFunction(0x78AE0L, "f33_load_u32", u32,
        new ParameterImpl("source", words, currentProgram));
    load.setComment("MOV r6,EP; SLD.W [EP],r10; JMP LP. Preserve r6/r7/r8. "
        + "Inline the real p-code so repeated ICU-S reads and the DataFlash "
        + "ECC-clear pointer/value retain their actual register dataflow.");
    load.setInline(true);
    Function store8 = semanticFunction(0x78AE6L, "f33_store_u8", VoidDataType.dataType,
        new ParameterImpl("destination", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("value", u8, currentProgram));
    store8.setComment("Store low8(r7) through r6. Only EP changes among GPRs; "
        + "preserve the pointer/value and prior r10 through the real inline p-code.");
    store8.setInline(true);
    Function store16 = semanticFunction(0x78AECL, "f33_store_u16", VoidDataType.dataType,
        new ParameterImpl("destination", new PointerDataType(u16, 4), currentProgram),
        new ParameterImpl("value", u16, currentProgram));
    store16.setComment("Store low16(r7) through r6. Only EP changes among GPRs. "
        + "Native execution exercises the documented halfword ECC-clear access.");
    store16.setInline(true);
    Function store32 = semanticFunction(0x78AF2L, "f33_store_u32", VoidDataType.dataType,
        new ParameterImpl("destination", words, currentProgram),
        new ParameterImpl("value", u32, currentProgram));
    store32.setComment("Store full32(r7) through r6. Only EP changes among GPRs. "
        + "Native execution exercises the documented word ECC-clear access.");
    store32.setInline(true);
    semanticFunction(0x792FCL, "f33_icus20_second_read_bit0", u32)
        .setComment("Read FFC5D020 twice through78AE0; return bit0 of the second "
            + "word. The first result is discarded, not the first access. "
            + "Explicit external transitions between the reads execute both "
            + "directions. No recovered OEM bit name, reset or completion semantics.");
    semanticFunction(0x8B018L, "f33_icus20_read_bit0", u32)
        .setComment("Read FFC5D020 once and return zero/one from bit0. "
            + "Different callers may use different polarity; no global permission "
            + "or busy/ready meaning is assigned to this opaque hardware input.");
    semanticFunction(0x78F28L, "f33_dataflash_copy_words_ecc", u32,
        new ParameterImpl("dataflash_offset", u32, currentProgram),
        new ParameterImpl("destination", words, currentProgram),
        new ParameterImpl("byte_count", u32, currentProgram))
        .setComment("Unchecked do/while copy from FF200000+offset. Clear DFERSTR "
            + "SEDF/DEDF through DFERSTC before the first word, then sample status "
            + "after each destination store. Nonzero status causes another clear; "
            + "DEDF sets sticky return6, otherwise return0. No rollback. The loop "
            + "compares unsigned source+4 against the wrapping computed end; "
            + "zero count still copies one word. ECC flags are explicit model "
            + "inputs, not calculated flash corruption/correction or timing.");
    semanticFunction(0x788B6L, "f33_dataflash_read_words", u32,
        new ParameterImpl("dataflash_offset", u32, currentProgram),
        new ParameterImpl("destination", words, currentProgram),
        new ParameterImpl("byte_count", u32, currentProgram))
        .setComment("Ordered admission: second ICU-S offset20 bit0 set returnsB; "
            + "FEBF6CB0!=1 returns4; FEBF6CB2!=E returnsC. Require nonNULL "
            + "destination, aligned offset<8000, nonzero aligned length<=64 "
            + "and inclusive source end<=7FFF; invalid arguments return3. "
            + "No local destination bounds/alignment check. Run78F28 and map "
            + "zero to2, nonzero to5. Return5 does not undo destination stores. "
            + "Conditional native execution is not a hardware readiness or "
            + "complete application NvM restoration claim.");
  }
  private void annotateFaciSubmission() throws Exception {
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    semanticFunction(0x78B3AL, "f33_flash_set_software_enables", VoidDataType.dataType,
        new ParameterImpl("value", u32, currentProgram))
        .setComment("Write full32 input to FHVE15 atFFF8A430 then FHVE3 atFFF82410; "
            + "read back FHVE3 and SYNCP. Hardware exposes only bit0; both enables "
            + "are required for programming/erasure/blank checking. This function "
            + "does not validate the input or verify both values.");
    semanticFunction(0x78DE2L, "f33_faci_check_dataflash_addresses", u32)
        .setComment("Return1 when full FSADDR<8000 and unsigned(FEADDR+3)<=7FFF, "
            + "else7. No start<=end or span check. Real address-register writes "
            + "discard low two bits; the final-word end input7FFF reads as7FFC.");
    semanticFunction(0x78EC6L, "f33_faci_submit_range_command", u32,
        new ParameterImpl("start_offset", u32, currentProgram),
        new ParameterImpl("end_offset", u32, currentProgram),
        new ParameterImpl("command", u8, currentProgram))
        .setComment("Clear EIC379 request, set FBCCNT=0 only for command71, "
            + "write FCPSR=0, FSADDR, FEADDR, then command byte. Check address "
            + "readback through78DE2; appendD0 only for result1. Preserve that "
            + "result through the final store helper. Result7 leaves a prefix "
            + "without D0; this is submission, not hardware completion.");
    semanticFunction(0x79044L, "f33_faci_decode_completion_status", u32)
        .setComment("FBCSTAT bit0 and software operation byte6CAC==3 return5 "
            + "before inspecting FSTATR. Otherwise PRGERR(bit12) returns3, then "
            + "ERSERR(bit13) returns4, otherwise0. No FRDY or CMDLK check here.");
    semanticFunction(0x7892AL, "f33_dataflash_blank_check", u32,
        new ParameterImpl("dataflash_offset", u32, currentProgram),
        new ParameterImpl("byte_count", u32, currentProgram))
        .setComment("Ordered ICU-S/software-state/range gates match788B6 except "
            + "there is no destination argument. Enter DataFlash P/E, enable both "
            + "FHVE controls, set operation3 and submit71,D0. Poll status, leave "
            + "P/E and disable enables on the completed path. Return2 for blank, "
            + "7 for nonblank,8 for completion/setup failure; admissionB/4/C/3. "
            + "Native blank/nonblank results are explicit hardware inputs. "
            + "Timeout reaches realB3 forced-stop; its completion is also an explicit hardware input.");
    Function sync = semanticFunction(0x7940EL, "f33_syncp", VoidDataType.dataType);
    sync.setComment("SYNCP; JMP LP. Inline the actual ordering operation; no "
        + "GPR modification or physical completion/timing claim.");
    sync.setInline(true);
  }
  private void repairCodeTail(long entry, long tail, long last) throws Exception {
    Function function = getFunctionAt(toAddr(entry));
    if (function == null) throw new IllegalStateException("missing repair entry " + toAddr(entry));
    currentProgram.getListing().clearCodeUnits(toAddr(tail), toAddr(last), false);
    if (!disassemble(toAddr(tail))) {
      throw new IllegalStateException("failed to recover code tail " + toAddr(tail));
    }
    function.setBody(new AddressSet(toAddr(entry), toAddr(last)));
  }
  private void annotateRecoveredBootEntries() throws Exception {
    // D48 is inside the four-byte MULHI atD46, not an entry. Its incoming
    // parameter reference is a scalar delay count, not a control-flow edge.
    repairCodeTail(0xC9AL, 0xD46L, 0xE53L);
    // The undefined4 datum at8374 covered MOV/BR instructions, truncating
    // this real copied-code dispatcher to its four-byte PREPARE.
    repairCodeTail(0x8370L, 0x8374L, 0x8399L);
    Function dispatch = getFunctionAt(toAddr(0x8370L));
    dispatch.setName("f33_boot_ram_dispatch", SourceType.USER_DEFINED);
    dispatch.setComment("Boot-phase source of the dispatcher copied by35E4 to "
        + "FEBF1000. Scan eight-byte {u32 key,u32 handler} records atFEBF0F00 "
        + "until key equals full32-bit r6 orFFFFFFFF; call the selected handler. "
        + "No local table bound. r6-r9 are unchanged before the call; DISPOSE "
        + "does not change callback result registers. No complete callback ABI "
        + "is imposed. Native execution covers matching/fallback selection and "
        + "real35E4 relocation followed by RAM instruction execution, stopping "
        + "before the callback. Synthetic input table; no flash operation.");
    semanticFunction(0x71C68L, "f33_spin_wait", VoidDataType.dataType,
        new ParameterImpl("outer_iterations", UnsignedIntegerDataType.dataType, currentProgram))
        .setComment("Full32-bit nonzero outer count; each iteration decrements "
            + "an inner counter from155 to zero. Zero bypasses both loops. "
            + "Exact execution takes4 instructions for zero,313*n+5 for "
            + "positive tested n=1,2,3400. These are instruction counts, not "
            + "clock-cycle or wall-time calibration. No ordinary return value.");
    semanticData(0x30D8CL, UnsignedIntegerDataType.dataType,
        "f33_startup_spin_iteration_count",
        "Scalar3400 (D48), loaded by63ABC and passed to71C68. "
        + "Not a pointer into the instruction atD46.");
  }
  private void annotateComposedMonitorLayouts() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
    FunctionDefinitionDataType predicate = new FunctionDefinitionDataType(category, "F33MonitorPredicate");
    predicate.setReturnType(u32);
    FunctionDefinitionDataType action = new FunctionDefinitionDataType(category, "F33MonitorAction");
    action.setReturnType(v);
    DataType predicatePointer = new PointerDataType(predicate, 4);
    DataType actionPointer = new PointerDataType(action, 4);
    StructureDataType terminalMonitorState = new StructureDataType(category, "F33TerminalMonitorState", 0);
    terminalMonitorState.setPackingEnabled(true);
    terminalMonitorState.add(u8, "status", null);
    terminalMonitorState.add(u8, "padding", null);
    terminalMonitorState.add(u16, "passing_count", null);
    terminalMonitorState.add(u16, "failing_count", null);
    terminalMonitorState.add(u16, "failing_high_water", null);
    resolve(terminalMonitorState);
    StructureDataType latchedMonitorState = new StructureDataType(category, "F33LatchedMonitorState", 0);
    latchedMonitorState.setPackingEnabled(true);
    latchedMonitorState.add(u32, "packed_status", null);
    latchedMonitorState.add(u16, "passing_count", null);
    latchedMonitorState.add(u16, "failing_count", null);
    latchedMonitorState.add(u16, "failing_high_water", null);
    resolve(latchedMonitorState);
    StructureDataType recoverableMonitorState = new StructureDataType(category, "F33RecoverableMonitorState", 0);
    recoverableMonitorState.setPackingEnabled(true);
    recoverableMonitorState.add(u32, "packed_status", null);
    recoverableMonitorState.add(u16, "passing_count", null);
    recoverableMonitorState.add(u16, "failing_count", null);
    recoverableMonitorState.add(u16, "failing_high_water", null);
    recoverableMonitorState.add(u16, "recovery_count", null);
    resolve(recoverableMonitorState);
    StructureDataType windowedMonitorState = new StructureDataType(category, "F33WindowedMonitorState", 0);
    windowedMonitorState.setPackingEnabled(true);
    windowedMonitorState.add(u32, "packed_status", null);
    windowedMonitorState.add(u16, "passing_count", null);
    windowedMonitorState.add(u16, "passing_window", null);
    windowedMonitorState.add(u16, "failing_count", null);
    windowedMonitorState.add(u16, "failing_window", null);
    windowedMonitorState.add(u16, "failing_high_water", null);
    resolve(windowedMonitorState);
    StructureDataType monitorRecoveryScratch = new StructureDataType(category, "F33MonitorRecoveryScratch", 0);
    monitorRecoveryScratch.setPackingEnabled(true);
    monitorRecoveryScratch.add(u16, "passing_count", null);
    monitorRecoveryScratch.add(u16, "opaque_02", null);
    monitorRecoveryScratch.add(u16, "failing_count", null);
    monitorRecoveryScratch.add(u16, "failing_high_water", null);
    monitorRecoveryScratch.add(u16, "opaque_08", null);
    monitorRecoveryScratch.add(u16, "recovery_count", null);
    monitorRecoveryScratch.add(u16, "opaque_0c", null);
    monitorRecoveryScratch.add(u16, "opaque_0e", null);
    monitorRecoveryScratch.add(u16, "opaque_10", null);
    resolve(monitorRecoveryScratch);
    StructureDataType monitorLimits = new StructureDataType(category, "F33MonitorLimits", 0);
    monitorLimits.setPackingEnabled(true);
    monitorLimits.add(u16, "passing_limit", null);
    monitorLimits.add(u16, "failing_limit", null);
    resolve(monitorLimits);
    StructureDataType recoverableMonitorLimits = new StructureDataType(category, "F33RecoverableMonitorLimits", 0);
    recoverableMonitorLimits.setPackingEnabled(true);
    recoverableMonitorLimits.add(u16, "passing_limit", null);
    recoverableMonitorLimits.add(u16, "failing_limit", null);
    recoverableMonitorLimits.add(u16, "recovery_limit", null);
    resolve(recoverableMonitorLimits);
    StructureDataType windowedMonitorLimits = new StructureDataType(category, "F33WindowedMonitorLimits", 0);
    windowedMonitorLimits.setPackingEnabled(true);
    windowedMonitorLimits.add(u16, "passing_limit", null);
    windowedMonitorLimits.add(u16, "passing_window_limit", null);
    windowedMonitorLimits.add(u16, "failing_limit", null);
    windowedMonitorLimits.add(u16, "failing_window_limit", null);
    resolve(windowedMonitorLimits);
    StructureDataType terminalMonitorCallbacks = new StructureDataType(category, "F33TerminalMonitorCallbacks", 0);
    terminalMonitorCallbacks.setPackingEnabled(true);
    terminalMonitorCallbacks.add(predicatePointer, "classify", null);
    terminalMonitorCallbacks.add(actionPointer, "healthy_observed", null);
    terminalMonitorCallbacks.add(actionPointer, "failed", null);
    resolve(terminalMonitorCallbacks);
    StructureDataType twoSidedMonitorCallbacks = new StructureDataType(category, "F33TwoSidedMonitorCallbacks", 0);
    twoSidedMonitorCallbacks.setPackingEnabled(true);
    twoSidedMonitorCallbacks.add(predicatePointer, "classify_normal", null);
    twoSidedMonitorCallbacks.add(predicatePointer, "classify_failing", null);
    twoSidedMonitorCallbacks.add(actionPointer, "enter_passing", null);
    twoSidedMonitorCallbacks.add(actionPointer, "leave_pending_passing", null);
    twoSidedMonitorCallbacks.add(actionPointer, "confirm_passing", null);
    twoSidedMonitorCallbacks.add(actionPointer, "leave_confirmed_passing", null);
    twoSidedMonitorCallbacks.add(actionPointer, "enter_failing", null);
    twoSidedMonitorCallbacks.add(actionPointer, "leave_pending_failing", null);
    twoSidedMonitorCallbacks.add(actionPointer, "confirm_failing", null);
    twoSidedMonitorCallbacks.add(actionPointer, "repeat_pending_passing", null);
    twoSidedMonitorCallbacks.add(actionPointer, "repeat_confirmed_passing", null);
    twoSidedMonitorCallbacks.add(actionPointer, "repeat_pending_failing", null);
    twoSidedMonitorCallbacks.add(actionPointer, "repeat_confirmed_failing", null);
    resolve(twoSidedMonitorCallbacks);
    StructureDataType recoverableMonitorCallbacks = new StructureDataType(category, "F33RecoverableMonitorCallbacks", 0);
    recoverableMonitorCallbacks.setPackingEnabled(true);
    recoverableMonitorCallbacks.add(predicatePointer, "classify_normal", null);
    recoverableMonitorCallbacks.add(predicatePointer, "classify_failing", null);
    recoverableMonitorCallbacks.add(predicatePointer, "classify_recovery", null);
    recoverableMonitorCallbacks.add(actionPointer, "enter_passing", null);
    recoverableMonitorCallbacks.add(actionPointer, "leave_pending_passing", null);
    recoverableMonitorCallbacks.add(actionPointer, "confirm_passing", null);
    recoverableMonitorCallbacks.add(actionPointer, "leave_confirmed_passing", null);
    recoverableMonitorCallbacks.add(actionPointer, "enter_failing", null);
    recoverableMonitorCallbacks.add(actionPointer, "leave_pending_failing", null);
    recoverableMonitorCallbacks.add(actionPointer, "confirm_failing", null);
    recoverableMonitorCallbacks.add(actionPointer, "recover_confirmed_failing", null);
    recoverableMonitorCallbacks.add(actionPointer, "repeat_pending_passing", null);
    recoverableMonitorCallbacks.add(actionPointer, "repeat_confirmed_passing", null);
    recoverableMonitorCallbacks.add(actionPointer, "repeat_pending_failing", null);
    recoverableMonitorCallbacks.add(actionPointer, "repeat_confirmed_failing", null);
    resolve(recoverableMonitorCallbacks);
  }
  private void annotateTerminalMonitorComposition() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType monitorLimitsType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33MonitorLimits");
    DataType F33MonitorLimitsPointer = new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33MonitorLimits"), 4);
    DataType terminalMonitorCallbacksType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33TerminalMonitorCallbacks");
    DataType F33TerminalMonitorCallbacksPointer = new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33TerminalMonitorCallbacks"), 4);
    DataType terminalMonitorStateType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33TerminalMonitorState");
    DataType F33TerminalMonitorStatePointer = new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33TerminalMonitorState"), 4);
    semanticFunction(0x3E624L, "f33_step_delayed_status_bit_triplet_a", v)
        .setComment("Configured mode0205 channela monitor; 3 eight-byte states at759C. Own qualification6764 bit0 holds "
            + "state without reset. Gate baseline_one (numeric states, no physical meaning); threshold "
            + "pass2/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot10 with "
            + "kind(s)0x1d; no confirmed source leaves previous action untouched. Callback table283C4; failure "
            + "events0x57,0x58,0x59. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x3E77EL, "f33_classify_delayed_status_bit_triplet_a", u32)
        .setComment("No-argument configured classifier. Gate baseline_one: requested==0 && observed==0 && "
            + "bit(6620,b+2)==1 && bit(661C,b+2)==1 && bit(6628,b+1)==0 && bit(6614,0)==1 &&65F0==5A. Closed gate "
            + "returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold partitions preserved in ROM. No "
            + "physical units/source identity asserted.");
    semanticFunction(0x3E7D4L, "f33_record_delayed_status_bit_triplet_a_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x3E7E4L, "f33_record_delayed_status_bit_triplet_a_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x3E8BCL, "f33_step_delayed_status_bit_triplet_b", v)
        .setComment("Configured mode0205 channelb monitor; 3 eight-byte states at75B8. Own qualification6764 bit1 holds "
            + "state without reset. Gate baseline_one (numeric states, no physical meaning); threshold "
            + "pass2/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot11 with "
            + "kind(s)0x1e; no confirmed source leaves previous action untouched. Callback table283D0; failure "
            + "events0x5d,0x5e,0x5f. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x3EA1CL, "f33_classify_delayed_status_bit_triplet_b", u32)
        .setComment("No-argument configured classifier. Gate baseline_one: requested==0 && observed==0 && "
            + "bit(6620,b+2)==1 && bit(661C,b+2)==1 && bit(6628,b+1)==0 && bit(6614,0)==1 &&65F0==5A. Closed gate "
            + "returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold partitions preserved in ROM. No "
            + "physical units/source identity asserted.");
    semanticFunction(0x3EA72L, "f33_record_delayed_status_bit_triplet_b_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x3EA82L, "f33_record_delayed_status_bit_triplet_b_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x3EB04L, "f33_step_matched_state2_status_bit_triplet_a", v)
        .setComment("Configured mode020D channela monitor; 3 eight-byte states at75D4. Own qualification6764 bit0 holds "
            + "state without reset. Gate off_both2 (numeric states, no physical meaning); threshold pass2/fail200 "
            + "with strict crossings. Any confirmed22 retains/replaces shared slot10 with kind(s)0x1b,0x32; no "
            + "confirmed source leaves previous action untouched. Callback table283DC; failure "
            + "events0xce,0xcf,0xd0. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x3EC40L, "f33_classify_matched_state2_status_bit_triplet_a", u32)
        .setComment("No-argument configured classifier. Gate off_both2: requested==2 &&observed==2 "
            + "&&(6620&(6<<b))==(4<<b) &&(661C&(6<<b))==(4<<b) &&bit(6628,b+1)==0 &&6614.bit0==0 && "
            + "own65F6/65F7==5A. Closed gate returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold "
            + "partitions preserved in ROM. No physical units/source identity asserted.");
    semanticFunction(0x3ECA2L, "f33_record_matched_state2_status_bit_triplet_a_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x3ECB2L, "f33_record_matched_state2_status_bit_triplet_a_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x3ED34L, "f33_step_matched_state2_status_bit_triplet_b", v)
        .setComment("Configured mode020D channelb monitor; 3 eight-byte states at75F0. Own qualification6764 bit1 holds "
            + "state without reset. Gate off_both2 (numeric states, no physical meaning); threshold pass2/fail200 "
            + "with strict crossings. Any confirmed22 retains/replaces shared slot11 with kind(s)0x1c,0x32; no "
            + "confirmed source leaves previous action untouched. Callback table283E8; failure "
            + "events0xdb,0xdc,0xdd. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x3EE70L, "f33_classify_matched_state2_status_bit_triplet_b", u32)
        .setComment("No-argument configured classifier. Gate off_both2: requested==2 &&observed==2 "
            + "&&(6620&(6<<b))==(4<<b) &&(661C&(6<<b))==(4<<b) &&bit(6628,b+1)==0 &&6614.bit0==0 && "
            + "own65F6/65F7==5A. Closed gate returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold "
            + "partitions preserved in ROM. No physical units/source identity asserted.");
    semanticFunction(0x3EED6L, "f33_record_matched_state2_status_bit_triplet_b_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x3EEE6L, "f33_record_matched_state2_status_bit_triplet_b_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x3F13AL, "f33_step_coupled_sample_threshold_both", v)
        .setComment("Configured mode0208 coupled-channel monitor; qualification6764&3 resets engine then forces status0 "
            + "rather than holding.. Gate coupled (numeric states, no physical meaning); threshold pass0/fail200 "
            + "with strict crossings. Any confirmed22 retains/replaces shared slot9 with kind(s)0x1a; no confirmed "
            + "source leaves previous action untouched. Callback table283F4; failure events0x60,0x61. See "
            + "configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x3F1C8L, "f33_classify_coupled_sample_threshold_both", u32)
        .setComment("No-argument configured classifier. Gate coupled: 64D8==2 &&64D9==2 &&64D0==0 &&64D1==0 "
            + "&&(6620&60006)==20002 &&(661C&40004)==40004 &&(6628&20002)==20002 &&6614.bit0==0 &&65F0==5A; hex "
            + "masks. Closed gate returns44, otherwise22 iff 66B2<1326 &&66B4<1326 (configured equal threshold "
            + "pairs;66B8 partition3328 covers all values), else11. Full threshold partitions preserved in ROM. No "
            + "physical units/source identity asserted.");
    semanticFunction(0x3F27CL, "f33_record_coupled_sample_threshold_both_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0x60,0x61.");
    semanticFunction(0x3F294L, "f33_record_coupled_sample_threshold_both_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0x60,0x61.");
    semanticFunction(0x3F3D2L, "f33_step_command_status_bit_clear_a", v)
        .setComment("Configured mode0206 channela monitor; 1 eight-byte states at7614. Own qualification6764 bit0 holds "
            + "state without reset. Gate baseline_zero (numeric states, no physical meaning); threshold "
            + "pass2/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot10 with "
            + "kind(s)0x1d; no confirmed source leaves previous action untouched. Callback table28400; failure "
            + "events0x74. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x3F452L, "f33_classify_command_status_bit_clear_a", u32)
        .setComment("No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0. "
            + "Closed gate returns44, otherwise22 iff 8291==0, else11. Full threshold partitions preserved in ROM. "
            + "No physical units/source identity asserted.");
    semanticFunction(0x3F4A6L, "f33_record_command_status_bit_clear_a_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0x74.");
    semanticFunction(0x3F4B6L, "f33_record_command_status_bit_clear_a_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0x74.");
    semanticFunction(0x3F5E8L, "f33_step_command_status_bit_clear_b", v)
        .setComment("Configured mode0206 channelb monitor; 1 eight-byte states at761C. Own qualification6764 bit1 holds "
            + "state without reset. Gate baseline_zero (numeric states, no physical meaning); threshold "
            + "pass2/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot11 with "
            + "kind(s)0x1e; no confirmed source leaves previous action untouched. Callback table2840C; failure "
            + "events0x75. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x3F668L, "f33_classify_command_status_bit_clear_b", u32)
        .setComment("No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0. "
            + "Closed gate returns44, otherwise22 iff 8292==0, else11. Full threshold partitions preserved in ROM. "
            + "No physical units/source identity asserted.");
    semanticFunction(0x3F6BCL, "f33_record_command_status_bit_clear_b_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0x75.");
    semanticFunction(0x3F6CCL, "f33_record_command_status_bit_clear_b_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0x75.");
    semanticFunction(0x3F744L, "f33_step_bounded_sample_or_status_a", v)
        .setComment("Configured mode0201 channela monitor; 1 eight-byte states at7624. Own qualification6764 bit0 holds "
            + "state without reset. Gate baseline_zero (numeric states, no physical meaning); threshold "
            + "pass2/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot10 with "
            + "kind(s)0x1d; no confirmed source leaves previous action untouched. Callback table28418; failure "
            + "events0x89. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x3F7D8L, "f33_classify_bounded_sample_or_status_a", u32)
        .setComment("No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0. "
            + "Closed gate returns44, otherwise22 iff 66BC<351 || 8284==5A, else11. Full threshold partitions "
            + "preserved in ROM. No physical units/source identity asserted.");
    semanticFunction(0x3F848L, "f33_record_bounded_sample_or_status_a_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0x89.");
    semanticFunction(0x3F858L, "f33_record_bounded_sample_or_status_a_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0x89.");
    semanticFunction(0x3F8D0L, "f33_step_bounded_sample_or_status_b", v)
        .setComment("Configured mode0201 channelb monitor; 1 eight-byte states at762C. Own qualification6764 bit1 holds "
            + "state without reset. Gate baseline_zero (numeric states, no physical meaning); threshold "
            + "pass2/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot11 with "
            + "kind(s)0x1e; no confirmed source leaves previous action untouched. Callback table28424; failure "
            + "events0x8a. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x3F964L, "f33_classify_bounded_sample_or_status_b", u32)
        .setComment("No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0. "
            + "Closed gate returns44, otherwise22 iff 66BE<351 || 8283==5A, else11. Full threshold partitions "
            + "preserved in ROM. No physical units/source identity asserted.");
    semanticFunction(0x3F9D4L, "f33_record_bounded_sample_or_status_b_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0x8a.");
    semanticFunction(0x3F9E4L, "f33_record_bounded_sample_or_status_b_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0x8a.");
    semanticFunction(0x3FABCL, "f33_step_requested_state_sample_threshold_a", v)
        .setComment("Configured mode0203 channela monitor; 1 eight-byte states at7634. Own qualification6764 bit0 holds "
            + "state without reset. Gate requested2_one (numeric states, no physical meaning); threshold "
            + "pass0/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot10 with "
            + "kind(s)0x1d; no confirmed source leaves previous action untouched. Callback table28430; failure "
            + "events0xef. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x3FB3CL, "f33_classify_requested_state_sample_threshold_a", u32)
        .setComment("No-argument configured classifier. Gate requested2_one: requested==2 &&observed==0 "
            + "&&bit(6620,b+2)==1 &&bit(661C,b+2)==1 &&bit(6628,b+1)==0 &&6614.bit0==1 &&65F0==5A. Closed gate "
            + "returns44, otherwise22 iff 66B2>1247 (both3328 partitions), else11. Full threshold partitions "
            + "preserved in ROM. No physical units/source identity asserted.");
    semanticFunction(0x3FBAEL, "f33_record_requested_state_sample_threshold_a_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0xef.");
    semanticFunction(0x3FBBEL, "f33_record_requested_state_sample_threshold_a_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0xef.");
    semanticFunction(0x3FC96L, "f33_step_requested_state_sample_threshold_b", v)
        .setComment("Configured mode0203 channelb monitor; 1 eight-byte states at7644. Own qualification6764 bit1 holds "
            + "state without reset. Gate requested2_one (numeric states, no physical meaning); threshold "
            + "pass0/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot11 with "
            + "kind(s)0x1e; no confirmed source leaves previous action untouched. Callback table2843C; failure "
            + "events0xf0. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x3FD16L, "f33_classify_requested_state_sample_threshold_b", u32)
        .setComment("No-argument configured classifier. Gate requested2_one: requested==2 &&observed==0 "
            + "&&bit(6620,b+2)==1 &&bit(661C,b+2)==1 &&bit(6628,b+1)==0 &&6614.bit0==1 &&65F0==5A. Closed gate "
            + "returns44, otherwise22 iff 66B4>1247 (both3328 partitions), else11. Full threshold partitions "
            + "preserved in ROM. No physical units/source identity asserted.");
    semanticFunction(0x3FD88L, "f33_record_requested_state_sample_threshold_b_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0xf0.");
    semanticFunction(0x3FD98L, "f33_record_requested_state_sample_threshold_b_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0xf0.");
    semanticFunction(0x3FDDEL, "f33_step_asserted_state_sample_threshold_a", v)
        .setComment("Configured mode0209 channela monitor; 1 eight-byte states at67F0. Own qualification6764 bit0 holds "
            + "state without reset. Gate asserted_zero (numeric states, no physical meaning); threshold "
            + "pass0/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot10 with "
            + "kind(s)0x1d; no confirmed source leaves previous action untouched. Callback table28448; failure "
            + "events0x9d. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x3FE4AL, "f33_classify_asserted_state_sample_threshold_a", u32)
        .setComment("No-argument configured classifier. Gate asserted_zero: requested==2 &&observed==0 "
            + "&&(6620&(6<<b))==(2<<b) &&bit(661C,b+2)==1 &&bit(6628,b+1)==1 &&6614.bit0==0 &&65F0==5A. Closed gate "
            + "returns44, otherwise22 iff 66B2<965 (configured equal thresholds in both3328 partitions), else11. "
            + "Full threshold partitions preserved in ROM. No physical units/source identity asserted.");
    semanticFunction(0x3FEC2L, "f33_record_asserted_state_sample_threshold_a_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0x9d.");
    semanticFunction(0x3FED2L, "f33_record_asserted_state_sample_threshold_a_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0x9d.");
    semanticFunction(0x3FF18L, "f33_step_asserted_state_sample_threshold_b", v)
        .setComment("Configured mode0209 channelb monitor; 1 eight-byte states at67F8. Own qualification6764 bit1 holds "
            + "state without reset. Gate asserted_zero (numeric states, no physical meaning); threshold "
            + "pass0/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot11 with "
            + "kind(s)0x1e; no confirmed source leaves previous action untouched. Callback table28454; failure "
            + "events0xc7. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x3FF84L, "f33_classify_asserted_state_sample_threshold_b", u32)
        .setComment("No-argument configured classifier. Gate asserted_zero: requested==2 &&observed==0 "
            + "&&(6620&(6<<b))==(2<<b) &&bit(661C,b+2)==1 &&bit(6628,b+1)==1 &&6614.bit0==0 &&65F0==5A. Closed gate "
            + "returns44, otherwise22 iff 66B4<965 (configured equal thresholds in both3328 partitions), else11. "
            + "Full threshold partitions preserved in ROM. No physical units/source identity asserted.");
    semanticFunction(0x3FFFCL, "f33_record_asserted_state_sample_threshold_b_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0xc7.");
    semanticFunction(0x4000CL, "f33_record_asserted_state_sample_threshold_b_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0xc7.");
    semanticFunction(0x400D0L, "f33_step_sample_difference_window_a", v)
        .setComment("Configured mode0200 channela monitor; 1 eight-byte states at7654. Own qualification6764 bit0 holds "
            + "state without reset. Gate baseline_zero (numeric states, no physical meaning); threshold "
            + "pass0/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot10 with "
            + "kind(s)0x1d,0x32; no confirmed source leaves previous action untouched. Callback table28460; failure "
            + "events0x79. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x40166L, "f33_classify_sample_difference_window_a", u32)
        .setComment("No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0. "
            + "Closed gate returns44, otherwise22 iff (int32(uint16(66B8))-int32(uint16(66AE))>1180 &&66B8<=4736) "
            + "|| (66AE<1055 &&66B8>4736), else11. Full threshold partitions preserved in ROM. No physical "
            + "units/source identity asserted.");
    semanticFunction(0x401DCL, "f33_record_sample_difference_window_a_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0x79.");
    semanticFunction(0x401ECL, "f33_record_sample_difference_window_a_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0x79.");
    semanticFunction(0x402B0L, "f33_step_sample_difference_window_b", v)
        .setComment("Configured mode0200 channelb monitor; 1 eight-byte states at765C. Own qualification6764 bit1 holds "
            + "state without reset. Gate baseline_zero (numeric states, no physical meaning); threshold "
            + "pass0/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot11 with "
            + "kind(s)0x1e,0x32; no confirmed source leaves previous action untouched. Callback table2846C; failure "
            + "events0xb8. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x40346L, "f33_classify_sample_difference_window_b", u32)
        .setComment("No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0. "
            + "Closed gate returns44, otherwise22 iff (int32(uint16(66B8))-int32(uint16(66B0))>1180 &&66B8<=4736) "
            + "|| (66B0<1055 &&66B8>4736), else11. Full threshold partitions preserved in ROM. No physical "
            + "units/source identity asserted.");
    semanticFunction(0x403BCL, "f33_record_sample_difference_window_b_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0xb8.");
    semanticFunction(0x403CCL, "f33_record_sample_difference_window_b_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0xb8.");
    semanticFunction(0x40516L, "f33_step_matched_state2_status_bit_a", v)
        .setComment("Configured mode020A channela monitor; 1 eight-byte states at7664. Own qualification6764 bit0 holds "
            + "state without reset. Gate off_both2 (numeric states, no physical meaning); threshold pass2/fail200 "
            + "with strict crossings. Any confirmed22 retains/replaces shared slot10 with kind(s)0x1d; no confirmed "
            + "source leaves previous action untouched. Callback table28478; failure events0x78. See "
            + "configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x40596L, "f33_classify_matched_state2_status_bit_a", u32)
        .setComment("No-argument configured classifier. Gate off_both2: requested==2 &&observed==2 "
            + "&&(6620&(6<<b))==(4<<b) &&(661C&(6<<b))==(4<<b) &&bit(6628,b+1)==0 &&6614.bit0==0 && "
            + "own65F6/65F7==5A. Closed gate returns44, otherwise22 iff 8282==5A, else11. Full threshold partitions "
            + "preserved in ROM. No physical units/source identity asserted.");
    semanticFunction(0x405F8L, "f33_record_matched_state2_status_bit_a_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0x78.");
    semanticFunction(0x40608L, "f33_record_matched_state2_status_bit_a_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0x78.");
    semanticFunction(0x40752L, "f33_step_matched_state2_status_bit_b", v)
        .setComment("Configured mode020A channelb monitor; 1 eight-byte states at766C. Own qualification6764 bit1 holds "
            + "state without reset. Gate off_both2 (numeric states, no physical meaning); threshold pass2/fail200 "
            + "with strict crossings. Any confirmed22 retains/replaces shared slot11 with kind(s)0x1e; no confirmed "
            + "source leaves previous action untouched. Callback table28484; failure events0xc4. See "
            + "configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x407D2L, "f33_classify_matched_state2_status_bit_b", u32)
        .setComment("No-argument configured classifier. Gate off_both2: requested==2 &&observed==2 "
            + "&&(6620&(6<<b))==(4<<b) &&(661C&(6<<b))==(4<<b) &&bit(6628,b+1)==0 &&6614.bit0==0 && "
            + "own65F6/65F7==5A. Closed gate returns44, otherwise22 iff 8281==5A, else11. Full threshold partitions "
            + "preserved in ROM. No physical units/source identity asserted.");
    semanticFunction(0x40838L, "f33_record_matched_state2_status_bit_b_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0xc4.");
    semanticFunction(0x40848L, "f33_record_matched_state2_status_bit_b_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0xc4.");
    semanticFunction(0x408BEL, "f33_step_baseline_sample_threshold_a", v)
        .setComment("Configured mode0202 channela monitor; 1 eight-byte states at7674. Own qualification6764 bit0 holds "
            + "state without reset. Gate baseline_zero (numeric states, no physical meaning); threshold "
            + "pass0/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot10 with "
            + "kind(s)0x1d; no confirmed source leaves previous action untouched. Callback table28490; failure "
            + "events0x9c. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x4093EL, "f33_classify_baseline_sample_threshold_a", u32)
        .setComment("No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0. "
            + "Closed gate returns44, otherwise22 iff 66B2>1247 (both3328 partitions), else11. Full threshold "
            + "partitions preserved in ROM. No physical units/source identity asserted.");
    semanticFunction(0x409B0L, "f33_record_baseline_sample_threshold_a_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0x9c.");
    semanticFunction(0x409C0L, "f33_record_baseline_sample_threshold_a_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0x9c.");
    semanticFunction(0x40A36L, "f33_step_baseline_sample_threshold_b", v)
        .setComment("Configured mode0202 channelb monitor; 1 eight-byte states at767C. Own qualification6764 bit1 holds "
            + "state without reset. Gate baseline_zero (numeric states, no physical meaning); threshold "
            + "pass0/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot11 with "
            + "kind(s)0x1e; no confirmed source leaves previous action untouched. Callback table2849C; failure "
            + "events0xc6. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x40AB6L, "f33_classify_baseline_sample_threshold_b", u32)
        .setComment("No-argument configured classifier. Gate baseline_zero: same as baseline_one except6614.bit0==0. "
            + "Closed gate returns44, otherwise22 iff 66B4>1247 (both3328 partitions), else11. Full threshold "
            + "partitions preserved in ROM. No physical units/source identity asserted.");
    semanticFunction(0x40B28L, "f33_record_baseline_sample_threshold_b_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0xc6.");
    semanticFunction(0x40B38L, "f33_record_baseline_sample_threshold_b_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0xc6.");
    semanticFunction(0x40C8EL, "f33_step_observed_state_sample_regions_a", v)
        .setComment("Configured mode0207 channela monitor; 1 eight-byte states at7684. Own qualification6764 bit0 holds "
            + "state without reset. Gate observed2_zero (numeric states, no physical meaning); threshold "
            + "pass0/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot10 with "
            + "kind(s)0x1d; no confirmed source leaves previous action untouched. Callback table284A8; failure "
            + "events0x7b. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x40D0EL, "f33_classify_observed_state_sample_regions_a", u32)
        .setComment("No-argument configured classifier. Gate observed2_zero: requested==0 &&observed==2 "
            + "&&bit(6620,b+2)==1 &&(661C&(6<<b))==(2<<b) &&bit(6628,b+1)==1 &&6614.bit0==0 &&65F0==5A. Closed gate "
            + "returns44, otherwise22 iff 66B2<886 ||66B2>6020 (six-region predicate partitions66B8 at2816/4736 "
            + "with equal lower/upper thresholds), else11. Full threshold partitions preserved in ROM. No physical "
            + "units/source identity asserted.");
    semanticFunction(0x40DC2L, "f33_record_observed_state_sample_regions_a_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0x7b.");
    semanticFunction(0x40DD2L, "f33_record_observed_state_sample_regions_a_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0x7b.");
    semanticFunction(0x40F28L, "f33_step_observed_state_sample_regions_b", v)
        .setComment("Configured mode0207 channelb monitor; 1 eight-byte states at768C. Own qualification6764 bit1 holds "
            + "state without reset. Gate observed2_zero (numeric states, no physical meaning); threshold "
            + "pass0/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot11 with "
            + "kind(s)0x1e; no confirmed source leaves previous action untouched. Callback table284B4; failure "
            + "events0xba. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x40FA8L, "f33_classify_observed_state_sample_regions_b", u32)
        .setComment("No-argument configured classifier. Gate observed2_zero: requested==0 &&observed==2 "
            + "&&bit(6620,b+2)==1 &&(661C&(6<<b))==(2<<b) &&bit(6628,b+1)==1 &&6614.bit0==0 &&65F0==5A. Closed gate "
            + "returns44, otherwise22 iff 66B4<886 ||66B4>6020 (six-region predicate partitions66B8 at2816/4736 "
            + "with equal lower/upper thresholds), else11. Full threshold partitions preserved in ROM. No physical "
            + "units/source identity asserted.");
    semanticFunction(0x41060L, "f33_record_observed_state_sample_regions_b_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection 0xba.");
    semanticFunction(0x41070L, "f33_record_observed_state_sample_regions_b_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection 0xba.");
    semanticFunction(0x4110CL, "f33_step_sample_range_triplet_a", v)
        .setComment("Configured mode020B channela monitor; 3 eight-byte states at7694. Own qualification6764 bit0 holds "
            + "state without reset. Gate range_both2 (numeric states, no physical meaning); threshold pass0/fail200 "
            + "with strict crossings. Any confirmed22 retains/replaces shared slot10 with kind(s)0x1b; no confirmed "
            + "source leaves previous action untouched. Callback table284C0; failure "
            + "events0x66,0x67,0x68,0x69,0x6a,0x6b. See configured-family matrix for readiness sequencing and exact "
            + "predicate.");
    semanticFunction(0x41234L, "f33_classify_sample_range_triplet_a", u32)
        .setComment("No-argument configured classifier. Gate range_both2: same as off_both2 but admission "
            + "own65F2/65F3==5A. Closed gate returns44, otherwise22 iff scratch_u16>54526 selects first event; "
            + "scratch_u16<10224 selects second event; inclusive10224..54526 healthy, else11. Full threshold "
            + "partitions preserved in ROM. No physical units/source identity asserted.");
    semanticFunction(0x412B4L, "f33_record_sample_range_triplet_a_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x412CEL, "f33_record_sample_range_triplet_a_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection uses persistent684A/6852 written only by actually executed range "
            + "predicate.");
    semanticFunction(0x41376L, "f33_step_sample_range_triplet_b", v)
        .setComment("Configured mode020B channelb monitor; 3 eight-byte states at76B4. Own qualification6764 bit1 holds "
            + "state without reset. Gate range_both2 (numeric states, no physical meaning); threshold pass0/fail200 "
            + "with strict crossings. Any confirmed22 retains/replaces shared slot11 with kind(s)0x1c; no confirmed "
            + "source leaves previous action untouched. Callback table284CC; failure "
            + "events0xf5,0xf6,0xf7,0xf8,0xf9,0xfa. See configured-family matrix for readiness sequencing and exact "
            + "predicate.");
    semanticFunction(0x4149EL, "f33_classify_sample_range_triplet_b", u32)
        .setComment("No-argument configured classifier. Gate range_both2: same as off_both2 but admission "
            + "own65F2/65F3==5A. Closed gate returns44, otherwise22 iff same unsigned range10224..54526; "
            + "first/second eventF5..F7/F8..FA, else11. Full threshold partitions preserved in ROM. No physical "
            + "units/source identity asserted.");
    semanticFunction(0x41522L, "f33_record_sample_range_triplet_b_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x4153CL, "f33_record_sample_range_triplet_b_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection uses persistent684A/6852 written only by actually executed range "
            + "predicate.");
    semanticFunction(0x415C0L, "f33_step_startup_status_bit_triplet_a", v)
        .setComment("Configured mode0204 channela monitor; 3 eight-byte states at76D4. Own qualification6764 bit0 holds "
            + "state without reset. Gate baseline_one (numeric states, no physical meaning); threshold "
            + "pass2/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot10 with "
            + "kind(s)0x1d; no confirmed source leaves previous action untouched. Callback table284D8; failure "
            + "events0x54,0x55,0x56. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x4170EL, "f33_classify_startup_status_bit_triplet_a", u32)
        .setComment("No-argument configured classifier. Gate baseline_one: requested==0 && observed==0 && "
            + "bit(6620,b+2)==1 && bit(661C,b+2)==1 && bit(6628,b+1)==0 && bit(6614,0)==1 &&65F0==5A. Closed gate "
            + "returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold partitions preserved in ROM. No "
            + "physical units/source identity asserted.");
    semanticFunction(0x41764L, "f33_record_startup_status_bit_triplet_a_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x41774L, "f33_record_startup_status_bit_triplet_a_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x417F8L, "f33_step_startup_status_bit_triplet_b", v)
        .setComment("Configured mode0204 channelb monitor; 3 eight-byte states at76F0. Own qualification6764 bit1 holds "
            + "state without reset. Gate baseline_one (numeric states, no physical meaning); threshold "
            + "pass2/fail200 with strict crossings. Any confirmed22 retains/replaces shared slot11 with "
            + "kind(s)0x1e; no confirmed source leaves previous action untouched. Callback table284E4; failure "
            + "events0x5a,0x5b,0x5c. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x41946L, "f33_classify_startup_status_bit_triplet_b", u32)
        .setComment("No-argument configured classifier. Gate baseline_one: requested==0 && observed==0 && "
            + "bit(6620,b+2)==1 && bit(661C,b+2)==1 && bit(6628,b+1)==0 && bit(6614,0)==1 &&65F0==5A. Closed gate "
            + "returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold partitions preserved in ROM. No "
            + "physical units/source identity asserted.");
    semanticFunction(0x4199CL, "f33_record_startup_status_bit_triplet_b_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x419ACL, "f33_record_startup_status_bit_triplet_b_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x41A2EL, "f33_step_matched_state2_startup_triplet_a", v)
        .setComment("Configured mode020C channela monitor; 3 eight-byte states at770C. Own qualification6764 bit0 holds "
            + "state without reset. Gate off_both2 (numeric states, no physical meaning); threshold pass2/fail200 "
            + "with strict crossings. Any confirmed22 retains/replaces shared slot10 with kind(s)0x1b,0x32; no "
            + "confirmed source leaves previous action untouched. Callback table284F0; failure "
            + "events0x7f,0x80,0x81. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x41B6AL, "f33_classify_matched_state2_startup_triplet_a", u32)
        .setComment("No-argument configured classifier. Gate off_both2: requested==2 &&observed==2 "
            + "&&(6620&(6<<b))==(4<<b) &&(661C&(6<<b))==(4<<b) &&bit(6628,b+1)==0 &&6614.bit0==0 && "
            + "own65F6/65F7==5A. Closed gate returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold "
            + "partitions preserved in ROM. No physical units/source identity asserted.");
    semanticFunction(0x41BCCL, "f33_record_matched_state2_startup_triplet_a_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x41BDCL, "f33_record_matched_state2_startup_triplet_a_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x41C5EL, "f33_step_matched_state2_startup_triplet_b", v)
        .setComment("Configured mode020C channelb monitor; 3 eight-byte states at7728. Own qualification6764 bit1 holds "
            + "state without reset. Gate off_both2 (numeric states, no physical meaning); threshold pass2/fail200 "
            + "with strict crossings. Any confirmed22 retains/replaces shared slot11 with kind(s)0x1c,0x32; no "
            + "confirmed source leaves previous action untouched. Callback table284FC; failure "
            + "events0x82,0x83,0x84. See configured-family matrix for readiness sequencing and exact predicate.");
    semanticFunction(0x41D9AL, "f33_classify_matched_state2_startup_triplet_b", u32)
        .setComment("No-argument configured classifier. Gate off_both2: requested==2 &&observed==2 "
            + "&&(6620&(6<<b))==(4<<b) &&(661C&(6<<b))==(4<<b) &&bit(6628,b+1)==0 &&6614.bit0==0 && "
            + "own65F6/65F7==5A. Closed gate returns44, otherwise22 iff scratch_byte==5A, else11. Full threshold "
            + "partitions preserved in ROM. No physical units/source identity asserted.");
    semanticFunction(0x41E00L, "f33_record_matched_state2_startup_triplet_b_healthy_observed", v)
        .setComment("Set healthy-observed6120 bit via51E2C; does not clear current/retained diagnostic failure. Event "
            + "selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x41E10L, "f33_record_matched_state2_startup_triplet_b_failure", v)
        .setComment("Call51C66(event,32 hex); diagnostic lifecycle rejection is separate from later control-action "
            + "publication. Event selection is mutable source scratch before each engine invocation.");
    semanticFunction(0x6A6ACL, "f33_reset_terminal_monitor", v,
        new ParameterImpl("state", F33TerminalMonitorStatePointer, currentProgram))
        .setComment("statusFF; pass/fail/highwater0; padding byte1 untouched. Eight-byte "
            + "layout:status0,padding1,pass2,fail4,highwater6.");
    semanticFunction(0x6A6BAL, "f33_step_terminal_monitor", u32,
        new ParameterImpl("state", F33TerminalMonitorStatePointer, currentProgram),
        new ParameterImpl("thresholds", F33MonitorLimitsPointer, currentProgram),
        new ParameterImpl("callbacks", F33TerminalMonitorCallbacksPointer, currentProgram))
        .setComment("Inputs r6 state*,r7 two uint16 thresholds*,r8 three-pointer callback table*. Test fail>threshold "
            + "first => status22 with no predicate or callback. Else pass>threshold => status0 with no predicate or "
            + "callback. Else call table[0].11 clears fail and increments pass; crossing strict pass>threshold "
            + "sets0 and calls table[1] once.22 clears pass and increments fail, updates highwater max; crossing "
            + "fail>threshold sets22 and calls table[2] once.44 or any other classification storesFF and preserves "
            + "all counters/highwater. Result r10 always11, not stored status. No automatic recovery from either "
            + "terminal state before explicit reset.");
    semanticFunction(0x6A744L, "f33_force_unconfirmed_terminal_monitor_healthy", u32,
        new ParameterImpl("state", F33TerminalMonitorStatePointer, currentProgram),
        new ParameterImpl("thresholds", F33MonitorLimitsPointer, currentProgram),
        new ParameterImpl("callbacks", F33TerminalMonitorCallbacksPointer, currentProgram))
        .setComment("Only when BOTH fail<=threshold and pass<=threshold, write status0, call table[1] if nonnull, set "
            + "fail0/pass=passThreshold+1. Does not change highwater. Already terminal healthy OR failed state "
            + "untouched. Therefore policy byte5A cannot heal confirmed failure. Callbacks use existing scratch "
            + "selection; wrappers do not refresh it in forced path.");
    semanticFunction(0x3EF1CL, "f33_publish_configured_monitor_failure_count_summary", v)
        .setComment("3EFD4\u21923EF1C evaluates27 per-root getters of FAIL COUNTS at state+4 (not status), then530FC(9,11) if "
            + "any fail count nonzero. A first failing observation makes this summary11 before status22 "
            + "confirmation. UnknownFF with zero failure count does not. Inadmissible44 preserves nonzero fail "
            + "counts and therefore summary; explicit reset clears them.");
    semanticFunction(0x3E5D2L, "f33_admit_delayed_status_bit_triplet_a", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x3E86AL, "f33_admit_delayed_status_bit_triplet_b", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x3F0C8L, "f33_admit_coupled_sample_monitor", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x3F396L, "f33_admit_command_status_monitor_a", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x3F5ACL, "f33_admit_command_status_monitor_b", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x3F71CL, "f33_admit_bounded_sample_monitor_a", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x3F8A8L, "f33_admit_bounded_sample_monitor_b", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x3FA80L, "f33_admit_requested_state_sample_monitor_a", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x3FC5AL, "f33_admit_requested_state_sample_monitor_b", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x4005EL, "f33_admit_sample_difference_monitor_a", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x400A8L, "f33_admit_sample_difference_elapsed_a", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x4023EL, "f33_admit_sample_difference_monitor_b", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x40288L, "f33_admit_sample_difference_elapsed_b", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x404BCL, "f33_admit_matched_state2_status_monitor_a", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x406F8L, "f33_admit_matched_state2_status_monitor_b", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x40896L, "f33_admit_baseline_sample_monitor_a", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x40A0EL, "f33_admit_baseline_sample_monitor_b", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x40C38L, "f33_admit_observed_state_sample_monitor_a", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x40ED2L, "f33_admit_observed_state_sample_monitor_b", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x410E4L, "f33_admit_sample_range_triplet_a", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticFunction(0x4134EL, "f33_admit_sample_range_triplet_b", u32)
        .setComment("Return readiness latch in r10:5A means admitted, not a void side-effect-only helper. Retain "
            + "completed latch until explicit stage initializer; pending sequencing and counts per "
            + "configured-family readiness contract. No hardware success is inferred from this software latch.");
    semanticData(0xFEBE759CL, new ArrayDataType(terminalMonitorStateType, 3, terminalMonitorStateType.getLength()), "f33_delayed_status_bit_triplet_a_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B66AL, monitorLimitsType, "f33_delayed_status_bit_triplet_a_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x283C4L, terminalMonitorCallbacksType, "f33_delayed_status_bit_triplet_a_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE75B8L, new ArrayDataType(terminalMonitorStateType, 3, terminalMonitorStateType.getLength()), "f33_delayed_status_bit_triplet_b_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B66EL, monitorLimitsType, "f33_delayed_status_bit_triplet_b_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x283D0L, terminalMonitorCallbacksType, "f33_delayed_status_bit_triplet_b_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE75D4L, new ArrayDataType(terminalMonitorStateType, 3, terminalMonitorStateType.getLength()), "f33_matched_state2_status_bit_triplet_a_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B672L, monitorLimitsType, "f33_matched_state2_status_bit_triplet_a_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x283DCL, terminalMonitorCallbacksType, "f33_matched_state2_status_bit_triplet_a_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE75F0L, new ArrayDataType(terminalMonitorStateType, 3, terminalMonitorStateType.getLength()), "f33_matched_state2_status_bit_triplet_b_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B676L, monitorLimitsType, "f33_matched_state2_status_bit_triplet_b_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x283E8L, terminalMonitorCallbacksType, "f33_matched_state2_status_bit_triplet_b_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE760CL, terminalMonitorStateType, "f33_coupled_sample_threshold_both_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B67AL, monitorLimitsType, "f33_coupled_sample_threshold_both_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x283F4L, terminalMonitorCallbacksType, "f33_coupled_sample_threshold_both_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE7614L, terminalMonitorStateType, "f33_command_status_bit_clear_a_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B67EL, monitorLimitsType, "f33_command_status_bit_clear_a_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x28400L, terminalMonitorCallbacksType, "f33_command_status_bit_clear_a_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE761CL, terminalMonitorStateType, "f33_command_status_bit_clear_b_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B682L, monitorLimitsType, "f33_command_status_bit_clear_b_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x2840CL, terminalMonitorCallbacksType, "f33_command_status_bit_clear_b_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE7624L, terminalMonitorStateType, "f33_bounded_sample_or_status_a_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B686L, monitorLimitsType, "f33_bounded_sample_or_status_a_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x28418L, terminalMonitorCallbacksType, "f33_bounded_sample_or_status_a_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE762CL, terminalMonitorStateType, "f33_bounded_sample_or_status_b_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B68AL, monitorLimitsType, "f33_bounded_sample_or_status_b_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x28424L, terminalMonitorCallbacksType, "f33_bounded_sample_or_status_b_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE7634L, terminalMonitorStateType, "f33_requested_state_sample_threshold_a_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B68EL, monitorLimitsType, "f33_requested_state_sample_threshold_a_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x28430L, terminalMonitorCallbacksType, "f33_requested_state_sample_threshold_a_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE7644L, terminalMonitorStateType, "f33_requested_state_sample_threshold_b_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B692L, monitorLimitsType, "f33_requested_state_sample_threshold_b_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x2843CL, terminalMonitorCallbacksType, "f33_requested_state_sample_threshold_b_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE67F0L, terminalMonitorStateType, "f33_asserted_state_sample_threshold_a_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B696L, monitorLimitsType, "f33_asserted_state_sample_threshold_a_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x28448L, terminalMonitorCallbacksType, "f33_asserted_state_sample_threshold_a_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE67F8L, terminalMonitorStateType, "f33_asserted_state_sample_threshold_b_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B69AL, monitorLimitsType, "f33_asserted_state_sample_threshold_b_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x28454L, terminalMonitorCallbacksType, "f33_asserted_state_sample_threshold_b_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE7654L, terminalMonitorStateType, "f33_sample_difference_window_a_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B69EL, monitorLimitsType, "f33_sample_difference_window_a_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x28460L, terminalMonitorCallbacksType, "f33_sample_difference_window_a_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE765CL, terminalMonitorStateType, "f33_sample_difference_window_b_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B6A2L, monitorLimitsType, "f33_sample_difference_window_b_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x2846CL, terminalMonitorCallbacksType, "f33_sample_difference_window_b_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE7664L, terminalMonitorStateType, "f33_matched_state2_status_bit_a_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B6A6L, monitorLimitsType, "f33_matched_state2_status_bit_a_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x28478L, terminalMonitorCallbacksType, "f33_matched_state2_status_bit_a_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE766CL, terminalMonitorStateType, "f33_matched_state2_status_bit_b_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B6AAL, monitorLimitsType, "f33_matched_state2_status_bit_b_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x28484L, terminalMonitorCallbacksType, "f33_matched_state2_status_bit_b_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE7674L, terminalMonitorStateType, "f33_baseline_sample_threshold_a_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B6AEL, monitorLimitsType, "f33_baseline_sample_threshold_a_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x28490L, terminalMonitorCallbacksType, "f33_baseline_sample_threshold_a_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE767CL, terminalMonitorStateType, "f33_baseline_sample_threshold_b_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B6B2L, monitorLimitsType, "f33_baseline_sample_threshold_b_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x2849CL, terminalMonitorCallbacksType, "f33_baseline_sample_threshold_b_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE7684L, terminalMonitorStateType, "f33_observed_state_sample_regions_a_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B6B6L, monitorLimitsType, "f33_observed_state_sample_regions_a_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x284A8L, terminalMonitorCallbacksType, "f33_observed_state_sample_regions_a_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE768CL, terminalMonitorStateType, "f33_observed_state_sample_regions_b_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B6BAL, monitorLimitsType, "f33_observed_state_sample_regions_b_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x284B4L, terminalMonitorCallbacksType, "f33_observed_state_sample_regions_b_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE7694L, new ArrayDataType(terminalMonitorStateType, 3, terminalMonitorStateType.getLength()), "f33_sample_range_triplet_a_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B6BEL, monitorLimitsType, "f33_sample_range_triplet_a_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x284C0L, terminalMonitorCallbacksType, "f33_sample_range_triplet_a_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE76B4L, new ArrayDataType(terminalMonitorStateType, 3, terminalMonitorStateType.getLength()), "f33_sample_range_triplet_b_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B6C2L, monitorLimitsType, "f33_sample_range_triplet_b_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x284CCL, terminalMonitorCallbacksType, "f33_sample_range_triplet_b_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE76D4L, new ArrayDataType(terminalMonitorStateType, 3, terminalMonitorStateType.getLength()), "f33_startup_status_bit_triplet_a_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B6C6L, monitorLimitsType, "f33_startup_status_bit_triplet_a_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x284D8L, terminalMonitorCallbacksType, "f33_startup_status_bit_triplet_a_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE76F0L, new ArrayDataType(terminalMonitorStateType, 3, terminalMonitorStateType.getLength()), "f33_startup_status_bit_triplet_b_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B6CAL, monitorLimitsType, "f33_startup_status_bit_triplet_b_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x284E4L, terminalMonitorCallbacksType, "f33_startup_status_bit_triplet_b_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE770CL, new ArrayDataType(terminalMonitorStateType, 3, terminalMonitorStateType.getLength()), "f33_matched_state2_startup_triplet_a_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B6CEL, monitorLimitsType, "f33_matched_state2_startup_triplet_a_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x284F0L, terminalMonitorCallbacksType, "f33_matched_state2_startup_triplet_a_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
    semanticData(0xFEBE7728L, new ArrayDataType(terminalMonitorStateType, 3, terminalMonitorStateType.getLength()), "f33_matched_state2_startup_triplet_b_states",
        "Eight-byte terminal states; padding is not cleared; each stage has mutable predicate selectors.");
    semanticData(0x2B6D2L, monitorLimitsType, "f33_matched_state2_startup_triplet_b_limits",
        "Strict passing/failing > thresholds; counts are observations, not measured elapsed time.");
    semanticData(0x284FCL, terminalMonitorCallbacksType, "f33_matched_state2_startup_triplet_b_callbacks",
        "Predicate and terminal-transition reporters; healthy-observed notification does not itself clear current diagnostic history.");
  }
  private void annotateScalarMonitorComposition() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType latchedMonitorStateType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33LatchedMonitorState");
    DataType F33LatchedMonitorStatePointer = new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33LatchedMonitorState"), 4);
    DataType monitorLimitsType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33MonitorLimits");
    DataType F33MonitorLimitsPointer = new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33MonitorLimits"), 4);
    DataType F33MonitorRecoveryScratchPointer = new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33MonitorRecoveryScratch"), 4);
    DataType recoverableMonitorCallbacksType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33RecoverableMonitorCallbacks");
    DataType F33RecoverableMonitorCallbacksPointer = new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33RecoverableMonitorCallbacks"), 4);
    DataType recoverableMonitorLimitsType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33RecoverableMonitorLimits");
    DataType F33RecoverableMonitorLimitsPointer = new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33RecoverableMonitorLimits"), 4);
    DataType recoverableMonitorStateType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33RecoverableMonitorState");
    DataType F33RecoverableMonitorStatePointer = new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33RecoverableMonitorState"), 4);
    DataType twoSidedMonitorCallbacksType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33TwoSidedMonitorCallbacks");
    DataType F33TwoSidedMonitorCallbacksPointer = new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33TwoSidedMonitorCallbacks"), 4);
    DataType windowedMonitorLimitsType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33WindowedMonitorLimits");
    DataType F33WindowedMonitorLimitsPointer = new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33WindowedMonitorLimits"), 4);
    DataType windowedMonitorStateType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33WindowedMonitorState");
    DataType F33WindowedMonitorStatePointer = new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33WindowedMonitorState"), 4);
    DataType ushortPointer = new PointerDataType(u16, 4);
    semanticFunction(0x45356L, "f33_step_local_output_status_a_monitor", v)
        .setComment("State7B50 -> slot7 index1. Qualification6764.bit0 holds confirmed state via6AE18; otherwise "
            + "predicate requires6624.bit0 and65F6=5A, then8284=5A fails. Limits200/200; event8E. Policy2BC54=0 in "
            + "this image.");
    semanticFunction(0x45410L, "f33_step_local_channel_mismatch_a_monitor", v)
        .setComment("State7B5C -> slot7 index0. Requires qualification bit0 clear andE820=5A; predicate "
            + "requires64DC.bit1/64D4.bit1 clear and65F6=5A, then8282=5A fails. Limits16/16; event77. Disabled gate "
            + "preserves confirmed state.");
    semanticFunction(0x45572L, "f33_step_local_output_status_b_monitor", v)
        .setComment("State7B6C -> slot8 index1. Qualification6764.bit1 holds confirmed state; predicate requires6624.bit1 "
            + "and65F7=5A, then8283=5A fails. Limits200/200; event8F.");
    semanticFunction(0x4562AL, "f33_step_local_channel_mismatch_b_monitor", v)
        .setComment("State7B78 -> slot8 index0. Requires qualification bit1 clear andE820=5A; predicate "
            + "requires64DC.bit17/64D4.bit17 clear and65F7=5A, then8281=5A fails. Limits16/16; event73.");
    semanticFunction(0x456FAL, "f33_step_admitted_scalar_receive_condition_monitor", v)
        .setComment("State7B84 -> slot6 index3. E820 admits recoverable qualifier with limits25/125/25. Reset/disabled "
            + "gate also clears admission count6868. Predicate relates E822/E823, receive803C/803E and "
            + "unsigned66B8; eventA5.");
    semanticFunction(0x45838L, "f33_step_paired_scalar_relation_monitor", v)
        .setComment("State7B90 -> slot6 index0. Requires qualification bits0/1 clear andE820=5A, otherwise retain "
            + "confirmed state. Relation predicate uses unsigned66B8 against66AE/66B0 plus source-status gates. "
            + "Recoverable limits125/125/25; eventA2.");
    semanticFunction(0x4599CL, "f33_step_qualified_scalar_relation_a_monitor", v)
        .setComment("State7B9C -> slot6 index1. Only qualification bit1 SET andE820=5A runs qualifier. Otherwise report "
            + "healthy-observed9E without clearing retained monitor state, then publish its low status byte. "
            + "Limits0/125; confirmed failure is latched until explicit reset.");
    semanticFunction(0x45A6CL, "f33_step_qualified_scalar_relation_b_monitor", v)
        .setComment("State7BA8 -> slot6 index2. Only qualification bit0 SET andE820=5A runs qualifier. Otherwise "
            + "healthy-observed9F leaves retained state unchanged. Limits0/125; raw source66B0 replaces66AE.");
    semanticFunction(0x45E74L, "f33_step_raw_thermistor_range_a_monitor", v)
        .setComment("State7BDC -> slot18 index0. Qualification bit0 clear admits recoverable qualifier; otherwise retain "
            + "confirmed state. Raw unsigned6492 range1206..65231 inclusive. Pass/fail/recovery limits25/25/25; "
            + "event88.");
    semanticFunction(0x45F32L, "f33_step_raw_thermistor_range_b_monitor", v)
        .setComment("State7BE8 -> slot18 index1. Qualification bit1 clear admits recoverable qualifier. Raw unsigned6498 "
            + "range1206..65231 inclusive; same25/25/25 limits; event85.");
    semanticFunction(0x3BAB2L, "f33_step_acquisition_status_a_monitor", v)
        .setComment("State70C8 -> slot20 index0. Predicate81D0=5A fails. Windowed qualifier limits pass2/windowFFFF and "
            + "fail3/window6; confirmed failure latches. EventD3; published status is low result byte.");
    semanticFunction(0x3BB44L, "f33_step_acquisition_status_b_monitor", v)
        .setComment("State70D8 -> slot20 index1. Predicate81D1=5A fails. Same windowed2/FFFF/3/6 limits; eventD4. Status "
            + "flags are staged from380A/B through66932 and50A06, not physical timing proof.");
    semanticFunction(0x3BC4CL, "f33_step_acquisition_range_a_monitor", v)
        .setComment("State70EC -> slot20 index2. Predicate requires81D4=5A, then unsigned81D6>=61211 and81D8<=3093. "
            + "Latched limits2/20; eventD6. Do not reinterpret these two separate unsigned bounds as a signed "
            + "interval.");
    semanticFunction(0x3BCFCL, "f33_step_acquisition_range_b_monitor", v)
        .setComment("State70F8 -> slot20 index3. Valid81D5 gates unsigned81DA>=61211 and81DC<=3093. Latched limits2/20; "
            + "eventD7.");
    semanticFunction(0x45324L, "f33_publish_local_channel_a_monitor_status", v,
        new ParameterImpl("index", u8, currentProgram),
        new ParameterImpl("packed_status", u32, currentProgram))
        .setComment("If low8(index)<2, store low8(packed_status) to FEBE7B4C+index. Other bits of the packed qualifier "
            + "result are not published.");
    semanticFunction(0x45540L, "f33_publish_local_channel_b_monitor_status", v,
        new ParameterImpl("index", u8, currentProgram),
        new ParameterImpl("packed_status", u32, currentProgram))
        .setComment("If low8(index)<2, store low8(packed_status) to FEBE7B68+index. Other bits of the packed qualifier "
            + "result are not published.");
    semanticFunction(0x45B9EL, "f33_publish_scalar_relation_monitor_status", v,
        new ParameterImpl("index", u8, currentProgram),
        new ParameterImpl("packed_status", u32, currentProgram))
        .setComment("If low8(index)<4, store low8(packed_status) to FEBE7BB4+index. Other bits of the packed qualifier "
            + "result are not published.");
    semanticFunction(0x46058L, "f33_publish_thermistor_range_monitor_status", v,
        new ParameterImpl("index", u8, currentProgram),
        new ParameterImpl("packed_status", u32, currentProgram))
        .setComment("If low8(index)<2, store low8(packed_status) to FEBE7BF4+index. Other bits of the packed qualifier "
            + "result are not published.");
    semanticFunction(0x3BC1AL, "f33_publish_acquisition_monitor_status", v,
        new ParameterImpl("index", u8, currentProgram),
        new ParameterImpl("packed_status", u32, currentProgram))
        .setComment("If low8(index)<4, store low8(packed_status) to FEBE70E8+index. Other bits of the packed qualifier "
            + "result are not published.");
    semanticFunction(0x4539EL, "f33_classify_local_output_status_a", u32)
        .setComment("6624.bit0 and65F6=5A admit;8284=5A returns22,otherwise11; inadmissible44.8284 is staged "
            + "local383A.bit3.");
    semanticFunction(0x4546AL, "f33_classify_local_channel_mismatch_a", u32)
        .setComment("64DC.bit1/64D4.bit1 clear and65F6=5A admit;8282=5A fails22 else11; inadmissible44.8282 is "
            + "local383A.bit9.");
    semanticFunction(0x455BAL, "f33_classify_local_output_status_b", u32)
        .setComment("6624.bit1 and65F7=5A admit;8283=5A fails22 else11; inadmissible44.8283 is local383A.bit2.");
    semanticFunction(0x45684L, "f33_classify_local_channel_mismatch_b", u32)
        .setComment("64DC.bit17/64D4.bit17 clear and65F7=5A admit;8281=5A fails22 else11; inadmissible44.8281 is "
            + "local383A.bit8.");
    semanticFunction(0x4574CL, "f33_classify_admitted_scalar_receive_condition", u32)
        .setComment("With E822=5A/E823=0, increment6868 until entry count11. Thereafter803C=1 and803E=0 fails22. "
            + "Strict2304<66B8<4096 returns11; outside gives33 after admitted delay,44 before it. Inactive gate "
            + "resets6868. Inputs and comparisons are unsigned.");
    semanticFunction(0x457BEL, "f33_classify_scalar_receive_recovery", u32)
        .setComment("Strict2304<66B8<4096 returns11; endpoints and outside return22. Recovery count is separate from "
            + "admission6868.");
    semanticFunction(0x45894L, "f33_classify_paired_scalar_relation", u32)
        .setComment("Any6751/52 or65C2/3/4/5 nonzero returns44. Otherwise66B8>4736 and either66AE/66B0<=4096 "
            + "returns22;66B8<=4736 and either peer<=4096 returns11; other combinations33. All raw values unsigned.");
    semanticFunction(0x45900L, "f33_classify_paired_scalar_recovery", u32)
        .setComment("Same six source-status gates; then inclusive768<=66B8<=4096 returns11,otherwise22. This is not the "
            + "entry predicate range.");
    semanticFunction(0x459F6L, "f33_classify_qualified_scalar_relation_a", u32)
        .setComment("6751 or65C2/4/5 nonzero returns44; otherwise unsigned66B8>4736 and66AE<=4096 returns22,else11.");
    semanticFunction(0x45AC6L, "f33_classify_qualified_scalar_relation_b", u32)
        .setComment("6752 or65C3/4/5 nonzero returns44; otherwise unsigned66B8>4736 and66B0<=4096 returns22,else11.");
    semanticFunction(0x45EBCL, "f33_classify_raw_thermistor_range_a", u32)
        .setComment("Unsigned6492 inside inclusive1206..65231 returns11,otherwise22. LD.HU and unsigned branches prove "
            + "raw-domain bounds, not signed temperatures.");
    semanticFunction(0x45F7AL, "f33_classify_raw_thermistor_range_b", u32)
        .setComment("Unsigned6498 inside inclusive1206..65231 returns11,otherwise22. Same predicate used for entry and "
            + "recovery.");
    semanticFunction(0x3BAECL, "f33_classify_acquisition_status_a", u32)
        .setComment("81D0=5A returns22; any other byte returns11. Full R10 is defined.");
    semanticFunction(0x3BB7EL, "f33_classify_acquisition_status_b", u32)
        .setComment("81D1=5A returns22; any other byte returns11. Full R10 is defined.");
    semanticFunction(0x3BC86L, "f33_classify_acquisition_range_a", u32)
        .setComment("81D4!=5A returns44. Otherwise unsigned81D6>=61211 AND81D8<=3093 returns11,else22. Separate lower and "
            + "upper samples, not a signed scalar range.");
    semanticFunction(0x3BD36L, "f33_classify_acquisition_range_b", u32)
        .setComment("81D5!=5A returns44. Otherwise unsigned81DA>=61211 AND81DC<=3093 returns11,else22.");
    semanticFunction(0x452A8L, "f33_publish_local_channel_monitor_actions_a", v)
        .setComment("Always retain/clear slot7, then low-byte confirmed mask22 at7B4D adds kind1B and7B4C adds1D; select "
            + "current. Any nonzero status sets diagnostic-cache blocker6=11; combined pending mask11 "
            + "sets817D[4]=5A, otherwise0. Pending and confirmed consumers differ.");
    semanticFunction(0x454C4L, "f33_publish_local_channel_monitor_actions_b", v)
        .setComment("Rebuild slot8 from7B69 kind1C and7B68 kind1E. Any nonzero sets blocker7=11; pending mask11 "
            + "sets817D[5]=5A. Current selected even when no action remains.");
    semanticFunction(0x45B20L, "f33_publish_scalar_relation_monitor_actions", v)
        .setComment("Always rebuild slot6; OR7BB4..7BB7 with mask22 selects kind16.7BB8 is any nonzero status;7BB9/7BBA "
            + "are confirmed indices0/3 respectively. General blocking is not the same as either endpoint-specific "
            + "flag.");
    semanticFunction(0x45FD4L, "f33_publish_thermistor_range_monitor_actions", v)
        .setComment("Rebuild slot18 with kind16 when either7BF4/5 has confirmed mask22. Publish packed per-channel status "
            + "at7BF8 with pending11 precedence over22 within each byte; always set publication marker7BF6=5A.");
    semanticFunction(0x3BBBAL, "f33_publish_acquisition_monitor_actions", v)
        .setComment("Always retain/clear slot20; any confirmed mask22 among70E8..EB selects kind31,then select current. "
            + "Any nonzero source status sets diagnostic-cache blocker1=11. Unlike shared startup-stage producers, "
            + "an all-clear invocation replaces current with zero.");
    semanticFunction(0x45CCEL, "f33_clear_reserved_monitor_action_slot", v)
        .setComment("Retain/clear slot21, select its empty current record, clear diagnostic-cache blocker10. No monitor "
            + "predicate or fault action is produced here.");
    semanticFunction(0xB3C6CL, "f33_publish_health_coherence_fault_actions", v)
        .setComment("Rebuild slot19 with kind16 unless B218/B21C bothA55A5AA5,B20E!=33,B215=0,B252=44,B253=0. Select "
            + "current even when clear. This checks staged health/coherence fields; no new diagnostic event is "
            + "reported here.");
    semanticFunction(0x33EE6L, "f33_publish_application_record_path_fault", v)
        .setComment("Report event52/capture-kind50,then independently retain/clear slot17,encodekind1,select current. "
            + "Called on terminal failure in33F14; diagnostic reporting inhibition does not veto the control "
            + "action.");
    semanticFunction(0x3588AL, "f33_step_learned_quad_record_completion", v)
        .setComment("After357C0, decrement nonzero6AE4. Valid source66D5=5A and marker6AF0=A55A5AA5 invoke learned-quad "
            + "restoration; failed restoration reports128 and sets6AE1=5A. Pending write/reset6ADD/6ADC poll "
            + "record100: exact10 succeeds,high-nibble20 waits,other status reports130 and publishes slot17/kind1. "
            + "Write success restores valid marker and passes0E; reset success clears marker and reports0E "
            + "through51D38. Publication and physical persistence remain distinct.");
    semanticFunction(0x530FCL, "f33_set_diagnostic_cache_blocker", v,
        new ParameterImpl("index", u8, currentProgram),
        new ParameterImpl("status", u8, currentProgram))
        .setComment("Store low8(status) at615B+low8(index) only for index<11. Independent families feed healthy-cache "
            + "refresh admission; a pending monitor may block without confirmed actions.");
    semanticFunction(0x4C794L, "f33_set_monitor_pending_projection", v,
        new ParameterImpl("index", u8, currentProgram),
        new ParameterImpl("status", u8, currentProgram))
        .setComment("Store low8(status) at817D+low8(index) only for index<10. Does not itself report a diagnostic event "
            + "or select a fault-action record.");
    semanticFunction(0x51E2CL, "f33_report_diagnostic_healthy_observed", v,
        new ParameterImpl("event", u32, currentProgram))
        .setComment("For low16(event)1..17F, call52A2A to mark the independent6120 bitmap. No diagnostic lifecycle gate "
            + "and no ordinary-pass clearing of6090/60C0/60F0.");
    semanticFunction(0x52A2AL, "f33_mark_diagnostic_healthy_observed", v,
        new ParameterImpl("event", u32, currentProgram))
        .setComment("For event1..17F, set its6120 bitmap bit only when absent, under saved/restored PMRFF00. Current and "
            + "retained failure histories are untouched.");
    semanticFunction(0x5D6DCL, "f33_snapshot_monitor_inputs", v)
        .setComment("Sequentially snapshot acquisition channels820C..8228, output/channel request state, conditioned "
            + "scalars7DA4..7DB6, monitor statuses, live qualification71EC/limit71F2, scalar availability7BBC..7BC3 "
            + "and application-record fields.66B8<-7DB0;66AE/B0<-7DA6/A8;6492/98<-821E/24. No local critical "
            + "section makes the entire snapshot atomic.");
    semanticFunction(0x50C9AL, "f33_snapshot_local_status_link_flags", v)
        .setComment("Publish62CD4 result at8294; expand cached local3838/383A/383C bits into8278..8292 and "
            + "packed8298,clear829C. In particular8284/8282/8283/8281 reflect383A bits3/9/2/8. These are software "
            + "cached status-link fields, not CAN wire joins or independent freshness proof.");
    semanticFunction(0x50A06L, "f33_snapshot_acquisition_status_flags", v)
        .setComment("Copy5F26/5F27 to81D0/81D1. Their producer66932 copies cached380A/380B; no physical error identity is "
            + "inferred.");
    semanticFunction(0x50A1CL, "f33_snapshot_acquisition_range_fields", v)
        .setComment("Copy5EEA/C/E/5EF0 to81D6/8/A/C; publish valid markers81D4/5 as5F26/27 XOR5A. Only source byte0 "
            + "produces the exact5A marker admitted by range predicates.");
    semanticFunction(0x66932L, "f33_publish_acquisition_diagnostic_snapshot", v)
        .setComment("Compose transfer-group copies62ABC,62B18,6294E into5EE0..5F24, and copy cached380A/B to5F26/27. The "
            + "range fields5EEA/C/E/5EF0 and later81D6/8/A/C are staged generations, not an atomic physical "
            + "measurement.");
    semanticFunction(0x62ABCL, "f33_copy_acquisition_diagnostic_samples", v,
        new ParameterImpl("destination", ushortPointer, currentProgram))
        .setComment("Copy four halfwords through62A50 then five through62A86 into the same destination; retain the "
            + "original destination across the first call. Firmware transfer groups6/14 are structural indices.");
    semanticFunction(0x62A50L, "f33_copy_transfer_group6_samples", v,
        new ParameterImpl("destination", ushortPointer, currentProgram))
        .setComment("Write four destination halfwords using group6 count/base plus four ROM30F20 byte indices and60630 "
            + "getter. No physical channel identity or freshness is added.");
    semanticFunction(0x62A86L, "f33_copy_transfer_group14_samples", v,
        new ParameterImpl("destination", ushortPointer, currentProgram))
        .setComment("Write five halfwords at destination+8 using group14 count/base plus ROM30F44 indices and606DA "
            + "getter. The first four halfwords are preserved.");
    semanticFunction(0x45BC8L, "f33_publish_primary_scalar_availability", v)
        .setComment("Unsigned7DB0>=2125 sets7BBC=5A; inclusive2125..4736 sets7BBD=5A. Below lower bound clears both; "
            + "above upper retains7BBC but clears7BBD.");
    semanticFunction(0x45BF4L, "f33_publish_channel_scalar_availability_a", v)
        .setComment("Unsigned7DA6>=1818 sets7BC0=5A;>=2125 additionally7BBE=5A. No upper bound in this helper.");
    semanticFunction(0x45C20L, "f33_publish_channel_scalar_availability_b", v)
        .setComment("Unsigned7DA8>=1818 sets7BC1=5A;>=2125 additionally7BBF=5A. No upper bound in this helper.");
    semanticFunction(0x45C4CL, "f33_publish_paired_scalar_availability", v)
        .setComment("7BC2/3=5A if primary7DB0 OR respective7DA6/7DA8 is inside inclusive2125..4736. EB85 selects "
            + "alternate ROM lower-bound entries, but both equal2125 in this exact image. Later5D6DC "
            + "publishes65F6/7.");
    semanticFunction(0x45CB2L, "f33_update_scalar_availability", v)
        .setComment("Run primary,channelA,channelB andpaired availability publishers in that order. Their destination "
            + "bank7BBC..7BC3 is distinct from the later65F0..65F7 snapshot.");
    semanticFunction(0x3BB02L, "f33_report_scalar_event_d3_healthy_observed", v)
        .setComment("Report eventD3 through51E2C/52A2A healthy-observed bitmap; does not clear current failure history.");
    semanticFunction(0x3BB12L, "f33_report_scalar_event_d3_failure", v)
        .setComment("Report eventD3 with capture kind10; diagnostic admission remains in51C66.");
    semanticFunction(0x3BB94L, "f33_report_scalar_event_d4_healthy_observed", v)
        .setComment("Report eventD4 through51E2C/52A2A healthy-observed bitmap; does not clear current failure history.");
    semanticFunction(0x3BBA4L, "f33_report_scalar_event_d4_failure", v)
        .setComment("Report eventD4 with capture kind10; diagnostic admission remains in51C66.");
    semanticFunction(0x3BCBAL, "f33_report_scalar_event_d6_healthy_observed", v)
        .setComment("Report eventD6 through51E2C/52A2A healthy-observed bitmap; does not clear current failure history.");
    semanticFunction(0x3BCCAL, "f33_report_scalar_event_d6_failure", v)
        .setComment("Report eventD6 with capture kind10; diagnostic admission remains in51C66.");
    semanticFunction(0x3BD6AL, "f33_report_scalar_event_d7_healthy_observed", v)
        .setComment("Report eventD7 through51E2C/52A2A healthy-observed bitmap; does not clear current failure history.");
    semanticFunction(0x3BD7AL, "f33_report_scalar_event_d7_failure", v)
        .setComment("Report eventD7 with capture kind10; diagnostic admission remains in51C66.");
    semanticFunction(0x453CCL, "f33_report_scalar_event_8e_healthy_observed", v)
        .setComment("Report event8E through51E2C/52A2A healthy-observed bitmap; does not clear current failure history.");
    semanticFunction(0x453DCL, "f33_report_scalar_event_8e_failure", v)
        .setComment("Report event8E with capture kind50; diagnostic admission remains in51C66.");
    semanticFunction(0x4549CL, "f33_report_scalar_event_77_healthy_observed", v)
        .setComment("Report event77 through51E2C/52A2A healthy-observed bitmap; does not clear current failure history.");
    semanticFunction(0x454ACL, "f33_report_scalar_event_77_failure", v)
        .setComment("Report event77 with capture kind50; diagnostic admission remains in51C66.");
    semanticFunction(0x455E6L, "f33_report_scalar_event_8f_healthy_observed", v)
        .setComment("Report event8F through51E2C/52A2A healthy-observed bitmap; does not clear current failure history.");
    semanticFunction(0x455F6L, "f33_report_scalar_event_8f_failure", v)
        .setComment("Report event8F with capture kind50; diagnostic admission remains in51C66.");
    semanticFunction(0x456B6L, "f33_report_scalar_event_73_healthy_observed", v)
        .setComment("Report event73 through51E2C/52A2A healthy-observed bitmap; does not clear current failure history.");
    semanticFunction(0x456C6L, "f33_report_scalar_event_73_failure", v)
        .setComment("Report event73 with capture kind50; diagnostic admission remains in51C66.");
    semanticFunction(0x457E0L, "f33_report_scalar_event_a5_healthy_observed", v)
        .setComment("Report eventA5 through51E2C/52A2A healthy-observed bitmap; does not clear current failure history.");
    semanticFunction(0x457F0L, "f33_report_scalar_event_a5_failure", v)
        .setComment("Clear admission counter6868 before reporting eventA5 with capture kind400; diagnostic rejection does "
            + "not undo that clear.");
    semanticFunction(0x45808L, "f33_report_scalar_event_a5_pass", v)
        .setComment("Report eventA5 through51D5E ordinary pass; current failure clears while normal retained histories "
            + "survive.");
    semanticFunction(0x45948L, "f33_report_scalar_event_a2_healthy_observed", v)
        .setComment("Report eventA2 through51E2C/52A2A healthy-observed bitmap; does not clear current failure history.");
    semanticFunction(0x45958L, "f33_report_scalar_event_a2_failure", v)
        .setComment("Report eventA2 with capture kind400; diagnostic admission remains in51C66.");
    semanticFunction(0x4596CL, "f33_report_scalar_event_a2_pass", v)
        .setComment("Report eventA2 through51D5E ordinary pass; current failure clears while normal retained histories "
            + "survive.");
    semanticFunction(0x45A38L, "f33_report_scalar_event_9e_failure", v)
        .setComment("Report event9E with capture kind400; diagnostic admission remains in51C66.");
    semanticFunction(0x45B08L, "f33_report_scalar_event_9f_failure", v)
        .setComment("Report event9F with capture kind400; diagnostic admission remains in51C66.");
    semanticFunction(0x45EDEL, "f33_report_scalar_event_88_healthy_observed", v)
        .setComment("Report event88 through51E2C/52A2A healthy-observed bitmap; does not clear current failure history.");
    semanticFunction(0x45EEEL, "f33_report_scalar_event_88_failure", v)
        .setComment("Report event88 with capture kind800; diagnostic admission remains in51C66.");
    semanticFunction(0x45F02L, "f33_report_scalar_event_88_pass", v)
        .setComment("Report event88 through51D5E ordinary pass; current failure clears while normal retained histories "
            + "survive.");
    semanticFunction(0x45F9CL, "f33_report_scalar_event_85_healthy_observed", v)
        .setComment("Report event85 through51E2C/52A2A healthy-observed bitmap; does not clear current failure history.");
    semanticFunction(0x45FACL, "f33_report_scalar_event_85_failure", v)
        .setComment("Report event85 with capture kind800; diagnostic admission remains in51C66.");
    semanticFunction(0x45FC0L, "f33_report_scalar_event_85_pass", v)
        .setComment("Report event85 through51D5E ordinary pass; current failure clears while normal retained histories "
            + "survive.");
    semanticFunction(0x6ADFCL, "f33_reset_latched_monitor", v,
        new ParameterImpl("state", F33LatchedMonitorStatePointer, currentProgram))
        .setComment("Clear packed status, passing/failing counts and failure high-water at offsets0/4/6/8. Exactly10 "
            + "bytes of the usual12-byte allocation; adjacent halfword untouched.");
    semanticFunction(0x6AE18L, "f33_retain_disabled_latched_monitor", v,
        new ParameterImpl("state", F33LatchedMonitorStatePointer, currentProgram),
        new ParameterImpl("limits", F33MonitorLimitsPointer, currentProgram))
        .setComment("Recompute state from counters without callbacks: retain failure22 when fail_count>fail_limit; "
            + "otherwise retain pass2200 only when fail_count=0 and pass_count>pass_limit. Clear pending paths; "
            + "preserve failure high-water. Gate closure is not a reset of a confirmed failure.");
    semanticFunction(0x6AE7CL, "f33_step_latched_monitor", u32,
        new ParameterImpl("state", F33LatchedMonitorStatePointer, currentProgram),
        new ParameterImpl("limits", F33MonitorLimitsPointer, currentProgram),
        new ParameterImpl("callbacks", F33TwoSidedMonitorCallbacksPointer, currentProgram))
        .setComment("Ten-byte state and13-pointer callbacks. Derive phase from counters, not old packed status.11/22 "
            + "classify healthy/failure; strict counter>limit confirms. Failed22 is terminal and bypasses "
            + "predicates; confirmed healthy still evaluates entry predicate for failure. Pending33/44 resets both "
            + "current counts. Transition hooks differ from repeated-state hooks. Write packed "
            + "status0/11001100/2200/00110011/22; return full R10=11,not status.");
    semanticFunction(0x6A874L, "f33_reset_recoverable_monitor", v,
        new ParameterImpl("state", F33RecoverableMonitorStatePointer, currentProgram))
        .setComment("Clear all12 bytes: packed status,passing/failing counts,failure high-water and recovery count.");
    semanticFunction(0x6A882L, "f33_retain_disabled_recoverable_monitor", v,
        new ParameterImpl("state", F33RecoverableMonitorStatePointer, currentProgram),
        new ParameterImpl("limits", F33RecoverableMonitorLimitsPointer, currentProgram))
        .setComment("Retain confirmed failure22 including its recovery count; preserve confirmed pass2200,otherwise "
            + "discard pending counts. Clear recovery only outside confirmed failure; high-water survives. No "
            + "predicate or reporting callback.");
    semanticFunction(0x6A8B4L, "f33_step_recoverable_monitor", u32,
        new ParameterImpl("state", F33RecoverableMonitorStatePointer, currentProgram),
        new ParameterImpl("limits", F33RecoverableMonitorLimitsPointer, currentProgram),
        new ParameterImpl("callbacks", F33RecoverableMonitorCallbacksPointer, currentProgram))
        .setComment("Twelve-byte state and15-pointer callbacks. Pending confirmation follows strict passing/failing "
            + "thresholds. Confirmed failure calls third predicate and70F56 recovery scratch: strict "
            + "recovery_count>limit clears current counts/status and invokes recovery callback. Preserve failure "
            + "high-water. Stores packed status; returns full R10=11. The local recovery scratch is not the same "
            + "layout as persistent state.");
    semanticFunction(0x6AE08L, "f33_reset_windowed_monitor", v,
        new ParameterImpl("state", F33WindowedMonitorStatePointer, currentProgram))
        .setComment("Clear14 used bytes of16-byte state allocation: result,pass count/window,fail count/window,fail "
            + "high-water. Adjacent trailing halfword untouched.");
    semanticFunction(0x6B31AL, "f33_step_windowed_monitor", u32,
        new ParameterImpl("state", F33WindowedMonitorStatePointer, currentProgram),
        new ParameterImpl("limits", F33WindowedMonitorLimitsPointer, currentProgram),
        new ParameterImpl("callbacks", F33TwoSidedMonitorCallbacksPointer, currentProgram))
        .setComment("Fourteen-byte state and13-pointer callbacks. Pending failure counts failing classifications within a "
            + "separately advancing window: healthy11 or ambiguous33 preserves accumulated failure count; invalid44 "
            + "resets it. Window expiry wins before another failure can confirm. Both confirmation and expiry use "
            + "strict > comparisons with16-bit increments. Exact acquisition config pass2/windowFFFF,fail3/window6. "
            + "Confirmed failure latches; packed status stored and full R10=11 returned.");
    semanticFunction(0x70F56L, "f33_step_monitor_recovery_scratch", u32,
        new ParameterImpl("classification", u8, currentProgram),
        new ParameterImpl("scratch", F33MonitorRecoveryScratchPointer, currentProgram),
        new ParameterImpl("limit", ushortPointer, currentProgram))
        .setComment("Truncate classification to8 bits.11 increments scratch recovery_count at+10 while<=limit; strict "
            + "crossing clears halfwords0/2/4/8/10/12/16 and returns0,else44000022.22/44 clear recovery_count and "
            + "return22; other classifications return22 preserving it. Scratch+6 high-water survives. This18-byte "
            + "transient layout is not the persistent monitor record.");
    semanticData(0xFEBE7B50L, latchedMonitorStateType, "f33_scalar_monitor_45356_state",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x2B9B4L, monitorLimitsType, "f33_scalar_monitor_45356_limits",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x28AC8L, twoSidedMonitorCallbacksType, "f33_scalar_monitor_45356_callbacks",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0xFEBE7B5CL, latchedMonitorStateType, "f33_scalar_monitor_45410_state",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x2B9B8L, monitorLimitsType, "f33_scalar_monitor_45410_limits",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x28AFCL, twoSidedMonitorCallbacksType, "f33_scalar_monitor_45410_callbacks",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0xFEBE7B6CL, latchedMonitorStateType, "f33_scalar_monitor_45572_state",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x2B9BCL, monitorLimitsType, "f33_scalar_monitor_45572_limits",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x28B30L, twoSidedMonitorCallbacksType, "f33_scalar_monitor_45572_callbacks",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0xFEBE7B78L, latchedMonitorStateType, "f33_scalar_monitor_4562a_state",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x2B9C0L, monitorLimitsType, "f33_scalar_monitor_4562a_limits",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x28B64L, twoSidedMonitorCallbacksType, "f33_scalar_monitor_4562a_callbacks",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0xFEBE7B84L, recoverableMonitorStateType, "f33_scalar_monitor_456fa_state",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x2B9C4L, recoverableMonitorLimitsType, "f33_scalar_monitor_456fa_limits",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x28B98L, recoverableMonitorCallbacksType, "f33_scalar_monitor_456fa_callbacks",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0xFEBE7B90L, recoverableMonitorStateType, "f33_scalar_monitor_45838_state",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x2B9CAL, recoverableMonitorLimitsType, "f33_scalar_monitor_45838_limits",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x28BD4L, recoverableMonitorCallbacksType, "f33_scalar_monitor_45838_callbacks",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0xFEBE7B9CL, latchedMonitorStateType, "f33_scalar_monitor_4599c_state",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x2B9D0L, monitorLimitsType, "f33_scalar_monitor_4599c_limits",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x28C10L, twoSidedMonitorCallbacksType, "f33_scalar_monitor_4599c_callbacks",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0xFEBE7BA8L, latchedMonitorStateType, "f33_scalar_monitor_45a6c_state",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x2B9D4L, monitorLimitsType, "f33_scalar_monitor_45a6c_limits",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x28C44L, twoSidedMonitorCallbacksType, "f33_scalar_monitor_45a6c_callbacks",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0xFEBE7BDCL, recoverableMonitorStateType, "f33_scalar_monitor_45e74_state",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x2BA0CL, recoverableMonitorLimitsType, "f33_scalar_monitor_45e74_limits",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x28C78L, recoverableMonitorCallbacksType, "f33_scalar_monitor_45e74_callbacks",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0xFEBE7BE8L, recoverableMonitorStateType, "f33_scalar_monitor_45f32_state",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x2BA12L, recoverableMonitorLimitsType, "f33_scalar_monitor_45f32_limits",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x28CB4L, recoverableMonitorCallbacksType, "f33_scalar_monitor_45f32_callbacks",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0xFEBE70C8L, windowedMonitorStateType, "f33_scalar_monitor_3bab2_state",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x2B5E0L, windowedMonitorLimitsType, "f33_scalar_monitor_3bab2_limits",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x27FCCL, twoSidedMonitorCallbacksType, "f33_scalar_monitor_3bab2_callbacks",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0xFEBE70D8L, windowedMonitorStateType, "f33_scalar_monitor_3bb44_state",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x2B5E8L, windowedMonitorLimitsType, "f33_scalar_monitor_3bb44_limits",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x28000L, twoSidedMonitorCallbacksType, "f33_scalar_monitor_3bb44_callbacks",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0xFEBE70ECL, latchedMonitorStateType, "f33_scalar_monitor_3bc4c_state",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x2B5F0L, monitorLimitsType, "f33_scalar_monitor_3bc4c_limits",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x28034L, twoSidedMonitorCallbacksType, "f33_scalar_monitor_3bc4c_callbacks",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0xFEBE70F8L, latchedMonitorStateType, "f33_scalar_monitor_3bcfc_state",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x2B5F4L, monitorLimitsType, "f33_scalar_monitor_3bcfc_limits",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
    semanticData(0x28068L, twoSidedMonitorCallbacksType, "f33_scalar_monitor_3bcfc_callbacks",
        "Exact configured monitor layout; callback events and action publication have separate retention rules.");
  }
  private void annotateApplicationModeTransitions() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    semanticFunction(0xB1808L, "f33_advance_application_mode", v)
        .setComment("Repair live mode, run at most one current-family internal transition, then family-prioritized major "
            + "requests. Low IDs acknowledge only selected/complement-qualified pending winner; losing low pending "
            + "requests retain.0701 pending2 can suppress10/7 until NvM/output snapshot readiness; exactFF038 "
            + "constant0 then requests foreground restart through mode0000, not0800. All families except0200 clear "
            + "direct-enable8B4C/4D. Mode publicationE8CC is separate.");
    semanticFunction(0xB16F4L, "f33_transition_application_mode", v,
        new ParameterImpl("new_mode", u16, currentProgram))
        .setComment("If old and new mode<0A00, run AEB00 old-family exit then new-family entry before redundant live "
            + "commitB11A/B0A0/B0A4. Hooks see old live mode. No same-mode/family short circuit and no E8CC "
            + "publication.");
    semanticFunction(0xB1620L, "f33_publish_live_application_mode", v,
        new ParameterImpl("mode", u16, currentProgram))
        .setComment("Commit liveB11A with XOR5555/B0A0 and XORAAAA/B0A4 throughD26D0 priority-protected redundant "
            + "publisher. Does not publishE8CC.");
    semanticFunction(0xB167EL, "f33_repair_live_application_mode", v)
        .setComment("Vote liveB11A and redundantB0A0/B0A4; republish voted value only on repairable statuses-12/-11. No "
            + "automatic invalid-to-zero fallback.");
    semanticFunction(0xB16BCL, "f33_probe_pending_mode_request", u32,
        new ParameterImpl("request_id", u8, currentProgram))
        .setComment("Return1 exactly when request slotB0A8+2*ID isA55A. Pending IDs<16 capture "
            + "selectedB10C/complementB0A6 and old liveB11C/complementB0A2. Internal IDs>=16 do not replace "
            + "selected metadata. Failed probes retain metadata. Caller must provide valid slot ID.");
    semanticFunction(0xB1738L, "f33_acknowledge_selected_mode_request", v,
        new ParameterImpl("request_id", u8, currentProgram))
        .setComment("Change pendingA55A to5AA5 only for matching selectedID/complement, or internalID>16. Does not clear "
            + "request bitmap or losing low pending slots. ID16 is not unconditional.");
    semanticFunction(0xB176EL, "f33_qualify_mode_restart_readiness", u32)
        .setComment("Require66F1E NvM readiness first. Then return5A/resetB114 when all sampledB072..B075 zero or "
            + "retainedcount>=20. Otherwise replace8A70/8AD0 owners0/1 with20002 and increment;19\u219220 still "
            + "returns0. NvM not ready freezes counter even above20 and with zero snapshots. Counts are "
            + "invocations, not measuredtime.");
    semanticFunction(0xB17EEL, "f33_request_foreground_restart_from_mode", v)
        .setComment("Clear redundantNvM gates0671/0672 viaFF010/FF024, transition0000 through realhooks, then publish "
            + "foreground request8C08=A55A throughFEFC0/5889A. Not an immediate CPU reset or mode snapshot publish.");
    semanticFunction(0xB166EL, "f33_reset_mode_readiness_counter", v)
        .setComment("Clear retainedB114 then call empty0100 entryhook. Separate reset path; normal familyexit does not "
            + "clear the readinesscounter.");
    semanticFunction(0xB1D00L, "f33_advance_mode100_substate", v)
        .setComment("Exact0100\u21920101(event17)\u21920102(18)\u21920103(19);0103 event20 requests major5. Internal events acknowledge "
            + "independently of selected majorID.0100/0103 self-request their next internalevent;0101 waits NvM "
            + "acquisition phase0 via5678A.");
    semanticFunction(0xB281EL, "f33_advance_mode200_output_sequence", v)
        .setComment("Advance exactly one0200..020D stage using matching IDs21..34. Each admitted channel gets "
            + "stage-specific owner masks; disabled B082 channels retain. Direct-output stages0203/020B/020C load "
            + "triplets then enable5A. Terminal020D requests3 plus6 only ifB32E0 selector!=1, clears direct "
            + "enables; major arbiter runs afterward.");
    semanticFunction(0x31FCAL, "f33_request_published_mode200_phase", v)
        .setComment("Use PUBLISHED E8CC family0200 and redundant6884/6885 readiness, with6764 channel bypassbits. Compute "
            + "low8(E8CC+0x15), admit<0x23, pass that ID inr6 toFDFFC, then clearbothreadinessflags. Live/published "
            + "generation skew may emit an older retainedphase request.");
    semanticFunction(0xB27FEL, "f33_complete_mode200_output_sequence", v)
        .setComment("Clear direct-enable bytes8B4C/8B4D, setB10F throughB32E0; when returnedselector!=1 request6, then "
            + "alwaysrequest3.0200 takes3\u21920300 first; retained6 may subsequentlyjoin0500 unless "
            + "higher-priorityrequests win.");
    semanticFunction(0xB32E0L, "f33_select_service_join_after_mode200", u32)
        .setComment("Set and returnB10F=1 if32-bitF208nonzero, otherwise2. CallerB27FE uses r10 to decide whether to "
            + "request6; do not typevoid.");
    semanticFunction(0xB2B9EL, "f33_advance_mode300_substate", v)
        .setComment("0300 matchingevent35/0x23 appliesB2B0A output/record actions then commits0301.0301 increments "
            + "retainedB10D to5, then requests36/0x24; accepting36 requestsmajor12\u21920400 without changing0301. "
            + "Counter is not reset on0300 entry/exit.");
    semanticFunction(0xB2B70L, "f33_step_mode301_invocation_counter", v)
        .setComment("If retainedB10D<5 increment; otherwise request36/0x24 andretaincounter. The invocationentering5 "
            + "doesnotrequest; no measuredtimeclaim.");
    semanticFunction(0xB2BF8L, "f33_apply_mode400_output_requests", v)
        .setComment("Clear owners0/1 of8B2C/8A9C/8AE8/8A50/8A2C/8260, conditionally write8AA8=2/20000 "
            + "forclearB082channelbits. Doesnotclear8A70/8AD0; top-level573FE separatelyclearsdirectenables.");
    semanticFunction(0xB2C82L, "f33_enter_mode400", v)
        .setComment("Finalize diagnosticlog45CFC, clear8B2Cowners0/1, setclassifier82A9=5A. Oldlive mode remainsvisible "
            + "until callercommitsnewmode.");
    semanticFunction(0xB2CFEL, "f33_advance_mode700_substate", u32)
        .setComment("Advance atmostone0700\u21920701(event38/0x26),0701\u21920702(39/0x27 retainedrecordsnapshot), or0702 "
            + "event40/0x28 requestsmajor10. ReturnB2CE4 r10:0onlywhilepost-worker live0701;5Aotherwise. "
            + "ParentB1808 usesreturnfor event2 restartbranch.");
    semanticFunction(0xB2CE4L, "f33_get_mode700_progress_marker", u32)
        .setComment("Return0 onlyfor exactlive0701, otherwise5A including0700/0702. Thisispost-submode "
            + "readinessbranchselector, not an independentlyqualified hardware readiness.");
    semanticFunction(0xB2D74L, "f33_request_mode701_snapshot_unless_health_selected", v)
        .setComment("Request39/0x27 unless selectedID/complementisvalidandID1. Calledin0700entrywhileoldlive mode "
            + "remains; health-selected1 delaysretainedsnapshotrequest for laterthermalproducer.");
    semanticFunction(0xB2D94L, "f33_request_mode700_initial_step", v)
        .setComment("Request38/0x26 andfinalize diagnosticlog45CFC. Doesnotmaterializeslotdirectly; "
            + "reconciliationlaterruns.");
    semanticFunction(0xB2DA8L, "f33_enter_mode700", v)
        .setComment("Reportserviceaborts;publishretained thermal/records8,9,D and conditionalrecords18/105;mark5F84.bit1 "
            + "andqualified89D2[].bit1;setB250=5A;request38andconditionally39;finalizelog. "
            + "Set8A48owner0=3,8B2Cowners0/1=70017001, clear8AD0/8AE8/8A50/8A2C/8260owners0/1,8AA8=4/40000. "
            + "Doesnotclear8A70owners.");
    semanticFunction(0xB2E64L, "f33_apply_mode800_ready_output_requests", v)
        .setComment("Onlyif66F1E==1replace8A70owners0/1=20002,8A9C=4/40000,8AD0/8AE8=0,8AA8=4/40000,8A88owners2/3=2/20000. "
            + "NvMbusy leavesmaskstateunchanged; top-leveldirectenableclearstilloccurs.");
    semanticFunction(0xB32F4L, "f33_enter_mode600", v)
        .setComment("ClearB110 on0600entry. Nootheraction; separateexitclearsB111 andresets6A60..6A62.");
    semanticFunction(0xB32FAL, "f33_exit_mode600", v)
        .setComment("ClearB111, call33FC6 toclear6A61/6A62 andset6A60=10 before newfamilyentry andlivecommit.");
    semanticFunction(0xB33DAL, "f33_enter_mode900", v)
        .setComment("Set8B2Cowners0/1=70017001,8A70owners0/1=20002,8AD0owners0/1=20002. "
            + "Thisrequestsoutput-ownerstate,notphysicalpowerconfirmation.0900exitandsteadyworkersareempty.");
    semanticFunction(0x66F1EL, "f33_application_nvm_is_ready", u32)
        .setComment("Return1 onlywhen all32family0/all16repairedfamily1 statuses avoidpending highnibble20,busy0690/0691 "
            + "neitherFFnorA5,and0673zero. Usedby0701/0800mode-readiness andexistingforegroundhandoff. No "
            + "hardwarepowerpredicate.");
    semanticFunction(0xFF038L, "f33_get_mode_restart_hardware_selector", u32)
        .setComment("Tail-wrapper66FEE returns0 inexactimage.0701event2-ready therefore takesB17EE "
            + "softwareforegroundrestart; return5A alternative0800edgeisnotreachablethroughthistarget.");
    semanticFunction(0x573FEL, "f33_clear_direct_output_enables", v)
        .setComment("Clear8B4C/8B4D only. "
            + "Majorarbitercallsbeforeeveryhandledfamilyexcept0200;stageandexitcallersalsoexplicitlyclear. "
            + "Doesnotclearownerrequestarraysorprovephysicalzerooutput.");
    semanticFunction(0xB1DA4L, "f33_apply_mode0201_entry_requests", v)
        .setComment("Apply per-channel output-owner bundle for transition0200\u21920201; "
            + "onlychannelswithclearB082bitarechanged. "
            + "Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table. "
            + "Directenable: 0.");
    semanticFunction(0xB1E70L, "f33_apply_mode0202_entry_requests", v)
        .setComment("Apply per-channel output-owner bundle for transition0201\u21920202; "
            + "onlychannelswithclearB082bitarechanged. "
            + "Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table. "
            + "Directenable: 0.");
    semanticFunction(0xB1F3AL, "f33_apply_mode0203_entry_requests", v)
        .setComment("Apply per-channel output-owner bundle for transition0202\u21920203; "
            + "onlychannelswithclearB082bitarechanged. "
            + "Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table. "
            + "Directenable: 0.");
    semanticFunction(0xB2004L, "f33_apply_mode0204_entry_requests", v)
        .setComment("Apply per-channel output-owner bundle for transition0203\u21920204; "
            + "onlychannelswithclearB082bitarechanged. "
            + "Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table. "
            + "Directenable: 5A with AF3DE triplet.");
    semanticFunction(0xB20E0L, "f33_apply_mode0205_entry_requests", v)
        .setComment("Apply per-channel output-owner bundle for transition0204\u21920205; "
            + "onlychannelswithclearB082bitarechanged. "
            + "Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table. "
            + "Directenable: 0.");
    semanticFunction(0xB21AAL, "f33_apply_mode0206_entry_requests", v)
        .setComment("Apply per-channel output-owner bundle for transition0205\u21920206; "
            + "onlychannelswithclearB082bitarechanged. "
            + "Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table. "
            + "Directenable: 0.");
    semanticFunction(0xB2274L, "f33_apply_mode0207_entry_requests", v)
        .setComment("Apply per-channel output-owner bundle for transition0206\u21920207; "
            + "onlychannelswithclearB082bitarechanged. "
            + "Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table. "
            + "Directenable: 0.");
    semanticFunction(0xB233AL, "f33_apply_mode0208_entry_requests", v)
        .setComment("Apply per-channel output-owner bundle for transition0207\u21920208; "
            + "onlychannelswithclearB082bitarechanged. "
            + "Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table. "
            + "Directenable: 0.");
    semanticFunction(0xB2400L, "f33_apply_mode0209_entry_requests", v)
        .setComment("Apply per-channel output-owner bundle for transition0208\u21920209; "
            + "onlychannelswithclearB082bitarechanged. "
            + "Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table. "
            + "Directenable: 0.");
    semanticFunction(0xB24CAL, "f33_apply_mode020a_entry_requests", v)
        .setComment("Apply per-channel output-owner bundle for transition0209\u2192020A; "
            + "onlychannelswithclearB082bitarechanged. "
            + "Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table. "
            + "Directenable: 0.");
    semanticFunction(0xB258EL, "f33_apply_mode020b_entry_requests", v)
        .setComment("Apply per-channel output-owner bundle for transition020A\u2192020B; "
            + "onlychannelswithclearB082bitarechanged. "
            + "Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table. "
            + "Directenable: 0.");
    semanticFunction(0xB2654L, "f33_apply_mode020c_entry_requests", v)
        .setComment("Apply per-channel output-owner bundle for transition020B\u2192020C; "
            + "onlychannelswithclearB082bitarechanged. "
            + "Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table. "
            + "Directenable: 5A with AF3DE triplet.");
    semanticFunction(0xB272AL, "f33_apply_mode020d_entry_requests", v)
        .setComment("Apply per-channel output-owner bundle for transition020C\u2192020D; "
            + "onlychannelswithclearB082bitarechanged. "
            + "Channel1masksshift16except50C82Boolean;shared5693Eowner0writtenlast. Exactbundle inphase_table. "
            + "Directenable: 5A with AF3E4 triplet.");
    semanticFunction(0x66FEEL, "f33_platform_restart_selector_constant_zero", u32)
        .setComment("Return full R10=0. Exact-image selector used through FF038: ready0701 request2 takes software "
            + "foreground restart, not0800.");
    semanticFunction(0xFEFFCL, "f33_query_application_nvm_readiness", u32)
        .setComment("Tail-call66F1E and preserve its full R10 readiness result. No independent hardware power or "
            + "persistence assertion.");
    semanticFunction(0xB1C32L, "f33_mode_hook_b1c32", v)
        .setComment("JMP LP with no state change; AEB00 table 0x0 entry, 0x0 exit. Exact-image hook, not a missing "
            + "implementation.");
    semanticFunction(0xB1DA0L, "f33_mode_hook_b1da0", v)
        .setComment("JMP LP with no state change; AEB00 table 0x100 exit. Exact-image hook, not a missing implementation.");
    semanticFunction(0xB2BF4L, "f33_mode_hook_b2bf4", v)
        .setComment("JMP LP with no state change; AEB00 table 0x300 entry. Exact-image hook, not a missing "
            + "implementation.");
    semanticFunction(0xB2BF6L, "f33_mode_hook_b2bf6", v)
        .setComment("JMP LP with no state change; AEB00 table 0x300 exit. Exact-image hook, not a missing implementation.");
    semanticFunction(0xB2CA2L, "f33_mode_hook_b2ca2", v)
        .setComment("JMP LP with no state change; AEB00 table 0x400 exit. Exact-image hook, not a missing implementation.");
    semanticFunction(0xB2E62L, "f33_mode_hook_b2e62", v)
        .setComment("JMP LP with no state change; AEB00 table 0x700 exit. Exact-image hook, not a missing implementation.");
    semanticFunction(0xB2EE2L, "f33_mode_hook_b2ee2", v)
        .setComment("JMP LP with no state change; AEB00 table 0x800 entry. Exact-image hook, not a missing "
            + "implementation.");
    semanticFunction(0xB2EE4L, "f33_mode_hook_b2ee4", v)
        .setComment("JMP LP with no state change; AEB00 table 0x800 exit. Exact-image hook, not a missing implementation.");
    semanticFunction(0xB342AL, "f33_mode_hook_b342a", v)
        .setComment("JMP LP with no state change; AEB00 table 0x900 exit. Exact-image hook, not a missing implementation.");
  }
  private void annotateResetAndForegroundOwnership() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType uintPointer = new PointerDataType(u32, 4);
    semanticFunction(0x0L, "f33_reset_vector", v)
        .setComment("Hardware reset-vector stub: SYNCP then absolute JMP01B0 without changingLP. The destination owns CPU "
            + "context/safety gates and first1404 call. Not an ordinary C-call/return ABI. Physical device vector "
            + "selection is outside this static proof.");
    semanticFunction(0x1B0L, "f33_reset_context_and_startup", v)
        .setComment("Nonreturning assembly reset entry. DI;initialize GPR/system-register "
            + "context,SPFEBE8000,GPFEBF9800,TP869C,EBASE1,INTBP0,PMRFFFF,MPM0. Gate JP0_4/BIST/ECM status with "
            + "rereads;failure publishes protected retained token and halts0744. Pass path clears/enables "
            + "instruction cache with unbounded readback waits,initializes data-buffer/MPU/FPU "
            + "state,clearsFEBE7000..7FFF,then calls1404 and cannot return normally. Do not infer physical reset "
            + "completion or register feedback from this software contract.");
    semanticFunction(0x1404L, "f33_boot_hardware_ram_init_and_select_image", v)
        .setComment("Called directly by reset assembly067C after first7000..7FFF clear and CPU setup. Perform "
            + "ordered79A/7B6/802/880/8C8/96E/C52 hardware controls;SYNCM;preserve the empty reversed-bound first "
            + "loop;clear established upper LocalRAM andGlobalRAM intervals;setEEPRDCYCL3;call13B0. Earlier "
            + "hardware readback loops have no software timeout. RAM-clear extents/tests remain77.17 owner.");
    semanticFunction(0x13B0L, "f33_boot_select_application_or_resident", v)
        .setComment("Run port/config,retainedECM snapshot,ECM reset and boundedclock controls before119E validates both "
            + "image regions/ECC/magic. Return0 calls the full-width application entry pointer atFFDB8 "
            + "(registered20880) with no diagnostic dwell or local pointer-range guard. Failure resetsINTC "
            + "controls,sets2908=FF andeight subsequentwords=FFFFFFFF,then enters resident1398. Any application "
            + "return halts1402. This branch is distinct from deliberate9F00 programming transfer.");
    semanticFunction(0x119EL, "f33_boot_validate_application_images", u32)
        .setComment("Return0 only after a successful pair of descriptor-backed CRC checks481A(1),481A(0) plus115A "
            + "CodeFlashECC snapshot/clear,then bothFFE00 and17E00 markerwords equal5AA5A55A. Each stage permits at "
            + "most3 attempts;stage2 is reached only afterstage1 success. Return1 otherwise. HardwareCRC/ECC "
            + "feedback is an external dependency;no fixed diagnostic startup interval is provided.");
    semanticFunction(0x481AL, "f33_boot_validate_crc_region", u32,
        new ParameterImpl("region", u32, currentProgram))
        .setComment("Validate region selector through344C/3438;reject missingdescriptor/count. For each16-byte "
            + "descriptor,require base andlength equal metadata-indirected words,then47EA streams words from "
            + "thatbase withCRC seedFFFFFFFF andmust return0. Return0 on allpassing;FFFFFFFF on failure. "
            + "Registeredselectors0/1 hold one recordeach;not generic pointer or image validity outside those "
            + "descriptors.");
    semanticFunction(0x1338L, "f33_boot_resident_initialize", v)
        .setComment("Initialize resident diagnostic/service mode with stateFEBF2904=1 and2900=0,then orderedresident "
            + "lower/service/flash/timer setup.1CA0 startsTAUJ0CH2. State1 prevents existing14A2 timer callback "
            + "services until main137A publishesstate2. Does not validate or launch application.");
    semanticFunction(0x137AL, "f33_boot_resident_service_iteration", v)
        .setComment("Publish resident stateFEBF2904=2 before invoking078C,4428,479A,4874 once. This is the body of1398 "
            + "resident loop and admits existingtimer callback14A2 services;it is not applicationCH3 foreground.");
    semanticFunction(0x1398L, "f33_boot_resident_main", v)
        .setComment("Nonreturning resident bootloader root reached by cold-start validation failure or explicit148E "
            + "programming handoff. Run1338 initialization,restore priority mask with7244(0),EI,then "
            + "repeatedly137A. Application66062 andapplicationvector/table ownership are not entered here.");
    semanticFunction(0x9F00L, "f33_application_transfer_to_boot_context", v,
        new ParameterImpl("handoff_record", uintPointer, currentProgram))
        .setComment("Assembly nonreturning application-to-boot context transfer,not a reset. Preserve r6 handoff-record "
            + "pointer;DI,PMRFFFF,clear SEGFLAG/SEGADDR/SEGCONT atFFFEE982/988/980 (hardware manual Table3.77); "
            + "setPSW18020,EBASE1,INTBP0,SPFEBE8000,GPFEBF9800,TP869C,MPM0,then148E. Does not run1404 RAM "
            + "sweeps or119E application validation. Parent65F5E suppliesROM31788. Ordinary return/stack "
            + "assumptions are invalid.");
    semanticFunction(0x148EL, "f33_boot_resident_enter_with_record", v,
        new ParameterImpl("handoff_record", uintPointer, currentProgram))
        .setComment("Copy exactlyninewords from r6 toFEBF2908 through real1478 word-copy,then enter1398 resident "
            + "bootloader. Requires bootGP/SP/context alreadyestablished by9F00;not an ordinaryapplication-callable "
            + "initializationhelper.");
    semanticFunction(0x62BAEL, "f33_startup_capture_retained_token", v)
        .setComment("Capture retained-register wordsFFC0A000/004/008/00C intoFEBE39B4/8DE4/8DF8/39B8 before "
            + "replacingregistertoken withA5A5A5A5/F0F0F0F0/0F0F0F0F andfourthword0. Snapshot is later classified "
            + "by62BF6;it is not a RAM-clear survivor inferred fromreset.");
    semanticFunction(0x62BF6L, "f33_startup_classify_retained_token", v)
        .setComment("Clear39BC..39BF;recognize exactprotected prior token9B9B9B9B,3E3E3E3E,6D6D6D6D,5A5A5A5A,setting "
            + "correspondingflag5A. Lasttoken additionallyrequires39B8.highbyte5A. Thenpublish7C7C7C7C "
            + "withXORcopies through62B90 andclearPowerOnResetflag viaRESFC=1. OEM tokenmeaning isnot "
            + "assigned;thisdoesnot establish physicalresetretention.");
    semanticFunction(0x62D5EL, "f33_startup_publish_image_identity_check", v)
        .setComment("Compare eightbytes17DA0/20850,then onlyif equalfivebytes17DC0/20870. Any mismatch publishesA55AA55A "
            + "instead0 through70A92 toFEBF0668/raw,10A4/XOR55555555,10C8/XORAAAAAAAA. Primaryeight-byte mismatch "
            + "additionallypublishes066C=5A;secondary-onlymismatchleaves066C=0. Returnswithout blockingstartup;do "
            + "not callthis a launchauthorizationgate.");
    semanticFunction(0x6378CL, "f33_startup_validate_resident_boot_crc", v)
        .setComment("Before releasingapplicationtimers,feedall10240wordsat0000..9FFF intoDCRA1 withCTL0/seedFFFFFFFF. "
            + "AcceptonlyCOUTFFFFFFFF;retryup tothree times,thenenter61940 fatalhandling. Areturned initializer "
            + "meanssoftwaregatepassedagainst suppliedhardwareCRCfeedback,not aphysicalCRCmodelproof.");
    semanticFunction(0x665F2L, "f33_startup_start_timers_and_load_steady_periods", v)
        .setComment("PulsePIC1ASST=1 tostart previouslyselected timers withtheir "
            + "configuredfirst-intervalCDRs;callrealspin_wait(1),writePWMcompares,thenreplacetimerreloadswithsteadyperiod-1. "
            + "Calledonlyafter666BC initializationand6378C bootCRCgate,andbefore701EA(0),EI,66062. "
            + "Triggercompletion/physicaltimingarenotmodeledhere.");
    semanticFunction(0x666BCL, "f33_application_initialize_before_timer_start", v)
        .setComment("Orderedapplicationinitializationdispatcher,calledby637EE "
            + "withinterruptsdisabledbeforebootCRCgateandtimerstart. Lowlevelandsoftwareinitializersinclude66BC8 "
            + "NvMacquisitioninitialization/boundedbootstrap,diagnostics/communications,664F6timerconfiguration,65F8Ebookkeeping,62BF6retainedclassification,6681Eclear5F28,and58804appstateinitialization/publication. "
            + "Noaggregatehardware-successreturnorrollbackexists;donotconflateinitializedstatewithacquireddataorphysicalreadiness.");
    semanticFunction(0x637EEL, "f33_startup_coordinator", v)
        .setComment("Nonreturningreset-selectedapplicationstartupownership:loadapplicationcontext715B4(abandonbootframes),clearoldbootstack632B2,configureguards/MPU/ECC/ECM/interrupts,publishretainedsnapshotandcopyROMdata,runstartupstatus/safety-devicegates,image-IDpublication62D5E,and666BCapplicationinitializers.6378CbootCRCmustpassbefore665F2startpulse;then701EA(0),EI,andforeground66062. "
            + "Hardwarewaitsareexternalboundaries;DISPOSEsuffixisnotanordinaryreturnpath.");
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
    annotateRecoveredBootEntries();
    annotateMemoryPrimitives();
    annotateRedundantStatePrimitives();
    annotateBootAndFreshness();
    annotateFreshnessLayouts();
    annotateBootDispatchAndCurves();
    annotateNvmDescriptors();
    annotateNvmLogicalRequests();
    annotateNvmRecordIntegrity();
    annotateApplicationRecords();
    annotateApplicationCompletion();
    annotateNvmQueues();
    annotateNvmStartup();
    annotateNvmPhysicalResults();
    annotateNvmPageClassification();
    annotateNvmAcquisition();
    annotateNvmRequestSelection();
    annotateRomGroupIntegrity();
    annotateInitializedNvmService();
    annotateApplicationRecordApis();
    annotateNvmDirectOperations();
    annotateControlPipeline();
    annotateSensingPipeline();
    annotateRateObserver();
    annotateEstimatorAcquisition();
    annotateEstimatorQualifiers();
    annotateRetainedEstimatorQualification();
    annotateEstablishedTracking();
    annotateThermalModels();
    annotateRemainingEcuThermalModels();
    annotateThermalHistoryLifecycle();
    annotateThermalArbitration();
    annotateFaultActions();
    annotatePairedMonitorActions();
    annotateSharedMonitorComposition();
    annotateCommunicationStatusComposition();
    annotateDiagnosticEventLifecycle();
    annotateDiagnosticAgingAndClear();
    annotateDiagnosticTransactions();
    annotateAssistComposition();
    annotateAssistConditioning();
    annotateAngleControllerComposition();
    annotateCompensationPublication();
    annotateTxPublication();
    annotatePairedSourceMonitorComposition();
    annotateDiagnosticServiceAdmission();
    annotateDiagnosticWritesAndRoutines();
    annotateApplicationLifecycle();
    annotateServiceLifecycle();
    annotateComposedMonitorLayouts();
    annotateTerminalMonitorComposition();
    annotateScalarMonitorComposition();
    annotateApplicationModeTransitions();
    annotateResetAndForegroundOwnership();
    annotateDataFlashReads();
    annotateFaciSubmission();
    annotatePwmCompareStaging();
    println("SeedCamryF33RecoveredFunctions: seeded " + count
        + " evidence-backed entries and applied exact-F33 semantic prototypes");
  }
}
