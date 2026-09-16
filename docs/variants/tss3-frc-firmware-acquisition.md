# TSS3 front-recognition-camera firmware and arbitration acquisition

This report tracks the remaining camera-side question behind the current TSS3
control model: **what does the FRC itself compute, select, and hand to the
vehicle-movement arbitration layer?** It separates what is already recovered
from GTS+/CUWs from the still-encrypted camera application.

The exact maintainer-Camry diagnostic identity is `0x792 -> 0x79A`, F181
`8646F3315000`, DID0105 `8646C06091`. No exact `8646F3315000` application
image is currently decoded in this repository. The system-level placement is
documented separately in
[toyota-tss3-vehicle-movement-arbitration.md](../architecture/toyota-tss3-vehicle-movement-arbitration.md).

## 1. The FRC recorder already exposes the implementation stages

Current GTS+ category 498 (`FRC_P5`) binds the dedicated
`GetTSS3OperationFFDP5_DT.dll` recorder. The recovered PCS Data Viewer schema
shows that the camera's Operation FFD vocabulary is not one opaque steering
value. It exposes a sequence of normalized request, arbitration-result, and
control-state objects.

For lateral control the important records are:

| Recorder data ID | FRC recorder object | Exact current layout |
|---|---|---|
| `0x5631` | **LTA feature request** | lateral ID `u8`; requested pinion angle `s16 * 0.001`; steering-assist gain `u8 * 0.01`; damping gain `u8 * 0.01` |
| `0x5531` | **LDA feature request** | identical geometry/scaling to `0x5631` |
| `0x5282` | **generic TSS lateral request** | identical geometry/scaling to `0x5631`/`0x5531` |
| `0x5285` | **arbitration-result lateral ID** | `u8` |
| `0x57DE` | **arbitration-result pinion angle** | `s16 * 0.001` |
| `0x5265` | controller-under-control state | includes **Active steering under-control flag** beside ABS/VSC/TRC/VDM/MCB/TSC state |
| `0x560D` | LTA/driver/EPS state | driver-steering detection/prohibition/state, **EPS pinion angle `s16 * 0.001`**, following/stop flags |

The longitudinal side has the same explicit layering: `0x5280` and `0x5281`
are lower/upper TSS request packages, `0x5284` is the arbitration-result
longitudinal ID, and `0x57DB` is arbitration-result acceleration. This is the
camera-recorder representation of the request/arbitration/result architecture;
it is substantially stronger evidence than inferring a pipeline from CAN field
correlation alone.

The recorder also keeps feature-local inputs. In particular, LTA `0x5631`, LDA
`0x5531`, and generic TSS request `0x5282` have **the same five-byte normalized
shape**. That is exactly the shape expected from a software request-normalization
stage: application-specific producers feed one common lateral request object,
after which separate arbitration-result objects are recorded. This is a
structural implementation result. It does **not** yet prove the runtime copy
direction between those objects or that every arbitration instruction executes
inside the FRC rather than being reflected into its recorder from another
controller.

The current PCS viewer's `SYSTEM_TYPE` field must not be over-read here. Static
recovery proves it classifies RoB trigger families; the parameter decoder scans
the global DID table without consulting `SYSTEM_TYPE`. `LDA` on a trigger row
is therefore not an ECU-ownership tag for every recorded DID.

### Current implementation model

Joined to Toyota's vehicle-movement-manager architecture, the cleanest current
answer is that the **FRC implements the application side, not the final actuator
arbiter**. Feature logic such as LTA/LDA constructs feature-local request objects;
the camera normalizes those into the generic TSS request object (`5282`, with
longitudinal peers `5280/5281`) and hands that request toward the vehicle-movement
manager. The Brake/VMM domain performs the downstream package arbitration/request
generation, returns result/status (`5285/57DE`, longitudinal `5284/57DB`) to the
applications, and emits the steering-controller target on the protected B6 path.
The FRC records both sides because it consumes the result/status feedback for
supervision and application state.

The current wire crosswalk is consistent with that split: `0x08A` carries the
request-side lateral ID/pinion/gain tuple corresponding to `5282`, while `0x081`
carries the Brake/VMM-owned selected/result lateral ID and pinion quantity
corresponding to `5285/57DE`. Exact-F33 EPS receives neither of those as its
external steering command; it receives the downstream B6 target/instruction.
What remains unknown is the private/network transformation by which the FRC's
normalized request reaches the Brake/VMM request input.

## 2. Exact read-only camera oracle

The current native Operation-FFD protocol is recovered from the exact GTS+
binary, not transferred from an older Techstream release:

```text
AB 11                                      -> EB 11 + behavior IDs
AB 12 + behavior_id:be16                   -> EB 12 + behavior + record IDs
AB 13 + behavior_id:be16 + record_id:be16 -> EB 13 + behavior + record + data
```

`EB13` byte 6 is a block count. A zero count means the host derives the count by
scanning complete blocks. Blocks begin at byte 7 and are:

```text
data_id:be16 || length:u8 || data[length]
```

The current plugin uses the ordinary P5 communication stack and imports no
SecurityAccess helper. The normal current-P5 outer lifecycle supplies extended
session handling. This is separate from **Image FFD**, whose live
`27 03/27 04` level-49 unlock was already demonstrated on the exact Camry.

`tools/targets/camry/live/camry_frc_operation_ffd_capture.py` now implements a
strictly read-only acquisition of this interface. Before using the proprietary
service it requires F181 to contain `8646F3315000`, enters `10 03`, then uses
only `AB11/12/13` plus ISO-TP flow control. It captures all incoming Panda buses
0..2 on the same monotonic clock and restores `10 01` and silent Panda safety on
exit. It has no SecurityAccess, RoutineControl, WDBI, flash, Active-Test, or
vehicle-control path.

The default RoB set targets stored steering/driver events (`LCS Steer Override`,
`Steering Angle Speed Threshold Exceeded`, `LTA Hands Free Cancel`, LCA
reject/cancel, and the hands-off family). `--all-robs` remains read-only if a
complete recorder census is wanted.

The highest-value same-record joins are:

```text
0x5631  LTA-local request
   -> 0x5282  normalized TSS request
   -> 0x5285 + 0x57DE  arbitration result
   -> 0x5265  active-steering under-control grant/state
   -> 0x560D  measured EPS pinion / driver-control state
```

A retained capture containing that chain, synchronized with CAN, can answer the
remaining camera implementation question without first decrypting the firmware:
which stage changes first, which stage is copied or transformed, which request
stage emerges as `0x08A`, and which result stage emerges as `0x081` before the
final protected EPS command path.

## 3. What the FRC CUWs actually contain

The local true-TSS3 `0x0792` corpus contains six Corolla FRC packages
(`T-0058/0060/0061/0062-23`, `T-0149/0150-24`). They are
`P5-Unified`, RequiredSpecReproVer `04`, ReproMethod `07`, and share one FRC
family `ServiceAuthKey` and descriptor `Nonce`.

Their whole `.xx` member is Motorola S-record framing around an **encrypted**
target region:

```text
0x008F6C00..0x008F7170  1,392-byte package routine slot
0x08E80000..0x0E000000  85,458,944-byte target span
```

Modern ReproStd sends whole/routine bytes with UDS DFI `0x01` and delta data
with DFI `0x21`. By the UDS DFI layout and Toyota's own phase-6 method names,
the low nibble is manufacturer-specific **encryption method 1**; high-nibble
method 2 is Toyota `DeltaRepro`. GTS+ does not decrypt these bytes. It passes the
encoded member to the ECU, where `10F5/10F6` perform the still-unrecovered
programming-side transform/application.

The current host-side unlock is completely recovered:

```text
10 02 -> 50 02
27 01 -> 67 01 + seed[16]
27 02 + CalcSeedKey(ServiceAuthKey, seed)[16] -> 67 02
```

The selected ReproStd path imports `GetServiceAuthKey`, but not
`GetNonce/GetSeedKey/GetECUAuthKey/GetSecurityProperty2`, and its flash writer
has no package-decryption path. The descriptor Nonce is therefore **not sent as
an explicit host-to-ECU payload-decoder input**. Any package-specific decrypt
context must be embedded, derived, or otherwise already available ECU-side.

RequiredSpec04 integrity is also closed at the transport boundary: the CUW
`DigitalSignature` field is 512 ASCII-hex characters encoding **256 binary
bytes**, and the ReproStd RoutineControl request declares an `0x0100`-byte
integrity object. The signature algorithm, signed object, and ECU public-key
storage remain unknown.

## 4. Cipher shape: useful constraint, not a solved key

The five distinct stored FRC whole images share **exactly the first two 16-byte
blocks** and diverge at byte 32. Beyond those two blocks there are zero shared
16-byte blocks. Two closed update chains need only ~1.76% and ~1.47% compact
delta input, while the resulting stored whole images decorrelate to random
chance after that 32-byte prefix.

That rules against treating the stored body as plaintext localized edits. A
fixed-key/fixed-IV chaining mode such as CBC is a particularly good structural
fit: identical first two plaintext blocks produce identical first two
ciphertext blocks, then the first changed block propagates divergence through
the rest of the chain. P1M-E Toyota/Denso firmware independently uses AES-CBC
for its DFI-low-nibble-1 payload path, so AES-CBC is the strongest concrete
cross-family candidate. Neither fact proves that the TMPV770 FRC uses the same
cipher, key derivation, or IV.

The two closed FRC update chains let us test candidate image keys more directly
than inspecting decrypted entropy. Under the CBC hypothesis, blocks from index 2
onward do not require the IV for an old/new plaintext comparison. The tracked
corpus analyzer now tests **43,845 unique one-step key candidates** built from
112 stable FRC/package/known-root atoms through AES-ECB encrypt/decrypt,
AES-CMAC, XOR, and explicit 16-byte MD5/SHA-256 adapters. It scores both
`T-0062->T-0149` and `T-0061->T-0150`, then fully rescans the first 64 KiB
for the strongest sparse candidates. No candidate recovers even 1% common
plaintext across both chains; the best minimum result is ~0.434%, essentially
random 1/256 behavior.

That is a substantially stronger negative than trying `ServiceAuthKey`, its
unwrapped working key, descriptor Nonce, or the known EPS roots one at a time.
It still is not exhaustive cryptanalysis: a protected camera root, another
cipher/mode, or a more complex KDF can trivially sit outside the tested grammar.
The useful conclusion is narrower and operational: **the FRC image key is not
an obvious one-step derivation from the package-visible values and Toyota roots
we already possess.** More combinatorial guessing is lower-value than acquiring
the ECU-side decoder/boot code or a raw plaintext/runtime image.

## 5. Physical-firmware acquisition boundary

The retained TechInsights TSS3 camera teardown under
`REFERENCE/tss3_camera_report/` is a useful hardware-family reference, not an
exact-Camry identity join. It identifies a Toshiba `TMPV7706XBG` Visconti5
processor and an Infineon/Cypress `S25HS01GT` **1-Gbit / 128-MiB serial NOR**,
plus LPDDR4 and CAN transceivers.

That physical flash capacity matters independently of the exact address map:
the TSS3 FRC CUW target span is only 85,458,944 bytes (~81.5 MiB), so a package
of this shape cannot be a complete 128-MiB NOR image. There is enough flash
outside the CUW-updated body to hold boot/programming/security code. The exact
**Toyota TMPV7706** address-to-NOR-offset mapping is still unproved and must not
be promoted from package S-record addresses alone.

### 5.1 Public Visconti5 sibling firmware localizes the programming service to the R4/flash domains

A public Labforge Bottlenose firmware bundle supplies the missing platform-level
control without being mistaken for Toyota firmware. Release `v0.2.134`
(`firmware-bottlenose-v0.2.134.tar`, published 2024-03-12, SHA-256
`9945ee81bcc7d02618856b26945a12378e862ba3e1320211be2fbafc751065de`)
contains an unstripped Linux image plus a real-time image `cr4dl0.img` whose
52,776-byte payload SHA-256 is
`6cfe5eb572bce81b9f6641f6b90fcf47bcdfdea8439467e032c8b6aa48325af3`.
The same payload is present in public releases as early as `v0.1.91`, so this is
a stable board-support component rather than a one-release accident.

Despite the `tmpv7706-bn3` filename convention in that bundle, its root device
tree explicitly identifies **`toshiba,tmpv7708-bn3`, `toshiba,tmpv7708`**. It
is therefore **TMPV7708 sibling-platform evidence**, not an exact TMPV7706XBG
camera image. This distinction is mandatory. The value of the image is the
shared Visconti5 execution/interconnect model, not target identity.

The sibling firmware gives three unusually strong address-domain joins:

1. `cr4dl0.img` is a legacy U-Boot firmware image with **load address and entry
   point `0x00800000`**. Thus `0x00xxxxxx` is a concrete Cortex-R4 executable
   domain on this Visconti5 implementation. The Toyota FRC package's downloaded
   routine target **`0x008F6C00`** lies in that same address domain.
2. Its device tree exposes Toshiba **GCOMM at `0x24040000`** and two 1-MiB
   shared-memory FIFOs at A53 physical addresses `0x4_80000000` and
   `0x4_80100000`. The R4 image contains the corresponding 32-bit aliases
   `0x80000000` and `0x80100000`; its active flash service registers receive
   endpoint `0x0008`, reply endpoint `0x0800`, and a GCOMM interrupt/callback
   path inside the same `0x2404xxxx` controller block.
3. Linux does not drive this platform's serial flash directly. Its unstripped
   kernel exposes `tmpv7700-mbox-flash` over GCOMM. The exact R4 consumer is
   recovered: after the outer GCOMM length word, service word `1` dispatches
   operation `0=erase`, `1=write`, `2=read` with `address`, `length`, and optional
   data. The R4 read path subtracts its configured flash base (initialized to
   zero) and reads from **`0x08000000 + offset`**. Thus this sibling maps serial
   NOR through a concrete `0x08000000` XIP aperture.

That makes the Toyota CUW address geometry substantially less mysterious. Its
85,458,944-byte application target **`0x08E80000..0x0E000000`** sits naturally
inside the sibling platform's `0x08xxxxxx` serial-NOR/XIP domain, while its
1,392-byte programming routine sits in the sibling platform's `0x00xxxxxx`
Cortex-R4 execution domain. The strongest current implementation hypothesis is
therefore:

```text
Toyota ReproStd / programming service
        |
        | encrypted DFI=1 download
        v
TMPV770 Cortex-R4 execution domain       (routine target 0x008F6C00)
        |
        +--> serial-NOR/XIP domain       (Toyota target 0x08E80000..0x0E000000)
        |
        +--> protected TMPV770 security services / HSM_CM3   (exact ABI open)
```

The first two arrows are strongly supported by independent package and sibling
platform address evidence; the final R4-to-HSM edge is the remaining software
join. This still does **not** prove the exact Toyota TMPV7706 flash aperture,
R4 firmware layout, UDS task placement, or HSM command ABI. It does make an
A53/Linux-side payload decryptor a poor next target: the actual FRC package
loads a routine into the R4 address domain, and a closely related Visconti5
platform already uses R4/GCOMM services to mediate the serial NOR.

For the exact Camry, a raw `8646C06091` camera NOR dump or a matching
`8646F3315000` CUW/boot image is therefore the highest-value static acquisition.
It should be searched first for:

1. ReproStd `10F5/10F6` handlers and DFI encryption-method-1 dispatch;
2. the payload decrypt key/KDF/IV source;
3. RequiredSpec04 256-byte signature verification and public-key material;
4. the normalized `LTA/LDA -> TSS request -> arbitration result` copy/select
   graph exposed by recorder IDs `5631/5531 -> 5282 -> 5285/57DE`;
5. the downstream handoff that ultimately becomes the protected steering command
   accepted by EPS.

Until that image is decoded, the most direct FRC implementation oracle is the
read-only Operation-FFD capture above, because it exposes those exact internal
semantic stages from the live camera instead of searching encrypted bytes for
strings that cannot exist in plaintext form yet.
