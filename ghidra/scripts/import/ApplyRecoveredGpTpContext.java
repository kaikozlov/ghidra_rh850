//@author kaikozlov
//@category Import
// Recover and apply boot/application GP+TP context from the target's own startup code.
//
// The resolver intentionally does NOT choose the most common write to register tp:
// RH850 code uses r5/tp as a general register in many peripheral routines.  The
// target context is recovered only from the startup idiom
//
//     mov immediate,gp
//     mov immediate,tp
//
// where the writes are adjacent/near-adjacent and repeat consistently inside the
// boot (<0x20000) or application (>=0x20000) CodeFlash region.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.ProgramContext;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public class ApplyRecoveredGpTpContext extends GhidraScript {
    private static final long APP_SPLIT = 0x00020000L;
    private static final long CODEFLASH_END = 0x00100000L;
    private static final long MAX_PAIR_DISTANCE = 0x10L;

    private static final class Pair {
        final long gp;
        final long tp;

        Pair(long gp, long tp) {
            this.gp = gp;
            this.tp = tp;
        }

        @Override
        public boolean equals(Object other) {
            if (!(other instanceof Pair)) return false;
            Pair rhs = (Pair) other;
            return gp == rhs.gp && tp == rhs.tp;
        }

        @Override
        public int hashCode() {
            return Long.hashCode(gp) * 31 + Long.hashCode(tp);
        }

        @Override
        public String toString() {
            return String.format(Locale.ROOT, "gp=0x%08X,tp=0x%08X", gp, tp);
        }
    }

    private static final class Observation {
        final Pair pair;
        final Address gpWrite;
        final Address tpWrite;

        Observation(Pair pair, Address gpWrite, Address tpWrite) {
            this.pair = pair;
            this.gpWrite = gpWrite;
            this.tpWrite = tpWrite;
        }
    }

    private boolean writesRegister(Instruction instruction, String registerName) {
        for (Object result : instruction.getResultObjects()) {
            if (result instanceof Register) {
                Register register = (Register) result;
                if (register.getName().equalsIgnoreCase(registerName)) return true;
            }
        }
        return false;
    }

    private Long immediate(Instruction instruction) {
        Long value = null;
        for (Object input : instruction.getInputObjects()) {
            if (!(input instanceof Scalar)) continue;
            Scalar scalar = (Scalar) input;
            long candidate = scalar.getUnsignedValue();
            if (value != null && value.longValue() != candidate) return null;
            value = candidate;
        }
        return value;
    }

    private List<Observation> observations(boolean application) throws Exception {
        List<Observation> out = new ArrayList<>();
        InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
        while (instructions.hasNext()) {
            monitor.checkCancelled();
            Instruction gpInstruction = instructions.next();
            long gpAddress = gpInstruction.getAddress().getOffset();
            boolean inApplication = gpAddress >= APP_SPLIT && gpAddress < CODEFLASH_END;
            if (inApplication != application) continue;
            if (!writesRegister(gpInstruction, "gp")) continue;
            Long gp = immediate(gpInstruction);
            if (gp == null) continue;
            // Context GP is a LocalRAM pointer on these P1M-E images.  This also
            // rejects ordinary arithmetic writes that happen to target r4/gp.
            if ((gp & 0xFFF00000L) != 0xFEB00000L) continue;

            Instruction candidate = currentProgram.getListing().getInstructionAfter(gpInstruction.getAddress());
            while (candidate != null) {
                long distance = candidate.getAddress().subtract(gpInstruction.getAddress());
                if (distance <= 0 || distance > MAX_PAIR_DISTANCE) break;
                if (writesRegister(candidate, "tp")) {
                    Long tp = immediate(candidate);
                    if (tp != null && tp >= 0 && tp < CODEFLASH_END) {
                        out.add(new Observation(new Pair(gp, tp), gpInstruction.getAddress(), candidate.getAddress()));
                    }
                    break;
                }
                // Do not jump across control flow when searching for the paired TP load.
                if (candidate.getFlowType() != null && candidate.getFlowType().isJump()) break;
                candidate = currentProgram.getListing().getInstructionAfter(candidate.getAddress());
            }
        }
        return out;
    }

    private Pair choose(String label, List<Observation> observations) {
        if (observations.isEmpty()) {
            throw new IllegalStateException("no " + label + " adjacent GP/TP startup pairs found");
        }
        Map<Pair, Integer> counts = new HashMap<>();
        for (Observation observation : observations) {
            counts.merge(observation.pair, 1, Integer::sum);
        }
        List<Map.Entry<Pair, Integer>> ranked = new ArrayList<>(counts.entrySet());
        ranked.sort(
            Comparator.<Map.Entry<Pair, Integer>>comparingInt(Map.Entry::getValue)
                .reversed()
                .thenComparingLong(entry -> entry.getKey().gp)
                .thenComparingLong(entry -> entry.getKey().tp)
        );
        Map.Entry<Pair, Integer> winner = ranked.get(0);
        if (ranked.size() > 1 && ranked.get(1).getValue().equals(winner.getValue())) {
            throw new IllegalStateException(
                label + " GP/TP pair is ambiguous at count " + winner.getValue() + ": " + ranked
            );
        }
        Pair pair = winner.getKey();
        println(String.format(
            Locale.ROOT,
            "RECOVERED %s %s count=%d candidates=%d",
            label, pair, winner.getValue(), counts.size()
        ));
        for (Observation observation : observations) {
            if (observation.pair.equals(pair)) {
                println(String.format(
                    Locale.ROOT,
                    "PAIR %s gp_write=%s tp_write=%s",
                    label, observation.gpWrite, observation.tpWrite
                ));
            }
        }
        return pair;
    }

    private Address address(long value) {
        return currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(value);
    }

    private void setRange(String registerName, long value, long start, long endExclusive)
            throws Exception {
        Register register = currentProgram.getRegister(registerName);
        if (register == null) throw new IllegalStateException("missing register " + registerName);
        ProgramContext context = currentProgram.getProgramContext();
        context.setValue(
            register,
            address(start),
            address(endExclusive - 1),
            BigInteger.valueOf(value)
        );
    }

    @Override
    public void run() throws Exception {
        Pair boot = choose("boot", observations(false));
        Pair app = choose("application", observations(true));

        setRange("gp", boot.gp, 0x00000000L, APP_SPLIT);
        setRange("tp", boot.tp, 0x00000000L, APP_SPLIT);
        setRange("gp", app.gp, APP_SPLIT, CODEFLASH_END);
        setRange("tp", app.tp, APP_SPLIT, CODEFLASH_END);

        println(String.format(
            Locale.ROOT,
            "APPLIED boot{%s} application{%s}", boot, app
        ));
    }
}
