//@author kaikozlov
//@category Analysis
// (1) Classify the secrets region, (2) report overall code/data/undefined coverage,
// (3) exhaustively scan the whole image for any stored 4-byte LE word whose value
//     lies in [0x13f00..0x14100] (i.e. any stored pointer to the secrets region).
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.*;

public class RegionReport extends GhidraScript {
    @Override
    public void run() throws Exception {
        long lo = 0x13f00L, hi = 0x14100L;
        Listing listing = currentProgram.getListing();
        Memory mem = currentProgram.getMemory();
        AddressSpace space = currentProgram.getAddressFactory().getDefaultAddressSpace();

        // (1) classify secrets region 0x13f00..0x14100
        int ins=0, data=0, undef=0;
        Address a = space.getAddress(lo);
        Address e = space.getAddress(hi);
        CodeUnitIterator cu = listing.getCodeUnits(a, true);
        while (cu.hasNext()) {
            CodeUnit u = cu.next();
            if (u.getMinAddress().compareTo(e) > 0) break;
            if (u instanceof Instruction) ins++;
            else if (u instanceof Data) data++;
            else undef++;
        }
        println("RegionReport: secrets region [0x13f00..0x14100]: ins="+ins+" data="+data+" undef="+undef);

        // (2) overall coverage
        long insBytes=0, dataBytes=0, undefBytes=0;
        CodeUnitIterator all = listing.getCodeUnits(true);
        while (all.hasNext()) {
            CodeUnit u = all.next();
            long len = u.getLength();
            if (u instanceof Instruction) insBytes += len;
            else if (u instanceof Data) dataBytes += len;
            else undefBytes += len;
        }
        println("  coverage: instr="+insBytes+"B  data="+dataBytes+"B  undef="+undefBytes+"B  total="+(insBytes+dataBytes+undefBytes)+"B");

        // (3) exhaustive scan for stored 4-byte LE words in [lo..hi] (anywhere, any alignment)
        MemoryBlock block = mem.getBlock(space.getAddress(0L));
        long size = block.getSize();
        byte[] buf = new byte[(int) size];
        block.getBytes(space.getAddress(0L), buf);
        int hits = 0;
        java.util.List<String> sample = new java.util.ArrayList<>();
        for (int off = 0; off + 4 <= buf.length; off++) {
            long v = ((buf[off] & 0xff))
                   | ((buf[off+1] & 0xff) << 8)
                   | ((buf[off+2] & 0xff) << 16)
                   | ((long)(buf[off+3] & 0xff) << 24);
            if (v >= lo && v <= hi) {
                hits++;
                if (sample.size() < 25) sample.add(String.format("  @0x%06x  word=0x%08x", off, v));
            }
        }
        println("  stored 4-byte LE words in [0x13f00..0x14100]: " + hits);
        for (String s : sample) println(s);
    }
}
