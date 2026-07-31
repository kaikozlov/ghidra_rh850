// Fixture for compiler-diagnostics regression: a script that compiles cleanly.
// @category Test
import ghidra.app.script.GhidraScript;

public class ValidScript extends GhidraScript {
    @Override
    public void run() throws Exception {
        println("ValidScript compiled and ran");
    }
}
