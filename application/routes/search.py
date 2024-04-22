from flask import Blueprint, request, render_template
from extensions import mysql

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['POST'])
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
            s.event_name,
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