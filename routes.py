import secrets
from flask import Flask, render_template

website = Flask(__name__)
def create_secret_key(length=32):
    return secrets.token_hex(length)

website.secret_key = create_secret_key()

from session_handling import *
from announcements import *
from manage_employees import *
from manage_quizzes import *
from history_log import *
from profile_page import *
from quiz_log import *
from edit_profile import *
from quiz_trends import *
from send_reports import *

@website.route('/')
def Welcome():
    return render_template('welcome.html')