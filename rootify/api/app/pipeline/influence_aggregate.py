def aggregate_influence(candidates):
    source_weights = {
        "wikipedia": 1.0,
        "youtube": 1.3,
        "wikidata": 0.8,
    }

    buckets = {}
    for c in candidates:
        name = c["influence_artist"]
        buckets.setdefault(name, []).append(c)

    def noisy_or(ps):
        prod = 1.0
        for p in ps:
            p = float(p)
            if p <= 0.0:
                continue
            if p >= 1.0:
                return 1.0
            prod *= (1.0 - p)
        return 1.0 - prod

    def item_rank(it):
        src = (it.get("source") or "").lower()
        sw = source_weights.get(src, 1.0)
        p = float(it.get("claim_probability", 1.0))
        return (-(sw * p), -p, it.get("section_path", ""), it.get("snippet", ""))

    out = []
    for name, items in buckets.items():
        by_source = {"wikipedia": [], "youtube": [], "wikidata": [], "_other": []}
        for it in items:
            src = (it.get("source") or "").lower()
            p = float(it.get("claim_probability", 1.0))
            if src in by_source:
                by_source[src].append(p)
            else:
                by_source["_other"].append(p)

        score = 0.0
        for src, ps in by_source.items():
            if not ps:
                continue
            sw = source_weights.get(src, 1.0)
            score += sw * noisy_or(ps)

        score = round(score, 3)
        items_sorted = sorted(items, key=item_rank)

        evidence = []
        for it in items_sorted:
            evidence.append(
                {
                    "source": it.get("source"),
                    "section_path": it.get("section_path"),
                    "snippet": it.get("snippet"),
                    "pattern_type": it.get("pattern_type"),
                    "claim_probability": float(it.get("claim_probability", 1.0)),
                }
            )

        out.append(
            {
                "influence_artist": name,
                "score": score,
                "evidence_count": len(items),
                "evidence": evidence[:3],
            }
        )

    out.sort(key=lambda x: (-x["score"], -x["evidence_count"], x["influence_artist"].lower()))
    return out
