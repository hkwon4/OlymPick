from flask import Blueprint, request, render_template, redirect, url_for, session
import MySQLdb.cursors
import bcrypt
from extensions import mysql
import base64

# Code Review - Having different files for different function make it a lot easier to troubleshoot.
# I find it a lot better than looking through main and trying to pinpoint the exact problem.
login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
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
        # Code Review - Im wondering if this is the cookies that are implemented so that the user could reload the page and not get logged out.
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['email'] = user['email']
            session['firstname'] = user['firstName']
            session['lastname'] = user['lastName']

            # Redirect to logged in landing page
            return redirect(url_for('login.loggedlanding', user_id=user['user_id'], full_name=user['fullName']))

        else:
            # User doesn't exist or password incorrect
            msg = 'Incorrect email/password!'

    return render_template('login.html', msg=msg)
# Code Review - So far the code spacing as well as the commenting throughout the entire program is consistent and helpful. 
@login_bp.route('/loggedlanding')
def loggedlanding():
    user_id = request.args.get('user_id')
    full_name = request.args.get('full_name')

    # Retrieve the latest uploaded profile picture for the user from the database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT file_data FROM UserProfileImg WHERE user_id = %s ORDER BY uploaded_at DESC LIMIT 1", [user_id])
    result = cursor.fetchone()
    cursor.close()

    if result:
        file_data = result[0]
        profile_picture = base64.b64encode(file_data).decode('utf-8')
    else:
        profile_picture = None

    return render_template('loggedlanding.html', user_id=user_id, full_name=full_name, profile_picture=profile_picture)
