//@author kaikozlov
//@category Analysis
// Throwaway: materialize the yc Venza RPRG runtime into the RuntimeRAM block
// so GP/TP-cell indirect calls resolve, and set TP=0xFEC03020 in register
// context (GP=0xFEC0102C is already active).
//
// Relocation rows (yc report §1 + §5.1):
//   FEBF0924 <- ExtendedUser 0x01000000..0x01007588  (boot.bin[0:0x7588])
//   FEBFBF90 <- ExtendedUser 0x01007588..0x01007BD0  (boot.bin[0x7588:0x7BD0])
//   FEBFB770 <- CodeFlash    0xBBAC..0xC3CC          (cflash.bin same range)

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.Memory;

public class ApplyVenzaRprgRelocations extends GhidraScript {
    private static final long EU = 0x01000000L;
    private static final long CF = 0L;

    private void move(long dst, long src, int len) throws Exception {
        Memory m = currentProgram.getMemory();
        Address d = toAddr(dst);
        var blk = m.getBlock(d);
        if (blk != null && !blk.isInitialized()) {
            boolean r = blk.isRead();
            boolean w = blk.isWrite();
            boolean x = blk.isExecute();
            m.removeBlock(blk, monitor);
            blk = m.createInitializedBlock("RuntimeRAM", d, 0x30000L, (byte) 0,
                monitor, false);
            blk.setRead(r);
            blk.setWrite(w);
            blk.setExecute(x);
            println("recreated RuntimeRAM as initialized");
        }
        byte[] buf = new byte[len];
        m.getBytes(toAddr(src), buf);
        m.setBytes(d, buf);
        println(String.format("moved %08x <- %08x len=0x%x", dst, src, len));
    }
    @Override

    public void run() throws Exception {
        move(0xFEBF0924L, EU, 0x7588);
        move(0xFEBFBF90L, EU + 0x7588, 0x7BD0 - 0x7588);
        move(0xFEBFB770L, CF + 0xBBAC, 0xC3CC - 0xBBAC);

        // TP register context across the whole program (v850 tp).
        var ctx = currentProgram.getProgramContext();
 for (var r : ctx.getRegisters()) {
            if (r.getName().equalsIgnoreCase("tp")) {
                var v = new ghidra.program.model.lang.RegisterValue(r, java.math.BigInteger.valueOf(0xFEC03020L));
                ctx.setRegisterValue(r.getAddressSpace().getMinAddress(), r.getAddressSpace().getMaxAddress(), v);
            }
        }
        println("done");
    }
}
