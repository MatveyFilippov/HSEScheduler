import sqlite3
import backend
import hashlib


class Keys:
    email = "email"
    username = "username"
    encrypted_password = "encrypted_password"


class User:
    def __init__(self, email: str):
        if not is_email_exists(email):
            raise KeyError(f"No User with '{Keys.email}': '{email}'")
        self.email = email
        self.encrypted_password = get_value_from_db_by_email(email=email, key=Keys.encrypted_password)
        self.username = get_value_from_db_by_email(email=email, key=Keys.username)

    def is_password_right(self, password: str, is_input_encrypted=False) -> bool:
        if not is_input_encrypted:
            password = get_encrypt_string(password)
        return self.encrypted_password == password

    def change_password(self, new_password: str, is_input_encrypted=False) -> str:
        if not is_input_encrypted:
            new_password = get_encrypt_string(new_password)

        connection = sqlite3.connect(backend.PATH_TO_DBFILE)
        cursor = connection.cursor()
        cursor.execute(
            f'UPDATE Users SET {Keys.encrypted_password} = ? WHERE {Keys.email} = ?', (new_password, self.email)
        )
        connection.commit()
        connection.close()

        self.encrypted_password = new_password
        return new_password


init_connection = sqlite3.connect(backend.PATH_TO_DBFILE)
init_cursor = init_connection.cursor()
init_cursor.execute(f'''CREATE TABLE IF NOT EXISTS Users (
{Keys.email} TEXT PRIMARY KEY,
{Keys.encrypted_password} TEXT NOT NULL,
{Keys.username} TEXT
)''')
init_cursor.execute(
    f'CREATE INDEX IF NOT EXISTS idx_email ON Users ({Keys.email})'
)
init_connection.commit()
init_connection.close()


def get_encrypt_string(input_string: str) -> str:
    return hashlib.sha256(input_string.encode()).hexdigest()


def create_new_user(email: str, encrypted_password: str, username: str) -> User:
    connection = sqlite3.connect(backend.PATH_TO_DBFILE)
    cursor = connection.cursor()
    try:
        cursor.execute(
            f'INSERT INTO Users ({Keys.email}, {Keys.encrypted_password}, {Keys.username}) VALUES (?, ?, ?)',
            (email, encrypted_password, username,)
        )
    except sqlite3.IntegrityError as ex:
        raise KeyError(ex)
    connection.commit()
    connection.close()
    return User(email)


def is_email_exists(email: str) -> bool:
    connection = sqlite3.connect(backend.PATH_TO_DBFILE)
    cursor = connection.cursor()
    cursor.execute(
        f'SELECT COUNT(*) FROM Users WHERE {Keys.email} = ?', (email,)
    )
    result = cursor.fetchone()[0]
    connection.close()
    return result == 1


def get_value_from_db_by_email(email: str, key: str):
    connection = sqlite3.connect(backend.PATH_TO_DBFILE)
    cursor = connection.cursor()
    cursor.execute(
        f'SELECT {key} FROM Users WHERE {Keys.email} = ?', (email,)
    )
    result = cursor.fetchone()[0]
    connection.close()
    return result
