-- Add carrel table
-- depends: 20210423_01_m8GP9-add-email-verification

CREATE TABLE if not exists carrels (
    owner       TEXT,   -- username of who "owns" this carrel
    shortname   TEXT,   -- the shortname of this carrel
    fullpath    TEXT,   -- the absolute path to the carrel directory
    status      TEXT,   -- the status of this carrel
    created     TEXT,   -- the datetime this carrel was created
    items       INTEGER,-- the number of source items
    words       INTEGER,-- the total number of source words
    readability INTEGER,-- the calculated readability score
    bytes       INTEGER -- the total number of source bytes
);

CREATE UNIQUE INDEX i_carrel_owner_name on carrels (owner, shortname);
CREATE INDEX i_carrel_owner on carrels (owner);
CREATE INDEX i_carrel_name on carrels (shortname);
CREATE INDEX i_carrel_status on carrels (status);
