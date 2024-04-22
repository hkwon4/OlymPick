from flask import Blueprint, request, render_template, redirect, url_for, session
import MySQLdb.cursors
import bcrypt
from extensions import mysql

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        return redirect(url_for('login.loggedlanding'))

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
            return redirect(url_for('login.loggedlanding'))
        else:
            # User doesn't exist or password incorrect
            msg = 'Incorrect email/password!'

    return render_template('login.html', msg=msg)

@login_bp.route('/loggedlanding')
def loggedlanding():
    if 'loggedin' not in session:
        return redirect(url_for('login.login'))

    return render_template('loggedlanding.html')

@login_bp.route('/logout')
def logout():
    # Clear session data
    session.clear()
    # Redirect to the landing page or login page
    return redirect(url_for('landing.landing'))
