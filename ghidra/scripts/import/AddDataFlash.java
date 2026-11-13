//@author kaikozlov
//@category Analysis
// Attach a DataFlash image at its registered base and size.
// Usage: AddDataFlash.java /absolute/path/to/dflash.bin <baseHex> <sizeHex>
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import java.io.File;
import java.io.FileInputStream;

public class AddDataFlash extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 3) {
            throw new IllegalArgumentException("expected <DataFlash .bin path> <baseHex> <sizeHex>");
        }
        File input = new File(args[0]);
        long base = Long.parseLong(args[1].replace("0x", ""), 16);
        long size = Long.parseLong(args[2].replace("0x", ""), 16);
        if (!input.isFile() || input.length() != size) {
            throw new IllegalArgumentException(
                "DataFlash must exist and be exactly 0x" + Long.toHexString(size)
                + " bytes: " + input);
        }

        Memory mem = currentProgram.getMemory();
        Address codeStart = toAddr(0x00000000L);
        MemoryBlock code = mem.getBlock(codeStart);
        if (code == null) {
            throw new IllegalStateException("expected a CodeFlash block at 0x0");
        }
        code.setName("CodeFlash");
        code.setRead(true);
        code.setWrite(false);
        code.setExecute(true);

        Address dataStart = toAddr(base);
        MemoryBlock old = mem.getBlock(dataStart);
        if (old != null) {
            println("DataFlash already mapped: " + old.getStart() + ".." + old.getEnd());
            return;
        }
        try (FileInputStream in = new FileInputStream(input)) {
            MemoryBlock data = mem.createInitializedBlock(
                "DataFlash", dataStart, in, size, monitor, false);
            data.setRead(true);
            data.setWrite(true);
            data.setExecute(false);
            println("Mapped CodeFlash 0x0.." + code.getEnd()
                    + " and DataFlash " + data.getStart() + ".." + data.getEnd());
        }
    }
}
