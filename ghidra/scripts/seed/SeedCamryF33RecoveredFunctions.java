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
    descriptor.add(Undefined4DataType.dataType, "opaque_00", "Not interpreted here.");
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
    annotateRedundantStatePrimitives();
    annotateBootAndFreshness();
    annotateFreshnessLayouts();
    annotateBootDispatchAndCurves();
    annotateNvmDescriptors();
    annotateNvmLogicalRequests();
    println("SeedCamryF33RecoveredFunctions: seeded " + count
        + " evidence-backed entries and applied exact-F33 semantic prototypes");
  }
}
