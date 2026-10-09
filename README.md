# RAG Answering Service

A minimal retrieval-augmented answering service built with FastAPI. Retrieves relevant snippets from a Kubernetes knowledge base using OpenAI embeddings and returns top-k results with a naive answer.

It is retrieval-only: there is no LLM generation step. The `answer` field is a templated summary built from the top-k snippets, so the only OpenAI calls are for embeddings.

## Features

- **12-snippet Kubernetes corpus** covering Pods, Deployments, Services, Secrets, HPA, Ingress, RBAC, Helm, and more
- **`POST /answer`** — query in, top-k snippets + templated answer out
- **`POST /compare`** — side-by-side comparison of cosine vs dot-product similarity with configurable k values
- **Denylist guardrail** — blocks prompt injection, SQL/XSS probes, and oversized queries before any API call
- **In-memory monitoring** — latency percentiles (P50/P95/P99) and retrieval hit-rate via `GET /metrics`

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env   # set OPENAI_API_KEY (the older OpenAI_KEY_TOKEN name is also accepted)
uvicorn main:app --host 0.0.0.0 --port 8321
```

The corpus is embedded once at startup, so the server needs a valid key to start. With the server running, in a second terminal:

```bash
python test_compare.py   # runs 5 queries through /compare against http://127.0.0.1:8321
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/answer` | Query → top-k snippets + naive answer |
| POST | `/compare` | Compare cosine vs dot-product, k=3 vs k=5 |
| GET | `/metrics` | Latency percentiles + hit-rate (recorded for `/answer` requests) |
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
├── test_compare.py      # Comparison script (5 targeted queries, needs a running server)
├── requirements.txt     # Dependencies
├── .env.example         # Template for the API key
├── WRITEUP.md           # Design decisions and trade-offs
└── RAG_Service_Design_Doc.docx  # Original version of WRITEUP.md
```

## Design Decisions

In the design doc's run of `test_compare.py` (5 queries), cosine and dot-product agreed on the top-1 snippet for all 5 queries, with top-1 cosine scores between 0.36 and 0.45. Cosine with k=3 is the recommended default.

See [WRITEUP.md](WRITEUP.md) (Markdown version of [RAG_Service_Design_Doc.docx](RAG_Service_Design_Doc.docx)) for detailed explanations on:
- Guardrail choice and rationale
- Cosine vs dot-product index comparison results
- Monitoring metrics design
- Production improvement paths

## License

MIT, see [LICENSE](LICENSE).
