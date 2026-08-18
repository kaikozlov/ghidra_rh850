//@author kaikozlov
//@category Analysis
// Resolve the callback-free ephemeral-runtime control/queue/COM skeleton from a
// fresh CodeFlash import. This is deliberately Level-1/fail-closed: it accepts
// only the machine/CFG shapes recovered on 8965B4512000 and emits ambiguity
// instead of inheriting known offsets.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.scalar.Scalar;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;
import java.util.regex.*;

public class ResolveEphemeralRuntime extends GhidraScript {
    static class Candidate {
        Function bootHandoff, startup, context, foreground, aggregate, comRx, queueHelper, timeoutHelper;
        Address startupFirst, startupAfter, startupFinalInit;
        int startupCount;
        List<Instruction> bootTransitionCalls = new ArrayList<>();
        List<Instruction> foregroundCalls = new ArrayList<>();
        List<Instruction> aggregateCalls = new ArrayList<>();
        int foregroundAggregateIndex = -1;
        int foregroundTimingBeginIndex = -1;
        int foregroundTimingEndIndex = -1;
        int aggregateGateIndex = -1;
        int tickBit;
        long tickDisp;
        Address timingFlag;
        Address tickCounter;
        Address descBase, queueHeadBase, rawBase, updateCounterBase, validityBase;
    }

    private String hex(Address a) { return a == null ? null : String.format("0x%X", a.getOffset()); }
    private String hex(long v) { return String.format("0x%X", v); }
    private String esc(String s) { return s.replace("\\", "\\\\").replace("\"", "\\\""); }

    private boolean directCall(Instruction i) {
        return i != null && i.getFlowType().isCall() && !i.getFlowType().isComputed() && i.getFlows().length == 1;
    }
    private Function targetFunction(Instruction i) {
        if (!directCall(i)) return null;
        return currentProgram.getFunctionManager().getFunctionAt(i.getFlows()[0]);
    }
    private List<Instruction> instructions(Function f) {
        List<Instruction> out = new ArrayList<>();
        InstructionIterator it = currentProgram.getListing().getInstructions(f.getBody(), true);
        while (it.hasNext()) out.add(it.next());
        return out;
    }
    private boolean movZeroR6(Instruction i) {
        return i != null && "mov".equals(i.getMnemonicString()) && i.getNumOperands() >= 2 &&
            "0x0".equals(i.getDefaultOperandRepresentation(0)) && "r6".equals(i.getDefaultOperandRepresentation(1));
    }
    private boolean contextShape(Function f) {
        if (f == null) return false;
        boolean intbp=false, ebase=false, gp=false, tp=false, sp=false, ret=false;
        for (Instruction i: instructions(f)) {
            String m=i.getMnemonicString(); String s=i.toString();
            if ("ldsr".equals(m) && s.contains("INTBP")) intbp=true;
            if ("ldsr".equals(m) && s.contains("EBASE")) ebase=true;
            if ("mov".equals(m) && s.endsWith(",gp")) gp=true;
            if ("mov".equals(m) && s.endsWith(",tp")) tp=true;
            if ("mov".equals(m) && s.endsWith(",sp")) sp=true;
            if ("jmp".equals(m) && s.contains("lp")) ret=true;
        }
        return intbp && ebase && gp && tp && sp && ret;
    }
    private Candidate startupCandidate(Function f) {
        List<Instruction> is = instructions(f);
        for (int ei=0; ei<is.size(); ei++) {
            if (!"ei".equals(is.get(ei).getMnemonicString())) continue;
            if (ei < 4 || ei+1 >= is.size() || !directCall(is.get(ei+1))) continue;
            if (!directCall(is.get(ei-1)) || !movZeroR6(is.get(ei-2))) continue;
            int end=ei-3, runStart=end;
            while (runStart >= 0 && directCall(is.get(runStart))) runStart--;
            runStart++;
            // The contiguous run begins with the application-context initializer,
            // followed by the replayable startup JARLs. Require that first target
            // to carry the EBASE/INTBP/GP/TP/SP context shape instead of treating
            // it as part of the replay list.
            Function ctx=targetFunction(is.get(runStart));
            if (!contextShape(ctx)) continue;
            int start=runStart+1;
            int count=end-start+1;
            if (count < 8 || count > 64) continue;
            Candidate c=new Candidate();
            c.startup=f; c.context=ctx; c.foreground=targetFunction(is.get(ei+1));
            c.startupFirst=is.get(start).getAddress();
            c.startupAfter=is.get(end).getAddress().add(is.get(end).getLength());
            c.startupFinalInit=targetFunction(is.get(ei-1)).getEntryPoint();
            c.startupCount=count;
            if (c.foreground == null) continue;
            return c;
        }
        return null;
    }

    private boolean reaches(Function from, Address target, int maxDepth) {
        if (from == null) return false;
        Deque<Object[]> q=new ArrayDeque<>(); Set<Address> seen=new HashSet<>();
        q.add(new Object[]{from,0}); seen.add(from.getEntryPoint());
        while(!q.isEmpty()) {
            Object[] x=q.removeFirst(); Function f=(Function)x[0]; int d=(Integer)x[1];
            if (f.getEntryPoint().equals(target)) return true;
            if (d>=maxDepth) continue;
            for (Instruction i: instructions(f)) if (directCall(i)) {
                Function t=targetFunction(i);
                if (t!=null && seen.add(t.getEntryPoint())) q.add(new Object[]{t,d+1});
            }
        }
        return false;
    }

    private Function findBootHandoff(Candidate c) {
        List<Function> hits=new ArrayList<>();
        Map<Function,List<Instruction>> hitCalls=new HashMap<>();
        FunctionIterator fi=currentProgram.getFunctionManager().getFunctions(true);
        while(fi.hasNext()) {
            Function f=fi.next(); List<Instruction> is=instructions(f);
            if(is.size()<12) continue;
            int run=-1;
            for(int i=0;i+7<is.size();i++) {
                boolean five=true;
                for(int j=0;j<5;j++) if(!directCall(is.get(i+j))) { five=false; break; }
                if(!five) continue;
                if(!"cmp".equals(is.get(i+5).getMnemonicString()) ||
                   !is.get(i+5).toString().contains("r0,r10") ||
                   !"be".equals(is.get(i+6).getMnemonicString())) continue;
                boolean computed=false;
                for(int k=i+7;k<Math.min(is.size(),i+32);k++)
                    if(is.get(k).getFlowType().isCall() && is.get(k).getFlowType().isComputed()) { computed=true; break; }
                if(computed) { run=i; break; }
            }
            if(run<0) continue;
            List<Instruction> calls=new ArrayList<>();
            for(int j=0;j<5;j++) calls.add(is.get(run+j));
            hits.add(f); hitCalls.put(f,calls);
        }
        if(hits.size()!=1) return null;
        Function f=hits.get(0); c.bootTransitionCalls=hitCalls.get(f); return f;
    }

    private boolean parseForeground(Candidate c, Address gate) {
        List<Instruction> is=instructions(c.foreground);
        int tst=-1;
        for(int i=0;i+2<is.size();i++) {
            if (!"tst1".equals(is.get(i).getMnemonicString())) continue;
            if (!"be".equals(is.get(i+1).getMnemonicString())) continue;
            if (!"clr1".equals(is.get(i+2).getMnemonicString())) continue;
            if (!is.get(i).getDefaultOperandRepresentation(0).equals(is.get(i+2).getDefaultOperandRepresentation(0))) continue;
            if (!is.get(i).getDefaultOperandRepresentation(1).equals(is.get(i+2).getDefaultOperandRepresentation(1))) continue;
            tst=i; break;
        }
        if (tst<0) return false;
        try {
            Scalar bit=(Scalar)is.get(tst).getOpObjects(0)[0];
            Scalar disp=(Scalar)is.get(tst).getOpObjects(1)[0];
            c.tickBit=(int)bit.getUnsignedValue(); c.tickDisp=disp.getSignedValue();
        } catch(Exception e) { return false; }
        Map<Address,Integer> refs=new HashMap<>();
        for(Instruction ins:is) for(Reference r:ins.getReferencesFrom()) if(r.getReferenceType().isData())
            refs.put(r.getToAddress(), refs.getOrDefault(r.getToAddress(),0)+1);
        for(Address a:refs.keySet()) {
            long v=a.getOffset();
            if(v < 0x100000 && c.timingFlag==null) c.timingFlag=a;
            if(v >= 0xFEBE0000L && v < 0xFEC00000L) c.tickCounter=a;
        }
        for(Instruction ins:is) if(directCall(ins)) c.foregroundCalls.add(ins);
        if(c.foregroundCalls.size()<5 || c.foregroundCalls.size()>16) return false;
        List<Instruction> owners=new ArrayList<>();
        for(Instruction ins:c.foregroundCalls) {
            Function t=targetFunction(ins); if(reaches(t,gate,10)) owners.add(ins);
        }
        if(owners.size()!=1) return false;
        Instruction owner=owners.get(0);
        c.foregroundAggregateIndex=c.foregroundCalls.indexOf(owner);
        // Level-1 scheduler shape: timing instrumentation is the first/last
        // direct call around the ordinary task sequence, with the SecOC-owning
        // aggregate strictly inside that interval.
        c.foregroundTimingBeginIndex=0;
        c.foregroundTimingEndIndex=c.foregroundCalls.size()-1;
        if(c.foregroundAggregateIndex<=c.foregroundTimingBeginIndex ||
           c.foregroundAggregateIndex>=c.foregroundTimingEndIndex) return false;
        c.aggregate=targetFunction(owner);
        for(Instruction ins:instructions(c.aggregate)) if(directCall(ins)) c.aggregateCalls.add(ins);
        if(c.aggregateCalls.size()!=6) return false;
        for(int i=0;i<c.aggregateCalls.size();i++)
            if(reaches(targetFunction(c.aggregateCalls.get(i)),gate,10)) {
                if(c.aggregateGateIndex!=-1) return false; c.aggregateGateIndex=i;
            }
        return c.aggregateGateIndex==1;
    }

    private Function findComRx() {
        List<Function> hits=new ArrayList<>();
        FunctionIterator fi=currentProgram.getFunctionManager().getFunctions(true);
        while(fi.hasNext()) {
            Function f=fi.next(); List<Instruction> is=instructions(f);
            if(is.size()<10) continue;
            String[] want={"prepare","mov","zxh","mov","mov","shl","add","ld.bu","ld.bu","movea"};
            boolean ok=true; for(int i=0;i<want.length;i++) if(!want[i].equals(is.get(i).getMnemonicString())) {ok=false;break;}
            if(!ok) continue;
            if(!is.get(1).toString().contains("r6,r29") || !is.get(2).toString().contains("r29") ||
               !is.get(3).toString().contains("r7,r27") || !is.get(5).toString().contains("0x3,r28")) continue;
            boolean computed=false;
            for(Instruction i:is) if(i.getFlowType().isCall() && i.getFlowType().isComputed()) computed=true;
            if(computed) hits.add(f);
        }
        return hits.size()==1 ? hits.get(0) : null;
    }

    private Function findTimeoutHelper(Function comRx, Candidate c) {
        if(comRx==null) return null;
        List<Function> hits=new ArrayList<>();
        for(Instruction call:instructions(comRx)) if(directCall(call)) {
            Function f=targetFunction(call); if(f==null) continue;
            Map<Address,Integer> local=new HashMap<>();
            for(Instruction i:instructions(f)) for(Reference r:i.getReferencesFrom()) if(r.getReferenceType().isData()) {
                long a=r.getToAddress().getOffset();
                if(a>=0xFEBE0000L && a<0xFEC00000L)
                    local.put(r.getToAddress(),local.getOrDefault(r.getToAddress(),0)+1);
            }
            Address twice=null, once=null;
            for(Map.Entry<Address,Integer> e:local.entrySet()) {
                if(e.getValue()>=2) twice=e.getKey(); else if(e.getValue()==1) once=e.getKey();
            }
            if(twice!=null && once!=null && local.size()==2) {
                hits.add(f); c.updateCounterBase=twice; c.validityBase=once;
            }
        }
        return hits.size()==1 ? hits.get(0) : null;
    }

    private Function findQueueHelper(Candidate c) {
        List<Function> hits=new ArrayList<>();
        Map<Function,List<Address>> hitRefs=new HashMap<>();
        FunctionIterator fi=currentProgram.getFunctionManager().getFunctions(true);
        while(fi.hasNext()) {
            Function f=fi.next(); List<Instruction> is=instructions(f);
            if(is.size()<14 || is.size()>24) continue;
            // Generated queue-storage accessor shape:
            // zxh r6; cmp 1,r6; bne; mov r7,ep;
            // movea BASE0; sst.w [ep+0]; movea BASE1; sst.w [ep+4];
            // movea BASE2; sst.w [ep+8]; mov 6; sst.h [ep+0xc]; jmp lp.
            String[] prefix={"zxh","cmp","bne","mov","movea","sst.w","mov","movea","sst.w","movea","sst.w","mov","sst.h","jmp"};
            boolean shape=true;
            for(int i=0;i<prefix.length;i++) if(!prefix[i].equals(is.get(i).getMnemonicString())) { shape=false; break; }
            if(!shape || !is.get(0).toString().contains("r6") || !is.get(3).toString().contains("r7,ep")) continue;
            List<Address> refs=new ArrayList<>();
            // Ghidra attaches the resolved DATA reference to the sst.w store
            // rather than the preceding movea that materializes its base.
            for(int idx: new int[]{5,8,10}) {
                Address found=null;
                for(Reference r:is.get(idx).getReferencesFrom()) if(r.getReferenceType().isData()) {
                    long a=r.getToAddress().getOffset();
                    if(a>=0xFEBE0000L && a<0xFEC00000L) found=r.getToAddress();
                }
                if(found==null) { shape=false; break; }
                refs.add(found);
            }
            if(!shape) continue;
            long lo=Long.MAX_VALUE, hi=0;
            for(Address a:refs){ lo=Math.min(lo,a.getOffset()); hi=Math.max(hi,a.getOffset()); }
            if(hi-lo>0x80) continue;
            hits.add(f); hitRefs.put(f,refs);
        }
        if(hits.size()!=1) return null;
        Function f=hits.get(0); List<Address> refs=hitRefs.get(f);
        // Preserve semantic order from the generated stores, not numeric order.
        c.descBase=refs.get(0); c.queueHeadBase=refs.get(1); c.rawBase=refs.get(2);
        return f;
    }

    private Address readGate(String path) throws Exception {
        String s=Files.readString(new File(path).toPath(), StandardCharsets.UTF_8);
        Matcher m=Pattern.compile("\\\"function\\\"\\s*:\\s*\\{[^}]*\\\"entry\\\"\\s*:\\s*\\\"(0x[0-9A-Fa-f]+)\\\"").matcher(s);
        if(!m.find()) throw new RuntimeException("gate resolution lacks function.entry");
        return toAddr(Long.decode(m.group(1)));
    }

    public void run() throws Exception {
        String[] args=getScriptArgs(); if(args.length!=2) throw new IllegalArgumentException("usage: <gate.json> <out.json>");
        Address gate=readGate(args[0]); List<Candidate> candidates=new ArrayList<>();
        FunctionIterator fi=currentProgram.getFunctionManager().getFunctions(true);
        while(fi.hasNext()) { Candidate c=startupCandidate(fi.next()); if(c!=null && parseForeground(c,gate)) candidates.add(c); }
        Candidate c = candidates.size()==1 ? candidates.get(0) : null;
        if(c!=null) {
            c.bootHandoff=findBootHandoff(c);
            c.comRx=findComRx(); c.timeoutHelper=findTimeoutHelper(c.comRx,c); c.queueHelper=findQueueHelper(c);
        }
        boolean controlOk=c!=null && c.timingFlag!=null;
        boolean complete=controlOk && c.bootHandoff!=null && c.bootTransitionCalls.size()==5 &&
            c.comRx!=null && c.timeoutHelper!=null && c.queueHelper!=null && c.tickCounter!=null;
        String status=complete?"resolved":controlOk?"control-resolved":"unresolved";
        StringBuilder j=new StringBuilder(); j.append("{\n");
        j.append("  \"schema\": \"p1me-ephemeral-runtime-semantic-v1\",\n");
        j.append("  \"status\": \"").append(status).append("\",\n");
        j.append("  \"candidate_count\": ").append(candidates.size()).append(",\n");
        j.append("  \"gate_entry\": \"").append(hex(gate)).append("\"");
        if(c!=null) {
            j.append(",\n  \"anchors\": {\n");
            j.append("    \"boot_application_handoff\": \"").append(c.bootHandoff==null?"":hex(c.bootHandoff.getEntryPoint())).append("\",\n");
            j.append("    \"boot_transition_call_targets\": [");
            for(int i=0;i<c.bootTransitionCalls.size();i++){ if(i>0)j.append(", "); j.append("\"").append(hex(c.bootTransitionCalls.get(i).getFlows()[0])).append("\""); }
            j.append("],\n    \"boot_validity_call_index\": 4,\n");
            j.append("    \"startup_coordinator\": \"").append(hex(c.startup.getEntryPoint())).append("\",\n");
            j.append("    \"application_context_init\": \"").append(hex(c.context.getEntryPoint())).append("\",\n");
            j.append("    \"startup_jarl_first\": \"").append(hex(c.startupFirst)).append("\",\n");
            j.append("    \"startup_jarl_after\": \"").append(hex(c.startupAfter)).append("\",\n");
            j.append("    \"startup_jarl_count\": ").append(c.startupCount).append(",\n");
            j.append("    \"startup_final_init\": \"").append(hex(c.startupFinalInit)).append("\",\n");
            j.append("    \"foreground_loop\": \"").append(hex(c.foreground.getEntryPoint())).append("\",\n");
            j.append("    \"tick_bit\": ").append(c.tickBit).append(",\n");
            j.append("    \"tick_displacement\": ").append(c.tickDisp).append(",\n");
            j.append("    \"timing_flag\": \"").append(hex(c.timingFlag)).append("\",\n");
            j.append("    \"foreground_tick_counter\": \"").append(hex(c.tickCounter)).append("\",\n");
            j.append("    \"foreground_timing_begin_call_index\": ").append(c.foregroundTimingBeginIndex).append(",\n");
            j.append("    \"foreground_aggregate_call_index\": ").append(c.foregroundAggregateIndex).append(",\n");
            j.append("    \"foreground_timing_end_call_index\": ").append(c.foregroundTimingEndIndex).append(",\n");
            j.append("    \"aggregate\": \"").append(hex(c.aggregate.getEntryPoint())).append("\",\n");
            j.append("    \"aggregate_gate_call_index\": ").append(c.aggregateGateIndex).append(",\n");
            j.append("    \"aggregate_bridge_after_call_index\": 3,\n");
            j.append("    \"aggregate_control_call_index\": 4,\n");
            j.append("    \"com_rx_indication\": \"").append(c.comRx==null?"":hex(c.comRx.getEntryPoint())).append("\",\n");
            j.append("    \"com_timeout_helper\": \"").append(c.timeoutHelper==null?"":hex(c.timeoutHelper.getEntryPoint())).append("\",\n");
            j.append("    \"com_update_counter_base\": \"").append(c.updateCounterBase==null?"":hex(c.updateCounterBase)).append("\",\n");
            j.append("    \"com_validity_base\": \"").append(c.validityBase==null?"":hex(c.validityBase)).append("\",\n");
            j.append("    \"secoc_queue_storage_helper\": \"").append(c.queueHelper==null?"":hex(c.queueHelper.getEntryPoint())).append("\",\n");
            j.append("    \"secoc_descriptor_base\": \"").append(c.descBase==null?"":hex(c.descBase)).append("\",\n");
            j.append("    \"secoc_queue_head_base\": \"").append(c.queueHeadBase==null?"":hex(c.queueHeadBase)).append("\",\n");
            j.append("    \"secoc_raw_buffer_base\": \"").append(c.rawBase==null?"":hex(c.rawBase)).append("\",\n");
            j.append("    \"foreground_call_targets\": [");
            for(int i=0;i<c.foregroundCalls.size();i++){ if(i>0)j.append(", "); j.append("\"").append(hex(c.foregroundCalls.get(i).getFlows()[0])).append("\""); }
            j.append("],\n    \"aggregate_call_targets\": [");
            for(int i=0;i<c.aggregateCalls.size();i++){ if(i>0)j.append(", "); j.append("\"").append(hex(c.aggregateCalls.get(i).getFlows()[0])).append("\""); }
            j.append("]\n  }");
        }
        j.append("\n}\n"); Files.writeString(new File(args[1]).toPath(),j.toString(),StandardCharsets.UTF_8);
        println("EPHEMERAL_RUNTIME_RESOLUTION="+status+" candidates="+candidates.size());
    }
}
