//@author kaikozlov
//@category Analysis
// Exact-target RH850/P1M-E profile for first-class 2026 Camry EPS 8965F3307000.
// Maps chip-level memory windows and applies only F33-proven application context.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.ProgramContext;
import ghidra.program.model.mem.*;
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
        String actual=imageSha(); if(!IMAGE_SHA.equals(actual)) throw new IllegalStateException("wrong F33 image "+actual);
        // R7F701381 chip-level memory geometry, independently confirmed by the target BOOT INFO AREA.
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
