from typing import Protocol, List, Dict, Any

class ClaimScorer(Protocol):
    def score_batch(self, candidates: List[Dict[str, Any]]) -> List[float]:
        ...

