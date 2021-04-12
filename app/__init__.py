from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
import os

app = Flask(__name__, template_folder=os.getcwd() + 'app\\templates',
            static_url_path='', static_folder=os.path.join(os.getcwd(), 'app\\static'))
app.debug = True
app.config['SECRET_KEY'] = 'Q(@fj29j73fas@j7sda*J@'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'app\\static\\uploads'

manager = Manager(app)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from . import views
