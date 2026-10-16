//@author kaikozlov
//@category Seed
// Generic table-driven recovered-semantics applier for registered first-class targets.
// Args: <recovered_functions.jsonl> <recovered_data.jsonl>
// Rows are applied in file order; unknown addresses, unresolved type names and
// malformed rows abort the run before any mutation (preflight then apply).
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.SourceType;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class ApplyRecoveredTables extends GhidraScript {
  private static final String CATEGORY = "/CamryF33";
  private final Map<String, DataType> typeCache = new LinkedHashMap<>();

  @Override
  public void run() throws Exception {
    String[] args = getScriptArgs();
    if (args.length != 2) {
      throw new IllegalArgumentException("expected <recovered_functions.jsonl> <recovered_data.jsonl>");
    }
    List<JsonObject> fnRows = readRows(args[0]);
    List<JsonObject> dataRows = readRows(args[1]);
    preflight(fnRows, true);
    preflight(dataRows, false);
    // data rows apply first: `@ADDR` type references in function signatures
    // resolve against defined data created by this same table
    int dataApplied = 0;
    for (JsonObject row : dataRows) {
      applyData(row);
      dataApplied++;
    }
    for (JsonObject row : fnRows) {
      resolveRowTypes(row, true);
    }
    int fnApplied = 0;
    for (JsonObject row : fnRows) {
      applyFunction(row);
      fnApplied++;
    }
    println("ApplyRecoveredTables: " + fnApplied + " functions, " + dataApplied + " data rows");
  }

  private List<JsonObject> readRows(String path) throws Exception {
    List<JsonObject> rows = new ArrayList<>();
    try (BufferedReader reader = new BufferedReader(new FileReader(path))) {
      String line = reader.readLine();
      long lineNo = 1;
      while (line != null) {
        String trimmed = line.trim();
        if (!trimmed.isEmpty()) {
          try {
            rows.add(JsonParser.parseString(trimmed).getAsJsonObject());
          } catch (RuntimeException e) {
            throw new IllegalStateException("malformed row at " + path + ":" + lineNo);
          }
        }
        line = reader.readLine();
        lineNo++;
      }
    }
    return rows;
  }

  private void preflight(List<JsonObject> rows, boolean functions) {
    Map<Long, Integer> seen = new LinkedHashMap<>();
    for (JsonObject row : rows) {
      long addr = parseAddr(row, "addr");
      if (seen.put(addr, 1) != null) {
        throw new IllegalStateException("duplicate address " + hex(addr));
      }
      if (functions && getFunctionAt(toAddr(addr)) == null) {
        throw new IllegalStateException("missing function at " + hex(addr));
      }
      if (!functions && row.get("name") == null) {
        throw new IllegalStateException("data row without name at " + hex(addr));
      }
    }
  }

  private void resolveRowTypes(JsonObject row, boolean functions) {
    if (functions) {
      if (row.get("return") != null) resolve(row.get("return").getAsString());
      JsonArray params = row.getAsJsonArray("params");
      if (params != null) {
        for (JsonElement e : params) resolve(e.getAsJsonObject().get("type").getAsString());
      }
    } else {
      resolve(row.get("type").getAsString());
    }
  }

  private void applyFunction(JsonObject row) throws Exception {
    long entry = parseAddr(row, "addr");
    Function function = getFunctionAt(toAddr(entry));
    if (function == null) throw new IllegalStateException("missing function at " + hex(entry));
    JsonElement name = row.get("name");
    if (name != null && !name.isJsonNull()) function.setName(name.getAsString(), SourceType.USER_DEFINED);
    JsonElement ret = row.get("return");
    if (ret != null) {
      function.setReturnType(resolve(ret.getAsString()), SourceType.USER_DEFINED);
      List<ParameterImpl> params = new ArrayList<>();
      JsonArray paramArray = row.getAsJsonArray("params");
      if (paramArray != null) {
        for (JsonElement e : paramArray) {
          JsonObject p = e.getAsJsonObject();
          params.add(new ParameterImpl(p.get("name").getAsString(),
              resolve(p.get("type").getAsString()), currentProgram));
        }
      }
      function.replaceParameters(Function.FunctionUpdateType.DYNAMIC_STORAGE_FORMAL_PARAMS,
          true, SourceType.USER_DEFINED, params.toArray(new ParameterImpl[0]));
    }
    JsonElement comment = row.get("comment");
    if (comment != null) function.setComment(comment.getAsString());
    if (bool(row, "inline")) function.setInline(true);
    if (bool(row, "no_return")) function.setNoReturn(true);
    JsonElement convention = row.get("calling_convention");
    if (convention != null) function.setCallingConvention(convention.getAsString());
    JsonElement thunk = row.get("thunk");
    if (thunk != null) {
      long target = Long.parseLong(thunk.getAsString().substring(2), 16);
      Function targetFunction = getFunctionAt(toAddr(target));
      if (targetFunction == null) {
        throw new IllegalStateException("missing thunk target " + hex(target) + " for " + hex(entry));
      }
      function.setThunkedFunction(targetFunction);
    }
  }

  private void applyData(JsonObject row) throws Exception {
    long entry = parseAddr(row, "addr");
    Address start = toAddr(entry);
    DataType type = resolve(row.get("type").getAsString());
    Listing listing = currentProgram.getListing();
    Data existing = listing.getDefinedDataAt(start);
    if (existing == null || existing.getLength() != type.getLength()
        || !existing.getDataType().isEquivalent(type)) {
      listing.clearCodeUnits(start, start.add(type.getLength() - 1L), false);
      createData(start, type);
    }
    createLabel(start, row.get("name").getAsString(), true);
    JsonElement comment = row.get("comment");
    if (comment != null) listing.setComment(start, CodeUnit.PLATE_COMMENT, comment.getAsString());
  }

  private boolean bool(JsonObject row, String key) {
    JsonElement e = row.get(key);
    return e != null && e.getAsJsonPrimitive().isBoolean() && e.getAsBoolean();
  }

  private long parseAddr(JsonObject row, String key) {
    JsonElement e = row.get(key);
    if (e == null) throw new IllegalStateException("row missing " + key);
    String raw = e.getAsString();
    if (!raw.startsWith("0x")) throw new IllegalStateException("address must be 0x-prefixed: " + raw);
    return Long.parseLong(raw.substring(2), 16);
  }

  private String hex(long addr) { return String.format("0x%X", addr); }

  private static int[] dims(String expr) {
    java.util.regex.Matcher m =
        java.util.regex.Pattern.compile("\\[(\\d+)\\]").matcher(expr.substring(expr.indexOf('[')));
    java.util.List<Integer> out = new java.util.ArrayList<>();
    while (m.find()) out.add(Integer.parseInt(m.group(1)));
    return out.stream().mapToInt(Integer::intValue).toArray();
  }

  private DataType resolve(String expr) {
    String e = expr.trim();
    DataType cached = typeCache.get(e);
    if (cached != null) return cached;
    DataType resolved;
    if (e.endsWith("*")) {
      resolved = new PointerDataType(resolve(e.substring(0, e.length() - 1)), 4);
    } else if (e.endsWith("]") && e.indexOf('[') > 0) {
      DataType inner = resolve(e.substring(0, e.indexOf('[')));
      for (int d : dims(e)) {
        inner = new ArrayDataType(inner, d, inner.getLength());
      }
      resolved = inner;
    } else if (e.startsWith("@")) {
      Address ref = toAddr(Long.parseLong(e.substring(3), 16));
      Data data = currentProgram.getListing().getDefinedDataAt(ref);
      if (data == null) throw new IllegalStateException("no defined data at reference " + e);
      resolved = data.getDataType();
    } else {
      resolved = builtin(e);
      if (resolved == null) {
        resolved = currentProgram.getDataTypeManager().getDataType(CATEGORY + "/" + e);
      }
      if (resolved == null) {
        resolved = currentProgram.getDataTypeManager().getDataType("/" + e);
      }
      if (resolved == null) throw new IllegalStateException("unresolved type " + e);
    }
    typeCache.put(e, resolved);
    return resolved;
  }

  private DataType builtin(String name) {
    switch (name) {
      case "void": return VoidDataType.dataType;
      case "u8": return UnsignedCharDataType.dataType;
      case "u16": return UnsignedShortDataType.dataType;
      case "u32": return UnsignedIntegerDataType.dataType;
      case "u64": return UnsignedLongDataType.dataType;
      case "s8": return ByteDataType.dataType;
      case "s16": return ShortDataType.dataType;
      case "s32": return IntegerDataType.dataType;
      case "s64": return LongDataType.dataType;
      case "float": return FloatDataType.dataType;
      case "bool": return BooleanDataType.dataType;
      case "char": return CharDataType.dataType;
      default: return null;
    }
  }
}
