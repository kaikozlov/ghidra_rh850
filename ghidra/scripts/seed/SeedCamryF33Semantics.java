//@author kaikozlov
//@category Seed
// Structural Camry F33 repairs required for a from-scratch rebuild.
// Names and C live in decomp/camry-8965F3307000/. This script does not apply comments.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.data.ArrayDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.listing.*;
import java.io.*;

public class SeedCamryF33Semantics extends GhidraScript {
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

  @Override
  public void run() throws Exception {
    String[] args = getScriptArgs();
    if (args.length != 1)
      throw new IllegalArgumentException("expected function_seeds.csv path");
    File file = new File(args[0]);
    if (!file.isFile())
      throw new IllegalStateException("missing seed file " + file);
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
    // 0xD48 is inside MULHI at 0xD46, not an entry.
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
    println("SeedCamryF33Semantics: seeded " + count + " entries and structural boundaries");
  }
}
