% Dynamic Predicates: These predicates can be dynamically added or removed during program execution.
:- dynamic calculate_student_gpa/1.
:- dynamic student_info/3.
:- dynamic module_info/3.
:- dynamic student_record/5.
:- dynamic faculty_info/3.
:- dynamic programme_info/3.

:- dynamic student_total_credits_for_semester_1/3.
:- dynamic student_total_credits_for_semester_2/3.

:- dynamic get_students_total_credits_for_semester/4.
:- dynamic get_grade_point_earned_sum/4.

:- dynamic student_total_grade_point_earned_for_semester_1/3.
:- dynamic student_total_grade_point_earned_for_semester_2/3.

:- dynamic get_student_gpa_for_semester_1/3.
:- dynamic get_student_gpa_for_semester_2/3.

:- dynamic gpa_is/3.

:- dynamic get_total_gpa_for_both_semesters/3.

% Facts: These are the base cases or known information about the grading system.
grading_system(grade('A+'),grade_point(4.3), percentage_scale('90.00 - 100')).
% ... other grading system facts ...

% Rules: These are the logical rules that define how to calculate GPA and other related information.

% Rule to check if a student's GPA needs to be calculated.
get_calculate_gpa(A):- calculate_student_gpa(A).

% Rule to calculate the total credits earned by a student for a specific semester.
get_students_total_credits_for_semester(StudentID, DesiredYear, Semester, TotalCredits) :-
    % Aggregate all credits from student_record and module_info for the given student, year, and semester.
    aggregate_all(sum(Credits),
        (student_record(ModuleID, Semester, StudentID, _, DesiredYear),
         module_info(ModuleID, _, Credits)),
        TotalCredits).

% Rule to calculate the total grade points earned by a student for a specific semester.
get_grade_point_earned_sum(StudentID, DesiredYear, Semester, TotalGradePointEarned) :-
    % Aggregate all grade points earned from student_record and module_info for the given student, year, and semester.
    aggregate_all(sum(GradePointEarned),
        (student_record(ModuleID, Semester, StudentID, GradePoint, DesiredYear),
         module_info(ModuleID, _, Credits),
         GradePointEarned is GradePoint * Credits),
        TotalGradePointEarned).

% Rule to calculate the GPA for Semester 1.
get_student_gpa_for_semester_1(StudentID, DesiredYear, Semester1TotalGPA) :-
    student_total_grade_point_earned_for_semester_1(StudentID, DesiredYear, TotalGradePointEarned),
    student_total_credits_for_semester_1(StudentID, DesiredYear, TotalCredits),
    Semester1TotalGPA is TotalGradePointEarned / TotalCredits.

% Rule to calculate the GPA for Semester 2.
get_student_gpa_for_semester_2(StudentID, DesiredYear, Semester2TotalGPA) :-
    student_total_grade_point_earned_for_semester_2(StudentID, DesiredYear, TotalGradePointEarned),
    student_total_credits_for_semester_2(StudentID, DesiredYear, TotalCredits),
    Semester2TotalGPA is TotalGradePointEarned / TotalCredits.

% Rule to calculate the cumulative GPA for both semesters.
get_total_gpa_for_both_semesters(StudentID, DesiredYear, CumulativeGPA) :-
    student_total_grade_point_earned_for_semester_1(StudentID, DesiredYear, TotalGradePointEarned1),
    student_total_grade_point_earned_for_semester_2(StudentID, DesiredYear, TotalGradePointEarned2),
    student_total_credits_for_semester_1(StudentID, DesiredYear, TotalCredits1),
    student_total_credits_for_semester_2(StudentID, DesiredYear, TotalCredits2),
    CumulativeGPA is (TotalGradePointEarned1 + TotalGradePointEarned2) / (TotalCredits1 + TotalCredits2).