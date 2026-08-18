# Current priorities

Short execution queue only. This page answers **what should we do next?** It is
not a historical roadmap and should not become one. Detailed unresolved state
belongs in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md); completed work belongs in
[FINDINGS.md](FINDINGS.md) and the canonical subsystem reports.

## P0 — highest information gain

### 1. Live slot-4 command-5 permission

**Question:** does provisioned ICU-S slot 4 actually permit command 5 MAC
generation in initialized application context?

Why this matters: static software already proves the application has selector-4
command-5 plumbing and a stock RID `0x100F` activation path. A positive hardware
result would make a production-resident signing proxy much more attractive than
extracting the key itself.

Ready now:

- bounded command-5 experiment under `exploit/command5/`;
- fresh-boot control/experiment artifact model;
- F181/route binding, chronology, RTT/jitter, pre/post DTC snapshots;
- no same-boot re-arm assumption.

Positive criterion: current-run generated output changes from the pre-stimulus
baseline under selector 4. A DTC-only negative does not separate command failure
from expected-result mismatch.

Canonical:
[../security/secoc/software-path-assessment.md](../security/secoc/software-path-assessment.md) ·
[../security/secoc/sender-implementation.md](../security/secoc/sender-implementation.md).

### 2. XCP physical reachability

**Question:** does the real bench/vehicle route deliver `0x7F7` to the EPS and
return `0x7F8`?

Why this matters: COM-005/007 already establish a powerful unauthenticated
application surface. If reachable, XCP immediately becomes the preferred
non-invasive dynamic observer for steering/SecOC experiments.

Ready now:

- CONNECT-only `exploit/followups/xcp_reachability.py`;
- bounded read probe;
- read-only DAQ profiles for actuation and diagnostic state.

First live step must remain CONNECT/read-only. Do not start by exercising the
F0/EC memory writers on a valuable ECU.

Canonical:
[../communications/xcp-command-dispatch.md](../communications/xcp-command-dispatch.md).

### 3. Acquire a foreign CodeFlash with steering SecOC profiles

The generic-transfer milestone is no longer artifact-blocked: tracked Corolla
`8965H1202000` independently resolves Gate-2, startup/scheduler, COM, and its
actual three-record SecOC queue. That image correctly reports the current
`0x2E4/0x131` steering bridge as unsupported, so the next acquisition should be
chosen for **applicability**, not merely foreignness.

The first command for any acquired EPS image remains:

```bash
tools/resolve_ephemeral_runtime_image.sh path/to/CodeFlash.bin \
  build/target-ephemeral-runtime.json
```

This one result tests Gate-2 transfer, callback-free startup/scheduler transfer,
SecOC queue/COM geometry, and whether exact image-bound RAM retention evidence
exists. Do not add a software-ID offset row to make a foreign image pass.

Highest-value targets are now ones likely to contain protected steering records:
Span's distinct `8965F1208000`, `8965B4514000`, or a blurbdust-supported F3/F4
calibration with an independently observed steering profile. `8965H1202000` is
already the negative-capability regression and should not be counted again as an
unresolved transfer target.

Why this matters: the H image has already proved the semantic Gate-2/runtime
resolver can transfer without Sienna offsets. The next image can answer the
remaining higher-value question: whether the current steering bridge and its
retained-RAM geometry generalize to a second **applicable** EPS. It can also
advance MEM-SAFE-001, XCP, diagnostic-policy, command-5/8, boot-SA, and
provisioning comparisons.

Ready now:

- read-only dumper under `exploit/dumper/`;
- `tools/check_variant_acquisition.py` for geometry/SHA/provenance/readiness;
- structural scanner and semantic patch resolver.

Canonical:
[../tooling/variant-acquisition-readiness.md](../tooling/variant-acquisition-readiness.md) ·
[../variants/README.md](../variants/README.md).

## P1 — decisive hardware proofs

### 4. Gate-2 MAC28 causal proof

The corrected compare-neutralization patch and evidence pipeline are locally
complete. yc's 2026-08-16 RAV4 Prime field report strongly corroborates the
correct Gate-2 direction, but because it forced the older profile and used a
dummy key it does not isolate MAC28. The missing decisive result is still the
three-phase behavioral experiment on matching hardware:

1. stock baseline works;
2. MAC28-only ablation is rejected on the same stock firmware;
3. the same ablation is accepted after the semantically resolved Gate-2 patch.

Write/reboot success by itself is **not** proof.

Ready now: `exploit/behavioral_proof/` and the manifest patch/restore tooling.

### 5. Dynamic steering-command → actuation discriminator

Static work has closed the obvious and non-obvious transfer paths from protected
`0x2E4`/`0x131` command state to the identified d/q reference cells without
finding a direct join. The next useful evidence is dynamic, not another generic
xref sweep.

Preferred setup if XCP is reachable: use the read-only DAQ
`actuation-discriminator` profile while separately applying valid signed command
modes on an isolated bench.

Canonical:
[../architecture/control-partition.md](../architecture/control-partition.md).

### 6. Passive command-8 / provisioning provenance

SECOC-047/048 statically close the second CAN-fed command-8 client and the
cross-bank completion-attribution bug. What is missing is production context:

- does RID `0x100E` / CAN `0x13..0x1A` appear during legitimate provisioning?
- how does dealer tooling interpret RID `0x1010` status `02` with zero proof?
- is any bank-0 terminal state externally observable?

Prefer passive capture of a legitimate flow. Do not synthesize random command-8
packages on the only original ECU.

### 7. Ephemeral SecOC scheduler bridge

The static architecture is now complete enough to stop searching for a stock
post-init callback. On `8965B4512000`, the pinned public encrypted RAM-dump
fixture already satisfies the exact authenticated 4 KiB payload gate with zero
DID-0201/0202 inputs; after its one successful `0x10F0`, MEM-SAFE-001 gives
boot-context RAM code. `FEBF0000..FEBF0307` is retained application-RWX, and the
pinned callback-free runtime fits there at 704 bytes with 72 bytes headroom.
The runtime reproduces stock startup, owns the TAUJ0-CH3 foreground schedule,
and bridges only marked zero-MAC `0x2E4/0x131` through stock
`application_com_rx_indication` after stock SecOC processing but before the
normal COM/system-mode/control task.

Highest-value next evidence, in order:

1. on an isolated bench, use the audited 332-byte
   `exploit/ephemeral_runtime/canary.c` build; post-auth substitute it, trigger
   the existing FF00 callback path, and read heartbeat `FEBFFBF0` through
   `application_rmba_probe.py --probe-ephemeral-canary`; prove foreground
   progression plus hardware-reset return to stock;
2. prove one-shot marked-frame queue capture with no COM delivery;
3. enable stock-COM delivery and run the existing three-phase behavioral proof.

For another EPS calibration, first join its software ID against
`data/variant_bootstrap_profiles.json`: bootstrap reuse is already established
for multiple B4/F3/F4 targets, and tracked `8965H1202000` now provides a direct
field-observed foreign execution case. Keep that evidence separate from exact
encrypted-fixture identity, from per-image retained-RWX/scheduler geometry, and
from whether the resolved queue actually contains `0x2E4/0x131`.

Do not spend more static effort on generic callback hunting unless one of those
dynamic steps falsifies a concrete invariant. Canonical:
[../security/ephemeral-secoc-bypass.md](../security/ephemeral-secoc-bypass.md) ·
`exploit/ephemeral_runtime/`.

## P2 — useful when a specific dependency appears

- **Reset-window replay / future-sync poisoning / tag-guess throughput / FD
  suffix behavior:** host trial constructors exist; run on an isolated bench
  when SecOC behavior itself is the active question.
- **Live stale-RDBI confirmation:** easy and bounded, but lower strategic value
  than the P0/P1 discriminators.
- **CommunicationControl availability experiment:** reversible and ready; useful
  for availability characterization, not a steering primitive.
- **Command 13 characterization:** only interesting as a possible Renesas SHE
  deviation; standard SHE already closes the old nonvolatile-key-export idea.
- **Power/EM / fault injection:** fallback paths after software/vehicle-side
  options are exhausted and physical topology is confirmed.

## Static work that remains worthwhile

Use the exploit-interest cohorts selectively. The reviewed-candidate ledger
`data/exploit_interest_reviewed_candidates.csv` prevents already-audited
functions from resurfacing as unexplained hits. New static work should have a
specific exploit hypothesis, externally reachable sink, or variant-transfer
question.

The remaining explicitly open cohort rows without a recovered ingress root are
not reason enough for another broad sweep by themselves.

## Do not repeat without new evidence

These directions have reached diminishing returns or have already been closed:

- another generic whole-image decompilation/semantic sweep;
- generic authenticated-command → d/q xref searching without a new concrete
  bridge;
- direct-reference searches for an XCP-window execution consumer using the same
  existing graph;
- interpreting the compiled-out `FF*16` KAT as the live slot-4 key;
- treating object 15 as proof of the current live ICU-S key;
- treating command 13 as a standard SHE nonvolatile-key export route;
- building software-ID → patch-offset lookup tables instead of improving the
  semantic resolver.

## When this page changes

Update this file only when the **execution order** changes. If an item is
resolved, move the result to the appropriate subsystem report / `FINDINGS.md`
and remove it here instead of appending a completion diary.
