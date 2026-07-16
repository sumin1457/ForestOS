## Unresolved Tensions — UPDATED

| Tension | Status | Resolution Path |
|---|---|---|
| **Shared universal nodes lose disease context** | **Resolved** |  Named Graphs implemented (`namedgraph/forestos_disease_as_deviation_model.py`). Node stays singular in default graph; location-specific edges live in `context/*` named graphs. See `docs/forestos_disease_as_deviation_model_explanation.md`. |
| **has_pathophysiology is disease-specific but nodes are universal** | **Resolved** |  Same Named Graph architecture — key anchor nodes stay in default graph, SPARQL traverses the rest, location-specific edges partitioned by context. |
| **Feedback loop dynamic resolution** | Deferred | Structurally encoded (SNS/RAAS → Ischaemia → SNS). ODE simulation resolves dynamics. SPARQL detects cycle topology. |
| **CDM competing inputs on same node** | Accepted architectural limit | OWL cannot resolve arithmetic net effects. Separate context-specific instances per scenario. ODE simulation layer resolves dynamics. |
| **SPARQL reads asserted triples only (no arithmetic)** | Accepted | Topology queries work. Dynamic resolution = Python/ODE layer. |
| **occursIn context encoding** |**Resolved** | Named Graphs — `occursIn` now feeds graph classification directly (Type B nodes), context lives in the graph itself, not just as a dangling data property. |
| **SWRL prefix inconsistency (forestos-SPARQL-3:)** | Cosmetic, known bug | SWRLTab display quirk. Functionally identical. Accept for now. |
| **Cascade complexity confounded with modelling granularity** | Active | `forestos_disease_score.py` Stage Score reflects ABox decomposition density, not clinical severity. Not cross-disease comparable until either a fixed atomic decomposition rule is applied, or score is normalized against total cascade node count. See `docs/disease_score_explanation.md` §5–6. |

---
