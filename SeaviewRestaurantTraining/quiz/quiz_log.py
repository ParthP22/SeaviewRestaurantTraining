# Author(s): Parth Patel, Ahmed Malik
# This file contains the code that is used to view the quiz history log,


from flask import render_template, session, request
import database
from . import quiz_bp
from enums import Role

@quiz_bp.route('/quiz-log', methods=['GET', 'POST'])
def quiz_log():
    if session['role'] == Role.MANAGER:
        cursor = database.conn.cursor()
        sort_by = request.args.get('sort', 'CHANGE_ID')
        order = request.args.get('order', 'asc')

        cursor.execute(
            f"SELECT log.CHANGE_ID, log.EMPLOYEE_ID, u.FIRST_NAME, u.LAST_NAME, q.QUIZ_ID, q.QUIZ_NAME, log.DATE_TIME, log.ACTION_TYPE "
            f"FROM QUIZ_HISTORY_LOG log, QUIZZES q, USERS u "
            f"WHERE log.QUIZ_ID = q.QUIZ_ID AND log.EMPLOYEE_ID = u.ID "
            f"ORDER BY {sort_by} {order}")
        history_logs = cursor.fetchall()
        return render_template('quiz/quiz-log.html', history_logs=history_logs, sort_by=sort_by, order=order)
    else:
        return render_template('error/prohibited.html')

