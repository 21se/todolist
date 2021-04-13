from app import app, db
from app.models import User, Task, TaskFile
from flask_script import Manager, Shell


def make_shell_context():
    return dict(app=app, db=db, User=User, Task=Task, TaskFile=TaskFile)


manager = Manager(app)
manager.add_command('shell', Shell(make_context=make_shell_context))

if __name__ == '__main__':
    manager.run()
