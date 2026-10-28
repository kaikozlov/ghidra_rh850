"""Exploit-interest ranking pipeline.

Host-side, deterministic, generated-evidence-only ranking of every recovered
function by *exploit* interest — how close an external ingress path is, how
much attacker-controlled selection/arithmetic reaches the body, and whether the
body writes through computed pointers into RAM/MMIO/flash/callback state.

This package is deliberately distinct from the semantic-interest ranking
(`tools/project/generate_semantic_interest_ranking.py`), which scores *semantic review*
interest (unknown functions worth human decompilation). This pipeline scores
*exploit* interest on functions that already exist in the canonical corpus.

Every input is a tracked generated or curated artifact derived from firmware bytes.
"""
