
import base64
import datetime
from flask import render_template, redirect, url_for, session, request
import database
from . import quiz_bp

@quiz_bp.route('/take-quiz', methods=['GET'])
def take_quiz():
    # Retrieve quiz ID from the request URL
    quiz_id = request.args.get('quiz_id')
    print("Quiz ID in Take Quiz: ", quiz_id)

    # Connect to SQLite database
    conn = database.conn

    # Fetch quiz details from the database
    cursor = conn.cursor()
    cursor.execute("SELECT QUIZ_NAME, QUIZ_DESC FROM QUIZZES WHERE QUIZ_ID = ?", (quiz_id,))
    quiz_info = cursor.fetchone()  # Assuming only one row will be returned
    quiz_name, quiz_desc = quiz_info if quiz_info else (None, None)

    # Fetch questions for the specified quiz from the database
    # cursor.execute(
    #     "SELECT QUESTION_ID, QUESTION, ANSWER_A, ANSWER_B, ANSWER_C, ANSWER_D, CORRECT_ANSWER FROM QUESTIONS WHERE QUIZ_ID = ?",
    #     (quiz_id,))
    questions = []
    for row in cursor.execute(
            "SELECT QUESTION_ID, QUESTION, ANSWER_A, ANSWER_B, ANSWER_C, ANSWER_D, CORRECT_ANSWER FROM QUESTIONS WHERE QUIZ_ID = ?",
            (quiz_id,)):
        question_id, question_text, answer_a, answer_b, answer_c, answer_d, correct_answer = row
        options = [
            {'option_id': 'optionA', 'option_text': answer_a},
            {'option_id': 'optionB', 'option_text': answer_b},
            {'option_id': 'optionC', 'option_text': answer_c},
            {'option_id': 'optionD', 'option_text': answer_d}
        ]
        questions.append({'id': question_id, 'question_text': question_text, 'options': options})

    cursor.close()

    # Render the template with quiz details and questions
    return render_template('quiz/take-quiz.html', quiz_id = quiz_id, quiz_name=quiz_name, quiz_desc=quiz_desc, questions=questions)