# Plugin verification: v850e3 SLEIGH against the P1M-E firmware

This records audits of the vendored `ghidra/ghidra_v850` processor module
against the RH850/P1M-E CodeFlash, establishing that the SLEIGH sources
correctly model every instruction and system register the firmware uses. Both
audits are reproducible via the scripts under `ghidra/scripts/investigate/`,
run against a working copy of the project (`make work-project`):

```bash
ghidra --projects-dir "$PWD/build/project" --project rh850_p1me_mapped \
       --program RH850_P1M-E_CodeFlash.bin \
       script run ghidra/scripts/investigate/<Script>.java
```

## System-register coverage (ldsr / stsr)

Script: `ghidra/scripts/investigate/FindSystemRegisterOps.java`.

Every system-register transfer in the firmware decodes with a correct register
name; there is nothing to add to the `selID` tables in `v850e3.sinc`. Across the
whole CodeFlash the firmware uses **324** such instructions (**242 `ldsr`** +
**82 `stsr`**) and **zero** `ldtc`/`sttc`/`ldvc`/`stvc` (the thread-/virtual-
context transfers are absent, consistent with the P1M-E having no hypervisor or
virtualization extension). No operand decodes to a blank or raw token.

The distinct registers referenced, all named correctly:

- **selID 0** (common, `v850_common.sinc`): `PSW`, `EIPC`, `EIPSW`, `FEPC`,
  `FEPSW`, `CTPC`, `CTPSW`, `EIIC`, `FEIC`, `EIWR`, `FEWR`, `CTBP`, `BSEL`.
- **selID 1**: `EBASE`, `INTBP`, `MCTL`, `SCCFG`, `SCBP`, `SPID`, `FPIPR`.
- **selID 2**: `MEA`, `MEI`, `ASID`, `IMSR`, `INTCFG`.
- **selID 4** (cache): `ICTAGL`, `ICTAGH`, `ICDATL`, `ICDATH`, `ICCTRL`, `ICERR`.
- **selID 5/6/7** (MPU): `MPM`, `MPRC`, `MCA`, `MCS`, `MCR`, `MPAT0–15`,
  `MPLA0–15`, `MPUA0–15`.
- **selID 13**: `RDBCR`.
- FPU: `FPSR`, `FPEC`, `FPEPC`.

Two points worth recording:

- `IMSR` (the subject of upstream issue #40, "decoded where it should be PMR")
  is **correct** for the P1M-E. The firmware uses it for the standard
  interrupt-mask critical section (`stsr IMSR,rN` / `ldsr rN,IMSR` around
  protected regions). Issue #40 concerns a newer multicore ICU, not this core.
- `EIC136`/`EIC292`/`EIC293` are **memory-mapped** peripheral registers at
  `0xFFFFB110` / `0xFFFFB248` / `0xFFFFB24A`, accessed via `ld.w`/`st.w`, not
  `ldsr`/`stsr`. They are therefore out of scope for the `selID` tables and are
  named through project labels (see the analysis docs), not the processor module.
