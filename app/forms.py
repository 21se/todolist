from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, DateTimeField
from wtforms.validators import DataRequired
from datetime import datetime


class SignupForm(FlaskForm):
    name = 'Signup'
    login = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    confirm_password = PasswordField("Потвердите пароль", validators=[DataRequired()])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField()
    to_login = SubmitField()


class LoginForm(FlaskForm):
    name = 'Login'
    login = StringField("Логин", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember = BooleanField("Запомнить меня")
    submit = SubmitField()
    to_signup = SubmitField()


class TasksForm(FlaskForm):
    name = 'Tasks'
    search_field = StringField("Поиск")
    search = SubmitField()
    create = SubmitField()
    logoff = SubmitField()


class TaskForm(FlaskForm):
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
