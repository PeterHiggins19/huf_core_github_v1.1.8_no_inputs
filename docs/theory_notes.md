# Theory Notes (HUF / UBH)

**Updated:** 2026-02-17

This repo is deliberately **artifact-first**: you can run real datasets and inspect outputs without accepting any theory claims.

If you *do* want the formal structure (definitions, taxonomy, and expanded proofs), see:

- **`docs/The_Higgins_Unity_Framework.md`** (full theoretical handbook)
- **Handbook** (conceptual + case-study narrative)

---

## What HUF is (in one paragraph)

HUF is a reproducibility wrapper around a single contract: a **Unity‑Budgeted Hierarchy (UBH)**.  
A UBH is a hierarchy where each node’s outgoing weights form a *budgeted, normalized distribution* (a “unity” constraint).  
HUF turns inputs into UBH elements, then emits auditable artifacts (tables, maps, images) plus a stability sweep that shows what structure survives across τ.

---

## Why “unity budget” matters

In practice, a unity budget behaves like a conserved quantity:
- it forces competing explanations to share the same budget,
- it makes comparisons across scales meaningful (local vs global),
- it makes stability sweeps interpretable (what stays when τ tightens?).

This was originally motivated by loudspeaker dispersion/diffraction work, but the same contract applies anywhere “parts must sum to a whole”.

---

## Proof burden and how HUF helps

HUF does not ask you to “believe the proof.”  
It asks you to:
1) run the same public dataset,
2) confirm you get the same artifacts,
3) inspect the stability packet,
4) only then argue about interpretation.

That’s why every run writes a `run_stamp.json`.

