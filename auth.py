from database import connect
from datetime import datetime
import bcrypt


def _hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def _is_bcrypt_hash(s: str) -> bool:
    return isinstance(s, str) and s.startswith("$2")


# Реєстрація
def register(login, password, birth_date):
    if not login:
        print("Логін не може бути порожнім.")
        return False

    if len(password) < 4:
        print("Пароль має бути мінімум 4 символи.")
        return False

    try:
        datetime.strptime(birth_date, "%Y-%m-%d")
    except ValueError:
        print("Дата має бути у форматі YYYY-MM-DD.")
        return False

    conn = connect()
    if not conn:
        print("Проблема з базою")
        return False

    cur = None
    try:
        cur = conn.cursor()
        pwd_hash = _hash_password(password)

        cur.execute(
            "INSERT INTO users (login, password, birth_date) VALUES (%s, %s, %s)",
            (login, pwd_hash, birth_date)
        )
        conn.commit()
        print("Реєстрація успішна!")
        return True

    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Помилка реєстрації:", e)
        return False

    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        conn.close()


# Вхід
def login(login, password):
    conn = connect()
    if not conn:
        print("Проблема з базою")
        return None

    cur = None
    try:
        cur = conn.cursor()

        # беремо хеш/пароль і id по логіну
        cur.execute(
            "SELECT id, password FROM users WHERE login = %s",
            (login,)
        )
        row = cur.fetchone()
        if not row:
            return None

        user_id, stored = row

        # bcrypt-логіка
        if _is_bcrypt_hash(stored):
            ok = bcrypt.checkpw(password.encode("utf-8"), stored.encode("utf-8"))
            return user_id if ok else None

        # backward compatible: якщо в БД старий plaintext
        if stored == password:
            # апгрейд до bcrypt
            new_hash = _hash_password(password)
            cur.execute(
                "UPDATE users SET password = %s WHERE id = %s",
                (new_hash, user_id)
            )
            conn.commit()
            return user_id

        return None

    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Помилка входу:", e)
        return None

    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        conn.close()


# Зміна пароля
def change_password(user_id):
    new_password = input("Новий пароль: ").strip()

    if len(new_password) < 4:
        print("Пароль має бути мінімум 4 символи.")
        return

    conn = connect()
    if not conn:
        print("Проблема з базою")
        return

    cur = None
    try:
        cur = conn.cursor()
        pwd_hash = _hash_password(new_password)

        cur.execute(
            "UPDATE users SET password = %s WHERE id = %s",
            (pwd_hash, user_id)
        )

        if cur.rowcount == 0:
            conn.rollback()
            print("Користувача не знайдено.")
            return

        conn.commit()
        print("Пароль успішно змінено!")

    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Помилка зміни пароля:", e)

    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        conn.close()


# Зміна дати народження
def change_birth_date(user_id):
    new_date = input("Нова дата народження (YYYY-MM-DD): ").strip()

    try:
        datetime.strptime(new_date, "%Y-%m-%d")
    except ValueError:
        print("Дата має бути у форматі YYYY-MM-DD.")
        return

    conn = connect()
    if not conn:
        print("Проблема з базою")
        return

    cur = None
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET birth_date = %s WHERE id = %s",
            (new_date, user_id)
        )

        if cur.rowcount == 0:
            conn.rollback()
            print("Користувача не знайдено.")
            return

        conn.commit()
        print("Дату народження успішно змінено!")

    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Помилка зміни дати:", e)

    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        conn.close()