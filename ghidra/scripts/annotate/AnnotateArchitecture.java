//@author kaikozlov
//@category Analysis
// Name and document verified boot/application architecture and CAN-routing
// landmarks. Vector/ISR wrapper names and __interrupt come from
// RecoverVectorHandlers (must run before this script).
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

        renameFunction(0x119eL, "boot_validity_check",
            "Boot validity gate called by boot_application_handoff. Runs up to 3 retry attempts for memory_crc_verify_descriptors of both CodeFlash regions, then up to 3 retry attempts for the marker equality check at 0x6C5A against markers 0x17E00 and 0xFFE00. Returns 0 on success, 1 on failure (never enters the application).");

        renameFunction(0x115aL, "boot_flash_status_check",
            "Boot flash sequencer status check. Writes the flash sequencer command window (0xFFD62034 area) with a clear/read-back sequence, checks error bits 0 and 2 of the status register, and returns 1 on error. Called inside the validity retry loop.");

        renameFunction(0x6c5aL, "boot_validity_marker_check",
            "Returns true if the 32-bit value at the parameter address is NOT equal to the validity marker 0x5AA5A55A. Called with 0xFFE00 and 0x17E00 (CodeFlash region markers). A true return means the marker is invalid/erased.");

        renameFunction(0xc9aL, "boot_peripheral_init",
            "Early boot peripheral initialization: initializes RSCFD CAN controller register windows (0xFFC20000/0xFFC24000/0xFFC34000 areas) and CAN channel descriptors from the table at 0x87A0.");

        renameFunction(0xe54L, "boot_key_mirror_init",
            "Boot key mirror initialization. Reads three DataFlash triple-copy values at 0xFFC0A000-A008, checks their XOR55/XORAA complements, and if valid copies the primary values into GP-relative mirrors at FEBFFC00-C14, then computes the XOR55 and XORAA complement copies.");

        renameFunction(0xf80L, "boot_flash_sequencer_init",
            "Boot flash sequencer initialization. Configures the flash sequencer protection registers (0xFFD62000-28 area) with the enable key 0xA5 and configures blank/erase state for DataFlash banks at 0xFFD60000 and 0xFFD61000.");

        renameFunction(0x10c6L, "boot_clock_init",
            "Boot clock generation initialization. Writes the clock control register at 0xFFF890C0 with value 4, polls the status register at 0xFFF890C8 for completion, then sets the main oscillator control at 0xFFF88818 to 0x50 (50 MHz main PLL configuration).");

        renameFunction(0x1206L, "boot_failure_trap",
            "Boot failure trap called when validity checks fail. Zeros the diagnostic state at 0xFFFEE980-988 and returns; the caller then falls through to the boot failure main loop.");

        renameFunction(0x1398L, "boot_failure_main_loop",
            "Non-returning boot failure main loop entered when validity checks fail. Calls boot_failure_init (0x1338), disables interrupt-driven services, enables IRQs, then loops forever calling boot_failure_periodic (0x137A) which runs flash_operation_task, bootloader operation release, and memory_crc_verify_task.");

        renameFunction(0x137aL, "boot_failure_periodic",
            "Boot failure main-loop body. Sets state 0xFEBF2904=2, calls bootloader periodic, flash_operation_task, bootloader_main_operation_release, and memory_crc_verify_task.");

        labelData(0x8e00L, "boot_validity_region_table",
            "Three 28-byte region descriptors for boot CRC validity: region 0 = CodeFlash 0x10000-0x17DFF (marker 0x17E00), region 1 = CodeFlash 0x18000-0xFFDFF (marker 0xFFE00), region 2 = RAM payload window 0xFEBF0000-0xFEBF0FFF (null marker). Each descriptor has base/end/emb-addr/emb-len/marker-addr fields plus CRC descriptor pointers at 0x8DD0/0x8DE0.");
        labelData(0x17e00L, "codeflash_region0_validity_marker",
            "Boot validity marker for CodeFlash region 0. Value 0x5AA5A55A indicates a valid/programmed region.");
        labelData(0xffe00L, "codeflash_region1_validity_marker",
            "Boot validity marker for CodeFlash region 1 (application region). Value 0x5AA5A55A indicates a valid/programmed region.");

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

        renameFunction(0x87610L, "icus_interrupt_channel292_dispatch", "Invoke the installed ICU-S driver callback only when its pointer/complement guard at GP+5994/+5998 is valid; otherwise set driver error GP+5991.");
        renameFunction(0x87636L, "icus_interrupt_channel293_dispatch", "Byte-identical second ICU-S interrupt callback dispatcher. Static analysis does not distinguish completion versus error between channels 292/293.");
        renameFunction(0x8913cL, "icus_interrupt_pair_set_enabled", "Mask or unmask EIC292/EIC293 at FFFFB248/FFFFB24A together, then issue the synchronization readback.");
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
        eol(0x13b4L, "jarl boot setup call 1: boot_peripheral_init (0xC9A)");
        eol(0x13b8L, "jarl boot setup call 2: boot_key_mirror_init (0xE54)");
        eol(0x13bcL, "jarl boot setup call 3: boot_flash_sequencer_init (0xF80)");
        eol(0x13c0L, "jarl boot setup call 4: boot_clock_init (0x10C6)");
        eol(0x13c4L, "jarl boot validity check: boot_validity_check (0x119E)");
        eol(0x6c60L, "Validity marker 0x5AA5A55A literal inside boot_validity_marker_check");
    }
}
