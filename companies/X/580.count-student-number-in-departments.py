#
# SQL solution stored in a Python file for this repository.
#

SOLUTION_SQL = """
SELECT d.dept_name, COUNT(s.student_id) AS student_number
FROM Department d
LEFT JOIN Student s ON s.dept_id = d.dept_id
GROUP BY d.dept_id, d.dept_name
ORDER BY student_number DESC, d.dept_name;
"""

"""
Interview explanation:
Departments with zero students must appear, so start from Department and LEFT JOIN Student. COUNT(student_id) counts only matched students. Sort by descending count and then department name as required.

Edge cases: LEFT JOIN is used whenever zero-count rows must remain; COUNT(DISTINCT ...) is used where duplicate relationships could distort the logical count.
"""
