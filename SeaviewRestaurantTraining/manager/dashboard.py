from flask import render_template, redirect, url_for, session, request
import SeaviewRestaurantTraining.employee.certificate as certificate
import database
from routes import website
from . import manager_bp

@manager_bp.route('/dashboard', methods=['GET', 'POST'])
def authenticate_manager():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    account = None
    cursor = database.conn.cursor()
    if 'logged_in' in session and session['logged_in']:
        cursor.execute('SELECT * FROM Users WHERE Username=? AND Password=?', (session['username'], session['password']))
        account = cursor.fetchone()
        if account and account[6] == 1:
            return render_template('manager/manager-dashboard.html')

    # Show the login form with message (if any)
    return redirect(url_for('auth.login'))