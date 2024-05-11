from datetime import datetime
from flask import Flask, render_template, request, make_response
import backend
from backend import scheduler_database, scheduler_email


app = Flask(
    __name__,
    static_folder=backend.STATIC_FOLDER_PATH,
    template_folder=backend.TEMPLATES_FOLDER_PATH,
)


all_users: dict[str, scheduler_database.User] = {}
user_while_registration: dict[str, dict[str, str]] = {}
user_while_password_changing: dict[str, str] = {}


@app.route('/', methods=['POST', 'GET'])
def welcome():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            user = scheduler_database.User(email)
            if not user.is_password_right(password):
                raise KeyError("Incorrect password")
            all_users[email] = user

            response = make_response(render_template('calendar.html', events=all_users[email].events))
            response.set_cookie('email', email)
            return response
        except KeyError:
            message = "Неверный логин или пароль"
            return render_template('index.html', message=message)
    else:
        response = make_response(render_template('index.html'))
        response.delete_cookie('email')
        return response


@app.route('/forgotten_password', methods=['POST', 'GET'])
def forgotten_password():
    if request.method == 'POST':
        email = request.form.get('email')
        if not scheduler_database.is_email_exists(email):
            message = "К этой почте не привязан ни один аккаунт"
            return render_template('forgottenPassword.html', message=message)

        try:
            secret_email_code = scheduler_email.send_checking_code_while_reset_password(email)
        except ValueError:
            return render_template('forgottenPassword.html', message="Проверьте корректность почты")

        user_while_password_changing[email] = secret_email_code

        response = make_response(render_template('codeForPasswordChanging.html'))
        response.set_cookie('email', email)
        return response
    else:
        response = make_response(render_template('forgottenPassword.html'))
        response.delete_cookie('email')
        return response


@app.route('/changing_password_code', methods=['POST', 'GET'])
def changing_password_code():
    if request.method == 'POST':
        email = request.cookies.get("email")
        if email not in user_while_password_changing:
            response = make_response(
                render_template('forgottenPassword.html', message="Ошибка системы, попробуйте ещё раз")
            )
            response.delete_cookie('email')
            return response
        input_code = request.form.get('email_code')
        right_code = user_while_password_changing[email]
        if input_code != right_code:
            return render_template(
                'codeForPasswordChanging.html', message=f"Код проверки для почты '{email}' не верный"
            )
        del user_while_password_changing[email]
        return render_template('newPassword.html')
    else:
        return render_template('codeForPasswordChanging.html')


@app.route('/new_password', methods=['POST', 'GET'])
def new_password():
    if request.method == 'POST':
        email = request.cookies.get("email")
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if not password1 or not password2:
            return render_template('newPassword.html', message="Заполните все поля")
        if password1 != password2:
            return render_template('newPassword.html', message="Пароли не совпадают")
        try:
            user = scheduler_database.User(email)
            user.change_password(new_password=password1)
            all_users[email] = user
        except KeyError:
            response = make_response(
                render_template('forgottenPassword.html', message="Ошибка системы, попробуйте ещё раз")
            )
            response.delete_cookie('email')
            return response
        return render_template('calendar.html', events=all_users[email].events)
    else:
        return render_template('newPassword.html')


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if not username or not email or not password1 or not password2:
            return render_template('registration.html', message="Заполните все поля")

        error_msg = None
        if scheduler_database.is_email_exists(email):
            error_msg = "Пользователь с такой почтой уже существует"
        if password1 != password2:
            error_msg = "Пароли не совпадают"
        if len(password1) < 8:
            error_msg = "Пароль должен быть длиннее 8 символов"
        if password1.count(" "):
            error_msg = "Пароль не может содержать пробелов"
        if error_msg:
            return render_template('registration.html', message=error_msg)

        try:
            secret_email_code = scheduler_email.send_checking_code_while_registration(email)
        except ValueError:
            return render_template('registration.html', message="Проверьте корректность почты")

        user_while_registration[email] = {
            'encrypted_password': scheduler_database.get_encrypt_string(password1),
            'username': username,
            'email_code': secret_email_code,
        }

        response = make_response(render_template('codeForRegistration.html'))
        response.set_cookie('email', email)
        return response
    else:
        return render_template('registration.html')


@app.route('/registration_code', methods=['POST', 'GET'])
def registration_code():
    if request.method == 'POST':
        email = request.cookies.get("email")
        if email not in user_while_registration:
            response = make_response(
                render_template('registration.html', message="Ошибка системы, попробуйте ещё раз")
            )
            response.delete_cookie('email')
            return response
        input_code = request.form.get('email_code')
        right_code = user_while_registration[email]['email_code']
        if input_code != right_code:
            return render_template(
                'codeForRegistration.html', message=f"Код проверки для почты '{email}' не верный"
            )
        try:
            all_users[email] = scheduler_database.create_new_user(
                email=email,
                encrypted_password=user_while_registration[email]['encrypted_password'],
                username=user_while_registration[email]['username'],
            )
        except KeyError:
            response = make_response(
                render_template('registration.html', message="Ошибка системы, попробуйте ещё раз")
            )
            response.delete_cookie('email')
            return response

        del user_while_registration[email]

        return render_template('calendar.html', events=all_users[email].events)
    else:
        return render_template('codeForRegistration.html')


@app.route('/calendar', methods=['POST', 'GET'])
def calendar():
    email = request.cookies.get("email")
    if email not in all_users:
        response = make_response(render_template('index.html'))
        response.delete_cookie('email')
        return response
    return render_template('calendar.html', events=all_users[email].events)


def get_date_for_event(date_str: str) -> str | None:
    datetime_list = date_str.strip().split(" ")
    try:
        datetime.strptime(datetime_list[0], '%Y-%m-%d')
        if len(datetime_list) > 1:
            datetime.strptime(datetime_list[1], '%H:%M')
            return datetime_list[0] + " " + datetime_list[1]
        else:
            return datetime_list[0]
    except ValueError:
        return None


@app.route('/add_new_event', methods=['GET', "POST"])
def add_new_event():
    email = request.cookies.get("email")
    if email not in all_users:
        response = make_response(render_template('index.html'))
        response.delete_cookie('email')
        return response
    if request.method == "POST":
        err_msg = None
        title = request.form.get('title')
        if title == '':
            err_msg = "Вы забыли вписать название задачи"
        description = request.form.get('description')
        color = request.form.get('color')
        if color == '':
            err_msg = "Заполните поле 'цвет'"
        file = request.form.get('file')  # TODO: бесполезный файл
        start = request.form.get('start')
        if start == '':  # TODO: много траблов с временем
            err_msg = "Заполните поле 'Дата и время начала'"
        start = get_date_for_event(start)
        if not start:
            err_msg = "Заполните дату 'начала' по формату 'гггг-мм-дд чч:мм'"
        end = request.form.get('end')
        url = request.form.get('url')  # TODO: бесполезный ссылка
        if end == '':
            end = start
        else:
            end = get_date_for_event(end)
            if not end:
                err_msg = "Заполните дату 'окончания' по формату 'гггг-мм-дд чч:мм'"
        if err_msg:
            return render_template("newEvent.html", message=err_msg)

        all_users[email].new_event(
            title=title,
            description=description,
            color=color,
            file=file,
            start=start,
            end=end,
            url=url,
        )
        return render_template('calendar.html', events=all_users[email].events)
    else:
        return render_template("newEvent.html")


@app.route('/event/<event_id>', methods=['GET', "POST"])
def event(event_id):
    email = request.cookies.get("email")
    if email not in all_users:
        response = make_response(render_template('index.html'))
        response.delete_cookie('email')
        return response
    if request.method == "POST":
        err_msg = None
        title = request.form.get('title')
        if title == '':
            err_msg = "Вы забыли вписать название задачи"
        description = request.form.get('description')
        color = request.form.get('color')
        if color == '':
            err_msg = "Заполните поле 'цвет'"
        file = request.form.get('file')  # TODO: бесполезный файл
        start = request.form.get('start')
        if start == '':  # TODO: много траблов с временем
            err_msg = "Заполните поле 'Дата и время начала'"
        start = get_date_for_event(start)
        if not start:
            err_msg = "Заполните дату 'начала' по формату 'гггг-мм-дд чч:мм'"
        end = request.form.get('end')
        url = request.form.get('url')  # TODO: бесполезный ссылка
        if end == '':
            end = start
        else:
            end = get_date_for_event(end)
            if not end:
                err_msg = "Заполните дату 'окончания' по формату 'гггг-мм-дд чч:мм'"
        if err_msg:
            return render_template("newEvent.html", message=err_msg)

        all_users[email].update_event(
            event_id=event_id,
            title=title,
            description=description,
            color=color,
            file=file,
            start=start,
            end=end,
            url=url,
        )
        return render_template('calendar.html', events=all_users[email].events)
    else:
        return render_template(
            "eventDescription.html", event_id=event_id,
            event=all_users[email].user_events.get_all_event(event_id)
        )


@app.route('/del_event/<event_id>')
def del_event(event_id):
    email = request.cookies.get("email")
    if email not in all_users:
        response = make_response(render_template('index.html'))
        response.delete_cookie('email')
        return response
    all_users[email].del_event(event_id)
    return render_template('calendar.html', events=all_users[email].events)


@app.route('/account')
def account():
    email = request.cookies.get("email")
    if email not in all_users:
        response = make_response(render_template('index.html'))
        response.delete_cookie('email')
        return response
    return render_template('account.html', username=all_users[email].username)


@app.route('/rewrite_password', methods=['GET', "POST"])
def rewrite_password():
    email = request.cookies.get("email")
    if email not in all_users:
        response = make_response(render_template('index.html'))
        response.delete_cookie('email')
        return response
    if request.method == "POST":
        old_password = request.form.get('old_password')
        new_password1 = request.form.get('new_password1')
        new_password2 = request.form.get('new_password2')
        error_msg = None
        if new_password1 != new_password2:
            error_msg = "Новые пароли не совпадают"
        if len(new_password1) < 8:
            error_msg = "Новый пароль должен быть длиннее 8 символов"
        if new_password1.count(" "):
            error_msg = "Новый пароль не может содержать пробелов"
        if not all_users[email].is_password_right(old_password):
            error_msg = "Старый пароль введён неверно"
        if error_msg:
            return render_template('changePassword.html', message=error_msg)
        all_users[email].change_password(new_password1)
        return render_template('calendar.html', events=all_users[email].events)
    else:
        return render_template('changePassword.html')


@app.route('/logout')
def logout():
    email = request.cookies.get("email")
    if email in all_users:
        del all_users[email]
    response = make_response(render_template('index.html'))
    response.delete_cookie('email')
    return response


if __name__ == '__main__':
    print(f"http://{backend.PROJECT_HOST}:{backend.PROJECT_PORT}")
    app.run(host=backend.PROJECT_HOST, port=backend.PROJECT_PORT)
