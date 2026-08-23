"""Structured npm authentication handoff helpers."""

from __future__ import annotations

import re
from typing import Any

NPM_LOGIN_URL_RE = re.compile(r"https://www\.npmjs\.com/(?:login|auth/cli)[^\s)>'\"]+")
OTP_RE = re.compile(r"(?:one-time password|Enter OTP|\bEOTP\b)", re.IGNORECASE)


def _clean_url(url: str) -> str:
    """Trim terminal punctuation while preserving query strings."""

    return url.rstrip(".,;]")


def parse_npm_auth_handoff(output: str) -> dict[str, Any]:
    """Parse npm CLI output for a user-auth handoff URL and OTP need.

    The returned shape is intentionally platform-neutral. Hermes/Feishu, Slack,
    or any other host adapter can turn ``login_url`` into a card/button and then
    continue the npm command once the user confirms completion.

    Only npmjs.com login/auth URLs are surfaced. Registry ``done?authId=...``
    URLs can carry one-time auth state and are deliberately ignored.
    """

    match = NPM_LOGIN_URL_RE.search(output or "")
    login_url = _clean_url(match.group(0)) if match else None
    otp_required = bool(OTP_RE.search(output or ""))
    return {
        "status": "auth_required" if login_url or otp_required else "none",
        "login_url": login_url,
        "otp_required": otp_required,
        "source": "npm_cli_output",
    }
