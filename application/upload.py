import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import MySQLdb.cursors
import re
import bcrypt

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'yu942u'
app.config['MYSQL_PASSWORD'] = 'Test!234'
app.config['MYSQL_DB'] = 'team5_db'

mysql = MySQL(app)


@app.route('/upload', methods=['GET', 'POST'])
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
        mysql.connection.commit()
        cursor.close()

        return "Image uploaded successfully!"

    return render_template('upload.html')