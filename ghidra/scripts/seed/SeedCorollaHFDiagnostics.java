//@author kaikozlov
//@category Seed
// Parse and seed the exact shared 226-record application RDBI table at 0x28F34.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.SourceType;
import java.util.*;
public class SeedCorollaHFDiagnostics extends GhidraScript {
  private Function ensure(long v,String name) throws Exception { Address a=toAddr(v); Listing l=currentProgram.getListing(); Instruction c=l.getInstructionContaining(a); if(c!=null&&!c.getMinAddress().equals(a)) l.clearCodeUnits(c.getMinAddress(),c.getMaxAddress(),false); CodeUnit u=l.getCodeUnitContaining(a); if(u!=null&&!(u instanceof Instruction)) l.clearCodeUnits(u.getMinAddress(),u.getMaxAddress(),false); if(l.getInstructionAt(a)==null&&!disassemble(a)) throw new IllegalStateException("disassembly failed "+a); Function f=currentProgram.getFunctionManager().getFunctionAt(a); if(f==null) f=createFunction(a,name); if(f==null) throw new IllegalStateException("function creation failed "+a); if(f.getName().startsWith("FUN_")||f.getName().startsWith("corolla_hf_rdbi_")) f.setName(name,SourceType.USER_DEFINED); return f; }
  private String name(int did){ return String.format("corolla_hf_rdbi_%04x_callback",did); }
  @Override public void run() throws Exception { long base=0x28F34L; int count=226; int first=currentProgram.getMemory().getShort(toAddr(base))&0xffff; int last=currentProgram.getMemory().getShort(toAddr(base+(count-1)*16L))&0xffff; if(first!=0x0100||last!=0xF18C) throw new IllegalStateException(String.format("RDBI geometry drift first=%04x last=%04x",first,last)); LinkedHashMap<Long,Integer> cb=new LinkedHashMap<>(); for(int i=0;i<count;i++){ long r=base+i*16L; int did=currentProgram.getMemory().getShort(toAddr(r))&0xffff; long fn=currentProgram.getMemory().getInt(toAddr(r+4))&0xffffffffL; if(did==0||fn==0||fn>=0x100000L) throw new IllegalStateException(String.format("bad RDBI record %d did=%04x fn=%08x",i,did,fn)); cb.putIfAbsent(fn,did); } for(var e:cb.entrySet()) ensure(e.getKey(),name(e.getValue())); if(cb.size()!=180) throw new IllegalStateException("RDBI callback count drift "+cb.size()); println("SeedCorollaHFDiagnostics: 226 records / 180 unique callbacks from 0x28F34"); }
}
