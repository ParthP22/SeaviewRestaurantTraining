import secrets
from flask import Flask, render_template

website = Flask(__name__)
def create_secret_key(length=32):
    return secrets.token_hex(length)

website.secret_key = create_secret_key()

from SeaviewRestaurantTraining.auth.session_handling import *
from SeaviewRestaurantTraining.announcement.announcements import *
from SeaviewRestaurantTraining.manager.manage_employees import *
from SeaviewRestaurantTraining.manager.manage_quizzes import *
from SeaviewRestaurantTraining.manager.history_log import *
from SeaviewRestaurantTraining.profile.profile_page import *
from SeaviewRestaurantTraining.quiz.quiz_log import *
from SeaviewRestaurantTraining.profile.edit_profile import *
from SeaviewRestaurantTraining.manager.quiz_trends import *
from SeaviewRestaurantTraining.manager.send_reports import *

@website.route('/')
def Welcome():
    return render_template('index.html')