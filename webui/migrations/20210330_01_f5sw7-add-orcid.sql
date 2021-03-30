-- add orcid
-- depends: 20210323_01_2Jk7q-initial-schema

-- ORCIDs are stored as "0000-0000-0000-0000"
ALTER TABLE patrons
    ADD COLUMN orcid TEXT;

CREATE INDEX IF NOT EXISTS patron_orcid_idx ON patrons (orcid);

