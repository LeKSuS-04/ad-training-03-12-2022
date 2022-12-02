from secrets import choice
from string import ascii_letters, digits
from functools import wraps
from flask import Flask, render_template, request, flash, redirect, url_for, g
from auth import encode_session, decode_session
from db import init_db, get_db

app = Flask(__name__, static_folder='static')
app.secret_key = 'goodmorning'

init_db()


def get_random_string(length: int = 10) -> str:
    return ''.join(choice(ascii_letters + digits) for _ in range(length))


@app.teardown_appcontext
def close_db_connection(_):
    con = g.get('database')
    if con is not None:
        con.close()


@app.before_request
def get_user_from_session():
    session = request.cookies.get('secure_session')
    if not session:
        return

    username = decode_session(session)
    cur = get_db().cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cur.fetchone()
    if not user:
        return

    g.username = username


def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not g.get('username'):
            flash('You must be authorized to view this page')
            return redirect('/login')
        return f(*args, **kwargs)

    return wrapped


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/login')
def login_view():
    return render_template('login.html')


@app.post('/login')
def login_handle():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Both username and password are required')
        return redirect(url_for('login_view'))

    cur = get_db().cursor()
    cur.execute(
        'SELECT * FROM users WHERE username = ? and password = ?', (username, password)
    )
    rows = cur.fetchone()
    if not rows:
        flash('User ne nayden')
        return redirect(url_for('login_view'))

    resp = redirect(url_for('index'))
    resp.set_cookie('secure_session', encode_session(username))
    return resp


@app.get('/sign-up')
def sign_up_view():
    return render_template('sign-up.html')


@app.post('/sign-up')
def sign_up_handler():
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        flash('Both username and password are required')
        return redirect(url_for('sign_up_view'))

    con = get_db()
    cur = con.cursor()
    cur.execute('SELECT * FROM users WHERE username = ?', (username,))
    rows = cur.fetchall()
    if rows:
        flash(f'User with username "{username}" already exists')
        return redirect(url_for('sign_up_view'))

    cur.execute(
        'INSERT INTO users (username, password) VALUES (?, ?)', (username, password)
    )
    con.commit()

    resp = redirect(url_for('index'))
    resp.set_cookie('secure_session', encode_session(username))
    return resp


@app.get('/logout')
def logout_handler():
    resp = redirect(url_for('login_view'))
    resp.delete_cookie('secure_session')
    return resp


@app.get('/all-shporas')
def all_shporas():
    cur = get_db().cursor()
    cur.execute('SELECT * FROM shporas WHERE is_public = 1')
    shporas = cur.fetchall()
    return render_template(
        'shporas-table.html', page_name='Public shporas', shporas=shporas
    )


@app.get('/my-shporas')
@login_required
def my_shporas_view():
    cur = get_db().cursor()
    cur.execute(f'SELECT * FROM shporas WHERE owner = "{g.username}"')
    shporas = cur.fetchall()
    return render_template(
        'shporas-table.html', page_name='Your shporas', shporas=shporas
    )


@app.get('/shpora')
def view_shpora():
    shpora_id = request.args.get('id')
    provided_passwd = request.args.get('password')

    params = {'id': shpora_id}

    cur = get_db().cursor()
    cur.execute('SELECT title, content, is_protected, password FROM shporas WHERE id = ?', (shpora_id, ))
    shpora = cur.fetchone()
    print(shpora)
    if shpora:
        title, content, is_protected, password = shpora
        print(is_protected, password, provided_passwd)
        if not is_protected or password == provided_passwd:
            params |= {
                'title': title,
                'content': content
            }

    return render_template('shpora.html', **params)


@app.get('/create-shpora')
@login_required
def create_view():
    return render_template('create.html')


@app.post('/create-shpora')
@login_required
def create_handle():
    title = request.form.get('title')
    content = request.form.get('content')
    is_private = request.form.get('is_private')
    is_protected = request.form.get('is_protected')
    password = request.form.get('password')
    print(f'{title=}, {content=}, {is_private=}, {is_protected=}, {password=}')

    if not title or not content:
        flash('Title and content are required')
        return redirect(url_for('create_view'))

    con = get_db()
    cur = con.cursor()
    note_id = get_random_string(16)
    cur.execute(
        'INSERT INTO shporas (id, owner, title, content, is_public, is_protected, password) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (
            note_id,
            g.username,
            title,
            content,
            0 if is_private else 1,
            1 if is_protected else 0,
            password,
        ),
    )
    con.commit()

    params = {'id': note_id}
    if password:
        params['password'] = password
    
    return redirect(url_for('view_shpora', **params))
