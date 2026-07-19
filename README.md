# Forest OS 

📍 **[Start here: Architecture Overview](ARCHITECTURE_OVERVIEW.md)** — a map of the project before diving into any individual doc.

A pharmacological reasoning ontology encoding 
context-specific bidirectional mediator cascades
with therapeutic effect inference.

## What This Does

Given a disease and its pathophysiological cascade,
the ontology infers:
- Which drugs suppress downstream processes
- At which biological layer each drug intervenes
- Which drugs target the immune cascade vs symptomatic relief

Disease is modelled as a **deviation from a homeostatic baseline** 
rather than as an independent entity — the same regulatory cascade 
that governs normal physiology produces disease when its balance is 
disrupted. This design choice converges with formal frameworks such 
as Qualitative Process Theory (Forbus) and BFO's Disposition theory: 
a process like bronchoconstriction is not inherently pathological, 
it becomes so only when dysregulated. See 
[`docs/v2_vision.md`](docs/v2_vision.md) for the full architecture 
this implies.

---

## Conceptual Framework

The ontology separates five ontological modes — not as five 
independent categories, but as five relational roles around a 
single biomedical layer:

```
Clinical_Framing  ────────────────  human-imposed disease label
        │
        │ classifies
        ▼
Biomedical_Layer (Homeostasis)  ──▶  Biomedical_Layer (Disrupted System)
        │  L4→L3→L2→L1                    │  same L4→L3→L2→L1
        │  normal regulation               │  deviation from baseline
        │                                  │
        │                                  ├──▶ Clinical_Manifestation
        │                                  │     (symptoms, biomarkers)
        │                                  │
        └───────────◀── Therapeutic_Perturbation
                          (drug intervenes on disrupted cascade)


External_Trigger ──▶ triggers deviation from homeostasis
                      (e.g. allergen exposure, plaque rupture)
```

**Biomedical Layer (Homeostasis)** — normal biological 
regulation across L4→L3→L2→L1 layers

**Biomedical Layer (Disrupted System)** — the same layers 
under pathological conditions. Disease is encoded as a 
deviation from homeostatic baseline, not as a separate entity.

**Clinical Framing** — human-imposed classification of 
disrupted cascades as named diseases

**Therapeutic Perturbation** — extrinsic drug interventions 
targeting specific cascade nodes

**Clinical Manifestation** — observable outputs (symptoms, 
biomarkers) produced by disrupted cascades

---

## Design Philosophy

Disease is modelled as a **deviation from homeostatic baseline** 
rather than as an independent entity. The same L4→L3→L2→L1 
cascade that operates in normal physiology produces disease 
when its balance is disrupted. This allows the ontology to 
represent health and disease within a single unified framework.

Full architectural reasoning and design decisions: 
[`docs/key_findings.md`](docs/key_findings.md)

---

## Example Query

A drug's mechanistic target and its clinical consequences are 
tracked as distinct, separately-queryable relations 
(`perturbs_mechanistically` vs `perturbs_functionally`) — so a 
single mechanism can be shown producing multiple downstream 
clinical effects:

"For each drug, what does it hit mechanistically, and what 
clinical goal does that produce?"

| Drug           | Mechanistic Target | Clinical Goal                |
|----------------|---------------------|-------------------------------|
| Corticosteroid | MastCell            | Airway_Remodelling_asthma    |
| Corticosteroid | MastCell            | Chronic_Inflammation_asthma  |
| Beta_Blocker   | SNS_Activation      | Ischaemia_endocardium        |

Full result set: [`sparql/results/drug_mechanistic_target_clinical_goal.csv`](sparql/results/drug_mechanistic_target_clinical_goal.csv)

SPARQL Query Full Description: [`sparql/RESULTS.md`](sparql/RESULTS.md)

---

## Architecture

Four-layer biomedical model:
- L4: Genetic predisposition
- L3: Immune cascade
- L2: Hormonal/biochemical mediators
- L1: Infrastructure (organ/tissue level)

Orthogonal descriptive axes:
- By_Structural_Substrate (spatial context)
- Mediator_Profile (functional role)
- Pathological_State (disease progression)

Full class hierarchy, object properties, SWRL rules, and complete 
ABox instance sets: [`docs/architecture.md`](docs/architecture.md)

---

## Research-style framing 

1. **hasResponsePattern** — generalised pharmacological
   directionality pattern encoding context-specific
   bidirectionality in concentration-dependent mediators

2. **perturbs_mechanistically / perturbs_functionally** — separates a 
   drug's biological target (upregulates/downregulates) from its 
   clinical intent (therapeutic_suppression/therapeutic_activation), 
   making side effects and off-target consequences formally 
   derivable rather than hand-coded

3. **Structure-derived layer scoring** — which layer a drug acts at is 
   a SPARQL query result (`rdfs:subClassOf*` traversal from its 
   mechanistic target), not a manually asserted value

4. **Faceted L1 infrastructure** — orthogonal organ system × 
   structural substrate axes with intersection classes

---

## Documentation

Start here: [`ARCHITECTURE_OVERVIEW.md`](ARCHITECTURE_OVERVIEW.md) — map of the whole project.

| File | Contents |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | Full TBox, RBox, SWRL rules, ABox instance sets |
| [`docs/key_findings.md`](docs/key_findings.md) | Architectural decisions and reasoning |
| [`docs/known_limitation.md`](docs/known_limitation.md) | Open modeling tensions and resolutions |
| [`docs/v2_vision.md`](docs/v2_vision.md) | Homeostasis-as-primary, Named Graph vision |
| [`docs/disease_as_deviation_model_explanation.md`](docs/disease_as_deviation_model_explanation.md) | Named Graph implementation |
| [`docs/clinical_timeline_explanation.md`](docs/clinical_timeline_explanation.md) | Structural acute/chronic classification |
| [`docs/disease_score_explanation.md`](docs/disease_score_explanation.md) | Disease staging (exploratory, limitations documented) |
| [`sparql/RESULTS.md`](sparql/RESULTS.md) | SPARQL query library walkthrough |

---

## SPARQL Queries

Query library lives in [`sparql/`](sparql/) — each `.rq` file has a 
matching `.csv` result in `sparql/results/`. See 
[`sparql/RESULTS.md`](sparql/RESULTS.md) for a narrated walkthrough 
of what each query demonstrates, including a known modeling 
limitation around cross-disease shared nodes (currently only 2 
detected between MI and Asthma — see RESULTS.md for why, and the 
planned GraphDB-level fix).

---

## Tools

- Protégé 5.6.9 (OWL 2.0.0)
- Pellet Reasoner Plug-in 2.2.0.(SWRL support)
- GraphDB: Triple store + SPARQL reasoning
- Python: Graph traversal and validation, replacing SWRL (+ODE)

**Note:** SWRL rules and the Pellet/SQWRL query pipeline used in 
early development have been removed. Only hasResponsePattern SWRL remains. 
Cross-cascade reasoning (e.g. multi-hop `increases`/`inhibits`/`leads_to` traversal) is 
now handled via SPARQL property paths against GraphDB rather than 
custom SWRL rules — this scales more cleanly across diseases and 
is directly queryable rather than requiring a rule re-run per case.

## Ontology Statistics
- 115 classes
- 32 object properties  
- 44 individuals
- 350 logical axioms

## Setup

1. Install [Protégé 5.6.9](https://protege.stanford.edu/) — for editing the ontology
2. Open `ontology/forest_os_ontology_v1.rdf` in Protégé to browse classes/properties
3. Install [GraphDB](https://graphdb.ontotext.com/) (free version) — for querying
4. Create a repository and import `forest_os_ontology_v1.rdf`
5. Open the SPARQL editor and run queries from [`sparql/`](sparql/), or paste them in directly

---

## Status

**Phase 1 complete:** Asthma cascade + MI cascade mapped, 
therapeutic queries validated via SPARQL against GraphDB

**Phase 1.5 complete:** SWRL rules removed (superseded by 
Python + GraphDB reasoning); object properties cleaned for 
disease co-occurrence; `perturbs_mechanistically` / 
`perturbs_functionally` asserted across all mapped drugs

**Phase 2 complete:** Named Graph solving universial nodes problem;

**Phase 3 active:** Mapping diseases for stress test; SNOMED-CT Foundation
course complete - next: aligning L1-L4 class hierarchy against SNOMED's clinical
terminology structure; Reification of cascade edges (CascadeEdge 
individuals carrying rate constants) feeding a Python ODE simulation 
layer

Reference tag: [`v1.2-named-graphs`](../../releases/tag/v1.2-named-graphs)

## Background

Built by a 3rd year MPharm student (2026/27) at the University 
of Manchester exploring biomedical knowledge architecture.
SNOMED-CT Foundation Course completed (July 2026).
