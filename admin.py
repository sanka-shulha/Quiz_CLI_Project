from database import (
    connect,
    list_categories,
    add_category as db_add_category,
    update_category,
    delete_category,
    list_questions_by_category,
    get_question_by_id,
    add_question as db_add_question,
    update_question,
    delete_question
)


def is_admin(user_id: int) -> bool:
    conn = connect()
    if not conn:
        return False
    cur = None
    try:
        cur = conn.cursor()
        cur.execute("SELECT is_admin FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        return bool(row and row[0] is True)
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        return False
    finally:
        try:
            if cur:
                cur.close()
        except Exception:
            pass
        conn.close()


def admin_menu():
    while True:
        print("\n=== Адмін-панель ===")
        print("1 - Категорії (CRUD)")
        print("2 - Питання (CRUD)")
        print("0 - Назад")

        choice = input("Вибір: ").strip()

        if choice == "1":
            categories_menu()
        elif choice == "2":
            questions_menu()
        elif choice == "0":
            return
        else:
            print("Неправильно, спробуй ще.")


def categories_menu():
    while True:
        print("\n--- Категорії ---")
        print("1 - Список")
        print("2 - Додати")
        print("3 - Оновити")
        print("4 - Видалити")
        print("0 - Назад")

        choice = input("Вибір: ").strip()

        if choice == "1":
            show_categories()
        elif choice == "2":
            add_category()
        elif choice == "3":
            edit_category()
        elif choice == "4":
            remove_category()
        elif choice == "0":
            return
        else:
            print("Неправильно, спробуй ще.")


def show_categories():
    rows = list_categories()
    if not rows:
        print("Категорій немає.")
        return

    print("\nID | Назва | Статус")
    for cid, name, active in rows:
        status = "ACTIVE" if active else "OFF"
        print(f"{cid} - {name} [{status}]")


def add_category():
    name = input("Назва нової категорії: ").strip()
    if not name:
        print("Назва не може бути порожньою.")
        return

    new_id = db_add_category(name)
    if new_id:
        print("Готово.")
    else:
        print("Не вдалося додати категорію.")


def edit_category():
    show_categories()
    raw = input("ID категорії для оновлення (0 - назад): ").strip()
    if raw == "0":
        return
    if not raw.isdigit():
        print("Потрібно ввести число.")
        return

    cat_id = int(raw)

    rows = list_categories()
    current = next((r for r in rows if r[0] == cat_id), None)
    if not current:
        print("Такої категорії немає.")
        return

    current_name, current_active = current[1], current[2]

    new_name = input("Нова назва (Enter - залишити без змін): ").strip()
    active_input = input("Активна? (y/n, Enter - залишити як є): ").strip().lower()

    if not new_name:
        new_name = current_name

    if active_input == "":
        is_active = current_active
    else:
        is_active = True if active_input in ("y", "yes", "1", "так", "t") else False

    ok = update_category(cat_id, new_name, is_active)
    if ok:
        print("Категорію оновлено.")
    else:
        print("Не вдалося оновити категорію.")


def remove_category():
    show_categories()
    raw = input("ID категорії для видалення (0 - назад): ").strip()
    if raw == "0":
        return
    if not raw.isdigit():
        print("Потрібно ввести число.")
        return

    cat_id = int(raw)

    confirm = input("Підтвердити видалення (деактивацію) категорії? (y/n): ").strip().lower()
    if confirm not in ("y", "yes", "1", "так", "t"):
        print("Скасовано.")
        return

    ok = delete_category(cat_id)  # safe-delete (is_active = FALSE)
    if ok:
        print("Категорію видалено.")
    else:
        print("Не вдалося видалити категорію.")


def questions_menu():
    while True:
        print("\n--- Питання ---")
        print("1 - Список по категорії")
        print("2 - Додати")
        print("3 - Оновити")
        print("4 - Видалити")
        print("0 - Назад")

        choice = input("Вибір: ").strip()

        if choice == "1":
            show_questions()
        elif choice == "2":
            add_question()
        elif choice == "3":
            edit_question()
        elif choice == "4":
            remove_question()
        elif choice == "0":
            return
        else:
            print("Неправильно, спробуй ще.")


def show_questions():
    show_categories()
    raw = input("ID категорії (0 - назад): ").strip()
    if raw == "0":
        return
    if not raw.isdigit():
        print("Потрібно ввести число.")
        return

    cat_id = int(raw)
    rows = list_questions_by_category(cat_id)

    if not rows:
        print("Питань немає.")
        return

    print("\nID | Текст | Правильна")
    for qid, text, correct in rows:
        short_text = text if len(text) <= 80 else text[:77] + "..."
        print(f"{qid} - {short_text} (правильна: {correct})")


def _ask_correct_letter(prompt="Правильна (a/b/c/d): "):
    while True:
        ans = input(prompt).strip().lower()
        if ans in ("a", "b", "c", "d"):
            return ans
        print("Введи тільки: a, b, c або d.")


def add_question():
    show_categories()
    raw = input("ID категорії (0 - назад): ").strip()
    if raw == "0":
        return
    if not raw.isdigit():
        print("Потрібно ввести число.")
        return

    category_id = int(raw)

    text = input("Текст питання: ").strip()
    a = input("Варіант A: ").strip()
    b = input("Варіант B: ").strip()
    c = input("Варіант C: ").strip()
    d = input("Варіант D: ").strip()

    if not all([text, a, b, c, d]):
        print("Усі поля мають бути заповнені.")
        return

    correct = _ask_correct_letter()

    new_id = db_add_question(category_id, text, a, b, c, d, correct)
    if new_id:
        print("Питання додано.")
    else:
        print("Не вдалося додати питання.")


def edit_question():
    show_questions()
    raw = input("ID питання для оновлення (0 - назад): ").strip()
    if raw == "0":
        return
    if not raw.isdigit():
        print("Потрібно ввести число.")
        return

    question_id = int(raw)
    q = get_question_by_id(question_id)
    if not q:
        print("Такого питання немає.")
        return

    _, category_id, old_text, old_a, old_b, old_c, old_d, old_correct = q

    print("\nEnter = залишити як є")
    text = input(f"Текст [{old_text}]: ").strip() or old_text
    a = input(f"A [{old_a}]: ").strip() or old_a
    b = input(f"B [{old_b}]: ").strip() or old_b
    c = input(f"C [{old_c}]: ").strip() or old_c
    d = input(f"D [{old_d}]: ").strip() or old_d

    correct_in = input(f"Правильна [{old_correct}] (a/b/c/d або Enter): ").strip().lower()
    correct = old_correct if correct_in == "" else correct_in
    if correct not in ("a", "b", "c", "d"):
        print("Неправильна відповідь.")
        return

    ok = update_question(question_id, text, a, b, c, d, correct)
    if ok:
        print("Питання оновлено.")
    else:
        print("Не вдалося оновити питання.")


def remove_question():
    show_questions()
    raw = input("ID питання для видалення (0 - назад): ").strip()
    if raw == "0":
        return
    if not raw.isdigit():
        print("Потрібно ввести число.")
        return

    ok = delete_question(int(raw))
    if ok:
        print("Питання видалено.")
    else:
        print("Не вдалося видалити питання.")