import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.pcode.*;
import ghidra.program.model.symbol.*;
import java.util.*;

/**
 * Enumerate high-pcode STORE pointer expressions whose statically recoverable
 * u32 range can hit analyst-supplied addresses that are not already represented
 * by canonical write references on the instruction. Unknown/unbounded pointers
 * are intentionally excluded: this is the register-arithmetic false-negative
 * audit complementary to pointer-table / callback provenance work.
 *
 * Usage: ... -- 0xFEBECC50 0xFEBECC62 ...
 */
public class AuditComputedStoreTargets extends GhidraScript {
  static final long U32 = 0xffffffffL;
  static class R {
    long lo, hi; boolean known;
    R(long a,long b,boolean k){lo=a&U32;hi=b&U32;known=k&&Long.compareUnsigned(lo,hi)<=0;}
    static R unk(){return new R(0,U32,false);}
  }
  R add(R a,R b){
    if(!a.known||!b.known)return R.unk();
    long lo=(a.lo+b.lo)&U32, hi=(a.hi+b.hi)&U32;
    if(Long.compareUnsigned(lo,hi)>0)return R.unk();
    return new R(lo,hi,true);
  }
  R mul(R a,R b){
    if(!a.known||!b.known)return R.unk();
    if(a.lo==a.hi){long k=a.lo;long lo=(b.lo*k)&U32,hi=(b.hi*k)&U32;if(Long.compareUnsigned(lo,hi)>0)return R.unk();return new R(lo,hi,true);}
    if(b.lo==b.hi)return mul(b,a);
    return R.unk();
  }
  R ev(Varnode v,int d,Set<Varnode> seen){
    if(v==null||d>24||!seen.add(v))return R.unk();
    if(v.isConstant()){long x=v.getOffset()&U32;return new R(x,x,true);}
    PcodeOp op=v.getDef();
    if(op==null){int bits=v.getSize()*8;if(bits<32)return new R(0,(1L<<bits)-1,true);return R.unk();}
    int c=op.getOpcode();
    if(c==PcodeOp.COPY||c==PcodeOp.CAST||c==PcodeOp.INDIRECT||c==PcodeOp.INT_ZEXT)return ev(op.getInput(0),d+1,seen);
    if(c==PcodeOp.PTRSUB){R a=ev(op.getInput(0),d+1,new HashSet<>(seen)),b=ev(op.getInput(1),d+1,new HashSet<>(seen));if(a.known&&a.lo==0&&a.hi==0&&b.known)return b;return add(a,b);}
    if(c==PcodeOp.INT_ADD)return add(ev(op.getInput(0),d+1,new HashSet<>(seen)),ev(op.getInput(1),d+1,new HashSet<>(seen)));
    if(c==PcodeOp.INT_SUB){R a=ev(op.getInput(0),d+1,new HashSet<>(seen)),b=ev(op.getInput(1),d+1,new HashSet<>(seen));if(a.known&&b.known&&b.lo==b.hi){long k=(-b.lo)&U32;return add(a,new R(k,k,true));}return R.unk();}
    if(c==PcodeOp.INT_MULT)return mul(ev(op.getInput(0),d+1,new HashSet<>(seen)),ev(op.getInput(1),d+1,new HashSet<>(seen)));
    if(c==PcodeOp.INT_LEFT){R a=ev(op.getInput(0),d+1,new HashSet<>(seen)),b=ev(op.getInput(1),d+1,new HashSet<>(seen));if(b.known&&b.lo==b.hi&&b.lo<32)return mul(a,new R(1L<<b.lo,1L<<b.lo,true));return R.unk();}
    if(c==PcodeOp.INT_AND){R a=ev(op.getInput(0),d+1,new HashSet<>(seen)),b=ev(op.getInput(1),d+1,new HashSet<>(seen));if(b.known&&b.lo==b.hi)return new R(0,b.lo,true);if(a.known&&a.lo==a.hi)return new R(0,a.lo,true);return R.unk();}
    if(c==PcodeOp.PTRADD){R a=ev(op.getInput(0),d+1,new HashSet<>(seen)),idx=ev(op.getInput(1),d+1,new HashSet<>(seen)),sz=ev(op.getInput(2),d+1,new HashSet<>(seen));return add(a,mul(idx,sz));}
    if(c==PcodeOp.MULTIEQUAL){long lo=U32,hi=0;boolean any=false;for(int i=0;i<op.getNumInputs();i++){R q=ev(op.getInput(i),d+1,new HashSet<>(seen));if(!q.known)return R.unk();if(Long.compareUnsigned(q.lo,lo)<0)lo=q.lo;if(Long.compareUnsigned(q.hi,hi)>0)hi=q.hi;any=true;}return any?new R(lo,hi,true):R.unk();}
    return R.unk();
  }
  String ex(Varnode v,int d,Set<Varnode> seen){
    if(v==null)return"null";if(v.isConstant())return String.format("0x%x",v.getOffset());if(d>10||!seen.add(v))return v.toString();PcodeOp op=v.getDef();if(op==null)return v.toString();StringBuilder b=new StringBuilder(PcodeOp.getMnemonic(op.getOpcode())).append('(');for(int i=0;i<op.getNumInputs();i++){if(i>0)b.append(',');b.append(ex(op.getInput(i),d+1,new HashSet<>(seen)));}return b.append(')').toString();
  }
  Set<Long> canonicalWrites(Instruction ins){
    Set<Long> out=new TreeSet<>(); if(ins==null)return out;
    for(Reference ref:ins.getReferencesFrom())if(ref.getReferenceType().isWrite())out.add(ref.getToAddress().getOffset()&U32);
    return out;
  }
  public void run() throws Exception {
    TreeSet<Long> targets=new TreeSet<>();
    for(String s:getScriptArgs())targets.add(Long.decode(s)&U32);
    if(targets.isEmpty())throw new IllegalArgumentException("supply one or more target addresses");
    DecompInterface di=new DecompInterface();di.openProgram(currentProgram);
    FunctionIterator fi=currentProgram.getFunctionManager().getFunctions(true);
    long fn=0,stores=0,known=0,candidates=0; Set<String> funcs=new TreeSet<>();
    while(fi.hasNext()){
      Function f=fi.next(); DecompileResults dr=di.decompileFunction(f,30,monitor);HighFunction hf=dr.getHighFunction();if(hf==null)continue;fn++;
      Iterator<PcodeOpAST> it=hf.getPcodeOps();
      while(it.hasNext()){
        PcodeOpAST op=it.next();if(op.getOpcode()!=PcodeOp.STORE)continue;stores++;
        R r=ev(op.getInput(1),0,new HashSet<>());if(!r.known)continue;known++;
        ArrayList<Long> hit=new ArrayList<>();for(long t:targets)if(Long.compareUnsigned(t,r.lo)>=0&&Long.compareUnsigned(t,r.hi)<=0)hit.add(t);if(hit.isEmpty())continue;
        Instruction ins=getInstructionAt(op.getSeqnum().getTarget());Set<Long> refs=canonicalWrites(ins);hit.removeIf(refs::contains);if(hit.isEmpty())continue;
        candidates++;funcs.add(f.getEntryPoint().toString());
        StringBuilder hs=new StringBuilder();for(int i=0;i<hit.size();i++){if(i>0)hs.append(',');hs.append(String.format("%08x",hit.get(i)));}
        println(String.format("CAND|%s|%s|lo=%08x|hi=%08x|hits=%s|expr=%s",f.getEntryPoint(),op.getSeqnum().getTarget(),r.lo,r.hi,hs,ex(op.getInput(1),0,new HashSet<>())));
      }
    }
    println("SUMMARY|functions="+fn+"|stores="+stores+"|knownRangeStores="+known+"|candidates="+candidates+"|candidateFunctions="+funcs.size());
    println("FUNCS|"+String.join(",",funcs));di.dispose();
  }
}
