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
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM UserProfile WHERE user_id = %s", [user_id])
            existing_about_me_count = cursor.fetchone()[0]
            if existing_about_me_count > 0:
                # If the user already has an about me record, update it with the new content
                cursor.execute("UPDATE UserProfile SET aboutMe = %s WHERE user_id = %s", (about_me, user_id))
            else:
                # If the user does not have an existing about me record, insert a new one
                cursor.execute("INSERT INTO UserProfile (user_id, aboutMe) VALUES (%s, %s)", (user_id, about_me))
            mysql.connection.commit()
            cursor.close()

        userlink = request.form.get('link_url')
        if userlink:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM UserLinks WHERE user_id = %s", [user_id])
            existing_links_count = cursor.fetchone()[0]
            if existing_links_count > 0:
                # If the user already has links, update them with the new content
                cursor.execute("UPDATE UserLinks SET link_url = %s WHERE user_id = %s", (userlink, user_id))
            else:
                # If the user does not have existing links, insert new ones
                cursor.execute("INSERT INTO UserLinks (user_id, link_url) VALUES (%s, %s)", (user_id, userlink))
            mysql.connection.commit()
            cursor.close()

        return redirect(url_for('profile.profile', user_id=user_id, full_name=full_name))


@profile_bp.route('/loggedlanding/<string:uni_name>/uploadprofile', methods=["GET"])
def uniprofile(uni_name):

    cursor = mysql.connection.cursor()

    # Fetch university_id based on the university name
    query_university_id = "SELECT university_id FROM Universities WHERE uni_name = %s"
    cursor.execute(query_university_id, (uni_name,))
    university_id = cursor.fetchone()[0]  # Fetch the first column of the first row

    # Retrieve university profile data from the database
    cursor.execute("SELECT * FROM UniversityProfile WHERE uni_id = %s", (university_id,))
    university_profile_data = cursor.fetchone()

    cursor.close()
    return render_template('unipage.html',  university_id=university_id, uni_name=uni_name,university_profile_data=university_profile_data)

@profile_bp.route('/loggedlanding/<int:university_id>/<string:uni_name>/uploadprofile', methods=["POST"])
def uniuploadprofile(university_id, uni_name):
    # Handle other profile details, like programs and contact info
    programs = request.form.get('programs')
    contactInfo = request.form.get('contactInfo')
    coachingStaff = request.form.get('coachingStaff')
    facilities = request.form.get('facilities')

    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM UniversityProfile WHERE uni_id = %s", (university_id,))
    existing_data = cursor.fetchone()

    # Combine existing data with new data
    if existing_data:
        existing_programs = existing_data[1]
        existing_contact_info = existing_data[2]
        existing_coaching_staff = existing_data[3]
        existing_facilities = existing_data[4]
        
        # Append new data to existing data
        combined_programs = existing_programs + ', ' + programs
        combined_contact_info = existing_contact_info + ', ' + contactInfo
        combined_coaching_staff = existing_coaching_staff + ', ' + coachingStaff
        combined_facilities = existing_facilities + ', ' + facilities
        
        # Update database with combined data
        cursor.execute("UPDATE UniversityProfile SET programs = %s, contactInfo = %s, coachingStaff = %s, facilities = %s WHERE uni_id = %s", 
                       (combined_programs, combined_contact_info, combined_coaching_staff, combined_facilities, university_id))
        
    else:
        # Insert new record into the database
        cursor.execute("INSERT INTO UniversityProfile (uni_id, programs, contactInfo, coachingStaff, facilities) VALUES (%s, %s, %s, %s, %s)", 
                       (university_id, programs, contactInfo, coachingStaff, facilities))

    # Commit changes to the database
    mysql.connection.commit()
    cursor.close()
        
    # Redirect to uniprofile route without passing additional parameters
    return render_template('universityHome.html',university_id= university_id, uni_name=uni_name)

@profile_bp.route('/loggedlanding/<int:university_id>/<string:uni_name>', methods=["GET"])
def uniloggedlanding(university_id, uni_name):
    cursor = mysql.connection.cursor()

    # Retrieve university profile data from the database
    cursor.execute("SELECT * FROM UniversityProfile WHERE uni_id = %s", (university_id,))
    UniversityProfile = cursor.fetchone()

    cursor.close()

    # Pass the retrieved data to the template context
    return render_template('uniloggedlanding.html', university_id=university_id, uni_name=uni_name, UniversityProfile=UniversityProfile)
