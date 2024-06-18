import sqlite3


def row_to_dict(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
    data = {}
    for idx, col in enumerate(cursor.description):
        data[col[0]] = row[idx]
    return data


class Database:
    def __init__(self, db):
        # 临时允许跨线程访问
        self.conn = sqlite3.connect(db, check_same_thread=False)
        self.conn.row_factory = row_to_dict
        self.cur = self.conn.cursor()

    def __del__(self):
        self.cur.close()
        self.conn.close()

    def execute(self, sql, params=()):
        self.cur.execute(sql, params)
        self.conn.commit()


class OutcomeDatabase:
    def __init__(self):
        self.db = Database("outcome.db")
        self.db.execute(
            sql="""CREATE TABLE IF NOT EXISTS outcome
                (id INTEGER PRIMARY KEY,
                 filename TEXT, path TEXT not null,
                 type TEXT not null,
                 md5 TEXT not null unique on conflict ignore,
                 save_path TEXT not null unique on conflict ignore,
                 status TEXT DEFAULT "pending",
                 created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                 updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )""",
        )

    def insert(self, filename, path, type, md5, save_path):
        self.db.execute(
            sql="""INSERT INTO outcome (filename, path, type, md5, save_path, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, "pending", CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
            params=(filename, path, type, md5, save_path),
        )
        return self.get(md5)

    def update(self, status, md5):
        self.db.execute(
            sql="""UPDATE outcome SET status = ? WHERE md5 = ?""",
            params=(status, md5),
        )
        return self.get(md5)

    def get(self, md5):
        self.db.execute(
            sql="""SELECT * FROM outcome WHERE md5 = ?""",
            params=(md5,),
        )
        return self.db.cur.fetchone()

    def get_all(self):
        self.db.execute(
            sql="""SELECT * FROM outcome""",
        )
        return self.db.cur.fetchall()

    def get_all_with_type(self, type, status=None):
        if status:
            self.db.execute(
                sql="""SELECT * FROM outcome WHERE type = ? AND status = ?""",
                params=(type, status),
            )
        else:
            self.db.execute(
                sql="""SELECT * FROM outcome WHERE type = ?""",
                params=(type,),
            )
        return self.db.cur.fetchall()

    def delete(self, md5):
        self.db.execute(
            sql="""DELETE FROM outcome WHERE md5 = ?""",
            params=(md5,),
        )

    def delete_all(self):
        self.db.execute()


class UserDatabase:
    def __init__(self) -> None:
        self.db = Database("user.db")
        self.db.execute(
            sql="""CREATE TABLE IF NOT EXISTS user
                (id INTEGER PRIMARY KEY,
                 username TEXT not null unique,
                 password TEXT not null,
                 status TEXT DEFAULT "active",
                 created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                 updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )""",
        )

    def insert(self, username, password):
        self.db.execute(
            sql="""INSERT INTO user (username, password, status, created_at, updated_at)
                VALUES (?, ?, "active", CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)""",
            params=(username, password),
        )
        return self.get(username)

    def get(self, username=None, userid=None):
        if username:
            self.db.execute(
                sql="""SELECT * FROM user WHERE username = ?""",
                params=(username,),
            )
        elif userid:
            self.db.execute(
                sql="""SELECT * FROM user WHERE id = ?""",
                params=(userid,),
            )
        return self.db.cur.fetchone()

    # 注销
    def deactivate(self, userid):
        self.db.execute(
            sql="""UPDATE user SET status = "inactive" WHERE id = ?""",
            params=(userid,),
        )
        return self.get(userid)
