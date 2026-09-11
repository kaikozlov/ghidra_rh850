# Exact continuous signer from the working steering handoff

This directory preserves the exact EPS LocalRAM artifacts identified in the
live handoff immediately preceding the operator's report that the Camry was
steering.  The artifacts are tracked verbatim; they are not reconstructed at
deployment time.

The working runtime was a two-part payload, not one binary:

| Artifact | Size | SHA-256 | Role |
|---|---:|---|---|
| `camry_f33_b6_inline_signer_continuous_payload.bin` | 4096 | `01ce993425e910a6ea37473580adb6e641bdff56a3568492d4c9e0388e02fc6c` | authenticated NRTD payload; installs the high-tail resident |
| `camry_f33_b6_inline_signer_continuous_resident.bin` | 524 | `31b1b2c31007f130d6b4679a0c99f5903a58f748daf11978f9c52f504aea3a3a` | resident at `0xFEBFF9F0` |
| `camry_f33_b6_inline_signer_continuous_helper.bin` | 588 | `74315a067cfe457c945cbeadb0e1432e70765bbe36ef022fc57ffad272cb4469` | unpadded helper at `0xFEBF0000` |
| `camry_f33_b6_inline_signer_continuous_helper_padded.bin` | 600 | `b417e12dde0dc7d6478ea6f242fe9eaa246a00a9fbbcc711a5d2d3adcf159a28` | exact 150-word C6 transfer image |
| `camry_f33_b6_inline_signer_continuous.bin` | 652 | `2b6fa690f3ea1ece5f301e976e2f4f781f802ff92c1a6667b8a61ae4d18deb45` | build staging image; not the authenticated 4 KiB payload |

The Comma's original temporary `/tmp/f33-valid-helper.bin` was no longer
reachable during preservation.  Its full SHA-256 had been recorded live.  The
recovered source emits the same complete `b417e12d...159a` SHA-256, and the
payload and resident likewise reproduce their complete recorded hashes.  The
tracked binaries are therefore byte-identical to the recorded live identities
under the ordinary SHA-256 collision assumption; they are not merely similar
or behaviorally equivalent reconstructions.

The complete build metadata is
`camry_f33_b6_inline_signer_continuous.json`.  The verbatim helper source is
`exploit/ephemeral_runtime/camry_f33_b6_inline_signer_continuous_helper.S`.
The builder rejects the continuous mode unless the emitted padded helper is
exactly `b417e12d...159a`.

## Exact behavior

The resident calls the helper after the stock receive-ring drain and before
the stock B6 SecOC consumer.  The helper first signs one untouched native B6
through ICU-S command 5 and requires its generated `FV4 || CMAC28` trailer to
equal Toyota's received trailer.  It fails closed if that oracle or freshness
reconstruction fails.

With a nonzero C7 mailbox sequence, it then handles every distinct native B6:

```text
00 C7 sequence 00 target_hi target_lo 00 00
```

It changes application bytes B3..B9 only: Target Lateral ID 11, signed big-endian
target in B4:B5, signal 265 cleared, and contribution bytes B8/B9 set to
100/100.  The command-5 domain is `00 B6 || B0..B27 || freshness48`, using
selector 4, config type 1, 36 input bytes, and 16 output bytes.  It writes the
new B28..B31 `FV4 || CMAC28` trailer before the unmodified stock receiver path.
A C7 sequence of zero disables replacement immediately and leaves native B6
untouched.  The helper sends no CAN frame and writes no flash.

The continuous helper differs from the reviewed one-shot helper at the sequence
gate:

```asm
    ld.bu 0x4a78[gp], r7
    cmp r8, r7
    nop
    st.b r8, 0x4a78[gp]
```

The one-shot source has `be .L_return` in place of that `nop`.  This is the only
source-instruction substitution needed to reproduce the exact live-loaded
`b417e12d...159a` image.  The branch encodes to four bytes and the RH850 NOP to
two, so the continuous helper is 588 bytes rather than the one-shot helper's
590 bytes and the following helper code moves by two bytes.

## Exact replay selection

Place this directory on the Comma and select these files explicitly.  Do not
run the launcher with its packaged defaults, because those defaults may select
the later one-shot helper.

```sh
cd /data/camry-f33-car-kit
export F33_INLINE_PAYLOAD_PATH=/data/camry-f33-working-steering/runtime/camry_f33_b6_inline_signer_continuous_payload.bin
export F33_INLINE_HELPER_PATH=/data/camry-f33-working-steering/runtime/camry_f33_b6_inline_signer_continuous_helper_padded.bin
export F33_INLINE_META_PATH=/data/camry-f33-working-steering/runtime/camry_f33_b6_inline_signer_continuous.json
./f33-secoc doctor
```

Starting with the EPS fully powered off, enter NRTD while Park/stationary, run
`./f33-secoc install`, transition directly from NRTD to READY without an OFF
cycle, and run `./f33-secoc load-arm` while still Park/stationary.  Accept the
load only if byte-exact helper readback and the native-trailer oracle both pass.
Return Panda ownership to exactly one clean manager/pandad tree before driving.
Full EPS power-off removes both volatile images.

The C7-enabled openpilot worktree is preserved separately as
`../kai-opendbc-c7-working-tree.patch`; its base and deployed file hashes are in
`../summary.json`.

## Live warning clear

The programming transition records U0131-87 in multiple Toyota ECUs.  On this
exact car, an earlier parked/READY pass cleared the warning without an ignition
cycle by sending physical UDS `14 FF FF FF` to `0x7A1`, `0x7B3`, `0x7C4`,
`0x7D0`, `0x792`, and `0x7A2`, followed by functional OBD Mode 04 frame
`01 04 00 00 00 00 00 00` on `0x7DF`.  Clearing DTC state does not reset the
EPS and therefore does not inherently remove its LocalRAM resident/helper.

That live clear is proven to remove the historical warning state, but it is not
yet proven to restore DRCC availability in the same ignition cycle.  DRCC may
remain latched unavailable until restart even after the dash warning clears.
