# Security

Three independent security domains. They share a broad AES construction shape
but use different secrets, handlers, sessions, and state — do not conflate
them.

| Domain | Purpose | Start here |
|---|---|---|
| Bootloader SecurityAccess + payload gate | Unlock programming services; authenticated download | [bootloader-payload-gate.md](bootloader-payload-gate.md) |
| Application SecurityAccess | Extended-session level 2 unlock | [application-security-access.md](application-security-access.md) |
| SecOC | Runtime CAN message authentication | [secoc/README.md](secoc/README.md) |

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
- SecOC findings here are specific to this calibration's unprovisioned/default
  key state. A provisioned unit must be tested dynamically; see
  [secoc/key-storage-and-lifecycle.md](secoc/key-storage-and-lifecycle.md).
