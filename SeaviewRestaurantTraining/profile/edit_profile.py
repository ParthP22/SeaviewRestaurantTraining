# Author(s): Ahmed Malik
# This file contains the code that is used to edit the users profile page

from flask import render_template, redirect, url_for, session, request, flash
import database
from routes import website
from . import profile_bp

@profile_bp.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        # This block will run when the form is submitted
        username = request.form.get('username')
        first_name = request.form.get('first-name')
        last_name = request.form.get('last-name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Update user data in database
        cursor = database.conn.cursor()
        cursor.execute(
            'UPDATE Users SET Username = ?, First_Name = ?, Last_Name = ?, Email = ?, Password = ? WHERE ID = ?',
            (username, first_name, last_name, email, password, session['id'])
        )
        database.conn.commit()
        session['password'] = password
        session['username'] = username


        flash('Profile updated successfully.')
        return redirect(url_for('profile_page'))

    # This block will run for a GET request, displaying the form
    # Optionally, you can pre-fill the form based on current user data
    return render_template('profile/edit-profile.html')

