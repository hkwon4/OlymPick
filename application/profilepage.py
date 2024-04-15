import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import MySQLdb.cursors
import re

app = Flask(__name__)
@app.route('/profilepage')
def profile():
    return render_template('userpage.html')