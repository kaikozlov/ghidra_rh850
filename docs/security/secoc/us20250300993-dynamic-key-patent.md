# US20250300993A1 / US12615265B2 — dynamic SecOC-key patent deep dive

> **Source:** Toyota Motor Corp., *System and method for providing secured CAN communications*
>
> **Application:** US18/613,700
>
> **Priority / filing:** 2024-03-22
>
> **A1 publication:** US20250300993A1, 2025-09-25
>
> **Grant:** US12615265B2, 2026-04-28
>
> **Evidence source:** external-source patent analysis joined to existing target-native SecOC RE
>
> **Scope warning:** this is a post-TSS3 filing. It is useful for Toyota terminology and future-architecture reasoning, not evidence that the 2026 Camry F33 implements the claimed scheme.

Public sources:

- https://patents.google.com/patent/US20250300993A1/en
- https://patents.google.com/patent/US12615265B2/en

Local source copies are intentionally kept untracked under `REFERENCE/patents/`.

## 1. The important distinction: related art vs invention

The patent describes ordinary AUTOSAR SecOC as **related art**:

- sender and receiver possess a static shared secret;
- sender computes a MAC and appends it to the secured PDU;
- receiver recomputes the MAC and rejects/discards the PDU on failure;
- an HSM may protect the key, but the description argues that systems containing
  ECUs without HSM protection can still expose the shared secret;
- compromise of that static shared secret has a broad blast radius because the
  attacker can create authenticated-looking CAN traffic for every ECU that
  trusts the same key.

That related-art discussion is useful vocabulary, but it is not an admission
that every Toyota production platform uses one vehicle-global static key.

The proposed invention changes **the operational MAC key**, not the existence
of persistent roots of trust.

The illustrated pipeline is:

```
persistent master seed
        + timestamp at/near IG-ON
        + vehicle geographical location
                 |
                 v
          passcode generator
                 |
                OTP
                 |
persistent master key
                 |
                 v
                KDF
                 |
       per-start shared key
                 |
        + freshness/counter
                 |
                 v
                MAC
                 |
      secured CAN PDU
```

Sender and receiver independently reproduce the same OTP/shared key rather than
transporting the derived operational key between them.

## 2. What is actually persistent

The repeated phrase that the derived shared key "does not exist" at IG-OFF is
best read as **not materialized/stored as the operational session key**.

The design still requires persistent secret material:

1. a **master key** pre-provisioned to sender and receiver;
2. in the principal timestamp/location embodiment, a **master seed** likewise
   pre-provisioned to the participants.

The patent explicitly allows the ECU nonvolatile storage component to hold
master seeds and master keys, and separately allows the passcode generator and
KDF to be implemented in hardware, firmware, software executed by an ordinary
processing unit, or combinations thereof.

Therefore the proposal does **not** remove long-lived secrets from the vehicle.
It replaces a long-lived **traffic-authentication key** with long-lived
**derivation roots** plus an ephemeral traffic-authentication key.

## 3. Application claims vs granted claims

This matters because the A1 application is much broader than the claim set that
actually issued in 2026.

### A1 independent claim 1

The published application originally claimed, at a high level:

```
generate OTP
obtain pre-provisioned master key
derive shared key from OTP + master key
generate MAC from derived key
append MAC
send via CAN
```

Timestamp, geographical location, per-ignition rotation, counters, and
truncation were dependent-claim limitations.

### B2 granted independent claim 1

The issued claim was narrowed so that independent claim 1 itself requires:

- OTP based on at least **timestamp + geographical location**;
- pre-provisioned master key;
- derived shared key;
- a **counter value**;
- MAC generated from derived shared key + counter;
- CAN transmission.

The issued system claim 11 is narrowed in the same way.

That distinction is useful technically even without making a legal conclusion:
the generic idea "derive a temporary key from an OTP and a root" is not the
final independent-claim shape. The surviving independent claims center the
time/location-derived context and freshness counter.

## 4. The OTP is really deterministic session context

In the principal embodiment, "OTP" is not a challenge-response OTP delivered by
one participant to another.

Each participant independently obtains:

- timestamp;
- geographical location;
- master seed;

then hashes/signs/otherwise combines them to reproduce an OTP. The shared key is
then derived from OTP + master key.

For a sender and receiver to verify one another, their derivation inputs must
produce the same result.

The patent addresses timestamp skew by allowing timestamp truncation or
rounding to a tolerance, but gives much less detail about how geographical
location is made identical across heterogeneous ECUs. It allows GPS, INS,
cellular/Wi-Fi positioning, and external timestamp sources.

Practical consequence: timestamp/location are best understood as **session
diversification context**, not secret entropy. In a production vehicle they are
likely observable or distributable state. Cryptographic secrecy still rests in
the persistent master material.

The description also allows multiple master seeds and/or master keys. Therefore
the patent does not require one vehicle-global root or one vehicle-global
derived key; separate security domains remain compatible with the disclosure.

## 5. What security property this can genuinely improve

The clearest improved threat model is **operational/session-key disclosure**.

Suppose an attacker obtains only the currently derived traffic key but does not
obtain the master key/seed:

- that session key can authenticate traffic during the current derived-key
  epoch;
- after the next IG-OFF -> IG-ON transition, a new operational key can be
  derived;
- an old captured session key no longer authenticates the new epoch;
- a key recovered from volatile runtime state is less useful for offline reuse.

This is a real improvement over a static traffic key.

It can also make at-rest acquisition of the *operational* key less useful:
there need not be a persistent copy of that particular session key.

## 6. What it does not solve

### 6.1 Root compromise

If an attacker recovers the master key and whatever master-seed material is
required, time/location rotation does not save the system. The attacker can
derive future session keys from future session context.

The blast radius then depends on key-domain design:

- pairwise/domain-specific roots limit scope;
- a root shared across many participants preserves a correspondingly large
  compromise domain.

The patent permits both styles and does not prove which Toyota uses.

### 6.2 Full ECU compromise or a signing oracle

If arbitrary code can invoke the protected MAC primitive under the active key,
the attacker does not need plaintext key recovery.

Per-ignition rotation therefore does little against a live **signing oracle**
during that ignition epoch. This is directly relevant to the RH850 work:
command-5-style hardware-backed signing can remain useful even if the active
operational key changes at every power cycle, provided the oracle targets the
current key slot and freshness is tracked correctly.

Likewise, compromise of the derivation root or of a privileged KDF/key-loading
path is qualitatively more powerful than disclosure of one session key.

### 6.3 The "ECUs without HSMs" problem is not automatically fixed

The patent's background motivates the invention partly by saying that a static
SecOC key can be exposed when some participants lack HSM protection.

But the new design still requires the same participants to retain a master key,
and the main embodiment additionally retains a master seed. The specification
expressly allows these values and the derivation machinery to live in ordinary
ECU storage/firmware/software.

Therefore the proposal only fixes the no-HSM problem if the implementation
actually gives the **root material** stronger protection than the old static
traffic key. Session rotation by itself does not do that.

## 7. Freshness is generic, not the exact Toyota TSS3 mechanism

The patent's freshness description is intentionally generic:

- optional monotonic counter;
- sender increments over time;
- sender/receiver counters "may be synchronized" at startup or communication
  initialization;
- counter may be called a freshness value;
- receiver accepts a counter greater than the previously received value;
- counter and MAC may be truncated to fit the CAN payload.

That is recognizably SecOC-shaped, but it is not the concrete Toyota classic/F33
freshness contract recovered in this repository.

The existing Toyota profile has materially richer state:

- trip counter;
- reset counter;
- independent per-PDU message counter;
- explicit synchronization PDU `0x00F`;
- truncated transmitted freshness;
- 28-bit transmitted CMAC;
- receiver reconstruction/window logic.

The patent contains no `0x00F`, no Toyota DataID construction, no
trip/reset/message geometry, and no AES-CMAC requirement.

Thus the patent is useful confirmation that Toyota thinks in the expected
"freshness + truncated MAC + synchronization" terms, but it should not be used
to rename or simplify the already recovered TSS3 freshness implementation.

## 8. Exact F33 comparison

| Property | Patent embodiment | Exact/recovered F33/TSS3 evidence | Assessment |
|---|---|---|---|
| Operational key | Derived dynamically per ignition | SecOC verification uses ICU-S selector/slot 4 | Different known interface shape |
| Persistent root | Master key; optionally master seed | Toyota ECU Security Key workflow uses authenticated SHE M1--M5 provisioning into protected key state | Both have persistent roots, but no proven identity |
| Per-start KDF | Central feature | No recovered F33 application-side timestamp/location KDF feeding SecOC slot 4 | **Not supported** |
| RAM-only traffic key | Natural implementation possibility | Exact F33 SecOC config selects slot 4; separate command-9/10 work treats RAM_KEY as a distinct volatile facility | **Patent-style RAM session key is not the current leading F33 model** |
| Freshness | Optional monotonic counter, generic startup sync | `0x00F` + trip/reset/message counters + per-PDU receiver state | Conceptually related, physically different |
| MAC | Generic keyed MAC | AES-CMAC-128 with truncated transmitted authenticator in recovered Toyota profiles | Compatible abstraction, not patent-specific |
| Counter/MAC truncation | Explicit | Exact Toyota profiles transmit truncated freshness/authenticator | Strong conceptual match |
| Key distribution | Derived independently; no session-key transport required | Current Toyota service flow provisions protected key material using standard SHE M1--M5 | Different lifecycle plane |
| Receiver failure | Reject/discard on bad MAC or stale counter | Exact receivers fail closed before normal COM/freshness commit | Strong conceptual match |

The strongest negative point is the missing F33 derivation path: exact firmware
contains the slot-4 verification machinery and the Toyota freshness receiver,
but no recovered application-side mechanism corresponding to
`timestamp + location + master seed -> OTP -> KDF -> new SecOC key every IG-ON`.

That is consistent with the patent's 2024 priority date: it should be treated as
a prospective/later architecture family unless a newer Toyota ECU independently
shows the derivation machinery.

## 9. Relationship to Toyota ECU Security Key / SHE M1--M5

The current Toyota service path and the patent solve different lifecycle
problems.

The recovered Toyota **ECU Security Key** flow carries the standard SHE
M1/M2/M3 authenticated memory-update object and receives M4/M5 proof. That lets
Toyota provision or replace protected persistent key state without exposing the
new key to the ordinary application CPU.

US20250300993A1 does **not** describe sending a per-ignition session key in such
an envelope. Its literal design has each participant derive the operational key
locally.

Therefore:

- this patent is not evidence that Toyota sends a fresh SecOC key to every ECU
  through M1--M5 on every boot;
- capturing an M1--M3 update envelope is not part of the patent's session-key
  mechanism;
- a future Toyota design could still use SHE provisioning to establish the
  persistent master roots, then derive ephemeral operational keys locally;
- the patent does not specify which SHE/HSM key slot would hold either root or
  derived key.

A volatile `RAM_KEY` is an intuitive implementation for "does not exist at
IG-OFF", but that is **our implementation inference**, not patent text.

## 10. The literal HSM implementation problem

If a platform uses an HSM and wants to preserve the patent's security benefit,
the ideal implementation is roughly:

```
persistent root stays non-exportable in HSM
             |
             +-- HSM/internal KDF(session context)
                         |
                         v
              volatile MAC key slot
                         |
                    SecOC CMAC
```

That prevents the ordinary application CPU from ever seeing either plaintext
root or plaintext derived key.

The patent does not require such an architecture. It explicitly permits
processor-executed software/firmware derivation and nonvolatile storage of the
master material.

On a standard SHE-like implementation without an internal key-to-key KDF, a
designer may have to materialize a derived key somewhere before loading a
volatile key slot. That can reduce the intended benefit by creating a
CPU-visible transient. A vendor-specific HSM KDF/key-derive primitive would
avoid that, but the patent does not disclose one.

This is why the patent cannot be used to infer new programmable HSM firmware,
an ICU-S KDF opcode, or a RAM_KEY boot-load path.

## 11. Reliability / synchronization holes in the disclosure

The patent is a broad architecture patent, not a production protocol
specification. Several details are intentionally or accidentally loose.

### 11.1 Same OTP without a key-confirmation protocol

Sender and receiver independently generate an OTP, but no explicit
key-confirmation handshake is specified. If their timestamp/location inputs
land in different tolerance buckets, authentication simply fails.

For a safety-critical in-vehicle network, a production design therefore needs
some unclaimed mechanism for:

- choosing a canonical ignition timestamp;
- choosing/canonicalizing vehicle location;
- distributing or measuring those inputs consistently;
- recovering from key-derivation disagreement;
- confirming the active epoch.

### 11.2 Counter synchronization is hand-waved

The specification says counters may be synchronized at startup, but does not
define the synchronization protocol. Exact Toyota TSS3 solves this class of
problem with an explicit authenticated synchronization stream and receiver
windows; the patent does not.

### 11.3 Description-level inconsistency around truncation

The sender path says the sender:

1. computes MAC from derived key + counter;
2. truncates **MAC + counter** for transmission.

Later receiver prose gives an example in which the receiver truncates the
**counter + derived shared key** before generating its MAC.

Those are not the same construction. The granted claims retain the sensible
sender formulation (MAC from derived key + counter, then truncated counter/MAC)
and do not claim that receiver-side "truncate the derived key" sentence.

Treat that receiver sentence as drafting noise, not an implementation rule.

### 11.4 "Within a level of similarity" for MAC verification

The detailed method text also momentarily says a received MAC can be the same
"or within a certain level of similarity." Cryptographic MAC verification is
normally exact (or exact over the transmitted truncated bits). The issued
claims use exact same/different language.

Again, the claims are a better guide to the intended security construction than
every sentence in the generic implementation boilerplate.

## 12. What this means for current Toyota RE

### For TSS3/F33

Do **not** spend time looking for timestamp/location OTP derivation merely
because of this patent. The priority date and the known slot/freshness
architecture make that a low-priority hypothesis for F33.

Continue treating exact target-native evidence as authoritative:

- slot-4 SecOC verification;
- command-5/7/8 HSM/SHE behavior;
- Toyota M1--M5 provisioning;
- Toyota `0x00F` freshness synchronization;
- protected per-PDU receive/transmit geometry.

### For newer Toyota generations

This patent gives excellent search signatures.

In newer ECU firmware, search for combinations of:

- IG-OFF / IG-ON transition handling;
- RTC / timestamp acquisition and seconds-level rounding;
- GPS/INS/location acquisition near security initialization;
- SHA-256 / SHA-512 / KDF calls at startup;
- persistent master-seed/master-key records;
- a derived 16-byte or 32-byte volatile key written into a crypto/HSM key slot;
- key-slot mutation immediately after ignition transition;
- a freshness epoch reset coupled to that mutation;
- failure/recovery behavior when peer MACs all fail immediately after startup.

The distinctive signature is not "there is SecOC." It is **security-key
material changing at ignition in dataflow proximity to time/location context**.

## 13. Bottom line

This patent is useful, but mostly because it defines a plausible **post-TSS3
key-lifecycle direction**, not because it explains the F33 implementation.

The security improvement is specific:

> compromise of one *derived operational key* need not survive the next
> ignition epoch.

It is **not**:

> there is no static secret left to steal.

The architecture still stands on persistent roots. If those roots are shared
widely or are software-readable in a weak ECU, compromise of them defeats the
rotation scheme. If they remain hardware-bound and only an ephemeral derived
key is exposed, the design can meaningfully reduce offline key-reuse risk.

For our present attack surface, hardware signing oracles and root/HSM compromise
remain the more powerful primitives. A per-ignition derived key does not remove
the utility of a live signer; it mainly changes the value of plaintext key
extraction and offline replay.
