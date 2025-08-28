# Author(s): Parth Patel

from flask import render_template
import database
from routes import website

@website.route('/quiz-trends', methods=['GET', 'POST'])
def quiz_trends():

    cursor = database.conn.cursor()

    cursor.execute('SELECT QUIZ_ID, QUIZ_NAME '
                   'FROM QUIZZES '
                   'WHERE IS_DELETED = 0 ')
    query = cursor.fetchall()
    quiz_names = []
    quiz_ids = []

    if query is not None:
        for row in query:
            quiz_ids.append(row[0])
            quiz_names.append(row[1])


    quizzes = []

    for quiz_id in quiz_ids:
        quiz_data = []
        quiz_questions = []
        num_correct = []
        num_incorrect = []
        cursor.execute('SELECT QUESTION, NUM_CORRECT, NUM_INCORRECT '
                       'FROM QUESTIONS ques JOIN QUIZZES quiz ON ques.QUIZ_ID = quiz.QUIZ_ID '
                       'WHERE ques.QUIZ_ID=? AND quiz.IS_DELETED=0 ', (quiz_id,))
        query = cursor.fetchall()
        if query is not None:

            for row in query:

                quiz_questions.append(row[0])
                num_correct.append(row[1])
                num_incorrect.append(row[2])
            quiz_data.append(quiz_questions)
            quiz_data.append(num_correct)
            quiz_data.append(num_incorrect)

        quizzes.append(quiz_data)


    return render_template('quiz/quiz-trends.html', quizzes=quizzes, quiz_names=quiz_names)