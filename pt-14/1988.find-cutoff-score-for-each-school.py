#
# @lc app=leetcode id=1988 lang=python3
#
# [1988] Find Cutoff Score for Each School
#
# https://leetcode.com/problems/find-cutoff-score-for-each-school/description/
#
# database
# Medium (67.05%)
# Likes:    83
# Dislikes: 162
# Total Accepted:    14.3K
# Total Submissions: 21.4K
# Testcase Example:  "{\"headers\":{\"Schools\":[\"school_id\",\"capacity\"],\"Exam\":[\"score\",\"student_count\"]},\"rows\":{\"Schools\":[[11,151],[5,48],[9,9],[10,99]],\"Exam\":[[975,10],[966,60],[844,76],[749,76],[744,100]]}}"
#
#
# Table: Schools
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | school_id   | int  |
# | capacity    | int  |
# +-------------+------+
# school_id is the column with unique values for this table.
# This table contains information about the capacity of some schools. The
# capacity is the maximum number of students the school can accept.
#
# Table: Exam
#
# +---------------+------+
# | Column Name   | Type |
# +---------------+------+
# | score         | int  |
# | student_count | int  |
# +---------------+------+
# score is the column with unique values for this table.
# Each row in this table indicates that there are student_count students
# that got at least score points in the exam.
# The data in this table will be logically correct, meaning a row
# recording a higher score will have the same or smaller student_count
# compared to a row recording a lower score. More formally, for every two
# rows i and j in the table, if score_i > score_j then student_count_i <=
# student_count_j.
#
# Every year, each school announces a minimum score requirement that a
# student needs to apply to it. The school chooses the minimum score
# requirement based on the exam results of all the students:
#
# They want to ensure that even if every student meeting the requirement
# applies, the school can accept everyone.
#
# They also want to maximize the possible number of students that can
# apply.
#
# They must use a score that is in the Exam table.
#
# Write a solution to report the minimum score requirement for each
# school. If there are multiple score values satisfying the above
# conditions, choose the smallest one. If the input data is not enough to
# determine the score, report -1.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Schools table:
# +-----------+----------+
# | school_id | capacity |
# +-----------+----------+
# | 11        | 151      |
# | 5         | 48       |
# | 9         | 9        |
# | 10        | 99       |
# +-----------+----------+
# Exam table:
# +-------+---------------+
# | score | student_count |
# +-------+---------------+
# | 975   | 10            |
# | 966   | 60            |
# | 844   | 76            |
# | 749   | 76            |
# | 744   | 100           |
# +-------+---------------+
# Output:
# +-----------+-------+
# | school_id | score |
# +-----------+-------+
# | 5         | 975   |
# | 9         | -1    |
# | 10        | 749   |
# | 11        | 744   |
# +-----------+-------+
# Explanation:
# - School 5: The school's capacity is 48. Choosing 975 as the min score
# requirement, the school will get at most 10 applications, which is
# within capacity.
# - School 10: The school's capacity is 99. Choosing 844 or 749 as the min
# score requirement, the school will get at most 76 applications, which is
# within capacity. We choose the smallest of them, which is 749.
# - School 11: The school's capacity is 151. Choosing 744 as the min score
# requirement, the school will get at most 100 applications, which is
# within capacity.
# - School 9: The data given is not enough to determine the min score
# requirement. Choosing 975 as the min score, the school may get 10
# requests while its capacity is 9. We do not have information about
# higher scores, hence we report -1.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. For each school with capacity, min exam score such that
        the count of students scoring >= that score is at least capacity.
        If impossible, cutoff = -1.

        Algorithm:
        - Suffix student counts by descending score; for each school pick the
          minimal score whose suffix count >= capacity (or -1).

        Complexity: O((E+S) log E) with joins/windows.
        """
        return self.sql

    sql = """
    WITH ordered AS (
        SELECT score, student_count,
               SUM(student_count) OVER (ORDER BY score DESC) AS suf
        FROM Exam
    )
    SELECT s.school_id,
           COALESCE(
               (SELECT MIN(o.score)
                FROM ordered o
                WHERE o.suf >= s.capacity),
               -1
           ) AS score
    FROM Schools s
    ORDER BY s.school_id;
    """

    def solve_join(self) -> str:
        """
        Interview explanation:
        Alternate: cross/join schools to scores with suf >= capacity; MIN score
        per school; UNION schools with no match as -1.

        Algorithm:
        - CTE suffix counts; LEFT JOIN + GROUP BY school_id with COALESCE(-1).

        Complexity: O(S*E) worst-case join.
        """
        return self.sql_join

    sql_join = """
    WITH ordered AS (
        SELECT score,
               SUM(student_count) OVER (ORDER BY score DESC) AS suf
        FROM Exam
    )
    SELECT s.school_id, COALESCE(MIN(o.score), -1) AS score
    FROM Schools s
    LEFT JOIN ordered o ON o.suf >= s.capacity
    GROUP BY s.school_id
    ORDER BY s.school_id;
    """
# @lc code=end

