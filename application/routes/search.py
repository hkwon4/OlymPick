from flask import Blueprint, request, render_template, session
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
            A.fullName AS Name,
            A.gender AS Gender,
            S.category AS Category,
            S.event_name AS Event,
            ASp.year AS Year,
            ASp.ranking AS Ranking,
            CASE
                WHEN ASp.ranking = 1 THEN 'Gold'
                WHEN ASp.ranking = 2 THEN 'Silver'
                WHEN ASp.ranking = 3 THEN 'Bronze'
                ELSE NULL
            END AS Medal
        FROM 
            Athletes A
                JOIN 
            AthleteSports ASp ON A.athlete_id = ASp.athlete_id
                JOIN 
            Sports S ON ASp.sport_id = S.sport_id
                JOIN 
            AthletesUniversities AU ON A.athlete_id = AU.athlete_id
                JOIN 
            Universities U ON AU.uni_id = U.university_id
        WHERE 
            U.uni_name = %s
        ORDER BY A.fullName, ASp.year;
        """
        cursor.execute(query, (searchTerm,))

    elif searchFilter == 'Sports':
        # SQL query for 'Sports' search
        query = """
        SELECT
            U.uni_name AS `University`,
            COUNT(DISTINCT S.sport_id) AS `Number of Events`,
            COUNT(DISTINCT A.athlete_id) AS `Number of Athletes`,
            SUM(CASE WHEN ASp.ranking <= 3 THEN 1 ELSE 0 END) AS `Number of Medals`
        FROM 
            Universities U
                JOIN 
            AthletesUniversities AU ON U.university_id = AU.uni_id
                JOIN 
            Athletes A ON AU.athlete_id = A.athlete_id
                JOIN 
            AthleteSports ASp ON A.athlete_id = ASp.athlete_id
                JOIN 
            Sports S ON ASp.sport_id = S.sport_id
        WHERE 
            S.event_name LIKE %s OR S.category LIKE %s
        GROUP BY U.uni_name
        ORDER BY `Number of Medals` DESC, U.uni_name;

        """

        like_term = f"%{searchTerm}%"
        cursor.execute(query, (like_term, like_term))

    elif searchFilter == 'State':
        # SQL query for 'State' search
        query = """
        SELECT
            U.uni_name AS `University`,
            COUNT(DISTINCT S.sport_id) AS `Number of Events`,
            COUNT(DISTINCT A.athlete_id) AS `Number of Athletes`,
            SUM(CASE WHEN ASp.ranking <= 3 THEN 1 ELSE 0 END) AS `Number of Medals`
        FROM 
            Universities U
                JOIN 
            AthletesUniversities AU ON U.university_id = AU.uni_id
                JOIN 
            Athletes A ON AU.athlete_id = A.athlete_id
                JOIN 
            AthleteSports ASp ON A.athlete_id = ASp.athlete_id
                JOIN 
            Sports S ON ASp.sport_id = S.sport_id
        WHERE 
            U.state = %s
        GROUP BY U.uni_name
        ORDER BY `Number of Medals` DESC, U.uni_name;
        """
        cursor.execute(query, (searchTerm,))

    # Fetching results and closing cursor
    result = cursor.fetchall()
    cursor.close()

    # Convert the result to the desired format
    # Convert the result to the desired format
    results_info = []
    if searchFilter == 'University':
        results_info = [{
            'fullName': row[0],
            'gender': row[1],
            'category': row[2],
            'event_name': row[3],
            'Year': row[4],
            'Ranking': row[5],
            'Medal': row[6]
        } for row in result]
    else:  # Applies to 'Sports' and 'State'
        results_info = [{
            'University Name': row[0],
            'Number of Events': row[1],
            'Number of Athletes': row[2],
            'Number of Medals': row[3]
        } for row in result]


    return render_template('results.html', results=results_info, searchTerm=searchTerm, searchFilter=searchFilter, user_id=session.get('user_id'), full_name=session.get('full_name'))