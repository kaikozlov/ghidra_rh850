//@author kaikozlov
//@category Seed
// Seed exact-F33 function entries whose provenance is tracked in function_seeds.csv.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import java.io.*;
public class SeedCamryF33RecoveredFunctions extends GhidraScript {
  private void ensure(long v) throws Exception { Address a=toAddr(v); Listing l=currentProgram.getListing(); Instruction c=l.getInstructionContaining(a); if(c!=null&&!c.getMinAddress().equals(a)) l.clearCodeUnits(c.getMinAddress(),c.getMaxAddress(),false); CodeUnit u=l.getCodeUnitContaining(a); if(u!=null&&!(u instanceof Instruction)) l.clearCodeUnits(u.getMinAddress(),u.getMaxAddress(),false); if(l.getInstructionAt(a)==null&&!disassemble(a)) throw new IllegalStateException("disassembly failed "+a); Function f=currentProgram.getFunctionManager().getFunctionAt(a); if(f==null) f=createFunction(a,null); if(f==null) throw new IllegalStateException("function creation failed "+a); }
  @Override public void run() throws Exception { String[] a=getScriptArgs(); if(a.length!=1) throw new IllegalArgumentException("expected function_seeds.csv path"); File f=new File(a[0]); if(!f.isFile()) throw new IllegalStateException("missing seed file "+f); int n=0; try(BufferedReader br=new BufferedReader(new FileReader(f))){ String h=br.readLine(); if(!"address,provenance,note".equals(h)) throw new IllegalStateException("seed CSV header drift"); String line; while((line=br.readLine())!=null){ if(line.isBlank()) continue; String[] p=line.split(",",3); if(p.length!=3||p[1].isBlank()) throw new IllegalStateException("invalid seed row: "+line); long v=Long.parseLong(p[0].replace("0x",""),16); ensure(v); n++; }} if(n!=71) throw new IllegalStateException("seed count drift "+n); println("SeedCamryF33RecoveredFunctions: seeded "+n+" evidence-backed entries"); }
}
