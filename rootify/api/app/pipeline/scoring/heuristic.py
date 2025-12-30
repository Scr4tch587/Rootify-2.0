from typing import List, Dict, Any

class HeuristicScorer:
    def score_batch(self, candidates: List[Dict[str, Any]]) -> List[float]:
        heuristic_scores = []
        for candidate in candidates:
            pattern_type = candidate.get("pattern_type")
            if pattern_type:
                if pattern_type == "direct":
                    score = 0.95
                elif pattern_type == "strong":
                    score = 0.80
                elif pattern_type == "weak":
                    score = 0.55
                else:
                    score = 1.0
            else:
                score = 1.0

            if candidate.get("influence_artist") == candidate.get("artist_name"):
                score *= 0.2
            score = min(max(score, 0.05), 1.0)
            heuristic_scores.append(score)
        return heuristic_scores