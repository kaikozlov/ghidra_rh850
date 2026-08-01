//@author kaikozlov
//@category Analysis
// Apply Techstream OEM diagnostic vocabulary to the annotated Ghidra project.
//
// Consumes data/generated/<sha>/diagnostic_vocabulary.json — the output of
// tools/diagnostics/correlate_vocabulary.py — and applies OEM names and
// comments to DID callbacks, service callbacks, and RAM/data locations.
//
// Match-grade policy:
//   exact / structural → rename functions, label data, apply full comments
//   family             → comment-only (never renames symbols)
//   candidate          → comment-only with conflict warning
//   rejected           → skip
//
// This script does NOT overwrite symbols created by AnnotateApplicationDiagnostics.
// It adds OEM vocabulary as a separate layer. If a function already has a
// USER_DEFINED name, the OEM name is appended as a comment, not a rename.
//
// Run after AnnotateApplicationDiagnostics in the Stage 4 post-analysis pass.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class ApplyDiagnosticVocabulary extends GhidraScript {

    private String loadVocabularyPath() throws Exception {
        // The vocabulary JSON lives at a deterministic path relative to the
        // project.  In the headless rebuild we pass it via a script argument;
        // in interactive mode we default to the repo-relative location.
        String[] args = getScriptArgs();
        if (args != null && args.length > 0) {
            return args[0];
        }
        // Default: resolve relative to the program's project directory
        Path p = Path.of("data/generated/21140bbd65e530a9/diagnostic_vocabulary.json");
        if (!Files.exists(p)) {
            // Try relative to home
            p = Path.of(System.getProperty("user.home"),
                "dev/inspect/repos/ghidra_rh850_analysis",
                "data/generated/21140bbd65e530a9/diagnostic_vocabulary.json");
        }
        if (!Files.exists(p)) {
            throw new Exception("diagnostic_vocabulary.json not found");
        }
        return p.toString();
    }

    private void addComment(long addr, String text) throws Exception {
        Address a = toAddr(addr);
        String existing = currentProgram.getListing().getComment(CodeUnit.PRE_COMMENT, a);
        if (existing == null) existing = "";
        if (existing.contains("Techstream")) return; // don't duplicate
        String prefix = existing.isEmpty() ? "" : existing + "\n";
        currentProgram.getListing().setComment(a, CodeUnit.PRE_COMMENT, prefix + text);
    }

    private void appendPlateComment(long addr, String text) throws Exception {
        Address a = toAddr(addr);
        String existing = currentProgram.getListing().getComment(CodeUnit.PLATE_COMMENT, a);
        if (existing == null) existing = "";
        if (existing.contains(text)) return;
        String prefix = existing.isEmpty() ? "" : existing + "\n";
        currentProgram.getListing().setComment(a, CodeUnit.PLATE_COMMENT, prefix + text);
    }

    private void nameFunctionIfUnnamed(long addr, String oemName, String suffix) throws Exception {
        Address a = toAddr(addr);
        Function f = currentProgram.getFunctionManager().getFunctionAt(a);
        if (f == null) return;
        String current = f.getName();
        // Don't overwrite an existing meaningful name (from AnnotateApplicationDiagnostics)
        if (!current.startsWith("FUN_") && !current.startsWith("LAB_")) {
            addComment(addr, "[Techstream OEM] " + oemName + " (" + suffix + ")");
            return;
        }
        String symbol = oemName.toLowerCase().replaceAll("[^a-z0-9]+", "_") + "_" + suffix;
        f.setName(symbol, SourceType.USER_DEFINED);
        println(a + " → " + symbol + " (Techstream OEM)");
    }

    private void nameDataIfUnnamed(long addr, String oemName, String suffix) throws Exception {
        Address a = toAddr(addr);
        SymbolTable st = currentProgram.getSymbolTable();
        Symbol s = st.getPrimarySymbol(a);
        if (s != null && !s.getName().startsWith("DAT_")) {
            addComment(addr, "[Techstream OEM] " + oemName + " (" + suffix + ")");
            return;
        }
        String symbol = oemName.toLowerCase().replaceAll("[^a-z0-9]+", "_") + "_" + suffix;
        if (s != null) {
            if (!s.getName().equals(symbol))
                s.setName(symbol, SourceType.USER_DEFINED);
        } else {
            s = st.createLabel(a, symbol, SourceType.USER_DEFINED);
        }
        println(a + " → " + symbol + " (Techstream OEM data)");
    }

    @Override
    public void run() throws Exception {
        String vocabPath = loadVocabularyPath();
        String json = Files.readString(Path.of(vocabPath));
        println("Loading diagnostic vocabulary from: " + vocabPath);

        int applied = 0, commented = 0, skipped = 0;

        // ── Apply DID callback names (exact matches only) ────────────────────
        // Parse the JSON manually — we only need a few fields per entry.
        // Using simple string scanning avoids a JSON library dependency.

        // Find all DID mappings with exact grade and a callback address
        int idx = 0;
        while (true) {
            int kindPos = json.indexOf("\"kind\"", idx);
            if (kindPos < 0) break;
            idx = kindPos + 1;

            // Extract the kind value
            int kindStart = json.indexOf('"', kindPos + 6) + 1;
            int kindEnd = json.indexOf('"', kindStart);
            String kind = json.substring(kindStart, kindEnd);

            // Find the enclosing object to get all fields
            int objStart = json.lastIndexOf('{', kindPos);
            int objEnd = findMatchingBrace(json, objStart);
            if (objEnd < 0) break;
            String obj = json.substring(objStart, objEnd + 1);

            String grade = extractStringField(obj, "match_grade");
            String action = extractStringField(obj, "annotation_action");
            String oemName = extractStringField(obj, "oem_name");
            if (oemName == null) oemName = extractStringField(obj, "oem_symbol");
            if (oemName == null) continue;

            if (grade == null || grade.equals("rejected")) {
                skipped++;
                continue;
            }

            String cbStr = extractStringField(obj, "firmware_callback");

            // ── DID and Service callbacks ────────────────────────────────────
            if ((kind.equals("did") || kind.equals("service")) && cbStr != null) {
                long cbAddr = parseHexAddr(cbStr);
                if (cbAddr == 0) continue;

                String suffix = kind.equals("did")
                    ? "did_" + extractStringField(obj, "identifier")
                    : "sid_" + extractStringField(obj, "sid");

                if (grade.equals("exact") || grade.equals("structural")) {
                    if (action != null && action.equals("name_callback")) {
                        nameFunctionIfUnnamed(cbAddr, oemName, suffix);
                        applied++;
                    } else {
                        addComment(cbAddr, "[Techstream OEM] " + oemName + " (" + suffix + ")");
                        commented++;
                    }
                } else if (grade.equals("family")) {
                    addComment(cbAddr, "[Techstream OEM candidate] " + oemName
                        + " (" + suffix + ", grade: family)");
                    commented++;
                } else {
                    addComment(cbAddr, "[Techstream OEM CONFLICT] " + oemName
                        + " (" + suffix + ", grade: candidate — multiple descriptions)");
                    commented++;
                }
                continue;
            }

            // ── DTC offsets ──────────────────────────────────────────────────
            if (kind.equals("dtc")) {
                String code = extractStringField(obj, "code");
                String idStr = extractStringField(obj, "dtc_identifier");
                // Firmware offsets are a JSON array of hex strings
                String offsetsStr = extractArrayField(obj, "firmware_offsets");
                if (offsetsStr == null) continue;
                for (String off : offsetsStr.split(",")) {
                    off = off.trim();
                    long addr = parseHexAddr(off);
                    if (addr == 0) continue;
                    String comment = "[Techstream DTC] " + code
                        + " (0x" + idStr + ") " + oemName;
                    if (grade.equals("candidate"))
                        comment += " — conflicting descriptions";
                    appendPlateComment(addr, comment);
                    commented++;
                }
                continue;
            }

            // ── Monitors and active tests (vocabulary-only) ──────────────────
            // These don't have firmware addresses yet — they are recorded for
            // future callback analysis.  No Ghidra application at this stage.
            skipped++;
        }

        println("");
        println("Diagnostic vocabulary application complete:");
        println("  Symbols renamed: " + applied);
        println("  Comments added: " + commented);
        println("  Skipped (no target / rejected): " + skipped);
    }

    // ── Minimal JSON field extractors ────────────────────────────────────────

    private String extractStringField(String json, String field) {
        String needle = "\"" + field + "\"";
        int pos = json.indexOf(needle);
        if (pos < 0) return null;
        pos = json.indexOf('"', pos + needle.length());
        if (pos < 0) return null;
        int end = json.indexOf('"', pos + 1);
        if (end < 0) return null;
        return json.substring(pos + 1, end);
    }

    private String extractArrayField(String json, String field) {
        String needle = "\"" + field + "\"";
        int pos = json.indexOf(needle);
        if (pos < 0) return null;
        int start = json.indexOf('[', pos);
        if (start < 0) return null;
        int end = json.indexOf(']', start);
        if (end < 0) return null;
        String content = json.substring(start + 1, end);
        return content.isEmpty() ? null : content;
    }

    private long parseHexAddr(String s) {
        s = s.trim().replace("\"", "");
        if (s.startsWith("0x") || s.startsWith("0X")) s = s.substring(2);
        try {
            return Long.parseLong(s, 16);
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    private int findMatchingBrace(String json, int openPos) {
        int depth = 0;
        for (int i = openPos; i < json.length(); i++) {
            char c = json.charAt(i);
            if (c == '{') depth++;
            else if (c == '}') {
                depth--;
                if (depth == 0) return i;
            }
        }
        return -1;
    }
}
