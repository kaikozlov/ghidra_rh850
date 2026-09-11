//@author kaikozlov
//@category Seed
// Seed exact-H entries that transfer to F through byte-identical application bytes.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import java.io.*;
public class SeedCorollaHFRecoveredFunctions extends GhidraScript {
  private void ensure(long v) throws Exception { Address a=toAddr(v); Listing l=currentProgram.getListing(); Instruction c=l.getInstructionContaining(a); if(c!=null&&!c.getMinAddress().equals(a)) l.clearCodeUnits(c.getMinAddress(),c.getMaxAddress(),false); CodeUnit u=l.getCodeUnitContaining(a); if(u!=null&&!(u instanceof Instruction)) l.clearCodeUnits(u.getMinAddress(),u.getMaxAddress(),false); if(l.getInstructionAt(a)==null&&!disassemble(a)) throw new IllegalStateException("disassembly failed "+a); Function f=currentProgram.getFunctionManager().getFunctionAt(a); if(f==null) f=createFunction(a,null); if(f==null) throw new IllegalStateException("function creation failed "+a); }
  @Override public void run() throws Exception { String[] a=getScriptArgs(); if(a.length!=1) throw new IllegalArgumentException("expected function_seeds.csv path"); File f=new File(a[0]); if(!f.isFile()) throw new IllegalStateException("missing seed file "+f); int n=0; try(BufferedReader br=new BufferedReader(new FileReader(f))){ String h=br.readLine(); if(!"address,provenance,note".equals(h)) throw new IllegalStateException("seed CSV header drift"); String line; while((line=br.readLine())!=null){ if(line.isBlank()) continue; String[] p=line.split(",",3); if(p.length!=3||p[1].isBlank()) throw new IllegalStateException("invalid seed row: "+line); long v=Long.parseLong(p[0].replace("0x",""),16); if(v<0x20000L||v>=0x100000L) throw new IllegalStateException("non-application seed "+p[0]); ensure(v); n++; }} if(n!=143) throw new IllegalStateException("seed count drift "+n); println("SeedCorollaHFRecoveredFunctions: seeded "+n+" evidence-backed shared-application entries"); }
}
