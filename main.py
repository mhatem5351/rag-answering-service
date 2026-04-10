import time
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from config import settings
from corpus import SNIPPETS
from embeddings import VectorIndex, get_embeddings
from guardrail import QueryGuardrail
from metrics import metrics


# ---------------------------------------------------------------------------
# Startup / lifespan
# ---------------------------------------------------------------------------

cosine_index: VectorIndex | None = None
dot_index: VectorIndex | None = None
guardrail: QueryGuardrail | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global cosine_index, dot_index, guardrail

    # Embed corpus once, build both indexes from the same vectors
    texts = [s["text"] for s in SNIPPETS]
    raw_vectors = get_embeddings(texts)
    cosine_index = VectorIndex(SNIPPETS, raw_vectors, similarity="cosine")
    dot_index = VectorIndex(SNIPPETS, raw_vectors, similarity="dot")
    guardrail = QueryGuardrail(settings.denied_terms, settings.max_query_length)

    print(f"Indexes ready — {len(SNIPPETS)} snippets loaded")
    yield


app = FastAPI(title="RAG Answering Service", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str
    top_k: int = Field(default=3, ge=1, le=10)
    similarity: Literal["cosine", "dot"] = "cosine"


class Snippet(BaseModel):
    id: str
    title: str
    text: str
    score: float


class AnswerResponse(BaseModel):
    query: str
    answer: str
    snippets: list[Snippet]
    similarity: str
    latency_ms: float


class CompareRequest(BaseModel):
    query: str
    top_k_values: list[int] = Field(default=[3, 5])


class CompareResult(BaseModel):
    similarity: str
    top_k: int
    snippets: list[Snippet]
    top1_score: float
    score_spread: float


class CompareResponse(BaseModel):
    query: str
    results: list[CompareResult]
    analysis: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _select_index(similarity: str) -> VectorIndex:
    return cosine_index if similarity == "cosine" else dot_index


def _build_naive_answer(snippets: list[dict], top_k: int) -> str:
    lines = [f"Based on the top {top_k} results:\n"]
    for i, s in enumerate(snippets, 1):
        lines.append(f"{i}. **{s['title']}** — {s['text']}")
    lines.append(f"\nThe most relevant topic is '{snippets[0]['title']}'.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/answer", response_model=AnswerResponse)
async def answer(req: QueryRequest):
    ok, reason = guardrail.check(req.query)
    if not ok:
        raise HTTPException(status_code=400, detail=reason)

    t0 = time.perf_counter()

    # Embed query
    t_emb = time.perf_counter()
    q_vec = get_embeddings([req.query])[0]
    embedding_ms = (time.perf_counter() - t_emb) * 1000

    # Search
    t_search = time.perf_counter()
    index = _select_index(req.similarity)
    results = index.search(q_vec, req.top_k)
    search_ms = (time.perf_counter() - t_search) * 1000

    total_ms = (time.perf_counter() - t0) * 1000

    # Record metrics
    metrics.record(
        total_latency_ms=total_ms,
        embedding_latency_ms=embedding_ms,
        search_latency_ms=search_ms,
        top1_score=results[0]["score"],
        top_k=req.top_k,
        similarity=req.similarity,
    )

    return AnswerResponse(
        query=req.query,
        answer=_build_naive_answer(results, req.top_k),
        snippets=results,
        similarity=req.similarity,
        latency_ms=round(total_ms, 2),
    )


@app.post("/compare", response_model=CompareResponse)
async def compare(req: CompareRequest):
    ok, reason = guardrail.check(req.query)
    if not ok:
        raise HTTPException(status_code=400, detail=reason)

    # Single embedding call for the query
    q_vec = get_embeddings([req.query])[0]

    compare_results: list[CompareResult] = []

    for sim_name, idx in [("cosine", cosine_index), ("dot", dot_index)]:
        for k in req.top_k_values:
            hits = idx.search(q_vec, k)
            scores = [h["score"] for h in hits]
            compare_results.append(
                CompareResult(
                    similarity=sim_name,
                    top_k=k,
                    snippets=hits,
                    top1_score=scores[0],
                    score_spread=round(max(scores) - min(scores), 6),
                )
            )

    # Build analysis
    cos_top1 = [r for r in compare_results if r.similarity == "cosine"][0].snippets[0].id
    dot_top1 = [r for r in compare_results if r.similarity == "dot"][0].snippets[0].id
    agree = cos_top1 == dot_top1

    cos_spread = [r.score_spread for r in compare_results if r.similarity == "cosine"]
    dot_spread = [r.score_spread for r in compare_results if r.similarity == "dot"]

    analysis_lines = [
        f"Top-1 agreement: {'YES' if agree else 'NO'} (cosine={cos_top1}, dot={dot_top1})",
        f"Cosine score spreads by k: {dict(zip(req.top_k_values, cos_spread))}",
        f"Dot score spreads by k: {dict(zip(req.top_k_values, dot_spread))}",
        "Cosine scores are bounded [-1,1] and more interpretable for thresholding.",
        "Dot scores reflect raw magnitude — useful when embedding norm carries signal.",
    ]

    return CompareResponse(
        query=req.query,
        results=compare_results,
        analysis="\n".join(analysis_lines),
    )


@app.get("/metrics")
async def get_metrics():
    return metrics.summary()


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "corpus_size": len(SNIPPETS),
        "indexes_loaded": cosine_index is not None and dot_index is not None,
    }
