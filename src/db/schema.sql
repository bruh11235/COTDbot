CREATE TABLE IF NOT EXISTS cfmap (
    discord TEXT PRIMARY KEY,
    codeforces TEXT,
    is_admin INTEGER NOT NULL DEFAULT 0 CHECK (is_admin IN (0, 1)),
    done_daily INTEGER NOT NULL DEFAULT 0 CHECK (done_daily IN (0, 1)),
    points INTEGER NOT NULL DEFAULT 0,
    mpoints INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS problem (
    pk INTEGER PRIMARY KEY,
    contestID TEXT,
    idx TEXT
);

CREATE INDEX IF NOT EXISTS pt_idx
ON cfmap(points);

CREATE INDEX IF NOT EXISTS mpt_idx
ON cfmap(mpoints);
