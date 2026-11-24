//@category Analysis
// Reach filter for the STORE population whose pointer range the
// AuditComputedStoreTargets resolver cannot bound (the TriageUnknownStoreBases
// set). Read-only; writes reach.csv, reach-unresolved-bases.csv and
// reach-report.md into --out (default: the Camry route2 reach directory). With
// --deep it adds a second pass over the stores whose base register the first
// pass could not describe and writes reach-deep.csv and reach-deep.md.
//
// For every store at a constant base plus a variable index, and every store
// through a register pointer plus a variable index whose base register is
// defined in the same function as a constant, sp+const, gp+const or tp+const,
// the script computes a saturating reach interval from coarse index bounds
// (operand widths, sign extension, masks, shifts, strides), intersects it with
// the control-relevant target set, and classifies each REACH store by tracing
// the index to its origin (loop counter, parameter, loaded data).
//
// The deep pass (reach-deep.csv / reach-deep.md) takes every `reg+var` store
// whose base register resolveBase() cannot describe (base read from memory,
// merge of pointers, argument register, value returned by a call, integer
// conversion of one of those, or a ROM/RAM/stack cell the decompiler hands
// over without a defining op) and ranges the whole pointer expression with the
// engine in deep mode: a loaded pointer is followed to the cell it comes from
// (CodeFlash word, or a LocalRAM/stack cell answered from an index of the
// STOREs with a closed pointer range), an argument register is hulled over
// its static call sites, a call result over the callee's returns, and a
// loop-carried merge keeps its init. The coarse interval is tested against the
// control set with the first pass's machinery; a row that reaches is
// classified by classify() with the base term left in the index tree, so a
// compare on the pointer itself tightens it. Rows that cannot be excluded are
// flagged (class DATA-BOUNDED-UNVALIDATED or UNBOUNDED, or a tight interval
// that still ends on a control object) with an origin text a reviewer can
// follow; UNREACHABLE-CODE closes stores in functions nothing calls.
//
// The deep pass is research state. Known limits of its current output: a base
// read from a stack slot is closed wrongly (Ghidra's p-code hands over the
// slot's address in place of its contents, e.g. 0x8bf28); a pointer argument
// forwarded through a caller can collapse to a small range (0x4fc40); loop-
// carried pointers get no induction bound; and one hull over a table of
// offsets loses the correlation with the index bound. Rows it does not flag
// are closed only where their base is a constant, a CodeFlash cell, a width-
// bounded offset, or a term a named compare bounds.
//
// Usage: ... -- [--out DIR] [--only 0xA,0xB] [--rows] [--dump] [--deep]
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.mem.Memory;
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
  // deep pass: p-code carries a negative immediate as an unsigned word, so a
  // sum with one lands 2^32 too high; bring a range back below 2^32 when both
  // ends overshoot by exactly that wrap
  static final long O32 = 1L << 32;
  static Rg norm32(Rg r) {
    if (r.lo >= O32 && r.hi < O32 << 1) return new Rg(r.lo - O32, r.hi - O32, r.open);
    return r;
  }

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
      if (op == null) {
        if (deep) { Rg r = deepNoDef(v, fc, d); if (r != null) return r; }
        return Rg.unk(v.getSize());
      }
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
          // deep pass: a value that already fits the narrower low piece keeps its range
          if (deep && k.isConstant() && k.getOffset() == 0) {
            Rg a = rng(in, ov, seen, d + 1, fc);
            long m = (1L << (8 * (long) v.getSize())) - 1;
            if (a.lo >= 0 && a.hi <= m) return new Rg(a.lo, a.hi, a.open);
          }
          return new Rg(0, (1L << (8 * (long) v.getSize())) - 1, false);
        }
        case PcodeOp.PIECE: {
          Rg h = rng(op.getInput(0), ov, new HashSet<>(seen), d + 1, fc);
          if (h.lo == 0 && h.hi == 0) return rng(op.getInput(1), ov, seen, d + 1, fc);
          return Rg.unk(v.getSize());
        }
        case PcodeOp.INT_ADD: {
          Rg q = addR(rng(op.getInput(0), ov, new HashSet<>(seen), d + 1, fc),
              rng(op.getInput(1), ov, new HashSet<>(seen), d + 1, fc));
          return deep ? norm32(q) : q;
        }
        case PcodeOp.INT_SUB: {
          Rg q = subR(rng(op.getInput(0), ov, new HashSet<>(seen), d + 1, fc),
              rng(op.getInput(1), ov, new HashSet<>(seen), d + 1, fc));
          return deep ? norm32(q) : q;
        }
        case PcodeOp.INT_MULT: {
          Rg q = mulR(rng(op.getInput(0), ov, new HashSet<>(seen), d + 1, fc),
              rng(op.getInput(1), ov, new HashSet<>(seen), d + 1, fc));
          return deep ? norm32(q) : q;
        }
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
          if (deep) { Rg r = deepLoopPhi(v, op, ov, seen, d, fc); if (r != null) return r; }
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
          Rg q = subR(ra, rb);
          return deep ? norm32(q) : q;
        }
        case PcodeOp.PTRADD: {
          Rg p = rng(op.getInput(0), ov, new HashSet<>(seen), d + 1, fc);
          Rg i = rng(op.getInput(1), ov, new HashSet<>(seen), d + 1, fc);
          Rg s = rng(op.getInput(2), ov, new HashSet<>(seen), d + 1, fc);
          Rg q = addR(p, mulR(i, s));
          return deep ? norm32(q) : q;
        }
        default: break;
      }
      if (BOOL_OPS.contains(c) || CMP_OPS.contains(c)) return new Rg(0, 1, false);
      if (deep) { Rg r = deepOp(v, op, ov, seen, d, fc); if (r != null) return r; }
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
    // deep pass: every p-code op of the function, and the lazy predecessor map
    final List<PcodeOp> ops = new ArrayList<>();
    // deep pass: STORE ops by instruction address (first pass and on-demand contexts alike)
    final Map<Long, List<PcodeOp>> storeAt = new HashMap<>();
    final List<PcodeOp> calls = new ArrayList<>();   // CALL and CALLIND ops
    Map<Address, List<Address>> pred;
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
      fc.ops.add(op);
      if (op.getOpcode() == PcodeOp.STORE) fc.storeAt.computeIfAbsent(t.getOffset(), k -> new ArrayList<>()).add(op);
      if (op.getOpcode() == PcodeOp.CALL || op.getOpcode() == PcodeOp.CALLIND) fc.calls.add(op);
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
    // deep pass (reach-deep.csv)
    String why, bTxt; long bLo, bHi; boolean bOpen, flag, dead, noteOnly, stackSlot, pvClosed; String note = "";
    long tMin, tMax; boolean tiOpen, wraps;   // recorded by classify; used by the deep pass
    Map<Varnode, Rg> ov;                      // classify's overrides, for the deep pass per-value evaluation
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
      ti = new Idx(); ti.min = best.min; ti.max = best.max; r.ov = best.ov;
      r.cls = best.imm && !best.kind.contains("DATA") ? "BOUNDED" : "DATA-BOUNDED-VALIDATED";
      r.evidence = best.how + (best.imm ? "" : " (bound from data " + best.bound + ")");
    } else if (mask != null) {
      ti = coarse; r.cls = "BOUNDED"; r.evidence = mask;
    } else if (allConst != null && !deep) {
      Map<Varnode, Rg> ov = new HashMap<>();
      for (Varnode v : tree) if (v.isRegister() && v.getDef() == null && isArg(v)) ov.put(v, Rg.cst(allConst.maxConst));
      ti = idxRange(r.terms, ov, fc); r.cls = "BOUNDED"; r.evidence = "const argument at all " + allConst.constSites + " static call sites (max " + hex(allConst.maxConst) + ")";
      r.ov = ov;
    } else if (allConst != null) {
      // deep pass: the linear-window constant of the first pass is not trusted here; the argument keeps the hull of its call-site values
      ti = idxRange(r.terms, Collections.emptyMap(), fc);
      StringBuilder ab = new StringBuilder();
      for (Varnode v : tree) if (v.isRegister() && v.getDef() == null && isArg(v)) {
        Rg q = rng(v, Collections.emptyMap(), new HashSet<>(), 0, fc);
        if (ab.length() > 0) ab.append(", ");
        ab.append(regName(v)).append(" = ").append(q == null ? "?" : rngText(q, fc));
      }
      r.cls = ti.open ? "UNBOUNDED" : "BOUNDED"; r.evidence = "argument " + ab + " (hull of the static call sites)";
    } else {
      ti = coarse; r.cls = r.idxOpen ? "UNBOUNDED" : "DATA-BOUNDED-UNVALIDATED"; r.evidence = "";
    }
    long tMin = ti.min + r.idxOff, tMax = ti.max + r.idxOff;
    Hit th;
    if (r.spBased) { r.tight = String.format("sp%s..sp%s", signed(tMin), signed(tMax + r.width - 1)); th = spHits(fc, tMin, tMax + r.width - 1); }
    else { long tl = sat0(r.baseLo + tMin), thh = satU(r.baseHi + tMax + r.width - 1); r.tight = hex(tl) + ".." + hex(thh); th = absHits(tl, thh); }
    r.tightTargets = th.targets; r.tightClosed = !th.any;
    r.tMin = tMin; r.tMax = tMax; r.tiOpen = ti.open;
    r.dataPath = r.idxClass + " <- " + r.origin + (r.callers.isEmpty() ? "" : " | " + r.callers);
    r.entries = entriesText(r.f);
  }

  // ------------------------------------------------------------- deep pass
  // Range-engine mode: false during the first pass, true only while the deep
  // pass runs. rng() consults it exactly where the first pass returns an
  // unknown range for a base that resolveBase() cannot describe.
  boolean deep = false;
  static final long CELL_SPAN = 0x1000, ROM_TOP = 0x100000L;
  static final int FLOW_DEPTH = 3, MAX_CTX = 2500;
  // Writer index, built by the first pass and numeric only: a STORE is
  // (function, pc, k) with k its rank among the STORE ops at that pc, and the
  // deep pass resolves its value varnode again through ctxOf(), so nothing
  // from a first-pass decompilation is kept.
  static final class Wr { long fn, pc; int k, width; Rg ptr; }   // pointer with a closed range
  static final class Stk { long pc, off; int k, width;                               // sp-relative, entry-relative offset
    Stk(long p, int kk, int w, long o) { pc = p; k = kk; width = w; off = o; } }
  static final class PWr { long pc, off; int k, width;                               // live-in register + constant
    PWr(long p, int kk, int w, long o) { pc = p; k = kk; width = w; off = o; } }
  static final class Unres { FC fc; Function f; PcodeOp op; String kind, why, shape;
    Unres(FC c, Function g, PcodeOp o, String k, String w, String s) { fc = c; f = g; op = o; kind = k; why = w; shape = s; } }
  static final class SV { Varnode v; Rg rg; String text; List<Varnode> alts; }
  final Map<Long, List<Wr>> ramBuckets = new HashMap<>();       // 4 KiB bucket -> writers
  final List<Wr> wideWriters = new ArrayList<>();                // writers spanning more than 64 buckets
  final Map<Long, List<Stk>> stackWriters = new HashMap<>();     // function -> sp-relative stores
  final Map<String, List<PWr>> paramWriters = new HashMap<>();   // "function:register" -> stores through it
  final List<Unres> unres = new ArrayList<>();
  final List<Row> deepRows = new ArrayList<>();
  final Map<Long, FC> fcCache = new HashMap<>();
  final FC NOFC = new FC();
  final List<long[]> cellGuard = new ArrayList<>();
  final List<String> slotGuard = new ArrayList<>(), liveGuard = new ArrayList<>();
  final List<Long> retGuard = new ArrayList<>();
  final Set<String> flowGuard = new HashSet<>();
  final Map<String, Rg> liveCache = new HashMap<>(), memCache = new HashMap<>(), slotCache = new HashMap<>();
  final Map<Long, List<FlowHit>> flowCache = new HashMap<>();
  final Map<String, String> liveText = new HashMap<>();
  final Map<String, SV> siteCache = new HashMap<>();
  final Map<Long, Map<Long, Varnode>> liveInCache = new HashMap<>();
  final Map<Long, Boolean> deadCache = new HashMap<>(), takenCache = new HashMap<>();
  final LinkedHashSet<String> rowNotes = new LinkedHashSet<>();
  int liveDepth = 0, txtDepth = 0;
  final Set<Varnode> txtSeen = new HashSet<>();
  long rowDeadline = 0;
  DecompInterface di;

  static long s32(long k) { k &= U32; return k >= 0x80000000L ? k - (1L << 32) : k; }
  static long fnOf(FC fc) { return fc.entry.getOffset() & U32; }
  // a varnode in the stack space (Varnode.isAddress() is false there: it is true only for RAM-type spaces)
  static boolean isStackVn(Varnode v) { return v != null && !v.isRegister() && !v.isConstant() && !v.isUnique() && v.getAddress() != null && v.getAddress().isStackAddress(); }
  static String opPc(PcodeOp op) { return op.getSeqnum() == null ? "?" : hex(op.getSeqnum().getTarget().getOffset()); }
  static String cl(Row r) { return r.cls == null ? "" : r.cls; }
  static Rg hullR(Rg a, Rg b) { return b == null ? a : a == null ? b : a.hull(b); }
  Expr flatExpr(Varnode ptr, FC fc) { Expr e = new Expr(); flat(ptr, 1, e, 0, fc); return e; }
  // deep pass: the index text of all terms (loads with their resolution)
  String dtTerms(List<Term> terms, FC fc) {
    if (terms.isEmpty()) return "none (exact address)";
    List<String> out = new ArrayList<>();
    for (Term t : terms) {
      PcodeOp td = t.v.getDef();
      String s = td != null && td.getOpcode() == PcodeOp.LOAD ? dt(t.v, fc, 1) : dtExpr(t.v, fc, 0);
      out.add((t.scale == 1 ? "" : (t.scale < 0 ? "-" + hex(-t.scale) + "*" : hex(t.scale) + "*")) + s);
    }
    return String.join(" + ", out);
  }
  String dtExpr(Varnode v, FC fc, int d) {
    if (txtLen > TXT_BUDGET) return "..";
    String s = dtExpr0(v, fc, d); txtLen += s.length(); return s;
  }
  // deep pass: structural text of an expression (a LOAD's pointer is its
  // second input; constants near GP/TP as offsets)
  String dtExpr0(Varnode v, FC fc, int d) {
    if (v == null) return "?";
    if (d > 10 || txtDepth > 60) return "..";
    v = strip(v);
    if (v.isConstant()) return constText(v.getOffset(), fc);
    if (isGp(v)) return "gp"; if (isTp(v)) return "tp"; if (isR0(v)) return "0";
    if (isSp(v)) return "sp";
    PcodeOp op = v.getDef();
    if (op == null) {
      if (v.isRegister()) return (isArg(v) ? "arg " : "reg ") + regName(v);
      if (isStackVn(v)) return "[stack sp" + signed(s32(v.getOffset())) + "]";
      if (v.isAddress() && v.getAddress().isMemoryAddress()) return "cell " + constText(v.getAddress().getOffset(), fc);
      return v.toString().replaceAll("\\s+", "");
    }
    Varnode x = op.getNumInputs() > 0 ? op.getInput(0) : null, a = op.getNumInputs() > 1 ? op.getInput(1) : null, b = op.getNumInputs() > 2 ? op.getInput(2) : null;
    boolean xc = x != null && x.isConstant(), ac = a != null && a.isConstant(), bc = b != null && b.isConstant();
    int c = op.getOpcode();
    switch (c) {
      case PcodeOp.LOAD: return "[" + dtExpr(a, fc, d + 1) + "]";
      case PcodeOp.COPY: case PcodeOp.CAST: case PcodeOp.INDIRECT: return dtExpr(x, fc, d + 1);
      case PcodeOp.INT_ADD:
        if (ac) return dtExpr(x, fc, d + 1) + signed(s32(a.getOffset()));
        if (xc) return dtExpr(a, fc, d + 1) + signed(s32(x.getOffset()));
        return dtExpr(x, fc, d + 1) + "+" + dtExpr(a, fc, d + 1);
      case PcodeOp.INT_SUB: return dtExpr(x, fc, d + 1) + (ac ? signed(-s32(a.getOffset())) : "-" + dtExpr(a, fc, d + 1));
      case PcodeOp.PTRSUB:
        if (xc && (x.getOffset() & U32) == 0 && ac) return constText(a.getOffset(), fc);
        return dtExpr(x, fc, d + 1) + (ac ? signed(-s32(a.getOffset())) : "-" + dtExpr(a, fc, d + 1));
      case PcodeOp.PTRADD: return dtExpr(x, fc, d + 1) + "+" + dtExpr(a, fc, d + 1) + (!bc || b.getOffset() == 1 ? "" : "*" + hex(b.getOffset()));
      case PcodeOp.INT_MULT:
        if (ac) return dtExpr(x, fc, d + 1) + "*" + hex(a.getOffset());
        if (xc) return dtExpr(a, fc, d + 1) + "*" + hex(x.getOffset());
        break;
      case PcodeOp.INT_LEFT: if (ac) return dtExpr(x, fc, d + 1) + "<<" + (a.getOffset() & 31); break;
      case PcodeOp.INT_RIGHT: if (ac) return dtExpr(x, fc, d + 1) + ">>" + (a.getOffset() & 31); break;
      case PcodeOp.INT_SRIGHT: if (ac) return dtExpr(x, fc, d + 1) + ">>s" + (a.getOffset() & 31); break;
      case PcodeOp.INT_AND: if (ac) return dtExpr(x, fc, d + 1) + "&" + hex(a.getOffset()); break;
      case PcodeOp.INT_ZEXT: return "zext" + (8 * x.getSize()) + "(" + dtExpr(x, fc, d + 1) + ")";
      case PcodeOp.INT_SEXT: return "sext" + (8 * x.getSize()) + "(" + dtExpr(x, fc, d + 1) + ")";
      case PcodeOp.SUBPIECE: return "sub" + (ac ? a.getOffset() : "?") + "(" + dtExpr(x, fc, d + 1) + ")";
      case PcodeOp.MULTIEQUAL: case PcodeOp.CALL: case PcodeOp.CALLIND: return dt(v, fc, d + 1);
      default: break;
    }
    StringBuilder sb = new StringBuilder(PcodeOp.getMnemonic(c).toLowerCase()).append('(');
    for (int i = 0; i < op.getNumInputs(); i++) { if (i > 0) sb.append(','); sb.append(dtExpr(op.getInput(i), fc, d + 1)); }
    return sb.append(')').toString();
  }

  String constText(long v, FC fc) {
    v &= U32;
    if (fc.gpKnown && Math.abs(v - fc.gp) <= 0x8000) return "gp" + signed(s32(v - fc.gp));
    if (fc.tpKnown && Math.abs(v - fc.tp) <= 0x8000) return "tp" + signed(s32(v - fc.tp));
    return hex(v);
  }
  String rngText(Rg r, FC fc) {
    if (r == null) return "?";
    if (r.lo == r.hi) return constText(r.lo, fc);
    return (r.lo >= RAM_LO && r.lo <= RAM_HI ? constText(r.lo, fc) : hexl(r.lo)) + ".." + (r.hi >= RAM_LO && r.hi <= RAM_HI ? constText(r.hi, fc) : hexl(r.hi)) + (r.open ? " open" : "");
  }

  // entry-SP-relative offset of a pointer that is one fixed stack slot: sp+c
  // after the prologue, or a stack-space varnode, whose offset is already
  // entry-relative with the hardware sign (-0x28 is 12[sp] after
  // prepare {r25..r29,lp},7, whose frame is 4*imm + 4*registers). The
  // decompiler writes `movea c, sp, rN` as PTRSUB(sp, k) with that same
  // offset as k, not as a distance from sp. Constants added on top of either
  // form are folded. null otherwise.
  Long slotOf(Varnode v, FC fc) {
    long off = 0;
    for (int i = 0; i < 8 && v != null; i++) {
      v = strip(v);
      if (v == null) return null;
      if (isStackVn(v)) return s32(v.getOffset()) + off;
      PcodeOp op = v.getDef();
      if (op == null) return null;
      int c = op.getOpcode();
      Varnode a = op.getInput(0), b = op.getNumInputs() > 1 ? op.getInput(1) : null;
      boolean bc = b != null && b.isConstant();
      if (c == PcodeOp.PTRSUB && bc && a.isRegister() && isSp(a)) return s32(b.getOffset()) + off;
      if (c == PcodeOp.INT_ADD && bc) { off += s32(b.getOffset()); v = a; continue; }
      if (c == PcodeOp.INT_SUB && bc) { off -= s32(b.getOffset()); v = a; continue; }
      if (c == PcodeOp.PTRADD && bc && op.getNumInputs() > 2 && op.getInput(2).isConstant() && op.getInput(2).getOffset() == 1) { off += s32(b.getOffset()); v = a; continue; }
      if (c == PcodeOp.COPY || c == PcodeOp.CAST || (c == PcodeOp.PTRSUB && a.isConstant() && a.getOffset() == 0)) { v = c == PcodeOp.PTRSUB ? b : a; continue; }
      return null;
    }
    return null;
  }
  // offset of v relative to `anchor` when v is anchor plus a constant; null otherwise
  Long anchorShift(Varnode v, Varnode anchor, FC fc) {
    Expr e = flatExpr(v, fc);
    if (e.spScale != 0 || e.terms.size() != 1 || e.terms.get(0).scale != 1 || !e.terms.get(0).v.equals(anchor)) return null;
    return s32(e.konst);
  }

  // First pass: record a STORE for the deep pass. Pure bookkeeping (flat() and
  // rng() only), so no first-pass result changes. An sp-relative store keeps
  // its entry-relative slot; a store through a live-in register its register
  // and constant; every other store with a closed pointer range keeps that range.
  void indexWriter(Function f, FC fc, PcodeOp op) {
    Varnode ptr = op.getInput(1), val = op.getInput(2);
    long fno = f.getEntryPoint().getOffset() & U32, pc = op.getSeqnum().getTarget().getOffset() & U32;
    List<PcodeOp> at = fc.storeAt.get(pc);
    int k = at == null ? -1 : at.indexOf(op);
    Expr e = flatExpr(ptr, fc);
    Long slot = slotOf(ptr, fc);
    if (slot != null) { stackWriters.computeIfAbsent(fno, x -> new ArrayList<>()).add(new Stk(pc, k, val.getSize(), slot)); return; }
    if (e.spScale == 0 && e.terms.size() == 1 && e.terms.get(0).scale == 1 && e.terms.get(0).v.isRegister() && e.terms.get(0).v.getDef() == null) {
      paramWriters.computeIfAbsent(fno + ":" + e.terms.get(0).v.getOffset(), x -> new ArrayList<>()).add(new PWr(pc, k, val.getSize(), s32(e.konst))); return;
    }
    if (e.spScale != 0) return;
    Rg q = rng(ptr, Collections.emptyMap(), new HashSet<>(), 0, fc);
    if (q.open || !q.ok()) return;
    Wr w = new Wr(); w.fn = fno; w.pc = pc; w.k = k; w.width = val.getSize(); w.ptr = q;
    long b0 = q.lo >> 12, b1 = (q.hi + w.width - 1) >> 12;
    if (b1 - b0 > 64) wideWriters.add(w);
    else for (long b = b0; b <= b1; b++) ramBuckets.computeIfAbsent(b, x -> new ArrayList<>()).add(w);
  }
  // indexed writers whose bytes meet [lo, hi]
  List<Wr> writersOf(long lo, long hi) {
    LinkedHashSet<Wr> out = new LinkedHashSet<>();
    for (Wr w : wideWriters) if (w.ptr.lo <= hi && w.ptr.hi + w.width - 1 >= lo) out.add(w);
    for (long b = lo >> 12; b <= hi >> 12; b++) for (Wr w : ramBuckets.getOrDefault(b, Collections.<Wr>emptyList())) if (w.ptr.lo <= hi && w.ptr.hi + w.width - 1 >= lo) out.add(w);
    return new ArrayList<>(out);
  }
  // the value varnode of an indexed STORE, resolved in its function's context
  Varnode storeVal(long fn, long pc, int k) {
    FC f = ctxOf(fn);
    if (f == null) return null;
    List<PcodeOp> l = f.storeAt.get(pc);
    return l == null || k < 0 || k >= l.size() ? null : l.get(k).getInput(2);
  }

  // function context, decompiled on demand (callers, callees, writers)
  FC ctxOf(long a) {
    if (a < 0 || a > U32) return null;
    FC c = fcCache.get(a);
    if (c != null) return c == NOFC ? null : c;
    if (fcCache.size() > MAX_CTX) { fcCache.put(a, NOFC); return null; }
    Function f = currentProgram.getFunctionManager().getFunctionAt(toAddr(a));
    if (f != null) {
      DecompileResults dr = di.decompileFunction(f, 30, monitor);
      HighFunction hf = dr == null ? null : dr.getHighFunction();
      if (hf != null) { c = buildFc(f, hf); fcCache.put(a, c); return c; }
    }
    fcCache.put(a, NOFC);
    return null;
  }

  Long romBytes(long a, int size) {
    try {
      Address ad = toAddr(a);
      Memory mem = currentProgram.getMemory();
      if (!mem.contains(ad) || !mem.contains(ad.add(size - 1))) return null;
      byte[] b = new byte[size]; mem.getBytes(ad, b);
      long v = 0; for (int i = size - 1; i >= 0; i--) v = (v << 8) | (b[i] & 0xffL);
      return v;
    } catch (Exception e) { return null; }
  }
  Rg writerRange(Wr w, int d) {
    Varnode val = storeVal(w.fn, w.pc, w.k);
    return val == null ? Rg.unk(4) : rng(val, Collections.emptyMap(), new HashSet<>(), d + 1, ctxOf(w.fn));
  }
  Rg writerRange(PWr w, Map<Varnode, Rg> ov, FC cf, int d) {
    Varnode val = storeVal(fnOf(cf), w.pc, w.k);
    return val == null ? Rg.unk(4) : rng(val, ov, new HashSet<>(), d + 1, cf);
  }
  // Case 1/3. The value candidates of `size` bytes at the addresses of the
  // closed interval [lo, hi]: one range per cell of a CodeFlash interval, read
  // from program memory at the expression's stride (the gcd of its terms'
  // scales, at most MAX_CANDS cells, access-size aligned when the stride is
  // finer), or one range per writer of a LocalRAM interval of span at most
  // CELL_SPAN (the indexed writers, and the STOREs a callee of fc makes
  // through a pointer that fc hands it inside the interval, the interval on a
  // guard set). null when a candidate cannot be read.
  List<Rg> memCells(long lo, long hi, int size, long stride, FC fc, int d) {
    tick();
    if (hi < lo || hi + size - 1 > U32) return null;
    if (hi + size - 1 < ROM_TOP) {
      long g = Math.max(1, stride), start = lo, st = g;
      if (g < size) {
        start = ((lo + size - 1) / size) * size;
        for (int n = 0; (start - lo) % g != 0 && n < 16; n++) start += size;
        if ((start - lo) % g != 0) { start = ((lo + size - 1) / size) * size; st = size; }
        else st = g * size / gcd(g, size);
      }
      if (start > hi || (hi - start) / st >= MAX_CANDS) return null;
      List<Rg> out = new ArrayList<>();
      for (long c = start; c <= hi; c += st) {
        Long w = romBytes(c, size); if (w == null) return null;
        out.add(Rg.cst(w));
      }
      return out;
    }
    if (lo >= RAM_LO && hi + size - 1 <= RAM_HI) {
      if (hi - lo > CELL_SPAN) return null;
      String key = fnOf(fc) + ":" + lo + ":" + hi + ":" + size;
      if (memCache.containsKey(key)) { Rg c = memCache.get(key); return c == null ? null : new ArrayList<>(Collections.singletonList(c)); }
      for (long[] g : cellGuard) if (g[1] >= lo && g[0] <= hi) return null;
      List<Rg> acc = new ArrayList<>();
      cellGuard.add(new long[]{lo, hi});
      try {
        for (Wr w : writersOf(lo, hi + size - 1)) {
          FC wf = ctxOf(w.fn); Varnode val = wf == null ? null : storeVal(w.fn, w.pc, w.k);
          acc.add(val == null ? Rg.unk(4) : rng(val, Collections.emptyMap(), new HashSet<>(), d + 1, wf));
        }
        for (FlowHit h : flowHits(fc)) if (!h.stack && h.thi >= lo && h.tlo <= hi + size - 1) { Rg q = writerRange(h, d); acc.add(q == null ? Rg.unk(4) : q); }
      } finally { cellGuard.remove(cellGuard.size() - 1); }
      if (acc.isEmpty()) { if (cellGuard.isEmpty()) memCache.put(key, null); return null; }
      // a hull cut by the guard is wider than the real one, so caching it is safe
      if (cellGuard.isEmpty()) memCache.put(key, hullOf(acc));
      return acc;
    }
    return null;
  }
  Rg memRange(long lo, long hi, int size, long stride, FC fc, int d) { List<Rg> l = memCells(lo, hi, size, stride, fc, d); return l == null ? null : hullOf(l); }

  List<Stk> slotWriters(long fn, long off, int size) {
    List<Stk> out = new ArrayList<>(), ws = stackWriters.get(fn);
    if (ws != null) for (Stk w : ws) if (w.off <= off + size - 1 && w.off + w.width - 1 >= off) out.add(w);
    return out;
  }
  // Case 1/3, stack: hull of the values the function's own STOREs put in the
  // slot and of those a callee puts there through the slot's address
  Rg slotRange(long fn, long off, int size, FC fc, int d) {
    tick();
    String key = fn + ":" + off + ":" + size;
    if (slotGuard.contains(key) || d > 24) return null;
    if (slotCache.containsKey(key)) return slotCache.get(key);
    Rg acc = null;
    slotGuard.add(key);
    try {
      for (Stk w : slotWriters(fn, off, size)) {
        Varnode val = storeVal(fn, w.pc, w.k);
        acc = hullR(acc, val == null ? Rg.unk(4) : rng(val, Collections.emptyMap(), new HashSet<>(), d + 1, fc));
      }
      for (FlowHit h : flowHits(fc)) if (h.stack && h.thi >= off && h.tlo <= off + size - 1) acc = hullR(acc, writerRange(h, d));
    } finally { slotGuard.remove(slotGuard.size() - 1); }
    if (acc != null || slotGuard.isEmpty()) slotCache.put(key, acc);
    return acc;
  }

  static final class FlowHit { FC cf, cg; PWr w; Address at; long tlo, thi; boolean stack; }
  // STOREs that reach memory through a pointer `g` hands to a callee: a stack
  // slot of `g`, or a closed RAM range. The pointer is followed through at
  // most FLOW_DEPTH calls (a callee passing it on). Each hit names the storing
  // function, the call site, the STORE and the interval it meets. Computed
  // once per function.
  List<FlowHit> flowHits(FC g) {
    List<FlowHit> out = flowCache.get(fnOf(g));
    if (out != null) return out;
    out = new ArrayList<>();
    flowCache.put(fnOf(g), out);
    // the callee pointers are looked up to locate their STOREs, not to range
    // the row's base: notes raised here do not bear on the row
    LinkedHashSet<String> saved = new LinkedHashSet<>(rowNotes); rowNotes.clear();
    try {
      for (PcodeOp op : g.calls) {
        long target = callTarget(op, Collections.emptyMap(), new HashSet<>(), 0, g);
        if (target < 0) continue;
        FC cf = ctxOf(target);
        if (cf == null) continue;
        Address at = op.getSeqnum().getTarget();
        for (Map.Entry<Long, Varnode> en : liveIns(cf).entrySet()) {
          SV s = valueAt(g, at, en.getKey(), 0);
          if (s == null || s.v == null) continue;
          Long so = slotOf(s.v, g);
          if (so != null) chain(out, g, at, cf, en.getKey(), en.getValue(), so, null, 0, new HashSet<>());
          else if (s.rg != null && !s.rg.open && s.rg.ok()) chain(out, g, at, cf, en.getKey(), en.getValue(), null, s.rg, 0, new HashSet<>());
        }
      }
    } finally { rowNotes.clear(); rowNotes.addAll(saved); }
    return out;
  }
  // the STOREs `cf` makes through its live-in register ro (the pointer
  // `anchor`), then those of whatever cf passes the pointer on to
  void chain(List<FlowHit> out, FC cg, Address at, FC cf, long ro, Varnode anchor, Long slot, Rg rg, int d, Set<String> guard) {
    for (PWr w : paramWriters.getOrDefault(fnOf(cf) + ":" + ro, Collections.<PWr>emptyList())) {
      FlowHit h = new FlowHit(); h.cf = cf; h.cg = cg; h.at = at; h.w = w; h.stack = slot != null;
      h.tlo = (slot != null ? slot : rg.lo) + w.off; h.thi = (slot != null ? slot : rg.hi) + w.off + w.width - 1;
      out.add(h);
    }
    if (d >= FLOW_DEPTH) return;
    tick();
    for (PcodeOp op : cf.calls) {
      long target = callTarget(op, Collections.emptyMap(), new HashSet<>(), 0, cf);
      if (target < 0) continue;
      FC c2 = ctxOf(target);
      if (c2 == null) continue;
      Address at2 = op.getSeqnum().getTarget();
      for (Map.Entry<Long, Varnode> en : liveIns(c2).entrySet()) {
        SV s = valueAt(cf, at2, en.getKey(), 0);
        if (s == null || s.v == null) continue;
        Long sh = anchorShift(s.v, anchor, cf);
        if (sh == null) continue;
        String key = fnOf(c2) + ":" + en.getKey();
        if (guard.add(key)) {
          try { chain(out, cf, at2, c2, en.getKey(), en.getValue(), slot == null ? null : slot + sh, rg == null ? null : rg.shift(sh), d + 1, guard); }
          finally { guard.remove(key); }
        }
      }
    }
  }
  Rg writerRange(FlowHit h, int d) {
    Varnode val = storeVal(fnOf(h.cf), h.w.pc, h.w.k);
    return val == null ? Rg.unk(4) : rng(val, callArgs(h.cg, h.at, h.cf, 0), new HashSet<>(), d + 1, h.cf);
  }

  // registers read without a definition in fc: arguments and callee-saved live-ins
  Map<Long, Varnode> liveIns(FC fc) {
    Map<Long, Varnode> m = liveInCache.get(fnOf(fc));
    if (m != null) return m;
    m = new HashMap<>();
    for (PcodeOp op : fc.ops) for (Varnode in : op.getInputs())
      if (in.isRegister() && in.getSize() == 4 && in.getDef() == null && !isGp(in) && !isTp(in) && !isR0(in) && !isSp(in)) m.putIfAbsent(in.getOffset(), in);
    liveInCache.put(fnOf(fc), m);
    return m;
  }
  Map<Address, List<Address>> predOf(FC fc) {
    if (fc.pred == null) {
      fc.pred = new HashMap<>();
      for (Map.Entry<Address, List<Address>> en : fc.succ.entrySet()) for (Address t : en.getValue()) fc.pred.computeIfAbsent(t, k -> new ArrayList<>()).add(en.getKey());
    }
    return fc.pred;
  }
  // instructions from which `at` is reachable through the known edges
  Set<Address> reaching(FC fc, Address at) {
    Set<Address> seen = new HashSet<>(); Deque<Address> q = new ArrayDeque<>(); q.add(at); seen.add(at);
    while (!q.isEmpty()) { Address a = q.poll(); for (Address p : predOf(fc).getOrDefault(a, NO)) if (seen.add(p)) q.add(p); }
    return seen;
  }
  // first instruction of the straight-line block that holds `at`; a call ends
  // the block unless ro is one of r20..r29, which a callee preserves
  Address blockStart(FC fc, Address at, long ro) {
    boolean saved = ro >= 0x50 && ro <= 0x74;
    Address s = at;
    while (true) {
      Instruction p = getInstructionBefore(s);
      if (p == null || fc.branchTargets.contains(s) || p.getFlowType().isJump() || (!saved && p.getFlowType().isCall())
          || !fc.succ.getOrDefault(p.getAddress(), NO).equals(Collections.singletonList(s))) break;
      s = p.getAddress();
    }
    return s;
  }
  Varnode blockWrite(FC fc, long ro, Address at) {
    Address s = blockStart(fc, at, ro);
    Varnode best = null; long bt = -1; int bo = -1;
    for (PcodeOp op : fc.ops) {
      Varnode o = op.getOutput();
      if (o == null || !o.isRegister() || o.getSize() != 4 || o.getOffset() != ro) continue;
      long t = op.getSeqnum().getTarget().getOffset();
      if (t < s.getOffset() || t >= at.getOffset()) continue;
      int q = op.getSeqnum().getOrder();
      if (t > bt || (t == bt && q > bo)) { best = o; bt = t; bo = q; }
    }
    return best;
  }
  Varnode callInputReg(FC cfc, Address at, long ro) {
    Varnode out = null;
    for (PcodeOp op : cfc.opsAt.getOrDefault(at, Collections.<PcodeOp>emptyList())) {
      if (op.getOpcode() != PcodeOp.CALL && op.getOpcode() != PcodeOp.CALLIND) continue;
      for (int k = 1; k < op.getNumInputs(); k++) { Varnode in = op.getInput(k); if (in.isRegister() && in.getSize() == 4 && in.getOffset() == ro) out = in; }
    }
    return out;
  }
  // value of register ro at address `at` of cfc: the call op's own input when
  // it lists the register, else the last write in the straight-line block
  // before `at`, else the function's live-in hulled with every write of the
  // register in a block from which `at` is reachable
  SV valueAt(FC cfc, Address at, long ro, int d) {
    String key = fnOf(cfc) + ":" + at.getOffset() + ":" + ro;
    SV c = siteCache.get(key); if (c != null) return c;
    SV s = new SV();
    s.v = callInputReg(cfc, at, ro);
    if (s.v == null) s.v = blockWrite(cfc, ro, at);
    if (s.v != null) s.rg = rng(s.v, Collections.emptyMap(), new HashSet<>(), d + 1, cfc);
    else {
      s.alts = new ArrayList<>();
      s.rg = liveInRange(ro, cfc, d);
      if (s.rg == null) s.rg = Rg.unk(4);
      Address bs = blockStart(cfc, at, ro);
      Set<Address> rs = cfc.openSucc.isEmpty() ? reaching(cfc, at) : null;
      for (PcodeOp op : cfc.ops) {
        Varnode o = op.getOutput();
        if (o == null || !o.isRegister() || o.getSize() != 4 || o.getOffset() != ro) continue;
        Address t = op.getSeqnum().getTarget();
        if (t.getOffset() >= bs.getOffset() && t.getOffset() < at.getOffset()) continue;
        if (rs != null && !rs.contains(t)) continue;
        s.alts.add(o);
        s.rg = s.rg.hull(rng(o, Collections.emptyMap(), new HashSet<>(), d + 1, cfc));
      }
    }
    siteCache.put(key, s);
    return s;
  }
  SV siteValue(long caller, long site, long ro, int d) { FC cfc = ctxOf(caller); return cfc == null ? null : valueAt(cfc, toAddr(site), ro, d); }
  String svText(SV s, FC cfc) {
    if (s == null) return "?";
    if (s.text == null) {
      StringBuilder sb = new StringBuilder();
      if (s.v != null) sb.append(dt(s.v, cfc, 1));
      else {
        sb.append("live-in");
        if (s.alts != null && !s.alts.isEmpty()) {
          sb.append(" or writes {");
          for (int i = 0; i < Math.min(4, s.alts.size()); i++) { if (i > 0) sb.append(", "); sb.append(hex(s.alts.get(i).getDef().getSeqnum().getTarget().getOffset())).append(':').append(dtExpr(s.alts.get(i), cfc, 0)); }
          if (s.alts.size() > 4) sb.append(", +").append(s.alts.size() - 4);
          sb.append('}');
        }
      }
      if (s.rg != null && (s.rg.lo != s.rg.hi || s.rg.open)) sb.append(" =").append(rngText(s.rg, cfc));
      s.text = sb.toString();
    }
    return s.text;
  }

  boolean addrTaken(long fn) {
    Boolean b = takenCache.get(fn); if (b != null) return b;
    boolean t = false;
    ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(toAddr(fn));
    while (it.hasNext()) if (it.next().getReferenceType().isData()) t = true;
    takenCache.put(fn, t); return t;
  }
  void noteTaken(long fn) {
    if (!addrTaken(fn)) return;
    rowNotes.add("argument hull of " + hex(fn) + " covers its static call sites only; its entry is referenced as data, so indirect callers are possible");
  }

  // Case 2. A register read without a definition carries the caller's value at
  // the call: hull over the static call sites, each evaluated in its caller's
  // context (depth-limited, recursion through the call graph cut).
  Rg liveInRange(long ro, FC fc, int d) {
    tick();
    long fn = fnOf(fc); String key = fn + ":" + ro;
    if (liveGuard.contains(key) || liveDepth > 8) return null;
    if (liveCache.containsKey(key)) { noteTaken(fn); return liveCache.get(key); }
    List<long[]> sites = sitesOf.getOrDefault(fn, Collections.<long[]>emptyList());
    liveGuard.add(key); liveDepth++;
    Rg out = null; StringBuilder sb = new StringBuilder();
    try {
      if (sites.isEmpty()) sb.append("no static call site");
      else {
        TreeMap<Long, List<String>> by = new TreeMap<>();
        for (long[] s : sites) {
          SV q = siteValue(s[0], s[1], ro, d);
          if (q == null || q.rg == null) out = out == null ? Rg.unk(4) : out.hull(Rg.unk(4));
          else out = out == null ? q.rg : out.hull(q.rg);
          List<String> l = by.computeIfAbsent(s[0], k -> new ArrayList<>());
          if (l.size() < 6) l.add(hex(s[1]) + ":" + (q == null ? "?" : svText(q, ctxOf(s[0]))));
          else if (l.size() == 6) l.add("more");
        }
        int n = 0;
        for (Map.Entry<Long, List<String>> en : by.entrySet()) {
          if (n == 4) { sb.append(" | +").append(by.size() - 4).append(" callers"); break; }
          if (n++ > 0) sb.append(" | ");
          sb.append(hex(en.getKey())).append(" call sites ").append(String.join(", ", en.getValue()));
        }
      }
    } finally { liveDepth--; liveGuard.remove(liveGuard.size() - 1); }
    liveCache.put(key, out); liveText.put(key, sb.toString());
    noteTaken(fn);
    return out;
  }

  String callTargetText(PcodeOp op) {
    Varnode t = strip(op.getInput(0));
    if (t.isConstant()) return hex(t.getOffset());
    if (t.isAddress() && !isStackVn(t)) return hex(t.getAddress().getOffset());
    return "?";
  }
  long callTarget(PcodeOp op, Map<Varnode, Rg> ov, Set<Varnode> seen, int d, FC fc) {
    Varnode t = strip(op.getInput(0));
    if (op.getOpcode() == PcodeOp.CALL) {
      if (t.isConstant()) return t.getOffset() & U32;
      if (t.isAddress() && !isStackVn(t)) return t.getAddress().getOffset() & U32;
      return -1;
    }
    Rg q = rng(t, ov, new HashSet<>(seen), d + 1, fc);
    return q.lo == q.hi && !q.open ? q.lo : -1;
  }
  // the callee's live-in varnodes mapped to their values at the call site
  Map<Varnode, Rg> callArgs(FC fc, Address at, FC cf, int d) {
    Map<Varnode, Rg> mo = new HashMap<>();
    for (Map.Entry<Long, Varnode> en : liveIns(cf).entrySet()) { SV q = valueAt(fc, at, en.getKey(), d); if (q != null && q.rg != null) mo.put(en.getValue(), q.rg); }
    return mo;
  }
  // Case 4. The value a direct call returns: the callee's argument-register
  // varnodes take the call site's values, and the range is the hull over the
  // callee's RETURN inputs under that map.
  SV retInfo(Varnode v, PcodeOp op, Map<Varnode, Rg> ov, Set<Varnode> seen, int d, FC fc) {
    tick();
    SV out = new SV(); out.v = v; out.text = "ret of ? <- indirect call";
    long target = callTarget(op, ov, seen, d, fc);
    if (target < 0) return out;
    out.text = "ret of " + hex(target) + " <- recursive";
    if (retGuard.contains(target)) return out;
    FC cf = ctxOf(target);
    if (cf == null) return out;
    retGuard.add(target);
    try {
      Map<Varnode, Rg> mo = callArgs(fc, op.getSeqnum().getTarget(), cf, d);
      StringBuilder sb = new StringBuilder();
      for (Map.Entry<Long, Varnode> en : liveIns(cf).entrySet()) {
        if (sb.length() > 0) sb.append(", ");
        sb.append(regName(en.getValue())).append('=').append(svText(valueAt(fc, op.getSeqnum().getTarget(), en.getKey(), d), fc));
      }
      Register retReg = currentProgram.getRegister(toAddr(ARG_OFFS[4]));
      boolean anyRet = false;
      for (PcodeOp o : cf.ops) {
        if (o.getOpcode() != PcodeOp.RETURN) continue;
        anyRet = true;
        Rg q = null;
        for (int k = 1; k < o.getNumInputs(); k++) { Rg x = rng(o.getInput(k), mo, new HashSet<>(), d + 1, cf); q = q == null ? x : q.hull(x); }
        if (q == null) {
          Varnode rv = retReg == null ? null : blockWrite(cf, retReg.getOffset(), o.getSeqnum().getTarget());
          q = rv == null ? Rg.unk(4) : rng(rv, mo, new HashSet<>(), d + 1, cf);
        }
        out.rg = out.rg == null ? q : out.rg.hull(q);
      }
      if (!anyRet) out.rg = Rg.unk(4);
      out.text = "ret of " + hex(target) + " <- " + sb;
    } finally { retGuard.remove(retGuard.size() - 1); }
    return out;
  }

  // deep pass: a varnode without a defining op. A register is the caller's
  // value at the call; a default-space varnode is the ROM or RAM cell at its
  // address. A 4-byte stack-space varnode is never closed: the decompiler
  // hands over the address of a slot where the program loaded the slot's
  // contents with a word load (the LOAD is gone from the p-code), so the value
  // is unknown. A byte or halfword slot is still answered by its writers.
  Rg deepNoDef(Varnode v, FC fc, int d) {
    tick();
    if (v.isRegister()) {
      if (v.getSize() == 4 && !isSp(v)) return liveInRange(v.getOffset(), fc, d);
      return null;
    }
    if (isStackVn(v)) {
      if (v.getSize() == 4) { rowNotes.add("stack-slot base sp" + signed(s32(v.getOffset())) + ": " + stackCaveat(fc, s32(v.getOffset()))); return Rg.unk(4); }
      return slotRange(fnOf(fc), s32(v.getOffset()), v.getSize(), fc, d);
    }
    if (v.isAddress() && v.getAddress().isMemoryAddress()) {
      long a = v.getAddress().getOffset() & U32;
      return memRange(a, a, v.getSize(), v.getSize(), fc, d);
    }
    return null;
  }
  // deep pass: LOAD (the base is a pointer read from memory) and CALL results
  Rg deepOp(Varnode v, PcodeOp op, Map<Varnode, Rg> ov, Set<Varnode> seen, int d, FC fc) {
    tick();
    int c = op.getOpcode();
    if (c == PcodeOp.LOAD) {
      if (d > 24) return null;
      Long slot = slotOf(op.getInput(1), fc);
      if (slot != null) {
        if (v.getSize() == 4) { rowNotes.add("stack-slot base sp" + signed(slot) + ": " + stackCaveat(fc, slot)); return Rg.unk(4); }
        return slotRange(fnOf(fc), slot, v.getSize(), fc, d);
      }
      Rg a = rng(op.getInput(1), ov, new HashSet<>(seen), d + 1, fc);
      long g = 0;
      for (Term t : flatExpr(op.getInput(1), fc).terms) g = gcd(g, Math.abs(t.scale));
      if (!a.open && a.ok()) { Rg q = memRange(a.lo, a.hi, v.getSize(), g, fc, d); if (q != null) return q; }
      // one hull is not enough (open or too wide an address): the candidate cells one by one
      if (d <= 6 && !candGuard.contains(v)) {
        candGuard.add(v);
        try {
          boolean cached = ov.isEmpty() && candCache.containsKey(v);
          Cands cd = cached ? candCache.get(v) : loadCands(v, ov, fc, d);
          if (!cached && cd.complete && cellGuard.isEmpty()) candCache.put(v, cd);
          if (cd.complete && !cd.list.isEmpty()) return hullOf(cd.list);
        } finally { candGuard.remove(candGuard.size() - 1); }
      }
      return null;
    }
    if (c == PcodeOp.CALL || c == PcodeOp.CALLIND) return retInfo(v, op, ov, seen, d, fc).rg;
    return null;
  }
  // deep pass: P = phi(init.., P + c..). The back edge is cut by `seen`, so the
  // plain hull loses the init; with constant steps of one sign the values stay
  // on the init's side of it (no 32-bit wrap assumed).
  Rg deepLoopPhi(Varnode v, PcodeOp op, Map<Varnode, Rg> ov, Set<Varnode> seen, int d, FC fc) {
    boolean loop = false;
    for (Varnode in : op.getInputs()) { Set<Varnode> t = new HashSet<>(); collectTree(in, t, 0); if (t.contains(v)) loop = true; }
    if (!loop) return null;
    Rg init = null; boolean pos = false, neg = false;
    for (Varnode in : op.getInputs()) {
      Set<Varnode> t = new HashSet<>(); collectTree(in, t, 0);
      if (!t.contains(v)) { Rg q = rng(in, ov, new HashSet<>(seen), d + 1, fc); init = init == null ? q : init.hull(q); continue; }
      Expr e = flatExpr(in, fc);
      if (e.spScale != 0 || e.terms.size() != 1 || e.terms.get(0).scale != 1 || !e.terms.get(0).v.equals(v)) return null;
      long st = s32(e.konst);
      if (st > 0) pos = true; else if (st < 0) neg = true;
    }
    if ((pos && neg) || init == null) return null;
    if (!pos && !neg) return init;
    if (pos) return init.lo < 0 ? null : new Rg(init.lo, U32, true);
    return new Rg(0, init.hi, true);
  }

  // deep pass: origin text a reviewer can follow. The path guard cuts the
  // cycles a pointer chain has (load -> writer's value -> merge -> same load).
  String dt(Varnode v, FC fc, int d) {
    if (v == null) return "?";
    v = strip(v);
    if (v.isConstant()) return constText(v.getOffset(), fc);
    if (isGp(v)) return "gp"; if (isTp(v)) return "tp"; if (isR0(v)) return "0";
    if (isSp(v)) return "sp";
    if (d > 7 || txtDepth > 60 || txtLen > TXT_BUDGET) return "..";
    if (!txtSeen.add(v)) return "(see above)";
    txtDepth++;
    try { return dtBody(v, fc, d); } finally { txtDepth--; txtSeen.remove(v); }
  }
  static final int TXT_BUDGET = 60000, TXT_CAP = 4000;
  int txtLen = 0;
  static String cap(String s) { return s == null || s.length() <= TXT_CAP ? s : s.substring(0, TXT_CAP) + " ...(+" + (s.length() - TXT_CAP) + " chars)"; }
  // deep pass: absolute interval of the pointer for an index span [tMin, tMax]
  // around the constant. The sums are 32-bit two's complement: a span lying
  // wholly below 0 wraps to the top of the space, and one straddling 0 wraps
  // onto both ends, so its hull is the whole space.
  void absInt(Row r, long tMin, long tMax, boolean tight) {
    long rl = tMin, rh = tMax + r.width - 1;
    if (rh < 0) { rl += O32; rh += O32; }
    r.wraps = rl < 0 && rh >= 0;
    long lo = r.wraps ? 0 : sat0(rl), hi = r.wraps ? U32 : satU(rh);
    Hit h = absHits(lo, hi);
    if (tight) { r.tight = hex(lo) + ".." + hex(hi) + (r.wraps ? " (wraps)" : ""); r.tightTargets = h.targets; r.tightClosed = !h.any && !r.tiOpen; }
    else { r.lo = lo; r.hi = hi; r.targets = h.targets; r.nearest = h.nearest; r.distance = h.distance; r.reach = h.any; }
  }
  String dtBody(Varnode v, FC fc, int d) {
    PcodeOp op = v.getDef();
    if (op == null) {
      if (v.isRegister()) {
        String nm = (isArg(v) ? "arg " : "reg ") + regName(v);
        if (d > 1) return nm;
        liveInRange(v.getOffset(), fc, d);
        return nm + " <- " + liveText.getOrDefault(fnOf(fc) + ":" + v.getOffset(), "?");
      }
      if (isStackVn(v)) return slotText(fnOf(fc), s32(v.getOffset()), v.getSize(), fc, d);
      if (v.isAddress() && v.getAddress().isMemoryAddress()) {
        long a = v.getAddress().getOffset() & U32;
        return "cell " + constText(a, fc) + " " + memText(Rg.cst(a), v.getSize(), fc, d);
      }
      return v.toString().replaceAll("\\s+", "");
    }
    Expr fe = flatExpr(v, fc);
    if (fe.spScale == 1 && fe.terms.isEmpty()) return "sp" + signed(s32(fe.konst));
    int c = op.getOpcode();
    if (c == PcodeOp.LOAD) {
      Long slot = slotOf(op.getInput(1), fc);
      if (slot != null) return "load@" + opPc(op) + "[sp" + signed(slot) + "] " + slotText(fnOf(fc), slot, v.getSize(), fc, d);
      Rg a = rng(op.getInput(1), Collections.emptyMap(), new HashSet<>(), d + 1, fc);
      String cell = a.open ? dtExpr(op.getInput(1), fc, d + 1) : (a.lo == a.hi ? constText(a.lo, fc) : constText(a.lo, fc) + ".." + hex(a.hi));
      return "load@" + opPc(op) + "[" + cell + "] " + (a.open ? "unknown (address open)" : (a.span() > CELL_SPAN ? "unknown (address span > 0x1000)" : memText(a, v.getSize(), fc, d)));
    }
    if (c == PcodeOp.MULTIEQUAL) return phiText(v, op, fc, d);
    if (c == PcodeOp.CALL || c == PcodeOp.CALLIND) {
      SV s = retInfo(v, op, Collections.emptyMap(), new HashSet<>(), d, fc);
      return s.text + (s.rg == null ? " unknown" : " = " + rngText(s.rg, fc));
    }
    String s = dtExpr(v, fc, d);
    Set<Varnode> tree = new HashSet<>(); collectTree(v, tree, 0);
    LinkedHashSet<String> extra = new LinkedHashSet<>();
    for (Varnode t : tree) {
      PcodeOp td = t.getDef();
      if (td != null && td.getOpcode() == PcodeOp.LOAD) extra.add(dt(t, fc, d + 1));
      else if (td == null && !t.isRegister() && (isStackVn(t) || (t.isAddress() && t.getAddress().isMemoryAddress()))) extra.add(dt(t, fc, d + 1));
    }
    return s + (extra.isEmpty() ? "" : " <= " + String.join("; ", extra));
  }
  String phiText(Varnode v, PcodeOp op, FC fc, int d) {
    List<Varnode> inits = new ArrayList<>(), backs = new ArrayList<>();
    for (Varnode in : op.getInputs()) { Set<Varnode> t = new HashSet<>(); collectTree(in, t, 0); if (t.contains(v)) backs.add(in); else inits.add(in); }
    List<String> p = new ArrayList<>();
    for (Varnode in : inits) p.add(dt(in, fc, d + 1));
    if (backs.isEmpty()) return "phi@" + opPc(op) + "{" + String.join(", ", p) + "}";
    TreeSet<Long> steps = new TreeSet<>(); boolean unk = false;
    for (Varnode in : backs) {
      Expr e = flatExpr(in, fc);
      if (e.spScale == 0 && e.terms.size() == 1 && e.terms.get(0).scale == 1 && e.terms.get(0).v.equals(v)) steps.add(s32(e.konst)); else unk = true;
    }
    StringBuilder sb = new StringBuilder("loop phi@" + opPc(op) + " step ");
    if (unk) sb.append("?");
    else { boolean first = true; for (long s : steps) { if (!first) sb.append('/'); first = false; sb.append(signed(s)); } }
    return sb.append(" (init ").append(String.join(" | ", p)).append(')').toString();
  }
  String slotText(long fn, long off, int size, FC fc, int d) {
    StringBuilder sb = new StringBuilder("stack slot sp" + signed(off) + " (entry-relative)");
    if (size == 4) sb.append(": ").append(stackCaveat(fc, off));
    List<String> p = new ArrayList<>();
    for (Stk w : slotWriters(fn, off, size)) { Varnode val = storeVal(fn, w.pc, w.k); p.add("st@" + hex(w.pc) + "=" + (val == null ? "?" : dt(val, fc, d + 1))); }
    List<String> q = new ArrayList<>();
    for (FlowHit h : flowHits(fc)) {
      if (!h.stack || h.thi < off || h.tlo > off + size - 1 || q.size() >= 10) continue;
      Varnode val = storeVal(fnOf(h.cf), h.w.pc, h.w.k);
      q.add("st@" + hex(h.w.pc) + " in " + hex(fnOf(h.cf)) + " (arg of call@" + hex(h.at.getOffset()) + ")=" + (val == null ? "?" : dt(val, h.cf, d + 1)));
    }
    if (p.isEmpty() && q.isEmpty()) {
      sb.append(" no STORE found");
      for (PcodeOp op : fc.calls) {
        for (int k = 1; k < op.getNumInputs(); k++) {
          Long s = slotOf(op.getInput(k), fc);
          if (s != null && s == off) sb.append("; address passed to ").append(callTargetText(op)).append('@').append(opPc(op));
        }
      }
    }
    if (!p.isEmpty()) sb.append(" writers {").append(String.join(", ", p)).append('}');
    if (!q.isEmpty()) sb.append(" callee writers {").append(String.join(", ", q)).append('}');
    return sb.toString();
  }
  String memText(Rg a, int size, FC fc, int d) {
    long lo = a.lo, hi = a.hi; int step = Math.max(1, size);
    if (hi + size - 1 < ROM_TOP) {
      Rg r = memRange(lo, hi, size, Math.max(1, size), fc, d);
      if (r == null) return "unknown (not in program memory)";
      return lo == hi ? "ROM=" + constText(r.lo, fc) : "ROM[" + constText(lo, fc) + ".." + constText(hi, fc) + "] -> " + rngText(r, fc);
    }
    if (lo >= RAM_LO && hi + size - 1 <= RAM_HI) {
      List<String> p = new ArrayList<>();
      for (Wr w : writersOf(lo, hi + size - 1)) {
        FC wf = ctxOf(w.fn); Varnode val = storeVal(w.fn, w.pc, w.k);
        if (p.size() < 10) p.add("st@" + hex(w.pc) + "/" + hex(w.fn) + (w.ptr.lo == w.ptr.hi ? "" : "[" + constText(w.ptr.lo, wf == null ? fc : wf) + ".." + hex(w.ptr.hi) + "]") + "=" + (val == null || wf == null ? "?" : dt(val, wf, d + 1)));
      }
      if (p.size() == 10) p.add("more");
      List<String> q = new ArrayList<>();
      for (FlowHit h : flowHits(fc)) {
        if (h.stack || h.thi < lo || h.tlo > hi + size - 1 || q.size() >= 10) continue;
        Varnode val = storeVal(fnOf(h.cf), h.w.pc, h.w.k);
        q.add("st@" + hex(h.w.pc) + " in " + hex(fnOf(h.cf)) + " (arg of call@" + hex(h.at.getOffset()) + ")=" + (val == null ? "?" : dt(val, h.cf, d + 1)));
      }
      if (p.isEmpty() && q.isEmpty()) return "RAM no indexed writer";
      return (p.isEmpty() ? "" : "RAM writers {" + String.join(", ", p) + "}") + (q.isEmpty() ? "" : " callee writers {" + String.join(", ", q) + "}");
    }
    return "unknown (outside CodeFlash/LocalRAM)";
  }
  // every 4-byte-aligned word of the program image: a function address that
  // appears in data may sit in a table Ghidra has no reference for
  Set<Long> romWords() {
    try {
      Memory mem = currentProgram.getMemory();
      Address lo = mem.getMinAddress();
      long n = Math.min(ROM_TOP, mem.getMaxAddress().getOffset() - lo.getOffset() + 1);
      byte[] b = new byte[(int) n]; mem.getBytes(lo, b);
      Set<Long> s = new HashSet<>();
      for (int i = 0; i + 4 <= n; i += 4) s.add((b[i] & 0xffL) | (b[i + 1] & 0xffL) << 8 | (b[i + 2] & 0xffL) << 16 | (b[i + 3] & 0xffL) << 24);
      return s;
    } catch (Exception e) { return null; }
  }
  // UNREACHABLE-CODE: no static caller, no reference to the entry, its address
  // in no word of the image, neither a vector-table nor a known entry
  boolean deadFn(Function f) {
    long fn = f.getEntryPoint().getOffset() & U32;
    Boolean b = deadCache.get(fn); if (b != null) return b;
    boolean dead = !callersOf.containsKey(fn) && !vectorRefs.containsKey(fn);
    for (long k : KNOWN_ENTRIES) if (k == fn) dead = false;
    if (dead && currentProgram.getReferenceManager().getReferencesTo(f.getEntryPoint()).hasNext()) dead = false;
    if (dead) { Set<Long> rw = romWords(); if (rw == null || rw.contains(fn)) dead = false; }
    deadCache.put(fn, dead); return dead;
  }

  // The deep pass: every store the first pass left unresolved, with all terms
  // of its pointer expression (the base included) ranged by the deep engine.
  // One row at a time under a Throwable catch and a time budget: a failure
  // flags its row instead of taking the shared bridge down.
  void deepPass() throws IOException {
    deep = true;
    long t0 = System.currentTimeMillis(); int n = 0;
    for (Unres u : unres) {
      long tRow = System.currentTimeMillis();
      rowDeadline = tRow + 120000;
      Row r;
      try { r = deepRow(u); } catch (Throwable t) { r = failRow(u, t); }
      deepRows.add(r);
      if (System.currentTimeMillis() - tRow > 2000) println("deep slow row " + hex(r.pc) + " ms=" + (System.currentTimeMillis() - tRow));
      if (++n % 40 == 0) println("deep progress rows=" + n + " ms=" + (System.currentTimeMillis() - t0) + " contexts=" + fcCache.size());
    }
    deep = false;
    writeDeep();
  }

  void tick() { if (System.currentTimeMillis() > rowDeadline) throw new IllegalStateException("deep budget exhausted"); }

  Row failRow(Unres u, Throwable t) {
    Row r = new Row();
    r.fc = u.fc; r.f = u.f; r.app = u.fc.app; r.fn = fnOf(u.fc); r.fnName = u.f.getName(); r.pc = u.op.getSeqnum().getTarget().getOffset() & U32;
    r.kind = u.kind; r.shape = u.shape; r.why = u.why; r.width = u.op.getInput(2).getSize();
    r.reach = true; r.cls = "UNBOUNDED"; r.bOpen = true; r.flag = true; r.bTxt = ""; r.idxClass = "";
    r.origin = "deep pass failed"; r.evidence = "deep pass failed: " + t.getClass().getSimpleName() + (t.getMessage() == null ? "" : " " + t.getMessage());
    r.entries = entriesText(u.f);
    println("deep failed row " + hex(r.pc) + " in " + hex(r.fn) + ": " + r.evidence);
    deep = true; liveDepth = 0; txtDepth = 0;
    liveGuard.clear(); cellGuard.clear(); slotGuard.clear(); retGuard.clear(); txtSeen.clear(); flowGuard.clear();
    return r;
  }
  Row deepRow(Unres u) {
    FC fc = u.fc; PcodeOp op = u.op;
    Expr e = flatExpr(op.getInput(1), fc);
    Row r = new Row();
    r.fc = fc; r.f = u.f; r.app = fc.app; r.fn = fnOf(fc); r.fnName = u.f.getName(); r.pc = op.getSeqnum().getTarget().getOffset() & U32;
    r.kind = u.kind; r.shape = u.shape; r.why = u.why; r.expr = op.getInput(1).toString().replaceAll("\\s+", "");
    r.width = op.getInput(2).getSize(); r.terms = new ArrayList<>(e.terms);
    long k = s32(e.konst), konst = k & U32;
    r.spBased = e.spScale == 1;
    r.baseKind = r.spBased ? "sp+deep" : "deep"; r.idxOff = k;
    r.baseLo = r.baseHi = 0; r.baseHow = "deep";
    r.baseTxt = r.spBased ? "sp" + (k == 0 ? "" : signed(k)) : constText(konst, fc);
    rowNotes.clear(); txtLen = 0;
    r.idxClass = dtTerms(r.terms, fc);
    r.stride = 0;
    for (Term t : r.terms) if (Math.abs(t.scale) > r.stride) r.stride = Math.abs(t.scale);
    Varnode bo = strip(baseOperand(op.getInput(1))); Term bt = null;
    for (Term t : r.terms) {
      if (t.v.equals(bo)) { bt = t; break; }
      Set<Varnode> tr = new HashSet<>(); collectTree(t.v, tr, 0);
      if (bo != null && tr.contains(bo)) bt = t;
    }
    rowNotes.clear(); txtLen = 0; candCache.clear();
    r.origin = "none (the base folded into the constant " + r.baseTxt + ")"; r.bTxt = "";
    if (bt != null) {
      Rg b = rng(bt.v, Collections.emptyMap(), new HashSet<>(), 0, fc);
      r.bOpen = b.open; r.bLo = bt.scale * Math.min(b.lo, b.hi); r.bHi = bt.scale * Math.max(b.lo, b.hi);
      r.bTxt = (bt.scale == 1 ? "" : hex(bt.scale) + "*") + rngText(b, fc);
      r.origin = dt(bt.v, fc, 0);
      if (!b.open && b.lo == 0 && b.hi == 0 && bt.scale == 1) {
        Set<Varnode> tr = new LinkedHashSet<>(); collectTree(bt.v, tr, 0);
        for (Varnode x : tr) if (x.getDef() != null && x.getDef().getOpcode() == PcodeOp.LOAD) { r.evidence = nullTest(x, fc, toAddr(r.pc)); break; }
      }
    }
    Idx ix = idxRange(r.terms, Collections.emptyMap(), fc);
    r.idxMin = ix.min; r.idxMax = ix.max; r.idxOpen = ix.open || r.bOpen;
    if (r.spBased) {
      r.spLo = k + ix.min; r.spHi = k + ix.max + r.width - 1; r.frameTxt = fc.frameTxt; r.lo = r.hi = -1;
      Hit h = spHits(fc, r.spLo, r.spHi); r.targets = h.targets; r.nearest = h.nearest; r.distance = h.distance; r.reach = h.any;
    } else absInt(r, k + ix.min, k + ix.max, false);
    if (e.spScale != 0 && e.spScale != 1) { r.reach = true; r.cls = "UNBOUNDED"; r.evidence = "sp enters the pointer with scale " + e.spScale; }
    else if (r.reach) { classify(r); if (!r.spBased && r.tight != null) absInt(r, r.tMin, r.tMax, true); }
    r.stackSlot = stackBased(r);
    if (r.reach && !r.spBased && !r.stackSlot) perValue(r);
    r.dead = deadFn(r.f);
    r.dataPath = cl(r);
    r.note = String.join("; ", rowNotes);
    if (r.dead) r.cls = "UNREACHABLE-CODE";
    else if (!r.reach) r.cls = "NO-REACH";
    // flag exactly as specified: unvalidated or unbounded, or a tight interval that still ends on a control object; a stack-slot base is never closed
    r.flag = !r.dead && (cl(r).equals("DATA-BOUNDED-UNVALIDATED") || cl(r).equals("UNBOUNDED") || (r.reach && !r.tightClosed) || r.stackSlot);
    r.noteOnly = !r.flag && !r.note.isEmpty();
    r.entries = entriesText(r.f);
    if (r.callers != null && !r.callers.isEmpty()) r.evidence = (r.evidence == null ? "" : r.evidence + " | ") + "callers: " + r.callers;
    r.origin = cap(r.origin); r.idxClass = cap(r.idxClass); r.evidence = cap(r.evidence); r.dataPath = cap(r.dataPath); r.note = cap(r.note);
    if (dump) println(String.format("  DEEP %s %s | konst=%s sp%d terms=%d | base %s | %s | coarse %s reach=%s %s %s", op.getSeqnum().getTarget(), u.why, hex(konst), e.spScale, r.terms.size(),
        r.bTxt, r.spBased ? "sp" : r.origin, r.spBased ? "sp" + signed(r.spLo) + "..sp" + signed(r.spHi) : hex(r.lo) + ".." + hex(r.hi), r.reach ? r.targets : "-", cl(r), r.evidence));
    if (dump) { println("    TREE " + op.getInput(1) + " (konst=" + hex(konst) + " sp" + e.spScale + ")" + (bt == null ? "" : " base-term " + (bt.scale == 1 ? "" : bt.scale + "*") + bt.v)); dumpTree(op.getInput(1), new HashSet<>(), 1); for (Term t : r.terms) dumpTree(t.v, new HashSet<>(), 1); }
    return r;
  }

  static long gcd(long a, long b) { while (b != 0) { long t = a % b; a = b; b = t; } return Math.abs(a); }
  static Rg hullOf(List<Rg> l) { Rg o = null; for (Rg r : l) o = o == null ? r : o.hull(r); return o; }
  static String firstTargets(String t) {
    if (t == null || t.isEmpty()) return "";
    String[] p = t.trim().split("\\s+"); StringBuilder sb = new StringBuilder();
    for (int i = 0; i < Math.min(3, p.length); i++) { if (i > 0) sb.append(' '); sb.append(p[i]); }
    if (p.length > 3) sb.append(" +").append(p.length - 3);
    return sb.toString();
  }
  static final int MAX_CANDS = 4096;
  static final class Cands { List<Rg> list = new ArrayList<>(); boolean complete = true; int combos, unresolved; }
  final List<Varnode> candGuard = new ArrayList<>();
  final Map<Varnode, Cands> candCache = new HashMap<>();   // per row: whole-candidate loads under an empty override
  // deep pass: the candidate values of a LOAD as at most MAX_CANDS ranges, or
  // an incomplete list when some cannot be enumerated. Each term of the load's
  // address contributes candidates: an argument register one per static call
  // site (its value there), a nested table load its own candidates, anything
  // else its range. Every closed address combination is then read cell by cell
  // at the stride of the terms that are still ranges (memCells); the cells stay
  // separate candidates while they fit, else each combination is one hull.
  Cands loadCands(Varnode v, Map<Varnode, Rg> ov, FC fc, int d) {
    tick();
    Cands out = new Cands();
    PcodeOp op = v.getDef();
    if (op == null || op.getOpcode() != PcodeOp.LOAD || d > 24 || slotOf(op.getInput(1), fc) != null) { out.complete = false; return out; }
    int size = v.getSize();
    Expr e = flatExpr(op.getInput(1), fc);
    if (e.spScale != 0) { out.complete = false; return out; }
    long k = s32(e.konst);
    List<List<Rg>> per = new ArrayList<>();
    long total = 1;
    for (Term t : e.terms) {
      List<Rg> l = termCands(t.v, ov, fc, d);
      if (l == null || l.isEmpty()) { out.complete = false; return out; }
      per.add(l); total *= l.size();
    }
    if (total > MAX_CANDS) { out.complete = false; return out; }
    int[] idx = new int[per.size()];
    Boolean separate = null;
    while (true) {
      long lo = k, hi = k, g = 0; boolean open = false;
      for (int i = 0; i < per.size(); i++) {
        Rg c = per.get(i).get(idx[i]); long s = e.terms.get(i).scale;
        if (c.open) open = true;
        lo += Math.min(s * c.lo, s * c.hi); hi += Math.max(s * c.lo, s * c.hi);
        if (c.lo != c.hi) g = gcd(g, Math.abs(s));
      }
      out.combos++;
      List<Rg> q = null;
      if (!open) {
        long rl = lo, rh = hi + size - 1;
        if (rh < 0) { rl += O32; rh += O32; }
        if (!(rl < 0 && rh >= 0)) q = memCells(rl, rh - size + 1, size, g, fc, d);
      }
      if (q == null) out.unresolved++;
      else {
        if (separate == null) separate = total * q.size() <= MAX_CANDS;
        if (separate) out.list.addAll(q); else out.list.add(hullOf(q));
      }
      int i = 0;
      for (; i < idx.length; i++) { if (++idx[i] < per.get(i).size()) break; idx[i] = 0; }
      if (i == idx.length) break;
    }
    out.complete = out.unresolved == 0;
    return out;
  }
  // the candidates of one address term of a LOAD (see loadCands)
  List<Rg> termCands(Varnode v, Map<Varnode, Rg> ov, FC fc, int d) {
    Rg o = ov.get(v);
    if (o != null) return new ArrayList<>(Collections.singletonList(o));
    Varnode s = strip(v);
    o = ov.get(s);
    if (o != null) return new ArrayList<>(Collections.singletonList(o));
    PcodeOp op = s.getDef();
    if (op == null && s.isRegister() && s.getSize() == 4 && !isSp(s) && !isGp(s) && !isTp(s) && !isR0(s)) {
      List<long[]> sites = sitesOf.getOrDefault(fnOf(fc), Collections.<long[]>emptyList());
      if (sites.isEmpty()) return null;
      List<Rg> out = new ArrayList<>(); Set<String> seen = new HashSet<>();
      for (long[] z : sites) {
        SV q = siteValue(z[0], z[1], s.getOffset(), d);
        Rg c = q == null || q.rg == null ? Rg.unk(4) : q.rg;
        if (seen.add(c.lo + ":" + c.hi + ":" + c.open) && out.size() < MAX_CANDS) out.add(c);
      }
      return out;
    }
    if (op != null && op.getOpcode() == PcodeOp.LOAD && !candGuard.contains(s)) {
      candGuard.add(s);
      try { Cands c = loadCands(s, ov, fc, d + 1); if (c.complete && !c.list.isEmpty() && c.list.size() <= 256) return c.list; }
      finally { candGuard.remove(candGuard.size() - 1); }
    }
    Rg q = rng(s, ov, new HashSet<>(), d + 1, fc);
    return new ArrayList<>(Collections.singletonList(q == null ? Rg.unk(4) : q));
  }
  // deep pass: per-value evaluation. One hull of the base's candidates can
  // span a control object that no single candidate reaches, so each candidate
  // value of a LOAD in the pointer expression (loadCands) is evaluated on its
  // own: the value plus the index interval under classify's overrides. The row
  // closes only when every candidate is enumerated and none reaches.
  void perValue(Row r) {
    FC fc = r.fc;
    Map<Varnode, Rg> base = r.ov == null ? Collections.<Varnode, Rg>emptyMap() : r.ov;
    LinkedHashSet<Varnode> loads = new LinkedHashSet<>();
    for (Term t : r.terms) {
      Set<Varnode> tree = new LinkedHashSet<>(); collectTree(t.v, tree, 0);
      for (Varnode x : tree) if (x.getDef() != null && x.getDef().getOpcode() == PcodeOp.LOAD) loads.add(x);
    }
    for (Varnode L : loads) {
      if (candGuard.contains(L)) continue;
      candGuard.add(L);
      Cands cd;
      try { cd = loadCands(L, base, fc, 2); } finally { candGuard.remove(candGuard.size() - 1); }
      if (cd.list.isEmpty()) continue;
      int hits = 0, openIdx = 0; long worst = -1; List<String> ex = new ArrayList<>();
      for (Rg c : cd.list) {
        Map<Varnode, Rg> o2 = new HashMap<>(base); o2.put(L, c);
        Idx ti = idxRange(r.terms, o2, fc);
        if (ti.open || c.open) { openIdx++; continue; }
        long rl = ti.min + r.idxOff, rh = ti.max + r.idxOff + r.width - 1;
        if (rh < 0) { rl += O32; rh += O32; }
        if (rl < 0 && rh >= 0) { rl = 0; rh = U32; }
        long lo = sat0(rl), hi = satU(rh);
        if (hi - lo > worst) worst = hi - lo;
        Hit h = absHits(lo, hi);
        if (h.any) { hits++; if (ex.size() < 3) ex.add(rngText(c, fc) + " -> " + hex(lo) + ".." + hex(hi) + " " + firstTargets(h.targets)); }
      }
      String sum = "per-value " + dtExpr(L, fc, 0) + ": " + cd.list.size() + " candidate values" + (cd.combos > 1 ? " from " + cd.combos + " address combinations" : "")
          + (cd.complete ? "" : ", " + cd.unresolved + " combinations unresolved") + ", widest interval " + (worst < 0 ? "-" : "0x" + Long.toHexString(worst) + " bytes");
      if (hits == 0 && openIdx == 0 && cd.complete) {
        r.tightClosed = true; r.pvClosed = true;
        if (cl(r).equals("DATA-BOUNDED-UNVALIDATED") || cl(r).equals("UNBOUNDED")) r.cls = "BOUNDED";
        r.evidence = (r.evidence == null || r.evidence.isEmpty() ? "" : r.evidence + "; ") + sum + ", none reaches a control object";
        r.origin = r.origin + " | " + sum + ", none reaches a control object";
        return;
      }
      r.origin = r.origin + " | " + sum + (hits > 0 ? "; " + hits + " reach a control object: " + String.join("; ", ex) : "") + (openIdx > 0 ? "; " + openIdx + " have an open index" : "");
      if (hits > 0) {
        r.tightClosed = false;
        r.evidence = (r.evidence == null || r.evidence.isEmpty() ? "" : r.evidence + "; ") + hits + " of " + cd.list.size() + " candidate values of " + dtExpr(L, fc, 0) + " reach a control object";
      }
    }
  }
  // deep pass: true when a term of the pointer expression is a 4-byte
  // stack-space varnode or a word load with an sp-relative address
  boolean stackBased(Row r) {
    for (Term t : r.terms) {
      Set<Varnode> tree = new HashSet<>(); collectTree(t.v, tree, 0);
      for (Varnode x : tree) {
        if (isStackVn(x) && x.getSize() == 4) return true;
        PcodeOp o = x.getDef();
        if (o != null && o.getOpcode() == PcodeOp.LOAD && x.getSize() == 4 && slotOf(o.getInput(1), r.fc) != null) return true;
      }
    }
    return false;
  }
  // the word loads of fc that read the stack slot `off` (entry-relative): the
  // displacement is body-relative, so the frame size is added back
  String slotLoads(FC fc, long off) {
    long c = off + (fc.raOff >= 0 ? fc.frameTop : 0);
    StringBuilder sb = new StringBuilder(); boolean epIsSp = false;
    java.util.regex.Pattern p = java.util.regex.Pattern.compile("^(s?ld)\\.w\\s*(0x[0-9a-f]+|\\d+)\\[(sp|ep)\\]");
    for (Instruction i : fc.ins) {
      String s = i.toString(), t = s.replaceAll("\\s+", "");
      java.util.regex.Matcher m = p.matcher(s);
      if (m.find()) {
        if ((m.group(3).equals("sp") || (m.group(3).equals("ep") && epIsSp)) && Long.decode(m.group(2)) == c) {
          if (sb.length() > 0) sb.append(", ");
          sb.append(t).append('@').append(hex(i.getAddress().getOffset()));
          if (sb.length() > 80) break;
        }
      } else if (t.equals("movsp,ep")) epIsSp = true;
      else if (t.endsWith(",ep")) epIsSp = false;
    }
    return sb.toString();
  }
  String stackCaveat(FC fc, long off) {
    String ins = slotLoads(fc, off);
    return "the p-code shows the slot's address, not its contents (" + (ins.isEmpty() ? "no word load from it in the listing" : ins) + "); the pointer the slot holds is not ranged, so the row is never closed";
  }
  // deep pass: a loaded base that is the constant 0. Finds the compare of that
  // load against 0 followed by a conditional branch and reports the side the
  // store is reached from.
  String nullTest(Varnode v, FC fc, Address S) {
    Set<Varnode> tree = new HashSet<>(); collectTree(v, tree, 0);
    for (Cmp c : fc.cmps) {
      if (!c.bImm || c.imm != 0 || c.a == null || !tree.contains(c.a)) continue;
      boolean viaT = c.tgt != null && reaches(fc, c.tgt, c.br.getAddress(), S), viaF = c.fall != null && reaches(fc, c.fall, c.br.getAddress(), S);
      return "the loaded base is 0 and " + hex(fnOf(fc)) + " tests it for null (" + c.ci.getMnemonicString() + "@" + c.at + ", " + c.cond + "@" + c.br.getAddress() + "): the store is reached from the " + (viaT && viaF ? "both sides" : viaT ? "branch side (zero)" : viaF ? "fall-through side (non-zero)" : "neither side");
    }
    return "the loaded base is 0";
  }

  void writeDeep() throws IOException {
    long noReach = 0, reach = 0, flagged = 0, deadN = 0, appFlag = 0, noteOnly = 0, openB = 0, failed = 0;
    TreeMap<String, Long> clsCount = new TreeMap<>(), whyCount = new TreeMap<>();
    for (Row r : deepRows) {
      clsCount.merge(cl(r), 1L, Long::sum); whyCount.merge(r.why, 1L, Long::sum);
      if (r.reach) reach++; else noReach++;
      if (r.flag) { flagged++; if (r.app) appFlag++; }
      if (r.dead) deadN++;
      if (r.noteOnly) noteOnly++;
      if (r.bOpen) openB++;
      if (r.origin.startsWith("deep pass failed")) failed++;
    }
    PrintWriter w = writer(new File(outDir, "reach-deep.csv"));
    w.println("region,function,fn_name,store_pc,kind,why,shape,base_origin,base_lo,base_hi,base_open,index_class,coarse_lo,coarse_hi,targets,nearest_target,distance,class,evidence,tight_reach,tight_targets,tight_closed,entries,flag,note");
    for (Row r : deepRows) {
      w.println(String.join(",",
          q(r.app ? "app" : "boot"), q(hex(r.fn)), q(r.fnName), q(hex(r.pc)), q(r.kind), q(r.why), q(r.shape), q(r.origin),
          q(r.bTxt.isEmpty() ? "" : hexl(r.bLo)), q(r.bTxt.isEmpty() ? "" : hexl(r.bHi)), q(Boolean.toString(r.bOpen)),
          q(r.idxClass), q(r.spBased ? "sp" + signed(r.spLo) : hex(r.lo)), q(r.spBased ? "sp" + signed(r.spHi) : hex(r.hi)),
          q(r.targets), q(r.nearest), q(r.spBased ? "" : Long.toString(r.distance)), q(cl(r)), q(r.evidence),
          q(r.tight), q(r.tightTargets), q(r.reach && !r.dead ? Boolean.toString(r.tightClosed) : ""), q(r.entries), q(r.flag ? "yes" : "no"), q(r.note)));
    }
    w.close();
    PrintWriter m = writer(new File(outDir, "reach-deep.md"));
    m.println("# Deep pass over the unresolved-base stores (camry-8965F3307000)");
    m.println();
    m.println("Generated by `ghidra/scripts/investigate/ReachOfUnknownBaseStores.java` on the shared read-only Ghidra project, after the first pass. Companion data: `reach-deep.csv` (one row per store that `reach-unresolved-bases.csv` lists).");
    m.println();
    m.println("## 1. Totals");
    m.println();
    m.println("| quantity | value |");
    m.println("|---|---:|");
    m.println("| unresolved `reg+var` stores from the first pass | " + deepRows.size() + " |");
    m.println("| coarse interval misses every control object (NO-REACH, closed) | " + noReach + " |");
    m.println("| coarse interval reaches a control object | " + reach + " |");
    m.println("| flagged for instruction-level review | " + flagged + " (application " + appFlag + ", boot " + (flagged - appFlag) + ") |");
    m.println("| closed rows carrying a note (argument hull over the static call sites of a function whose entry is referenced as data) | " + noteOnly + " |");
    m.println("| of which the deep pass itself failed (flagged UNBOUNDED) | " + failed + " |");
    m.println("| UNREACHABLE-CODE (function nothing calls) | " + deadN + " |");
    m.println("| rows whose base range is open | " + openB + " |");
    m.println();
    m.println("First-pass `why` of the rows: " + whyCount.entrySet().stream().map(en -> en.getKey() + "=" + en.getValue()).reduce((a, c) -> a + ", " + c).orElse("") + ".");
    m.println();
    m.println("## 2. Classes");
    m.println();
    m.println("| class | count |");
    m.println("|---|---:|");
    for (Map.Entry<String, Long> en : clsCount.entrySet()) m.println("| " + en.getKey() + " | " + en.getValue() + " |");
    m.println();
    m.println("## 3. Flagged rows");
    m.println();
    m.println("| fn | pc | region | why | base origin | base range | coarse reach | coarse targets | class | evidence | tight reach | tight targets | entries |");
    m.println("|---|---|---|---|---|---|---|---|---|---|---|---|---|");
    for (Row r : deepRows) {
      if (!r.flag) continue;
      m.println("| " + hex(r.fn) + " | " + hex(r.pc) + " | " + (r.app ? "app" : "boot") + " | " + r.why + " | " + md(r.origin) + " | " + md(r.bTxt) + " | " + (r.spBased ? "sp" + signed(r.spLo) + "..sp" + signed(r.spHi) : hex(r.lo) + ".." + hex(r.hi)) + " | " + md(r.targets) + " | " + cl(r) + " | " + md(r.evidence) + " | " + md(r.tight) + " | " + md(r.tightTargets) + " | " + md(r.entries) + " |");
    }
    m.println();
    m.println("## 3b. Closed rows that carry a note");
    m.println();
    m.println("| fn | pc | region | why | class | note |");
    m.println("|---|---|---|---|---|---|");
    for (Row r : deepRows) {
      if (r.flag || r.note == null || r.note.isEmpty()) continue;
      m.println("| " + hex(r.fn) + " | " + hex(r.pc) + " | " + (r.app ? "app" : "boot") + " | " + r.why + " | " + cl(r) + " | " + md(r.note) + " |");
    }
    m.println();
    m.println("## 4. UNREACHABLE-CODE rows");
    m.println();
    List<Row> dead = new ArrayList<>();
    for (Row r : deepRows) if (r.dead) dead.add(r);
    if (dead.isEmpty()) m.println("None.");
    else {
      m.println("| fn | pc | region | base origin | coarse reach | class before the override | evidence |");
      m.println("|---|---|---|---|---|---|---|");
      for (Row r : dead) m.println("| " + hex(r.fn) + " | " + hex(r.pc) + " | " + (r.app ? "app" : "boot") + " | " + md(r.origin) + " | " + (r.spBased ? "sp" + signed(r.spLo) + "..sp" + signed(r.spHi) : hex(r.lo) + ".." + hex(r.hi)) + " | " + md(r.dataPath) + " | " + md(r.evidence) + " |");
    }
    m.println();
    m.println("## 5. Method and limits");
    m.println();
    m.println("- The first pass and its three outputs are unchanged. The deep pass ranges every term of each unresolved store's pointer expression, the base term included, with the range engine in deep mode; the coarse interval is `konst + sum(scale x range)` and is tested with the same `absHits`/`spHits` reach test.");
    m.println("- `load`: the loaded pointer's address is ranged and its cells read one by one: a CodeFlash range from program memory at the expression's stride (the gcd of its terms' scales, at most 4096 cells); a LocalRAM range of span at most 0x1000 from every indexed writer that meets it and every STORE a callee of the loading function makes through a pointer it was handed inside the range. When that address is open or wider than the cell limit, the load's candidates are enumerated instead (loadCands): an argument register contributes the value at each of its static call sites, a nested table load its own cells, every other term its range, and each address combination its cells. An address that stays sp-relative or open, a cell that cannot be read, a range without a writer, or more than 4096 candidates leaves the value unknown.");
    m.println("- `param`: a register read without a definition carries the caller's value at the call: the hull over every static call site, the value taken from the call op's inputs, else the last write in the straight-line block before the call, else the caller's own live-in hulled with every write in a block that reaches the call (depth 8, recursion cut), so a forwarded argument is followed through its caller's call sites. An argument that resolves to nothing stays open; the first pass's linear-window constant is not used in the deep pass.");
    m.println("- `nodef`: a default-space varnode is the ROM or RAM cell at its address. A 4-byte stack-space varnode used in the pointer, and a word load whose address is sp-relative, are never closed: the decompiler hands over the address of a slot where the program loaded the slot's contents with a word load (the LOAD is gone from the p-code), so the base is open, the row is flagged, and the origin text names that instruction.");
    m.println("- Per-value: when one hull of a base's candidates spans a control object that no single candidate reaches, every candidate value of a LOAD in the pointer expression is evaluated on its own, as the value plus the index interval under classify's overrides (at most 4096 candidates). The row closes only when every candidate is enumerated and none reaches; otherwise `base_origin` gives the candidate count, the widest interval and up to three candidates that reach.");
    m.println("- A loaded base that is the constant 0 is reported with the null test on that load in the same function and the side the store is reached from.");
    m.println("- `callret`: a direct call's result is the hull of the callee's RETURN inputs under a map from the callee's argument-register varnodes to the call site's values; an indirect call stays unknown.");
    m.println("- `phi`: a merge hulls its inputs; a loop-carried pointer keeps its init as the bound on the side its constant step moves away from (no 32-bit wrap assumed) and the loop compare gives the other side through `classify`, with the base term left in the index tree.");
    m.println("- `UNREACHABLE-CODE`: the function has no static caller, no reference to its entry, its address in no word of the image, and is neither a vector-table nor a known entry.");
    m.println("- Limits: the writer index does not see a store through a pointer that another caller hands a callee, nor a store through a pointer nobody ranges (an unknown loaded value); a RAM hull is therefore complete only for the index. Argument hulls see static call sites only (a row whose function entry is referenced as data carries a note). The value at a call site is exact for a call-op input or a straight-line write and a hull otherwise. Stack-valued pointers (`sp+c` of a caller frame) stay open and flagged. Each row runs under a 120 s budget and a catch-all, so a failure flags its row as UNBOUNDED instead of ending the run.");
    m.close();
    println(String.format("DEEP|unresolved=%d|evaluated=%d|noReach=%d|reach=%d|flagged=%d|flaggedApp=%d|noteOnly=%d|failed=%d|unreachableCode=%d|openBase=%d|contexts=%d", unres.size(), deepRows.size(), noReach, reach, flagged, appFlag, noteOnly, failed, deadN, openB, fcCache.size()));
    for (Map.Entry<String, Long> en : clsCount.entrySet()) println("DEEPCLASS|" + en.getKey() + "|" + en.getValue());
    println("OUTPUT|deep " + outDir.getAbsolutePath());
  }

  void dumpTree(Varnode v, Set<Varnode> seen, int d) {
    if (v == null || d > 14 || !seen.add(v)) return;
    PcodeOp op = v.getDef();
    if (op == null) { println("      " + v + (v.isRegister() ? " " + regName(v) : "") + (isStackVn(v) ? " stack" : "")); return; }
    StringBuilder sb = new StringBuilder("      ").append(v).append(" = ").append(PcodeOp.getMnemonic(op.getOpcode()));
    for (Varnode in : op.getInputs()) sb.append(' ').append(in);
    println(sb.append(" @").append(opPc(op)).toString());
    for (Varnode in : op.getInputs()) dumpTree(in, seen, d + 1);
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
    String out = null; int max = -1; boolean deepRun = false;
    for (String a : getScriptArgs()) {
      if (a.equals("--rows")) printRows = true;
      else if (a.equals("--dump")) dump = true;
      else if (a.startsWith("--out=")) out = a.substring(6);
      else if (a.startsWith("--only=")) { only = new TreeSet<>(); for (String s : a.substring(7).split(",")) only.add(Long.decode(s) & U32); }
      else if (a.startsWith("--max=")) max = Integer.decode(a.substring(6));
      else if (a.equals("--deep")) deepRun = true;
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
    this.di = di;
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
        indexWriter(f, fc, op);
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
          unres.add(new Unres(fc, f, op, kind, wy, shape)); fcCache.putIfAbsent(fno, fc);
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
    writeOutputs(ctxWriters, fn, stores, unknown, kConstVar, kRegVar, kUnresolved, kWeird, noDecomp, otherKinds, unresWhy, baseKinds);
    if (deepRun) deepPass();
    di.dispose();
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
