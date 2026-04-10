import time
from collections import deque

import numpy as np


class MetricsCollector:
    """In-memory sliding-window metrics for latency and retrieval hit-rate."""

    def __init__(self, maxlen: int = 1000, hit_threshold: float = 0.35):
        self._buffer: deque[dict] = deque(maxlen=maxlen)
        self.hit_threshold = hit_threshold

    def record(
        self,
        total_latency_ms: float,
        embedding_latency_ms: float,
        search_latency_ms: float,
        top1_score: float,
        top_k: int,
        similarity: str,
    ):
        self._buffer.append(
            {
                "timestamp": time.time(),
                "total_latency_ms": total_latency_ms,
                "embedding_latency_ms": embedding_latency_ms,
                "search_latency_ms": search_latency_ms,
                "top1_score": top1_score,
                "top_k": top_k,
                "similarity": similarity,
            }
        )

    def summary(self) -> dict:
        if not self._buffer:
            return {"total_queries": 0, "message": "No queries recorded yet"}

        entries = list(self._buffer)
        latencies = np.array([e["total_latency_ms"] for e in entries])
        emb_latencies = np.array([e["embedding_latency_ms"] for e in entries])
        top1_scores = np.array([e["top1_score"] for e in entries])

        hits = sum(1 for s in top1_scores if s >= self.hit_threshold)

        return {
            "total_queries": len(entries),
            "latency_p50_ms": round(float(np.percentile(latencies, 50)), 2),
            "latency_p95_ms": round(float(np.percentile(latencies, 95)), 2),
            "latency_p99_ms": round(float(np.percentile(latencies, 99)), 2),
            "embedding_latency_p50_ms": round(float(np.percentile(emb_latencies, 50)), 2),
            "hit_rate": round(hits / len(entries), 4),
            "avg_top1_score": round(float(np.mean(top1_scores)), 4),
            "window_start": entries[0]["timestamp"],
            "window_end": entries[-1]["timestamp"],
        }


metrics = MetricsCollector()
