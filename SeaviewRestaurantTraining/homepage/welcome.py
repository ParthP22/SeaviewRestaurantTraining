from flask import render_template
from . import welcome_bp

@welcome_bp.route('/')
def welcome():
    return render_template('index.html')