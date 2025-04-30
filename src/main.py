from mysql import connector
from pyswip import Prolog

from tabulate import tabulate
import mailtrap as mt

import os
from dotenv import load_dotenv

load_dotenv()

MAILTRAP_API_TOKEN = os.getenv('MAILTRAP_API_TOKEN')

# Connects to the mysql server
db_connector = connector.connect(
    host="localhost",
    user="root",
    password="admin",
    database="apa_system_db",
)

# Connects the application to the prolog knowledge base
prolog = Prolog()
prolog.consult("knowledge_base.pl")

# Used to execute queries
cursor = db_connector.cursor()

# Set desired width for centring
line_width = 80

# Stores the user choice
choice = 0
# Stores the user ID
user_id = ""

# Semesters total credits
semester_1_total_credits = 0
semester_2_total_credits = 0

# Semesters total gpe
total_gpe_for_semester_1 = 0
total_gpe_for_semester_2 = 0

# Semesters gpa
semester_1_gpa = 0
semester_2_gpa = 0
cumulative_gpa = 0
gpa = 2.0


# Program starts here
def driver() -> None:
    # Fetch information from the database and add it to the knowledge base
    add_student_info_to_knowledge_base()
    add_modules_to_knowledge_base()
    add_student_record_to_knowledge_base()
    add_faculty_to_knowledge_base()
    add_programme_to_knowledge_base()

    # Login menu
    login_menu()


# Student menu
def student_menu() -> None:
    try:
        print("Student Menu")
        desired_year = input("Enter a desired year of student: ")
        process_gpa(user_id, desired_year, "")
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except ValueError:
        print("Invalid input. Please enter a valid integer.")


# Admin menu
def admin_menu() -> None:
    try:
        print("Administrative Menu")
        student_id = input("\nEnter a student's ID#: ")

        # Checks if student exists in the database
        while validate_student(student_id):
            print("Student does not exist, try again!")
            student_id = input("\nEnter a student's ID#: ")

        # Prompts the user to enter a desired year
        desired_year = input("Enter a desired year of student: ")
        optionally_gpa = input("Enter an optionally a desired GPA of student (Leave blank for default of 2.0): ")

        # Processes the GPA
        process_gpa(student_id, desired_year, optionally_gpa)
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except ValueError:
        print("Invalid input. Please enter a valid integer.")


# Processes the GPA
def process_gpa(student_id, desired_year, optionally_gpa):
    global cumulative_gpa, semester_1_total_credits, semester_2_total_credits, total_gpe_for_semester_1
    global total_gpe_for_semester_2, semester_1_gpa, semester_2_gpa, gpa

    try:
        # Checks if the user entered an optional GPA
        if optionally_gpa != "":
            while float(optionally_gpa) < 0.0 or float(optionally_gpa) > 4.3:
                print("Invalid GPA range, try again!")
                optionally_gpa = input(
                    "Enter an optionally a desired GPA of student (Leave blank for default of 2.0): ")

            gpa = float(optionally_gpa)

        # Checks if the user entered a valid year then assigns the total credits per semesters
        semester_1_total_credits = fetch_student_total_credits_for_semester(student_id, int(desired_year), 1)
        semester_2_total_credits = fetch_student_total_credits_for_semester(student_id, int(desired_year), 2)

        # Checks if both semesters have credits then adds it to the knowledge base
        if semester_1_total_credits != 0:
            prolog.assertz(
                f"gpa_is({student_id}, {desired_year}, {gpa})")

            # StudentID, DesiredYear, TotalCredits
            prolog.assertz(
                f"student_total_credits_for_semester_1({student_id}, {desired_year}, {semester_1_total_credits})")

            total_gpe_for_semester_1 = fetch_total_student_gpe_per_semester(student_id,
                                                                            int(desired_year),
                                                                            1)

            # StudentID, DesiredYear, TotalGradePointsEarned
            prolog.assertz(
                f"student_total_grade_point_earned_for_semester_1({student_id}, {desired_year}, "
                f"{total_gpe_for_semester_1})")

            semester_1_gpa_list = list(prolog.query(
                f"get_student_gpa_for_semester_1({student_id}, {desired_year}, Semester1TotalGPA)"))

            semester_1_gpa = round(semester_1_gpa_list[0]["Semester1TotalGPA"], 2)

            if semester_2_total_credits == 0:
                cumulative_gpa = semester_1_gpa
            else:
                # StudentID, DesiredYear, TotalCredits
                prolog.assertz(
                    f"student_total_credits_for_semester_2({student_id}, {desired_year}, {semester_2_total_credits})")

                total_gpe_for_semester_2 = fetch_total_student_gpe_per_semester(student_id,
                                                                                int(desired_year),
                                                                                2)

                # StudentID, DesiredYear, TotalGradePointsEarned
                prolog.assertz(
                    f"student_total_grade_point_earned_for_semester_2({student_id}, {desired_year}, "
                    f"{total_gpe_for_semester_2})")

                semester_2_gpa_list = list(prolog.query(
                    f"get_student_gpa_for_semester_2({student_id}, {desired_year}, Semester2TotalGPA)"))

                semester_2_gpa = round(semester_2_gpa_list[0]["Semester2TotalGPA"], 2)

                cumulative_gpa_list = list(prolog.query(
                    f"get_total_gpa_for_both_semesters({student_id}, {desired_year}, CumulativeGPA)"))

                cumulative_gpa = round(cumulative_gpa_list[0]["CumulativeGPA"], 2)

            student_info_list = fetch_student_info(student_id)
            student_name = f"{student_info_list[0][1]} {student_info_list[0][2]}"

            # StudentID, Semester1GPA, Semester1TotalCredits, Semester2GPA, Semester2TotalCredits, DesiredYear,
            # CumulativeGPA

            # Add the results to the database
            add_results_to_database(student_id, semester_1_gpa, semester_1_total_credits, semester_2_gpa,
                                    semester_2_total_credits, desired_year)

            # Print the results
            data = [
                [student_id, student_name, semester_1_gpa, semester_2_gpa, cumulative_gpa]
            ]

            # Header for the table
            headers = ["Student ID", "Student Name", "GPA Semester 1", "GPA Semester 2", "Cumulative GPA"]

            # centred header lines
            university_name = "University of Technology".center(line_width)
            report_title = "Academic Probation Alert GPA Report".center(line_width)
            year_line = f"Year: {desired_year}".center(line_width)
            gpa_line = f"GPA: {gpa}".center(line_width)

            # Print the centred report header
            print("\n\n")
            print(university_name)
            print(report_title)
            print(year_line)
            print(gpa_line)
            print("\n")

            # Print the table with data
            print(tabulate(data, headers, tablefmt="plain"))

            # Print if the student is eligible for probation
            if cumulative_gpa <= gpa:
                print("\n")
                print("Student is eligible for probation!")
                # Send email to all stakeholders
                notify_stakeholders(student_id)
                print("\n")
            elif cumulative_gpa > gpa:
                print("\n")
                print("Student is not eligible for probation!")
                print("\n")
        else:
            # Print if the student has no records
            print("\n")
            print("Student has no records from semester 1 for the given year.")
            print("Try another year.")
            print("\n")

            if choice == 1:
                student_menu()
            elif choice == 2:
                admin_menu()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except ValueError:
        print("Invalid input. Please enter a valid float.")


# Add results to the database
def add_results_to_database(student_id, sem_1_gpa, sem_1_total_credits, sem_2_gpa,
                            sem_2_total_credits, desired_year) -> None:
    sql_select_query = (
        "INSERT INTO student_result(student_id, semester_1_gpa, semester_1_total_credits, semester_2_gpa, "
        "semester_2_total_credits, year, cumulative_gpa) VALUES (%s, %s, %s, %s, %s, %s, %s)")

    cursor.execute(sql_select_query, (student_id, sem_1_gpa, sem_1_total_credits, sem_2_gpa,
                                      sem_2_total_credits, desired_year, cumulative_gpa))

    db_connector.commit()
    print("Student result was inserted successfully into the database")


# Sends email to all stakeholders if student is eligible for probation
def notify_stakeholders(student_id) -> None:
    # STUDENT, ADVISOR, PROGRAMME DIRECTOR, FACULTY ADMINISTRATOR
    email_list = fetch_stakeholders_emails(student_id)

    send_email_to_student(email_list[0], email_list[2], email_list[4],
                          email_list[1], email_list[5])

    send_email_to_advisor(email_list[0], email_list[2], email_list[4],
                          email_list[1], email_list[3])

    send_email_to_programme_director(email_list[0], email_list[2], email_list[4],
                                     email_list[1], email_list[3], email_list[5])

    send_email_to_faculty_administrator(email_list[0], email_list[2], email_list[4], email_list[1],
                                        email_list[5])


# Sends email to the student
def send_email_to_student(student_info, programme_info,
                          faculty_info, advisor_info, faculty_admin_info) -> None:
    sender = "info@demomailtrap.com"
    receiver = f"{student_info[3]}"
    subject = "Important: GPA Alert"

    message = f"""\
    Subject: {subject}
    To: {receiver}
    From: {sender}
    
    Dear {student_info[1]} {student_info[2]},
    
    We are writing to inform you that your current Grade Point Average (GPA) is below the minimum required threshold. 
    
    Default GPA: {gpa}
    Your GPA: {cumulative_gpa}
    Your Program: {programme_info[1]}
    Your School: {faculty_info[1]}
    
    Please be advised that this could impact your academic standing and eligibility for certain academic opportunities.
    We encourage you to review your academic progress and take necessary steps to improve your GPA. 
    
    We recommend that you consult with your academic advisor, {advisor_info[1]} {advisor_info[2]}, to discuss 
    strategies for improving your academic performance.
    
    Please contact your advisor or the appropriate academic department if you have any questions or concerns. 
    
    Sincerely,
    {faculty_admin_info[1]} {faculty_admin_info[2]}
    {faculty_admin_info[4]}
    {programme_info[1]}
    """

    send_email(receiver, subject, message)
    print(f"Email sent to {student_info[1]} {student_info[2]} notifying them of the GPA Alert.")


# Sends email to the advisor
def send_email_to_advisor(student_info, programme_info,
                          faculty_info, advisor_info, faculty_admin_info) -> None:
    sender = "info@demomailtrap.com"
    receiver = f"{advisor_info[5]}"
    subject = "Important: GPA Alert"

    message = f"""\
    Subject: GPA Alert for {student_info[1]} {student_info[2]}
    To: {receiver}
    From: {sender}
    
    Dear {advisor_info[1]} {advisor_info[2]},
    
    We are writing to inform you that {student_info[1]} {student_info[2]} current Grade Point Average (GPA) is 
    below the minimum required threshold.
    
    Default GPA: {gpa}
    Student's GPA: {cumulative_gpa}
    Student's Program: {programme_info[1]}
    Student's School: {faculty_info[1]}
    
    We recommend that you meet with the student to discuss their academic progress and provide guidance on how to 
    improve their GPA.
    
    Please let us know if you have any questions or concerns.
    
    Sincerely,
    {faculty_admin_info[1]} {faculty_admin_info[2]}
    {faculty_admin_info[4]}
    {faculty_info[1]}
    """

    send_email(receiver, subject, message)
    print(f"An email was sent to {student_info[1]} {student_info[2]} advisor notifying them of the GPA Alert.")


# Sends email to the programme director
def send_email_to_programme_director(student_info, programme_info,
                                     faculty_info, advisor_info, programme_director_info, faculty_admin_info
                                     ) -> None:
    sender = "info@demomailtrap.com"
    receiver = f"{advisor_info[5]}"
    subject = "Important: GPA Alert"

    message = f"""\
    Subject: GPA Alert for {student_info[1]} {student_info[2]}
    To: {receiver}
    From: {sender}
    
    Dear {programme_director_info[1]} {programme_director_info[2]},
    
    We are writing to inform you that {student_info[1]} {student_info[2]} current Grade Point Average (GPA) is below 
    the minimum required threshold.
    
    Default GPA: {gpa}
    Student's GPA: {cumulative_gpa}
    Student's Program: {programme_info[1]}
    Student's School: {faculty_info[1]}
    
    We recommend that you monitor the student's academic progress and take appropriate action if necessary. 
    
    Please let us know if you have any questions or concerns.
    
    Sincerely,
    {faculty_admin_info[1]} {faculty_admin_info[2]}
    {faculty_admin_info[4]}
    {faculty_info[1]}
    """

    send_email(receiver, subject, message)
    print(
        f"An email was sent to {programme_director_info[1]} {programme_director_info[2]} notifying them of "
        f"{student_info[1]} {student_info[2]} academic probation.")


# Sends email to the faculty administrator
def send_email_to_faculty_administrator(student_info, programme_info,
                                        faculty_info, advisor_info, faculty_admin_info) -> None:
    sender = "info@demomailtrap.com"
    receiver = f"{advisor_info[5]}"
    subject = "Important: GPA Alert"

    message = f"""\
    Subject: GPA Alert for {student_info[1]} {student_info[2]}
    To: {receiver}
    From: {sender}
    
    Dear {faculty_admin_info[1]} {faculty_admin_info[2]},
    
    We are writing to inform you that {student_info[1]} {student_info[2]} current Grade Point Average (GPA) is below 
    the minimum required threshold.
    
    Default GPA: {gpa}
    Student's GPA: {cumulative_gpa}
    Student's Program: {programme_info[1]}
    Student's School: {faculty_info[1]}
    
    Please take note of this information and take appropriate action if necessary.
    
    Sincerely,
    {faculty_admin_info[1]} {faculty_admin_info[2]}
    {faculty_admin_info[4]}
    {faculty_info[1]}
    """

    send_email(receiver, subject, message)
    print(f"An email was sent to {faculty_admin_info[1]} {faculty_admin_info[2]} notifying them of the GPA Alert.")


# Sends an email
def send_email(receiver, subject, message) -> None:
    mail = mt.Mail(
        sender=mt.Address(email="info@demomailtrap.com", name="Demo Mailtrap"),
        to=[mt.Address(email=receiver)],
        subject=subject,
        text=message
    )

    client = mt.MailtrapClient(token=MAILTRAP_API_TOKEN)
    client.send(mail)


# Fetches the stakeholders information from the database
def fetch_stakeholders_emails(student_id) -> list:
    email_list = []

    # Fetch the student email
    sql_select_query = "SELECT * FROM student_info WHERE student_id = %s"
    cursor.execute(sql_select_query, (student_id,))
    student_info = list(cursor.fetchall())
    email_list.append(student_info[0])

    # Fetch the advisor email
    sql_select_query = "SELECT * FROM staff_info WHERE staff_id = %s"
    cursor.execute(sql_select_query, (student_info[0][5],))
    advisor_info = list(cursor.fetchall())
    email_list.append(advisor_info[0])

    # Fetch the programme director email
    sql_select_query = "SELECT * FROM programme_info WHERE programme_id = %s"
    cursor.execute(sql_select_query, (student_info[0][4],))
    programme_director_info = list(cursor.fetchall())
    email_list.append(programme_director_info[0])

    sql_select_query = "SELECT * FROM staff_info WHERE staff_id = %s"
    cursor.execute(sql_select_query, (programme_director_info[0][2],))
    staff_info_director = list(cursor.fetchall())
    email_list.append(staff_info_director[0])

    # Fetch the faculty administrator email
    sql_select_query = "SELECT * FROM faculty_info WHERE faculty_id = %s"
    cursor.execute(sql_select_query, (student_info[0][7],))
    faculty_admin_info = list(cursor.fetchall())
    email_list.append(faculty_admin_info[0])

    sql_select_query = "SELECT * FROM staff_info WHERE staff_id = %s"
    cursor.execute(sql_select_query, (faculty_admin_info[0][2],))
    staff_info_faculty_admin = list(cursor.fetchall())
    email_list.append(staff_info_faculty_admin[0])

    return email_list


# Fetches the student total credits for a given semester from the knowledge base
def fetch_student_total_credits_for_semester(student_id, desired_year, semester) -> int:
    student_credits_list = list(
        prolog.query(
            f"get_students_total_credits_for_semester({student_id}, {desired_year}, {semester}, TotalCredits)"))

    return student_credits_list[0]["TotalCredits"]


# Fetches the student total grade points for a given semester from the knowledge base
def fetch_total_student_gpe_per_semester(student_id, desired_year, semester) -> int:
    student_grade_points_list = list(
        prolog.query(
            f"get_grade_point_earned_sum({student_id}, {desired_year}, {semester}, TotalGradePointEarned)"))

    return student_grade_points_list[0]["TotalGradePointEarned"]


# Adds the student information to the knowledge base
def add_student_info_to_knowledge_base() -> None:
    sql_select_query = "SELECT * FROM student_info"

    cursor.execute(sql_select_query)
    student_list = list(cursor.fetchall())

    # StudentID, fist_name, last_name, email, programme, advisor, password, school
    for student_info in student_list:
        prolog.assertz(
            f"student_info('{student_info[0]}', '{student_info[1]}', '{student_info[2]}', '{student_info[3]}', "
            f"'{student_info[4]}', '{student_info[5]}', '{student_info[6]}', '{student_info[7]}')")


# Adds the student record to the knowledge base
def add_student_record_to_knowledge_base() -> None:
    sql_select_query = "SELECT * FROM stud_mod_info"

    cursor.execute(sql_select_query)
    stud_mod_list = list(cursor.fetchall())

    # ModID, Semester, StudentID, GradePoint, Year
    for stud_mod in stud_mod_list:
        prolog.assertz(
            f"student_record('{stud_mod[0]}', {stud_mod[1]}, {stud_mod[2]}, {stud_mod[3]}, {stud_mod[4]})")


# Adds the module information to the knowledge base
def add_modules_to_knowledge_base() -> None:
    sql_select_query = "SELECT * FROM module_info"

    cursor.execute(sql_select_query)
    module_list = list(cursor.fetchall())

    for module in module_list:
        prolog.assertz(f"module_info('{module[0]}', '{module[1]}', {module[2]})")


# Adds the faculty information to the knowledge base
def add_faculty_to_knowledge_base() -> None:
    sql_select_query = "SELECT * FROM faculty_info"

    cursor.execute(sql_select_query)
    module_list = list(cursor.fetchall())

    for module in module_list:
        prolog.assertz(f"faculty_info('{module[0]}', '{module[1]}', {module[2]})")


# Adds the programme information to the knowledge base
def add_programme_to_knowledge_base() -> None:
    sql_select_query = "SELECT * FROM programme_info"

    cursor.execute(sql_select_query)
    module_list = list(cursor.fetchall())

    for module in module_list:
        prolog.assertz(f"programme_info('{module[0]}', '{module[1]}', {module[2]})")


# Fetches the student record from the knowledge base
def fetch_student_record(student_id: str, desired_year: str) -> list:
    sql_select_query = "SELECT * FROM stud_mod_info WHERE student_id = %s and year = %s"

    cursor.execute(sql_select_query, (student_id, desired_year))
    records = list(cursor.fetchall())
    return records


# Fetches the student information from the knowledge base
def fetch_student_info(student_id: str) -> list:
    sql_select_query = "SELECT * FROM student_info WHERE student_id = %s"

    cursor.execute(sql_select_query, (student_id,))
    records = list(cursor.fetchall())
    return records


# Main login menu
def login_menu() -> None:
    global choice

    try:
        print("Academic Probation Alert System")
        print("Account Type: (1) Student or (2) Administrator")
        choice = int(input("Enter your choice: "))

        while choice != 1 and choice != 2:
            print("Invalid choice")
            choice = int(input("Enter your choice: "))

        if choice == 1:
            student_authenticate()
        elif choice == 2:
            admin_authenticate()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except ValueError:
        print("Invalid input. Please enter a valid integer.")


# Authentication methods
def student_authenticate() -> None:
    global user_id

    try:
        print("\nStudent Login Menu")
        user_id = int(input("Enter your student ID: "))
        password = input("Enter your password: ")

        sql_select_query = "SELECT * FROM student_info WHERE student_id = %s and password = %s"
        cursor.execute(sql_select_query, (user_id, password))

        # get all records
        records = cursor.fetchall()

        if len(records) == 0:
            print("Invalid student ID or password. Try again\n")
            student_authenticate()
        else:
            for i in records:
                if i[0] == user_id and i[6] == password:
                    print(f"\nWelcome, {i[1]} {i[2]}!")
                    student_menu()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except ValueError:
        print("Invalid input. Please enter a valid integer.")


# Authentication methods
def admin_authenticate() -> None:
    global user_id

    try:
        print("\nAdministrator Login Menu")
        user_id = int(input("Enter your staff ID: "))
        password = input("Enter your password: ")

        sql_select_query = "SELECT * FROM staff_info WHERE staff_id = %s and password = %s"
        cursor.execute(sql_select_query, (user_id, password))

        # get all records
        records = cursor.fetchall()

        if len(records) == 0:
            print("Invalid student ID or password. Try again\n")
            admin_authenticate()
        else:
            for i in records:
                if i[0] == user_id and i[3] == password and i[4] == 'Admin':
                    print(f"\nWelcome, {i[1]} {i[2]}!")
                    admin_menu()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except ValueError:
        print("Invalid input. Please enter a valid integer.")


# Checks if the student is in the database
def validate_student(student_id) -> bool:
    sql_select_query = "SELECT * FROM student_info WHERE student_id = %s"
    cursor.execute(sql_select_query, (student_id,))

    # get all records
    records = cursor.fetchall()

    if len(records) == 0:
        return True
    else:
        return False


# Runs the program
driver()
