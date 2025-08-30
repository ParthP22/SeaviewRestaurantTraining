import base64
import datetime
from flask import render_template, redirect, url_for, session, request
import database
from . import quiz_bp

@quiz_bp.route('/submit-quiz', methods=['GET', 'POST'])
def submit_quiz():
    if request.method == 'POST' and session['role'] == 2:
        quiz_id = request.form.get('quiz_id')

        cursor = database.conn.cursor()
        cursor.execute("SELECT * FROM questions WHERE quiz_id = ?", (quiz_id,))
        questions = cursor.fetchall()

        cursor.execute("SELECT MAX(ATTEMPT_ID) FROM ATTEMPT_HISTORY_LOG ")
        query = cursor.fetchone()
        latest_attempt_id = 0
        if query[0] is not None:
            latest_attempt_id = query[0]

        #Creates an array of inputted answers. You don't even need this to be honest, but if you want all the answers in one array, here ya go
        inputtedAnswers = {}
        totalCorrect = 0
        totalIncorrect = 0
        cursor = database.conn.cursor()

        cursor.execute("SELECT MAX(ATTEMPT_NUMBER) FROM ATTEMPT_HISTORY_LOG WHERE EMPLOYEE_ID=? AND QUIZ_ID=?",
                       (session['id'], quiz_id))
        # curr_attempt = (0 if cursor.fetchone() is None else cursor.fetchone()[0]) + 1
        recent_attempt = cursor.fetchone()
        if recent_attempt[0] is not None:
            curr_attempt = recent_attempt[0] + 1
        else:
            curr_attempt = 1

        # Goes through each question in the quiz and checks them against the correct answer for each problem.
        for question in questions:
            question_id = question[0]
            inputAnswer = request.form.get('question_' + str(question_id))
            inputtedAnswers[question_id] = inputAnswer
            prev_result = (0,0)
            cursor.execute('SELECT IS_CORRECT FROM RESULTS WHERE ATTEMPT_ID=? AND EMPLOYEE_ID=? AND QUESTION_ID=? ', (latest_attempt_id,session['id'],question_id,))
            query = cursor.fetchone()
            if query is not None:
                if query[0] == 1:
                    prev_result = (1,0)
                    print(prev_result)
                else:
                    prev_result = (0,1)
                    print(prev_result)

            if inputAnswer == question[7]:
                #print("correct!") # This can be deleted, I was just testing it.

                totalCorrect += 1
                cursor.execute("UPDATE QUESTIONS SET NUM_CORRECT = NUM_CORRECT + 1 - ? WHERE QUESTION_ID=?", (prev_result[0],(question_id),))
                cursor.execute("UPDATE QUESTIONS SET NUM_INCORRECT = NUM_INCORRECT - ? WHERE QUESTION_ID=?",
                               (prev_result[1], (question_id),))

                # Records the submission for this question on this specific attempt into the RESULTS table
                print(f"{latest_attempt_id + 1} {session['id']} {quiz_id} {question_id} {question[7]}")
                cursor.execute('INSERT INTO RESULTS(ATTEMPT_ID,EMPLOYEE_ID,QUIZ_ID,QUESTION_ID,ANSWER,IS_CORRECT)'
                               'VALUES(?,?,?,?,?,?) ', (latest_attempt_id+1, session['id'], quiz_id,question_id,inputAnswer,1))
            else:
                totalIncorrect += 1
                cursor.execute("UPDATE QUESTIONS SET NUM_CORRECT = NUM_CORRECT - ? WHERE QUESTION_ID=?",
                               (prev_result[0], (question_id),))
                cursor.execute("UPDATE QUESTIONS SET NUM_INCORRECT = NUM_INCORRECT + 1 - ? WHERE QUESTION_ID=?",
                               (prev_result[1], (question_id),))

                print(f"{latest_attempt_id + 1} {session['id']} {quiz_id} {question_id} {question[7]}")
                # Records the submission for this question on this specific attempt into the RESULTS table
                cursor.execute('INSERT INTO RESULTS(ATTEMPT_ID,EMPLOYEE_ID,QUIZ_ID,QUESTION_ID,ANSWER,IS_CORRECT)'
                               'VALUES(?,?,?,?,?,?) ',
                               (latest_attempt_id + 1, session['id'], quiz_id, question_id, inputAnswer, 0))

            prev_attempt = (0, 0, 0)
            cursor.execute("SELECT MAX(ATTEMPT_NUMBER), NUM_CORRECT, NUM_INCORRECT "
                           "FROM ATTEMPT_HISTORY_LOG "
                           "WHERE EMPLOYEE_ID = ? AND QUIZ_ID = ?", (session['id'], quiz_id))
            query = cursor.fetchone()

            if query[0] is not None:
                prev_attempt = (query[0], query[1], query[2])

        cursor.execute("UPDATE QUIZZES SET TOTAL_CORRECT = TOTAL_CORRECT + ? WHERE QUIZ_ID=?",
                       (int(totalCorrect - prev_attempt[1]), int(quiz_id),))
        cursor.execute("UPDATE QUIZZES SET TOTAL_INCORRECT = TOTAL_INCORRECT + ? WHERE QUIZ_ID=?",
                       (int(totalIncorrect - prev_attempt[2]), int(quiz_id),))

        database.conn.commit()

        cursor.execute(
            "INSERT INTO ATTEMPT_HISTORY_LOG(ATTEMPT_ID,EMPLOYEE_ID,QUIZ_ID,ATTEMPT_NUMBER,DATE_TIME,IS_COMPLETED,NUM_CORRECT,NUM_INCORRECT) "
            "VALUES(?,?,?,?,?,?,?,?) ", (
            latest_attempt_id + 1, session['id'], quiz_id, curr_attempt, datetime.datetime.now(),
            1 if totalIncorrect == 0 else 0, totalCorrect, totalIncorrect,))




        # send_reports.quiz_submission_report(session['id'], latest_attempt_id + 1)

        database.conn.commit()




    # This redirects to the employee dashboard, I tried putting dashboard and it wouldn't let me so I did this.
    # Later this will redirect to another page where it'll display the score you got, if you get less than 100,
    # It will just contain a retry button, and if you get 100, there will be another button for returning to dashboard.
    return redirect(url_for('authenticate_user'))