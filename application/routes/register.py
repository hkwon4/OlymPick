from flask import Blueprint, request, render_template, redirect, url_for
import MySQLdb.cursors
import re
import bcrypt
from extensions import mysql

register_bp = Blueprint('register', __name__)

@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    msg = None  # Initialize msg
    if request.method == 'POST' and 'firstName' in request.form and 'lastName' in request.form and 'email' in request.form and 'password' in request.form:
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the email already exists in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM Users WHERE email = %s ', (email,))
        user = cursor.fetchone()

        if user:
            # If user with the same email already exists
            msg = 'An account with this email already exists.'
        elif not firstName or not lastName or not email or not password:
            msg = 'Please fill out all fields.'
        elif not re.match(r'^[A-Za-z0-9]+$', firstName):
            msg = 'Username must contain only letters and numbers.'
        elif not re.match(r'^[A-Za-z0-9]+$', lastName):
            msg = 'Username must contain only letters and numbers.'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address.'
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            # If the email is not already registered, proceed with registration
            cursor.execute("INSERT INTO Users (email, password, firstName, lastName) VALUES (%s, %s, %s, %s)", (email, hashed_password, firstName, lastName))
            mysql.connection.commit()
            msg = 'User registered successfully!'
            return redirect(url_for('login.login', msg=msg))  # Redirect to login page after successful registration

        cursor.close()

    return render_template('register.html', msg=msg)

@register_bp.route('/uniregister', methods=['GET', 'POST'])
def uniregister():
    print("hello from uni")
    msg = None  # Initialize msg
    if request.method == 'POST' and 'uni_name' in request.form and 'email' in request.form and 'password' in request.form:
        uni_name = request.form.get('uni_name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        address = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state')
        zipcode = request.form.get('zipcode')
        country = request.form.get('country')

        try:
            # Check if the email already exists in the database
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM Universities WHERE email = %s ', (email,))
            university = cursor.fetchone()

            if university: 
                # If university with the same email already exists
                msg = 'An account with this email already exists.'
            elif not uni_name or not email or not password or not phone or not address or not city or not state or not zipcode or not country:
                msg = 'Please fill out all fields.'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address.'
            else:
                print("i am here ")
                # If the email is not already registered, proceed with registration
                cursor.execute("INSERT INTO Universities (email, uni_name, password, phone, address, city, state, zipcode, country) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (email, uni_name, password, phone, address, city, state, zipcode, country))
                mysql.connection.commit()
                msg = 'University registered successfully!'
                return redirect(url_for('login.unilogin', msg=msg))  # Redirect to login page after successful registration

        except Exception as e:
            # Handle database errors
            msg = f"Error: {e}"

        finally:
            if 'cursor' in locals():
                cursor.close()

    return render_template('uniregister.html', msg=msg)