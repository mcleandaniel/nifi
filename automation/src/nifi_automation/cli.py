"""Command-line entry point for NiFi REST automation."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from rich.console import Console

from .auth import AuthenticationError, obtain_access_token
from .client import NiFiClient
from .config import AuthSettings, build_settings
from .controller_registry import ensure_root_controller_services
from .flow_builder import FlowDeploymentError, deploy_flow_from_file

console = Console()
app = typer.Typer(help="Interact with Apache NiFi via the REST API.")


def _resolve_settings(
    base_url: Optional[str],
    username: Optional[str],
    password: Optional[str],
    verify_ssl: Optional[bool],
    timeout: float,
) -> AuthSettings:
    return build_settings(base_url, username, password, verify_ssl, timeout)


def _ensure_credentials(settings: AuthSettings) -> AuthSettings:
    updated = settings
    if not updated.username:
        updated = updated.merged(username=typer.prompt("NiFi username"))
    if not updated.password:
        updated = updated.merged(password=typer.prompt("NiFi password", hide_input=True))
    return updated


@app.command("auth-token")
def auth_token(
    base_url: Optional[str] = typer.Option(
        None, help="NiFi base URL (e.g. https://localhost:8443/nifi-api)"
    ),
    username: Optional[str] = typer.Option(None, help="NiFi username"),
    password: Optional[str] = typer.Option(None, help="NiFi password"),
    verify_ssl: bool = typer.Option(False, "--verify-ssl", is_flag=True, help="Verify TLS certificates"),
    timeout: float = typer.Option(10.0, help="HTTP timeout in seconds"),
) -> None:
    """Fetch and display a bearer token."""

    settings = _resolve_settings(base_url, username, password, verify_ssl, timeout)
    settings = _ensure_credentials(settings)
    try:
        token = obtain_access_token(settings)
    except AuthenticationError as exc:
        console.print(f"[red]Authentication failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Token:[/green] {token}")


@app.command("flow-summary")
def flow_summary(
    base_url: Optional[str] = typer.Option(None, help="NiFi base URL"),
    username: Optional[str] = typer.Option(None, help="NiFi username"),
    password: Optional[str] = typer.Option(None, help="NiFi password"),
    verify_ssl: bool = typer.Option(False, "--verify-ssl", is_flag=True, help="Verify TLS certificates"),
    timeout: float = typer.Option(10.0, help="HTTP timeout in seconds"),
) -> None:
    """Retrieve the root process group summary."""

    settings = _resolve_settings(base_url, username, password, verify_ssl, timeout)
    settings = _ensure_credentials(settings)
    try:
        token = obtain_access_token(settings)
    except AuthenticationError as exc:
        console.print(f"[red]Authentication failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    with NiFiClient(settings, token) as client:
        response = client.get_root_flow()

    root_pg = response.get("processGroupFlow", {}).get("id", "<unknown>")
    name = (
        response.get("processGroupFlow", {})
        .get("breadcrumb", {})
        .get("breadcrumb", {})
        .get("name", "<unknown>")
    )
    console.print("[cyan]Root Process Group Summary[/cyan]")
    console.print(f"ID   : {root_pg}")
    console.print(f"Name : {name}")


@app.command("deploy-flow")
def deploy_flow(
    file: Path = typer.Argument(..., help="Path to flow specification YAML/JSON"),
    base_url: Optional[str] = typer.Option(None, help="NiFi base URL"),
    username: Optional[str] = typer.Option(None, help="NiFi username"),
    password: Optional[str] = typer.Option(None, help="NiFi password"),
    verify_ssl: bool = typer.Option(False, "--verify-ssl", is_flag=True, help="Verify TLS certificates"),
    timeout: float = typer.Option(10.0, help="HTTP timeout in seconds"),
) -> None:
    """Deploy a flow from a declarative specification file."""

    settings = _resolve_settings(base_url, username, password, verify_ssl, timeout)
    settings = _ensure_credentials(settings)

    spec_path = file if file.is_absolute() else Path.cwd() / file
    if not spec_path.exists():
        console.print(f"[red]Specification not found:[/red] {spec_path}")
        raise typer.Exit(code=1)

    try:
        token = obtain_access_token(settings)
    except AuthenticationError as exc:
        console.print(f"[red]Authentication failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    try:
        with NiFiClient(settings, token) as client:
            service_map = ensure_root_controller_services(client)
            pg_id = deploy_flow_from_file(client, spec_path, controller_service_map=service_map)
    except FlowDeploymentError as exc:
        console.print(f"[red]Deployment error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Flow deployed successfully[/green] (Process Group ID: {pg_id})")


if __name__ == "__main__":  # pragma: no cover - CLI entry
    app()
