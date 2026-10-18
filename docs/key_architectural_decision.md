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
| `therapeutic_intent` | `Therapeutic_Perturbation` → `Biomedical_Layer` | It bridges the intended purpose of the medication. |
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

**3. Object property taxonomy**
The following tree preserves the hierarchy in the existing project documentation. It is the **OWL object property organisation**; it should not be confused with the five conceptual perspectives. 

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
The four branches (Biological_Logic, Clinical_Logic, Drug_Interventio_Logic, External_Logic) organise predicates by broad semantic purpose. In particular, a clinical predicate can bridge perspective, while biological predicates can describe pathways entirely within the Biomedical_Layer. 
 
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
