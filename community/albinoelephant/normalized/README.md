# Normalized Corolla CodeFlash

`8965H1202000_CodeFlash.bin` is the canonical repository-local 1 MiB CodeFlash
view derived byte-for-byte from the first 1 MiB of the tracked 2 MiB owner-side
range dump in `../raw-20260818/albinoelephant-corolla-2023.20260814-0023/`.
The upper 1 MiB of that acquisition is all `0xFF` padding.

This normalized image is tracked so deterministic verification and generators
never depend on an ignored `build/` artifact.  The acquisition/normalization
suite independently reconstructs it from the raw dump and pins both hashes.
