//@author kaikozlov
//@category Seed
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.SourceType;
public class SeedCorollaHFEntries extends GhidraScript {
  private Function ensure(long v,String name) throws Exception { Address a=toAddr(v); Listing l=currentProgram.getListing(); Instruction c=l.getInstructionContaining(a); if(c!=null&&!c.getMinAddress().equals(a)) l.clearCodeUnits(c.getMinAddress(),c.getMaxAddress(),false); CodeUnit u=l.getCodeUnitContaining(a); if(u!=null&&!(u instanceof Instruction)) l.clearCodeUnits(u.getMinAddress(),u.getMaxAddress(),false); if(l.getInstructionAt(a)==null&&!disassemble(a)) throw new IllegalStateException("disassembly failed "+a); Function f=currentProgram.getFunctionManager().getFunctionAt(a); if(f==null) f=createFunction(a,name); if(f==null) throw new IllegalStateException("function creation failed "+a); if(!name.equals(f.getName())) f.setName(name,SourceType.USER_DEFINED); return f; }
  @Override public void run() throws Exception { ensure(0x20880L,"corolla_hf_application_entry"); ensure(0x5CAACL,"corolla_hf_startup_coordinator"); ensure(0x6A8C4L,"corolla_hf_application_context_init"); println("SeedCorollaHFEntries: seeded 3 exact shared-application roots"); }
}
