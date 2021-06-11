-- Add keywords field
-- depends: 20210510_01_VWuSb-add-carrel-table

-- Keywords are stored as a single comma-seperated string
ALTER TABLE carrels
    ADD COLUMN keywords TEXT;
