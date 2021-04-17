from flask import Flask
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'Q(@fj29j73fas@j7sda*J@'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:av4*A@VM78n@CM#*97@localhost/todolist'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'app\\static\\uploads'

manager = Manager(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь или зарегиструйтесь'
limiter = Limiter(
    app,
    key_func=get_remote_address
)

from . import views
