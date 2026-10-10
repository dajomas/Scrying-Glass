"""Reject browser mutations originating from a different origin."""
from fastapi import HTTPException, Request
from urllib.parse import urlsplit


async def same_origin(request: Request):
    origin = request.headers.get("origin")
    # A configured root_path is part of base_url, but not part of an origin.
    base = urlsplit(str(request.base_url))
    expected_origin = f"{base.scheme}://{base.netloc}"
    if origin and origin != expected_origin:
        raise HTTPException(403, "Cross-origin changes are not allowed")
    if request.headers.get("sec-fetch-site") == "cross-site":
        raise HTTPException(403, "Cross-site changes are not allowed")

