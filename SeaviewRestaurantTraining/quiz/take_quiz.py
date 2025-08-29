# Author(s): Ryan Minneo, Ryan Nguyen
# This file contains the code that allows the employees to take quizzes

from flask import render_template, request
import database
from routes import website
from . import quiz_bp

@quiz_bp.route('/take-quiz', methods=['GET'])
def take_quiz():
    quiz_id = request.args.get('id')
    # Connect to SQLite database
    cursor = database.conn.cursor()

    # Fetch questions from the database  --------------------------------- This quiz_id is undefined, fetch from the url.
    cursor.execute("SELECT QUESTION_ID, QUESTION FROM QUESTIONS WHERE QUIZ_ID = ?", quiz_id)
    questions = []
    for row in cursor.fetchall():
        question_id, question = row
        cursor.execute("SELECT ANSWER_A, ANSWER_B, ANSWER_C, ANSWER_D, CORRECT_ANSWER FROM QUESTIONS WHERE QUESTION_ID = ?", (question_id))
        answers = [{'answer_a': ANSWER_A, 'answer_b': ANSWER_B, 'answer_c': ANSWER_C, 'answer_d': ANSWER_D, 'correct_answer': CORRECT_ANSWER}
                   for ANSWER_A, ANSWER_B, ANSWER_C, ANSWER_D, CORRECT_ANSWER in cursor.fetchall()]
        questions.append({'id': question_id, 'question_text': question, 'options': answers})

    cursor.close()

    return render_template('quiz/take-quiz.html', questions=questions)