//@author kaikozlov
//@category Analysis
// Exact-pair RH850/P1M-E profile shared by the byte-identical H/F Corolla application.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.symbol.SourceType;
import java.math.BigInteger;
import java.security.MessageDigest;
import java.util.Set;

public class ApplyCorollaHFDeviceProfile extends GhidraScript {
    private static final Set<String> IMAGE_SHAS=Set.of(
        "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f",
        "fdb35b76891cf84a8b89e0a05c9c7c5cfcd27994cf85ccc01ff32828f53091f6"
    );
    private String imageSha() throws Exception {
        MessageDigest md=MessageDigest.getInstance("SHA-256"); byte[] buf=new byte[0x4000]; long off=0;
        while(off<0x100000L){ int n=(int)Math.min(buf.length,0x100000L-off); currentProgram.getMemory().getBytes(toAddr(off),buf,0,n); md.update(buf,0,n); off+=n; }
        StringBuilder s=new StringBuilder(); for(byte b:md.digest()) s.append(String.format("%02x",b&0xff)); return s.toString();
    }
    private void setRange(String reg,long value,long start,long endExclusive) throws Exception {
        Register r=currentProgram.getRegister(reg); if(r==null) throw new IllegalStateException("missing register "+reg);
        currentProgram.getProgramContext().setValue(r,toAddr(start),toAddr(endExclusive-1),BigInteger.valueOf(value));
    }
    private void setPoint(String reg,long value,long at) throws Exception {
        Register r=currentProgram.getRegister(reg); if(r==null) throw new IllegalStateException("missing register "+reg);
        currentProgram.getProgramContext().setValue(r,toAddr(at),toAddr(at),BigInteger.valueOf(value));
    }
    private void label(long at,String name,String comment) throws Exception {
        var st=currentProgram.getSymbolTable(); Address a=toAddr(at); var sym=st.getPrimarySymbol(a);
        if(sym==null){ sym=st.createLabel(a,name,SourceType.USER_DEFINED); sym.setPrimary(); }
        else if(!name.equals(sym.getName())) sym.setName(name,SourceType.USER_DEFINED);
        currentProgram.getListing().setComment(a,ghidra.program.model.listing.CodeUnit.PLATE_COMMENT,comment);
    }
    @Override public void run() throws Exception {
        String actual=imageSha(); if(!IMAGE_SHAS.contains(actual)) throw new IllegalStateException("wrong Corolla H/F image "+actual);

        if (currentProgram.getMemory().getBlock(toAddr(0xFEDE0000L)) == null) {
            throw new IllegalStateException("ApplyP1MDeviceProfile must run first");
        }

        // Both exact images contain these target-native startup loads. Application
        // bytes are identical; the low-image delta does not alter the boot pair.
        setRange("gp",0xFEBF9800L,0x00000000L,0x00020000L);
        setRange("tp",0x0000867CL,0x00000000L,0x00020000L);
        setRange("gp",0xFEBEB800L,0x00020000L,0x00100000L);
        setRange("tp",0x00023D6CL,0x00020000L,0x00100000L);
        setPoint("sp",0xFEBE2000L,0x00020880L);
        label(0x20880L,"corolla_hf_application_entry","Exact H/F application wrapper; directly calls 0x5CAAC");
        label(0x5CAACL,"corolla_hf_startup_coordinator","Exact H/F startup coordinator; calls context initialization first, then subsystem initialization");
        label(0x6A8C4L,"corolla_hf_application_context_init","Exact H/F application context loader: INTBP=20200 EBASE=20000 GP=FEBEB800 TP=23D6C SP=FEBE2000");
        println("ApplyCorollaHFDeviceProfile: exact H/F image and target-native contexts applied");
    }
}
