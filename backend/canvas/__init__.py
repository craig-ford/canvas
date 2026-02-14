from datetime import datetime, timezone


def success_response(data, status_code=200):
    """Return success response envelope."""
    return {
        "data": data,
        "meta": {"timestamp": datetime.now(timezone.utc).isoformat()}
    }


def list_response(data, total, page=1, per_page=25):
    """Return paginated list response envelope."""
    return {
        "data": data,
        "meta": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }