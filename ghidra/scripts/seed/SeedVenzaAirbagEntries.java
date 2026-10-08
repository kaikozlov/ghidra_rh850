//@author kaikozlov
//@category Seed
// Seed the exact Venza airbag 8917048E30 application roots recovered from the
// reset/startup and split-image seam analysis.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.SourceType;
public class SeedVenzaAirbagEntries extends GhidraScript {
  private Function ensure(long v,String name) throws Exception { Address a=toAddr(v); Listing l=currentProgram.getListing(); Instruction c=l.getInstructionContaining(a); if(c!=null&&!c.getMinAddress().equals(a)) l.clearCodeUnits(c.getMinAddress(),c.getMaxAddress(),false); CodeUnit u=l.getCodeUnitContaining(a); if(u!=null&&!(u instanceof Instruction)) l.clearCodeUnits(u.getMinAddress(),u.getMaxAddress(),false); if(l.getInstructionAt(a)==null&&!disassemble(a)) throw new IllegalStateException("disassembly failed "+a); Function f=currentProgram.getFunctionManager().getFunctionAt(a); if(f==null) f=createFunction(a,name); if(f==null) throw new IllegalStateException("function creation failed "+a); if(!name.equals(f.getName())) f.setName(name,SourceType.USER_DEFINED); return f; }
  @Override public void run() throws Exception {
    ensure(0x0BD0L,"venza_airbag_reset_entry");
    ensure(0x10ACL,"venza_airbag_startup_mode_resolver");
    ensure(0x0A304L,"venza_airbag_rprg_seam_entry");
    ensure(0x01000000L,"venza_rprg_extended_user_entry");
    println("SeedVenzaAirbagEntries: seeded 4 exact Venza airbag application roots");
  }
}
