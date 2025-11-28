"""HTTP client implementation using urllib."""

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class UrllibHttpClient:
    """HTTP client using Python's urllib."""

    def request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        data: bytes | None = None,
        timeout: float = 30,
    ) -> tuple[int, bytes]:
        """Make HTTP request using urllib.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Full URL to request
            headers: Optional request headers
            data: Optional request body
            timeout: Request timeout in seconds

        Returns:
            Tuple of (status_code, response_body)

        Raises:
            URLError: On network errors
        """
        req = Request(url, data=data, headers=headers or {}, method=method)

        try:
            with urlopen(req, timeout=timeout) as response:
                return response.status, response.read()
        except HTTPError as e:
            return e.code, e.read()
