from database import connect
from datetime import datetime


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

    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (login, password, birth_date) VALUES (%s, %s, %s)",
            (login, password, birth_date)
        )
        conn.commit()
        print("Реєстрація успішна!")
        return True

    except Exception as e:
        conn.rollback()
        print("Помилка реєстрації:", e)
        return False

    finally:
        try:
            cur.close()
        except:
            pass
        conn.close()

# Вхід

def login(login, password):
    conn = connect()
    if not conn:
        print("Проблема з базою")
        return None

    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM users WHERE login = %s AND password = %s",
            (login, password)
        )
        user = cur.fetchone()
        return user[0] if user else None

    except Exception as e:
        print("Помилка входу:", e)
        return None

    finally:
        try:
            cur.close()
        except:
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

    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET password = %s WHERE id = %s",
            (new_password, user_id)
        )
        conn.commit()
        print("Пароль успішно змінено!")

    except Exception as e:
        print("Помилка зміни пароля:", e)

    finally:
        try:
            cur.close()
        except:
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

    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET birth_date = %s WHERE id = %s",
            (new_date, user_id)
        )
        conn.commit()
        print("Дату народження успішно змінено!")

    except Exception as e:
        print("Помилка зміни дати:", e)

    finally:
        try:
            cur.close()
        except:
            pass
        conn.close()