import numpy as np
from openai import OpenAI

from config import settings


_client = OpenAI(api_key=settings.openai_api_key)


def get_embeddings(texts: list[str]) -> np.ndarray:
    """Embed a list of texts via OpenAI and return an (n, dim) numpy array."""
    resp = _client.embeddings.create(model=settings.embedding_model, input=texts)
    return np.array([item.embedding for item in resp.data], dtype=np.float64)


class VectorIndex:
    """In-memory vector index supporting cosine or dot-product similarity."""

    def __init__(self, corpus: list[dict], vectors: np.ndarray, similarity: str = "cosine"):
        self.corpus = corpus
        self.similarity = similarity

        if similarity == "cosine":
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            self.vectors = vectors / norms  # unit-normalize once at index time
        else:
            self.vectors = vectors.copy()

    def search(self, query_embedding: np.ndarray, top_k: int) -> list[dict]:
        """Return top-k corpus entries sorted by descending similarity."""
        if self.similarity == "cosine":
            # query also needs normalizing for true cosine
            q = query_embedding / np.linalg.norm(query_embedding)
        else:
            q = query_embedding

        scores = q @ self.vectors.T  # (dim,) @ (dim, n) -> (n,)
        ranked = np.argsort(scores)[::-1][:top_k]

        return [
            {
                "id": self.corpus[i]["id"],
                "title": self.corpus[i]["title"],
                "text": self.corpus[i]["text"],
                "score": round(float(scores[i]), 6),
            }
            for i in ranked
        ]
