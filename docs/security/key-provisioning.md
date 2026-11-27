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

## ICU-S command-8 lifecycle

RID `0x1010` enters at `0x96354` and dispatches through
`0x8AA1E -> 0x68E16 -> 0x6823C -> 0x88936 -> 0x870A8 -> 0x86E62 ->
0x8704C -> 0x8997A`, then writes `ICUSCMD = 8`. This is protected ICU-S
storage, not a CPU FACI DataFlash write.

The required reset property is atomic replacement of the authorized key and
counter. The machine supplies scripted command responses; slot persistence
across an interrupted update is unverified.

CUW reprogramming authorization is documented in
[Techstream tooling](../tooling/techstream.md) §5 and is independent of the
MACKey workflow.
