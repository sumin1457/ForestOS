# SPARQL Query Results — Forest OS Ontology

Reference: `v1.0-mi-complete` tag (MI + Asthma mapped, SWRL removed, mechanistic/functional drug properties asserted)

This file narrates what each query in `SPARQL/results/` demonstrates. Raw CSV output for each query sits alongside the corresponding `.rq` file for anyone who wants to verify or re-run against `forestos-ontology.rdf` directly.

---

## 1. Cross-Disease Pathophysiology

### `pathophysiology_asthma_mi.csv` — Union of all nodes
Full inventory of etiology/pathophysiology nodes across both MI and Asthma cascades (29 nodes total). This is a completeness check — confirms both disease chains are fully populated in the ontology — rather than a comorbidity signal, since most nodes here are disease-specific.

### `pathophysiology_shared_nodes_mi_asthma.csv` — Intersection
Of the 29 nodes above, only **`Shortness_of_Breath`** and **`Chest_Pain`** are reachable from *both* MI's and Asthma's etiology/pathophysiology chains. These sit at genuine structural convergence points between the two diseases — not just shared symptom vocabulary, but nodes actually derivable from both disease origins via the ontology's property chains.

**Known limitation:** this count is almost certainly an undercount of real physiological overlap. MI and Asthma likely share more mechanistic ground (e.g. autonomic and inflammatory crosstalk), but Protégé's OWL/individual modeling doesn't currently offer a clean way to represent a single physiological node as *simultaneously* shared infrastructure across disease-specific subgraphs — without either duplicating the node per-disease or losing disease-specific context on it.

This is being treated as a modeling gap to solve at the **GraphDB/graph layer**, not the OWL layer: the goal is to differentiate a "universal" physiological node from its disease-contextualized instances using graph structure, rather than forcing that distinction into the OWL class hierarchy. This maps directly onto the Forest OS v2 direction — a node like `Shortness_of_Breath` should arguably be one neutral physiological process with disease-specific triggers pointing into it, rather than duplicate per-disease instances that happen to share a name.

---

## 2. Drug → Target Queries

### `mi_drug_mechanistic_target.csv`
First-pass drug-target lookup scoped to MI only. Confirms each MI drug class (Statin, Antiplatelet, ACEi, Beta_Blocker) resolves to exactly one upstream mechanistic node via `perturbs_mechanistically`. Baseline sanity check before generalising the query across both diseases.

### `drug_layer_mechanistic_target.csv`
Drug → pathophysiology layer → mechanistic target, across both diseases. Shows which of the four layers (Genetic / Immune / Hormonal-Biochemical / Infrastructure) each drug intervenes at — e.g. Corticosteroid and Omalizumab act at layer 3 (immune), while ACEi, Antiplatelet, and Beta_Blocker act at layer 2. Operationalises the 4-layer pathophysiology model as a queryable structure rather than a diagram.

### `drug_layer_clinical_goal.csv`
Drug → layer → clinical goal, skipping the mechanistic intermediate. Same layer classification as above, resolved straight to the clinical endpoint (e.g. `Ischaemia_endocardium`, `Airway_Remodelling_asthma`). The "what is this drug *for*, clinically" view, layer-tagged.

### `drug_mechanistic_target_clinical_goal.csv`
**The key query.** For each drug, shows both what it hits mechanistically (`mechanisticTarget`) and what clinical effect that produces (`clinicalGoal`) — e.g. Corticosteroid → MastCell → `Airway_Remodelling_asthma` *and* → `Chronic_Inflammation_asthma` (one mechanism, two clinical consequences). This operationalises the `perturbs_mechanistically` / `perturbs_functionally` property split: the same biological target can map to multiple downstream clinical outcomes, which is the formal basis for representing side effects and off-target consequences (e.g. Beta-Blocker's cardiac benefit vs respiratory risk).

### `drug_layer_mechanistic_target_clinical_goal.csv`
Full combined view — drug, layer, mechanistic target, and clinical goal in a single table. The most information-dense artifact of the set; the queries above can be read as decompositions of this one.

---

## Summary

| Query | Rows | Purpose |
|---|---|---|
| `pathophysiology_asthma_mi.csv` | 29 | Union — completeness check |
| `pathophysiology_shared_nodes_mi_asthma.csv` | 2 | Intersection — comorbidity signal |
| `mi_drug_mechanistic_target.csv` | 4 | MI-only baseline |
| `drug_layer_mechanistic_target.csv` | 9 | Drug → layer → mechanism |
| `drug_layer_clinical_goal.csv` | 11 | Drug → layer → clinical goal |
| `drug_mechanistic_target_clinical_goal.csv` | 13 | Mechanism → clinical outcome bridge |
| `drug_layer_mechanistic_target_clinical_goal.csv` | 13 | Full combined view |

**Open question carried into v2:** how to represent physiologically universal nodes (shared across disease contexts) without duplicating them per-disease — see limitation note under §1. Candidate approach: model shared nodes as GraphDB-level graph structure rather than OWL individuals, deferring disease-context differentiation to the query layer.
