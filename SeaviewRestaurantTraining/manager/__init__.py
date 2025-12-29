from flask import Blueprint

manager_bp = Blueprint("manager", __name__, url_prefix="/manager")

from . import dashboard, history_log, manage_employees, manage_quizzes, quiz_trends, send_reports