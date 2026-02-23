from database import connect


def is_admin(user_id: int) -> bool:
    conn = connect()
    if not conn:
        print("Проблема з базою")
        return False
    try:
        cur = conn.cursor()
        cur.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        return bool(row and row[0] is True)
    except Exception as e:
        print("Помилка перевірки адміна:", e)
        return False
    finally:
        try:
            cur.close()
        except:
            pass
        conn.close()


def admin_menu():
    while True:
        print("\n=== Адмін-панель ===")
        print("1 - Список категорій")
        print("2 - Додати категорію")
        print("3 - Увімкнути/вимкнути категорію (is_active)")
        print("0 - Назад")

        choice = input("Вибір: ").strip()

        if choice == "1":
            list_categories(include_inactive=True)
        elif choice == "2":
            add_category()
        elif choice == "3":
            toggle_category_active()
        elif choice == "0":
            return
        else:
            print("Неправильно, спробуй ще")


def list_categories(include_inactive: bool = True):
    conn = connect()
    if not conn:
        print("Проблема з базою")
        return
    try:
        cur = conn.cursor()

        if include_inactive:
            cur.execute("SELECT id, name, is_active FROM categories ORDER BY id")
        else:
            cur.execute("SELECT id, name, is_active FROM categories WHERE is_active = TRUE ORDER BY id")

        rows = cur.fetchall()
        if not rows:
            print("Категорій немає.")
            return

        print("\n--- Категорії ---")
        for cid, name, active in rows:
            status = "ACTIVE" if active else "OFF"
            print(f"{cid} - {name} [{status}]")

    except Exception as e:
        print("Помилка:", e)
    finally:
        try:
            cur.close()
        except:
            pass
        conn.close()


def add_category():
    name = input("Назва нової категорії: ").strip()
    if not name:
        print("Назва не може бути порожньою.")
        return

    conn = connect()
    if not conn:
        print("Проблема з базою")
        return

    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO categories (name, is_active) VALUES (%s, TRUE) ON CONFLICT (name) DO NOTHING",
            (name,)
        )
        conn.commit()

        if cur.rowcount == 0:
            print("Така категорія вже існує.")
        else:
            print("Категорію додано!")

    except Exception as e:
        conn.rollback()
        print("Помилка:", e)
    finally:
        try:
            cur.close()
        except:
            pass
        conn.close()


def toggle_category_active():
    list_categories(include_inactive=True)
    raw = input("Введи ID категорії (0 - назад): ").strip()
    if raw == "0":
        return
    try:
        cat_id = int(raw)
    except ValueError:
        print("Потрібно ввести число.")
        return

    conn = connect()
    if not conn:
        print("Проблема з базою")
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT is_active, name FROM categories WHERE id = %s", (cat_id,))
        row = cur.fetchone()
        if not row:
            print("Такої категорії немає.")
            return

        current_active, name = row[0], row[1]
        new_active = not current_active

        cur.execute("UPDATE categories SET is_active = %s WHERE id = %s", (new_active, cat_id))
        conn.commit()

        status = "ACTIVE" if new_active else "OFF"
        print(f"Готово: '{name}' тепер [{status}]")

    except Exception as e:
        conn.rollback()
        print("Помилка:", e)
    finally:
        try:
            cur.close()
        except:
            pass
        conn.close()