# Author(s): Ahmed Malik
# This file contains the code that is used to view the users profile page


import re
from flask import Flask, render_template, redirect, url_for, session, request
import database
from routes import website

@website.route('/profile-page', methods=['GET', 'POST'])
def profile_page():
    cursor = database.conn.cursor()
    cursor.execute('SELECT Username, Password, Email, First_Name, Last_Name FROM Users WHERE Username=? AND Password=?', (session['username'], session['password'],))
    user_profile = cursor.fetchone()
    return render_template('profile/profile-page.html', user_profile=user_profile)

