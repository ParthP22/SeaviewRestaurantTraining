from flask import Blueprint

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")

from . import quiz_log, edit_quiz, quiz_material, submit_quiz, take_quiz