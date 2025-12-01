from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
import requests
 

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

# ----------------------------
# DRIVER DATA
# ----------------------------
driver_stats = [
    {"driver": "Ninel Benitez", "event_date": "2024-10-18", "car_class": "STX", "raw_time": 55.23, "pax_index": 0.801, "penalties": 2},
    {"driver": "Ava Smith", "event_date": "2024-09-22", "car_class": "GS", "raw_time": 54.89, "pax_index": 0.785, "penalties": 0},
    {"driver": "Thaleina Cruz", "event_date": "2024-08-12", "car_class": "DS", "raw_time": 56.02, "pax_index": 0.796, "penalties": 1},
    {"driver": "Carlos Martinez", "event_date": "2024-07-18", "car_class": "STR", "raw_time": 53.44, "pax_index": 0.799, "penalties": 0},
    {"driver": "Brianna Lopez", "event_date": "2024-07-18", "car_class": "HS", "raw_time": 58.91, "pax_index": 0.795, "penalties": 1},
    {"driver": "Marcus Green", "event_date": "2024-06-14", "car_class": "SS", "raw_time": 51.28, "pax_index": 0.812, "penalties": 0},
    {"driver": "Ethan Miller", "event_date": "2024-06-14", "car_class": "GS", "raw_time": 52.30, "pax_index": 0.785, "penalties": 0},
    {"driver": "Olivia Johnson", "event_date": "2024-06-14", "car_class": "ES", "raw_time": 59.72, "pax_index": 0.798, "penalties": 1},
    {"driver": "Daniel Reyes", "event_date": "2024-05-20", "car_class": "STU", "raw_time": 57.19, "pax_index": 0.801, "penalties": 0},
    {"driver": "Sofia Alvarez", "event_date": "2024-05-20", "car_class": "HS", "raw_time": 60.44, "pax_index": 0.795, "penalties": 1},
    {"driver": "Mason Wright", "event_date": "2024-04-10", "car_class": "STS", "raw_time": 55.80, "pax_index": 0.802, "penalties": 0},
    {"driver": "Isabella Flores", "event_date": "2024-04-10", "car_class": "GS", "raw_time": 58.20, "pax_index": 0.785, "penalties": 2},
]


# ----------------------------
# WEATHER LOOKUP FUNCTION
# ----------------------------
def lookup_weather(date):
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude=40.5142&longitude=-88.9906"
        f"&start_date={date}&end_date={date}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode"
        "&timezone=America/Chicago"
    )

    try:
        res = requests.get(url, timeout=10).json()
        if "daily" not in res:
            return {"high": None, "low": None, "precip": None, "conditions": "N/A"}

        d = res["daily"]

        high = round((d["temperature_2m_max"][0] * 9/5) + 32, 1)
        low = round((d["temperature_2m_min"][0] * 9/5) + 32, 1)
        precip = d["precipitation_sum"][0]

        code_map = {
            0: "Clear ☀️",
            2: "Partly Cloudy ⛅",
            3: "Overcast ☁️",
            61: "Light Rain 🌧",
            63: "Moderate Rain 🌧",
            65: "Heavy Rain 🌧🌧"
        }

        cond = code_map.get(d["weathercode"][0], "Unknown")

        return {
            "high": high,
            "low": low,
            "precip": precip,
            "conditions": cond
        }

    except:
        return {"high": None, "low": None, "precip": None, "conditions": "N/A"}


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
    cursor = db.cursor(dictionary=True)
    user_driver_name = session.get('drivername')

    cursor.execute(
        "SELECT * FROM Car WHERE car_driver_name = %s ORDER BY car_ID DESC LIMIT 1", (user_driver_name,)
    )

    latest_car = cursor.fetchone()
    cursor.close()

    return render_template('driver_status_logged_in_home.html', latest_car=latest_car)

@app.route('/schedule_race_logged_in')
def schedule_race_logged_in():
    return render_template('schedule_race_logged_in.html')

@app.route('/stats_logged_in')
def stats_logged_in():
    stats_with_weather = []

    for stat in driver_stats:
        weather = lookup_weather(stat["event_date"])

        raw = stat["raw_time"]
        pax = round(raw * stat["pax_index"], 2)
        final = round(raw + stat["penalties"] * 2, 2)

        stats_with_weather.append({
            "driver": stat["driver"],
            "event_date": stat["event_date"],
            "car_class": stat["car_class"],
            "raw_time": raw,
            "pax_time": pax,
            "penalties": stat["penalties"],
            "final_time": final,
            "high_temp": weather["high"],
            "low_temp": weather["low"],
            "precip": weather["precip"],
            "conditions": weather["conditions"]
        })


    # FASTEST CALCULATIONS
    fastest_raw = min(stats_with_weather, key=lambda x: x["raw_time"])
    fastest_pax = min(stats_with_weather, key=lambda x: x["pax_time"])

    return render_template(
        "stats_logged_in.html",
        data=stats_with_weather,
        fastest_raw=fastest_raw,
        fastest_pax=fastest_pax
    )


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


@app.route('/garage/delete_car/<int:car_id>', methods=['POST'])
def delete_car(car_id):
    cursor = db.cursor()
    car_driver_name = session.get('drivername')
    cursor.execute(
        "SELECT car_driver_name FROM Car WHERE car_id = %s", (car_id,)
    )
   
    result = cursor.fetchone()
    if  result and result[0] == car_driver_name:
        flash(" Car Deleted", "Success")
        cursor.execute(
            "DELETE FROM Car WHERE car_id = %s",(car_id,)
        )
        db.commit()
    else:
        flash("You are not authorized to delete this car.", "unsuccessful")
    
    cursor.close()
    return redirect(url_for('garage'))

# -------------------------
# RUN FLASK
# -------------------------
if __name__ == '__main__':
    app.run(debug=True)

