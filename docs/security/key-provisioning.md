# Key provisioning

Provisioning evidence is split by mechanism. Do not collapse these into one
"Toyota key" path:

- [MACKey Registration](mackey-registration.md) — Techstream online
  `ECUExchangeKey` request/response workflow. Exact vehicle write protocol and
  SecOC relationship remain open.
- [Bootloader payload gate](bootloader-payload-gate.md) — Sienna firmware-side
  programming authorization and authenticated payload handling.
- [Application SecurityAccess](application-security-access.md) — separate
  application diagnostic unlock.
- [SecOC](secoc/README.md) — runtime message-authentication path and ICU-S slot
  state; no proven join to Techstream MACKey Registration yet.

CUW reprogramming authorization is documented in
[Techstream tooling](../tooling/techstream.md) §5 and is independent of the
MACKey workflow.
