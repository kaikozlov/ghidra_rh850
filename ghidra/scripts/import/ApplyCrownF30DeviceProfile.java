//@author kaikozlov
//@category Analysis
// Exact-target RH850/P1M-E profile for mruno Crown EPS 8965F3012000.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.symbol.SourceType;
import java.math.BigInteger;
import java.security.MessageDigest;

public class ApplyCrownF30DeviceProfile extends GhidraScript {
    private static final String IMAGE_SHA="5b89fdbc69edc2f66ef8a557f88b08c758e3146bd4e90067320d7966812b1273";
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
        String actual=imageSha(); if(!IMAGE_SHA.equals(actual)) throw new IllegalStateException("wrong Crown F30 image "+actual);
        if (currentProgram.getMemory().getBlock(toAddr(0xFEDE0000L)) == null) {
            throw new IllegalStateException("ApplyP1MDeviceProfile must run first");
        }

        // Exact 8965F3012000 context loader at 0x709E4 differs from F33 only in TP:
        // INTBP=20200, EBASE=20000, GP=FEBEB800, TP=23C98, SP=FEBE2000.
        setRange("gp",0xFEBEB800L,0x00020000L,0x00100000L);
        setRange("tp",0x00023C98L,0x00020000L,0x00100000L);
        setPoint("sp",0xFEBE2000L,0x00020880L);
        label(0x20880L,"crown_f30_application_entry","8965F3012000 application entry wrapper");
        label(0x709E4L,"crown_f30_application_context_init","8965F3012000 context loader: INTBP=20200 EBASE=20000 GP=FEBEB800 TP=23C98 SP=FEBE2000");
        println("ApplyCrownF30DeviceProfile: exact image and application context applied");
    }
}
