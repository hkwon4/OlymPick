from flask import Blueprint, render_template, request, flash, redirect, url_for, session

inbox_bp = Blueprint('inbox', __name__)

# Dummy inbox data structure to store messages
inbox_data = {}

@inbox_bp.route('/loggedlanding/inbox')
def inbox():
    # Retrieve user information from session or set default values
    user_id = session.get('user_id')
    full_name = session.get('full_name')
    
    # If user information is not found in session, redirect to login page
    if not user_id or not full_name:
        flash('You need to log in first.', 'error')
        return redirect(url_for('auth.login'))
    
    # Retrieve messages for the logged-in user
    user_messages = inbox_data.get(user_id, [])
    
    return render_template('inbox.html', user_id=user_id, full_name=full_name, messages=user_messages)

@inbox_bp.route('/loggedlanding/inbox/send', methods=['POST'])
def send_message():
    # Retrieve user information from session
    user_id = session.get('user_id')
    full_name = session.get('full_name')
    
    # If user information is not found in session, redirect to login page
    if not user_id or not full_name:
        flash('You need to log in first.', 'error')
        return redirect(url_for('auth.login'))
    
    recipient = request.form.get('recipient')
    message = request.form.get('message')
    
    if not recipient or not message:
        flash('Recipient and message are required.', 'error')
    else:
        if recipient not in inbox_data:
            inbox_data[recipient] = []
        inbox_data[recipient].append({'sender': user_id, 'message': message})
        flash('Message sent successfully!', 'success')

    return redirect(url_for('inbox.inbox'))
