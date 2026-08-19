//@author kaikozlov
//@category Import
// Apply exact-image GP/TP context to a disposable foreign RH850 CodeFlash project.
//
// Usage:
//   ApplyVariantGpTpContext.java BOOT_GP BOOT_TP APP_GP APP_TP
//
// Values must be recovered from the target firmware's own startup instructions.
// This script deliberately does not infer or inherit canonical Sienna values.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.lang.RegisterValue;
import ghidra.program.model.listing.ProgramContext;
import java.math.BigInteger;

public class ApplyVariantGpTpContext extends GhidraScript {
    private long parse(String value) {
        return Long.decode(value);
    }

    private Address address(long value) {
        return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(value);
    }

    private void setRange(String registerName, long value, long start, long endExclusive)
            throws Exception {
        Register register = currentProgram.getRegister(registerName);
        if (register == null) {
            throw new IllegalStateException("missing register " + registerName);
        }
        ProgramContext context = currentProgram.getProgramContext();
        context.setValue(
            register,
            address(start),
            address(endExclusive - 1),
            BigInteger.valueOf(value)
        );
    }

    private void verify(String registerName, long expected, long probe) {
        Register register = currentProgram.getRegister(registerName);
        RegisterValue value = currentProgram.getProgramContext().getRegisterValue(register, address(probe));
        if (value == null || !value.hasValue()) {
            throw new IllegalStateException(
                String.format("%s context missing at 0x%X", registerName, probe)
            );
        }
        long actual = value.getUnsignedValue().longValue();
        if (actual != expected) {
            throw new IllegalStateException(
                String.format(
                    "%s context mismatch at 0x%X: expected 0x%X got 0x%X",
                    registerName, probe, expected, actual
                )
            );
        }
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 4) {
            throw new IllegalArgumentException(
                "usage: ApplyVariantGpTpContext.java BOOT_GP BOOT_TP APP_GP APP_TP"
            );
        }
        long bootGp = parse(args[0]);
        long bootTp = parse(args[1]);
        long appGp = parse(args[2]);
        long appTp = parse(args[3]);

        setRange("gp", bootGp, 0x00000000L, 0x00020000L);
        setRange("tp", bootTp, 0x00000000L, 0x00020000L);
        setRange("gp", appGp, 0x00020000L, 0x00100000L);
        setRange("tp", appTp, 0x00020000L, 0x00100000L);

        verify("gp", bootGp, 0x00000100L);
        verify("tp", bootTp, 0x00000100L);
        verify("gp", appGp, 0x00020880L);
        verify("tp", appTp, 0x00020880L);

        println(String.format(
            "Applied target GP/TP: boot gp=0x%08X tp=0x%08X; app gp=0x%08X tp=0x%08X",
            bootGp, bootTp, appGp, appTp
        ));
    }
}
