"""Cloudflare DNS management API."""

import sys
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

# Import existing cloudflare module
sys.path.insert(0, "/scripts")

router = APIRouter()


class DNSRecordCreate(BaseModel):
    """Request body for creating a DNS record."""
    type: str  # A, AAAA, CNAME, TXT, MX, etc.
    name: str
    content: str
    ttl: int = 1  # 1 = auto
    proxied: bool = False


@router.get("/zones")
async def list_zones(request: Request):
    """List Cloudflare zones."""
    try:
        from cloudflare import CloudflareAPI
        api = CloudflareAPI()
        zones = api.list_zones()
        return {"zones": zones}
    except ImportError:
        raise HTTPException(status_code=501, detail="Cloudflare module not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/zones/{zone_id}/records")
async def list_dns_records(request: Request, zone_id: str, type: str = None, name: str = None):
    """List DNS records for a zone."""
    try:
        from cloudflare import CloudflareAPI
        api = CloudflareAPI()
        records = api.list_dns_records(zone_id, record_type=type, name=name)
        return {"records": records, "count": len(records)}
    except ImportError:
        raise HTTPException(status_code=501, detail="Cloudflare module not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/zones/{zone_id}/records")
async def create_dns_record(request: Request, zone_id: str, record: DNSRecordCreate):
    """Create a new DNS record."""
    try:
        from cloudflare import CloudflareAPI
        api = CloudflareAPI()
        result = api.create_dns_record(
            zone_id,
            record_type=record.type,
            name=record.name,
            content=record.content,
            ttl=record.ttl,
            proxied=record.proxied,
        )
        return {"success": True, "record": result}
    except ImportError:
        raise HTTPException(status_code=501, detail="Cloudflare module not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/zones/{zone_id}/records/{record_id}")
async def delete_dns_record(request: Request, zone_id: str, record_id: str):
    """Delete a DNS record."""
    try:
        from cloudflare import CloudflareAPI
        api = CloudflareAPI()
        result = api.delete_dns_record(zone_id, record_id)
        return {"success": True, "deleted": record_id}
    except ImportError:
        raise HTTPException(status_code=501, detail="Cloudflare module not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
