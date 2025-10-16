"""Command-line entry point for NiFi REST automation."""

from __future__ import annotations


import logging
from pathlib import Path
from typing import Optional

import typer

from rich.console import Console

from .auth import AuthenticationError, obtain_access_token
from .client import NiFiClient
from .config import AuthSettings, build_settings
from .controller_registry import ensure_root_controller_services
from .flow_builder import FlowDeploymentError, deploy_flow_from_file
from .service_introspect import (
    collect_controller_service_requirements,
    format_requirements_as_json,
    format_requirements_as_markdown,
)

console = Console()
app = typer.Typer(help="Interact with Apache NiFi via the REST API.")
logger = logging.getLogger("nifi_automation.cli")


def _configure_logging(level: str) -> None:
    normalized = level.upper()
    mapping = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }
    if normalized not in mapping:
        raise typer.BadParameter(
            f"Invalid log level '{level}'. Choose from {', '.join(mapping.keys())}."
        )

    logging.basicConfig(
        level=mapping[normalized],
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    logger.debug("Log level configured: %s", normalized)


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
    log_level: str = typer.Option("INFO", "--log-level", help="Logging level"),
) -> None:
    """Fetch and display a bearer token."""

    _configure_logging(log_level)
    settings = _resolve_settings(base_url, username, password, verify_ssl, timeout)
    settings = _ensure_credentials(settings)
    try:
        logger.info("Requesting access token from %s", settings.base_url)
        token = obtain_access_token(settings)
    except AuthenticationError as exc:
        logger.error("Authentication failed: %s", exc)
        console.print(f"[red]Authentication failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    logger.info("Access token retrieved successfully.")
    console.print(f"[green]Token:[/green] {token}")


@app.command("flow-summary")
def flow_summary(
    base_url: Optional[str] = typer.Option(None, help="NiFi base URL"),
    username: Optional[str] = typer.Option(None, help="NiFi username"),
    password: Optional[str] = typer.Option(None, help="NiFi password"),
    verify_ssl: bool = typer.Option(False, "--verify-ssl", is_flag=True, help="Verify TLS certificates"),
    timeout: float = typer.Option(10.0, help="HTTP timeout in seconds"),
    log_level: str = typer.Option("INFO", "--log-level", help="Logging level"),
) -> None:
    """Retrieve the root process group summary."""

    _configure_logging(log_level)
    settings = _resolve_settings(base_url, username, password, verify_ssl, timeout)
    settings = _ensure_credentials(settings)
    try:
        logger.info("Obtaining access token for flow summary.")
        token = obtain_access_token(settings)
    except AuthenticationError as exc:
        logger.error("Authentication failed: %s", exc)
        console.print(f"[red]Authentication failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    with NiFiClient(settings, token) as client:
        logger.info("Fetching root flow information from NiFi.")
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
    log_level: str = typer.Option("INFO", "--log-level", help="Logging level"),
) -> None:
    """Deploy a flow from a declarative specification file."""

    _configure_logging(log_level)
    settings = _resolve_settings(base_url, username, password, verify_ssl, timeout)
    settings = _ensure_credentials(settings)

    spec_path = file if file.is_absolute() else Path.cwd() / file
    if not spec_path.exists():
        console.print(f"[red]Specification not found:[/red] {spec_path}")
        raise typer.Exit(code=1)

    try:
        logger.info("Authenticating to NiFi for deployment.")
        token = obtain_access_token(settings)
    except AuthenticationError as exc:
        logger.error("Authentication failed: %s", exc)
        console.print(f"[red]Authentication failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    try:
        with NiFiClient(settings, token) as client:
            logger.info("Ensuring root controller services are provisioned.")
            service_map = ensure_root_controller_services(client)
            logger.info("Deploying flow specification %s", spec_path)
            pg_id = deploy_flow_from_file(client, spec_path, controller_service_map=service_map)
    except FlowDeploymentError as exc:
        logger.exception("Deployment error: %s", exc)
        console.print(f"[red]Deployment error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    logger.info("Flow deployment completed. Process Group ID: %s", pg_id)
    console.print(f"[green]Flow deployed successfully[/green] (Process Group ID: {pg_id})")


@app.command("controller-services-report")
def controller_services_report(
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Path to write the report (stdout by default)"
    ),
    fmt: str = typer.Option(
        "markdown",
        "--format",
        "-f",
        help="Output format (markdown or json)",
        show_default=True,
    ),
    base_url: Optional[str] = typer.Option(None, help="NiFi base URL"),
    username: Optional[str] = typer.Option(None, help="NiFi username"),
    password: Optional[str] = typer.Option(None, help="NiFi password"),
    verify_ssl: bool = typer.Option(
        False, "--verify-ssl", is_flag=True, help="Verify TLS certificates"
    ),
    timeout: float = typer.Option(10.0, help="HTTP timeout in seconds"),
    log_level: str = typer.Option("INFO", "--log-level", help="Logging level"),
) -> None:
    """Generate a report of controller-service required properties."""

    _configure_logging(log_level)
    fmt = (fmt or "markdown").lower()
    valid_formats = {"markdown", "json"}
    if fmt not in valid_formats:
        raise typer.BadParameter(f"Unsupported format '{fmt}'. Choose from {sorted(valid_formats)}")

    settings = _resolve_settings(base_url, username, password, verify_ssl, timeout)
    settings = _ensure_credentials(settings)
    try:
        logger.info("Authenticating to NiFi for controller-service report.")
        token = obtain_access_token(settings)
    except AuthenticationError as exc:
        logger.error("Authentication failed: %s", exc)
        console.print(f"[red]Authentication failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    try:
        with NiFiClient(settings, token) as client:
            logger.info("Collecting controller service type metadata from NiFi.")
            requirements = collect_controller_service_requirements(client)
            logger.info("Retrieved %d controller service types.", len(requirements))
    except Exception as exc:  # pragma: no cover - network/REST failures
        logger.exception("Failed to collect controller service metadata: %s", exc)
        console.print(f"[red]Failed to collect controller service metadata:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    content = (
        format_requirements_as_json(requirements)
        if fmt == "json"
        else format_requirements_as_markdown(requirements)
    )

    if output:
        logger.info("Writing controller-service report to %s", output)
        output.write_text(content, encoding="utf-8")
        console.print(f"[green]Report written to[/green] {output}")
    else:
        logger.info("Writing controller-service report to stdout.")
        console.print(content)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    app()
