import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.pcode.*;
import java.util.*;

public class AuditCallConeMemoryOps extends GhidraScript {
  String vk(Varnode v){return v.getAddress().getAddressSpace().getName()+":"+Long.toUnsignedString(v.getOffset())+":"+v.getSize();}
  Set<String> paramKeys(HighFunction hf){
    Set<String> out=new HashSet<>(); FunctionPrototype fp=hf.getFunctionPrototype();
    for(int i=0;i<fp.getNumParams();i++){HighSymbol hs=fp.getParam(i); if(hs==null)continue; for(Varnode r:hs.getStorage().getVarnodes())if(r!=null)out.add(vk(r));}
    return out;
  }
  boolean paramDep(Varnode v,int d,Set<Varnode> seen,Set<String> params){
    if(v==null||d>40||!seen.add(v))return false; if(params.contains(vk(v)))return true;
    HighVariable hv=v.getHigh(); if(hv instanceof HighParam)return true; if(v.isConstant())return false;
    PcodeOp op=v.getDef(); if(op==null)return false;
    for(int i=0;i<op.getNumInputs();i++)if(paramDep(op.getInput(i),d+1,new HashSet<>(seen),params))return true; return false;
  }
  String ex(Varnode v,int d,Set<Varnode> seen){
    if(v==null)return"null"; if(v.isConstant())return String.format("0x%x",v.getOffset()); if(d>14||!seen.add(v))return v.toString();
    PcodeOp op=v.getDef(); if(op==null)return v.toString(); StringBuilder b=new StringBuilder(PcodeOp.getMnemonic(op.getOpcode())).append('(');
    for(int i=0;i<op.getNumInputs();i++){if(i>0)b.append(',');b.append(ex(op.getInput(i),d+1,new HashSet<>(seen)));}return b.append(')').toString();
  }
  public void run() throws Exception {
    FunctionManager fm=currentProgram.getFunctionManager(); TreeSet<Function> cone=new TreeSet<>(Comparator.comparingLong(f->f.getEntryPoint().getOffset())); ArrayDeque<Function> q=new ArrayDeque<>();
    for(String s:getScriptArgs()){Function f=fm.getFunctionAt(toAddr(Long.decode(s))); if(f==null)throw new IllegalArgumentException("no function at "+s); if(cone.add(f))q.add(f);}
    while(!q.isEmpty()){Function f=q.removeFirst();for(Function c:f.getCalledFunctions(monitor))if(c!=null&&!c.isExternal()&&cone.add(c))q.add(c);}
    println("CONE|functions="+cone.size()); DecompInterface di=new DecompInterface();di.openProgram(currentProgram);
    long loads=0,pLoads=0,inds=0,pInds=0,arith=0,pArith=0;
    for(Function f:cone){DecompileResults dr=di.decompileFunction(f,30,monitor);HighFunction hf=dr.getHighFunction();if(hf==null)continue;Set<String> params=paramKeys(hf);Iterator<PcodeOpAST> it=hf.getPcodeOps();
      while(it.hasNext()){PcodeOpAST op=it.next();int c=op.getOpcode();
        if(c==PcodeOp.LOAD){loads++;boolean p=paramDep(op.getInput(1),0,new HashSet<>(),params);if(p){pLoads++;println("LOAD|"+f.getEntryPoint()+"|"+op.getSeqnum().getTarget()+"|addr="+ex(op.getInput(1),0,new HashSet<>()));}}
        else if(c==PcodeOp.CALLIND||c==PcodeOp.BRANCHIND){inds++;boolean p=paramDep(op.getInput(0),0,new HashSet<>(),params);if(p){pInds++;println("IND|"+PcodeOp.getMnemonic(c)+"|"+f.getEntryPoint()+"|"+op.getSeqnum().getTarget()+"|target="+ex(op.getInput(0),0,new HashSet<>()));}}
        else if(c==PcodeOp.INT_DIV||c==PcodeOp.INT_SDIV||c==PcodeOp.INT_REM||c==PcodeOp.INT_SREM){arith++;boolean p=paramDep(op.getInput(1),0,new HashSet<>(),params);if(p){pArith++;println("ARITH|"+PcodeOp.getMnemonic(c)+"|"+f.getEntryPoint()+"|"+op.getSeqnum().getTarget()+"|divisor="+ex(op.getInput(1),0,new HashSet<>()));}}
      }
    }
    println("SUMMARY|functions="+cone.size()+"|loads="+loads+"|param_loads="+pLoads+"|indirects="+inds+"|param_indirects="+pInds+"|arith="+arith+"|param_arith="+pArith);di.dispose();
  }
}
