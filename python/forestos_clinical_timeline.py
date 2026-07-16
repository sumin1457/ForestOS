import requests

# ── Configuration ──────────────────────────────────────────────
QUERY_ENDPOINT = "http://localhost:7200/repositories/forestos_v4_20260714"
PREFIX = "PREFIX : <http://www.semanticweb.org/sumin/ontologies/2026/5/forestos-ontology-3#>"
RDFS   = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>"

# ── Query functions  ────────────────────────────────────

def get_symptom_timeline(disease_instance, location_graph):
    """
    Classifies symptoms as acute or chronic based on
    whether a time-dependent progression step (progresses_to)
    is required before the symptom manifests.

    acute:   L1 node leads_to symptom directly
             → immediate clinical presentation

    chronic: L1 node progresses_to structural change
             → structural change leads_to symptom
             → time-dependent, develops over weeks/months

    Uses progresses_to? (zero-or-one path) to detect
    whether progression occurred — a structurally-derived
    severity proxy without explicit severity assertions.
    """
    query = f"""
    {PREFIX}

    SELECT DISTINCT ?mid ?progressionNode ?symptom ?effectType WHERE {{

        :{disease_instance} (:has_etiology|:triggers)+ ?entry .

        ?entry (:increases|:inhibits|:targets|:modulates)* ?viaAcute .

        GRAPH <{location_graph}> {{
            ?viaAcute ?anyRel ?something .
            ?viaAcute :progresses_to* ?mid .
            ?mid :progresses_to? ?afterProgression .
            ?afterProgression :leads_to ?symptom .
        }}

        BIND(IF(?viaAcute = ?afterProgression, "acute", "chronic")
             AS ?effectType)

        BIND(IF(?viaAcute = ?afterProgression, "", ?afterProgression)
             AS ?progressionNode)

        FILTER(?mid != ?progressionNode)
    

    }}
    ORDER BY ?effectType 
    """

    response = requests.get(
        QUERY_ENDPOINT,
        params={"query": query},
        headers={"Accept": "application/sparql-results+json"}
    )

    acute_results   = []
    chronic_results = []

    for row in response.json()['results']['bindings']:
        via       = row['mid']['value'].split('#')[1]
        symptom   = row['symptom']['value'].split('#')[1]
        effect    = row['symptom']['value'] and row['effectType']['value']
        prog_node = row['progressionNode']['value']
        prog_clean = prog_node.split('#')[1] if '#' in prog_node else ''

        if row['effectType']['value'] == 'acute':
            acute_results.append((via, symptom))
        else:
            chronic_results.append((via, prog_clean, symptom))

    # Report
    print(f"\n{'='*55}")
    print(f"  Symptom Timeline — {disease_instance}")
    print(f"{'='*55}")

    print(f"\n  ACUTE (direct tissue → symptom):")
    if acute_results:
        for via, symptom in acute_results:
            print(f"      {via}  →  {symptom}")
    else:
        print(f"      none")

    print(f"\n  CHRONIC (tissue → progression → symptom):")
    if chronic_results:
        for via, prog, symptom in chronic_results:
            print(f"      {via}  →  {prog}  →  {symptom}")
    else:
        print(f"      none")

    print(f"\n  Acute symptoms:   {len(acute_results)}")
    print(f"  Chronic symptoms: {len(chronic_results)}")
    print(f"{'='*55}\n")

    return {
        'disease':  disease_instance,
        'acute':    acute_results,
        'chronic':  chronic_results
    }

# ── Symptom Timeline ──────────────────────────────────────────

print("\n--- Asthma symptom timeline ---")
get_symptom_timeline(
    "Asthma_instance",
    "http://forestos/context/Respiratory"
)

print("\n--- MI symptom timeline ---")
get_symptom_timeline(
    "MI_instance",
    "http://forestos/context/Cardiovascular"
)



   
