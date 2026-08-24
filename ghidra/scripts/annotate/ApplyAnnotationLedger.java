//@author kaikozlov
//@category Analysis
// Apply the tracked declarative annotation ledger (data/annotations/annotation_ledger.jsonl).
//
// The ledger is curated by tools/annotations, which owns canonical form,
// uniqueness, and conflict validation. This applier is the generic stage-4
// replay surface for mechanical overlays only: function renames, data labels,
// and explicit comments. Discovery, signatures, types, and structured overlays
// stay in dedicated scripts.
//
// Normal repository entry points validate the exact schema and conflict rules
// with tools/annotations first. Defense-in-depth checks here still fail closed
// before any program mutation when invoked directly:
//   - exactly one argument: an absolute path to the ledger file;
//   - every record's op/address and required fields must be recognized;
//   - a 'function' record requires a function at the address;
//   - a 'label' record requires NO function at the address (a label on a
//     function entry would silently rename the function's primary symbol);
//   - no function creation, deletion, signature, or memory mutation happens
//     here: renames/labels/comments only, so the recovered graph cannot move.
// Re-running the script over an already-annotated project is idempotent. The
// script intentionally uses two passes instead of relying on a nested Ghidra
// transaction: the persistent bridge already owns an outer transaction, and a
// nested rollback does not undo mutations inside it. Every deterministic target,
// field, comment-type, and symbol-name conflict is therefore checked first.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolTable;
import ghidra.program.model.symbol.SymbolIterator;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.BufferedReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class ApplyAnnotationLedger extends GhidraScript {
    private static final Map<String, Integer> COMMENT_TYPES = buildCommentTypes();

    private static Map<String, Integer> buildCommentTypes() {
        Map<String, Integer> types = new LinkedHashMap<>();
        types.put("plate", CodeUnit.PLATE_COMMENT);
        types.put("pre", CodeUnit.PRE_COMMENT);
        types.put("post", CodeUnit.POST_COMMENT);
        types.put("eol", CodeUnit.EOL_COMMENT);
        types.put("repeatable", CodeUnit.REPEATABLE_COMMENT);
        return types;
    }

    private Address parseLedgerAddress(String raw) {
        if (raw == null || !raw.matches("^0x[0-9a-f]{8}$")) {
            throw new IllegalStateException("address must be canonical 0x%08x hex, got " + raw);
        }
        try {
            return toAddr(Long.parseUnsignedLong(raw.substring(2), 16));
        } catch (NumberFormatException e) {
            throw new IllegalStateException("address must be canonical 0x%08x hex, got " + raw);
        }
    }

    private int commentType(String raw) {
        Integer type = raw == null ? null : COMMENT_TYPES.get(raw);
        if (type == null) {
            throw new IllegalStateException("unknown comment_type " + raw);
        }
        return type;
    }

    private static String stringField(JsonObject record, String field) {
        JsonElement element = record.get(field);
        if (element == null || !element.isJsonPrimitive() || !element.getAsJsonPrimitive().isString()) {
            return null;
        }
        return element.getAsString();
    }

    private static String requireName(JsonObject record, String field, Path ledger, long line) {
        String value = stringField(record, field);
        if (value == null || !value.matches("^[A-Za-z_][A-Za-z0-9_]{0,199}$")) {
            throw new IllegalStateException(ledger + ":" + line + ": invalid " + field);
        }
        return value;
    }

    private void validateOptionalComment(JsonObject record, Path ledger, long line) {
        String comment = stringField(record, "comment");
        String type = stringField(record, "comment_type");
        if ((comment == null) != (type == null)) {
            throw new IllegalStateException(
                ledger + ":" + line + ": comment and comment_type must be provided together");
        }
        if (comment != null) {
            if (comment.isBlank()) {
                throw new IllegalStateException(ledger + ":" + line + ": empty comment");
            }
            commentType(type);
        }
    }

    private void requireNameAvailable(
            String name, Address address, Path ledger, long line, Map<String, Address> plannedNames) {
        Address planned = plannedNames.get(name);
        if (planned != null && !planned.equals(address)) {
            throw new IllegalStateException(
                ledger + ":" + line + ": symbol name " + name +
                " is assigned to both " + planned + " and " + address);
        }
        plannedNames.put(name, address);

        SymbolIterator existing = currentProgram.getSymbolTable().getSymbols(name);
        while (existing.hasNext()) {
            Symbol symbol = existing.next();
            if (!symbol.getAddress().equals(address)) {
                throw new IllegalStateException(
                    ledger + ":" + line + ": symbol name " + name +
                    " already exists at " + symbol.getAddress());
            }
        }
    }

    private void preflightRecord(
            JsonObject record, Path ledger, long line, Map<String, Address> plannedNames) {
        String op = stringField(record, "op");
        String addressText = stringField(record, "address");
        if (op == null || addressText == null) {
            throw new IllegalStateException(ledger + ":" + line + ": missing op/address");
        }
        Address address = parseLedgerAddress(addressText);
        if (!currentProgram.getMemory().contains(address)) {
            throw new IllegalStateException(ledger + ":" + line + ": unmapped address " + address);
        }

        switch (op) {
            case "function": {
                String name = requireName(record, "name", ledger, line);
                validateOptionalComment(record, ledger, line);
                if (currentProgram.getFunctionManager().getFunctionAt(address) == null) {
                    throw new IllegalStateException(
                        ledger + ":" + line + ": no function at " + address + " for " + name);
                }
                requireNameAvailable(name, address, ledger, line, plannedNames);
                break;
            }
            case "label": {
                String name = requireName(record, "name", ledger, line);
                validateOptionalComment(record, ledger, line);
                if (currentProgram.getFunctionManager().getFunctionContaining(address) != null) {
                    throw new IllegalStateException(
                        ledger + ":" + line + ": label target " + address + " is inside a function body");
                }
                requireNameAvailable(name, address, ledger, line, plannedNames);
                break;
            }
            case "comment": {
                String text = stringField(record, "comment");
                String type = stringField(record, "comment_type");
                if (text == null || text.isBlank() || type == null) {
                    throw new IllegalStateException(
                        ledger + ":" + line + ": comment record requires nonempty comment and comment_type");
                }
                commentType(type);
                break;
            }
            default:
                throw new IllegalStateException(ledger + ":" + line + ": unknown op " + op);
        }
    }

    private void renameFunction(long addressRaw, Address address, String name, String comment, String commentType) throws Exception {
        Function function = currentProgram.getFunctionManager().getFunctionAt(address);
        if (function == null) {
            throw new IllegalStateException("no function at " + address + " for " + name);
        }
        function.setName(name, SourceType.USER_DEFINED);
        if (comment != null) {
            currentProgram.getListing().setComment(address, commentType(commentType), comment);
        }
        println(String.format("function 0x%x -> %s", addressRaw, name));
    }

    private void labelData(long addressRaw, Address address, String name, String comment, String commentType) throws Exception {
        if (currentProgram.getFunctionManager().getFunctionContaining(address) != null) {
            throw new IllegalStateException(
                "label record at " + address + " targets a function body; use a function record or a code label");
        }
        SymbolTable symbols = currentProgram.getSymbolTable();
        Symbol symbol = symbols.getPrimarySymbol(address);
        if (symbol != null) {
            symbol.setName(name, SourceType.USER_DEFINED);
        } else {
            symbol = symbols.createLabel(address, name, SourceType.USER_DEFINED);
            symbol.setPrimary();
        }
        if (comment != null) {
            currentProgram.getListing().setComment(address, commentType(commentType), comment);
        }
        println(String.format("data 0x%x -> %s", addressRaw, name));
    }

    private void setComment(long addressRaw, Address address, String text, String commentType) {
        Listing listing = currentProgram.getListing();
        listing.setComment(address, commentType(commentType), text);
        println(String.format("%s comment 0x%x set", commentType, addressRaw));
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException("expected one absolute ledger path");
        }
        Path ledger = Path.of(args[0]);
        if (!ledger.isAbsolute()) {
            throw new IllegalArgumentException("ledger path must be absolute: " + ledger);
        }
        if (!Files.isRegularFile(ledger)) {
            throw new IllegalStateException("ledger file not found: " + ledger);
        }

        // Pass 1: parse and validate the COMPLETE plan before changing the program.
        List<JsonObject> records = new ArrayList<>();
        Map<String, Address> plannedNames = new HashMap<>();
        long line = 0;
        try (BufferedReader reader = Files.newBufferedReader(ledger, StandardCharsets.UTF_8)) {
            String raw;
            while ((raw = reader.readLine()) != null) {
                line++;
                if (raw.isBlank()) {
                    throw new IllegalStateException(ledger + ":" + line + ": blank line");
                }
                JsonObject record;
                try {
                    JsonElement parsed = JsonParser.parseString(raw);
                    record = parsed.isJsonObject() ? parsed.getAsJsonObject() : null;
                } catch (com.google.gson.JsonParseException e) {
                    throw new IllegalStateException(ledger + ":" + line + ": invalid JSON");
                }
                if (record == null) {
                    throw new IllegalStateException(
                        ledger + ":" + line + ": record must be a JSON object");
                }
                preflightRecord(record, ledger, line, plannedNames);
                records.add(record);
            }
        }

        // Pass 2: all deterministic failures are behind us. Apply the validated plan.
        long functions = 0;
        long labels = 0;
        long comments = 0;
        for (JsonObject record : records) {
            String op = stringField(record, "op");
            String addressText = stringField(record, "address");
            Address address = parseLedgerAddress(addressText);
            long addressRaw = Long.parseUnsignedLong(addressText.substring(2), 16);
            switch (op) {
                case "function":
                    renameFunction(addressRaw, address, stringField(record, "name"),
                        stringField(record, "comment"), stringField(record, "comment_type"));
                    functions++;
                    break;
                case "label":
                    labelData(addressRaw, address, stringField(record, "name"),
                        stringField(record, "comment"), stringField(record, "comment_type"));
                    labels++;
                    break;
                case "comment":
                    setComment(addressRaw, address, stringField(record, "comment"),
                        stringField(record, "comment_type"));
                    comments++;
                    break;
                default:
                    throw new AssertionError("preflight admitted unknown op: " + op);
            }
        }

        println("ApplyAnnotationLedger: applied " + (functions + labels + comments)
            + " records (functions=" + functions + " labels=" + labels
            + " comments=" + comments + ") from " + ledger);
    }}
