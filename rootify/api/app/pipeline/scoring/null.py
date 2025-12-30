from typing import List, Dict, Any

class NullScorer:
    def score_batch(self, candidates: List[Dict[str, Any]]) -> List[float]:
        return [1.0] * len(candidates)