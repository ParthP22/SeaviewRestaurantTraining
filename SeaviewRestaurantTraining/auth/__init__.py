from flask import Blueprint

session_handling_bp = Blueprint("session_handling", __name__, url_prefix="/session_handling")

from . import login