//@author kaikozlov
//@category Analysis
// Apply Techstream OEM diagnostic vocabulary to the annotated Ghidra project.
//
// Consumes diagnostic_vocabulary.json — the output of
// tools/diagnostics/correlate_vocabulary.py — and applies OEM names and
// comments to DID callbacks, service callbacks, monitor callbacks, and
// DTC locations.
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
// The vocabulary path is passed as the first script argument.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.ArrayList;

public class ApplyDiagnosticVocabulary extends GhidraScript {

    private String vocabPath;

    private enum FunctionEffect {
        RENAMED, COMMENTED, UNCHANGED, MISSING
    }

    private String loadVocabularyPath() throws Exception {
        String[] args = getScriptArgs();
        if (args != null && args.length > 0 && !args[0].isEmpty()) {
            return args[0];
        }
        throw new Exception("diagnostic_vocabulary.json path must be passed as the first script argument");
    }

    private boolean addComment(long addr, String text) throws Exception {
        Address a = toAddr(addr);
        String existing = currentProgram.getListing().getComment(CodeUnit.PRE_COMMENT, a);
        if (existing == null) existing = "";
        if (existing.contains(text)) return false;
        String prefix = existing.isEmpty() ? "" : existing + "\n";
        currentProgram.getListing().setComment(a, CodeUnit.PRE_COMMENT, prefix + text);
        return true;
    }

    private boolean appendPlateComment(long addr, String text) throws Exception {
        Address a = toAddr(addr);
        String existing = currentProgram.getListing().getComment(CodeUnit.PLATE_COMMENT, a);
        if (existing == null) existing = "";
        if (existing.contains(text)) return false;
        String prefix = existing.isEmpty() ? "" : existing + "\n";
        currentProgram.getListing().setComment(a, CodeUnit.PLATE_COMMENT, prefix + text);
        return true;
    }

    private FunctionEffect nameFunctionIfUnnamed(
            long addr, String oemName, String suffix) throws Exception {
        Address a = toAddr(addr);
        Function f = currentProgram.getFunctionManager().getFunctionAt(a);
        if (f == null) return FunctionEffect.MISSING;
        String current = f.getName();
        // Don't overwrite an existing meaningful name (from AnnotateApplicationDiagnostics)
        boolean genericDidSeed = current.matches("did_[0-9a-fA-F]{4}_callback");
        if (!current.startsWith("FUN_") && !current.startsWith("LAB_")
                && !genericDidSeed) {
            return addComment(
                addr, "[Techstream OEM] " + oemName + " (" + suffix + ")"
            ) ? FunctionEffect.COMMENTED : FunctionEffect.UNCHANGED;
        }
        String symbol = oemName.toLowerCase().replaceAll("[^a-z0-9]+", "_") + "_" + suffix;
        f.setName(symbol, SourceType.USER_DEFINED);
        println(a + " → " + symbol + " (Techstream OEM)");
        return FunctionEffect.RENAMED;
    }

    @Override
    public void run() throws Exception {
        vocabPath = loadVocabularyPath();
        String json = Files.readString(Path.of(vocabPath));
        println("Loading diagnostic vocabulary from: " + vocabPath);

        int applied = 0, commented = 0, unchanged = 0, skipped = 0;

        // Parse the "mappings" array and process each entry.
        JsonParser parser = new JsonParser(json);
        JsonArray mappings = parser.getObject().getArray("mappings");

        for (int i = 0; i < mappings.size(); i++) {
            JsonObject entry = mappings.getObject(i);

            String kind = entry.getString("kind", "");
            String grade = entry.getString("match_grade", "");
            String action = entry.getString("annotation_action", "");
            String oemName = entry.getString("oem_name", null);

            if (grade.equals("rejected")) {
                skipped++;
                continue;
            }
            if (oemName == null) {
                skipped++;
                continue;
            }

            // ── DID, Service, and Monitor callbacks ────────────────────────
            // All three carry a firmware_callback hex string.
            if ((kind.equals("did") || kind.equals("service") || kind.equals("monitor"))
                    && (grade.equals("exact") || grade.equals("structural"))) {

                String cbStr = entry.getString("firmware_callback", null);
                if (cbStr == null) {
                    skipped++;
                    continue;
                }
                long cbAddr = parseHexAddr(cbStr);
                if (cbAddr == 0) {
                    skipped++;
                    continue;
                }

                // Build the suffix from the identifier or SID.
                // These are numeric in the JSON (integers, not strings).
                String suffix;
                if (kind.equals("did") || kind.equals("monitor")) {
                    long id = entry.getLong("identifier", 0);
                    suffix = "did_" + String.format("%04X", id);
                } else {
                    long sid = entry.getLong("sid", 0);
                    suffix = "sid_" + String.format("%02X", sid);
                }

                if (action != null && action.equals("name_callback")) {
                    FunctionEffect effect = nameFunctionIfUnnamed(cbAddr, oemName, suffix);
                    if (effect == FunctionEffect.MISSING) {
                        throw new Exception(
                            "missing " + grade + " callback function at " + toAddr(cbAddr)
                            + " for " + kind + " " + oemName
                        );
                    } else if (effect == FunctionEffect.RENAMED) {
                        applied++;
                    } else if (effect == FunctionEffect.COMMENTED) {
                        commented++;
                    } else {
                        unchanged++;
                    }
                } else {
                    if (addComment(
                            cbAddr, "[Techstream OEM] " + oemName + " (" + suffix + ")")) {
                        commented++;
                    } else {
                        unchanged++;
                    }
                }

                // Attach RAM source comment for monitors that have one
                if (kind.equals("monitor")) {
                    String ramSource = entry.getString("ram_source", null);
                    if (ramSource != null) {
                        if (addComment(cbAddr, "[RAM source] " + ramSource)) {
                            commented++;
                        } else {
                            unchanged++;
                        }
                    }
                }
                continue;
            }

            // Family/candidate grade callbacks — comment only
            if (kind.equals("did") || kind.equals("service") || kind.equals("monitor")) {
                String cbStr = entry.getString("firmware_callback", null);
                if (cbStr != null) {
                    long cbAddr = parseHexAddr(cbStr);
                    if (cbAddr != 0) {
                        String tag = grade.equals("candidate")
                            ? "[Techstream OEM CONFLICT] "
                            : "[Techstream OEM candidate] ";
                        if (addComment(
                                cbAddr, tag + oemName + " (grade: " + grade + ")")) {
                            commented++;
                        } else {
                            unchanged++;
                        }
                        continue;
                    }
                }
                skipped++;
                continue;
            }

            // ── DTC offsets ──────────────────────────────────────────────
            if (kind.equals("dtc")) {
                String code = entry.getString("code", "?");
                long dtcId = entry.getLong("dtc_identifier", 0);
                JsonArray offsets = entry.getArray("firmware_offsets");
                if (offsets == null || offsets.size() == 0) {
                    skipped++;
                    continue;
                }
                for (int j = 0; j < offsets.size(); j++) {
                    String off = offsets.getString(j);
                    long addr = parseHexAddr(off);
                    if (addr == 0) continue;
                    String comment = "[Techstream DTC] " + code
                        + " (0x" + String.format("%04X", dtcId) + ") " + oemName;
                    if (grade.equals("candidate"))
                        comment += " — conflicting descriptions";
                    if (appendPlateComment(addr, comment)) {
                        commented++;
                    } else {
                        unchanged++;
                    }
                }
                continue;
            }

            // Everything else (utility_procedure, active_test vocabulary)
            // has no firmware target — skip.
            skipped++;
        }

        println("");
        println("Diagnostic vocabulary application complete:");
        println("  Symbols renamed: " + applied);
        println("  Comments added: " + commented);
        println("  Already applied: " + unchanged);
        println("  Skipped (no target / rejected): " + skipped);
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

    // ── Minimal JSON parser (no external dependencies) ────────────────────
    // Ghidra does not ship Gson or javax.json. This parser correctly handles
    // numeric and string values, arrays, nested objects, and escape sequences.

    static class JsonParser {
        private final String s;
        private int pos;

        JsonParser(String s) { this.s = s; this.pos = 0; }

        JsonObject getObject() {
            skipWs();
            expect('{');
            return parseObject();
        }

        private JsonObject parseObject() {
            JsonObject obj = new JsonObject();
            skipWs();
            if (peek() == '}') { pos++; return obj; }
            while (true) {
                skipWs();
                String key = parseString();
                skipWs();
                expect(':');
                skipWs();
                char c = peek();
                if (c == '"') {
                    obj.setString(key, parseString());
                } else if (c == '{') {
                    pos++;
                    obj.setObject(key, parseObject());
                } else if (c == '[') {
                    pos++;
                    obj.setArray(key, parseArray());
                } else if (c == 't' || c == 'f') {
                    obj.setBool(key, parseBool());
                } else if (c == 'n') {
                    pos += 4; // null
                } else {
                    obj.setNumber(key, parseNumber());
                }
                skipWs();
                char sep = peek();
                if (sep == ',') { pos++; continue; }
                if (sep == '}') { pos++; break; }
                break;
            }
            return obj;
        }

        private JsonArray parseArray() {
            JsonArray arr = new JsonArray();
            skipWs();
            if (peek() == ']') { pos++; return arr; }
            while (true) {
                skipWs();
                char c = peek();
                if (c == '"') {
                    arr.addString(parseString());
                } else if (c == '{') {
                    pos++;
                    arr.addObject(parseObject());
                } else if (c == 'n') {
                    pos += 4; // null
                    arr.addString(null);
                } else {
                    arr.addNumber(parseNumber());
                }
                skipWs();
                char sep = peek();
                if (sep == ',') { pos++; continue; }
                if (sep == ']') { pos++; break; }
                break;
            }
            return arr;
        }

        private String parseString() {
            expect('"');
            StringBuilder sb = new StringBuilder();
            while (pos < s.length()) {
                char c = s.charAt(pos++);
                if (c == '"') break;
                if (c == '\\') {
                    if (pos >= s.length()) break;
                    char e = s.charAt(pos++);
                    switch (e) {
                        case '"': sb.append('"'); break;
                        case '\\': sb.append('\\'); break;
                        case '/': sb.append('/'); break;
                        case 'n': sb.append('\n'); break;
                        case 'r': sb.append('\r'); break;
                        case 't': sb.append('\t'); break;
                        case 'u':
                            if (pos + 4 <= s.length()) {
                                String hex = s.substring(pos, pos + 4);
                                sb.append((char) Integer.parseInt(hex, 16));
                                pos += 4;
                            }
                            break;
                        default: sb.append(e);
                    }
                } else {
                    sb.append(c);
                }
            }
            return sb.toString();
        }

        private double parseNumber() {
            int start = pos;
            if (peek() == '-') pos++;
            while (pos < s.length()) {
                char c = s.charAt(pos);
                if ((c >= '0' && c <= '9') || c == '.' || c == 'e' || c == 'E' || c == '+' || c == '-') {
                    pos++;
                } else {
                    break;
                }
            }
            return Double.parseDouble(s.substring(start, pos));
        }

        private boolean parseBool() {
            if (s.charAt(pos) == 't') { pos += 4; return true; }
            pos += 5; return false;
        }

        private char peek() {
            if (pos >= s.length()) return '\0';
            return s.charAt(pos);
        }

        private void skipWs() {
            while (pos < s.length() && Character.isWhitespace(s.charAt(pos))) pos++;
        }

        private void expect(char c) {
            if (peek() != c)
                throw new RuntimeException("Expected '" + c + "' at pos " + pos + ", got '" + peek() + "'");
            pos++;
        }
    }

    static class JsonObject {
        java.util.Map<String, Object> map = new java.util.LinkedHashMap<>();

        void setString(String k, String v) { map.put(k, v); }
        void setNumber(String k, double v) { map.put(k, v); }
        void setBool(String k, boolean v) { map.put(k, v); }
        void setObject(String k, JsonObject v) { map.put(k, v); }
        void setArray(String k, JsonArray v) { map.put(k, v); }

        String getString(String k, String def) {
            Object v = map.get(k);
            return v instanceof String ? (String) v : def;
        }

        long getLong(String k, long def) {
            Object v = map.get(k);
            if (v instanceof Double) return ((Double) v).longValue();
            return def;
        }

        JsonArray getArray(String k) {
            Object v = map.get(k);
            return v instanceof JsonArray ? (JsonArray) v : null;
        }

        JsonObject getObject(String k) {
            Object v = map.get(k);
            return v instanceof JsonObject ? (JsonObject) v : null;
        }
    }

    static class JsonArray {
        private List<Object> items = new ArrayList<>();

        void addString(String s) { items.add(s); }
        void addNumber(double n) { items.add(n); }
        void addObject(JsonObject o) { items.add(o); }

        int size() { return items.size(); }

        String getString(int i) {
            Object v = items.get(i);
            return v instanceof String ? (String) v : null;
        }

        JsonObject getObject(int i) {
            Object v = items.get(i);
            return v instanceof JsonObject ? (JsonObject) v : null;
        }
    }
}
