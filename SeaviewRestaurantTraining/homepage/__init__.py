from flask import Blueprint

welcome_bp = Blueprint("welcome", __name__, url_prefix="/welcome")

from . import welcome