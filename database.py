import sqlite3 as sql
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from logger import log


class Database:
    """Same API as original code, but with micro-optimisations and type hints."""

    def __init__(self, db_path: str | Path = "database.db", encryption_key: Optional[bytes] = None):
        from cryptography.fernet import Fernet  # lazy import to fail gracefully if absent

        self.path = Path(db_path)
        self._conn: Optional[sql.Connection] = None
        self._cursor: Optional[sql.Cursor] = None

        if encryption_key is None:
            log.warning("No encryption key supplied – generating volatile session key.")
            encryption_key = Fernet.generate_key()
        self.fernet = Fernet(encryption_key)

    def _enc(self, txt: str | None) -> str | None:
        return self.fernet.encrypt(txt.encode()).decode() if txt is not None else None

    def _dec(self, txt: str | None) -> str | None:
        return self.fernet.decrypt(txt.encode()).decode() if txt is not None else None

    def __enter__(self):
        self.open()
        self._create_tables()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def open(self):
        self._conn = sql.connect(self.path)
        self._cursor = self._conn.cursor()
        self._cursor.execute("PRAGMA foreign_keys = ON;")
        log.info("Opened DB at %s", self.path)

    def close(self):
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()
        self._cursor = self._conn = None
        log.info("Closed DB")

    @contextmanager
    def _tx(self):
        try:
            yield
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def _create_tables(self):
        with self._tx():
            cur = self._cursor
            cur.execute(
                    """CREATE TABLE IF NOT EXISTS User (
                        user_id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE,
                        hashed_password TEXT NOT NULL,
                        is_admin BOOLEAN NOT NULL
                    );"""
            )
            cur.execute(
                    """CREATE TABLE IF NOT EXISTS Task (
                        task_id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        description TEXT NOT NULL,
                        expiration_date TEXT,
                        validation_rules TEXT NOT NULL
                    );"""
            )
            cur.execute(
                    """CREATE TABLE IF NOT EXISTS TestCase (
                        test_id INTEGER PRIMARY KEY,
                        input_data TEXT NOT NULL,
                        expected_output TEXT NOT NULL,
                        task_id INTEGER NOT NULL
                            REFERENCES Task(task_id) ON DELETE CASCADE
                    );"""
            )
            cur.execute(
                    """CREATE TABLE IF NOT EXISTS UserTask (
                        user_id INTEGER NOT NULL REFERENCES User(user_id),
                        task_id INTEGER NOT NULL REFERENCES Task(task_id),
                        PRIMARY KEY (user_id, task_id)
                    );"""
            )

    def add_user(self, name: str, hashed_password: str, is_admin: bool):
        with self._tx():
            self._cursor.execute(
                    "INSERT INTO User(name, hashed_password, is_admin) VALUES (?,?,?);",
                    (name, self._enc(hashed_password), is_admin),
            )

    def get_users(self):
        self._cursor.execute("SELECT user_id, name, hashed_password, is_admin FROM User;")
        for uid, name, hp, adm in self._cursor.fetchall():
            yield uid, name, self._dec(hp), bool(adm)

    def get_user_id(self, name: str) -> Optional[int]:
        self._cursor.execute("SELECT user_id FROM User WHERE name=?;", (name,))
        res = self._cursor.fetchone()
        return res[0] if res else None

    def get_password(self, user_id: int) -> Optional[str]:
        self._cursor.execute("SELECT hashed_password FROM User WHERE user_id=?;", (user_id,))
        row = self._cursor.fetchone()
        return self._dec(row[0]) if row else None

    def is_admin(self, user_id: int) -> bool:
        self._cursor.execute("SELECT is_admin FROM User WHERE user_id=?;", (user_id,))
        row = self._cursor.fetchone()
        return bool(row[0]) if row else False

    def add_task(
        self,
        title: str,
        description: str,
        expiration_date: str | None,
        rules: str,
        tests: list[tuple[str, str]] | None = None,
    ) -> int:
        """Add a task and optional test cases. Return new task_id."""
        with self._tx():
            cur = self._cursor
            cur.execute(
                "INSERT INTO Task(title, description, expiration_date, validation_rules) VALUES (?,?,?,?);",
                (
                    self._enc(title),
                    self._enc(description),
                    self._enc(expiration_date) if expiration_date else None,
                    self._enc(rules),
                ),
            )
            task_id = cur.lastrowid
            if tests:
                for case, ans in tests:
                    cur.execute(
                        "INSERT INTO TestCase(input_data, expected_output, task_id) VALUES (?,?,?);",
                        (
                            self._enc(case),
                            self._enc(ans),
                            task_id,
                        ),
                    )
        return task_id

    def get_tasks_for_user(self, user_id: int):
        self._cursor.execute(
                """SELECT t.task_id, t.title, t.description, t.expiration_date, t.validation_rules
                   FROM Task t JOIN UserTask ut ON t.task_id = ut.task_id WHERE ut.user_id=?;""",
                (user_id,),
        )
        for row in self._cursor.fetchall():
            tid, tl, desc, exp, rules = row
            yield tid, self._dec(tl), self._dec(desc), self._dec(exp) if exp else None, self._dec(rules)

    def get_tasks(self):
        """Yield all tasks in the Task table (decoded)."""
        self._cursor.execute(
                "SELECT task_id, title, description, expiration_date, validation_rules FROM Task;"
        )
        for tid, tl, desc, exp, rules in self._cursor.fetchall():
            yield (
                tid,
                self._dec(tl),
                self._dec(desc),
                self._dec(exp) if exp else None,
                self._dec(rules),
            )

    def add_test_case(self, task_id: int, input_data: str, expected_output: str):
        """Add a new test case for the given task."""
        with self._tx():
            self._cursor.execute(
                "INSERT INTO TestCase(input_data, expected_output, task_id) VALUES (?,?,?);",
                (
                    self._enc(input_data),
                    self._enc(expected_output),
                    task_id,
                ),
            )

    def get_test_cases(self, task_id: int):
        """Yield (case, answer) pairs for the task."""
        self._cursor.execute(
            "SELECT input_data, expected_output FROM TestCase WHERE task_id=?;",
            (task_id,),
        )
        for case, ans in self._cursor.fetchall():
            yield self._dec(case), self._dec(ans)

    def assign_task(self, user_id: int, task_id: int):
        """Assign a task to the user."""
        with self._tx():
            self._cursor.execute(
                "INSERT OR IGNORE INTO UserTask(user_id, task_id) VALUES (?,?);",
                (user_id, task_id),
            )
