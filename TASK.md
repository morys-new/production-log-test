# ProdLog — Task Specification

## Product requirements

ProdLog is a small production reporting tool for a fictional mine, "Test Mine A". Three layers: a FastAPI backend, a Next.js web page, and an Expo mobile screen, all talking to the same backend.

You design the API, the schema, and the data shapes. We are not telling you what to name endpoints or what response objects look like. That is part of what we evaluate.

These are the product requirements. Your design should serve them.

- A mine has several pits. A user can create pits (a pit has a name).
- A site operator can log a production entry for one pit: report date, shift, material (ore or overburden), planned tonnes, and actual tonnes.
- Entries move through a status: draft → submitted → approved. A supervisor can also send a submitted entry back to draft. Approved is final.
- An operator can correct the numbers of an entry while it is not yet approved.
- Business rule: once an entry is approved it is locked. Its status cannot change and its numbers cannot be edited. Enforce this in the backend, not just the frontend.
- Users can view all entries and filter them by status and/or pit.
- A user can see a summary that a mine manager would find useful. What it contains is your design decision. Think about what a manager actually needs to know.
- Web and mobile display entries and allow filtering. The web app also allows creating entries.

## Technical constraints

These reflect the conventions of the codebase you'd work on if hired. They are non-negotiable.

**Backend**

- FastAPI + asyncpg. No ORM. No SQLAlchemy, no Tortoise. Raw SQL only.
- Every endpoint must have a Pydantic `response_model=`. No exceptions.
- Router functions stay thin. No business logic or db queries inline in routers.
- Full Python type hints on every function.
- Real local Postgres. The schema is yours: write `CREATE TABLE` statements in `migration.sql` and run them before you start building.

**Web (Next.js)**

- TypeScript `strict: true` (already set). No `any`.
- Define all API response interfaces in `shared/types.ts`. `web/types/api.ts` already re-exports everything from it, so import your types from there. Do not redefine them.

**Mobile (Expo)**

- TypeScript `strict: true`. No `any`.
- Import interfaces from `shared/types.ts`. Do not redefine them.

## Web

A single page that:

- Shows the summary and the entry list on load
- Filters entries by status without re-fetching
- Has a form to create an entry (including choosing a pit)
- Updates the list and summary after creating an entry
- Handles loading and error states

## Mobile

A single screen that shows the entry list, filters by status, and supports pull-to-refresh.

## Ambiguity note

The spec does not define what the summary should contain. If you have a question, ask before you build. If you make an assumption, note it and explain why.
