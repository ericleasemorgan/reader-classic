import datetime
import smtplib
from email.message import EmailMessage
from flask_login import UserMixin

from app import app
from db import get_db

# User represents a single person who interacts with this site.
# Make sure to save changes to a User to the database.
# Also, the identifiers used to identify a user is assigned by
# the database, so it won't be assigned until the record is saved
# to the database for the first time.
class User(UserMixin):
    def __init__(
        self,
        id_=None,
        username="",
        name="",
        email="",
        date="",
        orcid="",
        email_verify_date="",
    ):
        self.id = id_
        self.username = username
        self.name = name
        self.email = email
        self.create_date = date
        self.orcid = orcid
        self.email_verify_date = email_verify_date

    def save(self):
        db = get_db()
        if self.create_date == "":
            self.create_date = datetime.date.today()
        if self.id is None:
            rowid = db.execute(
                """INSERT INTO patrons (username, name, email, date, orcid, email_verify_date)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    self.username,
                    self.name,
                    self.email,
                    self.create_date,
                    self.orcid,
                    self.email_verify_date,
                ),
            )
            db.commit()
            # we need to figure out what rowid was assigned to the record.
            # (The INSERT INTO ... RETURNING statement is not in the production version of
            # sqlite)
            u = User.FromUsername(self.username)
            self.id = u.id
            return

        db.execute(
            """INSERT OR REPLACE INTO patrons (rowid, username, name, email, date, orcid, email_verify_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                self.id,
                self.username,
                self.name,
                self.email,
                self.create_date,
                self.orcid,
                self.email_verify_date,
            ),
        )
        db.commit()

    @staticmethod
    def FromID(id_):
        db = get_db()
        record = db.execute(
            """SELECT rowid, username, name, email, date, orcid, email_verify_date
            FROM patrons
            WHERE rowid = ?""",
            (id_,),
        ).fetchone()
        if not record:
            return None
        return User(
            record[0], record[1], record[2], record[3], record[4], record[5], record[6]
        )

    @staticmethod
    def FromUsername(username):
        db = get_db()
        record = db.execute(
            """SELECT rowid, username, name, email, date, orcid, email_verify_date
            FROM patrons
            WHERE username = ?""",
            (username,),
        ).fetchone()
        if record is None:
            return None
        return User(
            record[0], record[1], record[2], record[3], record[4], record[5], record[6]
        )

    @staticmethod
    def FromORCID(orcid):
        db = get_db()
        record = db.execute(
            """SELECT rowid, username, name, email, date, orcid, email_verify_date
            FROM patrons
            WHERE orcid = ?""",
            (orcid,),
        ).fetchone()
        if record is None:
            return None
        return User(
            record[0], record[1], record[2], record[3], record[4], record[5], record[6]
        )


class EmailToken(object):
    def __init__(self, token="", sentdate="", email="", userid=-1):
        self.token = token
        self.sentdate = sentdate
        self.email = email
        self.userid = userid

    def save(self):
        assert self.userid > 0
        db = get_db()
        if self.sentdate == "":
            self.sentdate = datetime.date.today()
        db.execute(
            """INSERT INTO email_tokens (token, sentdate, email, userid)
            VALUES (?, ?, ?, ?)""",
            (self.token, self.sentdate, self.email, self.userid),
        )
        db.commit()

    def delete(self):
        assert self.token != ""
        db = get_db()
        db.execute(
            """DELETE FROM email_tokens WHERE token = ?""",
            (self.token,),
        )
        db.commit()

    @staticmethod
    def FromToken(token):
        db = get_db()
        record = db.execute(
            """SELECT token, sentdate, email, userid
            FROM email_tokens
            WHERE token = ?""",
            (token,),
        ).fetchone()
        if record is None:
            return None
        return EmailToken(record[0], record[1], record[2], record[3])


def send_email(to="", subject="", body=""):
    if app.debug:
        print("Send Email")
        print("To: ", to)
        print("Subject: ", subject)
        print(body)
        return
    message = EmailMessage()
    message["Subject"] = subject
    message["To"] = to
    message["From"] = "noreply@distantreader.org"
    message.set_content(body)
    s = smtplib.SMTP("localhost")
    s.send_message(message)
    s.quit()


class StudyCarrel(object):
    def __init__(
        self,
        owner="",
        shortname="",
        fullpath="",
        status="",
        created="",
        size_items=0,
        size_words=0,
        readability=0,
        size_bytes=0,
        keywords="",
    ):
        self.owner = owner
        self.shortname = shortname
        self.fullpath = fullpath
        self.status = status
        self.created = created
        self.size_items = size_items
        self.size_words = size_words
        self.readability = readability
        self.size_bytes = size_bytes
        self.keywords = keywords

    def save(self):
        db = get_db()
        if self.created == "":
            self.created = datetime.date.today()
        db.execute(
            """INSERT OR REPLACE INTO carrels (owner, shortname, fullpath, status, created, items, words, readability, bytes, keywords) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                self.owner,
                self.shortname,
                self.fullpath,
                self.status,
                self.created,
                self.size_items,
                self.size_words,
                self.readability,
                self.size_bytes,
                self.keywords,
            ),
        )
        db.commit()

    @staticmethod
    def FromOwnerShortname(owner, shortname):
        db = get_db()
        record = db.execute(
            """SELECT owner, shortname, fullpath, status, created, items, words, readability, bytes, keywords
            FROM carrels
            WHERE owner = ? and shortname = ?""",
            (owner, shortname),
        ).fetchone()
        if record is None:
            return None
        return StudyCarrel(
            record[0],
            record[1],
            record[2],
            record[3],
            record[4],
            record[5],
            record[6],
            record[7],
            record[8],
            record[9],
        )

    @staticmethod
    def ForOwner(owner):
        db = get_db()
        records = db.execute(
            """SELECT owner, shortname, fullpath, status, created, items, words, readability, bytes, keywords
            FROM carrels
            WHERE owner = ?""",
            (owner,),
        ).fetchall()
        return [
            StudyCarrel(
                record[0],
                record[1],
                record[2],
                record[3],
                record[4],
                record[5],
                record[6],
                record[7],
                record[8],
                record[9],
            )
            for record in records
        ]

    @staticmethod
    def ForPublic():
        db = get_db()
        records = db.execute(
            """SELECT owner, shortname, fullpath, status, created, items, words, readability, bytes, keywords
            FROM carrels
            WHERE status = "public" """,
        ).fetchall()
        return [
            StudyCarrel(
                record[0],
                record[1],
                record[2],
                record[3],
                record[4],
                record[5],
                record[6],
                record[7],
                record[8],
                record[9],
            )
            for record in records
        ]

    @staticmethod
    def FromPublicShortname(shortname):
        db = get_db()
        record = db.execute(
            """SELECT owner, shortname, fullpath, status, created, items, words, readability, bytes, keywords
            FROM carrels
            WHERE status = "public" and shortname = ? """,
            (shortname,),
        ).fetchone()
        if record is None:
            return None
        return StudyCarrel(
            record[0],
            record[1],
            record[2],
            record[3],
            record[4],
            record[5],
            record[6],
            record[7],
            record[8],
            record[9],
        )

