
import base64
from flask import render_template, redirect, url_for, session, request
import database
from . import quiz_bp

@quiz_bp.route('/quiz-material', methods=['GET', 'POST'])
def quiz_material():
    quiz_id = request.args.get('id')

    cursor = database.conn.cursor()
    cursor.execute('SELECT MATERIAL_BYTES FROM TRAINING_MATERIALS WHERE QUIZ_ID=?', (quiz_id,))
    result = cursor.fetchone()

    if result:
        image_bytes = result[0]
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        # Save the image to a temporary file
    else:
        image_base64 = None


    return render_template('quiz/quiz-material.html', quiz_id=quiz_id, image_data=image_base64)