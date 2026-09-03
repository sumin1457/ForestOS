import requests

# ── Configuration ──────────────────────────────────────────────────────────────

QUERY_ENDPOINT  = "http://localhost:7200/repositories/REPONAME"
UPDATE_ENDPOINT = "http://localhost:7200/repositories/REPONAME/statements"

PREFIX = "PREFIX : <http://www.semanticweb.org/sumin/ontologies/2026/5/forestos-ontology-3#>"
RDFS   = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>"

# State named graph IRIs
STATE_GRAPHS = {
    "Homeostatic":     "http://forestos/state/homeostatic",
    "Physiological":   "http://forestos/state/physiological",
    "Pathological":    "http://forestos/state/pathological",
    "Pharmacological": "http://forestos/state/pharmacological",   # NEW
}

# ── Predicate sets ──────────────────────────────────────────────────────────────
#
# CHANGED FROM v1_3:
# Previously state was inferred by traversing generic props (causes, binds,
# etc.) downstream from root nodes. That approach can leak edges across
# states through shared/neutral scaffolding nodes (System_Event_Logic nodes,
# feedback edges) that don't themselves carry hasSystemState.
#
# New approach: membership is asserted, not inferred. A node belongs to a
# state graph if it has hasSystemState "X" asserted directly. Edges are
# assigned SOURCE-ANCHORED — an edge goes into graph X if its SOURCE node
# has hasSystemState "X", regardless of whether the target is tagged.
# This mirrors get_state_cascade_edges from v1_3 but drops the downstream
# traversal entirely — no ?prop+ path, no risk of crossing into another
# state's territory through a neutral node.
#
# SELF-DESCRIBING predicates (resolves_to, mimics, deviates_into,
# switches_on/off, balances_to, restores) are handled separately — see
# SELF_DESCRIBING_PROPS below. These are asserted into their graph based on
# the predicate itself, not on hasSystemState, because the predicate is
# unambiguous about which state it belongs to (except switches_on/off,
# which is ambiguous and stays source-anchored like the generic props).

GENERIC_PROPS = [
    "causes", "activates", "suppresses", "requires", "binds", "increases",
    "inhibits", "activates_transcription", "is_translated_into", "represses_transcription"
]

# Pathological also carries symptom/progression edges
PATHOLOGICAL_EXTRA_PROPS = ["leads_to", "progresses_to"]

# Self-describing predicates: predicate alone tells you the state.
# Asserted directly into their graph, no hasSystemState check needed.
SELF_DESCRIBING_PROPS = {
    "Physiological":   ["balances_to", "balances", "restores"],       # State 1 — recovery/resolution
    "Pathological":    ["deviates_into", "mimics"],         # State 2 — false trigger / transition
    "Pharmacological": ["resolves_to"],                     # State 3 — drug closes the loop
}

# Ambiguous predicate — appears across states 0/1/2 depending on which node
# is switching. Stays source-anchored via hasSystemState like GENERIC_PROPS.
SWITCH_PROPS = ["switches_on", "switches_off"]

# Data properties to preserve in named graphs
DATA_PROPS = [
    "occursIn", "hasRateState", "hasRegulatoryTone",
    "hasFiringRate", "hasSystemState",
    "hasDiscreteState", "hasAccessibilityState"
]


# ── Helpers ────────────────────────────────────────────────────────────────────

def sparql_query(query):
    response = requests.get(
        QUERY_ENDPOINT,
        params={"query": query},
        headers={"Accept": "application/sparql-results+json"}
    )
    return response.json()['results']['bindings']


def sparql_update(update):
    response = requests.post(
        UPDATE_ENDPOINT,
        data={"update": update},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return response.status_code


def bulk_insert(edges, graph_iri):
    """
    Insert edges into a named graph.
    Handles both IRI objects and literal objects.
    """
    if not edges:
        return 0

    triples = ""
    for edge in edges:
        target = edge['target']
        if edge.get('is_literal'):
            target_escaped = target.replace('"', '\\"')
            triples += f'        <{edge["source"]}> <{edge["prop"]}> "{target_escaped}" .\n'
        else:
            triples += f'        <{edge["source"]}> <{edge["prop"]}> <{target}> .\n'

    update = f"""
    INSERT DATA {{
        GRAPH <{graph_iri}> {{
{triples}
        }}
    }}
    """
    status = sparql_update(update)
    graph_name = graph_iri.split('/')[-1]
    print(f"    → {graph_name}: {len(edges)} edges (status {status})")
    return len(edges)


def clean_iri(iri):
    return iri.split('#')[1] if '#' in iri else iri.split('/')[-1]


def make_prop_values(props):
    return " ".join([f":{p}" for p in props])


# ── Query functions ────────────────────────────────────────────────────────────

def get_state_root_iris(system_state):
    """
    Get IRIs of all instances with hasSystemState = system_state.
    These are now the FULL membership of the graph, not just entry points —
    no downstream traversal happens beyond this set.
    """
    query = f"""
    {PREFIX}

    SELECT DISTINCT ?instance WHERE {{
        ?instance :hasSystemState "{system_state}" .
    }}
    """
    rows = sparql_query(query)
    iris = [r['instance']['value'] for r in rows]
    print(f"  {system_state} tagged nodes: {len(iris)}")
    return iris


def get_source_anchored_edges(system_state, props):
    """
    Get direct edges FROM nodes tagged hasSystemState = system_state.
    Source-anchored: target does not need to be tagged. This replaces
    v1_3's get_state_cascade_edges + get_downstream_from_nodes — no
    multi-hop traversal, so an edge can't cross into another state's
    graph through an untagged neutral node.
    """
    query = f"""
    {PREFIX}

    SELECT DISTINCT ?source ?prop ?target WHERE {{
        ?source :hasSystemState "{system_state}" .
        VALUES ?prop {{ {make_prop_values(props)} }}
        ?source ?prop ?target .
    }}
    """
    rows = sparql_query(query)
    edges = [{'source': r['source']['value'],
               'prop':   r['prop']['value'],
               'target': r['target']['value'],
               'is_literal': False} for r in rows]
    print(f"  {system_state} source-anchored edges: {len(edges)}")
    return edges


def get_self_describing_edges(props):
    """
    Get ALL edges using a self-describing predicate (resolves_to, mimics,
    deviates_into, balances_to, restores). No hasSystemState check —
    the predicate alone determines which graph these belong to.
    """
    if not props:
        return []
    query = f"""
    {PREFIX}

    SELECT DISTINCT ?source ?prop ?target WHERE {{
        VALUES ?prop {{ {make_prop_values(props)} }}
        ?source ?prop ?target .
    }}
    """
    rows = sparql_query(query)
    edges = [{'source': r['source']['value'],
               'prop':   r['prop']['value'],
               'target': r['target']['value'],
               'is_literal': False} for r in rows]
    print(f"  self-describing edges ({', '.join(props)}): {len(edges)}")
    return edges


def get_data_properties_for_graph(graph_iri):
    """
    Pass 2 — post-insert data property sweep.
    Unchanged from v1_3: after structural edges are inserted, find all
    subject nodes in the named graph and fetch their data properties from
    the default graph. Still needed for neutral/untagged nodes that appear
    only as edge targets (e.g. NO_instance, PGI2_instance, SCAP if untagged).
    """
    query = f"""
    {PREFIX}

    SELECT DISTINCT ?instance ?prop ?value WHERE {{

        GRAPH <{graph_iri}> {{
            ?instance ?anyProp ?anyObj .
        }}

        VALUES ?prop {{ {make_prop_values(DATA_PROPS)} }}
        ?instance ?prop ?value .
    }}
    """
    rows = sparql_query(query)
    edges = []
    for r in rows:
        val      = r['value']['value']
        val_type = r['value'].get('type', 'uri')
        edges.append({
            'source':     r['instance']['value'],
            'prop':       r['prop']['value'],
            'target':     val,
            'is_literal': val_type == 'literal'
        })
    graph_name = graph_iri.split('/')[-1]
    print(f"  Data property sweep ({graph_name}): {len(edges)}")
    return edges


# ── Main builder ───────────────────────────────────────────────────────────────

def build_state_graph(system_state, graph_iri, extra_generic_props=None,
                       self_describing_props=None):
    """
    Build a single state named graph.

    Pass 1 — structural edges:
        Source-anchored generic + switch edges from tagged nodes
        Self-describing edges (resolves_to/mimics/deviates_into/balances_to/restores)

    Pass 2 — data property sweep:
        All nodes now in graph queried for hasSystemState etc. from default
        graph, to catch untagged nodes reached only as edge targets.
    """
    print(f"\n[ {system_state} — Pass 1: structural edges ]")

    generic_props = GENERIC_PROPS + SWITCH_PROPS + (extra_generic_props or [])
    source_edges  = get_source_anchored_edges(system_state, generic_props)
    self_edges    = get_self_describing_edges(self_describing_props or [])

    total_inserted = bulk_insert(source_edges + self_edges, graph_iri)

    print(f"[ {system_state} — Pass 2: data property sweep ]")
    data_edges = get_data_properties_for_graph(graph_iri)
    total_inserted += bulk_insert(data_edges, graph_iri)

    return total_inserted


def build_state_graphs():
    print("\n" + "=" * 60)
    print("  Forest OS — State Graph Builder (v2, node-property membership)")
    print("=" * 60)

    total = 0

    total += build_state_graph(
        "Homeostatic", STATE_GRAPHS["Homeostatic"])

    total += build_state_graph(
        "Physiological", STATE_GRAPHS["Physiological"],
        self_describing_props=SELF_DESCRIBING_PROPS["Physiological"])

    total += build_state_graph(
        "Pathological", STATE_GRAPHS["Pathological"],
        extra_generic_props=PATHOLOGICAL_EXTRA_PROPS,
        self_describing_props=SELF_DESCRIBING_PROPS["Pathological"])

    total += build_state_graph(
        "Pharmacological", STATE_GRAPHS["Pharmacological"],
        self_describing_props=SELF_DESCRIBING_PROPS["Pharmacological"])

    print(f"\n{'=' * 60}")
    print(f"  Complete. Total triples inserted: {total}")
    print(f"{'=' * 60}\n")


# ── Rebuild ────────────────────────────────────────────────────────────────────

def rebuild_state_graphs():
    """
    Drop all existing state graphs and rebuild from scratch.
    Run after every Protégé re-export.
    """
    print("Dropping existing state graphs...")
    for name, graph_iri in STATE_GRAPHS.items():
        status = sparql_update(f"DROP SILENT GRAPH <{graph_iri}>")
        print(f"  Dropped {name} (status {status})")
    print("Done.")
    build_state_graphs()


# ── Verify ─────────────────────────────────────────────────────────────────────

def verify_state_graphs():
    """
    Count triples in each state graph after rebuild.
    Also shows a sample of edges per graph for spot-checking.
    """
    print("\n[ Verification ]")
    for name, graph_iri in STATE_GRAPHS.items():

        count_query = f"""
        SELECT (COUNT(*) AS ?count) WHERE {{
            GRAPH <{graph_iri}> {{ ?s ?p ?o }}
        }}
        """
        count = sparql_query(count_query)[0]['count']['value']
        print(f"\n  {name}: {count} triples")

        sample_query = f"""
        {PREFIX}

        SELECT ?s ?p ?o WHERE {{
            GRAPH <{graph_iri}> {{ ?s ?p ?o }}
        }} limit 5
        """
        rows = sparql_query(sample_query)
        for r in rows:
            s = clean_iri(r['s']['value'])
            p = clean_iri(r['p']['value'])
            o = clean_iri(r['o']['value'])
            print(f"    {s} → {p} → {o}")


# ── Run ────────────────────────────────────────────────────────────────────────

rebuild_state_graphs()
verify_state_graphs()
