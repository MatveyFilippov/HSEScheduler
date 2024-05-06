import smtplib
import backend
from email.message import EmailMessage
import random
import string
import re
import logging


LOGGER = logging.getLogger(f'{backend.LOGGER_NAME}.EmailPackage')


try:
    temp_email_connection = smtplib.SMTP(backend.EMAIL_HOST, backend.EMAIL_PORT)
    temp_email_connection.starttls()
    temp_email_connection.login(backend.EMAIL_LOGIN, backend.EMAIL_PASSWORD)
    temp_email_connection.quit()
except Exception as ex:
    LOGGER.exception(ex)
    raise ConnectionError("Failed connect with Mail: %s" % ex)

EMAIL_PATTERN = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'


class EmailMsg:
    def __init__(self, email_to: str, title: str, body: str):
        if not re.match(EMAIL_PATTERN, email_to):
            raise ValueError(f"'email_to': '{email_to}' is not looks like email address")

        try:
            self.email_connection = smtplib.SMTP(backend.EMAIL_HOST, backend.EMAIL_PORT)
            self.email_connection.starttls()
            self.email_connection.login(backend.EMAIL_LOGIN, backend.EMAIL_PASSWORD)
        except Exception as e:
            raise ConnectionError("Failed connect with Mail: %s" % e)

        self.message = EmailMessage()
        self.message["From"] = backend.EMAIL_LOGIN
        self.message["To"] = email_to
        self.message["Subject"] = title
        self.message.set_content(body)

    def __del__(self):
        try:
            self.email_connection.quit()
        except Exception as e:
            LOGGER.exception(e)

    def send(self):
        self.email_connection.sendmail(
            from_addr=self.message.get("From"),
            to_addrs=self.message.get("To"),
            msg=self.message.as_string()
        )

    @property
    def title(self) -> str:
        return self.message.get("Subject")

    @property
    def to_addr(self) -> str:
        return self.message.get("To")

    @property
    def from_addr(self) -> str:
        return self.message.get("From")

    @property
    def body(self) -> str:
        return self.message.get_content()


def __generate_random_code(length=6) -> str:
    characters = string.ascii_letters + string.digits  # Используем буквы и цифры для кода
    code = ''.join(random.choice(characters) for _ in range(length))
    return code


def send_checking_code_while_registration(email_to: str) -> str:
    code = __generate_random_code()

    title = "Код проверки для подтверждения регистрации в HSE Scheduler"
    body = f"Для завершения регистрации в нашем сервисе, пожалуйста, используйте следующий код для проверки:\n\n{code}\n\nС уважением, HSE Scheduler"

    msg = EmailMsg(email_to=email_to, title=title, body=body)
    msg.send()

    return code


def send_checking_code_while_reset_password(email_to: str) -> str:
    code = __generate_random_code()

    title = "Код восстановления пароля для HSE Scheduler"
    body = f"Для восстановления пароля к вашей учетной записи в HSE Scheduler, используйте следующий код для подтверждения:\n\n{code}\n\nЕсли Вы не запрашивали восстановление пароля, проигнорируйте это сообщение.\nС уважением, HSE Scheduler"

    msg = EmailMsg(email_to=email_to, title=title, body=body)
    msg.send()

    return code
