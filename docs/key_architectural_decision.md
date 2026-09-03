## Key Architectural Decisions — v2

| Decision | Reasoning |
|---|---|
| **State graph membership is asserted, not inferred** | A node belongs to a state graph if `hasSystemState "X"` is asserted directly. No downstream traversal. |
| **Edges are source-anchored** | An edge belongs to graph X if its *source* node is tagged X, regardless of the target's tag status. Chosen over both-endpoints-required (too strict — disconnects neutral nodes like SCAP) and either-endpoint (too loose — duplicates edges into states they don't structurally belong to). |
| **Self-describing predicates bypass hasSystemState** | `resolves_to` (State 3), `balances_to`/`restores` (State 1), `deviates_into`/`mimics` (State 2) are unambiguous by predicate alone — asserted directly into their graph, no tag check needed.|
| **intervenesAtLayerScore removed** | Replaced by SPARQL `rdfs:subClassOf*` traversal from `perturbs_mechanistically` target (`drug_layer_depth.sparql`). Structure derives the score — no manual assertion. |
| **perturbs_mechanistically vs therapeutic_intent** | Mechanism (`agonises_receptor`/`antagonises_receptor`/`upregulates`/`downregulates`) and clinical intent (`therapeutic_activation`/`therapeutic_suppression`) are asserted as independent properties, not collapsed into one label. A drug can mechanistically antagonise an inhibitory target to achieve a net activating intent — keeping them separate lets the ontology represent that gap. |
| **Named graphs are filtered views over one default graph** | The default graph holds every asserted node and edge, untyped by state. The four state graphs (Homeostatic / Physiological / Pathological / Pharmacological) are built from it, not maintained as a separate source of truth. Rebuilding from the default graph after every Protégé export is the intended workflow (`rebuild_state_graphs()`). |
| **Pharmacological graph added as a 4th state** | v1 only materialised Homeostatic/Physiological/Pathological as named graphs; drug reasoning worked only by querying `resolves_to` directly against the default graph. v2 gives State 3 the same named-graph convenience as the others. |
| **Disease Stage Score paused, not deleted** | Cascade complexity metric was confounded with modelling granularity (ABox decomposition density, not clinical severity) rather than a property of the disease itself. Moved to `docs/deprecated_ideas.md` pending an ODE-derived successor. |

---

## Major Findings — Hypercholesterolaemia Update

### The universal-node problem: same Tbox class, divergent-point instances

The v1 tension "shared universal nodes lose disease context" (see
`docs/archive/v1_notes.md`) is resolved not by full named-graph separation
of every instance, but selectively: a node stays under one Tbox class, and
multiple *instances* of that class exist, each tagged with a different
`hasSystemState` — but only at nodes that are genuine divergence points or
structurally pivotal for what happens next. Most of the cascade doesn't
need this; only the nodes where physiological and pathological paths
actually diverge do.

This is deliberately not blanket-applied. Duplicating every node per state
would recreate the eczema/asthma over-duplication problem the architecture
is trying to avoid. The instance split is
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

`physio_vs_patho_divergence.rq`'s LX_Receptor result (below) is the first
concrete case of this pattern doing real work, not just a one-off query.

---
