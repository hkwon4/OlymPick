from flask import Blueprint, request, render_template, redirect, url_for, session
import MySQLdb.cursors
import bcrypt
from extensions import mysql
import base64

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



@login_bp.route('/unilogin', methods=['GET', 'POST'])
def unilogin():
    msg = None  # Initialize msg
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']

        # Check if user exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Universities WHERE email = %s', (email,))
        # Fetch one record and return result
        university = cursor.fetchone()
        print(university)
        cursor.close()

        # If user exists and passwords match
        if university and password == university['password']:
            # Create session data
            session['loggedin'] = True
            session['email'] = university['email']
            session['university_id'] = university['university_id']
            session['uni_name'] = university['uni_name']
            # Redirect to logged in landing page
            return redirect(url_for('login.uniloggedlanding', university_id=university['university_id'], uni_name=university['uni_name']))

        else:
            # User doesn't exist or password incorrect
            msg = 'Incorrect email/password!'

    return render_template('unilogin.html', msg=msg)



@login_bp.route('/loggedlanding')
def loggedlanding():
    user_id = request.args.get('user_id')
    full_name = request.args.get('full_name')
    university_id = request.args.get('university_id')

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

@login_bp.route('/universityHome')
def uniloggedlanding():
    print("helo from unipage ")
    uni_name = request.args.get('uni_name')
    university_id = request.args.get('university_id')
    print(uni_name)

    cursor = mysql.connection.cursor()

    query = "SELECT address, city, state, zipcode, email, phone FROM Universities WHERE uni_name = %s"
    cursor.execute(query, (uni_name,))
    
    result = cursor.fetchone()
    print(result)
    cursor.close()

    if result:
        address, city, state, zipcode, email, phone_number = result
        formatted_address = f"{address}, {city}, {state} {zipcode}"
        API_KEY = 'AIzaSyByc-Nkq0OG7uysLeAzABMVjnPQpOeU1IU'
        return render_template('universityHome.html',university_id = university_id,  uni_name=uni_name, address=formatted_address, api_key=API_KEY, email=email, phone=phone_number)
    else:
        return "University not found"
    

    return render_template('universityHome.html', university_id = university_id, uni_name=uni_name, UniversityProfile= UniversityProfile) 