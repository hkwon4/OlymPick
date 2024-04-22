from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import base64
from datetime import datetime
import pytz
from extensions import mysql

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/loggedlanding/<int:user_id>/<string:full_name>/profilepage', methods=["GET"])
def profile(user_id, full_name):
    cursor = mysql.connection.cursor()

    # Retrieve the latest uploaded profile picture for the user from the database
    cursor.execute("SELECT file_data FROM UserProfileImg WHERE user_id = %s ORDER BY uploaded_at DESC LIMIT 1", [user_id])
    result = cursor.fetchone()
    profile_picture = None
    if result:
        file_data = result[0]
        profile_picture = base64.b64encode(file_data).decode('utf-8')

    # Retrieve the about me information for the user from the database
    cursor.execute("SELECT aboutMe FROM UserProfile WHERE user_id = %s", [user_id])
    about_me_result = cursor.fetchone()
    about_me = about_me_result[0] if about_me_result else None

    try:
        cursor.execute("SELECT link_url FROM UserLinks WHERE user_id = %s", [user_id])
        userlink_result = cursor.fetchone()
        userlink = userlink_result[0] if userlink_result else None
    except Exception as e:
        print("Error fetching user links:", e)
        userlink = None

    print(userlink)

    cursor.close()

    return render_template('userpage.html', user_id=user_id, full_name=full_name, profile_picture=profile_picture, about_me=about_me, userlink=userlink)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

@profile_bp.route('/loggedlanding/<int:user_id>/<string:full_name>/profilepage', methods=["POST"])
def uploadprofile(user_id, full_name):
    print("hello")
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

        about_me = request.form.get('aboutMe')
        if about_me:
            # Check if the user already has an existing about me record
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT aboutMe FROM UserProfile WHERE user_id = %s", [user_id])
            existing_about_me_result = cursor.fetchone()
            if existing_about_me_result:
                # If the user already has an about me record, update it with the new content
                existing_about_me = existing_about_me_result[0]
                about_me = existing_about_me + "\n" + about_me  # Append new about me to the existing one
                cursor.execute("UPDATE UserProfile SET aboutMe = %s WHERE user_id = %s", (about_me, user_id))
            else:
                # If the user does not have an existing about me record, insert a new one
                cursor.execute("INSERT INTO UserProfile (user_id, aboutMe) VALUES (%s, %s)", (user_id, about_me))
            mysql.connection.commit()
            cursor.close()

        

#'UserLinks - link_id, user_id, link_type, link_url'

        # Handle user links
        userlink = request.form.get('link_url')
        if userlink:
            
        # Check if the user already has existing links
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT link_url FROM UserLinks WHERE user_id = %s", [user_id])
            existing_links_result = cursor.fetchone()
            if existing_links_result:
            # If the user already has links, update them with the new content
                existing_links = existing_links_result[0]
                userlink = existing_links + "\n" + userlink  # Append new links to the existing ones
                cursor.execute("UPDATE UserLinks SET link_url = %s WHERE user_id = %s", (userlink, user_id))
            else:
            # If the user does not have existing links, insert new ones
                cursor.execute("INSERT INTO UserLinks (user_id, link_url) VALUES (%s, %s)", (user_id, userlink))
            mysql.connection.commit()
            cursor.close()
            
        flash('Profile updated successfully.')
        return redirect(url_for('profile.profile', user_id=user_id, full_name=full_name))