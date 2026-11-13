//@author kaikozlov
//@category Seed
// Existence-only recovery followed by repeatable target semantics. The normal
// rebuild runs this both before analysis and in its final no-analysis pass.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.HashSet;
import java.util.Set;

public class SeedR4pMeterRecoveredFunctions extends GhidraScript {
  private void ensure(long value) throws Exception {
    Address address = toAddr(value);
    var block = currentProgram.getMemory().getBlock(address);
    if ((value & 1) != 0 || block == null || !block.isInitialized() || !block.isExecute())
      throw new IllegalStateException("meter seed outside initialized executable memory " + address);
    Listing listing = currentProgram.getListing();
    Instruction containing = listing.getInstructionContaining(address);
    if (containing != null && !containing.getMinAddress().equals(address))
      listing.clearCodeUnits(containing.getMinAddress(), containing.getMaxAddress(), false);
    CodeUnit unit = listing.getCodeUnitContaining(address);
    if (unit != null && !(unit instanceof Instruction))
      listing.clearCodeUnits(unit.getMinAddress(), unit.getMaxAddress(), false);
    if (listing.getInstructionAt(address) == null && !disassemble(address))
      throw new IllegalStateException("disassembly failed " + address);
    Function function = getFunctionAt(address);
    if (function == null) function = createFunction(address, null);
    if (function == null) throw new IllegalStateException("function creation failed " + address);
  }

  @Override public void run() throws Exception {
    String[] args = getScriptArgs();
    if (args.length != 1) throw new IllegalArgumentException("expected function_seeds.csv path");
    File file = new File(args[0]);
    if (!file.isFile()) throw new IllegalStateException("missing seed file " + file);
    Set<Long> entries = new HashSet<>();
    try (BufferedReader reader = Files.newBufferedReader(file.toPath(), StandardCharsets.UTF_8)) {
      if (!"address,provenance,note".equals(reader.readLine()))
        throw new IllegalStateException("seed CSV header drift");
      String line;
      while ((line = reader.readLine()) != null) {
        if (line.isBlank()) continue;
        String[] fields = line.split(",", 3);
        if (fields.length != 3 || fields[1].isBlank() || fields[2].isBlank())
          throw new IllegalStateException("invalid seed row: " + line);
        long value = Long.parseLong(fields[0].replace("0x", ""), 16);
        if (!entries.add(value)) throw new IllegalStateException("duplicate meter seed " + fields[0]);
        ensure(value); // Never assign speculative semantic names from a CSV.
      }
    }
    if (entries.isEmpty()) throw new IllegalStateException("empty meter seed file");
    // Reapply tables as DATA, exact primitive arities, and returning-fill/caller
    // repairs after the last analyzer pass as well as during initial seeding.
    runScript("SeedR4pMeterDiagnostics.java", new String[0]);
    println("SeedR4pMeterRecoveredFunctions: seeded " + entries.size() + " verified entries and finalized meter semantics");
  }
}
