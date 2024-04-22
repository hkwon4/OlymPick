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