// Extract per-ECU Feistel key tables from CommandCommon.dll
// @category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.mem.*;

public class ExtractFeistelKeys extends GhidraScript {
    @Override
    public void run() throws Exception {
        // ECU tables from SetCommonKey decompilation
        long[][] tables = {
            {0x100B1CE8, 0x100B1D30},  // 0x353 level 3
            {0x100B2130, 0x100B2178},  // 0x353 level 0x14
            {0x100B2578, 0x100B25C0},  // 0x355
            {0x100B29C0, 0x100B2A08},  // 0x356
            {0x100B2E08, 0x100B2E50},  // 0x357
            {0x100B3250, 0x100B3298},  // 0x358
            {0x100B3698, 0x100B36E0},  // 0x359
        };
        String[] names = {"0x353_L3","0x353_L0x14","0x355","0x356","0x357","0x358","0x359"};

        Memory mem = currentProgram.getMemory();
        
        for (int i = 0; i < tables.length; i++) {
            long roundAddr = tables[i][0];
            long sboxAddr = tables[i][1];
            
            println("=== ECU " + names[i] + " ===");
            println("  Round keys @ 0x" + Long.toHexString(roundAddr) + ":");
            
            // 18 DWORDs = 72 bytes
            AddressFactory af = currentProgram.getAddressFactory();
            AddressSpace space = af.getDefaultAddressSpace();
            
            // 18 DWORDs = 72 bytes
            Address ra = space.getAddress(roundAddr);
            byte[] roundBytes = new byte[72];
            mem.getBytes(ra, roundBytes);
            
            StringBuilder sb = new StringBuilder("    ");
            for (int j = 0; j < 18; j++) {
                int dword = 0;
                for (int k = 0; k < 4; k++) {
                    dword |= ((roundBytes[j*4+k] & 0xFF) << (k*8));
                }
                sb.append(String.format("%08x ", dword));
                if ((j+1) % 6 == 0) {
                    println(sb.toString());
                    sb = new StringBuilder("    ");
                }
            }
            if (sb.length() > 4) println(sb.toString());
            
            // S-box: first 32 entries (of 256) for sampling
            println("  S-box (first 32 of 256 entries) @ 0x" + Long.toHexString(sboxAddr) + ":");
            Address sa = space.getAddress(sboxAddr);
            byte[] sboxBytes = new byte[128]; // 32 DWORDs
            mem.getBytes(sa, sboxBytes);
            
            sb = new StringBuilder("    ");
            for (int j = 0; j < 32; j++) {
                int dword = 0;
                for (int k = 0; k < 4; k++) {
                    dword |= ((sboxBytes[j*4+k] & 0xFF) << (k*8));
                }
                sb.append(String.format("%08x ", dword));
                if ((j+1) % 8 == 0) {
                    println(sb.toString());
                    sb = new StringBuilder("    ");
                }
            }
            println("");
        }
    }
}
