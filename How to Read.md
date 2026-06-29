# Forest OS — How to Read This Ontology

## The Core Insight

Most biomedical ontologies encode disease as a separate entity.
Forest OS encodes disease as a DEVIATION from homeostatic baseline.

The same L4→L3→L2→L1 cascade that operates in normal physiology
produces disease when its balance is disrupted.

## Start Here — The Four Layers

L4: Genetic predisposition (WHY someone is susceptible)
L3: Immune cascade (HOW the immune system responds)
L2: Biochemical mediators (WHAT molecules are released)
L1: Infrastructure (WHERE the physical disruption occurs)

## The Key Pattern: hasResponsePattern

Most ontologies assume high concentration → activation.
Biology doesn't work like that.

cAMP in platelets:   high → SUPPRESSES aggregation
cAMP in airways:     high → SUPPRESSES bronchoconstriction
Histamine in airways: high → PROMOTES bronchoconstriction

hasResponsePattern {"direct", "inverse"} encodes this
context-specific bidirectionality formally.

## How to Run a Query

1. Open forest_os_ontology.owx in Protégé
2. Start Pellet reasoner
3. Open SQWRLTab
4. Run S7: Drug x Layer x Target

Result: ranked drug table by layer of intervention