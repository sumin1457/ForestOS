# Forest OS
### A Biomedical Knowledge Architecture for Disease-as-Deviation Modelling

Built in OWL/Protégé. Queried via SPARQL. Simulated with Python for named graphs.

---

## What This Is

Forest OS models disease as **location-specific deviation from a universal
homeostatic baseline** — not as a catalogue of pathological nodes, but as a
formal representation of where, how, and why healthy biological machinery
goes wrong.

The deviation map doesn't add new biology. It corrupts existing biology —
in specific ways, at specific nodes — that drugs then target.

Full walkthrough of the state model, with a worked case study
(Hypercholesterolaemia), lives in [`docs/state_model.md`](docs/state_model.md).

---

## Conceptual Framework

The ontology separates five ontological modes — not as five independent
categories, but as five relational roles around a single biomedical layer:

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
named graphs, the drug taxonomy — is an instantiation of this skeleton.

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
| L1.5 — Enzyme | ACE, COX, HMG-CoA | Protein-level |
| L1.5 — Receptor | AT1, H1, LDL, Muscarinic | Reacts to molecular signal |

Drug intervention depth is computed from layer of action. A drug acting at
L3 suppresses more downstream nodes and is structurally closer to the
disease root than one acting at L1 — this is computed directly by
[`sparql/drug_layer_depth.sparql`](sparql/README.md#drug_layer_depth.sparql),
not asserted by hand.

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
  bigger disturbance. The defining feature is not signal size but that the
  correction pathway still successfully closes the loop.

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

Homeostatic graph:    Nodes with hasSystemState: "Homeostatic" entry + AUTO
                       full downstream cascade edges + data property preserved.

Physiological graph:  Nodes with hasSystemState: "Physiological" entry + AUTO
                       full downstream cascade edges + restores/balances edges
                       (resolution branch) + data property assertion.

Pathological graph:   Nodes with hasSystemState: "Pathological" entry +
                       mimics/deviates_into (signal hijacking + transition) +
                       AUTO-traverses full downstream from deviates_into
                       targets + data property assertion.
```

A single SPARQL query can enter through a disease context graph, traverse
universal biology in the default graph, and terminate in a
location-specific consequence — without duplicating a single node.

Adding a new disease means adding its entry point. Existing location
contexts are inherited automatically.

---

## State Graph Builder: Hypercholesterolaemia as a Case Study

Hypercholesterolaemia is not the body malfunctioning at random — it's the
cholesterol-sensing loop (SCAP/SREBP-2) being fed a false signal (ROS-driven
Oxysterol) that overrides a correctly-sensed low-cholesterol state, with no
endogenous path back.

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

## Architecture

```
Forest OS/
├── ontology/
│   ├── forestos_ontology_v2.rdf        ← OWL ontology (open in Protégé)
│   └── forestos_inferred_v2.rdf        ← Inferred axioms (import in GraphDB for SPARQL)
├── python/
│   ├── forestos_state_graph_builder.py
│   ├── forestos_clinical_timeline.py
│   └── forestos_disease_score.py
├── sparql/                             ← see sparql/README.md for full index
├── docs/
│   ├── state_model.md                  ← 4-state walkthrough + case studies
│   ├── architecture.md
│   ├── key_findings.md
│   ├── known_limitations.md
│   └── deprecated_ideas.md             ← ideas removed from active scope, kept for reference
└── diagrams/
│   ├── hypercholesterolaemia_state0_homeostatic.png
│   ├── hypercholesterolaemia_state1_physiological.png
│   ├── hypercholesterolaemia_state2_pathological.png
│   └── hypercholesterolaemia_state3_pharmacological.png
```

**Stack:** Protégé · OWL 2 DL · SWRL · SPARQL 1.1 · GraphDB · Python 3

---

## Current Coverage

- **2 diseases mapped:** Myocardial Infarction, Hypercholesterolaemia (primary, most complete)
- **Cross-disease SPARQL querying validated**

**NOTE** Asthma: mapped under V1 architecture. Drug-perturbation and 
  symptom-traversal queries work identically (proving those query 
  patterns generalize across versions). Not yet migrated to V2's 
  hasSystemState/named-graph model — asthma's immune cascade doesn't 
  cleanly decompose into Homeostatic/Physiological/Pathological the 
  same way metabolic/cardiac feedback loops do, and resolving that 
  mismatch is next on the roadmap.

---

## Roadmap

```
Now:        Four states update
            Homeostatic baseline layer (cortisol, SNS/PSNS, COX balance)
            SPARQL folder documentation

Later:      L4 Genetic layer deepened (FLG gene → Filaggrin protein →
            Skin Barrier Integrity — Gene Ontology alignment)
            BFO alignment
            Literature-grounded rate constants reification (ChEMBL, primary papers)
```

---

## Background

Built by a 3rd year MPharm student (2026/27) at the University of
Manchester exploring biomedical knowledge architecture. The project began
from a specific conviction: biological cascades are not linear lists of
facts, they have real semantic structure — which node causes which, at
what layer, resolved or not — and that structure should be representable
formally, not just described in prose. Forest OS is an attempt to
translate pathophysiology into something a query can actually traverse.

SNOMED-CT Foundation Course completed (July 2026).

---

*Protégé · OWL 2 DL · SWRL · SPARQL 1.1 · GraphDB · Python 3*
