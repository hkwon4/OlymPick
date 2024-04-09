import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'yu942u'
app.config['MYSQL_PASSWORD'] = 'Test!234'
app.config['MYSQL_DB'] = 'team5_db'

mysql = MySQL(app)

# Define a dictionary for each person's information
# Change your name, role in the group, and put some details in about
# To run, make sure your directory is in application, then type in the terminal "python main.py" (Flask required)
people_info = {
    'Johnny Kwon': {'name': 'Johnny Kwon', 'role': 'Team Lead', 'about': ''},
    'Fadee Ghiragosian': {'name': 'Fadee Ghiragosian', 'role': 'Backend Lead', 'about': ' I am pursuing a degree in Computer Science, my family is from Egypt and Armenia, and I love playing video games. '},
    'Ethan Ho': {'name': 'Ethan Ho', 'role': 'Github Lead', 'about': ' Last semester for CS Degree. I build custom keyboards, play video games, and read in my spare time. '},
    'Abby Lin': {'name': 'Abby Lin', 'role': 'Database', 'about': ' Last Semester CS Major, an international transfer student from Taiwan. I love music, swimming, and playing games.'},
    'Nichan Lama': {'name': 'Nichan lama', 'role': 'Backend', 'about': 'I am a CS major. I love trying out new food and working out.'},
    'Zabiullah Niemati': {'name': 'Zabiullah Niemati', 'role': 'Frontend', 'about': ''},
    'Zizo Ezzat': {'name': 'Zizo Ezzat', 'role': 'Frontend', 'about': '4th year CS Major, I love working out and listening to music.'},
}
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/Profile Page')
def profile():
    return render_template('userpage.html')

@app.route('/login', methods=['GET','POST'])
def login():
    msg = request.args.get('msg')  # Get the 'msg' parameter from the URL
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        password = request.form['password']
        # Check if user exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM newuser WHERE email = %s AND password = %s', (email, password,))
        # Fetch one record and return result
        user = cursor.fetchone()
        cursor.close()
        # If user exists in users table in our database
        if user:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = user['id']
            session['email'] = user['email']
            # Redirect to home page
            return 'Logged in successfully!'
        else:
            # User doesn't exist or email/password incorrect
            msg = 'Incorrect email/password!'

    return render_template('login.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = None  # Initialize msg
    if request.method == 'POST' and 'username' in request.form and 'email' in request.form and 'password' in request.form:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        # Check if the email already exists in the database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM newuser WHERE email = %s ', (email,))
        user = cursor.fetchone()

        if user:
            # If user with the same email already exists
            msg = 'An account with this email already exists.'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not email or not password:
            msg = 'Please fill out the form!'
        else:
            # If the email is not already registered, proceed with registration
            cursor.execute("INSERT INTO newuser (username, email, password, role) VALUES (%s, %s, %s, %s)", (username, email, password, role))
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
            u.uni_name = %s;
        """
        cursor.execute(query, (searchTerm,))
    elif searchFilter == 'Sports':
        # SQL query for 'Sports' search by event_name or category
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
            s.event_name LIKE %s
                OR s.category LIKE %s
        GROUP BY u.uni_name;
        """
        like_term = f"%{searchTerm}%"
        cursor.execute(query, (like_term, like_term))
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
        } if searchFilter == 'Sports' else {
            'fullName': row[0],
            'gender': row[1],
            'category': row[2],
            'event_name': row[3],
            'no_medals': row[4]
        }if searchFilter == 'University' else {}
        for row in result
    ]
    return render_template('results.html', results=results_info, searchTerm=searchTerm, searchFilter=searchFilter)
