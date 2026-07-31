// Fixture for compiler-diagnostics regression: a script with a deliberate
// compile error (undefined symbol). Used to verify that `script check` and
// `script run` surface real javac diagnostics, not a generic "class not found".
// @category Test
import ghidra.app.script.GhidraScript;

public class CompileError extends GhidraScript {
    @Override
    public void run() throws Exception {
        // Deliberate: UndefinedType is not a real type. This must fail to
        // compile and the error output must contain the javac diagnostic.
        UndefinedType x = new UndefinedType();
        println(x.toString());
    }
}
