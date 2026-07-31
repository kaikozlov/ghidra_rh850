// Force-create functions at addresses passed as args, then disassemble
// @category Analysis
// @args-off
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.app.cmd.function.CreateFunctionCmd;

public class ForceFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        AddressFactory af = currentProgram.getAddressFactory();
        AddressSpace space = af.getDefaultAddressSpace();
        FunctionManager fm = currentProgram.getFunctionManager();
        
        for (String arg : args) {
            long addr = Long.parseLong(arg.replace("0x", "").replace("0X", ""), 16);
            Address a = space.getAddress(addr);
            
            // Create function
            CreateFunctionCmd cmd = new CreateFunctionCmd(a);
            cmd.applyTo(currentProgram);
            
            Function f = fm.getFunctionAt(a);
            if (f != null) {
                println("Created function at 0x" + Long.toHexString(addr) + ": " + f.getName() + " (" + f.getBody().getNumAddresses() + " bytes)");
            } else {
                println("Failed to create function at 0x" + Long.toHexString(addr));
            }
        }
    }
}
