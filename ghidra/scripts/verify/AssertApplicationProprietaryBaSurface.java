//@author kaikozlov
//@category Verification
// Read-only topology assertion for application SID 0xBA proprietary operations.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.util.*;

public class AssertApplicationProprietaryBaSurface extends GhidraScript {
    @Override public void run() throws Exception {
        long[] starts={0x34b74L,0x34ba8L,0x34c50L,0x34c84L,0x34cb8L,0x34daeL,0x34ec0L,0x34f1aL,0x34f4eL,0x34f90L};
        long[] dones ={0x34b9aL,0x34bf4L,0x34c76L,0x34caaL,0x34d4eL,0x34e6cL,0x34f08L,0x34f40L,0x34f80L,0x34faaL};
        for(int i=0;i<10;i++){
            assertExactRefsByType(starts[i], "DATA", String.format("%08x:DATA",0x280a0L+i*16L));
            assertExactRefsByType(dones[i], "DATA", String.format("%08x:DATA",0x280a4L+i*16L));
        }
        assertExactRefs(0x34d96L,"00034db4:UNCONDITIONAL_CALL");
        assertExactRefs(0x8c8c6L,"00034d9a:UNCONDITIONAL_CALL");
        assertExactRefsByType(0xfebe5f27L,"READ","000348d6:READ","00034fbe:READ");
        assertExactRefsByType(0xfebe5f28L,"READ","00034fc0:READ");
        assertExactRefs(0xfebee894L,
            "0004ce4a:READ","000bcbea:WRITE","000be412:WRITE");
        assertExactRefs(0xfebeb116L,
            "000b20d4:WRITE","000ba2fe:READ","000bc5ca:READ","000bdb08:WRITE");
        assertExactRefs(0xfebeb117L,
            "000b20d8:WRITE","000bc5c8:READ","000bdb0a:WRITE");

        Set<Long> forbidden=new HashSet<>(Arrays.asList(
            0xfebe7f94L,0xfebef184L,0xfebeae20L,0xfebebf80L,0xfebebf84L,0xfebebf9aL,
            0xfebebfa2L,0xfebeacffL,0xfebeae60L,0xfebebff0L,0xfebec0beL,0xfebec0c8L,
            0xfebec0d6L,0xfebec144L,0xfebec170L,0xfebec1b8L,0xfebec1b4L,0xfebec1bcL,
            0xfebec1d4L,0xfebeb788L,0xfebeb87eL,0xfebeae16L,0xfebeae6eL,
            0xfebe6d18L,0xfebe6d1cL,0xfebe6d28L,0xfebe6d2aL));
        long[] cone={
            0x3485aL,0x34882L,0x348b4L,0x34946L,0x347b0L,0x34fb6L,0x65cd8L,0x65d34L,
            0x34b74L,0x34b9aL,0xb201aL,0xb209cL,0x34ba8L,0x34bf4L,0x3b252L,0x38dcaL,0x47958L,
            0x34c50L,0x34c76L,0x34c84L,0x34caaL,0x34cb8L,0x34d4eL,0x34d96L,0x34daeL,0x34e6cL,
            0x8c8c6L,0x8fdcaL,0x34ec0L,0x34f08L,0xb7d26L,0x34f1aL,0x34f40L,0x34f4eL,0x34f80L,
            0xb20ccL,0xbc5bcL,0x34f90L,0x34faaL,0xb20dcL,0xb80eeL};
        int checked=0;
        for(long entry:cone){
            Function f=getFunctionAt(toAddr(entry));
            if(f==null) throw new IllegalStateException(String.format("missing BA-cone function %06X",entry));
            checked++;
            InstructionIterator it=currentProgram.getListing().getInstructions(f.getBody(),true);
            while(it.hasNext()){
                monitor.checkCancelled(); Instruction ins=it.next();
                for(Reference ref:ins.getReferencesFrom()){
                    Address target=ref.getToAddress();
                    if(target!=null && target.isMemoryAddress() && forbidden.contains(target.getOffset()))
                        throw new IllegalStateException(String.format("%06X gained direct conditioned-command/dq ref %s -> %s",entry,ins.getAddress(),target));
                }
            }
        }
        println(String.format("ASSERT application-proprietary-ba: starts=10 completions=10 marker_readers=2 countdown_readers=1 vspda_snapshot_readers=1 cone_functions=%d direct_actuation_refs=0 unexpected=0",checked));
    }
    private void assertExactRefs(long target,String... expectedEntries){
        Set<String> expected=new TreeSet<>(Arrays.asList(expectedEntries)),actual=new TreeSet<>();
        for(Reference r:getReferencesTo(toAddr(target))) actual.add(r.getFromAddress().toString()+":"+r.getReferenceType());
        if(!actual.equals(expected)){Set<String> m=new TreeSet<>(expected);m.removeAll(actual);Set<String>x=new TreeSet<>(actual);x.removeAll(expected);throw new IllegalStateException(String.format("xref topology changed for %s missing=%s extra=%s",toAddr(target),m,x));}
    }
    private void assertExactRefsByType(long target,String type,String... expectedEntries){
        Set<String> expected=new TreeSet<>(Arrays.asList(expectedEntries)),actual=new TreeSet<>();
        for(Reference r:getReferencesTo(toAddr(target))) if(r.getReferenceType().toString().equals(type)) actual.add(r.getFromAddress().toString()+":"+r.getReferenceType());
        if(!actual.equals(expected)){Set<String> m=new TreeSet<>(expected);m.removeAll(actual);Set<String>x=new TreeSet<>(actual);x.removeAll(expected);throw new IllegalStateException(String.format("xref type %s changed for %s missing=%s extra=%s",type,toAddr(target),m,x));}
    }
}
