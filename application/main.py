import os
import sys
from flask import Flask
from routes.landing import landing_bp
from routes.profile import profile_bp
from routes.upload import upload_bp
from routes.login import login_bp
from routes.register import register_bp
from routes.about import about_bp
from routes.search import search_bp
from routes.inbox import inbox_bp
from routes.universityPage import universityPage_bp
from routes.chat import chat_bp
from extensions import mysql, socketio

app = Flask(__name__)

app.secret_key = 'your_secret_key_here'

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'yu942u'
app.config['MYSQL_PASSWORD'] = 'Test!234'
app.config['MYSQL_DB'] = 'team5_db_test'

mysql.init_app(app)
socketio.init_app(app)

# Register blueprints
app.register_blueprint(landing_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(about_bp)
app.register_blueprint(search_bp)
app.register_blueprint(inbox_bp)
app.register_blueprint(universityPage_bp)
app.register_blueprint(chat_bp)

if __name__ == '__main__':
<<<<<<< HEAD
    app.run(debug=True,port=5001)


=======
    socketio.run(app, debug=True)
>>>>>>> d6fc35ffc9daa3c35b12411872fefa48ccf44e30
