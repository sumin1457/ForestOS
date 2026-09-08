This document explains the predicates used in the ontology. Since the state model is built on both a data property (`hasSystemState`) and state-specific predicates, understanding these predicates is beneficial for interpreting the key findings and architectural decisions below. This document also covers major findings and the architectural decisions themselves.

---

## 1. Object Property Taxonomy
 
Every predicate used elsewhere in this document sits inside one of four
top-level branches under `owl:topObjectProperty`. 
 
```
owl:topObjectProperty
├── Biological_Logic
│   ├── Genetic_Logic          — activates_transcription, is_translated_into, represses_transcription
│   ├── Layer_Transition_Logic — deviates_into
│   ├── Signal_Semantics_Logic — mimics
│   ├── System_Event_Logic
│   │   ├── Discrete_Event_Logic       — activates, causes, suppresses
│   │   ├── Gating_Logic               — requires
│   │   ├── Molecular_Interaction_Logic — binds
│   │   └── Quantitative_Regulation_Logic — increases, inhibits
│   ├── System_Progression_Logic — progresses_to
│   ├── System_Recovery_Logic    — balances, balances_to, restores
│   └── System_Regulation_Logic  — feedbacks, switches_on, switches_off
├── Clinical_Logic
│   ├── Macro-Clinical_Logic — has_complication, has_etiology, has_manifestation, has_pathophysiology
│   └── Symptoms_Logic       — leads_to
├── Drug_Intervention_Logic
│   ├── Effect                    — resolves, resolves_to
│   ├── perturbs_mechanistically  — agonises_receptor, antagonises_receptor, downregulates, upregulates
│   └── therapeutic_intent        — therapeutic_activation, therapeutic_suppression
└── External_Logic
    └── triggers
```
 
### Genetic_Logic
Models epigenetic/transcriptional detail (`activates_transcription`,
`is_translated_into`, `represses_transcription`). Present in the ontology
but not yet used to the depth this level of granularity would support —
kept in place for when a disease case study actually needs it.
 
### Layer_Transition_Logic — `deviates_into`
Marks the transition from a normal physiological state to a pathological
one. This is the edge State 2 is built on: normal physiology
`deviates_into` pathology, structurally distinct from the false-trigger
mechanism below.
 
### Signal_Semantics_Logic — `mimics`
Represents a **false trigger** — a signal that structurally resembles a
real physiological trigger closely enough that downstream machinery
cannot distinguish it from the real one at the point of sensing.

Canonical case: `Plaque_Rupture --mimics--> Injury`. The cascade fires
exactly as it would for genuine tissue injury — `Injury` triggers the
normal physiological clotting response `(Injury → ... → Blood_Clot)` —
because the entry signal is indistinguishable from a real trigger. The
pathology isn't in the cascade responding; it's in what triggered it.
Where this response then fails to resolve (chronic re-triggering, no
clearance mechanism engaging) is where `Blood_Clot --deviates_into--> Vascular_Blockage` enters — the separate, second failure: not a false
signal anymore, but the loop itself failing to close.

`mimics` and `deviates_into` are often present together at a State 2
entry point (false trigger + broken brake, per the README's State 2
description) but are separate predicates because they describe different
failure mechanisms — one at the input (a fake signal fools the sensor),
one at the resolution (a real signal is sensed correctly but the
correction never engages) — not two strengths of the same failure.
 
### System_Event_Logic
The generic cascade machinery — activation, causation, suppression,
gating, binding, quantitative up/down-regulation. This is the "ordinary
biology happening" layer, used across all four states.
 
### System_Progression_Logic — `progresses_to`
The one predicate that explicitly involves **time**. Used to bridge
physiology into pathology across a temporal axis  — e.g. `Vascular_Blockage --progresses_to--> Ischaemia`, `LDL_Deviated --progresses_to--> Atherosclerosis`. 
It is structurally distinct from `deviates_into`: `deviates_into` 
marks a state boundary being crossed, `progresses_to` marks a duration between two points.
 
### System_Recovery_Logic — `balances`, `balances_to`, `restores`
Used only in State 1 (Physiological) — the self-resolving loop. The
distinction between `balances` and `balances_to` is a deliberate query
design choice, not just a naming variant:
 
- `balances` points to **what is being corrected** —
  `High_Heart_Rate --balances--> Hypoxia`, i.e. the target of correction.
- `balances_to` points to **the result state after correction** —
  `LDL_Receptor_High_instance --balances_to--> LDL_Low_instance`, i.e.
  where the system ends up.
`balances_to` was chosen for the resolution-chain queries specifically
because it makes the *outcome* directly queryable — a query walking
`balances_to` edges returns the actual resolved state at each step, not
just the name of the problem being solved. This is what
`physiological_self_resolution.rq` and `physio_vs_patho_divergence.rq`
depend on: without `balances_to` pointing at a result node, there would
be nothing on the Physiological-state instance to compare against the
Pathological-state instance's absence of resolution.
 
### System_Regulation_Logic — `feedbacks`, `switches_on`, `switches_off`
`switches_on`/`switches_off` is the ambiguous predicate pair discussed in
§3 below (source-anchored, not self-describing). `feedbacks` is
separate — it represents the closed-loop signal from an Effector back to
its originating Regulatory_Switch, and is what makes negative/positive
feedback chains queryable directly, e.g.
`LDL_Receptor_Low --feedbacks--> Cholesterol_ER_Low_instance`. Most
useful for showing Homeostatic states specifically, since
a functioning feedback edge is close to the definition of a closed loop.
 
### Clinical_Logic
Bridges `Clinical_Framing` (the disease label) to `Biomedical_Layer`
(the underlying mechanism) and to `Clinical_Manifestation` (the
observable symptoms) — two separate bridges, not one:
 
- `has_etiology` — disease → root mechanism, e.g.
  `MI_instance --has_etiology--> Atherosclerosis`.
- `has_manifestation` — disease → symptom, e.g.
  `MI_instance --has_manifestation--> Fatigue`.
- `leads_to` (Symptoms_Logic) — mechanism → symptom, e.g.
  `Epithelial_Damage --leads_to--> Cough`. This is what
  `symptoms_by_disease.rq` terminates on.
Keeping `has_etiology`/`has_manifestation` separate from `leads_to` means
a disease's link to a symptom, and the underlying mechanism's link to
that same symptom, are independently queryable — a disease can be
connected to a manifestation directly at the Clinical_Logic level while
the *mechanistic reason* for that manifestation is a separate, traceable
path through the Biomedical_Layer.
 
### Drug_Intervention_Logic
Covered in more detail under Key Findings §4 (`perturbs_mechanistically`
vs `therapeutic_intent`). `Effect` (`resolves`/`resolves_to`) is the
State 3 resolution predicate — `resolves_to` specifically is the
self-describing predicate used in the state graph builder.
 
### External_Logic — `triggers`
The entry point for anything originating outside the biological system
being modelled — e.g. an allergen exposure or a physical injury event
initiating a cascade. Kept as its own top-level branch, separate from
`Biological_Logic`, since a trigger is by definition not itself part of
the body's own machinery.
 
---

## 2. Major Finding

### The universal-node problem: same Tbox class, divergent-point instances

The v1 tension "shared universal nodes lose disease context" (see
`docs/archive/v1_notes.md`) is resolved not by full named-graph separation
of every instance, but selectively: a node stays under one Tbox class, and
multiple *instances* of that class exist, each tagged with a different
`hasSystemState` — but only at nodes that are genuine divergence points or
structurally crucial for what happens next. Most of the cascade doesn't
need this; only the nodes where physiological and pathological paths
actually diverge do.

Duplicating every node per state would create over-duplication problem 
the architecture is trying to avoid. The instance split is
reserved for nodes where the divergence is the finding — e.g. `LX_Receptor`,
where the state-specific instances resolve differently and *that
difference is the point*.

Because both instances share `rdf:type`, they're queryable as "sister
nodes": cross back to the shared class, find the other instance(s) under
it, and diff their outgoing edges directly — no separate schema needed per
state. This can be expressed either as a same-default-graph query
(`FILTER EXISTS` / direct `hasSystemState` match, as in
`physio_vs_patho_divergence.rq`) or scoped via `GRAPH {}` against the named
state graphs, depending on whether the comparison needs to stay within one
state's context or cross between two.

`physio_vs_patho_divergence.rq`'s LX_Receptor result is the first
concrete case of this pattern doing real work.

---

## 3. Key Architectural Decisions 

### Core State-Model Decisions

| Decision | Reasoning |
|---|---|
| **State graph membership is asserted, not inferred** | A node belongs to a state graph if `hasSystemState "X"` is asserted directly. No downstream traversal. |
| **Edges are source-anchored** | An edge belongs to graph X if its *source* node is tagged X, regardless of the target's tag status. Chosen over both-endpoints-required (too strict — disconnects neutral nodes like SCAP) and either-endpoint (too loose — duplicates edges into states they don't structurally belong to). |
| **Self-describing predicates bypass hasSystemState** | `resolves_to` (State 3), `balances_to`/`restores` (State 1), `deviates_into`/`mimics` (State 2) are unambiguous by predicate alone — asserted directly into their graph, no tag check needed. |
| **Named graphs are filtered views over one default graph** | The default graph holds every asserted node and edge, untyped by state. The four state graphs (Homeostatic / Physiological / Pathological / Pharmacological) are built from it, not maintained as a separate source of truth. Rebuilding from the default graph after every Protégé export is the intended workflow (`rebuild_state_graphs()`). |

### Secondary Design Decisions

| Decision | Reasoning |
|---|---|
| **perturbs_mechanistically vs therapeutic_intent** | Mechanism (`agonises_receptor`/`antagonises_receptor`/`upregulates`/`downregulates`) and clinical intent (`therapeutic_activation`/`therapeutic_suppression`) are asserted as independent properties, not collapsed into one label. A drug can mechanistically antagonise an inhibitory target to achieve a net activating intent — keeping them separate lets the ontology represent that gap. |
| **Pharmacological graph added as a 4th state** | v1 only materialised Homeostatic/Physiological/Pathological as named graphs; drug reasoning worked only by querying `resolves_to` directly against the default graph. v2 gives State 3 the same named-graph convenience as the others. |
| **intervenesAtLayerScore removed** | Replaced by SPARQL `rdfs:subClassOf*` traversal from `perturbs_mechanistically` target (`drug_layer_depth.sparql`). Structure derives the score — no manual assertion. |

### Deprioritized / Paused

| Decision | Reasoning |
|---|---|
| **Disease Stage Score paused, not deleted** | Cascade complexity metric was confounded with modelling granularity (ABox decomposition density, not clinical severity) rather than a property of the disease itself. Moved to `docs/deprecated_ideas.md` pending an ODE-derived successor. |
| **Clinical timeline paused, not deleted** | Acute/chronic pathology staging designed on `progresses_to` (the time-bearing predicate), but not yet integrated into the four-state model's SPARQL layer. Moved to `docs/deprecated_ideas.md` pending integration with the state graphs. |

---
