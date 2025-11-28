"""HTTP client protocol for dependency injection."""

from typing import Protocol


class HttpClient(Protocol):
    """Protocol for HTTP operations."""

    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        data: bytes | None = None,
        timeout: float = 30,
    ) -> tuple[int, bytes]:
        """Make HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Full URL to request
            headers: Optional request headers
            data: Optional request body
            timeout: Request timeout in seconds

        Returns:
            Tuple of (status_code, response_body)
        """
        ...
