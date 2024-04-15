import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import MySQLdb.cursors
import re
import bcrypt

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'yu942u'
app.config['MYSQL_PASSWORD'] = 'Test!234'
app.config['MYSQL_DB'] = 'team5_db'

mysql = MySQL(app)

@app.route('/login', methods=['GET','POST'])
def login():
    msg = None  # Initialize msg
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if user exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
        # Fetch one record and return result
        user = cursor.fetchone()
        cursor.close()

        # If user exists and passwords match
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['email'] = user['email']
            session['firstname'] = user['firstName']
            session['lastname'] = user['lastName']
            # Redirect to logged in landing page
            return redirect(url_for('loggedlanding'))
        else:
            # User doesn't exist or password incorrect
            msg = 'Incorrect email/password!'

    return render_template('login.html', msg=msg)