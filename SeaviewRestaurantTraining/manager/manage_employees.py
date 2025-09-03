# Author(s): Pranjal Singh, Parth Patel, Ahmed Malik
# This file contains the code that is used to manage employee accounts,
# such as being able to register new employees.

import re
import sqlite3
from flask import render_template, redirect, url_for, session, request
import database
from . import manager_bp
from SeaviewRestaurantTraining.enums import Role

@manager_bp.route('/register-employee')
def register_employee():
    if session['role'] == Role.MANAGER:
        cursor = database.conn.cursor()

        cursor.execute('SELECT * FROM Roles ')
        roles = cursor.fetchall()

        cursor.execute('SELECT ID, FIRST_NAME, LAST_NAME '
                       'FROM USERS '
                       'WHERE ROLE_ID = 1 ')
        managers = cursor.fetchall()
        print(managers)

        return render_template('manager/register-employee.html', roles=roles, managers=managers)
    else:
        return render_template('error/prohibited.html')

@manager_bp.route('/manage-employee')
def manage_employee():
    if session['role'] == Role.MANAGER:
        cursor = database.conn.cursor()

        cursor.execute('SELECT u.ID, u.USERNAME, u.FIRST_NAME || \' \' || u.LAST_NAME, u.EMAIL, r.ROLE_NAME, u.MANAGER_ID, m.FIRST_NAME || \' \' || m.LAST_NAME '
                       'FROM Users u JOIN Roles r ON u.ROLE_ID = r.ID LEFT JOIN Users m  ON u.MANAGER_ID = m.ID')
        users = cursor.fetchall()

        return render_template('manager/manage-employee.html', users = users)
    else:
        return render_template('error/prohibited.html')


@manager_bp.route('/registration', methods=['GET', 'POST'])
def registration():
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form\
    and 'first_name' in request.form and 'last_name' in request.form:
        # Create variables for easy access
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role_id = request.form.get('role')
        isRestricted = 0

        cursor = database.conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE Username=?', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email or role_id == '0':
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO Users (username, first_name, last_name, password, email, role_id, IsRestricted) VALUES ( ?, ?, ?, ?, ?, ?, ?)',
                           (username, first_name, last_name, password, email, role_id, isRestricted))
            database.conn.commit()
            msg = 'You have successfully registered!'

            cursor.execute(
                'SELECT u.ID, u.USERNAME, u.FIRST_NAME || \' \' || u.LAST_NAME, u.EMAIL, r.ROLE_NAME, u.MANAGER_ID, m.FIRST_NAME || \' \' || m.LAST_NAME '
                'FROM Users u JOIN Roles r ON u.ROLE_ID = r.ID LEFT JOIN Users m  ON u.MANAGER_ID = m.ID')
            users = cursor.fetchall()
            return render_template('manager/manage-employee.html', users=users)


    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    cursor.execute('SELECT * FROM Roles ')
    roles = cursor.fetchall()
    return render_template('manager/register-employee.html', roles=roles, msg=msg)


@manager_bp.route('/delete/<int:item_id>', methods=['GET'])
def delete_user(item_id):
    cursor = database.conn.cursor()
    cursor.execute("DELETE FROM Users WHERE id=?", (item_id,))
    database.conn.commit()
    return redirect(url_for('manager.manage_employee'))

@manager_bp.route('/restrict/<int:item_id>', methods=['GET'])
def restrict_user(item_id):
    cursor = database.conn.cursor()
    value = 1
    cursor.execute("UPDATE Users SET IsRestricted = ? WHERE id = ?", (value, item_id,))
    database.conn.commit()
    return redirect(url_for('manager.manage_employee'))    

@manager_bp.route('/edit-employee/<int:item_id>', methods=['GET', 'POST'])
def edit_employee(item_id):
    cursor = database.conn.cursor()
    # If it's a POST request, update the role
    if request.method == 'POST':
        new_role_id = request.form.get('role')
        new_manager_id = request.form.get('manager')
        if new_manager_id == 'None':
            new_manager_id = None
        cursor.execute("UPDATE Users SET ROLE_ID = ?, MANAGER_ID = ? WHERE ID = ?", (new_role_id, new_manager_id, item_id))

        database.conn.commit()
        print(new_role_id)
        if new_role_id == '2' and item_id == session['id']:
            return redirect(url_for('auth.logout'))

        else:
            return redirect(url_for('manager.manage_employee'))

    # For a GET request, show the edit form with current role
    cursor.execute('SELECT DISTINCT u.ROLE_ID, r.ROLE_NAME '
                   'FROM USERS u JOIN ROLES r ON u.ROLE_ID = r.ID '
                   'WHERE ROLE_ID IN '
                   '    (SELECT ROLE_ID '
                   '    FROM USERS '
                   '    WHERE ID = ?) ', (item_id,))

    curr_role = cursor.fetchone()

    cursor.execute('SELECT DISTINCT u.ROLE_ID, r.ROLE_NAME '
                   'FROM USERS u JOIN ROLES r ON u.ROLE_ID = r.ID '
                   'WHERE ROLE_ID NOT IN'
                   '    (SELECT ROLE_ID'
                   '    FROM USERS'
                   '    WHERE ID = ?) ', (item_id,))

    other_role = cursor.fetchone()

    roles = []
    roles.append(curr_role)
    roles.append(other_role)


    you = None
    if session['role'] == 1:
        cursor.execute('SELECT ID, FIRST_NAME || \' \' || LAST_NAME AS NAME '
                       'FROM USERS '
                       'WHERE ID = ?', (item_id,))
        you = cursor.fetchone()

    cursor.execute('SELECT ID, FIRST_NAME || \' \' || LAST_NAME AS NAME '
                   'FROM USERS '
                   'WHERE ROLE_ID = 1')
    query = cursor.fetchall()
    managers = query
    managers.append((None, None))


    cursor.execute('SELECT e.MANAGER_ID, m.FIRST_NAME || \' \' || m.LAST_NAME AS NAME '
                   'FROM USERS e JOIN USERS m ON e.MANAGER_ID = m.ID '
                   'WHERE e.ID = ? ', (item_id,))
    curr_manager = cursor.fetchone()

    if curr_manager is None:
        curr_manager = (None, None)

    if curr_manager in managers:
        managers.remove(curr_manager)

    if you is not None and you in managers:
        managers.remove(you)

    managers.insert(0,curr_manager)

    return render_template('manager/edit-employee.html', curr_role_id=curr_role[0], curr_manager_id=curr_manager[0], roles=roles, managers=managers, user_id=item_id)

