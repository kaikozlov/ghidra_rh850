//@author kaikozlov
//@category Seed
// Seed the exact Venza airbag 8917048E30 diagnostic surface recovered from the
// DCM/RoutineControl analysis: session transition, SID 0x10 programming route,
// RID dispatch, RID 0x1010 ECU Security Key update, and the WDBI DID
// 0x0201/0x0202 payload-credential writers. Geometry checks pin the two
// recovered tables before seeding.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.SourceType;
public class SeedVenzaAirbagDiagnostics extends GhidraScript {
  private Function ensure(long v,String name) throws Exception { Address a=toAddr(v); Listing l=currentProgram.getListing(); Instruction c=l.getInstructionContaining(a); if(c!=null&&!c.getMinAddress().equals(a)) l.clearCodeUnits(c.getMinAddress(),c.getMaxAddress(),false); CodeUnit u=l.getCodeUnitContaining(a); if(u!=null&&!(u instanceof Instruction)) l.clearCodeUnits(u.getMinAddress(),u.getMaxAddress(),false); if(l.getInstructionAt(a)==null&&!disassemble(a)) throw new IllegalStateException("disassembly failed "+a); Function f=currentProgram.getFunctionManager().getFunctionAt(a); if(f==null) f=createFunction(a,name); if(f==null) throw new IllegalStateException("function creation failed "+a); if(!name.equals(f.getName())) f.setName(name,SourceType.USER_DEFINED); return f; }
  @Override public void run() throws Exception {
    int ridCount = currentProgram.getMemory().getShort(toAddr(0x2506CL)) & 0xffff;
    int rid9 = currentProgram.getMemory().getShort(toAddr(0x255E4L + 9*8L)) & 0xffff;
    if (ridCount != 19 || rid9 != 0x1010)
      throw new IllegalStateException(String.format("RoutineControl geometry drift count=%d idx9=%04x", ridCount, rid9));
    int sub02Handler = currentProgram.getMemory().getInt(toAddr(0x237E0L)) & 0xffffffff;
    int sub02 = currentProgram.getMemory().getShort(toAddr(0x237EAL)) & 0xffff;
    if (sub02Handler != 0xC190C || sub02 != 0x02)
      throw new IllegalStateException(String.format("SID 0x10 subfunction table drift handler=%08x row1=%04x", sub02Handler, sub02));

    ensure(0xC32D8L,"venza_dcm_session_transition_core");
    ensure(0xC18ECL,"venza_dcm_sid10_subfunction01");
    ensure(0xC190CL,"venza_dcm_sid10_subfunction02_programming");
    ensure(0xC18FCL,"venza_dcm_sid10_subfunction03");
    ensure(0xC192EL,"venza_dcm_sid10_subfunction04");
    ensure(0xC191CL,"venza_dcm_sid10_subfunction40");
    ensure(0xC772CL,"venza_sid10_02_policy");
    ensure(0xC76C6L,"venza_sid10_02_handoff_writer");
    ensure(0xC780EL,"venza_sid10_02_halt_transition");
    ensure(0xC1C06L,"venza_dcm_rid_start_dispatcher");
    ensure(0xC1B00L,"venza_dcm_rid_result_dispatcher");
    ensure(0xC6672L,"venza_dcm_routine_dispatcher");
    ensure(0x69458L,"venza_rid1010_start_wrapper");
    ensure(0x69476L,"venza_rid1010_result_wrapper");
    ensure(0x7B306L,"venza_rid1010_start_staging");
    ensure(0x7B3A6L,"venza_rid1010_result_reader");
    ensure(0x654AL,"venza_dcm_wdbi_dispatcher");
    ensure(0x64DEL,"venza_dcm_wdbi_did0201_writer");
    ensure(0x6514L,"venza_dcm_wdbi_did0202_writer");
    println("SeedVenzaAirbagDiagnostics: seeded 19 exact Venza airbag diagnostic functions");
  }
}
