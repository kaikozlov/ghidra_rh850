"""Offline-only check of recorded OEM gateway preparation, not a vehicle probe."""

import collections
import json
import sys
import warnings
from pathlib import Path

sys.path.insert(0, "/Users/kai/dev/inspect/repos/kai-openpilot")
from openpilot.tools.lib.logreader import LogReader

root = Path("/Users/kai/dev/inspect/repos/ghidra_rh850_analysis")
source = root / "targets/camry-2026/raw-20260912/eps-recovery/saved-log-liveness.json"
files = [
    r["path"]
    for r in json.loads(source.read_text())["files"]
    if "/2026-09-04/" not in r["path"]
]
# Both are manufacturer-defined gateway families, not interchangeable EPS IDs.
addresses = {0x750, 0x758, 0x777, 0x786, 0x78E, 0x7A0, 0x7A1, 0x7A9, 0x7B0, 0x7B8, 0x7DF}
counts = collections.Counter()
messages = collections.Counter()
observations = []
for p in files:
    one = collections.Counter()
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter("always")
        for e in LogReader(p, only_union_types=True):
            kind = e.which()
            if kind not in {"can", "sendcan"}:
                continue
            for f in getattr(e, kind):
                a = int(f.address)
                if a not in addresses:
                    continue
                src = int(f.src)
                data = bytes(f.dat)
                counts[kind, src, a, len(data)] += 1
                # The shared 750/758 route uses an address-extension byte.
                off = 1 if a in {0x750, 0x758} else 0
                if len(data) <= off:
                    continue
                node = data[0] if off else None
                if data[off] >> 4:
                    continue  # these OEM preparations fit a single frame
                n = data[off] & 15
                if n == 0:
                    if len(data) <= off + 1:
                        continue
                    n = data[off + 1]
                    pos = off + 2
                else:
                    pos = off + 1
                if n == 0 or pos + n > len(data):
                    continue
                uds = data[pos : pos + n]
                # Do not retain VINs, IDs, seed/key exchanges, or memory contents.
                keep = uds[0] in {0x10, 0x50, 0x11, 0x51, 0x28, 0x68, 0x3E, 0x7E}
                if uds[0] in {0x31, 0x71} and len(uds) >= 4:
                    keep = int.from_bytes(uds[2:4], "big") in {0x1011, 0x1012, 0x117E}
                if uds[0] == 0x7F and len(uds) >= 3:
                    keep = uds[1] in {0x10, 0x11, 0x28, 0x31, 0x3E}
                if keep:
                    signature = (kind, src, a, node, uds[:8].hex())
                    messages[signature] += 1
                    one[signature] += 1
    rows = [
        {
            "event": k,
            "src": s,
            "address": hex(a),
            "node": None if n is None else hex(n),
            "uds": u,
            "count": v,
        }
        for (k, s, a, n, u), v in sorted(one.items(), key=lambda x: str(x[0]))
    ]
    observations.append(
        {"input": p, "warnings": [str(w.message) for w in ws], "messages": rows}
    )
result = {
    "watched_addresses": [f"0x{address:03X}" for address in sorted(addresses)],
    "scope": "Offline 39 retained post-incident segments only; missing transactions outside captured spans remain unknown. No wire-format inference; no requests transmitted. Only well-formed single-frame UDS is decoded.",
    "counts": [
        {"event": k, "src": s, "address": hex(a), "length": n, "count": v}
        for (k, s, a, n), v in sorted(counts.items())
    ],
    "messages": [
        {
            "event": k,
            "src": s,
            "address": hex(a),
            "node": None if n is None else hex(n),
            "uds": u,
            "count": v,
        }
        for (k, s, a, n, u), v in sorted(messages.items(), key=lambda x: str(x[0]))
    ],
    "files": observations,
}
out = (
    root
    / "build/work/f33-network-gateway-20260912/reproduced-saved-gateway-observation.json"
)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(result, indent=2) + "\n")
print("FILES", len(files), "DIAGNOSTIC FRAMES", sum(counts.values()))
for row in result["messages"]:
    print(row)
print("OUTPUT", out)
