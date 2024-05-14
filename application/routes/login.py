from flask import Blueprint, request, render_template, redirect, url_for, session,flash
import MySQLdb.cursors
import bcrypt
from extensions import mysql
import base64

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    msg = None  # Initialize msg
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['loggedin'] = True
            session['email'] = user['email']
            session['firstname'] = user['firstName']
            session['lastname'] = user['lastName']
            session['user_id'] = user['user_id']  
            if '@example' in user['email']:
                session['is_admin'] = True
            else:
                session['is_admin'] = False
            return redirect(url_for('login.loggedlanding', user_id=user['user_id'], full_name=user['fullName']))
        else:
            flash('Incorrect email/password!', 'error')  # Set a flash message

            msg = 'Incorrect email/password!'
    
    return render_template('login.html', msg=msg, session=session)

@login_bp.route('/unilogin', methods=['GET', 'POST'])
def unilogin():
    msg = None  # Initialize msg
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Universities WHERE email = %s', (email,))
        university = cursor.fetchone()
        cursor.close()

        if university and password == university['password']:
            session['loggedin'] = True
            session['email'] = university['email']
            session['university_id'] = university['university_id']
            session['uni_name'] = university['uni_name']
            if '@example' in university['email']:
                session['is_admin'] = True
            else:
                session['is_admin'] = False

            return redirect(url_for('login.uniloggedlanding', university_id=university['university_id'], uni_name=university['uni_name']))
        else:
            flash('Incorrect email/password!', 'error')  # Set a flash message

            msg = 'Incorrect email/password!'
    
    return render_template('unilogin.html', msg=msg)

@login_bp.route('/loggedlanding')
def loggedlanding():
    user_id = request.args.get('user_id')
    full_name = request.args.get('full_name')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT file_data FROM UserProfileImg WHERE user_id = %s ORDER BY uploaded_at DESC LIMIT 1", [user_id])
    result = cursor.fetchone()
    cursor.close()

    profile_picture = None
    if result:
        profile_picture = base64.b64encode(result[0]).decode('utf-8')

    return render_template('loggedlanding.html', user_id=user_id, full_name=full_name, profile_picture=profile_picture)

@login_bp.route('/universityHome')
def uniloggedlanding():
    uni_name = request.args.get('uni_name')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT address, city, state, zipcode, email, phone FROM Universities WHERE uni_name = %s", (uni_name,))
    result = cursor.fetchone()
    cursor.close()

    if result:
        address, city, state, zipcode, email, phone_number = result
        formatted_address = f"{address}, {city}, {state} {zipcode}"
        API_KEY = 'AIzaSyByc-Nkq0OG7uysLeAzABMVjnPQpOeU1IU'
        return render_template('universityHome.html', uni_name=uni_name, address=formatted_address, api_key=API_KEY, email=email, phone=phone_number)
    else:
        return "University not found"
