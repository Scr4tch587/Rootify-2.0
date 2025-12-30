import httpx

query = """
SELECT DISTINCT ?influencer ?influencerLabel WHERE {
  wd:Q44190 wdt:P737 ?influencer .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}
"""

async def fetch_wikidata_qid(artist_name: str) -> dict[str, str]:
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",   
        "search": artist_name,
        "language": "en",  
        "format": "json",
        "limit": 1,
        "type": "item",
    }
    headers = {
        "User-Agent": "Rootify/0.1 (contact: k318zhang@gmail.com)",
        "Accept": "application/json",
    }
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    results = data.get("search", [])
    if not results:
        raise ValueError(f"Wikidata entry not found for: {artist_name}")
    top = results[0]
    qid = top["id"]
    if not qid:
        raise ValueError(f"Wikidata QID not found for: {artist_name}")
    label = top["label"]
    return {"qid": qid, "label": label}

async def fetch_wikidata_influences(qid: str) -> dict[str, str]:
    url = "https://query.wikidata.org/sparql"
    query = """
    SELECT DISTINCT ?influencer ?influencerLabel WHERE {
    wd:Q44190 wdt:P737 ?influencer .
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
    }
    """
    headers = {
        "User-Agent": "Rootify/0.1 (contact: k318zhang@gmail.com)",
        "Accept": "application/sparql-results+json",
    }
    params = {
        "query": query,
        "format": "json",
    }
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    
    bindings = data["results"]["bindings"]
    out = []
    for b in bindings:
        out.append({
            "influencer_qid": b["influencer"]["value"].rsplit("/", 1)[-1],
            "influencer_label": b["influencerLabel"]["value"],
        })
    return out  