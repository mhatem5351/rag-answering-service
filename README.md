# RAG Answering Service

A minimal retrieval-augmented answering service built with FastAPI. Retrieves relevant snippets from a Kubernetes knowledge base using OpenAI embeddings and returns top-k results with a naive answer.

## Features

- **12-snippet Kubernetes corpus** covering Pods, Deployments, Services, Secrets, HPA, Ingress, RBAC, Helm, and more
- **`POST /answer`** — query in, top-k snippets + composed answer out
- **`POST /compare`** — side-by-side comparison of cosine vs dot-product similarity with configurable k values
- **Denylist guardrail** — blocks prompt injection, SQL/XSS probes, and oversized queries before any API call
- **In-memory monitoring** — latency percentiles (P50/P95/P99) and retrieval hit-rate via `GET /metrics`

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env   # add your OpenAI API key
uvicorn main:app --host 0.0.0.0 --port 8321
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/answer` | Query → top-k snippets + naive answer |
| POST | `/compare` | Compare cosine vs dot-product, k=3 vs k=5 |
| GET | `/metrics` | Latency percentiles + hit-rate |
| GET | `/health` | Service health check |

### Example

```bash
curl -X POST http://localhost:8321/answer \
  -H 'Content-Type: application/json' \
  -d '{"query": "how do I scale pods?", "top_k": 3, "similarity": "cosine"}'
```

## Project Structure

```
├── main.py              # FastAPI app and endpoints
├── corpus.py            # 12 hand-written Kubernetes snippets
├── embeddings.py        # OpenAI embeddings + VectorIndex class
├── guardrail.py         # Denylist + query-length guardrail
├── metrics.py           # In-memory latency and hit-rate tracking
├── config.py            # Settings via pydantic-settings
├── test_compare.py      # Comparison script (5 targeted queries)
├── requirements.txt     # Dependencies
└── WRITEUP.md           # Design decisions and trade-offs
```

## Design Decisions

See [WRITEUP.md](WRITEUP.md) for detailed explanations on:
- Guardrail choice and rationale
- Cosine vs dot-product index comparison results
- Monitoring metrics design
- Production improvement paths
