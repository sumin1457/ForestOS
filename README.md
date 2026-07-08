# Forest OS 

A pharmacological reasoning ontology encoding 
context-specific bidirectional mediator cascades
with therapeutic effect inference.

## What This Does

Given a disease and its pathophysiological cascade,
the ontology infers:
- Which drugs suppress downstream processes
- At which biological layer each drug intervenes
- Which drugs target the immune cascade vs symptomatic relief

## Why Forest?

The body is an ecosystem — trillions of interconnected 
processes, each a branch in a living system. Health is 
the forest in balance. Disease is not a separate entity 
but a disruption of that balance, cascading through layers.

Forest OS models this directly: the same L4→L3→L2→L1 
cascade that operates in homeostasis produces disease 
when disrupted. The forest metaphor is the architecture.

## Conceptual Framework

![Clinical Framework](diagrams/Clinical_Framework.png)
![Asthma Cascade](diagrams/Asthma_Figjam.png)

The ontology separates five ontological modes:

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


## Design Philosophy

Disease is modelled as a **deviation from homeostatic baseline** 
rather than as an independent entity. The same L4→L3→L2→L1 
cascade that operates in normal physiology produces disease 
when its balance is disrupted. This allows the ontology to 
represent health and disease within a single unified framework.

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

Full result set: [`SPARQL/results/drug_mechanistic_target_clinical_goal.csv`](SPARQL/results/drug_mechanistic_target_clinical_goal.csv)


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

## Research-style framing 

1. hasResponsePattern — generalised pharmacological
   directionality pattern encoding context-specific
   bidirectionality in concentration-dependent mediators

2. intervenesAtLayer — therapeutic depth scoring
   enabling layer-aware drug comparison

3. Faceted L1 infrastructure — orthogonal organ system
   × structural substrate axes with intersection classes

4. perturbs_mechanistically / perturbs_functionally — separates 
   a drug's biological target (upregulates/downregulates) from 
   its clinical intent (therapeutic_suppression/therapeutic_activation), 
   making side effects and off-target consequences formally derivable 
   rather than hand-coded

## SPARQL Queries

Query library lives in [`SPARQL/`](SPARQL/) — each `.rq` file has a 
matching `.csv` result in `SPARQL/results/`. See 
[`SPARQL/RESULTS.md`](SPARQL/RESULTS.md) for a narrated walkthrough 
of what each query demonstrates, including a known modeling 
limitation around cross-disease shared nodes (currently only 2 
detected between MI and Asthma — see RESULTS.md for why, and the 
planned GraphDB-level fix).

## Tools

- Protégé 5.6.9 (OWL 2.0.0)
- Pellet Reasoner Plug-in 2.2.0.(SWRL support)
- GraphDB: Triple store + SPARQL reasoning
- Python: Graph traversal and validation, replacing SWRL (+ODE)

**Note:** SWRL rules and the Pellet/SQWRL query pipeline used in 
early development have been removed. Only hasResponsePattern SWRL remians. 
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

1. Install [Protégé 5.6.9](https://protege.stanford.edu/)
2. Install Pellet reasoner plugin
3. Open Ontology folder
4. Open `ontology/forest_os_ontology_v2.rdf`
5. Reasoner → Pellet → Start Reasoner
6. Open SQWRLTab to run queries

## Status

**Phase 1 complete:** Asthma cascade + MI cascade mapped, 
therapeutic queries validated via SPARQL against GraphDB

**Phase 1.5 complete:** SWRL rules removed (superseded by 
Python + GraphDB reasoning); object properties cleaned for 
disease co-occurrence; `perturbs_mechanistically` / 
`perturbs_functionally` asserted across all mapped drugs

**Phase 2 active:** Python (via ODE)

**Phase 3 inactive:**  SNOMED-CT alignment, Graph DB

Reference tag: [`v1.0-mi-complete`](../../releases/tag/v1.0-mi-complete)

## Background

Built by a 3rd year(26/27) MPharm student at University 
of Manchester exploring biomedical ontology engineering.
Pursuing SNOMED-CT certification.
