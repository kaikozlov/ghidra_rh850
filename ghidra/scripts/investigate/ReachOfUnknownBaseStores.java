//@category Analysis
// Reach filter for the STORE population whose pointer range the
// AuditComputedStoreTargets resolver cannot bound (the TriageUnknownStoreBases
// set). Read-only; writes reach.csv, reach-unresolved-bases.csv and
// reach-report.md into --out (default: the Camry route2 reach directory).
//
// For every store at a constant base plus a variable index, and every store
// through a register pointer plus a variable index whose base register is
// defined in the same function as a constant, sp+const, gp+const or tp+const,
// the script computes a saturating reach interval from coarse index bounds
// (operand widths, sign extension, masks, shifts, strides), intersects it with
// the control-relevant target set, and classifies each REACH store by tracing
// the index to its origin (loop counter, parameter, loaded data).
//
// Usage: ... -- [--out DIR] [--only 0xA,0xB] [--rows] [--dump]
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.lang.Register;
import ghidra.program.model.pcode.*;
import ghidra.program.model.symbol.FlowType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;
import ghidra.program.model.scalar.Scalar;
import java.util.*;
import java.io.*;

public class ReachOfUnknownBaseStores extends GhidraScript {
  static final long U32 = 0xffffffffL;
  static final long APP_BASE = 0x20000L;
  // Context constants, observed in the image: boot GP/TP at 0x1F2/0x1F8,
  // application GP/TP at 0x715CC/0x715D2 (reset SP 0xFEBE8000 at 0x1EC,
  // application SP 0xFEBE2000 at 0x715D8).
  static final long APP_GP = 0xFEBEB800L, APP_TP = 0x23DFCL;
  static final long BOOT_GP = 0xFEBF9800L, BOOT_TP = 0x869CL;
  // Register bank offsets of ghidra/ghidra_v850/data/languages/v850_common.sinc.
  static final long OFF_GP = 0x10, OFF_TP = 0x14, OFF_EP = 0x78, OFF_R0 = 0x1080;
  static final long[] ARG_OFFS = {0x18, 0x1c, 0x20, 0x24, 0x28, 0x2c}; // r6..r11
  static final long[] HOOKS = {0xFEBF117CL, 0xFEBF1180L, 0xFEBF1194L, 0xFEBF1198L,
      0xFEBF131CL, 0xFEBF1320L, 0xFEBF1324L, 0xFEBE5628L, 0xFEBF0FD0L, 0xFEBF6B04L};
  static final long TAIL_LO = 0xFEBFF9F0L, TAIL_HI = 0xFEBFFBFBL;
  static final long RWX_LO = 0xFEBF7C00L, RWX_HI = 0xFEBFFBFFL;
  static final long[] STACK_TOPS = {0xFEBE2000L, 0xFEBE0800L, 0xFEBE1000L, 0xFEBE1800L, 0xFEBE2800L};
  static final long STACK_WIN = 512;
  static final long RAM_LO = 0xFEBE0000L, RAM_HI = 0xFEBFFFFFL;
  static final long VEC_LO = 0x20000L, VEC_HI = 0x20880L;
  // Diagnostic/transport/crypto entries driven directly by the prior dynamic
  // campaigns (fuzz_camry_f33_dcm_handlers.py, fuzz_camry_f33_cantp_ingress.py).
  static final long[] KNOWN_ENTRIES = {0x922AAL, 0x95978L, 0x97AE4L, 0x8B632L, 0x962F2L, 0x965C0L,
      0x7B894L, 0x8B872L, 0x697F4L, 0x69BD8L, 0x69C58L, 0x7A57AL};
  static final Set<String> CONDS = new HashSet<>(Arrays.asList("v", "nv", "c", "nc", "e", "ne",
      "nh", "h", "n", "p", "r", "sa", "lt", "ge", "le", "gt"));
  static final Set<String> FLAG_WRITERS = new HashSet<>(Arrays.asList("add", "addi", "sub", "subr",
      "cmp", "tst", "mul", "mulu", "mulh", "mulhi", "divh", "divhu", "div", "divu", "divq", "divqu",
      "shl", "shr", "sar", "satadd", "satsub", "abs", "neg", "inc", "dec", "clr1", "set1", "not1",
      "tst1", "bins", "binsr", "sat", "ldsr"));
  static final Set<Integer> CMP_OPS = new HashSet<>(Arrays.asList(PcodeOp.INT_EQUAL,
      PcodeOp.INT_NOTEQUAL, PcodeOp.INT_SLESS, PcodeOp.INT_SLESSEQUAL, PcodeOp.INT_LESS,
      PcodeOp.INT_LESSEQUAL));
  static final Set<Integer> BOOL_OPS = new HashSet<>(Arrays.asList(PcodeOp.BOOL_NEGATE,
      PcodeOp.BOOL_XOR, PcodeOp.BOOL_AND, PcodeOp.BOOL_OR, PcodeOp.INT_CARRY, PcodeOp.INT_SCARRY,
      PcodeOp.INT_SBORROW));

  Register spReg, gpReg, tpReg, epReg, r0Reg;
  long spOff;
  File outDir;
  boolean printRows, dump;
  Set<Long> only = null;

  // ---------------------------------------------------------------- range
  static final class Rg {
    long lo, hi; boolean open;
    Rg(long l, long h, boolean o) { lo = l; hi = h; open = o; }
    boolean ok() { return lo <= hi; }
    long span() { return hi - lo; }
    static Rg unk(int bytes) {
      if (bytes >= 4) return new Rg(0, U32, true);
      return new Rg(0, (1L << (8 * bytes)) - 1, false);
    }
    static Rg cst(long v) { return new Rg(v, v, false); }
    Rg copy() { return new Rg(lo, hi, open); }
    Rg hull(Rg o) { return new Rg(Math.min(lo, o.lo), Math.max(hi, o.hi), open || o.open); }
    Rg inter(Rg o) { return new Rg(Math.max(lo, o.lo), Math.min(hi, o.hi), open && o.open); }
    boolean same(Rg o) { return lo == o.lo && hi == o.hi; }
    Rg shift(long k) { return new Rg(lo + k, hi + k, open); }
  }

  boolean isGp(Varnode v) { return v.isRegister() && v.getSize() >= 4 && v.getOffset() == OFF_GP; }
  boolean isTp(Varnode v) { return v.isRegister() && v.getSize() >= 4 && v.getOffset() == OFF_TP; }
  boolean isSp(Varnode v) { return v.isRegister() && v.getAddress().equals(spReg.getAddress()); }
  boolean isR0(Varnode v) { return v.isRegister() && v.getOffset() == OFF_R0; }
  boolean isEp(Varnode v) { return v.isRegister() && v.getSize() == 4 && v.getOffset() == OFF_EP; }

  Varnode strip(Varnode v) {
    int d = 0;
    while (v != null && !v.isConstant() && d++ < 32) {
      PcodeOp op = v.getDef();
      if (op == null || op.getNumInputs() == 0) break;
      int c = op.getOpcode();
      if (c == PcodeOp.COPY || c == PcodeOp.CAST || c == PcodeOp.INDIRECT) v = op.getInput(0); else break;
    }
    return v;
  }

  Rg addR(Rg a, Rg b) { return new Rg(a.lo + b.lo, a.hi + b.hi, a.open || b.open); }
  Rg subR(Rg a, Rg b) { return new Rg(a.lo - b.hi, a.hi - b.lo, a.open || b.open); }
  Rg mulR(Rg a, Rg b) {
    long[] p = {a.lo * b.lo, a.lo * b.hi, a.hi * b.lo, a.hi * b.hi};
    long mn = p[0], mx = p[0];
    for (long q : p) { mn = Math.min(mn, q); mx = Math.max(mx, q); }
    boolean open = a.open || b.open;
    if (a.lo == a.hi && !a.open) open = b.open;
    if (b.lo == b.hi && !b.open) open = a.open;
    return new Rg(mn, mx, open);
  }
  static long fill(long x) { long m = 0; while (m < x) m = (m << 1) | 1; return m; }

  // Coarse unsigned/signed range of an integer varnode. "open" means the range
  // comes from the 32-bit default rather than from a width, mask or constant.
  Rg rng(Varnode v, Map<Varnode, Rg> ov, Set<Varnode> seen, int d, FC fc) {
    if (v == null) return Rg.unk(4);
    Rg o = ov.get(v);
    if (o != null) return o;
    if (v.isConstant()) return Rg.cst(v.getOffset() & U32);
    if (isGp(v) && fc.gpKnown) return Rg.cst(fc.gp);
    if (isTp(v) && fc.tpKnown) return Rg.cst(fc.tp);
    if (isR0(v)) return Rg.cst(0);
    if (d > 48 || !seen.add(v)) return Rg.unk(v.getSize());
    try {
      PcodeOp op = v.getDef();
      if (op == null) return Rg.unk(v.getSize());
      int c = op.getOpcode();
      switch (c) {
        case PcodeOp.COPY: case PcodeOp.CAST: case PcodeOp.INDIRECT:
          return rng(op.getInput(0), ov, seen, d + 1, fc);
        case PcodeOp.INT_ZEXT: {
          Varnode in = op.getInput(0);
          Rg a = rng(in, ov, seen, d + 1, fc);
          long m = (1L << (8 * (long) in.getSize())) - 1;
          if (a.lo < 0 || a.hi > m) return new Rg(0, m, false);
          return new Rg(a.lo, a.hi, false);
        }
        case PcodeOp.INT_SEXT: {
          Varnode in = op.getInput(0);
          int bits = 8 * in.getSize();
          Rg a = rng(in, ov, seen, d + 1, fc);
          long half = 1L << (bits - 1), mod = 1L << bits;
          if (a.hi < half) return new Rg(a.lo, a.hi, false);
          if (a.lo >= half && a.hi < mod) return new Rg(a.lo - mod, a.hi - mod, false);
          if (a.lo >= mod) return new Rg(a.lo, a.hi, false);
          return new Rg(-half, half - 1, false);
        }
        case PcodeOp.SUBPIECE: {
          Varnode in = op.getInput(0), k = op.getInput(1);
          if (v.getSize() >= 4 && k.isConstant() && k.getOffset() == 0) return rng(in, ov, seen, d + 1, fc);
          if (in.isConstant()) {
            long sh = 8 * (k.isConstant() ? k.getOffset() : 0);
            long val = ((in.getOffset() >>> sh)) & ((1L << (8 * (long) v.getSize())) - 1);
            return Rg.cst(val);
          }
          return new Rg(0, (1L << (8 * (long) v.getSize())) - 1, false);
        }
        case PcodeOp.PIECE: {
          Rg h = rng(op.getInput(0), ov, new HashSet<>(seen), d + 1, fc);
          if (h.lo == 0 && h.hi == 0) return rng(op.getInput(1), ov, seen, d + 1, fc);
          return Rg.unk(v.getSize());
        }
        case PcodeOp.INT_ADD:
          return addR(rng(op.getInput(0), ov, new HashSet<>(seen), d + 1, fc),
              rng(op.getInput(1), ov, new HashSet<>(seen), d + 1, fc));
        case PcodeOp.INT_SUB:
          return subR(rng(op.getInput(0), ov, new HashSet<>(seen), d + 1, fc),
              rng(op.getInput(1), ov, new HashSet<>(seen), d + 1, fc));
        case PcodeOp.INT_MULT:
          return mulR(rng(op.getInput(0), ov, new HashSet<>(seen), d + 1, fc),
              rng(op.getInput(1), ov, new HashSet<>(seen), d + 1, fc));
        case PcodeOp.INT_LEFT: {
          Varnode k = op.getInput(1);
          if (!k.isConstant()) return Rg.unk(v.getSize());
          int s = (int) (k.getOffset() & 31);
          Rg a = rng(op.getInput(0), ov, seen, d + 1, fc);
          if (a.lo < 0 || (a.hi << s) > U32) return new Rg(0, U32, true);
          return new Rg(a.lo << s, a.hi << s, a.open);
        }
        case PcodeOp.INT_RIGHT: {
          Varnode k = op.getInput(1);
          if (!k.isConstant()) return Rg.unk(v.getSize());
          int s = (int) (k.getOffset() & 31);
          Rg a = rng(op.getInput(0), ov, seen, d + 1, fc);
          if (a.lo < 0) return new Rg(0, U32 >>> s, false);
          return new Rg(a.lo >>> s, Math.min(a.hi >>> s, U32 >>> s), false);
        }
        case PcodeOp.INT_SRIGHT: {
          Varnode k = op.getInput(1);
          if (!k.isConstant()) return Rg.unk(v.getSize());
          int s = (int) (k.getOffset() & 31);
          Rg a = rng(op.getInput(0), ov, seen, d + 1, fc);
          long half = 1L << 31;
          if (a.lo < half && a.hi >= half) return new Rg((-half) >> s, (half - 1) >> s, false);
          long sl = a.lo >= half ? a.lo - (1L << 32) : a.lo;
          long sh = a.hi >= half ? a.hi - (1L << 32) : a.hi;
          return new Rg(sl >> s, sh >> s, false);
        }
        case PcodeOp.INT_AND: {
          Varnode x = op.getInput(0), y = op.getInput(1);
          if (y.isConstant() || x.isConstant()) {
            Varnode cv = y.isConstant() ? y : x, vv = y.isConstant() ? x : y;
            long k = cv.getOffset() & U32;
            Rg a = rng(vv, ov, seen, d + 1, fc);
            return new Rg(0, a.lo >= 0 ? Math.min(k, a.hi) : k, false);
          }
          Rg a = rng(x, ov, new HashSet<>(seen), d + 1, fc), b = rng(y, ov, new HashSet<>(seen), d + 1, fc);
          if (a.lo >= 0 && b.lo >= 0) return new Rg(0, Math.min(a.hi, b.hi), a.open || b.open);
          return Rg.unk(v.getSize());
        }
        case PcodeOp.INT_OR: {
          Varnode x = op.getInput(0), y = op.getInput(1);
          if (y.isConstant() || x.isConstant()) {
            Varnode cv = y.isConstant() ? y : x, vv = y.isConstant() ? x : y;
            long k = cv.getOffset() & U32;
            Rg a = rng(vv, ov, seen, d + 1, fc);
            if (a.lo < 0) return Rg.unk(v.getSize());
            return new Rg(k, Math.min(U32, fill(a.hi) | fill(k)), a.open);
          }
          return Rg.unk(v.getSize());
        }
        case PcodeOp.INT_NEGATE: {
          Rg a = rng(op.getInput(0), ov, seen, d + 1, fc);
          return new Rg(-a.hi, -a.lo, a.open);
        }
        case PcodeOp.INT_DIV: case PcodeOp.INT_SDIV: {
          Varnode k = op.getInput(1);
          if (!k.isConstant()) return Rg.unk(v.getSize());
          long kk = k.getOffset() & U32;
          if (kk == 0 || kk > 0x7fffffffL) return Rg.unk(v.getSize());
          Rg a = rng(op.getInput(0), ov, seen, d + 1, fc);
          if (a.lo < 0) return Rg.unk(v.getSize());
          return new Rg(a.lo / kk, a.hi / kk, a.open);
        }
        case PcodeOp.INT_REM: {
          Varnode k = op.getInput(1);
          if (!k.isConstant()) return Rg.unk(v.getSize());
          long kk = k.getOffset() & U32;
          if (kk == 0 || kk > 0x7fffffffL) return Rg.unk(v.getSize());
          Rg a = rng(op.getInput(0), ov, seen, d + 1, fc);
          if (a.lo < 0) return new Rg(-(kk - 1), kk - 1, false);
          return new Rg(0, kk - 1, false);
        }
        case PcodeOp.INT_SREM: {
          Varnode k = op.getInput(1);
          if (!k.isConstant()) return Rg.unk(v.getSize());
          long kk = Math.abs(k.getOffset() & U32);
          if (kk == 0 || kk > 0x7fffffffL) return Rg.unk(v.getSize());
          return new Rg(-(kk - 1), kk - 1, false);
        }
        case PcodeOp.MULTIEQUAL: {
          Rg out = null;
          for (int i = 0; i < op.getNumInputs(); i++) {
            Rg q = rng(op.getInput(i), ov, new HashSet<>(seen), d + 1, fc);
            out = out == null ? q : out.hull(q);
          }
          return out == null ? Rg.unk(v.getSize()) : out;
        }
        case PcodeOp.PTRSUB: {
          Varnode a = op.getInput(0), b = op.getInput(1);
          Rg ra = rng(a, ov, new HashSet<>(seen), d + 1, fc);
          Rg rb = rng(b, ov, new HashSet<>(seen), d + 1, fc);
          if (ra.lo == 0 && ra.hi == 0) return rb;
          return subR(ra, rb);
        }
        case PcodeOp.PTRADD: {
          Rg p = rng(op.getInput(0), ov, new HashSet<>(seen), d + 1, fc);
          Rg i = rng(op.getInput(1), ov, new HashSet<>(seen), d + 1, fc);
          Rg s = rng(op.getInput(2), ov, new HashSet<>(seen), d + 1, fc);
          return addR(p, mulR(i, s));
        }
        default: break;
      }
      if (BOOL_OPS.contains(c) || CMP_OPS.contains(c)) return new Rg(0, 1, false);
      return Rg.unk(v.getSize());
    } finally {
      seen.remove(v);
    }
  }

  // ------------------------------------------------------- expression flatten
  static final class Term { Varnode v; long scale; Term(Varnode n, long s) { v = n; scale = s; } }
  static final class Expr {
    long konst; long spScale; boolean usedGp, usedTp;
    List<Term> terms = new ArrayList<>();
  }

  void flat(Varnode v, long scale, Expr e, int d, FC fc) {
    if (v == null || d > 40) return;
    v = strip(v);
    if (v.isConstant()) { e.konst += scale * (v.getOffset() & U32); return; }
    if (isGp(v) && fc.gpKnown) { e.konst += scale * fc.gp; e.usedGp = true; return; }
    if (isTp(v) && fc.tpKnown) { e.konst += scale * fc.tp; e.usedTp = true; return; }
    if (isR0(v)) return;
    if (isSp(v)) { e.spScale += scale; return; }
    PcodeOp op = v.getDef();
    if (op == null) { e.terms.add(new Term(v, scale)); return; }
    int c = op.getOpcode();
    Varnode a = op.getInput(0), b = op.getNumInputs() > 1 ? op.getInput(1) : null;
    switch (c) {
      case PcodeOp.INT_ADD: flat(a, scale, e, d + 1, fc); flat(b, scale, e, d + 1, fc); return;
      case PcodeOp.INT_SUB:
        flat(a, scale, e, d + 1, fc);
        if (b.isConstant()) e.konst -= scale * (b.getOffset() & U32); else flat(b, -scale, e, d + 1, fc);
        return;
      case PcodeOp.PTRSUB:
        if (a.isConstant() && (a.getOffset() & U32) == 0) { flat(b, scale, e, d + 1, fc); return; }
        flat(a, scale, e, d + 1, fc);
        if (b.isConstant()) e.konst -= scale * (b.getOffset() & U32); else flat(b, -scale, e, d + 1, fc);
        return;
      case PcodeOp.PTRADD:
        flat(a, scale, e, d + 1, fc);
        if (op.getInput(2).isConstant()) flat(b, scale * (op.getInput(2).getOffset() & U32), e, d + 1, fc);
        else e.terms.add(new Term(b, scale));
        return;
      case PcodeOp.INT_MULT:
        if (a.isConstant()) flat(b, scale * (a.getOffset() & U32), e, d + 1, fc);
        else if (b.isConstant()) flat(a, scale * (b.getOffset() & U32), e, d + 1, fc);
        else e.terms.add(new Term(v, scale));
        return;
      case PcodeOp.INT_LEFT:
        if (b.isConstant()) flat(a, scale << (int) (b.getOffset() & 31), e, d + 1, fc);
        else e.terms.add(new Term(v, scale));
        return;
      default: e.terms.add(new Term(v, scale));
    }
  }

  // index offset range = sum over terms of scale * range
  static final class Idx { long min, max; boolean open; }
  Idx idxRange(List<Term> terms, Map<Varnode, Rg> ov, FC fc) {
    Idx r = new Idx();
    for (Term t : terms) {
      Rg q = rng(t.v, ov, new HashSet<>(), 0, fc);
      long p1 = t.scale * q.lo, p2 = t.scale * q.hi;
      r.min += Math.min(p1, p2);
      r.max += Math.max(p1, p2);
      r.open |= q.open;
    }
    return r;
  }

  // ------------------------------------------------------------ base resolver
  static final class Base { String kind; long lo, hi; boolean gp, tp, sp; String how; }
  Base constBase(long v, String how) { Base b = new Base(); b.kind = "const"; b.lo = b.hi = v & U32; b.how = how; return b; }
  Base shiftBase(Base b, long k, String how) {
    if (b == null) return null;
    Base n = new Base(); n.kind = b.kind; n.lo = (b.lo + k) & U32; n.hi = (b.hi + k) & U32; n.gp = b.gp; n.tp = b.tp; n.sp = b.sp;
    n.how = b.how + (k == 0 ? "" : String.format("%+d@", k)) + how;
    return n;
  }
  String pcOf(PcodeOp op) {
    if (op == null || op.getSeqnum() == null) return "?";
    Instruction i = getInstructionContaining(op.getSeqnum().getTarget());
    return String.format("%s%s", op.getSeqnum().getTarget(), i == null ? "" : ":" + i.getMnemonicString());
  }
  Base resolveBase(Varnode x, FC fc) { return resolveBase(x, fc, 0); }
  // depth-bounded: loop phis (P = phi(init, P + c)) are cyclic in the def graph
  Base resolveBase(Varnode x, FC fc, int depth) {
    x = strip(x);
    if (x == null || depth > 24) return null;
    if (x.isConstant()) return constBase(x.getOffset(), "const");
    if (isGp(x)) { if (!fc.gpKnown) return null; Base b = constBase(fc.gp, "gp"); b.gp = true; b.kind = "gp+const"; return b; }
    if (isTp(x)) { if (!fc.tpKnown) return null; Base b = constBase(fc.tp, "tp"); b.tp = true; b.kind = "tp+const"; return b; }
    if (isR0(x)) return constBase(0, "r0");
    if (isSp(x)) { Base b = new Base(); b.kind = "sp+const"; b.sp = true; b.how = "sp"; return b; }
    PcodeOp op = x.getDef();
    if (op == null) return null;
    int c = op.getOpcode();
    Varnode a = op.getInput(0), b = op.getNumInputs() > 1 ? op.getInput(1) : null;
    switch (c) {
      case PcodeOp.INT_ADD:
        if (b.isConstant()) return shiftBase(resolveBase(a, fc, depth + 1), b.getOffset() & U32, pcOf(op));
        if (a.isConstant()) return shiftBase(resolveBase(b, fc, depth + 1), a.getOffset() & U32, pcOf(op));
        return null;
      case PcodeOp.INT_SUB:
        if (b.isConstant()) return shiftBase(resolveBase(a, fc, depth + 1), -(b.getOffset() & U32), pcOf(op));
        return null;
      case PcodeOp.PTRSUB:
        if (a.isConstant() && (a.getOffset() & U32) == 0) return constBase(b.getOffset(), pcOf(op));
        if (b.isConstant()) return shiftBase(resolveBase(a, fc, depth + 1), -(b.getOffset() & U32), pcOf(op));
        return null;
      case PcodeOp.PTRADD:
        if (op.getInput(2).isConstant() && b.isConstant())
          return shiftBase(resolveBase(a, fc, depth + 1), (b.getOffset() & U32) * (op.getInput(2).getOffset() & U32), pcOf(op));
        return null;
      case PcodeOp.INT_MULT: case PcodeOp.INT_LEFT: {
        long k;
        if (c == PcodeOp.INT_LEFT) k = b.isConstant() ? 1L << (int) (b.getOffset() & 31) : -1;
        else k = a.isConstant() ? a.getOffset() : (b.isConstant() ? b.getOffset() : -1);
        if (k < 0 || k > 0x10000L) return null;
        Base r = resolveBase(a, fc, depth + 1);
        if (r == null || r.sp) return null;
        Base n = new Base(); n.kind = r.kind; n.lo = (r.lo * k) & U32; n.hi = (r.hi * k) & U32; n.gp = r.gp; n.tp = r.tp; n.how = r.how + "*" + k;
        return n;
      }
      case PcodeOp.MULTIEQUAL: {
        Base n = new Base(); boolean sp = false, first = true; long lo = Long.MAX_VALUE, hi = Long.MIN_VALUE;
        for (int i = 0; i < op.getNumInputs(); i++) {
          Base q = resolveBase(op.getInput(i), fc, depth + 1);
          if (q == null) return null;
          if (!first && sp != q.sp) return null;
          first = false; sp = q.sp;
          lo = Math.min(lo, q.lo); hi = Math.max(hi, q.hi);
          n.gp |= q.gp; n.tp |= q.tp;
        }
        n.kind = sp ? "sp+const" : (n.gp ? "gp+const" : (n.tp ? "tp+const" : "const"));
        n.lo = lo; n.hi = hi; n.sp = sp; n.how = "phi@" + pcOf(op);
        return n;
      }
      default: return null;
    }
  }

  String unresolvedWhy(Varnode x) {
    x = strip(x);
    if (x == null) return "null";
    if (x.isConstant() || isGp(x) || isTp(x) || isSp(x) || isR0(x)) return "resolves";
    PcodeOp op = x.getDef();
    if (op == null) {
      if (x.isRegister()) return "param:" + regName(x);
      return "nodef:" + x.toString().replaceAll("\\s+", "");
    }
    int c = op.getOpcode();
    if (c == PcodeOp.LOAD) return "load";
    if (c == PcodeOp.CALL || c == PcodeOp.CALLIND || c == PcodeOp.CALLOTHER) return "callret";
    if (c == PcodeOp.MULTIEQUAL) return "phi";
    return PcodeOp.getMnemonic(c).toLowerCase();
  }

  String regName(Varnode v) {
    Register r = currentProgram.getRegister(v);
    return r == null ? v.toString().replaceAll("\\s+", "") : r.getName();
  }

  // TriageUnknownStoreBases leaf of the pointer expression: the operand that
  // its base() labels as the base (first operand of the top-level operator).
  Varnode baseOperand(Varnode ptr) {
    Varnode v = strip(ptr);
    int d = 0;
    while (v != null && d++ < 16) {
      if (v.isConstant() || isGp(v) || isTp(v) || isSp(v) || isR0(v)) return v;
      PcodeOp op = v.getDef();
      if (op == null) return v;
      switch (op.getOpcode()) {
        case PcodeOp.PTRSUB:
          if (op.getInput(0).isConstant()) return v;
          v = strip(op.getInput(0)); break;
        case PcodeOp.PTRADD: case PcodeOp.INT_ADD: case PcodeOp.INT_SUB:
        case PcodeOp.INT_MULT: case PcodeOp.INT_LEFT:
          v = strip(op.getInput(0)); break;
        default: return v;
      }
    }
    return v;
  }

  // ------------------------------------------------------------- index class
  String cls(Varnode v, int d, Set<Varnode> seen, FC fc) {
    if (v == null) return "null";
    if (v.isConstant()) return String.format("0x%x", v.getOffset() & U32);
    if (isGp(v)) return "GP";
    if (isTp(v)) return "TP";
    if (isR0(v)) return "0";
    PcodeOp op = v.getDef();
    if (op == null) {
      if (v.isRegister()) return isArg(v) ? "param " + regName(v) : "reg " + regName(v);
      if (v.getAddress().isStackAddress()) return "stack";
      if (v.isAddress()) return "ram";
      return "tmp";
    }
    if (d > 6 || !seen.add(v)) return "..";
    try {
      int c = op.getOpcode();
      Varnode a = op.getInput(0), b = op.getNumInputs() > 1 ? op.getInput(1) : null;
      switch (c) {
        case PcodeOp.COPY: case PcodeOp.CAST: case PcodeOp.INDIRECT: return cls(a, d + 1, seen, fc);
        case PcodeOp.INT_ZEXT: return "zext" + (8 * a.getSize()) + "(" + cls(a, d + 1, seen, fc) + ")";
        case PcodeOp.INT_SEXT: return "sext" + (8 * a.getSize()) + "(" + cls(a, d + 1, seen, fc) + ")";
        case PcodeOp.SUBPIECE:
          if (v.getSize() >= 4 && b.isConstant() && b.getOffset() == 0) return cls(a, d + 1, seen, fc);
          return "sub" + (b.isConstant() ? b.getOffset() : "?") + "(" + cls(a, d + 1, seen, fc) + ")";
        case PcodeOp.INT_AND:
          if (b.isConstant()) return String.format("and(0x%x,%s)", b.getOffset() & U32, cls(a, d + 1, seen, fc));
          if (a.isConstant()) return String.format("and(0x%x,%s)", a.getOffset() & U32, cls(b, d + 1, seen, fc));
          return "and(" + cls(a, d + 1, seen, fc) + "," + cls(b, d + 1, seen, fc) + ")";
        case PcodeOp.INT_LEFT: return b.isConstant() ? "shl(" + (b.getOffset() & 31) + "," + cls(a, d + 1, seen, fc) + ")" : "shl(?)";
        case PcodeOp.INT_RIGHT: return b.isConstant() ? "shr(" + (b.getOffset() & 31) + "," + cls(a, d + 1, seen, fc) + ")" : "shr(?)";
        case PcodeOp.INT_SRIGHT: return b.isConstant() ? "sar(" + (b.getOffset() & 31) + "," + cls(a, d + 1, seen, fc) + ")" : "sar(?)";
        case PcodeOp.INT_MULT:
          if (b.isConstant()) return "mul(" + (b.getOffset() & U32) + "," + cls(a, d + 1, seen, fc) + ")";
          if (a.isConstant()) return "mul(" + (a.getOffset() & U32) + "," + cls(b, d + 1, seen, fc) + ")";
          return "mul(" + cls(a, d + 1, seen, fc) + "," + cls(b, d + 1, seen, fc) + ")";
        case PcodeOp.INT_ADD:
          if (b.isConstant()) return "add(" + (b.getOffset() & U32) + "," + cls(a, d + 1, seen, fc) + ")";
          if (a.isConstant()) return "add(" + (a.getOffset() & U32) + "," + cls(b, d + 1, seen, fc) + ")";
          return "add(" + cls(a, d + 1, seen, fc) + "," + cls(b, d + 1, seen, fc) + ")";
        case PcodeOp.INT_SUB:
          if (b.isConstant()) return "sub(" + (b.getOffset() & U32) + "," + cls(a, d + 1, seen, fc) + ")";
          return "sub(" + cls(a, d + 1, seen, fc) + "," + cls(b, d + 1, seen, fc) + ")";
        case PcodeOp.MULTIEQUAL: {
          StringBuilder sb = new StringBuilder("phi(");
          for (int i = 0; i < op.getNumInputs(); i++) { if (i > 0) sb.append('|'); sb.append(cls(op.getInput(i), d + 1, seen, fc)); }
          return sb.append(')').toString();
        }
        case PcodeOp.LOAD: return "load" + (8 * v.getSize()) + "[" + addrText(op.getInput(0), fc) + "]";
        case PcodeOp.CALL: case PcodeOp.CALLIND: return "ret" + (8 * v.getSize());
        case PcodeOp.PTRSUB: case PcodeOp.PTRADD: return "&" + addrText(v, fc);
        default: break;
      }
      if (BOOL_OPS.contains(c) || CMP_OPS.contains(c)) return "bool";
      return PcodeOp.getMnemonic(c).toLowerCase();
    } finally { seen.remove(v); }
  }

  boolean isArg(Varnode v) {
    if (!v.isRegister() || v.getSize() != 4) return false;
    long o = v.getOffset();
    for (long a : ARG_OFFS) if (a == o) return true;
    return false;
  }

  String addrText(Varnode p, FC fc) {
    if (p == null) return "?";
    Rg r = rng(p, Collections.emptyMap(), new HashSet<>(), 0, fc);
    if (r.lo == r.hi && !r.open) return String.format("0x%x", r.lo & U32);
    p = strip(p);
    PcodeOp op = p.getDef();
    if (op != null && op.getOpcode() == PcodeOp.PTRSUB && !op.getInput(0).isConstant()) {
      Rg b = rng(op.getInput(1), Collections.emptyMap(), new HashSet<>(), 0, fc);
      String base = leafText(op.getInput(0), fc);
      if (b.lo == b.hi) return String.format("%s%+d", base, (int) b.lo);
      return base + "+?";
    }
    if (op != null && op.getOpcode() == PcodeOp.PTRADD) return leafText(op.getInput(0), fc) + "+" + cls(op.getInput(1), 0, new HashSet<>(), fc) + "*" + (op.getInput(2).getOffset() & U32);
    if (op != null && op.getOpcode() == PcodeOp.INT_ADD && op.getInput(1).isConstant()) return leafText(op.getInput(0), fc) + String.format("%+d", (int) op.getInput(1).getOffset());
    if (op != null && op.getOpcode() == PcodeOp.INT_ADD) return leafText(op.getInput(0), fc) + "+" + cls(op.getInput(1), 0, new HashSet<>(), fc);
    return leafText(p, fc);
  }

  String leafText(Varnode v, FC fc) {
    v = strip(v);
    if (v == null) return "?";
    if (v.isConstant()) return String.format("0x%x", v.getOffset() & U32);
    if (v.isRegister()) return regName(v);
    PcodeOp op = v.getDef();
    if (op != null && op.getOpcode() == PcodeOp.LOAD) return "[" + addrText(op.getInput(0), fc) + "]";
    if (op != null) return PcodeOp.getMnemonic(op.getOpcode()).toLowerCase();
    return v.toString().replaceAll("\\s+", "");
  }

  // ----------------------------------------------------------- function context
  static final class Cmp { Address at; Instruction ci; Varnode a, b; boolean bImm, viaAddi; long imm; Instruction br; String cond; Address tgt, fall; }
  final class FC {
    Function f; HighFunction hf; boolean app; long gp, tp; boolean gpKnown = true, tpKnown = true; List<String> ctxWriters = new ArrayList<>();
    List<Instruction> ins = new ArrayList<>();
    Set<Address> branchTargets = new HashSet<>();
    Map<Address, List<Address>> succ = new HashMap<>();
    Set<Address> openSucc = new HashSet<>();
    List<Cmp> cmps = new ArrayList<>();
    Map<Address, List<PcodeOp>> opsAt = new HashMap<>();
    Map<Address, Instruction> insAt = new HashMap<>();
    long raOff = -1, frameTop = -1; int savedRegs = 0; String frameTxt = "";
    Address entry, maxAddr;
  }

  List<Address> NO = Collections.emptyList();

  boolean writesFlags(Instruction ins) {
    if (FLAG_WRITERS.contains(ins.getMnemonicString())) return true;
    for (Object o : ins.getResultObjects()) if (o instanceof Register && ((Register) o).getName().toUpperCase().startsWith("PSW")) return true;
    return false;
  }

  FC buildFc(Function f, HighFunction hf) {
    FC fc = new FC(); fc.f = f; fc.hf = hf;
    fc.app = (f.getEntryPoint().getOffset() & U32) >= APP_BASE;
    fc.gp = fc.app ? APP_GP : BOOT_GP; fc.tp = fc.app ? APP_TP : BOOT_TP;
    fc.entry = f.getEntryPoint(); fc.maxAddr = f.getBody().getMaxAddress();
    Listing listing = currentProgram.getListing();
    ReferenceManager rm = currentProgram.getReferenceManager();
    InstructionIterator ii = listing.getInstructions(fc.entry, true);
    while (ii.hasNext()) {
      Instruction i = ii.next();
      Address a = i.getAddress();
      if (!f.getBody().contains(a)) { if (a.compareTo(fc.maxAddr) > 0) break; else continue; }
      fc.ins.add(i); fc.insAt.put(a, i);
      if (rm.getReferencesTo(a).hasNext()) fc.branchTargets.add(a);
      for (Object o : i.getResultObjects()) {
        if (!(o instanceof Register)) continue;
        String nm = ((Register) o).getName();
        if (nm.equals("gp")) { fc.gpKnown = false; fc.ctxWriters.add(i.getAddress() + " " + i.toString().replaceAll("\\s+", " ")); }
        if (nm.equals("tp")) { fc.tpKnown = false; fc.ctxWriters.add(i.getAddress() + " " + i.toString().replaceAll("\\s+", " ")); }
      }
    }
    for (Instruction i : fc.ins) {
      Address a = i.getAddress(); List<Address> s = new ArrayList<>();
      FlowType ft = i.getFlowType(); Address fall = i.getFallThrough();
      if (ft.isCall()) { if (fall != null && f.getBody().contains(fall)) s.add(fall); }
      else if (ft.isJump()) {
        if (ft.isComputed()) { fc.openSucc.add(a); if (fall != null && f.getBody().contains(fall)) s.add(fall); }
        else for (Address t : i.getFlows()) if (f.getBody().contains(t)) s.add(t);
        if (ft.isConditional() && fall != null && f.getBody().contains(fall)) s.add(fall);
      } else if (!ft.isTerminal()) { if (fall != null && f.getBody().contains(fall)) s.add(fall); }
      fc.succ.put(a, s);
    }
    // frame: prepare {list}, imm reserves 4*imm bytes and stacks lp at sp+4*imm
    if (!fc.ins.isEmpty()) {
      Instruction e = fc.ins.get(0);
      java.util.regex.Matcher m = java.util.regex.Pattern.compile("prepare\\s*\\{([^}]*)\\}\\s*,\\s*(0x[0-9a-f]+|\\d+)").matcher(e.toString());
      if (e.getMnemonicString().equals("prepare") && m.find()) {
        long imm = Long.decode(m.group(2));
        java.util.regex.Matcher r = java.util.regex.Pattern.compile("r\\d+").matcher(m.group(1));
        int n = 0; while (r.find()) n++;
        fc.raOff = 4 * imm; fc.savedRegs = n; fc.frameTop = fc.raOff + 4 + 4 * n;
        fc.frameTxt = e.toString().replaceAll("\\s+", " ").trim();
      } else fc.frameTxt = "no prepare: " + e.toString().replaceAll("\\s+", " ").trim();
    }
    Iterator<PcodeOpAST> it = hf.getPcodeOps();
    while (it.hasNext()) {
      PcodeOpAST op = it.next();
      Address t = op.getSeqnum().getTarget();
      fc.opsAt.computeIfAbsent(t, k -> new ArrayList<>()).add(op);
    }
    // compare + conditional branch pairs (same basic block, flags not rewritten)
    for (int i = 0; i < fc.ins.size(); i++) {
      Instruction ci = fc.ins.get(i); String m = ci.getMnemonicString();
      if (!compareLike(ci)) continue;
      for (int j = i + 1; j < Math.min(fc.ins.size(), i + 16); j++) {
        Instruction bj = fc.ins.get(j);
        if (fc.branchTargets.contains(bj.getAddress())) break;
        FlowType ft = bj.getFlowType(); String bm = bj.getMnemonicString();
        if (ft.isJump() && ft.isConditional() && bm.length() > 1 && bm.charAt(0) == 'b' && CONDS.contains(bm.substring(1))) {
          Cmp c = new Cmp(); c.at = ci.getAddress(); c.ci = ci; c.br = bj; c.cond = bm.substring(1);
          Address[] fl = bj.getFlows(); c.tgt = fl.length > 0 ? fl[0] : null; c.fall = bj.getFallThrough();
          fillCompare(c, fc);
          if (c.a != null) fc.cmps.add(c);
          break;
        }
        if (ft.isJump() || ft.isCall() || ft.isTerminal()) break;
        if (writesFlags(bj)) break;
      }
    }
    return fc;
  }

  // cmp/tst, or an add/addi into r0 whose flags feed a branch (addi -N, rX, r0; blt)
  boolean compareLike(Instruction ci) {
    String m = ci.getMnemonicString();
    if (m.equals("cmp") || m.equals("tst")) return true;
    if (m.equals("addi") || m.equals("add")) {
      Object[] last = ci.getNumOperands() > 0 ? ci.getOpObjects(ci.getNumOperands() - 1) : new Object[0];
      for (Object o : last) if (o instanceof Register && ((Register) o).getOffset() == OFF_R0) return true;
    }
    return false;
  }

  // Operands of the compare as SSA varnodes. For cmp/tst the V850 flags are
  // computed from reg2 - reg1 (operand 0 is the imm/reg1 subtrahend, operand 1
  // is reg2), so A = reg2 and B = the operand-0 immediate or register. For
  // addi imm, reg1, r0 / add reg1, r0 the flags describe (reg1 + imm) against
  // zero, i.e. A = reg1 and B = -imm.
  void fillCompare(Cmp c, FC fc) {
    String m = c.ci.getMnemonicString();
    Object[] o0 = c.ci.getNumOperands() > 0 ? c.ci.getOpObjects(0) : new Object[0];
    Object[] o1 = c.ci.getNumOperands() > 1 ? c.ci.getOpObjects(1) : new Object[0];
    Register ra = null, rb = null;
    for (Object o : o1) if (o instanceof Register) ra = (Register) o;
    for (Object o : o0) { if (o instanceof Scalar) { c.bImm = true; c.imm = ((Scalar) o).getSignedValue(); } else if (o instanceof Register) rb = (Register) o; }
    if (m.equals("addi")) { c.viaAddi = true; c.imm = -c.imm; }
    else if (m.equals("add")) { c.viaAddi = true; ra = rb; c.bImm = true; c.imm = 0; }
    if (ra == null) return;
    c.a = ssaRead(fc, ra, c.at);
    if (!c.bImm && rb != null) c.b = ssaRead(fc, rb, c.at);
    else if (!c.bImm) c.bImm = true;
  }

  // The SSA version of register r read at address `at`: an input of the p-code
  // ops issued at that instruction, else the latest read at or before it.
  Varnode ssaRead(FC fc, Register r, Address at) {
    for (PcodeOp op : fc.opsAt.getOrDefault(at, Collections.emptyList()))
      for (Varnode in : op.getInputs()) if (in.isRegister() && in.getAddress().equals(r.getAddress())) return in;
    Varnode best = null; long bestAddr = -1;
    for (Map.Entry<Address, List<PcodeOp>> en : fc.opsAt.entrySet()) {
      long a = en.getKey().getOffset();
      if (a > at.getOffset() || a < bestAddr) continue;
      for (PcodeOp op : en.getValue()) for (Varnode in : op.getInputs()) if (in.isRegister() && in.getAddress().equals(r.getAddress())) { best = in; bestAddr = a; }
    }
    return best;
  }

  // true when S is reachable from `from` without deciding at the branch `stop`
  boolean reaches(FC fc, Address from, Address stop, Address s) {
    if (from == null) return false;
    Deque<Address> q = new ArrayDeque<>(); Set<Address> seen = new HashSet<>();
    q.add(from); seen.add(from);
    while (!q.isEmpty()) {
      Address a = q.poll();
      if (a.equals(s) || a.equals(stop)) return true;
      if (fc.openSucc.contains(a)) return true;
      for (Address b : fc.succ.getOrDefault(a, NO)) if (seen.add(b)) q.add(b);
    }
    return false;
  }

  // ------------------------------------------------------------ tree helpers
  void collectTree(Varnode v, Set<Varnode> out, int d) {
    if (v == null || d > 24 || !out.add(v)) return;
    PcodeOp op = v.getDef();
    if (op == null) return;
    for (Varnode in : op.getInputs()) collectTree(in, out, d + 1);
  }

  Varnode descend(Varnode v) {
    v = strip(v); int d = 0;
    while (v != null && d++ < 8) {
      PcodeOp op = v.getDef(); if (op == null) return v;
      int c = op.getOpcode(); Varnode a = op.getInput(0), b = op.getNumInputs() > 1 ? op.getInput(1) : null;
      if (c == PcodeOp.INT_MULT || c == PcodeOp.INT_ADD) { if (b != null && b.isConstant()) { v = strip(a); continue; } if (a.isConstant()) { v = strip(b); continue; } return v; }
      if (c == PcodeOp.INT_LEFT && b != null && b.isConstant()) { v = strip(a); continue; }
      return v;
    }
    return v;
  }

  // follow a narrowing chain (copy/cast/zext/sext/subpiece/and-const) from x to a varnode of the tree
  Varnode narrowLeaf(Varnode x, Set<Varnode> tree) {
    int d = 0;
    while (x != null && d++ < 12) {
      if (tree.contains(x)) return x;
      x = strip(x);
      if (tree.contains(x)) return x;
      PcodeOp op = x.getDef(); if (op == null) return null;
      int c = op.getOpcode();
      if (c == PcodeOp.INT_AND) {
        Varnode a = op.getInput(0), b = op.getInput(1);
        if (a.isConstant()) x = b; else if (b.isConstant()) x = a; else return null;
        continue;
      }
      if (c == PcodeOp.INT_ZEXT || c == PcodeOp.INT_SEXT || c == PcodeOp.SUBPIECE) { x = op.getInput(0); continue; }
      return null;
    }
    return null;
  }

  static final class PhiLink { Varnode phi; PcodeOp g; }
  // x = g(P) with P a MULTIEQUAL varnode of the tree
  PhiLink derivePhi(Varnode x, Set<Varnode> tree) {
    int d = 0;
    while (x != null && d++ < 12) {
      PcodeOp op = x.getDef(); if (op == null) return null;
      int c = op.getOpcode();
      Varnode a = op.getInput(0), b = op.getNumInputs() > 1 ? op.getInput(1) : null;
      Varnode next = null;
      if (c == PcodeOp.INT_ADD || c == PcodeOp.INT_MULT || c == PcodeOp.INT_LEFT || c == PcodeOp.INT_AND) {
        if (b != null && b.isConstant()) next = strip(a); else if (a.isConstant()) next = strip(b);
      } else if (c == PcodeOp.INT_ZEXT || c == PcodeOp.INT_SEXT || c == PcodeOp.SUBPIECE || c == PcodeOp.COPY || c == PcodeOp.CAST || c == PcodeOp.INDIRECT) next = strip(a);
      if (next == null) return null;
      if (tree.contains(next) && next.getDef() != null && next.getDef().getOpcode() == PcodeOp.MULTIEQUAL) { PhiLink l = new PhiLink(); l.phi = next; l.g = op; return l; }
      x = next;
    }
    return null;
  }

  Rg phiInitRange(Varnode phi, FC fc) {
    PcodeOp me = phi.getDef(); Rg out = null;
    for (Varnode in : me.getInputs()) {
      Set<Varnode> t = new HashSet<>(); collectTree(in, t, 0);
      if (t.contains(phi)) continue;
      Rg q = rng(in, Collections.emptyMap(), new HashSet<>(), 0, fc);
      out = out == null ? q : out.hull(q);
    }
    return out == null ? Rg.unk(4) : out;
  }
  static final class Clamp { Rg rg; String how; }

  // min(X, N) or max(X, N) select: the phi inputs are narrowing copies of X
  // plus the constant N that X is compared against by a flag-set/branch pair.
  // The branch condition gives the direction: x > N (h/nh) selects N for a
  // ceiling, x <= N (blt/ge/addi forms) selects N for a floor.
  Clamp clampRange(Varnode phi, FC fc) {
    PcodeOp me = phi.getDef(); if (me == null || me.getOpcode() != PcodeOp.MULTIEQUAL) return null;
    Varnode src = null; Long k = null;
    for (Varnode in : me.getInputs()) {
      Varnode s = strip(in);
      if (s.isConstant()) { if (k != null && k != (s.getOffset() & U32)) return null; k = s.getOffset() & U32; }
      else if (src == null) src = s; else if (!s.equals(src)) return null;
    }
    if (src == null || k == null) return null;
    for (Cmp c : fc.cmps) {
      if (!c.bImm) continue;
      long imm = c.imm & U32; int rel = relOf(c.cond);
      boolean ceiling = false, floor = false;
      if (imm == k && (rel == R_GTU || rel == R_LEU)) ceiling = true;
      else if (imm == k && (rel == R_GEU || rel == R_LTU || rel == R_GES || rel == R_LTS)) floor = true;
      else if (imm == k + 1 && c.viaAddi && (rel == R_GES || rel == R_LTS)) floor = true;
      else continue;
      Varnode x = c.a; if (x == null || isGp(x) || isTp(x) || isR0(x)) continue;
      Set<Varnode> one = new HashSet<>(); one.add(x);
      if (narrowLeaf(src, one) == null) continue;
      Rg xr = rng(x, Collections.emptyMap(), new HashSet<>(), 0, fc);
      if (xr.lo < 0) continue;
      Clamp cl = new Clamp();
      if (ceiling) { if (xr.hi <= k) continue; cl.rg = new Rg(xr.lo, k, false); }
      else { if (xr.lo >= k) continue; cl.rg = new Rg(k, xr.hi, false); }
      cl.how = String.format("%s(%s,%s) %s@%s b%s@%s", ceiling ? "min" : "max", leafText(x, fc), hex(k), c.ci.getMnemonicString(), c.at, c.cond, c.br.getAddress());
      return cl;
    }
    return null;
  }

  // range of a data bound varnode, tightened by a clamp select when applicable
  Rg boundRange(Varnode nV, FC fc) {
    Rg r = rng(nV, Collections.emptyMap(), new HashSet<>(), 0, fc);
    Varnode s = strip(nV);
    if (isPhi(s)) { Clamp cl = clampRange(s, fc); if (cl != null && cl.rg.hi < r.hi) r = cl.rg; }
    return r;
  }


  // invert g(P) = x for the bound on x: returns the implied range of P
  Rg invertG(PcodeOp g, Rg bx) {
    int c = g.getOpcode(); Varnode a = g.getInput(0), b = g.getNumInputs() > 1 ? g.getInput(1) : null;
    long k;
    switch (c) {
      case PcodeOp.INT_ADD: k = a.isConstant() ? a.getOffset() : b.getOffset(); return bx.shift(-(k <= 0x7fffffffL ? k : k - (1L << 32)));
      case PcodeOp.INT_MULT: k = (a.isConstant() ? a.getOffset() : b.getOffset()) & U32; if (k == 0) return null; return new Rg((long) Math.ceil((double) bx.lo / k), bx.hi / k, false);
      case PcodeOp.INT_LEFT: k = 1L << (int) (b.getOffset() & 31); return new Rg((long) Math.ceil((double) bx.lo / k), bx.hi / k, false);
      default: return bx.copy();
    }
  }

  static final int R_NONE = 0, R_LTS = 1, R_GES = 2, R_LES = 3, R_GTS = 4, R_LTU = 5, R_GEU = 6, R_LEU = 7, R_GTU = 8, R_EQ = 9, R_NE = 10;
  static int relOf(String cond) {
    switch (cond) {
      case "lt": return R_LTS; case "ge": return R_GES; case "le": return R_LES; case "gt": return R_GTS;
      case "c": return R_LTU; case "nc": return R_GEU; case "nh": return R_LEU; case "h": return R_GTU;
      case "e": return R_EQ; case "ne": return R_NE;
      default: return R_NONE;
    }
  }
  static int negate(int r) {
    switch (r) {
      case R_LTS: return R_GES; case R_GES: return R_LTS; case R_LES: return R_GTS; case R_GTS: return R_LES;
      case R_LTU: return R_GEU; case R_GEU: return R_LTU; case R_LEU: return R_GTU; case R_GTU: return R_LEU;
      case R_EQ: return R_NE; case R_NE: return R_EQ;
      default: return R_NONE;
    }
  }
  static int converse(int r) {
    switch (r) {
      case R_LTS: return R_GTS; case R_GES: return R_LES; case R_LES: return R_GES; case R_GTS: return R_LTS;
      case R_LTU: return R_GTU; case R_GEU: return R_LEU; case R_LEU: return R_GEU; case R_GTU: return R_LTU;
      default: return r;
    }
  }
  static String relText(int r) {
    switch (r) {
      case R_LTS: return "<s"; case R_GES: return ">=s"; case R_LES: return "<=s"; case R_GTS: return ">s";
      case R_LTU: return "<u"; case R_GEU: return ">=u"; case R_LEU: return "<=u"; case R_GTU: return ">u";
      case R_EQ: return "=="; case R_NE: return "!=";
      default: return "?";
    }
  }

  // range of x given "x rel n", intersected with the coarse range of x; null when no information
  Rg applyRel(Rg xr, int rel, Rg nr) {
    long lo = xr.lo, hi = xr.hi;
    boolean uns = rel == R_LTU || rel == R_GEU || rel == R_LEU || rel == R_GTU;
    if (uns && lo < 0) return null;
    long nlo = nr.lo, nhi = nr.hi;
    switch (rel) {
      case R_LTS: case R_LTU: hi = Math.min(hi, nhi - 1); break;
      case R_GES: case R_GEU: lo = Math.max(lo, nlo); break;
      case R_LES: case R_LEU: hi = Math.min(hi, nhi); break;
      case R_GTS: case R_GTU: lo = Math.max(lo, nlo + 1); break;
      case R_EQ: if (nlo != nhi) return null; lo = Math.max(lo, nlo); hi = Math.min(hi, nhi); break;
      default: return null;
    }
    if (lo > hi) return null;
    return new Rg(lo, hi, false);
  }

  // ------------------------------------------------------------ data path
  String originText(List<Term> terms, FC fc) {
    LinkedHashSet<String> parts = new LinkedHashSet<>();
    for (Term t : terms) {
      Set<Varnode> tree = new TreeSet<>((x, y) -> { int c = Long.compare(x.getSpace(), y.getSpace()); return c != 0 ? c : Long.compare(x.getOffset(), y.getOffset()); });
      collectTree(t.v, tree, 0);
      for (Varnode v : tree) {
        PcodeOp op = v.getDef();
        if (op == null) {
          if (v.isRegister() && !isGp(v) && !isTp(v) && !isR0(v) && !isSp(v)) parts.add(isArg(v) ? "param " + regName(v) + " (arg" + argIndex(v) + ")" : "reg " + regName(v));
          else if (!v.isRegister()) parts.add(v.getAddress().isStackAddress() ? "stack local" : "input " + v.toString().replaceAll("\\s+", ""));
        } else if (op.getOpcode() == PcodeOp.LOAD) parts.add("load u" + (8 * v.getSize()) + " [" + addrText(op.getInput(0), fc) + "]");
        else if (op.getOpcode() == PcodeOp.MULTIEQUAL) parts.add("loop-phi");
        else if (op.getOpcode() == PcodeOp.CALL || op.getOpcode() == PcodeOp.CALLIND) parts.add("call result");
      }
    }
    return String.join("; ", parts);
  }

  int argIndex(Varnode v) { long o = v.getOffset(); for (int i = 0; i < ARG_OFFS.length; i++) if (ARG_OFFS[i] == o) return i; return -1; }

  // ------------------------------------------------------------- call graph
  Map<Long, Set<Long>> callersOf = new HashMap<>();
  Map<Long, List<long[]>> sitesOf = new HashMap<>(); // callee -> {caller, site}
  Map<Long, List<Long>> vectorRefs = new HashMap<>();

  void addEdge(Function from, Function to, long site) {
    if (from == null || to == null || from.equals(to)) return;
    callersOf.computeIfAbsent(to.getEntryPoint().getOffset() & U32, k -> new TreeSet<>()).add(from.getEntryPoint().getOffset() & U32);
    sitesOf.computeIfAbsent(to.getEntryPoint().getOffset() & U32, k -> new ArrayList<>()).add(new long[]{from.getEntryPoint().getOffset() & U32, site});
  }

  void buildCallGraph() {
    FunctionManager fm = currentProgram.getFunctionManager();
    FunctionIterator fi = fm.getFunctions(true);
    while (fi.hasNext()) {
      Function f = fi.next();
      for (Instruction i : currentProgram.getListing().getInstructions(f.getBody(), true)) {
        FlowType ft = i.getFlowType();
        if (!ft.isCall() && !ft.isJump()) continue;
        for (Reference r : i.getReferencesFrom()) {
          if (r.getReferenceType().isCall() || (ft.isJump() && !ft.isConditional() && i.getMnemonicString().equals("jmp"))) {
            Function g = fm.getFunctionAt(r.getToAddress());
            if (g != null && !g.equals(f)) addEdge(f, g, i.getAddress().getOffset() & U32);
          }
        }
        if (ft.isComputed() && i.getMnemonicString().equals("jmp")) {
          // fixed-immediate thunk: movea/mov/ld.w of a function address precedes jmp [rX]
          Instruction p = i.getPrevious(); int k = 0;
          while (p != null && f.getBody().contains(p.getAddress()) && k++ < 3) {
            String m = p.getMnemonicString();
            if (m.equals("movea") || m.equals("mov") || m.startsWith("ld.")) {
              for (Reference r : p.getReferencesFrom()) {
                Function g = fm.getFunctionAt(r.getToAddress());
                if (g != null && !g.equals(f)) addEdge(f, g, i.getAddress().getOffset() & U32);
              }
            }
            p = p.getPrevious();
          }
        }
      }
    }
    // vector tables at the application base: word -> function entry
    for (long a = VEC_LO; a < VEC_HI; a += 4) {
      try {
        long w = getLong(toAddr(a)) & U32;
        Function g = fm.getFunctionAt(toAddr(w));
        if (g != null) vectorRefs.computeIfAbsent(w, k -> new ArrayList<>()).add(a);
      } catch (Exception e) { break; }
    }
  }

  String entryClass(String name) {
    String n = name.toLowerCase();
    if (n.matches(".*(dcm|diag|did|routine|uds|xcp|wdbi|rdbi|service).*")) return "diag";
    if (n.matches(".*(secoc|crypto|cmac|aes).*")) return "crypto";
    if (n.matches(".*(can|cantp|canif|rx|receiv|pdu|frame|com_).*")) return "can";
    if (n.matches(".*(nvm|fee|dataflash).*")) return "nvm";
    if (n.startsWith("boot")) return "boot";
    return "other";
  }

  // reverse reachability: roots and known entries that reach function `f`
  String entriesText(Function f) {
    long start = f.getEntryPoint().getOffset() & U32;
    Deque<Long> q = new ArrayDeque<>(); Set<Long> seen = new TreeSet<>(); q.add(start); seen.add(start);
    while (!q.isEmpty()) { long a = q.poll(); for (long c : callersOf.getOrDefault(a, Collections.emptySet())) if (seen.add(c)) q.add(c); }
    FunctionManager fm = currentProgram.getFunctionManager();
    List<String> roots = new ArrayList<>(); List<String> known = new ArrayList<>();
    for (long a : seen) {
      if (a == start) continue;
      Function g = fm.getFunctionAt(toAddr(a)); if (g == null) continue;
      boolean k = false; for (long e : KNOWN_ENTRIES) if (e == a) k = true;
      if (k) known.add(String.format("%s@%x", g.getName(), a));
      if (!callersOf.containsKey(a)) {
        roots.add(String.format("[%s]%s@%x%s", entryClass(g.getName()), g.getName(), a, vectorRefs.containsKey(a) ? "(vector)" : ""));
      }
    }
    String r = roots.isEmpty() ? "no root (indirect dispatch only)" : String.join(", ", roots.subList(0, Math.min(roots.size(), 5))) + (roots.size() > 5 ? " +" + (roots.size() - 5) : "");
    return r + (known.isEmpty() ? "" : " | known-entry: " + String.join(", ", known));
  }


  // ----------------------------------------------------- call-target RAM cells
  static final class CellSite { Address at; String fn; long cell; String how;
    CellSite(Address a, String f, long c, String h) { at = a; fn = f; cell = c; how = h; } }
  final TreeMap<Long, List<CellSite>> callCells = new TreeMap<>();
  long callSites = 0, callResolvedConst = 0, callUnresolved = 0;
  final TreeMap<String, Long> callUnresolvedWhy = new TreeMap<>();

  boolean writesRegister(Instruction ins, Register wanted) {
    for (Object o : ins.getResultObjects()) if (o instanceof Register && ((Register) o).equals(wanted)) return true;
    return false;
  }
  boolean isLoadMnemonic(String m) { return m.startsWith("ld.") || m.startsWith("sld."); }

  static final class Addr { long v; boolean sp; Addr(long a, boolean s) { v = a; sp = s; } }
  long gpOf(Function f) { return (f.getEntryPoint().getOffset() & U32) >= APP_BASE ? APP_GP : BOOT_GP; }
  long tpOf(Function f) { return (f.getEntryPoint().getOffset() & U32) >= APP_BASE ? APP_TP : BOOT_TP; }

  final Map<Long, Boolean> ctxKnownCache = new HashMap<>();
  // true when no instruction of f writes GP or TP (the boot routine at
  // 0x1AB00..0x1B5FF uses them as scratch registers)
  boolean ctxKnown(Function f) {
    long k = f.getEntryPoint().getOffset() & U32;
    Boolean b = ctxKnownCache.get(k);
    if (b != null) return b;
    boolean ok = true;
    for (Instruction i : currentProgram.getListing().getInstructions(f.getBody(), true))
      for (Object o : i.getResultObjects()) { if (o instanceof Register) { String nm = ((Register) o).getName(); if (nm.equals("gp") || nm.equals("tp")) ok = false; } }
    ctxKnownCache.put(k, ok);
    return ok;
  }

  // Value of register r immediately before `from`, by a linear bounded backtrack
  // over register-writing instructions. Resolves constants, GP/TP-relative
  // addresses and copies; null when the value is not a constant.
  Addr regValueBefore(Register r, Function f, Instruction from, int budget) {
    if (r == null || budget <= 0) return null;
    long gpv = gpOf(f), tpv = tpOf(f);
    if (r.getOffset() == OFF_GP) return ctxKnown(f) ? new Addr(gpv, false) : null;
    if (r.getOffset() == OFF_TP) return ctxKnown(f) ? new Addr(tpv, false) : null;
    if (r.getOffset() == OFF_R0) return new Addr(0, false);
    if (r.equals(spReg)) return new Addr(0, true);
    Instruction cur = from; int n = 0;
    while (n++ < budget) {
      cur = cur.getPrevious(); if (cur == null || !f.getBody().contains(cur.getAddress())) return null;
      if (!writesRegister(cur, r)) continue;
      String m = cur.getMnemonicString();
      Scalar sc = null; Register op0reg = null;
      for (Object o : cur.getOpObjects(0)) { if (o instanceof Scalar) sc = (Scalar) o; else if (o instanceof Register) op0reg = (Register) o; }
      if (m.equals("mov")) {
        if (sc != null) return new Addr(sc.getSignedValue() & U32, false);
        return regValueBefore(op0reg, f, cur, budget - n);
      }
      if (m.equals("movea") || m.equals("addi") || m.equals("ori")) {
        Register src = null;
        for (int op = 0; op < cur.getNumOperands(); op++) for (Object o : cur.getOpObjects(op)) if (o instanceof Register && !((Register) o).equals(r)) src = (Register) o;
        long imm = sc == null ? 0 : (m.equals("ori") ? sc.getUnsignedValue() : sc.getSignedValue());
        if (src == null) return null;
        if (src.getOffset() == OFF_R0) return new Addr(imm & U32, false);
        if (src.getOffset() == OFF_GP) return new Addr((gpv + imm) & U32, false);
        if (src.getOffset() == OFF_TP) return new Addr((tpv + imm) & U32, false);
        Addr b = regValueBefore(src, f, cur, budget - n);
        return b == null ? null : new Addr((b.v + imm) & U32, b.sp);
      }
      if (m.equals("add") || m.equals("sub")) {
        // add reg1, reg2: reg2 = reg2 op reg1
        Addr vr = regValueBefore(r, f, cur, budget - n), va = regValueBefore(op0reg, f, cur, budget - n);
        if (vr == null || va == null) return null;
        return new Addr((m.equals("add") ? vr.v + va.v : vr.v - va.v) & U32, vr.sp || va.sp);
      }
      return null;
    }
    return null;
  }

  // ClassifyComputedCallTargets logic (24-instruction backtrack from each
  // computed jarl/jmp to the nearest writer of the target register, following
  // mov copies), extended so the defining load's address is resolved from its
  // displacement and base register (GP/TP/const) when Ghidra has no operand
  // reference for it.
  void scanCallCells() {
    FunctionManager fm = currentProgram.getFunctionManager();
    InstructionIterator it = currentProgram.getListing().getInstructions(true);
    while (it.hasNext()) {
      Instruction call = it.next(); FlowType flow = call.getFlowType();
      if (!flow.isComputed()) continue;
      String cm = call.getMnemonicString();
      if (!cm.equals("jarl") && !cm.equals("jmp")) continue;
      Function f = fm.getFunctionContaining(call.getAddress()); if (f == null) continue;
      Register target = null;
      for (Object o : call.getOpObjects(0)) if (o instanceof Register) target = (Register) o;
      if (target == null) continue;
      callSites++;
      Instruction cur = call; Register trace = target; int seen = 0; String why = "window";
      while (seen < 24) {
        cur = cur.getPrevious(); if (cur == null || !f.getBody().contains(cur.getAddress())) break;
        seen++;
        if (!writesRegister(cur, trace)) continue;
        String m = cur.getMnemonicString();
        if (m.equals("mov")) {
          Register src = null;
          for (Object o : cur.getOpObjects(0)) if (o instanceof Register) src = (Register) o;
          if (src != null && !src.equals(trace)) { trace = src; continue; }
          why = "mov-imm"; break;
        }
        if (!isLoadMnemonic(m)) {
          if (m.equals("movea") || m.equals("addi") || m.equals("ori")) {
            Addr a = regValueBefore(trace, f, call, 24);
            if (a != null && !a.sp) { noteCell(call.getAddress(), f, a.v, "direct " + m); why = null; } else why = m;
          } else why = m;
          break;
        }
        Long refCell = null;
        for (Reference r : cur.getReferencesFrom()) { long t = r.getToAddress().getOffset(); if (t >= RAM_LO && t <= RAM_HI) refCell = t; }
        if (refCell != null) { noteCell(call.getAddress(), f, refCell, "operand-ref " + m); why = null; break; }
        Scalar disp = null; Register base = null; int n = cur.getNumOperands();
        for (int op = 0; op < n - 1; op++) for (Object o : cur.getOpObjects(op)) {
          if (o instanceof Scalar && disp == null) disp = (Scalar) o;
          else if (o instanceof Register && base == null) base = (Register) o;
        }
        if (base == null) { why = "load-form:" + m; break; }
        long d = disp == null ? 0 : (m.startsWith("sld") ? disp.getUnsignedValue() : disp.getSignedValue());
        Addr a = regValueBefore(base, f, cur, Math.max(2, 24 - seen));
        if (a == null) { why = "load-base:" + base.getName(); break; }
        if (a.sp) { why = "stack-load"; break; }
        noteCell(call.getAddress(), f, a.v + d, "load " + m + " " + base.getName()); why = null; break;
      }
      if (why != null) { callUnresolved++; callUnresolvedWhy.merge(why, 1L, Long::sum); }
    }
  }

  void noteCell(Address at, Function f, long cell, String how) {
    if (cell >= RAM_LO && cell <= RAM_HI) callCells.computeIfAbsent(cell, k -> new ArrayList<>()).add(new CellSite(at, f.getName(), cell, how));
    else callResolvedConst++;
  }

  // ------------------------------------------- TriageUnknownStoreBases helpers
  static class R {
    long lo, hi; boolean known;
    R(long a, long b, boolean k) { lo = a & U32; hi = b & U32; known = k && Long.compareUnsigned(lo, hi) <= 0; }
    static R unk() { return new R(0, U32, false); }
  }
  R add(R a, R b) {
    if (!a.known || !b.known) return R.unk();
    long lo = (a.lo + b.lo) & U32, hi = (a.hi + b.hi) & U32;
    if (Long.compareUnsigned(lo, hi) > 0) return R.unk();
    return new R(lo, hi, true);
  }
  R mul(R a, R b) {
    if (!a.known || !b.known) return R.unk();
    if (a.lo == a.hi) { long k = a.lo; long lo = (b.lo * k) & U32, hi = (b.hi * k) & U32; if (Long.compareUnsigned(lo, hi) > 0) return R.unk(); return new R(lo, hi, true); }
    if (b.lo == b.hi) return mul(b, a);
    return R.unk();
  }
  R ev(Varnode v, int d, Set<Varnode> seen) {
    if (v == null || d > 24 || !seen.add(v)) return R.unk();
    if (v.isConstant()) { long x = v.getOffset() & U32; return new R(x, x, true); }
    PcodeOp op = v.getDef();
    if (op == null) { int bits = v.getSize() * 8; if (bits < 32) return new R(0, (1L << bits) - 1, true); return R.unk(); }
    int c = op.getOpcode();
    if (c == PcodeOp.COPY || c == PcodeOp.CAST || c == PcodeOp.INDIRECT || c == PcodeOp.INT_ZEXT) return ev(op.getInput(0), d + 1, seen);
    if (c == PcodeOp.SUBPIECE && v.getSize() == 4 && op.getInput(1).isConstant() && op.getInput(1).getOffset() == 0) return ev(op.getInput(0), d + 1, seen);
    if (c == PcodeOp.PTRSUB) { R a = ev(op.getInput(0), d + 1, new HashSet<>(seen)), b = ev(op.getInput(1), d + 1, new HashSet<>(seen)); if (a.known && a.lo == 0 && a.hi == 0 && b.known) return b; return add(a, b); }
    if (c == PcodeOp.INT_ADD) return add(ev(op.getInput(0), d + 1, new HashSet<>(seen)), ev(op.getInput(1), d + 1, new HashSet<>(seen)));
    if (c == PcodeOp.INT_SUB) { R a = ev(op.getInput(0), d + 1, new HashSet<>(seen)), b = ev(op.getInput(1), d + 1, new HashSet<>(seen)); if (a.known && b.known && b.lo == b.hi) { long k = (-b.lo) & U32; return add(a, new R(k, k, true)); } return R.unk(); }
    if (c == PcodeOp.INT_MULT) return mul(ev(op.getInput(0), d + 1, new HashSet<>(seen)), ev(op.getInput(1), d + 1, new HashSet<>(seen)));
    if (c == PcodeOp.INT_LEFT) { R a = ev(op.getInput(0), d + 1, new HashSet<>(seen)), b = ev(op.getInput(1), d + 1, new HashSet<>(seen)); if (b.known && b.lo == b.hi && b.lo < 32) return mul(a, new R(1L << b.lo, 1L << b.lo, true)); return R.unk(); }
    if (c == PcodeOp.INT_AND) { R a = ev(op.getInput(0), d + 1, new HashSet<>(seen)), b = ev(op.getInput(1), d + 1, new HashSet<>(seen)); if (b.known && b.lo == b.hi) return new R(0, b.lo, true); if (a.known && a.lo == a.hi) return new R(0, a.lo, true); return R.unk(); }
    if (c == PcodeOp.PTRADD) { R a = ev(op.getInput(0), d + 1, new HashSet<>(seen)), idx = ev(op.getInput(1), d + 1, new HashSet<>(seen)), sz = ev(op.getInput(2), d + 1, new HashSet<>(seen)); return add(a, mul(idx, sz)); }
    if (c == PcodeOp.MULTIEQUAL) { long lo = U32, hi = 0; boolean any = false; for (int i = 0; i < op.getNumInputs(); i++) { R q = ev(op.getInput(i), d + 1, new HashSet<>(seen)); if (!q.known) return R.unk(); if (Long.compareUnsigned(q.lo, lo) < 0) lo = q.lo; if (Long.compareUnsigned(q.hi, hi) > 0) hi = q.hi; any = true; } return any ? new R(lo, hi, true) : R.unk(); }
    return R.unk();
  }
  String base(Varnode v, int d, Set<Varnode> seen) {
    if (v == null || d > 24 || !seen.add(v)) return "?";
    if (v.isConstant()) return v.getAddress().isStackAddress() ? "stack" : "const";
    if (v.isRegister()) {
      if (isSp(v)) return "stack";
      Register r = currentProgram.getRegister(v);
      return "reg:" + (r == null ? v.toString() : r.getName());
    }
    PcodeOp op = v.getDef(); if (op == null) return "reg?";
    int c = op.getOpcode();
    if (c == PcodeOp.COPY || c == PcodeOp.CAST || c == PcodeOp.INDIRECT || c == PcodeOp.INT_ZEXT || c == PcodeOp.INT_SEXT || c == PcodeOp.SUBPIECE) return base(op.getInput(0), d + 1, seen);
    if (c == PcodeOp.LOAD) return "load";
    if (c == PcodeOp.CALL || c == PcodeOp.CALLIND || c == PcodeOp.CALLOTHER) return "callret";
    if (c == PcodeOp.MULTIEQUAL) { TreeSet<String> s = new TreeSet<>(); for (int i = 0; i < op.getNumInputs(); i++) s.add(base(op.getInput(i), d + 1, new HashSet<>(seen))); return "phi{" + String.join("/", s) + "}"; }
    if (c == PcodeOp.PTRSUB || c == PcodeOp.PTRADD || c == PcodeOp.INT_ADD || c == PcodeOp.INT_SUB || c == PcodeOp.INT_MULT || c == PcodeOp.INT_LEFT || c == PcodeOp.INT_AND || c == PcodeOp.INT_OR || c == PcodeOp.INT_XOR) {
      Varnode a = op.getInput(0), b = op.getInput(1);
      boolean za = a.isConstant() && (a.getOffset() & U32) == 0, zb = b.isConstant() && (b.getOffset() & U32) == 0;
      if (za && !zb) return base(b, d + 1, seen);
      if (b.isConstant()) return base(a, d + 1, seen);
      if (a.isConstant()) return base(b, d + 1, seen);
      if ((c == PcodeOp.INT_MULT || c == PcodeOp.INT_LEFT) && !(isSp(a) || isSp(b))) return "scaled(" + base(a, d + 1, seen) + "," + base(b, d + 1, new HashSet<>(seen)) + ")";
      return base(a, d + 1, seen) + "+var(" + base(b, d + 1, new HashSet<>(seen)) + ")";
    }
    return PcodeOp.getMnemonic(c).toLowerCase();
  }
  String kind(String shape) {
    return shape.replaceAll("\\+var\\(.*\\)|scaled\\(.*\\)", "+var").replaceAll("reg:[a-z0-9]+", "reg");
  }

  // ------------------------------------------------------------------ rows
  static final class Cand { String kind; long min, max; String how; boolean imm; String bound; Map<Varnode, Rg> ov;
    Cand(String k, long a, long b, String h, boolean i, String bd, Map<Varnode, Rg> o) { kind = k; min = a; max = b; how = h; imm = i; bound = bd; ov = o; }
    long span() { return max - min; } }
  static final class Row {
    boolean app; long fn; String fnName; long pc; String kind, shape, expr;
    String baseKind, baseHow, baseTxt; long baseLo, baseHi; boolean spBased; long idxOff;
    long stride; int width; String idxClass; long idxMin, idxMax; boolean idxOpen; String origin;
    long lo, hi; String targets, nearest; long distance; boolean reach;
    long spLo, spHi; String frameTxt;
    String cls, evidence, tight, tightTargets, entries, callers, dataPath; boolean tightClosed;
    List<Term> terms; FC fc; Function f;
  }
  final List<Row> rows = new ArrayList<>();
  final List<String> unresolvedRows = new ArrayList<>();

  boolean isPhi(Varnode v) { PcodeOp op = v.getDef(); return op != null && op.getOpcode() == PcodeOp.MULTIEQUAL; }
  static String hex(long v) { return String.format("0x%x", v & U32); }
  static long sat0(long v) { return v < 0 ? 0 : Math.min(U32, v); }
  static long satU(long v) { return v > U32 ? U32 : Math.max(0, v); }
  static String hexl(long v) { return v < 0 ? "-0x" + Long.toHexString(-v) : "0x" + Long.toHexString(v); }
  static String signed(long v) { return v >= 0 ? "+" + hexl(v) : "-" + hexl(-v); }

  static final class Hit { String targets = "", nearest = ""; long distance = Long.MAX_VALUE; boolean any; }
  Hit absHits(long lo, long hi) {
    Hit h = new Hit();
    List<long[]> t = new ArrayList<>(); List<String> names = new ArrayList<>();
    for (long c : HOOKS) { t.add(new long[]{c, c + 3}); names.add("hook:" + hex(c)); }
    t.add(new long[]{TAIL_LO, TAIL_HI}); names.add("tail");
    t.add(new long[]{RWX_LO, RWX_HI}); names.add("rwx");
    for (long c : callCells.keySet()) { t.add(new long[]{c, c + 3}); names.add("call:" + hex(c)); }
    for (long s : STACK_TOPS) { t.add(new long[]{s - STACK_WIN, s - 1}); names.add("stackwin:" + hex(s)); }
    List<String> hit = new ArrayList<>();
    for (int i = 0; i < t.size(); i++) {
      long[] r = t.get(i);
      if (r[1] >= lo && r[0] <= hi) { hit.add(names.get(i)); if (h.distance != 0) { h.distance = 0; h.nearest = names.get(i); } continue; }
      long d = r[1] < lo ? lo - r[1] - 1 : r[0] - hi - 1;
      if (d < h.distance) { h.distance = d; h.nearest = names.get(i); }
    }
    h.targets = String.join(" ", hit); h.any = !hit.isEmpty();
    return h;
  }
  // sp-relative interval [olo, ohi] against the current frame and the stack-top windows
  Hit spHits(FC fc, long olo, long ohi) {
    Hit h = new Hit(); List<String> hit = new ArrayList<>();
    if (fc.raOff >= 0) {
      if (ohi >= fc.raOff && olo <= fc.raOff + 3) hit.add("FRAME-RA");
      if (ohi >= fc.raOff + 4 && olo <= fc.frameTop - 1) hit.add("FRAME-SAVED");
      if (ohi >= fc.frameTop) hit.add("ABOVE-FRAME");
      h.distance = Math.max(0, fc.raOff - ohi - 1); h.nearest = "FRAME-RA(sp+" + hex(fc.raOff) + ")";
    } else {
      if (ohi >= 0) hit.add("ABOVE-FRAME");
      h.distance = Math.max(0, -ohi - 1); h.nearest = "caller frame (RA kept in lp)";
    }
    if (ohi > -STACK_WIN) hit.add("STACKWIN?(depth-dependent)");
    h.targets = String.join(" ", hit); h.any = !hit.isEmpty();
    return h;
  }

  String idxClassOf(List<Term> terms, FC fc) {
    if (terms.isEmpty()) return "none (exact address)";
    List<String> out = new ArrayList<>();
    for (Term t : terms) {
      String c = cls(t.v, 0, new HashSet<>(), fc);
      if (t.scale == 1) out.add(c); else out.add((t.scale < 0 ? "-" + hex(-t.scale) + "*" : hex(t.scale) + "*") + c);
    }
    return String.join(" + ", out);
  }

  static final class CallerEv { String text = ""; int sites, constSites, callers; boolean allConst; long maxConst; }
  CallerEv callerEvidence(Function f, long regOff) {
    CallerEv ce = new CallerEv();
    List<long[]> sites = sitesOf.getOrDefault(f.getEntryPoint().getOffset() & U32, Collections.emptyList());
    ce.callers = callersOf.getOrDefault(f.getEntryPoint().getOffset() & U32, Collections.emptySet()).size();
    if (sites.isEmpty()) { ce.text = "no static call site"; return ce; }
    FunctionManager fm = currentProgram.getFunctionManager();
    List<String> consts = new ArrayList<>(), cmps = new ArrayList<>(), srcs = new ArrayList<>(); int n = 0, nc = 0;
    Register want = currentProgram.getRegister(toAddr(regOff));
    if (want == null) { ce.text = "register?"; return ce; }
    for (long[] s : sites) {
      Function c = fm.getFunctionAt(toAddr(s[0])); if (c == null) continue;
      Instruction k = getInstructionAt(toAddr(s[1])); if (k == null) continue;
      n++;
      Register trace = want; String kind = "reg32", cmp = null; long cval = 0; boolean isConst = false; int steps = 0; Instruction cur = k;
      while (steps++ < 48) {
        cur = cur.getPrevious(); if (cur == null || !c.getBody().contains(cur.getAddress())) break;
        String m = cur.getMnemonicString();
        if ((m.equals("cmp") || m.equals("tst")) && cmp == null) {
          boolean hit = false;
          for (int op = 0; op < cur.getNumOperands(); op++) for (Object o : cur.getOpObjects(op)) if (o instanceof Register && ((Register) o).equals(want)) hit = true;
          if (hit) cmp = cur.getAddress().toString();
        }
        if (!writesRegister(cur, trace)) continue;
        isConst = false;
        if (m.equals("mov")) {
          Object[] so = cur.getOpObjects(0);
          if (so.length > 0 && so[0] instanceof Scalar) { cval = ((Scalar) so[0]).getSignedValue(); isConst = true; break; }
          if (so.length > 0 && so[0] instanceof Register) { trace = (Register) so[0]; continue; }
          kind = "reg32"; break;
        }
        if (m.equals("movea") || m.equals("addi") || m.equals("ori")) {
          Scalar sc = null; boolean r0 = false;
          for (Object o : cur.getOpObjects(0)) if (o instanceof Scalar) sc = (Scalar) o;
          for (Object o : cur.getOpObjects(1)) if (o instanceof Register && ((Register) o).getOffset() == OFF_R0) r0 = true;
          if (sc != null && (r0 || m.equals("ori"))) { cval = sc.getSignedValue(); isConst = true; break; }
          kind = "derived"; break;
        }
        if (m.equals("zxb") || m.equals("zxh")) { kind = m; continue; }
        if (m.startsWith("ld.bu") || m.startsWith("ld.hu")) { kind = m.startsWith("ld.bu") ? "u8 data" : "u16 data"; break; }
        if (m.equals("jarl") || m.equals("jmp") || m.equals("br") || m.startsWith("b") && CONDS.contains(m.substring(1))) { kind = "not set in window"; break; }
        kind = "reg32"; break;
      }
      srcs.add(isConst ? "const" : kind);
      if (cmp != null) cmps.add(String.format("%x@%s", s[0], cmp));
      else if (isConst) { nc++; consts.add(String.format("%s@%x:%x", hex(cval), s[0], s[1])); ce.maxConst = Math.max(ce.maxConst, cval); }
    }
    ce.sites = n; ce.constSites = nc; ce.allConst = n > 0 && nc == n && n >= ce.callers;
    LinkedHashSet<String> s = new LinkedHashSet<>(srcs);
    StringBuilder sb = new StringBuilder(String.format("callers=%d", ce.callers));
    sb.append(" arg-source=").append(s.isEmpty() ? "?" : String.join("/", s));
    if (!consts.isEmpty()) sb.append(" const-sites=").append(nc).append('/').append(n).append(" [").append(String.join(",", consts.subList(0, Math.min(consts.size(), 4)))).append(']');
    if (!cmps.isEmpty()) sb.append(" caller-cmp(linear)=[").append(String.join(",", cmps.subList(0, Math.min(cmps.size(), 4)))).append(']');
    ce.text = sb.toString();
    return ce;
  }

  void classify(Row r) {
    FC fc = r.fc;
    Set<Varnode> tree = new HashSet<>(), boundTree = new HashSet<>();
    for (Term t : r.terms) collectTree(t.v, tree, 0);
    Address S = toAddr(r.pc);
    Idx coarse = idxRange(r.terms, Collections.emptyMap(), fc);
    long cspan = coarse.max - coarse.min;
    List<Cand> cands = new ArrayList<>();
    String mask = null;
    for (Term t : r.terms) {
      Varnode d = descend(t.v); PcodeOp op = d.getDef();
      if (op == null) continue;
      int c = op.getOpcode();
      if (c == PcodeOp.INT_AND || c == PcodeOp.INT_REM || c == PcodeOp.INT_SREM) {
        Varnode k = op.getInput(1).isConstant() ? op.getInput(1) : (op.getInput(0).isConstant() ? op.getInput(0) : null);
        if (k != null && (k.getOffset() & U32) != 0) mask = String.format("%s 0x%x @%s", PcodeOp.getMnemonic(c).toLowerCase().replace("int_", ""), k.getOffset() & U32, op.getSeqnum().getTarget());
      }
    }
    for (Cmp c : fc.cmps) {
      for (int side = 0; side < 2; side++) {
        Varnode x = side == 0 ? c.a : c.b;
        if (x == null || x.isConstant() || isGp(x) || isTp(x) || isR0(x)) continue;
        Varnode nV = side == 0 ? c.b : c.a;
        boolean nImm = side == 0 && c.bImm;
        if (!nImm && nV == null) continue;
        int rel = side == 0 ? relOf(c.cond) : converse(relOf(c.cond));
        if (rel == R_NONE) continue;
        if (c.viaAddi && (rel == R_LTU || rel == R_GEU || rel == R_LEU || rel == R_GTU)) continue;
        boolean viaT = reaches(fc, c.tgt, c.br.getAddress(), S), viaF = reaches(fc, c.fall, c.br.getAddress(), S);
        if (!viaT && !viaF) continue;
        Rg xn = rng(x, Collections.emptyMap(), new HashSet<>(), 0, fc);
        if (!xn.ok() || xn.lo == xn.hi) continue;
        Rg nr = nImm ? Rg.cst(c.imm & U32) : boundRange(nV, fc);
        if (!nImm) collectTree(nV, boundTree, 0);
        Varnode tgt = tree.contains(x) ? x : narrowLeaf(x, tree);
        boolean direct = tgt != null;
        PhiLink link = direct ? null : derivePhi(x, tree);
        boolean backEdge = c.tgt != null && c.tgt.compareTo(c.br.getAddress()) <= 0;
        boolean inBody = backEdge && S.compareTo(c.tgt) >= 0 && S.compareTo(c.br.getAddress()) <= 0;
        String boundTxt = nImm ? hex(c.imm) : cls(nV, 0, new HashSet<>(), fc);
        String how = String.format("%s@%s [%s %s %s] b%s@%s", c.ci.getMnemonicString(), c.at, leafText(x, fc), relText(rel), boundTxt, c.cond, c.br.getAddress());
        if (viaT && (direct || inBody)) {
          Rg bx = applyRel(xn, rel, nr);
          if (bx != null) {
            Map<Varnode, Rg> ov = new HashMap<>(); boolean ok = false, loop;
            if (direct) { Rg t2 = rng(tgt, Collections.emptyMap(), new HashSet<>(), 0, fc).inter(bx); if (t2.ok()) { ov.put(tgt, t2); ok = true; } loop = isPhi(tgt); }
            else if (link != null) { Rg pb = invertG(link.g, bx); if (pb != null) { ov.put(link.phi, phiInitRange(link.phi, fc).hull(pb)); ok = true; } loop = true; }
            else loop = false;
            if (ok) { Idx ti = idxRange(r.terms, ov, fc); cands.add(new Cand(loop ? "LOOP" : "DATA", ti.min, ti.max, how + " true-edge", nImm, boundTxt, ov)); }
          }
        }
        if (viaF && direct) {
          Rg bx = applyRel(xn, negate(rel), nr);
          if (bx != null) {
            Rg t2 = rng(tgt, Collections.emptyMap(), new HashSet<>(), 0, fc).inter(bx);
            if (t2.ok()) { Map<Varnode, Rg> ov = new HashMap<>(); ov.put(tgt, t2); Idx ti = idxRange(r.terms, ov, fc);
              cands.add(new Cand(isPhi(tgt) ? "LOOP" : "DATA", ti.min, ti.max, how + " false-edge", nImm, boundTxt, ov)); }
          }
        }
      }
    }
    // clamps: a phi of the index tree that selects between the compared value
    // and the immediate it is compared against (min(len, N) selects)
    for (Varnode v : tree) {
      if (!isPhi(v)) continue;
      Clamp cl = clampRange(v, fc);
      if (cl == null) continue;
      Map<Varnode, Rg> ov = new HashMap<>(); ov.put(v, cl.rg);
      Idx ti = idxRange(r.terms, ov, fc);
      if (ti.max - ti.min >= cspan) continue;
      cands.add(new Cand("CLAMP", ti.min, ti.max, "clamp " + cl.how, true, cl.how, ov));
    }
    // tightest single constraint, then combine constraints on other varnodes
    Cand best = null;
    for (Cand k : cands) {
      if (k.span() >= cspan) continue;
      if (best == null || k.span() < best.span() || (k.span() == best.span() && k.imm && !best.imm)) best = k;
    }
    if (best != null) {
      for (int round = 0; round < 4; round++) {
        Cand add = null;
        for (Cand k : cands) {
          if (k.span() >= best.span() || !Collections.disjoint(k.ov.keySet(), best.ov.keySet())) continue;
          Map<Varnode, Rg> ov = new HashMap<>(best.ov); ov.putAll(k.ov);
          Idx ti = idxRange(r.terms, ov, fc);
          if (ti.max - ti.min >= best.span()) continue;
          if (add == null || ti.max - ti.min < add.span()) add = new Cand(best.kind + "+" + k.kind, ti.min, ti.max, best.how + " & " + k.how, best.imm && k.imm, best.bound + ";" + k.bound, ov);
        }
        if (add == null) break;
        best = add;
      }
    }
    // caller evidence for parameter leaves
    Set<Long> argRegs = new TreeSet<>();
    for (Varnode v : tree) if (v.isRegister() && v.getDef() == null && isArg(v)) argRegs.add(v.getOffset());
    for (Varnode v : boundTree) if (v.isRegister() && v.getDef() == null && isArg(v)) argRegs.add(v.getOffset());
    StringBuilder cb = new StringBuilder(); CallerEv allConst = null;
    for (long off : argRegs) {
      CallerEv ce = callerEvidence(r.f, off);
      Register rr = currentProgram.getRegister(toAddr(off));
      if (cb.length() > 0) cb.append(" ; ");
      cb.append(rr == null ? hex(off) : rr.getName()).append(": ").append(ce.text);
      if (ce.allConst && allConst == null) allConst = ce;
    }
    r.callers = cb.toString();
    Idx ti;
    if (best != null) {
      ti = new Idx(); ti.min = best.min; ti.max = best.max;
      r.cls = best.imm && !best.kind.contains("DATA") ? "BOUNDED" : "DATA-BOUNDED-VALIDATED";
      r.evidence = best.how + (best.imm ? "" : " (bound from data " + best.bound + ")");
    } else if (mask != null) {
      ti = coarse; r.cls = "BOUNDED"; r.evidence = mask;
    } else if (allConst != null) {
      Map<Varnode, Rg> ov = new HashMap<>();
      for (Varnode v : tree) if (v.isRegister() && v.getDef() == null && isArg(v)) ov.put(v, Rg.cst(allConst.maxConst));
      ti = idxRange(r.terms, ov, fc); r.cls = "BOUNDED"; r.evidence = "const argument at all " + allConst.constSites + " static call sites (max " + hex(allConst.maxConst) + ")";
    } else {
      ti = coarse; r.cls = r.idxOpen ? "UNBOUNDED" : "DATA-BOUNDED-UNVALIDATED"; r.evidence = "";
    }
    long tMin = ti.min + r.idxOff, tMax = ti.max + r.idxOff;
    Hit th;
    if (r.spBased) { r.tight = String.format("sp%s..sp%s", signed(tMin), signed(tMax + r.width - 1)); th = spHits(fc, tMin, tMax + r.width - 1); }
    else { long tl = sat0(r.baseLo + tMin), thh = satU(r.baseHi + tMax + r.width - 1); r.tight = hex(tl) + ".." + hex(thh); th = absHits(tl, thh); }
    r.tightTargets = th.targets; r.tightClosed = !th.any;
    r.dataPath = r.idxClass + " <- " + r.origin + (r.callers.isEmpty() ? "" : " | " + r.callers);
    r.entries = entriesText(r.f);
  }

  PrintWriter writer(File f) throws IOException {
    return new PrintWriter(new BufferedWriter(new OutputStreamWriter(new FileOutputStream(f), "UTF-8")));
  }
  static String q(String s) {
    if (s == null) return "";
    String t = s.replace("\n", " ").replace("\r", "");
    return t.contains(",") || t.contains("\"") ? "\"" + t.replace("\"", "\"\"") + "\"" : t;
  }
  static String md(String s) { return s == null ? "" : s.replace("|", "\\|"); }

  public void run() throws Exception {
    String out = null; int max = -1;
    for (String a : getScriptArgs()) {
      if (a.equals("--rows")) printRows = true;
      else if (a.equals("--dump")) dump = true;
      else if (a.startsWith("--out=")) out = a.substring(6);
      else if (a.startsWith("--only=")) { only = new TreeSet<>(); for (String s : a.substring(7).split(",")) only.add(Long.decode(s) & U32); }
      else if (a.startsWith("--max=")) max = Integer.decode(a.substring(6));
      else throw new IllegalArgumentException("unknown argument " + a);
    }
    File src = getSourceFile() == null ? null : new File(getSourceFile().getAbsolutePath());
    // <repo>/ghidra/scripts/investigate/<script> -> <repo>
    File repo = src == null ? new File(".").getAbsoluteFile() : src.getParentFile().getParentFile().getParentFile().getParentFile();
    outDir = new File(out == null ? new File(repo, "build/out/targets/camry-8965F3307000/route2-20261123/reach").getPath() : out);
    outDir.mkdirs();
    spReg = currentProgram.getCompilerSpec().getStackPointer();
    List<String> ctxWriters = new ArrayList<>();
    InstructionIterator ai = currentProgram.getListing().getInstructions(true);
    while (ai.hasNext()) {
      Instruction i = ai.next();
      for (Object o : i.getResultObjects()) if (o instanceof Register) { String nm = ((Register) o).getName(); if (nm.equals("gp") || nm.equals("tp")) ctxWriters.add(String.format("%s %s %s", nm, i.getAddress(), i.toString().replaceAll("\\s+", " ").trim())); }
    }
    scanCallCells();
    // callback cells the baseline (§13.5) names for 0x8863E/0x8AF7A/0x8AF88/0x8AFAA;
    // their defining loads are farther back than either resolver here reaches
    for (long c : new long[]{0xFEBF1180L, 0xFEBF131CL, 0xFEBF1320L, 0xFEBF1324L})
      callCells.computeIfAbsent(c, k -> new ArrayList<>()).add(new CellSite(toAddr(0x8863EL), "(baseline 13.5)", c, "baseline-cited"));
    buildCallGraph();
    DecompInterface di = new DecompInterface(); di.openProgram(currentProgram);
    FunctionIterator fi = currentProgram.getFunctionManager().getFunctions(true);
    long fn = 0, stores = 0, unknown = 0, kConstVar = 0, kRegVar = 0, kUnresolved = 0, kWeird = 0, noDecomp = 0, processed = 0;
    TreeMap<String, Long> otherKinds = new TreeMap<>(), unresWhy = new TreeMap<>(), baseKinds = new TreeMap<>();
    while (fi.hasNext() && (max < 0 || processed < max)) {
      Function f = fi.next();
      long fno = f.getEntryPoint().getOffset() & U32;
      if (only != null && !only.contains(fno)) continue;
      processed++;
      DecompileResults dr = di.decompileFunction(f, 30, monitor); HighFunction hf = dr.getHighFunction();
      if (hf == null) { noDecomp++; continue; }
      fn++;
      FC fc = buildFc(f, hf);
      if (dump) {
        println("== " + f.getName() + " @" + hex(fno) + " app=" + fc.app + " gpKnown=" + fc.gpKnown + " tpKnown=" + fc.tpKnown + " ctxWriters=" + fc.ctxWriters + " frame=" + fc.frameTxt + " cmps=" + fc.cmps.size());
        for (Cmp c : fc.cmps) println(String.format("  CMP %s %s | a=%s b=%s%s | %s -> T=%s F=%s", c.at, c.ci.toString().replaceAll("\\s+", " "), c.a, c.b, c.bImm ? " imm=" + hex(c.imm) : "", c.br, c.tgt, c.fall));
      }
      Iterator<PcodeOpAST> it = hf.getPcodeOps();
      while (it.hasNext()) {
        PcodeOpAST op = it.next();
        int oc = op.getOpcode();
        if (oc == PcodeOp.CALLIND) {
          Varnode t = strip(op.getInput(0)); PcodeOp d = t.getDef();
          // the decompiler masks computed targets (jarl [rX] -> rX & ~1) before the load is seen
          for (int k = 0; k < 3 && d != null && d.getOpcode() == PcodeOp.INT_AND && (d.getInput(1).isConstant() || d.getInput(0).isConstant()); k++) {
            t = strip(d.getInput(1).isConstant() ? d.getInput(0) : d.getInput(1)); d = t.getDef();
          }
          List<PcodeOp> loads = new ArrayList<>();
          if (d != null && d.getOpcode() == PcodeOp.LOAD) loads.add(d);
          else if (d != null && d.getOpcode() == PcodeOp.MULTIEQUAL) for (Varnode in : d.getInputs()) { Varnode s = strip(in); if (s.getDef() != null && s.getDef().getOpcode() == PcodeOp.LOAD) loads.add(s.getDef()); }
          if (loads.isEmpty()) { callUnresolvedWhy.merge("pcode:" + (d == null ? "param" : PcodeOp.getMnemonic(d.getOpcode()).toLowerCase()), 1L, Long::sum); continue; }
          for (PcodeOp l : loads) {
            Rg q = rng(l.getInput(0), Collections.emptyMap(), new HashSet<>(), 0, fc);
            if (q.lo == q.hi && !q.open) noteCell(op.getSeqnum().getTarget(), f, q.lo, "pcode-load");
            else callUnresolvedWhy.merge("pcode:load-var", 1L, Long::sum);
          }
          continue;
        }
        if (oc != PcodeOp.STORE) continue;
        stores++;
        if (ev(op.getInput(1), 0, new HashSet<>()).known) continue;
        unknown++;
        String shape = base(op.getInput(1), 0, new HashSet<>()); String kind = kind(shape);
        boolean isRegVar = kind.startsWith("reg") && kind.contains("+var");
        if (!kind.equals("const+var") && !isRegVar) { otherKinds.merge(kind, 1L, Long::sum); continue; }
        if (kind.equals("const+var")) kConstVar++; else kRegVar++;
        Expr e = new Expr(); flat(op.getInput(1), 1, e, 0, fc);
        Varnode bo = baseOperand(op.getInput(1));
        Base b = resolveBase(bo, fc);
        if (isRegVar && b == null) {
          kUnresolved++; String wy = unresolvedWhy(bo); unresWhy.merge(wy, 1L, Long::sum);
          unresolvedRows.add(String.join(",", q(fc.app ? "app" : "boot"), q(hex(fno)), q(f.getName()), q(hex(op.getSeqnum().getTarget().getOffset())), q(kind), q(wy), q(shape)));
          if (dump) println(String.format("  UNRESOLVED %s %s | %s | %s", op.getSeqnum().getTarget(), kind, wy, shape));
          continue;
        }
        if ((e.spScale != 0 && e.spScale != 1) || (e.spScale == 1 && (b == null || !b.sp))) { kWeird++; if (dump) println("  WEIRD " + op.getSeqnum().getTarget() + " spScale=" + e.spScale); continue; }
        Row r = new Row(); r.fc = fc; r.f = f; r.app = fc.app; r.fn = fno; r.fnName = f.getName(); r.pc = op.getSeqnum().getTarget().getOffset() & U32;
        r.kind = kind; r.shape = shape; r.expr = op.getInput(1).toString().replaceAll("\\s+", ""); r.width = op.getInput(2).getSize();
        r.spBased = e.spScale == 1;
        List<Term> terms = new ArrayList<>(e.terms);
        if (r.spBased) { r.baseKind = "sp+const"; r.baseLo = r.baseHi = e.konst & U32; r.baseTxt = "sp" + (r.baseLo == 0 ? "" : signed(r.baseLo)); r.baseHow = b == null ? "sp" : b.how; r.idxOff = 0; }
        else if (isRegVar) {
          final Varnode bs = strip(bo); terms.removeIf(t -> t.v.equals(bs));
          long d = ((e.konst & U32) - b.lo) & U32; d = d >= 0x80000000L ? d - (1L << 32) : d;
          r.baseKind = b.kind; r.baseLo = (b.lo + d) & U32; r.baseHi = (b.hi + d) & U32; r.baseTxt = r.baseLo == r.baseHi ? hex(r.baseLo) : hex(r.baseLo) + ".." + hex(r.baseHi);
          r.baseHow = b.how + (d == 0 ? "" : String.format("%+d", d)); r.idxOff = 0;
        } else { r.baseKind = e.usedGp ? "const+gp" : (e.usedTp ? "const+tp" : "const"); r.baseLo = r.baseHi = e.konst & U32; r.baseTxt = hex(r.baseLo); r.baseHow = "const"; r.idxOff = 0; }
        r.terms = terms; r.stride = 0;
        for (Term t : terms) { long s = Math.abs(t.scale); if (s > r.stride) r.stride = s; }
        r.idxClass = idxClassOf(terms, fc);
        Idx ix = idxRange(terms, Collections.emptyMap(), fc);
        r.idxMin = ix.min + r.idxOff; r.idxMax = ix.max + r.idxOff; r.idxOpen = ix.open;
        r.origin = originText(terms, fc);
        Hit h;
        if (r.spBased) {
          r.spLo = r.idxMin; r.spHi = r.idxMax + r.width - 1; r.frameTxt = fc.frameTxt;
          r.lo = -1; r.hi = -1; h = spHits(fc, r.spLo, r.spHi);
        } else {
          r.lo = sat0(r.baseLo + r.idxMin); r.hi = satU(r.baseHi + r.idxMax + r.width - 1);
          h = absHits(r.lo, r.hi);
        }
        r.targets = h.targets; r.nearest = h.nearest; r.distance = h.distance; r.reach = h.any;
        baseKinds.merge(r.baseKind, 1L, Long::sum);
        if (r.reach) classify(r);
        rows.add(r);
        if (dump || printRows) println(String.format("  ROW %s %s base=%s idx=%s [%s..%s] %s reach=%s %s", op.getSeqnum().getTarget(), kind, r.baseTxt, r.idxClass, r.idxMin, r.idxMax, r.spBased ? "sp" : r.tight == null ? hex(r.lo) + ".." + hex(r.hi) : r.tight, r.reach ? r.targets : "-", r.reach ? r.cls + " " + r.evidence : ""));
      }
      if (fn % 500 == 0) println("progress functions=" + fn);
    }
    di.dispose();
    writeOutputs(ctxWriters, fn, stores, unknown, kConstVar, kRegVar, kUnresolved, kWeird, noDecomp, otherKinds, unresWhy, baseKinds);
  }

  void writeOutputs(List<String> ctxWriters, long fn, long stores, long unknown, long kConstVar, long kRegVar, long kUnresolved, long kWeird, long noDecomp,
                    TreeMap<String, Long> otherKinds, TreeMap<String, Long> unresolvedWhy, TreeMap<String, Long> baseKinds) throws IOException {
    long reachN = 0, noReachN = 0, reachApp = 0, noReachApp = 0, gpFixed = 0;
    TreeMap<String, Long> clsCount = new TreeMap<>();
    for (Row r : rows) {
      if (r.reach) { reachN++; if (r.app) reachApp++; clsCount.merge(r.cls, 1L, Long::sum); } else { noReachN++; if (r.app) noReachApp++; }
      if (r.terms.isEmpty()) gpFixed++;
    }
    PrintWriter w = writer(new File(outDir, "reach.csv"));
    w.println("region,function,fn_name,store_pc,kind,base_kind,base,base_def,elem,stride,width,index_class,index_lo,index_hi,reach_lo,reach_hi,targets,nearest_target,distance,verdict,class,evidence,tight_reach,tight_targets,tight_closed,origin,callers,entries");
    for (Row r : rows) {
      w.println(String.join(",",
          q(r.app ? "app" : "boot"), q(hex(r.fn)), q(r.fnName), q(hex(r.pc)), q(r.kind), q(r.baseKind), q(r.baseTxt), q(r.baseHow),
          q(r.idxClass), q(Long.toString(r.stride)), q(Integer.toString(r.width)), q(r.idxClass),
          q(r.spBased ? "sp" + signed(r.idxMin) : hexl(r.idxMin)), q(r.spBased ? "sp" + signed(r.idxMax) : hexl(r.idxMax)),
          q(r.spBased ? "sp" + signed(r.spLo) : hex(r.lo)), q(r.spBased ? "sp" + signed(r.spHi) : hex(r.hi)),
          q(r.targets), q(r.nearest), q(r.spBased ? "" : Long.toString(r.distance)), q(r.reach ? "REACH" : "NO-REACH"),
          q(r.reach ? r.cls : ""), q(r.evidence), q(r.tight), q(r.tightTargets), q(r.reach ? Boolean.toString(r.tightClosed) : ""),
          q(r.origin), q(r.callers), q(r.entries)));
    }
    w.close();
    PrintWriter u = writer(new File(outDir, "reach-unresolved-bases.csv"));
    u.println("region,function,fn_name,store_pc,kind,why,shape");
    for (String s : unresolvedRows) u.println(s);
    u.close();
    PrintWriter m = writer(new File(outDir, "reach-report.md"));
    m.println("# Reach filter for the unbounded-base stores (camry-8965F3307000)");
    m.println();
    m.println("Generated by `ghidra/scripts/investigate/ReachOfUnknownBaseStores.java` on the shared read-only Ghidra project. Companion data: `reach.csv` (one row per evaluated store) and `reach-unresolved-bases.csv`.");
    m.println();
    m.println("## 1. Totals");
    m.println();
    m.println("| quantity | value |");
    m.println("|---|---:|");
    m.println("| functions decompiled | " + fn + " (failed: " + noDecomp + ") |");
    m.println("| high-pcode STOREs | " + stores + " |");
    m.println("| stores the AuditComputedStoreTargets resolver cannot bound (TriageUnknownStoreBases set) | " + unknown + " |");
    m.println("| of which `const+var` | " + kConstVar + " |");
    m.println("| of which `reg+var` | " + kRegVar + " |");
    m.println("| `reg+var` base registers resolvable (constant, sp+const, gp+const, tp+const) | " + (kRegVar - kUnresolved - kWeird) + " |");
    m.println("| `reg+var` base registers unresolved (listed in reach-unresolved-bases.csv) | " + kUnresolved + " |");
    m.println("| stores evaluated | " + rows.size() + " |");
    m.println("| NO-REACH | " + noReachN + " (application " + noReachApp + ", boot " + (noReachN - noReachApp) + ") |");
    m.println("| REACH | " + reachN + " (application " + reachApp + ", boot " + (reachN - reachApp) + ") |");
    m.println();
    m.println("Base kinds of evaluated rows: " + baseKinds.entrySet().stream().map(en -> en.getKey() + "=" + en.getValue()).reduce((a, c) -> a + ", " + c).orElse("") + ". " + gpFixed + " rows have no variable term after GP/TP folding (the TriageUnknownStoreBases \"variable\" was the fixed GP/TP register); their address is exact.");
    m.println();
    m.println("Other unbounded kinds left out of scope (closed elsewhere or pointer-parameter stores): " + otherKinds.entrySet().stream().map(en -> en.getKey() + "=" + en.getValue()).reduce((a, c) -> a + ", " + c).orElse("none") + ".");
    m.println();
    m.println("Unresolved `reg+var` base kinds: " + unresolvedWhy.entrySet().stream().map(en -> en.getKey() + "=" + en.getValue()).reduce((a, c) -> a + ", " + c).orElse("none") + ".");
    m.println();
    m.println("## 2. Context and target set");
    m.println();
    m.println("GP/TP writers in the decoded instruction stream: " + String.join("; ", ctxWriters) + ". GP=" + hex(APP_GP) + " and TP=" + hex(APP_TP) + " are therefore treated as constants in functions at or above 0x20000, and GP=" + hex(BOOT_GP) + "/TP=" + hex(BOOT_TP) + " below it.");
    m.println();
    m.println("Computed `jarl`/`jmp` sites: " + callSites + "; resolved to a constant non-RAM target (direct address): " + callResolvedConst + "; nearest defining load hits a LocalRAM cell: " + callCells.size() + " distinct cells; unresolved: " + callUnresolved + " (" + callUnresolvedWhy.entrySet().stream().map(en -> en.getKey() + "=" + en.getValue()).reduce((a, c) -> a + ", " + c).orElse("") + ").");
    m.println();
    m.println("Call-target cells: " + callCells.keySet().stream().map(ReachOfUnknownBaseStores::hex).reduce((a, c) -> a + " " + c).orElse("none"));
    m.println();
    m.println("## 3. REACH classes");
    m.println();
    m.println("| class | count |");
    m.println("|---|---:|");
    for (Map.Entry<String, Long> en : clsCount.entrySet()) m.println("| " + en.getKey() + " | " + en.getValue() + " |");
    m.println();
    m.println("## 4. REACH table");
    m.println();
    m.println("| fn | pc | region | kind | base | elem/width | index class | coarse reach | coarse targets | class | evidence | tight reach | tight targets |");
    m.println("|---|---|---|---|---|---|---|---|---|---|---|---|---|");
    for (Row r : rows) {
      if (!r.reach) continue;
      m.println("| " + hex(r.fn) + " | " + hex(r.pc) + " | " + (r.app ? "app" : "boot") + " | " + r.kind + " | " + r.baseTxt + " | " + r.stride + "/" + r.width + " | " + md(r.idxClass) + " | " + (r.spBased ? "sp" + signed(r.spLo) + "..sp" + signed(r.spHi) : hex(r.lo) + ".." + hex(r.hi)) + " | " + md(r.targets) + " | " + r.cls + " | " + md(r.evidence) + " | " + md(r.tight) + " | " + md(r.tightTargets) + " |");
    }
    m.println();
    m.println("## 5. Remaining DATA-BOUNDED-UNVALIDATED and UNBOUNDED stores");
    m.println();
    List<Row> open = new ArrayList<>();
    for (Row r : rows) if (r.reach && (r.cls.equals("DATA-BOUNDED-UNVALIDATED") || r.cls.equals("UNBOUNDED"))) open.add(r);
    if (open.isEmpty()) m.println("None.");
    else {
      m.println("| fn | pc | region | base | index class | coarse reach | targets | class | data path | entries |");
      m.println("|---|---|---|---|---|---|---|---|---|---|");
      for (Row r : open) m.println("| " + hex(r.fn) + " | " + hex(r.pc) + " | " + (r.app ? "app" : "boot") + " | " + r.baseTxt + " | " + md(r.idxClass) + " | " + (r.spBased ? "sp" + signed(r.spLo) + "..sp" + signed(r.spHi) + " (" + md(r.frameTxt) + ")" : hex(r.lo) + ".." + hex(r.hi)) + " | " + md(r.targets) + " | " + r.cls + " | " + md(r.dataPath) + " | " + md(r.entries) + " |");
    }
    m.println();
    m.println("## 6. Bounded or validated REACH rows whose tight range still overlaps a target");
    m.println();
    List<Row> tightOpen = new ArrayList<>();
    for (Row r : rows) if (r.reach && !r.tightClosed && !r.cls.equals("DATA-BOUNDED-UNVALIDATED") && !r.cls.equals("UNBOUNDED")) tightOpen.add(r);
    if (tightOpen.isEmpty()) m.println("None.");
    else {
      m.println("| fn | pc | region | base | index class | class | evidence | tight reach | tight targets |");
      m.println("|---|---|---|---|---|---|---|---|---|");
      for (Row r : tightOpen) m.println("| " + hex(r.fn) + " | " + hex(r.pc) + " | " + (r.app ? "app" : "boot") + " | " + r.baseTxt + " | " + md(r.idxClass) + " | " + r.cls + " | " + md(r.evidence) + " | " + md(r.tight) + " | " + md(r.tightTargets) + " |");
    }
    m.println();
    m.println("## 7. Method and limits");
    m.println();
    m.println("- Coarse index bounds come from operand widths (zero-extended byte/halfword, sign extension, loaded widths), immediate masks, shifts and strides; a 32-bit value with none of these is `UNBOUNDED` and saturates the interval at 0xFFFFFFFF.");
    m.println("- A REACH row is classified by comparing every `cmp`/`tst` followed by a conditional branch in the same basic block against the index's SSA leaves: the branch edge through which the store is reachable (or, for a loop latch whose true edge is a back edge, induction from the phi inputs) gives the bound. `BOUNDED` means the bound or mask is an immediate; `DATA-BOUNDED-VALIDATED` names the validating compare and branch; caller evidence is a linear window before each static call site.");
    m.println("- The stack flag for sp-relative rows tests the saved `lp` at sp+4*imm (`prepare {list}, imm`), the saved-register area, and anything above the frame; the 512-byte windows below the five stack tops are tested literally for absolute intervals and depth-independently for sp-relative ones (`STACKWIN?`).");
    m.println("- Reachability from entries uses direct calls, unconditional tail jumps and fixed-immediate `jmp [rX]` thunks; interrupt handlers and callback-table dispatch appear as roots without static callers.");
    m.close();
    println(String.format("SUMMARY|functions=%d|stores=%d|unknown=%d|constVar=%d|regVar=%d|unresolvedBases=%d|evaluated=%d|noReach=%d|reach=%d|reachApp=%d", fn, stores, unknown, kConstVar, kRegVar, kUnresolved, rows.size(), noReachN, reachN, reachApp));
    for (Map.Entry<String, Long> en : clsCount.entrySet()) println("CLASS|" + en.getKey() + "|" + en.getValue());
    println("OUTPUT|" + outDir.getAbsolutePath());
  }
}
