"""Mock HTTP client for testing."""

import json


class MockHttpClient:
    """Mock HTTP client that returns preconfigured responses."""

    def __init__(self):
        self.responses: dict[tuple[str, str], tuple[int, bytes]] = {}
        self.calls: list[tuple[str, str, dict | None, bytes | None]] = []
        self.default_response: tuple[int, bytes] = (404, b'{"error": "not found"}')

    def set_response(self, method: str, url: str, status: int, body: bytes | dict) -> None:
        """Configure a response for a specific method/url combination.

        Args:
            method: HTTP method
            url: Full URL or URL pattern
            status: HTTP status code to return
            body: Response body (bytes or dict to be JSON-encoded)
        """
        if isinstance(body, dict):
            body = json.dumps(body).encode()
        self.responses[(method, url)] = (status, body)

    def set_default_response(self, status: int, body: bytes | dict) -> None:
        """Set the default response for unmatched requests."""
        if isinstance(body, dict):
            body = json.dumps(body).encode()
        self.default_response = (status, body)

    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        data: bytes | None = None,
        timeout: float = 30,
    ) -> tuple[int, bytes]:
        """Mock HTTP request that returns preconfigured response.

        Records the call for later assertion.
        """
        self.calls.append((method, url, headers, data))

        # Try exact match first
        if (method, url) in self.responses:
            return self.responses[(method, url)]

        # Try partial URL match (for query string variations)
        for (m, u), response in self.responses.items():
            if m == method and u in url:
                return response

        return self.default_response

    def assert_called_once(self) -> None:
        """Assert that exactly one request was made."""
        assert len(self.calls) == 1, f"Expected 1 call, got {len(self.calls)}"

    def assert_called_with(self, method: str, url: str) -> None:
        """Assert that a specific request was made."""
        for m, u, _, _ in self.calls:
            if m == method and url in u:
                return
        raise AssertionError(f"No call found for {method} {url}. Calls: {self.calls}")

    def reset(self) -> None:
        """Clear all recorded calls."""
        self.calls.clear()
