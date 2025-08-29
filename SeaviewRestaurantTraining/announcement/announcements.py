# Author(s): Parth Patel
# This file contains the code that is required to be able to successfully send an email
# through seaviewrestauranttraining@outlook.com on the announcements page.
import datetime

from flask import render_template, session, request
import database, smtplib, ssl, credentials, datetime
from . import announcement_bp

# This one is used for the announcements function
def send_mail(subject, body):
    cursor = database.conn.cursor()
    cursor.execute('SELECT DISTINCT Email FROM Users ')
    receiver_emails = cursor.fetchall()
    port = 587
    smtp_server = "smtp.office365.com"
    sender_email = credentials.email
    password = credentials.password
    message = f"""Subject: {subject}\n
{body}"""

    context = ssl.create_default_context()
    for receiver_email in receiver_emails:
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message)
    print("Email sent successfully")



@announcement_bp.route('/', methods=['GET', 'POST'])
def announcements():
    cursor = database.conn.cursor()
    cursor.execute('SELECT FIRST_NAME, LAST_NAME '
                   'FROM USERS '
                   'WHERE ID = ? ', (session['id'],))
    first_name, last_name = cursor.fetchone()

    if session['role'] == 1:
        # Admin
        status = "Type your message"
        if request.method == 'POST' and 'subject' in request.form and 'body' in request.form:

            subject = request.form['subject']
            mail_body = request.form['body']
            db_body = request.form['body']
            closing = f"""
            
- Sincerely,
{first_name} {last_name}   
            """

            send_mail(subject, mail_body + closing.rjust(len(mail_body)))
            status = "Email sent successfully"
            cursor.execute('SELECT MAX(MESSAGE_ID) FROM ANNOUNCEMENTS')
            query = cursor.fetchone()
            curr_message_id = 0
            if query[0] is not None:
                curr_message_id = query[0]
            cursor.execute('INSERT INTO ANNOUNCEMENTS(MESSAGE_ID, SUBJECT, MESSAGE, DATE_TIME, EMPLOYEE_ID) VALUES (?, ?, ?, ?, ?)', (curr_message_id + 1,subject,db_body,datetime.datetime.now(),session['id']))
            database.conn.commit()
            # return redirect(url_for('announcements'))
            return render_template('manager/announcements.html', status=status)

        else:
            return render_template('manager/announcements.html', status=status)

    else:
        # employee/basic user page
        cursor.execute('SELECT SUBJECT,MESSAGE,DATE_TIME, e.FIRST_NAME, e.LAST_NAME '
                       'FROM ANNOUNCEMENTS a JOIN USERS e '
                       'ON a.EMPLOYEE_ID = e.ID '
                       'ORDER BY MESSAGE_ID DESC ')
        emails = cursor.fetchall()
        return render_template('employee/announcements-history.html', emails=emails)


