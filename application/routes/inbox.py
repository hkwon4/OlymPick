from flask import Blueprint, render_template, request, flash, redirect, url_for, session

inbox_bp = Blueprint('inbox', __name__)

# Dummy inbox data structure to store messages
inbox_data = {}

@inbox_bp.route('/loggedlanding/inbox')
def inbox():
    user_id = request.args.get('user_id')
    full_name = request.args.get('full_name')
    return render_template('inbox.html', user_id=user_id, full_name=full_name)