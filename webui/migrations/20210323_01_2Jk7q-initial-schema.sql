--
-- Initial schema for patron database
--

CREATE TABLE patrons (
    -- the compute code uses these fields
	username TEXT PRIMARY KEY,
	name     TEXT,
	email    TEXT,
	date     TEXT
    -- from here on is only used by the webui
);

