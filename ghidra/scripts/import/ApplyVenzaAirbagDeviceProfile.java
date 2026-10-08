//@author kaikozlov
//@category Analysis
// Exact-target profile for the yc Venza airbag sensor 8917048E30 (RH850 P1x-C
// family; exact MCU part not established). Deliberately applies no P1M-E SFR
// map: this image is a different RH850 type and cross-type SFR transfer is
// unsupported. Establishes only image identity, the recovered RAM windows,
// register context, and the secure-service boundary labels pinned by
// tests/targets/venza/verify_yc_venza_airbag_reprogramming.py.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ArrayDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.lang.Register;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import java.math.BigInteger;
import java.security.MessageDigest;

public class ApplyVenzaAirbagDeviceProfile extends GhidraScript {
    private static final String IMAGE_SHA = "2dfaf7ce21cb04af1126192f574103f63802352f8717fa0f03986d5a11d067f9";
    private static final long CODE_SIZE = 0x300000L;

    private String imageSha() throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] buf = new byte[0x4000];
        long off = 0;
        while (off < CODE_SIZE) {
            int n = (int) Math.min(buf.length, CODE_SIZE - off);
            currentProgram.getMemory().getBytes(toAddr(off), buf, 0, n);
            md.update(buf, 0, n);
            off += n;
        }
        StringBuilder s = new StringBuilder();
        for (byte b : md.digest()) s.append(String.format("%02x", b & 0xff));
        return s.toString();
    }

    private void ram(String name, long start, long size) throws Exception {
        Memory mem = currentProgram.getMemory();
        if (mem.getBlock(toAddr(start)) != null) return;
        MemoryBlock b = mem.createUninitializedBlock(name, toAddr(start), size, false);
        b.setRead(true);
        b.setWrite(true);
        b.setExecute(false);
        println("Venza RAM window " + name + " " + b.getStart() + ".." + b.getEnd());
    }

    private void partitionCodeFlashFill() throws Exception {
        Memory mem = currentProgram.getMemory();
        Address ffStart = toAddr(0x00180000L);
        Address zeroStart = toAddr(0x002B0000L);

        MemoryBlock code = mem.getBlock(toAddr(0));
        if (code == null || !code.getStart().equals(toAddr(0)) ||
                code.getEnd().getOffset() < 0x002FFFFFL) {
            throw new IllegalStateException("unexpected Venza CodeFlash block");
        }
        if (code.getEnd().getOffset() >= ffStart.getOffset()) {
            mem.split(code, ffStart);
        }

        MemoryBlock ffFill = mem.getBlock(ffStart);
        if (ffFill == null || !ffFill.getStart().equals(ffStart)) {
            throw new IllegalStateException("missing Venza FF-fill block");
        }
        if (ffFill.getEnd().getOffset() >= zeroStart.getOffset()) {
            mem.split(ffFill, zeroStart);
        }

        code = mem.getBlock(toAddr(0));
        ffFill = mem.getBlock(ffStart);
        MemoryBlock zeroFill = mem.getBlock(zeroStart);
        if (code.getEnd().getOffset() != 0x0017FFFFL ||
                ffFill.getEnd().getOffset() != 0x002AFFFFL ||
                zeroFill == null || zeroFill.getEnd().getOffset() != 0x002FFFFFL) {
            throw new IllegalStateException("Venza CodeFlash partition drift");
        }
        code.setName("CodeFlash");
        ffFill.setName("CodeFlashFFFill");
        zeroFill.setName("CodeFlashZeroFill");
        code.setExecute(true);
        ffFill.setExecute(false);
        zeroFill.setExecute(false);
        if (getDataAt(ffStart) == null) {
            createData(ffStart, new ArrayDataType(ByteDataType.dataType, 0x130000, 1));
        }
        if (getDataAt(zeroStart) == null) {
            createData(zeroStart, new ArrayDataType(ByteDataType.dataType, 0x50000, 1));
        }
    }

    private void setRange(String reg, long value, long start, long endExclusive) throws Exception {
        Register r = currentProgram.getRegister(reg);
        if (r == null) throw new IllegalStateException("missing register " + reg);
        currentProgram.getProgramContext().setValue(r, toAddr(start), toAddr(endExclusive - 1),
            BigInteger.valueOf(value));
    }

    private void label(long at, String name, String comment) throws Exception {
        var st = currentProgram.getSymbolTable();
        Address a = toAddr(at);
        var sym = st.getPrimarySymbol(a);
        if (sym == null) {
            sym = st.createLabel(a, name, SourceType.USER_DEFINED);
            sym.setPrimary();
        } else if (!name.equals(sym.getName())) {
            sym.setName(name, SourceType.USER_DEFINED);
        }
        currentProgram.getListing().setComment(a,
            ghidra.program.model.listing.CodeUnit.PLATE_COMMENT, comment);
    }

    @Override
    public void run() throws Exception {
        String actual = imageSha();
        if (!IMAGE_SHA.equals(actual)) throw new IllegalStateException("wrong Venza airbag image " + actual);
        Memory mem = currentProgram.getMemory();
        if (mem.getBlock(toAddr(0x01000000L)) == null) {
            throw new IllegalStateException("AddExtendedUser must run first");
        }

        // Exact capture boundary: executable/non-fill content ends at 0x17FFFF;
        // 0x180000..0x2AFFFF is FF fill and 0x2B0000..0x2FFFFF is zero fill.
        // Keeping the fill non-executable prevents direct-call analysis from
        // manufacturing functions inside the erased optional-hook range.
        partitionCodeFlashFill();

        // Recovered RAM windows: runtime relocation targets (FEBEA7B0.. code
        // segment, FEBF0924.. RPRG, FEBFB770.. crypto/data incl. GP=FEC0102C),
        // the startup-preserved retained handoff record, the secure-service
        // request ring/descriptors, and the RH850-reserved secure window.
        ram("RuntimeRAM", 0xFEBE0000L, 0x30000L);
        ram("RetainedRAM", 0xFEF00000L, 0x10000L);
        ram("SecureRing", 0xFEFF0000L, 0x2000L);
        ram("SecureWindow", 0xFF1F0000L, 0x100L);

        // Register context recovered from the image's own startup: GP=FEC0102C
        // and TP=0x24050 across the meaningful code regions.
        setRange("gp", 0xFEC0102CL, 0x0L, 0x180000L);
        setRange("tp", 0x24050L, 0x0L, 0x180000L);
        setRange("gp", 0xFEC0102CL, 0x01000000L, 0x01008000L);

        // Secure-service boundary (byte-pinned by the venza verify test).
        label(0xFF1F0014L, "secure_service_shared_pointer", "read by ring helper 0x89E60; written by 0x8A04E");
        label(0xFF1F0044L, "secure_service_trigger", "single writer 0x89F6E");
        label(0xFEFF00F0L, "secure_ring_entry0", "four-entry request ring cell");
        label(0xFEFF0168L, "rid1010_key_update_staging", "64-byte M1/M2/M3 staging for RID 0x1010");
        label(0xFEFF01E8L, "secure_req_opcode10_descriptor", "opcode 0x10 service; entry 0xBD8C8; 4-byte result");
        label(0xFEFF0250L, "secure_req_opcode04_descriptor", "opcode 0x04 mode query; entry 0xBDA6E");
        label(0xFEFF02B8L, "secure_req_mac_generate_descriptor", "opcode 0x12; entry 0xBDC7A; SecOC TX");
        label(0xFEFF0330L, "secure_req_mac_verify_descriptor", "opcode 0x12; entry 0xBDE88; SecOC RX");
        label(0xFEFF0398L, "secure_req_key_update_descriptor", "opcode 0x31; entry 0xBE0CC; RID 0x1010");
        label(0xFEF0FFD0L, "retained_programming_handoff_record", "32-byte record preserved through startup RAM test");
        label(0xFEF0FFF0L, "retained_programming_magic", "0x5AA5A55A magic cell tested by 0x17BC");
        label(0x17FFC6L, "raw_identity_8917048E30", "raw identity string");
        label(0x17FFD0L, "raw_identity_8917F48692", "raw identity string");
        println("ApplyVenzaAirbagDeviceProfile: identity, RAM windows, context, and secure boundary applied");
    }
}
