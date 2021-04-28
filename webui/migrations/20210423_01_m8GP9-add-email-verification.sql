-- add email verification
-- depends: 20210330_01_f5sw7-add-orcid

CREATE TABLE email_tokens (
    token       TEXT,       -- the token sent
    sentdate    TEXT,
    email       TEXT,       -- email this token is verifying
    userid      INTEGER     -- foreign key to patrons
);

CREATE INDEX i_email_tokens on email_tokens (token);
CREATE INDEX i_email_patrons on email_tokens (userid);


ALTER TABLE patrons
    ADD COLUMN email_verify_date TEXT;

-- treat every existing account as being verified
UPDATE patrons
    SET email_verify_date = datetime("now");

