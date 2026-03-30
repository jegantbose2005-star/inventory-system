from flask import Flask, render_template, request, redirect, session
import os
import mysql.connector

app = Flask(__name__)
app.secret_key = 'secret123'

db = mysql.connector.connect(
    host=os.getenv("MYSQLHOST", "mysql.railway.internal"),
    user=os.getenv("MYSQLUSER", "root"),
    password=os.getenv("MYSQLPASSWORD"),
    database=os.getenv("MYSQLDATABASE", "railway"),
    port=int(os.getenv("MYSQLPORT", 3306))
)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            session['user'] = user['username']
            return redirect('/dashboard')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as total FROM assets")
    total = cursor.fetchone()['total']

    return render_template('dashboard.html', total=total)


@app.route('/assets')
def assets():
    if 'user' not in session:
        return redirect('/')

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM assets")
    data = cursor.fetchall()
    return render_template('assets.html', assets=data)


@app.route('/add', methods=['GET', 'POST'])
def add_asset():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        name = request.form['name']
        serial = request.form['serial']
        model = request.form['model']

        cursor = db.cursor()
        cursor.execute("INSERT INTO assets (name, serial, model) VALUES (%s, %s, %s)",
                       (name, serial, model))
        db.commit()

        return redirect('/assets')

    return render_template('add_asset.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
