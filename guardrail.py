import re


class QueryGuardrail:
    """Denylist + query-length guardrail.

    Runs before any embedding or retrieval call, so it adds zero latency
    to the critical path and protects against prompt-injection attempts,
    SQL/XSS probes, and oversized queries that burn embedding tokens.
    """

    def __init__(self, denied_terms: list[str], max_length: int):
        self.max_length = max_length
        self.denied_patterns = [
            (term, re.compile(re.escape(term), re.IGNORECASE))
            for term in denied_terms
        ]

    def check(self, query: str) -> tuple[bool, str | None]:
        if not query or not query.strip():
            return False, "Query cannot be empty"

        if len(query) > self.max_length:
            return False, f"Query exceeds maximum length of {self.max_length} characters"

        for term, pattern in self.denied_patterns:
            if pattern.search(query):
                return False, f"Query contains disallowed content"

        return True, None
