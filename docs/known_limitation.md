## Unresolved Tensions — UPDATED

| Tension | Status | Resolution Path |
|---|---|---|
| **Shared universal nodes lose disease context** | Active | Named Graphs (Month 2). One node, context in graph wrapper. |
| **has_pathophysiology is disease-specific but nodes are universal** | Pragmatic fix | Assert only to key anchor nodes. SPARQL traverses the rest. Named Graphs Month 2. |
| **Feedback loop dynamic resolution** | Deferred | Structurally encoded (SNS/RAAS → Ischaemia → SNS). ODE simulation resolves dynamics. SPARQL detects cycle topology. |
| **CDM competing inputs on same node** | Accepted architectural limit | OWL cannot resolve arithmetic net effects. Separate context-specific instances per scenario. ODE simulation layer resolves dynamics. |
| **SPARQL reads asserted triples only (no arithmetic)** | Accepted | Topology queries work. Dynamic resolution = Python/ODE layer. |
| **occursIn context encoding** | Temporary fix (data property) | Named Graphs Month 2 — context lives in graph, not in node. |
| **SWRL prefix inconsistency (forestos-SPARQL-3:)** | Cosmetic, known bug | SWRLTab display quirk. Functionally identical. Accept for now. |

---