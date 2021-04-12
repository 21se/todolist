from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1023))
    owner_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime(), default=datetime.now, nullable=False)
    end_time = db.Column(db.DateTime(), default=datetime.min)

    def __repr__(self):
        return '<{}:{}>'.format(self.id, self.title)


class TaskFile(db.Model):
    __tablename__ = 'task_files'
    id = db.Column(db.Integer(), primary_key=True)
    task_id = db.Column(db.Integer(), db.ForeignKey('tasks.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filename_stored = db.Column(db.String(255), nullable=False)
    mimetype = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<{}:{}>'.format(self.file_id, self.filename)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    login = db.Column(db.String(20), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.now)

    def __init__(self, login):
        self.login = login

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.login)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


db.create_all()

user = User(login='root')
user.set_password('pass')

if db.session.query(User).count() == 0:
    db.session.add(user)
    db.session.commit()
