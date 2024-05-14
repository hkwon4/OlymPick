from flask import Blueprint, render_template, request, session
from flask_socketio import join_room, leave_room, emit
from extensions import socketio, mysql

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat/<int:chatroom_id>')
def chat(chatroom_id):
    user_id = session['user_id']
    cursor = mysql.connection.cursor()

    # Fetch chat partner's name
    cursor.execute("""
        SELECT 
            CASE 
                WHEN c.user1_id = %s THEN CONCAT(u2.firstName, ' ', u2.lastName)
                ELSE CONCAT(u1.firstName, ' ', u1.lastName)
            END AS chat_partner_name
        FROM ChatRooms c
        JOIN Users u1 ON c.user1_id = u1.user_id
        JOIN Users u2 ON c.user2_id = u2.user_id
        WHERE c.chatroom_id = %s
    """, (user_id, chatroom_id))
    chat_partner_name = cursor.fetchone()[0]

    # Fetch messages for the chatroom
    cursor.execute("""
        SELECT 
            m.sender_id, 
            CONCAT(u.firstName, ' ', u.lastName) AS sender_name, 
            m.message_content AS content,
            m.status
        FROM Messages m
        JOIN Users u ON m.sender_id = u.user_id
        WHERE m.chatroom_id = %s
        ORDER BY m.message_id
    """, (chatroom_id,))
    messages = cursor.fetchall()

    messages = [
        {
            'sender_id': row[0], 
            'sender_name': row[1], 
            'content': row[2],
            'status': row[3]
        }
        for row in messages
    ]

    # Mark unread messages as read
    cursor.execute("""
        UPDATE Messages 
        SET status = 1 
        WHERE chatroom_id = %s AND receiver_id = %s AND status = 0
    """, (chatroom_id, user_id))
    mysql.connection.commit()

    cursor.close()

    return render_template('chat.html', chatroom_id=chatroom_id, chat_partner_name=chat_partner_name, messages=messages)


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('status', {'msg': username + ' has entered the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    emit('status', {'msg': username + ' has left the room.'}, room=room)

@socketio.on('message')
def on_message(data):
    chatroom_id = data['chatroom_id']
    sender_id = data['sender_id']
    content = data['content']
    sender_name = data['sender_name']
    room = data['room']

    # Determine the receiver_id based on the chatroom's users and the sender_id
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT user1_id, user2_id FROM ChatRooms WHERE chatroom_id = %s", (chatroom_id,))
    result = cursor.fetchone()
    user1_id, user2_id = result
    receiver_id = user2_id if sender_id == user1_id else user1_id
    

    # Save message to the database
    cursor.execute("INSERT INTO Messages (chatroom_id, sender_id, receiver_id, message_content) VALUES (%s, %s, %s, %s)",
                   (chatroom_id, sender_id, receiver_id, content))
    mysql.connection.commit()
    cursor.close()
    
    
    # Emit the message to the chatroom
    emit('message', {
        'sender_id': sender_id,
        'sender_name': sender_name,
        'content': content
    }, room=room)