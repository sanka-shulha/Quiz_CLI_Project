from auth import register, login, change_password, change_birth_date
from quiz import start_quiz, start_mixed_quiz
from reports import my_results, top_20, export_my_results_csv
from admin import is_admin, admin_menu


користувач = None
user_id = None


def menu_logged_in(is_admin_user: bool):
    print(f"\nПривіт, {користувач}!")
    print("1 - Почати вікторину (за категорією)")
    print("2 - Мої результати")
    print("3 - Топ-20 (за категорією)")
    print("4 - Змінити пароль")
    print("5 - Змінити дату народження")
    print("6 - Експорт моїх результатів (CSV)")
    print("7 - Змішана вікторина (20 питань з різних категорій) [BONUS]")
    if is_admin_user:
        print("8 - Адмін-панель (категорії) [BONUS]")
    print("0 - Вихід")


def menu_guest():
    print("\n1 - Реєстрація")
    print("2 - Вхід")
    print("0 - Вихід")


while True:
    if користувач:
        admin_flag = is_admin(user_id)

        menu_logged_in(admin_flag)
        вибір = input("Вибір: ").strip()

        if вибір == "1":
            start_quiz(user_id)

        elif вибір == "2":
            my_results(user_id)

        elif вибір == "3":
            top_20()

        elif вибір == "4":
            change_password(user_id)

        elif вибір == "5":
            change_birth_date(user_id)

        elif вибір == "6":
            export_my_results_csv(user_id)

        elif вибір == "7":
            start_mixed_quiz(user_id)

        elif вибір == "8" and admin_flag:
            admin_menu()

        elif вибір == "0":
            користувач = None
            user_id = None
            print("Вийшли з акаунта.")

        else:
            print("Неправильно, спробуй ще")

    else:
        menu_guest()
        вибір = input("Вибір: ").strip()

        if вибір == "1":
            логін = input("Логін: ").strip()
            пароль = input("Пароль: ").strip()
            дата = input("Дата народження (YYYY-MM-DD): ").strip()

            if register(логін, пароль, дата):
                print("Реєстрація успішна!")
            else:
                print("Логін зайнятий або помилка")

        elif вибір == "2":
            логін = input("Логін: ").strip()
            пароль = input("Пароль: ").strip()

            знайдений_id = login(логін, пароль)
            if знайдений_id:
                користувач = логін
                user_id = знайдений_id
                print("Вхід успішний!")
            else:
                print("Неправильно")

        elif вибір == "0":
            print("До побачення!")
            break

        else:
            print("Неправильно")