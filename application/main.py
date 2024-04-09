import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import bcrypt

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'yu942u'
app.config['MYSQL_PASSWORD'] = 'Test!234'
app.config['MYSQL_DB'] = 'test_schema'

mysql = MySQL(app)

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/login', methods=['GET','POST'])
def login():
    msg = None  # Initialize msg
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if user exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM newuser WHERE email = %s', (email,))
        # Fetch one record and return result
        user = cursor.fetchone()
        cursor.close()

        # If user exists and passwords match
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = user['id']
            session['email'] = user['email']
            session['username'] = user['username']
            # Redirect to logged in landing page
            return redirect(url_for('loggedlanding'))
        else:
            # User doesn't exist or password incorrect
            msg = 'Incorrect email/password!'

    return render_template('login.html', msg=msg)



@app.route('/loggedlanding' )
def loggedlanding():
    return render_template('loggedlanding.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = None  # Initialize msg
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        
        # Check if the email already exists in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM newuser WHERE email = %s ', (email,))
        user = cursor.fetchone()

        if user:
            # If user with the same email already exists
            msg = 'An account with this email already exists.'
        elif not username or not email or not password:
            msg = 'Please fill out all fields.'
        elif not re.match(r'^[A-Za-z0-9]+$', username):
            msg = 'Username must contain only letters and numbers.'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address.'
        else:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # If the email is not already registered, proceed with registration
           # If the email is not already registered, proceed with registration
            cursor.execute("INSERT INTO newuser (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
            mysql.connection.commit()
            msg = 'User registered successfully!'
            return redirect(url_for('login', msg=msg))  # Redirect to login page after successful registration
     
        cursor.close()
    
    return render_template('register.html', msg=msg)


@app.route('/About Me')
def team():
    names = list(people_info.keys())
    return render_template('index.html', names=names)
@app.route('/about/<name>')
def about(name):
    person = people_info.get(name)
    if person:
        return render_template('about.html', person=person)
    else:
        return "Person not found"
@app.route('/about/<name>/update', methods=['POST'])
def update_about(name):
    if request.method == 'POST':
        about = request.form['about']
        person = people_info.get(name)
        if person:
            person['about'] = about
            return redirect(url_for('about', name=name))
        else:
            return "Person not found"
    else:
        return redirect(url_for('about', name=name))
    
@app.route('/search', methods=['POST'])
def search():
    searchTerm = request.form.get('searchTerm')
    searchFilter = request.form.get('searchFilter')
    cursor = mysql.connection.cursor()

    if searchFilter == 'University':
        # SQL query for 'University' search
        query = """
        SELECT 
            a.fullName,
            a.gender,
            s.category,
            a.event_name,
            a.no_medals
        FROM
            Athletes a
                JOIN
            AthletesUniversities au ON a.athlete_id = au.athlete_id
                JOIN
            Universities u ON au.uni_id = u.university_id
                JOIN
            Sports s ON a.sport_id = s.sport_id
        WHERE
            u.uni_name = %s
        ORDER BY a.no_medals DESC;
        """
        cursor.execute(query, (searchTerm,))
    elif searchFilter == 'Sports':
        # SQL query for 'Sports' search
        query = """
        SELECT 
            u.uni_name,
            COUNT(DISTINCT s.event_name),
            COUNT(DISTINCT a.athlete_id),
            SUM(a.no_medals)
        FROM
            Universities u
                JOIN
            AthletesUniversities au ON u.university_id = au.uni_id
                JOIN
            Athletes a ON au.athlete_id = a.athlete_id
                JOIN
            Sports s ON a.sport_id = s.sport_id
        WHERE
            s.event_name LIKE %s OR s.category LIKE %s
        GROUP BY u.uni_name
        ORDER BY SUM(a.no_medals) DESC;
        """
        like_term = f"%{searchTerm}%"
        cursor.execute(query, (like_term, like_term))
    elif searchFilter == 'State':
        # SQL query for 'State' search
        query = """
        SELECT 
            u.uni_name,
            COUNT(DISTINCT s.event_name) AS EventCount,
            COUNT(DISTINCT a.athlete_id) AS AthleteCount,
            SUM(a.no_medals) AS TotalMedals
        FROM
            Universities u
                JOIN
            AthletesUniversities au ON u.university_id = au.uni_id
                JOIN
            Athletes a ON au.athlete_id = a.athlete_id
                JOIN
            Sports s ON a.sport_id = s.sport_id
        WHERE
            u.state = %s
        GROUP BY u.uni_name
        ORDER BY SUM(a.no_medals) DESC;
        """
        cursor.execute(query, (searchTerm,))

    # Fetching results and closing cursor
    result = cursor.fetchall()
    cursor.close()
    # Convert the result to the desired format
    results_info = [
        {
            'University Name': row[0],
            'Number of Events': row[1],
            'Number of Athletes': row[2],
            'Number of Medals': row[3]
        } if searchFilter in ['Sports', 'State'] else {
            'fullName': row[0],
            'gender': row[1],
            'category': row[2],
            'event_name': row[3],
            'no_medals': row[4]
        } for row in result
    ]
    return render_template('results.html', results=results_info, searchTerm=searchTerm, searchFilter=searchFilter)


if __name__ == '__main__':
    app.run(debug=True)