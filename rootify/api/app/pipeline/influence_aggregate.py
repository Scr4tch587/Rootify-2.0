def aggregate_influence(candidates):
    weights = {"direct": 3.0, "strong": 2.0, "weak": 0.5}

    buckets = {}
    for c in candidates:
        name = c["influence_artist"]
        buckets.setdefault(name, []).append(c)
    
    def item_rank(it):
        return (-weights.get(it["pattern_type"], 0.0), it["section_path"], it["snippet"])
    
    out = []
    for name, items in buckets.items():
        score = sum(
            weights.get(it["pattern_type"], 0.0) * it.get("claim_probability", 1.0)
            for it in items
        )
        score = round(score, 3)
        items_sorted = sorted(items, key=item_rank)

        evidence = [
            {
                "section_path": it["section_path"],
                "snippet": it["snippet"],
                "pattern_type": it["pattern_type"],
            }
            for it in items_sorted
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