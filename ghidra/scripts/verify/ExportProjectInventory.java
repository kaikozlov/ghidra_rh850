//@author kaikozlov
//@category Verification
// Export a deterministic, path-free JSONL inventory for exact project parity.
import ghidra.app.script.GhidraScript;
import ghidra.framework.Application;
import ghidra.program.database.mem.ByteMappingScheme;
import ghidra.program.database.mem.FileBytes;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressRangeIterator;
import ghidra.program.model.data.DataType;
import ghidra.program.model.listing.Bookmark;
import ghidra.program.model.listing.CommentType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.mem.MemoryBlockSourceInfo;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;

import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class ExportProjectInventory extends GhidraScript {
    private static final Comparator<String> TEXT_ORDER = ExportProjectInventory::compareText;
    private static final Comparator<Address> ADDRESS_ORDER = (left, right) -> {
        int bySpace = compareText(
            left.getAddressSpace().getName(), right.getAddressSpace().getName());
        return bySpace != 0 ? bySpace : Long.compareUnsigned(
            left.getOffset(), right.getOffset());
    };

    private static final class Counts {
        long functions;
        long bodyRanges;
        long bodyAddresses;
        long userFunctionNames;
        long userSymbols;
        long listingComments;
        long functionComments;
        long bookmarks;
        final Map<String, Long> callingConventions = new TreeMap<>();
        final Map<String, Long> nameSources = new TreeMap<>();
        final Map<String, Long> signatureSources = new TreeMap<>();
    }

    private static final class CommentRow {
        Address address;
        CommentType type;
        String text;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException("expected one absolute JSONL output path");
        }
        Path output = Path.of(args[0]);
        if (!output.isAbsolute()) {
            throw new IllegalArgumentException("output path must be absolute: " + output);
        }
        Files.createDirectories(output.getParent());

        Counts counts = new Counts();
        try (PrintWriter out = new PrintWriter(
                Files.newBufferedWriter(output, StandardCharsets.UTF_8))) {
            writeMeta(out);
            writeMemoryBlocks(out);
            List<Function> functions = sortedFunctions();
            writeFunctions(out, functions, counts);
            writeUserSymbols(out, counts);
            writeListingComments(out, counts);
            writeFunctionComments(out, functions, counts);
            writeBookmarks(out, counts);
            writeTotals(out, counts);
        }

        println("ExportProjectInventory: wrote canonical JSONL with " + counts.functions +
            " functions, " + counts.userSymbols + " user symbols, " +
            counts.listingComments + " listing comments, " + counts.functionComments +
            " function comments, and " + counts.bookmarks + " bookmarks to " + output);
    }

    private void writeMeta(PrintWriter out) {
        writeLine(out, "{" +
            field("record", "meta") + "," +
            numberField("schema_version", 1) + "," +
            field("ghidra_version", Application.getApplicationVersion()) + "," +
            field("program_name", currentProgram.getName()) + "," +
            field("executable_sha256", currentProgram.getExecutableSHA256()) + "," +
            field("executable_format", currentProgram.getExecutableFormat()) + "," +
            field("language_id", currentProgram.getLanguageID().getIdAsString()) + "," +
            field("compiler_spec_id",
                currentProgram.getCompilerSpec().getCompilerSpecID().getIdAsString()) +
            "}");
    }

    private void writeMemoryBlocks(PrintWriter out) {
        List<MemoryBlock> blocks = new ArrayList<>(
            Arrays.asList(currentProgram.getMemory().getBlocks()));
        blocks.sort(Comparator.comparing(MemoryBlock::getStart, ADDRESS_ORDER)
            .thenComparing(MemoryBlock::getName, TEXT_ORDER));
        for (MemoryBlock block : blocks) {
            writeLine(out, "{" +
                field("record", "memory_block") + "," +
                field("name", block.getName()) + "," +
                objectField("start", addressJson(block.getStart())) + "," +
                objectField("end", addressJson(block.getEnd())) + "," +
                numberField("size", block.getSize()) + "," +
                field("block_type", block.getType().toString()) + "," +
                boolField("initialized", block.isInitialized()) + "," +
                boolField("overlay", block.isOverlay()) + "," +
                boolField("loaded", block.isLoaded()) + "," +
                boolField("read", block.isRead()) + "," +
                boolField("write", block.isWrite()) + "," +
                boolField("execute", block.isExecute()) + "," +
                boolField("volatile", block.isVolatile()) + "," +
                boolField("artificial", block.isArtificial()) + "," +
                arrayField("source_infos", sourceInfosJson(block.getSourceInfos())) +
                "}");
        }
    }

    private List<Function> sortedFunctions() {
        List<Function> functions = new ArrayList<>();
        FunctionIterator iterator = currentProgram.getFunctionManager().getFunctions(true);
        while (iterator.hasNext()) functions.add(iterator.next());
        functions.sort(Comparator.comparing(Function::getEntryPoint, ADDRESS_ORDER));
        return functions;
    }

    private void writeFunctions(PrintWriter out, List<Function> functions, Counts counts) {
        for (Function function : functions) {
            List<AddressRange> body = new ArrayList<>();
            AddressRangeIterator ranges = function.getBody().getAddressRanges(true);
            while (ranges.hasNext()) body.add(ranges.next());
            body.sort(ExportProjectInventory::compareRanges);
            Symbol symbol = function.getSymbol();
            SourceType nameSource = symbol == null ? null : symbol.getSource();
            String userName = nameSource == SourceType.USER_DEFINED && symbol != null
                ? symbol.getName(true) : null;
            String signatureSource = sourceName(function.getSignatureSource());
            String callingConvention = nullToEmpty(function.getCallingConventionName());
            Function thunk = function.isThunk() ? function.getThunkedFunction(false) : null;

            counts.functions++;
            counts.bodyRanges += body.size();
            counts.bodyAddresses += function.getBody().getNumAddresses();
            if (userName != null) counts.userFunctionNames++;
            increment(counts.callingConventions, callingConvention);
            increment(counts.nameSources, sourceName(nameSource));
            increment(counts.signatureSources, signatureSource);

            writeLine(out, "{" +
                field("record", "function") + "," +
                objectField("entry", addressJson(function.getEntryPoint())) + "," +
                arrayField("body_ranges", rangeArray(body)) + "," +
                numberField("body_address_count", function.getBody().getNumAddresses()) + "," +
                boolField("is_thunk", function.isThunk()) + "," +
                objectField("thunk_target", addressJson(thunk == null ? null : thunk.getEntryPoint())) + "," +
                boolField("is_inline", function.isInline()) + "," +
                boolField("is_external", function.isExternal()) + "," +
                nullableField("user_name", userName) + "," +
                field("name_source", sourceName(nameSource)) + "," +
                field("signature_source", signatureSource) + "," +
                field("calling_convention", callingConvention) + "," +
                objectField("return", parameterReturnJson(function.getReturn())) + "," +
                arrayField("parameters", parametersJson(function.getParameters())) + "," +
                boolField("varargs", function.hasVarArgs()) + "," +
                boolField("no_return", function.hasNoReturn()) + "," +
                boolField("custom_storage", function.hasCustomVariableStorage()) + "," +
                numberField("stack_purge_size", function.getStackPurgeSize()) +
                "}");
        }
    }

    private void writeUserSymbols(PrintWriter out, Counts counts) {
        List<Symbol> symbols = new ArrayList<>();
        SymbolIterator iterator = currentProgram.getSymbolTable().getAllSymbols(true);
        while (iterator.hasNext()) {
            Symbol symbol = iterator.next();
            if (!symbol.isDeleted() && symbol.getSource() == SourceType.USER_DEFINED) {
                symbols.add(symbol);
            }
        }
        symbols.sort(Comparator.comparing(Symbol::getAddress, ADDRESS_ORDER)
            .thenComparing(symbol -> symbol.getName(true), TEXT_ORDER)
            .thenComparing(symbol -> symbol.getSymbolType().toString(), TEXT_ORDER));
        for (Symbol symbol : symbols) {
            writeLine(out, "{" +
                field("record", "user_symbol") + "," +
                objectField("address", addressJson(symbol.getAddress())) + "," +
                field("symbol_type", symbol.getSymbolType().toString()) + "," +
                field("qualified_name", symbol.getName(true)) + "," +
                boolField("primary", symbol.isPrimary()) +
                "}");
        }
        counts.userSymbols = symbols.size();
    }

    private void writeListingComments(PrintWriter out, Counts counts) {
        Listing listing = currentProgram.getListing();
        List<CommentRow> comments = new ArrayList<>();
        for (CommentType type : CommentType.values()) {
            AddressIterator addresses = listing.getCommentAddressIterator(
                type, currentProgram.getAddressFactory().getAddressSet(), true);
            while (addresses.hasNext()) {
                Address address = addresses.next();
                String text = listing.getComment(type, address);
                if (text == null) continue;
                CommentRow row = new CommentRow();
                row.address = address;
                row.type = type;
                row.text = text;
                comments.add(row);
            }
        }
        comments.sort(Comparator.comparing((CommentRow row) -> row.address, ADDRESS_ORDER)
            .thenComparing(row -> row.type.name(), TEXT_ORDER));
        for (CommentRow row : comments) {
            writeLine(out, "{" +
                field("record", "listing_comment") + "," +
                objectField("address", addressJson(row.address)) + "," +
                field("comment_type", row.type.name()) + "," +
                field("text", row.text) +
                "}");
        }
        counts.listingComments = comments.size();
    }

    private void writeFunctionComments(PrintWriter out, List<Function> functions, Counts counts) {
        for (Function function : functions) {
            if (function.getComment() != null) {
                writeFunctionComment(out, function, "regular", function.getComment());
                counts.functionComments++;
            }
            if (function.getRepeatableComment() != null) {
                writeFunctionComment(out, function, "repeatable", function.getRepeatableComment());
                counts.functionComments++;
            }
        }
    }

    private void writeFunctionComment(PrintWriter out, Function function,
                                      String commentType, String text) {
        writeLine(out, "{" +
            field("record", "function_comment") + "," +
            objectField("entry", addressJson(function.getEntryPoint())) + "," +
            field("comment_type", commentType) + "," +
            field("text", text) +
            "}");
    }

    private void writeBookmarks(PrintWriter out, Counts counts) {
        List<Bookmark> bookmarks = new ArrayList<>();
        Iterator<Bookmark> iterator = currentProgram.getBookmarkManager().getBookmarksIterator();
        while (iterator.hasNext()) bookmarks.add(iterator.next());
        bookmarks.sort(Comparator.comparing(Bookmark::getAddress, ADDRESS_ORDER)
            .thenComparing(bookmark -> nullToEmpty(bookmark.getTypeString()), TEXT_ORDER)
            .thenComparing(bookmark -> nullToEmpty(bookmark.getCategory()), TEXT_ORDER)
            .thenComparing(bookmark -> nullToEmpty(bookmark.getComment()), TEXT_ORDER));
        for (Bookmark bookmark : bookmarks) {
            writeLine(out, "{" +
                field("record", "bookmark") + "," +
                objectField("address", addressJson(bookmark.getAddress())) + "," +
                field("type", nullToEmpty(bookmark.getTypeString())) + "," +
                field("category", nullToEmpty(bookmark.getCategory())) + "," +
                field("comment", nullToEmpty(bookmark.getComment())) +
                "}");
        }
        counts.bookmarks = bookmarks.size();
    }

    private void writeTotals(PrintWriter out, Counts counts) {
        writeLine(out, "{" +
            field("record", "totals") + "," +
            numberField("functions", counts.functions) + "," +
            numberField("instructions", currentProgram.getListing().getNumInstructions()) + "," +
            numberField("symbols", currentProgram.getSymbolTable().getNumSymbols()) + "," +
            numberField("memory_blocks", currentProgram.getMemory().getBlocks().length) + "," +
            numberField("body_ranges", counts.bodyRanges) + "," +
            numberField("body_addresses", counts.bodyAddresses) + "," +
            numberField("user_function_names", counts.userFunctionNames) + "," +
            numberField("user_symbols", counts.userSymbols) + "," +
            numberField("listing_comments", counts.listingComments) + "," +
            numberField("function_comments", counts.functionComments) + "," +
            numberField("bookmarks", counts.bookmarks) + "," +
            objectField("name_sources", countMapJson(counts.nameSources)) + "," +
            objectField("calling_conventions", countMapJson(counts.callingConventions)) + "," +
            objectField("signature_sources", countMapJson(counts.signatureSources)) +
            "}");
    }

    private static String parameterReturnJson(Parameter parameter) {
        return "{" +
            field("source", sourceName(parameter.getSource())) + "," +
            objectField("formal_type", dataTypeJson(parameter.getFormalDataType())) + "," +
            objectField("data_type", dataTypeJson(parameter.getDataType())) + "," +
            field("storage", parameter.getVariableStorage().getSerializationString()) +
            "}";
    }

    private static String parametersJson(Parameter[] parameters) {
        StringBuilder result = new StringBuilder();
        for (Parameter parameter : parameters) {
            if (result.length() != 0) result.append(',');
            result.append('{')
                .append(numberField("ordinal", parameter.getOrdinal())).append(',')
                .append(field("source", sourceName(parameter.getSource()))).append(',')
                .append(objectField("formal_type", dataTypeJson(parameter.getFormalDataType()))).append(',')
                .append(objectField("data_type", dataTypeJson(parameter.getDataType()))).append(',')
                .append(boolField("auto", parameter.isAutoParameter())).append(',')
                .append(boolField("forced_indirect", parameter.isForcedIndirect())).append(',')
                .append(field("storage", parameter.getVariableStorage().getSerializationString()))
                .append('}');
        }
        return result.toString();
    }

    private static String dataTypeJson(DataType type) {
        return "{" + field("path", type.getPathName()) + "," +
            numberField("length", type.getLength()) + "}";
    }

    private static String rangeArray(List<AddressRange> ranges) {
        StringBuilder result = new StringBuilder();
        for (AddressRange range : ranges) {
            if (result.length() != 0) result.append(',');
            result.append('{')
                .append(objectField("min", addressJson(range.getMinAddress()))).append(',')
                .append(objectField("max", addressJson(range.getMaxAddress())))
                .append('}');
        }
        return result.toString();
    }

    private static String sourceInfosJson(List<MemoryBlockSourceInfo> sources) {
        List<MemoryBlockSourceInfo> ordered = new ArrayList<>(sources);
        ordered.sort((left, right) -> {
            int result = ADDRESS_ORDER.compare(left.getMinAddress(), right.getMinAddress());
            if (result != 0) return result;
            result = ADDRESS_ORDER.compare(left.getMaxAddress(), right.getMaxAddress());
            if (result != 0) return result;
            AddressRange leftMapped = left.getMappedRange().orElse(null);
            AddressRange rightMapped = right.getMappedRange().orElse(null);
            if (leftMapped == null || rightMapped == null) {
                result = leftMapped == rightMapped ? 0 : (leftMapped == null ? -1 : 1);
            }
            else {
                result = compareRanges(leftMapped, rightMapped);
            }
            if (result != 0) return result;
            ByteMappingScheme leftScheme = left.getByteMappingScheme().orElse(null);
            ByteMappingScheme rightScheme = right.getByteMappingScheme().orElse(null);
            if (leftScheme == null || rightScheme == null) {
                result = leftScheme == rightScheme ? 0 : (leftScheme == null ? -1 : 1);
            }
            else {
                result = Integer.compare(leftScheme.getMappedByteCount(), rightScheme.getMappedByteCount());
                if (result == 0) {
                    result = Integer.compare(
                        leftScheme.getMappedSourceByteCount(), rightScheme.getMappedSourceByteCount());
                }
            }
            if (result != 0) return result;
            FileBytes leftFile = left.getFileBytes().orElse(null);
            FileBytes rightFile = right.getFileBytes().orElse(null);
            if (leftFile == null || rightFile == null) {
                return leftFile == rightFile ? 0 : (leftFile == null ? -1 : 1);
            }
            result = compareText(
                pathFreeFilename(leftFile.getFilename()), pathFreeFilename(rightFile.getFilename()));
            if (result != 0) return result;
            result = Long.compare(leftFile.getFileOffset(), rightFile.getFileOffset());
            if (result != 0) return result;
            result = Long.compare(leftFile.getSize(), rightFile.getSize());
            return result != 0 ? result : Long.compare(
                left.getFileBytesOffset(), right.getFileBytesOffset());
        });
        StringBuilder result = new StringBuilder();
        for (MemoryBlockSourceInfo source : ordered) {
            if (result.length() != 0) result.append(',');
            AddressRange mapped = source.getMappedRange().orElse(null);
            ByteMappingScheme scheme = source.getByteMappingScheme().orElse(null);
            FileBytes fileBytes = source.getFileBytes().orElse(null);
            result.append('{')
                .append(objectField("destination_min", addressJson(source.getMinAddress()))).append(',')
                .append(objectField("destination_max", addressJson(source.getMaxAddress()))).append(',')
                .append(numberField("length", source.getLength())).append(',')
                .append("\"mapped_range\":")
                .append(mapped == null ? "null" : rangeJson(mapped)).append(',')
                .append("\"byte_mapping\":")
                .append(byteMappingJson(scheme)).append(',')
                .append("\"file_bytes\":")
                .append(fileBytesJson(fileBytes, source.getFileBytesOffset()))
                .append('}');
        }
        return result.toString();
    }

    private static String byteMappingJson(ByteMappingScheme scheme) {
        if (scheme == null) return "null";
        return "{" +
            numberField("mapped_byte_count", scheme.getMappedByteCount()) + "," +
            numberField("mapped_source_byte_count", scheme.getMappedSourceByteCount()) +
            "}";
    }

    private static String fileBytesJson(FileBytes fileBytes, long sourceOffset) {
        if (fileBytes == null) return "null";
        return "{" +
            field("filename", pathFreeFilename(fileBytes.getFilename())) + "," +
            numberField("file_offset", fileBytes.getFileOffset()) + "," +
            numberField("size", fileBytes.getSize()) + "," +
            numberField("source_offset", sourceOffset) +
            "}";
    }

    private static String pathFreeFilename(String filename) {
        String normalized = nullToEmpty(filename).replace('\\', '/');
        int separator = normalized.lastIndexOf('/');
        return separator < 0 ? normalized : normalized.substring(separator + 1);
    }

    private static String rangeJson(AddressRange range) {
        return "{" +
            objectField("min", addressJson(range.getMinAddress())) + "," +
            objectField("max", addressJson(range.getMaxAddress())) +
            "}";
    }

    private static int compareText(String left, String right) {
        int leftIndex = 0;
        int rightIndex = 0;
        while (leftIndex < left.length() && rightIndex < right.length()) {
            int leftPoint = left.codePointAt(leftIndex);
            int rightPoint = right.codePointAt(rightIndex);
            if (leftPoint != rightPoint) return Integer.compare(leftPoint, rightPoint);
            leftIndex += Character.charCount(leftPoint);
            rightIndex += Character.charCount(rightPoint);
        }
        return Integer.compare(left.length() - leftIndex, right.length() - rightIndex);
    }

    private static int compareRanges(AddressRange left, AddressRange right) {
        int result = ADDRESS_ORDER.compare(left.getMinAddress(), right.getMinAddress());
        return result != 0 ? result : ADDRESS_ORDER.compare(
            left.getMaxAddress(), right.getMaxAddress());
    }

    private static String countMapJson(Map<String, Long> counts) {
        StringBuilder result = new StringBuilder();
        for (Map.Entry<String, Long> entry : counts.entrySet()) {
            if (result.length() != 0) result.append(',');
            result.append(json(entry.getKey())).append(':').append(entry.getValue());
        }
        return "{" + result + "}";
    }

    private static String addressJson(Address address) {
        if (address == null || Address.NO_ADDRESS.equals(address)) {
            return "{" + field("space", "NO_ADDRESS") + ",\"offset\":null}";
        }
        int width = Math.max(8, (address.getAddressSpace().getSize() + 3) / 4);
        String offset = Long.toUnsignedString(address.getOffset(), 16);
        offset = "0".repeat(Math.max(0, width - offset.length())) + offset;
        return "{" + field("space", address.getAddressSpace().getName()) + "," +
            field("offset", offset) + "}";
    }

    private static void increment(Map<String, Long> counts, String key) {
        counts.put(key, counts.getOrDefault(key, 0L) + 1);
    }

    private static String sourceName(SourceType source) {
        return source == null ? "UNKNOWN" : source.name();
    }

    private static String nullToEmpty(String value) {
        return value == null ? "" : value;
    }

    private static void writeLine(PrintWriter out, String line) {
        out.print(line);
        out.print('\n');
    }

    private static String field(String name, String value) {
        return json(name) + ":" + json(nullToEmpty(value));
    }

    private static String nullableField(String name, String value) {
        return json(name) + ":" + (value == null ? "null" : json(value));
    }

    private static String objectField(String name, String jsonObject) {
        return json(name) + ":" + jsonObject;
    }

    private static String arrayField(String name, String contents) {
        return json(name) + ":[" + contents + "]";
    }

    private static String numberField(String name, long value) {
        return json(name) + ":" + value;
    }

    private static String boolField(String name, boolean value) {
        return json(name) + ":" + value;
    }

    private static String json(String value) {
        StringBuilder result = new StringBuilder("\"");
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            switch (c) {
                case '\\': result.append("\\\\"); break;
                case '"': result.append("\\\""); break;
                case '\b': result.append("\\b"); break;
                case '\f': result.append("\\f"); break;
                case '\n': result.append("\\n"); break;
                case '\r': result.append("\\r"); break;
                case '\t': result.append("\\t"); break;
                default:
                    if (c < 0x20) result.append(String.format("\\u%04x", (int)c));
                    else result.append(c);
            }
        }
        return result.append('"').toString();
    }
}