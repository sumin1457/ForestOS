# Forest OS
### A Biomedical Knowledge Architecture for Modelling Biological Regulation, Disease and Pharmacological Intervention

Biological systems are not simply collections of molecules, pathways and disease labels. They are interconnected regulatory-harmonised systems, where the same biological processes can behave differently depending on physiological conditions, pathological disturbances and pharmacological intervention. 

**Forest OS began with a question: how can we represent that complexity as structured, queryable knowledge?**

I started this independent project to explore how biomedical ontologies could connect different perspectives on disease — from underlying molecular mechanisms and regulatory processes to clinical manifestations and therapeutic interventions. 

Using OWL, Protégé and SPARQL, I’ve developed a prototype that organises biological knowledge through a shared conceptual architecture, while distinguishing how regulatory behaviour is represented across different contexts. 

The project is built around two connected challenges:

- Representing biological complexity: How can clinical, molecular, regulatory and pharmacological perspectives be organised within a coherent knowledge model?
- Representing biological change: How far can an ontology capture context-dependent regulatory behaviour, and what additional modelling approaches might be needed to represent dynamnics?

The second question emerged directly from building the first version of Forest OS. While OWL/RDF provides a powerful way to define biological entities and relationships, representing how a biological entity changes over time has proved more challenging. 

This has led me to explore whether qualitative dynamic models could complement ontology-based knowledges representation. 

---

## How Forest OS is Structured

Forest OS is built around three complementary dimensions: **how biological knowledge is viewed, how mechanisms are organised, and how regulatory behaviour differs across contexts.**

These dimensions serve different purposes. The conceptual framework **connects** different perspectives on disease and treatment. The biological layers **organise** the mechanisms themselves. The four-state model then allows those mechanisms to be **examined** under different regulatory conditions. 

**1. A Multi-Perspective Conceptual Framework**

Forest OS begins with a distinction between biological regulation and the clinical labels human assign to it. 

Biological systems operate through interconnected regulatory processes. When these processes deviate from homeostatic regulation, the resulting conditions may be recognised and classified clinically as particular diseases. In Forest OS, the disease label is therefore treated as a form of **Clinical Framing**, rather than as the biological mechanism itself.

This distinction shapes the ontology’s conceptual architecture. 

At its centre is the Biomedical Layer, which represents the biological entities, processes and regulatory relationships underlying a condition. Four other perspectives connect to this mechanistic backbone, each with a distinct role: 

| Perspective | Role in the architecture |
|---|---|
| Clinical Framing | Assigns a human-defined disease classification to a biological condition |
| Biomedical Layer | Represents the underlying biological mechanisms and regulatory processes |
| Clinical Manifestation | Captures observable consequences of those processes, such as symptoms and biomarkers |
| Therapeutic Perturbation | Represents pharmacological interventions acting on the biological system |
| External Trigger | Represents factors that initiate or contribute to a regulatory disturbance |

These perspectives are connected, but they are **not interchangeable descriptions of a disease**.

A clinical label classifies a condition; a biological mechanism explains how it arises or operates; a clinical manifestation describes what can be observed; and an intervention acts on the underlying system. 

The purpose of this separation is to preserve these different relationships without collapsing them into a single disease-centred representation. 

By keeping theses perspectives distinct and connecting them through explicitly defined relationships, Forest OS aims to support queries that move between clinical classifications, biological mechanisms, observable consequences and pharmacological interventions without conflating their different roles. 

This is particularly important when different diseases share parts of the same underlying biological pathways. The architecture is designed to reuse commmon mechanisms while preserving the disease-specific context in which they are represented, allowing SPARQL queries to explore both shared biology and differences between conditions. 

Conceptual Framework at a glance:

```
Clinical_Framing  ────────────────  human-imposed disease label
        │
        │ classifies
        ▼
Biomedical_Layer (Homeostatic & Physiological)  ──▶  Biomedical_Layer (Pathological)
        │  L4→L3→L2→L1                           │  **mimics** normal physiological signal
        │  normal regulation                     │
        │  Balance achieved                      │
        │                                        ├──▶ Clinical_Manifestation
        │                                        │     (symptoms, biomarkers)
        │                                        │
        └───────────────────────────◀── Therapeutic_Perturbation
                                       (drug intervenes on disrupted cascade)


External_Trigger ──▶ triggers deviation from homeostasis
                      (e.g. allergen exposure, plaque rupture)
```
---

**2. Organising the Biomedical Layer**

Within the Biomedical Layer, Forest OS uses a layered structure to organise different aspects of biological regulation. 

| Layer | Focus | Examples |
|---|---|---|
| L4 — Genetic | Genetic and epigenetic factors | Predispositions, mutations, epigenetic states | 
| L3 — Immune | Immune signalling and regulation | Th2, IgE signalling, dendritic cell activity | 
| L2 — Biochemical | Molecular signals and mediators | Histamine, prostaglandins, cAMP, NO, PGI2 | 
| L1 — Infrastructure | Tissue-level processes and consequences | Bronchoconstriction, ischaemia, atherosclerosis | 

The model also includes **L1.5 enzyme and receptor categories**, providing additional distinctions for molecular targets such as ACE, COX, HMG-CoA reductase and specific receptors. 

This structure serves three purposes: it helps classify and locate biological nodes, provides a startring point for exploring the **structural depth of pharmacological interventions**, and supports SPARQL queries across different biological categories and relationships.

Asthma prototype example: []()

[`sparql/drug_layer_depth.rq`](sparql/drug_layer_depth.rq).

---

**3. Four System States**

The next challenge I encountered was that **the same biologcial component can behave differently depending on the condition of the system**. A regulatory pathway may successfully restore balance under physiological conditions, become disrupted in disease, or respond differently following pharmacological intervention. 

To capture these differences, Forest OS uses four snapshots of biological context:

| State | Context | Interpretation |
|---|---|---|
| State 0 - Homeostatic | Ongoing baseline regulation | Endogenous regulatory processes maintain or restore balance |
| State 1 - Physiological | Emergency Signal | Still under homeostatic response, but regulatory response addresses a disturbance through endogenous mechanism. State 1 successfully restores back to state 0 |
| State 2 - Pathological | Disrupted | False trigger or broken break (loss of certain node) cause deviation from healthy state |
| State 3 - Pharmacological | Drug-modified state | An intervention changes the system’s behaviour or outcomes, without necessarily restoring normal regulation (S0) |

These snapshots allow SPARQL queries to compare **which nodes and relationships remain shared, where regulatory behaviour diverges, and how downstream consequences differe between states.**

This is my approach to representing aspects of dynamic biological behaviour within an ontology. It captures differences between selected states/condtions, although it does not yet simulate how the system moves between them over time.

For a more detailed explanation, including worked examples, see : [`docs/state_model.md`](docs/state_model.md).

---

## Named Graph Architecture

To build on the four-state model, I wrote a Python script that uses state membership and state-specific relationships to construct separate RDF named graphs for each system state. 

The aim was to create **queryable snapshots of the same underlying biological structure**, making it easier to compare shared nodes, context-dependent relationships and downstream consequences across states using SPARQL. 

This Named graph currently works as a ‘filtered view’ in SPARQL query. 

Python script for Named graph is in [`python/forestos_state_model_v2.py`](python/forestos_state_model_v2.py), 
explanation available in [`python/docs/forestos_state_model_design.md`](python/docs/forestos_state_model_design.md).

---
## Current Case Studies

**Hypercholesterolaemia** is the most developed case study. It explores cholesterol regulation, pathological disturbances and pharmacologial intervention within the four-context framework. 

**Myocardial infarction** is included as an earlier reference case, while **asthma** was explored under a previous version of the architecture and has not yet been fully migrated to the current state-model implementation. 

Some mechanistic relationships in these case studies remain expolratory modelling hypotheses and require further literature-based validation. 

The current SPAQRL queires demonstrate what can be retreived from the asserted model. [`sparql/README.md`](sparql/README.md)

---
## Architecture

```
Forest OS/
├── ontology/
│   ├── forestos_ontology_v2.rdf        ← OWL ontology (open in Protégé)
│   └── forestos_inferred_v2.rdf        ← Inferred axioms (import in GraphDB for SPARQL)
├── python/
│   └── forestos_state_model_v2.py      ← NamedGraph builder   
├── sparql/                             ← see sparql/README.md for full index
├── docs/
│   ├── state_model.md                  ← 4-state walkthrough + case studies
│   ├── key_architectural_decision.md   ← object Property/universal nodes design decision
│   └── deprecated_ideas.md             ← ideas removed from active scope, kept for reference
└── diagrams/                           ← png files for state_model.md

```

**Stack:** Protégé · OWL 2 DL · SWRL · SPARQL 1.1 · GraphDB · Python 3

---

## How to Read

### Prerequisites
- [Protégé](https://protege.stanford.edu/) (OWL 2 DL editor) — for viewing/editing the ontology
- [GraphDB](https://www.ontotext.com/products/graphdb/) (free edition is sufficient) — for SPARQL queries and the Python builder
- Python 3.x with `requests` installed (`pip install requests`) — only needed for the state graph builder script

### View the ontology
1. Download `ontology/forestos_ontology_v2.rdf`.
2. Open it in Protégé.

### Query via SPARQL
1. In GraphDB, create a new repository (any name).
2. Import `ontology/forestos_inferred_v2.rdf` into it.
3. Open each `.rq` file in `sparql/` and run it in GraphDB's SPARQL editor
   — one query at a time. See [`sparql/README.md`](sparql/README.md) for
   what each query answers before running.

### Run the state graph builder (Python)
1. Complete the SPARQL setup above (repository created, inferred RDF
   imported).
2. In `forestos_state_model_v2.py`, set `QUERY_ENDPOINT` and
   `UPDATE_ENDPOINT` to match your repository's URL.
3. Run the script. It rebuilds the four state named graphs
   (Homeostatic / Physiological / Pathological / Pharmacological) from
   the default graph — see
   [`docs/key_architectural_decision.md`](docs/key_architectural_decision.md) §2 for what
   it does and why.

---

## Background

Built by a 3rd year MPharm student (2026/27) at the University of Manchester
exploring biomedical knowledge architecture. The project started from a 
simple observation: biological cascades aren't flat lists of facts — there's 
real multi-dimensional structure underneath them, which node causes which, at what layer, resolved
or not. Forest OS is an attempt to actually draw that structure out and 
put it into a form a query can traverse.

SNOMED-CT Foundation Course completed (July 2026).

---

*Protégé · OWL 2 DL · SWRL · SPARQL 1.1 · GraphDB · Python 3*
