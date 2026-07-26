//@author kaikozlov
//@category Investigation
// Inspect candidate switch sites: for each address report inbound references
// (is the site reachable code at all?), the preceding instruction sequence
// (a real GHS switch is always preceded by a range bound check), the table's
// first entries with their computed targets, and whether each target lands on
// an instruction start. Read-only. Pass addresses as hex args, e.g.
//   InspectSwitchSites.java 0x18484 0x1b374
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.util.ArrayList;
import java.util.List;

public class InspectSwitchSites extends GhidraScript {
    private String fmt(Instruction insn) {
        if (insn == null) return "<none>";
        return String.format("%08x  %s", insn.getAddress().getOffset(),
                insn.toString().replaceAll("\\s+", " ").trim());
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length == 0) {
            println("no addresses supplied");
            return;
        }
        Listing listing = currentProgram.getListing();
        for (String s : args) {
            long addr;
            try {
                addr = Long.parseLong(s.replaceFirst("0x", ""), 16);
            } catch (NumberFormatException e) {
                println("bad address: " + s);
                continue;
            }
            Instruction sw = listing.getInstructionAt(toAddr(addr));
            println("==============================================================");
            if (sw == null) {
                println(String.format("0x%08x: no instruction at address (data/undefined)", addr));
                // Report inbound refs anyway
                printRefs(addr);
                continue;
            }
            println(String.format("site 0x%08x  mnemonic=%s len=%d", addr,
                    sw.getMnemonicString(), sw.getLength()));

            // Inbound references: is this site reachable?
            printRefs(addr);

            // Preceding 14 instructions (bound-check hunt)
            println("-- preceding 14 instructions --");
            Instruction cur = sw;
            for (int i = 0; i < 14; i++) {
                cur = cur.getPrevious();
                if (cur == null) break;
                println("  " + fmt(cur));
            }

            // Table layout
            int len = sw.getLength();
            long tableBase = addr + len;
            println(String.format("-- table @ 0x%08x (first 8 signed-halfword entries) --",
                    tableBase));
            for (int i = 0; i < 8; i++) {
                short off = getShort(toAddr(tableBase + i * 2L));
                long tgt = tableBase + (((long) off) << 1);
                Instruction ti = listing.getInstructionAt(toAddr(tgt));
                println(String.format("  [%d] off=%+d -> 0x%08x  %s", i, off, tgt,
                        ti == null ? "NOT an instruction start" : "insn: " + ti.getMnemonicString()));
            }
        }
    }

    private void printRefs(long addr) {
        Address a = toAddr(addr);
        ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(a);
        List<String> rs = new ArrayList<>();
        while (it.hasNext()) {
            Reference r = it.next();
            rs.add(String.format("%s %s", r.getFromAddress(), r.getReferenceType()));
        }
        println("inbound refs to site: " + (rs.isEmpty() ? "NONE (unreachable / data)" : rs));
    }
}
