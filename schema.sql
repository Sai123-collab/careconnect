CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id TEXT UNIQUE,
    phone TEXT,
    password TEXT
);

CREATE TABLE IF NOT EXISTS checkups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aadhaar TEXT,
    disease TEXT,
    prescription TEXT
);
