#
# @lc app=leetcode id=2356 lang=python3
#
# [2356] Number of Unique Subjects Taught by Each Teacher
#
# https://leetcode.com/problems/number-of-unique-subjects-taught-by-each-teacher/description/
#
# algorithms
# Easy (89.24%)
# Likes:    778
# Dislikes: 57
# Total Accepted:    566.5K
# Total Submissions: 634.8K
# Testcase Example:  "{\"headers\":{\"Teacher\":[\"teacher_id\",\"subject_id\",\"dept_id\"]},\"rows\":{\"Teacher\":[[1,2,3],[1,2,4],[1,3,3],[2,1,1],[2,2,1],[2,3,1],[2,4,1]]}}"
#
# Table: Teacher
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | teacher_id  | int  |
# | subject_id  | int  |
# | dept_id     | int  |
# +-------------+------+
# (subject_id, dept_id) is the primary key (combinations of columns with unique
# values) of this table.
# Each row in this table indicates that the teacher with teacher_id teaches the
# subject subject_id in the department dept_id.
#
#
#
# Write a solution to calculate the number of unique subjects each teacher
# teaches in the university.
#
# Return the result table in any order.
#
# The result format is shown in the following example.
#
#
#
# Example 1:
#
# Input:
# Teacher table:
# +------------+------------+---------+
# | teacher_id | subject_id | dept_id |
# +------------+------------+---------+
# | 1          | 2          | 3       |
# | 1          | 2          | 4       |
# | 1          | 3          | 3       |
# | 2          | 1          | 1       |
# | 2          | 2          | 1       |
# | 2          | 3          | 1       |
# | 2          | 4          | 1       |
# +------------+------------+---------+
# Output:
# +------------+-----+
# | teacher_id | cnt |
# +------------+-----+
# | 1          | 2   |
# | 2          | 4   |
# +------------+-----+
# Explanation:
# Teacher 1:
#   - They teach subject 2 in departments 3 and 4.
#   - They teach subject 3 in department 3.
# Teacher 2:
#   - They teach subject 1 in department 1.
#   - They teach subject 2 in department 1.
#   - They teach subject 3 in department 1.
#   - They teach subject 4 in department 1.
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        SQL: Teacher(teacher_id, subject_id, dept_id). Count unique subjects
        taught by each teacher.

        Algorithm:
        - GROUP BY teacher_id; COUNT(DISTINCT subject_id) AS cnt.

        Complexity: O(N).
        """
        self.sql = """
SELECT teacher_id, COUNT(DISTINCT subject_id) AS cnt
FROM Teacher
GROUP BY teacher_id;
"""
        return self.sql
# @lc code=end
