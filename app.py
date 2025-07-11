from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2
import psycopg2.extras
from urllib.parse import urlparse
import os
import json

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

# PostgreSQL Configuration
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

@app.route('/')
def home():
    return render_template('main.html', username=session.get('username'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        region = request.form['region']
        gender = request.form['gender']
        address = request.form['address']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']

        if password != confirm_password:
            return "Passwords do not match!"

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (name, email, phone, region, gender, address, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, email, phone, region, gender, address, password))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users WHERE name = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            if password == user['password']:
                session['loggedin'] = True
                session['username'] = user['name']
                session['user_id'] = user['id']
                flash('Logged in successfully!', 'success')
                return redirect('/')
            else:
                flash('Wrong password!', 'error')
        else:
            flash('User not found!', 'error')

    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        username = session['username']
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users WHERE name = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return render_template('profile.html', user=user)
    else:
        flash('Please log in first!', 'error')
        return redirect('/login')

@app.route('/order-now', methods=['POST'])
def order_now():
    if 'loggedin' not in session:
        return redirect('/login')

    cart = json.loads(request.form['cart'])
    user_id = session['user_id']

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT name, phone, email, address FROM users WHERE id = %s", (user_id,))
    user_details = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('order_now.html', cart=cart, customer=user_details)

@app.route('/go-back', methods=['POST'])
def go_back():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True)
