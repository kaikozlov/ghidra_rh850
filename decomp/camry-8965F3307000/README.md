# Camry `8965F3307000` decompilation

The image links from `symbols.jsonl` plus the original CodeFlash bytes.
`matched.jsonl` records each function as `equivalent` when its retained
oracles pass, `converted` when the C compiles and those oracles have not
passed, or `unconvertible` when it does not compile yet.

```bash
tools/decomp identity
tools/decomp status
tools/test camry_decomp
```

`symbols.jsonl` is the name and address map. `data.jsonl` is the named data
map. `oracles.jsonl` is the retained machine scenarios of the original bytes,
one JSON object per line, with the old per-scenario essays removed.

`tools/decomp corpus` rewrites every decompiler body into `src/all/` and
prints the largest compile-failure classes. `src/corpus.c` is the
oracle-checked slice. A function is `equivalent` only after its retained
oracles pass.
Hand-written C is listed the same way: add the function, its address, and
check the oracles whose memory and return values are that function's contract. Peripheral-rejection scenarios stay in `oracles.jsonl`
as original-byte evidence; they are not a substitute for the C. Do not add
a coverage ledger, a review spreadsheet, or a narrative section either.
