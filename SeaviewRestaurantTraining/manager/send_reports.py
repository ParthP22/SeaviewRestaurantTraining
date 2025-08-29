# Author(s): Parth Patel

import os
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import numpy as np
from flask import redirect, session
from matplotlib import pyplot as plt

import database, smtplib, ssl, credentials
from routes import website

import csv

from . import manager_bp

# This is for after you submit a quiz
def quiz_submission_report(user_id, attempt_id):
    cursor = database.conn.cursor()
    cursor.execute('SELECT e.FIRST_NAME, e.LAST_NAME, m.EMAIL '
                   'FROM USERS e JOIN USERS m '
                   'ON e.MANAGER_ID = m.ID '
                   'WHERE e.ID = ? ', (user_id,))
    query = cursor.fetchone()
    print(query)
    if query is None or query[0] is None or query[1] is None or query[2] is None:
        return
    first_name, last_name, manager_email = query[0], query[1], query[2]

    cursor.execute('SELECT q.QUIZ_ID, q.QUIZ_NAME, ah.ATTEMPT_NUMBER '
                   'FROM QUIZZES q JOIN ATTEMPT_HISTORY_LOG ah '
                   'ON q.QUIZ_ID = ah.QUIZ_ID '
                   'WHERE ah.ATTEMPT_ID = ? ', (attempt_id,))

    query = cursor.fetchone()

    quiz_id, quiz_name, attempt_num = query[0], query[1], query[2]

    cursor.execute('SELECT r.QUESTION_ID, q.QUESTION, r.ANSWER, r.IS_CORRECT, q.CORRECT_ANSWER '
                   'FROM RESULTS r JOIN QUESTIONS q '
                   'ON r.QUESTION_ID = q.QUESTION_ID '
                   'WHERE ATTEMPT_ID = ? ', (attempt_id,))

    data = cursor.fetchall()



    for i in range(len(data)):
        if data[i][3] == 1:
            data[i] = (data[i][0], data[i][1], data[i][2], "Yes", data[i][4])
        else:
            data[i] = (data[i][0], data[i][1], data[i][2], "No", data[i][4])


        db_correct_answer = data[i][4][-1]
        db_answer_choice = data[i][2][-1]

        cursor.execute('SELECT ANSWER_A, ANSWER_B, ANSWER_C, ANSWER_D '
                       'FROM QUESTIONS '
                       'WHERE QUESTION_ID = ? ', (data[i][0],))
        query = cursor.fetchone()

        choices = {'A' : query[0], 'B' : query[1], 'C' : query[2], 'D' : query[3]}
        correct_answer = choices[db_correct_answer]
        answer_choice = choices[db_answer_choice]

        if answer_choice is not None and correct_answer is not None:
            data[i] = (data[i][0], data[i][1], answer_choice, data[i][3], correct_answer)



    subject = f"{first_name} {last_name}'s Submission on Quiz {quiz_id}: {quiz_name} "
    recipient_email = manager_email
    body = f"""Attached to this email is a CSV file containing the results of {first_name} {last_name}'s submission on {quiz_name}.
This is their attempt number on this quiz: {attempt_num}. 
    """

    filename = 'results.csv'

    generate_csv(data=data, filename=filename)

    send_submission_report(subject=subject, recipient_email=recipient_email, body=body, filename=filename)



def generate_csv(data, filename):

    header = ['QUESTION_ID','QUESTION','ANSWER','IS_CORRECT','CORRECT_ANSWER']

    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)



def send_submission_report(subject, recipient_email, body, filename):
    port = 587
    smtp_server = "smtp.office365.com"
    sender_email = credentials.email
    password = credentials.password

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    with open(filename, 'rb') as attachment_file:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment_file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(part)

    message.attach(MIMEText(body, 'plain'))

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)

    os.remove(filename)
    print("Submission report with CSV sent successfully")




# This is for the manager dashboard
@manager_bp.route('/progress-report/<int:user_id>', methods=['GET'])
def send_report(user_id):
    cursor = database.conn.cursor()
    cursor.execute('SELECT EMAIL FROM USERS WHERE ID=? ', (session['id'],))
    manager_email = cursor.fetchone()[0]

    cursor.execute('SELECT FIRST_NAME, LAST_NAME FROM USERS WHERE ID=?', (user_id,))
    query = cursor.fetchone()
    first_name = query[0]
    last_name = query[1]

    create_double_bar_graph(user_id)

    if manager_email is not None:
        subject = f"{first_name} {last_name}'s Progress Report"
        body = f"Attached below is an image displaying a bar graph of {first_name} {last_name}'s progress."
        send_progress_report(subject, body, manager_email)
    return redirect('/manage-employee')


def create_double_bar_graph(user_id):
    cursor = database.conn.cursor()

    cursor.execute('SELECT FIRST_NAME, LAST_NAME FROM USERS WHERE ID=?', (user_id,))
    query = cursor.fetchone()

    name = "".join(f"{query[0]} {query[1]}")

    cursor.execute('SELECT QUIZ_NAME, NUM_CORRECT, NUM_INCORRECT, MAX(ATTEMPT_NUMBER) FROM ATTEMPT_HISTORY_LOG ah '
                   'RIGHT JOIN QUIZZES q ON ah.QUIZ_ID = q.QUIZ_ID '
                   'WHERE EMPLOYEE_ID=? AND q.IS_DELETED IS NOT 1 '
                   'GROUP BY q.QUIZ_ID ', (user_id,))
    query = cursor.fetchall()
    correct = []
    incorrect = []
    quiz_names = []
    if query is not None:
        for row in query:
            correct.append(row[1])
            incorrect.append(row[2])
            quiz_names.append(row[0])

    bar_width = 0.25
    x = np.arange(len(quiz_names))

    plt.bar(x - bar_width / 2, correct, bar_width, label='Correct', color="green")
    plt.bar(x + bar_width / 2, incorrect, bar_width, label='Incorrect', color="red")

    plt.xlabel('Quizzes')
    plt.ylabel('Num Of Answers')
    plt.title(f"{name}'s Quiz Progress")
    plt.xticks(x, quiz_names)
    plt.legend()

    plt.savefig(f'Quiz_Progress.png')

    plt.close()


# This one is used for the report function
def send_progress_report(subject, body, recipient_email):
    port = 587
    smtp_server = "smtp.office365.com"
    sender_email = credentials.email
    password = credentials.password

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    with open('Quiz_Progress.png', 'rb') as attachment_file:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment_file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename='Quiz_Progress.png')
        message.attach(part)

    message.attach(MIMEText(body, 'plain'))

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)

    os.remove('Quiz_Progress.png')
    print("Email sent successfully")