from functools import wraps

from flask import request, render_template
from flask_login import current_user, logout_user

from .models import Task, db
from .views import TasksForm


def request_args(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):

        if request.args.get('logout'):
            logout_user()
            return func(*args, **kwargs)

        search_field = request.args.get('search_field')
        if search_field:
            tasks_list_title = db.session.query(Task).filter(
                Task.owner_id == current_user.id,
                Task.title.like('%{}%'.format(search_field))
            )
            tasks_list_description = db.session.query(Task).filter(
                Task.owner_id == current_user.id,
                Task.description.like('%{}%'.format(search_field))
            )
            tasks_list = tasks_list_title.union(tasks_list_description).all()
            return render_template('tasks.html', form=TasksForm(), tasks_list=tasks_list, current_user=current_user)

        return func(*args, **kwargs)

    return decorated_function
