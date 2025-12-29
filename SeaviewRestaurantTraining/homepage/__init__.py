from flask import Blueprint

welcome_bp = Blueprint("homepage", __name__, url_prefix="/welcome")

from . import welcome