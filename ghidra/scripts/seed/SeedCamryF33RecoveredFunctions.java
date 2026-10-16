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
            + "Selected indices are not boolean bridge-disable flags; slot4 can outrank aggregate-request neutral slot3.");
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
        .setComment("Channels<16 combine descriptor+08/+18 halfwords with low16 arithmetic; otherwise return0. "
            + "BaseFFFF8400 is independent of GP. Ring consumers select six entries without per-offset modulo: "
            + "counts2/4 produce zero tails. Count and low16 payload acknowledgments do not establish sample age.");
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
    message.add(u32, "response_length", "Handler body length; main5630 includes retained prefixes after9126A. Transport extent is16-bit.");
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
        .setComment("Clear retained SID562C, callback5628 and prefix count562D, then reset message5630; this is not the NRC5624 reset.");
    semanticFunction(0x9165EL, "f33_dcm_cancel_active_service", v)
        .setComment("If callback exists, zero main message5630 then invoke operation2. Clear NRC5624 and active state afterward. Retained handler copies/application effects are independent.");
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
        .setComment("Compose62ABC,62B18,6294E into5EE0..5F24 and cached380A/B into5F26/27. "
            + "6294E rotates serial mask windows and publishes5F18/1A/22/24;66824 does not write these masks. "
            + "The range and mask fields are staged generations, not an atomic physical measurement.");
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
            + "Selectors0/1 cover CodeFlash and selector2 covers FEBF0000+FF0 with metadata atFEBF0FE0/4; "
            + "each has one descriptor. This is not generic pointer or image validity outside those descriptors.");
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
  private void annotateInitializationAndSnapshots() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    semanticFunction(0x58804L, "f33_initialize_application_and_request_first_generation", v)
        .setComment("Run cold software initialization58828, then request redundant8C08=A55A. This runs inside666BC before "
            + "timers; it is not physical reset or an aggregate hardware-success gate.");
    semanticFunction(0x58828L, "f33_initialize_cold_application_state", v)
        .setComment("Clear restart token, redundant restart classification8C1A/B/C, counters8C16/17 and cadence8C19. "
            + "Initialize cold ECU acquisition58C9A and cold control-retained cellsBF91E viaFDC00, then common58814. "
            + "This path differs from warm5886C.");
    semanticFunction(0x5886CL, "f33_reinitialize_application_for_foreground_restart", v)
        .setComment("Clear four task last-mode words8C00/02/04/06 and set inverses8C0C/0E/10/12=FFFF, then common58814. "
            + "Do not rerun58C9A/BF91E or reset task cadence/restart token. BF97A resets both live mode and "
            + "publishedE8CC to0; acquired inputs and cold-owned health generation history survive.");
    semanticFunction(0x58814L, "f33_initialize_generated_application_components", v)
        .setComment("Ordered common initializer:59448 ECU work state, FDC14\u2192BF97A control work state, then5C6D8 copies control "
            + "publications into ECU views. Both cold58828 and warm5886C call this; it does not invoke the "
            + "low-level666BC hardware/NvM startup sequence.");
    semanticFunction(0x59448L, "f33_initialize_ecu_application_work_state", v)
        .setComment("Generated ECU initialization and signal propagation. Reset monitor/action records and qualification, "
            + "initialize control/filter work state, copy current acquisition into task views; "
            + "final58070,FC4F8,58074,58802 sequence publishes ECU foreground outputs. No claim that every calibration "
            + "has an OEM physical meaning.");
    semanticFunction(0xBF97AL, "f33_initialize_control_application_work_state", v)
        .setComment("Generated control initialization and input propagation, including request bitmaps/slots, redundant live "
            + "mode, current-limit owner slots and filter/controller state. Cold-onlyBF91E is separate. Directly "
            + "seed the E800+ output image, includingE8CC=0, rather than calling periodic publisherBF3AA.");
    semanticFunction(0x58C9AL, "f33_initialize_cold_ecu_input_state", v)
        .setComment("Cold-only ECU input/status initialization before generated components. Both six-halfword acquisition "
            + "banks822C/8238 start8000; many status/validity cells have explicit nonzero defaults. Not a blanket "
            + "zeroing operation and not called by warm5886C.");
    semanticFunction(0xBF91EL, "f33_initialize_cold_control_retained_state", v)
        .setComment("Cold-only control-retained state: clearB195/B196 andBE7E with other retained input/filter cells; selected "
            + "qualifiers start1. Warm5886C skips this owner; health edge history can survive the common component "
            + "initialization.");
    semanticFunction(0x5C6D8L, "f33_snapshot_initialized_control_publications", v)
        .setComment("After both common initializers, copyE400/E600 publication fields into6434..644C and6768..6794 ECU views. "
            + "Does not publish liveB11A toE8CC or obtain new physical inputs.");
    semanticFunction(0x5897AL, "f33_snapshot_ch1_inputs", v)
        .setComment("Save PMR; setFFC0; copy ECU inputs through5C7B6 and control inputs throughFDC28; restore entryPMR. The "
            + "caller subsequently runs CH1 transition/steady workers.");
    semanticFunction(0x58A1CL, "f33_snapshot_ch2_inputs", v)
        .setComment("Save PMR; FFC0 protects5CA3A/FDC3C acquisition snapshot; FF80 protects5CF1C/FDC50 control snapshot; "
            + "restore entryPMR. These are ordered windows, not an all-task atomic generation.");
    semanticFunction(0x58B1AL, "f33_snapshot_foreground_inputs", v)
        .setComment("Save PMR; FFC0\u21925D12C/FDC64 acquisition views, FF80\u21925D5E0/FDC78 control views, FF00\u21925D6DC/FDC8C "
            + "monitor/health/service views; restore entryPMR. Not one interrupt-free snapshot and not physical input "
            + "freshness.");
    semanticFunction(0x5CA3AL, "f33_snapshot_ecu_ch2_acquisition", v)
        .setComment("Copy current ECU acquisition/status into CH2-specific views;822C/8238 banks become622C/6238. Called "
            + "in58A1C FFC0 window; foreground6450/645C copies remain a different generation.");
    semanticFunction(0x5D12CL, "f33_snapshot_ecu_foreground_acquisition", v)
        .setComment("Copy current ECU acquisition/status into foreground-specific views;822C/8238 banks become6450/645C. "
            + "Called in58B1A FFC0 window; does not overwrite CH2 copies622C/6238.");
    semanticFunction(0xC1B84L, "f33_snapshot_control_ch2_acquisition", v)
        .setComment("CopyEC00..EC24 publication into AF74..AF98 CH2 input view, preserving byte/halfword/word widths. FDC3C is "
            + "called within58A1C FFC0 window. ForegroundAFD4..AFF8 is separately sampled.");
    semanticFunction(0xC1C9EL, "f33_snapshot_control_foreground_acquisition", v)
        .setComment("CopyEC00..EC24 publication into AFD4..AFF8 foreground view, preserving widths. FDC64 is called "
            + "within58B1A FFC0 window; no synchronization with a previously sampled CH2 bank is implied.");
    semanticFunction(0xC1BE4L, "f33_snapshot_control_ch2_feedback", v)
        .setComment("CopyACxx controller fields andED00..ED12 outputs into AF9C..AFCA CH2 view under the58A1C FF80 window, "
            + "after the separately masked acquisition copy.");
    semanticFunction(0xC1CFEL, "f33_snapshot_control_foreground_feedback", v)
        .setComment("CopyB354/B3A0/B3A6/B430/B436, ACxx controller fields andED00..ED12 outputs into AFFC..B062 foreground "
            + "view under58B1A FF80, before monitor/health/service snapshot window.");
    semanticFunction(0x58074L, "f33_publish_foreground_ecu_outputs", v)
        .setComment("Publish current ECU state into F000/F1xx/F2xx shared outputs, including7F68\u2192F000 and6954\u2192F204. Called "
            + "after generated ECU initialization and by foreground transition/steady workers; publication does not make "
            + "all inputs temporally coherent.");
    semanticFunction(0xBCD62L, "f33_refresh_foreground_control_projection", v)
        .setComment("Prepare ACxx/ADxx control projection from foreground sampled inputs and current software state. "
            + "NormalizeF000 as0\u21920,2\u21922,3\u21924,other\u21921. ACC0 holds outside live0400 with groupedstatus16!=5A; inside that "
            + "gate it becomes(F09B==0 && F000==0). Integer scale conversions do not establish physical units. Called "
            + "only for captured modes0300..0522.");
    semanticFunction(0xBF3AAL, "f33_publish_foreground_control_outputs", v)
        .setComment("Publish control/health/current-limit state intoE800+ and copy immutable calibration bounds. Includes "
            + "liveB11A\u2192E8CC after the mode arbiter. Central transition/steady workers call this last even for mode0; "
            + "common initializationBF97A does not.");
    semanticFunction(0xB1C54L, "f33_start_mode100_after_foreground_restart", v)
        .setComment("After common warm reinitialization and all task input snapshots, transition live mode to0100 through real "
            + "entry/exit hooks. Not directE8CC publication; subsequent foreground dispatch owns the published "
            + "generation.");
    semanticFunction(0xC214CL, "f33_dispatch_control_foreground_transition", v,
        new ParameterImpl("cadence_mask", u32, currentProgram),
        new ParameterImpl("captured_mode", u32, currentProgram),
        new ParameterImpl("previous_mode", u32, currentProgram))
        .setComment("Use low16 new/old captured mode to run crossing-only initializers plus admitted steady components, with "
            + "cadence bits1/4 controlling slower work. Health is active above0100; current limit producers above01FF; "
            + "projectionBCD62 only0300..0522. Reconcile/advance live mode after producers, then publishBF3AA; later "
            + "workers still use captured arguments.");
    semanticFunction(0xC26A4L, "f33_dispatch_control_foreground_steady", v,
        new ParameterImpl("cadence_mask", u32, currentProgram),
        new ParameterImpl("captured_mode", u32, currentProgram))
        .setComment("Run components admitted by low16 captured mode and cadence bits, without crossing initializers. Health "
            + "above0100 precedes nonthermal/thermal limit producers above01FF; projection only0300..0522. "
            + "Reconcile/advance live mode, then publishBF3AA even when capturedmode0. No atomic change of other task "
            + "generations.");
  }
  private void annotateNonthermalCurrentLimits() throws Exception {
    semanticFunction(0xBA962L, "f33_reset_owner5_release_state", VoidDataType.dataType)
        .setComment("Clear owner5 request/accumulator/release state to0; BCAB=5A. Restrictive entry state, not nominal.");
    semanticFunction(0xBA97EL, "f33_decay_owner5_limit_request", UnsignedIntegerDataType.dataType)
        .setComment("Seed on first use from BCCC; retain k950 and unsigned16.16 decay toward0; snap<=128. Return full unsigned "
            + "R10.");
    semanticFunction(0xBAA18L, "f33_release_owner5_limit_request", UnsignedIntegerDataType.dataType,
        new ParameterImpl("target", UnsignedIntegerDataType.dataType, currentProgram))
        .setComment("Use low16 target; conditional hold or fast/ordinary quadratic release, mode-change rebase. Reset "
            + "decay-init and reseed decayaccumulator from returned request.");
    semanticFunction(0xBAAD8L, "f33_publish_owner5_limit_request", VoidDataType.dataType)
        .setComment("Publish owner5 from active decay, conditional release or retained hold. Family0500 with alreadyzero skips "
            + "decay; BCAA active and BCAB report markers remain distinct.");
    semanticFunction(0xBAB58L, "f33_reset_owner4_release_state", VoidDataType.dataType)
        .setComment("Set owner4 previous/base22170 and accumulator22170<<16; clear release mode, control mode and count.");
    semanticFunction(0xBAB72L, "f33_release_owner4_limit_request", UnsignedIntegerDataType.dataType)
        .setComment("Release owner4 toward22170 with conditional hold, k115828/4666 and mode-change quadratic rebase; clear its "
            + "decay accumulator.");
    semanticFunction(0xBAC2CL, "f33_force_owner4_nominal_request", UnsignedIntegerDataType.dataType)
        .setComment("Clear release mode and accumulator, return full22170; accumulator is0, not nominal<<16.");
    semanticFunction(0xBAC3AL, "f33_decay_owner4_limit_request", UnsignedIntegerDataType.dataType,
        new ParameterImpl("coefficient", UnsignedIntegerDataType.dataType, currentProgram))
        .setComment("Use low16 coefficient*50; mismatched previous/high16 accumulator reseeds from common BCCC, filter toward0 "
            + "and snap<=128.");
    semanticFunction(0xBAC9CL, "f33_force_owner4_zero_request", UnsignedIntegerDataType.dataType)
        .setComment("Clear release mode and decayaccumulator and return0.");
    semanticFunction(0xBACA8L, "f33_publish_owner4_limit_request", VoidDataType.dataType)
        .setComment("BCBD1 nominal,2 k250 decay,3 k6550 decay,4 zero,others conditional quadratic release; publish owner4 and "
            + "BCC2.");
    semanticFunction(0xBACF8L, "f33_set_owner4_limit_mode", VoidDataType.dataType,
        new ParameterImpl("mode", UnsignedIntegerDataType.dataType, currentProgram))
        .setComment("Store low8 mode toBCBD. Direct reference only from thunkFDFC6; no normal caller inferred.");
    semanticFunction(0xBAD02L, "f33_stage_absolute_limit_seeds", VoidDataType.dataType)
        .setComment("BCC8=symmetric sat_abs(AFE2), BCCA=sat_abs(AFE0), BCCC=min those two. Distinct owner8 seed versus common "
            + "owner4/5 seed.");
    semanticFunction(0xBAD46L, "f33_reset_owner8_release_state", VoidDataType.dataType)
        .setComment("Set owner8 request/base22170, accumulatornominal, mode/count0. Does not initialize active delayBCD8.");
    semanticFunction(0xBAD5EL, "f33_follow_owner8_qualification_floor", UnsignedIntegerDataType.dataType,
        new ParameterImpl("coefficient", UnsignedIntegerDataType.dataType, currentProgram))
        .setComment("After calibrated unsigned delay, filter toward B08A; coherency mismatch seeds BCC8; snap when filtered "
            + "output<target+128. Exact coefficient/delay0 produces B08A immediately.");
    semanticFunction(0xBADE2L, "f33_release_owner8_limit_request", UnsignedIntegerDataType.dataType)
        .setComment("When channelsclear, conditionally hold or quadraticrelease toward22170 using k117028/4663; clear "
            + "decayaccumulator anddelay.");
    semanticFunction(0xBAE9EL, "f33_publish_owner8_limit_request", VoidDataType.dataType)
        .setComment("B082&3 chooses qualification-floor path; otherwise retained quadraticrelease. Publish owner8 andBCD6.");
    semanticFunction(0xBAEE6L, "f33_reset_owner1_qualification_state", VoidDataType.dataType)
        .setComment("Clear qualification/counters/baseline; target22170, persisted-derived admission default5A, initmarker0. "
            + "BCF0 request reset is separateBB16C.");
    semanticFunction(0xBAF06L, "f33_initialize_owner1_persisted_admission", VoidDataType.dataType)
        .setComment("Only F027=5A admits persisted-derived decision; set BCE2=5A iff F1E0==0 and signedF182<0, else0; "
            + "publishBCE3=5A.");
    semanticFunction(0xBAF3EL, "f33_qualify_owner1_limit_state", VoidDataType.dataType)
        .setComment("Retained states0/11/22/33 qualify signed snapshot relationships, enter/release counters and reversal; "
            + "state22 maps F174 with AF06C and BEE2 gainAF084 into targetBCE8. Units unassigned.");
    semanticFunction(0xBB16CL, "f33_reset_owner1_limit_request", VoidDataType.dataType)
        .setComment("Initialize retained requestBCF0 to22170 only.");
    semanticFunction(0xBB176L, "f33_publish_owner1_limit_request", VoidDataType.dataType)
        .setComment("Use retained qualificationstate:0 +28 release,11 -28 decay,22 tiered13/10/4 decay or+28 recovery toward "
            + "target,33 nominal. Narrow arithmetic before final signed clamp[0,22170], publish owner1.");
    semanticFunction(0xBB2F6L, "f33_reset_owner6_calibration_envelope", VoidDataType.dataType)
        .setComment("Seed signed AFDC and unsignedB084 retained filters; nominal request/cap/candidates; clear markers, "
            + "transition/family state.");
    semanticFunction(0xBB33CL, "f33_select_owner6_calibration_family", VoidDataType.dataType)
        .setComment("Accept B30C55AAAA55 orAA5555AA; otherwise use exactfallbackAF1B8=AA5555AA.");
    semanticFunction(0xBB362L, "f33_update_owner6_gate_and_axis_filter", VoidDataType.dataType)
        .setComment("Opposite-sign AFDC/AFE0 dwell selects bypass marker; gated BEE2 hysteresis retains bank latch. Signed AFDC "
            + "filter k30573 uses signedDIVQ65536.");
    semanticFunction(0xBB43AL, "f33_update_owner6_source_transition", VoidDataType.dataType)
        .setComment("Clamp unsignedB084[2304,4096]; B1A9 override2816/cap22170; override-mode transition filterk6547 "
            + "untilresidual<26. Preserve retained mode/hysteresis.");
    semanticFunction(0xBB544L, "f33_publish_owner6_calibration_envelope", VoidDataType.dataType)
        .setComment("Select real family/bank map pair and extrapolation, recordrawcandidate; signed cap/floor gives "
            + "exactdesired22170. AF1760 immediate output with inclusive3 snap. Publish owner6.");
    semanticFunction(0xBB71CL, "f33_update_owner6_calibration_envelope", VoidDataType.dataType)
        .setComment("Compose real familyselection,gate/axisfilter,sourcetransition andscalarpublication in order.");
    semanticFunction(0xBBFBCL, "f33_reset_owner3_shutdown_request", VoidDataType.dataType)
        .setComment("Nominal22170 request/accumulator; active and cutoff latch0,cachedcoefficient0. Qualification reset "
            + "isBC0F8.");
    semanticFunction(0xBBFD4L, "f33_publish_owner3_shutdown_request", VoidDataType.dataType)
        .setComment("Active qualificationlow input decayswithk1300, reportsA1failure andactions; inclusive128 cutoff latch "
            + "publishesmask70017001. Holdbandkeepsoutput; inactivepassreleasesnominal andclearsacc/latch.");
    semanticFunction(0xBC0F8L, "f33_reset_owner3_signal_qualification", VoidDataType.dataType)
        .setComment("Clear BDA8/BDA9 and seed entrycount4/releasecount1.");
    semanticFunction(0xBC114L, "f33_qualify_owner3_shutdown_signal", VoidDataType.dataType)
        .setComment("AdmitB1A7=5A,B20E0/33,B1BC0. Strict low<2125 withentryinhibit andcount4; release onlystrict>2176 "
            + "withcount1. Equality/holdbehaviorretained.");
    semanticFunction(0xBC196L, "f33_set_owner3_entry_inhibit", VoidDataType.dataType,
        new ParameterImpl("inhibit", UnsignedIntegerDataType.dataType, currentProgram))
        .setComment("Store low8 entryinhibitBDAA; does not itself clearactivequalification.");
    semanticFunction(0xBC19EL, "f33_reset_owner2_deficit_request", VoidDataType.dataType)
        .setComment("Reset feedbackerrorstates/accumulators,nominalbase/request/minimum,entry2/release200/recovery2 "
            + "andactioncount520. ExternalBDB2 unchanged.");
    semanticFunction(0xBC1E4L, "f33_publish_owner2_deficit_limit_request", VoidDataType.dataType)
        .setComment("B1A7 andowner5activegate; delayed2304/3072 qualification ofEE20; "
            + "retainedfast/slow/highpasssignedfilters,base/minimum feedbackandsteppedrelease. Publishowner2 "
            + "andaction9/class3 countdown.");
    semanticFunction(0xBC5F4L, "f33_set_owner2_entry_inhibit", VoidDataType.dataType,
        new ParameterImpl("inhibit", UnsignedIntegerDataType.dataType, currentProgram))
        .setComment("Store low8 entryinhibitBDB2; no implicitreset ofqualificationorrequest.");
    semanticFunction(0x35CECL, "f33_update_limit_budget_branch0", VoidDataType.dataType)
        .setComment("71ECbit0 disables branch; otherwise selectedconstant minus62BC*62D4,dividebyabs62D6 "
            + "orboundonzero,clamp\u00b126604 into6AFC. No physicalunitsassigned.");
    semanticFunction(0x35D58L, "f33_update_limit_budget_branch1", VoidDataType.dataType)
        .setComment("Companionbranch using71ECbit1,62C0*62D8 andabs62DA,clamp\u00b126604 "
            + "into6B08;otherchannelbitselectsalternateconstant.");
    semanticFunction(0x35DC2L, "f33_reset_owner9_budget_limit_state", VoidDataType.dataType)
        .setComment("Seedfilteredbudget,maprequest/finalrequest26604, bothaccumulators26604<<16; "
            + "clearnegativequalificationandreleasemarkers/counts.");
    semanticFunction(0x35DE6L, "f33_map_owner9_budget_limit", UnsignedIntegerDataType.dataType,
        new ParameterImpl("budget", UnsignedIntegerDataType.dataType, currentProgram))
        .setComment("Zeroextend low16budget; map38678 withsigned6422 selector, signedcap22170 andzeroextendresult.");
    semanticFunction(0x35E06L, "f33_follow_owner9_limit_request", UnsignedIntegerDataType.dataType,
        new ParameterImpl("target", UnsignedIntegerDataType.dataType, currentProgram))
        .setComment("Enabledmode33 withcalibratedrisegain0 holdsincreasesandpassesdecreases, thenclamp[0,22170]. "
            + "Othermode11lowpass/mode22stepremainnotselectedbythisimage.");
    semanticFunction(0x35EE0L, "f33_publish_owner9_budget_limit", VoidDataType.dataType)
        .setComment("Clampbranchsum[0,26604],filterunsignedbudget,mapandretainrequest. Sustainednegative62DCmarkerA5 "
            + "or7827/7937nonzero bypassesrequesttonominal22170. RealFDFD4callerpublishesowner9.");
    semanticFunction(0x38678L, "f33_lookup_signed_five_map_signal", IntegerDataType.dataType,
        new ParameterImpl("value", IntegerDataType.dataType, currentProgram),
        new ParameterImpl("selector", ShortDataType.dataType, currentProgram))
        .setComment("Symmetricabs signedinput bounded65535, interpolate128-grid unsignedordinates from5 realmapsselected "
            + "bysignedselector andQ10crossmapweight,restoreinputsign. No physicalaxisunitsclaimed.");
    semanticFunction(0xD12D2L, "f33_filter_unsigned_sample_accumulator", VoidDataType.dataType,
        new ParameterImpl("sample", new PointerDataType(UnsignedShortDataType.dataType, 4), currentProgram),
        new ParameterImpl("coefficient", UnsignedIntegerDataType.dataType, currentProgram),
        new ParameterImpl("output", new PointerDataType(UnsignedShortDataType.dataType, 4), currentProgram),
        new ParameterImpl("accumulator", new PointerDataType(UnsignedIntegerDataType.dataType, 4), currentProgram))
        .setComment("8-bytesample prevU16,targetU16,accU32. Coefficientoutside1..65535 becomes65536. Low32 unsigned "
            + "recurrence,logicalhigh16output andwordaccumulatorthroughr8/r9. Reusehelper,nonewphysicalmodel.");
    semanticFunction(0xD1D0AL, "f33_store_signed_halfword_max", VoidDataType.dataType,
        new ParameterImpl("value", ShortDataType.dataType, currentProgram),
        new ParameterImpl("bound", ShortDataType.dataType, currentProgram),
        new ParameterImpl("output", new PointerDataType(ShortDataType.dataType, 4), currentProgram))
        .setComment("Sign-extend low16 inputs and store their signed maximum throughR8. R10 is not a defined return; the only "
            + "live caller is owner1 BB176. Explicit output pointer prevents a lost retained-request update in "
            + "decompilation.");
    semanticFunction(0xD1D3CL, "f33_store_signed_halfword_min", VoidDataType.dataType,
        new ParameterImpl("value", ShortDataType.dataType, currentProgram),
        new ParameterImpl("bound", ShortDataType.dataType, currentProgram),
        new ParameterImpl("output", new PointerDataType(ShortDataType.dataType, 4), currentProgram))
        .setComment("Sign-extend low16 inputs and store their signed minimum throughR8. R10 is not a defined return; the only "
            + "live caller is owner1 BB176. Explicit output pointer prevents a lost retained-request update in "
            + "decompilation.");
    semanticData(0xAF034L, UnsignedIntegerDataType.dataType, "f33_owner5_fast_release_coefficient",
        "Raw32 quadraticrelease scalar115828; not pointer/address. MULU square/coefficient dataflow in corresponding release helper.");
    semanticData(0xAF038L, UnsignedIntegerDataType.dataType, "f33_owner5_normal_release_coefficient",
        "Raw32 quadraticrelease scalar4666; not pointer/address. MULU square/coefficient dataflow in corresponding release helper.");
    semanticData(0xAF048L, UnsignedIntegerDataType.dataType, "f33_owner4_fast_release_coefficient",
        "Raw32 quadraticrelease scalar115828; not pointer/address. MULU square/coefficient dataflow in corresponding release helper.");
    semanticData(0xAF04CL, UnsignedIntegerDataType.dataType, "f33_owner4_normal_release_coefficient",
        "Raw32 quadraticrelease scalar4666; not pointer/address. MULU square/coefficient dataflow in corresponding release helper.");
    semanticData(0xAEFA0L, UnsignedIntegerDataType.dataType, "f33_owner8_fast_release_coefficient",
        "Raw32 quadraticrelease scalar117028; not pointer/address. MULU square/coefficient dataflow in corresponding release helper.");
    semanticData(0xAEFA4L, UnsignedIntegerDataType.dataType, "f33_owner8_normal_release_coefficient",
        "Raw32 quadraticrelease scalar4663; not pointer/address. MULU square/coefficient dataflow in corresponding release helper.");
  }

  private void annotateHealthCoherencePolicy() throws Exception {
    semanticFunction(0xB3CC8L, "f33_initialize_source_coherence_history", VoidDataType.dataType)
        .setComment("Initialize only redundant B18E to0; preserve receive-generation B195/B196 and counters. Not a cold "
            + "application reset.");
    semanticFunction(0xB3CE2L, "f33_reset_current_source_coherence_observations", VoidDataType.dataType)
        .setComment("Clear B198/B19A/B19C,B190/B191 and redundant summary; preserveB195/B196 and separateB193/B194/B19E/B1A0.");
    semanticFunction(0xB3D08L, "f33_qualify_packed_channel_zero_status", UnsignedIntegerDataType.dataType,
        new ParameterImpl("count", new PointerDataType(UnsignedShortDataType.dataType, 4), currentProgram),
        new ParameterImpl("packed_status_qualifier_limit", UnsignedIntegerDataType.dataType, currentProgram),
        new ParameterImpl("current_tag", UnsignedIntegerDataType.dataType, currentProgram),
        new ParameterImpl("expected_tag", UnsignedIntegerDataType.dataType, currentProgram),
        new ParameterImpl("generation_armed", UnsignedCharDataType.dataType, currentProgram))
        .setComment("R6 counter; R7 packed byte status,byte qualifier,uint16 threshold; R8 current tag; R9 expected; fifth "
            + "argument low byte at incomingSP. Armed!=5A preserves count and returns0. Otherwise "
            + "exactA5/status0/B084>=2304/tag match or33333333/FFFFFFFF; strict uint16 count>limit. FullR10=0/1.");
    semanticFunction(0xB3D7CL, "f33_qualify_secondary_received_status_delay", UnsignedIntegerDataType.dataType)
        .setComment("BEDD5A,BEDE>=512,B084>=2304; strictB19C>200, otherwise reset0. Independent ofB196.");
    semanticFunction(0xB3DC0L, "f33_refresh_gated_source_coherence_indicator", VoidDataType.dataType,
        new ParameterImpl("source_history", UnsignedIntegerDataType.dataType, currentProgram))
        .setComment("Only called byB3F44 under entryB1D1==5A; recomputeB192. Unlike summarybit3, standalonebit1 is not direct "
            + "trigger; selected-problem branch acceptsbit1 orF093bit1.");
    semanticFunction(0xB3E50L, "f33_update_latched_secondary_channel_qualification", VoidDataType.dataType)
        .setComment("IndependentB19E/B1A0 pair, shared generation gateB196; stickyB194bit0 thenB1935A; called under "
            + "entryB1D6==5A.");
    semanticFunction(0xB3F2AL, "f33_is_health_or_command_completion_observed", UnsignedIntegerDataType.dataType)
        .setComment("FullR10=1 onlyB20E==11 orB190==5A; numeric state22 alone does not assert this predicate.");
    semanticFunction(0xB3F44L, "f33_update_source_coherence_history", VoidDataType.dataType)
        .setComment("Vote/republish stickyB18E; detect admitted receive-generation edge; currentchannel delays andB191 lowbits; "
            + "conditionalB192 and separate sticky qualifier; OR aggregatebit3 and prior qualified/commandcompletionbit4. "
            + "Always saveBE7E->B195. BE7E is consumed route30 generation, not a global coherent receive epoch "
            + "or B6 command generation; frozen decoding can still consume the edge.");
    semanticFunction(0xB4158L, "f33_clear_source_coherence_reentry_history", VoidDataType.dataType)
        .setComment("ClearB198/B19A/B19C andB192; publishB18E&F4 clearingbits0/1/3 only. PreserveB191,B195/B196 and separate "
            + "sticky pair.");
    semanticFunction(0xB4180L, "f33_close_health_receive_generation_qualification", VoidDataType.dataType)
        .setComment("Clear onlyB196. Invoked by qualifiedB20E11->22; does not rewriteB195.");
    semanticFunction(0xB4186L, "f33_reset_secondary_channel_qualification_history", VoidDataType.dataType)
        .setComment("ClearB19E/B1A0,B193 andonlybit0ofB194.");
    semanticFunction(0xB419AL, "f33_latch_health_command_completion", VoidDataType.dataType)
        .setComment("SetB190=5A; laterB3F2A OR-latches sourcehistorybit4; no mode request here.");
    semanticFunction(0xB41AEL, "f33_initialize_health_record_lifecycle", VoidDataType.dataType)
        .setComment("Only redundantB1A4=0; preserve neighboring one-shot and stage-entry history.");
    semanticFunction(0xB41C8L, "f33_reset_health_record_lifecycle_entry", VoidDataType.dataType)
        .setComment("ClearB1A5/B1A7 and redundantB1A4; distinct fromB41AE initializer.");
    semanticFunction(0xB41E8L, "f33_publish_health_lifecycle_mode_indicator", VoidDataType.dataType)
        .setComment("B1A6 zero for family<=0300 or0400withB1BD5A, otherwise5A.");
    semanticFunction(0xB4214L, "f33_advance_health_record_lifecycle", VoidDataType.dataType)
        .setComment("VoteB1A4 fallback11. Sticky sourcehistorybit3 enters family-specific record "
            + "invalidation/request23/lifecycle11; old11+completionbit4 enters22. State0->11 cannot also complete same "
            + "call. Republish lifecycle triplet.");
    semanticFunction(0xB49E4L, "f33_qualify_health_source_recovery", VoidDataType.dataType)
        .setComment("Qualify strictB0802125..4096 orF0FD1/F0FE0; on recovery event8Dpass/cache flags/sourcehistory "
            + "reentry-clear; B1C8bit4->bit2. ConditionalB192 feedback clearsB1D1.");
    semanticFunction(0xB4AB6L, "f33_latch_health_source_unavailability", VoidDataType.dataType)
        .setComment("Gated call fromB4EF4: latchB1CE andB1C8bit4 while clearingbit2; reportevent8D failure independently of "
            + "health publication.");
    semanticFunction(0xB4C4CL, "f33_update_health_secondary_qualification_handshake", VoidDataType.dataType)
        .setComment("StageB1D5/B1D6 from paired receivedstatuses andB193. Later exact0/0 reset branch wins, callsB4186 and "
            + "returnsstageA5; no invented permission.");
    semanticFunction(0xB4D26L, "f33_latch_qualified_health_entry_conditions", VoidDataType.dataType)
        .setComment("Existing staged-source eligibility plus conditionedmulti-input/count paths OR-latchB1C8bit3/B1CD. Preserve "
            + "numeric software policy; physical meanings unknown.");
    semanticFunction(0xB4E4EL, "f33_latch_qualified_health_completion_conditions", VoidDataType.dataType)
        .setComment("UnderB1CD5A, strict2125<B080<4096: after40 counts ORbit0; family0800 ORbit1 immediately. Outside resets "
            + "counter not latchedbits.");
    semanticFunction(0xB4EF4L, "f33_update_qualified_health_source_policy", VoidDataType.dataType)
        .setComment("Advance received/conditioned recovery policy, gated unavailability/fade, secondary handshake, "
            + "entry/completion latches; called afterB3F44/B4214 beforeB4FFC.");
    semanticFunction(0xB4F52L, "f33_initialize_qualified_health_state", VoidDataType.dataType)
        .setComment("Initialize redundantB20E0 only; not stickyB20F or source-generation reset.");
    semanticFunction(0xB4F6CL, "f33_reset_qualified_health_state_entry", VoidDataType.dataType)
        .setComment("Initialize redundantB20E0 andclearB20F; doesnotclearB195/B196.");
    semanticFunction(0xBE65CL, "f33_refresh_first_health_source_cache", VoidDataType.dataType)
        .setComment("Existing arithmetic uses F194 from route26. F0FB1/0/other->BE79A5/5A/FF; F0FB and F052 "
            + "both copy route30 payload bit8031, not independent physical channels.");
    semanticFunction(0xBE6E0L, "f33_refresh_second_health_source_cache", VoidDataType.dataType)
        .setComment("F0521/0/other->BE7AA5/5A/FF; BE7B uses overrideB18F when not1; save F052 inBE78. "
            + "Normal58074 duplicates route30 payload bit8031 into both F052 and F0FB.");
    semanticFunction(0xBE712L, "f33_refresh_health_channel_classifications", VoidDataType.dataType)
        .setComment("PublishBE7C/BE7D0/11/22 from paired status gates and low F057/F051 bits. Both sources "
            + "copy route30 receive status802F, not payload bits or persisted selection tags.");
    semanticFunction(0xBE778L, "f33_refresh_health_received_source_generation", VoidDataType.dataType)
        .setComment("Refresh both caches and classifications, then F13F->BE7E on admitted cadence bit1. "
            + "F13F is route30 consumed copy generation; it can advance while payload decoding is frozen. "
            + "Arithmetic sampleF194 comes from separate route26, so this is not simultaneous freshness.");
    semanticFunction(0xD1306L, "f33_reset_application_latched_monitor", VoidDataType.dataType,
        new ParameterImpl("state", new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33LatchedMonitorState"), 4), currentProgram))
        .setComment("Application copy of ten-byte latched-monitor reset: clear+0word,+4/+6/+8halfwords; preserve "
            + "allocationtail.");
    semanticFunction(0xD1386L, "f33_step_application_latched_monitor", UnsignedIntegerDataType.dataType,
        new ParameterImpl("state", new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33LatchedMonitorState"), 4), currentProgram),
        new ParameterImpl("limits", new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33MonitorLimits"), 4), currentProgram),
        new ParameterImpl("callbacks", new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33TwoSidedMonitorCallbacks"), 4), currentProgram))
        .setComment("Application-region equivalent of6AE7C. Existing ten-byte state and13callbacks; strictcounters, "
            + "terminalfailure22, fullR10=11. Reuseexistingtypes, not a secondmonitorconvention.");
    semanticFunction(0xBB248L, "f33_initialize_lifecycle_difference_monitor", VoidDataType.dataType)
        .setComment("D1306resetofBCF4ten-bytestate.");
    semanticFunction(0xBB258L, "f33_reset_lifecycle_difference_monitor_entry", VoidDataType.dataType)
        .setComment("SameD1306resetofBCF4; separateentryowner.");
    semanticFunction(0xBB268L, "f33_step_lifecycle_difference_monitor", VoidDataType.dataType)
        .setComment("D1386(BCF4,AF050,AECA0),limits0/6; scheduledbyexistingmaskbit4.");
    semanticFunction(0xBB284L, "f33_classify_lifecycle_conditioned_sample_difference", UnsignedIntegerDataType.dataType)
        .setComment("B1A4!=11->44. Else signedconvertedB02CminusB00C>=1920,BEDE>1280,BEF0==11->22; otherwise11. No physicalunit "
            + "or OEMmeaning inferred.");
    semanticFunction(0xBB2DCL, "f33_confirm_lifecycle_difference_diagnostic", VoidDataType.dataType)
        .setComment("Latchdiagnosticstatusslot10through545DE, thenconditionallysubmitrecord8/capture800through51CF6. No "
            + "directmoderequest.");
    semanticFunction(0xB451AL, "f33_update_health_status_delay_summaries", VoidDataType.dataType)
        .setComment("B4346 classification0/1/3 is retainedinR10 acrossB4370(noR10write), thenpassedtoB4430; "
            + "B4370maydestructivelyshiftR6. BothfeedB44E0current/heldsummaries. Do notinventsecondpermissionreturn.");
    semanticFunction(0xB4346L, "f33_classify_received_status_delay", UnsignedIntegerDataType.dataType)
        .setComment("F058 bit0 clear resetsB1B4 and returns0; otherwise return1 until strict count>268, then3. "
            + "Confirmed count holds. R10 is reused across the following first-window helper.");
    semanticFunction(0xB4370L, "f33_update_first_health_status_window", VoidDataType.dataType,
        new ParameterImpl("classification", UnsignedIntegerDataType.dataType, currentProgram))
        .setComment("UnderBE9C5A, received-status windows use1200/2000 counters and current B191/classification inhibition. "
            + "Inactive hold release uses200; publishB1AA/B1AB. Exact192-byte leaf preservesR10 while shiftingR6. "
            + "Inline real p-code so B451A forwards its original classifier to the second window.");
    getFunctionAt(toAddr(0xB4370L)).setInline(true);
    semanticFunction(0xB4430L, "f33_update_second_health_status_window", VoidDataType.dataType,
        new ParameterImpl("classification", UnsignedIntegerDataType.dataType, currentProgram))
        .setComment("CompanionB1AC/B1AD window. Initial F04E1 branch uses B191/classification inhibition; alternate "
            + "F04C!=0/B1BD5A branch does not. Distinct1200/2000 active counters and200-observation held release.");
    semanticFunction(0xB44E0L, "f33_publish_current_and_held_health_windows", VoidDataType.dataType)
        .setComment("Rebuild B1A8 from currentB1AA/B1AC, B1A9 from heldB1AB/B1AD. Current inhibits owner1 "
            + "qualification; held selects owner6 source override. No meaningful scalar return contract.");
    semanticFunction(0xB4FFCL, "f33_advance_qualified_health_state", VoidDataType.dataType)
        .setComment("VoteB20E/B20C/B20D with fallback0 only on uncorrectable disagreement. States0/33 take11 first onB1C8 "
            + "bit3/5; otherwise0\u219233 onbit4 and33\u21920 onbit2.11\u219222 onbit0/1 latchesB20F and clearsB196. Route new state "
            + "before publishing;22 does not self-clear. Numeric software phases, not OEM failure labels.");
    semanticFunction(0xB4F8AL, "f33_route_qualified_health_mode_requests", VoidDataType.dataType,
        new ParameterImpl("qualified_state", UnsignedCharDataType.dataType, currentProgram))
        .setComment("State11 requests1, with BCB0==0 in0400/0500;22 requests1 only in0400/0500 and2 in0700/0800. Exact0522 also "
            + "requiresAFCE!=11 andBCB0==0. Never cancels request1. Routing consumes the new qualified state before "
            + "redundant publication.");
    semanticData(0xFEBEB18CL, UnsignedCharDataType.dataType, "f33_source_coherence_summary_xor55",
        "Encoded peer of stickyB18E, XOR55; next byte XORAA.");
    semanticData(0xFEBEB18EL, UnsignedCharDataType.dataType, "f33_source_coherence_history",
        "Sticky OR bits0 channel qualification,1 secondary qualification,3 aggregate trigger,4 qualified-state11 or software completion; D268C publishes redundant peers.");
    semanticData(0xFEBEB191L, UnsignedCharDataType.dataType, "f33_current_source_coherence_observations",
        "Low two bits rebuilt per B3F44 invocation; upper bits preserved; not interchangeable with stickyB18E.");
    semanticData(0xFEBEB195L, UnsignedCharDataType.dataType, "f33_previous_health_receive_generation",
        "Always updated fromBE7E, even whileF000>=2 blocks edge admission.");
    semanticData(0xFEBEB196L, UnsignedCharDataType.dataType, "f33_health_receive_generation_armed",
        "Latch5A on changedBE7E only whenF000<2. Shared current and independent sticky qualifier pairs; B20E11->22 closes it.");
    semanticData(0xFEBEBCF4L, currentProgram.getDataTypeManager().getDataType("/CamryF33/F33LatchedMonitorState"), "f33_application_lifecycle_difference_monitor_state",
        "Exact ten-byte state; do not absorb adjacent allocation padding.");
    semanticData(0xAF050L, currentProgram.getDataTypeManager().getDataType("/CamryF33/F33MonitorLimits"), "f33_application_lifecycle_difference_monitor_limits",
        "Passing0/failing6; strict counter crossings.");
    semanticData(0xAECA0L, currentProgram.getDataTypeManager().getDataType("/CamryF33/F33TwoSidedMonitorCallbacks"), "f33_application_lifecycle_difference_monitor_callbacks",
        "Normal/failing classifierBB284; confirm_failingBB2DC; every other callback null. Existing13-pointer layout.");
  }


  private void annotateResidentFlashOperationLifecycle() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
    StructureDataType policy = new StructureDataType(category, "F33BootRangePolicyEntry", 0);
    policy.setPackingEnabled(true);
    policy.add(u32, "lower", "Inclusive start.");
    policy.add(u32, "upper", "Inclusive end.");
    policy.add(u32, "kind_mask", "Bit(kind&31), current33.");
    policy.add(u8, "storage_class", "0 CodeFlash,1 resident RAM; not operation class2B17.");
    policy.add(u8, "completion_selector", "Current0; used for completion-bit updates.");
    policy.add(u16, "reserved", null);
    DataType policyType = resolve(policy);
    semanticData(0x8DA0L, new ArrayDataType(policyType, 3, 16), "f33_boot_service_range_policy",
        "32D2/3318 explicitly reject a wrapped last address before applying these range/kind predicates.");
    StructureDataType crc = new StructureDataType(category, "F33BootCrcDescriptor", 0);
    crc.setPackingEnabled(true);
    crc.add(u32, "base", "Region data address.");
    crc.add(u32, "length", "CRC byte extent.");
    crc.add(new PointerDataType(u32, 4), "base_metadata", "Word that must equal base.");
    crc.add(new PointerDataType(u32, 4), "length_metadata", "Word that must equal length.");
    DataType crcType = resolve(crc);
    semanticData(0x8DD0L, new ArrayDataType(crcType, 3, 16), "f33_boot_region_crc_descriptors",
        "Two CodeFlash regions and one downloaded RAM region; CRC acceptance is not physical programming proof.");
    StructureDataType region = new StructureDataType(category, "F33BootRegionDescriptor", 0);
    region.setPackingEnabled(true);
    region.add(u32, "lower", "Inclusive range start.");
    region.add(u32, "upper", "Inclusive range end.");
    region.add(u32, "authentication_trailer", "3392 lookup; not an executable callback.");
    region.add(u32, "marker_block", "33CC lookup; zero for RAM region.");
    region.add(u32, "counter_block", "3402 lookup; zero for RAM region.");
    region.add(u32, "crc_count", "Count of CRC descriptors.");
    region.add(new PointerDataType(crcType, 4), "crc_descriptors", "Descriptor array.");
    DataType regionType = resolve(region);
    semanticData(0x8E00L, new ArrayDataType(regionType, 3, 28), "f33_boot_regions",
        "Resident CodeFlash and RAM ranges; range-kind admission32D2/3318 is separate from335E lookup.");
    semanticData(0x86ECL, new ArrayDataType(u32, 39, 4), "f33_boot_flash_block_boundaries",
        "38 half-open block intervals: eight8KiB blocks then thirty32KiB blocks, ending100000.");
    FunctionDefinitionDataType blank = new FunctionDefinitionDataType(category, "F33BootBlankCheckCallback");
    blank.setReturnType(u32);
    blank.setArguments(new ParameterDefinition[] {
        new ParameterDefinitionImpl("address", u32, null),
        new ParameterDefinitionImpl("word_count", u32, null)});
    DataType blankType = currentProgram.getDataTypeManager().addDataType(blank, DataTypeConflictHandler.REPLACE_HANDLER);
    semanticData(0x86E4L, new PointerDataType(blankType, 4), "f33_boot_relocated_blank_check_entry",
        "FEBF11F0 corresponds to copied ROM8560 during boot; distinct from downloaded driver wordFEBF0FD0.");
    semanticFunction(0x335EL, "f33_boot_select_region_for_range", u32,
        new ParameterImpl("address", u32, currentProgram),
        new ParameterImpl("length", u32, currentProgram),
        new ParameterImpl("region", new PointerDataType(u32, 4), currentProgram))
        .setComment("Reject zero length; scan three28-byte8E00 records. First unsigned address>=lower and "
            + "modulo32(address+length-1)<=upper wins; write selector. No separate overflow or address<=upper guard. "
            + "Returns0found/1missing.");
    semanticFunction(0x3402L, "f33_boot_select_counter_block_for_range", u32,
        new ParameterImpl("address", u32, currentProgram),
        new ParameterImpl("length", u32, currentProgram),
        new ParameterImpl("counter_block", new PointerDataType(u32, 4), currentProgram))
        .setComment("Same inclusive modulo32 region search as335E, but output descriptor+16 counter-block address. Zero for RAM "
            + "region2; no implicit overflow guard.");
    semanticFunction(0x3438L, "f33_boot_crc_descriptor_count", u32,
        new ParameterImpl("region", u32, currentProgram))
        .setComment("Unsigned selector<3 returns region record+20 count; otherwise0. All exact records contain1.");
    semanticFunction(0x344CL, "f33_boot_crc_descriptors", new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33BootCrcDescriptor"), 4),
        new ParameterImpl("region", u32, currentProgram))
        .setComment("Unsigned selector<3 returns region record+24 descriptor pointer; otherwiseNULL. Include RAM region2, not "
            + "just boot/application image regions. Real leaf preserves R6 for the following3438 call in481A; inline its "
            + "exact instructions.");
    getFunctionAt(toAddr(0x344CL)).setInline(true);
    semanticFunction(0x3474L, "f33_boot_find_flash_block_start", u32,
        new ParameterImpl("address", u32, currentProgram),
        new ParameterImpl("block_start", new PointerDataType(u32, 4), currentProgram))
        .setComment("Search38 half-open intervals in39-word86EC boundary array. Write containing lower bound andreturn0; "
            + "otherwisewriteF8000 andreturn1.");
    semanticFunction(0x34A8L, "f33_boot_find_flash_block_end", u32,
        new ParameterImpl("address", u32, currentProgram),
        new ParameterImpl("block_end", new PointerDataType(u32, 4), currentProgram))
        .setComment("Search same38 half-open intervals. Write containing upper bound andreturn0; otherwisewrite100000 "
            + "andreturn1.");
    semanticFunction(0x34DAL, "f33_boot_get_flash_block_skip_flag", u32,
        new ParameterImpl("address", u32, currentProgram))
        .setComment("Return zero-extended2954[containing block index], or0 outside38 intervals.4332 skips lower erase only for "
            + "exact flag1. Do not infer a physical erased-state witness.");
    semanticFunction(0x3506L, "f33_boot_clear_flash_block_skip_flags", v,
        new ParameterImpl("first_block", u32, currentProgram),
        new ParameterImpl("last_block", u32, currentProgram))
        .setComment("If first<=last, clear2954 entries for covered successive intervals underFFFF PMR; stop after crossinglast. "
            + "RestoreentryPMR. Numeric block addresses, not interrupt callbacks.");
    semanticFunction(0x3552L, "f33_boot_check_relocated_blank_words", u32,
        new ParameterImpl("address", u32, currentProgram),
        new ParameterImpl("word_count", u32, currentProgram))
        .setComment("Invoke ROM86E4 pointerFEBF11F0, copied fromCF8560 by35E4, forwardingR6/R7 andreturningR10. This ECC-backed "
            + "blank check is distinct from programming callback[FEBF0FD0].");
    semanticFunction(0x3562L, "f33_boot_check_rounded_program_span_blank", u32,
        new ParameterImpl("address", u32, currentProgram),
        new ParameterImpl("length", u32, currentProgram))
        .setComment("Round nonzero byte length up256 with32-bit arithmetic, divideby4, andcall3552(address,word_count); "
            + "normalize nonzero resultto1. Length0 reaches wrapped arithmetic andzero wordcount; do not add absent "
            + "validation. Hardware ECC/test-mode feedback remains bounded.");
    semanticFunction(0x40A2L, "f33_boot_prepare_aligned_input_ring", u32,
        new ParameterImpl("address", u32, currentProgram),
        new ParameterImpl("length", u32, currentProgram),
        new ParameterImpl("aligned_address", new PointerDataType(u32, 4), currentProgram),
        new ParameterImpl("padded_length", new PointerDataType(u32, 4), currentProgram))
        .setComment("Length0returns1 unchanged. Otherwise alignaddressdown512, add low9bits tolength modulo32, fillthat manyFF "
            + "prefixbytes in1800 ring; publishproducer=prefix,consumer0 andreturn0. Realleaf preservesR6/R7/R9 for411A "
            + "subsequent40E0; inlineactualp-code. Lateradmission failure doesnotundo ringmutation.");
    getFunctionAt(toAddr(0x40A2L)).setInline(true);
    semanticFunction(0x40E0L, "f33_boot_select_operation_blocks", u32,
        new ParameterImpl("address", u32, currentProgram),
        new ParameterImpl("length", u32, currentProgram),
        new ParameterImpl("first_block", new PointerDataType(u32, 4), currentProgram),
        new ParameterImpl("last_block", new PointerDataType(u32, 4), currentProgram))
        .setComment("Rejectlength0 orfailedfirst3474 lookup. Lookup modulo32lastaddress, ignoresecondlookupreturn, "
            + "andreturn(last_block<first_block). An out-of-range lastaddress can use3474 fallbackF8000; this is not "
            + "complete region validation.");
    semanticFunction(0x411AL, "f33_boot_submit_erase_program_stream", u32,
        new ParameterImpl("address", u32, currentProgram),
        new ParameterImpl("length", u32, currentProgram))
        .setComment("Rejectbusy2AA1.40A2prepares512-aligned ringbefore40E0rangeadmission. Onaccept "
            + "setmode0,currentblock/nextboundary,writecursor,paddedremaining,result1,busy1; clearfinal/cancel/pause. "
            + "Retain prior2994counter-block selection.0accepted/1rejected; notflashcompletion.");
    semanticFunction(0x4188L, "f33_boot_submit_program_stream", u32,
        new ParameterImpl("address", u32, currentProgram),
        new ParameterImpl("length", u32, currentProgram))
        .setComment("Rejectbusy;40A2seedsalignmentprefixbefore3562 ECC-backedroundedblankcheck. Onaccept "
            + "setmode1,writecursor,paddedremaining,result1,busy1;clearfinal/cancel/pause.0accepted/1rejected. "
            + "Hardwareblankcheck andfailed-admission ringeffects are separate.");
    semanticFunction(0x41E0L, "f33_boot_submit_block_erase", u32,
        new ParameterImpl("address", u32, currentProgram),
        new ParameterImpl("length", u32, currentProgram))
        .setComment("Rejectbusy;40E0selectsfirst/lastblocks;3402selectscounterblock. Clearcoveredskipflags3506; "
            + "setmode2,first/last/nextblock,counteraddress,result1,busy1;clearfinal/cancel/pause.0accepted/1rejected; no "
            + "deviceoperation until4428.");
    semanticFunction(0x4260L, "f33_boot_set_flash_worker_pause", v,
        new ParameterImpl("paused", u8, currentProgram))
        .setComment("Storelow8 into299F. Any nonzero pauses4428 work, but finalcancel processing remains active.");
    semanticFunction(0x4266L, "f33_boot_request_flash_worker_cancel", v)
        .setComment("Set299E=1; doesnot immediatelyclearbusy orchange result.4428 later consumes it evenwhenpaused.");
    semanticFunction(0x4276L, "f33_boot_append_program_input", v,
        new ParameterImpl("source", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("length", u16, currentProgram))
        .setComment("Append low16length bytes fromsource to1800 ring; wrapproducer at1100 andpublish2998 afterward. No "
            + "owncapacitycheck orPMR. Caller42D8 admission protectsreservedslot.");
    semanticFunction(0x42A4L, "f33_boot_program_input_occupancy", u32)
        .setComment("Snapshotu16producer2998 andconsumer299A underFFFF PMR; compute modulo1100 occupancy, zxh tofullR10, "
            + "restorePMR. Equalindicesmeanempty.");
    semanticFunction(0x42D8L, "f33_boot_program_input_has_insufficient_space", u32,
        new ParameterImpl("requested_length", u16, currentProgram))
        .setComment("Return signed(1100-occupancy < low16(requested_length)+1). Reserveoneslot; validcapacity4351. No enqueue "
            + "orstatechange.");
    semanticFunction(0x42F6L, "f33_boot_stage_preserved_program_counter", u32)
        .setComment("Ifnonzero2994 lies in[currentblock,nextboundary), stage32-bitcounter+1modulo32 then63FFFFFFFFwords "
            + "in29A0;return0. Otherwisereturn1unchanged. Counterblockpreservation, notrequestpayload.");
    semanticFunction(0x4332L, "f33_boot_erase_current_block_preserving_counter", u32)
        .setComment("Skipcallbackonlyif34DA(currentblock)==1. Otherwise42F6 optionallystagescounter; "
            + "call[FEBF0FD0](block,0,1,&status), thenonstatus0 andstagedcounter call(pointer,29A0,0,&status). Any "
            + "nonzero statusreturns1, else0. Boot-phase dynamicdriverboundary; overlapping "
            + "applicationNvMglobalisnotcallee.");
    semanticFunction(0x4390L, "f33_boot_consume_program_input", v,
        new ParameterImpl("destination", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("length", u16, currentProgram))
        .setComment("Copylow16length bytes from1800 ring,wrapconsumerat1100,publish299Aaftercopy. Caller43BEchecksavailability; "
            + "no localcapacitycheck.");
    semanticFunction(0x43BEL, "f33_boot_stage_and_program_input_chunk", u32,
        new ParameterImpl("length", u32, currentProgram))
        .setComment("Return2withoutmutation iflow16length>ringoccupancy. Otherwiseconsumeinto29A0,padFF to256 "
            + "usingfullsignedlength comparison, theninvoke[FEBF0FD0](cursor,buffer,0,&status) "
            + "unlesscursor==2994counterblock. Returnbool(status!=0); skippedcounterblockreturns0. "
            + "Consumptionprecedesdevicefailure;4428supplieslength<=256.");
    semanticFunction(0x4428L, "f33_boot_advance_flash_operation", v)
        .setComment("UnderFFFF PMR, busy0returns; nonzeropause skipswork. "
            + "Mode0erasesanddrains<=256chunks,mode1drains,mode2erasescoveredblocks. rc2waitsforinput;rc1clearsbusy "
            + "retainingresult; successfulcompletionsetsresult0/busy0. "
            + "Finalcancel==1alwaysclearcancel/busy/pausewithoutpromotingsuccess. "
            + "Devicecallbackandphysicalcompletionremainexplicitboundary.");
    semanticFunction(0x4590L, "f33_boot_reset_flash_operation_queue", v)
        .setComment("Clearbusy,pause,cancel,finalmarker,ringproducer/consumer;setresult1. "
            + "Doesnotclearcursor,remaining,counterblock orstaging; no lowerdevicecancel.");
    semanticFunction(0x47BAL, "f33_boot_submit_region_crc_verification", u32,
        new ParameterImpl("address", u32, currentProgram),
        new ParameterImpl("length", u32, currentProgram),
        new ParameterImpl("opaque_tag", u8, currentProgram))
        .setComment("If2AADnonzeroreturn1unchanged; otherwisequeueaddress/length/tag,setresult2,pending1,return0. No "
            + "rangevalidationhere;4874 validatesselectedregion later. Noterase.");
    semanticFunction(0x47DEL, "f33_boot_region_crc_result", u32)
        .setComment("Returnzero-extended2AAC result: initializer/admission2, worker0success/1failure.");
    semanticFunction(0x47E4L, "f33_boot_region_crc_pending", u32)
        .setComment("Returnzero-extended2AAD pendingbyte; notCRCresult.");
    semanticFunction(0x4874L, "f33_boot_advance_region_crc_verification", v)
        .setComment("Onlypending==1 and335Evalidrange call481A onselectedwholeregion, notrequestedsubrange. ThenunderFFFF "
            + "PMRclear pending/start/length andsetresultbool(CRC!=0);opaque tagretained. Invalidorzerolength remains "
            + "pending unchanged.");
    semanticFunction(0x48C4L, "f33_boot_reset_region_crc_verification", v)
        .setComment("SetCRCresult2 andpending0; retainaddress,length,opaque tag. Separatefrom47AC transition-job reset.");
  }

  private void annotateReceivedInputConditioning() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    semanticFunction(0x49F20L, "f33_advance_dual_source_admission_qualification", v)
        .setComment("Configured source qualifier: local0 + predicate22 starts11 and shared mode1. Persistent22 with entry "
            + "count>=5 selects local22/shared2; entry persistence>=200 selects local44/shared3. Local11 resets on any "
            + "predicate other than22, including inapplicable44. Local22 recovers on11 immediately with configured "
            + "recovery limit0; predicate44 resets counters only. Local44 recovers only after entry healthy-count>=200; "
            + "other predicates reset that recovery count. Direct shared7F68 writes are ordered, not a max/OR reduction.");
    semanticFunction(0x4A05EL, "f33_advance_first_source_admission_qualification", v)
        .setComment("Configured source qualifier: local0 + predicate22 starts11 and shared mode1. Persistent22 with entry "
            + "count>=5 selects local22/shared2; entry persistence>=200 selects local44/shared3. Local11 resets on any "
            + "predicate other than22, including inapplicable44. Local22 recovers on11 immediately with configured "
            + "recovery limit0; predicate44 resets counters only. Local44 has no ordinary recovery branch; cause "
            + "latch7F6A is set on entry. Direct shared7F68 writes are ordered, not a max/OR reduction.");
    semanticFunction(0x4A160L, "f33_advance_second_source_admission_qualification", v)
        .setComment("Configured source qualifier: local0 + predicate22 starts11 and shared mode1. Persistent22 with entry "
            + "count>=5 selects local22/shared2; entry persistence>=200 selects local44/shared3. Local11 resets on any "
            + "predicate other than22, including inapplicable44. Local22 recovers on11 immediately with configured "
            + "recovery limit0; predicate44 resets counters only. Local44 has no ordinary recovery branch; cause "
            + "latch7F6B is set on entry. Direct shared7F68 writes are ordered, not a max/OR reduction.");
    semanticFunction(0xBE304L, "f33_scale_staged_byte_pair_to_control_raw", v)
        .setComment("Scale unsignedF03D/F03E by5243 then logicalshift12 intoBE54/BE56. NormalECUpublisher setsbothsources0; no "
            + "physicalunits.");
    semanticFunction(0xBE326L, "f33_condition_staged_offset_scalar", v)
        .setComment("F02D8..108 ->signed(F02D-48)*128;outsideholdBE5E andstatus0->1. "
            + "Alwayscopyfourdefaultstatusbytes;noF000gate.");
    semanticFunction(0xBE38CL, "f33_initialize_received_word_age_from_record13", v)
        .setComment("Readlogicalrecord13;onlyresult10adoptsword+0andage+4,otherwiseclearboth. Notamodetierreentryage-reset.");
    semanticFunction(0xBE3C4L, "f33_condition_received_word_and_age", v,
        new ParameterImpl("policy", u8, currentProgram))
        .setComment("Hold5A;resetseedA5;adoptadmittedfreshnonFFFFF18A;resetageonlyonchangedvalue,otherwiseadd5withFFFFFFFEsentinelhandling. "
            + "AlwaysconsumeF039generation.");
    semanticFunction(0xBE43AL, "f33_condition_received_typed_scalar", v,
        new ParameterImpl("policy", u8, currentProgram))
        .setComment("Hold5A;resetA5;invalidstatusclears;admittednewgenerationadoptsuint32F218<=999999withtype1/2,otherwisezero. "
            + "AlwaysconsumeF066generation;BE74isnotapointer.");
    semanticFunction(0xBE4A4L, "f33_validate_packed_decimal_byte", u32,
        new ParameterImpl("packed_value", u8, currentProgram))
        .setComment("Returnunchangedlow8R6whenbothnibblesaredecimaldigits,elsefullR10=FF. Validationonly,noconversion.");
    semanticFunction(0xBE4C2L, "f33_condition_received_packed_decimal_fields", v,
        new ParameterImpl("policy", u8, currentProgram))
        .setComment("Hold5A/resetA5;invalidstatusorinvalidfreshsix-membertuple->allFF. "
            + "Nibbledigitsandrawbyteboundsretainedwithoutdecimalconversion;alwaysconsumeF0F7generation.");
    semanticFunction(0xBE5AAL, "f33_refresh_received_control_metadata", v)
        .setComment("B20E11/33selecthold5A;prior33->0selectresetA5;else0. Callthreeconditioners;saveB20EandpublishBE64=5A.");
    semanticFunction(0xBE5FCL, "f33_stage_received_word_age_record13", v)
        .setComment("StagewordBE6E,reservedhalfword0,ageBE70aslogicalrecord13throughFF09C.");
    semanticFunction(0xBE622L, "f33_seed_health_received_source_filter", v)
        .setComment("TierentryinitializesBE78/7B,BE79/7A=5Aandfixed-ratioF194filterseedindependentlyofoptionalBE778cadence. "
            + "NoOEMsourceidentity.");
    semanticFunction(0xBEA14L, "f33_publish_first_fixed_received_marker", v)
        .setComment("SetBED4=55AAAA55,BE9D/BEB3=0,BEA7=5A. Unconditionalsoftwaremarker,notreceivedidentity.");
    semanticFunction(0xBEA2CL, "f33_publish_second_fixed_received_marker", v)
        .setComment("SetBED8=55AAAA55,BE9E/BEB4=0,BEA8=5A. Unconditionalsoftwaremarker.");
    semanticFunction(0xBEA44L, "f33_initialize_fixed_received_markers", v)
        .setComment("Callbothfixedmarkerpublishersduringcommoncontrolinitialization.");
    semanticFunction(0xBEA56L, "f33_qualify_received_scalar_startup", v)
        .setComment("WhileBEA2=0,F000<2qualifiesBEC4atentry>=300,clearsBE98;badgateresetscount. "
            + "Stickycompletion;alwaysBEAD0andBEAE=BE98.");
    semanticFunction(0xBEAA4L, "f33_qualify_received_channel_b_startup", v)
        .setComment("WhileBEA3=0,F000<2,F0280,F02B1qualifyBEBCatentry>=48->BEA3/BE99=5A;alwaysBEAF0. "
            + "Canonicalpublisherdefaultsinhibitnewqualification.");
    semanticFunction(0xBEAFAL, "f33_qualify_received_channel_c_startup", v)
        .setComment("WhileBEA4=0,F000<2,F0600qualifyBEBEatentry>=96->BEA4/BE9A=5A;alwaysBEB00. CanonicalF0601inhibits.");
    semanticFunction(0xBEB48L, "f33_qualify_received_channel_d_startup", v)
        .setComment("WhileBEA5=0,F000<2andF069receive-status0qualifyBEC0atentry>=40->BEA5/BE9B5A;alwaysBEB2=BE9B. "
            + "Stickycompletion.");
    semanticFunction(0xBEB96L, "f33_qualify_received_channel_e_startup", v)
        .setComment("WhileBEA6=0,F000<2andF04Creceive-status0qualifyBEC2atentry>=64->BEA6/BE9C5A;alwaysBEB1=BE9C.");
    semanticFunction(0xBEBE4L, "f33_publish_received_channel_f_defaults", v)
        .setComment("PublishBE9F/BEB6=5Awithoutwirepredicate.");
    semanticFunction(0xBEBF2L, "f33_publish_received_channel_g_default", v)
        .setComment("PublishBEA0=5Awithoutwirepredicate.");
    semanticFunction(0xBEBFCL, "f33_publish_received_channel_h_default", v)
        .setComment("PublishBEA1=5Awithoutwirepredicate.");
    semanticFunction(0xBEC06L, "f33_publish_fixed_received_channel_defaults", v)
        .setComment("ComposeBEBE4/BEBF2/BEBFCconstantsoftwaredefaults.");
    semanticFunction(0xBEC1AL, "f33_clear_fixed_received_metadata", v)
        .setComment("ClearBEB8/BEB5;noinputsampling.");
    semanticFunction(0xBEC24L, "f33_qualify_received_paired_channel_startup", v)
        .setComment("WhileBEBB=0,F000<2and(F1480orF1490)qualifyBED0atentry>=200->BEBB/BEBA5A;alwaysBEB7=BEBA. "
            + "Canonicalboth1inhibit.");
    semanticFunction(0xBEC7AL, "f33_publish_received_startup_delay_default", v)
        .setComment("ClearonlyBEADduringglobalstartupdelay;otherchannelstateisretained.");
    semanticFunction(0xBEC80L, "f33_update_delayed_received_startup_qualification", v)
        .setComment("EntryBEC6<200onlyclearsBEADandincrements;entry>=200runsreadiness/defaultgroup. "
            + "Alwayspublishbothfixedmarkersaftereitherbranch. Mode>=0101everyforegroundinvocation.");
    semanticFunction(0xBF0AAL, "f33_qualify_record8_admitted_observations", v,
        new ParameterImpl("result", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("completed", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("zero_count", new PointerDataType(u16, 4), currentProgram),
        new ParameterImpl("nonzero_count", new PointerDataType(u16, 4), currentProgram))
        .setComment("R6resultbyte*,R7completionbyte*,R8zero-countu16*,R9nonzero-countu16*. "
            + "Prefercount>=3resultACEDovercount>=8result0;clampwinningcount.");
    semanticFunction(0xBF0ECL, "f33_step_record8_confirmation_window", v,
        new ParameterImpl("result", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("completed", new PointerDataType(u8, 4), currentProgram))
        .setComment("Increment16-bittotal;strict>10failsbeforeobservations. "
            + "F0690permitsF06Ezero/nonzeroobservationcounts;statusnonzeroqualifiesinvalidcount>=8. "
            + "Result/completionpointersarepreservedacrossrealBF0AA.");
    semanticFunction(0xBF18AL, "f33_advance_record8_startup_confirmation", v)
        .setComment("OnceonlywhileinitialACED5A;strictincrementedwarmup>60;B080>4096rejects;F0015Aadmitswindowelseclearinnercounts. "
            + "OnoldBF040->newcompletion5AcommitBD86Eandsnapshot.");
    semanticFunction(0xBF232L, "f33_update_initialized_record8_confirmation", v)
        .setComment("CallBF18AonlyACEE==5A;closedgatefreezesallstate. "
            + "Calledmode>=0101beforeoptionalhealthsourcecachegeneration.");
    semanticFunction(0xBF24CL, "f33_update_acquired_scalar_hysteresis", v)
        .setComment("Saturatingabs16AFE0andROMenable5A;setBF11at>=5120,clearat<=2560,retainbetween. "
            + "Acquiredscalar,notwireidentity.");
    semanticFunction(0xBF298L, "f33_debounce_acquired_scalar_hysteresis", v)
        .setComment("Incrementselectedu16counteronlywhile<=limitandclearoppositeonlyonincrementpath;strict>limitupdatesBF10. "
            + "ROMlimit0givesone-invocationordinaryresponse.");
    semanticFunction(0xBF2E4L, "f33_refresh_acquired_scalar_status_publication", v)
        .setComment("ComposeBF24ChysteresisthenBF298debouncedBF10publishedtoE848byBF3AA;mode>=0100.");
    semanticFunction(0x4B378L, "f33_refresh_route30_health_inputs", v)
        .setComment("Route30classical51E/8;only7F68<2andchanged5356decodefourfields. "
            + "Alwaysconsume5356->802Eandrefreshstatusselector12->802F,evenwithfrozendecode.802EfeedsF13F/BE7E.");
    semanticFunction(0x4A298L, "f33_update_internal_source_admission_lifecycle", v)
        .setComment("Set7F6Ffrom7F2C1/2,runthreeconfiguredobservationfamiliesinorder,then7F70admission. "
            + "Shared7F68isorderedlastwriter,notwirepayloadoraggregateOR.");
    semanticFunction(0x4A26AL, "f33_publish_internal_source_observation_admission", v)
        .setComment("7F70=5Aonlyunsigned66B8in2304..4096and7F68not2/3;otherwise0. IndependentlypublishedF001.");
    semanticFunction(0x4A306L, "f33_classify_dual_internal_source_observations", u32)
        .setComment("Return44for6764lowqualificationbitsorclosed7F6F;22foravailable66B8outside2304..4096andboth66AE/66B0below2304orbothabove4096;else11.");
    semanticFunction(0x4A360L, "f33_classify_first_internal_source_observation", u32)
        .setComment("Requires6764.bit1and7F6F5A,else44;available66B8outside2304..4096plus66AEoutsidefails22;else11.");
    semanticFunction(0x4A3AEL, "f33_classify_second_internal_source_observation", u32)
        .setComment("Requires6764.bit0and7F6F5A,else44;available66B8outside2304..4096plus66B0outsidefails22;else11.");
    semanticData(0xFEBE7F68L, u8, "f33_internal_source_admission_state",
        "Ordered internal qualifier state0/1/2/3. Not a decoded physical/OEM input; publishedF000.");
    semanticData(0xFEBEF000L, u8, "f33_published_internal_source_admission_state",
        "58074copyof7F68;0/1admitF000<2. No physicalidentityassertion.");
    semanticData(0xFEBE5356L, u8, "f33_route30_copy_generation",
        "COM5338+30bytegeneration;incrementedmodulo256by8E772afteraccepted7D72Cpublication.");
    semanticData(0xFEBE802EL, u8, "f33_route30_consumed_generation",
        "4B378alwayssnapshots5356,evenwhen7F68>=2preventspayloaddecode.");
    semanticData(0xFEBE802FL, u8, "f33_route30_receive_status",
        "Statusselector12(bit0rawinvalid,bit1confirmedtimeout);notgenerationorpayload.");
    semanticData(0xFEBEF13FL, u8, "f33_published_route30_consumed_generation",
        "58074copyof802E;canadvancewithoutnewscalar8031.");
    semanticData(0xFEBEBE7EL, u8, "f33_health_cached_route30_generation",
        "BE778copyF13Fonlyonadmittedcadence;notuniversalhealthsamplegeneration.");
    semanticData(0xFEBEBE54L, u16, "f33_scaled_staged_byte_a",
        "floor(uint8F03D*5243/4096),normally0;rawfixedratio.");
    semanticData(0xFEBEBE56L, u16, "f33_scaled_staged_byte_b",
        "floor(uint8F03E*5243/4096),normally0;rawfixedratio.");
    semanticData(0xFEBEBE5EL, s16, "f33_conditioned_offset_scalar",
        "(F02D-48)*128for8..108;holdoutsidewithstatusqualificationBE58.");
    semanticData(0xFEBEBE6EL, u16, "f33_received_retained_word",
        "AdmittednonFFFFF18A;logicalrecord13word+0.");
    semanticData(0xFEBEBE70L, u32, "f33_received_word_unchanged_age",
        "Increment5pernonheldBE3C4callunlessadoptedvaluechanges. FFFFFFFEisreset-cycle sentinel,notpermanentsaturation;nowall-timeunits.");
    semanticData(0xFEBEBE74L, u32, "f33_received_typed_scalar",
        "Numeric0..999999withBE62type1/2;notCodeFlashpointer. Canonicalpointerrenderingmustberepaired.");
    semanticData(0xFEBEF218L, u32, "f33_published_route31_numeric_scalar",
        "Unsigned32 route31 scalar published by58074, compared numerically against999999 byBE43A; not a pointer.");
    semanticData(0xFEBE8034L, u32, "f33_route31_numeric_scalar",
        "4B40E decodes raw unsigned32 signalAB from route31 into this cell; physical units remain unassigned.");
    semanticData(0xFEBEBE66L, new ArrayDataType(u8, 6, 1), "f33_received_packed_decimal_fields",
        "Validatedpackeddecimalbytesretainedunchanged;anyinvalidmemberpublishesallFF. NoOEMcalendaridentity.");
    semanticData(0xFEBEBEC6L, u16, "f33_received_qualification_startup_count",
        "Entry<200incrementswithoutchannelstep;entry>=200admitseight-membergroup.");
    semanticData(0xFEBEBF04L, u8, "f33_record8_confirmation_complete",
        "Completion5Afreezesone-shotdecision;onlyold0->5AcommitsACECandsnapshot.");
    semanticData(0xFEBEBF05L, u8, "f33_record8_confirmation_result",
        "One-shotresultpassedtoBD86E,notreceivefaultclassification.");
    semanticData(0xFEBEBF06L, u16, "f33_record8_confirmation_warmup_count",
        "uint16incrementthenstrict>60admitswindow;clamp60afterexpiry.");
    semanticData(0xFEBEBF08L, u16, "f33_record8_zero_observation_count",
        "F0690/F06E0count;inclusive>=3positivecompletion.");
    semanticData(0xFEBEBF0AL, u16, "f33_record8_nonzero_observation_count",
        "F0690/F06Enonzerocount;inclusive>=8zeroresultcompletion.");
    semanticData(0xFEBEBF0CL, u16, "f33_record8_invalid_observation_count",
        "F069nonzerocount;inclusive>=8zeroresultcompletion.");
    semanticData(0xFEBEBF0EL, u16, "f33_record8_confirmation_window_count",
        "uint16increment;strict>10expiresbeforeobservationclassification.");
  }

  private void annotateResidentDiagnosticLifecycle() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
    FunctionDefinitionDataType service = new FunctionDefinitionDataType(category, "F33BootServiceCallback");
    service.setReturnType(v);
    service.setArguments(new ParameterDefinition[] {new ParameterDefinitionImpl("request_length", u16, null)});
    DataType serviceType = currentProgram.getDataTypeManager().addDataType(service, DataTypeConflictHandler.REPLACE_HANDLER);
    StructureDataType layout0 = new StructureDataType(category, "F33BootPduInfo", 0);
    layout0.setPackingEnabled(true);
    layout0.add(new PointerDataType(u8, 4), "data", null);
    layout0.add(u16, "length", null);
    layout0.add(u16, "padding", null);
    DataType layout0Type = resolve(layout0);
    StructureDataType layout1 = new StructureDataType(category, "F33BootServiceEntry", 0);
    layout1.setPackingEnabled(true);
    layout1.add(u8, "sid", null);
    layout1.add(u8, "address_mode_mask", null);
    layout1.add(u16, "reserved", null);
    layout1.add(new PointerDataType(serviceType, 4), "handler", null);
    DataType layout1Type = resolve(layout1);
    semanticData(0x8E54L, new ArrayDataType(layout1Type, 20, 8), "f33_boot_diagnostic_services",
        "5222passeslengthinr6aftercheckingSIDand1<<30BFagainstmask.");
    StructureDataType layout2 = new StructureDataType(category, "F33BootChannelEntry", 0);
    layout2.setPackingEnabled(true);
    layout2.add(u32, "handoff_selector", null);
    layout2.add(u8, "transport_handle", null);
    layout2.add(u8, "address_mode", null);
    layout2.add(u16, "reserved", null);
    DataType layout2Type = resolve(layout2);
    semanticData(0x8F04L, new ArrayDataType(layout2Type, 2, 8), "f33_boot_diagnostic_channels",
        "Usedby6504recordmatch,6374addressmode,65AA/674Aoutgoinghandle;notunconditionallyaCANIDtable.");
    StructureDataType layout3 = new StructureDataType(category, "F33BootDidEntry", 0);
    layout3.setPackingEnabled(true);
    layout3.add(new PointerDataType(u8, 4), "target", null);
    layout3.add(u16, "payload_length", null);
    layout3.add(u16, "identifier", null);
    layout3.add(u8, "access_flags", null);
    layout3.add(u8, "job_mode", null);
    layout3.add(u8, "reply_prefix", null);
    layout3.add(u8, "reserved", null);
    DataType layout3Type = resolve(layout3);
    semanticData(0x8F14L, new ArrayDataType(layout3Type, 4, 12), "f33_boot_diagnostic_identifiers",
        "Flags1read/2write;jobmode0queuedring,1RAMcopy;prefixFFabsent.");
    StructureDataType layout4 = new StructureDataType(category, "F33BootRoutineEntry", 0);
    layout4.setPackingEnabled(true);
    layout4.add(u32, "opaque_word", null);
    layout4.add(u16, "identifier", null);
    layout4.add(u8, "configured_subfunction", null);
    layout4.add(u8, "request_option_length", null);
    layout4.add(u8, "response_extra_length", null);
    layout4.add(new ArrayDataType(u8, 3, 1), "reserved", null);
    DataType layout4Type = resolve(layout4);
    semanticData(0x8F44L, new ArrayDataType(layout4Type, 5, 12), "f33_boot_diagnostic_routines",
        "Allopaque_wordsFFFFFFFFnotcallbackpointers;567EusesdescriptorfieldsandexplicitRIDdispatch.");
    StructureDataType layout5 = new StructureDataType(category, "F33BootTimerSlot", 0);
    layout5.setPackingEnabled(true);
    layout5.add(u32, "deadline", null);
    layout5.add(u32, "token", null);
    layout5.add(u8, "armed", null);
    layout5.add(u8, "generation", null);
    layout5.add(u16, "reserved", null);
    DataType layout5Type = resolve(layout5);
    semanticData(0xFEBF2938L, new ArrayDataType(layout5Type, 2, 12), "f33_boot_timer_slots",
        "1D9Aclearsarmedbeforecallback;generationcomparedin30D2preventsaleventconsumption.");
    StructureDataType layout6 = new StructureDataType(category, "F33BootHandoffRecord", 0);
    layout6.setPackingEnabled(true);
    layout6.add(u32, "tag", null);
    layout6.add(u32, "channel_selector", null);
    layout6.add(new ArrayDataType(u32, 2, 4), "opaque_words2_3", null);
    layout6.add(u32, "session_subfunction", null);
    layout6.add(u32, "suppress_positive", null);
    layout6.add(new ArrayDataType(u32, 3, 4), "opaque_words6_8", null);
    DataType layout6Type = resolve(layout6);
    semanticData(0x31788L, layout6Type, "f33_boot_application_handoff_record",
        "148Ecopiesninewords;6A22readsfirsteight;6504useslowbyteofsubfunctionandnonzerotestofsuppression.");
    semanticData(0xFEBF2908L, layout6Type, "f33_boot_captured_handoff_record",
        "Resident phase nine-word record copied by148E; not an application DCM request.");
    semanticData(0xFEBF2B0EL, u8, "f33_boot_diagnostic_session",
        "Resident boot phase only; application RAM reuse is not this ownership contract.");
    semanticData(0xFEBF2B0FL, u8, "f33_boot_security_state",
        "Resident boot phase only; application RAM reuse is not this ownership contract.");
    semanticData(0xFEBF2B13L, u8, "f33_boot_download_state",
        "Resident boot phase only; application RAM reuse is not this ownership contract.");
    semanticData(0xFEBF2B17L, u8, "f33_boot_operation_region_class",
        "Resident boot phase only; application RAM reuse is not this ownership contract.");
    semanticData(0xFEBF2BBAL, u8, "f33_boot_request_state",
        "Resident boot phase only; application RAM reuse is not this ownership contract.");
    semanticData(0xFEBF2BBBL, u8, "f33_boot_response_state",
        "Resident boot phase only; application RAM reuse is not this ownership contract.");
    semanticData(0xFEBF2BBCL, u8, "f33_boot_response_pending_in_flight",
        "Resident boot phase only; application RAM reuse is not this ownership contract.");
    semanticData(0xFEBF2BBDL, u8, "f33_boot_terminal_after_response",
        "Resident boot phase only; application RAM reuse is not this ownership contract.");
    semanticData(0xFEBF2BB8L, u16, "f33_boot_request_append_index",
        "Resident boot phase only; application RAM reuse is not this ownership contract.");
    semanticData(0xFEBF30B8L, u16, "f33_boot_request_length",
        "Resident boot phase only; application RAM reuse is not this ownership contract.");
    semanticData(0xFEBF30BAL, u16, "f33_boot_response_remaining",
        "Resident boot phase only; application RAM reuse is not this ownership contract.");
    semanticData(0xFEBF30BCL, u16, "f33_boot_active_channel",
        "Resident boot phase only; application RAM reuse is not this ownership contract.");
    semanticData(0xFEBF30BEL, u8, "f33_boot_active_sid",
        "Resident boot phase only; application RAM reuse is not this ownership contract.");
    semanticData(0xFEBF30BFL, u8, "f33_boot_address_mode",
        "Resident boot phase only; application RAM reuse is not this ownership contract.");
    semanticData(0xFEBF30C0L, new ArrayDataType(u8, 4096, 1), "f33_boot_request_bytes",
        "Resident boot phase only; application RAM reuse is not this ownership contract.");
    semanticFunction(0x5222L, "f33_boot_dispatch_diagnostic_service", v,
        new ParameterImpl("sid", u8, currentProgram),
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("ROM8E54twentyentryresident-onlyservice/address-modedispatch;unmatchedormaskdenied\u219251FA(SID,11).NoapplicationDCMtable.");
    semanticFunction(0x614AL, "f33_boot_service_session_control", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Resident SID10: require length2 and masked subfunction1/2/3; reject target2 from session1 or target3 from "
            + "session2 with7E. Stage requested session in2B9F/2BA0 and deferred state2BA3; programming entry queues4776 "
            + "or foreground flag2BA2.6244 publishes the session only after the foreground join, then "
            + "responds50/subfunction/00 32 01 F4.");
    semanticFunction(0x60C2L, "f33_boot_service_reset_request", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Resident SID11: session2, security2, length2, masked subfunction1 only. Stage51/subfunction positive "
            + "response and request terminal action through67DA; successful response completion joins159E "
            + "resident-state3/interrupt-disable halt path, not a proven physical ECU reset.");
    semanticFunction(0x5516L, "f33_boot_service_security_access", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Resident SID27: session2; masked subfunctions1 and2 only. Both seed and key requests require18 bytes.5328 "
            + "stages16 client bytes and returns a16-byte challenge;53F2 derives and compares16 expected key bytes. "
            + "Success stores security2B0F=2 before response submission; handshake2B55=3 follows its return. "
            + "Bad key35; a second counted failure gives36 and raw-counter delay. Active delay rejects seed "
            + "with37 before length validation; reseed and replay behavior are owned by5328/53F2.");
    semanticFunction(0x688AL, "f33_boot_service_communication_control", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Resident SID28: session3, length3, masked subfunction1 and communication byte1 only; invalid "
            + "subfunction12, invalid communication byte31, bad length13. Store original subfunction and "
            + "form68/masked-subfunction with bit7 positive-response suppression. No physical communication-disable side "
            + "effect is established by this handler.");
    semanticFunction(0x4FF8L, "f33_boot_service_tester_present", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Resident SID3E: sessions1/2/3, length2, subfunction00 or80 only. Form7E/00 through4FCE; original bit7 "
            + "controls positive-response suppression. Functional3E80 has a separate request-admission special case while "
            + "another request is receiving.");
    semanticFunction(0x693AL, "f33_boot_service_dtc_setting", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Resident SID85: session3, length2 and masked subfunction2 only. Store original subfunction and formC5/02 "
            + "through6910 with bit7 positive-response suppression. No application DTC-state mutation is established "
            + "here.");
    semanticFunction(0x5FB8L, "f33_boot_service_read_did", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Resident SID22: sessions1/2/3, length3 and a read-enabled match among four8F14 descriptors. Only "
            + "configured F181 is readable: reply62/F181/02 followed by32 literal21 bytes generated by5F3E. Unknown or "
            + "unreadable DID31; bad length13.5F3E receives descriptor index inr6 and payload offset inr7.");
    semanticFunction(0x4948L, "f33_boot_service_write_did", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Resident SID2E: session2, security2, exact length3+8F14 descriptor payload and write flag2.0201 "
            + "requires2AB2=1 and schedules16-byte job then state2;0202 requires state2, schedules16-byte job, "
            + "sets2B16=1/state0;0203 requires state0 and returns immediate6E/state1.4A9A waits asynchronous job "
            + "completion and emits6E or72.");
    semanticFunction(0x567EL, "f33_boot_service_routine_control", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Resident SID31: session2, security2, masked start subfunction1, exact length4+configured options.8F44 "
            + "configures10F0/10F1/10F2/10F3/FF00; all except10F3 require45 00 plus BE32 address/length. Range-kind "
            + "gates32D2/3318 precede CRC-verification47BA or queued operation41E0. Timer5C06 owns deferred "
            + "completion;10F3 immediately sets alternate download state8 and responds71.");
    semanticFunction(0x5D68L, "f33_boot_service_request_download", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Resident SID34: session2/security2, exact13-byte custom request; DFI high nibble0, low nibble2B15, "
            + "following format46, selector00/01 then00, BE32 address and size.32D2 classifies the range; normal state0 "
            + "stages download1, alternate state8 stages9. Store2B00/2B04 and reset transfer counters; optional block "
            + "crypto starts6BA8. Positive response is four bytes74 20 04 02.");
    semanticFunction(0x4DBAL, "f33_boot_service_transfer_data", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Resident SID36: preserve request length inr6; advance download1 to2 or9 to10, then call4B7C program/copy "
            + "or4CA2 comparison. Payload is at most1024 bytes and full1024 except final; sequence mismatches73, "
            + "duplicate sequence repeats76 without requeue. Actual ready data consumption occurs later in "
            + "foreground4F50; timer4DF2/4E92 owns completion and positive76/sequence.");
    semanticFunction(0x5C92L, "f33_boot_service_transfer_exit", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Resident SID37: session2, download state2 or10, remaining transfer bytes0 and exact length1. Optionally "
            + "end block crypto; clear operation class2B17, address2B00, length2B04 and download state2B13; respond77. "
            + "Incomplete transfer rejects24 and may request4266 cancellation. No call to426E final-input setter is "
            + "present.");
    semanticFunction(0x69B0L, "f33_boot_service_reject_configured", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Sharedconfiguredcallbackfor23/2C/14/19/2F/AB/BA/BB;readsSIDfromrequestbyte0andreturnsNRC7F.Doesnotimplementthoseservices.");
    semanticFunction(0x2B8AL, "f33_boot_transport_receive_frame", v,
        new ParameterImpl("selector", u16, currentProgram),
        new ParameterImpl("pdu", new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33BootPduInfo"), 4), currentProgram))
        .setComment("Checksresidenttransportenabled,selector<2,length2..8;routesPCI0/10/20/30usingexact8D50config.PDUisnotcompletedrequestdata.");
    semanticFunction(0x1EEEL, "f33_boot_transport_rx_record_callback", v,
        new ParameterImpl("record", new PointerDataType(v, 4), currentProgram))
        .setComment("ActualROM88FCcallback,buildsPDUandcalls2B8A.Record+4u16selector,+8u32length,+Cinlinebytes.");
    semanticFunction(0x6374L, "f33_boot_request_admit", u32,
        new ParameterImpl("channel", u16, currentProgram),
        new ParameterImpl("first_chunk", new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33BootPduInfo"), 4), currentProgram),
        new ParameterImpl("total_length", u16, currentProgram),
        new ParameterImpl("remaining_capacity", new PointerDataType(u16, 4), currentProgram))
        .setComment("Admissionreturns0accepted/1busy/3tooLong.Maximum4096;writesr9capacity;storesSID/address-mode/channelandresetsappendindex.Seeexceptionalreceivingreplacementbehavior.");
    semanticFunction(0x6464L, "f33_boot_request_append", u32,
        new ParameterImpl("channel", u16, currentProgram),
        new ParameterImpl("chunk", new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33BootPduInfo"), 4), currentProgram),
        new ParameterImpl("remaining_capacity", new PointerDataType(u16, 4), currentProgram))
        .setComment("Returns0success/1capacityerror;readsONLYlowbyteofdescriptorlength,updatesu16total30B8,andcalls6422.6422mustpreserver8capacityoutputliveacrosscall.");
    semanticFunction(0x6422L, "f33_boot_request_append_bytes", v,
        new ParameterImpl("source", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("length", u8, currentProgram))
        .setComment("Appendinto4096-byteFEBF30C0using2BB8index.Preservesr8;inlineexactleafinGhidraso6464doesnotinventextraout_r8.");
    getFunctionAt(toAddr(0x6422L)).setInline(true);
    semanticFunction(0x64B8L, "f33_boot_request_receive_complete", v,
        new ParameterImpl("channel", u16, currentProgram),
        new ParameterImpl("status", u8, currentProgram))
        .setComment("Status0capturesrawcountertimestamps,publishesexecuting2/substate0anddispatchesSID+length.Nonzerostatusabortsthereceive.");
    semanticFunction(0x6B4CL, "f33_boot_transport_request_admit", u32,
        new ParameterImpl("channel", u16, currentProgram),
        new ParameterImpl("first_chunk", new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33BootPduInfo"), 4), currentProgram),
        new ParameterImpl("total_length", u16, currentProgram),
        new ParameterImpl("remaining_capacity", new PointerDataType(u16, 4), currentProgram))
        .setComment("Enabledgateveneerpreservesr9fourthargumentto6374;returns1whendisabled.");
    semanticFunction(0x6B6CL, "f33_boot_transport_request_append", u32,
        new ParameterImpl("channel", u16, currentProgram),
        new ParameterImpl("chunk", new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33BootPduInfo"), 4), currentProgram),
        new ParameterImpl("remaining_capacity", new PointerDataType(u16, 4), currentProgram))
        .setComment("Registerpreserving6464veneer;notvoidone-argumentCfunction.");
    semanticFunction(0x6B7AL, "f33_boot_transport_receive_complete", v,
        new ParameterImpl("channel", u16, currentProgram),
        new ParameterImpl("status", u8, currentProgram))
        .setComment("Correcttypedveneerfor64B8completion.");
    semanticFunction(0x66FAL, "f33_boot_response_copy_chunk", u32,
        new ParameterImpl("channel", u16, currentProgram),
        new ParameterImpl("chunk", new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33BootPduInfo"), 4), currentProgram),
        new ParameterImpl("unused", u32, currentProgram),
        new ParameterImpl("remaining", new PointerDataType(u16, 4), currentProgram))
        .setComment("Outgoingrequestdescriptorlengthlowbytecontrolsactualcopy;consumes30BAremaining,writesr9remaining;caller6B8Aforwardsliveregisters.");
    semanticFunction(0x6B8AL, "f33_boot_transport_response_copy", u32,
        new ParameterImpl("channel", u16, currentProgram),
        new ParameterImpl("chunk", new PointerDataType(currentProgram.getDataTypeManager().getDataType("/CamryF33/F33BootPduInfo"), 4), currentProgram),
        new ParameterImpl("unused", u32, currentProgram),
        new ParameterImpl("remaining", new PointerDataType(u16, 4), currentProgram))
        .setComment("Realresponsechunkcallbackveneerforwardingr7/r8/r9;notvoidone-argument.");
    semanticFunction(0x66BEL, "f33_boot_response_complete", v,
        new ParameterImpl("channel", u16, currentProgram),
        new ParameterImpl("status", u8, currentProgram))
        .setComment("Duringresponse-pendingstate3onlyclearsinflightlock2BBC;othercompletionreleasesrequestownerandmayjointheterminalpath159E.");
    semanticFunction(0x6B98L, "f33_boot_transport_response_complete", v,
        new ParameterImpl("channel", u16, currentProgram),
        new ParameterImpl("status", u8, currentProgram))
        .setComment("Responsecompletionveneerfor66BE;notreceivecompletion64B8.");
    semanticFunction(0x674AL, "f33_boot_response_submit", v,
        new ParameterImpl("mode", u8, currentProgram),
        new ParameterImpl("data", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("length", u16, currentProgram))
        .setComment("Stagesresponseorcompletesasuppressedrequest;forcestransmissionafterprevious78pending.Same-countertickdeferralavoidsimmediatesend,then65AAownsprogress.");
    semanticFunction(0x51FAL, "f33_boot_negative_response", v,
        new ParameterImpl("sid", u8, currentProgram),
        new ParameterImpl("nrc", u8, currentProgram))
        .setComment("Forms7F,SID,NRC;mode0functionalelse2physical;submitslength3.");
    semanticFunction(0x51D8L, "f33_boot_session_publish", v,
        new ParameterImpl("session", u8, currentProgram))
        .setComment("Prioritymaskedpublicationof2B0Efollowed55FCsecurityhandshakereset.");
    semanticFunction(0x6244L, "f33_boot_session_progress", v)
        .setComment("Timer-contextdeferredsessiontransition;waits4794/478Ethenforeground62DCflagbeforepublication/positive50.");
    semanticFunction(0x62DCL, "f33_boot_session_foreground_join", v)
        .setComment("Consumes2BA2flag;preparesdriveronlyif2BD1!=1,thenalwaysclearsflag.");
    semanticFunction(0x6B1EL, "f33_boot_programming_prepare", v)
        .setComment("Clears2BD2,152Adriverprepare/519Cformatinitialize,thenpublishes2BD1=1.");
    semanticFunction(0x4F50L, "f33_boot_transfer_foreground_consume", v)
        .setComment("Readyqueuebridgeonlywhenoperationclass1/2;u16lenfrom2AC4,ringsource2AC0orRAMcopyto2AB8,clear2ACBandadvanceaddress.");
    semanticFunction(0x6AACL, "f33_boot_diagnostic_foreground", v)
        .setComment("Enabledforegroundruns51C8/6E60/6EE0/6BDE/6C8Einthatorder;separatefromtimer51AC.");
    semanticFunction(0x6A06L, "f33_boot_diagnostic_timer_services", v)
        .setComment("Enabledtimer666Cthen51AC;doesnotcallhardwareforeground4428.");
    semanticFunction(0x51ACL, "f33_boot_diagnostic_timer_progress", v)
        .setComment("6244session,5584securitydelay,4A9ADID,5C06routine,4F1Ctransferorderedtimerwork.");
    semanticFunction(0x69D2L, "f33_boot_diagnostic_enable_from_handoff", v)
        .setComment("Enablesonlyhandofftag0orFF;noapplicationDCMinitialization.");
    semanticFunction(0x6A22L, "f33_boot_diagnostic_initialize_from_handoff", v)
        .setComment("Resetsresidentserviceworkers;tag0preparesdriverandreplaysrecordsessionthrough6504;tagFFwaitswithtimestamp.");
    semanticFunction(0x6504L, "f33_boot_diagnostic_replay_handoff_session", v)
        .setComment("Matchchannelrecord8F04/8F0C,forceextendedsession3andreadsubfunction/suppressionfromhandoffword4/5,thenadmit/append/complete10request.");
    semanticFunction(0x65AAL, "f33_boot_response_timer_progress", v)
        .setComment("Ownstimestamp-gatedsend,78pending,inflightlockandoverallterminalstate;doesnotownFACIoperation.");
    semanticFunction(0x666CL, "f33_boot_diagnostic_timeout_progress", v)
        .setComment("Executingrequests\u219265AA;idlesession2/3rawelapsedtimeoutpublishesdefault1.");
    semanticFunction(0x6C8EL, "f33_boot_transfer_compare_progress", v)
        .setComment("Atmost16bytespercall;firstmismatchclearsbusybutkeepsfailure1;onlycompleteall-matchclearsfailure0.");
    semanticFunction(0x4A9AL, "f33_boot_write_did_progress", v)
        .setComment("Waits2BFBjobcompletion;responds6Eor72afterrequestpendinglockclears.");
    semanticFunction(0x5C06L, "f33_boot_routine_timer_progress", v)
        .setComment("ExplicitRIDdispatch10F0/10F1\u21925936,10F2\u21925A04,FF00\u21925B70;noROMcallbackcallthroughFFFFFFFF.");
    semanticFunction(0x4F1CL, "f33_boot_transfer_timer_progress", v)
        .setComment("Downloadstate2\u21924DF2program/copy;10\u21924E92compare,otherwiseclearsactive.");
    semanticFunction(0x5D40L, "f33_boot_download_positive_response", v)
        .setComment("Forms74 20 04 02andpasseslength4inr8to674A;repairmisrenderedmissinglength.");
    semanticFunction(0x5F3EL, "f33_boot_read_did_fill_payload", u32,
        new ParameterImpl("descriptor_index", u8, currentProgram),
        new ParameterImpl("payload_offset", u16, currentProgram))
        .setComment("FirmwarefillsconfiguredDIDpayloadbyteswithliteral0x21;keepscallerregisterABI(notanOEManumberread).");
    semanticFunction(0x6C6CL, "f33_boot_compare_submit", u32,
        new ParameterImpl("left", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("right", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("length", u32, currentProgram))
        .setComment("Returns1ifalreadybusyelse0,setsfailure1/active1andfull32-bitremaining/pointers;4CA2preserveslivelengthr8acrosssetup.");
    semanticFunction(0x6BB4L, "f33_boot_block_transform_submit", u32,
        new ParameterImpl("length", u16, currentProgram),
        new ParameterImpl("source", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("destination", new PointerDataType(u8, 4), currentProgram))
        .setComment("Returns1busy/0accepted;storeslengthu16,pointers,sets2BDEactive;worker6BDEtransformsfull16-byteblocks.");
    semanticFunction(0x32D2L, "f33_boot_classify_service_range", u32,
        new ParameterImpl("start", u32, currentProgram),
        new ParameterImpl("length", u32, currentProgram),
        new ParameterImpl("kind", u8, currentProgram),
        new ParameterImpl("storage_class", new PointerDataType(u8, 4), currentProgram))
        .setComment("Return0/write class byte for first permitted8DA0 range, else1/output unchanged. Require nonzero length and "
            + "unsigned start<=end after modulo32 end=start+length-1. Check kind-mask bit(kind&31) and inclusive bounds. "
            + "Actual classes:0 CodeFlash windows10000..17DFF/18000..FFDFF;1 RAM FEBF0000..0FFF. All rows mask33. Used by "
            + "download, transfer and routine admission.");
    semanticFunction(0x3318L, "f33_boot_service_range_completion_selector", u32,
        new ParameterImpl("start", u32, currentProgram),
        new ParameterImpl("length", u32, currentProgram),
        new ParameterImpl("kind", u8, currentProgram),
        new ParameterImpl("completion_selector", new PointerDataType(u8, 4), currentProgram))
        .setComment("Same nonzero/no-wrap/kind-mask/inclusive predicates as32D2, but output8DA0 row byte+13. Return0/write "
            + "output on match, else1/output unchanged. All current selector bytes are0;567E stores this as2B68 for "
            + "completion bit updates. This is not the storage class or descriptor index.");
    semanticFunction(0x3392L, "f33_boot_lookup_authentication_trailer", u32,
        new ParameterImpl("start", u32, currentProgram),
        new ParameterImpl("length", u32, currentProgram),
        new ParameterImpl("trailer_address", new PointerDataType(u32, 4), currentProgram))
        .setComment("Return0/write nonzero8E00 descriptor+8 pointer for nonzero length with lower<=start and modulo32 "
            + "end<=upper; else1/output unchanged. No explicit start<=end or start<=upper check. Current "
            + "outputs17DF0/FFDF0/FEBF0FF0.7122 stores the pointer for7170 final16-byte comparison; lookup alone does not "
            + "verify CRC or authentication.");
    semanticFunction(0x33CCL, "f33_boot_lookup_completion_marker", u32,
        new ParameterImpl("start", u32, currentProgram),
        new ParameterImpl("length", u32, currentProgram),
        new ParameterImpl("marker_address", new PointerDataType(u32, 4), currentProgram))
        .setComment("Return0/write8E00 descriptor+12 marker address for nonzero length with lower<=start and modulo32 "
            + "end<=upper; else1/output unchanged. No explicit no-wrap check and no null-marker rejection: current "
            + "outputs17E00/FFE00/0.5A04 caller is already kind4/class0 admitted before5286 queues5AA5A55A at the marker.");
    semanticFunction(0x4B7CL, "f33_boot_admit_program_transfer_chunk", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Consume the full low16 request length forwarded from4DBA. Require session2, nonzero remaining, sequence "
            + "admission and payload1..1024, full1024 unless final. Decrement remaining at admission; classify RAM versus "
            + "CodeFlash, stage source/length and transform-or-ready state. Foreground4F50 consumes later; failures "
            + "request queue cancellation.");
    semanticFunction(0x4CA2L, "f33_boot_admit_compare_transfer_chunk", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Consume low16 request length from4DBA with the same payload/sequence shape, but stage comparison rather "
            + "than direct transfer. Preserve payload length in R8 for6C6C; optional block transform precedes comparison. "
            + "Foreground comparison and timer response are separate completion owners.");
    semanticFunction(0x4D8CL, "f33_boot_reject_transfer_state", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Use request length even in unsupported download state: wrong session gives7F; otherwise length<3 gives13, "
            + "else24. Reply through4B38; no input consumption.");
    semanticData(0x8EF4L, new ArrayDataType(u8, 16, 1), "f33_boot_service_session_constants",
        "Service-local required sessions and admission lists; not interrupt-table fields or a single permission bitmask.");
  }

  private void annotateAcquisitionOwnership() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
    StructureDataType layout0 = new StructureDataType(category, "F33AcquisitionGroupPair", 0);
    layout0.setPackingEnabled(true);
    layout0.add(new ArrayDataType(u16, 6, 2), "group0", null);
    layout0.add(new ArrayDataType(u16, 6, 2), "group8", null);
    DataType layout0Type = resolve(layout0);
    StructureDataType layout1 = new StructureDataType(category, "F33SerialAcquisitionRecord", 0);
    layout1.setPackingEnabled(true);
    layout1.add(u16, "field14_0", null);
    layout1.add(u16, "field14_1", null);
    layout1.add(u16, "field12", null);
    layout1.add(u8, "rx_count_failures", null);
    layout1.add(u8, "rx_or_tx_failures", null);
    layout1.add(u8, "crc_failures", null);
    layout1.add(u8, "sequence_failures", null);
    layout1.add(new ArrayDataType(u8, 2, 1), "untouched_tail", null);
    DataType layout1Type = resolve(layout1);
    StructureDataType layout2 = new StructureDataType(category, "F33SerialAcquisitionMasks", 0);
    layout2.setPackingEnabled(true);
    layout2.add(u16, "first", null);
    layout2.add(u16, "second", null);
    DataType layout2Type = resolve(layout2);
    StructureDataType layout3 = new StructureDataType(category, "F33SerialControllerStatus", 0);
    layout3.setPackingEnabled(true);
    layout3.add(u8, "status_bit8", null);
    layout3.add(u8, "status_bit7", null);
    layout3.add(u8, "status_bit3", null);
    layout3.add(u8, "count0_7bit", null);
    layout3.add(u8, "count1_7bit", null);
    layout3.add(u8, "count2_7bit", null);
    DataType layout3Type = resolve(layout3);
    semanticFunction(0x620DCL, "f33_select_acquisition_six_entry_base", u16,
        new ParameterImpl("count", u16, currentProgram),
        new ParameterImpl("capacity", u16, currentProgram))
        .setComment("Odd count selects count-3; even selects count-6 with one capacity addition only when count<6. Return "
            + "low16; caller does not modulo-wrap each following offset. Boundary counts2/4 yield out-of-range zero "
            + "tails, not ring wrap. No freshness/reachability claim.");
    semanticFunction(0x620FEL, "f33_copy_acquisition_group0_samples", v,
        new ParameterImpl("output", new PointerDataType(layout0Type, 4), currentProgram))
        .setComment("Real R6 is the output pointer, not an unused integer. Read descriptor count for channel0, select "
            + "six-entry base with capacity432, consume offsets0..5 from30F2C through60676. Store six u16 at output+0. "
            + "No software cursor advancement, per-entry validity check or retained-value fallback; out-of-range "
            + "returns0.");
    semanticFunction(0x6213EL, "f33_copy_acquisition_group8_samples", v,
        new ParameterImpl("output", new PointerDataType(layout0Type, 4), currentProgram))
        .setComment("Real R6 is the output pointer, not an unused integer. Read descriptor count for channel8, select "
            + "six-entry base with capacity432, consume offsets0..5 from30F34 through60720. Store six u16 at output+12. "
            + "No software cursor advancement, per-entry validity check or retained-value fallback; out-of-range "
            + "returns0.");
    semanticFunction(0x6217EL, "f33_copy_acquisition_group_pair", v,
        new ParameterImpl("output", new PointerDataType(layout0Type, 4), currentProgram))
        .setComment("Call620FE then6213E with the SAME real R6 pointer, saved inR29. Produces group0[6],group8[6] at "
            + "offsets0/12. Fix auto-decompiler missing620FE argument; native62182/62188 explicitly preserve/restore it. "
            + "Descriptor counts are separate reads, not one producer epoch.");
    semanticFunction(0x60676L, "f33_consume_acquisition_group0_entry", u32,
        new ParameterImpl("index", u16, currentProgram))
        .setComment("Index<432: read u32[FEEF81E0+index*4], return(value&7FF8)<<1, and rewrite only retained upper16 (low16 "
            + "cleared). Out-of-range returns0 without access. Ignores low3/bit15 and upper metadata for acceptance; no "
            + "freshness flag or producer-count update.");
    semanticFunction(0x60720L, "f33_consume_acquisition_group8_entry", u32,
        new ParameterImpl("index", u16, currentProgram))
        .setComment("Index<432: read u32[FEEF8A20+index*4], return(value&7FF8)<<1, and rewrite only retained upper16 (low16 "
            + "cleared). Out-of-range returns0 without access. Ignores low3/bit15 and upper metadata for acceptance; no "
            + "freshness flag or producer-count update.");
    semanticFunction(0x66824L, "f33_publish_fast_acquisition_inputs", v)
        .setComment("Buffer twelve halfwords through6217E, then permute group0[0:3],group8[0:3],group0[3:6],group8[3:6] "
            + "to5EC8..5EDE. Then629A2 copies cached serial triplets/counters and publish5F12/14/16,5F1C/1E/20,5F29..30. "
            + "Does NOT write5F18/1A/22/24 ancillary masks. Sequential stores, no validity gate or atomic cross-source "
            + "generation.");
    semanticFunction(0x629A2L, "f33_copy_cached_serial_acquisition_records", v,
        new ParameterImpl("output", new PointerDataType(layout1Type, 4), currentProgram))
        .setComment("Write two12-byte-stride records: threeu16 plus fouru8 occurrence counters; offsets10/11 remain untouched. "
            + "Types ROM31678={0,11}: second record negates modulo14/14/12 bits; first copies raw. Does not acquire, "
            + "validate, clear counters, copy ancillary masks or distinguish current/retained sample.");
    semanticFunction(0x62488L, "f33_decode_serial_acquisition_frame", v,
        new ParameterImpl("channel", u8, currentProgram),
        new ParameterImpl("fifo", u8, currentProgram),
        new ParameterImpl("crc_failure", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("sequence_failure", new PointerDataType(u8, 4), currentProgram))
        .setComment("Caller62576 guarantees channel<2 and initializes verdicts0. Use descriptor low count31676[channel] to "
            + "select two five-u16 FIFO blocks; validate second with623EE. Bad CRC retains sequence/triplet/masks. "
            + "CRC-valid incoming sequence is stored BEFORE next-sequence comparison; mismatch sets5A and retains "
            + "triplet/masks while resynchronizing. Accepted14/14/12-bit fields write38D0+12*channel and OR two11-bit "
            + "masks through6245A. No FIFO acknowledgment.");
    semanticFunction(0x62576L, "f33_sample_serial_acquisition_channel", v,
        new ParameterImpl("channel", u8, currentProgram))
        .setComment("Channel<2: snapshot61054 into38E8+6*channel. Only status.byte2==0 and byte3==10 decode62488. Otherwise "
            + "retain decoded sample and set RX/count failure. CRC/sequence local flags reset0 on every call before "
            + "admission; publish scratch+29/+2A/+2B/+2D verdicts, not counters.");
    semanticFunction(0x627E0L, "f33_accumulate_serial_acquisition_failures", v,
        new ParameterImpl("channel", u8, currentProgram))
        .setComment("Channel<2: increment wrappingu8 counters38D6..D9+12*channel for missing/wrong RX count, combined "
            + "RX-status or TX-submission failure, software CRC failure, sequence failure. Equality5A only. Numeric "
            + "retention and sequence acceptance are separate; zero after wrap is not healthy/fresh proof.");
    semanticFunction(0x62846L, "f33_service_serial_acquisition_channel", v,
        new ParameterImpl("channel", u8, currentProgram))
        .setComment("Run62576, then command/reply branch selected by "
            + "entry39D8&3:0->62636(0),626D6(1);1->6276C(0);2->62636(1),626D6(0);3->6276C(1). Call60F7C(channel,0), "
            + "then627E0. Sample decoding can fail/retain while a current command error updates counters. Task "
            + "advances39D8 only after both channels and application dispatch.");
    semanticFunction(0x6289CL, "f33_service_serial_acquisition_pair", v)
        .setComment("Service logical channels0 then1 through62846, without incrementing task phase between them.66786 invokes "
            + "this before66824 caches serial samples/counters. No ADC or serial timing guarantee.");
    semanticFunction(0x6245AL, "f33_accumulate_serial_acquisition_masks", v,
        new ParameterImpl("channel", u8, currentProgram),
        new ParameterImpl("first_mask", u16, currentProgram),
        new ParameterImpl("second_mask", u16, currentProgram))
        .setComment("Channel<2: OR accepted11-bit frame masks into scratch+30/+38 arrays using(cursor+2E&3). Does not advance "
            + "cursor, clear prior slot or publish application masks.6294E owns cursor advancement and previous-slot "
            + "clear.");
    semanticFunction(0x6294EL, "f33_rotate_and_copy_serial_acquisition_masks", v,
        new ParameterImpl("output", new PointerDataType(layout2Type, 4), currentProgram))
        .setComment("For channels0/1: clear mask arrays at previous(cursor-1)&3, read current first mask, advance "
            + "cursor(cursor+1)&3, publish first mask then read/publish current second mask. Output two4-byte mask "
            + "pairs. Current slot is not cleared in this call.66932 publication5F18/1A/22/24 belongs to another task "
            + "generation than66824 numeric/counters.");
    semanticFunction(0x62192L, "f33_initialize_serial_acquisition_channel", v,
        new ParameterImpl("channel", u8, currentProgram))
        .setComment("Channel<2: clear driver buffers/flags/four-slot mask arrays/cursor and published occurrence counters; "
            + "seed prior sequence3 and numeric triplet{0,0,0800}. First valid incoming sequence0 qualifies. No "
            + "acquisition completed by initialization.");
    semanticFunction(0x61054L, "f33_read_serial_controller_status", v,
        new ParameterImpl("channel", u8, currentProgram),
        new ParameterImpl("acknowledgment", u16, currentProgram),
        new ParameterImpl("output", new PointerDataType(layout3Type, 4), currentProgram))
        .setComment("Physical channel<2: ROM3140C+50*channel selects controller block. Snapshot status bits8/7/3 and "
            + "three7-bit counts into six bytes, then acknowledge with halfword(ack&100)|(status&8).62576 uses byte2==0 "
            + "and byte3==10; other status bytes do not gate decoding there. This is register contract, not current "
            + "sample age.");
    semanticFunction(0x61008L, "f33_copy_serial_fifo_words", v,
        new ParameterImpl("channel", u8, currentProgram),
        new ParameterImpl("output", new PointerDataType(u16, 4), currentProgram),
        new ParameterImpl("offset", u8, currentProgram),
        new ParameterImpl("count", u8, currentProgram))
        .setComment("Channel<2 and offset<=configured_capacity-count: copy countu16 words from ROM313FC[channel] FIFO; caller "
            + "uses capacity20 and count5. No wrap, clear, cursor advance, status check or return verdict; rejected "
            + "bounds leave destination unchanged.");
    semanticFunction(0x60934L, "f33_read_transfer_primary_count_low", u32,
        new ParameterImpl("channel", u8, currentProgram))
        .setComment("Return low16 of u32[FFFF8408+64*low8(channel)]. No<16 bounds gate here;62488 supplies ROM channels2/10. "
            + "Distinct from60940 combined-count calculation. This SFR is an explicit native model boundary, not "
            + "ordinary RAM.");
    semanticFunction(0x50B6AL, "f33_copy_acquisition_banks_to_application", v)
        .setComment("Copy fast5EC8..5EDE banks into application822C..8242: group first triples ->8238/823E reference-side "
            + "inputs; group last triples ->822C/8232 measured-side inputs. No validity/freshness test.5DE82 mode>FF "
            + "admits copy, mode>100 admits downstream conditioning.");
    semanticFunction(0x50BBCL, "f33_copy_serial_acquisition_to_application", v)
        .setComment("Publish first two cached serial fields shiftedleft2, third unchanged; expand eight cached wrapping "
            + "counters5F29..30 to interleaved application8244..4B; independently copy masks5F18/1A/22/24 "
            + "->8258/5A/5C/5E. These mask fields come from66932/6294E, not629A2, and may be another generation. No "
            + "per-call validity gate.");
    semanticData(0x30F2CL, new ArrayDataType(u8, 6, 1), "f33_acquisition_group0_offsets",
        "Exact00,01,02,03,04,05; next2bytes padding not part of six-entry loop.");
    semanticData(0x30F34L, new ArrayDataType(u8, 6, 1), "f33_acquisition_group8_offsets",
        "Exact00,01,02,03,04,05.");
    semanticData(0x31674L, new ArrayDataType(u8, 2, 1), "f33_serial_acquisition_fifo_channels",
        "Exact0,1, driver FIFO/status selection.");
    semanticData(0x31676L, new ArrayDataType(u8, 2, 1), "f33_serial_acquisition_transfer_channels",
        "Exact2,10 descriptor low-count selection.");
    semanticData(0x31678L, new ArrayDataType(u8, 2, 1), "f33_serial_acquisition_field_encoding",
        "Exact0,11;11 selects modular negation in629A2.");
    semanticData(0xFEBE38D0L, new ArrayDataType(layout1Type, 2, 12), "f33_serial_acquisition_retained_records",
        "Two12byte decoded records; numeric fields retained on missing/rejected input; counters separately accumulated.");
    semanticData(0xFEBE5EC8L, new ArrayDataType(u16, 12, 2), "f33_acquisition_application_sample_banks",
        "Permuted group0 first3,group8 first3,group0 last3,group8 last3; no freshness marker.");
    semanticData(0xFEBE5F29L, new ArrayDataType(u8, 8, 1), "f33_serial_acquisition_failure_counter_snapshot",
        "Channel0 four counters thenchannel1 four;wrapping occurrences,not validity flags.");
  }
  private void annotateResidentSecurityCrypto() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
    StructureDataType layout0 = new StructureDataType(category, "F33BootAes128Context", 0);
    layout0.setPackingEnabled(true);
    layout0.add(new ArrayDataType(u8, 176, 1), "round_keys", null);
    layout0.add(new ArrayDataType(u8, 16, 1), "row_order_state", null);
    layout0.add(u8, "valid", null);
    layout0.add(u8, "round", null);
    layout0.add(new ArrayDataType(u8, 2, 1), "padding", null);
    DataType layout0Type = resolve(layout0);
    StructureDataType layout1 = new StructureDataType(category, "F33BootAes128CtrContext", 0);
    layout1.setPackingEnabled(true);
    layout1.add(layout0Type, "aes", null);
    layout1.add(new ArrayDataType(u8, 16, 1), "cleared_extension", null);
    layout1.add(new ArrayDataType(u8, 16, 1), "counter_be", null);
    DataType layout1Type = resolve(layout1);
    StructureDataType layout2 = new StructureDataType(category, "F33BootChallengeExclusionRecord", 0);
    layout2.setPackingEnabled(true);
    layout2.add(new ArrayDataType(new PointerDataType(u8, 4), 3, 4), "excluded_blocks", null);
    layout2.add(u8, "count", null);
    layout2.add(new ArrayDataType(u8, 3, 1), "padding", null);
    DataType layout2Type = resolve(layout2);
    semanticFunction(0x5328L, "f33_boot_security_seed_request", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Resident SID27 seed request. Active delay==1 gives37 before exact18-byte length check13. State1 copies16 "
            + "client bytes from request+2 to2B34, calls6F22 into2B24 ignoring its0/1 status, copies challenge to2B44 "
            + "and schedules handshake2 after response submission returns. State2 replaces client material but reuses "
            + "same challenge. State3 returns16 zero response bytes without changing client. Invalid handshake0/>3 "
            + "silently normalizes1. Valid paths preserve original subfunction at2B54 and form67 response via52DE. Not a "
            + "successful native unlock/entropy claim.");
    semanticFunction(0x53F2L, "f33_boot_security_key_request", v,
        new ParameterImpl("request_length", u16, currentProgram))
        .setComment("Only handshake2 checks exact18-byte request and derives expected16 bytes at currentSP "
            + "using704C(client2B34,challenge2B24,SP). Compare is early-exit bytewise, not constant-time. Valid key "
            + "storessecurity2,clearsfailurecountandchallenge,forms6702,pendinghandshake3inr29;2B55=3onlyafter52DE/674Areturns. "
            + "First mismatch increments shared failed count and35,pendingstate1; second mismatch or second "
            + "malformed-length attempt captures raw counter "
            + "andstarts200000000delay,clearscount/challenge,gives36,pendingstate1. First malformed length13 also "
            + "counts. States1/3reject24;state0/>3silentlynormalizes1.No explicit delay gate in key path.");
    semanticFunction(0x6F22L, "f33_boot_security_generate_challenge", u32,
        new ParameterImpl("challenge_out", new PointerDataType(u8, 4), currentProgram))
        .setComment("Output-only r6 pointer; return r10=0 accepted transformed candidate,1 fallback raw timer-derived16 bytes. "
            + "Two-attempt rejection sampler:48D2 gathers low16bits of8 raw timer reads big-endian into16-byte stack "
            + "key;72D6 initializesAES128CTRwithzeroROM8FD0counter;729C transformszeroROM8FC0block into "
            + "AES_timerkey(0^128);7346wipes228-byteCTRcontext2E0C. Exclude zero andFF "
            + "blocks;afterprioracceptedoutputalsoexclude2D38. Onaccepted candidatecopyto2D38andset30B4=1. "
            + "Onsecondrejection/libraryfailurecopylast rawstackkeytooutputwithoutupdatinghistory. No entropy-quality "
            + "guarantee. Incoming r28 is NOT an ABI argument: both ROM records have nonzero count2/3, and each "
            + "comparison initializes r28 before use.");
    semanticFunction(0x6FECL, "f33_boot_security_decrypt_client_material", v,
        new ParameterImpl("client_material", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("intermediate_key", new PointerDataType(u8, 4), currentProgram))
        .setComment("AES-128 single-block DECRYPT client_material under exactROMBFE8 key into intermediate_key;not encryption "
            + "andnotCMAC. Shared AES contextFEBF2D48 init7680,length16,decrypt7470,length16,clear76C6.");
    semanticFunction(0x701EL, "f33_boot_security_encrypt_block", v,
        new ParameterImpl("key", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("plaintext", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("ciphertext", new PointerDataType(u8, 4), currentProgram))
        .setComment("AES-128 single-block encryption with16-byte key/input/output,using shared "
            + "contextFEBF2D48;clearsentire196-bytecontextafteroperation. r6key,r7plaintext,r8output; "
            + "noapplicationGP/SecOCsemantics.");
    semanticFunction(0x704CL, "f33_boot_security_derive_expected_key", v,
        new ParameterImpl("client_material", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("challenge", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("expected_key", new PointerDataType(u8, 4), currentProgram))
        .setComment("Expected key = AES128_ENCRYPT(AES128_DECRYPT(ROM[BFE8..BFF7], client_material), challenge). The16-byte "
            + "intermediate is stack-local, not CMAC, hash or a seed-only mapping. Both operations clear the "
            + "shared196-byte context; intermediate and expected-key stack buffers are not explicitly cleared. "
            + "Independent known-answer native composition verifies this transform, not complete transport/unlock.");
    semanticFunction(0x7352L, "f33_boot_aes128_encrypt_block", u32,
        new ParameterImpl("plaintext", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("ciphertext", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("length", u8, currentProgram),
        new ParameterImpl("context", new PointerDataType(layout0Type, 4), currentProgram))
        .setComment("SoftwareAES128singleblock:requirelength16andcontext.valid1;row-orientedstateat+B0,10rounds,noMixColumnsinlastround,outputstandardcolumnorder.Return0success,FFinvalid.Exact-leaflive-registerpreservation "
            + "matters:7B42callswithr8=16/r9contextalreadylive.");
    semanticFunction(0x7470L, "f33_boot_aes128_decrypt_block", u32,
        new ParameterImpl("ciphertext", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("plaintext", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("length", u8, currentProgram),
        new ParameterImpl("context", new PointerDataType(layout0Type, 4), currentProgram))
        .setComment("SoftwareinverseAES128singleblock;length16andvalid1;round10AddRoundKeythen10inverseShiftRows/inverseSubBytes/AddRoundKeyroundswithinverseMixColumnsonlynonfinalrounds;return0/FF.");
    semanticFunction(0x7680L, "f33_boot_aes128_initialize_context", u32,
        new ParameterImpl("key", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("key_length", u8, currentProgram),
        new ParameterImpl("context", new PointerDataType(layout0Type, 4), currentProgram))
        .setComment("Only16-bytekeyaccepted;clearstate/valid/round,expand44words=176byteswith7594,setvalid1.Return0orFF.7594preserveslivecontextpointerr8at76ACdespiteordinarydecompilerextraout_r8;useexistingexact-leafinliningconventionratherthaninventingextraABIresult.");
    semanticFunction(0x76C6L, "f33_boot_aes128_clear_context", v,
        new ParameterImpl("context", new PointerDataType(layout0Type, 4), currentProgram))
        .setComment("Clearvalidthenall196bytesvia76B6wordzero loop.");
    semanticFunction(0x729CL, "f33_boot_security_generate_candidate_block", u32,
        new ParameterImpl("challenge_out", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("context", new PointerDataType(layout1Type, 4), currentProgram))
        .setComment("CopyzeroROM8FC0blocktostack;7B42AESCTRtransformintooutputusingr9context.Return0/FF.");
    semanticFunction(0x72D6L, "f33_boot_security_initialize_candidate_context", u32,
        new ParameterImpl("timer_key", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("key_length", u8, currentProgram),
        new ParameterImpl("context", new PointerDataType(layout1Type, 4), currentProgram))
        .setComment("CopyROM8FD0zero16-bytecounter;onlylength16;call7C9A(key,16,counter,16,context)withfifthargstack+0atcallerSP.Return0/FF.");
    semanticFunction(0x7346L, "f33_boot_security_clear_candidate_context", v,
        new ParameterImpl("context", new PointerDataType(layout1Type, 4), currentProgram))
        .setComment("Forwardr6to7D3C,wipeentire228-byteAESCTRcontext;notzeroargumentdespitemissingpseudoparameter.");
    semanticFunction(0x5584L, "f33_boot_security_delay_progress", v)
        .setComment("Onlydelayflag1:unsigned32elapsed=(timer-start),cleardelayonlyelapsed>duration(strict);doesnotresetfailures,handshake,security,buffers.Timer51ACownsperiodiccall;noexplicitseconds.");
    semanticFunction(0x55AAL, "f33_boot_security_initialize_handshake", v)
        .setComment("Installraw200000000durationandcapturecounter;setdelay1,failcount0;clearretainedchallenge/client/responsechallenge;lastsubfunction0;handshake1.Doesnotitselfstoresecurity2B0Fanddoesnotresetprevious-challenge2D38/30B4.5086setsinitialsession1/security1;50EAsetsession2withoutitsownsecuritystore.");
    semanticFunction(0x55FCL, "f33_boot_security_invalidate_handshake", v)
        .setComment("Calledbyprioritymasked51D8sessionpublication.Ifhandshake1:securityunchanged;handshake2:clear16challengebyteswithoutwritingsecurity;otherstates(includingaccepted3):security1.Thenhandshake1.Retainsclient,responsecache,failcount,delay/history.");
    semanticFunction(0x562AL, "f33_boot_security_cancel_delay", v)
        .setComment("Onlyclearactive-delayflag.5148callsonapplicationhandoffreplaypath6504;doesnotresetfailurecountorhandshakeorclient/challenge.");
    semanticFunction(0x7594L, "f33_boot_aes128_expand_round_keys", v,
        new ParameterImpl("key", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("round_keys", new PointerDataType(u8, 4), currentProgram))
        .setComment("Expand16 key bytes into176 bytes (44 words), using the standard forward S-box and ten round constants. "
            + "Exact leaf preserves incoming R8 context, subsequently used at76AC; inline real p-code instead of "
            + "inventing another return value.");
    semanticFunction(0x7C9AL, "f33_boot_aes128_ctr_initialize", u32,
        new ParameterImpl("key", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("key_length", u8, currentProgram),
        new ParameterImpl("counter", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("counter_length", u8, currentProgram),
        new ParameterImpl("context", new PointerDataType(layout1Type, 4), currentProgram))
        .setComment("Require low8 key/counter lengths16. Fifth argument is context at callerSP+0, calleeSP+8 after saves. "
            + "Clear extension, copy16-byte big-endian counter to+D4 and initialize AES context. Return0 success orFF "
            + "invalid.");
    semanticFunction(0x7B42L, "f33_boot_aes128_ctr_transform_block", u32,
        new ParameterImpl("input", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("output", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("length", u8, currentProgram),
        new ParameterImpl("context", new PointerDataType(layout1Type, 4), currentProgram))
        .setComment("Require length16, valid context and counter not allFF. Encrypt counter, XOR16 input bytes into output, "
            + "increment counter as128-bit big-endian. Return0 orFF. R8 length andR9 context remain live for7352; not an "
            + "arbitrary-length streaming API.");
    semanticFunction(0x7D3CL, "f33_boot_aes128_ctr_clear", v,
        new ParameterImpl("context", new PointerDataType(layout1Type, 4), currentProgram))
        .setComment("Clear valid then all228 context bytes through76B6. Does not clear caller stack buffers or retained "
            + "challenge history.");
    semanticData(0x8FA0L, layout2Type, "f33_boot_security_initial_exclusions",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    semanticData(0x8FB0L, layout2Type, "f33_boot_security_history_exclusions",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    semanticData(0xBFE8L, new ArrayDataType(u8, 16, 1), "f33_boot_security_client_decryption_key",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    semanticData(0xFEBF2B1CL, u32, "f33_boot_security_delay_duration",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    semanticData(0xFEBF2B20L, u32, "f33_boot_security_delay_start",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    semanticData(0xFEBF2B24L, new ArrayDataType(u8, 16, 1), "f33_boot_security_challenge",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    semanticData(0xFEBF2B34L, new ArrayDataType(u8, 16, 1), "f33_boot_security_client_material",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    semanticData(0xFEBF2B44L, new ArrayDataType(u8, 16, 1), "f33_boot_security_response_challenge",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    semanticData(0xFEBF2B54L, u8, "f33_boot_security_request_subfunction",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    semanticData(0xFEBF2B55L, u8, "f33_boot_security_handshake_state",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    semanticData(0xFEBF2B56L, u8, "f33_boot_security_delay_active",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    semanticData(0xFEBF2B57L, u8, "f33_boot_security_failed_attempts",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    semanticData(0xFEBF2D38L, new ArrayDataType(u8, 16, 1), "f33_boot_security_previous_accepted_challenge",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    semanticData(0xFEBF2D48L, layout0Type, "f33_boot_security_aes_context",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    semanticData(0xFEBF2E0CL, layout1Type, "f33_boot_security_candidate_context",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    semanticData(0xFEBF30B4L, u8, "f33_boot_security_challenge_history_valid",
        "Resident security lifetime only; not application SecOC ownership. See challenge, protocol and context contracts.");
    // The real leaf preserves R8 used by the context-valid store after expansion.
    getFunctionAt(toAddr(0x7594L)).setInline(true);
    semanticData(0x8FF1L, new ArrayDataType(u8, 256, 1), "CRYPT_AES_Encryption_SBox",
        "Standard forward AES substitution box; used by key expansion and forward rounds.");
    semanticData(0x90F1L, new ArrayDataType(u8, 256, 1), "CRYPT_AES_Decryption_SBox_Inverse",
        "Standard inverse AES substitution box; preserve established Findcrypt name.");
  }
  private void annotatePhaseModulation() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
    semanticFunction(0x38C7CL, "f33_transform_first_regulated_phase_commands", v)
        .setComment("Transform limited first-bank axes with output-frame sine/cosine coefficients. Signed division truncates "
            + "toward zero. Compute third phase from the negative sum of UNSATURATED first/second intermediates; publish "
            + "all three saturated to +/-32767 at6E68/6A/6C. Measured-current and reference-compensation transforms are "
            + "different producers.");
    semanticFunction(0x38D6CL, "f33_transform_second_regulated_phase_commands", v)
        .setComment("Second-bank output-frame transform to6E70/72/74. Third phase uses unsaturated intermediate sum before its "
            + "own +/-32767 clamp. Native nonzero composition covers both banks, subsequent compensation, modulation and "
            + "losing slot0 publication.");
    semanticFunction(0x37C4CL, "f33_select_phase_modulation_modes", v)
        .setComment("Square signed16 axis pairs6C40/42 and6C44/46 into unsigned32 energies6D64/68. Curve input is "
            + "low16(energy>>12), with32-count interpolation and fixed endpoint beyond index126. Selector6D6C swaps "
            + "upper/lower offset maps between banks. Each8B88/89==5A overrides energy with mode0 and offset6144. "
            + "Otherwise energy<6166256 gives0, <54546923 gives5A, elseA5. These are software modulation classes, not "
            + "physical bridge states.");
    semanticFunction(0x368B0L, "f33_map_phase_compensation_gain", v)
        .setComment("Use saturating absolute signed16 command6E0A to interpolate unsigned ordinates of2BD10 with16-count "
            + "spacing; index>=127 returns1024. Publish6BE4. Table x words and finalFFFFFFFF row are not read by this "
            + "consumer.");
    semanticFunction(0x36678L, "f33_refresh_phase_compensation_amplitude", v)
        .setComment("Only8A14==1 recomputes32-bit6B98; otherwise retain it. Exact calibrated7DB2 base curve collapses to100. "
            + "WhenEAC6<512, abs(7EA8)>683 reduces the base toward0 at3413, and above3413 selects0. Scale by6BE4/1024. "
            + "No recovered physical units; native composition exercises retained amplitude, not this entire "
            + "recomputation surface.");
    semanticFunction(0x36750L, "f33_compensate_first_regulated_phases", v)
        .setComment("Retain raw regulated triplet in6BB4/B8/BC. Reference6E58/5A/5C selects signed compensation bounded by "
            + "+/-6B98, linear within +/-96. Always calculate6BA8/AC/B0; modeA5 suppresses ADDITION, not calculation. "
            + "Publish adjusted32-bit triplet6B9C/BA0/BA4.");
    semanticFunction(0x367FEL, "f33_compensate_second_regulated_phases", v)
        .setComment("Second bank: reference6E60/62/64 and regulated6E70/72/74; raw backup6BD8/DC/E0, computed "
            + "deltas6BCC/D0/D4, adjusted6BC0/C4/C8. ModeA5 retains raw output despite nonzero computed deltas. Signed "
            + "divisions truncate toward zero.");
    semanticFunction(0x38842L, "f33_modulate_first_phase_triplet", v)
        .setComment("Mode0 adds the recovered offset. Mode5A aligns max to11426 when selector5A, otherwise min to492. Other "
            + "modes choose upper12288-max when3*max>12288, otherwise0-min, then clamp each32-bit sum to0..12288. "
            + "Publish halfwords6E3A/3C/3E; subsequent scaling and arbitration remain distinct.");
    semanticFunction(0x3894CL, "f33_modulate_second_phase_triplet", v)
        .setComment("Paired modulation to6E4A/4C/4E. Mode5A selects upper alignment for selectorA5, opposite the first bank. "
            + "Mode0 adds its offset; other modes use the same strict3*max threshold and0..12288 clamp. Native "
            + "composition exercises first5A and secondA5 with nonzero deltas.");
    semanticFunction(0x37DE4L, "f33_initialize_phase_offset_selector", v)
        .setComment("Set selector6D6C=5A, adjacent byte6D6D=0 and counter6D6E=0. This initializes software offset alternation, "
            + "not a PWM period or electrical phase.");
    semanticFunction(0x37DF4L, "f33_advance_phase_offset_selector", v)
        .setComment("Increment low16 counter; entry>=125 or increment reaching125 resets counter and toggles5A toA5, any other "
            + "selector to5A. ROM31B18 then overrides to5A for33 orA5 for22; exact value11 leaves alternation enabled. "
            + "No physical cadence inferred.");
    semanticFunction(0x575F6L, "f33_reduce_phase_output_code_limits", v)
        .setComment("Per bank, reduce three unsigned requested limits from nominal8000 only when cached minimum/complement "
            + "disagree. Publish minimum8B92/9C and flag8B88/89=5A exactly when below8000. Thus ordinary reduced limits "
            + "also force mode0 in37C4C. Self-consistent caches are retained; not an independent bridge-disable "
            + "permission.");
    semanticFunction(0x57484L, "f33_stage_phase_output_history", v)
        .setComment("Average current/prior triplets only when both new and previous selected indices are0, ROM3190C!=5A and "
            + "the threshold conditions admit. Nonzero winners bypass averaging but still shift current to prior and "
            + "prior to older history, and publish winner indices8B5C/D plus averaging flags8B5E/F. Hardware commit "
            + "occurs later.");
    semanticFunction(0x57DF0L, "f33_stage_live_phase_halfword_compares", v)
        .setComment("Forward selected triplets8BEE/F0/F2 and8BF4/F6/F8 through669DA and66A40 into halfword compare staging. No "
            + "arbitration, recomputation or hardware commit here.");
    semanticFunction(0x57FD2L, "f33_publish_current_control_snapshot", v)
        .setComment("Unconditionally publish the current-control diagnostic snapshotEC00..24, including raw5F36 and retained "
            + "command/current/limit fields.5E202 calls this even when control computation and output staging are both "
            + "skipped. No atomic acquisition generation is implied.");
    semanticData(0x31AE4L, u16, "f33_phase_forced_offset",
        "Exact6144; used when the published code-limit flag is5A.");
    semanticData(0x31AE8L, u32, "f33_phase_modulation_first_energy_threshold",
        "Exact6166256; inclusive transition from0 to5A.");
    semanticData(0x31AECL, u32, "f33_phase_modulation_second_energy_threshold",
        "Exact54546923; inclusive transition toA5.");
    semanticData(0x31B18L, u8, "f33_phase_offset_selector_override",
        "Exact11;33 forces5A and22 forcesA5 after counter progression.");
    semanticData(0x31B26L, u16, "f33_phase_offset_selector_period",
        "Exact125 software advances, not an established hardware time.");
    semanticData(0xFEBE6D6CL, u8, "f33_phase_offset_selector",
        "Alternating5A/A5; chooses opposite upper/lower alignment between banks.");
    semanticData(0xFEBE6D6EL, u16, "f33_phase_offset_selector_counter",
        "Reset/toggled on reaching125; independent from arbitration winner indices.");
    DataType point = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33CurvePointS16U16");
    if (point == null) throw new IllegalStateException("missing exact-F33 curve point layout");
    semanticData(0x2BD10L, new ArrayDataType(point, 129, 4), "f33_phase_compensation_gain_curve",
        "128 numerical rows followed by FFFFFFFF. These consumers index ordinates directly and use fixed endpoint constants, not the sentinel.");
    semanticData(0x2BF14L, new ArrayDataType(point, 129, 4), "f33_phase_upper_modulation_offset_curve",
        "128 numerical rows followed by FFFFFFFF. These consumers index ordinates directly and use fixed endpoint constants, not the sentinel.");
    semanticData(0x2C118L, new ArrayDataType(point, 129, 4), "f33_phase_lower_modulation_offset_curve",
        "128 numerical rows followed by FFFFFFFF. These consumers index ordinates directly and use fixed endpoint constants, not the sentinel.");
  }
  private void annotateResidentImageCrypto() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType F33BootAes128ContextType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33BootAes128Context");
    if (F33BootAes128ContextType == null) throw new IllegalStateException("missing resident AES context layout");
    StructureDataType imageLayout0 = new StructureDataType(category, "F33BootAes128CbcContext", 0);
    imageLayout0.setPackingEnabled(true);
    imageLayout0.add(F33BootAes128ContextType, "aes", null);
    imageLayout0.add(new ArrayDataType(u8, 16, 1), "previous_ciphertext", null);
    imageLayout0.add(new ArrayDataType(u8, 16, 1), "unused_extension", null);
    DataType F33BootAes128CbcContextType = resolve(imageLayout0);
    StructureDataType imageLayout1 = new StructureDataType(category, "F33BootAes128CmacContext", 0);
    imageLayout1.setPackingEnabled(true);
    imageLayout1.add(F33BootAes128ContextType, "aes", null);
    imageLayout1.add(new ArrayDataType(u8, 16, 1), "chain", null);
    imageLayout1.add(new ArrayDataType(u8, 16, 1), "subkey1", null);
    imageLayout1.add(new ArrayDataType(u8, 16, 1), "subkey2", null);
    imageLayout1.add(u8, "subkeys_ready", null);
    imageLayout1.add(new ArrayDataType(u8, 3, 1), "padding", null);
    DataType F33BootAes128CmacContextType = resolve(imageLayout1);
    semanticFunction(0x7068L, "f33_boot_image_derive_key", v)
        .setComment("Derive retained2D18=AES128_ENCRYPT(ROMBFD8,configured2D08),one16-byte block. Shared AES2D48 "
            + "cleared196bytes afterward; configured/derived buffers retained. Distinct from SID27 BFE8 decrypt "
            + "derivation.");
    semanticFunction(0x709AL, "f33_boot_image_initialize_contexts", v)
        .setComment("Initialize CBC2EF0 with derived key2D18/IV2CF8; initialize CMAC2C00 same key with zero chain then derive "
            + "CMAC subkeys. Wrapper ignores all statuses. Does not consume authentication prefix yet.");
    semanticFunction(0x70D4L, "f33_boot_image_crypto_initialize", v)
        .setComment("Derive image key7068 then initialize both CBC/CMAC709A. Reinitializes shared image contexts, not a "
            + "per-transfer-chunk action.");
    semanticFunction(0x70E4L, "f33_boot_image_clear_contexts", v)
        .setComment("Clear CBC2EF0 all228 bytes then CMAC2C00 all248 bytes. Retain IV/material/derived key/output and "
            + "authentication cursors; does not reset activity flags.");
    semanticFunction(0x70FCL, "f33_boot_image_crypto_clear", v)
        .setComment("Forward to70E4, wiping CBC and CMAC contexts only. TransferExit6BD2 and routine completion6F04 share this "
            + "owner.");
    semanticFunction(0x7108L, "f33_boot_image_decrypt_block", u32,
        new ParameterImpl("ciphertext", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("plaintext", new PointerDataType(u8, 4), currentProgram))
        .setComment("AES128-CBC decrypt one16-byte block with persistent2EF0 context through8162. Return0 success or1 failure; "
            + "foreground6BDE ignores this return.");
    semanticFunction(0x7122L, "f33_boot_image_authentication_begin", u32,
        new ParameterImpl("start", u32, currentProgram),
        new ParameterImpl("length", u32, currentProgram))
        .setComment("Select fixed descriptor trailer; feed configured IV2CF8 as NONFINAL16-byte CMAC prefix into2D28; on "
            + "success seed cursor=start and last_block=start+length-16. Return0/1. No length-multiple/minimum/alignment "
            + "validation; context must already be initialized. Trailer is stored even if prefix update fails.");
    semanticFunction(0x7170L, "f33_boot_image_authentication_step", u32)
        .setComment("One16-byte CMAC update or exact-trailer skip. Final when cursor==last_block OR "
            + "cursor+16==last_block==trailer. Final compares16 bytes early-exit, incrementing trailer cursor only for "
            + "equal bytes. Return2busy/0match/1failure; data cursor always advances16, including skip/failure. Does not "
            + "wipe or invalidate context.");
    semanticFunction(0x7D50L, "f33_boot_aes128_cmac_derive_subkeys", u32,
        new ParameterImpl("context", new PointerDataType(F33BootAes128CmacContextType, 4), currentProgram))
        .setComment("AES_K(16 zero ROM91F1 bytes), then big-endian128-bit doubling twice; XOR87 into low byte for each "
            + "high-bit carry. Store K1 at+D4,K2 at+E4,ready1 at+F4. Return0/FF.");
    semanticFunction(0x7E0CL, "f33_boot_aes128_cmac_update_block", u32,
        new ParameterImpl("input", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("output", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("length", u8, currentProgram),
        new ParameterImpl("final_block", u32, currentProgram),
        new ParameterImpl("context", new PointerDataType(F33BootAes128CmacContextType, 4), currentProgram))
        .setComment("AES128-CMAC update. Nonfinal length16; final==1 allows1..16 (zero rejected). Full final XOR K1; partial "
            + "final80/zero pad XOR K2. XOR retained chain, encrypt, copy output to chain. Require "
            + "AES.valid1/subkeys_ready1. Return0/FF; does NOT invalidate/finalize-latch or wipe. Fifth arg callerSP+0.");
    semanticFunction(0x7FB4L, "f33_boot_aes128_cmac_initialize", u32,
        new ParameterImpl("key", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("key_length", u8, currentProgram),
        new ParameterImpl("context", new PointerDataType(F33BootAes128CmacContextType, 4), currentProgram))
        .setComment("Require key length16, clear AES.valid and49-byte chain/K1/K2/ready extension, initialize shared AES base. "
            + "Does not derive subkeys;7D50 required separately. Return0/FF.");
    semanticFunction(0x7FFCL, "f33_boot_aes128_cmac_clear", v,
        new ParameterImpl("context", new PointerDataType(F33BootAes128CmacContextType, 4), currentProgram))
        .setComment("Clear valid then all248 CMAC context bytes through76B6; not caller configured key/material or output.");
    semanticFunction(0x8162L, "f33_boot_aes128_cbc_decrypt_block", u32,
        new ParameterImpl("ciphertext", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("plaintext", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("length", u8, currentProgram),
        new ParameterImpl("context", new PointerDataType(F33BootAes128CbcContextType, 4), currentProgram))
        .setComment("Require length16 and AES.valid1; decrypt ciphertext to16-byte local, XOR previous_ciphertext at+C4 into "
            + "output, then copy original input into previous_ciphertext. Return0/FF. Input/output aliasing not "
            + "generally supported inside primitive;6BDE uses separate local output then copies back, preserving "
            + "in-place transfer chain.");
    semanticFunction(0x82B6L, "f33_boot_aes128_cbc_initialize", u32,
        new ParameterImpl("key", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("key_length", u8, currentProgram),
        new ParameterImpl("iv", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("iv_length", u8, currentProgram),
        new ParameterImpl("context", new PointerDataType(F33BootAes128CbcContextType, 4), currentProgram))
        .setComment("Require low8 key/IV lengths16; clear AES.valid, copyIV to+C4, initialize AES base under key, setvalid1 on "
            + "success. Return0/FF. Fifth argument callerSP+0/calleeSP+8. Does not initialize unused final16 bytes "
            + "of228-byte clear allocation.");
    semanticFunction(0x834EL, "f33_boot_aes128_cbc_clear", v,
        new ParameterImpl("context", new PointerDataType(F33BootAes128CbcContextType, 4), currentProgram))
        .setComment("Clear AES.valid then entire228-byte CBC allocation through76B6. Does not clear configured IV/key "
            + "material.");
    semanticFunction(0x6BA8L, "f33_boot_transfer_crypto_initialize", v)
        .setComment("SID34 optional-transform setup forwards70D4; derives image key and resets BOTH CBC/CMAC contexts.");
    semanticFunction(0x6BD2L, "f33_boot_transfer_crypto_clear", v)
        .setComment("TransferExit optional-transform cleanup forwards70FC; wipes BOTH CBC and CMAC, not worker "
            + "activity/pointers or configured materials.");
    semanticFunction(0x6C52L, "f33_boot_block_transform_clear_activity", v)
        .setComment("Clear2BDE active only; retain transform remaining/source/destination and all crypto contexts. Resident "
            + "initialization6A22 uses this, not a secure erase.");
    semanticFunction(0x6EAEL, "f33_boot_authentication_crypto_initialize", v)
        .setComment("Routine CRC-success path initializes image key/BOTH CBC-CMAC contexts via70D4 before authentication "
            + "submission.");
    semanticFunction(0x6EBAL, "f33_boot_region_authentication_submit", u32,
        new ParameterImpl("start", u32, currentProgram),
        new ParameterImpl("length", u32, currentProgram))
        .setComment("Real r6/r7 start,length passed unchanged to7122; reject ifactive2BFD!=0, else seed CMAC-prefix/cursors "
            + "and publishresult1/active1 on success. Return0accepted/1rejected. Does not initialize contexts by itself.");
    semanticFunction(0x6F04L, "f33_boot_region_authentication_clear_contexts", v)
        .setComment("Routine wait-auth terminal cleanup forwards70FC; wipes both CBC and CMAC, retaining "
            + "result/activity/cursors/configured materials/output.");
    semanticFunction(0x6F10L, "f33_boot_region_authentication_clear_activity", v)
        .setComment("Setresult2BFC=1,clearactive2BFD=0 only; no context/material/cursor wipe. Resident6A22 initialization "
            + "caller.");
    semanticFunction(0x6BDEL, "f33_boot_transfer_block_transform_progress", v)
        .setComment("Refine existing owner: CBC decrypt at most one full16-byte block via7108 into stack-local then copy back; "
            + "preserve originalciphertext chain for in-place job. Ignore crypto failure and copy local regardless. "
            + "Tail1..15 deducted without decrypt/copy or pointer advancement; active clears atremaining0.");
    semanticFunction(0x6EE0L, "f33_boot_region_authentication_progress", v)
        .setComment("Retain established name. Process onlyactive,7170return2busy;0clearsresult;terminal0/1clearsactive. Does "
            + "not wipe contexts/configured key/output/cursors; timer routine5936/5A04 separately clearscontexts on "
            + "normal terminal consumption.");
    semanticData(0xBFD8L, new ArrayDataType(u8, 16, 1), "f33_boot_image_key_derivation_key",
        "Resident image-crypto state; distinct from security-access and application SecOC lifetimes.");
    semanticData(0xFEBF2D08L, new ArrayDataType(u8, 16, 1), "f33_boot_image_key_material",
        "Resident image-crypto state; distinct from security-access and application SecOC lifetimes.");
    semanticData(0xFEBF2D18L, new ArrayDataType(u8, 16, 1), "f33_boot_image_derived_key",
        "Resident image-crypto state; distinct from security-access and application SecOC lifetimes.");
    semanticData(0xFEBF2CF8L, new ArrayDataType(u8, 16, 1), "f33_boot_image_iv_and_authentication_prefix",
        "Resident image-crypto state; distinct from security-access and application SecOC lifetimes.");
    semanticData(0xFEBF2D28L, new ArrayDataType(u8, 16, 1), "f33_boot_image_authentication_block",
        "Resident image-crypto state; distinct from security-access and application SecOC lifetimes.");
    semanticData(0xFEBF2C00L, F33BootAes128CmacContextType, "f33_boot_image_cmac_context",
        "Resident image-crypto state; distinct from security-access and application SecOC lifetimes.");
    semanticData(0xFEBF2EF0L, F33BootAes128CbcContextType, "f33_boot_image_cbc_context",
        "Resident image-crypto state; distinct from security-access and application SecOC lifetimes.");
    semanticData(0xFEBF30A8L, u32, "f33_boot_authentication_last_block",
        "Resident image-crypto state; distinct from security-access and application SecOC lifetimes.");
    semanticData(0xFEBF30ACL, new PointerDataType(u8, 4), "f33_boot_authentication_trailer_cursor",
        "Resident image-crypto state; distinct from security-access and application SecOC lifetimes.");
    semanticData(0xFEBF30B0L, new PointerDataType(u8, 4), "f33_boot_authentication_data_cursor",
        "Resident image-crypto state; distinct from security-access and application SecOC lifetimes.");
  }

  private void annotateApplicationAdaptation() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
    StructureDataType curvePoint = new StructureDataType(category, "F33CurvePointU16S16", 0);
    curvePoint.setPackingEnabled(true);
    curvePoint.add(u16, "x", "Unsigned axis; FFFF terminates traversal.");
    curvePoint.add(s16, "y", "Signed interpolation ordinate; physical units unassigned.");
    semanticData(0x31B5CL, new ArrayDataType(resolve(curvePoint), 9, 4),
        "f33_switched_signed_request_curve",
        "37FD2 passes this unsigned-axis/signed-ordinate curve to702B0 when6B4C=5A. Eight numerical rows "
            + "and FFFF sentinel; the sentinel returns the preceding ordinate0. Typing the full36-byte "
            + "table removes the false JARL decoded at31B66, which otherwise recreates interior function33966.");
    // 33966 is fall-through after DIVQ33962, sharing the sole PREPARE336B8 and DISPOSE33AA0.
    currentProgram.getFunctionManager().removeFunction(toAddr(0x33966L));
    Function fit = getFunctionAt(toAddr(0x336B8L));
    if (fit == null) throw new IllegalStateException("missing six-channel fit root");
    fit.setBody(new AddressSet(toAddr(0x336B8L), toAddr(0x33AA3L)));
    StructureDataType fitLayout0 = new StructureDataType(category, "F33SixChannelFitWork", 0);
    fitLayout0.setPackingEnabled(true);
    fitLayout0.add(u8, "state", null);
    fitLayout0.add(u8, "active", null);
    fitLayout0.add(u8, "unsigned_initialized", null);
    fitLayout0.add(u8, "signed_initialized", null);
    fitLayout0.add(u8, "coverage_count", null);
    fitLayout0.add(new ArrayDataType(u8, 1, 1), "reserved_5", null);
    fitLayout0.add(s16, "previous_angle", null);
    fitLayout0.add(new ArrayDataType(u16, 6, 2), "unsigned_max", null);
    fitLayout0.add(new ArrayDataType(u16, 6, 2), "unsigned_min", null);
    fitLayout0.add(new ArrayDataType(u16, 6, 2), "unsigned_previous", null);
    fitLayout0.add(new ArrayDataType(u16, 6, 2), "first_gain", null);
    fitLayout0.add(new ArrayDataType(u16, 6, 2), "first_center", null);
    fitLayout0.add(new ArrayDataType(s16, 6, 2), "signed_max", null);
    fitLayout0.add(new ArrayDataType(s16, 6, 2), "signed_min", null);
    fitLayout0.add(new ArrayDataType(s16, 6, 2), "signed_previous", null);
    fitLayout0.add(new ArrayDataType(u16, 6, 2), "second_gain", null);
    fitLayout0.add(new ArrayDataType(s16, 6, 2), "second_center", null);
    fitLayout0.add(new ArrayDataType(u16, 3, 2), "component_angle", null);
    fitLayout0.add(new ArrayDataType(u8, 2, 1), "reserved_134", null);
    fitLayout0.add(s32, "coverage_sum", null);
    fitLayout0.add(s32, "coverage_min", null);
    fitLayout0.add(s32, "coverage_max", null);
    fitLayout0.add(new ArrayDataType(u32, 6, 4), "unsigned_q16", null);
    fitLayout0.add(new ArrayDataType(s32, 6, 4), "signed_q16", null);
    DataType F33SixChannelFitWorkType = resolve(fitLayout0);
    semanticData(0xFEBE6960L, F33SixChannelFitWorkType, "f33_six_channel_fit_work",
        "Expose retained numerical flow without physically naming six channels; actual unsigned/signed differences and accumulator arithmetic matter.");
    StructureDataType fitLayout1 = new StructureDataType(category, "F33Mode600StimulusFitWork", 0);
    fitLayout1.setPackingEnabled(true);
    fitLayout1.add(u8, "state", null);
    fitLayout1.add(u8, "active", null);
    fitLayout1.add(u8, "stimulus_valid", null);
    fitLayout1.add(new ArrayDataType(u8, 1, 1), "reserved_3", null);
    fitLayout1.add(s16, "positive_mean", null);
    fitLayout1.add(s16, "negative_mean", null);
    fitLayout1.add(s16, "stimulus", null);
    fitLayout1.add(u16, "hold_count", null);
    fitLayout1.add(u16, "sample_count", null);
    fitLayout1.add(new ArrayDataType(u8, 2, 1), "reserved_14", null);
    fitLayout1.add(s32, "folded_angle_sum", null);
    fitLayout1.add(s32, "signed_component_sum", null);
    DataType F33Mode600StimulusFitWorkType = resolve(fitLayout1);
    semanticData(0xFEBE6A60L, F33Mode600StimulusFitWorkType, "f33_mode600_stimulus_fit_work",
        "Make partial cancel/abort vs full initialization and independent sums explicit; not an actuator/sensor success object.");
    StructureDataType fitLayout2 = new StructureDataType(category, "F33FitCoefficients", 0);
    fitLayout2.setPackingEnabled(true);
    fitLayout2.add(new ArrayDataType(u16, 6, 2), "first_center", null);
    fitLayout2.add(new ArrayDataType(u16, 6, 2), "first_gain", null);
    fitLayout2.add(new ArrayDataType(s16, 6, 2), "second_center", null);
    fitLayout2.add(new ArrayDataType(u16, 6, 2), "second_gain", null);
    fitLayout2.add(new ArrayDataType(u16, 3, 2), "component_angle", null);
    DataType F33FitCoefficientsType = resolve(fitLayout2);
    semanticData(0xFEBE6A26L, F33FitCoefficientsType, "f33_published_fit_coefficients",
        "Published and retained27-halfword groups compared by33AB6; NOT the serialized0202 order, which interleaves pairs.");
    semanticData(0xFEBE6A84L, F33FitCoefficientsType, "f33_retained_fit_coefficients",
        "Published and retained27-halfword groups compared by33AB6; NOT the serialized0202 order, which interleaves pairs.");
    semanticFunction(0x336B8L, "f33_step_six_channel_fit", v)
        .setComment("Mode0512/0600 six-channel numerical-fit controller; active6961=5A, states0/11/22/33/44/55/66. Prior-angle "
            + "update occurs even while inactive or phase-admission fails. First sweep follows literal0x8000, not "
            + "acquired samples; numerical success is not physical calibration. Terminal flag clears on next invocation. "
            + "Interior33966 shares this function frame; it is not an independent ABI.");
    semanticFunction(0x32D26L, "f33_track_fit_angular_coverage", u32,
        new ParameterImpl("angle", s16, currentProgram),
        new ParameterImpl("required_spans", u8, currentProgram))
        .setComment("Wrapped signed16 angle delta accumulates signed32 directional extrema; max-min>=65536 increments wrapping "
            + "byte span count. Return0/5A/A5; does not update previous-angle itself.");
    semanticFunction(0x32D88L, "f33_step_unsigned_literal_fit_sweep", v,
        new ParameterImpl("angle", s16, currentProgram))
        .setComment("Admission gates from raw retained5F36 and7DB0; invalid gate clears phase-init only. Six unsigned Q16 "
            + "recurrences track literal32768, seed all extrema/outputs32768 and use exact gain11258. Calls angular "
            + "coverage threshold5; final coverage changes root state11->22.");
    semanticFunction(0x330A0L, "f33_step_signed_constant_fit_sweep", v,
        new ParameterImpl("angle", s16, currentProgram))
        .setComment("Derive six signed channels from retained first gains/centers and literal32768, not live sample channels. "
            + "Symmetric saturation, signed division and six Q16 recurrences use truncation toward zero. Same input "
            + "gates and coverage threshold5 advance33->44.");
    semanticFunction(0x33AA4L, "f33_begin_six_channel_fit", v)
        .setComment("Set state6960=0 and active6961=5A only; does not erase prior fits before subsequent phase initialization.");
    semanticFunction(0x33D3CL, "f33_check_foreground_fit_bounds", u32)
        .setComment("Check foreground snapshot, not mutable worker arrays. Returns5A for accepted and0 otherwise. Exact "
            + "configured unsigned bounds are full0..65535 and signed centers full-32768..32767; therefore not a "
            + "meaningful physical calibration validation.");
    semanticFunction(0x33F14L, "f33_step_fit_completion", v)
        .setComment("Active6A5C=5A starts worker then watches cached foreground6528.55 plus snapshot bounds stages0202 and "
            + "state22;66 or failed check reports existing52/slot17 and state44. Later22 responds0;44 responds-9. Does "
            + "not await physical NvM completion.");
    semanticFunction(0x33F9CL, "f33_request_six_channel_fit", u32)
        .setComment("Set6A5C=5A and return0; retains6A5D. Only recovered direct caller32CA0; this helper alone does not "
            + "guarantee a fresh run.");
    semanticFunction(0x348DAL, "f33_publish_fit_candidate_record", v)
        .setComment("Copy foreground centers/gains/angles into retained6A84..6AB8, serialize64-byte0202 record markerA55A5AA5 "
            + "plus reserved zero, enqueue setter; publish6A7A=44 and6ABC marker immediately. Do not interpret immediate "
            + "software marker as durable write success.");
    semanticFunction(0x34028L, "f33_step_mode600_stimulus_fit", v)
        .setComment("Family0600 active5A sequencer: positive and negative1280 stimulus, bounded delayed angle averaging and "
            + "independent signed component sum, paired correction staging, mean agreement, queued records0208/0209. "
            + "Abort response-6 resets live request but retains count/sums. Completion polls only RAM marker.");
    semanticFunction(0x33FAAL, "f33_initialize_mode600_stimulus_fit", v)
        .setComment("State10; clear request-valid, means, stimulus, timer, sample count and both32-bit sums. Retain "
            + "active6A61;343F0 sets it5A before calling here.");
    semanticFunction(0x33FC6L, "f33_cancel_mode600_stimulus_fit", v)
        .setComment("Only clear6A61/6A62 and set state6A60=10. Preserve remaining means/stimulus/counters/sums. Existing "
            + "mode0600 exit owner calls this and retains its name/contract.");
    semanticFunction(0x33FD6L, "f33_abort_mode600_stimulus_fit", v,
        new ParameterImpl("active", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("request_valid", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("stimulus", new PointerDataType(s16, 4), currentProgram),
        new ParameterImpl("hold_count", new PointerDataType(u16, 4), currentProgram),
        new ParameterImpl("positive_mean", new PointerDataType(s16, 4), currentProgram),
        new ParameterImpl("negative_mean", new PointerDataType(s16, 4), currentProgram),
        new ParameterImpl("state", new PointerDataType(u8, 4), currentProgram))
        .setComment("Clear passed active/request/stimulus/hold/means, set state10; stage zero pair, respond-6, cancel worker. "
            + "Does not clear sample count or accumulators. Last three pointer arguments at entry SP+0/+4/+8.");
    semanticFunction(0x343F0L, "f33_begin_mode600_stimulus_fit", u32)
        .setComment("Set active6A61=5A then full initializer33FAA and return0. No registered call/xref was recovered; keep "
            + "admission boundary unresolved rather than claiming diagnostic reachability.");
    semanticFunction(0x32594L, "f33_stage_pair_correction", s32,
        new ParameterImpl("selector", u8, currentProgram),
        new ParameterImpl("values", new PointerDataType(s16, 4), currentProgram))
        .setComment("Selector0 copies both raw halfwords to68AA/AC, writes software markerA55A5AA5, returns0; other selector "
            + "returns-6. Existing32454 record projection can independently replace these slots; no calibration "
            + "durability claim.");
    semanticFunction(0x325C8L, "f33_queue_pair_correction_records", v)
        .setComment("Build marker+pair records and request setters0208/0209; ignore returns and write RAM markerA55A5AA5 "
            + "immediately. Persistence/physical copy consensus remain existing NvM boundary.");
    semanticFunction(0x32CA0L, "f33_step_mode600_fit_request", v)
        .setComment("When695A==5A, state0 requests6A5C and moves1; nonzero completion state starts "
            + "request6959=5A/valueROM30EA8 and moves2; completion22/44 clears stimulus and moves3/4; next terminal pass "
            + "clears695A. This is distinct from34028 worker active6A61.");
    semanticFunction(0x34C56L, "f33_select_mode600_stimulus_request", v)
        .setComment("Prioritize cached6210/6212 from34028 over6959/695C request, else signed torque map. Publish source ID and "
            + "negated selected request. No inferred physical current actuation, freshness or actual output consumer.");
    semanticFunction(0x344F4L, "f33_check_retained_fit_bounds", u32)
        .setComment("Return5A for invalid retained6A84..6AB8,0 valid. Unlike permissive foreground candidate check, exact "
            + "retained gains24097..32768, first centers31623..33913, signed second centers-286..286 and "
            + "angles8118..8374. Does not mutate retained values.");
    semanticFunction(0x34C3AL, "f33_check_fit_record_admission", u32)
        .setComment("Preserve344F4 full R10 result across PREPARE/DISPOSE.33CDC consumes0 for admissible changed record and5A "
            + "for invalid. Replace existing void prototype; no unrelated register clobber/inline fiction.");
    semanticFunction(0x33CDCL, "f33_step_retained_fit_coherence", v)
        .setComment("Only on8A18==5A: require6ABC markerA55A5AA5; compare27 halfwords against last publication. Unchanged "
            + "skips validation; changed+valid retained bounds copies, invalid marker/bounds resets published arrays to "
            + "defaults.6A24/25 retain comparison and validation statuses.");
    semanticFunction(0x33AB6L, "f33_compare_retained_fit_coefficients", u32)
        .setComment("Compare all27 halfwords of6A26 publication with6A84 retained candidate. Return0 identical,5A changed; not "
            + "a calibration-health verdict.");
    semanticFunction(0x33BEAL, "f33_copy_retained_fit_coefficients", v)
        .setComment("Copy grouped centers/gains/angles6A84..6AB8 to6A26..6A5A after coherence admission; no physical "
            + "calibration transformation.");
    semanticFunction(0x33C98L, "f33_reset_published_fit_coefficients", v)
        .setComment("Default published first centers/gains and second gains to8000, second centers0, angles2000. Retained "
            + "source6A84 and marker remain independent.");
    semanticFunction(0x34408L, "f33_restore_fit_coefficients", v)
        .setComment("Get64-byte0202 record and publish unpacked centers/gains/angles only when getter returns10, under "
            + "existing PMR helper. Does not itself validate marker or numeric bounds; caller346F0 owns marker/status "
            + "and346B2 owns bounds/defaulting.");
    semanticFunction(0x3465AL, "f33_reset_retained_fit_coefficients", v)
        .setComment("Under existing FFC0 priority mask, default retained first centers/gains and second gains8000, second "
            + "centers0 and angles2000; does not imply accepted physical calibration.");
    semanticFunction(0x346B2L, "f33_validate_or_default_retained_fit", u32)
        .setComment("Return344F4 status;5A first defaults retained values via3465A. Existing346F0 marker/diagnostic owner "
            + "remains separate from candidate publication.");
    StructureDataType parameters = new StructureDataType(category, "F33FitParameters", 0);
    parameters.setPackingEnabled(true);
    parameters.add(u8, "unsigned_coverage_spans", null);
    parameters.add(u8, "signed_coverage_spans", null);
    parameters.add(u16, "qualifier_lower", null);
    parameters.add(u16, "qualifier_upper", null);
    parameters.add(u16, "reserved_06", null);
    parameters.add(s16, "magnitude_upper", null);
    parameters.add(u16, "unsigned_filter_half_gain", null);
    parameters.add(u16, "signed_filter_half_gain", null);
    parameters.add(u16, "first_gain_numerator", null);
    parameters.add(u16, "second_gain_numerator", null);
    parameters.add(u16, "gain_upper", null);
    parameters.add(u16, "gain_lower", null);
    parameters.add(u16, "reserved_16", null);
    parameters.add(new ArrayDataType(u16, 10, 2), "candidate_bound_words", null);
    parameters.add(s16, "stimulus", null);
    parameters.add(u16, "initial_hold_calls", null);
    parameters.add(s16, "sample_admission", null);
    parameters.add(u16, "release_hold_calls", null);
    parameters.add(u16, "recheck_hold_calls", null);
    parameters.add(s16, "component_mean_limit", null);
    parameters.add(s16, "folded_angle_limit", null);
    parameters.add(s16, "pass_difference_limit", null);
    parameters.add(u16, "mode600_input_upper", null);
    parameters.add(u16, "mode600_qualifier_lower", null);
    parameters.add(u16, "sample_count", null);
    semanticData(0x30EACL, resolve(parameters), "f33_fit_parameters",
        "Exact fit/stimulus thresholds and invocation counts. Candidate bounds retain encoded halfwords; no physical units assigned.");
  }

  private void annotateOutputOwnerLifetimes() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
    semanticFunction(0x35FAEL, "f33_initialize_terminal_output_ramp", v)
        .setComment("Clear active6B2C,phase6B2D,reserved6B2E and invocation counter6B30. Does not itself release slot1 or "
            + "request word7.");
    semanticFunction(0x35FBCL, "f33_step_terminal_output_ramp", v)
        .setComment("Only active6B2C==5A publishes slot1 in both banks. Entry count<60000 requests owner7 mask40004, advances "
            + "by200 only when6798==1 otherwise1, interpolates exact30E60, and sets phase1. Map is0 through59950 then "
            + "rises to8000 at60000. Already-terminal count requests70017001, codes8000 and phase2 without advancing. "
            + "Inactive clears request7/count/phase and releases slot1, retaining its triplets. No wall-time or "
            + "electrical-duty claim; later aggregate neutral slot3 can outrank slot1.");
    semanticFunction(0x360BCL, "f33_request_terminal_output_ramp", v)
        .setComment("Set active6B2C=5A only; do not reset retained ramp count. Fault output router3C470 is the recovered "
            + "requester.");
    semanticFunction(0x360C6L, "f33_cancel_terminal_output_ramp", v)
        .setComment("Clear active6B2C only. Subsequent35FBC invocation clears request7/count/phase and releases slot1; this "
            + "setter is not immediate output retirement.");
    semanticFunction(0x5737AL, "f33_set_output_request_word", v,
        new ParameterImpl("owner", u8, currentProgram),
        new ParameterImpl("request", u32, currentProgram))
        .setComment("Low8 owner<8 replaces one u32 at8B2C. No reduction, physical port write or slot arbitration here.");
    semanticFunction(0x571B4L, "f33_apply_output_request_port_levels", u32,
        new ParameterImpl("request", u32, currentProgram))
        .setComment("Map request bit0/16 to configured port-level callbacks and return only those bits. If prior8B28 has both "
            + "bit1/17 set, perform preliminary paired writes for both-new-set or both-new-clear before normal per-bank "
            + "writes. No GPIO feedback or software permission is derived.");
    semanticFunction(0x5721CL, "f33_stage_output_request_phase_masks", u32,
        new ParameterImpl("request", u32, currentProgram))
        .setComment("Per bank start6-bit mask3F; requestbit2 selects38, bits12/13/14 AND F6/ED/1B and echo their status bits. "
            + "All three phase bits add statusbit1; otherwise low3 mask zero addsbit2. Repeat at+16. Stage masks "
            + "through61C40 and publish8B24/25. Masking alone40004 does not activate neutral slot3.");
    semanticFunction(0x572E6L, "f33_publish_aggregate_output_requests", v)
        .setComment("OR eight owner words8B2C; apply configured GPIO levels571B4 and phase-mask staging5721C, OR returned "
            + "status. Per-bank status&3 activates slot3 with three exact31908=4000 codes; otherwise release slot3. "
            + "Finally publish8B28. This does not select a winner. Full native entry stops at unmapped "
            + "GPIOFFC100C4;57308..57376 continuation has explicit R28/R10 handoff, not physical-output proof.");
    semanticFunction(0x57390L, "f33_initialize_direct_output_requests", v)
        .setComment("Clear request enables8B4C/D and initialize both retained triplets8B4E..58 to4000. Called on crossing into "
            + "mode>0100; unlike573FE it also resets codes.");
    semanticFunction(0x573AEL, "f33_publish_direct_output_requests", v)
        .setComment("Each nonzero request byte8B4C/D copies its retained triplet to slot4 with context10 and activates that "
            + "bank. Zero releases slot4 without erasing its codes. Flags dirty selection only on change. Native "
            + "composition verifies independent activation/release then real arbitration, including slot1 clamp "
            + "exemption.");
    semanticFunction(0x57408L, "f33_clear_direct_output_bank0", v)
        .setComment("Store0 to request byte8B4C only. Publication/release of slot4 occurs later in573AE; retained triplet is "
            + "unchanged.");
    semanticFunction(0x57414L, "f33_request_direct_output_bank0", v)
        .setComment("Store5A to request byte8B4C only. Publication/release of slot4 occurs later in573AE; retained triplet is "
            + "unchanged.");
    semanticFunction(0x5740EL, "f33_clear_direct_output_bank1", v)
        .setComment("Store0 to request byte8B4D only. Publication/release of slot4 occurs later in573AE; retained triplet is "
            + "unchanged.");
    semanticFunction(0x5741EL, "f33_request_direct_output_bank1", v)
        .setComment("Store5A to request byte8B4D only. Publication/release of slot4 occurs later in573AE; retained triplet is "
            + "unchanged.");
    semanticFunction(0x57428L, "f33_set_direct_output_codes_bank0", v,
        new ParameterImpl("codes", new PointerDataType(u16, 4), currentProgram))
        .setComment("Copy three halfwords into retained direct request at8B4E; do not activate the request or publish slot4. "
            + "No local pointer or code-range validation.");
    semanticFunction(0x57440L, "f33_set_direct_output_codes_bank1", v,
        new ParameterImpl("codes", new PointerDataType(u16, 4), currentProgram))
        .setComment("Copy three halfwords into retained direct request at8B54; do not activate the request or publish slot4. "
            + "No local pointer or code-range validation.");
    semanticFunction(0x575BAL, "f33_initialize_output_code_limit_requests", v)
        .setComment("Set all three requested limits per bank and cached minima to8000; complements7FFF. Published limits/flags "
            + "are separate575F6 outputs.");
    semanticFunction(0x5775CL, "f33_set_output_code_limit_bank0", v,
        new ParameterImpl("owner", u8, currentProgram),
        new ParameterImpl("limit", u16, currentProgram))
        .setComment("Low8 owner<3 stores requested u16 limit; reduce all three from nominal8000 and update minimum/complement. "
            + "Unchanged request may return early when cache is already no greater. Only owner1 has a recovered "
            + "requester,3C6A8. Published limits/flags wait for575F6.");
    semanticFunction(0x577CCL, "f33_set_output_code_limit_bank1", v,
        new ParameterImpl("owner", u8, currentProgram),
        new ParameterImpl("limit", u16, currentProgram))
        .setComment("Low8 owner<3 stores requested u16 limit; reduce all three from nominal8000 and update minimum/complement. "
            + "Unchanged request may return early when cache is already no greater. Only owner1 has a recovered "
            + "requester,3C6A8. Published limits/flags wait for575F6.");
    semanticFunction(0x5790CL, "f33_release_output_code_limit_bank0", v,
        new ParameterImpl("owner", u8, currentProgram))
        .setComment("Low8 owner<3 restores requested limit8000; reduce all three from nominal8000 and update "
            + "minimum/complement. Unchanged request may return early when cache is already no greater. Only owner1 has "
            + "a recovered requester,3C6A8. Published limits/flags wait for575F6.");
    semanticFunction(0x5797AL, "f33_release_output_code_limit_bank1", v,
        new ParameterImpl("owner", u8, currentProgram))
        .setComment("Low8 owner<3 restores requested limit8000; reduce all three from nominal8000 and update "
            + "minimum/complement. Unchanged request may return early when cache is already no greater. Only owner1 has "
            + "a recovered requester,3C6A8. Published limits/flags wait for575F6.");
    semanticFunction(0x579F4L, "f33_initialize_phase_output_slots", v)
        .setComment("Clear both five-slot enable banks and dirty flags; initialize all triplets4000. Select index0, "
            + "complementFF and enable slot0 in both banks. Does not overwrite selected output triplets8BEE..F8.");
    semanticFunction(0x57BCAL, "f33_write_phase_output_slot_pair", v,
        new ParameterImpl("context", u16, currentProgram),
        new ParameterImpl("slot", u8, currentProgram),
        new ParameterImpl("first", new PointerDataType(u16, 4), currentProgram),
        new ParameterImpl("second", new PointerDataType(u16, 4), currentProgram))
        .setComment("Low8 slot<5 copies three u16 codes per bank; does not activate slot. Context low16<3 writes directly, "
            + "otherwise uses existing FFC0 priority mask pair. No code clamp here.");
    semanticFunction(0x57CB4L, "f33_write_phase_output_slot_bank0", v,
        new ParameterImpl("context", u16, currentProgram),
        new ParameterImpl("slot", u8, currentProgram),
        new ParameterImpl("codes", new PointerDataType(u16, 4), currentProgram))
        .setComment("Low8 slot<5 copies three u16 codes in this bank without activation. Context low16<3 writes directly, "
            + "otherwise existing FFC0 priority mask pair; no clamp or all-interrupt atomicity claim.");
    semanticFunction(0x57D4EL, "f33_write_phase_output_slot_bank1", v,
        new ParameterImpl("context", u16, currentProgram),
        new ParameterImpl("slot", u8, currentProgram),
        new ParameterImpl("codes", new PointerDataType(u16, 4), currentProgram))
        .setComment("Low8 slot<5 copies three u16 codes in this bank without activation. Context low16<3 writes directly, "
            + "otherwise existing FFC0 priority mask pair; no clamp or all-interrupt atomicity claim.");
    semanticFunction(0x57C48L, "f33_activate_phase_output_slot_pair", v,
        new ParameterImpl("slot", u8, currentProgram))
        .setComment("Low8 slot<5 writes enable5A in both banks. Only changed flags dirty that bank selector; triplets and "
            + "current selected index remain retained until57A5A.");
    semanticFunction(0x57C7EL, "f33_release_phase_output_slot_pair", v,
        new ParameterImpl("slot", u8, currentProgram))
        .setComment("Low8 slot<5 writes enable0 in both banks. Only changed flags dirty that bank selector; triplets and "
            + "current selected index remain retained until57A5A.");
    semanticFunction(0x57D0CL, "f33_activate_phase_output_slot_bank0", v,
        new ParameterImpl("slot", u8, currentProgram))
        .setComment("Low8 slot<5 writes enable5A in first bank. Only changed flags dirty that bank selector; triplets and "
            + "current selected index remain retained until57A5A.");
    semanticFunction(0x57D2EL, "f33_release_phase_output_slot_bank0", v,
        new ParameterImpl("slot", u8, currentProgram))
        .setComment("Low8 slot<5 writes enable0 in first bank. Only changed flags dirty that bank selector; triplets and "
            + "current selected index remain retained until57A5A.");
    semanticFunction(0x57DA6L, "f33_activate_phase_output_slot_bank1", v,
        new ParameterImpl("slot", u8, currentProgram))
        .setComment("Low8 slot<5 writes enable5A in second bank. Only changed flags dirty that bank selector; triplets and "
            + "current selected index remain retained until57A5A.");
    semanticFunction(0x57DCAL, "f33_release_phase_output_slot_bank1", v,
        new ParameterImpl("slot", u8, currentProgram))
        .setComment("Low8 slot<5 writes enable0 in second bank. Only changed flags dirty that bank selector; triplets and "
            + "current selected index remain retained until57A5A.");
    semanticFunction(0x5E8A8L, "f33_update_mode_owned_application_requests", v,
        new ParameterImpl("context", u32, currentProgram),
        new ParameterImpl("mode", u16, currentProgram),
        new ParameterImpl("previous_mode", u16, currentProgram))
        .setComment("R7/R8 low16 current/prior mode. Mode>0100 updates aggregate and direct output owners; crossing from<=0100 "
            + "also resets direct enables/codes before publication. Mode>=0200 advances offset selector;0300..0400 "
            + "clears reserved monitor action slot;>0101 updates additional paired outputs. Ends57F00. These are "
            + "mode-dependent calls, not a second steering permission system.");
    semanticFunction(0x5EBA0L, "f33_update_steady_application_requests", v,
        new ParameterImpl("context", u32, currentProgram),
        new ParameterImpl("mode", u16, currentProgram))
        .setComment("Steady-mode counterpart: low16 mode>0100 updates aggregate/direct output owners and other configured "
            + "requests without entry reset;>=0200 advances phase offset,0300..0400 clears reserved monitor slot,>0101 "
            + "updates additional paired outputs. Ends57F00; no implied physical scheduling interval.");
    semanticFunction(0x61C40L, "f33_stage_configured_phase_mask", v,
        new ParameterImpl("bank", u32, currentProgram),
        new ParameterImpl("mask", u32, currentProgram))
        .setComment("For absent input bits0/3/1/4/2/5, OR descriptor315D4+bank*1C halfwords+8/A/C/E/10/12 into the software "
            + "PWM port_mask. No peripheral write here; later commit owner is separate. Recovered callers pass bank0/1; "
            + "no local bank bound.");
    semanticFunction(0x61F32L, "f33_write_configured_output_port_level_a", v,
        new ParameterImpl("bank", u32, currentProgram))
        .setComment("Use descriptor315D4+bank*1C: port group bits8..15, pin low4 and level byte+4. Write "
            + "((level&1)|10000)<<pin to FFC10004+group*40. Exact banks0/1 targetFFC100C4 bit6 andFFC10084 bit4; level-a "
            + "is1 and level-b0. No local bank bound, GPIO readback or physical bridge-state proof.");
    semanticFunction(0x61F64L, "f33_write_configured_output_port_level_b", v,
        new ParameterImpl("bank", u32, currentProgram))
        .setComment("Use descriptor315D4+bank*1C: port group bits8..15, pin low4 and level byte+5. Write "
            + "((level&1)|10000)<<pin to FFC10004+group*40. Exact banks0/1 targetFFC100C4 bit6 andFFC10084 bit4; level-a "
            + "is1 and level-b0. No local bank bound, GPIO readback or physical bridge-state proof.");
    semanticFunction(0x66A12L, "f33_write_output_bank0_port_level_a", v)
        .setComment("Fixed bank0 veneer for configured port level-a. Physical output response is outside the recovered "
            + "software contract.");
    semanticFunction(0x66A20L, "f33_write_output_bank0_port_level_b", v)
        .setComment("Fixed bank0 veneer for configured port level-b. Physical output response is outside the recovered "
            + "software contract.");
    semanticFunction(0x66A78L, "f33_write_output_bank1_port_level_a", v)
        .setComment("Fixed bank1 veneer for configured port level-a. Physical output response is outside the recovered "
            + "software contract.");
    semanticFunction(0x66A86L, "f33_write_output_bank1_port_level_b", v)
        .setComment("Fixed bank1 veneer for configured port level-b. Physical output response is outside the recovered "
            + "software contract.");
    semanticFunction(0x669C8L, "f33_stage_output_bank0_phase_mask", v,
        new ParameterImpl("mask", u8, currentProgram))
        .setComment("Forward mask to61C40 with fixed bank0; software port-mask staging, not immediate hardware commit.");
    semanticFunction(0x66A2EL, "f33_stage_output_bank1_phase_mask", v,
        new ParameterImpl("mask", u8, currentProgram))
        .setComment("Forward mask to61C40 with fixed bank1; software port-mask staging, not immediate hardware commit.");
    semanticData(0xFEBE8B2CL, new ArrayDataType(u32, 8, 4), "f33_output_request_words", "Eight independently replaced request words;572E6 OR reduction.");
    semanticData(0xFEBE8B28L, u32, "f33_output_request_status", "Returned status after configured port writes and phase-mask staging; not pin feedback.");
    semanticData(0xFEBE8B24L, new ArrayDataType(u8, 2, 1), "f33_output_phase_masks", "Current six-bit masks; software staging, not physical output proof.");
    semanticData(0xFEBE8B4CL, new ArrayDataType(u8, 2, 1), "f33_direct_output_request_enables", "Any nonzero byte requests bank-local slot4; publication is deferred.");
    semanticData(0xFEBE8B4EL, new ArrayDataType(u16, 3, 2), "f33_direct_output_codes_bank0", "Retained first-bank direct request codes.");
    semanticData(0xFEBE8B54L, new ArrayDataType(u16, 3, 2), "f33_direct_output_codes_bank1", "Retained second-bank direct request codes.");
    semanticData(0xFEBE8BA2L, new ArrayDataType(u8, 5, 1), "f33_output_slot_enables_bank0", "Only exact5A participates in highest-slot selection.");
    semanticData(0xFEBE8BA8L, new ArrayDataType(u8, 5, 1), "f33_output_slot_enables_bank1", "Release retains triplet and dirties later selection.");
    semanticData(0xFEBE8BB2L, new ArrayDataType(u16, 15, 2), "f33_output_slot_codes_bank0", "Five contiguous triplets; slot1 is exempt from code clamp.");
    semanticData(0xFEBE8BD0L, new ArrayDataType(u16, 15, 2), "f33_output_slot_codes_bank1", "Five contiguous triplets; writers do not activate automatically.");
  }

  private void annotateCurrentReferenceFeedback() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
    StructureDataType layout0 = new StructureDataType(category, "F33CurrentReferenceTransientState", 0);
    layout0.setPackingEnabled(true);
    layout0.add(u8, "active", null);
    layout0.add(u8, "previous_predicate", null);
    layout0.add(u16, "invocation_count", null);
    DataType F33CurrentReferenceTransientStateType = resolve(layout0);
    StructureDataType layout1 = new StructureDataType(category, "F33CurrentReferenceQualification", 0);
    layout1.setPackingEnabled(true);
    layout1.add(s16, "first_absolute_threshold", null);
    layout1.add(s16, "first_combined_threshold", null);
    layout1.add(s16, "second_combined_threshold", null);
    layout1.add(u16, "window_upper_exclusive", null);
    layout1.add(u16, "window_lower_inclusive", null);
    layout1.add(u16, "count_limit", null);
    DataType F33CurrentReferenceQualificationType = resolve(layout1);
    StructureDataType layout2 = new StructureDataType(category, "F33CurrentReferenceFeedbackState", 0);
    layout2.setPackingEnabled(true);
    layout2.add(s16, "request", null);
    layout2.add(s16, "ratio", null);
    layout2.add(s16, "previous_error", null);
    layout2.add(new ArrayDataType(u8, 2, 1), "opaque_06", null);
    layout2.add(s32, "error", null);
    layout2.add(s32, "current_gain", null);
    layout2.add(s32, "previous_gain", null);
    layout2.add(s32, "opaque_14", null);
    layout2.add(s32, "request_before_global_clamp", null);
    layout2.add(s32, "retained_transient_delta", null);
    layout2.add(s32, "saturated_base_plus_delta", null);
    DataType F33CurrentReferenceFeedbackStateType = resolve(layout2);
    StructureDataType layout3 = new StructureDataType(category, "F33CurrentReferenceFeedbackCalibration", 0);
    layout3.setPackingEnabled(true);
    layout3.add(u8, "opaque_00", null);
    layout3.add(u8, "shared_ceiling_enabled", null);
    layout3.add(u8, "error_gain_scaling_enabled", null);
    layout3.add(u8, "bypass_shared_ceiling", null);
    layout3.add(s16, "ratio_upper", null);
    layout3.add(s16, "error_lower", null);
    layout3.add(s16, "ratio_target", null);
    layout3.add(s16, "normal_current_gain", null);
    layout3.add(s16, "normal_previous_gain", null);
    layout3.add(s16, "transient_current_gain", null);
    layout3.add(s16, "transient_previous_gain", null);
    layout3.add(s16, "opaque_12", null);
    layout3.add(s32, "request_upper_q15", null);
    layout3.add(s32, "request_lower_q15", null);
    layout3.add(s32, "transient_delta_upper", null);
    layout3.add(s32, "transient_delta_lower", null);
    layout3.add(s32, "positive_error_gain_scale", null);
    layout3.add(s32, "nonpositive_error_gain_scale", null);
    DataType F33CurrentReferenceFeedbackCalibrationType = resolve(layout3);
    StructureDataType layout4 = new StructureDataType(category, "F33CurrentReferenceFloorState", 0);
    layout4.setPackingEnabled(true);
    layout4.add(u8, "previous_transient", null);
    layout4.add(u8, "filter_active", null);
    layout4.add(s16, "selected_request", null);
    layout4.add(s16, "curve_floor", null);
    layout4.add(s16, "raw_floor", null);
    layout4.add(s16, "narrowed_delta", null);
    layout4.add(s16, "filtered_candidate", null);
    layout4.add(new ArrayDataType(u8, 4, 1), "opaque_0c", null);
    layout4.add(s32, "accumulator_q16", null);
    DataType F33CurrentReferenceFloorStateType = resolve(layout4);
    StructureDataType layout5 = new StructureDataType(category, "F33CurrentReferenceFloorCalibration", 0);
    layout5.setPackingEnabled(true);
    layout5.add(u8, "force_enabled", null);
    layout5.add(u8, "opaque_01", null);
    layout5.add(s16, "forced_request", null);
    layout5.add(s16, "request_upper", null);
    layout5.add(u16, "filter_coefficient", null);
    layout5.add(s16, "release_delta_threshold", null);
    DataType F33CurrentReferenceFloorCalibrationType = resolve(layout5);
    StructureDataType layout6 = new StructureDataType(category, "F33AdditionalFirstCurrentReference", 0);
    layout6.setPackingEnabled(true);
    layout6.add(s16, "gain_q7", null);
    layout6.add(s16, "scaled_request", null);
    layout6.add(s16, "delta", null);
    layout6.add(s16, "delta_passthrough", null);
    layout6.add(s16, "candidate", null);
    layout6.add(s16, "output", null);
    layout6.add(s16, "previous_output", null);
    DataType F33AdditionalFirstCurrentReferenceType = resolve(layout6);
    semanticFunction(0x3629AL, "f33_update_transient_current_reference_qualification", v)
        .setComment("Unsigned EB94 window[8960,38400), plus abs(s16 63D4)>=2347 or abs63D4>=1630 and abs63D8>=2048, forms "
            + "predicate5A. Rising predicate OR prior active5A with count<3000 admits only if7568/E603 zero,71EC&1FF "
            + "zero andEB83=11. Predicate is published even on denied activation. Failed admission clears active/count; "
            + "admitted count increments only below3000. A new edge at3000 can retain active for that invocation "
            + "without restarting the budget. Raw invocation count and sampled qualifiers have no assigned physical "
            + "units.");
    semanticFunction(0x36346L, "f33_reset_bank0_current_reference_feedback", v)
        .setComment("Clear output, previous error, current error, gains, raw/clamped correction fields and opaque reset-only "
            + "word. Retain measured ratio and padding; do not clear the separate387CE staged snapshot.");
    semanticFunction(0x364DEL, "f33_reset_bank1_current_reference_feedback", v)
        .setComment("Clear output, previous error, current error, gains, raw/clamped correction fields and opaque reset-only "
            + "word. Retain measured ratio and padding; do not clear the separate387CE staged snapshot.");
    semanticFunction(0x3635EL, "f33_initialize_bank0_current_reference_feedback", v)
        .setComment("Mode-entry initializer forwards to bank0 feedback reset; no enable test or acquisition.");
    semanticFunction(0x364F6L, "f33_initialize_bank1_current_reference_feedback", v)
        .setComment("Mode-entry initializer forwards to bank1 feedback reset; no enable test or acquisition.");
    semanticFunction(0x3636AL, "f33_update_bank0_current_reference_feedback", v)
        .setComment("Use prior unclipped second-axis regulator output: saturating signed16 absolute magnitude*1024 divided by "
            + "min(bank envelope,shared6CE4). Zero denominator selects1024; ratio clamps0..1024. Error922-ratio "
            + "clamps-1024..1024 and halves toward zero when71EC&3. Gains6144/-1228, or30720/-6144 for transient5A; "
            + "exact optional gain-scaling flag0. Correction is low32(gain0*error-gain1*previous_error), added to "
            + "prior6DCA*32768 with symmetric signed32 saturation. Transient path then clamps the relative delta to "
            + "+/-41943040 and re-adds baseline without another saturation. Global bounds[-726474424,0], division "
            + "toward zero by32768 and signed16 publication follow. Normal mode retains old transient delta. Native "
            + "scheduled composition checks independent histories and zero-denominator behavior.");
    semanticFunction(0x36502L, "f33_update_bank1_current_reference_feedback", v)
        .setComment("Use prior unclipped second-axis regulator output: saturating signed16 absolute magnitude*1024 divided by "
            + "min(bank envelope,shared6CE4). Zero denominator selects1024; ratio clamps0..1024. Error922-ratio "
            + "clamps-1024..1024 and halves toward zero when71EC&3. Gains6144/-1228, or30720/-6144 for transient5A; "
            + "exact optional gain-scaling flag0. Correction is low32(gain0*error-gain1*previous_error), added to "
            + "prior6DCA*32768 with symmetric signed32 saturation. Transient path then clamps the relative delta to "
            + "+/-41943040 and re-adds baseline without another saturation. Global bounds[-726474424,0], division "
            + "toward zero by32768 and signed16 publication follow. Normal mode retains old transient delta. Native "
            + "scheduled composition checks independent histories and zero-denominator behavior.");
    semanticFunction(0x37F92L, "f33_current_reference_curve_feedback_magnitude", u32)
        .setComment("Read signed second-axis feedback mirror6D72; double when71EC&3, clamp to +/-32767, then return saturated "
            + "absolute magnitude. This is measured-feedback-derived map input, not the sampled torque command.");
    semanticFunction(0x37FD2L, "f33_update_current_reference_curve_floor", v,
        new ParameterImpl("feedback_magnitude", u16, currentProgram))
        .setComment("Transient5A uses unsigned-axis/signed-ordinate31B5C; ordinary mode interpolates signed2C31E ordinates "
            + "in128-count intervals and applies floor6F7E. Halve toward zero when71EC&3. Leaving transient seeds Q16 "
            + "accumulator from previous output and enables filtering. While active "
            + "A=low32(A-old_output*K+raw*K),K=304; publish trunc(A/65536). Signed16(raw-old_output)<=128 releases "
            + "directly to raw, not an absolute-delta test. Accumulator/filtered candidate are updated before release; "
            + "inactive filtering retains those fields.");
    semanticFunction(0x380DEL, "f33_select_feedback_bounded_first_current_request", v)
        .setComment("Refresh curve floor first. MarkerEAD0=5AA5A55A resets both feedback banks and selects0. Otherwise "
            + "healthy banks select min(staged6E1A,6E1C); bit0 selects bank1/resetbank0, else bit1 selects "
            + "bank0/resetbank1. Both bits therefore take bit0 precedence, not neutral fallback. Clamp selected request "
            + "at upper0 then lower curve floor6D8C, publish6D8A. Reset leaves staged snapshot/ratio intact. Exact "
            + "forced-override31B2C is0.");
    semanticFunction(0x38582L, "f33_scale_additional_first_current_request", s16,
        new ParameterImpl("request", s16, currentProgram))
        .setComment("Multiply signed input by signed gain6DF0, divide toward zero by128 and return signed low16 inR10. "
            + "Publish prior output, quotient and unsaturated difference/pass-through observables; no actual slew clamp "
            + "occurs in this image. Native bank1 gain69 case checks return use by385C4.");
    semanticFunction(0x385A8L, "f33_clamp_additional_first_current_request", s16,
        new ParameterImpl("request", s16, currentProgram))
        .setComment("Return max(retained curve floor6D8C,min(signed input,ROM31B30=0)). Clamp occurs after38582 signed16 "
            + "narrowing.");
    semanticFunction(0x385C4L, "f33_update_additional_first_current_request", v)
        .setComment("Select gain calibration by E5C3&1. E741=11/22 maps saturated abs(s32 E744); other states use default128. "
            + "Exact bank0 curve is flat128; bank1 decreases128 to0 between5287 and6809. With31B2C!=1,31D40=1 "
            + "and6EA8=5A, scale6D8A through38582 then re-clamp385A8; otherwise retain unscaled6D8A. Publish6DFA. E744 "
            + "is a staged AC1C copy, not independently identified external CAN authority.");
    semanticFunction(0x3835EL, "f33_select_actual_and_feedback_first_current_baselines", v)
        .setComment("Publish actual first-axis6DC8=min(base map6DEC,additional bound6DFA), except exact disabled "
            + "override31BF0=0. Separately publish feedback baseline6DCA=min(base map6DEC,pre-additional request6D8A). "
            + "These can differ; paired feedback uses6DCA, not final6DC8. Native scaled-release composition verifies "
            + "this distinction.");
    semanticFunction(0x38502L, "f33_map_sampled_command_to_base_first_current", v)
        .setComment("Saturating abs(s16 sampled command6E0A), including-32768 to32767, selects signed2E33E ordinates with "
            + "seven fractional bits. Index>=255 uses-7297. Clamp to exact[-25600,0], publish base first-axis6DEC and "
            + "independent command magnitude6DEE. This is not the measured-feedback floor map37FD2.");
    semanticFunction(0x387CEL, "f33_latch_current_feedback_and_reference_inputs", v)
        .setComment("Sequentially stage measured halfwords and full32-bit component banks6B34..48, paired feedback "
            + "requests6B50/74 to6E1A/1C, diagnostic sibling6AF6 and prior saturation directions. Later380DE resets do "
            + "not rewrite this generation; no atomic hardware acquisition claim.");
    semanticFunction(0x37F16L, "f33_publish_corrected_current_reference_pairs", v)
        .setComment("Mirror actual main second/first commands6DD6/6DC8 to6D84/86. Add main corrections6DA8/6DA6 with "
            + "symmetric signed16 saturation into common references6D7C/80. Differential references6D7E/82 add retained "
            + "correction and ROM baseline without the same saturation. Feedback baseline6DCA is not the published "
            + "first-axis command.");
    semanticFunction(0x5DE02L, "f33_update_mode_owned_current_feedback", v,
        new ParameterImpl("workmask", u32, currentProgram),
        new ParameterImpl("mode", u16, currentProgram),
        new ParameterImpl("previous_mode", u16, currentProgram))
        .setComment("Current mode>=0200 runs entry resets when prior mode<0200; workmask bit0 gates measured transform, "
            + "envelope qualification and paired feedback steps. Mode>=0101 separately initializes/reduces output-code "
            + "requests. Always publish57FD2 snapshot. Distinct generation from bit1 current-control composition.");
    semanticFunction(0x5DF1EL, "f33_update_steady_current_feedback", v,
        new ParameterImpl("workmask", u32, currentProgram),
        new ParameterImpl("mode", u16, currentProgram))
        .setComment("With workmask bit0 and mode>=0200, transform measured currents, update envelope qualifier, then bank0 "
            + "and bank1 feedback. Mode>=0101 independently gates code-limit reduction. Always publish57FD2 diagnostic "
            + "snapshot. Does not itself execute387CE consumer staging or current regulation.");
    semanticFunction(0x377DEL, "f33_initialize_shared_second_axis_envelope", v)
        .setComment("Set retained6CE4 to exact317AC=20480 only; no fresh input or qualification.");
    semanticFunction(0x377EEL, "f33_map_additional_second_axis_envelope", v,
        new ParameterImpl("magnitude", s16, currentProgram))
        .setComment("For E741=11/22 use signed-axis70208 curve selected byE5C3&1 and supplied absolute magnitude; otherwise "
            + "choose configured default. Publish6CE2.37840 supplies the saturated absolute E744 in actualR6.");
    semanticFunction(0x37840L, "f33_refresh_shared_second_axis_envelope", v)
        .setComment("Only8A20==1 refreshes. Saturate s32 E744 to +/-32767, take abs, store6CE0 and pass actualR6 to377EE. "
            + "Choose mapped6CE2 only when qualifier6EA8=5A, otherwise20480; lower-bound by selected signed calibration "
            + "and publish6CE4. Closed gate retains all state; paired first-axis feedback consumes this prior envelope.");
    semanticFunction(0x378D4L, "f33_apply_shared_second_axis_envelope", v)
        .setComment("Copy regulated second-axis bank outputs6BEE/6C1A to6CEC/6CEE, clamping symmetrically to6CE4 only "
            + "for6EA8=5A. This later output-envelope use is separate from the denominator choice in3636A/36502.");
    semanticFunction(0x38FACL, "f33_current_reference_envelope_signed_product", s32)
        .setComment("Use706AE symmetric signed32 saturation on s32 E744 times sign-extended s16 E5C4; return resulting "
            + "fullR10 product. Qualifier38FC6 tests its sign; no physical-unit assignment.");
    semanticFunction(0x38FC6L, "f33_qualify_additional_current_reference_envelope", u32,
        new ParameterImpl("signed_product", s32, currentProgram))
        .setComment("Admit5A for E741=0 or E741=11/22 with positive supplied product; require EAC0!=11 or unsignedEAC6 below "
            + "selected threshold, plusE740/E742 zero. Exact317B0=0 does not force rejection; EAC2=5A does. This is "
            + "numerical envelope qualification, not engagement authority.");
    semanticFunction(0x3903AL, "f33_refresh_current_reference_envelope_qualification", v)
        .setComment("Only8A20==1 recomputes signed product38FAC and qualifier38FC6, publishing6EA8. Other invocations retain "
            + "the previous qualifier; consumers run in separate current-control generations.");
    semanticData(0xFEBE6B4CL, F33CurrentReferenceTransientStateType, "f33_current_reference_transient", "Predicate, active request and invocation budget are distinct retained fields; no wall-time unit.");
    semanticData(0x31944L, F33CurrentReferenceQualificationType, "f33_current_reference_qualification", "Exact raw thresholds and unsigned half-open window consumed by3629A.");
    semanticData(0xFEBE6B50L, new ArrayDataType(F33CurrentReferenceFeedbackStateType, 2, 36), "f33_current_reference_feedback", "Independent36-byte banks. Reset retains ratio; ordinary step retains transient delta and opaque_14.");
    semanticData(0x31950L, new ArrayDataType(F33CurrentReferenceFeedbackCalibrationType, 2, 44), "f33_current_reference_feedback_calibration", "Two identical44-byte calibration rows; first and offset12 fields are not interpreted by these step functions.");
    semanticData(0xFEBE6D88L, F33CurrentReferenceFloorStateType, "f33_current_reference_floor", "Filtered lower bound and selected first-axis request are separate; negative delta releases immediately.");
    semanticData(0x31B2CL, F33CurrentReferenceFloorCalibrationType, "f33_current_reference_floor_calibration", "Force0, request upper0, coefficient304 and signed release threshold128; not an absolute-delta threshold.");
    semanticData(0xFEBE6DF0L, F33AdditionalFirstCurrentReferenceType, "f33_additional_first_current_reference", "Configured additional scaling observables, not a separate slew limiter or independent command source.");
    semanticData(0xFEBE6DC8L, s16, "f33_actual_first_current_command", "After additional selected scaling; published by37F16 and used for current conversion.");
    semanticData(0xFEBE6DCAL, s16, "f33_first_current_feedback_baseline", "Before additional selected scaling; paired3636A/36502 feedback uses this retained generation.");
    semanticData(0xFEBE6EA8L, u8, "f33_additional_current_envelope_qualified", "Refresh only8A20==1; consumers otherwise use retained qualification.");
    semanticData(0xFEBE6CE4L, s16, "f33_shared_second_axis_envelope", "37840 lower-bounds selected envelope by calibration. Used as both feedback denominator ceiling and later output clamp.");
  }

  private void annotateApplicationSessionSecurity() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType F33BootAes128ContextType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33BootAes128Context");
    if (F33BootAes128ContextType == null) throw new IllegalStateException("missing F33BootAes128Context");
    DataType F33BootAes128CtrContextType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33BootAes128CtrContext");
    if (F33BootAes128CtrContextType == null) throw new IllegalStateException("missing F33BootAes128CtrContext");
    DataType F33BootChallengeExclusionRecordType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33BootChallengeExclusionRecord");
    if (F33BootChallengeExclusionRecordType == null) throw new IllegalStateException("missing F33BootChallengeExclusionRecord");
    DataType F33DcmMessageContextType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33DcmMessageContext");
    if (F33DcmMessageContextType == null) throw new IllegalStateException("missing F33DcmMessageContext");
    DataType F33DcmSubfunctionType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33DcmSubfunction");
    if (F33DcmSubfunctionType == null) throw new IllegalStateException("missing F33DcmSubfunction");
    StructureDataType layout0 = new StructureDataType(category, "F33DcmSessionTimingRow", 0);
    layout0.setPackingEnabled(true);
    layout0.add(u8, "transition_kind", "0 immediate,2 configured programming deferred;1 supported structurally but not configured");
    layout0.add(u8, "session", null);
    layout0.add(u16, "response_timing_a_raw", null);
    layout0.add(u16, "transport_timing_b_raw", null);
    layout0.add(u16, "transport_timing_c_raw", null);
    layout0.add(u16, "response_timing_d_raw", null);
    DataType F33DcmSessionTimingRowType = resolve(layout0);
    StructureDataType layout1 = new StructureDataType(category, "F33DcmSecurityLevelConfig", 0);
    layout1.setPackingEnabled(true);
    layout1.add(u32, "seed_client_length", null);
    layout1.add(u32, "failed_attempt_delay_raw", null);
    layout1.add(u32, "initial_delay_raw", null);
    layout1.add(u32, "submitted_key_length", null);
    layout1.add(u32, "seed_response_length", null);
    layout1.add(u8, "security_level", null);
    layout1.add(u8, "attempt_threshold", null);
    layout1.add(new ArrayDataType(u8, 2, 1), "opaque_padding", null);
    DataType F33DcmSecurityLevelConfigType = resolve(layout1);
    StructureDataType layout2 = new StructureDataType(category, "F33DcmProgrammingRequest", 0);
    layout2.setPackingEnabled(true);
    layout2.add(u16, "logical_transport_identifier", null);
    layout2.add(u8, "configured_transport_kind", null);
    layout2.add(u8, "service_id", null);
    layout2.add(u8, "target_session", null);
    layout2.add(u8, "is_programming_target", null);
    layout2.add(u8, "zero_06", null);
    layout2.add(u8, "positive_response_enabled", null);
    DataType F33DcmProgrammingRequestType = resolve(layout2);
    StructureDataType layout3 = new StructureDataType(category, "F33DcmSessionSnapshot", 0);
    layout3.setPackingEnabled(true);
    layout3.add(u8, "current", null);
    layout3.add(u8, "previous", null);
    layout3.add(u8, "target", null);
    layout3.add(u8, "pending_publication", null);
    DataType F33DcmSessionSnapshotType = resolve(layout3);
    semanticFunction(0x95D0CL, "f33_dcm_session_1_callback", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Configured SID10 operation callback for target0x01; forwards operation/message plus fixed target inr8 "
            + "to95C52. Callback return is ignored by existing F33DcmServiceCallback dispatcher. No direct hardware "
            + "transition.");
    semanticFunction(0x95D1CL, "f33_dcm_session_2_callback", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Configured SID10 operation callback for target0x02; forwards operation/message plus fixed target inr8 "
            + "to95C52. Callback return is ignored by existing F33DcmServiceCallback dispatcher. No direct hardware "
            + "transition.");
    semanticFunction(0x95D2CL, "f33_dcm_session_3_callback", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Configured SID10 operation callback for target0x03; forwards operation/message plus fixed target inr8 "
            + "to95C52. Callback return is ignored by existing F33DcmServiceCallback dispatcher. No direct hardware "
            + "transition.");
    semanticFunction(0x95D3CL, "f33_dcm_session_64_callback", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Configured SID10 operation callback for target0x40; forwards operation/message plus fixed target inr8 "
            + "to95C52. Callback return is ignored by existing F33DcmServiceCallback dispatcher. No direct hardware "
            + "transition.");
    semanticFunction(0x95C52L, "f33_dcm_session_operation", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram),
        new ParameterImpl("target", u8, currentProgram))
        .setComment("Operation0\u219295A3E admission;2\u219295B48 cancellation;3\u219295B88 pending-response notification. Other operations "
            + "no action.");
    semanticFunction(0x95A3EL, "f33_dcm_session_request", u32,
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram),
        new ParameterImpl("target", u8, currentProgram))
        .setComment("Copies advanced28-byte message to5D58; requires zero remaining bytes and application precondition. "
            + "ROM26122 has immediate1/3/40 and deferred2. Immediate transition requires capacity>=4, publishes "
            + "session/security/application notifications BEFORE timing response. Global26120=0 selects immediate "
            + "publication, not after-response policy. Programming2 sets5D55=1 and sends78; does not publish2 or queue9 "
            + "here.");
    semanticFunction(0x95B88L, "f33_dcm_programming_pending_response_join", u32,
        new ParameterImpl("target", u8, currentProgram))
        .setComment("Only state1 constructs eight-byte record5D4C using current logical transport config and "
            + "target/suppression.8B334 returns10 on successful mode9 request; state2/event0E/78 retained. State3\u21924 "
            + "calls95D4E(6), an exact no-op. No app session2 store or successful handoff follows this callback.");
    semanticFunction(0x95CB0L, "f33_dcm_programming_deferred_event", v)
        .setComment("Event0E re-enters8B334 with5D4C. Generic0/1/10 outcomes mapstate3/state0+22/requeue0E. Exact wrapper "
            + "latches pending10 after accepted software request; no timer/transport receipt alone proves handoff.");
    semanticFunction(0x95B48L, "f33_dcm_session_cancel", v)
        .setComment("For selected non-immediate row and state1/2 clear localstate/reset8B134 through95D4E(0). Invalidate "
            + "event0E and release5D24. Does not revoke request9, clear81AE, publishdefault, or prove cancellation of "
            + "already admitted mode/hardware action.");
    semanticFunction(0x9254AL, "f33_dcm_stage_or_publish_session", v,
        new ParameterImpl("target", u8, currentProgram),
        new ParameterImpl("defer", u8, currentProgram))
        .setComment("Under98CDA/98CE6 store target595E and previous595D. defer==1 sets pending595F only; otherwise "
            + "storecurrent595C, clearpending, then security0 and92518 callbacks outside critical section. Even "
            + "same-session publication runs notifications.");
    semanticFunction(0x925AEL, "f33_dcm_commit_or_discard_staged_session", v,
        new ParameterImpl("commit", u8, currentProgram))
        .setComment("commit1 publishes595E to595C only if595F==1, retaining pending for925DC notification; other values "
            + "clearpending without rolling current session back. Distinct from925DC security/application "
            + "notifications.");
    semanticFunction(0x925DCL, "f33_dcm_finish_staged_session_notifications", v)
        .setComment("When595F==1, clear published security, invoke92518(old595D,target595E), then clearpending. Does not "
            + "itself storecurrent session. Called at completed-response joins, independently of SID10 exact immediate "
            + "policy.");
    semanticFunction(0x92518L, "f33_dcm_notify_session_publication", v,
        new ParameterImpl("old_session", u8, currentProgram),
        new ParameterImpl("new_session", u8, currentProgram))
        .setComment("Invoke ROM25F48 callbacks968CC and9704E in order, then92044\u21928B0DE\u21924D582/6A156. Network restore effects "
            + "owned by network slice. Security bits already cleared by publication callers; challenge/client reset "
            + "occurs later4D582.");
    semanticFunction(0x4D582L, "f33_diagnostic_session_changed_application", v,
        new ParameterImpl("old_session", u8, currentProgram),
        new ParameterImpl("new_session", u8, currentProgram))
        .setComment("Always8D66A clears app-SA active/result/challenge/copy/client. Only new1 or old1\u2192new40 clears8196/8197, "
            + "requests event88 and clears nonrunning routine results. Network uses8196; do not claim every session "
            + "clears it.");
    semanticFunction(0x91B18L, "f33_dcm_restore_default_session", v)
        .setComment("Publishdefault1 immediately (relocks and notifies), clear three receive-active slots, set diagnostic "
            + "transportstate0, run91A24 and no-op925A0. Timer5 callback91B78 reaches this path. No physical reset or "
            + "ECU power action.");
    semanticFunction(0x91EA8L, "f33_dcm_restart_inactivity_after_request", v)
        .setComment("Read current session snapshot. Nondefault arms timer5 with protocol-selected raw S3 value from25EC8 and "
            + "sets5960=1; default sets5960=0 without explicitly cancelling an already armed slot. Clear receive-active "
            + "slots. Called from response/release joins and TesterPresent special case.");
    semanticFunction(0x959C6L, "f33_dcm_tester_present_request", u32,
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Advanced message must have zero remaining payload. Valid00/80 was selected by generic subfunction "
            + "dispatch; signal normal zero-body response through95644 or13 for extra bytes. Handler does not directly "
            + "write session or own S3. Actual release joins arm inactivity.");
    semanticFunction(0x9240EL, "f33_dcm_read_security_bitmap_level", u32,
        new ParameterImpl("level", new PointerDataType(u8, 4), currentProgram))
        .setComment("Return0 after snapshot of5954[2] undercritical. Output0 for locked; scan first set bit perword, later "
            + "nonzero second word can replace first-word level.92470 maintains one-hot level1..63 or allzero. "
            + "Caller91AE0 supplies the output pointer.");
    semanticFunction(0x92470L, "f33_dcm_publish_security_level", v,
        new ParameterImpl("level", u8, currentProgram))
        .setComment("For level<64 store two-word one-hot bitmap5954, or zero for level0, then no-op92054 notification. Called "
            + "on keyaccept BEFORE response and on session publication BEFORE session callbacks.");
    semanticFunction(0x96B48L, "f33_dcm_security_sub1_callback", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Configured SID27 sub1; wrapper preserves message inr8, moves operation tor7 and fixedsubfunction tor6. "
            + "Level=(sub+1)>>1. Odd seed dispatch969E4, even key96B04; r8 carries the consumed message pointer.");
    semanticFunction(0x96B5CL, "f33_dcm_security_sub2_callback", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Configured SID27 sub2; wrapper preserves message inr8, moves operation tor7 and fixedsubfunction tor6. "
            + "Level=(sub+1)>>1. Odd seed dispatch969E4, even key96B04; r8 carries the consumed message pointer.");
    semanticFunction(0x96B70L, "f33_dcm_security_sub3_callback", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Configured SID27 sub3; wrapper preserves message inr8, moves operation tor7 and fixedsubfunction tor6. "
            + "Level=(sub+1)>>1. Odd seed dispatch969E4, even key96B04; r8 carries the consumed message pointer.");
    semanticFunction(0x96B84L, "f33_dcm_security_sub4_callback", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Configured SID27 sub4; wrapper preserves message inr8, moves operation tor7 and fixedsubfunction tor6. "
            + "Level=(sub+1)>>1. Odd seed dispatch969E4, even key96B04; r8 carries the consumed message pointer.");
    semanticFunction(0x969E4L, "f33_dcm_security_seed_operation", u32,
        new ParameterImpl("subfunction", u8, currentProgram),
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Operation0\u2192968E2 seed admission,2\u219296990 cancellation; others return0. Actual third argument retained "
            + "inr8 and consumed by968E2.");
    semanticFunction(0x96B04L, "f33_dcm_security_key_operation", u32,
        new ParameterImpl("subfunction", u8, currentProgram),
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Operation0\u219296A04 key admission,2\u219296AB6 cancellation; others return0. Actual third argument retained "
            + "inr8.");
    semanticFunction(0x968E2L, "f33_dcm_security_seed_request", u32,
        new ParameterImpl("subfunction", u8, currentProgram),
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Retain advanced context5DD4, select level row, require16 seed-client bytes and seed capacity16. "
            + "Badlength13; insufficient capacity silently returns afterclearingtoken. Calls96692; delay is checked "
            + "there AFTER application seed callback. Not resident5328 lifetime.");
    semanticFunction(0x96692L, "f33_dcm_security_seed_callback_join", u32,
        new ParameterImpl("level", u8, currentProgram),
        new ParameterImpl("operation", u8, currentProgram))
        .setComment("Calls96B98(level,retainedrequest,op,response,&NRC) before delay/current-security tests. Return0 "
            + "sets5DCE=1; delay mask then clears token/NRC37. Otherwise already-unlocked samelevel zeroes16 response "
            + "and token0, else tokenlevel. Stages16-byte response. Return1 clears token and uses callbackNRC;10 "
            + "supportsgeneric pending but actual callbacks never10.");
    semanticFunction(0x96A04L, "f33_dcm_security_key_request", u32,
        new ParameterImpl("subfunction", u8, currentProgram),
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Require selectedrow<2, matching retainedlevel token5DCD, exact16 key bytes. Wronglength counts saturated "
            + "failure and13; mismatched nonzero token counts failure then24; zerotoken24 doesnotcount. These "
            + "malformed/sequence paths do NOT run delay-threshold logic. Valid structure\u219296788.");
    semanticFunction(0x96788L, "f33_dcm_security_key_callback_join", u32,
        new ParameterImpl("level", u8, currentProgram),
        new ParameterImpl("operation", u8, currentProgram))
        .setComment("Application0 clears selected failures, publishes security via91E12, clears token, stageszero-body "
            + "response BEFORE95644. ApplicationB saturating increments; belowthreshold2 NRC35 else armraw10000 "
            + "timer7/8, setdelaybit andNRC36. Failures/challenge retained. Callback1 usesNRC;10genericpending only, "
            + "actualcallbacks never10.");
    semanticFunction(0x96646L, "f33_dcm_security_initialize_delays", v)
        .setComment("Cold module initializer clearsdelaymask andboth failures, arms configured initial10000 delays on "
            + "timers7/8 and setsbits, then token/issuedflag0. Actual95590 init table26104 selects it. Does not itself "
            + "clear application crypto buffers8D66A.");
    semanticFunction(0x9689CL, "f33_dcm_security_delay_expired", v,
        new ParameterImpl("timer_slot", u8, currentProgram))
        .setComment("Timer callback7/8 matches26159/2615B and clears respective5DC8 bit only; "
            + "attempts/challenge/client/security/token unchanged.");
    semanticFunction(0x968CCL, "f33_dcm_security_session_notification", v,
        new ParameterImpl("old_session", u8, currentProgram),
        new ParameterImpl("new_session", u8, currentProgram))
        .setComment("ROM25F48-selected application session callback. Exact instructions ignore both args: if5DCE==1 clear5DCD "
            + "and5DCE; otherwise retain token. No delay/failure reset and no challenge clear here;4D582 later owns "
            + "application crypto reset.");
    semanticFunction(0x96990L, "f33_dcm_security_cancel_seed", u32,
        new ParameterImpl("subfunction", u8, currentProgram),
        new ParameterImpl("operation", u8, currentProgram))
        .setComment("Invalidate event0F, and only if5D28==1 call application seed-cancel wrapper, then clearasyncflag. Always "
            + "clear generic token and release5D24. Retains issuedflag/delay/failures/challenge for actual synchronous "
            + "path. Exact application wrapper ignoresoperation and is not a hardware cancellation guarantee.");
    semanticFunction(0x96AB6L, "f33_dcm_security_cancel_key", u32,
        new ParameterImpl("subfunction", u8, currentProgram),
        new ParameterImpl("operation", u8, currentProgram))
        .setComment("Invalidate event10; only5D28==1 invokes key callback withcancel operation; always "
            + "cleartoken/release5D24. Exact key callback ignoresoperation; reachable synchronous implementation "
            + "neverreturns10 and doesnotown asynchronous operation to cancel.");
    semanticFunction(0x8D824L, "f33_app_security_prepare_seed", u32,
        new ParameterImpl("client_material", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("seed_out", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("negative_response", new PointerDataType(u8, 4), currentProgram))
        .setComment("Always copy16 client bytes to497A. If4958==0 or retainedchallenge allzero generate8D74A; failureNRC22. "
            + "Otherwise copyexisting challenge495A toseed_out unchanged. Delay/current-security gating occurs "
            + "later96692. No CMAC or ICU-S ownership.");
    semanticFunction(0x8D91AL, "f33_app_security_compare_key", u32,
        new ParameterImpl("submitted_key", new PointerDataType(u8, 4), currentProgram))
        .setComment("Require active4958==5A; derive intermediate=AES128_DECRYPT(ROM20840,497A), "
            + "expected=AES128_ENCRYPT(intermediate,495A). Early-exit16-byte compare returnsB on firstmismatch. Success "
            + "clears495A/496A andactive4958, retains497A; publishesresult4959. Doesnotpublish security itself, "
            + "which96788 doesnext. Stackintermediate/expected notwiped.");
    semanticFunction(0x8D8ACL, "f33_app_security_decrypt_client_material", u32,
        new ParameterImpl("client_material", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("intermediate_key", new PointerDataType(u8, 4), currentProgram))
        .setComment("Software AES128 single-block DECRYPT underROM20840 key, via876C4/864DE in shared196-byte498C context; "
            + "clearcontext87AC2 thenreturnstatus.");
    semanticFunction(0x8D8E6L, "f33_app_security_encrypt_challenge", u32,
        new ParameterImpl("intermediate_key", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("challenge", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("expected_key", new PointerDataType(u8, 4), currentProgram))
        .setComment("Software AES128 single-block ENCRYPT via876C4/863A0 inshared498C context; clearentire196-bytecontext "
            + "afterward. No SecOC secret, CMAC or hardwarecrypto command is used.");
    semanticFunction(0x8D74AL, "f33_app_security_generate_challenge", u32,
        new ParameterImpl("seed_out", new PointerDataType(u8, 4), currentProgram))
        .setComment("Up to2 timer-derived candidates: sample16 bytes, initializeCTR(timerkey,counter0), "
            + "outputAES_timerkey(0), reinitializeCTR(output,currentcounter1), then outputAES_output(1). "
            + "Clear228-byteCTRcontext4A50. Exclusion checkzero/FF and activehistory496A. If transformedcandidates "
            + "fail, rawlasttimerkey is ALSO checked; accepted raw fallback updateschallenge/copy/active. Unlike "
            + "resident6F22, invalid raw fallback returns failure rather than unconditionalsuccess. A prior "
            + "library-failure marker isnotreseton retry, so not every second attempt is independent.");
    semanticFunction(0x8D66AL, "f33_app_security_reset_challenge_material", v)
        .setComment("Zerochallenge495A[16],copy496A[16],client497A[16],active4958/result4959. Calledstartup, every session "
            + "notification4D582 and fullapplicationdiagnostic reset8E62A. Genericdelaybits/failures/securitybitmap "
            + "areseparate.");
    semanticFunction(0x8B334L, "f33_app_programming_handoff_pending_join", u32)
        .setComment("Exact wrapper ignores incomingr6 record pointer constructedby95B88; no consumed formal arguments.8B1B2 "
            + "admissionthen8B262 submissionusing ownzeroedword3B14. Successsets3B19=5A andreturns10; anynonzero3B19 "
            + "laterreturns10 withoutpollingcompletion. Constructed5D4C data isnotdirectresidenthandoffrecord;65F5E "
            + "usesfixedROM31788. No completedprogramming/sessionpublication implied.");
    semanticFunction(0x4D604L, "f33_app_request_programming_transition", v)
        .setComment("Addressing819A==0 and81AE==0 requestsmajor9 viaB15AC thenlatches81AE=5A. Nonzeroaddressing branch resets "
            + "diagnostic owners; admission4D5D8 normally rejectsnonzerobeforethisstage, but globaladdressing "
            + "isretained/non-atomic. No directresident transfer, flashprogramming or securityunlock here.");
    semanticFunction(0x8B262L, "f33_app_programming_submit_local_word", u32,
        new ParameterImpl("local_word", new PointerDataType(u32, 4), currentProgram))
        .setComment("R10 returns merged status. Stage1 formats4 bytes big-endian fromlocalword for "
            + "exactno-oplower8B10C(08000201,10,...), then4D604; stage2 polls exactno-oplower8B110. Own3B1A/B/C/D "
            + "stage/status state; initial8B334passesownzero3B14, not5D4C record.");
    semanticFunction(0x8B1B2L, "f33_app_programming_admit_and_stage", u32)
        .setComment("Lower8B10C/8B110return0 exactly; application8B17E\u21924D5D8 rejectsE81F==11,66BA<0A00,or819A!=0. "
            + "Successclears81AE onceandsets3B18=5A. "
            + "Genericmergedstatusandstageownershipremainseparatefrommode9request.");
    semanticFunction(0x4D5BAL, "f33_app_session_transition_precondition", u32,
        new ParameterImpl("current_session_ignored", u8, currentProgram),
        new ParameterImpl("target", u8, currentProgram))
        .setComment("Onlytarget2 rejectsunsignedE892>ROM318B0=384 withapplicationstatus0B\u2192NRC88 via8E6EC; equalityadmitted. "
            + "Other targets admitted; the E892 load still occurs before target selection. r6current "
            + "snapshotpassedby8B36E butnotreadhere.");
    semanticData(0x259ECL, new ArrayDataType(F33DcmSubfunctionType, 3, 16), "f33_app_session_subfunctions", "Exact sharedservice-bank25C54 selection; existingtype reused.");
    semanticData(0x25B2CL, new ArrayDataType(F33DcmSubfunctionType, 2, 16), "f33_app_session_selector3_subfunctions", "Exact sharedservice-bank25C54 selection; existingtype reused.");
    semanticData(0x25B4CL, new ArrayDataType(F33DcmSubfunctionType, 2, 16), "f33_app_session_selector4_subfunctions", "Exact sharedservice-bank25C54 selection; existingtype reused.");
    semanticData(0x25A5CL, new ArrayDataType(F33DcmSubfunctionType, 4, 16), "f33_app_security_subfunctions", "Exact sharedservice-bank25C54 selection; existingtype reused.");
    semanticData(0x25ACCL, new ArrayDataType(F33DcmSubfunctionType, 1, 16), "f33_app_tester_present_subfunctions", "Exact sharedservice-bank25C54 selection; existingtype reused.");
    semanticData(0x25BACL, new ArrayDataType(F33DcmSubfunctionType, 1, 16), "f33_app_tester_present_selector4_subfunctions", "Exact sharedservice-bank25C54 selection; existingtype reused.");
    semanticData(0x26122L, new ArrayDataType(F33DcmSessionTimingRowType, 4, 10), "f33_app_session_timing_rows", "Fourconfiguredrows1/2/3/40; followingzero terminator isnotfifthvalidsession.");
    semanticData(0x26164L, new ArrayDataType(F33DcmSecurityLevelConfigType, 2, 24), "f33_app_security_level_rows", "Both16 client/16key/16seed, initial/failure10000,levels1/2,threshold2.");
    semanticData(0xFEBE5954L, new ArrayDataType(u32, 2, 4), "f33_app_dcm_security_bitmap", "Application publishedlevels; allzero locked. Not resident2B0F.");
    semanticData(0xFEBE595CL, F33DcmSessionSnapshotType, "f33_app_dcm_session_snapshot", "Current/previous/target/pending, distinctfrom request5D55.");
    semanticData(0xFEBE5D4CL, F33DcmProgrammingRequestType, "f33_app_dcm_constructed_programming_request", "Constructedmetadataignoredbyexact8B334; notROM31788residenthandoffrecord.");
    semanticData(0xFEBE5D54L, u8, "f33_app_dcm_session_row_index", "Indexinto26122; notsessionnumber.");
    semanticData(0xFEBE5D55L, u8, "f33_app_dcm_session_deferred_state", "0idle,1pendingfirst78ack,2applicationpending,3genericcomplete,4notified; exactwrapperneverturnspendinglatchintosuccess.");
    semanticData(0xFEBE5D58L, F33DcmMessageContextType, "f33_app_dcm_session_message", "Retainedadvancedmessagecopiedby95A3E.");
    semanticData(0xFEBE5DC8L, u32, "f33_app_security_delay_bits", "Bits0/1initial/failuredelay; callbacks7/8clearonlybit.");
    semanticData(0xFEBE5DCCL, u8, "f33_app_security_selected_row", "0/1index,not securitylevel.");
    semanticData(0xFEBE5DCDL, u8, "f33_app_security_issued_level", "0noeligibleissuedseed,1/2leveltokenconsumedatkey/denial/cancel.");
    semanticData(0xFEBE5DCEL, u8, "f33_app_security_seed_callback_succeeded", "Setbeforegenericdelay/unlockedchecks;sessioncallback968CCconditionallyclearstoken/flag.");
    semanticData(0xFEBE5DCFL, new ArrayDataType(u8, 2, 1), "f33_app_security_failed_attempts", "Saturatingperrow;delayexpiry/reseed/sessionnotificationdonotreset.");
    semanticData(0xFEBE5DD4L, F33DcmMessageContextType, "f33_app_dcm_security_message", "Retainedadvancedrequest/responsepointersandlengths.");
    semanticData(0xFEBE5D28L, u8, "f33_app_dcm_callback_pending", "Genericcallback10pendingstate; exactappSAcallbacksnever10.");
    semanticData(0xFEBF4958L, u8, "f33_app_security_challenge_active", "5Avalidchallenge;0reinitialize. Notgenericissuedtoken orpublishedsecurity.");
    semanticData(0xFEBF4959L, u8, "f33_app_security_comparison_result", "0accepted/cleared,Bbadkey,independentlyreadbyapplication.");
    semanticData(0xFEBF495AL, new ArrayDataType(u8, 16, 1), "f33_app_security_challenge", "Retainedthroughbadkey/delay/cancel,reusedonseedwhileactive.");
    semanticData(0xFEBF496AL, new ArrayDataType(u8, 16, 1), "f33_app_security_challenge_duplicate", "Copiedtogetherwithchallenge;clearedaftervalidkey/sessionreset,notpersistentprevious-challengehistory.");
    semanticData(0xFEBF497AL, new ArrayDataType(u8, 16, 1), "f33_app_security_client_material", "16clientbytesfromseedrequest;AES-decryptedunderROM20840toderivechallengekey. Retainedafterkeyaccept.");
    semanticData(0xFEBF498CL, F33BootAes128ContextType, "f33_app_security_aes_context", "ApplicationsoftwareAES196-bytecontext;structurallayoutreuseonly;wipedaftereachblock.");
    semanticData(0xFEBF4A50L, F33BootAes128CtrContextType, "f33_app_security_candidate_context", "Applicationcandidate228-bytecontext,notresident2E0Cowner.");
    semanticData(0x20840L, new ArrayDataType(u8, 16, 1), "f33_app_security_client_decryption_key", "ExactsoftwareapplicationSAkey893E08418C741FFA2A9C044BFFA55813. NotSecOC/CryptoIfkeyslot.");
    semanticData(0x25620L, F33BootChallengeExclusionRecordType, "f33_app_security_initial_exclusions", "zero/FFtwoexclusions,structurallayoutreuseonly.");
    semanticData(0x25630L, F33BootChallengeExclusionRecordType, "f33_app_security_active_exclusions", "zero/FFand496Athreeexclusionswhileactive.");
    semanticData(0xFEBF3B14L, u32, "f33_app_programming_local_word", "Exact8B334zerosownwordbeforesubmission,notclient-suppliedhandoffbytes.");
    semanticData(0xFEBF3B18L, u8, "f33_app_programming_admission_latched", "5Aafterapplicationgateadmitted;retaineduntil8B134reset.");
    semanticData(0xFEBF3B19L, u8, "f33_app_programming_pending_latch", "Nonzero=>8B334returns10withoutcompletionpoll.");
    semanticData(0xFEBE81AEL, u8, "f33_app_programming_mode_request_latched", "4D604sets5Aafterrequest9;localSID10canceldoesnotclearit.");
  }

  private void annotateApplicationNetworkLifetimes() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType F33DcmMessageContextType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33DcmMessageContext");
    if (F33DcmMessageContextType == null) throw new IllegalStateException("missing F33DcmMessageContext");
    DataType F33DcmSubfunctionType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33DcmSubfunction");
    if (F33DcmSubfunctionType == null) throw new IllegalStateException("missing F33DcmSubfunction");
    FunctionDefinitionDataType policyCallback = new FunctionDefinitionDataType(category, "F33NormalNetworkPolicyCallback");
    policyCallback.setReturnType(u32);
    policyCallback.setArguments(new ParameterDefinitionImpl("network", u8, null));
    DataType F33NormalNetworkPolicyCallbackType = currentProgram.getDataTypeManager().addDataType(policyCallback, DataTypeConflictHandler.REPLACE_HANDLER);
    EnumDataType driverStates = new EnumDataType(category, "F33DriverChannelSoftwareState", 2);
    driverStates.add("uninitialized", 0x6e91L);
    driverStates.add("initialized", 0x6d92L);
    driverStates.add("stopped_software_state", 0x6b94L);
    driverStates.add("running_software_state", 0x57a8L);
    driverStates.add("start_pending", 0x3bc4L);
    driverStates.add("stop_pending", 0x3ec1L);
    driverStates.add("recovery_pending", 0x3dc2L);
    DataType F33DriverChannelSoftwareStateType = currentProgram.getDataTypeManager().addDataType(driverStates, DataTypeConflictHandler.REPLACE_HANDLER);
    StructureDataType layout0 = new StructureDataType(category, "F33DcmCommunicationLocalState", 0);
    layout0.setPackingEnabled(true);
    layout0.add(u8, "admission_result", null);
    layout0.add(u8, "application_status", null);
    layout0.add(u8, "lower_status", null);
    layout0.add(u8, "action_state", null);
    layout0.add(u8, "retained_subnet", null);
    layout0.add(u8, "side_status", null);
    layout0.add(u8, "last_mapped_mode", null);
    layout0.add(u8, "last_tx_disable_bit", null);
    DataType F33DcmCommunicationLocalStateType = resolve(layout0);
    StructureDataType layout1 = new StructureDataType(category, "F33DcmCommunicationLifetime", 0);
    layout1.setPackingEnabled(true);
    layout1.add(u16, "protocol_selector", null);
    layout1.add(u8, "subfunction", null);
    layout1.add(u8, "resume_row", null);
    layout1.add(u8, "accepted_active", null);
    layout1.add(new ArrayDataType(u8, 3, 1), "padding_uninterpreted", null);
    layout1.add(F33DcmMessageContextType, "retained_message", null);
    DataType F33DcmCommunicationLifetimeType = resolve(layout1);
    StructureDataType layout2 = new StructureDataType(category, "F33RequestedNormalNetworkPolicy", 0);
    layout2.setPackingEnabled(true);
    layout2.add(u8, "requested_policy", null);
    layout2.add(u8, "reconciled_software_policy", null);
    layout2.add(u16, "remaining_delay", null);
    DataType F33RequestedNormalNetworkPolicyType = resolve(layout2);
    StructureDataType layout3 = new StructureDataType(category, "F33SelectedNetworkModeState", 0);
    layout3.setPackingEnabled(true);
    layout3.add(u16, "mode_state", null);
    layout3.add(u8, "remaining_delay", null);
    layout3.add(u8, "uninterpreted", null);
    DataType F33SelectedNetworkModeStateType = resolve(layout3);
    StructureDataType layout4 = new StructureDataType(category, "F33SelectedNetworkRecoveryState", 0);
    layout4.setPackingEnabled(true);
    layout4.add(u16, "recovery_state", null);
    layout4.add(s16, "remaining_hold", null);
    layout4.add(u16, "aggregated_cause", null);
    layout4.add(u8, "reported_fault_class", null);
    layout4.add(u8, "uninterpreted", null);
    DataType F33SelectedNetworkRecoveryStateType = resolve(layout4);
    StructureDataType layout5 = new StructureDataType(category, "F33CommunicationChannelSelection", 0);
    layout5.setPackingEnabled(true);
    layout5.add(u8, "active", null);
    layout5.add(u8, "channel", null);
    DataType F33CommunicationChannelSelectionType = resolve(layout5);
    StructureDataType layout6 = new StructureDataType(category, "F33NormalNetworkPolicyCallbacks", 0);
    layout6.setPackingEnabled(true);
    layout6.add(new PointerDataType(F33NormalNetworkPolicyCallbackType, 4), "request_disable", null);
    layout6.add(new PointerDataType(F33NormalNetworkPolicyCallbackType, 4), "request_enable", null);
    DataType F33NormalNetworkPolicyCallbacksType = resolve(layout6);
    StructureDataType layout7 = new StructureDataType(category, "F33DcmCommunicationConfiguration", 0);
    layout7.setPackingEnabled(true);
    layout7.add(u8, "restore_enabled", null);
    layout7.add(u8, "normal_enabled", null);
    layout7.add(u8, "nm_enabled", null);
    layout7.add(u8, "current_network_enabled", null);
    layout7.add(u8, "channel_count", null);
    layout7.add(u8, "subnet_count", null);
    layout7.add(u8, "node_count", null);
    layout7.add(u8, "opaque_07", null);
    layout7.add(new PointerDataType(F33CommunicationChannelSelectionType, 4), "channels", null);
    layout7.add(new PointerDataType(v, 4), "subnets", null);
    layout7.add(new PointerDataType(v, 4), "nodes", null);
    DataType F33DcmCommunicationConfigurationType = resolve(layout7);
    semanticFunction(0x97142L, "f33_dcm_communication_enable_rx_tx", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("ConfiguredSID28sub0/session3 wrapper; shared9701C lifetime, only communicationByte01 admitted by image.");
    semanticFunction(0x97152L, "f33_dcm_communication_enable_rx_disable_tx", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("ConfiguredSID28sub1/session3; application effect is retained8196Tx-policy request, not controller "
            + "confirmation or7F97.");
    semanticFunction(0x97162L, "f33_dcm_communication_disable_rx_tx_request", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Configuredsub3 name describes request only; actual local actionusesmappedmodebit0 and does not "
            + "independently implement Rxdisable.");
    semanticFunction(0x9701CL, "f33_dcm_dispatch_communication_control_lifetime", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram),
        new ParameterImpl("subfunction", u8, currentProgram))
        .setComment("Operation0 starts96E6A;2 removes queued26h continuation and clears diagnostic sentinel, not retained "
            + "policy; otheroperationsreturn0.");
    semanticFunction(0x96E6AL, "f33_dcm_begin_configured_communication_request", u32,
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram),
        new ParameterImpl("subfunction", u8, currentProgram))
        .setComment("Copy28-byte context, validateexactpayload, "
            + "communicationselectorandlocaladmission;retainprotocol/subfunction/activeflag;dispatchactualactionandcompletion.");
    semanticFunction(0x96BFCL, "f33_dcm_validate_configured_communication_selection", u32,
        new ParameterImpl("subfunction", u8, currentProgram),
        new ParameterImpl("communication_class", u8, currentProgram),
        new ParameterImpl("subnet", u8, currentProgram),
        new ParameterImpl("node", u16, currentProgram))
        .setComment("Exactconfiguration admitslow1/high0 only; optional4/5nodepaths are unconfigured.");
    semanticFunction(0x97116L, "f33_dcm_check_communication_application_admission", u32,
        new ParameterImpl("subfunction", u8, currentProgram),
        new ParameterImpl("communication_type", u8, currentProgram),
        new ParameterImpl("node", u16, currentProgram),
        new ParameterImpl("nrc", new PointerDataType(u8, 4), currentProgram))
        .setComment("Forward the fourth R9 NRC pointer to8DA10 and return its meaningful R10 admission result.");
    semanticFunction(0x8DA10L, "f33_admit_application_communication_request", u32,
        new ParameterImpl("subfunction", u8, currentProgram),
        new ParameterImpl("communication_type", u8, currentProgram),
        new ParameterImpl("node", u16, currentProgram),
        new ParameterImpl("nrc", new PointerDataType(u8, 4), currentProgram))
        .setComment("Idle45A0andE892<=384 admit;busy/strictunsignedgreaterreject22. "
            + "Stagehighnibbleandactionstate;459Drecordsadmission.");
    semanticFunction(0x8DA5EL, "f33_apply_and_complete_communication_policy_request", u32,
        new ParameterImpl("channel", u8, currentProgram),
        new ParameterImpl("mapped_mode", u8, currentProgram))
        .setComment("RealR10merge status;state1loweradapterisexactreturn0,dispatchgatefixed5A,then4FD18publishes8196. "
            + "Retainlastmappedmode/bit0aftercompletion.");
    semanticFunction(0x4FD04L, "f33_communication_request_sample_above_limit", u32)
        .setComment("CompareunsignedE892toROM318B0=384,returnstrictgreater. Do notaddnominalarguments "
            + "merelybecausecallerspopulateR6/R7.");
    semanticFunction(0x4FD18L, "f33_publish_diagnostic_normal_tx_policy_request", v,
        new ParameterImpl("network_selector", u8, currentProgram),
        new ParameterImpl("disable_tx", u8, currentProgram))
        .setComment("R6ignored;R7=0stores8196=00,R7=1stores11;otherlowbytesretain. Not7F97andnotphysicaldisable.");
    semanticFunction(0x96D72L, "f33_dcm_complete_or_queue_communication_request", v,
        new ParameterImpl("subnet", u8, currentProgram),
        new ParameterImpl("subfunction", u8, currentProgram),
        new ParameterImpl("node", u16, currentProgram),
        new ParameterImpl("mapped_mode", u8, currentProgram),
        new ParameterImpl("start_index", u8, currentProgram))
        .setComment("Iterateactiveconfiguredchannels;action0positivecompletes,1returns,10savestherowcursorandqueues26h. "
            + "Stackargumentfromrealcallsite,notafifthGPR.");
    semanticFunction(0x970C0L, "f33_dcm_resume_queued_communication_request", v)
        .setComment("Actual26B18[26h]callback at26BB0;resume5DF8/5DF2/5DF3. Event26hnotahardwaretimer.");
    semanticFunction(0x97004L, "f33_dcm_cancel_communication_continuation", v)
        .setComment("Invalidateallqueued26hentriesandclear5D24sentinel;no8196rollbackorcontrollerstop/start.");
    semanticFunction(0x9704EL, "f33_dcm_notify_communication_session_change", v,
        new ParameterImpl("old_session", u8, currentProgram),
        new ParameterImpl("new_session", u8, currentProgram))
        .setComment("Exact261C4=0 disablesrestorebody. Latentnew1/retainedSID28invalidrestore8targetsarealsoempty. "
            + "KeepR8new_sessionforwardingto916EC;thisdoesnotclear8196.");
    semanticFunction(0x49AD2L, "f33_reconcile_application_normal_network_policy", v)
        .setComment("Snapshot8196/81CC;composechannelmonitor;enableonlystate2&&8196!=11&&81CC==5A,otherwiseissuedisableedge. "
            + "Publish7F3Asoftwarestatus.");
    semanticFunction(0x7C110L, "f33_request_normal_network_policy_disable", u32,
        new ParameterImpl("network", u8, currentProgram))
        .setComment("SelectedROM2184Cslot0leaf;change3DE0from1Eto0Freturn0,otherwiserequestheldreturn12h. NoMMIO.");
    semanticFunction(0x7C136L, "f33_request_normal_network_policy_enable", u32,
        new ParameterImpl("network", u8, currentProgram))
        .setComment("SelectedROM2184Cslot1;retain3DE1separately,set3DE0=1Eanddelay3DE2;return13hifalreadyrequested,else0.");
    semanticFunction(0x7C1D4L, "f33_reconcile_requested_normal_network_policy", u32,
        new ParameterImpl("local_index", u8, currentProgram),
        new ParameterImpl("clear_request", u8, currentProgram))
        .setComment("Four-byte3DE0requested/reconciled/countdownrecord;callback21820from7BF10. "
            + "Reconciledstateissoftwarepolicy,nothardwareacknowledgement.");
    semanticFunction(0x7F4DCL, "f33_request_logical_controller_run_stop", u32,
        new ParameterImpl("logical_controller", u8, currentProgram),
        new ParameterImpl("requested_mode", u8, currentProgram))
        .setComment("Mode2start,3stop;logicalcache48D8mayupdatebeforemappeddriver5020acknowledges.");
    semanticFunction(0x83FFAL, "f33_driver_request_channel_start_stop", u32,
        new ParameterImpl("driver_index", u8, currentProgram),
        new ParameterImpl("request", u8, currentProgram))
        .setComment("0start/1stop;stage3BC4/3EC1beforephysicalhelpers;return0includespending. "
            + "Commit57A8/6B94onlyafterzerohelperresult;7FB5Cindicationisempty.");
    semanticFunction(0x840C2L, "f33_driver_poll_pending_channel_modes", v)
        .setComment("Poll3BC4/3EC1/3DC2andcommitstateonlyonzeroresult;nocreatedphysicalsuccess. Calledby79F16.");
    semanticFunction(0x837D6L, "f33_driver_observe_and_clear_bus_off_entry", u32,
        new ParameterImpl("driver_index", u8, currentProgram))
        .setComment("ReadERFLbit3BOEF;write7FF7andlatch5010=5Aifset;returntruewhenabsent. "
            + "Selectedindex1isRSCFD0channel1,notvehiclebus1.");
    semanticFunction(0x80CD2L, "f33_publish_mapped_controller_bus_off_event", v,
        new ParameterImpl("driver_index", u8, currentProgram))
        .setComment("Mapdriver1\u2192logical0using21978;publish48FEbits7:6=10bunderlockonlyforinitializedlogicalstate. NotSID28.");
    semanticFunction(0x7CE24L, "f33_update_selected_network_fault_recovery", v,
        new ParameterImpl("selected_network", u8, currentProgram))
        .setComment("Aggregatehardware/softwareevents,gateonlogicalmode2/3,requestrecoverystop/start,retain491C/491Eandcause. "
            + "Holdexpiryisnotphysicalbusrecoveryproof.");
    semanticFunction(0x7CBB6L, "f33_get_selected_network_software_mode", u32,
        new ParameterImpl("network", u8, currentProgram),
        new ParameterImpl("mode", new PointerDataType(u8, 4), currentProgram))
        .setComment("Expose0/1/2from4924and491Crecovery,notdriverCSTS. Unknownstatesreturn1withoutpublication.");
    semanticData(0xFEBF459DL, F33DcmCommunicationLocalStateType, "f33_dcm_communication_local_state", "Recovered software lifetime layout; no physical bus, acknowledgement or elapsed-time implication.");
    semanticData(0xFEBE5DF0L, F33DcmCommunicationLifetimeType, "f33_dcm_communication_lifetime", "Recovered software lifetime layout; no physical bus, acknowledgement or elapsed-time implication.");
    semanticData(0xFEBE3DE0L, F33RequestedNormalNetworkPolicyType, "f33_requested_normal_network_policy", "Recovered software lifetime layout; no physical bus, acknowledgement or elapsed-time implication.");
    semanticData(0xFEBE4924L, F33SelectedNetworkModeStateType, "f33_selected_network_mode", "Recovered software lifetime layout; no physical bus, acknowledgement or elapsed-time implication.");
    semanticData(0xFEBE491CL, F33SelectedNetworkRecoveryStateType, "f33_selected_network_recovery", "Recovered software lifetime layout; no physical bus, acknowledgement or elapsed-time implication.");
    semanticData(0x261C0L, new ArrayDataType(F33CommunicationChannelSelectionType, 1, 2), "f33_dcm_communication_channels", "Recovered software lifetime layout; no physical bus, acknowledgement or elapsed-time implication.");
    semanticData(0xFEBE5020L, new ArrayDataType(F33DriverChannelSoftwareStateType, 3, 2), "f33_driver_channel_software_states", "Driver-indexed software state; pending request, completion and observed hardware status remain distinct.");
    createLabel(toAddr(0x25CFCL), "f33_dcm_communication_control_service_descriptor", true);
    currentProgram.getListing().setComment(toAddr(0x25CFCL), CodeUnit.PLATE_COMMENT, "Exact configured SID28/network data; selected software interface only.");
    semanticData(0x25A9CL, new ArrayDataType(F33DcmSubfunctionType, 3, 16), "f33_dcm_communication_control_subfunctions", "Exact configured SID28/network data; selected software interface only.");
    semanticData(0x261ACL, new ArrayDataType(new ArrayDataType(u8, 3, 1), 6, 3), "f33_dcm_communication_mode_map", "Onlynormalcolumn0ofsubrows0/1/3configured;261ABprecedingbyteisnotrow0column0.");
    semanticData(0x261C4L, F33DcmCommunicationConfigurationType, "f33_dcm_communication_configuration", "Exact restore0, normal1, NM0, current-network0; one active channel and no subnet/node rows.");
    semanticData(0xFEBE8196L, u8, "f33_diagnostic_normal_tx_policy_request", "00release/11disable;softwarepolicyrequestnot7F97");
    semanticData(0x318B0L, u16, "f33_communication_control_admission_limit", "Noengineeringunitassignedfromaddressalone.");
    semanticData(0x2184CL, F33NormalNetworkPolicyCallbacksType, "f33_selected_normal_network_policy_callbacks", "Exact configured SID28/network data; selected software interface only.");
    semanticData(0x21978L, new ArrayDataType(u8, 3, 1), "f33_driver_to_logical_controller_map", "Driverindex1\u2192logical0;FFunmapped. Notvehiclebusidentity.");
    semanticData(0x22F68L, new ArrayDataType(new PointerDataType(v, 4), 3, 4), "f33_driver1_rscfd0_channel1_control_status_error_pointers", "Manualp2982CFDC1CTR/STS/ERFL;notphysicalvehiclebusnumber. Pointer identities do not assign register access widths.");
    createLabel(toAddr(0x26BB0L), "f33_dcm_event26_communication_resume_callback", true);
    currentProgram.getListing().setComment(toAddr(0x26BB0L), CodeUnit.PLATE_COMMENT, "98946dispatchbase26B18,event26h.");
    semanticData(0xFEBE3DF0L, new ArrayDataType(u8, 1, 1), "f33_upper_network_software_indication", "0/1/3;separatefromrequestedpolicyanddriverstate");
    semanticData(0xFEBE48D8L, new ArrayDataType(u16, 1, 2), "f33_logical_controller_request_cache", "Canbeupdatedbeforephysicaldrivercompletion;neveruseasCSTSack.");
    semanticData(0xFEBE5010L, new ArrayDataType(u8, 3, 1), "f33_driver_bus_off_observation_latch", "3Cclear/5Aobserved;setfromERFLBOEF");
  }

  private void annotateMonitorCalibrationAndOutputEnvelopes() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType s8 = SignedByteDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    StructureDataType layout0 = new StructureDataType(category, "F33MonitorCurrentCoefficients", 0);
    layout0.setPackingEnabled(true);
    StructureDataType layout1 = new StructureDataType(category, "F33MonitorCurrentActiveCalibration", 0);
    layout1.setPackingEnabled(true);
    StructureDataType layout2 = new StructureDataType(category, "F33MonitorCurrentStagedCalibration", 0);
    layout2.setPackingEnabled(true);
    StructureDataType layout3 = new StructureDataType(category, "F33MonitorCurrentRecord", 0);
    layout3.setPackingEnabled(true);
    StructureDataType layout4 = new StructureDataType(category, "F33RegulatorOutputEnvelopeCalibration", 0);
    layout4.setPackingEnabled(true);
    StructureDataType layout5 = new StructureDataType(category, "F33RegulatorOutputEnvelopeState", 0);
    layout5.setPackingEnabled(true);
    layout0.add(new ArrayDataType(s16, 6, 2), "negative_residual_gain", "Selected for residual<0.");
    layout0.add(new ArrayDataType(s16, 6, 2), "nonnegative_residual_gain", "Selected for residual>=0.");
    layout0.add(new ArrayDataType(s16, 6, 2), "bias", "Signed residual offset, not a physical zero claim.");
    layout1.add(u8, "changed", "5A iff staged coefficients differ on valid nonbusy source path.");
    layout1.add(u8, "range_error", "5A for rejected changed coefficients; equal bypasses validation.");
    layout1.add(layout0, "coefficients", "Consumed by current conditioning before later scheduled adoption.");
    layout1.add(new ArrayDataType(u8, 2, 1), "opaque_26", "Not assigned a calibration meaning.");
    layout2.add(u8, "source_status", "32A8C publishes44/22.");
    layout2.add(u8, "busy", "5A while refresh is unresolved.");
    layout2.add(layout0, "coefficients", "Grouped by sign/bias across both banks.");
    layout2.add(new ArrayDataType(u8, 2, 1), "opaque_26", "Not interpreted.");
    layout2.add(u32, "marker", "A55A5AA5 valid; complementary failure. Setter publication is not acceptance.");
    layout3.add(u32, "marker", "Record0200 marker, separate from status10.");
    layout3.add(new ArrayDataType(s16, 3, 2), "bank1_negative_gain", "Serialized bank1 before bank0; different order from staged arrays.");
    layout3.add(new ArrayDataType(s16, 3, 2), "bank1_nonnegative_gain", "Serialized bank1 before bank0; different order from staged arrays.");
    layout3.add(new ArrayDataType(s16, 3, 2), "bank1_bias", "Serialized bank1 before bank0; different order from staged arrays.");
    layout3.add(new ArrayDataType(s16, 3, 2), "bank0_negative_gain", "Serialized bank1 before bank0; different order from staged arrays.");
    layout3.add(new ArrayDataType(s16, 3, 2), "bank0_nonnegative_gain", "Serialized bank1 before bank0; different order from staged arrays.");
    layout3.add(new ArrayDataType(s16, 3, 2), "bank0_bias", "Serialized bank1 before bank0; different order from staged arrays.");
    layout4.add(s8, "cubic_coefficient", "SLD.B at36982/36C8E loadsF5 as-11, not16-bit245.");
    layout4.add(u8, "opaque_01", "Not part of the signed coefficient.");
    layout4.add(s16, "first_upper", "Inclusive7658 saturation.");
    layout4.add(s16, "first_lower", "Inclusive-7658 saturation.");
    layout4.add(s16, "quadratic_coefficient", "Exact127.");
    layout4.add(s16, "linear_coefficient", "Exact-1135.");
    layout4.add(u16, "scale_upper", "Exact1707.");
    layout4.add(u16, "scale_lower", "Exact700.");
    layout4.add(new ArrayDataType(u8, 2, 1), "opaque_0e", "Not interpreted.");
    layout4.add(s32, "base", "17365676; final addition is symmetrically saturated.");
    layout4.add(s32, "lower", "Exact0.");
    layout4.add(s32, "upper", "Exact17365676.");
    layout4.add(s32, "band_width", "Exact209715 before/2048.");
    layout5.add(u8, "second_saturation", "0interior,1positive,2negative; equality saturates.");
    layout5.add(u8, "first_saturation", "0interior,1positive,2negative; equality saturates.");
    layout5.add(u8, "reset_cleared_status", "Reset clears; no further role assigned here.");
    layout5.add(u8, "opaque_03", "Preserved padding.");
    layout5.add(s16, "first", "Clamped first-axis output.");
    layout5.add(s16, "second", "Prior magnitude participates in next limit selection.");
    layout5.add(s16, "selected_second_limit", "Magnitude clamp inside current envelope band.");
    layout5.add(s16, "second_lower", "Lower envelope edge.");
    layout5.add(s16, "second_upper", "Upper envelope edge.");
    layout5.add(new ArrayDataType(u8, 2, 1), "opaque_0e", "Preserved padding.");
    layout5.add(s32, "first_unclipped", "Scaled first-axis value before7658 clamp.");
    layout5.add(s32, "second_unclipped", "Scaled second-axis value before selected limit.");
    layout5.add(s32, "raw_cubic", "Cubic before its lower/upper clamp.");
    layout5.add(s32, "lower_before_clamp", "Clamped cubic minus band width; before lower clamp.");
    layout5.add(s32, "combined_second", "Common or wrapping common+/-differential divided2.");
    layout5.add(u32, "retained_24", "Reset1024; normal composition preserves this field.");
    layout5.add(u32, "retained_28", "Reset1024; normal composition preserves this field.");
    semanticFunction(0x48D48L, "f33_refresh_monitor_current_reference_banks", v)
        .setComment("Exact31E58=1: refresh each retained three-channel reference bank7E6C/7E72 only when corresponding "
            + "snapshot636A/636B equals5A; otherwise hold the older reference generation.");
    semanticFunction(0x48DA6L, "f33_condition_monitor_current_planes", v)
        .setComment("Refresh qualified reference banks, then project six channels with signed residual-dependent gains6906/6912 "
            + "and biases691E.7E78 uses622C minus retained7E6C minus bias;7E84 uses6238 minus32768 and bias;7E90 uses622C "
            + "with the fixed midpoint. Symmetric32 multiply saturation, truncation/16384, then symmetric16 saturation. CH2 "
            + "monitor representation, not rotating-frame feedback.");
    semanticFunction(0x32724L, "f33_monitor_current_coefficients_differ", u32)
        .setComment("Compare all18 active/staged signed halfwords; return5A iff any differ, else0. Comparison precedes range "
            + "validation in32876.");
    semanticFunction(0x327D6L, "f33_adopt_monitor_current_coefficients", v)
        .setComment("Copy staged negative/nonnegative gain arrays and biases into active6906/6912/691E. Does not publish source "
            + "marker or changed/error bytes.");
    semanticFunction(0x32848L, "f33_reset_active_monitor_current_coefficients", v)
        .setComment("Set all12 active gains to signedBE36=-16842 and all six biases0. Does not clear6904/6905 status bytes.");
    semanticFunction(0x32876L, "f33_update_active_monitor_current_calibration", v)
        .setComment("Only8A18==5A acts. Valid6954=A55A5AA5 and busy692D=0: compare; equal skips validation and publishes "
            + "statuses0/0; changed validates, adopts on0 or resets active defaults on5A. Invalid marker/busy resets active "
            + "coefficients but retains previous changed/error bytes. Stage and source marker are not invalidated by range "
            + "rejection.");
    semanticFunction(0x328D4L, "f33_copy_monitor_calibration_from_rom_record", v)
        .setComment("Makes its own40-byte family2 record0200 getter call, separate from caller marker read. Copy coefficients "
            + "only on status10; serialized bank1 precedes bank0, while RAM arrays group both banks by sign/bias. Getter "
            + "reads immutable ROMA000, not setter RAMF5D0; no atomic two-read claim.");
    semanticFunction(0x32972L, "f33_validate_staged_monitor_current_coefficients", u32)
        .setComment("Return0 iff all12 gains are inclusively[-20912,-14080] and all six biases inclusively[-1835,1835]; "
            + "otherwise5A. Signed16 calibration bounds30EA0..30EA6; no state mutation.");
    semanticFunction(0x32A48L, "f33_reset_staged_monitor_current_coefficients", v)
        .setComment("Set staged12 gains to-16842 and six biases0. Exact leaf changesR1/EP and preservesR10, which32A76 returns "
            + "from preceding validation. Inline real p-code to preserve this ABI fact.");
    semanticFunction(0x32A76L, "f33_validate_or_reset_staged_monitor_current_coefficients", u32)
        .setComment("Return original range-validation status0/5A. On5A reset staged coefficients through32A48, without converting "
            + "the failed result into success.");
    semanticFunction(0x32A8CL, "f33_restore_monitor_current_calibration", v)
        .setComment("First0200 getter must return10 with markerA55A5AA5;328D4 separately gets/copies coefficients, then "
            + "validation may reset them. Success sets markerA55A5AA5/source44 and diagnostic0124 healthy; failure sets "
            + "complementary marker5AA5A55A/source22 and event0124/failure32. No persistence or two-read atomicity claim.");
    semanticFunction(0x32AF0L, "f33_reload_monitor_current_calibration_marker", u32)
        .setComment("First0200 getter checks status10/marker; second independent getter through328D4 copies coefficients;32A76 "
            + "validates/resets stage. ReturnA55A5AA5 on success, complementary5AA5A55A on failure. Reads ROM, not the "
            + "setter RAM mirror.");
    semanticFunction(0x32B30L, "f33_refresh_monitor_current_calibration", v)
        .setComment("When6501==5A and source marker valid, set busy5A, reload via32AF0 and clear busy only on valid return; "
            + "invalid return reports0124/failure32. Other admission states clear busy and retain marker. Active "
            + "coefficients are adopted separately later.");
    semanticFunction(0x32BE8L, "f33_submit_monitor_current_calibration_record", v)
        .setComment("Serialize bank1 then bank0 coefficients after valid record marker and call setter0200. Ignore setter "
            + "admission result; unconditionally publish valid6954 afterward. This marker is neither setter acceptance nor "
            + "durability, and later getter still reads ROMA000.");
    semanticFunction(0x32C78L, "f33_get_staged_monitor_current_range_status", u32)
        .setComment("Forward32972 range result inR10; no additional gate or transformation.");
    semanticFunction(0x3695EL, "f33_regulator_output_envelope_cubic_bank0", s32)
        .setComment("Bank0 cubic in saturating abs16 of clamped first-axis output. Leading coefficient is signed BYTEF5=-11 "
            + "(SLD.B), not halfword245. Sequential truncation: ((-1135+((127+(-11*x)/128)*x)/1024)/4)*x; symmetric32 "
            + "saturated add to17365676. No physical unit inferred.");
    semanticFunction(0x36C6AL, "f33_regulator_output_envelope_cubic_bank1", s32)
        .setComment("Bank1 cubic in saturating abs16 of clamped first-axis output. Leading coefficient is signed BYTEF5=-11 "
            + "(SLD.B), not halfword245. Sequential truncation: ((-1135+((127+(-11*x)/128)*x)/1024)/4)*x; symmetric32 "
            + "saturated add to17365676. No physical unit inferred.");
    semanticFunction(0x369E4L, "f33_compose_regulator_output_bank0", v)
        .setComment("Bank0: reset on8BAE nonzero or8B28&40004. Healthy71EC low bits0 uses wrapping32 common+differential then "
            + "signed/2; any invalid bit uses common terms directly. Clamp own signed scale6CF0 to700..1707; truncate/256, "
            + "symmetric32 multiply, truncate/2048. First axis clamps+/-7658 with equality saturation. Second limit uses "
            + "signed-byte cubic and209715-wide band, retaining prior output magnitude inside new band; current magnitude "
            + "below lower edge selects lower edge. Publish separate unclipped values, band and saturation directions. Not "
            + "physical PWM delivery.");
    semanticFunction(0x36CF0L, "f33_compose_regulator_output_bank1", v)
        .setComment("Bank1: reset on8BAF nonzero or8B28&40004. Healthy71EC low bits0 uses wrapping32 common-differential then "
            + "signed/2; any invalid bit uses common terms directly. Clamp own signed scale6CF4 to700..1707; truncate/256, "
            + "symmetric32 multiply, truncate/2048. First axis clamps+/-7658 with equality saturation. Second limit uses "
            + "signed-byte cubic and209715-wide band, retaining prior output magnitude inside new band; current magnitude "
            + "below lower edge selects lower edge. Publish separate unclipped values, band and saturation directions. Not "
            + "physical PWM delivery.");
    semanticFunction(0x5E444L, "f33_step_transitioned_channel_monitor_slice", v,
        new ParameterImpl("unused_r6", u32, currentProgram),
        new ParameterImpl("current_mode", u16, currentProgram),
        new ParameterImpl("previous_mode", u16, currentProgram))
        .setComment("Low16 current modeR7/prior modeR8 control entry initialization and monitor groups. For current>100h "
            + "condition current planes before monitor consumers; for current>102h adopt active calibration only after "
            + "fault aggregation. Thus this invocation uses the prior active-calibration generation. Mode600 sampling and "
            + "later owner9 budgets are separate branches; no task-period claim.");
    semanticFunction(0x5E9F2L, "f33_step_steady_channel_monitor_slice", v,
        new ParameterImpl("unused_r6", u32, currentProgram),
        new ParameterImpl("current_mode", u16, currentProgram))
        .setComment("Steady-mode counterpart: current planes when low16 mode>100h; aggregate actions then calibration adoption "
            + "when mode>102h. No transition initializers. Current conditioning therefore precedes active-calibration "
            + "adoption in this call.");
    semanticData(0xFEBE6904L, resolve(layout1), "f33_monitor_current_active_calibration",
        "Exact recovered software layout; source generation and publication are separate.");
    semanticData(0xFEBE692CL, resolve(layout2), "f33_monitor_current_staged_calibration",
        "Exact recovered software layout; source generation and publication are separate.");
    semanticData(0xA000L, resolve(layout3), "f33_monitor_current_rom_record",
        "Exact recovered software layout; source generation and publication are separate.");
    semanticData(0xFEBEF5D0L, resolve(layout3), "f33_monitor_current_setter_ram_record",
        "Exact recovered software layout; source generation and publication are separate.");
    semanticData(0x319E0L, new ArrayDataType(resolve(layout4), 2, 32), "f33_regulator_output_envelope_calibrations",
        "Exact recovered software layout; source generation and publication are separate.");
    semanticData(0xFEBE6BE8L, new ArrayDataType(resolve(layout5), 2, 44), "f33_regulator_output_envelopes",
        "Exact recovered software layout; source generation and publication are separate.");
    semanticData(0xFEBE7E6CL, new ArrayDataType(u16, 6, 2), "f33_monitor_current_retained_reference",
        "Two independently qualified three-channel reference generations.");
    semanticData(0xFEBE7E78L, new ArrayDataType(s16, 6, 2), "f33_monitor_current_dynamic_reference_plane",
        "622C minus retained reference and bias; not rotating-frame feedback.");
    semanticData(0xFEBE7E84L, new ArrayDataType(s16, 6, 2), "f33_monitor_current_second_midpoint_plane",
        "6238 minus32768 and bias; signed calibrated projection.");
    semanticData(0xFEBE7E90L, new ArrayDataType(s16, 6, 2), "f33_monitor_current_first_midpoint_plane",
        "622C minus32768 and bias; separate source generation.");
    semanticData(0x30EA0L, new ArrayDataType(s16, 4, 2), "f33_monitor_current_gain_bias_bounds",
        "Gain upper/lower=-14080/-20912; bias upper/lower=1835/-1835, inclusive.");
    getFunctionAt(toAddr(0x32A48L)).setInline(true);
  }

  private void annotateDiagnosticTransportOwnership() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType F33DcmMessageContextType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33DcmMessageContext");
    DataType F33PduInfoType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33PduInfo");
    StructureDataType layout0 = new StructureDataType(category, "F33DcmReceiveRoute", 0);
    layout0.setPackingEnabled(true);
    StructureDataType layout1 = new StructureDataType(category, "F33DcmReceiveBufferConfiguration", 0);
    layout1.setPackingEnabled(true);
    StructureDataType layout2 = new StructureDataType(category, "F33DcmReceiveBufferState", 0);
    layout2.setPackingEnabled(true);
    StructureDataType layout3 = new StructureDataType(category, "F33DcmReceiveDescriptor", 0);
    layout3.setPackingEnabled(true);
    StructureDataType layout4 = new StructureDataType(category, "F33DcmTransmitDescriptor", 0);
    layout4.setPackingEnabled(true);
    StructureDataType layout5 = new StructureDataType(category, "F33DcmConnection", 0);
    layout5.setPackingEnabled(true);
    StructureDataType layout6 = new StructureDataType(category, "F33DcmProtocolConfiguration", 0);
    layout6.setPackingEnabled(true);
    StructureDataType layout7 = new StructureDataType(category, "F33DcmResponseNode", 0);
    layout7.setPackingEnabled(true);
    StructureDataType layout8 = new StructureDataType(category, "F33DcmResponseQueue", 0);
    layout8.setPackingEnabled(true);
    StructureDataType layout9 = new StructureDataType(category, "F33DcmRetryInfo", 0);
    layout9.setPackingEnabled(true);
    StructureDataType layout10 = new StructureDataType(category, "F33CanTpFrameInfo", 0);
    layout10.setPackingEnabled(true);
    StructureDataType layout11 = new StructureDataType(category, "F33CanTpTxStatePrefix", 0);
    layout11.setPackingEnabled(true);
    StructureDataType layout12 = new StructureDataType(category, "F33CanTpConfiguration", 0);
    layout12.setPackingEnabled(true);
    StructureDataType layout13 = new StructureDataType(category, "F33CanTpTxConnection", 0);
    layout13.setPackingEnabled(true);
    layout0.add(u16, "protocol_index", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(u16, "connection_index", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(u16, "receive_descriptor_index", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(u16, "communication_slot", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(u16, "paired_receive_slot_or_ffff", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(u16, "receive_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(u32, "capacity", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(new PointerDataType(u8, 4), "base", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(new PointerDataType(u8, 4), "write_cursor", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(u16, "received_length", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(new ArrayDataType(u8, 2, 1), "opaque_06", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(u16, "remaining_capacity", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(u8, "receiving", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(u8, "abort_pending", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(u8, "inactivity_participant", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(new ArrayDataType(u8, 3, 1), "opaque_0d", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(u32, "functional_timeout_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(u16, "upper_receive_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(u16, "lower_receive_cancel_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(u8, "addressing_kind", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(u8, "functional_response_inhibit", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(new ArrayDataType(u8, 2, 1), "opaque_0a", "Recovered field use; opaque fields remain uninterpreted.");
    layout4.add(u32, "response_capacity", "Recovered field use; opaque fields remain uninterpreted.");
    layout4.add(u16, "upper_confirmation_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout4.add(u16, "lower_transmit_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout4.add(u8, "retain_session_on_failure", "Recovered field use; opaque fields remain uninterpreted.");
    layout4.add(new ArrayDataType(u8, 3, 1), "opaque_09", "Recovered field use; opaque fields remain uninterpreted.");
    layout5.add(u16, "configured_protocol_tag", "Recovered field use; opaque fields remain uninterpreted.");
    layout5.add(u8, "opaque_02", "Recovered field use; opaque fields remain uninterpreted.");
    layout5.add(u8, "priority", "Recovered field use; opaque fields remain uninterpreted.");
    layout5.add(new PointerDataType(layout3, 4), "receive_rows", "Recovered field use; opaque fields remain uninterpreted.");
    layout5.add(new PointerDataType(layout4, 4), "transmit", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(new PointerDataType(new PointerDataType(layout5, 4), 4), "connections", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u32, "overall_timeout_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u16, "inactivity_timeout_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u16, "dispatch_delay_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u16, "p2_margin_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u16, "p2_star_margin_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u8, "published_protocol_value", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u8, "allow_lower_cancellation", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(new ArrayDataType(u8, 2, 1), "opaque_12", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(new PointerDataType(layout7, 4), "next", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(new PointerDataType(u8, 4), "data", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(u16, "length", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(new ArrayDataType(u8, 2, 1), "opaque_0a", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(u8, "disposition", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(new ArrayDataType(u8, 3, 1), "opaque_0d", "Recovered field use; opaque fields remain uninterpreted.");
    layout8.add(new PointerDataType(layout7, 4), "sentinel", "Recovered field use; opaque fields remain uninterpreted.");
    layout8.add(new PointerDataType(layout7, 4), "tail", "Recovered field use; opaque fields remain uninterpreted.");
    layout8.add(new PointerDataType(u8, 4), "copy_cursor", "Recovered field use; opaque fields remain uninterpreted.");
    layout8.add(u16, "remaining_length", "Recovered field use; opaque fields remain uninterpreted.");
    layout8.add(new ArrayDataType(u8, 2, 1), "opaque_0e", "Recovered field use; opaque fields remain uninterpreted.");
    layout8.add(u8, "notification_result", "Recovered field use; opaque fields remain uninterpreted.");
    layout8.add(u8, "pending_notification", "Recovered field use; opaque fields remain uninterpreted.");
    layout8.add(new ArrayDataType(u8, 2, 1), "opaque_12", "Recovered field use; opaque fields remain uninterpreted.");
    layout9.add(u8, "retry_kind", "Recovered field use; opaque fields remain uninterpreted.");
    layout9.add(u8, "opaque_01", "Recovered field use; opaque fields remain uninterpreted.");
    layout9.add(u16, "retry_count", "Recovered field use; opaque fields remain uninterpreted.");
    layout10.add(new PointerDataType(u8, 4), "data", "Recovered field use; opaque fields remain uninterpreted.");
    layout10.add(u32, "length", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(u32, "remaining_or_accepted_length", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(u16, "transmit_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(u16, "timeout_ticks", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(u8, "state", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(u8, "sequence_number", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(u8, "block_remaining", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(u8, "flow_control_flag", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(u8, "spacing_ticks", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(new ArrayDataType(u8, 3, 1), "opaque_0d", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(new PointerDataType(v, 4), "channel_rows", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(u16, "first_receive_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(u16, "first_transmit_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(u16, "opaque_08", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(u16, "first_canif_confirmation_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(u8, "channel_count", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(u8, "receive_count", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(u8, "transmit_count", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(u8, "opaque_0f", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(u8, "canif_confirmation_count", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(new ArrayDataType(u8, 3, 1), "opaque_11", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "opaque_00", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "channel_state_index", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u16, "transmit_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(new ArrayDataType(u8, 4, 1), "opaque_04", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u16, "upper_response_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u16, "canif_frame_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "addressing_format", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "single_frame_only", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "address_byte", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "opaque_0f", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u16, "frame_confirmation_timeout_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u16, "flow_control_timeout_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(new ArrayDataType(u8, 2, 1), "opaque_14", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "frame_capacity", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "cancel_supported", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "opaque_18", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "pad_frames_to_eight", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(new ArrayDataType(u8, 6, 1), "opaque_1a", "Recovered field use; opaque fields remain uninterpreted.");
    semanticFunction(0x91386L, "f33_dcm_reset_message_context", v)
        .setComment("Zero main message pointers, lengths, addressing, suppression, capacity, SID and selector; opaque padding is "
            + "untouched. Cancellation invokes this before operation2.");
    semanticFunction(0x911B2L, "f33_dcm_stage_negative_response", v,
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram),
        new ParameterImpl("nrc", u8, currentProgram))
        .setComment("NRC78 requests pending-response lifetime without setting final NRC5624. Other NRCs set5624 and "
            + "serialize7F/SID/NRC at5967.");
    semanticFunction(0x911DAL, "f33_dcm_select_response_disposition", v,
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Select disposition0 positive,1 negative,2 suppressed positive,3 silent negative. Exact flag26AEB=0 disallows "
            + "responses to SID bit6. Prior pending acceptance59EA bypasses suppress-positive and functional NRC "
            + "suppression, not SID-bit6 filtering.");
    semanticFunction(0x9126AL, "f33_dcm_complete_service_response", v,
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Copy remaining request length/routing to main5630, add retained prefix count to body length, then select and "
            + "stage final disposition. Does not itself mean transport confirmation.");
    semanticFunction(0x912BEL, "f33_dcm_deliver_response_notification", u32,
        new ParameterImpl("result", u8, currentProgram),
        new ParameterImpl("pending_notification", u8, currentProgram))
        .setComment("Nonzero pending flag invokes operation3 without clearing active state. Final notification runs "
            + "service/generic observers, then clears active context and NRC; it does not invoke operation3.");
    semanticFunction(0x91C0AL, "f33_dcm_dispatch_retained_receive", v,
        new ParameterImpl("receive_slot", u16, currentProgram))
        .setComment("Build routing from25EE8 and configured RX descriptors, obtain completed receive buffer and shared768-byte "
            + "response buffer, then invoke91566 admission.");
    semanticFunction(0x91C92L, "f33_dcm_run_queued_response_notification", v)
        .setComment("Consume latched queue result/pending flag. Final notification resets queue transport state and finishes "
            + "staged-session notifications before observers; pending flag preserves callback and invokes operation3.");
    semanticFunction(0x91CE2L, "f33_dcm_stage_final_response", v,
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram),
        new ParameterImpl("disposition", u8, currentProgram))
        .setComment("Only overall phase5960==2 stages a response. Use shared root5A20 and truncate total message response length "
            + "to16-bit PduInfo before933F8.");
    semanticFunction(0x920BEL, "f33_dcm_start_of_reception", u32,
        new ParameterImpl("receive_id", u16, currentProgram),
        new ParameterImpl("first_frame", new PointerDataType(F33PduInfoType, 4), currentProgram),
        new ParameterImpl("total_length", u16, currentProgram),
        new ParameterImpl("available", new PointerDataType(u16, 4), currentProgram))
        .setComment("Map receive IDs2/3/4 to slots0/1/2; check communication permission and pending abort. Zero total length "
            + "queries configured capacity only. Nonzero <=256 claims receive slot and arms watchdog0; larger returns3. "
            + "Initial data pointer is not copied here.");
    semanticFunction(0x92152L, "f33_dcm_copy_receive_data", u32,
        new ParameterImpl("receive_id", u16, currentProgram),
        new ParameterImpl("chunk", new PointerDataType(F33PduInfoType, 4), currentProgram),
        new ParameterImpl("available", new PointerDataType(u16, 4), currentProgram))
        .setComment("Require mapped active slot, communication admission and chunk length <=remaining capacity; copy into "
            + "retained receive cursor and update16-bit received/remaining lengths. Rejection releases/reset slot and may "
            + "restart inactivity.");
    semanticFunction(0x921D2L, "f33_dcm_receive_indication", v,
        new ParameterImpl("receive_id", u16, currentProgram),
        new ParameterImpl("result", u8, currentProgram))
        .setComment("Only active mapped slots participate. Success with permission arbitrates ownership; selected codes10..13 "
            + "claim pending-dispatch slot, phase2, P2/overall timers and deferred event0 scheduling via timer6. Failure "
            + "releases slot and considers S3 restart.");
    semanticFunction(0x922AAL, "f33_dcm_run_scheduled_request", v)
        .setComment("Event0 snapshots pending-dispatch slot and overall phase; phase2 installs current-dispatch slot and admits "
            + "service, otherwise resets pending receive buffer.");
    semanticFunction(0x926D2L, "f33_dcm_copy_transmit_data", u32,
        new ParameterImpl("transmit_id", u16, currentProgram),
        new ParameterImpl("chunk", new PointerDataType(F33PduInfoType, 4), currentProgram),
        new ParameterImpl("retry", new PointerDataType(layout9, 4), currentProgram),
        new ParameterImpl("available", new PointerDataType(u16, 4), currentProgram))
        .setComment("Require matching configured confirmation ID and state30/31/32/40. Copy response cursor bytes into lower "
            + "buffer, advance pointer/decrement16-bit length; retry descriptors may rewind. Rearm watchdog1. This copy is "
            + "not final confirmation.");
    semanticFunction(0x927A4L, "f33_dcm_map_response_delivery_result", u32,
        new ParameterImpl("disposition", u8, currentProgram),
        new ParameterImpl("transport_result", u8, currentProgram))
        .setComment("Positive0 maps success/failure0/1; negative1 maps2/3; suppressed positive2 always0; other dispositions "
            + "including silent3 and pending10 map2. Return is four-valued, not bool.");
    semanticFunction(0x92836L, "f33_dcm_transmit_confirmation", v,
        new ParameterImpl("transmit_id", u16, currentProgram),
        new ParameterImpl("result", u8, currentProgram))
        .setComment("Matching configured ID pops queue head, latches mapped result and explicit-pending flag. Pending30..32 "
            + "restarts pending timers and may queue29/1; final40 finalizes session/receive ownership and queues29. Actual "
            + "callback notification occurs later.");
    semanticFunction(0x9296AL, "f33_dcm_submit_transport_response", u32,
        new ParameterImpl("transmit_id", u16, currentProgram),
        new ParameterImpl("response", new PointerDataType(F33PduInfoType, 4), currentProgram),
        new ParameterImpl("disposition", u8, currentProgram))
        .setComment("Dispositions>1 except10/11 bypass lower transmission and return84. Check communication; propagate lower "
            + "refusal as81, unavailable as82, pending-inhibited as83. Zero lower return arms watchdog1; pending10 also "
            + "sets59EA. Software acceptance is not CAN transmission.");
    semanticFunction(0x92AB0L, "f33_dcm_reset_response_queue", v)
        .setComment("Initialize shared response cursor/capacity and fixed sentinel plus four response nodes: "
            + "positive0,negative1,silent3,pending10. Reset forced/explicit pending flags5965/5966; do not erase "
            + "handler-retained request copies.");
    semanticFunction(0x92C5CL, "f33_dcm_transport_watchdog_expired", v)
        .setComment("Timer1 stops processing timers. Final/queued-final states notify failure, service/pending states cancel "
            + "operation2, then release receive/session joins and reset queue. Lower cancellation is requested only in the "
            + "specified in-flight states.");
    semanticFunction(0x92E00L, "f33_dcm_try_final_response", v,
        new ParameterImpl("transmit_id", u16, currentProgram),
        new ParameterImpl("response", new PointerDataType(F33PduInfoType, 4), currentProgram),
        new ParameterImpl("disposition", u8, currentProgram))
        .setComment("Try9296A; accepted response retains queue until confirmation. Communication unavailability queues "
            + "retry2B/state21 unless forced pending forbids it. Suppression/refusal complete software ownership without "
            + "proving delivery.");
    semanticFunction(0x92F76L, "f33_dcm_try_pending_response", v,
        new ParameterImpl("transmit_id", u16, currentProgram),
        new ParameterImpl("response", new PointerDataType(F33PduInfoType, 4), currentProgram),
        new ParameterImpl("explicit_pending", u8, currentProgram))
        .setComment("Submit pending10. Explicit service request may receive operation3 after acknowledgement; automatic P2 "
            + "pending does not. Pending refusal retires node, handles session failure and timers, without fabricating a "
            + "successful network frame.");
    semanticFunction(0x93188L, "f33_dcm_append_response_node", v,
        new ParameterImpl("queue", new PointerDataType(layout8, 4), currentProgram),
        new ParameterImpl("node", new PointerDataType(layout7, 4), currentProgram))
        .setComment("Append fixed node via tail->next; update tail and clear node next. No payload copy or allocation.");
    semanticFunction(0x93198L, "f33_dcm_enqueue_pending_response", new PointerDataType(F33PduInfoType, 4),
        new ParameterImpl("service_id", u8, currentProgram))
        .setComment("Serialize7F/SID/78 at596A, append fixed pending node4, refresh cursor and return node4 descriptor. Payload "
            + "remains owned by DCM until copied/confirmed.");
    semanticFunction(0x931CEL, "f33_dcm_p2_response_deadline", v,
        new ParameterImpl("service_id", u8, currentProgram))
        .setComment("Automatic deadline sets5965=1 and sends NRC78 from state10; states23/24 first cancel old service and may "
            + "cancel lower Tx. Explicit-pending callback latch5966 is not set here.");
    semanticFunction(0x93286L, "f33_dcm_enqueue_general_reject", v,
        new ParameterImpl("service_id", u8, currentProgram))
        .setComment("Timer2 policy constructs final7F/SID/10 using fixed negative node. Preserve in-flight pending ownership via "
            + "states32/22 or submit final; do not confuse generated10 with pending78.");
    semanticFunction(0x933F8L, "f33_dcm_enqueue_final_disposition", v,
        new ParameterImpl("response", new PointerDataType(F33PduInfoType, 4), currentProgram),
        new ParameterImpl("disposition", u8, currentProgram))
        .setComment("Select fixed positive/negative/silent node. State30 appends behind in-flight pending and becomes31 without "
            + "another lower submit. Active10/11/20 submit final40; cancellation states use separate software completion "
            + "joins.");
    semanticFunction(0x93538L, "f33_dcm_request_explicit_pending_response", v,
        new ParameterImpl("service_id", u8, currentProgram))
        .setComment("Explicit NRC78 in state10 cancels timer4, sets5965/5966 and submits pending30; state11 queues pending20 "
            + "until timer3; state30 coalesces by setting notification latch only.");
    semanticFunction(0x936E6L, "f33_dcm_compare_protocol_priority", u32,
        new ParameterImpl("candidate_slot", u16, currentProgram),
        new ParameterImpl("owner_slot", u16, currentProgram))
        .setComment("Compare configured protocol priority bytes:2 candidate numerically lower/higher priority,1 equal,0 candidate "
            + "numerically greater. Return is ternary, not bool.");
    semanticFunction(0x9373AL, "f33_dcm_claim_receive_slot", u32,
        new ParameterImpl("receive_slot", u16, currentProgram))
        .setComment("Use overall phase, protocol identity and existing receive owner to accept/reset slot; pause S3 for admitted "
            + "active-session receive. Mark receive-in-progress separately from service/dispatch ownership.");
    semanticFunction(0x93978L, "f33_dcm_arbitrate_completed_receive", u32,
        new ParameterImpl("receive_slot", u16, currentProgram))
        .setComment("Functional exact3E80 during active-session phase1 takes receive shortcut. Otherwise arbitrate candidate "
            + "against pending owner, cancel/release displaced reception or queue service-cancellation event28 for "
            + "higher-priority protocol.");
    semanticFunction(0x93B50L, "f33_dcm_get_overall_request_timeout", u32)
        .setComment("Return configured protocol timeout or selected functional override, and publish zero-time flag59EC. Real R10 "
            + "return is used by timer2 admission; not void.");
    semanticFunction(0x93BD6L, "f33_dcm_select_response_deadline", u16,
        new ParameterImpl("use_retained", u8, currentProgram),
        new ParameterImpl("use_current_session", u8, currentProgram))
        .setComment("Fresh selection reads session raw timings and subtracts protocol margins with floor0; retains P2star at59D8 "
            + "and pending spacing at59DA. Return initial raw P2 or retained P2star.");
    semanticFunction(0x93DE8L, "f33_dcm_append_receive_chunk", u32,
        new ParameterImpl("receive_slot", u16, currentProgram),
        new ParameterImpl("chunk", new PointerDataType(F33PduInfoType, 4), currentProgram),
        new ParameterImpl("available", new PointerDataType(u16, 4), currentProgram))
        .setComment("Copy exactly16-bit chunk length into slot cursor, add received and subtract remaining16-bit lengths. "
            + "Caller92152 owns capacity check.");
    semanticFunction(0x93E3EL, "f33_dcm_count_receiving_slots", u16)
        .setComment("Count three59F0-stride10 slot receive-active bytes equal1. Real R10 result is consumed by release and "
            + "inactivity decisions; not void.");
    semanticFunction(0x95626L, "f33_dcm_report_negative_or_pending", v,
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram),
        new ParameterImpl("nrc", u8, currentProgram))
        .setComment("Stage NRC;78 leaves service pending and does not finalize message. Other NRCs complete "
            + "through9126A/disposition queue.");
    semanticFunction(0x95644L, "f33_dcm_report_positive_response", v,
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Forward handler-retained body length/routing through9126A. This is response readiness, not delivery.");
    semanticFunction(0x79DBEL, "f33_pdur_cantp_transmit_adapter", u32,
        new ParameterImpl("transmit_id", u16, currentProgram),
        new ParameterImpl("response", new PointerDataType(F33PduInfoType, 4), currentProgram))
        .setComment("Forward to7A376; only descriptor16-bit length is consumed by CanTp admission. Payload remains at upper "
            + "owner.");
    semanticFunction(0x7A376L, "f33_cantp_transmit_descriptor", u32,
        new ParameterImpl("transmit_id", u16, currentProgram),
        new ParameterImpl("response", new PointerDataType(F33PduInfoType, 4), currentProgram))
        .setComment("Read response length at+4 and pass to7A334; propagate real R10 result. Does not copy payload.");
    semanticFunction(0x7A728L, "f33_cantp_find_transmit_connection", new PointerDataType(layout13, 4),
        new ParameterImpl("configuration", new PointerDataType(layout12, 4), currentProgram),
        new ParameterImpl("transmit_id", u16, currentProgram))
        .setComment("Range-check namespaced ID then scan configured channel Tx rows by+2 ID; return matching pointer or null. "
            + "Exact instructions preserve R10=0 until match.");
    semanticFunction(0x7B3D0L, "f33_cantp_accept_transmit_length", u32,
        new ParameterImpl("configuration", new PointerDataType(layout12, 4), currentProgram),
        new ParameterImpl("transmit_id", u16, currentProgram),
        new ParameterImpl("length", u32, currentProgram))
        .setComment("Require1..4095, configured connection, idleE1 and half-duplex peer qualification. Store TxID,length and "
            + "stateD2 in0x20-byte channel stride;0 means accepted length only, not copied or emitted.");
    semanticFunction(0x7B540L, "f33_cantp_copy_upper_transmit_bytes", u32,
        new ParameterImpl("upper_id", u16, currentProgram),
        new ParameterImpl("chunk", new PointerDataType(layout10, 4), currentProgram),
        new ParameterImpl("remaining", new PointerDataType(u32, 4), currentProgram))
        .setComment("Build16-bit PduInfo and call PduR81A66 with null retry; return actual copy result and zero-extended "
            + "remaining count. DCM926D2 owns cursor.");
    semanticFunction(0x7B20CL, "f33_cantp_submit_can_frame", u32,
        new ParameterImpl("canif_id", u16, currentProgram),
        new ParameterImpl("frame", new PointerDataType(layout10, 4), currentProgram))
        .setComment("Build F33PduInfo, run exact no-op81FFA then existing CanIf7FEF8 snapshot/enqueue.0 means software lower "
            + "acceptance only; driver/controller and physical network remain separate.");
    semanticFunction(0x7B894L, "f33_cantp_run_transmit_channels", v)
        .setComment("Scheduled task resolves acceptedD2 to single/first-frame construction, obtains upper bytes, submits CanIf "
            + "frame and advances segmented transport states. Timeout paths clear channel and report upper failure.");
    semanticFunction(0x7BB0EL, "f33_cantp_handle_frame_confirmation", v,
        new ParameterImpl("connection", new PointerDataType(layout13, 4), currentProgram))
        .setComment("CanIf software confirmation advances single/multi-frame state. Only completed aggregate transport clears "
            + "channel and reports upper result0; intermediate frames may wait for flow-control or spacing.");
    semanticData(0x25EE8L, new ArrayDataType(resolve(layout0), 3, 12), "f33_dcm_receive_route",
        "93B32/93CCE field loads 25EE8..25F0B exact little-endian bytes");
    semanticData(0x25E90L, new ArrayDataType(resolve(layout1), 3, 8), "f33_dcm_receive_buffer_configuration",
        "920BE capacity check 93C6C/93C9A/93E5C configured buffer references");
    semanticData(0xFEBE59F0L, new ArrayDataType(resolve(layout2), 3, 16), "f33_dcm_receive_buffer_state",
        "93DE8 copies and arithmetic 93C9A clears receiving/participant, not abort_pending 93EF6 writes abort_pending "
            + "93F66 queues inactive-slot cancellation then marks abort_pending");
    semanticData(0x25EA8L, resolve(layout3), "f33_dcm_receive_descriptor_0",
        "91C0A,91B84,93D2E,93D9A,93B50,9238C exact field use");
    semanticData(0x25EB4L, resolve(layout3), "f33_dcm_receive_descriptor_1",
        "91C0A,91B84,93D2E,93D9A,93B50,9238C exact field use");
    semanticData(0x25F24L, resolve(layout3), "f33_dcm_receive_descriptor_2",
        "91C0A,91B84,93D2E,93D9A,93B50,9238C exact field use");
    semanticData(0x25F0CL, resolve(layout4), "f33_dcm_transmit_descriptor_0",
        "93CE6 capacity 93E82 lower Tx ID 93EBC confirmation ID 92B66 configured failure gate");
    semanticData(0x25F18L, resolve(layout4), "f33_dcm_transmit_descriptor_1",
        "93CE6 capacity 93E82 lower Tx ID 93EBC confirmation ID 92B66 configured failure gate");
    semanticData(0x25F30L, resolve(layout5), "f33_dcm_connection_0",
        "91C0A,936E6,95B88 Protocol tags are not promoted to physical CAN IDs from this structure alone.");
    semanticData(0x25F3CL, resolve(layout5), "f33_dcm_connection_1",
        "91C0A,936E6,95B88 Protocol tags are not promoted to physical CAN IDs from this structure alone.");
    semanticData(0x25EC0L, new ArrayDataType(resolve(layout6), 2, 20), "f33_dcm_protocol_configuration",
        "93B18,93B50,93BD6,921D2,92A1E,937B0 exact field use");
    semanticData(0xFEBE5984L, new ArrayDataType(resolve(layout7), 5, 16), "f33_dcm_response_node",
        "92AB0 initialization 9317A index*16 93188/92B98 append/pop 933F8 node selection 93696 retirement");
    semanticData(0xFEBE5970L, resolve(layout8), "f33_dcm_response_queue",
        "92AB0,92A74,92BD8,926D2,936CA");
    semanticData(0xFEBE4F40L, resolve(layout11), "f33_cantp_tx_state_prefix_0",
        "7B3D0 admission 7B452 reset 7B74E segmented copy 7BB0E confirmation Only prefix of0x20-byte channel storage; "
            + "Rx peer state starts+0x10 and is not given a full new type here.");
    semanticData(0xFEBE4F60L, resolve(layout11), "f33_cantp_tx_state_prefix_1",
        "7B3D0 admission 7B452 reset 7B74E segmented copy 7BB0E confirmation Only prefix of0x20-byte channel storage; "
            + "Rx peer state starts+0x10 and is not given a full new type here.");
    semanticData(0xFEBE4F80L, resolve(layout11), "f33_cantp_tx_state_prefix_2",
        "7B3D0 admission 7B452 reset 7B74E segmented copy 7BB0E confirmation Only prefix of0x20-byte channel storage; "
            + "Rx peer state starts+0x10 and is not given a full new type here.");
    semanticData(0x22C70L, resolve(layout12), "f33_cantp_configuration",
        "7A334/7A728/7A67E exact offsets and22C70 bytes");
    semanticData(0x22B9EL, resolve(layout13), "f33_cantp_tx_connection_0",
        "7A728 selects by+2 7B3D0 state_index+1 and single-frame-only+13 7B596/7B64E/7B74E "
            + "upper+8,CanIf+10,capacity+22,padding+25 7B47E cancellation flag+23 Both exact configured rows use zero "
            + "addressing-format overhead.");
    semanticData(0x22BBEL, resolve(layout13), "f33_cantp_tx_connection_1",
        "7A728 selects by+2 7B3D0 state_index+1 and single-frame-only+13 7B596/7B64E/7B74E "
            + "upper+8,CanIf+10,capacity+22,padding+25 7B47E cancellation flag+23 Both exact configured rows use zero "
            + "addressing-format overhead.");
    semanticData(0xFEBE5624L, u8, "f33_dcm_final_nrc",
        "0 positive; final NRC otherwise. Explicit78 uses596A and does not set this byte.");
    semanticData(0xFEBE5960L, u8, "f33_dcm_request_phase",
        "0 default/idle;1 nondefault-session inactivity lifetime;2 active dispatch/request. Independent of response "
            + "transport state5964.");
    semanticData(0xFEBE5964L, u8, "f33_dcm_response_transport_state",
        "Opaque numeric enum documented in grouped state map, not a physical CAN state.");
    semanticData(0xFEBE5965L, u8, "f33_dcm_forced_pending_deadline",
        "P2/explicit pending and retry policy latch, cleared by queue reset.");
    semanticData(0xFEBE5966L, u8, "f33_dcm_explicit_pending_notification",
        "Service-requested78 requires eventual operation3; automatic78 does not.");
    semanticData(0xFEBE5967L, new ArrayDataType(u8, 3, 1), "f33_dcm_final_negative_response",
        "7F originalSID NRC; separate from pending buffer.");
    semanticData(0xFEBE596AL, new ArrayDataType(u8, 3, 1), "f33_dcm_pending_negative_response",
        "7F originalSID78, independently transport-owned.");
    semanticData(0xFEBE59D8L, u16, "f33_dcm_retained_p2_star_raw",
        "Selected transport timingB minus protocol margin; raw3500 in exact configured sessions.");
    semanticData(0xFEBE59DAL, u16, "f33_dcm_pending_spacing_raw",
        "Selected timingC raw2000; timer3.");
    semanticData(0xFEBE59E0L, u16, "f33_dcm_pending_dispatch_receive_slot",
        "Selected receive completion owner used by event0 and timer admission.");
    semanticData(0xFEBE59E2L, u16, "f33_dcm_current_dispatch_receive_slot",
        "Current service route; not necessarily still receiving bytes.");
    semanticData(0xFEBE59E8L, u16, "f33_dcm_displaced_transmit_id",
        "Saved lower Tx cancellation target during preemption.");
    semanticData(0xFEBE59EAL, u8, "f33_dcm_pending_transport_accepted",
        "Set only after lower acceptance of pending10, overrides some later suppression gates; reset on receive/queue "
            + "release joins.");
    semanticData(0xFEBE59EBL, u8, "f33_dcm_zero_p2_deadline",
        "Zero selected P2 raw value flag.");
    semanticData(0xFEBE59ECL, u8, "f33_dcm_zero_overall_timeout",
        "Zero overall timeout flag; timer2 may resolve SID from pending receive buffer before dispatch.");
    semanticData(0xFEBE5A20L, new ArrayDataType(u8, 768, 1), "f33_dcm_shared_response_buffer",
        "Single shared protocol-independent response store; queue nodes/copy cursors hold references, not copies.");
  }

  private void annotateDiagnosticReadPublication() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType F33DcmMessageContextType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33DcmMessageContext");
    StructureDataType layout0 = new StructureDataType(category, "F33DidPublicationMetadata", 0);
    layout0.setPackingEnabled(true);
    StructureDataType layout1 = new StructureDataType(category, "F33DcmDidClass", 0);
    layout1.setPackingEnabled(true);
    StructureDataType layout2 = new StructureDataType(category, "F33DiagSourceBuffer", 0);
    layout2.setPackingEnabled(true);
    StructureDataType layout3 = new StructureDataType(category, "F33DiagOutputView", 0);
    layout3.setPackingEnabled(true);
    StructureDataType layout4 = new StructureDataType(category, "F33DtcTuple", 0);
    layout4.setPackingEnabled(true);
    StructureDataType layout5 = new StructureDataType(category, "F33SnapshotIdentifierTuple", 0);
    layout5.setPackingEnabled(true);
    StructureDataType layout6 = new StructureDataType(category, "F33CaptureFieldDescriptor", 0);
    layout6.setPackingEnabled(true);
    StructureDataType layout7 = new StructureDataType(category, "F33DiagProprietaryMessage", 0);
    layout7.setPackingEnabled(true);
    FunctionDefinitionDataType F33DidPayloadReader = new FunctionDefinitionDataType(category, "F33DidPayloadReader");
    F33DidPayloadReader.setReturnType(u32);
    F33DidPayloadReader.setArguments(new ParameterDefinitionImpl("output", new PointerDataType(u8, 4), null),
        new ParameterDefinitionImpl("length", u16, null));
    FunctionDefinitionDataType F33DiagnosticAvailability = new FunctionDefinitionDataType(category, "F33DiagnosticAvailability");
    F33DiagnosticAvailability.setReturnType(u32);
    FunctionDefinitionDataType F33DidClassPresence = new FunctionDefinitionDataType(category, "F33DidClassPresence");
    F33DidClassPresence.setReturnType(u32);
    F33DidClassPresence.setArguments(new ParameterDefinitionImpl("did", u16, null),
        new ParameterDefinitionImpl("operation", u8, null),
        new ParameterDefinitionImpl("absent", new PointerDataType(u8, 4), null));
    FunctionDefinitionDataType F33DidClassLength = new FunctionDefinitionDataType(category, "F33DidClassLength");
    F33DidClassLength.setReturnType(u32);
    F33DidClassLength.setArguments(new ParameterDefinitionImpl("did", u16, null),
        new ParameterDefinitionImpl("operation", u8, null),
        new ParameterDefinitionImpl("length", new PointerDataType(u16, 4), null));
    FunctionDefinitionDataType F33DidClassRead = new FunctionDefinitionDataType(category, "F33DidClassRead");
    F33DidClassRead.setReturnType(u32);
    F33DidClassRead.setArguments(new ParameterDefinitionImpl("did", u16, null),
        new ParameterDefinitionImpl("output", new PointerDataType(u8, 4), null),
        new ParameterDefinitionImpl("operation", u8, null),
        new ParameterDefinitionImpl("length", new PointerDataType(u16, 4), null),
        new ParameterDefinitionImpl("nrc", new PointerDataType(u8, 4), null));
    FunctionDefinitionDataType F33DidClassWrite = new FunctionDefinitionDataType(category, "F33DidClassWrite");
    F33DidClassWrite.setReturnType(u32);
    F33DidClassWrite.setArguments(new ParameterDefinitionImpl("did", u16, null),
        new ParameterDefinitionImpl("payload", new PointerDataType(u8, 4), null),
        new ParameterDefinitionImpl("operation", u8, null),
        new ParameterDefinitionImpl("length", u16, null),
        new ParameterDefinitionImpl("nrc", new PointerDataType(u8, 4), null));
    FunctionDefinitionDataType F33CaptureFieldSerializer = new FunctionDefinitionDataType(category, "F33CaptureFieldSerializer");
    F33CaptureFieldSerializer.setReturnType(v);
    F33CaptureFieldSerializer.setArguments(new ParameterDefinitionImpl("view", u8, null),
        new ParameterDefinitionImpl("output", new PointerDataType(u8, 4), null));
    layout0.add(u16, "did", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(u16, "payload_length", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(new PointerDataType(F33DidPayloadReader, 4), "reader", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(new PointerDataType(F33DiagnosticAvailability, 4), "available", "Null admits; otherwise exact5A");
    layout0.add(u8, "route_kind", "Only kind0 selected by4D36E");
    layout0.add(new ArrayDataType(u8, 3, 1), "opaque_0d", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(new PointerDataType(F33DidClassPresence, 4), "presence", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(new PointerDataType(F33DidClassLength, 4), "length", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(new PointerDataType(F33DidClassRead, 4), "read", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(new PointerDataType(F33DidClassWrite, 4), "write", "Reuse existing write callback ABI; not an untyped request-derived target");
    layout1.add(new PointerDataType(v, 4), "policy", "Fixed class access-policy object");
    layout1.add(u16, "first_did", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(u16, "last_did", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(u8, "probe_presence", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(new ArrayDataType(u8, 3, 1), "opaque_19", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(u8, "status", "Status namespace differs by operation; not a universal success Boolean");
    layout2.add(u8, "detail", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(u16, "length", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(new PointerDataType(u8, 4), "bytes", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(new PointerDataType(u8, 4), "bytes", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(new PointerDataType(u16, 4), "length", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(new PointerDataType(u16, 4), "capacity", "Recovered field use; opaque fields remain uninterpreted.");
    layout4.add(new ArrayDataType(u8, 3, 1), "dtc_msb_first", "Recovered field use; opaque fields remain uninterpreted.");
    layout4.add(u8, "status", "Recovered field use; opaque fields remain uninterpreted.");
    layout5.add(new ArrayDataType(u8, 3, 1), "dtc_msb_first", "Recovered field use; opaque fields remain uninterpreted.");
    layout5.add(u8, "record_number", "1 or10, not DTC status");
    layout6.add(u16, "identifier", "Capture field namespace; do not equate to RDBI DID");
    layout6.add(u8, "exclude_secondary_view", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u8, "opaque_03", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(new PointerDataType(F33CaptureFieldSerializer, 4), "serialize_capture", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u32, "opaque_08", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(new PointerDataType(v, 4), "serialize_event_data", "Separate selector3/event format callback");
    layout6.add(new PointerDataType(F33DiagnosticAvailability, 4), "available", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u16, "opaque_14", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u8, "payload_length", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u8, "opaque_17", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(new PointerDataType(u8, 4), "request", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(u32, "request_length", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(new PointerDataType(u8, 4), "response", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(u32, "response_length", "Recovered field use; opaque fields remain uninterpreted.");
    semanticFunction(0x962F2L, "f33_dcm_read_did_service", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Operation0 admits configured SID22;2 cancels retained read continuation. Other operations return0. Message "
            + "snapshot, read preparation and serialization are separate from response delivery.");
    semanticFunction(0x961DCL, "f33_dcm_begin_read_did_request", u32,
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Copy28-byte advanced message to5D84. Reject remaining length<2, odd, or more than one DID with13. Reset "
            + "cursors and preflight output length before invoking payload readers.");
    semanticFunction(0x9613CL, "f33_dcm_preflight_read_did_body", u32,
        new ParameterImpl("operation", u8, currentProgram))
        .setComment("Resolve/precondition one configured DID and add payload length plus two DID bytes. Reject expected "
            + "body>min(capacity,65534) with14 before positive-body serialization. Generic loop does not expand configured "
            + "admission beyond one DID.");
    semanticFunction(0x95FB4L, "f33_dcm_serialize_read_did_body", u32,
        new ParameterImpl("operation", u8, currentProgram))
        .setComment("Echo admitted DID then invoke fixed class reader into retained response. Advance body by reported u16 "
            + "length, enforce post-read cap and submit only at completed cursor. Pending/iteration events are generic "
            + "machinery, not configured multi-DID support.");
    semanticFunction(0x95EDCL, "f33_dcm_resolve_read_did_route", u32)
        .setComment("Dynamic DID bank count0 selects static class ranges. Require read capability; retain class index5D78 and "
            + "route kind5D7A. Class membership alone does not prove available metadata.");
    semanticFunction(0x95DCCL, "f33_dcm_check_read_did_policy_and_length", u32)
        .setComment("Read current session/security snapshots, apply class policy, then fixed local callback and length callback. "
            + "Session rejection31 and security33 are distinct from metadata absence31 and whole-body capacity14.");
    semanticFunction(0x8B464L, "f33_did_read_application_adapter", u32,
        new ParameterImpl("output", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("length", new PointerDataType(u16, 4), currentProgram),
        new ParameterImpl("nrc", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("did", u16, currentProgram))
        .setComment("Retain metadata-selected payload length and choose local kind0 serializer or kind1 side route. Direct "
            + "metadata reader returns application status, mapped through8B41A. Pending state3B26..2B is adapter state, not "
            + "source-sampling atomicity.");
    semanticFunction(0x4D802L, "f33_read_selected_did_payload", u32,
        new ParameterImpl("output", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("length", u16, currentProgram))
        .setComment("Use selected metadata index81B8 and invoke fixed record+4 reader; out-of-range returns3. Length and "
            + "availability selection are separate operations.");
    semanticFunction(0x4D836L, "f33_get_did_metadata_route_kind", u8,
        new ParameterImpl("did", u16, currentProgram))
        .setComment("Scan all242 metadata records and return matching record kind orFF. Kind is a route discriminator, not an "
            + "arbitrary memory-access class.");
    semanticFunction(0x4D278L, "f33_serialize_available_did_bitmap", v,
        new ParameterImpl("did_page", u16, currentProgram),
        new ParameterImpl("output", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("length", u16, currentProgram))
        .setComment("Clear output then set MSB-first bits for kind0 metadata strictly above page base and below base+256, with "
            + "null/5A availability callback. Bitmap is generated from current availability, not a cached guarantee that a "
            + "later read succeeds.");
    semanticFunction(0x8C2E0L, "f33_dcm_clear_diagnostic_service", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Clear service operation callback. Retain advanced message for operation0; nonzero operations reset/cancel "
            + "module state. Response submission is not acknowledgement or durable completion.");
    semanticFunction(0x8C69AL, "f33_dcm_read_dtc_count_service", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("DTC count operation callback. Retain advanced message for operation0; nonzero operations reset/cancel module "
            + "state. Response submission is not acknowledgement or durable completion.");
    semanticFunction(0x8CB1AL, "f33_dcm_read_dtc_list_service", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("DTC list operation callback. Retain advanced message for operation0; nonzero operations reset/cancel module "
            + "state. Response submission is not acknowledgement or durable completion.");
    semanticFunction(0x8CE84L, "f33_dcm_read_snapshot_identifiers_service", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Snapshot identifiers operation callback. Retain advanced message for operation0; nonzero operations "
            + "reset/cancel module state. Response submission is not acknowledgement or durable completion.");
    semanticFunction(0x8D416L, "f33_dcm_read_snapshot_by_dtc_service", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Snapshot records operation callback. Retain advanced message for operation0; nonzero operations reset/cancel "
            + "module state. Response submission is not acknowledgement or durable completion. Exact capacity4 path "
            + "reaches95626 with NRC0 and consequently submits a positive header-only response through CanTp length "
            + "acceptance; not NRC14 or a transmitted negative response.");
    semanticFunction(0x8C234L, "f33_dcm_begin_clear_diagnostic_request", u32,
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Require exactly3 remaining bytes, assemble big-endian24 group and retain message3BD4. Application validation "
            + "accepts onlyFFFFFF; accepted group enters existing asynchronous clear owner1410.");
    semanticFunction(0x4D682L, "f33_validate_clear_all_diagnostic_group", u32,
        new ParameterImpl("group", u32, currentProgram))
        .setComment("Return0 only for24-bit groupFFFFFF; other groups return1. No configured per-DTC selective-clear API is "
            + "implied.");
    semanticFunction(0x4D690L, "f33_get_dtc_status_availability_mask", u32,
        new ParameterImpl("mask", new PointerDataType(u8, 4), currentProgram))
        .setComment("StoreB9 and return0. Status availability is not event-history bitmap layout.");
    semanticFunction(0x4D69CL, "f33_begin_filtered_dtc_iteration", u32,
        new ParameterImpl("mask", u8, currentProgram))
        .setComment("Retain mask&B9 at8198 and reset u16 result count81B4 and cursor81B6. Actual derived-status snapshot is "
            + "deferred until first527D6 scan.");
    semanticFunction(0x4D6D4L, "f33_next_filtered_dtc", u32,
        new ParameterImpl("dtc", new PointerDataType(u32, 4), currentProgram),
        new ParameterImpl("status", new PointerDataType(u8, 4), currentProgram))
        .setComment("Advance through snapshot status5F87 and DTC catalogue30850. Return0 for next matching tuple,1 for "
            + "exhausted/invalid; retain cursor and limit successful results to1023. DTC index is not event number.");
    semanticFunction(0x527D6L, "f33_scan_dtc_status_snapshot", u32,
        new ParameterImpl("mask", u8, currentProgram),
        new ParameterImpl("dtc", new PointerDataType(u32, 4), currentProgram),
        new ParameterImpl("status", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("start_index", u16, currentProgram))
        .setComment("Starting index1 refreshes160 status bytes at5F87 from derived DTC banks and healthy-observed events, then "
            + "scans configured nonzero DTCs. Later cursor reads use that status generation rather than rebuilding each "
            + "item.");
    semanticFunction(0x5261AL, "f33_build_dtc_status_snapshot", v,
        new ParameterImpl("status", new PointerDataType(u8, 4), currentProgram))
        .setComment("For configured DTC indices synthesize bit0 from602C,28 from6040 and80 from6054. Add10 when an associated "
            + "event lacks6120 healthy observation and retained bit3 is clear. These are derived DTC generations, not raw "
            + "event bitmaps.");
    semanticFunction(0x51FD2L, "f33_rebuild_derived_diagnostic_banks", v,
        new ParameterImpl("generation_selector", u8, currentProgram))
        .setComment("A5 maps current6090 into602C and classifier-qualified6054; other selector maps retained60C0 into6040. Map "
            + "descriptors only for event1..17F, nonzero DTC index<160 and flagbit6. Rebuild auxiliary banks "
            + "separately;6054 is not60F0.");
    semanticFunction(0x8C7F2L, "f33_append_dtc_tuple_if_fits", u32,
        new ParameterImpl("tuple", new PointerDataType(u8, 4), currentProgram))
        .setComment("Append exactly4 bytes only with nonnull response and unsigned remaining capacity>3. Failure returns1 without "
            + "partial tuple; caller merge continues, allowing a complete-tuple prefix rather than NRC14.");
    semanticFunction(0x8C858L, "f33_merge_dtc_list_sources", u32,
        new ParameterImpl("local", new PointerDataType(layout2, 4), currentProgram),
        new ParameterImpl("side", new PointerDataType(layout2, 4), currentProgram))
        .setComment("Merge ascending24-bit DTC tuples; deduplicate equal DTCs, OR statuses and clear bit10 when combined "
            + "status&29 is nonzero. Appends are bounded per tuple; omitted trailing tuples do not force whole-response "
            + "failure.");
    semanticFunction(0x8CC14L, "f33_merge_snapshot_identifier_sources", u32,
        new ParameterImpl("local", new PointerDataType(layout2, 4), currentProgram),
        new ParameterImpl("side", new PointerDataType(layout2, 4), currentProgram),
        new ParameterImpl("output", new PointerDataType(layout3, 4), currentProgram))
        .setComment("Copy each nonempty source only if its whole length fits u16 capacity. Compare first24-bit DTCs to avoid "
            + "duplicate second source; do not merge snapshot record numbers or publish partial source bytes.");
    semanticFunction(0x5310EL, "f33_get_secondary_capture_record_mask", u32,
        new ParameterImpl("dtc", new PointerDataType(u32, 4), currentProgram))
        .setComment("For occupied capture slot1 require duplicate events to map to same nonzero packed DTC, then return mask3 for "
            + "available record numbers1 and10. Event duplicates are not complements.");
    semanticFunction(0x4D72CL, "f33_next_snapshot_identifier_tuple", u32,
        new ParameterImpl("dtc", new PointerDataType(u32, 4), currentProgram),
        new ParameterImpl("record_number", new PointerDataType(u8, 4), currentProgram))
        .setComment("Retain slot1 DTC at81C4 and record mask8199; emit record1 then10, then clear cached pair on exhaustion. "
            + "Record numbers are not DTC status bytes.");
    semanticFunction(0x531E0L, "f33_serialize_retained_capture_record", s32,
        new ParameterImpl("record_view", u8, currentProgram),
        new ParameterImpl("output", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("capacity", u16, currentProgram))
        .setComment("Views0/1 serialize record numbers1/10 from configured75-field table2A364, with field gate and view "
            + "exclusion. Emit record number/count then identifier/length/payload. Return-1 on capacity crossing; payload "
            + "callbacks choose retained sources, not a new physical sample.");
    semanticFunction(0x8DDCCL, "f33_dcm_enable_dtc_setting_service", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Operation0 forwards fixed selection1 and requires zero remaining bytes; other operations reset module "
            + "continuation. Application action clears8197, not stored diagnostic histories.");
    semanticFunction(0x8DDEAL, "f33_dcm_disable_dtc_setting_service", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Operation0 forwards fixed selection2 and requires zero remaining bytes; other operations reset continuation. "
            + "Application action requests8197=5A; grouped status propagation occurs later.");
    semanticFunction(0x50904L, "f33_publish_dtc_setting_request", v,
        new ParameterImpl("selection", u8, currentProgram))
        .setComment("Store8197=5A only for selection2, otherwise0. Does not clear events, captures, classifiers or control "
            + "actions; later49E22 and58074 publish consequences.");
    semanticFunction(0x965C0L, "f33_dcm_read_memory_service", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Operation0 validates configured ALFID15 and bounded memory family;2 cancels adapter state;3 enters "
            + "configured continuation path. No memory write or indirect executable dispatch.");
    semanticFunction(0x4FC8EL, "f33_read_configured_application_memory", u32,
        new ParameterImpl("address_record", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("output", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("length", u16, currentProgram))
        .setComment("Require1..255 bytes. Memory family1 copies allowed local-RAM bytes after five overlap exclusions; family2 "
            + "uses bounded DataFlash read after two exclusions. Other family/range returns3, bad length/read failure4.");
    semanticFunction(0x9862EL, "f33_dcm_begin_proprietary_event_read", u32,
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram),
        new ParameterImpl("selector", u8, currentProgram))
        .setComment("Selector1 requires0 request bytes;2 requires2-byte event ID;3 requires event ID plus2-byte subselector. "
            + "Retain message5E34, echo event ID for2/3, then fixed catalogue selection and output merge. Not generic "
            + "arbitrary memory access.");
    semanticFunction(0x8DE98L, "f33_begin_proprietary_event_selection", u32,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("selector", u8, currentProgram),
        new ParameterImpl("event_id", u16, currentProgram),
        new ParameterImpl("subselector", u16, currentProgram))
        .setComment("Retain bounded selector/IDs at45D0/45D2/45DC and publish selection through50916. IDs index event data "
            + "catalogue, not callback addresses.");
    semanticFunction(0x50922L, "f33_serialize_selected_proprietary_event", u32,
        new ParameterImpl("output", new PointerDataType(u8, 4), currentProgram),
        new ParameterImpl("length", new PointerDataType(u16, 4), currentProgram))
        .setComment("Selector1 formats enabled IDs,2 event data,3 selected event record. Bounded catalogue2AB70 has51 populated "
            + "IDs in64 slots. Map signed helper errors-4/-1 to4/6, otherwise10; do not assign OEM names from ID/type.");
    semanticFunction(0x4D3BEL, "f33_did_available_4d3be", u32)
        .setComment("0x5A when expression holds; otherwise 0 for u32[FEBEE91C] == 0xAA5555AA. BF3AA: FEBEB314 -> FEBEE91C.");
    semanticFunction(0x4D3D6L, "f33_did_available_4d3d6", u32)
        .setComment("0x5A when expression holds; otherwise 0 for u8[FEBEE802] == 0x5A. BF3AA: FEBEBE9C -> FEBEE802.");
    semanticFunction(0x4D3E4L, "f33_did_available_4d3e4", u32)
        .setComment("0x5A when expression holds; otherwise 0 for u8[FEBEE804] == 0x5A. BF3AA: FEBEBE9A -> FEBEE804.");
    semanticFunction(0x4D3F2L, "f33_did_available_4d3f2", u32)
        .setComment("0x5A when expression holds; otherwise 0 for u8[FEBEE803] == 0x5A. BF3AA: FEBEBE99 -> FEBEE803.");
    semanticFunction(0x4D400L, "f33_did_available_4d400", u32)
        .setComment("0x5A when expression holds; otherwise 0 for u8[FEBEE870] != 0x5A. BF3AA: FEBEBE9D -> FEBEE870.");
    semanticFunction(0x4D412L, "f33_did_available_4d412", u32)
        .setComment("0x5A when expression holds; otherwise 0 for u8[FEBEE870] == 0x5A. BF3AA: FEBEBE9D -> FEBEE870.");
    semanticFunction(0x4D420L, "f33_did_available_4d420", u32)
        .setComment("0x5A when expression holds; otherwise 0 for u8[FEBEE805] == 0x5A. BF3AA: FEBEBE9F -> FEBEE805.");
    semanticFunction(0x4D42EL, "f33_did_available_4d42e", u32)
        .setComment("0x5A when expression holds; otherwise 0 for u8[FEBEE806] == 0x5A. BF3AA: FEBEBEA0 -> FEBEE806.");
    semanticFunction(0x8C448L, "f33_count_merged_dtc_sources", u32,
        new ParameterImpl("local", new PointerDataType(layout2, 4), currentProgram),
        new ParameterImpl("side", new PointerDataType(layout2, 4), currentProgram))
        .setComment("Walk ascending24-bit DTC tuples, counting one for equal IDs and one for each unmatched ID. Count accumulates "
            + "inR6 with16-bit wrapping and is passed directly to8C422; return0. Missing count in C is an ABI/dataflow "
            + "defect, not a constant zero result.");
    semanticFunction(0x8C422L, "f33_append_dtc_count", v,
        new ParameterImpl("count", u16, currentProgram))
        .setComment("Append big-endian16-bit count and increment body length by2. Caller19/01 only tests capacity!=0 before "
            + "writing its4-byte body; shared transport allocation is larger but this is not a general4-byte "
            + "caller-capacity guard.");
    semanticFunction(0x8C3A8L, "f33_begin_dtc_count_iteration", u32,
        new ParameterImpl("mask", u8, currentProgram))
        .setComment("Forward status mask to4D69C and retain unmasked byte3BF5. Preserve returnedR10 through final store/dispose; "
            + "caller8C66A checks it.");
    semanticFunction(0x8C214L, "f33_dcm_join_clear_diagnostic_phases", u32,
        new ParameterImpl("group", u32, currentProgram),
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Preserve group/message, call8C018(message,group), and on success8C104(message,group). Return "
            + "consequentialR10 from last phase without manufacturing success;8C2A8 retains it.");
    semanticFunction(0x4D520L, "f33_begin_proprietary_operation", u8,
        new ParameterImpl("operation", u8, currentProgram),
        new ParameterImpl("message", new PointerDataType(layout7, 4), currentProgram),
        new ParameterImpl("selected_index", new PointerDataType(u8, 4), currentProgram))
        .setComment("Operation0 passes request byte count, request pointer, response+1 and selected-index pointer to34DD4. Retain "
            + "message81C8 and BA10/BA00 owner, then return4D4F2 status inR10. Nonzero operation follows notification "
            + "branch. Not void.");
    semanticFunction(0x4D560L, "f33_finish_proprietary_operation", u8,
        new ParameterImpl("selected_index", u8, currentProgram),
        new ParameterImpl("response_length", new PointerDataType(u32, 4), currentProgram))
        .setComment("Invoke fixed finish callback34E66(index,length), update BA10/BA00 owner, and return translated4D4F2 status "
            + "inR10. Both second argument and result are consumed by8E2DE; not a void one-argument notifier.");
    semanticFunction(0x8E2DEL, "f33_proprietary_operation_finish_join", u32,
        new ParameterImpl("selected_index", u8, currentProgram),
        new ParameterImpl("response_length", new PointerDataType(u32, 4), currentProgram))
        .setComment("Join local fixed finish callback and exact side stub0. Preserve full mergeR10 through status stores and "
            + "dispose; caller8E3A2 compares0/2/other for completion/pending/error. No fake side completion needed.");
    semanticFunction(0x50990L, "f33_get_did_publication_metadata", new PointerDataType(layout0, 4),
        new ParameterImpl("count", new PointerDataType(u16, 4), currentProgram))
        .setComment("Write exact count242 and return2927C, including leading0100/4FB10. Metadata membership is distinct from "
            + "kind0 plus current availability admission.");
    semanticData(0x2927CL, new ArrayDataType(resolve(layout0), 242, 16), "f33_did_publication_metadata",
        "50990 4D36E 4D492 4D802 ROM bytes");
    semanticData(0x2603CL, new ArrayDataType(resolve(layout1), 5, 28), "f33_dcm_did_class",
        "Five configured classes; following zero spare is not traversed by count26016=5.");
    semanticData(0x2A364L, new ArrayDataType(resolve(layout6), 75, 24), "f33_capture_field_descriptor",
        "56664 53190 531E0 ROM bytes");
    semanticData(0xFEBF48ECL, resolve(layout7), "f33_diag_proprietary_message",
        "Retained first-four-word operation view, not the28-byte DCM context; full context retained separately "
            + "at493C.");
    semanticData(0xFEBE5D74L, u32, "f33_dcm_read_expected_body_length",
        "Preflight aggregate length including two DID bytes; not actual emitted body.");
    semanticData(0xFEBE5D78L, u16, "f33_dcm_read_selected_class",
        "Static class index retained separately from metadata81B8.");
    semanticData(0xFEBE5D7AL, u8, "f33_dcm_read_route_kind",
        "1 static class,2 generic dynamic route; exact dynamic bank empty.");
    semanticData(0xFEBE5D7CL, u16, "f33_dcm_read_current_did",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBE5D7EL, u16, "f33_dcm_read_did_cursor",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBE5D80L, u16, "f33_dcm_read_did_count",
        "Configured request admission permits only1.");
    semanticData(0xFEBE5D84L, F33DcmMessageContextType, "f33_dcm_read_message",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBE5F87L, new ArrayDataType(u8, 160, 1), "f33_dtc_status_iteration_snapshot",
        "Rebuilt at first527D6 start1; not live event/physical fault state.");
    semanticData(0xFEBE602CL, new ArrayDataType(u32, 5, 4), "f33_derived_current_dtc_bitmap",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBE6040L, new ArrayDataType(u32, 5, 4), "f33_derived_retained_dtc_bitmap",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBE6054L, new ArrayDataType(u32, 5, 4), "f33_derived_classified_current_dtc_bitmap",
        "Generated from current events with classifier!=0; NOT second-retained event history60F0.");
    semanticData(0xFEBE8197L, u8, "f33_dtc_setting_inhibit_request",
        "Direct85 state; grouped status and F002 are separately scheduled projections.");
    semanticData(0xFEBE8198L, u8, "f33_dtc_requested_status_mask",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBE81B4L, u16, "f33_dtc_iteration_result_count",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBE81B6L, u16, "f33_dtc_iteration_catalogue_cursor",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBE81C4L, u32, "f33_snapshot_identifier_cached_dtc",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBF3BD4L, F33DcmMessageContextType, "f33_dcm_clear_message",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBF3BFCL, F33DcmMessageContextType, "f33_dcm_dtc_count_message",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBF3F24L, F33DcmMessageContextType, "f33_dcm_dtc_list_message",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBF4248L, F33DcmMessageContextType, "f33_dcm_snapshot_identifiers_message",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBF457CL, F33DcmMessageContextType, "f33_dcm_snapshot_record_message",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBF45B4L, F33DcmMessageContextType, "f33_dcm_dtc_setting_message",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBF3C18L, new ArrayDataType(u8, 768, 1), "f33_dtc_count_local_tuple_scratch",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBF3F40L, new ArrayDataType(u8, 768, 1), "f33_dtc_list_local_tuple_scratch",
        "Retained software state; interpretation follows the owning publication/consumer.");
    semanticData(0xFEBF4264L, new ArrayDataType(u8, 768, 1), "f33_snapshot_identifier_local_scratch",
        "Retained software state; interpretation follows the owning publication/consumer.");
    StructureDataType continuation = new StructureDataType(category, "F33DtcListContinuation", 0);
    continuation.setPackingEnabled(true);
    continuation.add(u16, "opaque_00", "Retained then cleared; no further role assigned.");
    continuation.add(u16, "scratch_length", "Complete local tuples already collected.");
    continuation.add(u8, "phase", "0 starts,2 polls; distinct from operation and transport phase.");
    continuation.add(u8, "requested_mask", "Retained request status mask.");
    continuation.add(u8, "local_result", "1 iterator finished;2 requests continuation.");
    continuation.add(u8, "yielded", "First ready pass stores5A after actually queuingED.");
    continuation.add(u8, "side_status", "Exact side callback is a zero-return stub, not a modeled completion.");
    continuation.add(u8, "side_result", "2 keeps the side source pending.");
    continuation.add(new ArrayDataType(u8, 2, 1), "opaque_0a", "Not interpreted.");
    semanticData(0xFEBF3F18L, resolve(continuation), "f33_dtc_list_continuation",
        "Retained local source generation and one-pass yield barrier; queuedED delivery is separate.");
    semanticFunction(0x8C960L, "f33_dcm_advance_dtc_list_request", u32,
        new ParameterImpl("message", new PointerDataType(F33DcmMessageContextType, 4), currentProgram))
        .setComment("Collect local tuples and poll side source; always queueED before the first ready result. "
            + "A later ready call merges retained scratch, retaining only complete tuples that fit, then calls95644. "
            + "Clear continuation only after that API returns. A later derived-status generation does not replace "
            + "the already collected local snapshot; direct native re-entry is not proof of OS event dispatch.");
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
    annotateInitializationAndSnapshots();
    annotateNonthermalCurrentLimits();
    annotateHealthCoherencePolicy();
    annotateResidentFlashOperationLifecycle();
    annotateReceivedInputConditioning();
    annotateResidentDiagnosticLifecycle();
    annotateAcquisitionOwnership();
    annotateResidentSecurityCrypto();
    annotateResidentImageCrypto();
    annotateApplicationAdaptation();
    annotateOutputOwnerLifetimes();
    annotateCurrentReferenceFeedback();
    annotateApplicationSessionSecurity();
    annotateApplicationNetworkLifetimes();
    annotateMonitorCalibrationAndOutputEnvelopes();
    annotateDiagnosticTransportOwnership();
    annotateDiagnosticReadPublication();
    annotatePhaseModulation();
    annotateDataFlashReads();
    annotateFaciSubmission();
    annotatePwmCompareStaging();
    println("SeedCamryF33RecoveredFunctions: seeded " + count
        + " evidence-backed entries and applied exact-F33 semantic prototypes");
  }
}
