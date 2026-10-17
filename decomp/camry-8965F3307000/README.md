# Camry `8965F3307000` decompilation

The image links from `symbols.jsonl` plus the original CodeFlash bytes. C in
`src/` replaces a function only after it matches that function's retained
original-byte behavior. `matched.jsonl` lists those functions.
`status` is `equivalent` until a compiler reproduces the original bytes.

```bash
tools/decomp identity
tools/decomp status
tools/test camry_decomp
```

`symbols.jsonl` is the name and address map. `data.jsonl` is the named data
map. `oracles.jsonl` is the retained machine scenarios of the original bytes,
one JSON object per line, with the old per-scenario essays removed.

`tools/decomp corpus` compiles decompiler bodies into `src/corpus.c` and
appends a function to `matched.jsonl` only after its retained oracles pass.
Hand-written C is listed the same way: add the function, its address, and
check the oracles whose memory and return values are that function's contract. Peripheral-rejection scenarios stay in `oracles.jsonl`
as original-byte evidence; they are not a substitute for the C. Do not add
a coverage ledger, a review spreadsheet, or a narrative section either.
