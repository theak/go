CREATE TABLE IF NOT EXISTS link (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL,
    description TEXT DEFAULT NULL,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    metadata JSON DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS name_values (
    name TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT OR IGNORE INTO name_values (name, value) VALUES ("domain", "go");
