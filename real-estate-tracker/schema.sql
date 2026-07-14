CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address TEXT NOT NULL,
    suburb TEXT NOT NULL,
    price_text TEXT,
    price_numeric REAL,
    bedrooms INTEGER,
    bathrooms INTEGER,
    car_spaces INTEGER,
    land_size_sqm REAL,
    nearest_station TEXT,
    distance_to_station_m INTEGER,
    commute_to_flinders_min INTEGER,
    aspect TEXT,
    full_of_light INTEGER NOT NULL DEFAULT 0,
    listing_url TEXT,
    agent_name TEXT,
    agent_phone TEXT,
    inspection_date TEXT,
    status TEXT NOT NULL DEFAULT 'watching',
    notes TEXT,
    date_added TEXT NOT NULL,
    date_updated TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
