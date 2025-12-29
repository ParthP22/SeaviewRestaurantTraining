# <p align="center">Seaview Restaurant Training Website</p>


<p align="center">
  <img src="https://raw.githubusercontent.com/Minneo03/CSCI4485-SeaviewRestaurantTraining/refs/heads/main/static/images/SeaviewLogo.webp" alt="Description" width="300">
</p>


Our team developed a training website for the employees of Seaview Golf Club's restaurant using the Flask framework in Python. 

This website contains an employee dashboard, where employees can take their assigned quizzes.

In addition, a manager dashboard has also been implemented and consists of various features, such as being able to create/edit/delete accounts, create quizzes, view quiz trends, and more.


Required Downloads:
- Flask
- WKHMTLToPDF (needed for PDFKit)
- SQLite

To run this project, a "credentials.py" file is required. This file contains the email address and its password that will be used in order to send announcements from the manager's dashboard.

We have deployed the website using Python Anywhere, and it can be accessed here: https://seaviewtraining.pythonanywhere.com/

To run this project locally:
1. Clone the repo: <code>git clone github.com/Minneo03/CSCI4485-SeaviewRestaurantTraining</code>
2. Open your terminal and create a Python virtual environment by doing: <code>python -m venv venv</code>
3. Activate your virtual environment by doing either: <code>source venv/bin/activate</code> OR <code>source venv/Scripts/activate</code>
4. To download all the required packages for this project, do: <code>pip install -r requirements.txt</code>
5. Finally, to run the project, make sure you are in the root directory of this project and do: <code>python app.py</code>

**Team Members and General Contributions**

Parth Patel (ParthP22):
- Team Leader
- Developed the employees' dashboard
- Implemented all emailing functionalities
- Implemented charts to track quiz trends and progress

Ahmed Malik (AhmedM13):
- Implemented profile-editing functionalities
- Implemented history log functionalities for quiz attempts and quiz changes
- Designed a certificate that is granted to an employee upon completion of all quizzes

Pranjal Singh (pranjal0416):
- Regularly communicated with our client
- Created login system
- Developed the managers' dashboard

Ryan Minneo (Minneo03):
- Developed quiz taking/creating/editing/deleting functionalities
- Implemented auxiliary functions, such as forward/backward arrows
- Implemented functionality to upload PDFs for quizzes

Ryan Nguyen (nguyenryan113):
- Team Secretary
- Recorded minutes and summary of each group meeting
- Developed quiz taking/creating/editing/deleting functionalities
- Implemented functionality to upload PDFs for quizzes

**Ryan Nguyen and Ryan Minneo utilized pair programming strategies to complete their portion of this project.
