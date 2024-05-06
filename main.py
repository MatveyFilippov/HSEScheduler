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

            response = make_response(render_template('tempMainWindow.html', username=user.username))
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
        return render_template('tempMainWindow.html', username=all_users[email].username)
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

        return render_template('tempMainWindow.html', username=all_users[email].username)
    else:
        return render_template('codeForRegistration.html')


@app.route('/temp_main_window', methods=['POST', 'GET'])
def temp_main_window():
    email = request.cookies.get("email")
    if email not in all_users:
        response = make_response(render_template('index.html'))
        response.delete_cookie('email')
        return response
    return render_template('tempMainWindow.html', username=all_users[email].username)


if __name__ == '__main__':
    print(f"http://{backend.PROJECT_HOST}:{backend.PROJECT_PORT}")
    app.run(host=backend.PROJECT_HOST, port=backend.PROJECT_PORT)
