# Security

Three independent security domains. They share a broad AES construction shape
but use different secrets, handlers, sessions, and state — do not conflate
them.

| Domain | Purpose | Start here |
|---|---|---|
| Bootloader SecurityAccess + payload gate | Unlock programming services; authenticated download | [bootloader-payload-gate.md](bootloader-payload-gate.md) |
| Application SecurityAccess | Extended-session level 2 unlock | [application-security-access.md](application-security-access.md) |
| SecOC | Runtime CAN message authentication and ICU-S software-path assessment | [secoc/README.md](secoc/README.md) |
| Memory-safety audit | Externally reachable input-handler vulnerabilities | [memory-safety-audit.md](memory-safety-audit.md) |

Dealer/tooling key-provisioning evidence is separate from those firmware
domains. Start with [key-provisioning.md](key-provisioning.md); the recovered
Techstream online flow is in
[mackey-registration.md](mackey-registration.md). Its relationship to SecOC is
not yet proven.

## Important distinctions

- Bootloader SA uses `SEED_KEY_SECRET` (`0xBFE8`) and
  `PAYLOAD_BUILD_SECRET` (`0xBFD8`); application SA level 2 uses a separate
  16-byte secret at CodeFlash `0x20840`. The algorithm template is the same
  (`expected = AES-ENC(AES-DEC(secret, data_record), seed)`); the secrets and
  call paths are not.
- Application SA level 1 (`01/02`, programming) is a **compiled stub**
  (`return 1`). Only level 2 (`03/04`, extended) is functional.
- This Sienna calibration has **no configured SecurityAccess gating at the
  Dcm dispatch layer** — all 17 services have `sec_count=0`, all DIDs have no
  security level > 0. The machinery is wired and exercised; the policy tables
  are empty. The Corolla is a different calibration and may populate them —
  see [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md).
- SecOC verifies through ICU-S slot 4, but static CodeFlash does not determine
  the donor's live key state. The former `FF*16` inference was disproved
  because the KAT is compiled out. A paired command-5 generation primitive
  exists; its only configured stock caller is a dormant test harness, and
  Stage 7 strengthens that harness's activator to a whole-image bounded static
  negative. The stock graph has no production SecOC transmit path. Separately,
  the initialized application exposes serialized command-5 plumbing and a
  foreground hook location sufficient to specify a minimum signing proxy;
  live slot-4 permission and performance remain dynamic. See
  [secoc/application-chain.md](secoc/application-chain.md),
  [secoc/sender-implementation.md](secoc/sender-implementation.md), and
  [secoc/software-path-assessment.md](secoc/software-path-assessment.md).
