//@author OpenAI
//@category Import
// Apply registry-owned auto-analysis choices before a deterministic rebuild pass.
import ghidra.app.script.GhidraScript;

import java.util.Map;

public class ApplyAnalysisOptions extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length == 0)
            throw new IllegalArgumentException("expected NAME=VALUE analysis options");
        Map<String, String> known = getCurrentAnalysisOptionsAndValues(currentProgram);
        for (String arg : args) {
            int separator = arg.lastIndexOf('=');
            if (separator <= 0 || separator == arg.length() - 1)
                throw new IllegalArgumentException("invalid analysis option: " + arg);
            String name = arg.substring(0, separator);
            String value = arg.substring(separator + 1);
            if (!known.containsKey(name))
                throw new IllegalArgumentException("unknown analysis option: " + name);
            setAnalysisOption(currentProgram, name, value);
            String actual = getCurrentAnalysisOptionsAndValues(currentProgram).get(name);
            if (!value.equalsIgnoreCase(actual))
                throw new IllegalStateException(
                    "analysis option did not persist: " + name + "=" + actual);
            println("ApplyAnalysisOptions: " + name + "=" + actual);
        }
    }
}
