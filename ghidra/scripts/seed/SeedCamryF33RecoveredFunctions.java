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
    for (long entry : new long[] {0x67948L, 0x67208L}) {
      Function getter = getFunctionAt(toAddr(entry));
      if (getter == null) throw new IllegalStateException("missing record getter " + toAddr(entry));
      getter.setReturnType(u32, SourceType.USER_DEFINED);
      getter.replaceParameters(Function.FunctionUpdateType.DYNAMIC_STORAGE_FORMAL_PARAMS,
          true, SourceType.USER_DEFINED,
          new ParameterImpl("object", u16, currentProgram),
          new ParameterImpl("destination", words, currentProgram));
    }
    semanticFunction(0x66DFCL, "f33_nvm_get_ram_record", u32,
        new ParameterImpl("selector", u32, currentProgram),
        new ParameterImpl("destination", words, currentProgram))
        .setComment("Decode only selector bits8..15 and pass low8 object plus "
            + "the unchanged destination to67948/68144/67208 for families0/1/2. "
            + "Forward the callee result; other families returnFF without data access. "
            + "Upper16 selector bits are ignored. This is not a physical NvM read.");
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
  private void annotateApplicationReadCompletion() throws Exception {
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
    StructureDataType stage = new StructureDataType(category, "F33NvmReadCopyStage", 0);
    stage.setPackingEnabled(true);
    DataType lane = new ArrayDataType(u8, 32, 1);
    stage.add(lane, "raw", "Only this lane is repaired by encoded-copy consensus.");
    stage.add(lane, "xor55", "Decode each payload byte with55.");
    stage.add(lane, "xorAA", "Decode each payload byte withAA.");
    semanticData(0xFEBF0B08L, new ArrayDataType(resolve(stage), 4, 96),
        "f33_nvm_family1_read_stages",
        "Slot=object&3. Payload lengths8/16/32 leave lane padding untouched. "
        + "Shared-slot execution ordering is a separate queue/scheduler question.");
    semanticData(0xFEBF0358L, new ArrayDataType(u8, objectCount, 1),
        "f33_nvm_family1_completion",
        "FF admits the application callback; read consensus publishes5A/A5. "
        + "Distinct from the redundant application-status bytes atFEBF0328.");
    semanticData(0xFEBF0691L, u8, "f33_nvm_family1_busy",
        "68E9E clears this on leaf return5A, including failed read consensus. "
        + "Its current value is not an admission gate in68E9E.");
    semanticData(0xFEBF0694L, u8, "f33_nvm_family1_copy_read_retry",
        "Shared per-copy retry counter. Success clears it; nonzero result retries "
        + "while below2, consuming an attempt even if73FE8 rejects submission.");
    semanticData(0xFEBF0698L, new ArrayDataType(u32, 4, 4),
        "f33_nvm_family1_copy_failure_masks",
        "One word per shared slot. Each copy uses bits5A in its byte, not an "
        + "arbitrary-nonzero-byte test. Copy0 resets the entire word.");
    StructureDataType request = new StructureDataType(category, "F33NvmFamily1RequestCell", 0);
    request.setPackingEnabled(true);
    request.add(u8, "state", "67AE6 does not inspect this byte.");
    request.add(u8, "opaque_01", "Not interpreted by the membership/finalization proof.");
    request.add(u16, "object", "FFFF marks an empty object field; membership scans all rows.");
    semanticData(0xFEBF058CL, new ArrayDataType(resolve(request), requestCount, 4),
        "f33_nvm_family1_request_cells",
        "49 four-byte cells at058C, not048C.67AE6 ignores state and queue indices.");
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
    semanticFunction(0x68E9EL, "f33_nvm_route_application_result", u32,
        new ParameterImpl("event", u8, currentProgram),
        new ParameterImpl("logical_handle", u16, currentProgram),
        new ParameterImpl("result", u8, currentProgram))
        .setComment("Decode family/object from2B010. Require family completionFF "
            + "and nonFFFF first handle; event6/7 selects read/write result handler. "
            + "Leaf return5A clears that family's busy byte even on failed consensus. "
            + "Always return0. Native proof covers family1 read/gates; family0 and "
            + "write-result processing are separate, not established by this proof.");
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
            + "Valid phase22/33 with completion5A publishes checksum seed then status10. "
            + "Read failure uses68A6C to choose30/11. Write failure retries below2 "
            + "through6869E and returns before cleanup regardless submission result; "
            + "otherwise status31. Any matching request cell overrides status to20 "
            + "after seed publication. Publish all three status planes, then clear "
            + "phase, preserve recovered producer index and set active objectFFFF. "
            + "Invalid phase/object performs cleanup only. Hardware-backed read-failure "
            + "classification and accepted whole-write rearming remain separate.");
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
    semanticFunction(0x68324L, "f33_nvm_submit_bulk_reads", u32)
        .setComment("For family1 completion!=5A and nonFFFF first handle, submit "
            + "base/base+4/base+8 to slot(object&3) raw/55/AA destinations, ignoring "
            + "each enqueue result, then set completionFF. No family busy gate or "
            + "payload access. Then process family0 descriptor handle ranges. "
            + "ReturnFF if any eligible object attempted, otherwise0. Native proof "
            + "covers all11 enabled family1 objects, a rejected pending copy and "
            + "already-complete arrays; family0 acquisition remains separate.");
    semanticFunction(0x68626L, "f33_nvm_submit_family1_read_copies", u32,
        new ParameterImpl("object", u16, currentProgram))
        .setComment("Read descriptor before gating on busy0 and first handle!=FFFF; "
            + "no local object bound. Submit three copies through73FE8, ignore their "
            + "return values, set busyFF and slot failure mask005A5A5A, return0. "
            + "Rejected gate returnsFF. Preserve completion byte and staging; this "
            + "is submission, not acquired data or completed restoration.");
    semanticFunction(0x7936EL, "f33_nvm_initialize_dataflash_read_controls", VoidDataType.dataType)
        .setComment("Write EEPRDCYCL=F, DFECCCTL=4000, DFERRINT=0, DFTSTCTL=4000. "
            + "Manual PROT01 keys are not retained: normal ECC enabled, ECC test "
            + "disabled, notification enables cleared. Eight native instructions "
            + "from nonzero control state; no physical timing or ECM delivery proof.");
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
            + "Timeout reaches realB3 forced-stop, still an unsupported model boundary.");
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
    annotateApplicationReadCompletion();
    annotateNvmQueues();
    annotateNvmStartup();
    annotateDataFlashReads();
    annotateFaciSubmission();
    annotatePwmCompareStaging();
    println("SeedCamryF33RecoveredFunctions: seeded " + count
        + " evidence-backed entries and applied exact-F33 semantic prototypes");
  }
}
