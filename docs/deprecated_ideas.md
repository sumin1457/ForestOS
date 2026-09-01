# Deprecated / Paused Ideas

Ideas that were part of an earlier draft of Forest OS but are currently
removed from the active README — either because they were unfinished,
superseded, or need rework before they're worth presenting. Kept here so
the thinking isn't lost, and so the main README stays a description of
what's actually built rather than what's planned or half-built.

---

## Disease Stage Score

**Status:** Paused, not deleted from the ontology — just removed from the
README's main narrative until the scoring method is reworked.

**Original idea:** Two dimensions computed structurally from the ontology:

| Dimension | Method | Reliability |
|---|---|---|
| Chronic depth | Count of `progresses_to` transitions (time-axis property) | High — model-density independent |
| Cascade complexity | Node count from entry to first L1 node | Moderate — reflects ABox granularity |

Early results:

| Disease | Cascade Complexity | Chronic Depth |
|---|---|---|
| Asthma | 8 | 2 |
| MI | 6 | 2 |

**Why paused:** Cascade complexity is sensitive to how densely a given
disease has been modelled (ABox granularity) rather than a property of the
disease itself — two diseases mapped to different levels of detail aren't
comparable on this metric yet. Chronic depth is more defensible but hasn't
been validated against enough diseases to claim it generalises.

**Planned successor:** ODE-derived severity (peak activation + time-to-peak
per L1 node), which would ground the score in simulated dynamics rather
than static graph structure. Revisit once the Python simulation layer
(`forestos_disease_score.py`) is rebuilt around named graphs rather than
the earlier ad hoc version.

---

## Pharmacological Taxonomy

Drugs are classified by how they relate to the healthy baseline:

```
Type 1 — Homeostatic mimicry
  Drug mimics the body's own molecule.
  Corticosteroid → mimics cortisol (endogenous anti-inflammatory)
  Nitrate → donates NO (endogenous platelet inhibitor)
  Closest to root. Widest cascade suppression.

Type 2 — Physiological hijacking
  Drug exploits existing machinery unrelated to disease cause.
  LABA → uses SNS bronchodilation pathway
  SNS has no role in why asthma develops.
  Addresses downstream output, not upstream cause.

Type 3 — Enzymatic blockade
  Drug blocks rate-limiting enzyme in pathological substrate.
  Statin → HMGCoA reductase (cholesterol synthesis)
  Aspirin → COX inhibition (arachidonic acid cascade)
```

Side effects follow structurally: LABA causes tachycardia because SNS
bronchodilation and cardiac rate share machinery. The adverse effect is
derivable from the mechanism — not asserted manually.

---

*(Add further entries above this line as ideas are paused or removed.)*
