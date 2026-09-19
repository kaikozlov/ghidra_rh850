# Exact-F33 valid-0x090 route-40 experiment

The ignition topology permits `OFF -> NRTD -> READY` and then `READY/NRTD ->
OFF`. It does **not** permit `READY -> NRTD`. This experiment therefore uses
one authenticated carrier for the entire ignition cycle.

During NRTD installation, the payload places an ABI-preserving resident in the
proven high tail and a bounded helper in executable GlobalRAM. After the single
NRTD-to-READY transition, the helper:

1. captures a native `0x090` application and current `0x00F` freshness;
2. flips only B6, outside F33's recovered `0x090` signal extraction, and
   recomputes the exact-F33 B7 checksum;
3. signs DataID `0x0090` and a future message-2 freshness with stock command 5,
   selector 4;
4. arms a continuous exact-trailer observer for raw route40
   `FEBE4BAF..FEBE4BCE`;
5. waits for native message 1 in the signed reset and transmits message 2 once;
6. reads the sticky full-frame latch.

The carrier never patches a route table, bypasses SecOC, writes flash, or
transmits CAN itself. The host is the sole `0x090` transmitter.

## Field sequence

```text
# Car OFF, then enter NRTD
./f33-route40 install

# Transition NRTD -> READY, remain in Park and stationary
./f33-route40 status
./f33-route40 run /tmp/f33-090-route40-result.json

# Transition READY -> OFF to remove the resident
```

There is no pre-READY message generation and no READY-to-NRTD transition.

## Interpretation

- `valid_authenticated_090_reached_f33_route40_raw_com`: the exact unique host
  frame was latched at the EPS route40 raw COM boundary.
- `route40_exact_frame_latched_but_native_collision_prevents_source_attribution`:
  a byte-identical native frame was also visible, so source attribution is
  ambiguous.
- `valid_authenticated_090_not_latched_while_native_route40_remained_live`: the
  exact host trailer was absent while native route40 generation advanced. This
  excludes invalid MAC28, freshness progression, and B7 as sufficient causes,
  but cannot exclude another unknown upstream semantic check on the B6 marker.
- `no_route40_match_and_native_route40_liveness_not_proven`: inconclusive.

## 2026-09-19 field result

The retained stationary run produced
`valid_authenticated_090_not_latched_while_native_route40_remained_live`.
Command 5 completed successfully for DataID `0x0090`, selector 4. The host
frame had the exact-F33 B7 checksum and reset 3259/message 2 freshness. It was
submitted about 2.476 ms after the corresponding native message 1; Toyota's
native message 2 appeared about 7.146 ms after host submission, so the host was
not late. Panda returned the transmitted frame, its error counters did not
grow, and F33 route-40 generation advanced by 182 modulo 256. The exact host
trailer was never latched at `FEBE4BAF`, and the route-40 bad-checksum counter
remained zero.

Raw evidence and provenance are retained under
`targets/camry-2026/raw-20260919/f33-090-route40-valid-auth-negative/`.

This dynamically disproves invalid P5/MAC28, stale freshness, and invalid B7 as
sufficient explanations for the tested direct-Panda rejection. It also removes
the proposed standard-ID-versus-extended-ID CAN-FD distinction: both the native
and host treatment were standard-ID `0x090` FD32 frames. The result does **not**
prove which external component rejected the frame. An ingress/source/port rule
is now the leading explanation, but an additional upstream semantic check on
the deliberately unique application byte, or another stale application field,
remains possible.

## Architectural consequence

The comma is not merely on the wrong side of its own relay. In the established
harness mapping, Panda bus 2 is the FRC side and bus 0 is already the
chassis-facing side. Sending this treatment on bus 2 would move it toward the
FRC; it would not bypass a downstream Brake/VMM/EBU boundary.

The joined evidence instead places the current tap at the request plane:

```text
FRC -- protected 0x08A request --> comma bus2/bus0 split
    --> Brake/VMM arbitration and request generation
    --> suspected admitted/local EBU attachment --> B6 / EPS receive PDUs
```

The logical `0x08A -> Brake/VMM -> B6` separation is supported independently by
Toyota's movement-manager architecture, GTS vocabulary, Brake-owned `0x081`,
and exact-F33 B6 source attribution. The exact physical bridge, local segment,
and ownership of `0x025`/`0x090` forwarding remain bounded.

This is therefore not evidence that Panda cannot transmit CAN-FD. It is
evidence that arbitrary EPS-targeted FD from the current FRC tap is not
equivalent to an admitted native producer path. The viable integration seams
are now:

1. remain at the camera tap, replace an authenticated FRC request such as
   `0x08A`, and let Brake/VMM produce the final B6 instruction;
2. attach downstream of the suspected Brake/VMM/EBU boundary and transmit a
   correctly authenticated B6 on the EPS-local segment;
3. recover the Brake/VMM firmware and its request-validation, routing,
   source-suppression, and signing contract; or
4. retain the already-demonstrated EPS-resident admitted-B6 rewrite strictly as
   a development mechanism, not a native production architecture.

The next lowest-cost localization is an exact-frame observer at F33's earliest
RSCFD/CanIf boundary for route 40. Absence there would place the loss before
successful EPS controller decode. The definitive physical follow-up is a
simultaneous passive capture on Panda bus 0 and the CAN pair at the EPS/EBU
attachment, followed by the same stationary authenticated `0x090` treatment on
that downstream pair. A route-40 latch only from the downstream attachment
would close the topology question.
