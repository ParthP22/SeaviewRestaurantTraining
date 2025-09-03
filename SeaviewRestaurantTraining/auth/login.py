# Author(s): Pranjal Singh, Parth Patel
# This file contains the code that handles a user's session, such as login, logout
# and authenticating the user.


from flask import render_template, redirect, url_for, session, request
import database
from . import auth_bp
from SeaviewRestaurantTraining.enums import AccountStatus, Role

# Simply shows the login page
@auth_bp.route('/show-login')
def show_login():
    return render_template('login.html')

# Handles the actual login functionality once the form
# on the login page is submitted
@auth_bp.route('/login', methods=['GET','POST'])
def login():
    # Initialize message variable
    msg = ''

    # Create variables for easy access
    username = request.form['username']
    password = request.form['password']

    # Check if account exists using SQLite
    cursor = database.conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE Username=? AND Password=?', (username, password,))
    account = cursor.fetchone()

    # If account exists in the database
    if account:

        # Update all session variables with the new session
        session['id'] = account[0]
        session['logged_in'] = True
        session['username'] = username
        session['password'] = password
        session['role'] = account[6]
        session['restricted'] = account[8]

        # If the account is restricted, then return to login page with
        # message.
        if session['restricted'] == AccountStatus.RESTRICTED.value:
            msg = 'Account is restricted'
            return render_template('login.html', msg=msg)

        # After successful login, redirect to manager dashboard if
        # the user is a manager
        if session['role'] == Role.MANAGER.value:
            return redirect(url_for('manager.authenticate_manager'))
        # Else, the user is an employee, so redirect to employee dashboard
        else:
            return redirect(url_for('employee.authenticate_employee'))
        
    # Else, the account doesn't exist, so return to login page
    else:
        msg = 'Incorrect username/password!'
        return render_template('login.html', msg=msg)

# Handle log out functionality
@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    
    # Clear all the variables that were set in the session
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('password', None)
    session.pop('id', None)
    session.pop('role', None)
    session.pop('restricted', None)

    # Return to the welcome page
    return redirect(url_for('homepage.welcome'))

# Verify the role of the user and redirect them to their respective
# dashboard
@auth_bp.route('/verify-role', methods=['GET', 'POST'])
def verify_role():

    # Check if the user is logged in
    if session['logged_in'] == True:

        # Return them to their respective dashboard based on their role
        if session['role'] == Role.MANAGER.value:
            return redirect(url_for('manager.authenticate_manager'))
        else:
            return redirect(url_for('employee.authenticate_employee'))
