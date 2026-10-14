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
    println("SeedCamryF33RecoveredFunctions: seeded " + count
        + " evidence-backed entries and applied exact-F33 semantic prototypes");
  }
}
