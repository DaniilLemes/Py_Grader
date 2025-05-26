from __future__ import annotations

import hashlib
from app import AppM
from database import Database
from utils import hash_sha256


def main():
    key = b"6FZ8yxGRNCJ9YB5QeT1J3z2tKf5uXyJdvC9Bn8lT6iY="
    with Database(encryption_key=key) as db:
        if db.get_user_id("admin") is None:
            db.add_user("admin", hash_sha256("admin"), True)
        AppM(db).mainloop()


if __name__ == "__main__":
    main()