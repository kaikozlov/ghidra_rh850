//@author kaikozlov
//@category Analysis
// Recover boot/application vector-table handlers and apply __interrupt to
// true ISR wrappers (not their normal callees). Owns semantic ISR names.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryAccessException;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.SourceType;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class RecoverVectorHandlers extends GhidraScript {
    private final Map<Long, String> semanticNames = new HashMap<>();
    private final Map<Long, String> plateComments = new HashMap<>();
    private final Set<Long> interruptWrappers = new HashSet<>();

    private void seedKnownNames() {
        // Boot exception / EIINT wrappers.
        name(0x1e1eL, "boot_default_exception_handler",
            "Shared boot direct-vector handler used by most exception slots.");
        name(0x1e2aL, "boot_secondary_exception_handler",
            "Shared boot handler used by direct-vector offsets 0x20, 0xB0, and 0xD0.");
        name(0x1e36L, "boot_fatal_exception_trap",
            "Reports fatal code 0xFFFF through 0x721E and then loops forever.");
        name(0x1e44L, "boot_tauj0_ch2_isr", "Boot EIINT 135 / source code 0x1087: TAUJ0 channel 2 wrapper.");
        name(0x1e50L, "boot_can0_rx_isr", "Boot EIINT 184 / source code 0x10B8: RSCAN CAN0 receive wrapper.");
        name(0x1e5eL, "boot_can0_tx_isr", "Boot EIINT 185 / source code 0x10B9: RSCAN CAN0 transmit wrapper.");
        name(0x1e6cL, "boot_can1_rx_isr", "Boot EIINT 187 / source code 0x10BB: RSCAN CAN1 receive wrapper.");
        name(0x1e7aL, "boot_can1_tx_isr", "Boot EIINT 188 / source code 0x10BC: RSCAN CAN1 transmit wrapper.");
        name(0x1e88L, "boot_can2_rx_isr", "Boot EIINT 192 / source code 0x10C0: RSCAN CAN2 receive wrapper.");
        name(0x1e96L, "boot_can2_tx_isr", "Boot EIINT 193 / source code 0x10C1: RSCAN CAN2 transmit wrapper.");
        name(0x1ea4L, "boot_unexpected_eiint_trap",
            "Default boot EIINT dispatch target; reports 0xFFFF and loops forever.");

        // Application ISR wrappers (INTBP / EBASE targets).
        name(0x61d88L, "application_default_exception_handler",
            "Default target for direct application exceptions and 373 of the 384 INTBP entries.");
        name(0x64b3eL, "application_vector_0x90_handler",
            "Specialized handler reached from application direct-vector offset 0x90; records fault context before recovery/reset handling.");
        name(0x70a54L, "application_ecm_maskable_isr",
            "Application EIINT channel 8: maskable Error Control Module interrupt.");
        name(0x70320L, "application_tauj0_ch0_isr",
            "Application EIINT channel 133: TAUJ0 channel 0 interrupt wrapper.");
        name(0x703caL, "application_tauj0_ch1_isr",
            "Application EIINT channel 134: TAUJ0 channel 1 interrupt wrapper.");
        name(0x70476L, "application_tauj0_ch2_isr",
            "Application EIINT channel 135: TAUJ0 channel 2 interrupt wrapper.");
        name(0x6506aL, "application_can1_rx_isr",
            "Application EIINT channel 187: RSCAN CAN1 receive interrupt wrapper.");
        name(0x65028L, "application_can1_tx_isr",
            "Application EIINT channel 188: RSCAN CAN1 transmit interrupt wrapper.");
        name(0x650acL, "application_icus_ch292_isr",
            "EIINT channel 292 wrapper for the ICU-S crypto-driver callback path. The generic P1M-E table marks this channel number reserved, but this vector is active in firmware.");
        name(0x650eeL, "application_icus_ch293_isr",
            "EIINT channel 293 wrapper for the second ICU-S crypto-driver callback path. The generic P1M-E table marks this channel number reserved, but this vector is active in firmware.");
        name(0x65130L, "application_flash_end_isr",
            "Application EIINT channel 379: flash sequencer-end interrupt wrapper.");

        interruptWrappers.addAll(semanticNames.keySet());
    }

    private void name(long addr, String name, String comment) {
        semanticNames.put(addr, name);
        plateComments.put(addr, comment);
    }

    private boolean isCodeFlashFunction(long addr) {
        return addr >= 0L && addr < 0x100000L && (addr & 1L) == 0L;
    }

    private Function ensureFunction(long addr) throws Exception {
        if (!isCodeFlashFunction(addr)) {
            println(String.format("skip non-CodeFlash vector target 0x%x", addr));
            return null;
        }
        Address a = toAddr(addr);
        Listing listing = currentProgram.getListing();

        // Drop conflicting data (false pointer creation into mapped SFR windows)
        // and split any function that contains but does not start at this entry.
        Function containingFn = getFunctionContaining(a);
        if (containingFn != null && !containingFn.getEntryPoint().equals(a)) {
            listing.clearCodeUnits(containingFn.getEntryPoint(),
                containingFn.getBody().getMaxAddress(), false);
            currentProgram.getFunctionManager().removeFunction(containingFn.getEntryPoint());
        }
        if (listing.getDataContaining(a) != null || listing.getInstructionContaining(a) != null) {
            // Clear a small window so disassembly can claim the entry.
            listing.clearCodeUnits(a, a.add(7), false);
        }

        Instruction containing = listing.getInstructionContaining(a);
        if (containing != null && !containing.getMinAddress().equals(a)) {
            listing.clearCodeUnits(containing.getMinAddress(), containing.getMaxAddress(), false);
        }
        if (listing.getInstructionAt(a) == null) {
            disassemble(a);
        }
        if (listing.getInstructionAt(a) == null) {
            println(String.format("WARN: could not disassemble vector target 0x%x", addr));
            return null;
        }
        Function f = getFunctionAt(a);
        if (f == null) {
            f = createFunction(a, null);
        }
        if (f == null) {
            println(String.format("WARN: could not create function at vector target 0x%x", addr));
        }
        return f;
    }

    private void applyInterrupt(Function f) throws Exception {
        if (f == null) return;
        try {
            f.setCallingConvention("__interrupt");
            println("set __interrupt on " + f.getName() + " @ " + f.getEntryPoint());
        } catch (Exception ex) {
            println("WARN: could not set __interrupt on " + f.getName() + ": " + ex.getMessage());
        }
    }

    private void maybeRename(Function f, long addr) throws Exception {
        if (f == null) return;
        String name = semanticNames.get(addr);
        if (name != null && !name.equals(f.getName())) {
            f.setName(name, SourceType.USER_DEFINED);
        }
        String comment = plateComments.get(addr);
        if (comment != null) {
            currentProgram.getListing().setComment(f.getEntryPoint(),
                CodeUnit.PLATE_COMMENT, comment);
        }
    }

    private void addVectorReference(long from, long to, RefType type) {
        Address fromAddr = toAddr(from);
        Address toAddr = toAddr(to);
        Reference[] refs = currentProgram.getReferenceManager().getReferencesFrom(fromAddr);
        for (Reference ref : refs) {
            if (ref.getToAddress().equals(toAddr)) return;
        }
        currentProgram.getReferenceManager().addMemoryReference(
                fromAddr, toAddr, type, SourceType.ANALYSIS, 0);
    }

    private int recoverBootDispatchTable() throws Exception {
        // Eight-byte records at 0x869C: EIIC code (u32) + handler (u32).
        int created = 0;
        for (int i = 0; i < 8; i++) {
            long record = 0x869cL + i * 8L;
            long handler = Integer.toUnsignedLong(getInt(toAddr(record + 4)));
            if (handler == 0xFFFFFFFFL) {
                println("boot dispatch terminator at index " + i);
                break;
            }
            addVectorReference(record + 4, handler, RefType.DATA);
            Function f = ensureFunction(handler);
            maybeRename(f, handler);
            if (interruptWrappers.contains(handler)) applyInterrupt(f);
            created++;
        }
        return created;
    }

    private int recoverPointerTable(long base, int count, String label) throws Exception {
        int created = 0;
        Set<Long> seen = new HashSet<>();
        for (int i = 0; i < count; i++) {
            long ptrAddr = base + i * 4L;
            long handler;
            try {
                handler = Integer.toUnsignedLong(getInt(toAddr(ptrAddr)));
            } catch (MemoryAccessException ex) {
                break;
            }
            if (handler == 0 || handler == 0xFFFFFFFFL) continue;
            if (!isCodeFlashFunction(handler)) {
                // INTBP reserved slots may hold non-flash sentinels; leave them alone.
                continue;
            }
            addVectorReference(ptrAddr, handler, RefType.DATA);
            if (!seen.add(handler)) continue;
            Function f = ensureFunction(handler);
            maybeRename(f, handler);
            if (interruptWrappers.contains(handler)) applyInterrupt(f);
            created++;
        }
        println(label + ": unique CodeFlash handlers ensured=" + created);
        return created;
    }

    private int recoverDirectVectorStubs(long base, int count, String label)
            throws Exception {
        // Direct vectors are 16-byte stubs beginning with JMP disp32[r0].
        // The common encoding is 1f 00 e0 06 <target:u32>; boot vector 0xd0
        // uses the verified alternate 1f 00 80 07 form. Other encodings (for
        // example application 0x20100+) are executable stubs, not pointers.
        Set<Long> seen = new HashSet<>();
        int created = 0;
        for (int i = 0; i < count; i++) {
            long slot = base + i * 0x10L;
            long prefix = Integer.toUnsignedLong(getInt(toAddr(slot)));
            if (prefix != 0x06e0001fL && prefix != 0x0780001fL) continue;
            long handler = Integer.toUnsignedLong(getInt(toAddr(slot + 4)));
            if (!isCodeFlashFunction(handler) || handler == 0) continue;
            addVectorReference(slot, handler, RefType.UNCONDITIONAL_JUMP);
            if (!seen.add(handler)) continue;
            Function f = ensureFunction(handler);
            maybeRename(f, handler);
            applyInterrupt(f);
            created++;
        }
        println(label + ": parsed unique CodeFlash handlers=" + created);
        return created;
    }

    @Override
    public void run() throws Exception {
        seedKnownNames();

        int directBoot = recoverDirectVectorStubs(0x10L, 15, "boot-direct");
        int boot = recoverBootDispatchTable();
        int ebase = recoverDirectVectorStubs(0x20000L, 32, "EBASE");
        // Application INTBP: 384 entries at 0x20200 (true pointer table).
        int intbp = recoverPointerTable(0x20200L, 384, "INTBP");

        // Explicitly ensure known ISR wrappers exist and use __interrupt even if
        // a table slot was unusual.
        for (long addr : interruptWrappers) {
            Function f = ensureFunction(addr);
            maybeRename(f, addr);
            applyInterrupt(f);
        }

        // Explicitly do NOT mark normal ICU dispatch callees as interrupt.
        for (long addr : new long[]{0x87610L, 0x87636L}) {
            Function f = getFunctionAt(toAddr(addr));
            if (f != null && "__interrupt".equals(f.getCallingConventionName())) {
                f.setCallingConvention("default");
                println("cleared mistaken __interrupt on normal callee " + f.getName());
            }
        }

        println(String.format(
            "RecoverVectorHandlers: boot_direct=%d boot_dispatch=%d ebase=%d intbp_unique=%d",
            directBoot, boot, ebase, intbp));
    }
}
