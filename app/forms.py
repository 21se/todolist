from datetime import datetime

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, DateTimeField
from wtforms.validators import DataRequired


class NewTaskForm(FlaskForm):
    title = StringField('Название', [DataRequired()])
    description = TextAreaField('Описание')
    end_time = DateTimeField(format='%d.%m.%Y %H:%M')
    start_time = DateTimeField(format='%d.%m.%Y %H:%M')
    create = SubmitField('Создать задачу')


class SignupForm(FlaskForm):
    login = StringField()
    password = PasswordField()
    confirm_password = PasswordField()
    remember = BooleanField("Запомнить меня")
    submit = SubmitField()
    to_login = SubmitField()


class LoginForm(FlaskForm):
    login = StringField()
    password = PasswordField()
    remember = BooleanField("Запомнить меня")
    submit = SubmitField()
    to_signup = SubmitField()


class TaskForm(FlaskForm):
    title = StringField('Название', [DataRequired()])
    description = TextAreaField('Описание')
    end_time = DateTimeField(format='%Y-%m-%dT%H:%M')
    start_time = DateTimeField(format='%Y-%m-%dT%H:%M')
    file = FileField()
    upload = SubmitField('Загрузить файл')
    save = SubmitField('Сохранить задачу')
    delete = SubmitField('Удалить задачу')

    def populate(self, title, description='', start_time=datetime.now, end_time=datetime.max):
        self.title.data = title
        self.description.data = description
        self.start_time.data = start_time
        if end_time != datetime.max:
            self.end_time.data = end_time
