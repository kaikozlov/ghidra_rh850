import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.lang.Register;
import ghidra.program.model.pcode.*;
import ghidra.program.model.symbol.*;
import java.util.*;
import java.io.*;

/**
 * Read-only provenance aid for variable-index stores and call-site arguments.
 * Writes a line-oriented report to a file so a bridge timeout cannot lose the
 * result.
 *
 * Arguments: <mode: stores|calls|both> <loHex> <hiHex> <maxDepth> <outFile>
 *
 *   tools/gtarget camry-8965F3307000 script run \
 *     ghidra/scripts/investigate/TraceStoreIndexProvenance.java -- \
 *     both 0x67176 0x735E6 2 <outFile>
 *
 * stores: for every function whose entry lies in [lo,hi), print each high-pcode
 *   STORE's pointer shape, the leaf varnodes of the address expression with their
 *   defining instruction, and every compare op in the function consuming a leaf
 *   (candidate bound instruction) with address and constant.
 * calls: for every call site (any function) whose direct target lies in [lo,hi),
 *   print the shape of each argument at the call site, recursing through callers
 *   up to maxDepth for forwarded parameters.
 */
public class TraceStoreIndexProvenance extends GhidraScript {
  long lo, hi; int maxDepth = 1; String mode = "both"; PrintWriter out;
  Register gpReg, spReg, tpReg, epReg;
  Map<Long, HighFunction> cache = new HashMap<>();

  void emit(String s) { out.println(s); out.flush(); }

  String regName(Varnode v) {
    if (!v.isRegister()) return null;
    Register r = currentProgram.getRegister(v);
    return r == null ? ("r?" + v.getOffset()) : r.getName();
  }
  boolean isReg(Varnode v, Register r) { return v != null && v.isRegister() && r != null && v.getAddress().equals(r.getAddress()); }

  HighFunction hfOf(Function f) {
    HighFunction h = cache.get(f.getEntryPoint().getOffset());
    if (h != null) return h;
    DecompInterface di = new DecompInterface(); di.openProgram(currentProgram);
    DecompileResults dr = di.decompileFunction(f, 60, monitor);
    h = dr.getHighFunction();
    di.dispose();
    cache.put(f.getEntryPoint().getOffset(), h);
    return h;
  }
  boolean inRange(long a) { return a >= lo && a < hi; }

  String shape(Varnode v, int d, Set<Varnode> seen) {
    if (v == null) return "null";
    if (v.isConstant()) return String.format("K:0x%x", v.getOffset() & 0xffffffffL);
    if (d > 16 || !seen.add(v)) return "cycle";
    if (isReg(v, gpReg)) return "GP";
    if (isReg(v, spReg)) return "SP";
    if (isReg(v, epReg)) return "EP";
    if (isReg(v, tpReg)) return "TP";
    if (v.isRegister()) return "P:" + regName(v);
    if (v.isUnique()) return "u:" + Long.toHexString(v.getOffset());
    PcodeOp op = v.getDef();
    if (op == null) return v.toString();
    int c = op.getOpcode();
    if (c == PcodeOp.COPY || c == PcodeOp.CAST || c == PcodeOp.INDIRECT || c == PcodeOp.INT_ZEXT || c == PcodeOp.INT_SEXT)
      return shape(op.getInput(0), d + 1, seen);
    if (c == PcodeOp.PTRSUB) {
      Varnode a = op.getInput(0), b = op.getInput(1);
      if (a != null && a.isConstant() && (a.getOffset() & 0xffffffffL) == 0) return shape(b, d + 1, seen);
      if (a != null && a.isRegister() && !isReg(a, spReg) && b != null && b.isConstant()) return shape(a, d + 1, seen) + "+" + String.format("0x%x", b.getOffset());
      String sa = shape(a, d + 1, new HashSet<>(seen)), sb = shape(b, d + 1, new HashSet<>(seen));
      return sa + "+" + sb;
    }
    if (c == PcodeOp.INT_ADD || c == PcodeOp.INT_SUB || c == PcodeOp.INT_MULT || c == PcodeOp.INT_LEFT || c == PcodeOp.INT_AND || c == PcodeOp.INT_OR || c == PcodeOp.INT_XOR || c == PcodeOp.INT_SRIGHT || c == PcodeOp.INT_RIGHT) {
      String m = c == PcodeOp.INT_ADD ? "+" : c == PcodeOp.INT_SUB ? "-" : c == PcodeOp.INT_MULT ? "*" : c == PcodeOp.INT_LEFT ? "<<" : c == PcodeOp.INT_AND ? "&" : c == PcodeOp.INT_OR ? "|" : c == PcodeOp.INT_XOR ? "^" : c == PcodeOp.INT_SRIGHT ? ">>s" : ">>";
      return "(" + shape(op.getInput(0), d + 1, new HashSet<>(seen)) + m + shape(op.getInput(1), d + 1, new HashSet<>(seen)) + ")";
    }
    if (c == PcodeOp.PTRADD) return "(" + shape(op.getInput(0), d + 1, new HashSet<>(seen)) + "+[" + shape(op.getInput(1), d + 1, new HashSet<>(seen)) + "]*" + shape(op.getInput(2), d + 1, new HashSet<>(seen)) + ")";
    if (c == PcodeOp.MULTIEQUAL) {
      TreeSet<String> s = new TreeSet<>();
      for (int i = 0; i < op.getNumInputs(); i++) s.add(shape(op.getInput(i), d + 1, new HashSet<>(seen)));
      return "phi{" + String.join("/", s) + "}";
    }
    if (c == PcodeOp.LOAD) return "LD[" + shape(op.getInput(1), d + 1, new HashSet<>(seen)) + "]";
    if (c == PcodeOp.CALL || c == PcodeOp.CALLIND || c == PcodeOp.CALLOTHER) return "CALLRET";
    if (c == PcodeOp.SUBPIECE) return shape(op.getInput(0), d + 1, seen) + ".sub";
    return PcodeOp.getMnemonic(c).toLowerCase();
  }

  void leaves(Varnode v, int d, Set<Varnode> seen, List<Varnode> out) {
    if (v == null || d > 20 || !seen.add(v)) return;
    if (v.isConstant()) return;
    if (isReg(v, gpReg) || isReg(v, spReg) || isReg(v, epReg) || isReg(v, tpReg)) return;
    PcodeOp op = v.getDef();
    if (op == null) { out.add(v); return; }
    int c = op.getOpcode();
    if (c == PcodeOp.COPY || c == PcodeOp.CAST || c == PcodeOp.INDIRECT || c == PcodeOp.INT_ZEXT || c == PcodeOp.INT_SEXT || c == PcodeOp.SUBPIECE) { leaves(op.getInput(0), d + 1, seen, out); return; }
    if (c == PcodeOp.MULTIEQUAL) { for (int i = 0; i < op.getNumInputs(); i++) leaves(op.getInput(i), d + 1, new HashSet<>(seen), out); return; }
    if (c == PcodeOp.LOAD || c == PcodeOp.CALL || c == PcodeOp.CALLIND || c == PcodeOp.CALLOTHER) { out.add(v); return; }
    if (c == PcodeOp.PTRSUB || c == PcodeOp.PTRADD || c == PcodeOp.INT_ADD || c == PcodeOp.INT_SUB || c == PcodeOp.INT_MULT || c == PcodeOp.INT_LEFT || c == PcodeOp.INT_AND || c == PcodeOp.INT_OR || c == PcodeOp.INT_XOR || c == PcodeOp.INT_SRIGHT || c == PcodeOp.INT_RIGHT) {
      for (int i = 0; i < op.getNumInputs(); i++) leaves(op.getInput(i), d + 1, new HashSet<>(seen), out);
      return;
    }
    out.add(v);
  }
  boolean derives(Varnode w, Varnode x, int d, Set<Varnode> seen) {
    if (w == null || d > 12 || !seen.add(w)) return false;
    if (w.equals(x)) return true;
    if (w.isConstant()) return false;
    PcodeOp op = w.getDef();
    if (op == null) return false;
    int c = op.getOpcode();
    if (c == PcodeOp.COPY || c == PcodeOp.CAST || c == PcodeOp.INT_ZEXT || c == PcodeOp.INT_SEXT || c == PcodeOp.SUBPIECE) return derives(op.getInput(0), x, d + 1, seen);
    return false;
  }
  String addrOf(PcodeOp op) {
    if (op.getSeqnum() == null) return "?";
    return String.format("%06x", op.getSeqnum().getTarget().getOffset());
  }
  String insText(PcodeOp op) {
    if (op.getSeqnum() == null) return "";
    Instruction ins = getInstructionAt(op.getSeqnum().getTarget());
    return ins == null ? "" : ins.toString().replaceAll("\\s+", " ").trim();
  }
  Set<String> cmpMnemonics = new HashSet<>(Arrays.asList("INT_LESS", "INT_LESSEQUAL", "INT_SLESS", "INT_SLESSEQUAL", "INT_EQUAL", "INT_NOTEQUAL"));


  String exprOf(Varnode vv, int d, Set<Varnode> seen) {
    Varnode v = vv;
    if (v == null) return "null";
    if (v.isConstant()) return String.format("0x%x", v.getOffset() & 0xffffffffL);
    if (v.isRegister()) return regName(v);
    if (v.getAddress().isStackAddress()) return "stk";
    if (d > 14 || !seen.add(v)) return v.toString();
    PcodeOp op = v.getDef();
    if (op == null) return v.toString();
    StringBuilder b = new StringBuilder(PcodeOp.getMnemonic(op.getOpcode()).substring(4).toLowerCase()).append('(');
    for (int i = 0; i < op.getNumInputs(); i++) { if (i > 0) b.append(','); b.append(exprOf(op.getInput(i), d + 1, new HashSet<>(seen))); }
    return b.append(')').append('@').append(addrOf(op)).toString();
  }
  boolean sameHigh(Varnode a, Varnode b) {
    if (a == null || b == null) return false;
    HighVariable ha = a.getHigh(), hb = b.getHigh();
    if (ha != null && hb != null) return ha == hb;
    return a.equals(b);
  }
  String highInfo(Varnode v) {
    HighVariable h = v.getHigh();
    if (h == null) return "nohigh";
    String kind = (h instanceof HighParam) ? "PARAM" : (h instanceof HighLocal) ? "local" : "var";
    StringBuilder defs = new StringBuilder();
    for (Varnode inst : h.getInstances()) {
      PcodeOp d = inst.getDef();
      if (d == null) continue;
      String s = PcodeOp.getMnemonic(d.getOpcode()) + "@" + addrOf(d);
      if (defs.indexOf(s) < 0) { if (defs.length() > 0) defs.append(';'); defs.append(s); }
    }
    return kind + "[" + defs + "]";
  }
  public void run() throws Exception {
    String[] a = getScriptArgs();
    mode = a[0]; lo = Long.decode(a[1]); hi = Long.decode(a[2]);
    if (a.length > 3) maxDepth = Integer.decode(a[3]);
    out = new PrintWriter(new BufferedWriter(new FileWriter(a[4])));
    gpReg = currentProgram.getRegister("gp"); spReg = currentProgram.getCompilerSpec().getStackPointer();
    epReg = currentProgram.getRegister("ep"); tpReg = currentProgram.getRegister("tp");
    FunctionManager fm = currentProgram.getFunctionManager();
    List<Function> inRange = new ArrayList<>();
    FunctionIterator fi = fm.getFunctions(true);
    while (fi.hasNext()) { Function f = fi.next(); if (inRange(f.getEntryPoint().getOffset())) inRange.add(f); }
    emit(String.format("RANGE|lo=%06x|hi=%06x|functions=%d|maxDepth=%d|mode=%s", lo, hi, inRange.size(), maxDepth, mode));

    if (mode.equals("stores") || mode.equals("both")) {
      for (Function f : inRange) {
        HighFunction hf = hfOf(f);
        if (hf == null) { emit("NOHF|" + f.getEntryPoint()); continue; }
        List<PcodeOpAST> ops = new ArrayList<>();
        Iterator<PcodeOpAST> it = hf.getPcodeOps();
        while (it.hasNext()) ops.add(it.next());
        for (PcodeOpAST op : ops) {
          if (op.getOpcode() != PcodeOp.STORE) continue;
          Varnode ptr = op.getInput(1);
          String sh = shape(ptr, 0, new HashSet<>());
          List<Varnode> lv = new ArrayList<>();
          leaves(ptr, 0, new HashSet<>(), lv);
          StringBuilder lb = new StringBuilder();
          for (Varnode x : lv) {
            if (lb.length() > 0) lb.append(';');
            String s;
            if (x.isRegister()) s = "P:" + regName(x);
            else if (x.isUnique()) s = "u:" + Long.toHexString(x.getOffset());
            else s = x.toString();
            PcodeOp def = x.getDef();
            if (def != null) s += "<=" + PcodeOp.getMnemonic(def.getOpcode()) + "@" + addrOf(def) + "[" + insText(def) + "]";
            lb.append(s);
          }
          StringBuilder cb = new StringBuilder();
          for (PcodeOpAST c : ops) {
            if (!cmpMnemonics.contains(PcodeOp.getMnemonic(c.getOpcode()))) continue;
            for (int i = 0; i < c.getNumInputs() && i < 2; i++) {
              Varnode in = c.getInput(i);
              if (in == null || in.isConstant()) continue;
              boolean hit = false;
              for (Varnode x : lv) if (x.isRegister() && sameHigh(in, x)) { hit = true; break; }
              if (!hit) continue;
              Varnode k = (i == 0) ? c.getInput(1) : c.getInput(0);
              String ks = (k != null && k.isConstant()) ? String.format("0x%x", k.getOffset() & 0xffffffffL) : (k == null ? "" : shape(k, 0, new HashSet<>()));
              String br = "";
              Varnode res = c.getOutput();
              if (res != null) {
                Iterator<PcodeOp> ui = res.getDescendants();
                while (ui.hasNext()) { PcodeOp u = ui.next(); if (u.getOpcode() == PcodeOp.CBRANCH) { br = "->br@" + addrOf(u); break; } }
              }
              String e = PcodeOp.getMnemonic(c.getOpcode()) + "@" + addrOf(c) + " " + ks + br + " [" + insText(c) + "]";
              if (cb.indexOf(e) < 0) { if (cb.length() > 0) cb.append(';'); cb.append(e); }
            }
          }
          StringBuilder hb = new StringBuilder();
          for (Varnode x : lv) { if (x.isRegister()) { if (hb.length() > 0) hb.append(';'); hb.append(regName(x)).append(':').append(highInfo(x)); } }
          emit(String.format("STORE|%s|%s|%s|size=%d|shape=%s|leaves=%s|highs=%s|cmps=%s|expr=%s", f.getEntryPoint(), addrOf(op), f.getName(), op.getInput(2).getSize(), sh, lb, hb, cb, exprOf(ptr, 0, new HashSet<>())));
        }
      }
    }

    if (mode.equals("calls") || mode.equals("both")) {
      TreeMap<Long, Function> byEntry = new TreeMap<>();
      for (Function f : inRange) byEntry.put(f.getEntryPoint().getOffset(), f);
      Map<Long, Integer> depthOf = new HashMap<>();
      ArrayDeque<Function> q = new ArrayDeque<>();
      for (Function f : inRange) { depthOf.put(f.getEntryPoint().getOffset(), 0); q.add(f); }
      while (!q.isEmpty()) {
        Function f = q.remove(); int d = depthOf.get(f.getEntryPoint().getOffset());
        if (d >= maxDepth) continue;
        for (Function c : f.getCallingFunctions(monitor)) {
          if (c == null || c.isExternal()) continue;
          long k = c.getEntryPoint().getOffset();
          if (!depthOf.containsKey(k)) { depthOf.put(k, d + 1); q.add(c); }
        }
      }
      emit("CALLERCONE|functions=" + depthOf.size());
      int n = 0;
      for (Long k : new TreeSet<>(depthOf.keySet())) {
        Function caller = fm.getFunctionAt(toAddr(k));
        if (caller == null) continue;
        HighFunction hf = hfOf(caller);
        if (hf == null) { emit("NOHF|" + caller.getEntryPoint()); continue; }
        Iterator<PcodeOpAST> it = hf.getPcodeOps();
        while (it.hasNext()) {
          PcodeOpAST op = it.next();
          int c = op.getOpcode();
          if (c != PcodeOp.CALL && c != PcodeOp.CALLIND) continue;
          Varnode tgt = op.getInput(op.getNumInputs() - 1);
          if (tgt == null || !tgt.isConstant()) continue;
          long te = tgt.getOffset() & 0xffffffffL;
          if (!byEntry.containsKey(te)) continue;
          StringBuilder args = new StringBuilder();
          for (int i = 0; i < op.getNumInputs() - 1; i++) {
            if (i > 0) args.append(',');
            args.append(shape(op.getInput(i), 0, new HashSet<>()));
          }
          emit(String.format("CALLSITE|%s|%s|%s|%s|depth=%d|nargs=%d|%s", caller.getEntryPoint(), addrOf(op), caller.getName(), byEntry.get(te).getEntryPoint(), depthOf.get(k), op.getNumInputs() - 1, args));
          n++;
        }
      }
      emit("CALLSITES|" + n);
    }
    emit("DONE");
    out.close();
  }
}
