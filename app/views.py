import os
from datetime import datetime
from shutil import rmtree
from time import time

from flask import request, render_template, flash, redirect, url_for, send_from_directory
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.utils import secure_filename

from app import app, limiter
from .forms import TaskForm, NewTaskForm, LoginForm, SignupForm
from .models import Task, TaskFile, User, db
from .utils import get_date_fact, translate


@app.context_processor
def inject_now():
    return {
        'datetime_max': datetime.max,
        'current_user': current_user
    }


@app.route('/')
@login_required
def index():
    return redirect(url_for('tasks'))


@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    tasks_list = db.session.query(Task).filter(Task.owner_id == current_user.id).all()
    return render_template('tasks.html', tasks_list=tasks_list)


@app.route('/tasks/new', methods=['GET', 'POST'])
@limiter.limit(['1 per second'])
@login_required
def new_task():
    messages = []

    if request.method == 'POST':
        form = NewTaskForm(request.form)
        if form.is_submitted():

            end_time = datetime.max
            start_time = datetime.now()

            if form.data.get('end_time'):
                end_time = form.data.get('end_time')
            if form.data.get('start_time'):
                start_time = form.data.get('start_time')

            if end_time < start_time:
                flash("Дата конца задачи меньше чем дата начала ({})".format(start_time.strftime('%d.%m.%Y %H:%M')),
                      'Ошибка')
                return render_template('new_task.html', form=form)

            new_user_task = Task()
            new_user_task.title = form.title.data
            new_user_task.description = form.description.data
            new_user_task.owner_id = current_user.id
            new_user_task.end_time = end_time
            new_user_task.start_time = start_time
            db.session.add(new_user_task)
            db.session.commit()

            return redirect(url_for('task', task_id=new_user_task.id))

    return render_template('new_task.html', form=NewTaskForm(), messages=messages)


@app.route('/tasks/<int:task_id>', methods=['GET', 'POST'])
@limiter.limit(['2 per second'])
@login_required
def task(task_id):
    user_task = db.session.query(Task).filter(Task.owner_id == current_user.id, Task.id == task_id).first()

    if not user_task:
        return redirect(url_for('index'))

    form = TaskForm()
    if request.method == 'POST':
        if form.is_submitted():
            if form.save.data:

                end_time = datetime.max
                start_time = datetime.now()

                if form.data.get('end_time'):
                    end_time = form.data.get('end_time')
                if form.data.get('start_time'):
                    start_time = form.data.get('start_time')

                if end_time < start_time:
                    flash("Дата конца задачи меньше чем дата начала ({})".format(start_time.strftime('%d.%m.%Y %H:%M')),
                          'Ошибка')
                    return render_template('task.html', form=form, task=user_task)

                user_task.title = form.title.data
                user_task.description = form.description.data
                if end_time:
                    user_task.end_time = end_time
                if start_time:
                    user_task.start_time = start_time
                db.session.add(user_task)
                db.session.commit()

                return redirect(url_for('task', task_id=user_task.id))
            elif form.delete.data:
                return redirect(url_for('delete_task', task_id=task_id))
            elif form.upload.data:
                task_file = form.file.data
                if not task_file:
                    flash("Не указан файл для загрузки", 'Ошибка')
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

    file_list = db.session.query(TaskFile).filter(TaskFile.task_id == task_id).all()
    form.populate(user_task.title, user_task.description, user_task.start_time, user_task.end_time)

    fact = get_date_fact(user_task.start_time.day, user_task.start_time.month)
    facts = [fact]

    if user_task.end_time != datetime.max:
        fact = get_date_fact(user_task.end_time.day, user_task.end_time.month)
        facts.append(fact)

    translated_facts = translate(facts)

    return render_template('task.html', form=form, task=user_task, files=file_list, facts=translated_facts)


@app.route('/tasks/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.form:
        search_field = request.form.get('find', default='')

        tasks_list_title = db.session.query(Task).filter(
            Task.owner_id == current_user.id,
            Task.title.like('%{}%'.format(search_field))
        )
        tasks_list_description = db.session.query(Task).filter(
            Task.owner_id == current_user.id,
            Task.description.like('%{}%'.format(search_field))
        )
        tasks_list = tasks_list_title.union(tasks_list_description).all()

        return render_template('tasks.html', tasks_list=tasks_list, form=request.form, search=True)

    return redirect(url_for('tasks'))


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
@limiter.limit(['1 per second'])
@login_required
def delete_file(task_id, file_id):
    task_file = db.session.query(TaskFile).filter(TaskFile.task_id == task_id, TaskFile.id == file_id).first()

    if not task_file:
        return 'file not found'

    db.session.delete(task_file)
    os.remove(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], str(task_id), task_file.filename_stored))
    db.session.commit()

    return redirect(url_for('task', task_id=task_id))


@app.route('/tasks/<int:task_id>/delete', methods=['GET', 'POST'])
@limiter.limit(['1 per second'])
@login_required
def delete_task(task_id):
    user_task = db.session.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()

    if user_task:
        dir_path = os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], str(task_id))
        if os.path.isdir(dir_path):
            rmtree(os.path.join(dir_path))
        db.session.query(TaskFile).filter(TaskFile.task_id == user_task.id).delete()
        db.session.delete(user_task)
        db.session.commit()

    return redirect(url_for('index'))


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = SignupForm()

    if form.is_submitted():
        if form.submit.data:
            user = db.session.query(User).filter(User.login == form.login.data).first()

            if user:
                flash("Указанный логин уже зарегистрирован", 'error')
                return render_template('signup.html', form=form)
            if not form.password.data or not form.login.data:
                flash("Укажите логин и пароль", 'error')
                return render_template('signup.html', form=form)
            if form.password.data != form.confirm_password.data:
                flash("Пароли не совпадают!", 'error')
                return render_template('signup.html', form=form)
            if len(form.password.data) > 30 or len(form.login.data) > 20:
                flash("Слишком длинный логин/пароль", 'error')
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


@app.route('/logout')
@login_required
def logout():
    logout_user()

    return redirect(url_for('index'))
