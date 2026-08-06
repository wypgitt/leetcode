#
# @lc app=leetcode id=1412 lang=python3
#
# [1412] Find the Quiet Students in All Exams
#
# https://leetcode.com/problems/find-the-quiet-students-in-all-exams/description/
#
# database
# Hard (58.02%)
# Likes:    228
# Dislikes: 28
# Total Accepted:    36.1K
# Total Submissions: 62.2K
# Testcase Example:  "{\"headers\": {\"Student\": [\"student_id\", \"student_name\"], \"Exam\": [\"exam_id\", \"student_id\", \"score\"]}, \"rows\": {\"Student\": [[1, \"Daniel\"], [2, \"Jade\"], [3, \"Stella\"], [4, \"Jonathan\"], [5, \"Will\"]], \"Exam\": [[10, 1, 70], [10, 2, 80], [10, 3, 90], [20, 1, 80], [30, 1, 70], [30, 3, 80], [30, 4, 90], [40, 1, 60], [40, 2, 70], [40, 4, 80]]}}"
#
#
# Table: Student
#
# +---------------------+---------+
# | Column Name         | Type    |
# +---------------------+---------+
# | student_id          | int     |
# | student_name        | varchar |
# +---------------------+---------+
# student_id is the primary key (column with unique values) for this
# table.
# student_name is the name of the student.
#
# Table: Exam
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | exam_id       | int     |
# | student_id    | int     |
# | score         | int     |
# +---------------+---------+
# (exam_id, student_id) is the primary key (combination of columns with
# unique values) for this table.
# Each row of this table indicates that the student with student_id had a
# score points in the exam with id exam_id.
#
# A quiet student is the one who took at least one exam and did not score
# the highest or the lowest score.
#
# Write a solution to report the students (student_id, student_name) being
# quiet in all exams. Do not return the student who has never taken any
# exam.
#
# Return the result table ordered by student_id.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Student table:
# +-------------+---------------+
# | student_id  | student_name  |
# +-------------+---------------+
# | 1           | Daniel        |
# | 2           | Jade          |
# | 3           | Stella        |
# | 4           | Jonathan      |
# | 5           | Will          |
# +-------------+---------------+
# Exam table:
# +------------+--------------+-----------+
# | exam_id    | student_id   | score     |
# +------------+--------------+-----------+
# | 10         |     1        |    70     |
# | 10         |     2        |    80     |
# | 10         |     3        |    90     |
# | 20         |     1        |    80     |
# | 30         |     1        |    70     |
# | 30         |     3        |    80     |
# | 30         |     4        |    90     |
# | 40         |     1        |    60     |
# | 40         |     2        |    70     |
# | 40         |     4        |    80     |
# +------------+--------------+-----------+
# Output:
# +-------------+---------------+
# | student_id  | student_name  |
# +-------------+---------------+
# | 2           | Jade          |
# +-------------+---------------+
# Explanation:
# For exam 1: Student 1 and 3 hold the lowest and high scores
# respectively.
# For exam 2: Student 1 hold both highest and lowest score.
# For exam 3 and 4: Student 1 and 4 hold the lowest and high scores
# respectively.
# Student 2 and 5 have never got the highest or lowest in any of the
# exams.
# Since student 5 is not taking any exam, he is excluded from the result.
# So, we only return the information of Student 2.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. A quiet student took at least one exam and was never the
        unique highest or unique lowest scorer in any exam they took.
        (Students who never took exams are excluded.)

        Algorithm:
        - Per exam find min/max score; mark students who hit min or max in an exam.
        - Quiet = took >=1 exam and never marked; join Student for names; order by id.

        Complexity: O(E) with aggregations.
        """
        return self.sql

    sql = """
    SELECT s.student_id, s.student_name
    FROM Student s
    WHERE s.student_id IN (SELECT DISTINCT student_id FROM Exam)
      AND s.student_id NOT IN (
        SELECT e.student_id
        FROM Exam e
        JOIN (
            SELECT exam_id, MIN(score) AS mn, MAX(score) AS mx
            FROM Exam
            GROUP BY exam_id
        ) t ON e.exam_id = t.exam_id
        WHERE e.score = t.mn OR e.score = t.mx
      )
    ORDER BY s.student_id;
    """
# @lc code=end
