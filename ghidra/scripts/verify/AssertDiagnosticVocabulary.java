//@author kaikozlov
//@category Verification
// Assert the seven firmware-backed Techstream monitor annotations after the
// vocabulary post-script has run during a clean rebuild.
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Function;
import java.util.ArrayList;
import java.util.List;

public class AssertDiagnosticVocabulary extends GhidraScript {
    private static final long[] CALLBACKS = {
        0x4cbfcL, 0x4cc76L, 0x4ccc4L, 0x4cd38L,
        0x4cd74L, 0x4cdd4L, 0x4ce00L,
    };

    private static final String[] NAMES = {
        "vehicle_speed_did_0102",
        "engine_revolution_speed_did_0103",
        "motor_instruction_current_did_0105",
        "steering_torque_did_0109",
        "output_of_torque_sensor_2_did_010B",
        "ig_switch_status_did_0110",
        "no_of_diagnosis_codes_did_0112",
    };

    private static final String[][] LANDMARKS = {
        {"febee90c", "febee896", "febee815"},
        {"febee910", "febee814", "0xf4240"},
        {"000212f8", "0x204"},
        {"febee867", "febee813"},
        {"00021308", "0x20a"},
        {"febee664"},
        {"febe8ab0", "febe89a4"},
    };

    @Override
    public void run() throws Exception {
        List<String> failures = new ArrayList<>();
        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);

        for (int i = 0; i < CALLBACKS.length; i++) {
            Function function = getFunctionAt(toAddr(CALLBACKS[i]));
            if (function == null) {
                failures.add(String.format("missing callback function at 0x%x", CALLBACKS[i]));
                continue;
            }
            if (!NAMES[i].equals(function.getName())) {
                failures.add(String.format(
                    "callback 0x%x named %s, expected %s",
                    CALLBACKS[i], function.getName(), NAMES[i]
                ));
            }
            if (!"__stdcall".equals(function.getCallingConventionName())) {
                failures.add(String.format(
                    "callback 0x%x convention=%s, expected __stdcall",
                    CALLBACKS[i], function.getCallingConventionName()
                ));
            }
            String comment = currentProgram.getListing().getComment(
                CodeUnit.PRE_COMMENT, function.getEntryPoint()
            );
            if (comment == null || !comment.contains("[RAM source]")) {
                failures.add(String.format(
                    "callback 0x%x lacks RAM-source pre-comment", CALLBACKS[i]
                ));
            }

            DecompileResults results = decompiler.decompileFunction(function, 60, monitor);
            if (results == null || !results.decompileCompleted()) {
                failures.add(String.format("decompile failed for callback 0x%x", CALLBACKS[i]));
                continue;
            }
            String code = results.getDecompiledFunction().getC().toLowerCase();
            for (String landmark : LANDMARKS[i]) {
                if (!code.contains(landmark.toLowerCase())) {
                    failures.add(String.format(
                        "callback 0x%x lacks decompiler landmark %s",
                        CALLBACKS[i], landmark
                    ));
                }
            }
        }

        decompiler.dispose();
        println(String.format(
            "ASSERT diagnostic-vocabulary: callbacks=%d failures=%d",
            CALLBACKS.length, failures.size()
        ));
        if (!failures.isEmpty()) {
            for (String failure : failures) println("FAIL: " + failure);
            throw new IllegalStateException(String.format(
                "%d diagnostic-vocabulary failures: %s",
                failures.size(), String.join("; ", failures)
            ));
        }
    }
}
