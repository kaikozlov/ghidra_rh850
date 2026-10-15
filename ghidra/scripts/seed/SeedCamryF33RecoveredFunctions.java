//@author kaikozlov
//@category Seed
// Seed exact-F33 entries and apply target-native, execution-backed semantic types.
import ghidra.app.script.GhidraScript;
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
    annotateDataFlashReads();
    annotateFaciSubmission();
    annotatePwmCompareStaging();
    println("SeedCamryF33RecoveredFunctions: seeded " + count
        + " evidence-backed entries and applied exact-F33 semantic prototypes");
  }
}
