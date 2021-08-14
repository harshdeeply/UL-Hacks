from flask import Flask, render_template, flash, redirect, url_for, session, request
from flask_mysqldb import MySQL
from functools import wraps
from wtforms import Form, StringField, TextAreaField, PasswordField, form, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

# Configure your database configs here
app.config['MYSQL_HOST'] = 'localhost' # MySQL host
app.config['MYSQL_USER'] = 'root' # MySQL user
app.config['MYSQL_PASSWORD'] = 'root' # MySQL user login password
app.config['MYSQL_DB'] = 'myFlaskApp' # MySQL DB Name
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' # MySQL Cursor Class

# Creating MySQL instance
mysql = MySQL(app)


@app.route("/")
def root():
    return render_template("index.html")

# Registeration Form Class
class RegisterForm(Form):
    name = StringField('Name', validators=[validators.input_required(), validators.Length(min=3, max=20)])
    username  = StringField('Username', validators=[validators.input_required(), validators.Length(min=3, max=20)])
    email  = StringField('Email', validators=[validators.Length(min=6, max=30)])
    password = PasswordField('Password', validators=[validators.DataRequired(), validators.EqualTo('confirm', message="Passwords do not match!")])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    # If valid request
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username=form.username.data
        password = sha256_crypt.encrypt(str((form.password.data)))
        # Initiating connection
        cur = mysql.connection.cursor()
        # INSERT query
        cur.execute("INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)", (name, email, username, password))
        # Committing transaction
        mysql.connection.commit()
        # Closing connection
        cur.close()
        # Success Log
        flash("Successfully registered.", 'success')
        # Redirecting on success
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        if result > 0:
            data = cur.fetchone()
            password = data['password']
            if sha256_crypt.verify(password_candidate, password):
                app.logger.info("User found!")
                session['logged_in'] = True
                session['username'] = username
                flash('Success', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid Password."
                return render_template('login.html', error=error)
            cur.close()
        else:
                error = "User does not exist."
                return render_template('login.html', error=error)
    return render_template('login.html')

def is_user_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Login to continue.', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/dashboard')
@is_user_logged_in
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'success')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.secret_key = 'secret_key'
    app.run(debug=True)
