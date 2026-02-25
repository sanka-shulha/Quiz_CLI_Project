import os
import psycopg2
from psycopg2 import errors
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


def connect():
    try:
        os.environ["PGCLIENTENCODING"] = "UTF8"
        return psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            options="-c lc_messages=C"
        )
    except Exception as e:
        print(f"Помилка підключення: {e}")
        return None


def list_categories():
    conn = connect()
    if not conn:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, is_active
                FROM categories
                ORDER BY id;
            """)
            return cur.fetchall()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Помилка читання категорій.")
        return []
    finally:
        conn.close()


def add_category(name):
    conn = connect()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO categories (name) VALUES (%s) RETURNING id;",
                (name,)
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id

    except errors.UniqueViolation:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Категорія з такою назвою вже існує.")
        return None

    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Не вдалося додати категорію.")
        return None

    finally:
        conn.close()


def update_category(category_id, new_name, is_active):
    conn = connect()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE categories
                SET name=%s, is_active=%s
                WHERE id=%s;
            """, (new_name, is_active, category_id))

            if cur.rowcount == 0:
                conn.rollback()
                print("Такої категорії немає.")
                return False

        conn.commit()
        return True

    except errors.UniqueViolation:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Категорія з такою назвою вже існує.")
        return False

    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Не вдалося оновити категорію.")
        return False

    finally:
        conn.close()


def delete_category(category_id):
    """
    SAFE DELETE: замість реального DELETE робимо деактивацію,
    щоб не стерти questions/results каскадом.
    """
    conn = connect()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE categories SET is_active = FALSE WHERE id=%s;",
                (category_id,)
            )

            if cur.rowcount == 0:
                conn.rollback()
                print("Такої категорії немає.")
                return False

        conn.commit()
        return True

    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Не вдалося деактивувати категорію.")
        return False

    finally:
        conn.close()


def list_questions_by_category(category_id):
    conn = connect()
    if not conn:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, text, correct_option
                FROM questions
                WHERE category_id=%s
                ORDER BY id;
            """, (category_id,))
            return cur.fetchall()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Помилка читання питань.")
        return []
    finally:
        conn.close()


def get_question_by_id(question_id):
    conn = connect()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, category_id, text,
                       option_a, option_b, option_c, option_d,
                       correct_option
                FROM questions
                WHERE id=%s;
            """, (question_id,))
            return cur.fetchone()
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Помилка читання питання.")
        return None
    finally:
        conn.close()


def add_question(category_id, text, a, b, c, d, correct):
    conn = connect()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO questions
                (category_id, text, option_a, option_b, option_c, option_d, correct_option)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                RETURNING id;
            """, (category_id, text, a, b, c, d, correct))
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id

    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Не вдалося додати питання.")
        return None

    finally:
        conn.close()


def update_question(question_id, text, a, b, c, d, correct):
    conn = connect()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE questions
                SET text=%s,
                    option_a=%s,
                    option_b=%s,
                    option_c=%s,
                    option_d=%s,
                    correct_option=%s
                WHERE id=%s;
            """, (text, a, b, c, d, correct, question_id))

            if cur.rowcount == 0:
                conn.rollback()
                print("Такого питання немає.")
                return False

        conn.commit()
        return True

    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Не вдалося оновити питання.")
        return False

    finally:
        conn.close()


def delete_question(question_id):
    conn = connect()
    if not conn:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM questions WHERE id=%s;",
                (question_id,)
            )

            if cur.rowcount == 0:
                conn.rollback()
                print("Такого питання немає.")
                return False

        conn.commit()
        return True

    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        print("Не вдалося видалити питання.")
        return False

    finally:
        conn.close()