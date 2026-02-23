from database import connect
import random

MAX_Q = 20


def start_quiz(user_id: int):
    """Звичайна вікторина: користувач обирає категорію (лише активні)."""
    conn = connect()
    if not conn:
        print("Проблема з базою")
        return

    cur = None
    try:
        cur = conn.cursor()

        # активні категорії тільки
        cur.execute("SELECT id, name FROM categories WHERE is_active = TRUE ORDER BY id")
        categories = cur.fetchall()

        if not categories:
            print("Немає активних категорій.")
            return

        print("\nОбери категорію:")
        for cid, name in categories:
            print(f"{cid} - {name}")
        print("0 - Назад")

        choice = input("Номер категорії: ").strip()
        if choice == "0":
            return

        try:
            cat_id = int(choice)
        except ValueError:
            print("Введи число!")
            return


        cur.execute("SELECT id FROM categories WHERE id = %s AND is_active = TRUE", (cat_id,))
        if not cur.fetchone():
            print("Такої активної категорії немає")
            return


        cur.execute(
            """
            SELECT text, option_a, option_b, option_c, option_d, correct_option
            FROM questions
            WHERE category_id = %s
            """,
            (cat_id,)
        )
        qs = cur.fetchall()

        if not qs:
            print("Питань у цій категорії немає")
            return

        random.shuffle(qs)
        qs = qs[:MAX_Q]

        score = run_questions(qs)


        cur.execute(
            """
            INSERT INTO results (user_id, category_id, score, total_questions)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, cat_id, score, len(qs))
        )
        conn.commit()
        print("Результат збережено!")

    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        print("Помилка:", e)

    finally:
        try:
            if cur:
                cur.close()
        except:
            pass
        conn.close()


def start_mixed_quiz(user_id: int):
    """БОНУС: змішана вікторина — 20 випадкових питань з усіх категорій."""
    conn = connect()
    if not conn:
        print("Проблема з базою")
        return

    cur = None
    try:
        cur = conn.cursor()


        cur.execute(
            """
            SELECT text, option_a, option_b, option_c, option_d, correct_option
            FROM questions
            """
        )
        qs = cur.fetchall()

        if not qs:
            print("Питань у базі немає.")
            return

        random.shuffle(qs)
        qs = qs[:MAX_Q]

        print("\n=== Змішана вікторина (20 питань) ===")
        score = run_questions(qs)


        cur.execute("SELECT id FROM categories WHERE name = %s", ("Змішана вікторина",))
        row = cur.fetchone()

        if row:
            mixed_cat_id = row[0]
        else:
            cur.execute(
                "INSERT INTO categories (name, is_active) VALUES (%s, TRUE) RETURNING id",
                ("Змішана вікторина",)
            )
            mixed_cat_id = cur.fetchone()[0]
            conn.commit()


        cur.execute(
            """
            INSERT INTO results (user_id, category_id, score, total_questions)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, mixed_cat_id, score, len(qs))
        )
        conn.commit()
        print("Результат збережено!")

    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        print("Помилка:", e)

    finally:
        try:
            if cur:
                cur.close()
        except:
            pass
        conn.close()


def run_questions(qs):
    """Показує питання і повертає кількість правильних відповідей."""
    score = 0
    total = len(qs)

    for i, q in enumerate(qs, 1):
        print(f"\nПитання {i}/{total}: {q[0]}")
        print(f"a) {q[1]}")
        print(f"b) {q[2]}")
        print(f"c) {q[3]}")
        print(f"d) {q[4]}")

        ans = input("Відповідь (a/b/c/d): ").strip().lower()

        if ans == q[5]:
            score += 1
            print("Правильно!")
        else:
            print(f"Ні, правильна: {q[5]}")

    print(f"\nТи набрав {score} з {total}")
    return score