def aggregate_influence(candidates):
    weights = {"direct": 3.0, "strong": 2.0, "weak": 1.0}

    buckets = {}
    for c in candidates:
        name = c["influence_artist"]
        buckets.setdefault(name, []).append(c)
    
    out = []
    for name, items in buckets.items():
        score = 0.0
        for it in items:
            score += weights.get(it["pattern_type"], 0.0)

        evidence = [
            {
                "section_path": it["section_path"],
                "snippet": it["snippet"],
                "pattern_type": it["pattern_type"],
            }
            for it in items
        ]

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