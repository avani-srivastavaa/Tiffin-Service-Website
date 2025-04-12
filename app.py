from flask import Flask, render_template, request, redirect, url_for,  flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'Avani@123'  # Add any random string here


# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'         # Your MySQL username
app.config['MYSQL_PASSWORD'] = 'Ambadnya@108'         # Your MySQL password
app.config['MYSQL_DB'] = 'swadisht'       # Your database name

mysql = MySQL(app)

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
        # Get form data
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

        # Insert into DB
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO users (name, email, phone, region, gender, address, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, email, phone, region, gender, address, password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('home'))  # Redirect to home or login
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE name = %s", (username,))
        user = cur.fetchone()
        cur.close()

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
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE name = %s", (username,))
        user = cur.fetchone()  # Get the user data

        cur.close()

        return render_template('profile.html', user=user)
    else:
        flash('Please log in first!', 'error')
        return redirect('/login')


@app.route('/order-now', methods=['POST'])
def order_now():
    if 'loggedin' not in session:
        return redirect('/login')

    import json
    cart = json.loads(request.form['cart'])
    user_id = session['user_id']

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT name, phone, email, address FROM users WHERE id = %s", (user_id,))
    user_details = cur.fetchone()
    cur.close()
    return render_template('order_now.html', cart=cart, customer=user_details)

@app.route('/go-back', methods=['POST'])
def go_back():
    return render_template('main.html')


if __name__ == '__main__':
    app.run(debug=True)
