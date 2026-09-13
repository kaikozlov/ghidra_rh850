//@author kaikozlov
//@category Analysis
// Exact-target RH850/P1M-E profile for mruno Crown EPS 8965F3012000.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.mem.*;
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
    private MemoryBlock block(String name,long start,long size,boolean read,boolean write,boolean exec,boolean vol) throws Exception {
        Memory mem=currentProgram.getMemory(); Address a=toAddr(start); MemoryBlock b=mem.getBlock(a);
        if(b!=null){ if(!name.equals(b.getName()) || !b.getStart().equals(a) || b.getSize()!=size) throw new IllegalStateException("conflicting block "+a); }
        else b=mem.createUninitializedBlock(name,a,size,false);
        b.setRead(read); b.setWrite(write); b.setExecute(exec); b.setVolatile(vol); return b;
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
        block("LocalRAM",0xFEBE0000L,0x20000L,true,true,false,false);
        block("GlobalRAM_A",0xFEEF8000L,0x8000L,true,true,false,false);
        block("GlobalRAM_B",0xFEF00000L,0x8000L,true,true,false,false);
        block("SFR_EIC",0xFFFFB000L,0x1000L,true,true,false,true);
        block("SFR_RSCFD",0xFFD20000L,0x10000L,true,true,false,true);
        block("SFR_ICUS",0xFFC5D000L,0x1000L,true,true,false,true);
        block("SFR_CLKGEN",0xFFF88000L,0x2000L,true,true,false,true);
        block("SFR_FCU",0xFFD62000L,0x100L,true,true,false,true);
        block("SFR_ADCG0",0xFFF91000L,0x1000L,true,true,false,true);
        block("SFR_ADCG1",0xFFF92000L,0x1000L,true,true,false,true);
        block("SFR_DMAC_CM",0xFFFF8100L,0x40L,true,true,false,true);
        block("SFR_TSG3",0xFFE70000L,0x2000L,true,true,false,true);

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
