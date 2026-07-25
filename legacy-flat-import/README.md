# Legacy incorrect flat-import investigation

These scripts were used against the invalid `rh850fw` project, which mapped the
entire combined `0x108000` file contiguously at virtual address `0x0`.

That file is actually `0x8000` bytes of DataFlash followed by `0x100000` bytes of
CodeFlash. The flat mapping shifted every CodeFlash virtual address by `+0x8000`
and produced false findings, including the claim that the two family secrets
were unreferenced.

Do **not** use these scripts against the corrected project. They are preserved
only to document the failed analysis path.
