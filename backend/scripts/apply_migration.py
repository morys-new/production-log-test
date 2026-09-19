#!/usr/bin/env python3
"""Apply backend/migration.sql to the configured database.

Usage (run from the repo root or from backend/):
    python backend/scripts/apply_migration.py
    python backend/scripts/apply_migration.py --reset --yes
"""
from __future__ import annotations

import argparse
import asyncio
import os
import re
import sys
from pathlib import Path

try:
    import asyncpg
except ImportError:
    sys.exit("asyncpg not found — activate the virtual environment first.")

MIGRATION_FILE = Path(__file__).resolve().parent.parent / "migration.sql"


def _mask(url: str) -> str:
    return re.sub(r"(?<=://)([^:]+):([^@]+)@", r"\1:***@", url)


def _has_ddl(sql: str) -> bool:
    for line in sql.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("--"):
            return True
    return False


async def _run(database_url: str, reset: bool) -> None:
    db_name = database_url.rstrip("/").split("/")[-1].split("?")[0]
    if reset and "test" not in db_name:
        sys.exit(
            f"Safety check: --reset refused because the database name '{db_name}' "
            "does not contain 'test'. Point this script at a test database."
        )

    try:
        conn: asyncpg.Connection[asyncpg.Record] = await asyncpg.connect(database_url)
    except Exception as exc:
        sys.exit(f"Connection failed ({_mask(database_url)}): {exc}")

    try:
        async with conn.transaction():
            if reset:
                print("Dropping and recreating public schema…")
                await conn.execute("DROP SCHEMA public CASCADE")
                await conn.execute("CREATE SCHEMA public")

            sql = MIGRATION_FILE.read_text(encoding="utf-8").strip()
            if not _has_ddl(sql):
                print("migration.sql contains no DDL — nothing to apply.")
            else:
                await conn.execute(sql)
                print("Migration applied successfully.")
    finally:
        await conn.close()


def _load_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if url:
        return url

    for candidate in (
        Path(__file__).resolve().parent.parent / ".env",
        Path.cwd() / "backend" / ".env",
        Path.cwd() / ".env",
    ):
        if candidate.exists():
            for line in candidate.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("DATABASE_URL="):
                    return line[len("DATABASE_URL="):]

    sys.exit(
        "DATABASE_URL not set.\n"
        "  Option 1: copy backend/.env.example → backend/.env\n"
        "            then edit credentials if needed.\n"
        "  Option 2: export DATABASE_URL=postgresql://... before running this script."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Drop and recreate the public schema before applying (destructive).",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the interactive confirmation for --reset.",
    )
    args = parser.parse_args()

    if args.reset and not args.yes:
        confirm = input(
            "WARNING: --reset will DROP the entire public schema. "
            "Type 'yes' to continue: "
        )
        if confirm.strip().lower() != "yes":
            print("Aborted.")
            sys.exit(0)

    asyncio.run(_run(_load_database_url(), args.reset))


if __name__ == "__main__":
    main()
