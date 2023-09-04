import flask
import numpy as np
import pandas as pd
from flask import render_template, request, make_response, jsonify, redirect
from flaskext.mysql import MySQL
from matplotlib import pyplot as plt
import pdfkit
import re

plt.style.use('fivethirtyeight')

# Creating Flask Applications to render Web Pages
app = flask.Flask(__name__)

# Configuring Development Mode
app.config['DEBUG'] = True

# DataBase Configuration
mysql = MySQL()

# MYSQL credentials
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Pass@123'
app.config['MYSQL_DATABASE_DB'] = 'school_db'
mysql.init_app(app) 


# Function to Create and Show Databases
def create_and_show_databases():
    try:
        # Establish Database connection
        con = mysql.connect()
        cur = con.cursor()

        

        # Show list of databases
        # cur.execute("SHOW DATABASES")
        # databases = cur.fetchall()
        # print("List of databases:")
        # for db in databases:
        #     print(db[0])
            
        # Create database if not exists
        cur.execute("CREATE DATABASE IF NOT EXISTS school_management")
        cur.execute("ALTER TABLE students MODIFY roll_no INT(11) NOT NULL DEFAULT 1;")
        cur.close()
        con.close()

        print("Database operations completed successfully!")
    except Exception as e:
        print("Error: {}".format(str(e)))

# Function to Insert Data into Database
def insert_statement(query):
    
    con = mysql.connect()
    cur = con.cursor()

    # Execute the Query
    cur.execute(query)

    print(cur.lastrowid)

    # Make changes Permanent
    con.commit()

    # Close connection
    cur.close()
    con.close()

    return cur.lastrowid


# Function to return selected Data
def select_statement(query):
    # Establish Database connection
    con = mysql.connect()
    cur = con.cursor()

    # Execute the Query
    cur.execute(query)

    # Fetch all the data
    return cur.fetchall()


# Function to Update Data
def update_statement(query):
    print('inside this')
    print(query)
    # Establish Database connection
    con = mysql.connect()
    cur = con.cursor()

    # Execute the Query
    cur.execute(query)

    # Make changes Permanent
    con.commit()

    # Close connection
    cur.close()
    con.close()


# Function to calculate the grades according to Percentage
def grade_calculator(percentage):
    if percentage < 35:
        grade = 'F'
    elif 35 <= percentage < 50:
        grade = 'D'
    elif 50 <= percentage < 60:
        grade = 'C'
    elif 60 <= percentage < 75:
        grade = 'B'
    elif 75 <= percentage < 90:
        grade = 'A'
    else:
        grade = 'A+'

    return grade


# Calculates the Percentage for each Student
def percentage_calculator(dataframe, passing_marks, number_of_subjects):
    percentage = dataframe['TOTAL MARKS'] / number_of_subjects

    for i in dataframe.index[:number_of_subjects]:

        if dataframe[i] < passing_marks:
            return 'F', percentage

    # Calling the Grade calculator Function to calculate the GRades
    grade = grade_calculator(percentage)

    return grade, percentage


# Function to Plot Grouped Bar Charts
def grouped_bar(bars, xticklabels, legend, ylabel, title):
    x = np.arange(len(xticklabels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=[10, 8])
    rects1 = ax.bar(x - width / 2, bars[0], width, color='green')
    rects2 = ax.bar(x + width / 2, bars[1], width, color='red')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(ylabel)
    ax.set_title(title, pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(xticklabels)

    ax.legend(legend)

    # Function to print labels above each bar
    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()

    # plt.savefig(f'static/images/Image-2.png', bbox_inches='tight')


# Create pdf of the HTML Page
def make_pdf(file):
    
    # path where the application is located
    config = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")

    pdf = pdfkit.from_string(file, False, configuration=config)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=output.pdf'
    return response


# Displays the Home Page
@app.route("/", methods=['GET'])
def index_page():
    return render_template('index.html')


# Displays the Home Page
@app.route("/home", methods=['GET'])
def home_page():
    return render_template('home.html')


# Add students to the Database through Form
@app.route("/register", methods=['POST'])
def enter_student_details():
    # Save Request data into variables
    fname = request.form['fname']
    lname = request.form['lname']
    standard = request.form['standard']
    division = request.form['division']

    # Insert Query
    query = "INSERT INTO students (fname, lname, standard, division) VALUES ('{}', '{}', '{}', '{}');".format(fname,
                                                                                                              lname,
                                                                                                              standard,
                                                                                                              division)

    # Calling the insert Function
    last_row_id = insert_statement(query)
    month_lst = 'January,February,March,April,May,June,July,August,September,October,November,December'

    query = "INSERT INTO fees (balance, months, student_id) VALUES('{}', '{}', '{}')".format(12000, month_lst,
                                                                                             last_row_id)
    insert_statement(query)

    return redirect('/home')


# Add students to the Database by CSV file
@app.route("/student_data_csv", methods=['POST'])
def student_data_csv():
    if request.method == 'POST':

        # Read the CSV file using Pandas
        data = pd.read_csv(request.files['details_csv'])

        # Loop through the DataFrame
        for row in range(len(data)):
            # Save Data into variables
            fname = data.loc[row]['fname']
            lname = data.loc[row]['lname']
            standard = data.loc[row]['standard']
            division = data.loc[row]['division']

            # Insert Query
            query = "INSERT INTO students (fname, lname, standard, division) VALUES ('{}', '{}', '{}', '{}');".format(
                fname, lname, standard, division)

            # Calling the insert Function
            last_row_id = insert_statement(query)
            month_lst = 'January,February,March,April,May,June,July,August,September,October,November,December'

            query = "INSERT INTO fees (balance, months, student_id) VALUES('{}', '{}', '{}')".format(12000, month_lst,
                                                                                                     last_row_id)
            insert_statement(query)

        return redirect('/home')


# Displays all the students from Standard & Division
@app.route("/get-student-list", methods=["GET", "POST"])
def student_list():
    if request.method == 'POST':

        # Saving the Data inside variables
        standard = request.form['standard']
        division = request.form['division']

        # Storing student data inside a tuple
        params = (standard, division)

        print()

        # Query to Select data
        query = "SELECT * FROM students WHERE standard = '{}' AND division = '{}' ORDER BY roll_no".format(standard,
                                                                                                           division)

        # Passing the data & Query to the function
        results = select_statement(query)

        # Creating an empty list to save Data
        row_data = []

        for row in results:
            # Saving the Data in the Dictionary
            data = {
                'id': row[0],
                'fname': row[1],
                'lname': row[2],
                'roll_no': row[3]
            }

            # Appending the Data in the list
            row_data.append(data)

        return render_template("student_list.html", data=row_data, params=params)

    else:
        return render_template("student_list.html")


# Generates the Roll Numbers of the students sorted by Last Name & First Name
@app.route("/generate-roll-number", methods=["POST"])
def generate_roll_no():
    standard = request.form['standard']
    division = request.form['division']

    # Query to generate roll numbers sorted by last name & first name
    query = """UPDATE students SET roll_no = (@rownumber := @rownumber+1) WHERE standard='{}' AND division='{}' AND (
    1 + (@rownumber := 0)) ORDER BY fname, lname""".format(standard, division)

    # Calling the update function
    update_statement(query)

    return render_template("student_list.html", message="Roll Numbers Generated Successfully")


# Upload CSV of marks, Calculate Grades & save marks to Database
@app.route("/upload-marks", methods=["GET", "POST"])
def upload_marks():
    if request.method == 'POST':

        # Read the CSV files using pandas and convert it into a DataFrame
        marks_df = pd.read_csv(request.files['marks_csv'], index_col='ROLL NUMBER')

        # Save the number of Subjects inside a variable
        number_of_subjects = len(marks_df.columns)

        # Get total marks for each Student
        marks_df['TOTAL MARKS'] = marks_df.sum(axis=1)

        # Add Grade & Percentage columns to the DataFrame
        passing_marks = 35
        marks_df['GRADE'], marks_df['PERCENTAGE'] = zip(*marks_df.apply(percentage_calculator,
                                                                        args=(passing_marks, number_of_subjects),
                                                                        axis=1))

        # Toppers of Class
        index = marks_df.PERCENTAGE.sort_values(ascending=False)[:3].index
        toppers = marks_df.loc[index]

        # List of Failed Students
        failed = marks_df[marks_df['GRADE'] == 'F']

        # Creating a  Pie Chart of No. of Passed & Failed Students
        passed_students = len(marks_df[marks_df['GRADE'] != 'F'])

        counts = [passed_students, len(failed)]

        labels = ['Passed Students', 'Failed Students']
        colors = ['lightblue', 'salmon']

        # Function to plot the actual values inside Pie Chart instead of Percentages
        def plot_value(vals):
            a = np.round(vals / 100. * sum(counts), 0)
            return int(a)

        # Plotting the Pie Chart
        plt.figure(figsize=(8, 6))
        plt.pie(counts, startangle=45, autopct=plot_value, colors=colors,
                explode=(0, 0.1), textprops={'fontsize': 18})

        plt.legend(labels, loc=6, bbox_to_anchor=(0.5, 1))

        exam_name = request.form['exam_name'].replace(' ', '-')

        # plt.savefig(f'static/images/{exam_name}-1.png')

        # Bar Charts for number of Passed & Failed students
        subjects = [subject for subject in marks_df.columns[:number_of_subjects]]
        total_passed = [len(marks_df.loc[marks_df[i] >= 35]) for i in marks_df.columns[:number_of_subjects]]
        total_failed = [len(marks_df.loc[marks_df[i] < 35]) for i in marks_df.columns[:number_of_subjects]]

        bars = [total_passed, total_failed]
        legend = ['Passed', 'Failed']
        ylabel = 'Number of Students'
        title = 'Passed Vs Failed Students'

        # Calling the grouped_bar function to generate Bar Charts
        grouped_bar(bars=bars, xticklabels=subjects, legend=legend,
                    ylabel=ylabel, title=title)

        # Grouping Students by Grades
        grades = marks_df['GRADE'].value_counts()

        plt.figure(figsize=(8, 6))
        plt.pie(grades, startangle=45, autopct=plot_value,
                textprops={'fontsize': 15}, pctdistance=0.8, radius=1.5)
        centre_circle = plt.Circle((0, 0), radius=1, fc='white')
        plt.gca().add_artist(centre_circle)

        plt.legend(grades.index, loc=10, prop={'size': 20})

        # Saving the Grouped Bar chart Image
        # plt.savefig(f'static/images/{exam_name}-3.png', bbox_inches='tight')

        standard = request.form['standard']
        division = request.form['division']
        exam_name = request.form['exam_name'].replace(' ', '-')

        # Looping through the Dataframe
        for row in range(1, len(marks_df) + 1):
            roll_no = row
            english = marks_df.loc[row]['ENGLISH']
            maths = marks_df.loc[row]['MATHS']
            science = marks_df.loc[row]['SCIENCE']
            history = marks_df.loc[row]['HISTORY']
            total_marks = marks_df.loc[row]['TOTAL MARKS']
            grade = marks_df.loc[row]['GRADE']
            percentage = marks_df.loc[row]['PERCENTAGE']

            # Query to store the marks details into the Database
            query = """INSERT INTO marks
             (roll_no, ENGLISH, MATH, SCIENCE, HISTORY, TOTAL_MARKS, GRADE, PERCENTAGE, 
            EXAM_NAME, standard, division)
             VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', 
            '{}');""".format(roll_no, english,
                             maths,
                             science, history,
                             total_marks, grade,
                             percentage, exam_name,
                             standard, division)

            # Calling the insert Statement
            insert_statement(query)

            # Storing the variables inside a Tuple to pass to the HTML page
        params = (exam_name, standard, division)

        return render_template("upload_marks.html", results=marks_df.to_dict('index'),
                               columns=marks_df.columns.tolist(), toppers=toppers.to_dict('index'),
                               failed=failed.to_dict('index'), params=params)

    else:
        return render_template("upload_marks.html")


# Print result to each student
@app.route("/view-result/<roll_no>/<exam>/<standard>/<division>", methods=['GET'])
def print_result(roll_no, exam, standard, division):
    # Query to get Data from the Database
    query = """SELECT * FROM marks WHERE roll_no = '{}' AND EXAM_NAME = '{}'
     AND standard = '{}' AND division = '{}' """.format(roll_no, exam, standard, division)

    # Calling the function to execute the Query
    results = select_statement(query)

    # Storing the marks Data inside a variable
    marks = [
        {'subjects': 'ENGLISH', 'Marks Out Of': 100, 'Marks Required': 35, 'Marks Obtained': results[0][2]},
        {'subjects': 'MATHS', 'Marks Out Of': 100, 'Marks Required': 35, 'Marks Obtained': results[0][3]},
        {'subjects': 'HINDI', 'Marks Out Of': 100, 'Marks Required': 35, 'Marks Obtained': results[0][4]},
        {'subjects': 'MARATHI', 'Marks Out Of': 100, 'Marks Required': 35, 'Marks Obtained': results[0][5]}
    ]

    # Query to select the name of the Student
    query = "SELECT CONCAT(fname, ' ', lname) FROM students WHERE roll_no='{}' AND standard='{}' AND division='{}'" \
        .format(roll_no, standard, division)

    # Executing the query
    student_info = select_statement(query)

    # Storing the variables inside a Tuple for passing to the HTML page
    params = (results[0][8], results[0][7], exam, student_info[0][0].upper(), roll_no, standard, division)

    # Storing the rendered HTML page inside a variable
    rendered = render_template('view_result.html', data=marks, params=params)

    return rendered


@app.route("/print-all-results", methods=["POST"])
def print_all_results():

    # Receiving the Exam parameters in form of string
    params = request.form['params']

    # Extracting the required information using REGEX
    pattern = re.compile(r'([1-2]+[a-z\-]+)\', \'([0-9])\', \'([A-Z])', re.I)

    # Find the matching patters
    match = pattern.findall(params)

    # Assigning the values to variables
    exam = match[0][0]
    standard = match[0][1]
    division = match[0][2]

    # Query to select all the students from given standard
    query = "SELECT roll_no from students WHERE standard='{}' AND division='{}'".format(standard, division)

    # Storing all the roll numbers
    roll_numbers = select_statement(query)

    # Making an empty string to store the rendered HTML page as string
    pdf = ''

    # For separating pdf into multiple pages
    br = '<br><br><br><br><br><br><br><br><br>'

    # Looping through all the roll numbers
    for roll_number in roll_numbers:

        # Concatenating every HTML page to pdf variable
        pdf = pdf + print_result(roll_number[0], exam, standard, division) + br

    # Downloading the PDF
    return make_pdf(pdf)


# Generate the annual report of the Student
@app.route("/print-annual-report/<roll_no>/<standard>/<division>")
def annual_report(roll_no, standard, division):
    # Query the select the student information
    query = "SELECT * FROM marks WHERE roll_no = '{}' AND standard = '{}' AND division = '{}'".format(
        roll_no, standard, division)

    # Executing the Query
    results = select_statement(query)

    # Creating an empty list to store the subject marks for each exam
    bars = []

    # Storing the subject marks  for each exam inside a list
    for result in results:
        bars.append([result[2], result[3], result[4], result[5]])

    # Storing the information required for Bar charts
    ylabel = 'Marks'
    title = 'Marks Comparison Between Exams'
    subjects = ['ENGLISH', 'MATH', 'SCIENCE', 'HISTORY']
    legend = [results[0][9], results[1][9]]

    # Calling the function to generate bar charts
    grouped_bar(bars=bars, xticklabels=subjects, legend=legend,
                ylabel=ylabel, title=title)

    # Query to select average Percentage of all students for all exams
    query = """SELECT roll_no, AVG(PERCENTAGE) FROM marks GROUP BY roll_no"""

    # Executing the Query & storing the val
    results = select_statement(query)

    # Creating a DataFrame from average Percentages of each student, where Roll Number is the index
    percentages = pd.DataFrame(results).set_index(0)[1]

    # Getting the percentage of student according to their roll no
    student_percentage = percentages.loc[int(roll_no)]
    y_values = [5 for _ in range(len(percentages))]

    # Generating the Line plot
    plt.figure(figsize=(8, 6))
    plt.plot(percentages, y_values, marker=".", markersize=20, alpha=0.3, color='blue')
    plt.plot(student_percentage, 5, marker=".", markersize=20, color='red')

    # Plotting the average of the class
    plt.axvline(percentages.mean(), color='green', linestyle='dashed', linewidth=3)

    # Plot related information
    plt.xlabel('Percentage')
    ax = plt.gca()
    ax.axes.yaxis.set_visible(False)
    plt.title('Percentage Comparison with other Students', pad=50)
    plt.tight_layout()
    plt.xticks([i * 10 for i in range(2, 10)])
    min_ylim, max_ylim = plt.ylim()
    plt.text(percentages.mean() * 1.05, max_ylim, 'Class Average: {:.2f} %'.format(percentages.mean()))

    # Saving the Image of the Plot
    # plt.savefig(f'static/images/Image-1.png')

    # Query to select the average subject marks & percentage for each Student
    query = """SELECT roll_no, AVG(PERCENTAGE), AVG(ENGLISH), AVG(MATH), AVG(SCIENCE),
                 AVG(HISTORY) FROM marks WHERE roll_no='{}' GROUP BY roll_no""".format(roll_no)

    # Fetch the results of the query
    results = select_statement(query)

    # Storing the marks in a Dictionary to pass to the HTML page
    marks = [
        {'subjects': 'ENGLISH', 'Marks Out Of': 100, 'Marks Required': 35, 'Marks Obtained': int(results[0][2])},
        {'subjects': 'MATHS', 'Marks Out Of': 100, 'Marks Required': 35, 'Marks Obtained': int(results[0][3])},
        {'subjects': 'HINDI', 'Marks Out Of': 100, 'Marks Required': 35, 'Marks Obtained': int(results[0][4])},
        {'subjects': 'MARATHI', 'Marks Out Of': 100, 'Marks Required': 35, 'Marks Obtained': int(results[0][5])}
    ]

    # Query to select the name of the Student
    query = "SELECT CONCAT(fname, ' ', lname) FROM students WHERE roll_no='{}' AND standard='{}' AND division='{}'" \
        .format(roll_no, standard, division)

    # Executing the query
    student_info = select_statement(query)

    # Calculating the Grade for the student
    grade = grade_calculator(results[0][1])

    # Storing data in a tuple to pass to the HTML page
    params = (grade, round(results[0][1], 2), student_info[0][0].upper(), roll_no, standard, division)

    # Render the HTML Page
    rendered = render_template('annual_report.html', data=marks, params=params)

    # Calling the Make PDF function to make pdf of the rendered Page
    return make_pdf(rendered)


# Ajax call to get the Fees information according to the student id
@app.route("/get-student-fees/<student_id>", methods=['GET'])
def student_fees_records(student_id):
    # Query to fetch the the Fee information of the Students
    query = "SELECT months, balance, student_id FROM fees WHERE student_id='{}'".format(student_id)

    # Storing the results in a variable
    results = select_statement(query)

    # Converting the Tuple into JSON
    return jsonify(results)


# Ajax call to get the list of Students  according to their standard & division
@app.route("/fees-records", methods=["GET", "POST"])
def fees_records():
    if request.method == 'POST':
        standard = request.form['standard']
        division = request.form['division']

        # Query to get a list of Students according to Standard & Division
        query = "SELECT fname, lname, id FROM students WHERE standard='{}' AND division='{}'".format(standard, division)

        results = select_statement(query)

        return jsonify(results)

    return render_template('collect_fees.html')


# Function to update the fee records of the Student & print PDF
@app.route("/collect-fees", methods=['POST'])
def collect_fees():
    # Storing the information received from the Form
    amount = int(request.form['amount'])
    months_paid = len(request.form['months'].split(','))
    student_id = request.form['student_id']

    # Get fee information of the Student
    query = "SELECT * FROM fees WHERE student_id='{}'".format(student_id)

    # Execute the Query, fetch the results
    results = select_statement(query)

    # Updating the Balance of the Student
    balance_amount = results[0][1] - amount


    # Removing the months where Fee is paid
    months = results[0][2].split(',')
    months = ','.join(months[months_paid:])


    # Query to update the fees information
    query = "UPDATE fees SET balance='{}', months='{}'  WHERE student_id='{}'".format(balance_amount, months,
                                                                                      student_id)

    # Updating the Fees records of the Student
    update_statement(query)

    # Converting the string to list of months
    months = request.form['months'].split(',')

    # Creating a Tuple to pass to the HTML page
    params = (months, amount)

    # Rendering the HTML page
    rendered = render_template('fees_receipt.html', params=params)

    # Calling the PDF page to create PDF of the fee receipt
    return make_pdf(rendered)




if __name__ == '__main__':
    create_and_show_databases()
    app.run(debug=True)