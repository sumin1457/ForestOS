
# **Forest OS Query Scripts — Clinical Timeline**

Reference: forestos_clinical_timeline.py 

This file narrates what python script `python/forestos_clinical_timeline.py` demonstrates.

---

## 1. Purpose

Classifies a disease's symptoms as acute or chronic based on whether a time-dependent structural progression step is required before the symptom manifests. Provides a structurally-derived clinical framing without explicit severity assertions.

---

## 2. Method

Uses the progresses_to? zero-or-one path operator in SPARQL to detect whether a progression node exists between the L1 tissue node and the symptom:

```
?viaAcute :progresses_to? ?afterProgression .
?afterProgression :leads_to ?symptom .
BIND(IF(?viaAcute = ?afterProgression, "acute", "chronic") AS ?effectType)

```

When progresses_to? matches zero times — ?viaAcute = ?afterProgression — no structural progression occurred and the symptom is classified acute. When it matches once, a progression node exists and the symptom is classified chronic. A single query produces both classifications simultaneously.

The query enters the cascade through the disease instance in the default graph (has_etiology / has_pathophysiology), traverses the cascade through the default graph, then terminates in the location context named graph (context/Respiratory, context/Cardiovascular) for the symptom pathway.

---

## 3. Results

```
Asthma (context/Respiratory):
    Acute (3):
        Bronchoconstriction  →  Shortness_of_Breath
        Bronchoconstriction  →  Wheeze
        Epithelial_Damage    →  Cough

    Chronic (5):
        Bronchoconstriction  →  Airway_Remodelling       →  Shortness_of_Breath
        Bronchoconstriction  →  Airway_Remodelling       →  Wheeze
        Epithelial_Damage    →  Chronic_Inflammation     →  Chest_Pain
        Chronic_Inflammation    →  Airway_Remodelling    →  Shortness_of_Breath
        Chronic_Inflammation    →  Airway_Remodelling    →  Wheeze

MI (context/Cardiovascular):
    Acute (0):
        none

    Chronic (3):
        BloodClot  →  Ischaemia  →  Shortness_of_Breath
        BloodClot  →  Ischaemia  →  Chest_Pain
        Ischaemia  →  Necrosis  →  Fatigue

```

---

## 4. Clinical interpretation

Asthma presents with both acute and chronic symptoms — Bronchoconstriction produces immediate wheeze and dyspnoea, while long-term structural remodelling sustains and amplifies those same symptoms chronically. The same symptom (Shortness_of_Breath) appears in both acute and chronic categories, reflecting dual-pathway production.

MI in the current model produces only chronic symptoms — all symptom pathways require progression through Ischaemia before clinical manifestation. This reflects the modelling decision to anchor MI's acute presentation at the Ischaemia node, which is itself a progression consequence of BloodClot formation rather than a direct tissue-to-symptom edge.

---

## 5. What this classification captures

```
effectType = "acute"   →  direct tissue → symptom
                           no time-dependent structural change required
                           clinically: immediate presentation on cascade activation

effectType = "chronic" →  tissue → progresses_to → structural change → symptom
                           time-dependent — requires repeated insult or sustained
                           activation before symptom manifests
                           clinically: develops over weeks to months
```

---

## 6. Known limitation

This is a structural proxy for clinical acuity, not a severity score. It captures whether time-dependent structural change is required for symptom production — but not how severe the symptom is, how quickly the acute presentation occurs, or how reversible the chronic change is. These dimensions require either explicit severity data properties (hasSeverityScore) or ODE-derived activation peaks once rate constants are grounded in the ontology.

The MI result (acute: 0) reflects current modelling granularity — MI's acute presentation (chest pain at time of infarction) is clinically immediate but is not represented as a direct L1→symptom edge in the current ABox. This is a known modelling gap to address in a future version.

---

## 7. Generalisation

The function accepts any disease instance and location context graph. When COPD is mapped to context/Respiratory, the same function will automatically differentiate COPD-specific acute from chronic symptoms without modification, inheriting the shared Respiratory context progression chain.
