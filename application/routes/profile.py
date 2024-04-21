from flask import Blueprint, render_template

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profilepage')
def profile():
    return render_template('userpage.html')