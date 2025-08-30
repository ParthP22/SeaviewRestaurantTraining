
import base64
import datetime
from flask import render_template, redirect, url_for, session, request
import database
from . import quiz_bp

#Routes quiz list to the quiz editor
@quiz_bp.route('/quiz-editor')
def quiz_editor():
    if session['role'] == 1:
        quiz_id = request.args.get('quiz_id')
        quiz_name = request.args.get('quiz_name')
        quiz_desc = request.args.get('quiz_desc')

        cursor = database.conn.cursor()

        # Fetch all questions associated with the quiz
        cursor.execute(
            "SELECT QUESTION, ANSWER_A, ANSWER_B, ANSWER_C, ANSWER_D, CORRECT_ANSWER FROM QUESTIONS WHERE QUIZ_ID = ?",
            (quiz_id,))
        questions = []
        for row in cursor.fetchall():
            question_text, option_a, option_b, option_c, option_d, correct_answer = row
            questions.append({
                'question_text': question_text,
                'option_a': option_a,
                'option_b': option_b,
                'option_c': option_c,
                'option_d': option_d,
                'correct_answer': correct_answer
            })

        cursor.close()

        return render_template('quiz/quiz-editor.html', quiz_id=quiz_id, quiz_name=quiz_name, quiz_desc=quiz_desc,
                               questions=questions)
    else:
        return render_template('error/prohibited.html')