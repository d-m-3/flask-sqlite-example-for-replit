from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)


# Create or initialize the database
def init_db():
    try:
        conn = sqlite3.connect('db.db')  # Connect to SQLite database
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                field TEXT NOT NULL
            )
        ''')
        c.execute("INSERT OR IGNORE INTO users (id, name, field) VALUES (1, 'Alice', 'CS')")
        c.execute("INSERT OR IGNORE INTO users (id, name, field) VALUES (2, 'Bob', 'Maths')")
        conn.commit()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


@app.route('/')
def get_users():
    if not os.path.exists('db.db'):
        print("Database file not found. Initializing database...")
        init_db()  # Initialize the database only if needed
    else:
        print("Database file exists. Skipping initialization.")
    conn = sqlite3.connect('db.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    conn.close()
    return render_template('users.html', users=users)


@app.route('/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    conn = sqlite3.connect('db.db')
    c = conn.cursor()

    try:
        if request.method == 'POST':
            # Update user data
            name = request.form.get('name')
            field = request.form.get('field')
            if not name or not field:
                return "Invalid form data", 400  # Bad Request
            c.execute('UPDATE users SET name = ?, field = ? WHERE id = ?', (name, field, user_id))
            conn.commit()
            return redirect(url_for('get_users'))

        # Fetch user data to prefill the form
        c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        if not user:
            return "User not found", 404  # Not Found
        return render_template('edit_user.html', user=user)

    except sqlite3.Error as e:
        return f"Database error: {e}", 500  # Internal Server Error

    finally:
        conn.close()


@app.route('/delete/<int:user_id>', methods=['GET'])
def delete_user(user_id):
    conn = sqlite3.connect('db.db')
    c = conn.cursor()

    try:
        # Delete the user by ID
        c.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        print(f"User with ID {user_id} deleted.")
        return redirect(url_for('get_users'))  # Redirect back to the user list

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return f"Error deleting user: {e}", 500

    finally:
        conn.close()


@app.route('/add', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form.get('name')
        field = request.form.get('field')

        if not name or not field:
            return "Invalid input. Both fields are required.", 400  # Bad Request

        conn = sqlite3.connect('db.db')
        c = conn.cursor()
        try:
            # Insert the new user into the database
            c.execute('INSERT INTO users (name, field) VALUES (?, ?)', (name, field))
            conn.commit()
            print(f"User {name} added to the database.")
            return redirect(url_for('get_users'))  # Redirect to the user list

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return f"Error adding user: {e}", 500  # Internal Server Error

        finally:
            conn.close()

    # Render the add user form for GET requests
    return render_template('add_user.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)