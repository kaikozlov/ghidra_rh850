//@author kaikozlov
//@category Analysis
// Throwaway: create functions along the yc Venza RPRG (boot.bin extended-user
// image at 0x01000000) SID-0x34/0x36/0x37 chain that auto-analysis skipped.

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Instruction;

public class MarkVenzaRprgDownloadChain extends GhidraScript {
    @Override
    public void run() throws Exception {
        long[] addrs = {
            0x010063b2L, 0x010028a0L, 0x010028b0L, 0x01002974L, 0x01002710L,
            0x01003f14L, 0x01004036L, 0x01003e3aL, 0x01003e86L,
            0x01004130L, 0x01004148L, 0x01004d44L,
        };
        String[] names = {
            "rprg_download_accept_crypto_check", "rprg_state_grant_a",
            "rprg_state_grant_b", "rprg_format_byte_decode",
            "rprg_download_addrsize_extract", "rprg_request_download_setup",
            "rprg_request_download_dispatch", "rprg_download_addrfmt_parse",
            "rprg_download_req_validate", "rprg_transfer_data_service",
            "rprg_transfer_data_core", "rprg_transfer_exit_service",
        };
        for (int i = 0; i < addrs.length; i++) {
            Address a = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(addrs[i]);
            Instruction ins = currentProgram.getListing().getInstructionAt(a);
            if (ins == null) {
                DisassembleCommand dc = new DisassembleCommand(a, new AddressSet(a, a.add(0x600)), false);
                dc.applyTo(currentProgram, monitor);
            }
            boolean ok = new CreateFunctionCmd(names[i], a, null,
                ghidra.program.model.symbol.SourceType.USER_DEFINED)
                .applyTo(currentProgram, monitor);
            println(String.format("0x%08x %s -> %b", addrs[i], names[i], ok));
        }
    }
}
