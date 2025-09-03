from flask import render_template, redirect, url_for, session
from .certificate import generate_certificate
import database
import datetime
from . import employee_bp
from SeaviewRestaurantTraining.enums import Role

# This calculates the data that will be used in the progress bar at
# the top of the employee dashboard
def calculate_progress_bar(account,cursor):
    # Obtain all the current records of the user's attempts on quizzes
    # for all quizzes that have not been deleted.
    cursor.execute('SELECT NUM_CORRECT, NUM_INCORRECT, MAX(ATTEMPT_NUMBER) '
                   'FROM ATTEMPT_HISTORY_LOG '
                   'WHERE EMPLOYEE_ID=? AND QUIZ_ID IN (SELECT QUIZ_ID FROM QUIZZES WHERE IS_DELETED=0)'
                   'GROUP BY QUIZ_ID',
                   (account[0],))

    recent_attempts = cursor.fetchall()
    total_correct = 0
    total_questions = 0

    # Get all the questions from the quizzes that have not been deleted
    cursor.execute('SELECT TOTAL_QUESTIONS FROM QUIZZES WHERE IS_DELETED IS NOT 1 ')
    query = cursor.fetchall()

    # Count the total number of questions across all existing quizzes
    if query is not None:
        for row in query:
            total_questions += row[0]

    # Count the total number of correct answers that the employee has 
    # answered across all existing quizzes
    if recent_attempts is not None:
        for attempt in recent_attempts:
            total_correct += attempt[0]

    # If there are no quizzes with questions, let the percentage be 0
    # (Note: we have to do this, because we don't want to accidentally 
    # divide by 0)
    if total_questions == 0:
        return total_correct, total_questions, 0
    
    # Calculate the percentage that the employee has gotten correct over
    # all quizzes 
    else:
        percent = total_correct / total_questions * 100
        percent = round(percent, 2)
        return total_correct, total_questions, percent
    
# Computes all data needed by ChartJS for the bar graph displayed on the
# employee dashboard which shows the employee's current progress
def compute_data_for_graph(cursor):
    # Obtain all quizzes that have not been deleted and add them to the quiz_list
    # (this will be displayed on the chart on the employee dashboard)
    cursor.execute('SELECT QUIZ_NAME FROM QUIZZES WHERE IS_DELETED IS NOT 1 ')
    quiz_list = []
    for quiz in cursor.fetchall():
        if quiz is not None:
            quiz_list.append(quiz)

    # Obtain the most recent attempt for each existing quiz that the employee has completed
    cursor.execute('SELECT NUM_CORRECT, NUM_INCORRECT, MAX(ATTEMPT_NUMBER) '
                   'FROM ATTEMPT_HISTORY_LOG '
                   'WHERE EMPLOYEE_ID=? AND QUIZ_ID IN (SELECT DISTINCT QUIZ_ID FROM QUIZZES WHERE IS_DELETED IS NOT 1) '
                   'GROUP BY QUIZ_ID ', (session['id'],))

    # Create lists of the numbeer of correct and incorrect answers by this employee for each
    # existing quiz so that it can be displayed on the bar graph
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
    
    return quiz_list, num_correct, num_incorrect

# Gathers all data for the remaining list of quizzes that are displayed on the
# left-hand side of the employee dashboard
def remaining_quizzes_list(cursor):
    # Obtain all quizzes that have not yet been completed by the employee
    # (this will be displayed along the side of the employee dashboard)
    cursor.execute('SELECT * FROM QUIZZES WHERE QUIZ_ID NOT IN '
                   '(SELECT DISTINCT QUIZ_ID FROM ATTEMPT_HISTORY_LOG WHERE IS_COMPLETED=1 AND EMPLOYEE_ID=?) ', (session['id'],))
    quizzes = cursor.fetchall()

    # Get the current time (this will be used to see if the employee is past the due date or not)
    current_datetime = datetime.datetime.now()
    formatted_current_datetime = current_datetime.strftime("%Y-%m-%dT%H:%M:%S")

    return quizzes, formatted_current_datetime

# Helper function to carry out rendering the employee dashboard
def render_employee_dashboard(account, cursor):

    # Note to self: as of right now (9/3/2025) the span tag in employee-dashboard.html that
    # uses this percent variable has been commented out, so I made remove this variable
    # entirely in the future.
    percent_complete, total_correct, total_questions = calculate_progress_bar(account,cursor)

    quiz_list, num_correct, num_incorrect = compute_data_for_graph(cursor)

    quizzes, current_date = remaining_quizzes_list(cursor)

    return render_template('employee/employee-dashboard.html', progress=total_correct, total_questions=total_questions, quizzes=quizzes, percent=percent_complete, num_correct=num_correct, num_incorrect=num_incorrect, quiz_list=quiz_list, current_date = current_date)

# Route the employee to the dashboard
@employee_bp.route('/dashboard', methods=['GET', 'POST'])
def authenticate_employee():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    account = None
    cursor = database.conn.cursor()
    if 'logged_in' in session and session['logged_in']:
        cursor.execute('SELECT * FROM Users WHERE Username=? AND Password=?', (session['username'], session['password']))
        account = cursor.fetchone()
        if account and account[6] == Role.EMPLOYEE.value:
            cursor.execute('SELECT IS_COMPLETED FROM USERS WHERE ID=? ', (session['id'],))
            query = cursor.fetchone()
            is_completed = query[0]
            if is_completed == 0:
                generate_certificate()
            return render_employee_dashboard(account, cursor)

    # Show the login form with message (if any)
    return redirect(url_for('auth.login'))


