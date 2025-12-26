from flask import Flask, render_template, request, redirect, url_for, flash, session
from classes.SchedulePageScrapper import get_schedule
from datetime import datetime
import mysql.connector
import requests
import re

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


@app.route('/add_data', methods=['GET', 'POST'])
def add_data():
    if request.method == 'POST':
        driver = request.form['driver']
        event_date_str = request.form['event_date']  # e.g., "2025-10-18"
        car_class = request.form['car_class']
        raw_time = request.form['raw_time']
        pax_time = request.form['pax_time']
        penalties = request.form['penalties']
        final_time = request.form['final_time']
        high_temp = request.form['high_temp']
        low_temp = request.form['low_temp']
        precip = request.form['precip']
        conditions = request.form['conditions']
 
 
        # Ensure event_date is in proper date object (optional)
        event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
 
 
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO Results
            (driver, event_date, car_class, raw_time, pax_time, penalties, final_time, high_temp, low_temp, precip, conditions)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (driver, event_date, car_class, raw_time, pax_time, penalties, final_time, high_temp, low_temp, precip, conditions))
        db.commit()
        cursor.close()
 
 
        return redirect(url_for('stats_logged_in'))
    return render_template('add_data.html')



@app.route('/')
def home():


    events = get_schedule()
    most_recent_event = None

    if events:
        today = datetime.now()


        closest_event = None
        min_diff = None

        for event in events:
            try:
                date_str = event.get("date", "")
                if date_str and date_str != "" and date_str != "Dates not found":
                    year_match = re.search(r', (\d{4})$', date_str)
                    if not year_match:
                        continue

                    year = year_match.group(1)
                    
                    first_date_part = date_str.split("&")[0].strip()

                    if not re.search(r'\d{4}', first_date_part):
                        first_date_part = f"{first_date_part}, {year}"

                    event_date = datetime.strptime(first_date_part, "%B %d, %Y")

                    diff = abs((event_date - today).days)
                    print(f"  -> Parsed date: {event_date.strftime('%B %d, %Y')} | Diff: {diff} days")


                    if min_diff is None or diff < min_diff:
                        min_diff = diff
                        closest_event = event
                       
            except ValueError as e:
            
                continue

        most_recent_event = closest_event
        if most_recent_event:
            print(f"\n=== FINAL: Closest event is '{most_recent_event.get('name')}' ===\n")

            


    return render_template('driver_status_home.html', 
                         most_recent_event=most_recent_event)


@app.route('/schedule_race')
def schedule_race():
    events = get_schedule()
    return render_template('schedule_race.html', events=events)

@app.route('/stats')
def stats():
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            driver,
            event_date,
            car_class,
            raw_time,
            pax_time,
            penalties,
            final_time,
            high_temp,
            low_temp,
            precip,
            conditions
        FROM Results
        ORDER BY event_date DESC, driver ASC
    """)

    results = cursor.fetchall()
    cursor.close()

    stats_with_weather = []
    for stat in results:

        final_time = stat["final_time"]
        if final_time == 0:
            final_time = stat["raw_time"] + (stat["penalties"] * 2)
        

        stats_with_weather.append({
            "driver": stat["driver"],
            "event_date": stat["event_date"].strftime("%Y-%m-%d"), 
            "car_class": stat["car_class"],
            "raw_time": float(stat["raw_time"]),
            "pax_time": float(stat["pax_time"]),
            "penalties": stat["penalties"],
            "final_time": float(final_time),
            "high_temp": stat["high_temp"],
            "low_temp": stat["low_temp"],
            "precip": stat["precip"],
            "conditions": stat["conditions"]
        })

        if stats_with_weather:
            fastest_raw = min(stats_with_weather, key=lambda x: x["raw_time"])
            fastest_pax = min(stats_with_weather, key=lambda x: x["pax_time"])
        else:
            fastest_raw = fastest_pax = None
    return render_template(
        "stats.html",
        data=stats_with_weather,
        fastest_raw=fastest_raw,
        fastest_pax=fastest_pax
    )

@app.route('/home_logged_in')
def home_logged_in():
    cursor = db.cursor(dictionary=True)
    user_driver_name = session.get('drivername')

    cursor.execute(
        "SELECT * FROM Car WHERE car_driver_name = %s ORDER BY car_ID DESC LIMIT 1", (user_driver_name,)
    )

    latest_car = cursor.fetchone()
    cursor.close()

    events = get_schedule()
    most_recent_event = None

    if events:
        today = datetime.now()
        print(f"\n=== DEBUG: Finding closest event to {today.strftime('%B %d, %Y')} ===")


        closest_event = None
        min_diff = None

        for event in events:
            try:
                date_str = event.get("date", "")
                if date_str and date_str != "" and date_str != "Dates not found":
                    year_match = re.search(r', (\d{4})$', date_str)
                    if not year_match:
                        continue

                    year = year_match.group(1)
                    
                    first_date_part = date_str.split("&")[0].strip()

                    if not re.search(r'\d{4}', first_date_part):
                        first_date_part = f"{first_date_part}, {year}"

                    event_date = datetime.strptime(first_date_part, "%B %d, %Y")

                    diff = abs((event_date - today).days)
                    print(f"  -> Parsed date: {event_date.strftime('%B %d, %Y')} | Diff: {diff} days")


                    if min_diff is None or diff < min_diff:
                        min_diff = diff
                        closest_event = event
                        print(f"  -> NEW CLOSEST EVENT!")
            except ValueError as e:
                print(f"  -> ERROR parsing date: {e}")
                continue

        most_recent_event = closest_event
        if most_recent_event:
            print(f"\n=== FINAL: Closest event is '{most_recent_event.get('name')}' ===\n")

            


    return render_template('driver_status_logged_in_home.html', 
                         latest_car=latest_car, 
                         most_recent_event=most_recent_event)

@app.route('/schedule_race_logged_in')
def schedule_race_logged_in():
    events = get_schedule()
    return render_template('schedule_race_logged_in.html', events=events)


@app.route('/stats_logged_in')
def stats_logged_in():
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            driver,
            event_date,
            car_class,
            raw_time,
            pax_time,
            penalties,
            final_time,
            high_temp,
            low_temp,
            precip,
            conditions
        FROM Results
        ORDER BY event_date DESC, driver ASC
    """)

    results = cursor.fetchall()
    cursor.close()

    stats_with_weather = []
    for stat in results:

        final_time = stat["final_time"]
        if final_time == 0:
            final_time = stat["raw_time"] + (stat["penalties"] * 2)
        

        stats_with_weather.append({
            "driver": stat["driver"],
            "event_date": stat["event_date"].strftime("%Y-%m-%d"),  # Convert date to string
            "car_class": stat["car_class"],
            "raw_time": float(stat["raw_time"]),
            "pax_time": float(stat["pax_time"]),
            "penalties": stat["penalties"],
            "final_time": float(final_time),
            "high_temp": stat["high_temp"],
            "low_temp": stat["low_temp"],
            "precip": stat["precip"],
            "conditions": stat["conditions"]
        })

        if stats_with_weather:
            fastest_raw = min(stats_with_weather, key=lambda x: x["raw_time"])
            fastest_pax = min(stats_with_weather, key=lambda x: x["pax_time"])
        else:
            fastest_raw = fastest_pax = None
    return render_template(
        "stats_logged_in.html",
        data=stats_with_weather,
        fastest_raw=fastest_raw,
        fastest_pax=fastest_pax
    )

  

@app.route('/personal_stats')
def personal_stats():
    cursor = db.cursor()
    
    user_driver_name = session.get('drivername')

    query = """Select DISTINCT P.session_id, P.personal_best, TP.best_time, W.name, W.date, W.high, W.low, W.link
from 
		(Select min(spd.sp_pax_time) as personal_best, spd.event_session_id as session_id
		from Session_PAX_Data spd
			join Car c
				on c.car_id = spd.car_id 
		where c.car_driver_name = (%s)
		group by spd.event_session_id) as P
		JOIN 
			(Select min(spd.sp_pax_time) as best_time, spd.event_session_id as session_id
			from Session_PAX_Data spd
				join Car c
					on c.car_id = spd.car_id
			group by spd.event_session_id) as TP
		on P.session_id = TP.session_id
		JOIN 
		(Select e.event_name as name, es.evt_session_date as date, wd.high_temp as high, wd.low_temp as low, wd.day_icon as link, spd.event_session_id as session_id 
	from Session_PAX_Data spd
		join Car c
			on c.car_id = spd.car_id
		join Weather_Data wd 
			on wd.event_session_id = spd.event_session_id
		join Event_Session es 
			on es.event_session_id = wd.event_session_id 
		join Event e
			on e.event_id = es.event_id 
	where c.car_driver_name = (%s)) as W
	on TP.session_id = W.session_id
	Order by W.date ASC;"""

    cursor.execute(query,(user_driver_name,user_driver_name))

    response = cursor.fetchall()

    dict = {}
    for row in response:
        event_name = row[3]
        if event_name not in dict.keys():
            dict[event_name] = []
        
        dict[event_name].append([row[1],row[2],row[4].strftime(r'%m/%d/%Y'),row[5],row[6],row[7]])



    return render_template('personal_stats.html',event_data=dict)

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




