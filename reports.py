from database import connect
import csv
import os


def my_results(user_id):
    conn = connect()
    if not conn:
        print("Проблема з базою")
        return

    cur = None
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT c.name, r.score, r.total_questions, r.created_at
            FROM results r
            JOIN categories c ON r.category_id = c.id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
        """, (user_id,))

        res = cur.fetchall()

        if not res:
            print("Результатів немає.")
            return

        print("\n--- Мої результати ---")
        for r in res:
            print(f"{r[0]}: {r[1]}/{r[2]} ({r[3]})")

    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Помилка при отриманні результатів:", e)

    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        conn.close()


def top_20():
    conn = connect()
    if not conn:
        print("Проблема з базою")
        return

    cur = None
    try:
        cur = conn.cursor()

        # активні категорії - тільки
        cur.execute("SELECT id, name FROM categories WHERE is_active = TRUE ORDER BY id")
        cats = cur.fetchall()

        if not cats:
            print("Категорій немає.")
            return

        print("\nОберіть категорію для Топ-20 (тільки активні):")
        for c in cats:
            print(f"{c[0]} - {c[1]}")

        choice = input("Номер категорії: ").strip()

        try:
            category_id = int(choice)
        except ValueError:
            print("Потрібно ввести число.")
            return

        if category_id not in {c[0] for c in cats}:
            print("Категорія неактивна або неіснує.")
            return

        cur.execute("""
            SELECT u.login, r.score, r.total_questions, r.created_at
            FROM results r
            JOIN users u ON r.user_id = u.id
            WHERE r.category_id = %s
            ORDER BY r.score DESC, r.created_at ASC
            LIMIT 20
        """, (category_id,))

        top = cur.fetchall()

        if not top:
            print("Результатів для цієї категорії немає.")
            return

        print("\n--- Топ-20 ---")
        for i, t in enumerate(top, 1):
            print(f"{i}. {t[0]} — {t[1]}/{t[2]} ({t[3]})")

    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Помилка при отриманні топу:", e)

    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        conn.close()


def export_my_results_csv(user_id):
    conn = connect()
    if not conn:
        print("Проблема з базою")
        return

    cur = None
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT c.name, r.score, r.total_questions, r.created_at
            FROM results r
            JOIN categories c ON r.category_id = c.id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
        """, (user_id,))

        rows = cur.fetchall()

        if not rows:
            print("Немає результатів для експорту.")
            return

        os.makedirs("export", exist_ok=True)
        filepath = "export/my_results.csv"

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Категорія", "Бали", "Кількість питань", "Дата"])
            writer.writerows(rows)

        print(f"Експортовано у файл: {filepath}")

    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Помилка експорту:", e)

    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        conn.close()


# додала 3-й звіт
def report_questions_in_active_categories():
    conn = connect()
    if not conn:
        print("Проблема з базою")
        return

    cur = None
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT c.name, COUNT(q.id) AS questions_count
            FROM categories c
            LEFT JOIN questions q ON q.category_id = c.id
            WHERE c.is_active = TRUE
            GROUP BY c.id, c.name
            ORDER BY questions_count DESC, c.name ASC
        """)

        rows = cur.fetchall()

        print("\n--- Звіт: кількість питань в активних категоріях ---")
        if not rows:
            print("Немає даних.")
            return

        for name, cnt in rows:
            print(f"{name}: {cnt}")

    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Помилка звіту:", e)

    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        conn.close()