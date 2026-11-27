//@author kaikozlov
//@category Seed
// Seed exact-H entries that transfer to F through byte-identical application bytes.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.SourceType;
import java.io.*;

public class SeedCorollaHFRecoveredFunctions extends GhidraScript {
  private Function ensure(long value) throws Exception {
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
    if (function == null) function = createFunction(address, null);
    if (function == null) throw new IllegalStateException("function creation failed " + address);
    return function;
  }

  @Override public void run() throws Exception {
    String[] args = getScriptArgs();
    if (args.length != 1) throw new IllegalArgumentException("expected function_seeds.csv path");
    File file = new File(args[0]);
    if (!file.isFile()) throw new IllegalStateException("missing seed file " + file);
    int count = 0;
    try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
      if (!"address,provenance,note".equals(reader.readLine()))
        throw new IllegalStateException("seed CSV header drift");
      String line;
      while ((line = reader.readLine()) != null) {
        if (line.isBlank()) continue;
        String[] fields = line.split(",", 3);
        if (fields.length != 3 || fields[1].isBlank())
          throw new IllegalStateException("invalid seed row: " + line);
        long value = Long.parseLong(fields[0].replace("0x", ""), 16);
        if (value < 0x20000L || value >= 0x100000L)
          throw new IllegalStateException("non-application seed " + fields[0]);
        Function function = ensure(value);
        if (fields[2].startsWith("name=")) {
          int end = fields[2].indexOf(';');
          if (end < 6) throw new IllegalStateException("invalid named seed row: " + line);
          function.setName(fields[2].substring(5, end), SourceType.USER_DEFINED);
        }
        count++;
      }
    }
    if (count == 0) throw new IllegalStateException("empty seed file");
    println("SeedCorollaHFRecoveredFunctions: seeded " + count +
      " evidence-backed shared-application entries");
  }
}
