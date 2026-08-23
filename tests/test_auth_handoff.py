import json

from click.testing import CliRunner

from chatnpm.auth_handoff import parse_npm_auth_handoff
from chatnpm.cli import main


def test_parse_npm_auth_handoff_extracts_security_key_url_without_done_url():
    output = """
npm notice Publishing to https://registry.npmjs.org/ with tag latest and public access
npm notice Open https://www.npmjs.com/login/56a1028f-cec6-4f2d-aa06-2c4c517b7dbc to use your security key for authentication
This operation requires a one-time password.
Enter OTP:
After authenticating, your token can be retrieved from:
  https://registry.npmjs.org/-/v1/done?authId=secret-auth-id
"""

    result = parse_npm_auth_handoff(output)

    assert result == {
        "status": "auth_required",
        "login_url": "https://www.npmjs.com/login/56a1028f-cec6-4f2d-aa06-2c4c517b7dbc",
        "otp_required": True,
        "source": "npm_cli_output",
    }
    assert "authId" not in json.dumps(result)


def test_parse_npm_auth_handoff_extracts_cli_login_url():
    output = """
Login at:
https://www.npmjs.com/login?next=/login/cli/72ea5b19-3561-4465-bfa5-375fe8c720f1
Press ENTER to open in the browser...
"""

    result = parse_npm_auth_handoff(output)

    assert result["status"] == "auth_required"
    assert result["login_url"] == "https://www.npmjs.com/login?next=/login/cli/72ea5b19-3561-4465-bfa5-375fe8c720f1"
    assert result["otp_required"] is False


def test_parse_npm_auth_handoff_reports_no_auth_required():
    assert parse_npm_auth_handoff("+ qpet-adventure@0.0.1") == {
        "status": "none",
        "login_url": None,
        "otp_required": False,
        "source": "npm_cli_output",
    }


def test_auth_parse_output_cli_outputs_json():
    result = CliRunner().invoke(
        main,
        ["auth", "parse-output", "--format", "json"],
        input="Open https://www.npmjs.com/login/abc to use your security key\nEnter OTP:\n",
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["login_url"] == "https://www.npmjs.com/login/abc"
    assert payload["otp_required"] is True


def test_auth_parse_output_text_is_card_handoff_friendly():
    result = CliRunner().invoke(
        main,
        ["auth", "parse-output"],
        input="Login at:\nhttps://www.npmjs.com/login?next=/login/cli/abc\n",
    )

    assert result.exit_code == 0, result.output
    assert "Status: auth_required" in result.output
    assert "Login URL: https://www.npmjs.com/login?next=/login/cli/abc" in result.output
    assert "OTP required: no" in result.output
