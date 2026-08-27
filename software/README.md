# External software corpora

This directory defines the local layout for proprietary/vendor inputs used by
reverse engineering. The source distributions themselves are **never tracked**
and must not be redistributed from this repository.

Canonical local layout:

```text
software/
├── Techstream/
│   ├── v18/                 # ignored Toyota Techstream V18 distribution
│   ├── gtsplus/             # ignored Toyota GTS+ distribution/reconstructed local PEs
│   └── cuw/                 # ignored Toyota calibration-update package corpus
├── Renesas/                 # ignored Renesas Flash Programmer distribution
└── locks/                   # tracked hashes/provenance for analyzed source artifacts
```

The boundary is provenance-based:

- `software/Techstream/**` and `software/Renesas/**` contain source/vendor bytes
  and are ignored by Git.
- `software/locks/` contains tracked identity/provenance manifests for those
  inputs.
- `tools/`, `tests/`, `docs/`, and `data/generated/` contain our parsers,
  decompilation-derived evidence, semantic reconstructions, generated tables,
  and deterministic verification. Those are first-class repository content.
- `REFERENCE/` remains informal context/handoff material. Proprietary software
  corpora that participate in canonical verification belong under this `software/`
  layout instead of being consumed from `REFERENCE/`.

The verification runner owns external corpus availability through
`verification.toml`. Portable/core verification consumes tracked derived evidence
only; local/required-external verification rechecks it against the ignored source
bytes when those corpora are present.
