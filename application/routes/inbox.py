from flask import Blueprint, render_template, request, session, redirect, url_for
from extensions import mysql

inbox_bp = Blueprint('inbox', __name__)

@inbox_bp.route('/loggedlanding/inbox')
def inbox():
    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    # Fetch distinct chat rooms with unread message counts
    cursor.execute("""
        SELECT
            c.chatroom_id,
            CASE
                WHEN c.user1_id = %s THEN u2.user_id
                ELSE u1.user_id
            END AS chat_partner_id,
            CASE
                WHEN c.user1_id = %s THEN CONCAT(u2.firstName, ' ', u2.lastName)
                ELSE CONCAT(u1.firstName, ' ', u1.lastName)
            END AS chat_partner_name,
            (
                SELECT COUNT(*)
                FROM Messages m
                WHERE m.chatroom_id = c.chatroom_id AND m.receiver_id = %s AND m.status = 0
            ) AS unread_count
        FROM ChatRooms c
        JOIN Users u1 ON c.user1_id = u1.user_id
        JOIN Users u2 ON c.user2_id = u2.user_id
        WHERE %s IN (c.user1_id, c.user2_id)
    """, (user_id, user_id, user_id, user_id))
    chatrooms = cursor.fetchall()

    chatrooms = [
        {'chatroom_id': row[0], 'chat_partner_id': row[1], 'chat_partner_name': row[2], 'unread_count': row[3]}
        for row in chatrooms
    ]

    return render_template('inbox.html', chatrooms=chatrooms)



@inbox_bp.route('/loggedlanding/inbox/send', methods=['POST'])
def send_message():
    sender_id = session['user_id']
    recipient_email = request.form['recipient']
    message_content = request.form['message']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT user_id FROM Users WHERE email = %s", (recipient_email,))
    result = cursor.fetchone()
    if result:
        receiver_id = result[0]
        # Check if a chatroom already exists for the two users
        cursor.execute("SELECT chatroom_id FROM ChatRooms WHERE (user1_id = %s AND user2_id = %s) OR (user1_id = %s AND user2_id = %s)",
                       (sender_id, receiver_id, receiver_id, sender_id))
        chatroom = cursor.fetchone()
        if chatroom:
            chatroom_id = chatroom[0]
        else:
            # Create a new chatroom
            cursor.execute("INSERT INTO ChatRooms (user1_id, user2_id) VALUES (%s, %s)",
                           (sender_id, receiver_id))
            chatroom_id = cursor.lastrowid
        # Insert the message into the Messages table
        cursor.execute("INSERT INTO Messages (chatroom_id, sender_id, receiver_id, message_content) VALUES (%s, %s, %s, %s)",
                       (chatroom_id, sender_id, receiver_id, message_content))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('inbox.inbox'))
    else:
        cursor.close()
        return "Recipient not found"