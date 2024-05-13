from flask import Blueprint, request, render_template, session, redirect, url_for
import MySQLdb.cursors
from extensions import mysql
import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'routes/team05.json'

# Runs a simple report on a Google Analytics 4 property.
# TODO(developer): Uncomment this variable and replace with your
# Google Analytics 4 property ID before running the sample.
property_id = "440696384"

# Using a default constructor instructs the client to use the credentials
# specified in GOOGLE_APPLICATION_CREDENTIALS environment variable.
client = BetaAnalyticsDataClient()

universityPage_bp = Blueprint('universityPage', __name__)

@universityPage_bp.route('/universityPage', methods=['GET', 'POST'])
def home():
    
    uni_name = request.args.get('uni_name')
    university_id = request.args.get('university_name')

    cursor = mysql.connection.cursor()

    query = "SELECT address, city, state, zipcode, email, phone FROM Universities WHERE uni_name = %s"
    cursor.execute(query, (uni_name,))
    
    result = cursor.fetchone()
    cursor.close()

    if result:
        address, city, state, zipcode, email, phone_number = result
        formatted_address = f"{address}, {city}, {state} {zipcode}"
        API_KEY = 'AIzaSyByc-Nkq0OG7uysLeAzABMVjnPQpOeU1IU'
        return render_template('universityHome.html',university_id= university_id, uni_name=uni_name, address=formatted_address, api_key=API_KEY, email=email, phone=phone_number)
    else:
        return "University not found"
    
@universityPage_bp.route('/universityPage/sports', methods=['GET', 'POST'])
def sports():
    uni_name = request.args.get('uni_name')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT university_id from Universities where uni_name = %s", (uni_name,))
    university_id = cursor.fetchone()  # Fetch one row
   

    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT university_id from Universities where uni_name = %s", (uni_name,))
        university_id = cursor.fetchone()  # Fetch one row

        
        sport_id = request.form.get('sport_id')
        event_name = request.form.get('event_name')
        category = request.form.get('category')
        season = request.form.get('season')
        year = request.form.get('year')
        gender = request.form.get('gender')

        if None in (event_name, category, season, gender):
            return "Missing form data", 400

        query = """
        INSERT INTO Sports (sport_id, event_name, category, season, gender)
    VALUES (%s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    event_name = VALUES(event_name),
    category = VALUES(category),
    season = VALUES(season),
    gender = VALUES(gender)
    """

        query_params = (sport_id, event_name, category, season, gender)
        cursor.execute(query, query_params)
        mysql.connection.commit()

        # Fetch updated sports information after insertion or update
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Sports s JOIN AthleteSports a ON s.sport_id = a.sport_id JOIN AthletesUniversities au ON a.athlete_id = au.athlete_id WHERE au.uni_id = %s",(university_id,))
        sports_info = cursor.fetchall()
        cursor.close()

        return render_template('universitySports.html', uni_name=uni_name, sports_info=sports_info)

    # For GET requests, simply render the template with existing sports information
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Sports s JOIN AthleteSports a ON s.sport_id = a.sport_id JOIN AthletesUniversities au ON a.athlete_id = au.athlete_id WHERE au.uni_id = %s",(university_id,))
    sports_info = cursor.fetchall()
    cursor.close()

    return render_template('universitySports.html', uni_name=uni_name, sports_info=sports_info)


@universityPage_bp.route('/universityPage/athletes', methods=['GET', 'POST'])
def athletes():
    uni_name = request.args.get('uni_name')
    university_id = request.args.get('university_id')
    athletes_info = None  # Initialize athletes_info with a default value

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT university_id from Universities where uni_name = %s", (uni_name,))
    result = cursor.fetchone()  # Fetch one row
    cursor.close()

    if result:
        university_id = result[0]  # Assign university_id from the result
        print("University ID:", university_id)

        # Now use university_id to retrieve athletes_info
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT a.* FROM Athletes a JOIN AthletesUniversities au ON a.athlete_id = au.athlete_id WHERE au.uni_id = %s", (university_id,))
        athletes_info = cursor.fetchall()
        cursor.close()

    if request.method == 'POST':
        # Retrieve form data
        athlete_id = request.form.get('athlete_id')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        gender = request.form.get('gender')
     
        
        # Insert data into the database
        cursor = mysql.connection.cursor()
        query = "INSERT INTO Athletes (athlete_id,  firstName, lastName, gender) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (athlete_id, firstName, lastName, gender))
        mysql.connection.commit()
        cursor.close()

        # Redirect to the same page after POST to avoid form resubmission
        return redirect(url_for('universityPage.athletes', uni_name=uni_name, university_id=university_id, athletes_info=athletes_info))

    # For GET requests or after POST requests, render the template with existing athletes information
    return render_template('universityAthletes.html', university_id=university_id, uni_name=uni_name, athletes_info=athletes_info)

@universityPage_bp.route('/universityPage/faculty', methods=['GET', 'POST'])
def faculty():
    uni_name = request.args.get('uni_name')
    cursor = mysql.connection.cursor()

    query_university_id = "SELECT university_id FROM Universities WHERE uni_name = %s"
    cursor.execute(query_university_id, (uni_name,))
    university_id = cursor.fetchone()[0]  # Fetch the first column of the first row

    
    if request.method == 'POST':
        # Handle form submission here
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
    
        cursor = mysql.connection.cursor()
        query = "INSERT INTO Faculty (university_id, email, password, firstName, lastName) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (university_id, email, password, first_name, last_name))
        mysql.connection.commit()
        cursor.close()
    else:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * from Faculty") 
        result = cursor.fetchall()
        print(result)
    return render_template('universityFaculty.html', uni_name=uni_name, result=result)


@universityPage_bp.route('/universityPage/contact', methods=['GET', 'POST'])
def contact():
    uni_name = request.args.get('uni_name')
    cursor = mysql.connection.cursor()

    query = "SELECT address, city, state, zipcode, email, phone FROM Universities WHERE uni_name = %s"
    cursor.execute(query, (uni_name,))
    
    result = cursor.fetchone()
    cursor.close()

    if result:
        address, city, state, zipcode, email, phone_number = result
        formatted_address = f"{address}, {city}, {state} {zipcode}"
        API_KEY = 'AIzaSyByc-Nkq0OG7uysLeAzABMVjnPQpOeU1IU'
        return render_template('universityHome.html', uni_name=uni_name, address=formatted_address, api_key=API_KEY, email=email, phone=phone_number)
    else:
        return "University not found"
    
@universityPage_bp.route('/university_profile/<uni_name>', methods=['GET', 'POST'])
def university_profile(uni_name):
    cursor = mysql.connection.cursor()

   # Fetch university_id based on the university name
    query_university_id = "SELECT university_id FROM Universities WHERE uni_name = %s"
    cursor.execute(query_university_id, (uni_name,))
    university_id = cursor.fetchone()[0]  # Fetch the first column of the first row

# Fetch data from UniversityProfile table
    query_university_profile = "SELECT * FROM UniversityProfile WHERE uni_id = %s"
    print(query_university_profile)
    cursor.execute(query_university_profile, (university_id,))
    university_profile_data = cursor.fetchall()
    cursor.close()
    
    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name="city")],
        metrics=[Metric(name="activeUsers")],
        date_ranges=[DateRange(start_date="2024-03-31", end_date="today")],
    )
    response = client.run_report(request)
    report_data = []
    for row in response.rows:
        report_data.append({
            'city': row.dimension_values[0].value,
            'active_users': row.metric_values[0].value
        })
    
    return render_template('unipage.html', uni_name=uni_name, university_id=university_id, university_profile_data=university_profile_data, report_data=report_data)