//@author kaikozlov
//@category Seed
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.SourceType;
public class SeedCamryF33Entries extends GhidraScript {
  private Function ensure(long v,String name) throws Exception { Address a=toAddr(v); Listing l=currentProgram.getListing(); Instruction c=l.getInstructionContaining(a); if(c!=null&&!c.getMinAddress().equals(a)) l.clearCodeUnits(c.getMinAddress(),c.getMaxAddress(),false); CodeUnit u=l.getCodeUnitContaining(a); if(u!=null&&!(u instanceof Instruction)) l.clearCodeUnits(u.getMinAddress(),u.getMaxAddress(),false); if(l.getInstructionAt(a)==null&&!disassemble(a)) throw new IllegalStateException("disassembly failed "+a); Function f=currentProgram.getFunctionManager().getFunctionAt(a); if(f==null) f=createFunction(a,name); if(f==null) throw new IllegalStateException("function creation failed "+a); if(!name.equals(f.getName())) f.setName(name,SourceType.USER_DEFINED); return f; }
  @Override public void run() throws Exception { ensure(0x20880L,"f33_application_entry"); ensure(0x637EEL,"f33_startup_coordinator"); ensure(0x636D4L,"f33_startup_copy_helper"); ensure(0x715B4L,"f33_application_context_init"); println("SeedCamryF33Entries: seeded 4 exact F33 application roots"); }
}
