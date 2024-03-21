from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

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
            Athletes.fullName, 
            Athletes.gender, 
            Sports.category,
            Sports.event_name, 
            Athletes.no_medals
        FROM 
            Athletes
        INNER JOIN 
            Universities ON Athletes.uni_id = Universities.uni_id
        INNER JOIN 
            Sports ON Athletes.sport_id = Sports.sport_id
        WHERE 
            Universities.uniName = %s;
        """
        cursor.execute(query, (searchTerm,))

    elif searchFilter == 'Sports':
        # SQL query for 'Sports' search by event_name or category
        query = """
        SELECT 
            Universities.uniName AS university_name,
            COUNT(DISTINCT Sports.event_name) AS number_of_events,
            COUNT(DISTINCT Athletes.athlete_id) AS number_of_athletes,
            SUM(Athletes.no_medals) AS number_of_medals
        FROM 
            Athletes
        INNER JOIN 
            Universities ON Athletes.uni_id = Universities.uni_id
        INNER JOIN 
            Sports ON Athletes.sport_id = Sports.sport_id
        WHERE 
            Sports.event_name LIKE %s OR Sports.category LIKE %s
        GROUP BY 
            Universities.uniName;
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
        }
        for row in result
    ]

    return render_template('results.html', results=results_info, searchTerm=searchTerm, searchFilter=searchFilter)

if __name__ == '__main__':
    app.run(debug=True)
