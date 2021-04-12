from app import app
from .forms import TasksForm, TaskForm, SignupForm, LoginForm
from .models import Task, TaskFile, User, db
from flask_login import login_required, current_user, login_user, logout_user
from flask import request, render_template, flash, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
from shutil import rmtree
from time import time


@app.route('/')
@login_required
def index():
    return redirect(url_for('tasks'))


@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    form_name = request.form.get('name')
    form = TasksForm()

    if form_name == 'Tasks':
        if form.is_submitted():
            if form.create.data:
                return render_template('create_task.html', form=TaskForm(), task=Task())
            elif form.search.data and form.search_field.data:
                tasks_list_title = db.session.query(Task).filter(
                    Task.owner_id == current_user.id,
                    Task.title.like('%{}%'.format(form.search_field.data))
                )
                tasks_list_description = db.session.query(Task).filter(
                    Task.owner_id == current_user.id,
                    Task.description.like('%{}%'.format(form.search_field.data))
                )
                tasks_list = tasks_list_title.union(tasks_list_description).all()
                return render_template('tasks.html', form=form, tasks_list=tasks_list, current_user=current_user)
            elif form.logoff.data:
                logout_user()
                return redirect(url_for('login'))

    elif form_name == 'Task':
        form = TaskForm()

        if form.is_submitted():
            if form.create.data and form.title.data:
                new_task = Task(
                    title=form.title.data,
                    description=form.description.data,
                    owner_id=current_user.id,
                    end_time=form.end_time.data or None)
                db.session.add(new_task)
                db.session.commit()
                return redirect(url_for('task', task_id=new_task.id))
            elif form.exit.data:
                return redirect(url_for('index'))

            flash("Не заполнено название задачи!", 'error')
            return render_template('create_task.html', form=form, task=Task())

    tasks_list = db.session.query(Task).filter(Task.owner_id == current_user.id).all()

    return render_template('tasks.html', form=form, tasks_list=tasks_list, current_user=current_user)


@app.route('/tasks/<int:task_id>', methods=['GET', 'POST'])
@login_required
def task(task_id):
    user_task = db.session.query(Task).filter(Task.owner_id == current_user.id, Task.id == task_id).first()

    if not user_task:
        return 'no task with id "{}"'.format(task_id)

    form = TaskForm()

    if form.is_submitted():
        if form.delete.data:
            db.session.delete(user_task)
            db.session.query(TaskFile).filter(TaskFile.task_id == user_task.id).delete()
            rmtree(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], str(task_id)))
            db.session.commit()
            return redirect(url_for('index'))

        elif form.save.data:

            user_task.title = form.title.data
            user_task.description = form.description.data
            user_task.start_time = form.start_time.data
            user_task.end_time = form.end_time.data

            if len(user_task.title) == 0:
                flash("Не заполнено название задачи!", 'error')
                return render_template('task.html', form=form, task=user_task)

            db.session.add(user_task)
            db.session.commit()

            return render_template('task.html', form=form, task=user_task)

        elif form.upload.data:

            task_file = form.file.data

            if not task_file:
                flash("Не указан файл для загрузки!", 'error')
                return render_template('task.html', form=form, task=user_task)

            filename_stored = '{}_{}'.format(int(time()), secure_filename(task_file.filename))
            save_dir = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], str(task_id))
            if not os.path.isdir(save_dir):
                os.mkdir(save_dir)
            file_path = os.path.join(save_dir, filename_stored)

            task_file.save(file_path)

            new_task_file = TaskFile()
            new_task_file.task_id = task_id
            new_task_file.filename = task_file.filename
            new_task_file.filename_stored = filename_stored
            new_task_file.mimetype = task_file.mimetype

            db.session.add(new_task_file)
            db.session.commit()

            return redirect(url_for('task', task_id=task_id))

        elif form.exit.data:
            return redirect(url_for('index'))

    file_list = db.session.query(TaskFile).filter(TaskFile.task_id == task_id).all()
    form.populate(user_task.title, user_task.description, user_task.start_time, user_task.end_time)

    return render_template('task.html', form=form, task=user_task, files=file_list)


@app.route('/tasks/<int:task_id>/files/<int:file_id>', methods=['GET', 'POST'])
@login_required
def file(task_id, file_id):
    task_file = db.session.query(TaskFile).filter(TaskFile.task_id == task_id, TaskFile.id == file_id).first()

    if not task_file:
        return 'file not found'

    if db.session.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).count() != 1:
        return 'file not found'

    path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], str(task_id))
    return send_from_directory(path, task_file.filename_stored, as_attachment=True,
                               attachment_filename=task_file.filename, mimetype=task_file.mimetype)


@app.route('/tasks/<int:task_id>/files/<int:file_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_file(task_id, file_id):
    task_file = db.session.query(TaskFile).filter(TaskFile.task_id == task_id, TaskFile.id == file_id).first()

    if not task_file:
        return 'file not found'

    db.session.delete(task_file)
    os.remove(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], str(task_id), task_file.filename_stored))
    db.session.commit()

    return redirect(url_for('task', task_id=task_id))


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = SignupForm()

    if form.is_submitted():
        if form.submit.data:
            user = db.session.query(User).filter(User.login == form.login.data).first()

            if user:
                flash("Указанный логин уже зарегистрирован!", 'error')
                return render_template('signup.html', form=form)
            if not form.password.data or not form.login.data:
                flash("Укажите логин и пароль!", 'error')
                return render_template('signup.html', form=form)
            if form.password.data != form.confirm_password.data:
                flash("Пароли не совпадают!", 'error')
                return render_template('signup.html', form=form)
            if len(form.password.data) > 30 or len(form.login.data) > 20:
                flash("Слишком длинный логин/пароль!", 'error')
                return render_template('signup.html', form=form)

            new_user = User(login=form.login.data)
            new_user.set_password(form.password.data)

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=form.remember.data)
            return redirect(url_for('index'))

        else:
            return redirect(url_for('login'))

    return render_template('signup.html', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.is_submitted():
        if form.submit.data:
            user = db.session.query(User).filter(User.login == form.login.data).first()

            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('index'))

            flash("Invalid login/password", 'error')
            return render_template('login.html', form=form)

        else:
            return redirect(url_for('signup'))

    return render_template('login.html', form=form)
