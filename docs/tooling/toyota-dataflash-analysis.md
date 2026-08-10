# Toyota EPS DataFlash structural and key-domain analyzer

> **Tool:** `tools/analyze_toyota_dataflash.py`
>
> **Reference geometry:** `8965B4512000` 32 KiB DataFlash +
> `data/dataflash_nvm_records.csv`
>
> **Reference output:**
> `data/generated/dataflash_structural_analysis_4512000.json`
>
> **Verification:** `tests/verify_toyota_dataflash_analyzer.py`

This analyzer is the offline end point for a future Corolla/Sienna/Yaris EPS
DataFlash artifact. It deliberately separates **storage-structure evidence**
from **cryptographic key evidence** so a high-entropy 16-byte field is never
called a key merely because of its appearance or address.

## 1. Every 16-byte window is considered

For an N-byte dump there are `N - 15` sliding 16-byte windows. The analyzer
computes all of them, deduplicates equal values for ranking/scanning, computes
Shannon entropy, and emits a configurable entropy-ranked list containing only:

- file offset;
- virtual address;
- entropy;
- SHA-256.

Raw candidate key bytes are not written to the report.

For the committed 32 KiB `4512000` dump this means all **32,753** possible
sliding windows are covered, not merely 16-byte-aligned fields.

## 2. Physical NvM validity model

The analyzer consumes the independently generated physical record map in
`data/dataflash_nvm_records.csv`. For every configured record it evaluates only
the two validity properties already proved by firmware/layout analysis:

```text
first u16 == configured storage index
final u32 == 0xAAAAAAAA
```

A record satisfying both is reported as `observable_valid`.

The second 16-bit physical header word is retained in output as
`opaque_header_word1`. **It is not called a checksum or CRC.** The current
firmware analysis has not established that semantic identity. This distinction
is important for cross-variant work: the tool detects the known physical
commit/validity structure without inventing an integrity algorithm that has not
been recovered.

## 3. Raw / XOR55 / XORAA redundant-object reconstruction

For every enabled triplicate object in the `4512000` reference layout, the tool
finds its three configured physical copies and decodes their payloads as:

```text
raw    -> payload
xor55  -> payload XOR 0x55
xoraa  -> payload XOR 0xAA
```

It reports:

- physical validity per copy;
- decoded-payload SHA-256 and entropy;
- number of valid copies;
- whether all decoded copies agree;
- majority decoded consensus count;
- valid-copy consensus count;
- consensus hash when at least two decoded copies agree.

The committed reference result reproduces the existing firmware conclusions:

| object(s) | result in `4512000` dump |
|---|---|
| `0,1,2,3,5,6` | all three copies physically valid and decode to one consensus payload |
| `4` | no valid copy |
| `12,13,14,15` | no valid copy |

Synthetic verification rewrites object 15 into three correctly encoded,
physically committed records and proves that the analyzer recovers one decoded
32-byte consensus across raw/XOR55/XORAA.

## 4. Object-15 geometry and related-variant comparison

The known 32-byte object-15 layout is made explicit:

| copy | record | decoded second-field address |
|---|---|---|
| raw | `0xFF206E00` | **`0xFF206E14`** |
| XOR55 | `0xFF206D00` | `0xFF206D14` |
| XORAA | `0xFF206C00` | `0xFF206C14` |
| restored RAM | — | `0xFEBF02F8` |

The raw location exactly aligns with the externally CMAC-validated
`8965B4514000` field at `0xFF206E14` (reported SHA-256 prefix
`1d1c53a6d634016a`). The analyzer records that **geometry alignment** while
keeping `runtime_key_equivalence = unproven`.

For the committed `4512000` image it reproduces the expected negative:
object 15 has zero physically valid copies, its three decoded payloads do not
agree, and its raw second field is low entropy. This is structural evidence,
not a runtime statement about protected ICU-S slot 4.

A future Corolla dump can therefore be compared immediately:

1. Does the same object-15 geometry contain physically committed records?
2. Do raw/XOR55/XORAA decode to one 32-byte consensus?
3. Is the second field shared across all decoded copies?
4. Does that field have any cryptographic relation to captured SecOC traffic?

If the layout differs, lack of `4512000`-style consensus is reported as such;
the reference geometry is not silently promoted to a universal Toyota layout.

## 5. Cryptographic key-domain scan

With `--capture --domain-scan`, the analyzer uses the generic classic Toyota
SecOC oracle to test **every unique sliding high-entropy 16-byte window** against
independent traffic domains.

The scan does not require a candidate to authenticate synchronization before it
is considered. Each candidate is first tested against:

- one synchronization sample, if present; and
- one sample from each observed protected CAN ID.

Only candidates that pass at least one cryptographic probe receive full capture
verification. This keeps the all-window scan tractable while allowing discovery
of keys that belong to protected traffic but not `0x00F` synchronization.

Full verification classifies a candidate as one of:

```text
sync only
0x116 only
0x24D only
common 0x116+0x24D
common protected <ID>+<ID>...
common sync+protected
no cryptographic evidence
```

The exact passing protected IDs are always emitted separately, so
`common sync+protected` does not hide whether the same candidate authenticated
`0x116`, `0x24D`, steering traffic, or some other classic domain.

Synthetic fixtures prove all of the requested discriminator cases:

- a key authenticating only `0x00F`;
- an independent `0x116` key;
- an independent `0x24D` key;
- one key shared by `0x116` and `0x24D` but not synchronization;
- one key shared by synchronization plus both protected IDs.

## 6. Corolla workflow

The public 2023-US-Corolla route already supplies a usable classic oracle:
`0x00F`, `0x116`, and `0x24D` on bus 1. Once the reported 32 KiB DataFlash dump
is available, the intended offline sequence is:

```bash
# Export/ingest public CAN into the session/oracle NDJSON first.
uv run --locked python tools/analyze_toyota_dataflash.py \
  corolla_dataflash.bin \
  --capture corolla_oracle.ndjson \
  --domain-scan \
  --output corolla_dataflash_analysis.json
```

The result answers, independently:

- whether `4512000`-style NvM/object-15 redundancy is present;
- whether any physically valid object-15 consensus exists;
- whether the structural second field is cryptographically useful;
- whether some other sliding 16-byte field authenticates synchronization;
- whether the same/different field authenticates `0x116` and `0x24D`;
- whether no CPU-visible candidate has cryptographic evidence at all.

That last outcome is meaningful: after a complete sliding-window domain scan,
failure to validate a DataFlash candidate is evidence against a plaintext
CPU-visible 16-byte key in the captured dump, while still not proving where a
protected/HSM key resides.
