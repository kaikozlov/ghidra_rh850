#!/usr/bin/env python3
"""Verify first-class analysis-target registry, identities, and snapshot safety."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/analysis_targets.json"
RESOLVER = ROOT / "tools/project/analysis_target.py"

passed = failed = 0

def check(name: str, cond: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(cond); passed += int(ok); failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][generated_self_check] {name}" + (f" ({detail})" if detail else ""))

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def within(child: Path, parent: Path) -> bool:
    child = child.resolve(strict=False); parent = parent.resolve(strict=False)
    return child != parent and parent in child.parents

obj = json.loads(REGISTRY.read_text())
check("registry schema exact", obj.get("schema") == "ghidra-rh850-analysis-targets-v1")
check("Sienna remains default", obj.get("default_target") == "sienna-8965B4512000")
targets = obj.get("targets", {})
expected_targets = {
    "sienna-8965B4512000",
    "camry-8965F3307000",
    "corolla-8965H1202000",
    "corolla-8965F1208000",
}
check("exact registered target set", set(targets) == expected_targets)

required = {
    "status", "vehicle", "software_id", "codeflash", "codeflash_sha256", "codeflash_size", "codeflash_base",
    "dataflash", "dataflash_sha256", "dataflash_size", "dataflash_base", "mcu", "processor",
    "project_name", "program_name", "snapshot_dir", "work_dir", "inventory_baseline", "decompiler_corpus", "rebuild_profile",
}
name_re = re.compile(r"^[A-Za-z0-9_.-]+$")
work_paths: list[Path] = []
snapshot_paths: list[Path] = []
for name, row in targets.items():
    print(f"\n== {name} ==")
    check(f"{name} registry complete", required <= set(row))
    cf = ROOT / row["codeflash"]; df = ROOT / row["dataflash"]
    check(f"{name} CodeFlash exists/size", cf.is_file() and cf.stat().st_size == row["codeflash_size"])
    check(f"{name} CodeFlash hash", cf.is_file() and sha(cf) == row["codeflash_sha256"])
    check(f"{name} DataFlash exists/size", df.is_file() and df.stat().st_size == row["dataflash_size"])
    check(f"{name} DataFlash hash", df.is_file() and sha(df) == row["dataflash_sha256"])
    check(f"{name} bases exact", row["codeflash_base"] == "0x00000000" and row["dataflash_base"] == "0xFF200000")
    expected_mcu = "R7F701383" if name.startswith("corolla-") else "R7F701381"
    check(f"{name} RH850 target exact", row["mcu"] == expected_mcu and row["processor"] == "v850e3:LE:32:default")
    check(f"{name} safe Ghidra names", bool(name_re.fullmatch(row["project_name"])) and bool(name_re.fullmatch(row["program_name"])))
    work = ROOT / row["work_dir"]; snap = ROOT / row["snapshot_dir"]
    work_paths.append(work); snapshot_paths.append(snap)
    check(f"{name} work path isolated below build/work", within(work, ROOT / "build/work"))
    check(f"{name} snapshot is committed, not build state", not within(snap, ROOT / "build") and (snap == ROOT / "project" or within(snap, ROOT / "projects")))
    baseline = ROOT / row["inventory_baseline"]; corpus = ROOT / row["decompiler_corpus"]
    check(f"{name} inventory baseline tracked", baseline.is_file() and baseline.stat().st_size > 0)
    check(f"{name} decompiler corpus tracked", corpus.is_file() and corpus.stat().st_size > 0)
    check(f"{name} packed snapshot exists", (snap / f"{row['project_name']}.gpr.snapshot").is_file() and (snap / f"{row['project_name']}.rep.snapshot").is_dir())
    check(f"{name} committed snapshot is non-openable", not (snap / f"{row['project_name']}.gpr").exists() and not (snap / f"{row['project_name']}.rep").exists())

check("work paths unique", len({p.resolve(strict=False) for p in work_paths}) == len(work_paths))
resolved_snaps = [p.resolve(strict=False) for p in snapshot_paths]
check("snapshot roots unique and non-nested", len(set(resolved_snaps)) == len(resolved_snaps) and all(a not in b.parents and b not in a.parents for i,a in enumerate(resolved_snaps) for b in resolved_snaps[i+1:]))

camry = targets["camry-8965F3307000"]
check("Camry is first-class", camry["status"] == "first_class" and camry["capture_root"] == "targets/camry-2026")
stage_fields = ("function_seeds", "device_profile_script", "entry_seed_script", "diagnostic_seed_script", "recovered_seed_script")
for name, row in targets.items():
    if name == obj["default_target"]:
        continue
    check(f"{name} is first-class", row["status"] == "first_class")
    for field in stage_fields:
        check(f"{name} target rebuild metadata has {field}", bool(row.get(field)))
check("Camry registered function seeds exist", (ROOT / camry["function_seeds"]).is_file())
raw_cf = ROOT / "targets/camry-2026/raw-20260826/codeflash/camry_8965F3307000_codeflash_20260826T213719Z.bin"
check("Camry canonical CodeFlash equals acquired lower MiB", raw_cf.is_file() and raw_cf.read_bytes()[:0x100000] == (ROOT / camry["codeflash"]).read_bytes())
raw_df = ROOT / "targets/camry-2026/raw-20260826/secoc-recovery/dataflash/dump_ff200000_ff208000.bin"
check("Camry canonical DataFlash equals acquired evidence", raw_df.is_file() and raw_df.read_bytes() == (ROOT / camry["dataflash"]).read_bytes())
check("Camry identity pair embedded", (ROOT / camry["codeflash"]).read_bytes()[0x20860:0x2086C] == b"8965F3307000" and (ROOT / camry["codeflash"]).read_bytes()[0x17DC0:0x17DCC] == b"8A3113303100")

h = targets["corolla-8965H1202000"]
f = targets["corolla-8965F1208000"]
check("Corolla targets share only application rebuild inputs", all(h[field] == f[field] for field in stage_fields))
check("Corolla H historical label is not conflated with direct F181", h["identity_role"] == "historical auxiliary DID 0x2032 image label" and h["direct_f181_primary_id"] == "8965F1208000")
h_cf = (ROOT / h["codeflash"]).read_bytes(); f_cf = (ROOT / f["codeflash"]).read_bytes()
check("Corolla H/F application is byte-identical", h_cf[0x20000:] == f_cf[0x20000:])
check("Corolla H identities embedded", h_cf[0x20860:0x2086C] == b"8965F1208000" and h_cf[0x17DC0:0x17DCC] == b"8A3111202000" and h_cf[0x17D80:0x17D8C] == b"8965H1202000")
check("Corolla F identities embedded", f_cf[0x20860:0x2086C] == b"8965F1208000" and f_cf[0x17DC0:0x17DCC] == b"8A3111213000" and f_cf[0x17D80:0x17D8C] == b"8965H1213000")
for producer in (
    "tools/targets/corolla/builders/promote_corolla_analysis_inputs.py",
    "tools/targets/corolla/builders/build_corolla_hf_function_seeds.py",
):
    r = subprocess.run([sys.executable, str(ROOT / producer), "--check"], cwd=ROOT, capture_output=True, text=True)
    check(f"{Path(producer).name} reproduces tracked outputs", r.returncode == 0, r.stderr.strip())

# Resolver owns registry lookup only. Runtime wrappers select their target via
# GHIDRA_ANALYSIS_TARGET and resolve individual fields; there is no second shell-
# export API carrying overlapping project identity.
r = subprocess.run([sys.executable, str(RESOLVER), "camry-8965F3307000", "--json"], cwd=ROOT, capture_output=True, text=True)
check("resolver JSON succeeds", r.returncode == 0 and json.loads(r.stdout)["name"] == "camry-8965F3307000")
check("resolver retired shell-export API", "--shell" not in subprocess.check_output([sys.executable, str(RESOLVER), "--help"], cwd=ROOT, text=True))
r = subprocess.run([sys.executable, str(RESOLVER), "definitely-not-a-target", "--json"], cwd=ROOT, capture_output=True, text=True)
check("unknown target fails closed", r.returncode != 0 and "unknown analysis target" in (r.stderr + r.stdout))

# Guard checks are toolchain-free: tools/g rejects committed snapshots before CLI bootstrap.
for target, row in targets.items():
    snap = ROOT / row["snapshot_dir"]
    env = dict(__import__("os").environ, GHIDRA_ANALYSIS_TARGET=target, GHIDRA_PROJECT=str(snap))
    r = subprocess.run([str(ROOT / "tools/g"), "session-status"], cwd=ROOT, env=env, capture_output=True, text=True)
    check(f"{target} committed snapshot guard", r.returncode != 0 and "REFUSING" in r.stderr)

rebuild = (ROOT / "tools/project/rebuild_target_project.sh").read_text()
check("non-default rebuild preserves four-stage analysis", all(x in rebuild for x in ("1/4", "2/4", "3/4", "4/4", "4b")))
check("target rebuild resolves registered stage scripts", all(token in rebuild for token in ("field function_seeds", "field device_profile_script", "field entry_seed_script", "field diagnostic_seed_script", "field recovered_seed_script")))
check("target rebuild has no Camry path/profile coupling", "data/targets/camry-8965F3307000" not in rebuild and "camry_f33_v1" not in rebuild)
check("non-default destructive rebuild is build/work bounded", "refusing target rebuild destination outside dedicated build/work descendant" in rebuild and "is_symlink" in rebuild)
snapshot = (ROOT / "tools/project/snapshot_target_project.sh").read_text()
check("first promotion requires independent parity build", "first target promotion requires --parity-project-dir" in snapshot and "independent target rebuild inventories differ" in snapshot)
check("canonical corpus rechecks tracked baseline", "generate_target_decompiler_corpus.py" in snapshot)
check("target snapshot has no Camry profile coupling", "camry_f33_v1" not in snapshot)
makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
check(
    "Makefile target identity is registry-backed for default and non-default targets",
    all(
        f'--field {field}' in makefile
        for field in ("work_dir", "snapshot_dir", "inventory_baseline", "decompiler_corpus", "project_name", "program_name")
    )
    and 'PROJECT_NAME := rh850_p1me_mapped' not in makefile
    and 'PROGRAM_NAME := RH850_P1M-E_CodeFlash.bin' not in makefile,
)
r = subprocess.run([str(ROOT / "tools/gtarget"), "list"], cwd=ROOT, capture_output=True, text=True)
check("gtarget lists configured targets", r.returncode == 0 and all(name in r.stdout for name in expected_targets))
r = subprocess.run([str(ROOT / "tools/gtarget"), "show", "camry-8965F3307000"], cwd=ROOT, capture_output=True, text=True)
check("gtarget shows registry metadata", r.returncode == 0 and json.loads(r.stdout)["function_seeds"] == camry["function_seeds"])

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
