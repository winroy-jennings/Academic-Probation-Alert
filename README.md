# UTech Academic Probation Alert System (AI Class Project)

![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)

## Overview

This is a terminal-based Python application developed as an AI class project for the University of Technology, Jamaica. The system aims to identify students who may be eligible for academic probation based on their Grade Point Average (GPA). It utilizes a MySQL database to store student and course information and a Prolog knowledge base to define rules for GPA calculation and probation eligibility. The system can notify relevant stakeholders (student, advisor, programme director, faculty administrator) via email if a student's GPA falls below a specified threshold.

## Features

* **User Authentication:** Separate login interfaces for Students and Administrators.
* **Database Integration:** Connects to a MySQL database (`apa_system_db`) to fetch student records, module information, faculty details, etc.
* **Prolog Knowledge Base:**
    * Loads data from the database into a Prolog knowledge base (`knowledge_base.pl`).
    * Uses Prolog rules to calculate Semester 1 GPA, Semester 2 GPA, and Cumulative GPA.
    * Determines probation eligibility based on calculated GPA against a threshold (default 2.0, configurable by admin).
* **GPA Calculation:** Processes student records for a specific year to calculate relevant GPAs.
* **Reporting:** Displays calculated GPA results in a formatted table using `tabulate`.
* **Stakeholder Notification:** Sends email alerts using Mailtrap to the student and relevant university staff if the student is flagged for probation.
* **Result Persistence:** Stores the calculated GPA results back into the `student_result` table in the database.
* **Role-Based Access:**
    * **Students:** Can log in and check their own GPA status for a specific year.
    * **Administrators:** Can log in and check the GPA status of any student for a specific year, optionally setting a custom GPA threshold for the check.

## Technologies Used

* **Language:** Python 3.x
* **Database:** MySQL
* **Knowledge Base:** SWI-Prolog (or compatible Prolog interpreter)
* **Python Libraries:**
    * `mysql-connector-python`: For MySQL database interaction.
    * `pyswip`: For interfacing Python with Prolog.
    * `tabulate`: For creating formatted tables in the terminal output.
    * `mailtrap-python`: For sending emails via the Mailtrap service (for testing/development).

## Prerequisites

Before running the application, ensure you have the following installed and configured:

1.  **Python 3:** Version 3.x recommended.
2.  **MySQL Server:** A running MySQL server instance.
3.  **Prolog Interpreter:** SWI-Prolog is commonly used with `pyswip`. Ensure it's installed and accessible in your system's PATH or configured correctly for `pyswip` to find it.
4.  **Database:**
    * Create a MySQL database named `apa_system_db`.
    * Set up the required tables (e.g., `student_info`, `staff_info`, `module_info`, `stud_mod_info`, `faculty_info`, `programme_info`, `student_result`). You will need to define the schema based on the queries in the Python script.
    * Populate the database with necessary sample data for testing.
5.  **Prolog Knowledge Base File:**
    * Create a file named `knowledge_base.pl` in the same directory as the Python script.
    * Define the necessary Prolog facts and rules for GPA calculation and student record processing (e.g., `get_students_total_credits_for_semester`, `get_grade_point_earned_sum`, `get_student_gpa_for_semester_1`, etc.).

## Setup & Installation

1.  **Clone the Repository (if applicable):**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```

2.  **Install Python Dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
    Create a `requirements.txt` file with the following content:
    ```txt
    mysql-connector-python
    pyswip
    tabulate
    mailtrap-python
    ```
    Then install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Database Connection:**
    * **IMPORTANT:** The current code has **hardcoded** database credentials (`root`/`admin` for `localhost`). This is **insecure** and not recommended for production or shared environments.
    * **Recommendation:** Modify the script to use environment variables, a configuration file (e.g., `.env`, `config.ini`), or secure credential management practices.
    * For now, ensure the credentials in the script match your local MySQL setup:
      ```python
      db_connector = connector.connect(
          host="localhost",      # Change if your DB is not local
          user="root",         # Change to your MySQL username
          password="admin",      # Change to your MySQL password
          database="apa_system_db", # Ensure this database exists
      )
      ```

4.  **Configure Mailtrap:**
    * **IMPORTANT:** The current code has a **hardcoded** Mailtrap API token (`17c83627dc411b149aa8e7e009f2ef2f`). This is **insecure**. Anyone with this token can send emails using your Mailtrap quota.
    * **Recommendation:** Replace the hardcoded token with an environment variable or another secure configuration method.
    * Sign up for a Mailtrap account (mailtrap.io) if you don't have one and get your API token. Update the `send_email` function accordingly:
      ```python
      # Replace "YOUR_MAILTRAP_TOKEN" with your actual token or load from config
      client = mt.MailtrapClient(token="YOUR_MAILTRAP_TOKEN")
      client.send(mail)
      ```

5.  **Place Knowledge Base File:**
    * Ensure the `knowledge_base.pl` file containing your Prolog rules is in the same directory as your main Python script (e.g., `main.py`).

## Running the Application

1.  Make sure your MySQL server is running.
2.  Navigate to the project directory in your terminal.
3.  Activate your virtual environment (if using one).
4.  Run the main Python script (assuming it's named `main.py`):
    ```bash
    python main.py
    ```
5.  Follow the prompts in the terminal to log in as a Student or Administrator and use the system.

## How It Works

1.  **Initialization:** The script connects to the MySQL database and the Prolog interpreter, loading the `knowledge_base.pl` file.
2.  **Data Loading:** It fetches initial data (students, modules, records, faculty, programme) from MySQL and asserts these as facts into the Prolog knowledge base.
3.  **Login:** The user selects their role (Student/Admin) and provides credentials, which are validated against the database (`student_info` or `staff_info` table).
4.  **Menu:** Based on the role, the appropriate menu (Student or Admin) is displayed.
5.  **GPA Processing (`process_gpa`):**
    * The user (or admin for a specific student) inputs the desired academic year and optionally a GPA threshold (admin only).
    * The script queries the database/Prolog KB to get total credits and grade points earned for each semester of the specified year.
    * It asserts temporary facts into Prolog (like the target GPA, total credits, total GPEs).
    * It queries Prolog using predefined rules (`get_student_gpa_for_semester_1`, etc.) to calculate Semester 1, Semester 2, and Cumulative GPAs.
    * The results are displayed in a formatted table.
    * The calculated results are saved to the `student_result` table in MySQL.
6.  **Probation Check & Notification:**
    * The calculated cumulative GPA is compared against the relevant threshold (user-defined or default 2.0).
    * If the GPA is below or equal to the threshold, the system indicates probation eligibility.
    * The `notify_stakeholders` function is called, which fetches email addresses for the student, advisor, programme director, and faculty administrator from the database.
    * Formatted emails are constructed and sent via Mailtrap to each stakeholder.

## Database Schema Notes

The application relies on a specific database schema in `apa_system_db`. Key tables inferred from the code include:

* `student_info`: Stores student details (ID, name, email, programme, advisor, password, school/faculty).
* `staff_info`: Stores staff details (ID, name, password, role, email - inferred from usage).
* `module_info`: Stores module details (ID, name, credits).
* `stud_mod_info`: Links students to modules, storing grades/points, semester, and year.
* `faculty_info`: Stores faculty details (ID, name, administrator ID).
* `programme_info`: Stores programme details (ID, name, director ID).
* `student_result`: Stores calculated GPA results (student ID, semester GPAs, credits, year, cumulative GPA).

Ensure your database schema matches the expectations of the queries within the Python script.

## Prolog Knowledge Base (`knowledge_base.pl`)

This file is crucial and must contain the Prolog logic. It should include:

* Dynamic predicate declarations for facts loaded from the database (e.g., `student_info/8`, `student_record/5`, `module_info/3`).
* Dynamic predicate declarations for temporary facts asserted during calculation (e.g., `gpa_is/3`, `student_total_credits_for_semester_1/3`).
* Rules for calculating total credits, total grade points earned, semester GPAs, and cumulative GPA (e.g., `get_students_total_credits_for_semester/4`, `get_grade_point_earned_sum/4`, `get_student_gpa_for_semester_1/3`, `get_total_gpa_for_both_semesters/3`).

## Author

* **Winroy Jennings** - Artificial Intelligence Class Project, University of Technology, Jamaica.

## License

This project is licensed under the MIT License.

**Disclaimer:** This software was developed as part of an AI class project at the University of Technology, Jamaica (as of November 2024). It is intended for educational and demonstration purposes only and should not be used in a production environment without significant review, testing, and modification, particularly concerning security aspects like credential management identified in this README.
