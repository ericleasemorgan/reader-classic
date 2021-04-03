import datetime
from flask_login import UserMixin

from db import get_db

# User represents a single person who interacts with this site.
# Make sure to save changes to a User to the database.
# Also, the identifiers used to identify a user is assigned by
# the database, so it won't be assigned until the record is saved
# to the database for the first time.
class User(UserMixin):
    def __init__(self, id_=None, username="", name="", email="", date="", orcid=""):
        self.id = id_
        self.username = username
        self.name = name
        self.email = email
        self.create_date = date
        self.orcid = orcid

    def save(self):
        db = get_db()
        if self.create_date == "":
            self.create_date = datetime.date.today()
        if self.id is None:
            rowid = db.execute("""INSERT INTO patrons (username, name, email, date, orcid)
                VALUES (?, ?, ?, ?)
                RETURNING rowid""",
                (self.username,
                self.name,
                self.email,
                self.create_date,
                self.orcid)).fetchone()
            self.id = rowid[0]
            db.commit()
            return

        db.execute("""INSERT OR REPLACE INTO patrons (rowid, username, name, email, date, orcid)
            VALUES (?, ?, ?, ?, ?)""",
            self.id,
            self.username,
            self.name,
            self.email,
            self.create_date,
            self.orcid)
        db.commit()

    @staticmethod
    def FromID(id_):
        db = get_db()
        record = db.execute("""SELECT rowid, username, name, email, date, orcid
            FROM patrons
            WHERE rowid = ?""",
            (id_,)).fetchone()
        if not record:
            return None
        return User(record[0], record[1], record[2], record[3], record[4], record[5])

    @staticmethod
    def FromUsername(username):
        db = get_db()
        record = db.execute("""SELECT rowid, username, name, email, date, orcid
            FROM patrons
            WHERE username = ?""",
            (username,)).fetchone()
        if record is None:
            return None
        return User(record[0], record[1], record[2], record[3], record[4], record[5])

    @staticmethod
    def FromORCID(orcid):
        db = get_db()
        record = db.execute("""SELECT rowid, username, name, email, date, orcid
            FROM patrons
            WHERE orcid = ?""",
            (orcid,)).fetchone()
        if record is None:
            return None
        return User(record[0], record[1], record[2], record[3], record[4], record[5])



