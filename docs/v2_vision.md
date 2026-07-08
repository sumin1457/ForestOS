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
