#
# @lc app=leetcode id=2346 lang=python3
#
# [2346] Compute the Rank as a Percentage
#
# https://leetcode.com/problems/compute-the-rank-as-a-percentage/description/
#
# database
# Medium (33.91%)
# Likes:    32
# Dislikes: 80
# Total Accepted:    7.7K
# Total Submissions: 22.7K
# Testcase Example:  "{\"headers\": {\"Students\": [\"student_id\", \"department_id\", \"mark\"]}, \"rows\": {\"Students\": [[2, 2, 650], [8, 2, 650], [7, 1, 920], [1, 1, 610], [3, 1, 530]]}}"
#
#
# Table: Students
#
# +---------------+------+
# | Column Name   | Type |
# +---------------+------+
# | student_id    | int  |
# | department_id | int  |
# | mark          | int  |
# +---------------+------+
# student_id contains unique values.
# Each row of this table indicates a student's ID, the ID of the
# department in which the student enrolled, and their mark in the exam.
#
# Write a solution to report the rank of each student in their department
# as a percentage, where the rank as a percentage is computed using the
# following formula: (student_rank_in_the_department - 1) * 100 /
# (the_number_of_students_in_the_department - 1). The percentage should be
# rounded to 2 decimal places. student_rank_in_the_department is
# determined by descending mark, such that the student with the highest
# mark is rank 1. If two students get the same mark, they also get the
# same rank.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Students table:
# +------------+---------------+------+
# | student_id | department_id | mark |
# +------------+---------------+------+
# | 2          | 2             | 650  |
# | 8          | 2             | 650  |
# | 7          | 1             | 920  |
# | 1          | 1             | 610  |
# | 3          | 1             | 530  |
# +------------+---------------+------+
# Output:
# +------------+---------------+------------+
# | student_id | department_id | percentage |
# +------------+---------------+------------+
# | 7          | 1             | 0.0        |
# | 1          | 1             | 50.0       |
# | 3          | 1             | 100.0      |
# | 2          | 2             | 0.0        |
# | 8          | 2             | 0.0        |
# +------------+---------------+------------+
# Explanation:
# For Department 1:
#  - Student 7: percentage = (1 - 1) * 100 / (3 - 1) = 0.0
#  - Student 1: percentage = (2 - 1) * 100 / (3 - 1) = 50.0
#  - Student 3: percentage = (3 - 1) * 100 / (3 - 1) = 100.0
# For Department 2:
#  - Student 2: percentage = (1 - 1) * 100 / (2 - 1) = 0.0
#  - Student 8: percentage = (1 - 1) * 100 / (2 - 1) = 0.0
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        SQL: Students(student_id, department_id, mark). Percentage rank in
        department: (rank-1)*100/(cnt-1), rank by mark DESC (ties same rank),
        rounded to 2 decimals; 0 if department size 1.

        Algorithm:
        - RANK() and COUNT() window functions; IFNULL for single-student depts.

        Complexity: O(N log N).
        """
        self.sql = """
SELECT
    student_id,
    department_id,
    IFNULL(
        ROUND(
            (RANK() OVER (PARTITION BY department_id ORDER BY mark DESC) - 1) * 100
            / (COUNT(1) OVER (PARTITION BY department_id) - 1),
            2
        ),
        0
    ) AS percentage
FROM Students;
"""
        return self.sql
# @lc code=end
