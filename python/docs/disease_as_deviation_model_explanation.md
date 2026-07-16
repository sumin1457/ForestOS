
# **Forest OS — Disease-as-Deviation Model**

Reference: forestos_disease_as_deviation_model.py

This file narrates what python script `python/forestos_disease_as_deviation_model.py` demonstrates. 

---

## **About**

Forest OS models disease as location-specific deviation from a universal homeostatic baseline. Rather than duplicating biological nodes per disease, the system separates three distinct concerns — what the biology is, where it occurs, and what disease triggered it — assigning each to a different layer of the knowledge architecture.

---

## **The Layered Architecture**

The ontology is organised across four biological layers, each representing a different level of biological abstraction:

L4 (Genetic) defines the starting conditions — predispositions, mutations, and epigenetic modifications that determine an individual's baseline capacity before any disease process begins.

L3 (Immune) and L2 (Biochemical) form the homeostatic base — the regulatory machinery that operates in healthy individuals. Th2 activation, IgE signalling, histamine, prostaglandins, cAMP — these nodes exist universally and are not inherently pathological. Disease occurs when this machinery is dysregulated or overstimulated.

L1 (Infrastructure) is where deviation becomes visible at the tissue level. Bronchoconstriction, atherosclerosis, ischaemia, epithelial damage — these are the pathological consequences that manifest when L2/L3 machinery drives tissue-level disruption. L1 nodes are inherently location-specific: the same process (ischaemia, chronic inflammation) produces different clinical consequences depending on which tissue it occurs in.

---

## **The Universal Node Problem and Its Solution**

A fundamental challenge in biomedical ontology engineering is that universal biological processes — ischaemia, chronic inflammation, epithelial damage — appear across multiple diseases in different tissue contexts. Duplicating nodes per disease inflates the ABox and breaks cross-disease reasoning. Leaving them singular loses context.

Forest OS resolves this by placing context on the edge, not the node. Universal nodes (typed as `Universal_Process`) remain singular in the default graph. Location context is asserted via an `occursIn` data property on location-specific instances — a minimal ABox expansion at L1 only, one instance per tissue context. Named graphs then hold the location-specific edges that connect these nodes to their tissue consequences, without duplicating the nodes themselves.

---

## **Named Graph Architecture**

The system uses two levels of named graph:

Location context graphs (`context/Respiratory`, `context/Cardiovascular`, etc.) hold edges that are specific to a tissue location. The same mediator node — histamine, for example — targets bronchoconstriction in the respiratory context and vasoconstriction in the cardiovascular context. The node is universal; the named graph encodes where its effect occurs. When a new disease is mapped that shares the same tissue (e.g. COPD sharing `context/Respiratory` with Asthma), no duplication occurs — the location context is already there.

The default graph holds the complete ontology as exported from Protégé — all nodes, all asserted edges, all inferred axioms. It is never modified. Named graphs are built on top of it as queryable overlays, rebuilt automatically after each Protégé re-export.

---

## **The Python Script**

`forestos_disease_as_deviation_model.py` implements the graph builder in three steps, each corresponding to a biological transition:

Step 1 classifies L2/L3 → L1 edges — the bridge from homeostatic machinery to tissue-level pathology. Each edge is classified by its target node's location, determined either from the TBox class hierarchy (Type A nodes like Bronchoconstriction, already typed as `Respiratory_System`) or from the `occursIn` data property (Type B universal nodes like `Ischaemia_endocardium_instance`).

Step 2 classifies L1 → symptom edges — the bridge from tissue pathology to observable clinical manifestation. These are location-specific: the same symptom (shortness of breath) can arise from different tissue contexts, each entered through a different named graph.

Step 3 classifies L1 → L1 progression edges — acute to chronic disease progression within the tissue layer. Bronchoconstriction progressing to airway remodelling, ischaemia progressing to necrosis.

Running `rebuild_all_graphs()` drops all existing context graphs and rebuilds them from scratch, keeping the named graph structure automatically synchronised with the ontology after each Protégé re-export.

---

## **Cross-Graph Querying**

The architecture enables queries that cross multiple named graphs in a single SPARQL statement. A query can enter the system through a disease context graph (retrieving the disease-specific entry point), traverse the cascade through the default graph (following universal biological edges), and terminate in a location context graph (retrieving tissue-specific symptoms or chronic consequences) — all without duplicating a single node.

This makes Forest OS extensible by design: each new disease mapped in Protégé adds its entry point to the system, inherits the shared location context graphs automatically, and immediately becomes queryable in cross-disease comparison without restructuring the existing architecture.

---

## **Current Coverage**

Two diseases mapped — Myocardial Infarction and Asthma — across two location contexts (Cardiovascular, Respiratory), 23 classified edges, 0 unclassified. The architecture is validated for cross-disease querying and ready for extension to COPD, Eczema, Stroke, and further diseases sharing the existing location contexts.
