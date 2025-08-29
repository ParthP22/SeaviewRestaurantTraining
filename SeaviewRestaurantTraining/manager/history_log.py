# Author(s): Ahmed Malik
# This file contains the code that is used to view the history log,

from flask import render_template, session, request
import database
from . import manager_bp


@manager_bp.route('/history-log', methods=['GET', 'POST'])
def history_log():
    if session['role'] == 1:
        cursor = database.conn.cursor()
        sort_by = request.args.get('sort', 'ATTEMPT_ID')  # Default sort is by 'ATTEMPT_ID'
        order = request.args.get('order', 'asc')  # Default order
        # Select the relevant data. Join for first and last names since they are not in ATTEMPT_HISTORY_LOG table.
        query = f"""
                SELECT ah.ATTEMPT_ID, ah.EMPLOYEE_ID, e.First_Name, e.Last_Name, ah.QUIZ_ID, ah.DATE_TIME, 
                       (ah.NUM_CORRECT * 1.0 / (ah.NUM_CORRECT + ah.NUM_INCORRECT)) * 100 AS Score 
                FROM ATTEMPT_HISTORY_LOG ah
                JOIN Users e ON ah.EMPLOYEE_ID = e.ID 
                ORDER BY {sort_by} {order}
                """
        cursor.execute(query)
        history_logs = cursor.fetchall()  # Fetching all records from the query execution
        return render_template('manager/history-log.html', history_logs=history_logs, sort_by=sort_by, order=order)
    else:
        return render_template('error/prohibited.html')

