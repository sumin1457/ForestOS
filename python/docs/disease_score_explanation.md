**Forest OS — Disease Score Model**

Reference: `python/forestos_disease_score.py`

This file narrates what the script demonstrates.

---

## 1. Purpose

Computes a structural disease staging profile for any mapped disease in Forest OS, derived entirely from ontology architecture — no external clinical scoring systems, no manually asserted severity values. Two dimensions are computed and combined into a single stage score.

---

## 2. Method

Queries GraphDB across two graph layers — the default graph (full ontology) and the location context named graphs (`context/Respiratory`, `context/Cardiovascular`) built by `forestos_disease_as_deviation_model.py`.

### Dimension 1 — Cascade Complexity

Counts intermediate cascade nodes traversed from the disease entry point (`has_etiology` / `triggers`) to each L1 infrastructure node, via the cascade property chain (`increases`, `inhibits`, `targets`, `modulates`). The L1 node must appear in the relevant location context graph, confirming tissue membership.

```sparql
:{disease} (:has_etiology|:triggers) ?entry .
?entry (:increases|:inhibits|:targets|:modulates)+ ?step .
?step  (:increases|:inhibits|:targets|:modulates)* ?l1node .
?l1class rdfs:subClassOf* :L1_Infrastructure .
GRAPH <{location}> { ?l1node ?anyProp ?anyObj . }
GROUP BY ?l1node
```

### Dimension 2 — Chronic Depth

Counts `progresses_to` transitions within the location context graph, from the first reachable L1 node to the terminal structural consequence. Uses `progresses_to` exclusively — the only property in the Forest OS RBox that explicitly encodes a time axis.

```sparql
?entry (:increases|:inhibits|:targets|:modulates)* ?viaAcute .
GRAPH <{location}> {
    FILTER EXISTS { ?viaAcute :progresses_to+ ?any . }
    ?viaAcute :progresses_to+ ?mid .
    ?mid :progresses_to* ?node .
}
GROUP BY ?node
```

### Stage Score

```
stage_score = max_cascade_complexity + max_chronic_depth
```

---

## 3. Results

| Disease | Cascade Complexity | Chronic Depth | Stage Score |
|---|---|---|---|
| Asthma | 8 | 2 | 10 |
| MI | 6 | 2 | 8 |

**Asthma acute nodes:**
- Epithelial_Damage_respiratory → complexity 4
- Bronchoconstriction → complexity 8

**Asthma chronic nodes:**
- Chronic_Inflammation_respiratory → stage 1
- Airway_Remodelling → stage 2

**MI acute nodes:**
- Ischaemia_endocardium → complexity 3
- BloodClot_cardiovascular → complexity 6

**MI chronic nodes:**
- Ischaemia_endocardium → stage 1
- Necrosis_heart → stage 2

---

## 4. Clinical Interpretation

MI reaches critical tissue damage at lower cascade complexity than Asthma (depth 3 vs 8 for the primary acute node) — fewer upstream nodes required before tissue-level damage occurs. Consistent with MI's character as a more acutely dangerous event with a smaller therapeutic window.

Both diseases show chronic depth of 2 — two time-dependent structural transitions between initial tissue damage and terminal consequence. The terminal nodes differ fundamentally in reversibility: Airway_Remodelling (Asthma) is partially reversible with sustained treatment, while Necrosis_heart (MI) is irreversible. The chronic depth score is equal, but the biological meaning is not — a limitation of the current structural scoring approach, addressed below.

---

## 5. Known Limitations

**Cascade complexity is model-dependent.**
Reflects ABox modelling density, not inherent biological speed of onset. Nodes were deliberately collapsed during mapping to prevent instance explosion, particularly at L2/L3 where intermediate signalling steps were condensed. A more granular model of the same disease produces higher complexity scores; a more collapsed model produces lower scores. Cross-disease comparison is valid only when diseases are modelled at consistent granularity — not yet guaranteed.

**Cascade complexity does not represent clinical severity.**
The score measures structural participation — how many cascade nodes are traversed before tissue damage occurs — not biological speed, clinical urgency, or therapeutic window size. These require either explicit severity data properties (`hasSeverityScore`, `hasOnsetSpeed`) sourced from literature, or ODE-derived activation peaks once rate constants are grounded in the ontology via `CascadeEdge` individuals.

**Chronic depth does not capture reversibility.**
Two diseases can show identical chronic depth while differing fundamentally in whether the terminal consequence is reversible. Airway_Remodelling and Necrosis_heart both sit at chronic stage 2 in the current model. A reversibility dimension — assertable as a data property on L1 nodes — would resolve this and is noted as future work.

**Stage score uses addition, not multiplication.**
`max_cascade_complexity + max_chronic_depth` maintains a linear, interpretable scale where each unit represents one additional cascade step. Multiplicative scoring would amplify differences non-linearly and isn't currently justified given the model-dependent nature of cascade complexity.

---

## 6. Proposed Path to Genuine Severity Scoring

Three approaches planned for future versions, in order of rigor:

1. **ODE-derived severity** — once rate constants are grounded in `CascadeEdge` individuals in Protégé, peak activation level and time-to-peak for each L1 node can be computed from the ODE simulation. A node reaching high activation rapidly has genuinely high acute severity. Derives severity from biological dynamics rather than graph structure — the most rigorous approach available.

2. **Explicit severity assertions** — `hasSeverityScore` and `hasOnsetSpeed` data properties on L1 nodes, sourced from literature and stored as auditable ontology assertions, consistent with the `CascadeEdge` rate constant pattern already planned.

3. **TBox-derived disruption classification** — the existing `Acute_Functional_Disruption` / `Chronic_Structural_Disruption` class hierarchy encodes a coarse severity axis already, and is immediately queryable without new assertions. Nearest-term addition to the stage score output.

---

## 7. Generalisation

The function accepts any disease instance and location context graph. When new diseases are mapped in Protégé and the context graphs are rebuilt by `forestos_disease_as_deviation_model.py`, the stage score function requires no modification — it derives all dimensions dynamically from ontology structure at query time.
