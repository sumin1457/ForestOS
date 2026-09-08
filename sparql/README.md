# SPARQL Queries

Each query runs against `forestos-ontology-3`. All traverse the
same core predicates (`System_Event_Logic`, `Genetic_Logic`, `resolves_to`,
`deviates_into`, `switches_on`, `switches_off`, `balances_to`) but ask
different structural questions of the graph. Run order doesn't matter —
each is independent.

---

## drug_layer_depth.rq
**Question:** For every drug, what target does it perturb, what biological
layer (L1–L4) does that target sit in, and how many downstream nodes does
that intervention eliminate?

**Why it matters:** Turns "layer of action" from a label into a computed
depth score — a drug acting at L3 provably clears more downstream nodes
than one acting at L1, rather than this being asserted by hand.

**Reads:** `Drug_Intervention` --`perturbs_mechanistically`--> target --
(`System_Event_Logic`|`Genetic_Logic`|`resolves_to`)*--> downstream, grouped
by drug/target/layer, counted, ordered by eliminated nodes descending.

**Result shape:** `drug | target | layer | eliminatedNodes`

| Drug | Target | Layer | Eliminated Nodes |
|---|---|---|---|
| ACEi | ACE | 1.5 | 10 |
| Corticosteroid | Th2 | 3 | 9 |
| Omalizumab | IgE_Signalling | 3 | 6 |
| Corticosteroid | MastCell | 3 | 5 |
| Aspirin | COX1_Platelet | 1.5 | 3 |
| Statin | HMGCR_pharmacological | 1.5 | 3 |
| Bisoprolol | Beta1_Receptor_Cardiovascular | 1.5 | 2 |
| Propanolol | Beta1_Receptor_Cardiovascular | 1.5 | 2 |
| Propanolol | Beta2_Receptor_Respiratory | 1.5 | 2 |
| SABA | Beta2_Receptor_Respiratory | 1.5 | 2 |
| LTRA | Leukotriene_asthma | 2 | 2 |

---

## drug_resolution_chain.rq
**Question:** Starting from a single named drug (e.g. Statin), what is the
full chain of effects it triggers, including secondary effects one step
beyond the immediate resolution?

**Why it matters:** Validates that a drug's mechanism, as modelled, actually
closes a traceable loop back through the ontology rather than terminating
at an isolated node.

**Reads:** `Statin_instance` --`perturbs_mechanistically`--> target --
`resolves_to`+ --> drugEffect --(state-change predicates)*--> mid --
`resolves_to`+--> secondaryEffect.

**Result shape:** `drugEffect | secondaryEffect`

| Drug Effect | Secondary Effect |
|---|---|
| Cholesterol_ER_pharmacological | Oxysterol_Low |
| Cholesterol_ER_pharmacological | Cholesterol_ER_pharmacological |
| Cholesterol_ER_pharmacological | LDL_pharmacological |

**NOTES**: Second row (repeated cholesterol) shows a closed feedback. 

---

## pathological_resolution_status.rq
**Question:** For a given disease, which pathological entry-point nodes
have no pharmacological resolution anywhere downstream?

**Why it matters:** Surfaces etiology the current drug taxonomy doesn't
reach — a gap map of the model, not just a traversal. Distinguishes
"resolved by an existing drug class" from "structurally still open."

**Reads:** `Hypercholesterolaemia_instance` --`has_etiology`--> entry --
(`System_Event_Logic`|`Genetic_Logic`|`deviates_into`|`switches_on`|
`switches_off`)* --> probNode, checked for a `hasSystemState
"Pathological"` node, then optionally matched against a downstream node
with `hasSystemState "Pharmacological"`.

**Result shape:** `probNode | class | resolvingNode | clearState`
(`clearState` is `"Pharmacologically Resolved"` or `"Unresolved"`)

| Problem Node | Class | Resolving Node | Clear State |
|---|---|---|---|
| SFA_pathological | Saturated_Fatty_Acid | | Unresolved |
| ROS_Oxysterol | Reactive_Oxygen_Species | | Unresolved |
| Oxysterol_Deviated | Oxysterol | Oxysterol_Low | Pharmacologically Resolved |
| LDL_Deviated | LDL | LDL_pharmacological | Pharmacologically Resolved |
| LX_Receptor_pathological | Liver_X_Receptor | | Unresolved |
| VLDL_Deviated | VLDL | | Unresolved |

---

## physiological_self_resolution.rq
**Question:** Starting from a physiological (State 1) trigger, does the
endogenous system resolve back to baseline without external intervention,
and what secondary effects does that resolution produce?

**Why it matters:** Confirms State 1's defining property — the loop closes
on its own — is actually true of the asserted graph, not just true in the
text description.

**Reads:** `Saturated_Fatty_Acid` with `hasConcentrationState "High"` --
(`System_Event_Logic`|`Genetic_Logic`)* --> physioEffect -- `balances_to` -->
resolveEffect --(System_Event_Logic)+ --> mid2 -- `balances_to` -->
secondaryEffect. Filtered to nodes with `hasSystemState "Physiological"`.

**Result shape:** `physioEffect | resolveEffect | secondaryEffect`

| Physio Effect | Resolve Effect | Secondary Effect |
|---|---|---|
| VLDL_SFA | | |
| Cholesterol_ER_physiological | | |
| LDL_SFA | | |
| Oxysterol_High | | |
| LX_Receptor_physiological | SFA_Low | LDL_Low |

---

## physio_vs_patho_divergence.rq
**Question:** For the same node class (e.g. LX_Receptor), does the
physiological-state instance resolve (`balances_to` something) while the
pathological-state instance of that same class does not?

**Why it matters:** This is the formal argument for *why* State 2 counts
as pathological rather than a label choice — the resolution machinery
demonstrably exists (proven by the State 1 instance resolving) but is
unreachable from the State 2 entry point. Same class, divergent outcome.

**Reads:** Matches a `Physiological`-state and a `Pathological`-state
instance of the same `rdf:type` (most specific subclass only, via
`FILTER NOT EXISTS` on subclasses), then checks whether the physiological
instance has an outgoing `balances_to` edge.

**Result shape:** `physiomid | clearPoint | pathomid`
(`clearPoint` = `"Clear"` if the physiological instance resolves)

| Physio Mid | Clear Point | Patho Mid |
|---|---|---|
| VLDL_SFA | | VLDL_Deviated |
| LDL_SFA | | LDL_Deviated |
| Oxysterol_High | | Oxysterol_Deviated |
| LX_Receptor_physiological | Clear | LX_Receptor_pathological |

---

### Note on results worth flagging
The `physio_vs_patho_divergence` query currently returns a positive case for
`LX_Receptor`: the physiological instance clears (`"Clear"`), the
pathological instance of the same class does not. This is a concrete,
queryable instance of the model's core claim — see [`docs/key_architectural_decision.md`](docs/key_architectural_decision.md).
