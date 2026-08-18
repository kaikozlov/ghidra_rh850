# Ephemeral runtime semantic target resolver

> **Scope:** transfer the callback-free RAM scheduler / SecOC-COM bridge to a
> new RH850/P1M-E EPS CodeFlash image without inheriting Sienna offsets.
>
> **Canonical runtime analysis:**
> [../security/ephemeral-secoc-bypass.md](../security/ephemeral-secoc-bypass.md)
>
> **Resolver:** `tools/resolve_ephemeral_runtime_image.sh`
>
> **Manifest builder:** `tools/build_ephemeral_runtime_manifest.py`

## Goal

The Sienna `8965B4512000` runtime is only useful for newer Toyota vehicles if
its dependencies can be rediscovered from the target firmware itself. A table
of software-ID-to-address offsets would not establish that the same architecture
exists and would make a wrong calibration look deployable.

The runtime therefore consumes one **SHA-bound target manifest**. The manifest
must independently establish four classes of evidence:

1. the boot -> application transition and foreground scheduler skeleton;
2. the SecOC-owned foreground subtask and the post-SecOC COM/control splice;
3. the raw SecOC queue/record and COM update geometry used by `0x2E4` / `0x131`;
4. authenticated-download plus application-retention RAM geometry for the exact
   CodeFlash image.

If the first three resolve but the fourth does not, the manifest is useful for
variant comparison but is explicitly **not runtime-build-ready**.

## One-command fresh-image workflow

```bash
tools/resolve_ephemeral_runtime_image.sh path/to/CodeFlash.bin \
  build/new_eps_ephemeral_runtime.json
```

The input must be a bare 1 MiB CodeFlash image. The wrapper creates a disposable
project below `build/ephemeral-runtime-targets/<sha>/`; it never opens or changes
committed `project/` and never modifies the input image.

The same fresh import runs, in order:

1. `ResolveSecocAcceptanceGate.java` — existing calibration-independent Gate-2
   resolver;
2. `ResolveEphemeralRuntime.java` — callback-free startup/scheduler control
   resolver;
3. `build_ephemeral_runtime_manifest.py` — raw-machine completion, SecOC record
   scan, and RAM-geometry join.

For the analyzed Sienna, the fresh unannotated import intentionally reports
`control-resolved`: bare Ghidra has no LocalRAM blocks and does not automatically
promote several pointer-table-only callbacks. The raw-image layer then recovers
those missing anchors and the final manifest becomes `runtime-build-ready`.

## Level-1 control resolver

`ResolveEphemeralRuntime.java` embeds no Sienna target addresses. It accepts only
the currently recovered machine/CFG family and fails closed when it becomes
ambiguous.

It resolves:

- application startup coordinator;
- application CPU-context initializer from its `EBASE/INTBP/GP/TP/SP` shape;
- the consecutive stock startup `jarl disp22` span and final initializer;
- TAUJ foreground bit/displacement and top-level call sequence;
- the unique foreground child whose direct-call cone reaches the resolved
  Gate-2 function;
- the six-call aggregate shape and the position of the SecOC/control splice.

The compact runtime currently requires the same Level-1 scheduler shape as the
Sienna implementation: ten foreground direct calls, aggregate at index 5, and a
six-call aggregate with the Gate-2-owning communication task at index 1. A
foreign image with different task geometry may still be semantically
interesting, but the current code generator refuses to build it until that new
shape is reviewed.

## Raw-machine completion

Bare CodeFlash analysis does not need imported RAM blocks or manually seeded
callback functions. `build_ephemeral_runtime_manifest.py` recovers the missing
anchors directly from target-independent RH850/compiler shapes:

- **boot handoff:** unique prologue + five direct `jarl disp22` calls +
  `cmp r0,r10`;
- **application GP:** immediate loaded inside the resolved context initializer;
- **foreground tick counter:** GP-relative byte increment tail in the resolved
  foreground loop;
- **`Com_RxIndication`:** unique register/prologue prefix, independent of
  calibration addresses;
- **COM validity/update helper:** generated `PDU < limit` helper shape, with RAM
  bases derived from GP-relative displacements;
- **SecOC queue-storage helper:** generated three-store helper shape, with
  descriptor / queue-head / raw-buffer bases derived from GP-relative
  displacements.

If Ghidra already resolved one of these values, the raw result must agree with
it exactly. A disagreement aborts manifest generation.

## Raw SecOC record join

The builder requires one six-record `0x50`-byte SecOC table with the recovered
Level-1 order:

```text
0x00F, 0x2E4, 0x131, 0x132, 0x090, 0x0D7
```

For each record it reads only raw descriptor fields:

- CAN ID at `+0x0A`;
- raw secured-buffer offset at `+0x28`;
- application PDU ID at `+0x34`;
- secured PDU length at `+0x3C`.

The two steering bridge profiles are then derived rather than hard-coded:

```text
raw_buffer    = secoc_raw_base + record.raw_offset
descriptor    = secoc_descriptor_base + record_index * 8
update_counter = com_update_counter_base + record.pdu_id
```

The current runtime requires both `0x2E4` and `0x131` to retain the classic
8-byte secured-record shape.

## RAM execution and retention are a separate proof

Application similarity is not enough to inherit RAM geometry. The resolver
joins `data/variant_ram_exec_requirements.json` only when its entry is bound to
the **exact CodeFlash SHA-256**.

A runtime-build-ready target presently needs verified values for:

- authenticated download base/size;
- payload callback base and callback cell;
- link VMA;
- application-retained R/W/X base/end/size.

A canary additionally needs a target-specific verified observation cell. This
is deliberately separate from retained-code geometry. On Sienna the observed
cell remains `FEBFFBF0`; it now comes from the target manifest rather than from
`canary.c`.

External evidence such as a reported `FEBE0000` link VMA is retained as useful
variant evidence but cannot make a target build-ready until it is bound to a
specific firmware image and the retention/MPU geometry is proven.

Supplying the Sienna variant ID against a foreign CodeFlash SHA is rejected.
There is no fallback that clones Sienna RAM addresses.

## Target-driven builders

Once the manifest says `runtime_build_ready=true`, both RH850 sources are built
from a generated `target_config.h`:

```bash
uv run --locked python exploit/ephemeral_runtime/build_canary.py \
  --manifest build/new_eps_ephemeral_runtime.json

uv run --locked python exploit/ephemeral_runtime/build_shellcode.py \
  --manifest build/new_eps_ephemeral_runtime.json
```

`main.c` and `canary.c` contain no calibration addresses for boot calls,
application startup, scheduler calls, SecOC queue cells, COM delivery, or tick
state. The generated header is the sole address contract.

For Sienna this refactor reproduces both previously audited executables
byte-for-byte:

```text
bridge: 704 bytes
SHA-256 8f486d36ae38d233165563ad2cc4a71d006cf5c8cf9a876345a3b6ab72f10495

canary: 332 bytes
SHA-256 81176c6e1c33451cfa63bd3b4a0e07b8b0fb952c70b3d67442f1a294ed6b651e
```

That identity is a regression property: the semantic manifest reconstructs the
same Sienna executable rather than a second hard-coded implementation.

## Bootstrap is a separate cross-vehicle evidence axis

A build-ready runtime manifest does **not** by itself prove bootloader bootstrap
compatibility, but the bootstrap is also **not Sienna-only**. Existing
SECOC-024/028 evidence already establishes a reusable Denso EPS family:

- shared boot SecurityAccess secret `f05f36b7d78c03e24ab4faef2a57d044`;
- `0203 -> 0201 -> 0202`, with zero `0201/0202` in the public tooling;
- authenticated download at `FEBF0000`, size `0x1000`;
- `0x10F0` verify and `0xFF00` execution flow;
- public-payload/bootstrap reuse across listed `8965B4x` targets and the
  blurbdust F3/F4 patcher targets.

`data/variant_bootstrap_profiles.json` records that evidence independently from
RAM-retention geometry. The target manifest joins a bootstrap profile by raw
software ID when one is known. `build_substitution_plan.py` no longer rejects a
foreign CodeFlash merely because its SHA is not Sienna's.

The important narrower boundary is **exact encrypted fixture identity**. The
repository's `ram_dump_payload.bin` is cryptographically verified byte-for-byte
against `8965B4512000`. Other family rows retain their external-source grade;
when the exact local fixture is not pinned for that target, the planner requires
an explicit target-accepted 4 KiB fixture plus its SHA-256. Thus three questions
remain independent: bootstrap-family compatibility, exact payload bytes, and
application-time RAM retention/scheduler geometry.

## Fail-closed regression coverage

`tests/verify_ephemeral_runtime_resolver.py` pins the fresh-import result and
mutates individual machine signatures. It requires rejection when the boot
handoff, `Com_RxIndication`, queue helper, timeout helper, SecOC record table, or
RAM-geometry identity no longer matches.

It also asserts that:

- the semantic resolver source contains no Sienna target addresses;
- foreign SHA cannot select Sienna geometry;
- external-only geometry remains non-buildable;
- the disposable wrapper runs Gate-2 resolution before runtime resolution.

The next useful transfer artifact is another target CodeFlash image. Run the
resolver unchanged first; do not add an offset row to make it pass.
