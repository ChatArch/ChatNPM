"""CLI entrypoint for chatnpm."""

import json
from pathlib import Path
from typing import Any

import click
from chatstyle import (
    CommandField,
    CommandSchema,
    add_interactive_option,
    render_success,
    resolve_command_inputs,
)

from chatnpm import __version__
from chatnpm.registry import DEFAULT_REGISTRY, inspect_package
from chatnpm.trusted import audit_trusted_publishing_repo


HELLO_SCHEMA = CommandSchema(
    name="hello",
    fields=(CommandField("name", prompt="name", required=True),),
)


TREE_TEXT = """chatnpm
├── hello
├── package
│   └── inspect
└── trusted
    └── audit
""".rstrip()


@click.group(invoke_without_command=True)
@click.version_option(__version__, prog_name="chatnpm")
@click.option("--tree", is_flag=True, help="Print the command tree and exit.")
@click.pass_context
def main(ctx: click.Context, tree: bool) -> None:
    """chatnpm command line interface."""

    if tree:
        click.echo(TREE_TEXT)
        ctx.exit(0)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(0)


@main.command()
@click.argument("name", required=False)
@add_interactive_option
def hello(name: str | None, interactive: bool | None) -> None:
    """Print a greeting with ChatStyle-backed input resolution."""

    values = resolve_command_inputs(
        schema=HELLO_SCHEMA,
        provided={"name": name},
        interactive=interactive,
        usage="Usage: chatnpm hello [NAME]",
    )
    render_success(f"Hello, {values['name']}!")


@main.group(name="package")
def package_group() -> None:
    """Inspect npm package registry metadata."""


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
    """Read npm registry publisher/provenance metadata for PACKAGE."""

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
    """Audit npm Trusted Publishing evidence."""


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
    """Read local package/workflow evidence for npm Trusted Publishing."""

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
