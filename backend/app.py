from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)  # ✅ FIXED: name instead of name
CORS(app)

# Database Configuration
db_config = {
    'host': '34.61.89.248',  # mysql database public-ip
    'user': 'test',
    'password': 'admin@123',
    'database': 'dev'
}

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(**db_config)

# 1️⃣ Get all users
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

# 2️⃣ Get user by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

# 3️⃣ Add a new user
@app.route('/users/add', methods=['POST'])
def add_user():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    if not name or not email:
        return jsonify({'error': 'Name and Email are required'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", (name, email))
        conn.commit()
        return jsonify({'message': 'User added successfully'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# 4️⃣ Update user by ID
@app.route('/users/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    name = data.get('name')
    email = data.get('email')
    if not name or not email:
        return jsonify({'error': 'Name and Email are required'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    if not cursor.fetchone():
        return jsonify({'error': 'User not found'}), 404
    try:
        cursor.execute("UPDATE users SET name = %s, email = %s WHERE id = %s", (name, email, user_id))
        conn.commit()
        return jsonify({'message': 'User updated successfully'})
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# 5️⃣ Delete user by ID
@app.route('/users/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    if not cursor.fetchone():
        return jsonify({'error': 'User not found'}), 404
    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return jsonify({'message': 'User deleted successfully'})
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# Serve HTML home page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>User API</title></head>
<body>
  <h2>Welcome to the Flask User API</h2>
  <p>Use endpoints like /users, /users/add, etc. with Postman or curl.</p>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# ✅ Correct entry point
if __name__ == '__main__':  # ✅ FIXED
    app.run(host='0.0.0.0', port=5000, debug=True)  # ✅ FIXED
