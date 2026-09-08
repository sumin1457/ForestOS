# State Graph Builder — Design Decisions (v2)

This document explains why `forestos_state_model_v2.py` builds state graphs
differently from `v1_3`, and what the new rule trades away. The script's
docstrings say *what* each function does; this file is for the *why*,
so the reasoning doesn't get silently reverted by a future edit that
re-introduces the problem v2 was written to fix.

---

## Why v1_3 was replaced

v1_3 found each state's root nodes via `hasSystemState`, then traversed
**downstream** through generic predicates (`causes`, `binds`, `modulates`,
etc.) to pull in everything reachable from those roots:

```
?root (:causes|:binds|:modulates|...)+ ?downstreamNode .
```

This works as long as every path from a root stays inside that root's own
state. It breaks the moment a path crosses a **neutral node** — a node with
no `hasSystemState` of its own that sits between two different states'
territory. `System_Event_Logic` nodes and feedback edges (the edges an
Effector uses to feed back into a Regulatory_Switch) are exactly this kind
of neutral scaffolding: they're shared machinery, not state-specific, but
downstream traversal doesn't know that — it just follows the edge and pulls
whatever it finds into whichever graph is currently being built.

Concretely: if a Pathological root's downstream traversal passes through a
neutral node that also happens to feed into a Homeostatic node's territory,
that Homeostatic node's edges get pulled into the Pathological graph too.
The traversal has no way to stop at the state boundary, because the state
boundary isn't marked on the neutral node — it's only marked on the nodes
at either end.

## The membership rule (v2)

**State graph membership is asserted, not inferred.** A node belongs to
graph X if and only if it has `hasSystemState "X"` asserted directly.
No multi-hop traversal happens at all — this removes the failure mode
above entirely, because there's no path for an edge to "leak" through.

Edges are assigned using a **source-anchored** rule: an edge goes into
graph X if its *source* node is tagged `hasSystemState "X"`, regardless of
whether the target is tagged or untagged. Three options were considered:

| Rule | Description | Risk |
|---|---|---|
| Both-endpoints-required | Edge included only if source *and* target are both tagged X | Safest, but loses real edges through untagged neutral nodes (e.g. SCAP) — graph becomes disconnected |
| **Source-anchored (chosen)** | Edge included if source is tagged X; target's tag status doesn't matter | Neutral nodes appear as targets in multiple graphs but never as sources anywhere — acceptable, since they're meant to be shared scaffolding |
| Either-endpoint | Edge included if source *or* target is tagged X | Most permissive — an edge between a State-1 node and a State-2 node would get duplicated into both graphs, misrepresenting either as belonging structurally to the other |

Source-anchored was chosen because it matches how the ontology is actually
authored: a `hasSystemState` tag describes what a node *is*, not what it's
connected to, so it's the source of an assertion that should determine
which graph the assertion belongs to. Neutral nodes (SCAP, Insig, and
similar) are expected to show up as targets across several state graphs
without themselves belonging to any one state — this is intentional, not
a gap. The default graph remains the complete, untyped record of every
node and edge; the state graphs are filtered views over it.

## Predicate table: self-describing 

Some predicates introduced with the Hypercholesterolaemia update are
**self-describing** — the predicate itself only ever appears in one state,
so it can be asserted into its graph directly, with no `hasSystemState`
check needed at all:

| Predicate | Graph | Why unambiguous |
|---|---|---|
| `balances_to`, `restores` | Physiological | Only used for the State 1 recovery/resolution branch |
| `deviates_into`, `mimics` | Pathological | Only used for the false-trigger / state-transition mechanism that defines State 2 |
| `resolves_to` | Pharmacological | Only used to describe a drug closing a blocked loop — State 3 by definition |

## What this trades away

- **No downstream traversal** means a node several hops from a tagged root,
  with no `hasSystemState` of its own and reached only through generic
  predicates, will not appear as a *source* in any state graph — only as a
  target, if something tagged points to it. If a future case study needs
  deep multi-hop cascades to be fully queryable within a single named
  graph rather than via `hasSystemState` filters in SPARQL, this rule will
  need revisiting.
- **Pass 2 (the data property sweep)** is still required and unchanged from
  v1_3 — it's what allows untagged nodes reached as edge targets (NO,
  PGI2, CD39, SCAP) to carry their `occursIn`/`hasRateState`/etc. properties
  into the graph, since the source-anchored rule alone wouldn't otherwise
  populate their data properties.
