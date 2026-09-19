#!/usr/bin/env python3
"""ProdLog environment doctor — stdlib only, safe to run before any install.

Run from the repository root:
    python scripts/doctor.py
"""
import importlib
import importlib.util
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT / "backend"

# ── result tracking ──────────────────────────────────────────────────────────

_results: list[tuple[str, str, str]] = []  # (status, label, hint)


def _record(status: str, label: str, hint: str = "") -> None:
    _results.append((status, label, hint))
    icon = {"PASS": "+", "WARN": "!", "FAIL": "x"}[status]
    line = f"  [{icon}] {status:<4}  {label}"
    if hint:
        line += f"\n             -> {hint}"
    print(line)


# ── individual checks ────────────────────────────────────────────────────────

def check_python() -> None:
    v = sys.version_info
    label = f"Python {v.major}.{v.minor}.{v.micro}"
    if v >= (3, 10):
        _record("PASS", label)
    else:
        _record("FAIL", label, "Upgrade to Python 3.10 or newer.")


def check_node() -> None:
    node_path = shutil.which("node")
    if node_path is None:
        _record("FAIL", "Node not found", "Install Node 20+ from https://nodejs.org")
        return
    out = subprocess.run([node_path, "--version"], capture_output=True, text=True)
    ver = out.stdout.strip().lstrip("v")
    try:
        major = int(ver.split(".")[0])
    except ValueError:
        major = 0
    label = f"Node {ver}"
    if major >= 20:
        _record("PASS", label)
    else:
        _record("FAIL", label, "Upgrade to Node 20+ (use nvm or https://nodejs.org).")


def check_npm() -> None:
    npm_path = shutil.which("npm")
    if npm_path is None:
        _record("FAIL", "npm not found", "npm is bundled with Node -- install Node 20+.")
        return
    out = subprocess.run([npm_path, "--version"], capture_output=True, text=True)
    _record("PASS", f"npm {out.stdout.strip()}")


def check_git() -> None:
    git_path = shutil.which("git")
    if git_path is None:
        _record("FAIL", "git not found", "Install git from https://git-scm.com")
        return
    out = subprocess.run([git_path, "--version"], capture_output=True, text=True)
    _record("PASS", out.stdout.strip())


def check_backend_env() -> str | None:
    env_path = BACKEND_DIR / ".env"
    if not env_path.exists():
        _record(
            "FAIL",
            "backend/.env missing",
            "cp backend/.env.example backend/.env  (then edit if needed)",
        )
        return None
    _record("PASS", "backend/.env exists")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL="):
            return line[len("DATABASE_URL="):].strip()
    return None


def check_frontend_envs() -> None:
    for name in ("web/.env", "mobile/.env"):
        path = ROOT / name
        status = "PASS" if path.exists() else "WARN"
        hint = "" if path.exists() else f"cp {name}.example {name}"
        _record(status, f"{name} {'exists' if path.exists() else 'missing'}", hint)


def _mask(url: str) -> str:
    return re.sub(r"(?<=://)([^:]+):([^@]+)@", r"\1:***@", url)


def _parse_host_port(url: str) -> tuple[str, int]:
    hostpart = url.split("://", 1)[-1].split("@", 1)[-1].split("/")[0]
    if ":" in hostpart:
        host, port_str = hostpart.rsplit(":", 1)
        return host, int(port_str)
    return hostpart, 5432


def check_database(database_url: str | None) -> None:
    if database_url is None:
        _record("FAIL", "DATABASE_URL not set -- skipping DB check", "Fix backend/.env first.")
        return

    masked = _mask(database_url)
    host, port = _parse_host_port(database_url)

    try:
        with socket.create_connection((host, port), timeout=3):
            pass
    except OSError as exc:
        _record(
            "FAIL",
            f"DB TCP {host}:{port} unreachable",
            f"{exc}  -- is Postgres running?  (docker compose up -d prodlog-db)",
        )
        return

    # Deeper check when asyncpg is already installed
    try:
        import asyncio

        import asyncpg  # type: ignore[import-untyped]

        async def _ping() -> str:
            conn = await asyncpg.connect(database_url)
            try:
                ver: str = await conn.fetchval("SELECT version()")
            finally:
                await conn.close()
            return ver

        ver = asyncio.run(_ping())
        major = int(ver.split()[1].split(".")[0])
        if major >= 13:
            _record("PASS", f"Postgres {ver.split()[1]} -- reachable and SELECT 1 OK")
        else:
            _record(
                "FAIL",
                f"Postgres {ver.split()[1]} too old",
                "gen_random_uuid() requires Postgres 13+.  Upgrade your server.",
            )
    except ImportError:
        _record(
            "PASS",
            f"DB TCP {host}:{port} reachable (asyncpg not installed; install deps for full check)",
        )
    except Exception as exc:
        _record("FAIL", f"DB query failed ({masked})", str(exc))


def check_backend_deps() -> None:
    packages = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "pydantic": "pydantic",
        "pydantic_settings": "pydantic-settings",
        "asyncpg": "asyncpg",
    }
    missing = [pip for mod, pip in packages.items() if importlib.util.find_spec(mod) is None]
    if not missing:
        _record("PASS", "Backend Python deps importable")
    else:
        _record(
            "FAIL",
            f"Missing backend deps: {', '.join(missing)}",
            "pip install -r backend/requirements.txt",
        )


def check_node_modules() -> None:
    for name in ("web", "mobile"):
        nm = ROOT / name / "node_modules"
        if nm.is_dir():
            _record("PASS", f"{name}/node_modules present")
        else:
            _record("WARN", f"{name}/node_modules missing", f"cd {name} && npm ci")


def check_ports() -> None:
    for port in (8000, 3000):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.3):
                _record(
                    "WARN",
                    f"Port {port} already in use",
                    f"Another process is on :{port} -- stop it or it will conflict.",
                )
        except OSError:
            _record("PASS", f"Port {port} free")


# ── entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    print("\n=== ProdLog Doctor ===\n")

    check_python()
    check_node()
    check_npm()
    check_git()
    db_url = check_backend_env()
    check_frontend_envs()
    check_database(db_url)
    check_backend_deps()
    check_node_modules()
    check_ports()

    passes = sum(1 for s, _, _ in _results if s == "PASS")
    warns  = sum(1 for s, _, _ in _results if s == "WARN")
    fails  = sum(1 for s, _, _ in _results if s == "FAIL")

    print()
    print("=" * 50)
    print("  SUMMARY")
    print(f"  OS      : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"  Python  : {sys.version.split()[0]}")
    node_ver = "n/a"
    _node_path = shutil.which("node")
    if _node_path:
        r = subprocess.run([_node_path, "--version"], capture_output=True, text=True)
        node_ver = r.stdout.strip()
    print(f"  Node    : {node_ver}")
    print(f"  Checks  : {passes} PASS  {warns} WARN  {fails} FAIL")
    if fails:
        print("\n  Fix FAIL items above before starting the test.")
    elif warns:
        print("\n  Required checks pass. Resolve WARNs when convenient.")
    else:
        print("\n  All checks pass. You're good to go.")
    print("=" * 50 + "\n")

    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
