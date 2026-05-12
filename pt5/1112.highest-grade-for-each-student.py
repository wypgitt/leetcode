SQL = """
SELECT
    student_id,
    course_id,
    grade
FROM (
    SELECT
        student_id,
        course_id,
        grade,
        ROW_NUMBER() OVER (
            PARTITION BY student_id
            ORDER BY grade DESC, course_id ASC
        ) AS row_num
    FROM Enrollments
) AS ranked
WHERE row_num = 1
ORDER BY student_id;
"""

