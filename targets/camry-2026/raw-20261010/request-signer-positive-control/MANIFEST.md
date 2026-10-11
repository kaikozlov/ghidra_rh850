# 2026-10-10 Camry request-signer positive control

Exact retained JSON from the maintainer 2026 Camry after two successful fresh bringups using the current ELM327 request-signer host path.

- `ui/`: `/data/tss3-oracle-runs/20261011T015518-4394-5365370735398` from the comma-four UI bringup.
- `ssh/`: `/tmp/tss3-request-signer-ui-bringup-20261011T015651` from the immediately following SSH bringup after vehicle-off wait.
- Both runs use authenticated payload SHA-256 `c1cfd265611feb8e47438f81a3f4c508afea52a2be98c55ccf8d2346d7398a5d`.
- Both report live Panda `DEV-92eb5651-DEBUG`, installed/local firmware signature prefix `b3d9a0324cddaa9e`, ELM327 mode 3 param 1 attested, four accepted and zero rejected `0x777` TX receipts, first-attempt `0x7A9/C9` signer response, fresh self-test response, and healthy control domains.
- Both successful runs also report RAM-exec `telemetry_frames=0` and `timed_out=true`; those fields are therefore not signer-probe failure evidence.

## SHA-256

```text
29f1939af737084b027ff6f45b493962c9ad8d7669f4d369918403f672642f1f  ssh/control-domain-state.json
8fddea8d9a1425153c843a5ba78cb9554151db980ffa9fe8f1368b3389ae96b7  ssh/request-signer-install.json
116a030ff54459fb008ab9fd2974fe273c7fe4c165570a0998f044a8f123e231  ssh/request-signer-self-test.json
30b2dad70f4d0cc8c8c23bb56ed881489e114e87fa219f915de22a9df9e33da5  ssh/startup-programming.json
ed288c007431cebf31790823ecb510f2d42133fb82b9cc69234e649f941d1953  ssh/summary.json
29f1939af737084b027ff6f45b493962c9ad8d7669f4d369918403f672642f1f  ui/control-domain-state.json
b9bacee02b8c209cf7a34d0edfbb4536508f0b19777b6180360d48cad6e8b5b3  ui/request-signer-install.json
3d123e5380b3136bbdcdb6a0ea0b00686e516bf7402152bb610588ebe088769b  ui/request-signer-self-test.json
93b7f205afb08c80e9afaea8cec8aad0a8b06e5a2d4795fa905de0853bba6300  ui/startup-programming.json
e56634edc13c9db232827c150b80283631fbf3362a8d75705e243a28867b3aa6  ui/summary.json
```
