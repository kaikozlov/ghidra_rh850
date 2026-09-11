//@author kaikozlov
//@category Analysis
// Exact-pair RH850/P1M-E profile shared by the byte-identical H/F Corolla application.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.mem.*;
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
    private MemoryBlock block(String name,long start,long size,boolean read,boolean write,boolean exec,boolean vol) throws Exception {
        Memory mem=currentProgram.getMemory(); Address a=toAddr(start); MemoryBlock b=mem.getBlock(a);
        if(b!=null){ if(!name.equals(b.getName())||!b.getStart().equals(a)||b.getSize()!=size) throw new IllegalStateException("conflicting block "+a); }
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
        String actual=imageSha(); if(!IMAGE_SHAS.contains(actual)) throw new IllegalStateException("wrong Corolla H/F image "+actual);

        // R7F701383 geometry: 1 MiB CodeFlash, 32 KiB DataFlash, 128 KiB LocalRAM.
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
