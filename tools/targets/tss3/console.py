"""Human-readable console output for the TSS3 signer build/onboard/kit CLIs.

Each command keeps its complete machine-readable JSON on disk (report.json or
the build metadata file); these renderers only summarize what a human needs
to decide "did it work, and if not, why" at the terminal.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

_ONBOARD_VERDICTS = {
    "covered-by-current-build": "COMPATIBLE - covered by the current universal build",
    "compatible-profile-missing": "COMPATIBLE - new profile row resolved and rebuilt",
    "not-proven-compatible": "NOT PROVEN COMPATIBLE",
    "candidate-build-failed": "CANDIDATE BUILD FAILED",
    "simulation-failed": "SIMULATION FAILED",
    "machine-verification-failed": "MACHINE VERIFICATION FAILED",
}

_SCENARIO_PREFIX = "tss3-dynamic-"


@dataclass
class _Rows:
    entries: list[tuple[str, str]] = field(default_factory=list)

    def add(self, label: str, value: str) -> None:
        self.entries.append((label, value))

    def render(self) -> str:
        width = max((len(label) for label, _ in self.entries), default=0)
        return "\n".join(f"  {label:<{width}}  {value}" for label, value in self.entries)


def _path(text: str) -> str:
    if text.startswith(os.getcwd() + os.sep):
        return text[len(os.getcwd()) + 1 :]
    return text


def _short_digest(digest: str | None) -> str:
    if not digest:
        return "-"
    return f"{digest[:8]}…{digest[-6:]}" if len(digest) > 20 else digest


def _component_rows(report: dict[str, Any], rows: _Rows) -> None:
    components = report.get("capabilities", {}).get("components", {})
    if not components:
        return
    resolved = sum(1 for row in components.values() if row["status"] == "resolved")
    rows.add("components", f"{resolved}/{len(components)} resolved")
    for name, row in components.items():
        if row["status"] == "resolved":
            continue
        reason = row.get("reason")
        rows.add(f"  {name}", f"{row['status']}: {reason}" if reason else row["status"])


def _machine_rows(report: dict[str, Any], rows: _Rows) -> None:
    machine = report.get("machine_verification")
    if not machine:
        return
    if machine["status"] == "verified-local-execution":
        scenarios = machine.get("scenarios", [])
        rows.add(
            "machine verification",
            f"PASS  {len(scenarios)}/{len(scenarios)} scenarios on "
            f"{machine['target']} (P1M-E, exact firmware)",
        )
        for scenario in scenarios:
            name = scenario["name"].removeprefix(_SCENARIO_PREFIX)
            rows.add(f"  {name}", f"{scenario['instruction_count']} instr")
    else:
        rows.add("machine verification", machine["status"])
        if "reason" in machine:
            rows.add("  reason", machine["reason"])


def render_onboard(report: dict[str, Any]) -> str:
    codeflash = report["codeflash"]
    size_mib = codeflash["size"] / (1 << 20)
    rows = _Rows()
    rows.add(
        "dump",
        f"{_path(codeflash['path'])} ({size_mib:.1f} MiB, {_short_digest(codeflash['sha256'])})",
    )
    identity = report.get("identity")
    if identity:
        rows.add(
            "identity",
            f"selector {identity['runtime_software_id']}"
            f" · app {identity['firmware_software_id']}"
            f" · secondary {identity['secondary_software_id']}",
        )
    verdict = _ONBOARD_VERDICTS.get(report["status"], report["status"].upper())
    rows.add("verdict", verdict)
    if report.get("current_targets"):
        rows.add("registered targets", ", ".join(report["current_targets"]))
    if report.get("reason"):
        rows.add("reason", report["reason"])
    _component_rows(report, rows)
    if "simulation" in report:
        rows.add("simulation", "PASS  fallback + idle-fast (GNU sim, exact dump)")
    _machine_rows(report, rows)
    rows.add("report", f"{_path(report.get('output_dir', '<output dir>'))}/report.json (full JSON)")
    return "TSS3 request signer - dump onboarding\n" + rows.render()


def render_build(meta: dict[str, Any], output_dir: str | None = None) -> str:
    request = meta["request"]
    response = meta["response"]
    rows = _Rows()
    rows.add("target", meta["target"]["name"])
    rows.add("codec", f"{request['codec']} ({request['carrier']}, {request['frame_count']} frames)")
    rows.add("request", f"bus {request['bus']} {request['can_id']}")
    rows.add("response", f"bus {response['bus']} {response['can_id']}")
    rows.add("payload sha256", meta["authenticated_payload"]["sha256"])
    rows.add("compatibility", meta["compatibility"]["status"])
    if output_dir:
        rows.add("output", _path(output_dir))
    return "TSS3 request signer - build\n" + rows.render()


def render_kit(result: dict[str, Any], output_dir: str) -> str:
    if "kits" in result:
        kits = result["kits"]
        rows = _Rows()
        rows.add("payload sha256", next(iter(kits.values()))["payload_sha256"])
        rows.add("output", _path(output_dir))
        for name in kits:
            rows.add(f"  {name}", f"{_path(output_dir)}/{name}/tss3-request-signer")
        rows.add("next", f"{_path(output_dir)}/{next(iter(kits))}/tss3-request-signer doctor")
        return f"TSS3 RAM kit set - {len(kits)} kits, codec {result['codec']}\n" + rows.render()
    rows = _Rows()
    rows.add("target", result["target"])
    rows.add("codec", result["codec"])
    rows.add("payload sha256", result["payload_sha256"])
    rows.add("output", _path(output_dir))
    rows.add("next", f"{_path(output_dir)}/tss3-request-signer doctor")
    return "TSS3 RAM kit\n" + rows.render()
