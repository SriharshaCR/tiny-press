CREATE TABLE IF NOT EXISTS compression_runs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp         TEXT    NOT NULL,
    model             TEXT    NOT NULL,
    tokenizer         TEXT    NOT NULL,
    input_tokens      INTEGER NOT NULL,
    output_tokens     INTEGER NOT NULL,
    target_tokens     INTEGER NOT NULL,
    compression_ratio REAL    NOT NULL,
    quality_score     REAL    NOT NULL,
    duration_ms       REAL    NOT NULL,
    input_text        TEXT    NOT NULL,
    output_text       TEXT    NOT NULL,
    feedback          INTEGER,
    feedback_comment  TEXT
);
