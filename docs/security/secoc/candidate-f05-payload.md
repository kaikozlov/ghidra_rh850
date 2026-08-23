# Vance candidate-f05 payload

Canonical analysis of
`payload_candidate_f05_dataflash_ff200000_ff208000.bin` from Vance's pinned
`20260531_othersienna_secoc_bundle_v3.zip`. This is an external deployment
artifact for the `8965B4514000` investigation, not firmware from that variant
and not evidence that the partner ECU executed it.

## Conclusion

Candidate-f05 is a **full 32 KiB DataFlash dump payload**. It reads every
32-bit word in `0xFF200000..0xFF207FFF` and emits 8,192 classic-CAN frames on
`0x7A9` through RSCFD transmit slot 16. Each frame is:

```text
07 || address_low24_le || memory_word_le32
```

It is not an ICU-S probe, key-slot scan, RAM dump, CodeFlash dump, equality
oracle, or signature search. It reads the structural object-15 field at
`0xFF206E14` only because that word lies inside the complete DataFlash range;
there is no object-15-specific literal, branch, or parser.

The standard and candidate payloads implement the same dump loop and wire
format. Candidate-f05 was recompiled with a call-capable stack frame and calls
bootloader reset target `0x157E` after the final word. The standard payload
instead branches to itself forever. That code relocation and different stack
layout explain the apparently large 360-byte pre-callback diff.

Evidence source: pinned external payload bytes plus the committed Sienna
CodeFlash secrets. Confidence: **verified** for authentication, bytes,
references, loop bounds, transport, and terminal behavior; **bounded** for
human provenance and whether any ECU ran it.

## Independent payload reproduction

The transformations were first reproduced directly with OpenSSL AES-128 and an
independent CRC32 calculation, then encoded in the deterministic generator and
test. DID `0x201` and IV `0x202` are both 16 zero bytes in these fixtures.

| Property | Standard DataFlash payload | Candidate-f05 |
|---|---|---|
| Ciphertext SHA-256 | `d48988366b5e6d2ddd7438caca5e6f6f02daba9b650263c323a2ffd770a06e34` | `296d87d2e89b9c7e800122e4c7f6d3b9c876362e52586530cdd53c86ba1116f5` |
| Build-secret source | `PAYLOAD_BUILD_SECRET @ 0xBFD8` | `SEED_KEY_SECRET @ 0xBFE8` |
| Derived AES key | `80d221a05622b4f9d4f287922e6c78d1` | `2b582a654ca922994ad867ab00480039` |
| Plaintext SHA-256 | `ec332718e01a3e346939fedf21833500b0fecd8ff08c5b9f218ba5724a4d3a10` | `ec39ef6c4a19c3687ee59183e2526bdea9e6d4886f11fbe4ab1f5382c484e1c0` |
| CRC32 over `0x000..0xFEF` | residue `0xFFFFFFFF` | residue `0xFFFFFFFF` |
| CMAC | `6a563caf953a8d30f8a4b52000ed5066` | `9898cc47de513f116e4fb79713276bec` |
| Callback at `+0xFD0` | `0xFEBF0000` | `0xFEBF0000` |
| CRC descriptor at `+0xFE0` | `(0xFEBF0000, 0xFF0)` | `(0xFEBF0000, 0xFF0)` |

Candidate-f05 fails both CRC and CMAC when decrypted under the normal
payload-build secret. Its valid plaintext contains neither the SecurityAccess
secret, the derived key, nor ASCII `f05`; `f05` is tied to the filename and
authentication choice, not an embedded runtime signature.

## Recovered RH850 control flow

Both plaintexts were imported independently as raw `v850e3:LE:32:default`
programs at `0xFEBF0000`. Ghidra recovered the following candidate boundaries;
the deterministic test pins the full `0x1B2`-byte body hash and the critical
instruction windows.

| Range | Recovered role |
|---|---|
| `0xFEBF0000..0xFEBF0073` | save `lp/r29`, allocate stack, materialize RSCFD pointers, disable interrupts, initialize source pointer |
| `0xFEBF0074..0xFEBF0097` | test transmit-slot status bits `0x06`; retry outer loop if busy |
| `0xFEBF0098..0xFEBF012B` | set classic DLC 8, CAN ID `0x7A9`, address marker/word data, clear FD control, request transmit |
| `0xFEBF012C..0xFEBF0145` | poll transmit completion until status bits `0x06` become nonzero |
| `0xFEBF0146..0xFEBF0177` | clear status bits with `& 0xF9`; advance source by four bytes |
| `0xFEBF0178..0xFEBF018B` | continue while the word pointer is at most `0xFF207FFC` |
| `0xFEBF018C..0xFEBF019B` | load reset target `0x157E` and call local trampoline |
| `0xFEBF019C..0xFEBF019F` | adjust `lp`, then indirect-jump to reset target |
| `0xFEBF01A0..0xFEBF01B1` | return epilogue if the reset target unexpectedly returns |

The operational pseudocode is:

```text
disable_interrupts()
for address in range(0xFF200000, 0xFF208000, 4):
    wait/retry until RSCFD transmit slot 16 is free
    slot16.DLC      = 8
    slot16.CAN_ID   = 0x7A9
    slot16.DATA0    = (address << 8) | 0x07
    slot16.DATA1    = *(uint32_t *)address
    slot16.FD_CTRL  = 0
    slot16.REQUEST |= 1
    wait until transmission completes
    slot16.STATUS &= 0xF9
call 0x157E
```

Absolute RSCFD references resolve to `0xFFD20260`, `0xFFD202E0`, and
`0xFFD24200/204/208/20C/210`. No instruction in the fully disassembled body
references the ICU-S `0xFFC5Dxxx` window, object-15 RAM `0xFEBF02E8`, a key-slot
mirror, or a second input/search range.

## Semantic diff from the standard payload

| Dimension | Result |
|---|---|
| Total plaintext bytes different | 380 / 4096 |
| Bytes different before callback slot | 360 |
| Trailer bytes different | 20: four-byte CRC adjustment plus 16-byte CMAC |
| Memory source | unchanged: full `0xFF200000..0xFF207FFF` DataFlash |
| RSCFD register set / slot | unchanged |
| CAN arbitration ID | unchanged: `0x7A9` |
| Frame format / word stride | unchanged |
| Search/probe behavior | none in either payload |
| Terminal behavior | standard: infinite self-branch; candidate: call boot reset `0x157E` |

The standard code body is 394 bytes (`0x000..0x189`). Candidate-f05 is 434
bytes (`0x000..0x1B1`) because saving `lp`, changed stack displacements, shifted
branches, the indirect-call trampoline, and the return epilogue relocate most
compiled bytes. The difference is compiler/control-flow layout, not a new
memory-search algorithm.

## Answers to the handoff questions

1. The changed pre-callback bytes are a relocated version of the same RSCFD
   DataFlash-dump loop plus a reset call and epilogue.
2. It is an alternate build of the same full DataFlash dump.
3. It reads DataFlash only. It does not read RAM or CodeFlash.
4. It does not touch `0xFFC5Dxxx` ICU-S registers.
5. It reads `0xFF206E14` incidentally within the full dump; it does not touch
   object-15 RAM or special-case object 15.
6. It performs no scan for key-slot structures.
7. It is a deterministic sequential dump, not an oracle/probe.
8. It preserves CAN ID `0x7A9` and the exact result-frame format.
9. No `f05` byte/string/signature is embedded beyond the external
   authentication/filename association.
10. Its source structure matches the pinned I-CAN-hack and Bk2ol dump-loop
    family statement-for-statement after substituting the DataFlash bounds.
    No exact candidate source file or build invocation is retained.

## Source and provenance boundary

The identical candidate ciphertext appears in Vance bundle v1, v2, and v3.
The ZIP member timestamp is `2026-05-11 02:38`; Git records Vance425 uploading
the three archives on 2026-05-31 at commits `97ba3d1`, `3ee08a4`, and
`795aeda`. The v3 README says only that it is a retained candidate and is not
used by default.

The loop is structurally the same as the pinned I-CAN-hack `shellcode/main.c`
(present by commit `4ce19cc`, 2025-03-04) and the later Bk2ol
`main_ff1ff000_ff209000.c` source (added at the pinned July 2026 revision),
including RSCFD slot 16, CAN `0x7A9`, address/data packing, status handling,
and reset target `0x157E`. This establishes the community source family, not
authorship. The retained history does not prove who compiled candidate-f05,
which exact source revision/toolchain produced it, whether choosing
`SEED_KEY_SECRET` as the build secret was intentional, or what failed/succeeded
vehicle experiment motivated retaining it. The filename's `f05` prefix and
exclusive authentication under that secret make deliberate selection
plausible, but it remains **bounded**, not a provenance fact.

## Reproduction

- Fixture: `tests/fixtures/payloads/candidate_f05_dataflash_payload.bin`
- Generator: `tools/generate_candidate_f05_semantics.py`
- Machine-readable record: `data/generated/candidate_f05_payload.json`
- Deterministic verifier: `tests/verify_candidate_f05_payload.py`
- Ghidra raw-payload seeder: `ghidra/scripts/investigate/SeedRawPayload.java`

## Historical provenance boundary

The pinned Vance Git history now gives an exact **earliest public artifact**
boundary. `payload_candidate_f05_dataflash_ff200000_ff208000.bin` first appears
inside `scripts/secoc/20260531_othersienna_secoc_bundle.zip` at commit
`97ba3d1d9e77a6e047887da04767538fe81fc674`, authored by `Vance425` at
**2026-05-31 20:26:27 +0800**. The archive manifest records the same ciphertext
SHA-256 already pinned here:
`296d87d2e89b9c7e800122e4c7f6d3b9c876362e52586530cdd53c86ba1116f5`.
V2 and V3 were uploaded later that evening and retain byte-identical candidate
ciphertext.

The archive's internal file timestamp for the candidate is 2026-05-11, but a
ZIP member timestamp is not source-control provenance and is not used to assign
author/build date. The contemporaneous README describes it only as a retained
candidate that is not the default payload. The bundled uploader selects the
opaque file and contains `SEED_KEY_SECRET`; it does not contain candidate
shellcode source or a compiler invocation.

A Vance helper committed May 28,
`patch_secoc_payload_dump_range.py`, can decrypt an old payload, replace exactly
two dump-range constants, repair CRC/CMAC, and re-encrypt it. That mechanism
cannot explain candidate-f05's hundreds of changed pre-trailer bytes or its
new post-dump reset call, so it is not the candidate's build recipe.

The closest later public source family is Bk2ol's full DataFlash shellcode plus
`v850-elf-gcc`/`objcopy` build script and `build_payload.py`. In the pinned
history those sources first appear at
`db453752beeb7cdd024a1a9c38c6711c981e75ad` on **2026-07-11**, after the Vance
artifact was already public. They corroborate the implementation family and
explain why a recompiled DataFlash loop with `0x157E` reset is plausible, but
they cannot establish candidate-f05's original author, source commit, compiler
version/flags, or exact build invocation.

**Stage-7 provenance conclusion:** retained public history can establish the
first public binary/hash and later source-family corroboration. It **cannot establish**
the original candidate-f05 author/build environment or why `SEED_KEY_SECRET`
was deliberately used as the payload-build secret. That is now a bounded
provenance negative rather than an open static-analysis task.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [SECOC-031](../../reference/index.md#finding-secoc-031)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->
