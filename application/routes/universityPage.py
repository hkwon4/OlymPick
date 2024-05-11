from flask import Blueprint, request, render_template, session, redirect, url_for
import MySQLdb.cursors
from extensions import mysql

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

    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        
        sport_id = request.form.get('sport_id')
        event_name = request.form.get('event_name')
        category = request.form.get('category')
        season = request.form.get('season')
        year = request.form.get('year')
        gender = request.form.get('gender')

        if None in (event_name, category, season, year, gender):
            return "Missing form data", 400

        query = """
        INSERT INTO Sports (event_name, category, season, year, gender)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        event_name = VALUES(event_name),
        category = VALUES(category),
        season = VALUES(season),
        year = VALUES(year),
        gender = VALUES(gender)
        """

        query_params = (event_name, category, season, year, gender)
        cursor.execute(query, query_params)
        mysql.connection.commit()
        cursor.close()

        # Fetch updated sports information after insertion or update
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM Sports")
        sports_info = cursor.fetchall()
        cursor.close()

        return render_template('universitySports.html', uni_name=uni_name, sports_info=sports_info)

    # For GET requests, simply render the template with existing sports information
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Sports")
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
        cursor.execute("SELECT * FROM Athletes WHERE uni_id = %s", (university_id,))
        athletes_info = cursor.fetchall()
        print(athletes_info)
        cursor.close()

    if request.method == 'POST':
        # Retrieve form data
        sport_id = request.form.get('sport_id')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        gender = request.form.get('gender')
        no_medals = request.form.get('no_medals')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        # Insert data into the database
        cursor = mysql.connection.cursor()
        query = "INSERT INTO Athletes (uni_id,sport_id,  firstName, lastName, gender, no_medals, start_date, end_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (university_id, sport_id, firstName, lastName, gender, no_medals, start_date, end_date))
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


    return render_template('unipage.html', uni_name=uni_name, university_id=university_id, university_profile_data=university_profile_data)