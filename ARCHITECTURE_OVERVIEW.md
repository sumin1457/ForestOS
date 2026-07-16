# Forest OS — Architecture Overview

A map of the project, in order. Read this first — the individual docs go deep on one piece each; this shows how they fit together.

---

## 1. The Core Problem

Biomedical processes are universal — ischaemia, chronic inflammation, bronchoconstriction happen the same way regardless of disease. But the same process shows up in different diseases, in different tissues, with different consequences.

```
Ischaemia in MI          → cardiovascular tissue → chest pain
Ischaemia in Stroke       → neural tissue         → different symptoms

Same biological node. Different disease. Different meaning.
```

OWL/Protégé forces a choice: duplicate the node per disease (breaks cross-disease reasoning, inflates the ABox), or keep it singular (loses which context it's acting in). Neither is acceptable. This tension is documented in `docs/known_limitation.md` from the v1.0 milestone — it's the problem the rest of this architecture exists to solve.

---

## 2. The Core Solution — Named Graphs

**Context belongs on the edge, not the node.**

```
Default graph:
    Every node, every asserted edge — the full ontology as
    exported from Protégé. Universal biology. Never modified.

context/Cardiovascular, context/Respiratory, context/Neural, ...:
    Location-specific EDGES only — which L2/L3 machinery connects
    to which L1 tissue consequence, in that specific context.

The node stays singular in the default graph.
The named graph says where its effect applies.
```

Built by `namedgraph/forestos_disease_as_deviation_model.py`. Nodes are classified into a location context two ways: Type A nodes already have a location class in the TBox (e.g. `Bronchoconstriction SubClassOf Respiratory_System`); Type B universal nodes (e.g. `Ischaemia`) get a minimal `occursIn` assertion per instance. Full reasoning: `docs/disease_as_deviation_model_explanation.md`.

**Status: proven at 2 diseases, 2 contexts, 0 unclassified edges. About to be stress-tested at 4-5 diseases (COPD, Stroke).**

---

## 3. What's Built On Top

Two analytical tools query the named graph structure to derive clinically meaningful classifications — without any manually asserted severity or timing data.

### Clinical Timeline (`python/forestos_clinical_timeline.py`)
Classifies each symptom as acute or chronic based purely on whether a `progresses_to` structural step exists between tissue damage and symptom. A single SPARQL zero-or-one path operator (`progresses_to?`) does the classification. No `hasSeverity` property needed — the structure IS the answer.

**Status: working, validated against MI and Asthma. One honest anomaly found and documented (MI shows 0 acute symptoms — a real modelling granularity gap, not a bug) — see `docs/clinical_timeline_explanation.md` §6.**

### Disease Stage Score (`python/forestos_disease_score.py`)
Computes a two-dimensional staging profile (cascade complexity + chronic depth) purely from graph traversal depth.

**Status: exploratory, not yet validated for cross-disease comparison. Score is confounded with ABox modelling granularity — a disease mapped in more detail scores "worse" for reasons that have nothing to do with its actual severity. This is documented in detail, not hidden, in `docs/disease_score_explanation.md` §5, with three named paths to a genuine fix (§6).**

---

## 4. Reading Order

```
1. This file           — the map
2. README.md           - Overview of ontology
3. known_limitation.md — what problems exist / are resolved
4. disease_as_deviation_model_explanation.md  — how Named Graphs work
5. clinical_timeline_explanation.md           — first thing built on it
6. disease_score_explanation.md               — second thing, and its open problem
7. RESULTS.md           — the SPARQL query library this all sits on top of
```

---

## 5. What's Proven vs. Still Open

```
PROVEN:
  Named Graph architecture resolves shared-node duplication
  Clinical Timeline derives real classification from pure structure
  Cross-graph SPARQL queries work (default graph ↔ context graphs)
  Old queries (pre-Named-Graph) still return identical results — additive, non-destructive

OPEN:
  Disease Stage Score not yet cross-disease valid (granularity confound)
  Named Graph pattern proven at 2 diseases — generalisation untested past that
  No reversibility dimension yet (Airway_Remodelling vs Necrosis_heart
    score identically despite very different clinical meaning)
  Rate constants / ODE layer not yet connected to any of this
```

---

## 6. Current Milestone

Tag: `v1.2-named-graphs`

Two diseases (MI, Asthma), two location contexts (Cardiovascular, Respiratory), Named Graph architecture validated, two analytical layers built on top, one open limitation clearly scoped. Next: COPD and Stroke, to stress-test whether the architecture holds at scale.
