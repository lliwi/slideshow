
from flask import (
    Blueprint, flash, g, render_template, request, url_for, session, redirect, current_app, make_response, send_file
)

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import functools
import os

from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def get_all_images():
    image_folder = 'app/static/images/slide'
    images = [img for img in os.listdir(image_folder)
              if img.endswith(".jpg") or
              img.endswith(".jpeg") or
              img.endswith("png")]
    return images

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db, c = get_db()
        error = None
        c.execute(
            'select id, user, password from users where user = %s', (username,)
        )

        user = c.fetchone()

        if user is None:
            error = 'invalid user / password'
        elif not check_password_hash(user['password'], password):
            error = 'invalid user / password'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('auth.index'))

        flash(error)
        print('si, error')

        resp = make_response(render_template('auth/login.html', error=error))
        return resp

    else:

        resp = make_response(render_template('auth/login.html'))
        return resp


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.usert = None
    else:
        db, c = get_db()
        c.execute(
            'select * from users where id = %s', (user_id,)
        )
        g.user = c.fetchone()


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.route('/')
@login_required
def index():

    images = get_all_images()

    resp = make_response(render_template('auth/index.html', images = images))
    return resp

@bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        username = request.form['username']
        password = request.form['password']

        db, c = get_db()
        error = None
        c.execute(
            'select id from users where user = %s', (username,)
        )
        if not username:
            error = 'Username es requerido'
        if not password:
            error = 'Password es requerido'
        elif c.fetchone() is not None:
            error = 'User {} exists.'.format(
                username)

        if error is None:
            c.execute(
                'insert into users (name, surname, user, password) values (%s, %s, %s, %s)',
                (name, surname, username, generate_password_hash(password))
            )
            db.commit()

            db, c = get_db()
            c.execute('select id, name, surname, user from users')
            users = c.fetchall()
   
            return render_template('auth/register.html', users=users)
        db, c = get_db()
        c.execute('select id, name, surname, user from users')
        users = c.fetchall()

        flash(error)
       
        return render_template('auth/register.html', error=error, users=users)
        error = None

    else:
        db, c = get_db()
        c.execute('select id, name, surname, user from users')
        users = c.fetchall()
        return render_template('auth/register.html',  users=users)


@bp.route('/delete')
@login_required
def delete():
    id = request.args.get('id')
    db, c = get_db()
    c.execute('delete  from users where id = %s', (id,))
    db.commit()

    db, c = get_db()
    c.execute('select id, name, surname, user from users')
    users = c.fetchall()
    return redirect(url_for('auth.register'))

@bp.route('/image_upload', methods=['POST'])
def image_upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('auth.index'))
   

@bp.route('/image_delete')
@login_required
def image_delete():
    id = request.args.get('id')
    os.remove('app/static/images/slide/' + id)
    return redirect(url_for('auth.index'))

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

