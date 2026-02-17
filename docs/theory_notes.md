# HUF Theory Notes (Optional)

This file exists only to park *optional* theory so the Handbook + Reference Manual stay operational and short.

## The invariant

HUF treats a system as finite elements with a **unity budget**:

- **Mass budget**: nonnegative weights that sum to 1 (allocation / frequency / share)
- **Energy budget**: nonnegative energy-like weights that sum to 1 (power / squared magnitude)

The contract requirement is simple:

- Every operation that changes membership or grouping must **renormalize**
- Every run must emit the mandatory artifacts (or the run is invalid)

## Why “unity” matters

Unity is what makes comparisons stable:

- active sets are comparable between runs
- discards are meaningful (you can say exactly how much budget you threw away)
- stability packets can quantify brittleness (Jaccard, rank stability)

## Error metrics

HUF always reports **discarded budget**. Domain metrics are pluggable:

- Total variation distance (mass-type)
- RMSE / Parseval-derived energy error (energy-type)
- Any custom metric computed from the kept set

That’s it. Everything else (category theory, sphere mapping, etc.) is useful background, but it’s not required to *run* HUF.
