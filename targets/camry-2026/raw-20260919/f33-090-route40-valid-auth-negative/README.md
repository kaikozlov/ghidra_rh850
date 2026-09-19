# F33 authenticated `0x090` route-40 negative

This directory preserves the 2026-09-19 stationary in-car result from the
one-boot exact-F33 route-40 experiment introduced by analysis commit
`7aabfeba`.

The comma was rebooted after the run, so the original
`/tmp/f33-090-route40-result.json` no longer existed. The operator pasted the
complete terminal output into the repository immediately afterward.

- `terminal-transcript.txt` is that pasted terminal transcript, retained
  byte-for-byte. SHA-256:
  `e6594005012f9696b4c3795bf32f6b6eab426ab9d64ce74ecd11a7b198f60e27`.
- `result.json` is the JSON object extracted from the transcript by removing
  only the leading command/panda-info lines and trailing shell prompt.
  SHA-256:
  `e316223cd38a65467a2053be7958e6047a4a295a8034110f0d57dadf009b0449`.

The machine outcome is
`valid_authenticated_090_not_latched_while_native_route40_remained_live`.
Command 5 succeeded for DataID `0x0090`, selector 4; the host sent reset 3259
message 2 about 2.476 ms after the corresponding native message 1 and received
a Panda TX echo. The first subsequent native `0x090` arrived about 7.146 ms
after host submission. Route-40 generation advanced by 182 modulo 256,
`invalid_checksum` remained zero, and the exact host trailer was not latched at
F33 raw COM `FEBE4BAF`.

This is dynamic evidence that valid P5/SecOC and the exact-F33 B7 checksum were
not sufficient for the tested host frame to reach F33 route 40. It does not by
itself distinguish ingress/source/port filtering from an additional upstream
application-semantic check on the deliberately unique payload.
