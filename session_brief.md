# Forest OS Ontology — Session Brief v2 (Week 2 Complete)

## Current Status

**Tool:** Protégé 5.6.9 (OWL 2, Pellet reasoner)
**Duration:** ~12 days
**Stage:** Asthma mapping COMPLETE. Ready for DL Query/SPARQL
**Reasoner:** Pellet (HermiT fails on SWRL built-ins)

---

## Current Architecture

### Top-Level Ontology Modes (Disjoint)

```
owl:Thing
├── Biomedical_Layer          ← biological machinery
├── Clinical_Framing          ← human-imposed disease classification
├── Clinical_Manifestation    ← observable outputs
├── External_Trigger          ← environmental factors
└── Therapeutic_Perturbation  ← drug interventions
```

---

### Biomedical_Layer (TBox)

```
Biomedical_Layer
├── Descriptive_Axes (orthogonal, cross-layer)
│   ├── By_Structural_Substrate
│   │   ├── Vascular_Substrate
│   │   ├── Parenchymal_Substrate
│   │   ├── Interstitial_Substrate
│   │   └── Neural_Substrate
│   ├── Mediator_Profile
│   │   ├── Concentration_Dependent_Mediator (CDM) ← EquivalentTo defined
│   │   ├── Downstream_Process
│   │   │   ├── Bronchoconstriction
│   │   │   └── Platelet_Activation
│   │   ├── Feedback_Regulated_Entity
│   │   ├── Receptor_Mediated_Signaller
│   │   └── Signalling_Intermediate
│   │       ├── Ca2+
│   │       └── PKA_Signalling
│   └── Pathological_State
│       ├── Acute_Functional_Disruption
│       │   └── Bronchoconstriction
│       └── Chronic_Structural_Disruption
│           ├── Airway_Remodelling
│           ├── Epithelial_Damage
│           └── Chronic_Inflammation
│
├── L1_Infrastructure
│   ├── By_Organ_System
│   │   ├── Cardiovascular_System
│   │   ├── Respiratory_System
│   │   │   ├── Airway_Remodelling
│   │   │   ├── Bronchoconstriction
│   │   │   └── Epithelial_Damage
│   │   ├── Renal_System
│   │   ├── GI_System
│   │   └── Liver_System
│   └── Structural_Process (universal L1 processes)
│       ├── Epithelial_Damage
│       └── Chronic_Inflammation
│
├── L2_Hormone_and_biochemical_signalling
│   ├── cAMP_Production (SubClassOf CDM)
│   ├── PKA_Signalling (SubClassOf Signalling_Intermediate)
│   ├── Platelet_Activation
│   ├── Thromboxane_A2_Signalling
│   ├── Prostacyclin_Production
│   ├── Leukotriene
│   ├── Histamine
│   ├── Prostaglandin
│   ├── Hypercholesterolaemia
│   ├── RAAS_Activation
│   └── Sympathetic_Nervous_System_Activation
│
├── L3_Immune
│   ├── Adaptive_Immunity
│   │   ├── IgE_Signalling (SubClassOf Feedback_Regulated_Entity)
│   │   ├── Allergen_Sensitisation
│   │   │   └── IgE_Mediated_Sensitisation
│   │   └── Eosinophil_Recruitment
│   └── Innate_Immunity
│       └── Mast_Cell_Degranulation
│
└── L4_Genetic
    ├── Genetic_Mutation
    │   └── HER2_Overexpression
    ├── Genetic_Predisposition
    │   └── Atopy_Predisposition
    └── Epigenetic_Modification
```

---

### Object Property Hierarchy (RBox)

```
owl:topObjectProperty
├── Biological_Logic
│   ├── System_Regulation_Logic
│   │   ├── Asserted_Logic (ground facts only — never infer these manually)
│   │   │   ├── increases
│   │   │   ├── inhibits
│   │   │   ├── targets
│   │   │   └── progresses_to (Pathological_State → Pathological_State)
│   │   └── Inferred_Logic (SWRL outputs only — never assert manually)
│   │       ├── causes
│   │       ├── promotes
│   │       └── suppresses
│   └── Clinical_Logic
│       ├── Symptoms_Logic
│       │   └── leads_to (Biomedical_Layer → Clinical_Manifestation)
│       └── Macro_Clinical_Logic
│           ├── has_complication (Clinical_Condition → Clinical_Condition)
│           ├── has_etiology (Clinical_Condition → Biomedical_Layer)
│           ├── has_manifestation (Clinical_Condition → Clinical_Manifestation)
│           └── has_pathophysiology (Clinical_Condition → Biomedical_Layer)
└── Drug_Intervention_Logic
    └── perturbs
        ├── perturbs_mechanistically
        │   ├── upregulates (SubPropertyOf: increases)
        │   └── downregulates (SubPropertyOf: inhibits)
        └── perturbs_functionally
            ├── therapeutic_activation
            └── therapeutic_suppression
```

### SubPropertyChains Declared

```
On causes:
  increases o targets   → causes
  inhibits o targets    → causes
  increases o causes    → causes
  inhibits o causes     → causes
  inhibits o increases  → causes

On has_pathophysiology:
  has_etiology o increases  → has_pathophysiology
  has_etiology o triggers   → has_pathophysiology
  has_etiology o inhibits   → has_pathophysiology
  has_pathophysiology o increases → has_pathophysiology
  has_pathophysiology o inhibits  → has_pathophysiology
  has_pathophysiology o targets   → has_pathophysiology
```

---

### Key Class Definitions (EquivalentTo)

```
CDM EquivalentTo: Mediator_Profile
                  and (hasConcentrationLevel some xsd:string)
```

---

### Data Properties

```
hasConcentrationLevel
  Domain: CDM
  Range: xsd:string {"low", "high", "normal"}

hasResponsePattern
  Domain: Biomedical_Layer
  Range: xsd:string {"direct", "inverse"}
  direct:  high→promotes, low→suppresses
  inverse: high→suppresses, low→promotes

intervenesAtLayerScore
  Domain: Drug_Intervention
  Range: xsd:integer {1, 2, 3, 4}
```

---

## ABox — Complete Instance Set

### Platelet Cascade (TXA2/PGI2 context)

```
TXA2_instance (Thromboxane_A2_Signalling)
  inhibits → cAMP_TXA2_platelet_instance

PGI2_instance (Prostacyclin_Production)
  increases → cAMP_PGI2_platelet_instance

cAMP_TXA2_platelet_instance (cAMP_Production)
  hasConcentrationLevel: "low"
  hasResponsePattern: "inverse"
  increases → PKA_TXA2_platelet_instance

cAMP_PGI2_platelet_instance (cAMP_Production)
  hasConcentrationLevel: "high"
  hasResponsePattern: "inverse"
  increases → PKA_PGI2_platelet_instance

PKA_TXA2_platelet_instance (PKA_Signalling)
  hasConcentrationLevel: "low"
  hasResponsePattern: "inverse"
  targets → Platelet_Activation_instance

PKA_PGI2_platelet_instance (PKA_Signalling)
  hasConcentrationLevel: "high"
  hasResponsePattern: "inverse"
  targets → Platelet_Activation_instance

Platelet_Activation_instance (Platelet_Activation)
```


### Asthma Cascade — Complete

```
[External Trigger]
Allergen_Exposure_instance (External_Trigger)
  triggers → IgE_Mediated_Sensitisation_instance

[L4]
Atopy_Predisposition_instance (Atopy_Predisposition)
  increases → IgE_Mediated_Sensitisation_instance

[L3 — Sensitisation]
IgE_Mediated_Sensitisation_instance (IgE_Mediated_Sensitisation)
  increases → IgE_Signalling_instance

IgE_Signalling_instance (IgE_Signalling, Feedback_Regulated_Entity)
  increases → MastCell_asthma_instance
  [Omalizumab downregulates this]

[L3 — Effector]
MastCell_asthma_instance (Mast_Cell_Degranulation)
  increases → Leukotriene_asthma_instance
  increases → Histamine_asthma_instance
  increases → PGD2_asthma_instance
  increases → Eosinophil_asthma_instance
  [Corticosteroid downregulates this]

Eosinophil_asthma_instance (Eosinophil_Recruitment)
  increases → Epithelial_Damage_Respiratory_instance

Th2_instance (Adaptive_Immunity)
  [structural node for has_pathophysiology]
  increases → Eosinophil_asthma_instance
  increases → IgE_Signalling_instance ← resensitisation loop
  [Corticosteroid downregulates this]
  

[L2 — Mediators]
Leukotriene_asthma_instance (Leukotriene)
  hasResponsePattern: "direct"
  targets → Bronchoconstriction_instance
  [LTRA downregulates this]

Histamine_asthma_instance (Histamine)
  hasResponsePattern: "direct"
  targets → Bronchoconstriction_instance

PGD2_asthma_instance (Prostaglandin)
  hasResponsePattern: "direct"
  targets → Bronchoconstriction_instance

cAMP_ASM_instance (cAMP_Production)
  hasConcentrationLevel: "high"
  hasResponsePattern: "inverse"
  targets → Bronchoconstriction_instance
  [SABA/LABA upregulates this]

[L1 — Infrastructure]
Bronchoconstriction_instance (Bronchoconstriction, Downstream_Process,
                               Acute_Functional_Disruption, Respiratory_System)
  progresses_to → Epithelial_Damage_Respiratory_instance

Epithelial_Damage_Respiratory_instance (Epithelial_Damage, Respiratory_System)
  progresses_to → Chronic_Inflammation_asthma_instance

Chronic_Inflammation_asthma_instance (Chronic_Inflammation)
  progresses_to → Airway_Remodelling_asthma_instance

Airway_Remodelling_asthma_instance (Airway_Remodelling, Respiratory_System,
                                     Chronic_Structural_Disruption)

[Drugs]
LTRA_instance (LTRA, L2_Mediator_Antagonist)
  intervenesAtLayerScore: 2
  downregulates → Leukotriene_asthma_instance

SABA_LABA_instance (SABA/LABA, L1_Functional_Agent)
  intervenesAtLayerScore: 1
  upregulates → cAMP_ASM_instance

Corticosteroid_instance (Corticosteroid, L3_Immunomodulator)
  intervenesAtLayerScore: 3
  downregulates → MastCell_asthma_instance

Omalizumab_instance (Omalizumab, L3_Immunomodulator)
  intervenesAtLayerScore: 3
  downregulates → IgE_Signalling_instance

[Clinical_Framing]
Asthma_instance (Asthma)
  has_etiology → Atopy_Predisposition_instance
  has_etiology → Allergen_Exposure_instance
  has_pathophysiology → Bronchoconstriction_instance  ← manual (SQWRL target)
  has_pathophysiology → Airway_Remodelling_asthma_instance ← manual
  has_pathophysiology → [rest inferred via SubPropertyChain]
  has_manifestation → Wheeze_instance
  has_manifestation → Cough_instance
  has_manifestation → Shortness_of_Breath_instance
  has_manifestation → Chest_Pain_instance

[Symptoms]
Wheeze_instance (Symptoms)
Cough_instance (Symptoms)
Shortness_of_Breath_instance (Symptoms)
Chest_Pain_instance (Symptoms)
```

---

## SWRL Rules — Complete Set

### State Assignment (Rules 1/2)

```
Rule 1: CDM(?m) ^ inhibits(?x, ?m)
        → hasConcentrationLevel(?m, "low")

Rule 2: CDM(?m) ^ increases(?x, ?m)
        → hasConcentrationLevel(?m, "high")
```

### Effect Inference (Rules A-D)

```
Rule A: CDM(?m) ^ hasConcentrationLevel(?m, "high")
        ^ hasResponsePattern(?m, "direct")
        ^ targets(?m, ?t) ^ Downstream_Process(?t)
        → promotes(?m, ?t)

Rule B: CDM(?m) ^ hasConcentrationLevel(?m, "low")
        ^ hasResponsePattern(?m, "direct")
        ^ targets(?m, ?t) ^ Downstream_Process(?t)
        → suppresses(?m, ?t)

Rule C: CDM(?m) ^ hasConcentrationLevel(?m, "high")
        ^ hasResponsePattern(?m, "inverse")
        ^ targets(?m, ?t) ^ Downstream_Process(?t)
        → suppresses(?m, ?t)

Rule D: CDM(?m) ^ hasConcentrationLevel(?m, "low")
        ^ hasResponsePattern(?m, "inverse")
        ^ targets(?m, ?t) ^ Downstream_Process(?t)
        → promotes(?m, ?t)
```

### Therapeutic Effect Rules (TS/TA)

```
Rule TS1 (downregulates direct → suppression):
Drug_Intervention(?drug) ^ downregulates(?drug, ?bio)
^ Biomedical_Layer(?bio) ^ hasResponsePattern(?bio, "direct")
^ targets(?bio, ?t) ^ Downstream_Process(?t)
→ therapeutic_suppression(?drug, ?t)

Rule TS2 (upregulates inverse → suppression):
Drug_Intervention(?drug) ^ upregulates(?drug, ?bio)
^ Biomedical_Layer(?bio) ^ hasResponsePattern(?bio, "inverse")
^ targets(?bio, ?t) ^ Downstream_Process(?t)
→ therapeutic_suppression(?drug, ?t)

Rule TA1 (upregulates direct → activation):
Drug_Intervention(?drug) ^ upregulates(?drug, ?bio)
^ Biomedical_Layer(?bio) ^ hasResponsePattern(?bio, "direct")
^ targets(?bio, ?t) ^ Downstream_Process(?t)
→ therapeutic_activation(?drug, ?t)

Rule TA2 (downregulates inverse → activation):
Drug_Intervention(?drug) ^ downregulates(?drug, ?bio)
^ Biomedical_Layer(?bio) ^ hasResponsePattern(?bio, "inverse")
^ targets(?bio, ?t) ^ Downstream_Process(?t)
→ therapeutic_activation(?drug, ?t)

Rule TS1' (two-hop: downregulates→increases→targets):
Drug_Intervention(?drug) ^ downregulates(?drug, ?b1)
^ Biomedical_Layer(?b1) ^ increases(?b1, ?b2)
^ Biomedical_Layer(?b2) ^ hasResponsePattern(?b2, "direct")
^ targets(?b2, ?t) ^ Downstream_Process(?t)
→ therapeutic_suppression(?drug, ?t)

Rule TS1'' (three-hop: downregulates→increases→increases→targets):
Drug_Intervention(?drug) ^ downregulates(?drug, ?b1)
^ Biomedical_Layer(?b1) ^ increases(?b1, ?b2)
^ Biomedical_Layer(?b2) ^ increases(?b2, ?b3)
^ Biomedical_Layer(?b3) ^ hasResponsePattern(?b3, "direct")
^ targets(?b3, ?t) ^ Downstream_Process(?t)
→ therapeutic_suppression(?drug, ?t)
```

---

## Verified Working SQWRL Queries

```
S4:  therapeutic_suppression(?drug, ?t) → sqwrl:select(?drug, ?t)
     Returns: LTRA/SABA/Corticosteroid/Omalizumab → Bronchoconstriction ✓

S6:  has_manifestation(Asthma_instance, ?s) → sqwrl:select(?s)
     Returns: Wheeze, Cough, SOB, Chest_Pain ✓

S7:  has_etiology(Asthma_instance, ?x) → sqwrl:select(?x)
     Returns: Atopy_Predisposition, Allergen_Exposure ✓

S9:  L3_Immune(?L3) ^ downregulates(?drug, ?L3) ^ therapeutic_suppression(?drug, ?t)
     → sqwrl:select(?drug, ?t)
     Returns: Corticosteroid, Omalizumab → Bronchoconstriction ✓
     [answers: "which drugs act at immune layer?"]

S11: has_pathophysiology(Asthma_instance, ?t)
     ^ therapeutic_suppression(?drug, ?t)
     ^ intervenesAtLayerScore(?drug, ?score)
     → sqwrl:select(?drug, ?score, ?t)
     Returns: drug × layer × target table ✓
     [answers: "what layer does each asthma drug target?"]

S12: therapeutic_suppression(?drug, ?t) → sqwrl:select(?drug) ^ sqwrl:count(?t)
     Returns: all drugs with suppression count ✓
```

---

## Key Classification Decisions

| Decision | Reasoning |
|---|---|
| **Descriptive_Axes peer to L1-L4** | L1-L4 = what things ARE. By_Structural_Substrate, Mediator_Profile, Pathological_State = how we DESCRIBE them. Different ontological kinds — not nested |
| **CDM EquivalentTo uses hasConcentrationLevel not targets** | Avoids dependency on property type (targets vs increases). Classification fires from data property alone — stable across cascade depth changes |
| **hasResponsePattern on ALL terminal mediators** | Unifies CDM and non-CDM mediators (LT, Histamine) under same rule set. Direct assertions use "direct"/"inverse" — Rules A-D fire on all |
| **Pathological_State separate from L1** | L1 describes normal machinery. Pathological_State describes failure of machinery. Distinct modes — Bronchoconstriction is dual-classified (Downstream_Process + Acute_Functional_Disruption) |
| **Structural_Process under L1** | Universal container for L1-level processes occurring across organ systems. Organ specificity added at instance level |
| **Epithelial_Damage/Chronic_Inflammation not organ-specific at class level** | These occur across respiratory, GI, renal contexts. Class is universal. Instance carries organ context via Type assertion |
| **progresses_to vs leads_to** | progresses_to: Pathological_State→Pathological_State (same mode, temporal disease progression). leads_to: Biomedical_Layer→Clinical_Manifestation (mode bridge) |
| **has_pathophysiology via SubPropertyChain** | Avoids O(diseases × cascade_depth) manual assertions. Inferred from has_etiology o increases chain automatically. Terminal nodes manually asserted for SQWRL queryability |
| **intervenesAtLayer data property** | Elegant single assertion per drug encoding layer-of-intervention. Enables drug comparison queries without complex reasoning. L1=symptom, L2=mediator, L3=immune, L4=genetic |
| **IgE_Mediated_Sensitisation as specific subclass** | Allergen sensitisation doesn't always produce IgE (Th1 vs Th2 skewing). IgE_Mediated_Sensitisation is Th2-specific. Cell_Mediated_Sensitisation placeholder for future Type 4 hypersensitivity |
| **Resensitisation loop structurally encoded** | MastCell increases IgE_Signalling + IgE_Signalling increases MastCell. Both asserted. IgE_Signalling typed as Feedback_Regulated_Entity. Not reasoned over — cycles unreliable in SWRL |
| **LT/Histamine/PGD2 not CDM** | Unidirectional in asthma context. No bidirectionality — high always promotes, low is absence of effect. hasResponsePattern "direct" + targets sufficient. No CDM machinery needed |

---

## Unresolved Tensions

| Tension | Status | Resolution Path |
|---|---|---|
| **SQWRL cannot read SubPropertyChain inferences** | Accepted limitation | Month 2: SPARQL reads all OWL inferences. Currently: manual assertions on SQWRL query targets |
| **has_pathophysiology manual for SQWRL** | Pragmatic fix | Assert terminal nodes manually. SubPropertyChain handles structural completeness. Month 2: Named Graphs replace has_pathophysiology entirely |
| **occursIn location encoding** | Deferred | Data property string temporary fix. Month 2: Named Graphs for disease context isolation |
| **Universal vs disease-specific instances** | Partially resolved | Entry point instances disease-specific (IgE_Sensitisation_asthma). Downstream universal where possible. Full resolution: Named Graphs + SPARQL |
| **SWRL multi-hop rule explosion** | Accepted | Manual rules per depth level (TS1, TS1', TS1''). Current max depth: 3. Manageable at current scale |
| **therapeutic_suppression count = 1 for all** | Accepted | Jumping rules collapse cascade to terminal node. intervenesAtLayer communicates depth more elegantly than count |
| **Feedback loop reasoning** | Deferred | Structurally encoded. Not reasoned over. Full reasoning requires cycle detection — Month 2 SPARQL |
| **By_Structural_Substrate scope** | Pending | Should apply cross-layer but currently under Descriptive_Axes. Use selectively — only when substrate is architecturally defining |

---

## Design Philosophy (Complete)

1. **Beauty precedes correctness** — structural elegance is the truth detector. Redundancy signals wrong abstraction level.

2. **Assert only ground truth** — never assert what should be inferred. If manually asserting promotes/suppresses, something is architecturally wrong.

3. **SWRL as translator, not propagator** — translates data property state into object property effect at terminal nodes only. SubPropertyChain handles structural propagation.

4. **Two inference engines, clean division** — OWL classifier: structural, direction-blind. SWRL: data-property-aware, direction-sensitive. Never mix roles.

5. **Queries reveal meaning** — SWRL rules are silent. SQWRL queries expose emergent knowledge. Design for queryability.

6. **Fidelity matches competency questions** — encode at the level your drug acts at. Don't add intermediate nodes until a query requires them.

7. **Context-specific instances, generalised rules** — shared biological nodes require context-specific instances. Rules stay generalised because they fire on class membership.

8. **Domain declarations are dangerous** — OWL Domain infers type on any individual using that property. Use narrowly. Unexpected domain inference is the most common inconsistency source.

9. **Ontological modes matter** — Biomedical_Layer, Clinical_Framing, Clinical_Manifestation, Therapeutic_Perturbation are hard boundaries. DisjointWith formalises them.

10. **intervenesAtLayer is your scoring seed** — one data property per drug communicates therapeutic depth. Seed of the full Therapeutic Engine scoring system.

---

## Technical Notes

```
Reasoner: Pellet 2.2.0 (not HermiT — fails on SWRL built-ins)
Known issue: Protégé sync — restart when SQWRL returns empty
             despite OWL reasoner showing correct inferences
             sqwrl:columnNames issue - Pellet cannot read SWRL

Literal matching: ensure "direct"^^xsd:string consistency
                  across data property assertions and SWRL rules

has_pathophysiology SQWRL gap:
  SubPropertyChain inferences not readable by SQWRL
  Fix: manually assert terminal nodes on disease instances
  Future: Named Graphs replace this entirely

Domain declarations:
  hasConcentrationLevel Domain: CDM only
  causes: NO domain (must cross ontological modes)
  therapeutic_suppression: NO domain
  intervenesAtLayer Domain: Drug_Intervention

Property naming convention:
  Asserted_Logic properties: assert once per instance, ground truth
  Inferred_Logic properties: NEVER assert manually — SWRL output only
  Drug_Intervention_Logic: upregulates/downregulates on drug instances
```
