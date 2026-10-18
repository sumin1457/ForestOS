# Architectural Decisions and Property Semantics

This document explains the modelling decisions behind Forest OS, especially how it represents **shared biological mechanims with context-dependent relationships**. It also serves as a reference for the ontology’s object property taxonomy and the Python-generated state-specific named graphs. 

Forest OS is an exploratory knowledge representation project. The relationship described here are modelled assertions, not automatically validated biological mechanisms. 

---

## 1. Connecting conceptual perspectives through object properties 

Forest OS separates five conceptual perspectives around a shared biological backbone: 

- Clinical_Framing — disease classifications and associated clinical descriptions
- Biomedical_Layer — biologiccal entities, mechanisms and regulatory relationships
- Clinical_Manifestation — observable consequences, symptoms and biomarkers
- Therapeutic_Perturbation — interventions acting on biological mechanisms
- External_Trigger — initiating or contributing factors in the mode

**Architectural decision:** these perspectives are distinguished conceptually but connected through explicitly named object properties. The predicates specify **what kind of relationship** links them. 

**Cross-perspective relationships**
| Relationship | Connection represented | Why it is distinguished |
| --- | --- | --- |
| `has_etiology` | `Clinical_Framing` → `Biomedical_Layer` (representing core cause of the named disease) | Associates a clinical classification with its modelled causal context |
| `has_pathophysiology` | `Clinical_Framing` → `Biomedical_Layer` (To core pathophysiological nodes) | Associates a clinical classification with its core pathological node |
| `has_manifestation` | `Clinical_Framing` → `Clinical_Manifestation` | Linking a clinical classification with symptoms |
| `leads_to` | `Biomedical_Layer` → `Clinical_Manifestation` | Records a mechanistic connection to an observable consequence |
| `perturbs_mechansitically` and subproperties | `Therapeutic_Perturbation` → `Biomedical_Layer` | Connects medication to its molecular/biological action |
| `triggers` | `External_Trigger` → `Biomedical_Layer` | Locates a contributing factor to the relative within biological system |

**Example**: `MI_instance` - `has_manifestation` → `Fatigue_instance` is a clinical association, whereas `Epithelial_Damage` -`leads_to` → `Cough_instance` connects a biological process to a manifestation. 

**Why this matters for querying**. A SPARQL query can follow a clinical entry point into a biological pathway, then reach manifestations or drug targets through relationships with different meanings. 

**2. Relationships within the Biomedical Layer**

A second design decision is to **distinguish different kinds of biological relationships within the shared backbone**. Biological layers (L4 Genetic, L3 Immune, L2 Biochemical, L1 Infrastructure, with L1.5 enzyme/receptor categoreis) describe **what kind of node is being represented and its modelling position**. Object properties descrie how nodes are connected. 

The current taxonomy groups biological predicates as follows:
| Property family | Predicates in the supplied taxonomy | Intended modelling role |
| --- | --- | --- |
| `Genetic_Logic` | `activates_transcription`, `is_translated_into`, `represses_transcription` | Transcriptional/translation-related assertions; generated to describe epigenetic, but less developed in current examples. |
| `System_Event_Logic` | `activates`, `causes`, `suppresses`, `requires`, `binds`, `increases`,`inhibits` | General events and mechanisms used across context. |
| `System_Regulation_Logic` | `feedbacks`, `switches_on`, `switches_off` | Regulatory switching and feedback relationships. `feedbacks` show how the loop closed in state 0/1. |
| `System_Recovery_Logic` | `balances`, `balances_to`, `restores` | Represent outcomes of regulation, only used in state 1. |
| `Signal_Semantics_Logic` | `mimics` | Bridge between state 2 (pathological) to state 0/1 (homeostatic/physiological). It models a false-trigger or analogous-trigger relationship.|
| `Layer_Transition_Logic` | `deviates_into` | Marks the transition from state 0/1 to state 2(pathological). It is a transtion point from normal state to pathological state. |
| `System_Progression_Logic` | `progresses_to` | Marks a duration between two points. It involves ‘time’ between the nodes. |

**Distinctions that affect interpretation**
- **balances vs balances_to:** in the current design, `balances` points to what is being corrected, while `balances_to` points to a represented outcome. For example, `LDL_Receptor_High_instance` -`balances_to`→ `LDL_Low_instance` makes that outcome node directly retrievable. The exact boundary of `restores` is a relative to these properties.
- **mimics vs deviates_into**: `mimics` describes an false/analogous trigger, while `deviates_into` marks a pathological deviation. `mimics` serves a transition from pathological node to homeostatic/physiological node while `deviates_into` marks a transition from physiological node to pathological node.




 
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
but not yet used to the depth this level of granularity.
 
### Layer_Transition_Logic — `deviates_into`
Marks the transition from a normal physiological state to a pathological
one. This is the edge State 2 is built on: normal physiology
`deviates_into` pathology, structurally distinct from the false-trigger
mechanism below.
 
### Signal_Semantics_Logic — `mimics`
Represents a **false trigger** — a signal that structurally resembles a
real physiological trigger closely enough that downstream machinery
cannot distinguish it from the real one at the point of sensing.

Case: `Plaque_Rupture --mimics--> Injury`. The cascade fires
exactly as it would for genuine tissue injury — `Injury` triggers the
normal physiological clotting response `(Injury → ... → Blood_Clot)` —
because the entry signal is indistinguishable from a real trigger. The
pathology isn't in the cascade responding; it's in what triggered it.
Where this response then fails to resolve (chronic re-triggering, no
clearance mechanism engaging) is where `Blood_Clot --deviates_into--> Vascular_Blockage` enters — the separate, second failure.

`mimics` and `deviates_into` are often present together at a State 2
entry point (false trigger + broken brake, per the README's State 2
description) but are separate predicates because they describe different
failure mechanisms — one at the input (a fake signal fools the sensor),
one at the resolution (a real signal is sensed correctly but the
correction never engages).
 
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
depend on: without `balances_to` pointing at a result node, it would be
impossible to compare the pathological resolution node against the
Pathological-state instance.
 
### System_Regulation_Logic — `feedbacks`, `switches_on`, `switches_off`
`switches_on`/`switches_off` links Regulatory switch and Sensor. `feedbacks` is
separate — it represents the closed-loop signal from an Effector back to
its originating Regulatory_Switch, and is what makes negative/positive
feedback chains queryable directly in the homeostatic state, e.g.
`LDL_Receptor_Low --feedbacks--> Cholesterol_ER_Low_instance`.
 
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
Covered in more detail under Key Findings §3, Secondary Design Decisions 
(`perturbs_mechanistically`vs `therapeutic_intent`). `Effect` (`resolves`/`resolves_to`) 
is the State 3 resolution predicate — `resolves_to` specifically is the
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

The four-state model itself exists to capture disease as a dynamic process. 
Implementing that model then surfaced a structural problem worth documenting on its own:

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
