from flask import render_template, redirect, url_for, session
from .certificate import generate_certificate
import database
import datetime
from . import employee_bp

def render_employee_dashboard(account, cursor):
    cursor.execute('SELECT NUM_CORRECT, NUM_INCORRECT, MAX(ATTEMPT_NUMBER) '
                   'FROM ATTEMPT_HISTORY_LOG '
                   'WHERE EMPLOYEE_ID=? AND QUIZ_ID IN (SELECT QUIZ_ID FROM QUIZZES WHERE IS_DELETED=0)'
                   'GROUP BY QUIZ_ID',
                   (account[0],))

    recent_attempts = cursor.fetchall()
    total_correct = 0
    total_questions = 0

    cursor.execute('SELECT TOTAL_QUESTIONS FROM QUIZZES WHERE IS_DELETED IS NOT 1 ')
    query = cursor.fetchall()

    if query is not None:
        for row in query:
            total_questions += row[0]
    # cursor.execute('SELECT QUIZ_ID FROM QUIZZES')
    # total_quizzes = cursor.fetchall()
    # total_correct = 0
    # total_questions = 0
    # if total_quizzes is not NoneType:
    #     for quiz in total_quizzes:
    #         cursor.execute(
    #             'SELECT NUM_CORRECT, NUM_INCORRECT, MAX(ATTEMPT_NUMBER) FROM ATTEMPT_HISTORY_LOG WHERE EMPLOYEE_ID=? AND QUIZ_ID=?',
    #             (account[0], quiz[0]))
    #         progress = cursor.fetchone()
    #         total_correct += progress[0]
    #         total_questions += progress[0] + progress[1]


    if recent_attempts is not None:
        for attempt in recent_attempts:
            total_correct += attempt[0]

    if total_questions == 0:
        percent = 0
    else:
        percent = total_correct / total_questions * 100
        percent = round(percent, 2)

    cursor.execute('SELECT * FROM QUIZZES WHERE QUIZ_ID NOT IN '
                   '(SELECT DISTINCT QUIZ_ID FROM ATTEMPT_HISTORY_LOG WHERE IS_COMPLETED=1 AND EMPLOYEE_ID=?) ', (session['id'],))
    quizzes = cursor.fetchall()

    cursor.execute('SELECT QUIZ_ID, QUIZ_NAME FROM QUIZZES WHERE IS_DELETED IS NOT 1 ')

    quiz_list = []

    for _, quiz in cursor.fetchall():
        if quiz is not None:
            quiz_list.append(quiz)



    cursor.execute('SELECT NUM_CORRECT, NUM_INCORRECT, MAX(ATTEMPT_NUMBER) '
                   'FROM ATTEMPT_HISTORY_LOG '
                   'WHERE EMPLOYEE_ID=? AND QUIZ_ID IN (SELECT DISTINCT QUIZ_ID FROM QUIZZES WHERE IS_DELETED IS NOT 1) '
                   'GROUP BY QUIZ_ID ', (session['id'],))

    num_correct = []
    num_incorrect = []
    for correct, incorrect, _ in cursor.fetchall():
        if correct is not None:
            num_correct.append(correct)
        else:
            num_correct.append(0)
        if incorrect is not None:
            num_incorrect.append(incorrect)
        else:
            num_incorrect.append(0)

    current_datetime = datetime.datetime.now()
    formatted_current_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    return render_template('employee/employee-dashboard.html', progress=total_correct, total_questions=total_questions, quizzes=quizzes, percent=percent, num_correct=num_correct, num_incorrect=num_incorrect, quiz_list=quiz_list, current_date = formatted_current_datetime)

@employee_bp.route('/dashboard', methods=['GET', 'POST'])
def authenticate_employee():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    account = None
    cursor = database.conn.cursor()
    if 'logged_in' in session and session['logged_in']:
        cursor.execute('SELECT * FROM Users WHERE Username=? AND Password=?', (session['username'], session['password']))
        account = cursor.fetchone()
        if account and account[6] == 2:
            cursor.execute('SELECT IS_COMPLETED FROM USERS WHERE ID=? ', (session['id'],))
            query = cursor.fetchone()
            is_completed = query[0]
            if is_completed == 0:
                generate_certificate()
            return render_employee_dashboard(account, cursor)

    # Show the login form with message (if any)
    return redirect(url_for('login'))


