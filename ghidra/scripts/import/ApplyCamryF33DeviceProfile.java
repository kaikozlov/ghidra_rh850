//@author kaikozlov
//@category Analysis
// Exact-target RH850/P1M-E profile for first-class 2026 Camry EPS 8965F3307000.
// Applies only F33-proven context after the common P1M-E chip profile.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.symbol.SourceType;
import java.math.BigInteger;
import java.security.MessageDigest;

public class ApplyCamryF33DeviceProfile extends GhidraScript {
    private static final String IMAGE_SHA="42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7";
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
        String actual=imageSha(); if(!IMAGE_SHA.equals(actual)) throw new IllegalStateException("wrong F33 image "+actual);
        if (currentProgram.getMemory().getBlock(toAddr(0xFEDE0000L)) == null) {
            throw new IllegalStateException("ApplyP1MDeviceProfile must run first");
        }

        // Exact F33 0x715B4 context loader: INTBP=20200, EBASE=20000,
        // GP=FEBEB800, TP=23DFC, SP=FEBE2000. GP/TP remain fixed application-wide.
        setRange("gp",0xFEBEB800L,0x00020000L,0x00100000L);
        setRange("tp",0x00023DFCL,0x00020000L,0x00100000L);
        setPoint("sp",0xFEBE2000L,0x00020880L);
        label(0x20880L,"f33_application_entry","Exact F33 application entry wrapper -> startup coordinator 0x637EE");
        label(0x715B4L,"f33_application_context_init","Exact F33 context loader: INTBP=20200 EBASE=20000 GP=FEBEB800 TP=23DFC SP=FEBE2000");
        println("ApplyCamryF33DeviceProfile: exact image and target-native application context applied");
    }
}
