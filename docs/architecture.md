
## Architecture — Current State

### Top-Level Ontology Modes (Disjoint)

```
owl:Thing
├── Biomedical_Layer          ← biological machinery
├── Clinical_Framing          ← disease classification
├── Clinical_Manifestation    ← observable symptoms
├── External_Trigger          ← environmental factors
└── Therapeutic_Perturbation  ← drug interventions
```

---

### Biomedical_Layer TBox

```
Biomedical_Layer
├── Descriptive_Axes (orthogonal, cross-layer)
│   ├── By_Structural_Substrate
│   │   ├── Vascular_Substrate
│   │   ├── Parenchymal_Substrate
│   │   ├── Interstitial_Substrate
│   │   └── Neural_Substrate
│   ├── Mediator_Profile
│   │   ├── Concentration_Dependent_Mediator (CDM)
│   │   ├── Signalling_Intermediate          ← CDM modulation target (SWRL boundary)
│   │   │   ├── Ca2+
│   │   │   └── PKA_Signalling
│   │   ├── Feedback_Regulated_Entity
│   │   │   ├── SNS_Activation               ← NEW: MI feedback loop
│   │   │   └── RAAS_Activation              ← NEW: MI feedback loop
│   │   └── Receptor_Mediated_Signaller
│   └── Pathological_State
│       ├── Acute_Functional_Disruption
│       │   ├── Bronchoconstriction
│       │   ├── Blood_Clot                   ← NEW: MI
│       │   └── Coronary_Blockage            ← collapsed into Blood_Clot
│       └── Chronic_Structural_Disruption
│           ├── Airway_Remodelling
│           ├── Atherosclerosis              ← NEW: MI
│           ├── Epithelial_Damage
│           └── Chronic_Inflammation
│
├── L1_Infrastructure
│   ├── Cardiovascular_System               ← NEW: MI nodes
│   │   ├── Atherosclerosis
│   │   ├── Plaque_Rupture
│   │   └── Necrosis
│   ├── Respiratory_System
│   │   ├── Bronchoconstriction
│   │   ├── Airway_Remodelling
│   │   └── Epithelial_Damage
│   ├── Renal_System
│   ├── GI_System
│   ├── Liver_System
│   └── Universal_Process                   ← cross-organ processes
│       ├── Ischaemia                        ← NEW: universal (MI, stroke, renal)
│       ├── Chronic_Inflammation
│       └── Epithelial_Damage
│
├── L2_Hormone_and_biochemical_signalling
│   ├── cAMP_Production (SubClassOf CDM)
│   ├── Signalling_Intermediate
│   │   ├── Ca2+
│   │   └── PKA_Signalling
│   ├── Feedback_Regulated_Entity
│   │   ├── SNS_Activation                  ← NEW
│   │   └── RAAS_Activation                 ← NEW
│   ├── Leukotriene
│   ├── Histamine
│   ├── Prostaglandin
│   ├── Hypercholesterolaemia               ← NEW: MI etiology
│   ├── TXA2_Signalling
│   ├── Prostacyclin_Production
│   ├── MLCK_Activation                     ← NEW: Ca2+ → Contractility pathway
│   └── NO_Production                       ← NEW: endothelial pathway
│
├── L3_Immune
│   ├── Adaptive_Immunity
│   │   ├── IgE_Signalling (SubClassOf Feedback_Regulated_Entity)
│   │   ├── IgE_Mediated_Sensitisation
│   │   ├── Th2_Activation
│   │   └── Eosinophil_Recruitment
│   └── Innate_Immunity
│       ├── Mast_Cell_Degranulation
│       └── Macrophage_Activation           ← NEW: MI atherosclerosis driver
│
└── L4_Genetic
    ├── Genetic_Mutation
    │   ├── HER2_Overexpression
    │   └── Filaggrin_Mutation              ← NEW: eczema (partial)
    ├── Genetic_Predisposition
    │   ├── Atopy_Predisposition
    │   └── LDLR_Mutation                   ← NEW: familial hypercholesterolaemia
    └── Epigenetic_Modification
```

---

### Object Property Hierarchy (RBox) — UPDATED

```
owl:topObjectProperty
├── Biological_Logic
│   ├── System_Regulation_Logic
│   │   ├── Asserted_Logic
│   │   │   ├── increases
│   │   │   ├── inhibits
│   │   │   ├── modulates      ← NEW: CDM → Signalling_Intermediate (neutral direction)
│   │   │   ├── targets        ← L2/L3 node → Pathological_State (terminal)
│   │   │   └── progresses_to  ← Pathological_State → Pathological_State (time-involved)
│   │   └── Inferred_Logic (SWRL outputs — never assert manually)
│   │       ├── promotes
│   │       └── suppresses
│   └── Clinical_Logic
│       ├── Symptoms_Logic
│       │   └── leads_to       ← Biomedical_Layer → Clinical_Manifestation
│       └── Macro_Clinical_Logic
│           ├── has_etiology
│           ├── has_manifestation
│           ├── has_pathophysiology
│           └── has_complication
└── Drug_Intervention_Logic
    └── perturbs
        ├── perturbs_mechanistically  ← WHERE drug acts (L2/L3 target node)
        │   ├── downregulates
        │   └── upregulates
        └── perturbs_functionally     ← WHAT drug achieves (L1 clinical goal)
            ├── therapeutic_suppression
            └── therapeutic_activation
```

### Object Property Grammar Rules

```
increases/inhibits:  basic causal connection between nodes (any layer)
modulates:           CDM → Signalling_Intermediate only (direction TBD by data properties)
targets:             L2/L3 node → Acute_Pathological_State (terminal downstream)
progresses_to:       Pathological_State → Pathological_State (time involved, within same mode)
leads_to:            Pathological_State/Biomedical_Layer → Clinical_Manifestation
triggers:            External_Logic → Biomedical_Layer only
perturbs_mechanistically: drug → where it acts (determines layer score via SPARQL)
therapeutic_suppression:  drug → what it achieves clinically (L1 outcome)
```

---

### SubPropertyChains — CURRENT (REDUCED)

```
KEPT:
  promotes o increases → promotes
  promotes o targets   → promotes
  suppresses o increases → suppresses
  suppresses o targets   → suppresses

REMOVED:
  has_pathophysiology chains (replaced by SPARQL property paths)
  TS/TA multi-hop therapeutic suppression chains (replaced by direct assertion)
  causes chains (no longer needed)
```

---

### Data Properties — UPDATED

```
hasConcentrationLevel
  Domain: CDM
  Range: xsd:string {"low", "high"}

hasResponsePattern
  Domain: Biomedical_Layer (generalised — no longer CDM-only)
  Range: xsd:string {"direct", "inverse"}
  direct:  high→promotes, low→suppresses
  inverse: high→suppresses, low→promotes

occursIn
  Domain: Biomedical_Layer
  Range: xsd:string (organ system context)
  Used for: context-specific universal instances

REMOVED:
  intervenesAtLayerScore  ← replaced by SPARQL rdfs:subClassOf* derivation
  intervenesAtLayer (string version) ← deprecated
```

---

## SWRL Rules — CURRENT (MINIMAL)

```
KEPT — CDM Directional Logic (4 rules):
  Rule A: CDM(?m) ∧ modulates(?m, ?bio) ∧ Signalling_Intermediate(?bio)
          ∧ hasConcentrationLevel(?m, "high") ∧ hasResponsePattern(?m, "direct")
          → promotes(?m, ?bio)

  Rule B: CDM(?m) ∧ modulates(?m, ?bio) ∧ Signalling_Intermediate(?bio)
          ∧ hasConcentrationLevel(?m, "high") ∧ hasResponsePattern(?m, "inverse")
          → suppresses(?m, ?bio)

  Rule C: CDM(?m) ∧ modulates(?m, ?bio) ∧ Signalling_Intermediate(?bio)
          ∧ hasConcentrationLevel(?m, "low") ∧ hasResponsePattern(?m, "direct")
          → suppresses(?m, ?bio)

  Rule D: CDM(?m) ∧ modulates(?m, ?bio) ∧ Signalling_Intermediate(?bio)
          ∧ hasConcentrationLevel(?m, "low") ∧ hasResponsePattern(?m, "inverse")
          → promotes(?m, ?bio)

REMOVED:
  TS1, TS1', TS1'' (multi-hop therapeutic suppression)
  TA rules (therapeutic activation multi-hop)
  → replaced by direct therapeutic_suppression/activation assertions
```

---

## ABox — Complete Instance Sets

### Asthma Cascade

```
Asthma_instance (Asthma, SubClassOf Respiratory_Diseases)
  has_etiology → Atopy_Predisposition_instance
  has_etiology → Allergen_Exposure_instance
  has_pathophysiology → IgE_Mediated_asthma_instance
  has_pathophysiology → Chronic_Inflammation_asthma_instance
  has_manifestation → Wheeze_instance
  has_manifestation → Cough_instance
  has_manifestation → Shortness_of_Breath_instance
  has_manifestation → Chest_Pain_instance

Allergen_Exposure_instance (External_Trigger)
  triggers → IgE_Mediated_asthma_instance

Atopy_Predisposition_instance (Genetic_Predisposition)
  increases → IgE_Mediated_asthma_instance

IgE_Mediated_asthma_instance (IgE_Mediated_Sensitisation)
  increases → IgE_Signalling_instance
  increases → MastCell_instance

IgE_Signalling_instance (IgE_Signalling, Feedback_Regulated_Entity)
  increases → MastCell_instance
  increases → IgE_Mediated_asthma_instance  ← feedback loop

MastCell_instance (Mast_Cell_Degranulation)
  increases → Histamine_asthma_instance
  increases → Leukotriene_asthma_instance
  increases → PGD2_asthma_instance
  increases → IgE_Signalling_instance  ← feedback loop

Histamine_asthma_instance (Histamine)
  targets → Bronchoconstriction_instance
  hasResponsePattern: "direct"

Leukotriene_asthma_instance (Leukotriene)
  targets → Bronchoconstriction_instance
  targets → Chronic_Inflammation_asthma_instance

PGD2_asthma_instance (Prostaglandin)
  targets → Bronchoconstriction_instance

Th2_instance (Th2_Activation)
  increases → Eosinophil_asthma_instance

Eosinophil_asthma_instance (Eosinophil_Recruitment)
  increases → Epithelial_Damage_Respiratory_instance
  increases → Chronic_Inflammation_asthma_instance

Bronchoconstriction_instance (Bronchoconstriction, Acute_Functional_Disruption)
Chronic_Inflammation_asthma_instance (Chronic_Inflammation, Chronic_Structural_Disruption)
Airway_Remodelling_asthma_instance (Airway_Remodelling, Chronic_Structural_Disruption)
Epithelial_Damage_Respiratory_instance (Epithelial_Damage, Chronic_Structural_Disruption)
```

### Asthma Drug Instances

```
SABA_LABA_instance (SABA_LABA, L1_Functional_Agent)
  perturbs_mechanistically → cAMP_ASM_instance (upregulates)
  therapeutic_suppression → Bronchoconstriction_instance
  intervenesAtLayerScore: derived by SPARQL = 2

LTRA_instance (LTRA, L2_Mediator_Antagonist)
  perturbs_mechanistically → Leukotriene_asthma_instance (downregulates)
  therapeutic_suppression → Bronchoconstriction_instance
  therapeutic_suppression → Chronic_Inflammation_asthma_instance

Corticosteroid_instance (Corticosteroid, L3_Immunomodulator)
  perturbs_mechanistically → MastCell_instance (downregulates)
  perturbs_mechanistically → Th2_instance (downregulates)
  therapeutic_suppression → Airway_Remodelling_asthma_instance
  therapeutic_suppression → Chronic_Inflammation_asthma_instance

Omalizumab_instance (Omalizumab, L3_Immunomodulator)
  perturbs_mechanistically → IgE_Signalling_instance (downregulates)
  therapeutic_suppression → MastCell_instance
  therapeutic_suppression → Bronchoconstriction_instance
```

### MI Cascade — NEW

```
MI_instance (MI, SubClassOf Cardiovascular_Diseases)
  has_etiology → Hypercholesterolaemia_instance
  has_pathophysiology → Atherosclerosis_instance
  has_pathophysiology → Ischaemia_endocardium_instance
  has_manifestation → Chest_Pain_instance
  has_manifestation → Shortness_of_Breath_instance
  has_manifestation → Fatigue_instance

LDLR_Mutation_instance (LDLR_Mutation, L4_Genetic)
  increases → Hypercholesterolaemia_instance    ← optional etiology, not universal

Hypercholesterolaemia_instance (Hypercholesterolaemia, L2)
  increases → Atherosclerosis_instance

Macrophage_enzyme_instance (Macrophage_Activation, L3)
  increases → Atherosclerosis_instance          ← collapsed (no separate plaque buildup)

Atherosclerosis_instance (Atherosclerosis, Chronic_Structural_Disruption, Cardiovascular_System)
  increases → Plaque_Rupture_instance

Plaque_Rupture_instance (L1, Cardiovascular_System)
  increases → TXA2_platelet_instance            ← REUSED from platelet cascade ✓

TXA2_platelet_instance (TXA2_Signalling, CDM)
  inhibits → cAMP_TXA2_instance
  hasConcentrationLevel: "low"
  hasResponsePattern: "inverse"

cAMP_TXA2_instance (cAMP_Production, CDM, Signalling_Intermediate)
  modulates → Platelet_Activation_instance
  hasConcentrationLevel: "low"
  hasResponsePattern: "inverse"
  [SWRL fires]: suppresses(cAMP_TXA2, Platelet_Activation)

Platelet_Activation_instance (Signalling_Intermediate)
  targets → Blood_Clot_MI_instance

Blood_Clot_MI_instance (Acute_Functional_Disruption, Cardiovascular_System)
  progresses_to → Ischaemia_endocardium_instance

Ischaemia_endocardium_instance (Ischaemia, Universal_Process)
  occursIn: "Cardiovascular"
  increases → SNS_Activation_instance           ← feedback loop
  increases → RAAS_Activation_instance          ← feedback loop
  progresses_to → Necrosis_heart_instance
  leads_to → Chest_Pain_instance
  leads_to → Shortness_of_Breath_instance

SNS_Activation_instance (SNS_Activation, Feedback_Regulated_Entity)
  increases → Ischaemia_endocardium_instance    ← closes feedback

RAAS_Activation_instance (RAAS_Activation, Feedback_Regulated_Entity)
  increases → Ischaemia_endocardium_instance    ← closes feedback

Necrosis_heart_instance (Necrosis, Cardiovascular_System)
  leads_to → Fatigue_instance

Bradykinin_Adenosine_instance (L2)
  leads_to → Chest_Pain_instance
```

### MI Drug Instances — NEW

```
Statin_instance (Statin, L2_Mediator_Antagonist)
  perturbs_mechanistically → Hypercholesterolaemia_instance (downregulates)
  therapeutic_suppression → Atherosclerosis_instance
  [SPARQL derived layer: 2]

Antiplatelet_instance (Dual_antiplatelets, L2_Mediator_Antagonist)
  perturbs_mechanistically → TXA2_platelet_instance (downregulates)
  therapeutic_suppression → Blood_Clot_MI_instance
  [SPARQL derived layer: 2]

Beta_Blocker_instance (Beta_Blocker, L2_Mediator_Antagonist)
  perturbs_mechanistically → SNS_Activation_instance (downregulates)
  therapeutic_suppression → Ischaemia_endocardium_instance
  [SPARQL derived layer: 2]
  Note: therapeutic intent = reduce myocardial oxygen demand via SNS blockade

ACEi_instance (ACE_Inhibitor, L2_Mediator_Antagonist)
  perturbs_mechanistically → RAAS_Activation_instance (downregulates)
  therapeutic_suppression → Ischaemia_endocardium_instance
  [SPARQL derived layer: 2]
```

---

## Python Stack — Current

### GraphDB → networkx Graph Visualisation

```python
# forest_os_python.py — pulls full cascade from GraphDB, renders as coloured graph
# Green edges: increases, Red edges: inhibits, Gray edges: targets/other
# seed=42 for stable layout
```

### ODE Simulation (Platelet Cascade)

```python
# forest_os_ode.py — platelet cascade ODE
# Normal state vs Aspirin state comparison
# TXA2 rate constant reduced in Aspirin simulation
# Shows: cAMP, cAMP_TXA2, Platelet_Activation trajectories over time
```

---