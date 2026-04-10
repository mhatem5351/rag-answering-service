"""
Run against a live server:  python test_compare.py
Starts uvicorn automatically if nothing is listening on :8000.
"""

import httpx

BASE = "http://127.0.0.1:8321"

QUERIES = [
    "How do I scale my application automatically?",
    "What is the best way to store database passwords?",
    "How does traffic reach my containers from outside the cluster?",
    "How do I manage configuration across environments?",
    "What happens when a container crashes?",
]


def run():
    with httpx.Client(base_url=BASE, timeout=30) as client:
        # Health check
        r = client.get("/health")
        r.raise_for_status()
        print(f"Health: {r.json()}\n")

        for query in QUERIES:
            print(f"{'='*70}")
            print(f"QUERY: {query}\n")

            resp = client.post("/compare", json={"query": query, "top_k_values": [3, 5]})
            resp.raise_for_status()
            data = resp.json()

            for result in data["results"]:
                sim = result["similarity"].upper()
                k = result["top_k"]
                print(f"  [{sim} k={k}]  top1_score={result['top1_score']:.4f}  spread={result['score_spread']:.4f}")
                for s in result["snippets"]:
                    print(f"    {s['score']:.4f}  {s['id']}  {s['title']}")
                print()

            print(f"  Analysis:\n  {data['analysis']}\n")

        # Print metrics
        r = client.get("/metrics")
        print(f"{'='*70}")
        print(f"METRICS: {r.json()}")


if __name__ == "__main__":
    run()
