from flask import Blueprint, request, render_template, session
import MySQLdb.cursors
from extensions import mysql

universityPage_bp = Blueprint('universityPage', __name__)

@universityPage_bp.route('/universityPage', methods=['GET', 'POST'])
def home():
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
    

@universityPage_bp.route('/universityPage/sports', methods=['GET', 'POST'])
def sports():
    uni_name = request.args.get('uni_name')
    return render_template('universitySports.html', uni_name=uni_name)


@universityPage_bp.route('/universityPage/athletes', methods=['GET', 'POST'])
def athletes():
    uni_name = request.args.get('uni_name')
    return render_template('universityAthletes.html', uni_name=uni_name)


@universityPage_bp.route('/universityPage/faculty', methods=['GET', 'POST'])
def faculty():
    uni_name = request.args.get('uni_name')
    return render_template('universityFaculty.html', uni_name=uni_name)


@universityPage_bp.route('/universityPage/contact', methods=['GET', 'POST'])
def contact():
    uni_name = request.args.get('uni_name')
    return render_template('universityContact.html', uni_name=uni_name)