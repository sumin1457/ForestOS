# Forest OS
### A Biomedical Knowledge Architecture for Disease-as-Deviation Modelling

Built in OWL/Protégé. Queried via SPARQL. Named graphs built and queried via Python + GraphDB.

---

## What This Is

Forest OS models disease as **location-specific deviation from a universal
homeostatic baseline**. Rather than listing pathological facts of disease, 
ForestOS aims to translate dynamic biological physiology into queryable structure
— where a disease's mechanism can be traced and compared against the healthy
machinery it deviates from. 

**Two companion docs go deeper**: [`docs/state_model.md`](docs/state_model.md) 
works through the four-state model on a real case study, with diagrams and 
SPARQL-verified results. [`docs/key_architectural_decision.md`](docs/key_architectural_decision.md) explains the predicate design and named-graph mechanics that make the model queryable — including how the ontology handles a universal biological process needing to behave differently across disease states.

---

## Conceptual Framework

The ontology separates five ontological modes as five relational roles around a single biomedical layer:

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

Everything else in this document — the four layers, the four states, the
named graphs, the drug taxonomy — is based on this skeleton.

---

## Four-Layer Biological Model

Every biological node (from `Biomedical_Layer`) is classified into one of
four layers:

| Layer | Domain | Role |
|---|---|---|
| L4 — Genetic | Predispositions, mutations, epigenetic state | Starting conditions |
| L3 — Immune | Th2, IgE signalling, dendritic cell activity | Regulatory immune machinery |
| L2 — Biochemical | Histamine, prostaglandins, cAMP, NO, PGI2 | Molecular mediators |
| L1 — Infrastructure | Bronchoconstriction, ischaemia, atherosclerosis | Tissue-level consequence |


Extra Layers:
| Layer | Domain | Role |
|---|---|---|
| L1.5 — Enzyme | ACE, COX, HMG-CoA | Protein-level |
| L1.5 — Receptor | AT1, H1, LDL, Muscarinic | Reacts to molecular signal |

Drug intervention depth is computed from layer of action. A drug acting at
L3 suppresses more downstream nodes and is structurally closer to the
disease root than one acting at L1 — this is computed directly by
[`sparql/drug_layer_depth.rq`](sparql/drug_layer_depth.rq).

---

## The Four States

Four states underlie the entire system. States 0 and 1 both describe the
**healthy body** — the same organism, doing what it's built to do, whether
resting or responding to a real stimulus. State 2 is the only state where
something has actually gone wrong. State 3 shows how a drug resolves the
State 2 deviation.

```
State 0 — Homeostatic (Negative Feedback, Loop Closed)
  A Regulatory_Switch has deviated from its setpoint, a Sensor has detected
  it, and the resulting Effector response is actively correcting it back to
  baseline. Ordinary, continuous self-correction. Regulatory machinery is
  engaged and succeeding.

State 1 — Physiological (Emergency Signal, Loop Still Closes)
  A larger-magnitude or acute trigger arrives — still using the same
  Sensor–Switch–Effector architecture as State 0, just responding to a
  bigger disturbance. The correction pathway still successfully closes the loop.

State 2 — Pathological (Loop Blocked)
  The same architecture is engaged, but the loop fails to close, via one
  of two structural mechanisms:
    False trigger  → a competing signal overrides the correct one
    Broken brake   → chronic suppression of a regulatory node prevents
                      the correction from ever engaging
  No resolution loop. The switch stays deviated indefinitely.

State 3 — Pharmacological (Loop Closed by External Intervention)
  The endogenous loop remains blocked (State 2's cause is still present),
  but an external agent closes the loop by a different route — typically
  bypassing the blocked step rather than repairing it.
```

Worked example for all four states (Hypercholesterolaemia), with diagrams
and SPARQL-verified results: [`docs/state_model.md`](docs/state_model.md).

---

## Named Graph Architecture

```
Default graph:        complete ontology (Protégé export) — Biomedical layer,
                       clinical framing, clinical manifestation (symptoms),
                       therapeutic perturbation (drugs). All nodes, all
                       asserted edges.

Homeostatic graph:    Nodes with hasSystemState: "Homeostatic" entry +
                      data property preserved.

Physiological graph:  Nodes with hasSystemState: "Physiological" entry +
                      restores/balances_to/balances edges (resolution branch) +
                      data property assertion.

Pathological graph:   Nodes with hasSystemState: "Pathological" entry +
                       mimics/deviates_into (signal hijacking + transition) +
                      data property assertion.

Pharmacological graph: Nodes with hasSystemState: "Pharmacological" entry +
                       resolves_to edge + data property assertion.

```

Python script for Named graph is in [`python/forestos_state_model_v2.py`](python/forestos_state_model_v2.py), 
explanation available in [`python/docs/forestos_state_model_design.md`](python/docs/forestos_state_model_design.md).

---

## State Graph Builder: Hypercholesterolaemia as a Case Study

Hypercholesterolaemia is not the body malfunctioning at random — it's the
cholesterol-sensing loop (SCAP/SREBP-2) being fed a false signal (ROS-driven
Oxysterol) that overrides a correctly-sensed low-cholesterol state.

```
HEALTHY RESPONSE (State 0/1):
  Cholesterol_ER drops → SCAP/SREBP-2 activate → LDLR transcription rises
  → LDL cleared → Cholesterol_ER restored.
  Acute SFA surge → Oxysterol rises → SREBP-2 transiently shut down → SFA
  cleared via LXR → Oxysterol falls → SREBP-2 reactivates → LDL cleared.
  Two-phase, but resolves.

PATHOLOGICAL DEVIATION (State 2):
  Chronic high SFA → ROS-driven Oxysterol → overrides SREBP-2 regardless
  of the correctly-sensed low-cholesterol signal, and LXR's balancing
  response no longer clears it → no endogenous path back.

PHARMACOLOGICAL CLOSURE (State 3):
  Statin inhibits HMG-CoA Reductase directly, depleting the cholesterol
  pool that feeds Oxysterol → SREBP-2 reactivates → LDL clears, without
  ROS or SFA ever being addressed. The drug closes the LDL loop; the root
  cause remains open.
```

Full diagrams and the SPARQL queries that verify this (including where the
model shows the same node class resolving in State 1 but not State 2) are
in [`docs/state_model.md`](docs/state_model.md).


MI remains mapped as the earlier reference case and is included there for
comparison.

---

## Pharmacological Property Hierarchy

Drug action is modelled at two levels: mechanism (what happens at the
target) and intent (why it's being done, clinically).

```
perturbs_mechanistically      — the physical/molecular action on a target
├── agonises_receptor          — binds and activates a receptor
├── antagonises_receptor       — binds and blocks a receptor
├── downregulates               — reduces expression/activity of a target
└── upregulates                 — increases expression/activity of a target

therapeutic_intent             — the clinical direction of that action
├── therapeutic_activation      — intent is to increase a pathway/output
└── therapeutic_suppression     — intent is to decrease a pathway/output
```

Why both are needed separately: mechanism and intent answer different questions — mechanism is what the drug physically does at the target; intent is the clinical goal that mechanism is being used to achieve. Keeping mechanism and intent as independent properties lets the ontology represent the means and the goal separately. 

Full predicate taxonomy and the reasoning behind every top-level branch: [`docs/key_architectural_decision.md`](docs/key_architectural_decision.md)

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

## Current Coverage

- **2 diseases mapped:** 2 diseases mapped under the current architecture (V2); a third (Asthma) under migration from V1 — see note below.
- **SPARQL query validated** [`sparql/README.md`](sparql/README.md)

**NOTE** 

- Asthma: mapped under V1 architecture. Drug-perturbation and 
  symptom-traversal queries work identically (proving those query 
  patterns generalize across versions). Not yet migrated to V2's 
  hasSystemState/named-graph model — asthma's immune cascade doesn't 
  cleanly decompose into Homeostatic/Physiological/Pathological the 
  same way metabolic/cardiac feedback loops do, and resolving that 
  mismatch is next on the roadmap.

- The Python named-graph builder was developed with AI assistance; the ontology design, predicate taxonomy, and state-model architecture are independently authored.

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

## Roadmap

```
Now:        Four states update
            SPARQL query
            NamedGraph architecture solving universal nodes problem

Longer-term: BFO alignment is a directions I'm exploring, not committed next steps

```

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
