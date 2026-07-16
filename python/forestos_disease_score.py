import requests

# ── Configuration ──────────────────────────────────────────────
QUERY_ENDPOINT = "http://localhost:7200/repositories/forestos_v4_20260714"
PREFIX = "PREFIX : <http://www.semanticweb.org/sumin/ontologies/2026/5/forestos-ontology-3#>"
RDFS   = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>"

# ── Query functions  ────────────────────────────────────

def get_disease_stage_score(disease_instance, location_graph):
    """
    Forest OS Disease Stage Score — full profile for a disease.
    
    Computes three dimensions from ontology structure alone:
    
    1. Cascade Depth   — cascade steps from disease entry to L1 tissue damage
                       lower = faster onset, smaller therapeutic window (NOTE:
                       Intended to be acute depth, however reach limitation. Check
                       explanation file.)
    
    2. Chronic Depth — progression stages after tissue damage
                       higher = more established disease, harder to reverse
    
    3. Stage Score   — acute_depth × chronic_depth
                       combined disease burden measure
    """

    print(f"\n{'='*55}")
    print(f"  Forest OS Disease Stage Score — {disease_instance}")
    print(f"{'='*55}")

    # ── cascade_complexity ───────────────────────────────────────────
    cascade_query = f"""
    {PREFIX}
    {RDFS}

    SELECT DISTINCT ?l1node (COUNT(DISTINCT ?step) AS ?acuteDepth) WHERE {{

        :{disease_instance}
            (:has_etiology|:triggers)+ ?entry .

        ?entry (:increases|:inhibits|:targets|
                :modulates)+ ?step .
        ?step  (:increases|:inhibits|:targets|
                :modulates)* ?l1node .

        ?l1node rdf:type ?l1class .
        ?l1class rdfs:subClassOf* :L1_Infrastructure .

        GRAPH <{location_graph}> {{
            ?l1node ?anyProp ?anyObj .
        }}

    }} GROUP BY ?l1node ORDER BY ?acuteDepth
    """

    response = requests.get(
        QUERY_ENDPOINT,
        params={"query": cascade_query},
        headers={"Accept": "application/sparql-results+json"}
    )

    cascade_results = []
    for row in response.json()['results']['bindings']:
        node  = row['l1node']['value'].split('#')[1]
        depth = int(row['acuteDepth']['value'])
        cascade_results.append((node, depth))

    # ── Chronic depth ─────────────────────────────────────────
    chronic_query = f"""
    {PREFIX}

    SELECT DISTINCT ?node (COUNT(DISTINCT ?mid) AS ?chronicDepth) WHERE {{

        :{disease_instance}
            (:has_etiology|:targets)+ ?entry .

        ?entry (:increases|:inhibits|:targets|
                :modulates)* ?viaAcute .

        GRAPH <{location_graph}> {{
            FILTER EXISTS {{ ?viaAcute :progresses_to+ ?any . }}
            ?viaAcute :progresses_to+ ?mid .
            ?mid :progresses_to* ?node .
        }}

    }} GROUP BY ?node ORDER BY ?chronicDepth
    """

    response = requests.get(
        QUERY_ENDPOINT,
        params={"query": chronic_query},
        headers={"Accept": "application/sparql-results+json"}
    )

    chronic_results = []
    for row in response.json()['results']['bindings']:
        node  = row['node']['value'].split('#')[1]
        depth = int(row['chronicDepth']['value'])
        chronic_results.append((node, depth))

    # ── Compute stage score ───────────────────────────────────
    max_cascade   = max([d for _, d in cascade_results],   default=0)
    max_chronic = max([d for _, d in chronic_results], default=0)
    stage_score = max_cascade + max_chronic

    # ── Report ────────────────────────────────────────────────
    print(f"\n  Casecade depth (entry → tissue damage):")
    for node, depth in cascade_results:
        print(f"      {node}  →  depth {depth}")

    print(f"\n  Chronic depth (tissue damage → structural consequence):")
    for node, depth in chronic_results:
        print(f"      {node}  →  stage {depth}")

    print(f"\n  Max cascade depth:    {max_cascade}")
    print(f"  Max chronic depth:  {max_chronic}")
    print(f"  Stage score:        {max_cascade} + {max_chronic} = {stage_score}")
    print(f"{'='*55}\n")

    return {
        'disease':        disease_instance,
        'cascade_complexity':          cascade_results,
        'chronic':        chronic_results,
        'max_cascade':      max_cascade,
        'max_chronic':    max_chronic,
        'stage_score':    stage_score
    }

# ── Run ───────────────────────────────────────────────────────

asthma = get_disease_stage_score(
    "Asthma_instance",
    "http://forestos/context/Respiratory"
)

mi = get_disease_stage_score(
    "MI_instance",
    "http://forestos/context/Cardiovascular"
)

# ── Comparison ────────────────────────────────────────────────
print("  Comparison:")
print(f"  {'Disease':<20} {'cascade_complexity':>8} {'Chronic':>10} {'Score':>8}")
print(f"  {'-'*48}")
for result in [asthma, mi]:
    print(f"  {result['disease']:<20} "
          f"{result['max_cascade']:>8} "
          f"{result['max_chronic']:>10} "
          f"{result['stage_score']:>8}")
