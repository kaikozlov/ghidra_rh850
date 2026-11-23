import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.lang.Register;
import ghidra.program.model.pcode.*;
import java.util.*;

/**
 * Label every high-pcode STORE whose pointer range the
 * AuditComputedStoreTargets resolver cannot bound. That script closes
 * known-range stores against chosen targets; this one makes the
 * unknown-range class countable and reviewable by naming the base kind
 * (stack, register, loaded pointer, call result, phi) and whether a
 * non-constant index is added to it.
 *
 * Usage: no arguments.
 */
public class TriageUnknownStoreBases extends GhidraScript {
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
    if(c==PcodeOp.SUBPIECE&&v.getSize()==4&&op.getInput(1).isConstant()&&op.getInput(1).getOffset()==0)return ev(op.getInput(0),d+1,seen);
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
  Register spReg;
  boolean isConst(Varnode v){return v!=null&&v.isConstant();}
  boolean isZero(Varnode v){return isConst(v)&&(v.getOffset()&U32)==0;}
  boolean isSp(Varnode v){return v.isRegister()&&v.getAddress().equals(spReg.getAddress());}
  String base(Varnode v,int d,Set<Varnode> seen){
    if(v==null||d>24||!seen.add(v))return "?";
    if(v.isConstant())return v.getAddress().isStackAddress()?"stack":"const";
    if(v.isRegister()){
      if(isSp(v))return "stack";
      Register r=currentProgram.getRegister(v);
      return "reg:"+(r==null?v.toString():r.getName());
    }
    PcodeOp op=v.getDef();if(op==null)return "reg?";
    int c=op.getOpcode();
    if(c==PcodeOp.COPY||c==PcodeOp.CAST||c==PcodeOp.INDIRECT||c==PcodeOp.INT_ZEXT||c==PcodeOp.INT_SEXT||c==PcodeOp.SUBPIECE)return base(op.getInput(0),d+1,seen);
    if(c==PcodeOp.LOAD)return "load";
    if(c==PcodeOp.CALL||c==PcodeOp.CALLIND||c==PcodeOp.CALLOTHER)return "callret";
    if(c==PcodeOp.MULTIEQUAL){TreeSet<String> s=new TreeSet<>();for(int i=0;i<op.getNumInputs();i++)s.add(base(op.getInput(i),d+1,new HashSet<>(seen)));return "phi{"+String.join("/",s)+"}";}
    if(c==PcodeOp.PTRSUB||c==PcodeOp.PTRADD||c==PcodeOp.INT_ADD||c==PcodeOp.INT_SUB||c==PcodeOp.INT_MULT||c==PcodeOp.INT_LEFT||c==PcodeOp.INT_AND||c==PcodeOp.INT_OR||c==PcodeOp.INT_XOR){
      Varnode a=op.getInput(0),b=op.getInput(1);
      if(isZero(a)&&!isZero(b))return base(b,d+1,seen);
      if(isConst(b))return base(a,d+1,seen);
      if(isConst(a))return base(b,d+1,seen);
      if((c==PcodeOp.INT_MULT||c==PcodeOp.INT_LEFT)&&!(isSp(a)||isSp(b)))return "scaled("+base(a,d+1,seen)+","+base(b,d+1,new HashSet<>(seen))+")";
      return base(a,d+1,seen)+"+var("+base(b,d+1,new HashSet<>(seen))+")";
    }
    return PcodeOp.getMnemonic(c).toLowerCase();
  }
  String kind(String shape){
    return shape.replaceAll("\\+var\\(.*\\)|scaled\\(.*\\)","+var").replaceAll("reg:[a-z0-9]+","reg");
  }
  public void run() throws Exception {
    spReg=currentProgram.getCompilerSpec().getStackPointer();
    DecompInterface di=new DecompInterface();di.openProgram(currentProgram);
    FunctionIterator fi=currentProgram.getFunctionManager().getFunctions(true);
    long fn=0,stores=0,unknown=0;TreeMap<String,Long> shapes=new TreeMap<>();
    while(fi.hasNext()){
      Function f=fi.next();DecompileResults dr=di.decompileFunction(f,30,monitor);HighFunction hf=dr.getHighFunction();if(hf==null)continue;fn++;
      Iterator<PcodeOpAST> it=hf.getPcodeOps();
      while(it.hasNext()){
        PcodeOpAST op=it.next();if(op.getOpcode()!=PcodeOp.STORE)continue;stores++;
        if(ev(op.getInput(1),0,new HashSet<>()).known)continue;unknown++;
        String shape=base(op.getInput(1),0,new HashSet<>());shapes.merge(kind(shape),1L,Long::sum);
        println(String.format("UNK|%s|%s|%s|expr=%s",f.getEntryPoint(),op.getSeqnum().getTarget(),shape,ex(op.getInput(1),0,new HashSet<>())));
      }
    }
    for(String k:shapes.keySet())println(String.format("SHAPE|%s|%d",k,shapes.get(k)));
    println("SUMMARY|functions="+fn+"|stores="+stores+"|unknownRangeStores="+unknown);
    di.dispose();
  }
}
