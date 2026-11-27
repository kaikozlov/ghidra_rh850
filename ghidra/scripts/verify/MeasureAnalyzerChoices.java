//@author OpenAI
//@category Verification
// Set Address Tables and Non-Returning Functions options or measure the resulting project.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.Array;
import ghidra.program.model.data.Structure;
import ghidra.program.model.listing.Bookmark;
import ghidra.program.model.listing.BookmarkType;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.listing.FlowOverride;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;

import java.io.PrintWriter;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class MeasureAnalyzerChoices extends GhidraScript {
    private static final String ADDRESS_TABLES = "Create Address Tables";
    private static final String NO_RETURN = "Non-Returning Functions - Discovered";
    private static final Pattern TABLE_LENGTH = Pattern.compile("Address table\\[(\\d+)\\] created");

    private static final class TableResult {
        Address start;
        int entries;
        int badEntries;
        final List<String> bad = new ArrayList<>();
    }

    private static final class NoReturnResult {
        Function function;
        boolean reachesReturn;
        int callers;
        int cutCallers;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length == 3 && args[0].equals("configure")) {
            configure(args[1], args[2]);
            return;
        }
        if (args.length == 2 && args[0].equals("export-functions")) {
            exportFunctions(args[1]);
            return;
        }
        if (args.length == 3 && args[0].equals("measure")) {
            measure(args[1], args[2]);
            return;
        }
        throw new IllegalArgumentException(
            "usage: MeasureAnalyzerChoices.java configure ADDRESS_TABLES NO_RETURN | " +
            "export-functions OUTPUT | measure CONFIG OUTPUT_JSON");
    }

    private void configure(String addressTables, String noReturn) {
        if (!addressTables.equals("unchanged"))
            setAnalysisOption(currentProgram, ADDRESS_TABLES, addressTables);
        if (!noReturn.equals("unchanged"))
            setAnalysisOption(currentProgram, NO_RETURN, noReturn);
        var options = getCurrentAnalysisOptionsAndValues(currentProgram);
        println("MeasureAnalyzerChoices: " + ADDRESS_TABLES + "=" +
            options.get(ADDRESS_TABLES) + ", " + NO_RETURN + "=" + options.get(NO_RETURN));
    }

    private void exportFunctions(String outputPath) throws Exception {
        try (PrintWriter out = new PrintWriter(outputPath)) {
            FunctionIterator iterator = currentProgram.getFunctionManager().getFunctions(true);
            while (iterator.hasNext())
                out.println(iterator.next().getEntryPoint().getOffset());
        }
        println("MeasureAnalyzerChoices: wrote " + outputPath);
    }

    private void measure(String config, String outputPath) throws Exception {
        Listing listing = currentProgram.getListing();
        long functions = currentProgram.getFunctionManager().getFunctionCount();
        long instructions = 0;
        long switches = 0;
        long switchesInFunctions = 0;
        InstructionIterator instructionIterator = listing.getInstructions(true);
        while (instructionIterator.hasNext()) {
            Instruction instruction = instructionIterator.next();
            instructions++;
            if (instruction.getMnemonicString().equalsIgnoreCase("switch")) {
                switches++;
                if (getFunctionContaining(instruction.getAddress()) != null) switchesInFunctions++;
            }
        }
        long symbols = currentProgram.getSymbolTable().getNumSymbols();

        List<TableResult> tables = measureAddressTables();
        int tableEntries = 0;
        int badTableEntries = 0;
        for (TableResult table : tables) {
            tableEntries += table.entries;
            badTableEntries += table.badEntries;
        }

        List<NoReturnResult> noReturns = measureNoReturns();
        int falseNoReturns = 0;
        int callerCuts = 0;
        int wrongCallerCuts = 0;
        for (NoReturnResult result : noReturns) {
            if (result.reachesReturn) falseNoReturns++;
            callerCuts += result.cutCallers;
            if (result.reachesReturn) wrongCallerCuts += result.cutCallers;
        }

        try (PrintWriter out = new PrintWriter(outputPath)) {
            out.println("{");
            out.println("  \"config\": \"" + json(config) + "\",");
            out.println("  \"functions\": " + functions + ",");
            out.println("  \"instructions\": " + instructions + ",");
            out.println("  \"symbols\": " + symbols + ",");
            out.println("  \"decoded_switches\": " + switches + ",");
            out.println("  \"decoded_switches_in_functions\": " + switchesInFunctions + ",");
            out.println("  \"address_tables_created\": " + tables.size() + ",");
            out.println("  \"address_table_entries\": " + tableEntries + ",");
            out.println("  \"address_table_bad_entries\": " + badTableEntries + ",");
            out.println("  \"no_return_functions\": " + noReturns.size() + ",");
            out.println("  \"false_no_return_functions\": " + falseNoReturns + ",");
            out.println("  \"caller_flow_cuts\": " + callerCuts + ",");
            out.println("  \"wrong_caller_flow_cuts\": " + wrongCallerCuts + ",");
            out.println("  \"address_tables\": [");
            for (int i = 0; i < tables.size(); i++) {
                TableResult table = tables.get(i);
                out.println("    {\"start\": \"" + table.start + "\", \"entries\": " +
                    table.entries + ", \"bad_entries\": " + table.badEntries +
                    ", \"bad\": [" + quoted(table.bad) + "]}" +
                    (i + 1 == tables.size() ? "" : ","));
            }
            out.println("  ],");
            out.println("  \"no_returns\": [");
            for (int i = 0; i < noReturns.size(); i++) {
                NoReturnResult result = noReturns.get(i);
                out.println("    {\"entry\": \"" + result.function.getEntryPoint() +
                    "\", \"name\": \"" + json(result.function.getName(true)) +
                    "\", \"reaches_return\": " + result.reachesReturn +
                    ", \"callers\": " + result.callers + ", \"cut_callers\": " +
                    result.cutCallers + "}" + (i + 1 == noReturns.size() ? "" : ","));
            }
            out.println("  ]");
            out.println("}");
        }
        println("MeasureAnalyzerChoices: wrote " + outputPath);
    }

    private List<TableResult> measureAddressTables() throws Exception {
        List<TableResult> results = new ArrayList<>();
        Iterator<Bookmark> bookmarks = currentProgram.getBookmarkManager().getBookmarksIterator();
        while (bookmarks.hasNext()) {
            Bookmark bookmark = bookmarks.next();
            if (!BookmarkType.ANALYSIS.equals(bookmark.getTypeString()) ||
                !"Address Table".equals(bookmark.getCategory())) continue;
            Matcher matcher = TABLE_LENGTH.matcher(bookmark.getComment());
            if (!matcher.matches()) continue;
            TableResult result = new TableResult();
            result.start = bookmark.getAddress();
            result.entries = Integer.parseInt(matcher.group(1));
            for (int i = 0; i < result.entries; i++) {
                Address member = result.start.add(i * 4L);
                long rawTarget = currentProgram.getMemory().getInt(member) & 0xffffffffL;
                Address target = toAddr(rawTarget);
                if (!isFunctionEntryOrSeededTableMember(target)) {
                    result.badEntries++;
                    result.bad.add(member + "->" + target);
                }
            }
            results.add(result);
        }
        return results;
    }

    private boolean isFunctionEntryOrSeededTableMember(Address target) {
        if (currentProgram.getFunctionManager().getFunctionAt(target) != null) return true;
        Data data = currentProgram.getListing().getDefinedDataContaining(target);
        if (data == null) return false;
        while (data.getParent() != null) data = data.getParent();
        if (!(data.getDataType() instanceof Array) && !(data.getDataType() instanceof Structure)) {
            return false;
        }
        Symbol primary = currentProgram.getSymbolTable().getPrimarySymbol(data.getMinAddress());
        return primary != null && primary.getSource() == SourceType.USER_DEFINED;
    }

    private List<NoReturnResult> measureNoReturns() {
        List<NoReturnResult> results = new ArrayList<>();
        FunctionIterator iterator = currentProgram.getFunctionManager().getFunctions(true);
        while (iterator.hasNext()) {
            Function function = iterator.next();
            if (!function.hasNoReturn()) continue;
            NoReturnResult result = new NoReturnResult();
            result.function = function;
            result.reachesReturn = reachesReturn(function);
            ReferenceIterator references =
                currentProgram.getReferenceManager().getReferencesTo(function.getEntryPoint());
            while (references.hasNext()) {
                Reference reference = references.next();
                if (!reference.getReferenceType().isCall()) continue;
                result.callers++;
                Instruction call = getInstructionAt(reference.getFromAddress());
                if (call != null && (call.getFlowOverride() == FlowOverride.CALL_RETURN ||
                    call.getFallThrough() == null)) result.cutCallers++;
            }
            results.add(result);
        }
        return results;
    }

    private boolean reachesReturn(Function function) {
        ArrayDeque<Address> pending = new ArrayDeque<>();
        Set<Address> visited = new HashSet<>();
        pending.add(function.getEntryPoint());
        while (!pending.isEmpty() && visited.size() < 100000) {
            Address address = pending.removeFirst();
            if (!visited.add(address)) continue;
            Function other = getFunctionAt(address);
            if (other != null && !other.equals(function)) continue;
            Instruction instruction = getInstructionAt(address);
            if (instruction == null) continue;
            if (isReturnClass(instruction)) return true;
            if (instruction.getFlowType().isCall()) {
                Address fallthrough = instruction.getFallThrough();
                if (fallthrough != null) pending.add(fallthrough);
                continue;
            }
            for (Address flow : instruction.getFlows()) pending.add(flow);
            Address fallthrough = instruction.getFallThrough();
            if (fallthrough != null) pending.add(fallthrough);
        }
        return false;
    }

    private boolean isReturnClass(Instruction instruction) {
        String mnemonic = instruction.getMnemonicString().toLowerCase();
        if (mnemonic.equals("ctret") || mnemonic.equals("eiret") || mnemonic.equals("feret")) {
            return true;
        }
        if (!mnemonic.equals("jmp") && !mnemonic.equals("dispose")) return false;
        for (int i = 0; i < instruction.getNumOperands(); i++) {
            String operand = instruction.getDefaultOperandRepresentation(i).toLowerCase();
            if (operand.contains("lp")) return true;
        }
        return false;
    }

    private static String quoted(List<String> values) {
        StringBuilder result = new StringBuilder();
        for (String value : values) {
            if (result.length() != 0) result.append(", ");
            result.append('\"').append(json(value)).append('\"');
        }
        return result.toString();
    }

    private static String json(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"")
            .replace("\n", "\\n").replace("\r", "\\r");
    }
}
