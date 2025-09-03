
import base64
import datetime
from flask import render_template, redirect, url_for, session, request
import database
from . import quiz_bp
from SeaviewRestaurantTraining.enums import Role

#Routes quiz list to the quiz editor
@quiz_bp.route('/quiz-editor')
def quiz_editor():
    if session['role'] == Role.MANAGER.value:

        cursor = database.conn.cursor()

        quiz_id = request.args.get('quiz_id', type=int)
        print(quiz_id)

        quiz_name, quiz_desc = None, None
        questions = []

        
        if quiz_id:
            
            cursor.execute(
                "SELECT QUIZ_NAME, QUIZ_DESC " \
                "FROM QUIZZES " \
                "WHERE QUIZ_ID = ?",
                (quiz_id,))

            quiz_row = cursor.fetchone()
            if not quiz_row:
                return "Quiz not found", 404

            quiz_name, quiz_desc = quiz_row

            # Fetch all questions associated with the quiz
            cursor.execute(
                "SELECT QUESTION, ANSWER_A, ANSWER_B, ANSWER_C, ANSWER_D, CORRECT_ANSWER FROM QUESTIONS WHERE QUIZ_ID = ?",
                (quiz_id,))
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
    

@quiz_bp.route('/submit-quiz-edit', methods=['GET', 'POST'])
def submit_quiz_edit():
    if session['role'] == Role.MANAGER.value:
        count = 0
        file_data = None  # Define file_data variable outside the conditional block
        # Check if the quiz name, quiz description, and material name is inputted into their text boxes.
        if request.method == 'POST' and 'quiz_name' in request.form and 'quiz_desc' in request.form and 'material_name' in request.form:
            # Retrieve data from the HTML form
            # quiz_id = request.form['quiz_id']
            # print("URL: ", request.url)
            # The first one handles quiz edits, while the second one handles quiz creation
            quiz_id = request.form.get('quiz_id') or request.args.get('quiz_id')
            # print("Quiz ID: ?, Type: ?",(quiz_id,type(quiz_id)))
            quiz_name = request.form['quiz_name']
            quiz_desc = request.form['quiz_desc']
            material_name = request.form['material_name']
            is_visible = 1 if request.form.get('isVisible') == '1' else 0
            due_date = request.form['due_date']

            # Retrieve questions and answers dynamically
            questions = []
            for key, value in request.form.items():
                if key.startswith('question'):
                    question_number = key.replace('question', '')
                    question = {
                        'QUESTION': value,
                        'ANSWER_A': request.form[f'option{question_number}A'],
                        'ANSWER_B': request.form[f'option{question_number}B'],
                        'ANSWER_C': request.form[f'option{question_number}C'],
                        'ANSWER_D': request.form[f'option{question_number}D'],
                        'CORRECT_ANSWER': request.form[f'correctAnswer{question_number}']
                    }
                    count = count + 1
                    questions.append(question)

            cursor = database.conn.cursor()
            if quiz_id:
                print("Deleting old quiz version...")
                cursor.execute('UPDATE QUIZZES SET IS_DELETED=1 WHERE QUIZ_ID=?', (int(quiz_id),))
            print("Quiz Desc: " + quiz_desc)
            cursor.execute('INSERT INTO QUIZZES (QUIZ_NAME, TOTAL_QUESTIONS, TOTAL_CORRECT, TOTAL_INCORRECT, IS_VISIBLE, QUIZ_DESC, IS_DELETED, DUE_DATE) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (quiz_name, count, 0, 0, is_visible, quiz_desc, 0, due_date))
            cursor.execute('UPDATE USERS SET IS_COMPLETED=0 ')
            #Gets the ID from the quiz that was just created to upload that into the questions that are created.
            cursor.execute('SELECT MAX(QUIZ_ID) FROM QUIZZES')
            quizID = cursor.fetchone()[0]

            # cursor.execute("SELECT MAX(CHANGE_NUMBER) FROM QUIZ_HISTORY_LOG WHERE EMPLOYEE_ID=? AND QUIZ_ID=?",
            #                (session['id'], quizID))
            # recent_change = cursor.fetchone()
            # curr_change = 1
            # if recent_change[0] is not None:
            #     curr_change = recent_change[0] + 1
            # else:
            #     curr_change = 1

            cursor.execute(
                'INSERT INTO QUIZ_HISTORY_LOG(CHANGE_ID, EMPLOYEE_ID, QUIZ_ID, DATE_TIME, ACTION_TYPE)'
                'VALUES(?,?,?,?,?)', (None, session['id'], quizID, datetime.datetime.now(), 'CREATE'))

            #Uploads questions into the database
            for question in questions:
                cursor.execute('''INSERT INTO QUESTIONS (QUIZ_ID, QUESTION, ANSWER_A, ANSWER_B, ANSWER_C, ANSWER_D, 
                CORRECT_ANSWER, NUM_CORRECT, NUM_INCORRECT, NUM_EMPLOYEES_COMPLETED, QUESTION_TYPE)
                                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               (quizID, question['QUESTION'], question['ANSWER_A'], question['ANSWER_B'],
                               question['ANSWER_C'], question['ANSWER_D'], question['CORRECT_ANSWER'], 0, 0, 0, "Multiple Choice"))

            # Retrieve data for pdf images
            # Handle file upload
            file = request.files.get('file')  # Simplified file retrieval
            if file and file.filename != '':
                file_data = file.read()
                if file_data:
                    cursor.execute(
                        'INSERT INTO TRAINING_MATERIALS (MATERIAL_NAME, MATERIAL_BYTES, QUIZ_ID) VALUES (?, ?, ?)',
                        (material_name, file_data, quizID))
            else:
                # If no new file is uploaded, reuse existing file data
                material = cursor.execute(
                    "SELECT MATERIAL_NAME, MATERIAL_BYTES FROM TRAINING_MATERIALS WHERE QUIZ_ID = ?",
                    (quiz_id,)).fetchone()
                if material:
                    cursor.execute(
                        'INSERT INTO TRAINING_MATERIALS (MATERIAL_NAME, MATERIAL_BYTES, QUIZ_ID) VALUES (?, ?, ?)',
                        (material[0], material[1], quizID))

            # Commit changes to the database
            database.conn.commit()

            return redirect(url_for('manager.manage_quizzes'))
    else:
        render_template('error/prohibited.html')