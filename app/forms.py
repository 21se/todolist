from datetime import datetime

from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, DateTimeField
from wtforms.validators import DataRequired


class BaseForm(FlaskForm):
    current_user = current_user
    search_field = StringField()


class SignupForm(BaseForm):
    name = 'Signup'
    login = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    confirm_password = PasswordField("Потвердите пароль", validators=[DataRequired()])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField()
    to_login = SubmitField()


class LoginForm(BaseForm):
    name = 'Login'
    login = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField()
    to_signup = SubmitField()


class TasksForm(BaseForm):
    name = 'Tasks'
    create = SubmitField()
    logoff = SubmitField()


class TaskForm(BaseForm):
    name = 'Task'
    title = StringField("Название", validators=[DataRequired()])
    description = TextAreaField("Описание")
    start_time = DateTimeField("Дата создания")
    end_time = DateTimeField("Конец задачи")
    file = FileField('file')
    upload = SubmitField()
    create = SubmitField()
    delete = SubmitField()
    exit = SubmitField()
    save = SubmitField()

    def populate(self, title, description='', start_time=datetime.now, end_time=datetime.min):
        self.title.data = title
        self.description.data = description
        self.start_time.data = start_time
        self.end_time.data = end_time
