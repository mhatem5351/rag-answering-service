# RAG Answering Service: Design Decisions & Trade-offs

*Markdown version of [RAG_Service_Design_Doc.docx](RAG_Service_Design_Doc.docx).*

## Architecture Overview

A minimal FastAPI service that retrieves relevant snippets from a 12-document Kubernetes corpus using OpenAI embeddings (text-embedding-3-small) and returns a naive answer composed from the top-k results. No LLM generation step — the "answer" is assembled directly from retrieved snippets, keeping costs zero and latency predictable.

**Files:**

| File | Role |
|---|---|
| `corpus.py` | 12 hand-written Kubernetes snippets |
| `embeddings.py` | OpenAI embedding calls + VectorIndex (cosine / dot) |
| `guardrail.py` | Denylist + query-length filter |
| `metrics.py` | In-memory latency & hit-rate tracking |
| `main.py` | FastAPI endpoints: /answer, /compare, /metrics, /health |
| `config.py` | Settings via pydantic-settings + .env |
| `test_compare.py` | Comparison script exercising 5 targeted queries |

## Guardrail: Denylist + Query-Length Limiter

**What it does:** Before any embedding or retrieval, the guardrail rejects queries that:

1. Contain known prompt-injection phrases ("ignore previous instructions", "system prompt", "jailbreak", "DROP TABLE", `<script>`, etc.)
2. Exceed 500 characters
3. Are empty

**Why this guardrail is practical:**

- **Zero additional latency** — runs before any API call or vector computation, so clean queries pay no cost.
- **Covers real attack vectors** — prompt injection is the #1 threat against LLM-adjacent APIs. SQL injection and XSS probes are cheap to block at the boundary.
- **Budget protection** — the length cap prevents abuse where an attacker sends 10KB queries to burn embedding tokens.
- **Easy to extend** — adding terms is a config change, not a code change. In production, the denylist lives in a config file or feature flag service.

**Trade-off acknowledged:** A regex denylist is bypassable by a determined attacker (Unicode tricks, rephrasing). A more robust guardrail would use a classifier model, but that adds latency and complexity. For a production-minded prototype, a denylist is the right first guardrail — it catches the low-hanging fruit cheaply.

## Index Comparison: Cosine vs Dot-Product

### Setup

Two `VectorIndex` instances are built from the **same** embedding vectors (one OpenAI API call for the corpus). The cosine index L2-normalizes vectors at index time; the dot index stores raw vectors. At query time, both use a dot product — the normalization makes them semantically different.

### Results from test_compare.py (5 queries)

| Query | Cosine Top-1 | Dot Top-1 | Agreement? |
|---|---|---|---|
| How do I scale my application automatically? | k8s_08 (HPA) 0.41 | k8s_08 (HPA) 0.41 | YES |
| What is the best way to store database passwords? | k8s_06 (Secrets) 0.40 | k8s_06 (Secrets) 0.40 | YES |
| How does traffic reach my containers from outside? | k8s_09 (Ingress) 0.42 | k8s_09 (Ingress) 0.42 | YES |
| How do I manage configuration across environments? | k8s_05 (ConfigMaps) 0.45 | k8s_05 (ConfigMaps) 0.45 | YES |
| What happens when a container crashes? | k8s_10 (Probes) 0.36 | k8s_10 (Probes) 0.36 | YES |

### Key observations

1. **Top-1 ranking always agrees.** OpenAI's text-embedding-3-small produces embeddings with near-uniform L2 norms, so normalizing has negligible effect on ranking order.
2. **Score magnitudes are nearly identical** for this embedding model. With models that produce variable-norm embeddings (e.g., older word2vec or sentence-transformers), dot-product scores would diverge significantly.
3. **Score spread increases with k.** Going from k=3 to k=5 roughly doubles the spread (e.g., 0.10 → 0.18 for the scaling query). The extra results bring in less-relevant snippets, widening the gap.
4. **k=3 vs k=5 trade-off:** k=3 returns tighter, more relevant results. k=5 adds context but includes weaker matches (scores drop below 0.20 in some cases). For a production system with a downstream LLM, k=3 gives a better signal-to-noise ratio; k=5 is useful when recall matters more than precision.

### Recommendation

**Cosine with k=3** is the default choice because:

- Scores are bounded [−1, 1], making threshold-based decisions (like hit-rate) interpretable and portable.
- k=3 avoids diluting context with low-relevance snippets.
- If a downstream LLM is added later, fewer but better snippets reduce hallucination risk.

## Monitoring Metrics

### 1. Query Latency (P50 / P95 / P99)

**What:** End-to-end time from request receipt to response, split into embedding latency and search latency.

**Why it matters:** Embedding latency dominates (50–200ms per OpenAI call) while search is microseconds for 12 vectors. If P95 spikes, you know immediately whether it's the external API degrading or your own code.

**How tracked:** In-memory `collections.deque(maxlen=1000)` circular buffer. Each request appends `{total_latency_ms, embedding_latency_ms, search_latency_ms}`. The `/metrics` endpoint computes percentiles via `numpy.percentile`.

**Production path:** Emit these as Prometheus histograms or Datadog distributions. Set alerts on P95 > 500ms.

### 2. Retrieval Hit-Rate

**What:** Fraction of queries where the top-1 similarity score exceeds a threshold (default: 0.35 for cosine).

**Why it matters:** Hit-rate is a proxy for retrieval quality without needing labeled relevance judgments. If users start asking questions the corpus doesn't cover, hit-rate drops — signaling you need to expand the corpus. It also detects embedding model drift after provider updates.

**How tracked:** Same deque buffer. Each entry records `top1_score`. The summary computes `hits / total` where `hits = count(top1_score >= threshold)`.

**Production path:** Track weekly rolling hit-rate. A 10%+ drop triggers a corpus review. Combine with query logging to identify the most common "miss" topics.

## Running the Service

```bash
# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
cp .env.example .env  # then edit with your key
# or: export OPENAI_API_KEY="sk-..."

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8321

# Test
curl -X POST http://localhost:8321/answer \
  -H 'Content-Type: application/json' \
  -d '{"query": "how do I scale pods?"}'

# Compare index configs
curl -X POST http://localhost:8321/compare \
  -H 'Content-Type: application/json' \
  -d '{"query": "how do I scale pods?", "top_k_values": [3, 5]}'

# Check metrics
curl http://localhost:8321/metrics

# Run full comparison
python test_compare.py
```
