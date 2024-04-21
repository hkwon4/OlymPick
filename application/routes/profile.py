from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import base64
from datetime import datetime
import pytz
from extensions import mysql

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/loggedlanding/<int:user_id>/<string:full_name>/profilepage', methods=["GET"])
def profile(user_id, full_name):
    # Retrieve the latest uploaded profile picture for the user from the database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT file_data FROM UserProfileImg WHERE user_id = %s ORDER BY uploaded_at DESC LIMIT 1", [user_id])
    result = cursor.fetchone()
    cursor.close()

    if result:
        file_data = result[0]
        profile_picture = base64.b64encode(file_data).decode('utf-8')
    else:
        profile_picture = None

    return render_template('userpage.html', user_id=user_id, full_name=full_name, profile_picture=profile_picture)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

@profile_bp.route('/loggedlanding/<int:user_id>/<string:full_name>/profilepage', methods=["POST"])
def uploadprofile(user_id, full_name):
    if request.method == 'POST':
        files = request.files.getlist('files[]')
        for file in files:
            if file:
                file_extension = file.filename.rsplit('.', 1)[1].lower()
                if file_extension in ALLOWED_EXTENSIONS:
                    first_name = session['firstname']
                    # Generate the new filename using user_id
                    filename = f"pfp_{first_name}{user_id}.{file_extension}"
                    file_data = file.read()
                    current_timestamp = datetime.now(pytz.timezone('America/Los_Angeles')).strftime('%Y-%m-%d %H:%M:%S')

                    cursor = mysql.connection.cursor()
                    cursor.execute("INSERT INTO UserProfileImg (user_id, file_name, file_data, uploaded_at) VALUES (%s, %s, %s, %s)", [user_id, filename, file_data, current_timestamp])
                    mysql.connection.commit()
                    cursor.close()
                else:
                    flash('Invalid file extension. Allowed extensions: png, jpg, jpeg, gif')
                    return redirect(url_for('profile.profile', user_id=user_id, full_name=full_name))

        flash('Profile updated successfully.')
        return redirect(url_for('profile.profile', user_id=user_id, full_name=full_name))