//@author kaikozlov
//@category Analysis
// Normalize the block at 0x0 as CodeFlash and attach an optional extended-user
// image at a registered base (e.g. boot.bin at 0x01000000).
// Unlike AddDataFlash this makes no P1M-E assumption: the CodeFlash block may be
// any size and the extended-user area is read/execute like the code area.
// Usage: AddExtendedUser.java /absolute/path/to/boot.bin <baseHex> <sizeHex>
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import java.io.File;
import java.io.FileInputStream;

public class AddExtendedUser extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 3) {
            throw new IllegalArgumentException("expected <extended-user .bin path> <baseHex> <sizeHex>");
        }
        File input = new File(args[0]);
        long base = Long.parseLong(args[1].replace("0x", ""), 16);
        long size = Long.parseLong(args[2].replace("0x", ""), 16);
        if (!input.isFile() || input.length() != size) {
            throw new IllegalArgumentException(
                "extended-user image must exist and be exactly 0x" + Long.toHexString(size)
                + " bytes: " + input);
        }

        Memory mem = currentProgram.getMemory();
        Address codeStart = toAddr(0x00000000L);
        MemoryBlock code = mem.getBlock(codeStart);
        if (code == null) {
            throw new IllegalStateException("expected a code block at 0x0");
        }
        code.setName("CodeFlash");
        code.setRead(true);
        code.setWrite(false);
        code.setExecute(true);

        Address extStart = toAddr(base);
        MemoryBlock old = mem.getBlock(extStart);
        if (old != null) {
            println("Extended-user already mapped: " + old.getStart() + ".." + old.getEnd());
            return;
        }
        try (FileInputStream in = new FileInputStream(input)) {
            MemoryBlock ext = mem.createInitializedBlock(
                "ExtendedUser", extStart, in, size, monitor, false);
            ext.setRead(true);
            ext.setWrite(false);
            ext.setExecute(true);
            println("Mapped CodeFlash 0x0.." + code.getEnd()
                + " and ExtendedUser " + ext.getStart() + ".." + ext.getEnd());
        }
    }
}
