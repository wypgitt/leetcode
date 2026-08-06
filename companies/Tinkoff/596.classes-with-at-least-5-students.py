#
# @lc app=leetcode id=596 lang=python3
#
# [596] Classes With at Least 5 Students
#
# https://leetcode.com/problems/classes-with-at-least-5-students/description/
#
# algorithms
# Easy (64.52%)
# Likes:    1362
# Dislikes: 1084
# Total Accepted:    950K
# Total Submissions: 1.5M
# Testcase Example:  "{\"headers\": {\"Courses\": [\"student\", \"class\"]}, \"rows\": {\"Courses\": [[\"A\", \"Math\"], [\"B\", \"English\"], [\"C\", \"Math\"], [\"D\", \"Biology\"], [\"E\", \"Math\"], [\"F\", \"Computer\"], [\"G\", \"Math\"], [\"H\", \"Math\"], [\"I\", \"Math\"]]}}"
#
# Table: Courses
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | student | varchar |
# | class | varchar |
# +-------------+---------+
# (student, class) is the primary key (combination of columns with unique
# values) for this table.
# Each row of this table indicates the name of a student and the class in which
# they are enrolled.
#
# Write a solution to find all the classes that have at least five students.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Courses table:
# +---------+----------+
# | student | class |
# +---------+----------+
# | A | Math |
# | B | English |
# | C | Math |
# | D | Biology |
# | E | Math |
# | F | Computer |
# | G | Math |
# | H | Math |
# | I | Math |
# +---------+----------+
# Output:
# +---------+
# | class |
# +---------+
# | Math |
# +---------+
# Explanation:
# - Math has 6 students, so we include it.
# - English has 1 student, so we do not include it.
# - Biology has 1 student, so we do not include it.
# - Computer has 1 student, so we do not include it.
#


# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Count students per class and keep classes with at least 5 students.

        Algorithm:
        - GROUP BY class HAVING COUNT(*) >= 5 (or COUNT(DISTINCT student) if needed).
        - SELECT class.

        Complexity: O(C) scan/group over Courses.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT class
    FROM Courses
    GROUP BY class
    HAVING COUNT(*) >= 5;
    """
# @lc code=end

