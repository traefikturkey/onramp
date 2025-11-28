#!/usr/bin/env python
"""
cloudflare.py - Cloudflare API operations for OnRamp

Commands:
  dns list
  dns delete --name <subdomain>
  zone info

Features:
- Proper API client with error handling
- Structured error messages
- Credential handling via environment variables

Note: Tunnel creation/deletion is handled via cloudflared CLI (docker compose).
This script handles the DNS API operations that were done via curl/jq.
"""

import argparse
import json
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ports.http import HttpClient


class CloudflareAPI:
    """Cloudflare API client."""

    BASE_URL = "https://api.cloudflare.com/client/v4"

    def __init__(
        self,
        api_token: str | None = None,
        domain: str | None = None,
        http_client: "HttpClient | None" = None,
    ):
        self.api_token = api_token or os.environ.get("CF_DNS_API_TOKEN", "")
        self.domain = domain or os.environ.get("HOST_DOMAIN", "")

        if not self.api_token:
            raise ValueError("CF_DNS_API_TOKEN environment variable not set")
        if not self.domain:
            raise ValueError("HOST_DOMAIN environment variable not set")

        # Use injected client or create default
        if http_client is not None:
            self._http = http_client
        else:
            from adapters.urllib_http import UrllibHttpClient

            self._http = UrllibHttpClient()

    def _request(self, method: str, endpoint: str, data: dict | None = None) -> dict:
        """Make API request."""
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        body = json.dumps(data).encode() if data else None

        status, response_body = self._http.request(method, url, headers, body, timeout=30)

        try:
            result = json.loads(response_body.decode())
        except json.JSONDecodeError:
            raise RuntimeError(f"HTTP {status}: {response_body.decode()}")

        if status >= 400:
            errors = result.get("errors", [])
            if errors:
                raise RuntimeError(f"API Error: {errors[0].get('message', 'Unknown error')}")
            raise RuntimeError(f"HTTP {status}: {response_body.decode()}")

        return result

    def get_zone_id(self) -> str:
        """Get zone ID for the configured domain."""
        result = self._request("GET", f"/zones?name={self.domain}")

        if not result.get("success"):
            raise RuntimeError(f"Failed to get zone: {result.get('errors', 'Unknown error')}")

        zones = result.get("result", [])
        if not zones:
            raise RuntimeError(f"Zone not found for domain: {self.domain}")

        return zones[0]["id"]

    def get_zone_info(self) -> dict:
        """Get zone information."""
        zone_id = self.get_zone_id()
        result = self._request("GET", f"/zones/{zone_id}")

        if not result.get("success"):
            raise RuntimeError(f"Failed to get zone info: {result.get('errors', 'Unknown error')}")

        return result.get("result", {})

    def list_dns_records(self, record_type: str | None = None) -> list[dict]:
        """List DNS records for the zone."""
        zone_id = self.get_zone_id()

        endpoint = f"/zones/{zone_id}/dns_records"
        if record_type:
            endpoint += f"?type={record_type}"

        result = self._request("GET", endpoint)

        if not result.get("success"):
            raise RuntimeError(f"Failed to list DNS records: {result.get('errors', 'Unknown error')}")

        return result.get("result", [])

    def find_dns_record(self, name: str, record_type: str = "CNAME") -> dict | None:
        """Find a specific DNS record by name and type."""
        zone_id = self.get_zone_id()

        # Ensure FQDN
        if not name.endswith(self.domain):
            name = f"{name}.{self.domain}"

        endpoint = f"/zones/{zone_id}/dns_records?type={record_type}&name={name}"
        result = self._request("GET", endpoint)

        if not result.get("success"):
            raise RuntimeError(f"Failed to find DNS record: {result.get('errors', 'Unknown error')}")

        records = result.get("result", [])
        return records[0] if records else None

    def delete_dns_record(self, name: str, record_type: str = "CNAME") -> bool:
        """Delete a DNS record by name."""
        zone_id = self.get_zone_id()

        # Find the record first
        record = self.find_dns_record(name, record_type)
        if not record:
            print(f"DNS record not found: {name} ({record_type})")
            return False

        record_id = record["id"]

        result = self._request("DELETE", f"/zones/{zone_id}/dns_records/{record_id}")

        if not result.get("success"):
            raise RuntimeError(f"Failed to delete DNS record: {result.get('errors', 'Unknown error')}")

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Cloudflare API operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment variables:
  CF_DNS_API_TOKEN  - Cloudflare API token (required)
  HOST_DOMAIN       - Domain name (required)

Examples:
  cloudflare.py dns list                    # List all DNS records
  cloudflare.py dns list --type CNAME       # List only CNAME records
  cloudflare.py dns delete --name tunnel    # Delete tunnel.example.com
  cloudflare.py zone info                   # Show zone information
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # DNS commands
    dns_parser = subparsers.add_parser("dns", help="DNS record operations")
    dns_subparsers = dns_parser.add_subparsers(dest="dns_action", help="DNS action")

    dns_list = dns_subparsers.add_parser("list", help="List DNS records")
    dns_list.add_argument("--type", "-t", help="Filter by record type (A, CNAME, etc.)")

    dns_delete = dns_subparsers.add_parser("delete", help="Delete DNS record")
    dns_delete.add_argument("--name", "-n", required=True, help="Record name (subdomain or FQDN)")
    dns_delete.add_argument("--type", "-t", default="CNAME", help="Record type (default: CNAME)")

    # Zone commands
    zone_parser = subparsers.add_parser("zone", help="Zone operations")
    zone_subparsers = zone_parser.add_subparsers(dest="zone_action", help="Zone action")

    zone_subparsers.add_parser("info", help="Show zone information")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        api = CloudflareAPI()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        if args.command == "dns":
            if args.dns_action == "list":
                records = api.list_dns_records(record_type=args.type)
                if not records:
                    print("No DNS records found")
                    return 0

                print(f"{'Name':<40} {'Type':<8} {'Content':<50}")
                print("-" * 100)
                for r in records:
                    print(f"{r['name']:<40} {r['type']:<8} {r['content']:<50}")
                return 0

            if args.dns_action == "delete":
                if api.delete_dns_record(args.name, args.type):
                    print(f"Deleted DNS record: {args.name}")
                    return 0
                return 1

        if args.command == "zone":
            if args.zone_action == "info":
                info = api.get_zone_info()
                print(f"Zone: {info.get('name')}")
                print(f"  ID: {info.get('id')}")
                print(f"  Status: {info.get('status')}")
                print(f"  Plan: {info.get('plan', {}).get('name')}")
                print(f"  Name servers: {', '.join(info.get('name_servers', []))}")
                return 0

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
