from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Needed for flash messages

# -------------------------
# MySQL connection
# -------------------------
db = mysql.connector.connect(
    host="10.111.21.71",          # VM IP over VPN
    user="admin",                 # admin can connect remotely
    password="admin#ab12cd34",
    database="ccsccDB"
)

# -------------------------
# ROUTES
# -------------------------

@app.route('/')
def home():
    """Driver stats home page"""
    return render_template('driver_status_home.html')

@app.route('/schedule_race')
def schedule_race():
    return render_template('schedule_race.html')

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/home_logged_in')
def home_logged_in():
    return render_template('driver_status_logged_in_home.html')

@app.route('/schedule_race_logged_in')
def schedule_race_logged_in():
    return render_template('schedule_race_logged_in.html')

@app.route('/stats_logged_in')
def stats_logged_in():
    return render_template('logged_in_stats.html')

@app.route('/personal_stats')
def personal_stats():
    return render_template('personal_stats.html')

@app.route('/weather')
def weather():
    return render_template('weather.html')

@app.route('/profile')
def profile():
    user = {
        'email': session['email'],
        'username': session['username'],
        'drivername': session['drivername']
    }
    return render_template('profile.html', user=user)

'''
@app.route('/garage')
def garage():
    cursor = db.cursor(dictionary=True)
    user_driver_name = session.get('drivername')  # consistent key
     # fetch cars for logged-in user
    cursor.execute(
        "SELECT * FROM Car WHERE car_driver_name = %s ORDER BY car_ID DESC",
        (user_driver_name,)
    )
    cars = cursor.fetchall()

    return render_template('garage.html')
'''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login form submission"""
    if request.method == 'POST':
        email = request.form['username']  # matches HTML input name
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute("SELECT verify_login(%s, %s)", (email, password))
        result = cursor.fetchone()

        if result and result[0]:  # True if login successful
            flash("Login successful!", "success")
            print("account found")
            return redirect(url_for('home_logged_in'))  # redirect to driver_status_home page
        else:
            flash("Invalid email or password.", "danger")
            print("account not found")
            return redirect(url_for('login'))

    # GET request → show login page
    return render_template('login.html')

'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']  # form input for email
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute("SELECT verify_login(%s, %s)", (email, password))
        result = cursor.fetchone()

        if result and result[0]:  # True if login successful
            # Fetch the user's details from Account table
            cursor.execute("SELECT act_email, act_username, act_drivername FROM Account WHERE act_email = %s", (email,))
            user = cursor.fetchone()

            # Store info in Flask session (NOT password)
            session['email'] = user[0]
            session['username'] = user[1]
            session['drivername'] = user[2]

            flash("Login successful!", "success")
            print("account found")
            return redirect(url_for('home_logged_in'))
        else:
            flash("Invalid email or password.", "danger")
            print("account not found")
            return redirect(url_for('login'))

    return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle account creation form submission"""
    if request.method == 'POST':
        username = request.form['username']
        drivername = request.form['drivername']
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor()
        cursor.callproc('create_account', (username, drivername, email, password))
        db.commit()

        flash("Account created (if email was unique). Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/garage', methods=['GET', 'POST'])
def garage():
    cursor = db.cursor(dictionary=True)
    user_driver_name = session.get('drivername')

    if request.method == 'POST':
        car_year = request.form['car_year']
        car_make = request.form['car_make']
        car_model = request.form['car_model']
        wheelbase = request.form.get('wheelbase', None)
        mods = request.form.get('mods', None)
        tire_description = request.form.get('tire_description', None)
        weight = request.form.get('weight', None)

        cursor.callproc('add_car', (
            user_driver_name, car_year, car_make, car_model,
            wheelbase, mods, tire_description, weight
        ))
        db.commit()
        flash("Car successfully added!", "success")

    # Fetch cars for logged-in user
    cursor.execute(
        "SELECT * FROM Car WHERE car_driver_name = %s ORDER BY car_ID DESC",
        (user_driver_name,)
    )
    cars = cursor.fetchall()

    return render_template('garage.html', cars=cars)



# -------------------------
# RUN FLASK
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)
