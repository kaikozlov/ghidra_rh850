import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.SourceType;

public class SeedCamryF33TxFreshness extends GhidraScript {
    @Override
    public void run() throws Exception {
        Address entry = toAddr(0x000903F6L);
        Address end = toAddr(0x00090429L);
        FunctionManager fm = currentProgram.getFunctionManager();
        Function existing = fm.getFunctionAt(entry);
        if (existing == null) {
            AddressSet body = new AddressSet(entry, end);
            existing = fm.createFunction("f33_secoc_tx_freshness", entry, body, SourceType.USER_DEFINED);
        }
        if (existing == null) throw new IllegalStateException("failed to create 0x903F6 Tx freshness callback");
        if (!"f33_secoc_tx_freshness".equals(existing.getName())) {
            existing.setName("f33_secoc_tx_freshness", SourceType.USER_DEFINED);
        }
        println(String.format("seeded %s @ %s body=%s", existing.getName(), existing.getEntryPoint(), existing.getBody()));
    }
}
