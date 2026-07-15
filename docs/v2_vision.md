### Why v2

```
Mapping eczema alongside asthma exposed a structural problem the v1
model couldn't represent honestly. Nodes like `Th2_Activation`
and several inflammatory processes aren't disease-specific — they're
genuine shared physiological infrastructure, reachable from more than
one disease's etiology chain. But OWL/Protégé only offered two options:
duplicate the node per disease (losing the fact that it's one real
thing) or merge it into a single instance (losing disease-specific
context on it).

Neither is correct. A node like `Th2_Activation` is one process
that means something different depending on which cascade activates
it — and v1 had no way to say that without either instance duplication
or ambiguity. That's the problem v2 exists to solve.

```

### Forest OS Research Contribution

```
Novel aspects:
  1. Four-layer pathophysiological model (L1-L4) formally in OWL
  2. hasResponsePattern — bidirectional concentration-dependent
     mediator logic as generalised OWL pattern
  3. perturbs_mechanistically/functionally — dual drug assertion
     separating mechanism from therapeutic intent
  4. Named Graph disease context isolation (Month 2)
  5. Structure-derived layer scoring via rdfs:subClassOf* SPARQL
  6. Homeostatic baseline + disease deviation framework (v2 vision)

```

### Forest OS v2 Vision

```
Current (v1): pathology as primary — Bronchoconstriction IS pathological
Future (v2):  homeostasis as primary — Bronchoconstriction is a normal
              process that becomes pathological when dysregulated

v2 architecture:
  Shared_biology graph: universal processes, homeostatic baseline
  Disease_context graph: which processes deviate from baseline
  Drug_context graph: which processes drugs perturb in which context

Side effects = drug perturbs a node appearing in multiple disease contexts
→ formally derivable from named graph structure
→ Beta-Blocker + Asthma contraindication derivable from structure alone

```

### Named Graph Solution to the Universal Node Problem

```
Context does NOT belong inside nodes.
Context belongs in the GRAPH WRAPPER around triples.
Universal_node stays universal:
[MI_graph]    { Universal_node occursIn Cardiovascular }
[Stroke_graph]{ Universal_node occursIn Nervous }
Same node. Different contexts. No duplication.
Side effects become formally derivable as cross-context perturbations
— rather than something that has to be hand-coded per drug

This is the resolution to the eczema/asthma wall above: the node
persists once, and disease-context becomes a property of which graph
it's queried within, not something asserted onto the node itself.

```
