"""Tests for cloudflare.py with mocked HTTP client."""

import json
import pytest
import sys
from pathlib import Path

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from cloudflare import CloudflareAPI
from tests.mocks.http import MockHttpClient


class TestCloudflareAPIInit:
    """Tests for CloudflareAPI initialization."""

    def test_raises_without_token(self, monkeypatch):
        """Should raise ValueError when CF_DNS_API_TOKEN is not set."""
        monkeypatch.delenv("CF_DNS_API_TOKEN", raising=False)
        monkeypatch.delenv("HOST_DOMAIN", raising=False)

        with pytest.raises(ValueError, match="CF_DNS_API_TOKEN"):
            CloudflareAPI()

    def test_raises_without_domain(self, monkeypatch):
        """Should raise ValueError when HOST_DOMAIN is not set."""
        monkeypatch.setenv("CF_DNS_API_TOKEN", "test-token")
        monkeypatch.delenv("HOST_DOMAIN", raising=False)

        with pytest.raises(ValueError, match="HOST_DOMAIN"):
            CloudflareAPI()

    def test_accepts_explicit_params(self):
        """Should accept explicit api_token and domain parameters."""
        mock_http = MockHttpClient()
        api = CloudflareAPI(
            api_token="test-token",
            domain="example.com",
            http_client=mock_http,
        )

        assert api.api_token == "test-token"
        assert api.domain == "example.com"

    def test_uses_env_vars_when_params_not_provided(self, monkeypatch):
        """Should use environment variables when params not provided."""
        monkeypatch.setenv("CF_DNS_API_TOKEN", "env-token")
        monkeypatch.setenv("HOST_DOMAIN", "env-domain.com")

        mock_http = MockHttpClient()
        api = CloudflareAPI(http_client=mock_http)

        assert api.api_token == "env-token"
        assert api.domain == "env-domain.com"

    def test_uses_injected_http_client(self):
        """Should use injected HTTP client instead of creating default."""
        mock_http = MockHttpClient()
        api = CloudflareAPI(
            api_token="test",
            domain="example.com",
            http_client=mock_http,
        )

        assert api._http is mock_http


class TestGetZoneId:
    """Tests for get_zone_id() method."""

    @pytest.fixture
    def mock_http(self):
        return MockHttpClient()

    @pytest.fixture
    def api(self, mock_http):
        return CloudflareAPI(
            api_token="test-token",
            domain="example.com",
            http_client=mock_http,
        )

    def test_returns_zone_id_on_success(self, api, mock_http):
        """Should return zone ID when zone is found."""
        mock_http.set_response(
            "GET",
            "/zones?name=example.com",
            200,
            {"success": True, "result": [{"id": "zone123", "name": "example.com"}]},
        )

        zone_id = api.get_zone_id()

        assert zone_id == "zone123"
        mock_http.assert_called_once()

    def test_raises_when_zone_not_found(self, api, mock_http):
        """Should raise RuntimeError when zone is not found."""
        mock_http.set_response(
            "GET",
            "/zones?name=example.com",
            200,
            {"success": True, "result": []},
        )

        with pytest.raises(RuntimeError, match="Zone not found"):
            api.get_zone_id()

    def test_raises_on_api_error(self, api, mock_http):
        """Should raise RuntimeError on API failure."""
        mock_http.set_response(
            "GET",
            "/zones?name=example.com",
            200,
            {"success": False, "errors": [{"message": "Authentication failed"}]},
        )

        with pytest.raises(RuntimeError, match="Failed to get zone"):
            api.get_zone_id()


class TestGetZoneInfo:
    """Tests for get_zone_info() method."""

    @pytest.fixture
    def mock_http(self):
        return MockHttpClient()

    @pytest.fixture
    def api(self, mock_http):
        return CloudflareAPI(
            api_token="test-token",
            domain="example.com",
            http_client=mock_http,
        )

    def test_returns_zone_info(self, api, mock_http):
        """Should return zone information."""
        # First call: get zone ID
        mock_http.set_response(
            "GET",
            "/zones?name=example.com",
            200,
            {"success": True, "result": [{"id": "zone123"}]},
        )
        # Second call: get zone info
        mock_http.set_response(
            "GET",
            "/zones/zone123",
            200,
            {
                "success": True,
                "result": {
                    "id": "zone123",
                    "name": "example.com",
                    "status": "active",
                    "plan": {"name": "Free"},
                },
            },
        )

        info = api.get_zone_info()

        assert info["name"] == "example.com"
        assert info["status"] == "active"


class TestListDnsRecords:
    """Tests for list_dns_records() method."""

    @pytest.fixture
    def mock_http(self):
        return MockHttpClient()

    @pytest.fixture
    def api(self, mock_http):
        return CloudflareAPI(
            api_token="test-token",
            domain="example.com",
            http_client=mock_http,
        )

    def test_lists_all_records(self, api, mock_http):
        """Should list all DNS records."""
        mock_http.set_response(
            "GET",
            "/zones?name=example.com",
            200,
            {"success": True, "result": [{"id": "zone123"}]},
        )
        mock_http.set_response(
            "GET",
            "/zones/zone123/dns_records",
            200,
            {
                "success": True,
                "result": [
                    {"id": "rec1", "type": "A", "name": "example.com", "content": "1.2.3.4"},
                    {"id": "rec2", "type": "CNAME", "name": "www.example.com", "content": "example.com"},
                ],
            },
        )

        records = api.list_dns_records()

        assert len(records) == 2
        assert records[0]["type"] == "A"
        assert records[1]["type"] == "CNAME"

    def test_filters_by_record_type(self, api, mock_http):
        """Should filter records by type when specified."""
        mock_http.set_response(
            "GET",
            "/zones?name=example.com",
            200,
            {"success": True, "result": [{"id": "zone123"}]},
        )
        mock_http.set_response(
            "GET",
            "/zones/zone123/dns_records?type=CNAME",
            200,
            {
                "success": True,
                "result": [
                    {"id": "rec2", "type": "CNAME", "name": "www.example.com", "content": "example.com"},
                ],
            },
        )

        records = api.list_dns_records(record_type="CNAME")

        assert len(records) == 1
        assert records[0]["type"] == "CNAME"

    def test_returns_empty_list_when_no_records(self, api, mock_http):
        """Should return empty list when no records found."""
        mock_http.set_response(
            "GET",
            "/zones?name=example.com",
            200,
            {"success": True, "result": [{"id": "zone123"}]},
        )
        mock_http.set_response(
            "GET",
            "/zones/zone123/dns_records",
            200,
            {"success": True, "result": []},
        )

        records = api.list_dns_records()

        assert records == []


class TestFindDnsRecord:
    """Tests for find_dns_record() method."""

    @pytest.fixture
    def mock_http(self):
        return MockHttpClient()

    @pytest.fixture
    def api(self, mock_http):
        return CloudflareAPI(
            api_token="test-token",
            domain="example.com",
            http_client=mock_http,
        )

    def test_finds_record_by_subdomain(self, api, mock_http):
        """Should find record when given subdomain name."""
        mock_http.set_response(
            "GET",
            "/zones?name=example.com",
            200,
            {"success": True, "result": [{"id": "zone123"}]},
        )
        mock_http.set_response(
            "GET",
            "dns_records?type=CNAME&name=www.example.com",
            200,
            {
                "success": True,
                "result": [{"id": "rec1", "name": "www.example.com", "type": "CNAME"}],
            },
        )

        record = api.find_dns_record("www")

        assert record is not None
        assert record["id"] == "rec1"

    def test_finds_record_by_fqdn(self, api, mock_http):
        """Should find record when given full FQDN."""
        mock_http.set_response(
            "GET",
            "/zones?name=example.com",
            200,
            {"success": True, "result": [{"id": "zone123"}]},
        )
        mock_http.set_response(
            "GET",
            "dns_records?type=CNAME&name=www.example.com",
            200,
            {
                "success": True,
                "result": [{"id": "rec1", "name": "www.example.com", "type": "CNAME"}],
            },
        )

        record = api.find_dns_record("www.example.com")

        assert record is not None
        assert record["id"] == "rec1"

    def test_returns_none_when_not_found(self, api, mock_http):
        """Should return None when record is not found."""
        mock_http.set_response(
            "GET",
            "/zones?name=example.com",
            200,
            {"success": True, "result": [{"id": "zone123"}]},
        )
        mock_http.set_response(
            "GET",
            "dns_records?type=CNAME",
            200,
            {"success": True, "result": []},
        )

        record = api.find_dns_record("nonexistent")

        assert record is None


class TestDeleteDnsRecord:
    """Tests for delete_dns_record() method."""

    @pytest.fixture
    def mock_http(self):
        return MockHttpClient()

    @pytest.fixture
    def api(self, mock_http):
        return CloudflareAPI(
            api_token="test-token",
            domain="example.com",
            http_client=mock_http,
        )

    def test_deletes_existing_record(self, api, mock_http, capsys):
        """Should delete record and return True."""
        mock_http.set_response(
            "GET",
            "/zones?name=example.com",
            200,
            {"success": True, "result": [{"id": "zone123"}]},
        )
        mock_http.set_response(
            "GET",
            "dns_records?type=CNAME&name=test.example.com",
            200,
            {
                "success": True,
                "result": [{"id": "rec456", "name": "test.example.com"}],
            },
        )
        mock_http.set_response(
            "DELETE",
            "/zones/zone123/dns_records/rec456",
            200,
            {"success": True},
        )

        result = api.delete_dns_record("test")

        assert result is True
        mock_http.assert_called_with("DELETE", "/zones/zone123/dns_records/rec456")

    def test_returns_false_when_record_not_found(self, api, mock_http, capsys):
        """Should return False when record doesn't exist."""
        mock_http.set_response(
            "GET",
            "/zones?name=example.com",
            200,
            {"success": True, "result": [{"id": "zone123"}]},
        )
        mock_http.set_response(
            "GET",
            "dns_records?type=CNAME",
            200,
            {"success": True, "result": []},
        )

        result = api.delete_dns_record("nonexistent")

        assert result is False
        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_raises_on_api_error(self, api, mock_http):
        """Should raise RuntimeError on API failure."""
        mock_http.set_response(
            "GET",
            "/zones?name=example.com",
            200,
            {"success": True, "result": [{"id": "zone123"}]},
        )
        mock_http.set_response(
            "GET",
            "dns_records?type=CNAME&name=test.example.com",
            200,
            {
                "success": True,
                "result": [{"id": "rec456", "name": "test.example.com"}],
            },
        )
        mock_http.set_response(
            "DELETE",
            "/zones/zone123/dns_records/rec456",
            200,
            {"success": False, "errors": [{"message": "Permission denied"}]},
        )

        with pytest.raises(RuntimeError, match="Failed to delete"):
            api.delete_dns_record("test")


class TestRequestErrorHandling:
    """Tests for _request() error handling."""

    @pytest.fixture
    def mock_http(self):
        return MockHttpClient()

    @pytest.fixture
    def api(self, mock_http):
        return CloudflareAPI(
            api_token="test-token",
            domain="example.com",
            http_client=mock_http,
        )

    def test_handles_http_400_error(self, api, mock_http):
        """Should raise RuntimeError on HTTP 400 error."""
        mock_http.set_response(
            "GET",
            "/zones",
            400,
            {"success": False, "errors": [{"message": "Bad Request"}]},
        )

        with pytest.raises(RuntimeError, match="API Error: Bad Request"):
            api._request("GET", "/zones")

    def test_handles_http_401_error(self, api, mock_http):
        """Should raise RuntimeError on HTTP 401 error."""
        mock_http.set_response(
            "GET",
            "/zones",
            401,
            {"success": False, "errors": [{"message": "Invalid API token"}]},
        )

        with pytest.raises(RuntimeError, match="API Error: Invalid API token"):
            api._request("GET", "/zones")

    def test_handles_invalid_json_response(self, api, mock_http):
        """Should raise RuntimeError on invalid JSON response."""
        mock_http.set_response(
            "GET",
            "/zones",
            500,
            b"Internal Server Error",
        )

        with pytest.raises(RuntimeError, match="HTTP 500"):
            api._request("GET", "/zones")
