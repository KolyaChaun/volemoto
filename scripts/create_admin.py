import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from getpass import getpass

from src.core.security import hash_password
from src.db.database import SessionLocal
from src.models.admin import Admin


def main():
    username = input("Логін адміністратора: ").strip()
    if not username:
        print("Логін не може бути порожнім.")
        sys.exit(1)

    password = getpass("Пароль: ")
    if len(password) < 8:
        print("Пароль повинен бути не менше 8 символів.")
        sys.exit(1)

    confirm = getpass("Повторіть пароль: ")
    if password != confirm:
        print("Паролі не збігаються.")
        sys.exit(1)

    db = SessionLocal()
    try:
        if db.query(Admin).filter_by(username=username).first():
            print(f"Адміністратор '{username}' вже існує.")
            sys.exit(1)

        admin = Admin(username=username, password_hash=hash_password(password))
        db.add(admin)
        db.commit()
        print(f"Адміністратор '{username}' успішно створений.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
