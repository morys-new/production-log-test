-- migration.sql
-- Add your DDL here. Run:  python scripts/apply_migration.py
-- The entire file executes in a single transaction; any error rolls back everything.

-- Re-runnable: drops and recreates every ProdLog object, so re-running WIPES ALL DATA.
-- (apply_migration.py --reset refuses database names without "test", e.g. "prodlog".)
DROP TABLE IF EXISTS production_entries;
DROP TABLE IF EXISTS pits;
DROP FUNCTION IF EXISTS production_entries_before_change();

-- Every pit belongs to the one mine this app serves ("Test Mine A"), so there is no
-- mines table.
CREATE TABLE pits (
    id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name       TEXT        NOT NULL CHECK (btrim(name) <> ''),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Case-insensitive, so "Pit A" and "pit a" cannot both exist.
CREATE UNIQUE INDEX pits_name_key ON pits (lower(name));

CREATE TABLE production_entries (
    id             UUID           PRIMARY KEY DEFAULT gen_random_uuid(),
    pit_id         UUID           NOT NULL REFERENCES pits (id) ON DELETE RESTRICT,
    report_date    DATE           NOT NULL,
    shift          TEXT           NOT NULL CHECK (shift IN ('day', 'night')),
    material       TEXT           NOT NULL CHECK (material IN ('ore', 'overburden')),
    planned_tonnes NUMERIC(12, 2) NOT NULL CHECK (planned_tonnes >= 0),
    actual_tonnes  NUMERIC(12, 2) NOT NULL CHECK (actual_tonnes >= 0),
    status         TEXT           NOT NULL DEFAULT 'draft'
                                  CHECK (status IN ('draft', 'submitted', 'approved')),
    created_at     TIMESTAMPTZ    NOT NULL DEFAULT now(),
    updated_at     TIMESTAMPTZ    NOT NULL DEFAULT now(),
    -- One report per pit, date, shift and material: a duplicate would double-count
    -- tonnes in the summary.
    CONSTRAINT production_entries_pit_date_shift_material_key
        UNIQUE (pit_id, report_date, shift, material)
);

-- Filtering by pit uses the unique key above (pit_id is its leading column).
CREATE INDEX production_entries_status_idx ON production_entries (status);
CREATE INDEX production_entries_report_date_idx ON production_entries (report_date);

-- Safety net under the service layer: an approved entry is final, so no UPDATE or
-- DELETE may touch it, whichever client runs the SQL. Also keeps updated_at current.
CREATE FUNCTION production_entries_before_change() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    IF OLD.status = 'approved' THEN
        RAISE EXCEPTION 'production entry % is approved and locked', OLD.id;
    END IF;
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;
    NEW.updated_at := now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER production_entries_before_change
    BEFORE UPDATE OR DELETE ON production_entries
    FOR EACH ROW EXECUTE FUNCTION production_entries_before_change();
