"""CLI entrypoint for chatnpm."""

import json
from pathlib import Path
from typing import Any

import click
from chatstyle import add_tree_option

from chatnpm import __version__
from chatnpm.auth_handoff import parse_npm_auth_handoff
from chatnpm.registry import DEFAULT_REGISTRY, inspect_package
from chatnpm.trusted import audit_trusted_publishing_repo


@click.group(name="chatnpm", invoke_without_command=True)
@click.version_option(__version__, prog_name="chatnpm")
@add_tree_option(renderer_options={"root_name": "chatnpm"})
@click.pass_context
def main(ctx: click.Context) -> None:
    """ChatArch npm registry and publishing-evidence helper."""

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(0)


@main.group(name="auth")
def auth_group() -> None:
    """Parse npm authentication handoff prompts."""


def _render_auth_handoff_text(result: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"Status: {result.get('status')}",
            f"Login URL: {result.get('login_url') or '(none)'}",
            f"OTP required: {'yes' if result.get('otp_required') else 'no'}",
        ]
    )


@auth_group.command(name="parse-output")
@click.option("--format", "output_format", type=click.Choice(["text", "json"]), default="text", show_default=True)
def auth_parse_output(output_format: str) -> None:
    """Parse npm CLI output from stdin into a card-handoff payload."""

    raw_output = click.get_text_stream("stdin").read()
    result = parse_npm_auth_handoff(raw_output)
    if output_format == "json":
        click.echo(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        click.echo(_render_auth_handoff_text(result))


@main.group(name="package")
def package_group() -> None:
    """Inspect public npm registry metadata; read-only network access."""


def _render_package_text(summary: dict[str, Any]) -> str:
    dist = summary.get("dist") or {}
    provenance = summary.get("provenance") or {}
    maintainers = summary.get("maintainers") or []
    repository = summary.get("repository")

    lines = [
        f"Package: {summary.get('package')}@{summary.get('version')}",
        f"Registry: {summary.get('registry', DEFAULT_REGISTRY)}",
        f"Scope: {summary.get('scope') or '(none)'}",
        f"Maintainers: {len(maintainers)}",
        f"Repository: {repository or '(none)'}",
        (
            "Dist: "
            f"integrity={bool(dist.get('integrity_present'))}, "
            f"signatures={dist.get('signature_count', 0)}, "
            f"attestation={bool(dist.get('attestation_present'))}"
        ),
        f"Provenance: {provenance.get('present')} ({provenance.get('source') or 'none'})",
        "Trusted Publishing settings: not exposed by public npm registry",
    ]
    return "\n".join(lines)


@package_group.command(name="inspect")
@click.argument("package")
@click.option("--version", "package_version", help="Inspect a specific package version instead of latest.")
@click.option("--registry", default=DEFAULT_REGISTRY, show_default=True, help="npm registry base URL.")
@click.option("--format", "output_format", type=click.Choice(["text", "json"]), default="text", show_default=True)
def package_inspect(package: str, package_version: str | None, registry: str, output_format: str) -> None:
    """Read public package metadata; sends one request and never outputs auth values."""

    try:
        summary = inspect_package(package, version=package_version, registry=registry)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    if output_format == "json":
        click.echo(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        click.echo(_render_package_text(summary))


@main.group(name="trusted")
def trusted_group() -> None:
    """Audit npm Trusted Publishing evidence; read-only filesystem access."""


def _render_trusted_text(report: dict[str, Any]) -> str:
    package_json = report.get("package_json") or {}
    trusted = report.get("trusted_publishing") or {}
    workflows = report.get("workflows") or []
    lines = [
        f"Path: {report.get('path')}",
        f"Package: {package_json.get('name') or '(none)'}@{package_json.get('version') or '(unknown)'}",
        f"Workflow files: {len(workflows)}",
        f"OIDC provenance workflow: {bool(trusted.get('oidc_provenance_workflow_present'))}",
        f"Token fallback present: {bool(trusted.get('token_fallback_present'))}",
    ]
    return "\n".join(lines)


@trusted_group.command(name="audit")
@click.argument("path", required=False, type=click.Path(path_type=Path, file_okay=False, dir_okay=True), default=Path("."))
@click.option("--format", "output_format", type=click.Choice(["text", "json"]), default="text", show_default=True)
def trusted_audit(path: Path, output_format: str) -> None:
    """Read package/workflow evidence under PATH; no account access or secret output."""

    try:
        report = audit_trusted_publishing_repo(path)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    if output_format == "json":
        click.echo(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        click.echo(_render_trusted_text(report))


if __name__ == "__main__":
    main()
