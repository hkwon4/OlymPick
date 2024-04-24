from flask import Blueprint, request, render_template, current_app
from werkzeug.utils import secure_filename
from extensions import mysql

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            return "No file uploaded", 400
        
        filename = secure_filename(file.filename)
        mimetype = file.mimetype
        img = file.read()
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO file (img, mimetype, name) VALUES (%s, %s, %s)", (img, mimetype, filename))
        current_app.config['MYSQL'].connection.commit()
        cursor.close()
        
        return "Image uploaded successfully!"
    
    return render_template('upload.html')