## Key Architectural Decisions — UPDATED

| Decision | Reasoning |
|---|---|
| **intervenesAtLayerScore REMOVED** | Replaced by SPARQL rdfs:subClassOf* traversal from perturbs_mechanistically target. Structure derives the score. No manual assertion. |
| **perturbs_mechanistically vs perturbs_functionally** | mechanistic = WHERE drug acts (L2/L3 node). functional = WHAT it achieves (L1 clinical outcome). Both asserted directly. No SWRL needed. |
| **has_pathophysiology minimal** | Only key anchor nodes asserted (cascade entry + key clinical targets). Full cascade traversed by SPARQL property paths. |
| **modulates as neutral CDM connector** | CDM → Signalling_Intermediate only. Direction determined by hasResponsePattern + hasConcentrationLevel via SWRL. Not increases/inhibits (direction unknown at assertion time). |
| **Signalling_Intermediate as SWRL boundary** | Replaces Downstream_Process as SWRL target. Prevents rule firing across entire ontology. CDM rules fire only within SI boundary. |
| **Pathological_State = terminal clinical node** | therapeutic_suppression targets these. Not reachable via CDM SWRL rules directly — chain extends there. |
| **SNS/RAAS as Feedback_Regulated_Entity at CLASS level** | Intrinsic homeostatic regulators — feedback is their nature, not context-specific. Instances inherit via class typing. |
| **Atherosclerosis as Chronic_Structural_Disruption** | Develops over decades, permanently remodels arterial wall — analogous to Airway_Remodelling. Not Acute_Functional_Disruption. |
| **Ischaemia as Universal_Process under L1** | Same mechanism everywhere (heart, brain, kidney). Context via occursIn data property on instance. |
| **Blood_Clot as Acute_Functional_Disruption** | Sudden, acutely disrupts blood flow. Blood_Clot progresses_to Ischaemia (time-involved). |
| **Beta_Blocker dual assertion** | perturbs_mechanistically → SNS (L2, where it acts). therapeutic_suppression → Ischaemia (L1, what it achieves). Mechanistic target ≠ therapeutic intent — both must be formally represented. |
| **TXA2_platelet_instance reused in MI** | First universal node shared between asthma (platelet) and MI cascades. Demonstrates architecture working. Named Graphs will formalise this. |
| **SPARQL property paths replace SubPropertyChain** | SubPropertyChain (has_pathophysiology chains) removed. SPARQL (:increases|:targets|...)* traverses full cascade dynamically. More flexible, no pre-computation. |

---

## Major Discoveries This Session

### 1 — Tool Stack Hierarchy

```
DL Query:   TBox viewport only — useless for instance-rich ontology
SQWRL:      reads asserted + SWRL outputs — blind to SubPropertyChain
SPARQL:     reads everything in exported inferred graph ✓
ODE/Python: resolves dynamic competition between inputs ✓

DL Query → SQWRL → SPARQL → ODE: each layer goes deeper
```

### 2 — Named Graph Architecture 

```
Context does NOT belong inside nodes
Context belongs in the GRAPH WRAPPER around triples

Universal_node stays universal
[MI_graph] { Universal_node occursIn Cardiovascular }
[Stroke_graph] { Universal_node occursIn Nervous }

Same node. Different contexts. No duplication.
Side effects formally derivable as cross-context perturbations.
```

### 3 — Layer Score Derivation

```
intervenesAtLayerScore (manual) → REMOVED
Replaced by: rdfs:subClassOf* traversal from perturbs_mechanistically target
"Where the drug acts structurally IS the layer score"
No manual assertion. Structure derives the score.
```

### 4 — Dual Drug Assertion Pattern

```
perturbs_mechanistically → WHERE it acts (L2/L3 mechanism)
therapeutic_suppression  → WHAT it achieves (L1 clinical goal)

These are different things. Both must be formally represented.
Beta_Blocker: acts at SNS (L2) to achieve reduced ischaemia (L1)
Not a compromise — a more faithful representation than either alone.
```

---

## Design Philosophy — UPDATED

1. **Beauty precedes correctness** — structural elegance is the truth detector

2. **Assert only ground truth** — never assert what should be inferred

3. **SWRL as minimal translator** — CDM concentration → direction only. Nothing else.

4. **SPARQL replaces SWRL for traversal** — property paths are cleaner than chains for cascade membership

5. **Context belongs in the graph, not the node** — Named Graph principle

6. **Structure derives scores** — layer score is a SPARQL query result, not a data property

7. **Two drug assertions per drug** — mechanistic target + clinical goal. Not one or the other.

8. **Fidelity matches competency questions** — don't add nodes until a query requires them

9. **Universal nodes, contextual graphs** — the ontology encodes topology, the graph layer encodes context

10. **ODE resolves what OWL cannot** — competing inputs, dynamic feedback, temporal evolution

---