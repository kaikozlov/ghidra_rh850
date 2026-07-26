//@author kaikozlov
//@category Analysis
// Name and document verified boot/application architecture, interrupt, and CAN-routing landmarks.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class AnnotateArchitecture extends GhidraScript {
    private void renameFunction(long addr, String name, String comment) throws Exception {
        Address a = toAddr(addr);
        Function f = currentProgram.getFunctionManager().getFunctionAt(a);
        if (f == null) throw new IllegalStateException("no function at " + a + " for " + name);
        f.setName(name, SourceType.USER_DEFINED);
        currentProgram.getListing().setComment(a, CodeUnit.PLATE_COMMENT, comment);
        println(String.format("function 0x%x -> %s", addr, name));
    }

    private void labelData(long addr, String name, String comment) throws Exception {
        Address a = toAddr(addr);
        SymbolTable symbols = currentProgram.getSymbolTable();
        Symbol symbol = symbols.getPrimarySymbol(a);
        if (symbol != null) symbol.setName(name, SourceType.USER_DEFINED);
        else {
            symbol = symbols.createLabel(a, name, SourceType.USER_DEFINED);
            symbol.setPrimary();
        }
        currentProgram.getListing().setComment(a, CodeUnit.PLATE_COMMENT, comment);
        println(String.format("data 0x%x -> %s", addr, name));
    }

    private void eol(long addr, String comment) {
        currentProgram.getListing().setComment(toAddr(addr), CodeUnit.EOL_COMMENT, comment);
    }

    @Override
    public void run() throws Exception {
        renameFunction(0x1b0L, "boot_reset_startup",
            "Reset target from vector 0x0. Disables interrupts, clears registers, and establishes boot SP/GP/TP before boot initialization.");
        renameFunction(0x748L, "boot_eiint_dispatch",
            "Boot EIINT dispatcher. Searches the (EIIC code, handler) pairs at 0x869C and invokes the match or final default entry.");
        renameFunction(0x13b0L, "boot_application_handoff",
            "Runs final boot checks. On success, loads the entry pointer at 0xFFDB8 and calls application entry 0x20880; otherwise stays in the boot failure path.");
        renameFunction(0x1e1eL, "boot_default_exception_handler",
            "Shared boot direct-vector handler used by most exception slots.");
        renameFunction(0x1e2aL, "boot_secondary_exception_handler",
            "Shared boot handler used by direct-vector offsets 0x20, 0xB0, and 0xD0.");
        renameFunction(0x1e36L, "boot_fatal_exception_trap",
            "Reports fatal code 0xFFFF through 0x721E and then loops forever.");
        renameFunction(0x1e44L, "boot_tauj0_ch2_isr", "Boot EIINT 135 / source code 0x1087: TAUJ0 channel 2 wrapper.");
        renameFunction(0x1e50L, "boot_can0_rx_isr", "Boot EIINT 184 / source code 0x10B8: RSCAN CAN0 receive wrapper.");
        renameFunction(0x1e5eL, "boot_can0_tx_isr", "Boot EIINT 185 / source code 0x10B9: RSCAN CAN0 transmit wrapper.");
        renameFunction(0x1e6cL, "boot_can1_rx_isr", "Boot EIINT 187 / source code 0x10BB: RSCAN CAN1 receive wrapper.");
        renameFunction(0x1e7aL, "boot_can1_tx_isr", "Boot EIINT 188 / source code 0x10BC: RSCAN CAN1 transmit wrapper.");
        renameFunction(0x1e88L, "boot_can2_rx_isr", "Boot EIINT 192 / source code 0x10C0: RSCAN CAN2 receive wrapper.");
        renameFunction(0x1e96L, "boot_can2_tx_isr", "Boot EIINT 193 / source code 0x10C1: RSCAN CAN2 transmit wrapper.");
        renameFunction(0x1ea4L, "boot_unexpected_eiint_trap", "Default boot EIINT dispatch target; reports 0xFFFF and loops forever.");

        labelData(0x869cL, "boot_interrupt_dispatch_table",
            "Eight-byte records: EIIC source code then handler pointer. Seven explicit entries (TAUJ0 CH2 and CAN0/1/2 RX/TX), followed by 0xFFFFFFFF/default trap.");
        labelData(0xffdb8L, "application_entry_pointer",
            "Boot-to-application entry pointer. The stored little-endian value is 0x00020880.");
        labelData(0x20000L, "application_exception_vector_base",
            "Application EBASE value installed by application_cpu_context_init. Direct exception vectors occupy 0x20000..0x201FF.");
        labelData(0x20200L, "application_interrupt_pointer_table",
            "Application INTBP table: 384 little-endian handler pointers for EIINT channels 0..383.");

        renameFunction(0x20880L, "application_entry", "Entry selected by the pointer at 0xFFDB8; calls the application startup coordinator.");
        renameFunction(0x62758L, "application_startup_coordinator",
            "Initializes CPU context and application modules, enables EI interrupts, then enters the non-returning foreground cyclic loop.");
        renameFunction(0x70524L, "application_cpu_context_init",
            "Installs INTBP=0x20200, EBASE=0x20000, GP=0xFEBEB800, TP=0x23EE4, and SP=0xFEBE2000.");
        renameFunction(0x64fccL, "application_foreground_cyclic_loop",
            "Polled foreground scheduler. Waits for TAUJ0 CH3 EIRF at EIC136 (0xFFFFB110 bit 12), clears it, then runs NvM/CSM, application, and SecOC-NvM cyclic groups.");
        renameFunction(0x61d88L, "application_default_exception_handler",
            "Default target for direct application exceptions and 373 of the 384 INTBP entries.");
        renameFunction(0x64b3eL, "application_vector_0x90_handler",
            "Specialized handler reached from application direct-vector offset 0x90; records fault context before recovery/reset handling.");

        renameFunction(0x70a54L, "application_ecm_maskable_isr", "Application EIINT channel 8: maskable Error Control Module interrupt.");
        renameFunction(0x70320L, "application_tauj0_ch0_isr", "Application EIINT channel 133: TAUJ0 channel 0 interrupt wrapper.");
        renameFunction(0x703caL, "application_tauj0_ch1_isr", "Application EIINT channel 134: TAUJ0 channel 1 interrupt wrapper.");
        renameFunction(0x70476L, "application_tauj0_ch2_isr", "Application EIINT channel 135: TAUJ0 channel 2 interrupt wrapper.");
        renameFunction(0x6506aL, "application_can1_rx_isr", "Application EIINT channel 187: RSCAN CAN1 receive interrupt wrapper.");
        renameFunction(0x65028L, "application_can1_tx_isr", "Application EIINT channel 188: RSCAN CAN1 transmit interrupt wrapper.");
        renameFunction(0x650acL, "application_icus_ch292_isr", "EIINT channel 292 wrapper for the ICU-S crypto-driver callback path. The generic P1M-E table marks this channel number reserved, but this vector is active in firmware.");
        renameFunction(0x650eeL, "application_icus_ch293_isr", "EIINT channel 293 wrapper for the second ICU-S crypto-driver callback path. The generic P1M-E table marks this channel number reserved, but this vector is active in firmware.");
        renameFunction(0x87610L, "icus_interrupt_channel292_dispatch", "Invoke the installed ICU-S driver callback only when its pointer/complement guard at GP+5994/+5998 is valid; otherwise set driver error GP+5991.");
        renameFunction(0x87636L, "icus_interrupt_channel293_dispatch", "Byte-identical second ICU-S interrupt callback dispatcher. Static analysis does not distinguish completion versus error between channels 292/293.");
        renameFunction(0x8913cL, "icus_interrupt_pair_set_enabled", "Mask or unmask EIC292/EIC293 at FFFFB248/FFFFB24A together, then issue the synchronization readback.");
        renameFunction(0x65130L, "application_flash_end_isr", "Application EIINT channel 379: flash sequencer-end interrupt wrapper.");
        renameFunction(0x64f18L, "application_tauj0_ch0_body", "TAUJ0 channel 0 periodic interrupt body and event counter update.");
        renameFunction(0x64f54L, "application_tauj0_ch1_body", "TAUJ0 channel 1 periodic interrupt body and event counter update.");
        renameFunction(0x64f90L, "application_tauj0_ch2_body", "TAUJ0 channel 2 periodic interrupt body and event counter update.");

        labelData(0x22fe0L, "application_rscfd_channel_register_map",
            "Three 0x74-byte records of RSCFD SFR addresses for CAN channels 0..2. The active application interrupt wrappers select channel 1.");
        labelData(0x231a0L, "application_can1_acceptance_rules",
            "51 RSCFD acceptance-rule records (16 bytes each) plus a 0xFFFFFFFF terminator. Rules 0..46 are normal application RX; 47..50 are 0x7A1, 0x777, 0x7A0, and 0x7F7.");
        labelData(0x22018L, "application_normal_rx_can_ids",
            "47 (standard CAN ID, expected length/flags) records mirrored by acceptance rules 0..46. Includes 0x2E4, 0x0F, and 0x131.");
        labelData(0x21fc8L, "application_diagnostic_rx_can_ids",
            "Three standard diagnostic receive IDs routed together: 0x7A1, 0x777, and 0x7A0. ID 0x7F7 uses the separate receive callback class.");
        labelData(0x219acL, "application_can_rx_queue_map",
            "51-byte hardware-rule-to-software-queue map used by the receive ISR path.");
        labelData(0x21fe0L, "application_rx_route_flags",
            "Per-PDU receive routing flags consumed by app_can_normal_rx_demux.");

        renameFunction(0x82e40L, "application_can1_rx_interrupt_body", "RSCFD receive interrupt body specialized for CAN channel 1.");
        renameFunction(0x8474eL, "application_can1_tx_interrupt_body", "RSCFD transmit-confirmation interrupt body specialized for CAN channel 1.");
        renameFunction(0x7fa56L, "application_can_rx_queue_ingress",
            "Maps the RSCFD hardware receive label to a software route, validates the frame, and queues it for foreground dispatch.");
        renameFunction(0x80006L, "application_can_normal_rx_demux",
            "Matches one of 47 normal receive CAN IDs and converts acceptance-rule index n to application PDU ID 6+n before PDU routing.");
        renameFunction(0x80114L, "application_can_diagnostic_rx_demux",
            "Matches diagnostic IDs 0x7A1/0x777/0x7A0 and forwards the selected transport PDU route.");
        renameFunction(0x7ff86L, "application_can_special_rx_demux",
            "Separate receive callback class used by acceptance rule 50 / standard CAN ID 0x7F7.");
        renameFunction(0x80c44L, "application_pdu_rx_router",
            "Configuration-driven upper PDU receive router reached after normal CAN receive demultiplexing.");

        eol(0x13f2L, "Load application entry pointer from CodeFlash 0xFFDB8.");
        eol(0x13feL, "Indirect boot-to-application call; resolved target is 0x20880.");
        eol(0x7052cL, "INTBP = 0x20200 (384-entry EIINT pointer table).");
        eol(0x70538L, "EBASE = 0x20000 (application direct exception vectors).");
        eol(0x64fd0L, "Poll EIC136.EIRF: TAUJ0 channel 3 is the foreground-loop tick source.");
        eol(0x64fd6L, "Clear EIC136.EIRF after accepting the polled foreground tick.");
    }
}
