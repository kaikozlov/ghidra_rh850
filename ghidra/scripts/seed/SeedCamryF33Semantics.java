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
public class SeedCamryF33Semantics extends GhidraScript {
  private void ensure(long v) throws Exception { Address a=toAddr(v); Listing l=currentProgram.getListing(); Instruction c=l.getInstructionContaining(a); if(c!=null&&!c.getMinAddress().equals(a)) l.clearCodeUnits(c.getMinAddress(),c.getMaxAddress(),false); CodeUnit u=l.getCodeUnitContaining(a); if(u!=null&&!(u instanceof Instruction)) l.clearCodeUnits(u.getMinAddress(),u.getMaxAddress(),false); if(l.getInstructionAt(a)==null&&!disassemble(a)) throw new IllegalStateException("disassembly failed "+a); Function f=currentProgram.getFunctionManager().getFunctionAt(a); if(f==null) f=createFunction(a,null); if(f==null) throw new IllegalStateException("function creation failed "+a); }
  private void annotateMemoryPrimitives() throws Exception {
    DataType pointer = new PointerDataType(VoidDataType.dataType, 4);
    Function copy = getFunctionAt(toAddr(0x89F2EL));
    Function zero = getFunctionAt(toAddr(0x8A134L));
    if (copy == null || zero == null) {
      throw new IllegalStateException("missing exact-F33 memory primitives");
    }
  }
  private void annotateRedundantStatePrimitives() throws Exception {
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType bytes = new PointerDataType(u8, 4);
    DataType halfwords = new PointerDataType(u16, 4);
    DataType words = new PointerDataType(u32, 4);
  }
  private void annotateBootAndFreshness() throws Exception {
    Function relocate = getFunctionAt(toAddr(0x35E4L));
    Function commit = getFunctionAt(toAddr(0x90D6AL));
    if (relocate == null || commit == null) {
      throw new IllegalStateException("missing exact-F33 relocation/freshness functions");
    }
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

    FunctionDefinitionDataType callback =
        new FunctionDefinitionDataType(category, "F33BootInterruptCallback");
    callback.setReturnType(VoidDataType.dataType);
    currentProgram.getDataTypeManager().addDataType(callback, DataTypeConflictHandler.REPLACE_HANDLER);
    StructureDataType dispatch = new StructureDataType(category, "F33BootInterruptEntry", 0);
    dispatch.setPackingEnabled(true);
    dispatch.add(u32, "eiic", "Exact EIIC match; FFFFFFFF is the terminating default.");
    dispatch.add(new PointerDataType(callback, 4), "handler", "No ordinary C arguments.");
    currentProgram.getDataTypeManager().addDataType(dispatch, DataTypeConflictHandler.REPLACE_HANDLER);
    currentProgram.getFunctionManager().removeFunction(toAddr(0x869CL));
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
    getFunctionAt(toAddr(0x74884L)).setInline(true);
    getFunctionAt(toAddr(0x74892L)).setInline(true);
    getFunctionAt(toAddr(0x748A2L)).setInline(true);
    getFunctionAt(toAddr(0x748B0L)).setInline(true);
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
    StructureDataType request =
        new StructureDataType(category, "F33NvmOperation", 0);
    request.setPackingEnabled(true);
    request.add(u32, "operation", "Published operation selector; admission does not validate it.");
    request.add(u16, "logical_handle", "Logical descriptor index, not the physical storage handle.");
    request.add(Undefined2DataType.dataType, "padding_06", "Not copied or initialized by73ADC/73AB0.");
    request.add(pointer, "buffer_08", "Read operation callback consumes this destination pointer.");
    request.add(pointer, "buffer_0c", "Write operation callback consumes this source pointer.");
    DataType requestType = resolve(request);
    getFunctionAt(toAddr(0x745DAL)).setInline(true);
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
    currentProgram.getDataTypeManager().addDataType(halfwords, DataTypeConflictHandler.REPLACE_HANDLER);
    StructureDataType words =
        new StructureDataType(category, "F33PwmWordStage", 0);
    words.setPackingEnabled(true);
    words.add(u32, "w", "Zero-extended quantized third input; reverse lane order.");
    words.add(u32, "v", "Zero-extended quantized second input.");
    words.add(u32, "u", "Zero-extended quantized first input.");
    currentProgram.getDataTypeManager().addDataType(words, DataTypeConflictHandler.REPLACE_HANDLER);
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
    StructureDataType commit =
        new StructureDataType(category, "F33NvmCommitContext", 0);
    commit.setPackingEnabled(true);
    commit.add(recordPointer, "record", "Set by778C6.");
    commit.add(u32, "marker", "77AA8 reads the final-allocation word here and requiresAAAAAAAA.");
    currentProgram.getDataTypeManager().addDataType(commit, DataTypeConflictHandler.REPLACE_HANDLER);
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
    DataType quad = new ArrayDataType(u16, 4, 2);
    StructureDataType record =
        new StructureDataType(category, "F33LearnedQuadRecord", 0);
    record.setPackingEnabled(true);
    record.add(u32, "marker", "3584A requires A55A5AA5, not AA5A5AA5.");
    record.add(quad, "values", "Four raw unsigned halfwords; physical units not recovered.");
    record.add(u32, "opaque_tail", "Included in the application checksum; not published by355F6.");
    currentProgram.getDataTypeManager().addDataType(record, DataTypeConflictHandler.REPLACE_HANDLER);
    StructureDataType bounds =
        new StructureDataType(category, "F33LearnedQuadBounds", 0);
    bounds.setPackingEnabled(true);
    bounds.add(s32, "pair1_upper", "Inclusive signed bound for values0 and1.");
    bounds.add(s32, "pair1_lower", "Inclusive signed bound for values0 and1.");
    bounds.add(s32, "pair2_upper", "Inclusive signed bound for values2 and3.");
    bounds.add(s32, "pair2_lower", "Inclusive signed bound for values2 and3.");
    DataType boundsType = resolve(bounds);
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
    currentProgram.getDataTypeManager().addDataType(stage, DataTypeConflictHandler.REPLACE_HANDLER);
    semanticData(0xFEBF0358L, new ArrayDataType(u8, objectCount, 1),
        "f33_nvm_family1_completion",
        "FF admits the application callback; terminal read/write handlers publish5A/A5. "
        + "Distinct from the redundant application-status bytes atFEBF0328.");
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
    semanticData(eventRows, new ArrayDataType(pairType, eventCount, 8),
        "f33_nvm_operation_event_rows", "Consumed through the counted lookup header.");
    FunctionDefinitionDataType callback =
        new FunctionDefinitionDataType(category, "F33NvmApplicationResultCallback");
    callback.setReturnType(u32);
    callback.setArguments(
        new ParameterDefinitionImpl("event", u8, null),
        new ParameterDefinitionImpl("logical_handle", u16, null),
        new ParameterDefinitionImpl("result", u8, null));
    currentProgram.getDataTypeManager().addDataType(callback, DataTypeConflictHandler.REPLACE_HANDLER);
    FunctionDefinitionDataType zeroCallback =
        new FunctionDefinitionDataType(category, "F33NvmZeroHandleResultCallback");
    zeroCallback.setReturnType(VoidDataType.dataType);
    zeroCallback.setArguments(
        new ParameterDefinitionImpl("event", u8, null),
        new ParameterDefinitionImpl("result", u8, null));
    currentProgram.getDataTypeManager().addDataType(zeroCallback, DataTypeConflictHandler.REPLACE_HANDLER);
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
    getFunctionAt(toAddr(0x7314EL)).setInline(true);
    getFunctionAt(toAddr(0x73552L)).setInline(true);
    getFunctionAt(toAddr(0x73640L)).setInline(true);
  }
  private void annotateNvmStartup() throws Exception {
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
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
    currentProgram.getDataTypeManager().addDataType(classes, DataTypeConflictHandler.REPLACE_HANDLER);
    StructureDataType masks = new StructureDataType(category, "F33NvmDiagnosticMaskMap", 0);
    masks.setPackingEnabled(true);
    masks.add(u32, "source_mask", "Any intersecting input bit selects this row.");
    masks.add(u32, "destination_mask", "OR into the full32 result; not first-match lookup.");
    currentProgram.getDataTypeManager().addDataType(masks, DataTypeConflictHandler.REPLACE_HANDLER);
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
  }
  private void annotateNvmAcquisition() throws Exception {
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType bytes = new PointerDataType(u8, 4);

  }
  private void annotateNvmRequestSelection() throws Exception {
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType byteOut = new PointerDataType(u8, 4);
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
    semanticData(0xFEBF0650L, new ArrayDataType(u8, count, 1),
        "f33_nvm_family2_status", "670C4 bypasses ROM CRC for repaired10;67176 also publishes10 after a RAM update.");
    semanticData(0xFEBF1098L, new ArrayDataType(u8, count, 1),
        "f33_nvm_family2_status_xor55", "Redundant status plane, not CRC bytes.");
    semanticData(0xFEBF10BCL, new ArrayDataType(u8, count, 1),
        "f33_nvm_family2_status_xorAA", "Redundant status plane, not CRC bytes.");
  }
  private void annotateInitializedNvmService() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType operation = getDataAt(toAddr(0xFEBF6AECL)).getDataType();
    StructureDataType guards = new StructureDataType(category, "F33NvmServiceGuards", 0);
    guards.setPackingEnabled(true);
    guards.add(u8, "service", "79A50 clears;79A94 sets1.");
    guards.add(u8, "paired_call", "79AAA clears;79ABE sets1.");
    guards.add(u8, "deferred", "79A32 consumes asFF only when both preceding bytes equal1.");
    currentProgram.getDataTypeManager().addDataType(guards, DataTypeConflictHandler.REPLACE_HANDLER);
  }
  private void annotateApplicationRecordApis() throws Exception {
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType words = new PointerDataType(u32, 4);
    int count = currentProgram.getMemory().getShort(toAddr(0x2AD74L)) & 0xFFFF;
    semanticData(0xFEBF065BL, new ArrayDataType(u8, count, 1),
        "f33_nvm_family2_setter_flags", "66FFE clears and67176 writes5A. No reader recovered; not a proven persistence flag.");
  }
  private void annotateNvmDirectOperations() throws Exception {
    DataType u32 = UnsignedIntegerDataType.dataType;
  }
  private void annotateControlPipeline() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType halfwords = new PointerDataType(u16, 4);
    // Inline real leaf p-code so the shared R6 scale survives the first call.
    getFunctionAt(toAddr(0x38E52L)).setInline(true);
    getFunctionAt(toAddr(0x38EE2L)).setInline(true);
  }
  private void annotateSensingPipeline() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    // Preserve the actual R7 bank across this leaf, not an invented extra return or ABI shim.
    getFunctionAt(toAddr(0x47D62L)).setInline(true);
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
    currentProgram.getDataTypeManager().addDataType(sample, DataTypeConflictHandler.REPLACE_HANDLER);
  }
  private void annotateEstimatorAcquisition() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
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
  }
  private void annotateRetainedEstimatorQualification() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType bytes = new PointerDataType(u8, 4);
  }
  private void annotateEstablishedTracking() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType words = new PointerDataType(s32, 4);
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
    currentProgram.getDataTypeManager().addDataType(following, DataTypeConflictHandler.REPLACE_HANDLER);
  }
  private void annotateRemainingEcuThermalModels() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType point = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33CurvePointS16U16");
    DataType currentCurve = new ArrayDataType(point, 7, 4);
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
    currentProgram.getDataTypeManager().addDataType(record, DataTypeConflictHandler.REPLACE_HANDLER);
  }
  private void annotateThermalHistoryLifecycle() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
  }
  private void annotateThermalArbitration() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType byteOut = new PointerDataType(u8, 4);
  }
  private void annotateFaultActions() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType words = new PointerDataType(u16, 4);
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
  }
  private void annotateDiagnosticAgingAndClear() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType bytes = new PointerDataType(u8, 4);
    DataType halves = new PointerDataType(u16, 4);
  }
  private void annotateDiagnosticTransactions() throws Exception {
    DataType v = VoidDataType.dataType;
  }
  private void annotateAssistComposition() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
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
    StructureDataType calibration = new StructureDataType(new CategoryPath("/CamryF33"), "F33GainSlewCalibration", 0);
    calibration.setPackingEnabled(true);
    DataType halfwordPointer = new PointerDataType(u16, 4);
    calibration.add(halfwordPointer, "down_target", "Dereferenced by C5106.");
    calibration.add(halfwordPointer, "down_step", "Dereferenced by C5106.");
    calibration.add(u16, "up_target", "Inline value, not a pointer.");
    calibration.add(u16, "opaque_0a", "Not consumed by C5106.");
    calibration.add(halfwordPointer, "up_step", "Dereferenced by C5106.");
    currentProgram.getDataTypeManager().addDataType(calibration, DataTypeConflictHandler.REPLACE_HANDLER);
  }
  private void annotatePairedMonitorActions() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
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
    long[] predicateAddresses = {0x43FB2L,0x44064L,0x44654L,0x44702L,0x447C4L,0x448B2L,
        0x4611CL,0x461BAL,0x463F2L,0x46490L,0x46AA6L,0x46AC6L,0x46C58L,0x46F62L,
        0x47470L,0x4749CL,0x47538L,0x47564L,0x47606L,0x4770CL,0x4782AL,0x47860L,0x479C6L,0x479FCL};
    long[] retained = {0x462D8L,0x465AEL,0x46D92L,0x4709CL,0x478CEL,0x47A6AL};
  }
  private void annotateCommunicationStatusComposition() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
  }
  private void annotateAngleControllerComposition() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
  }
  private void annotateCompensationPublication() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
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
    currentProgram.getDataTypeManager().addDataType(slot, DataTypeConflictHandler.REPLACE_HANDLER);
  }
  private void annotatePairedSourceMonitorComposition() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
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
    currentProgram.getDataTypeManager().addDataType(callback, DataTypeConflictHandler.REPLACE_HANDLER);
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
    FunctionDefinitionDataType writeDidPrecondition = new FunctionDefinitionDataType(category, "F33WriteDidPrecondition");
    writeDidPrecondition.setReturnType(u32);
    currentProgram.getDataTypeManager().addDataType(writeDidPrecondition, DataTypeConflictHandler.REPLACE_HANDLER);
    FunctionDefinitionDataType writeDidAction = new FunctionDefinitionDataType(category, "F33WriteDidAction");
    writeDidAction.setReturnType(u32);
    writeDidAction.setArguments(new ParameterDefinitionImpl("payload", bytes, null),
        new ParameterDefinitionImpl("length", u16, null));
    currentProgram.getDataTypeManager().addDataType(writeDidAction, DataTypeConflictHandler.REPLACE_HANDLER);
    StructureDataType writeDid = new StructureDataType(category, "F33WriteDidCallbacks", 0);
    writeDid.setPackingEnabled(true);
    writeDid.add(u16, "identifier", "Configured diagnostic identifier.");
    writeDid.add(u16, "opaque_02", "Zero in the exact registered table.");
    writeDid.add(new PointerDataType(writeDidPrecondition, 4), "precondition", "Fixed callback or null; return3 retries same matched row.");
    writeDid.add(new PointerDataType(writeDidAction, 4), "action", "Fixed callback or null; admission is separate from completion.");
    currentProgram.getDataTypeManager().addDataType(writeDid, DataTypeConflictHandler.REPLACE_HANDLER);
    FunctionDefinitionDataType routinePrecondition = new FunctionDefinitionDataType(category, "F33RoutinePrecondition");
    routinePrecondition.setReturnType(u32);
    routinePrecondition.setArguments(new ParameterDefinitionImpl("control_type", u8, null),
        new ParameterDefinitionImpl("input", bytes, null),
        new ParameterDefinitionImpl("input_length", u16, null));
    currentProgram.getDataTypeManager().addDataType(routinePrecondition, DataTypeConflictHandler.REPLACE_HANDLER);
    FunctionDefinitionDataType routineAction = new FunctionDefinitionDataType(category, "F33RoutineAction");
    routineAction.setReturnType(u32);
    routineAction.setArguments(new ParameterDefinitionImpl("control_type", u8, null),
        new ParameterDefinitionImpl("input", bytes, null),
        new ParameterDefinitionImpl("input_length", u16, null),
        new ParameterDefinitionImpl("output", bytes, null),
        new ParameterDefinitionImpl("output_length", halves, null));
    currentProgram.getDataTypeManager().addDataType(routineAction, DataTypeConflictHandler.REPLACE_HANDLER);
    StructureDataType routine = new StructureDataType(category, "F33RoutineCallbacks", 0);
    routine.setPackingEnabled(true);
    routine.add(u16, "identifier", "Configured diagnostic identifier.");
    routine.add(u16, "opaque_02", "Zero in the exact registered table.");
    routine.add(new PointerDataType(routinePrecondition, 4), "precondition", "Fixed callback or null; return3 retries same matched row.");
    routine.add(new PointerDataType(routineAction, 4), "action", "Fixed callback or null; admission is separate from completion.");
    currentProgram.getDataTypeManager().addDataType(routine, DataTypeConflictHandler.REPLACE_HANDLER);
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
    // Each phase worker retains its input when its transition condition is not met.
    // Formal child arguments are needed as well as the dispatcher's scalar return.
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
    CategoryPath category = new CategoryPath("/CamryF33");
    FunctionDefinitionDataType callback = new FunctionDefinitionDataType(category, "F33ModeFamilyHook");
    callback.setReturnType(v);
    currentProgram.getDataTypeManager().addDataType(callback, DataTypeConflictHandler.REPLACE_HANDLER);
    StructureDataType hooks = new StructureDataType(category, "F33ModeFamilyHooks", 0);
    hooks.setPackingEnabled(true);
    hooks.add(new PointerDataType(callback, 4), "entry", "Called before publishing new live mode.");
    hooks.add(new PointerDataType(callback, 4), "exit", "Old-family exit precedes new-family entry.");
    currentProgram.getDataTypeManager().addDataType(hooks, DataTypeConflictHandler.REPLACE_HANDLER);
    StructureDataType port = new StructureDataType(category, "F33ChannelPortDescriptor", 0);
    port.setPackingEnabled(true);
    port.add(u32, "output_selector", "Output bit in low4; output port in bits8..15.");
    port.add(u8, "input_port", "Input register stride is0x40 bytes.");
    port.add(u8, "input_bit", "Bit selected from a halfword port read.");
    port.add(u8, "reference_level", "Compared against input and selected by a clear request bit.");
    port.add(u8, "requested_level", "Selected by an asserted request bit.");
    currentProgram.getDataTypeManager().addDataType(port, DataTypeConflictHandler.REPLACE_HANDLER);
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
    currentProgram.getDataTypeManager().addDataType(channels, DataTypeConflictHandler.REPLACE_HANDLER);
  }
  private void annotateDataFlashReads() throws Exception {
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType words = new PointerDataType(u32, 4);
  }
  private void annotateFaciSubmission() throws Exception {
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
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
  }
  private void annotateComposedMonitorLayouts() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
    FunctionDefinitionDataType predicate = new FunctionDefinitionDataType(category, "F33MonitorPredicate");
    predicate.setReturnType(u32);
    currentProgram.getDataTypeManager().addDataType(predicate, DataTypeConflictHandler.REPLACE_HANDLER);
    FunctionDefinitionDataType action = new FunctionDefinitionDataType(category, "F33MonitorAction");
    action.setReturnType(v);
    currentProgram.getDataTypeManager().addDataType(action, DataTypeConflictHandler.REPLACE_HANDLER);
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
  }
  private void annotateApplicationModeTransitions() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
  }
  private void annotateResetAndForegroundOwnership() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType uintPointer = new PointerDataType(u32, 4);
  }
  private void annotateInitializationAndSnapshots() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
  }

  private void annotateHealthCoherencePolicy() throws Exception {
    getFunctionAt(toAddr(0xB4370L)).setInline(true);
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
    StructureDataType crc = new StructureDataType(category, "F33BootCrcDescriptor", 0);
    crc.setPackingEnabled(true);
    crc.add(u32, "base", "Region data address.");
    crc.add(u32, "length", "CRC byte extent.");
    crc.add(new PointerDataType(u32, 4), "base_metadata", "Word that must equal base.");
    crc.add(new PointerDataType(u32, 4), "length_metadata", "Word that must equal length.");
    DataType crcType = resolve(crc);
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
    FunctionDefinitionDataType blank = new FunctionDefinitionDataType(category, "F33BootBlankCheckCallback");
    blank.setReturnType(u32);
    blank.setArguments(new ParameterDefinition[] {
        new ParameterDefinitionImpl("address", u32, null),
        new ParameterDefinitionImpl("word_count", u32, null)});
    currentProgram.getDataTypeManager().addDataType(blank, DataTypeConflictHandler.REPLACE_HANDLER);
    DataType blankType = currentProgram.getDataTypeManager().addDataType(blank, DataTypeConflictHandler.REPLACE_HANDLER);
    getFunctionAt(toAddr(0x344CL)).setInline(true);
    getFunctionAt(toAddr(0x40A2L)).setInline(true);
  }

  private void annotateReceivedInputConditioning() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
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
    currentProgram.getDataTypeManager().addDataType(service, DataTypeConflictHandler.REPLACE_HANDLER);
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
    StructureDataType layout2 = new StructureDataType(category, "F33BootChannelEntry", 0);
    layout2.setPackingEnabled(true);
    layout2.add(u32, "handoff_selector", null);
    layout2.add(u8, "transport_handle", null);
    layout2.add(u8, "address_mode", null);
    layout2.add(u16, "reserved", null);
    DataType layout2Type = resolve(layout2);
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
    StructureDataType layout4 = new StructureDataType(category, "F33BootRoutineEntry", 0);
    layout4.setPackingEnabled(true);
    layout4.add(u32, "opaque_word", null);
    layout4.add(u16, "identifier", null);
    layout4.add(u8, "configured_subfunction", null);
    layout4.add(u8, "request_option_length", null);
    layout4.add(u8, "response_extra_length", null);
    layout4.add(new ArrayDataType(u8, 3, 1), "reserved", null);
    DataType layout4Type = resolve(layout4);
    StructureDataType layout5 = new StructureDataType(category, "F33BootTimerSlot", 0);
    layout5.setPackingEnabled(true);
    layout5.add(u32, "deadline", null);
    layout5.add(u32, "token", null);
    layout5.add(u8, "armed", null);
    layout5.add(u8, "generation", null);
    layout5.add(u16, "reserved", null);
    DataType layout5Type = resolve(layout5);
    StructureDataType layout6 = new StructureDataType(category, "F33BootHandoffRecord", 0);
    layout6.setPackingEnabled(true);
    layout6.add(u32, "tag", null);
    layout6.add(u32, "channel_selector", null);
    layout6.add(new ArrayDataType(u32, 2, 4), "opaque_words2_3", null);
    layout6.add(u32, "session_subfunction", null);
    layout6.add(u32, "suppress_positive", null);
    layout6.add(new ArrayDataType(u32, 3, 4), "opaque_words6_8", null);
    DataType layout6Type = resolve(layout6);
    getFunctionAt(toAddr(0x6422L)).setInline(true);
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
    // The real leaf preserves R8 used by the context-valid store after expansion.
    getFunctionAt(toAddr(0x7594L)).setInline(true);
  }
  private void annotatePhaseModulation() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType point = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33CurvePointS16U16");
    if (point == null) throw new IllegalStateException("missing exact-F33 curve point layout");
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
    currentProgram.getDataTypeManager().addDataType(curvePoint, DataTypeConflictHandler.REPLACE_HANDLER);
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
    StructureDataType fitLayout2 = new StructureDataType(category, "F33FitCoefficients", 0);
    fitLayout2.setPackingEnabled(true);
    fitLayout2.add(new ArrayDataType(u16, 6, 2), "first_center", null);
    fitLayout2.add(new ArrayDataType(u16, 6, 2), "first_gain", null);
    fitLayout2.add(new ArrayDataType(s16, 6, 2), "second_center", null);
    fitLayout2.add(new ArrayDataType(u16, 6, 2), "second_gain", null);
    fitLayout2.add(new ArrayDataType(u16, 3, 2), "component_angle", null);
    DataType F33FitCoefficientsType = resolve(fitLayout2);
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
    currentProgram.getDataTypeManager().addDataType(parameters, DataTypeConflictHandler.REPLACE_HANDLER);
  }

  private void annotateOutputOwnerLifetimes() throws Exception {
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    CategoryPath category = new CategoryPath("/CamryF33");
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
    currentProgram.getDataTypeManager().addDataType(policyCallback, DataTypeConflictHandler.REPLACE_HANDLER);
    DataType F33NormalNetworkPolicyCallbackType = currentProgram.getDataTypeManager().addDataType(policyCallback, DataTypeConflictHandler.REPLACE_HANDLER);
    EnumDataType driverStates = new EnumDataType(category, "F33DriverChannelSoftwareState", 2);
    driverStates.add("uninitialized", 0x6e91L);
    driverStates.add("initialized", 0x6d92L);
    driverStates.add("stopped_software_state", 0x6b94L);
    driverStates.add("running_software_state", 0x57a8L);
    driverStates.add("start_pending", 0x3bc4L);
    driverStates.add("stop_pending", 0x3ec1L);
    driverStates.add("recovery_pending", 0x3dc2L);
    currentProgram.getDataTypeManager().addDataType(driverStates, DataTypeConflictHandler.REPLACE_HANDLER);
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
    createLabel(toAddr(0x25CFCL), "f33_dcm_communication_control_service_descriptor", true);
    currentProgram.getListing().setComment(toAddr(0x25CFCL), CodeUnit.PLATE_COMMENT, "Exact configured SID28/network data; selected software interface only.");
    createLabel(toAddr(0x26BB0L), "f33_dcm_event26_communication_resume_callback", true);
    currentProgram.getListing().setComment(toAddr(0x26BB0L), CodeUnit.PLATE_COMMENT, "98946dispatchbase26B18,event26h.");
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
    currentProgram.getDataTypeManager().addDataType(layout0, DataTypeConflictHandler.REPLACE_HANDLER);
    layout1.add(u8, "changed", "5A iff staged coefficients differ on valid nonbusy source path.");
    layout1.add(u8, "range_error", "5A for rejected changed coefficients; equal bypasses validation.");
    layout1.add(layout0, "coefficients", "Consumed by current conditioning before later scheduled adoption.");
    layout1.add(new ArrayDataType(u8, 2, 1), "opaque_26", "Not assigned a calibration meaning.");
    currentProgram.getDataTypeManager().addDataType(layout1, DataTypeConflictHandler.REPLACE_HANDLER);
    layout2.add(u8, "source_status", "32A8C publishes44/22.");
    layout2.add(u8, "busy", "5A while refresh is unresolved.");
    layout2.add(layout0, "coefficients", "Grouped by sign/bias across both banks.");
    layout2.add(new ArrayDataType(u8, 2, 1), "opaque_26", "Not interpreted.");
    layout2.add(u32, "marker", "A55A5AA5 valid; complementary failure. Setter publication is not acceptance.");
    currentProgram.getDataTypeManager().addDataType(layout2, DataTypeConflictHandler.REPLACE_HANDLER);
    layout3.add(u32, "marker", "Record0200 marker, separate from status10.");
    layout3.add(new ArrayDataType(s16, 3, 2), "bank1_negative_gain", "Serialized bank1 before bank0; different order from staged arrays.");
    layout3.add(new ArrayDataType(s16, 3, 2), "bank1_nonnegative_gain", "Serialized bank1 before bank0; different order from staged arrays.");
    layout3.add(new ArrayDataType(s16, 3, 2), "bank1_bias", "Serialized bank1 before bank0; different order from staged arrays.");
    layout3.add(new ArrayDataType(s16, 3, 2), "bank0_negative_gain", "Serialized bank1 before bank0; different order from staged arrays.");
    layout3.add(new ArrayDataType(s16, 3, 2), "bank0_nonnegative_gain", "Serialized bank1 before bank0; different order from staged arrays.");
    layout3.add(new ArrayDataType(s16, 3, 2), "bank0_bias", "Serialized bank1 before bank0; different order from staged arrays.");
    currentProgram.getDataTypeManager().addDataType(layout3, DataTypeConflictHandler.REPLACE_HANDLER);
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
    currentProgram.getDataTypeManager().addDataType(layout4, DataTypeConflictHandler.REPLACE_HANDLER);
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
    currentProgram.getDataTypeManager().addDataType(layout5, DataTypeConflictHandler.REPLACE_HANDLER);
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
    StructureDataType layout14 = new StructureDataType(category, "F33CanTpRxConnection", 0);
    layout14.setPackingEnabled(true);
    StructureDataType layout15 = new StructureDataType(category, "F33CanTpRxState", 0);
    layout15.setPackingEnabled(true);
    StructureDataType layout16 = new StructureDataType(category, "F33CanTpChannelConfiguration", 0);
    layout16.setPackingEnabled(true);
    layout0.add(u16, "protocol_index", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(u16, "connection_index", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(u16, "receive_descriptor_index", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(u16, "communication_slot", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(u16, "paired_receive_slot_or_ffff", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(u16, "receive_id", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout0, DataTypeConflictHandler.REPLACE_HANDLER);
    layout1.add(u32, "capacity", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(new PointerDataType(u8, 4), "base", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout1, DataTypeConflictHandler.REPLACE_HANDLER);
    layout2.add(new PointerDataType(u8, 4), "write_cursor", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(u16, "received_length", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(new ArrayDataType(u8, 2, 1), "opaque_06", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(u16, "remaining_capacity", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(u8, "receiving", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(u8, "abort_pending", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(u8, "inactivity_participant", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(new ArrayDataType(u8, 3, 1), "opaque_0d", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout2, DataTypeConflictHandler.REPLACE_HANDLER);
    layout3.add(u32, "functional_timeout_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(u16, "upper_receive_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(u16, "lower_receive_cancel_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(u8, "addressing_kind", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(u8, "functional_response_inhibit", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(new ArrayDataType(u8, 2, 1), "opaque_0a", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout3, DataTypeConflictHandler.REPLACE_HANDLER);
    layout4.add(u32, "response_capacity", "Recovered field use; opaque fields remain uninterpreted.");
    layout4.add(u16, "upper_confirmation_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout4.add(u16, "lower_transmit_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout4.add(u8, "retain_session_on_failure", "Recovered field use; opaque fields remain uninterpreted.");
    layout4.add(new ArrayDataType(u8, 3, 1), "opaque_09", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout4, DataTypeConflictHandler.REPLACE_HANDLER);
    layout5.add(u16, "configured_protocol_tag", "Recovered field use; opaque fields remain uninterpreted.");
    layout5.add(u8, "opaque_02", "Recovered field use; opaque fields remain uninterpreted.");
    layout5.add(u8, "priority", "Recovered field use; opaque fields remain uninterpreted.");
    layout5.add(new PointerDataType(layout3, 4), "receive_rows", "Recovered field use; opaque fields remain uninterpreted.");
    layout5.add(new PointerDataType(layout4, 4), "transmit", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout5, DataTypeConflictHandler.REPLACE_HANDLER);
    layout6.add(new PointerDataType(new PointerDataType(layout5, 4), 4), "connections", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u32, "overall_timeout_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u16, "inactivity_timeout_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u16, "dispatch_delay_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u16, "p2_margin_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u16, "p2_star_margin_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u8, "published_protocol_value", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(u8, "allow_lower_cancellation", "Recovered field use; opaque fields remain uninterpreted.");
    layout6.add(new ArrayDataType(u8, 2, 1), "opaque_12", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout6, DataTypeConflictHandler.REPLACE_HANDLER);
    layout7.add(new PointerDataType(layout7, 4), "next", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(new PointerDataType(u8, 4), "data", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(u16, "length", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(new ArrayDataType(u8, 2, 1), "opaque_0a", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(u8, "disposition", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(new ArrayDataType(u8, 3, 1), "opaque_0d", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout7, DataTypeConflictHandler.REPLACE_HANDLER);
    layout8.add(new PointerDataType(layout7, 4), "sentinel", "Recovered field use; opaque fields remain uninterpreted.");
    layout8.add(new PointerDataType(layout7, 4), "tail", "Recovered field use; opaque fields remain uninterpreted.");
    layout8.add(new PointerDataType(u8, 4), "copy_cursor", "Recovered field use; opaque fields remain uninterpreted.");
    layout8.add(u16, "remaining_length", "Recovered field use; opaque fields remain uninterpreted.");
    layout8.add(new ArrayDataType(u8, 2, 1), "opaque_0e", "Recovered field use; opaque fields remain uninterpreted.");
    layout8.add(u8, "notification_result", "Recovered field use; opaque fields remain uninterpreted.");
    layout8.add(u8, "pending_notification", "Recovered field use; opaque fields remain uninterpreted.");
    layout8.add(new ArrayDataType(u8, 2, 1), "opaque_12", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout8, DataTypeConflictHandler.REPLACE_HANDLER);
    layout9.add(u8, "retry_kind", "Recovered field use; opaque fields remain uninterpreted.");
    layout9.add(u8, "opaque_01", "Recovered field use; opaque fields remain uninterpreted.");
    layout9.add(u16, "retry_count", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout9, DataTypeConflictHandler.REPLACE_HANDLER);
    layout10.add(new PointerDataType(u8, 4), "data", "Recovered field use; opaque fields remain uninterpreted.");
    layout10.add(u32, "length", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout10, DataTypeConflictHandler.REPLACE_HANDLER);
    layout11.add(u32, "remaining_or_accepted_length", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(u16, "transmit_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(u16, "timeout_ticks", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(u8, "state", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(u8, "sequence_number", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(u8, "block_remaining", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(u8, "block_size", "Initial FC BS; zero means unrestricted, not boolean.");
    layout11.add(u8, "spacing_ticks", "Recovered field use; opaque fields remain uninterpreted.");
    layout11.add(new ArrayDataType(u8, 3, 1), "opaque_0d", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout11, DataTypeConflictHandler.REPLACE_HANDLER);
    layout12.add(new PointerDataType(layout16, 4), "channel_rows", "Exact configured channel records.");
    layout12.add(u16, "first_receive_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(u16, "first_transmit_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(u16, "first_canif_receive_id", "Receive-frame namespace starts0804.");
    layout12.add(u16, "first_canif_confirmation_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(u8, "channel_count", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(u8, "receive_count", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(u8, "transmit_count", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(u8, "canif_receive_count", "Three configured frame receive IDs.");
    layout12.add(u8, "canif_confirmation_count", "Recovered field use; opaque fields remain uninterpreted.");
    layout12.add(new ArrayDataType(u8, 3, 1), "opaque_11", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout12, DataTypeConflictHandler.REPLACE_HANDLER);
    layout13.add(u8, "opaque_00", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "channel_state_index", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u16, "transmit_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u16, "canif_confirmation_id", "7A5C2 active-owner lookup.");
    layout13.add(u16, "flow_control_receive_id", "7A480 FC routing.");
    layout13.add(u16, "upper_response_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u16, "canif_frame_id", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "addressing_format", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "single_frame_only", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "address_byte", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "flow_control_address_byte", "Format4 incoming address; exact rows use normal format.");
    layout13.add(u16, "frame_confirmation_timeout_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u16, "flow_control_timeout_raw", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u16, "consecutive_copy_timeout_raw", "N_Cs budget with software spacing adjustments.");
    layout13.add(u8, "frame_capacity", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "cancel_supported", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "overlap_final_confirmation_policy", "Generic final-overlap success policy; configured0.");
    layout13.add(u8, "pad_frames_to_eight", "Recovered field use; opaque fields remain uninterpreted.");
    layout13.add(u8, "require_padded_flow_control", "7B9C8 short-frame gate; configured1.");
    layout13.add(u8, "extended_transmit_address_byte", "Formats2/3 only; exact rows normal.");
    layout13.add(u8, "preemption_rank", "Compared with RX rank; exact per-channel ranks equal.");
    layout13.add(new ArrayDataType(u8, 3, 1), "opaque_1d", "Unproved trailing fields.");
    currentProgram.getDataTypeManager().addDataType(layout13, DataTypeConflictHandler.REPLACE_HANDLER);
    layout14.add(u8, "connection_index", "7A84C/7A89A indexes complementary parameter storage");
    layout14.add(u8, "channel_state_index", "7AEBE/7B126 select32-byte state stride");
    layout14.add(u16, "receive_id", "7A6D2 lookup and retained ownership");
    layout14.add(u16, "canif_receive_id", "7A41C dispatch");
    layout14.add(u16, "canif_fc_confirmation_id", "7A620 matching");
    layout14.add(u16, "upper_receive_id", "7AD64/7A8E8/7A79E upper interface");
    layout14.add(u16, "canif_fc_transmit_id", "7A96C submit;FFFF disables configured FF");
    layout14.add(u8, "addressing_format", "22B98 PCI offset lookup");
    layout14.add(u8, "single_frame_only", "7AE76 rejects nonzero");
    layout14.add(u8, "receive_address_byte", "7A41C format4 address match only; all exact rows normal");
    layout14.add(u8, "flow_control_address_byte", "7A96C format4 outgoing address only; all exact rows normal");
    layout14.add(u16, "frame_confirmation_timeout_raw", "7A9DE timerN_Ar+2");
    layout14.add(u16, "buffer_wait_timeout_raw", "7AEBE/7B18A N_Br-3");
    layout14.add(u16, "consecutive_receive_timeout_raw", "7B06A/7B18A N_Cr+2");
    layout14.add(u8, "default_block_size", "7A862 fallback and7A84C init");
    layout14.add(u8, "default_stmin_encoding", "7A8B0 fallback and7A89A init");
    layout14.add(u16, "wait_frame_limit", "7A9DE compares wait count before WAIT");
    layout14.add(u8, "require_padded_receive", "7ABA2/7AFF8 extent gates");
    layout14.add(u8, "pad_flow_control_to_eight", "7A96C");
    layout14.add(u8, "extended_flow_address_byte", "7A96C format2/3 outgoing; exact rows normal");
    layout14.add(u8, "preemption_rank", "7AC9C/7ABE6 lower numeric rank may displace owner; exact per-channel ranks equal");
    layout14.add(new ArrayDataType(u8, 2, 1), "opaque_1e", "Unproved; retain opaque bytes.");
    currentProgram.getDataTypeManager().addDataType(layout14, DataTypeConflictHandler.REPLACE_HANDLER);
    if (layout14.getLength() != 32) throw new IllegalStateException("F33CanTpRxConnection extent drift");
    layout15.add(u32, "remaining_length", "7AEBE subtract first payload;7B06A append");
    layout15.add(u16, "receive_id", "7AEBE store;7A77E resetFFFF");
    layout15.add(u16, "timeout_ticks", "7A9DE/7B18A and7B248");
    layout15.add(u16, "wait_frame_count", "7A9DE increments timed WAIT; reset on CTS");
    layout15.add(u8, "state", "E1 idle,69 capacity poll,5A awaiting FC confirm,4B receiving CF");
    layout15.add(u8, "first_frame_dlc", "7AEBE stores byte from frame length; no new meaning inferred");
    layout15.add(u8, "expected_sequence_number", "7AEBE initializes1;7B06A modulo16");
    layout15.add(u8, "block_remaining", "7A9DE reloadBS;7B06A decrements only nonzero");
    layout15.add(u8, "flow_status_marker", "F0 CTS/E1 WAIT/D2 OVERFLOW internal markers; low nibble emitted");
    layout15.add(u8, "admission_generation", "SF/FF admission increments;7AAF2 qualifies reset by snapshot equality;7A77E preserves");
    currentProgram.getDataTypeManager().addDataType(layout15, DataTypeConflictHandler.REPLACE_HANDLER);
    if (layout15.getLength() != 16) throw new IllegalStateException("F33CanTpRxState extent drift");
    layout16.add(new PointerDataType(layout14, 4), "receive_rows", "7A41C/7A6D2");
    layout16.add(new PointerDataType(layout13, 4), "transmit_rows", "7A480/7A728");
    layout16.add(u8, "half_duplex", "7B3D0 requires peerE1 when1; SF/FF gate7ADF8/7AF76");
    layout16.add(u8, "receive_count", "7A41C/7A6D2");
    layout16.add(u8, "transmit_count", "7A480/7A728");
    layout16.add(u8, "configured_index", "ROM0,1,2; no runtime semantic beyond identity assigned");
    currentProgram.getDataTypeManager().addDataType(layout16, DataTypeConflictHandler.REPLACE_HANDLER);
    if (layout16.getLength() != 12) throw new IllegalStateException("F33CanTpChannelConfiguration extent drift");
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
    currentProgram.getDataTypeManager().addDataType(F33DidPayloadReader, DataTypeConflictHandler.REPLACE_HANDLER);
    FunctionDefinitionDataType F33DiagnosticAvailability = new FunctionDefinitionDataType(category, "F33DiagnosticAvailability");
    F33DiagnosticAvailability.setReturnType(u32);
    currentProgram.getDataTypeManager().addDataType(F33DiagnosticAvailability, DataTypeConflictHandler.REPLACE_HANDLER);
    FunctionDefinitionDataType F33DidClassPresence = new FunctionDefinitionDataType(category, "F33DidClassPresence");
    F33DidClassPresence.setReturnType(u32);
    F33DidClassPresence.setArguments(new ParameterDefinitionImpl("did", u16, null),
        new ParameterDefinitionImpl("operation", u8, null),
        new ParameterDefinitionImpl("absent", new PointerDataType(u8, 4), null));
    currentProgram.getDataTypeManager().addDataType(F33DidClassPresence, DataTypeConflictHandler.REPLACE_HANDLER);
    FunctionDefinitionDataType F33DidClassLength = new FunctionDefinitionDataType(category, "F33DidClassLength");
    F33DidClassLength.setReturnType(u32);
    F33DidClassLength.setArguments(new ParameterDefinitionImpl("did", u16, null),
        new ParameterDefinitionImpl("operation", u8, null),
        new ParameterDefinitionImpl("length", new PointerDataType(u16, 4), null));
    currentProgram.getDataTypeManager().addDataType(F33DidClassLength, DataTypeConflictHandler.REPLACE_HANDLER);
    FunctionDefinitionDataType F33DidClassRead = new FunctionDefinitionDataType(category, "F33DidClassRead");
    F33DidClassRead.setReturnType(u32);
    F33DidClassRead.setArguments(new ParameterDefinitionImpl("did", u16, null),
        new ParameterDefinitionImpl("output", new PointerDataType(u8, 4), null),
        new ParameterDefinitionImpl("operation", u8, null),
        new ParameterDefinitionImpl("length", new PointerDataType(u16, 4), null),
        new ParameterDefinitionImpl("nrc", new PointerDataType(u8, 4), null));
    currentProgram.getDataTypeManager().addDataType(F33DidClassRead, DataTypeConflictHandler.REPLACE_HANDLER);
    FunctionDefinitionDataType F33DidClassWrite = new FunctionDefinitionDataType(category, "F33DidClassWrite");
    F33DidClassWrite.setReturnType(u32);
    F33DidClassWrite.setArguments(new ParameterDefinitionImpl("did", u16, null),
        new ParameterDefinitionImpl("payload", new PointerDataType(u8, 4), null),
        new ParameterDefinitionImpl("operation", u8, null),
        new ParameterDefinitionImpl("length", u16, null),
        new ParameterDefinitionImpl("nrc", new PointerDataType(u8, 4), null));
    currentProgram.getDataTypeManager().addDataType(F33DidClassWrite, DataTypeConflictHandler.REPLACE_HANDLER);
    FunctionDefinitionDataType F33CaptureFieldSerializer = new FunctionDefinitionDataType(category, "F33CaptureFieldSerializer");
    F33CaptureFieldSerializer.setReturnType(v);
    F33CaptureFieldSerializer.setArguments(new ParameterDefinitionImpl("view", u8, null),
        new ParameterDefinitionImpl("output", new PointerDataType(u8, 4), null));
    currentProgram.getDataTypeManager().addDataType(F33CaptureFieldSerializer, DataTypeConflictHandler.REPLACE_HANDLER);
    layout0.add(u16, "did", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(u16, "payload_length", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(new PointerDataType(F33DidPayloadReader, 4), "reader", "Recovered field use; opaque fields remain uninterpreted.");
    layout0.add(new PointerDataType(F33DiagnosticAvailability, 4), "available", "Null admits; otherwise exact5A");
    layout0.add(u8, "route_kind", "Only kind0 selected by4D36E");
    layout0.add(new ArrayDataType(u8, 3, 1), "opaque_0d", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout0, DataTypeConflictHandler.REPLACE_HANDLER);
    layout1.add(new PointerDataType(F33DidClassPresence, 4), "presence", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(new PointerDataType(F33DidClassLength, 4), "length", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(new PointerDataType(F33DidClassRead, 4), "read", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(new PointerDataType(F33DidClassWrite, 4), "write", "Reuse existing write callback ABI; not an untyped request-derived target");
    layout1.add(new PointerDataType(v, 4), "policy", "Fixed class access-policy object");
    layout1.add(u16, "first_did", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(u16, "last_did", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(u8, "probe_presence", "Recovered field use; opaque fields remain uninterpreted.");
    layout1.add(new ArrayDataType(u8, 3, 1), "opaque_19", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout1, DataTypeConflictHandler.REPLACE_HANDLER);
    layout2.add(u8, "status", "Status namespace differs by operation; not a universal success Boolean");
    layout2.add(u8, "detail", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(u16, "length", "Recovered field use; opaque fields remain uninterpreted.");
    layout2.add(new PointerDataType(u8, 4), "bytes", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout2, DataTypeConflictHandler.REPLACE_HANDLER);
    layout3.add(new PointerDataType(u8, 4), "bytes", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(new PointerDataType(u16, 4), "length", "Recovered field use; opaque fields remain uninterpreted.");
    layout3.add(new PointerDataType(u16, 4), "capacity", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout3, DataTypeConflictHandler.REPLACE_HANDLER);
    layout4.add(new ArrayDataType(u8, 3, 1), "dtc_msb_first", "Recovered field use; opaque fields remain uninterpreted.");
    layout4.add(u8, "status", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout4, DataTypeConflictHandler.REPLACE_HANDLER);
    layout5.add(new ArrayDataType(u8, 3, 1), "dtc_msb_first", "Recovered field use; opaque fields remain uninterpreted.");
    layout5.add(u8, "record_number", "1 or10, not DTC status");
    currentProgram.getDataTypeManager().addDataType(layout5, DataTypeConflictHandler.REPLACE_HANDLER);
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
    currentProgram.getDataTypeManager().addDataType(layout6, DataTypeConflictHandler.REPLACE_HANDLER);
    layout7.add(new PointerDataType(u8, 4), "request", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(u32, "request_length", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(new PointerDataType(u8, 4), "response", "Recovered field use; opaque fields remain uninterpreted.");
    layout7.add(u32, "response_length", "Recovered field use; opaque fields remain uninterpreted.");
    currentProgram.getDataTypeManager().addDataType(layout7, DataTypeConflictHandler.REPLACE_HANDLER);
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
    currentProgram.getDataTypeManager().addDataType(continuation, DataTypeConflictHandler.REPLACE_HANDLER);
  }

  private void annotateBaApplicationLifetimes() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    StructureDataType layout0 = new StructureDataType(category, "F33BaConfiguredOperation", 0);
    layout0.setPackingEnabled(true);
    StructureDataType layout1 = new StructureDataType(category, "F33BaApplicationWork", 0);
    layout1.setPackingEnabled(true);
    FunctionDefinitionDataType numeric = new FunctionDefinitionDataType(category, "F33BaNumericSource");
    numeric.setReturnType(v);
    numeric.setArguments(new ParameterDefinitionImpl("first", new PointerDataType(u32, 4), null), new ParameterDefinitionImpl("second", new PointerDataType(u32, 4), null));
    currentProgram.getDataTypeManager().addDataType(numeric, DataTypeConflictHandler.REPLACE_HANDLER);
    FunctionDefinitionDataType start = new FunctionDefinitionDataType(category, "F33BaStart");
    start.setReturnType(s32);
    start.setArguments(new ParameterDefinitionImpl("phase", u8, null), new ParameterDefinitionImpl("payload", new PointerDataType(u8, 4), null), new ParameterDefinitionImpl("output", new PointerDataType(u8, 4), null));
    currentProgram.getDataTypeManager().addDataType(start, DataTypeConflictHandler.REPLACE_HANDLER);
    FunctionDefinitionDataType finish = new FunctionDefinitionDataType(category, "F33BaFinish");
    finish.setReturnType(s32);
    currentProgram.getDataTypeManager().addDataType(finish, DataTypeConflictHandler.REPLACE_HANDLER);
    layout0.add(u8, "operation", "Exact field offset/width from instruction dataflow.");
    layout0.add(u8, "request_length", "Exact field offset/width from instruction dataflow.");
    layout0.add(u8, "response_body_length", "Exact field offset/width from instruction dataflow.");
    layout0.add(u8, "numeric_format", "Exact field offset/width from instruction dataflow.");
    layout0.add(new PointerDataType(numeric, 4), "numeric_source", "Null in every configured row; no numeric-source output used.");
    layout0.add(new PointerDataType(start, 4), "start", "Exact field offset/width from instruction dataflow.");
    layout0.add(new PointerDataType(finish, 4), "finish", "Exact field offset/width from instruction dataflow.");
    currentProgram.getDataTypeManager().addDataType(layout0, DataTypeConflictHandler.REPLACE_HANDLER);
    if (layout0.getLength() != 16) throw new IllegalStateException("F33BaConfiguredOperation extent drift");
    layout1.add(u8, "retained_start_phase", "Exact field offset/width from instruction dataflow.");
    layout1.add(u8, "selected_index", "Exact field offset/width from instruction dataflow.");
    layout1.add(u8, "opaque_02", "Exact field offset/width from instruction dataflow.");
    layout1.add(u8, "admission", "Exact field offset/width from instruction dataflow.");
    layout1.add(u8, "remaining_mode700_entries", "Exact field offset/width from instruction dataflow.");
    layout1.add(u8, "thermal_clear_phase", "Exact field offset/width from instruction dataflow.");
    layout1.add(u8, "staged_unsigned_override", "Exact field offset/width from instruction dataflow.");
    layout1.add(u8, "finished_projection_latch", "Exact field offset/width from instruction dataflow.");
    currentProgram.getDataTypeManager().addDataType(layout1, DataTypeConflictHandler.REPLACE_HANDLER);
    if (layout1.getLength() != 8) throw new IllegalStateException("F33BaApplicationWork extent drift");
  }

  private void annotateRetainedControlProfiles() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    StructureDataType layout0 = new StructureDataType(category, "F33RetainedControlProfile", 0);
    layout0.setPackingEnabled(true);
    layout0.add(u8, "scalar_kind", "Exact field offset/width from instruction dataflow.");
    layout0.add(new ArrayDataType(u8, 6, 1), "packed_metadata", "Exact field offset/width from instruction dataflow.");
    layout0.add(u8, "current_first_profile_validity", "Exact field offset/width from instruction dataflow.");
    layout0.add(u8, "current_elapsed_source_validity", "Exact field offset/width from instruction dataflow.");
    layout0.add(u8, "unwritten_09", "Gather never writes; not serialized.");
    layout0.add(u16, "integrated_source", "Exact field offset/width from instruction dataflow.");
    layout0.add(u16, "elapsed_groups", "Exact field offset/width from instruction dataflow.");
    layout0.add(u16, "source_u16_max", "Exact field offset/width from instruction dataflow.");
    layout0.add(u16, "source_u16_mean", "Exact field offset/width from instruction dataflow.");
    layout0.add(s16, "received_composite", "Exact field offset/width from instruction dataflow.");
    layout0.add(s16, "scaled_b054_max", "Exact field offset/width from instruction dataflow.");
    layout0.add(s16, "scaled_b054_mean", "Exact field offset/width from instruction dataflow.");
    layout0.add(s16, "capture_value", "Exact field offset/width from instruction dataflow.");
    layout0.add(s16, "f1c6_max", "Exact field offset/width from instruction dataflow.");
    layout0.add(s16, "f1c6_mean", "Exact field offset/width from instruction dataflow.");
    layout0.add(s16, "f1c8_max", "Exact field offset/width from instruction dataflow.");
    layout0.add(s16, "f1c8_mean", "Exact field offset/width from instruction dataflow.");
    layout0.add(s16, "f1ca_max", "Exact field offset/width from instruction dataflow.");
    layout0.add(s16, "f1ca_mean", "Exact field offset/width from instruction dataflow.");
    layout0.add(s16, "scaled_ae5c_max", "Exact field offset/width from instruction dataflow.");
    layout0.add(s16, "scaled_ae5c_min", "Exact field offset/width from instruction dataflow.");
    layout0.add(new ArrayDataType(u8, 2, 1), "unwritten_2a", "Gather never writes; not serialized.");
    layout0.add(u32, "route31_scalar", "Exact field offset/width from instruction dataflow.");
    layout0.add(s32, "scaled_f228", "Exact field offset/width from instruction dataflow.");
    currentProgram.getDataTypeManager().addDataType(layout0, DataTypeConflictHandler.REPLACE_HANDLER);
    if (layout0.getLength() != 52) throw new IllegalStateException("F33RetainedControlProfile extent drift");
  }

  private void annotateTaskProgressAndProfiling() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    StructureDataType layout0 = new StructureDataType(category, "F33TaskRateWindow", 0);
    layout0.setPackingEnabled(true);
    StructureDataType layout1 = new StructureDataType(category, "F33TaskRatePolicy", 0);
    layout1.setPackingEnabled(true);
    StructureDataType layout2 = new StructureDataType(category, "F33DmaProgressWindow", 0);
    layout2.setPackingEnabled(true);
    StructureDataType layout3 = new StructureDataType(category, "F33DmaProgressPolicy", 0);
    layout3.setPackingEnabled(true);
    StructureDataType layout4 = new StructureDataType(category, "F33ExecutionProfiles", 0);
    layout4.setPackingEnabled(true);
    layout0.add(u8, "phase", "Exact field offset/width from instruction dataflow.");
    layout0.add(u8, "count", "Exact field offset/width from instruction dataflow.");
    layout0.add(u8, "maximum", "Exact field offset/width from instruction dataflow.");
    layout0.add(u8, "minimum", "Exact field offset/width from instruction dataflow.");
    currentProgram.getDataTypeManager().addDataType(layout0, DataTypeConflictHandler.REPLACE_HANDLER);
    if (layout0.getLength() != 4) throw new IllegalStateException("F33TaskRateWindow extent drift");
    layout1.add(u8, "window", "Exact field offset/width from instruction dataflow.");
    layout1.add(u8, "minimum", "Exact field offset/width from instruction dataflow.");
    layout1.add(u8, "maximum", "Exact field offset/width from instruction dataflow.");
    layout1.add(u8, "opaque_03", "Exact field offset/width from instruction dataflow.");
    currentProgram.getDataTypeManager().addDataType(layout1, DataTypeConflictHandler.REPLACE_HANDLER);
    if (layout1.getLength() != 4) throw new IllegalStateException("F33TaskRatePolicy extent drift");
    layout2.add(u8, "phase", "Exact field offset/width from instruction dataflow.");
    layout2.add(u8, "opaque_01", "Exact field offset/width from instruction dataflow.");
    layout2.add(u16, "sum", "Exact field offset/width from instruction dataflow.");
    layout2.add(u16, "maximum", "Exact field offset/width from instruction dataflow.");
    layout2.add(u16, "minimum", "Exact field offset/width from instruction dataflow.");
    currentProgram.getDataTypeManager().addDataType(layout2, DataTypeConflictHandler.REPLACE_HANDLER);
    if (layout2.getLength() != 8) throw new IllegalStateException("F33DmaProgressWindow extent drift");
    layout3.add(u8, "channel", "Exact field offset/width from instruction dataflow.");
    layout3.add(u8, "window", "Exact field offset/width from instruction dataflow.");
    layout3.add(u16, "minimum", "Exact field offset/width from instruction dataflow.");
    layout3.add(u16, "maximum", "Exact field offset/width from instruction dataflow.");
    layout3.add(u16, "opaque_06", "Exact field offset/width from instruction dataflow.");
    currentProgram.getDataTypeManager().addDataType(layout3, DataTypeConflictHandler.REPLACE_HANDLER);
    if (layout3.getLength() != 8) throw new IllegalStateException("F33DmaProgressPolicy extent drift");
    layout4.add(new ArrayDataType(u32, 10, 4), "ch2_exclusive", "Exact field offset/width from instruction dataflow.");
    layout4.add(u32, "slot4_exclusive", "Exact field offset/width from instruction dataflow.");
    layout4.add(new ArrayDataType(u32, 16, 4), "foreground_exclusive", "Exact field offset/width from instruction dataflow.");
    layout4.add(new ArrayDataType(u32, 10, 4), "ch2_inclusive", "Exact field offset/width from instruction dataflow.");
    layout4.add(u32, "slot4_inclusive", "Exact field offset/width from instruction dataflow.");
    layout4.add(new ArrayDataType(u32, 16, 4), "foreground_inclusive", "Exact field offset/width from instruction dataflow.");
    layout4.add(u32, "idle_previous", "Exact field offset/width from instruction dataflow.");
    layout4.add(u32, "idle_accumulated", "Exact field offset/width from instruction dataflow.");
    layout4.add(u32, "idle_last", "Exact field offset/width from instruction dataflow.");
    layout4.add(new ArrayDataType(u32, 6, 4), "start", "Exact field offset/width from instruction dataflow.");
    layout4.add(new ArrayDataType(u32, 6, 4), "child_ticks", "Exact field offset/width from instruction dataflow.");
    layout4.add(new ArrayDataType(u16, 8, 2), "ch0_inclusive", "Exact field offset/width from instruction dataflow.");
    layout4.add(new ArrayDataType(u16, 8, 2), "ch1_exclusive", "Exact field offset/width from instruction dataflow.");
    layout4.add(new ArrayDataType(u16, 8, 2), "ch1_inclusive", "Exact field offset/width from instruction dataflow.");
    layout4.add(new ArrayDataType(u8, 4, 1), "ring_heads", "Exact field offset/width from instruction dataflow.");
    layout4.add(u8, "active", "Exact field offset/width from instruction dataflow.");
    layout4.add(new ArrayDataType(u8, 7, 1), "parent", "Exact field offset/width from instruction dataflow.");
    currentProgram.getDataTypeManager().addDataType(layout4, DataTypeConflictHandler.REPLACE_HANDLER);
    if (layout4.getLength() != 336) throw new IllegalStateException("F33ExecutionProfiles extent drift");
    getFunctionAt(toAddr(0x61940L)).setNoReturn(true);
    getFunctionAt(toAddr(0x64E2AL)).setInline(true);
  }

  private void annotateCanTpPayloadLifecycle() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType F33CanTpConfigurationType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33CanTpConfiguration");
    if (F33CanTpConfigurationType == null) throw new IllegalStateException("missing F33CanTpConfiguration");
    DataType F33CanTpFrameInfoType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33CanTpFrameInfo");
    if (F33CanTpFrameInfoType == null) throw new IllegalStateException("missing F33CanTpFrameInfo");
    DataType F33CanTpRxConnectionType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33CanTpRxConnection");
    if (F33CanTpRxConnectionType == null) throw new IllegalStateException("missing F33CanTpRxConnection");
    DataType F33CanTpRxStateType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33CanTpRxState");
    if (F33CanTpRxStateType == null) throw new IllegalStateException("missing F33CanTpRxState");
    DataType F33CanTpTxConnectionType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33CanTpTxConnection");
    if (F33CanTpTxConnectionType == null) throw new IllegalStateException("missing F33CanTpTxConnection");
    DataType F33CanTpTxStatePrefixType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33CanTpTxStatePrefix");
    if (F33CanTpTxStatePrefixType == null) throw new IllegalStateException("missing F33CanTpTxStatePrefix");
    DataType F33PduInfoType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33PduInfo");
    if (F33PduInfoType == null) throw new IllegalStateException("missing F33PduInfo");
    getFunctionAt(toAddr(0x7B452L)).setInline(true);
    getFunctionAt(toAddr(0x7B524L)).setInline(true);

  }

  private void annotateDcmQueuedDelivery() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    DataType F33DcmMessageContextType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33DcmMessageContext");
    if (F33DcmMessageContextType == null) throw new IllegalStateException("missing F33DcmMessageContext");
    DataType F33DcmResponseQueueType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33DcmResponseQueue");
    if (F33DcmResponseQueueType == null) throw new IllegalStateException("missing F33DcmResponseQueue");
    DataType F33DiagProprietaryMessageType = currentProgram.getDataTypeManager().getDataType("/CamryF33/F33DiagProprietaryMessage");
    if (F33DiagProprietaryMessageType == null) throw new IllegalStateException("missing F33DiagProprietaryMessage");
    StructureDataType layout0 = new StructureDataType(category, "F33DcmEventRing", 0);
    layout0.setPackingEnabled(true);
    StructureDataType layout1 = new StructureDataType(category, "F33DcmSoftwareTimer", 0);
    layout1.setPackingEnabled(true);
    StructureDataType layout2 = new StructureDataType(category, "F33DcmProprietaryContinuation", 0);
    layout2.setPackingEnabled(true);
    FunctionDefinitionDataType callback0 = new FunctionDefinitionDataType(category, "F33DcmEventCallback");
    callback0.setReturnType(v);
    callback0.setArguments(new ParameterDefinitionImpl("event_id", u8, null));
    currentProgram.getDataTypeManager().addDataType(callback0, DataTypeConflictHandler.REPLACE_HANDLER);
    FunctionDefinitionDataType callback1 = new FunctionDefinitionDataType(category, "F33DcmTimerCallback");
    callback1.setReturnType(v);
    callback1.setArguments(new ParameterDefinitionImpl("timer_slot", u8, null));
    currentProgram.getDataTypeManager().addDataType(callback1, DataTypeConflictHandler.REPLACE_HANDLER);
    layout0.add(u8, "producer", "Exact instruction-bound field extent.");
    layout0.add(u8, "consumer", "Exact instruction-bound field extent.");
    layout0.add(u8, "occupied_slots", "Exact instruction-bound field extent.");
    layout0.add(new ArrayDataType(u8, 31, 1), "event_ids", "FF tombstones remain occupied until popped.");
    currentProgram.getDataTypeManager().addDataType(layout0, DataTypeConflictHandler.REPLACE_HANDLER);
    if (layout0.getLength() != 34) throw new IllegalStateException("F33DcmEventRing extent drift");
    layout1.add(u32, "remaining", "Exact instruction-bound field extent.");
    layout1.add(u8, "active", "Only exactly1 is serviced.");
    layout1.add(new ArrayDataType(u8, 3, 1), "opaque_05", "Exact instruction-bound field extent.");
    currentProgram.getDataTypeManager().addDataType(layout1, DataTypeConflictHandler.REPLACE_HANDLER);
    if (layout1.getLength() != 8) throw new IllegalStateException("F33DcmSoftwareTimer extent drift");
    layout2.add(u8, "selected_index", "Exact instruction-bound field extent.");
    layout2.add(u8, "phase", "0 idle/begin;1 pending start join;2 finish join.");
    layout2.add(u8, "application_result", "Exact instruction-bound field extent.");
    layout2.add(u8, "side_result", "Exact instruction-bound field extent.");
    layout2.add(u8, "side_status", "Exact instruction-bound field extent.");
    layout2.add(new ArrayDataType(u8, 3, 1), "opaque_05", "Exact instruction-bound field extent.");
    currentProgram.getDataTypeManager().addDataType(layout2, DataTypeConflictHandler.REPLACE_HANDLER);
    if (layout2.getLength() != 8) throw new IllegalStateException("F33DcmProprietaryContinuation extent drift");
    getFunctionAt(toAddr(0x92A6EL)).setInline(true);
  }

  private void annotateCryptoBankLifetimes() throws Exception {
    CategoryPath category = new CategoryPath("/CamryF33");
    DataType v = VoidDataType.dataType;
    DataType u8 = UnsignedCharDataType.dataType;
    DataType u16 = UnsignedShortDataType.dataType;
    DataType u32 = UnsignedIntegerDataType.dataType;
    DataType s16 = ShortDataType.dataType;
    DataType s32 = IntegerDataType.dataType;
    getFunctionAt(toAddr(0x68FAAL)).setInline(true);
    getFunctionAt(toAddr(0x6915AL)).setInline(true);
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
    annotateBaApplicationLifetimes();
    annotateRetainedControlProfiles();
    annotateTaskProgressAndProfiling();
    annotateCanTpPayloadLifecycle();
    annotateDcmQueuedDelivery();
    annotateCryptoBankLifetimes();
    annotatePhaseModulation();
    annotateDataFlashReads();
    annotateFaciSubmission();
    annotatePwmCompareStaging();
    println("SeedCamryF33Semantics: seeded " + count
        + " evidence-backed entries; function/data semantics apply from registered tables");
  }
}
