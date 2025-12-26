from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from datetime import datetime

web_routes = Blueprint('web_routes', __name__)

def init_web_routes(account_repo, car_repo, db):
    @web_routes.route('/')
    def home():
        """Driver stats home page"""
        return render_template('driver_status_home.html')

    @web_routes.route('/schedule_race')
    def schedule_race():
        return render_template('schedule_race.html')

    @web_routes.route('/stats')
    def stats():
        return render_template('stats.html')

    @web_routes.route('/home_logged_in')
    def home_logged_in():
        return render_template('driver_status_logged_in_home.html')

    @web_routes.route('/schedule_race_logged_in')
    def schedule_race_logged_in():
        return render_template('schedule_race_logged_in.html')

    @web_routes.route('/stats_logged_in')
    def stats_logged_in():
        return render_template('logged_in_stats.html')

    @web_routes.route('/personal_stats')
    def personal_stats():
        return render_template('personal_stats.html')

    @web_routes.route('/weather')
    def weather():
        return render_template('weather.html')

    @web_routes.route('/profile')
    def profile():
        user = {
            'email': session['email'],
            'username': session['username'],
            'drivername': session['drivername']
        }
        return render_template('profile.html', user=user)

    @web_routes.route('/garage', methods=['GET', 'POST'])
    def garage():
        cursor = db.cursor(dictionary=True)
        user_driver_name = session.get('drivername')

        # Fetch cars for logged-in user
        cursor.execute(
            "SELECT * FROM Car WHERE car_driver_name = %s ORDER BY car_ID DESC",
            (user_driver_name,)
        )
        cars = cursor.fetchall()

        return render_template('garage.html', cars=cars)

    @web_routes.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('web_routes.home'))

    @web_routes.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['username']
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
                return redirect(url_for('web_routes.home_logged_in'))
            else:
                flash("Invalid email or password.", "danger")
                print("account not found")
                return redirect(url_for('web_routes.login'))

        return render_template('login.html')

    @web_routes.route('/register', methods=['GET', 'POST'])
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
            return redirect(url_for('web_routes.login'))

        return render_template('register.html')