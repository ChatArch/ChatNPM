"""Safe rendering helpers for npm metadata reports."""

from __future__ import annotations

import re
import urllib.parse
from typing import Any

SAFE_PUBLISH_CONFIG_KEYS = {"access", "provenance", "registry", "tag"}
SAFE_ACCESS_VALUES = {"public", "restricted"}
SAFE_TAG_RE = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")
SENSITIVE_KEY_RE = re.compile(r"(auth|credential|key|otp|password|secret|token)", re.IGNORECASE)


def sanitize_url(value: Any) -> str | None:
    """Return a URL without userinfo, query, or fragment.

    Malformed URLs can make urllib raise ValueError whose text includes raw
    credential-like netloc/port values. Treat those inputs as unsupported
    instead of bubbling exception text into CLI errors or reports.
    """

    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parts = urllib.parse.urlsplit(value.strip())
        if not parts.scheme or not parts.netloc:
            return None
        host = parts.hostname or ""
        if not host:
            return None
        netloc = host
        port = parts.port
    except ValueError:
        return None
    if port is not None:
        netloc = f"{netloc}:{port}"
    return urllib.parse.urlunsplit((parts.scheme, netloc, parts.path, "", ""))


def sanitize_repository(value: Any) -> dict[str, Any] | str | None:
    """Return repository metadata without credential-bearing URL parts."""

    if isinstance(value, str):
        return sanitize_url(value)
    if not isinstance(value, dict):
        return None
    safe: dict[str, Any] = {}
    repo_type = value.get("type")
    if isinstance(repo_type, str) and repo_type:
        safe["type"] = repo_type
    url = sanitize_url(value.get("url"))
    if url:
        safe["url"] = url
    directory = value.get("directory")
    if isinstance(directory, str) and directory and not SENSITIVE_KEY_RE.search(directory):
        safe["directory"] = directory
    return safe or None


def sanitize_publish_config(value: Any) -> dict[str, Any]:
    """Summarize publishConfig with an allowlist and redaction counts.

    `publishConfig` is usually public package metadata, but malformed local
    package.json files or private registry packuments can put auth material in
    arbitrary keys or URL query/userinfo. The report therefore keeps only known
    public npm fields and counts everything else instead of echoing keys/values.
    """

    if not isinstance(value, dict) or not value:
        return {"present": False, "redacted_key_count": 0, "unsupported_key_count": 0}

    safe: dict[str, Any] = {"present": True}
    redacted = 0
    unsupported = 0
    for key, item in value.items():
        key_text = key if isinstance(key, str) else ""
        key_lower = key_text.lower()
        if key_lower not in SAFE_PUBLISH_CONFIG_KEYS:
            if key_text and SENSITIVE_KEY_RE.search(key_text):
                redacted += 1
            else:
                unsupported += 1
            continue
        if key_lower == "access":
            if isinstance(item, str) and item in SAFE_ACCESS_VALUES:
                safe["access"] = item
            else:
                unsupported += 1
        elif key_lower == "provenance":
            if isinstance(item, bool):
                safe["provenance"] = item
            else:
                unsupported += 1
        elif key_lower == "registry":
            url = sanitize_url(item)
            if url:
                safe["registry"] = url
            else:
                unsupported += 1
        elif key_lower == "tag":
            if isinstance(item, str) and SAFE_TAG_RE.fullmatch(item) and not SENSITIVE_KEY_RE.search(item):
                safe["tag"] = item
            else:
                unsupported += 1
    safe["redacted_key_count"] = redacted
    safe["unsupported_key_count"] = unsupported
    return safe
