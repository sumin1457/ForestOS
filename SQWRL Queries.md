# Forest OS — SQWRL Queries

## S1 - CDM, hasResponsePattern 'promotes'
autogen0:promotes(?m, ?t) -> sqwrl:select(?m, ?t)
Returns: PKA_TXA2_platelet_instance & 
Platelet_Activation_instance

## S2 - CDM, hasResponsePattern 'suppresses'
autogen0:suppresses(?m, ?t) -> sqwrl:select(?m, ?t)
Returns: PKA_PGI2_platelet_instance &
Platelet_Activation_instance

## S3 — Therapeutic Suppression
autogen0:therapeutic_suppression(?drug, ?t) 
→ sqwrl:select(?drug, ?t)
Returns: all drugs and their suppressed targets

## S4 — Asthma Symptoms  
autogen0:has_manifestation(autogen0:Asthma_instance, ?s) 
→ sqwrl:select(?s)

## S5 — Asthma Etiology
autogen0:has_etiology(autogen0:Asthma_instance, ?x) 
→ sqwrl:select(?x) ^ sqwrl:columnNames("Asthma Etiology")

## S6 — Immune-Targeting Drugs
autogen0:L3_Immune(?L3) 
^ autogen0:downregulates(?drug, ?L3) 
^ autogen0:therapeutic_suppression(?drug, ?t)
→ sqwrl:select(?drug, ?t) ^ sqwrl:columnNames("L3 Drug", "Target")
Returns: Corticosteroid, Omalizumab

## S7 — Drug × Layer × Target Table
autogen0:has_pathophysiology(autogen0:Asthma_instance, ?t)
^ autogen0:therapeutic_suppression(?drug, ?t)
^ autogen0:intervenesAtLayerScore(?drug, ?score)
→ sqwrl:select(?drug, ?score, ?t)
^ sqwrl:columnNames("Drug", “Layer”, "Target")
^ sqwrl:orderByDescending(?score)