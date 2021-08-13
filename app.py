from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'myFlaskApp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route("/")
def root():
    return render_template("index.html")

class RegisteForm(Form):
    name = StringField('Name', validators=[validators.input_required(), validators.Length(min=3, max=20)])
    username  = StringField('Username', validators=[validators.input_required(), validators.Length(min=3, max=20)])
    email  = StringField('Email', validators=[validators.Length(min=6, max=30)])
    password = PasswordField('Password', validators=[validators.DataRequired(), validators.EqualTo('confirm', message="Passwords do not match!")])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisteForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username=form.username.data
        password = sha256_crypt.encrypt(str((form.password.data)))
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)", (name, email, username, password))
        mysql.connection.commit()
        cur.close()

        flash("Successfully registered", 'success')
        redirect(url_for('index'))

    return render_template('register.html', form=form)

if __name__ == "__main__":
    app.run(debug=True)
