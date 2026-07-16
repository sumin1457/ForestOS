import requests

# ── Configuration ─────────────────────────────────────────────────────────────

QUERY_ENDPOINT  = "http://localhost:7200/repositories/forestos_v4_20260714"
UPDATE_ENDPOINT = "http://localhost:7200/repositories/forestos_v4_20260714/statements"

PREFIX = "PREFIX : <http://www.semanticweb.org/sumin/ontologies/2026/5/forestos-ontology-3#>"
RDFS   = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>"

# Location string → named graph IRI
# Add new locations here as new diseases are mapped
LOCATION_TO_GRAPH = {
    "Respiratory":    "http://forestos/context/Respiratory",
    "Cardiovascular": "http://forestos/context/Cardiovascular",
    "Renal":          "http://forestos/context/Renal",
    "Neural":         "http://forestos/context/Neural",
    "Skin":           "http://forestos/context/Skin",
}

# Location system class IRI → location string
# Used to classify Type A nodes (location already in TBox)
LOCATION_CLASSES = {
    "http://www.semanticweb.org/sumin/ontologies/2026/5/forestos-ontology-3#Respiratory_System":    "Respiratory",
    "http://www.semanticweb.org/sumin/ontologies/2026/5/forestos-ontology-3#Cardiovascular_System": "Cardiovascular",
    "http://www.semanticweb.org/sumin/ontologies/2026/5/forestos-ontology-3#Renal_System":          "Renal",
    "http://www.semanticweb.org/sumin/ontologies/2026/5/forestos-ontology-3#Neural_Substrate":      "Neural",
}


# ── Query Functions ────────────────────────────────────────────────────────────

def get_homeostasis_to_deviation_edges():
    """
    Step 1 — L2/L3 → L1 bridge edges (homeostasis → deviation).
    Finds all edges where:
        source = L2 (biochemical) or L3 (immune) node
        target = L1 (infrastructure/tissue) node
    These are the edges where homeostatic machinery
    causes tissue-level pathological consequences.
    """
    query = f"""
    {PREFIX}
    {RDFS}

    SELECT DISTINCT ?source ?prop ?target WHERE {{

        # Source must be L2 or L3 (homeostatic base)
        ?source rdf:type ?sourceClass .
        ?sourceClass rdfs:subClassOf* ?sourceLayer .
        VALUES ?sourceLayer {{
            :L2_Hormone_and_biochemical_signalling
            :L3_Immune
        }}

        # Edge between source and target
        VALUES ?prop {{
            :increases :inhibits :targets :modulates
        }}
        ?source ?prop ?target .

        # Target must be L1 (deviation consequence)
        ?target rdf:type ?targetClass .
        ?targetClass rdfs:subClassOf* :L1_Infrastructure .
    }}
    """
    return _run_edge_query(query, label="L2/L3 → L1")


def get_l1_to_symptom_edges():
    """
    Step 2 — L1 → symptom edges (deviation → clinical surface).
    Finds all leads_to edges from L1 tissue nodes
    to Clinical_Manifestation nodes.
    These are location-specific — same symptom can arise
    from different tissue contexts.
    """
    query = f"""
    {PREFIX}
    {RDFS}

    SELECT DISTINCT ?source ?prop ?target WHERE {{

        # Source must be L1 (tissue/infrastructure)
        ?source rdf:type ?sourceClass .
        ?sourceClass rdfs:subClassOf* :L1_Infrastructure .

        VALUES ?prop {{ :leads_to }}
        ?source ?prop ?target .

        # Target must be Clinical_Manifestation
        ?target rdf:type ?targetClass .
        ?targetClass rdfs:subClassOf* :Clinical_Manifestation .
    }}
    """
    return _run_edge_query(query, label="L1 → symptom")


def get_l1_to_l1_edges():
    """
    Step 3 — L1 → L1 progression edges (acute → chronic).
    Finds all progresses_to edges within the L1 layer.
    These capture chronic disease progression:
        Bronchoconstriction → Airway_Remodelling
        Ischaemia → Necrosis
    Location classified by source node.
    """
    query = f"""
    {PREFIX}
    {RDFS}

    SELECT DISTINCT ?source ?prop ?target WHERE {{

        # Source must be L1
        ?source rdf:type ?sourceClass .
        ?sourceClass rdfs:subClassOf* :L1_Infrastructure .

        VALUES ?prop {{ :progresses_to }}
        ?source ?prop ?target .

        # Target must also be L1
        ?target rdf:type ?targetClass .
        ?targetClass rdfs:subClassOf* :L1_Infrastructure .
    }}
    """
    return _run_edge_query(query, label="L1 → L1 progression")


def _run_edge_query(query, label):
    """
    Internal helper — runs a SELECT query and returns
    list of {source, prop, target} dicts.
    """
    response = requests.get(
        QUERY_ENDPOINT,
        params={"query": query},
        headers={"Accept": "application/sparql-results+json"}
    )
    edges = []
    for row in response.json()['results']['bindings']:
        edges.append({
            'source': row['source']['value'],
            'prop':   row['prop']['value'],
            'target': row['target']['value']
        })
    print(f"Found {len(edges)} {label} edges")
    return edges


# ── Classification ─────────────────────────────────────────────────────────────

def get_node_location(node_iri):
    """
    Returns location string for a node using two strategies:

    Priority 1 — TBox class membership (Type A nodes):
        Node SubClassOf Respiratory_System → "Respiratory"
        Node SubClassOf Cardiovascular_System → "Cardiovascular"
        Already encoded in class hierarchy, no assertion needed.

    Priority 2 — occursIn data property (Universal_Process nodes):
        Ischaemia_endocardium_instance :occursIn "Cardiovascular"
        Minimal ABox expansion — one instance per location context.

    Returns None if node is truly universal (no location context).
    """
    query = f"""
    {PREFIX}
    {RDFS}

    SELECT DISTINCT ?locationClass ?occursIn WHERE {{

        # Priority 1 — location in TBox class hierarchy
        OPTIONAL {{
            <{node_iri}> rdf:type ?nodeClass .
            ?nodeClass rdfs:subClassOf* ?locationClass .
            VALUES ?locationClass {{
                :Respiratory_System
                :Cardiovascular_System
                :Renal_System
                :Neural_Substrate
            }}
        }}

        # Priority 2 — occursIn data property (Universal_Process)
        OPTIONAL {{
            <{node_iri}> :occursIn ?occursIn .
        }}
    }}
    """

    response = requests.get(
        QUERY_ENDPOINT,
        params={"query": query},
        headers={"Accept": "application/sparql-results+json"}
    )

    for row in response.json()['results']['bindings']:
        # Priority 1 — TBox location class
        if 'locationClass' in row:
            loc_class = row['locationClass']['value']
            if loc_class in LOCATION_CLASSES:
                return LOCATION_CLASSES[loc_class]
        # Priority 2 — occursIn data property
        if 'occursIn' in row:
            return row['occursIn']['value']

    return None  # Truly universal — stays in default graph only


# ── Insertion ──────────────────────────────────────────────────────────────────

def insert_edge_into_context(source, prop, target, graph_iri):
    """
    Inserts one edge into a named graph context.
    Does NOT remove the edge from the default graph —
    default graph remains the single source of truth (Protégé export).
    Named graph holds a copy for scoped querying.
    """
    update = f"""
    INSERT DATA {{
        GRAPH <{graph_iri}> {{
            <{source}> <{prop}> <{target}> .
        }}
    }}
    """
    response = requests.post(
        UPDATE_ENDPOINT,
        data={"update": update},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.status_code


# ── Orchestration ──────────────────────────────────────────────────────────────

def classify_and_insert(edges, classify_by="target"):
    """
    Classifies each edge by the location of the node
    indicated by classify_by ("source" or "target"),
    then inserts into the correct named graph.

    classify_by="target"  → used for L2/L3→L1 (target has location)
    classify_by="source"  → used for L1→symptom and L1→L1 (source has location)
    """
    classified   = {}
    unclassified = []

    for edge in edges:
        node_to_classify = edge[classify_by]
        location = get_node_location(node_to_classify)

        if location and location in LOCATION_TO_GRAPH:
            graph_iri = LOCATION_TO_GRAPH[location]
            insert_edge_into_context(
                edge['source'], edge['prop'], edge['target'], graph_iri
            )
            if graph_iri not in classified:
                classified[graph_iri] = []
            s = edge['source'].split('#')[1]
            p = edge['prop'].split('#')[1]
            o = edge['target'].split('#')[1]
            classified[graph_iri].append(f"{s} {p} {o}")

        else:
            s = edge['source'].split('#')[1]
            o = edge['target'].split('#')[1]
            unclassified.append(f"{s} → {o}")

    # Report
    for graph_iri, edge_list in classified.items():
        graph_name = graph_iri.split('/')[-1]
        print(f"\n  {graph_name} ({len(edge_list)} edges):")
        for e in edge_list:
            print(f"      {e}")

    if unclassified:
        print(f"\n  Unclassified (universal, no location): {len(unclassified)}")
        for e in unclassified:
            print(f"      {e}")


def build_location_context_graphs():
    """
    Builds all Forest OS location context named graphs.

    Three steps reflecting the Disease-as-Deviation model:

    Step 1 — L2/L3 → L1 (homeostasis → deviation bridge)
        Where biochemical/immune machinery causes tissue pathology.
        Classified by TARGET node location.

    Step 2 — L1 → symptom (deviation → clinical surface)
        Where tissue pathology produces observable symptoms.
        Classified by SOURCE node location.

    Step 3 — L1 → L1 (acute → chronic progression)
        Where acute pathology progresses to chronic structural disruption.
        Classified by SOURCE node location.
    """
    print("=" * 60)
    print("  Forest OS — Disease-as-Deviation Graph Builder")
    print("=" * 60)

    print("\nStep 1: L2/L3 → L1 edges (homeostasis → deviation)")
    bridge_edges = get_homeostasis_to_deviation_edges()
    classify_and_insert(bridge_edges, classify_by="target")

    print("\nStep 2: L1 → symptom edges (deviation → clinical surface)")
    symptom_edges = get_l1_to_symptom_edges()
    classify_and_insert(symptom_edges, classify_by="source")

    print("\nStep 3: L1 → L1 progression edges (acute → chronic)")
    progression_edges = get_l1_to_l1_edges()
    classify_and_insert(progression_edges, classify_by="source")

    print("\n" + "=" * 60)
    print("  Context graphs complete.")
    print("=" * 60)


def rebuild_all_graphs():
    """
    Entry point — drops all existing context graphs
    and rebuilds from scratch.

    Run after every Protégé re-export to keep
    context graphs in sync with the ontology.
    """
    print("Dropping existing context graphs...")
    for graph_iri in LOCATION_TO_GRAPH.values():
        requests.post(
            UPDATE_ENDPOINT,
            data={"update": f"DROP SILENT GRAPH <{graph_iri}>"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
    print("Done.\n")
    build_location_context_graphs()


# ── Run ────────────────────────────────────────────────────────────────────────

rebuild_all_graphs()
