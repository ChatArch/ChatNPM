"""CLI entrypoint for chatnpm."""

import json
from pathlib import Path
from typing import Any

import click

from chatnpm import __version__
from chatnpm.registry import DEFAULT_REGISTRY, inspect_package
from chatnpm.trusted import audit_trusted_publishing_repo


def _purpose(command: click.Command) -> str:
    """Return a compact one-line purpose for a Click command."""

    help_text = command.help or command.short_help or ""
    return " ".join(help_text.strip().split()).rstrip(".") or "Run this command"


def _option_token(option: click.Option) -> str:
    long_name = next((opt for opt in option.opts if opt.startswith("--")), option.opts[-1])
    if option.is_bool_flag or option.is_flag:
        return long_name
    if isinstance(option.type, click.Choice):
        metavar = "|".join(str(choice) for choice in option.type.choices)
    else:
        metavar = (option.metavar or option.name or "VALUE").upper().replace("_", "-")
    token = f"{long_name} {metavar}"
    if option.required:
        return token
    return f"[{token}]"


def _argument_token(argument: click.Argument) -> str:
    name = argument.name.upper().replace("_", "-")
    if argument.nargs == -1:
        name = f"{name}..."
    if not argument.required:
        return f"[{name}]"
    return name


def _command_signature(command: click.Command) -> str:
    tokens: list[str] = []
    for param in command.params:
        if isinstance(param, click.Argument):
            tokens.append(_argument_token(param))
        elif isinstance(param, click.Option):
            if param.name in {"help"}:
                continue
            tokens.append(_option_token(param))
    return " ".join(tokens)


def _tree_lines(command: click.Command, name: str, prefix: str = "") -> list[str]:
    lines: list[str] = []
    if isinstance(command, click.Group):
        visible_commands = [(key, cmd) for key, cmd in command.commands.items() if not cmd.hidden]
        for index, (child_name, child) in enumerate(visible_commands):
            last = index == len(visible_commands) - 1
            connector = "└── " if last else "├── "
            child_prefix = "    " if last else "│   "
            signature = _command_signature(child)
            label = f"{child_name} {signature}".rstrip()
            lines.append(f"{prefix}{connector}{label}  # {_purpose(child)}.")
            lines.extend(_tree_lines(child, child_name, prefix + child_prefix))
    return lines


def render_command_tree(command: click.Command, prog_name: str = "chatnpm") -> str:
    """Render the public command tree from the registered Click surface."""

    lines = [f"{prog_name}  # {_purpose(command)}."]
    lines.extend(
        [
            "├── --help  # Show this help message.",
            "├── --version  # Show the installed package version.",
            "├── --tree  # Print the registered command tree.",
        ]
    )
    child_lines = _tree_lines(command, prog_name)
    if child_lines:
        # The top-level pseudo-options above are siblings of the real command groups.
        # Keep their branches open by converting the first real child connector if needed.
        lines.extend(child_lines)
    return "\n".join(lines)


@click.group(invoke_without_command=True)
@click.version_option(__version__, prog_name="chatnpm")
@click.option("--tree", is_flag=True, help="Print the command tree and exit.")
@click.pass_context
def main(ctx: click.Context, tree: bool) -> None:
    """ChatArch npm registry and publishing-evidence helper."""

    if tree:
        click.echo(render_command_tree(ctx.command, "chatnpm"))
        ctx.exit(0)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        ctx.exit(0)


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
