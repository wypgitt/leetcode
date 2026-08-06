#
# @lc app=leetcode id=1112 lang=python3
#
# [1112] Highest Grade For Each Student
#
# https://leetcode.com/problems/highest-grade-for-each-student/description/
#
# database
# Medium (71.21%)
# Likes:    316
# Dislikes: 15
# Total Accepted:    79.9K
# Total Submissions: 112.2K
# Testcase Example:  "{\"headers\":{\"Enrollments\":[\"student_id\",\"course_id\",\"grade\"]},\"rows\":{\"Enrollments\":[[2,2,95],[2,3,95],[1,1,90],[1,2,99],[3,1,80],[3,2,75],[3,3,82]]}}"
#
#
# Table: Enrollments
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | student_id    | int     |
# | course_id     | int     |
# | grade         | int     |
# +---------------+---------+
# (student_id, course_id) is the primary key (combination of columns with
# unique values) of this table.
# grade is never NULL.
#
# Write a solution to find the highest grade with its corresponding course
# for each student. In case of a tie, you should find the course with the
# smallest course_id.
#
# Return the result table ordered by student_id in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Enrollments table:
# +------------+-------------------+
# | student_id | course_id | grade |
# +------------+-----------+-------+
# | 2          | 2         | 95    |
# | 2          | 3         | 95    |
# | 1          | 1         | 90    |
# | 1          | 2         | 99    |
# | 3          | 1         | 80    |
# | 3          | 2         | 75    |
# | 3          | 3         | 82    |
# +------------+-----------+-------+
# Output:
# +------------+-------------------+
# | student_id | course_id | grade |
# +------------+-----------+-------+
# | 1          | 2         | 99    |
# | 2          | 2         | 95    |
# | 3          | 3         | 82    |
# +------------+-----------+-------+
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. For each student, the course with the highest grade; ties
        break by smallest course_id. Order by student_id.

        Algorithm:
        - ROW_NUMBER() PARTITION BY student_id ORDER BY grade DESC, course_id ASC.
        - Keep rn = 1.

        Complexity: O(N log N) ranking.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT student_id, course_id, grade
    FROM (
        SELECT student_id, course_id, grade,
               ROW_NUMBER() OVER (
                   PARTITION BY student_id
                   ORDER BY grade DESC, course_id ASC
               ) AS rn
        FROM Enrollments
    ) t
    WHERE rn = 1
    ORDER BY student_id;
    """
# @lc code=end
