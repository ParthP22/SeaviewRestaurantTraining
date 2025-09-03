# Author(s): Ryan Minneo, Ryan Nguyen
# This file contains the code that is used to manage quizzes,
# such as being able to register new quizzes, edit existing quizzes, and delete quizzes if need be.
import base64
import datetime
from flask import render_template, redirect, url_for, session, request
import database
import SeaviewRestaurantTraining.manager.send_reports as send_reports
from . import manager_bp
from enums import Role

@manager_bp.route('/manage-quizzes')
def manage_quizzes():
    if session['role'] == Role.MANAGER:
        cursor = database.conn.cursor()

        current_datetime = datetime.datetime.now()
        formatted_current_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%S")

        cursor.execute('SELECT * FROM QUIZZES')
        quizzes = cursor.fetchall()
        return render_template('manager/manage-quizzes.html', quizzes = quizzes, current_date = formatted_current_datetime)
    else:
        return render_template('error/prohibited.html')

@manager_bp.route('/delete-quiz/<int:quiz_id>', methods=['GET'])
def delete_quiz_route(quiz_id):
    cursor = database.conn.cursor()
    cursor.execute("UPDATE QUIZZES SET IS_DELETED = 1 WHERE QUIZ_ID=?", (quiz_id,))

    # cursor.execute("SELECT MAX(CHANGE_NUMBER) FROM QUIZ_HISTORY_LOG WHERE EMPLOYEE_ID=? AND QUIZ_ID=?",
    #                (session['id'], quiz_id))
    #
    # recent_change = cursor.fetchone()
    # curr_change = 1
    # if recent_change[0] is not None:
    #     curr_change = recent_change[0] + 1
    # else:
    #     curr_change = 1

    cursor.execute(
        'INSERT INTO QUIZ_HISTORY_LOG(CHANGE_ID, EMPLOYEE_ID, QUIZ_ID, DATE_TIME, ACTION_TYPE)'
        'VALUES(?,?,?,?,?)', (None, session['id'], quiz_id, datetime.datetime.now(), 'DELETE'))

    database.conn.commit()

    return redirect(url_for('manager.manage_quizzes'))

@manager_bp.route('/edit-quiz/<int:quiz_id>', methods=['GET'])
def edit_quiz_route(quiz_id):
    cursor = database.conn.cursor()
    cursor.execute("UPDATE QUIZZES SET IS_DELETED = 1 WHERE QUIZ_ID=?", (quiz_id,))

    cursor.execute(
        'INSERT INTO QUIZ_HISTORY_LOG(CHANGE_ID, EMPLOYEE_ID, QUIZ_ID, DATE_TIME, ACTION_TYPE)'
        'VALUES(?,?,?,?,?)', (None, session['id'], quiz_id, datetime.datetime.now(), 'DELETE'))

    database.conn.commit()

    return redirect(url_for('manager.manage_quizzes'))
