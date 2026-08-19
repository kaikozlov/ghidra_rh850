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
3. the target's actual raw SecOC queue/record and COM update geometry;
4. whether that queue contains the classic `0x2E4` / `0x131` records required by
   the current steering bridge;
5. authenticated-download plus application-retention RAM geometry for the exact
   CodeFlash image.

If the control/queue structure resolves but either steering capability or exact
RAM geometry does not, the manifest remains useful for variant comparison but is
explicitly **not runtime-build-ready**. Missing steering records are reported as
`semantic-resolved-steering-unsupported`, not as a resolver failure.

## One-command fresh-image workflow

```bash
tools/resolve_ephemeral_runtime_image.sh path/to/CodeFlash.bin \
  build/new_eps_ephemeral_runtime.json
```

The input may be either a bare 1 MiB CodeFlash image or the tracked range-dumper
shape: 2 MiB with an entirely `0xFF` upper 1 MiB. The latter is normalized only
in a disposable workspace, while the output manifest preserves both source and
normalized hashes. Any other oversized/truncated geometry fails closed. The
wrapper creates a disposable project below
`build/ephemeral-runtime-targets/<normalized-sha>/`; it never opens or changes
committed `project/` and never modifies the input image.

The same fresh import runs, in order:

1. `ApplyRecoveredGpTpContext.java` — recover boot/application GP+TP directly
   from the target's repeated startup `mov immediate,gp` / `mov immediate,tp`
   pairs and apply that context to the disposable project;
2. `ResolveSecocAcceptanceGate.java` — existing calibration-independent Gate-2
   resolver;
3. `ResolveEphemeralRuntime.java` — callback-free startup/scheduler control
   resolver;
4. `build_ephemeral_runtime_manifest.py` — raw-machine completion, SecOC record
   scan, and RAM-geometry join.

The context pre-pass is intentionally target-native. It does not copy the
canonical Sienna GP/TP constants and it does not select the most common write to
`tp`, because RH850 code also uses that register as ordinary scratch state. The
raw completion layer below still recovers GP/TP independently and requires exact
agreement with any Ghidra-resolved values, so the context pass adds analysis
quality without weakening the existing fail-closed cross-check.

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
- **application GP/TP:** immediates loaded inside the resolved context initializer;
- **foreground tick counter:** GP-relative byte increment tail in the resolved
  foreground loop;
- **`Com_RxIndication`:** unique register/prologue prefix, independent of
  calibration addresses;
- **COM validity/update helper:** generated `PDU < limit` helper shape, with RAM
  bases derived from GP-relative displacements;
- **SecOC queue-1 storage case:** generated three-output-store contract, with
  descriptor / queue-head / raw-buffer bases derived from GP-relative
  displacements and the configured record count recovered from the `+0xC`
  output; harmless compiler scheduling of the success return is tolerated;
- **SecOC record table:** Gate-2's own `index * 0x50` plus TP-relative table-base
  machine shape identifies the table without any CAN-ID signature.

If Ghidra already resolved one of these values, the raw result must agree with
it exactly. A disagreement aborts manifest generation.

## Raw SecOC record join

The builder no longer treats Sienna's six-record order as a discovery signature.
The queue-1 helper supplies the target's configured **record count**, and Gate-2
itself supplies the table base. Each of those records must independently satisfy
the generated Level-1 shape before it is accepted.

For each configured record the builder reads only raw descriptor fields:

- CAN ID at `+0x0A`;
- raw secured-buffer offset at `+0x28`;
- application PDU ID at `+0x34` (with its generated duplicate);
- secured PDU length at `+0x3C` (with its generated duplicate).

Only after the target's real table is recovered does the current steering bridge
ask for `0x2E4` and `0x131`. When both exist with the classic 8-byte shape, their
addresses are derived algebraically:

```text
raw_buffer     = secoc_raw_base + record.raw_offset
descriptor     = secoc_descriptor_base + record_index * 8
update_counter = com_update_counter_base + record.pdu_id
```

If either steering record is absent or has an incompatible secured length, the
manifest records the missing/incompatible IDs and returns
`semantic-resolved-steering-unsupported`. This is a successful capability
classification: the target's SecOC architecture resolved, but the current Sienna
steering bridge does not apply.

## First foreign regression: Corolla `8965H1202000`

The tracked albinoelephant CodeFlash is the first non-Sienna image run through
the complete workflow. The 2 MiB source range dump has SHA-256
`97f9d42d936b97a99e7ab3d3ef20c6fb4c1fc3cc2ba199f6b158675a1709aee6`;
after the validated all-`0xFF` upper half is removed, the exact 1 MiB CodeFlash
SHA-256 is
`0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f`.

Without target offsets, the fresh Ghidra stage resolves Gate-2 at `0x88C16` and
the runtime control skeleton. Raw completion then recovers:

```text
boot handoff          0x1394
startup coordinator   0x5CAAC
context init          0x6A8C4
foreground loop       0x5F30C
aggregate             0x5FAF2
GP / TP               FEBEB800 / 0x23D6C
Com_RxIndication      0x76A3C
COM timeout helper    0x87A82
queue helper / case   0x87B72 / 0x87B92
queue record count    3
record table          0x2572C
```

The three Gate-2 queue records are `0x00F`, `0x0D7`, and `0x0B6`; the latter two
are 32-byte secured records. There is no queue-1 `0x2E4` or `0x131`, so the
foreign manifest intentionally ends as
`semantic-resolved-steering-unsupported`. This image exposed the old resolver's
two Sienna overfits—exact queue-helper bytes and exact six-ID table order—and is
now the regression proving they are gone. It also exposed a software-ID parser
bug where the first 12 characters of the longer ECU serial looked like an ID;
token-boundary extraction now rejects that false positive.

The same image independently resolves the Gate-2 CMP patch at `0x88C62` (`e0d1 -> e001`) and validates the stock/modified CRC construction, so semantic
Gate resolution is known to transfer even where steering-bridge applicability
does not. Canonical firmware interpretation is in
[../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md).

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
  blurbdust F3/F4 patcher targets;
- direct field-observed range-payload execution on tracked `8965H1202000`, whose
  CodeFlash also carries the same boot SA root and application/payload roots.

`data/variant_bootstrap_profiles.json` records that evidence independently from
RAM-retention geometry. The target manifest joins a bootstrap profile by raw
software ID when one is known. `build_substitution_plan.py` no longer rejects a
foreign CodeFlash merely because its SHA is not Sienna's.

The important narrower boundary is **exact encrypted fixture identity**. The
repository's `ram_dump_payload.bin` is cryptographically verified byte-for-byte
against `8965B4512000`. Other family rows retain their own evidence grade (`8965H1202000` is now
field-observed; the B4/F3/F4 rows remain external-source); when the exact local
fixture is not pinned for that target, the planner requires
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
- the tracked `8965H1202000` range dump normalizes reproducibly and resolves the
  exact three-record foreign queue;
- missing `0x2E4/0x131` produces an unsupported-capability manifest rather than
  an exception or a Sienna fallback;
- the disposable wrapper recovers/applies target GP/TP before Gate-2 and runtime resolution.

The next strategically useful CodeFlash is not merely "another target"; it is a
foreign EPS whose resolved queue actually contains classic `0x2E4/0x131`, so
that steering-bridge geometry and application RAM retention can be tested on a
second applicable calibration. Run the resolver unchanged first; do not add an
offset row to make it pass.
