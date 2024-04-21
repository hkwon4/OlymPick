from flask import Blueprint, render_template, request

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/loggedlanding/profilepage')
def profile():
    user_id = request.args.get('user_id')
    full_name = request.args.get('full_name')
    return render_template('userpage.html', user_id=user_id, full_name=full_name)