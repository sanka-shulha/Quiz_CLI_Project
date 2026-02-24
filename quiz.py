from database import connect
import random

MAX_Q = 20


def start_quiz(user_id: int):
    """Вікторина по вибраній (активній) категорії."""
    conn = connect()
    if not conn:
        print("Проблема з базою")
        return

    cur = None
    try:
        cur = conn.cursor()

        cur.execute("SELECT id, name FROM categories WHERE is_active = TRUE ORDER BY id")
        categories = cur.fetchall()

        if not categories:
            print("Немає активних категорій.")
            return


        print("\nОбери категорію:")
        for i, (cid, name) in enumerate(categories, start=1):
            print(f"{i} - {name}")
        print("0 - Назад")

        choice = input("Номер категорії: ").strip()
        if choice == "0":
            return

        if not choice.isdigit():
            print("Введи число!")
            return

        idx = int(choice)
        if idx < 1 or idx > len(categories):
            print("Такої активної категорії немає")
            return


        cat_id = categories[idx - 1][0]


        cur.execute(
            "SELECT id FROM categories WHERE id = %s AND is_active = TRUE",
            (cat_id,)
        )
        if not cur.fetchone():
            print("Такої активної категорії немає")
            return


        cur.execute("SELECT COUNT(*) FROM questions WHERE category_id = %s", (cat_id,))
        q_count = cur.fetchone()[0]
        if q_count < MAX_Q:
            print(f"Недостатньо питань у категорії: є {q_count}, потрібно мінімум {MAX_Q}.")
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
        except Exception:
            pass
        print("Помилка:", e)

    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        conn.close()


def start_mixed_quiz(user_id: int):
    """Змішана вікторина — 20 випадкових питань з усіх категорій."""
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

        if len(qs) < MAX_Q:
            print(f"Недостатньо питань у базі: є {len(qs)}, потрібно мінімум {MAX_Q}.")
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
        except Exception:
            pass
        print("Помилка:", e)

    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        conn.close()


def ask_answer() -> str:
    """Валідація відповіді: тільки a/b/c/d."""
    while True:
        ans = input("Відповідь (a/b/c/d): ").strip().lower()
        if ans in ("a", "b", "c", "d"):
            return ans
        print("Введи тільки a, b, c або d.")


def run_questions(qs) -> int:
    """Показує питання і повертає кількість правильних відповідей."""
    score = 0
    total = len(qs)

    for i, q in enumerate(qs, 1):
        text, a, b, c, d, correct = q

        print(f"\nПитання {i}/{total}: {text}")
        print(f"a) {a}")
        print(f"b) {b}")
        print(f"c) {c}")
        print(f"d) {d}")

        ans = ask_answer()

        if ans == correct:
            score += 1
            print("Правильно!")
        else:
            print(f"Ні, правильна: {correct}")

    print(f"\nТи набрав {score} з {total}")
    return score