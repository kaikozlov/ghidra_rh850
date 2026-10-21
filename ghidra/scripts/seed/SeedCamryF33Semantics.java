//@author kaikozlov
//@category Seed
// Structural repairs and annotation replay from the curated Camry source maps.
// Function discovery remains owned by function_seeds.csv; source ranges are not replayed.
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.app.cmd.function.ApplyFunctionSignatureCmd;
import ghidra.app.cmd.function.FunctionRenameOption;
import ghidra.app.util.parser.FunctionSignatureParser;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import com.google.gson.*;
import java.io.*;
import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class SeedCamryF33Semantics extends GhidraScript {
  private static final CategoryPath TYPES = new CategoryPath("/CamryF33");
  private final Map<String, DataType> types = new LinkedHashMap<>();
  private final Map<Long, String> objectTypes = new LinkedHashMap<>();
  private final Set<Long> seededEntries = new LinkedHashSet<>();

  private JsonObject readObject(File file) throws Exception {
    try (Reader reader = Files.newBufferedReader(file.toPath(), StandardCharsets.UTF_8)) {
      return JsonParser.parseReader(reader).getAsJsonObject();
    }
  }

  private List<JsonObject> readRows(File file) throws Exception {
    List<JsonObject> rows = new ArrayList<>();
    try (BufferedReader reader = Files.newBufferedReader(file.toPath(), StandardCharsets.UTF_8)) {
      String line;
      while ((line = reader.readLine()) != null) {
        monitor.checkCancelled();
        if (!line.isBlank())
          rows.add(JsonParser.parseString(line).getAsJsonObject());
      }
    }
    return rows;
  }

  private long number(String value) {
    return Long.decode(value);
  }

  private void alias(String name, DataType type) {
    types.put(name, new TypedefDataType(TYPES, name, type, currentProgram.getDataTypeManager()));
  }

  private DataType type(String spelling) {
    return type(spelling.replaceAll("\\s+", ""), new HashSet<>());
  }

  private DataType type(String spelling, Set<Long> seen) {
    if (spelling.startsWith("@")) {
      long address = number(spelling.substring(1));
      String target = objectTypes.get(address);
      if (target == null || !seen.add(address))
        throw new IllegalArgumentException("unresolved object type " + spelling);
      return type(target.replaceAll("\\s+", ""), seen);
    }
    int array = spelling.indexOf('[');
    if (array >= 0) {
      DataType result = type(spelling.substring(0, array), seen);
      List<Integer> dimensions = new ArrayList<>();
      Matcher matcher = Pattern.compile("\\[(\\d+)\\]").matcher(spelling.substring(array));
      int end = 0;
      while (matcher.find()) {
        if (matcher.start() != end)
          throw new IllegalArgumentException("invalid array type " + spelling);
        dimensions.add(Integer.parseInt(matcher.group(1)));
        end = matcher.end();
      }
      if (end != spelling.length() - array)
        throw new IllegalArgumentException("invalid array type " + spelling);
      // C dimensions are outermost first: u16[2][3] is two arrays of three.
      for (int i = dimensions.size() - 1; i >= 0; --i)
        result = new ArrayDataType(result, dimensions.get(i), result.getLength(),
            currentProgram.getDataTypeManager());
      return result;
    }
    if (spelling.endsWith("*32"))
      return new PointerDataType(type(spelling.substring(0, spelling.length() - 3), seen),
          4, currentProgram.getDataTypeManager());
    if (spelling.endsWith("*"))
      return new PointerDataType(type(spelling.substring(0, spelling.length() - 1), seen),
          4, currentProgram.getDataTypeManager());
    DataType result = types.get(spelling);
    if (result == null)
      throw new IllegalArgumentException("unresolved source datatype " + spelling);
    return result;
  }

  private void replayTypes(JsonObject layouts) throws Exception {
    types.put("void", VoidDataType.dataType);
    types.put("byte", ByteDataType.dataType);
    types.put("sbyte", SignedByteDataType.dataType);
    types.put("uchar", UnsignedCharDataType.dataType);
    types.put("ushort", UnsignedShortDataType.dataType);
    types.put("short", ShortDataType.dataType);
    types.put("uint", UnsignedIntegerDataType.dataType);
    types.put("int", IntegerDataType.dataType);
    types.put("undefined", DataType.DEFAULT);
    for (int width = 1; width <= 8; ++width)
      types.put("undefined" + width, Undefined.getUndefinedDataType(width));
    alias("u8", types.get("uchar"));
    alias("u16", types.get("ushort"));
    alias("u32", types.get("uint"));
    alias("s8", types.get("sbyte"));
    alias("s16", types.get("short"));
    alias("s32", types.get("int"));
    // Only names survive for these callback targets. An opaque target typedef
    // preserves a named 32-bit pointer without asserting a callable prototype.
    for (JsonElement element : layouts.getAsJsonArray("functions")) {
      String name = element.getAsString();
      alias(name, Undefined1DataType.dataType);
    }
    for (JsonElement element : layouts.getAsJsonArray("enums")) {
      JsonObject row = element.getAsJsonObject();
      String name = row.get("name").getAsString();
      EnumDataType enumeration = new EnumDataType(TYPES, name, row.get("size").getAsInt(),
          currentProgram.getDataTypeManager());
      types.put(name, enumeration);
    }
    // Allocate every full-size shell before resolving recursive pointers or
    // by-value members. Packing must not move the retained explicit offsets.
    for (JsonElement element : layouts.getAsJsonArray("structs")) {
      JsonObject row = element.getAsJsonObject();
      String name = row.get("name").getAsString();
      StructureDataType structure = new StructureDataType(TYPES, name, row.get("size").getAsInt(),
          currentProgram.getDataTypeManager());
      structure.setPackingEnabled(false);
      types.put(name, structure);
    }
    for (JsonElement element : layouts.getAsJsonArray("structs")) {
      monitor.checkCancelled();
      JsonObject row = element.getAsJsonObject();
      Structure structure = (Structure) types.get(row.get("name").getAsString());
      for (JsonElement fieldElement : row.getAsJsonArray("fields")) {
        JsonObject field = fieldElement.getAsJsonObject();
        String spelling = field.get("type").getAsString();
        DataType fieldType = type(spelling);
        int size = field.get("size").getAsInt();
        int offset = field.get("offset").getAsInt();
        if (fieldType.getLength() != size && spelling.matches("undefined\\d+")) {
          println("SeedCamryF33Semantics: opaque width " + structure.getName() + "."
              + field.get("name").getAsString() + ": " + spelling + " -> " + size + " bytes");
          fieldType = Undefined.getUndefinedDataType(size);
        }
        if (fieldType.getLength() != size || offset < 0 || offset + size > structure.getLength())
          throw new IllegalArgumentException("source field layout mismatch " + row.get("name")
              + "." + field.get("name"));
        structure.replaceAtOffset(offset, fieldType, size, field.get("name").getAsString(), null);
      }
    }
    DataTypeManager manager = currentProgram.getDataTypeManager();
    for (Map.Entry<String, DataType> entry : types.entrySet())
      entry.setValue(manager.addDataType(entry.getValue(), DataTypeConflictHandler.REPLACE_HANDLER));
    println("SeedCamryF33Semantics: retained "
        + layouts.getAsJsonArray("functions").size() + " opaque callback target names and "
        + layouts.getAsJsonArray("enums").size() + " enum widths without inventing prototypes/values");
  }

  private void replayAnnotations(File source) throws Exception {
    List<JsonObject> objects = readRows(new File(source, "data.jsonl"));
    for (JsonObject row : objects)
      objectTypes.put(number(row.get("addr").getAsString()), row.get("type").getAsString());
    replayTypes(readObject(new File(source, "struct_layouts.json")));
    FunctionSignatureParser parser =
        new FunctionSignatureParser(currentProgram.getDataTypeManager(), null);
    int names = 0, signatures = 0, dataTypes = 0;
    AddressSet protectedCode = new AddressSet();
    MemoryBlock relocated = currentProgram.getMemory().getBlock("F33BootFlashDriver");
    for (JsonObject row : readRows(new File(source, "symbols.jsonl"))) {
      monitor.checkCancelled();
      long offset = number(row.get("addr").getAsString());
      Address address = offset >= relocated.getStart().getOffset()
          && offset <= relocated.getEnd().getOffset()
          ? relocated.getStart().add(offset - relocated.getStart().getOffset()) : toAddr(offset);
      Function function = getFunctionAt(address);
      if (function == null)
        throw new IllegalStateException("source annotation has no discovered function " + address);
      protectedCode.add(function.getBody());
      for (JsonElement element : row.getAsJsonArray("ranges")) {
        JsonArray range = element.getAsJsonArray();
        protectedCode.add(address.getAddressSpace().getAddress(range.get(0).getAsLong()),
            address.getAddressSpace().getAddress(range.get(1).getAsLong()));
      }
      String name = row.get("name").getAsString();
      if (!name.matches("FUN_[0-9a-fA-F]+")) {
        function.setName(name, SourceType.USER_DEFINED);
        names++;
      }
      String signature = row.get("signature").getAsString();
      // undefined f() indicates that the contract remains unrecovered.
      if (signature.equals("undefined " + row.get("name").getAsString() + "()"))
        continue;
      FunctionDefinitionDataType definition = parser.parse(null, signature);
      ApplyFunctionSignatureCmd command = new ApplyFunctionSignatureCmd(address, definition,
          SourceType.USER_DEFINED, true, false, DataTypeConflictHandler.REPLACE_HANDLER,
          FunctionRenameOption.NO_CHANGE);
      if (!command.applyTo(currentProgram, monitor))
        throw new IllegalStateException("signature replay failed at " + address + ": "
            + command.getStatusMsg());
      signatures++;
    }
    for (long entry : seededEntries) {
      Function function = getFunctionAt(toAddr(entry));
      if (function != null)
        protectedCode.add(function.getBody());
    }
    // Later curated rows take priority where boot/application lifetimes or old
    // table extents overlap. Keep all labels, but never pretend both listing
    // types can coexist or let annotation replay overwrite structural code.
    AddressSet claimed = new AddressSet();
    Listing listing = currentProgram.getListing();
    for (int i = objects.size() - 1; i >= 0; --i) {
      monitor.checkCancelled();
      JsonObject row = objects.get(i);
      Address address = toAddr(number(row.get("addr").getAsString()));
      DataType objectType = type(row.get("type").getAsString());
      Address end = address.add(objectType.getLength() - 1L);
      AddressSet span = new AddressSet(address, end);
      if (claimed.intersects(span)) {
        println("SeedCamryF33Semantics: overlapping listing type not applied: " + row);
        continue;
      }
      Instruction first = listing.getInstructionContaining(address);
      Instruction last = listing.getInstructionContaining(end);
      Address clearStart = first == null ? address : first.getMinAddress();
      Address clearEnd = last == null ? end : last.getMaxAddress();
      AddressSet clearSpan = new AddressSet(clearStart, clearEnd);
      if (protectedCode.intersects(clearSpan))
        throw new IllegalStateException("source data overlaps retained/structural code: " + row);
      // Analysis may have disassembled constant tables. Curated data wins only
      // outside retained ranges and repaired/discovered function bodies.
      List<Address> falseEntries = new ArrayList<>();
      Iterator<Function> overlaps =
          currentProgram.getFunctionManager().getFunctionsOverlapping(clearSpan);
      while (overlaps.hasNext()) {
        Function function = overlaps.next();
        SourceType provenance = function.getSymbol().getSource();
        if (provenance != SourceType.DEFAULT && provenance != SourceType.ANALYSIS)
          throw new IllegalStateException("source data overlaps nonautomatic function "
              + function.getEntryPoint() + ": " + row);
        falseEntries.add(function.getEntryPoint());
      }
      for (Address entry : falseEntries)
        currentProgram.getFunctionManager().removeFunction(entry);
      listing.clearCodeUnits(clearStart, clearEnd, false);
      createData(address, objectType);
      claimed.add(span);
      dataTypes++;
    }
    for (JsonObject row : objects) {
      Address address = toAddr(number(row.get("addr").getAsString()));
      String name = row.get("name").getAsString();
      Symbol symbol = currentProgram.getSymbolTable().getSymbol(name, address, null);
      if (symbol == null)
        symbol = currentProgram.getSymbolTable().createLabel(address, name, SourceType.USER_DEFINED);
      symbol.setPrimary();
    }
    println("SeedCamryF33Semantics: replayed " + names + " names, " + signatures
        + " signatures, " + objects.size() + " data labels and " + dataTypes + " listing types");
  }

  private void ensure(long value) throws Exception {
    Address address = toAddr(value);
    Listing listing = currentProgram.getListing();
    Instruction containing = listing.getInstructionContaining(address);
    if (containing != null && !containing.getMinAddress().equals(address))
      listing.clearCodeUnits(containing.getMinAddress(), containing.getMaxAddress(), false);
    CodeUnit unit = listing.getCodeUnitContaining(address);
    if (unit != null && !(unit instanceof Instruction))
      listing.clearCodeUnits(unit.getMinAddress(), unit.getMaxAddress(), false);
    if (listing.getInstructionAt(address) == null && !disassemble(address))
      throw new IllegalStateException("disassembly failed " + address);
    Function function = currentProgram.getFunctionManager().getFunctionAt(address);
    if (function == null)
      function = createFunction(address, null);
    if (function == null)
      throw new IllegalStateException("function creation failed " + address);
    seededEntries.add(value);
  }

  private void repairCodeTail(long entry, long tail, long last) throws Exception {
    Function function = getFunctionAt(toAddr(entry));
    if (function == null)
      throw new IllegalStateException("missing repair entry " + toAddr(entry));
    currentProgram.getListing().clearCodeUnits(toAddr(tail), toAddr(last), false);
    if (!disassemble(toAddr(tail)))
      throw new IllegalStateException("failed to recover code tail " + toAddr(tail));
    function.setBody(new AddressSet(toAddr(entry), toAddr(last)));
  }

  private void forceData(long address, int length) throws Exception {
    Address start = toAddr(address);
    currentProgram.getFunctionManager().removeFunction(start);
    currentProgram.getListing().clearCodeUnits(start, start.add(length - 1L), false);
    createData(start, new ArrayDataType(ByteDataType.dataType, length, 1));
  }

  private void recoverBootRelocation() throws Exception {
    Memory memory = currentProgram.getMemory();
    // 35E4 copies these words before 36D4 calls the TP+4C callback.
    byte[] code = new byte[0x32C];
    memory.getBytes(toAddr(0x8370L), code);
    // Application crypto later owns the same physical RAM. Keep this boot-only
    // snapshot in its own space, never initialize or alias the ordinary LocalRAM.
    String name = "F33BootFlashDriver";
    MemoryBlock block = memory.getBlock(name);
    if (block == null)
      block = memory.createInitializedBlock(name, toAddr(0xFEBF1000L),
          new ByteArrayInputStream(code), code.length, monitor, true);
    Address start = block.getStart();
    if (!start.getAddressSpace().isOverlaySpace() || start.getOffset() != 0xFEBF1000L
        || block.getSize() != code.length || !block.isInitialized())
      throw new IllegalStateException("unexpected F33 boot relocation block");
    byte[] existing = new byte[code.length];
    memory.getBytes(start, existing);
    if (!Arrays.equals(code, existing))
      throw new IllegalStateException("F33 boot relocation bytes differ");
    block.setRead(true);
    block.setWrite(true);
    block.setExecute(true);
    block.setSourceName("CodeFlash 00008370..0000869b copied at 000035e4 (boot phase)");
    currentProgram.getProgramContext().setValue(currentProgram.getRegister("gp"),
        start, block.getEnd(), BigInteger.valueOf(0xFEBF9800L));
    currentProgram.getProgramContext().setValue(currentProgram.getRegister("tp"),
        start, block.getEnd(), BigInteger.valueOf(0x869CL));
    // Exact ROM bodies, translated without patching PC-relative instructions.
    long[][] bodies = {
      {0x8370L, 0x8399L}, {0x84F8L, 0x851BL}, {0x851CL, 0x8541L},
      {0x8542L, 0x855FL}, {0x8560L, 0x8627L}, {0x8628L, 0x869BL}
    };
    for (long[] body : bodies) {
      Address entry = start.add(body[0] - 0x8370L);
      AddressSet bounds = new AddressSet(entry, start.add(body[1] - 0x8370L));
      if (getInstructionAt(entry) == null
          && !new DisassembleCommand(entry, bounds, true).applyTo(currentProgram, monitor))
        throw new IllegalStateException("boot relocation disassembly failed " + entry);
      Function function = getFunctionAt(entry);
      if (function == null)
        function = createFunction(entry, "boot_relocated_" + Long.toHexString(body[0]));
      if (function == null)
        throw new IllegalStateException("boot relocation function failed " + entry);
      function.setBody(bounds);
    }
    Address callback = start.add(0x2B8);
    var refs = currentProgram.getReferenceManager();
    for (Reference ref : refs.getReferencesFrom(toAddr(0x36D4L)))
      if (ref.getToAddress().equals(toAddr(0xFEBF12B8L)) && ref.getReferenceType().isCall())
        refs.delete(ref);
    Reference call = refs.addMemoryReference(toAddr(0x36D4L), callback,
        RefType.CALL_OVERRIDE_UNCONDITIONAL, SourceType.USER_DEFINED, 0);
    refs.setPrimary(call, true);
    Address ordinary = toAddr(0xFEBF12B8L);
    Function placeholder = getFunctionAt(ordinary);
    if (placeholder != null && placeholder.getBody().getNumAddresses() == 1
        && getInstructionAt(ordinary) == null)
      currentProgram.getFunctionManager().removeFunction(ordinary);
  }

  @Override
  public void run() throws Exception {
    String[] args = getScriptArgs();
    if (args.length < 1 || args.length > 2)
      throw new IllegalArgumentException("expected function_seeds.csv path [decomp source directory]");
    File file = new File(args[0]);
    if (!file.isFile())
      throw new IllegalStateException("missing seed file " + file);
    File seedDirectory = file.getCanonicalFile().getParentFile();
    File source = args.length == 2 ? new File(args[1])
        : new File(seedDirectory.getParentFile().getParentFile().getParentFile(),
            "decomp/" + seedDirectory.getName());
    // A false instruction at 50000 overlapped this callback's four-byte entry.
    currentProgram.getListing().clearCodeUnits(toAddr(0x4FFFEL), toAddr(0x50025L), false);
    ensure(0x4FFFEL);
    getFunctionAt(toAddr(0x4FFFEL)).setBody(new AddressSet(toAddr(0x4FFFEL), toAddr(0x50025L)));
    int count = 0;
    try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
      if (!"address,provenance,note".equals(reader.readLine()))
        throw new IllegalStateException("seed CSV header drift");
      String line;
      while ((line = reader.readLine()) != null) {
        if (line.isBlank())
          continue;
        String[] fields = line.split(",", 3);
        if (fields.length != 3 || fields[1].isBlank())
          throw new IllegalStateException("invalid seed row: " + line);
        ensure(Long.parseLong(fields[0].replace("0x", ""), 16));
        count++;
      }
    }
    repairCodeTail(0x802L, 0x83CL, 0x87FL);
    // 0xD48 is inside MULHI at 0xD46.
    repairCodeTail(0xC9AL, 0xD46L, 0xE53L);
    // Undefined data at 0x8374 covered the copied-code dispatcher.
    repairCodeTail(0x8370L, 0x8374L, 0x8399L);
    // Curve row 0x18108 was misclassified as JMP TP. 0x88 bytes is two 0x44-byte rows.
    forceData(0x18100L, 0x88);
    // Eight-byte EIIC records at TP. 8 records * 8 bytes.
    forceData(0x869CL, 0x40);
    // 0x33966 is fall-through after DIVQ, sharing PREPARE at 0x336B8 and DISPOSE at 0x33AA0.
    currentProgram.getFunctionManager().removeFunction(toAddr(0x33966L));
    Function fit = getFunctionAt(toAddr(0x336B8L));
    if (fit == null)
      throw new IllegalStateException("missing six-channel fit root");
    fit.setBody(new AddressSet(toAddr(0x336B8L), toAddr(0x33AA3L)));
    recoverBootRelocation();
    replayAnnotations(source);
    println("SeedCamryF33Semantics: seeded " + count + " entries and structural boundaries");
  }
}
