#
# @lc app=leetcode id=3421 lang=python3
#
# [3421] Find Students Who Improved
#
# https://leetcode.com/problems/find-students-who-improved/description/
#
# database
# Medium (49.48%)
# Likes:    114
# Dislikes: 10
# Total Accepted:    32.8K
# Total Submissions: 66.3K
# Testcase Example:  "{\"headers\":{\"Scores\":[\"student_id\",\"subject\",\"score\",\"exam_date\"]},\"rows\":{\"Scores\":[[101,\"Math\",70,\"2023-01-15\"],[101,\"Math\",85,\"2023-02-15\"],[101,\"Physics\",65,\"2023-01-15\"],[101,\"Physics\",60,\"2023-02-15\"],[102,\"Math\",80,\"2023-01-15\"],[102,\"Math\",85,\"2023-02-15\"],[103,\"Math\",90,\"2023-01-15\"],[104,\"Physics\",75,\"2023-01-15\"],[104,\"Physics\",85,\"2023-02-15\"]]}}"
#
#
# Table: Scores
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | student_id  | int     |
# | subject     | varchar |
# | score       | int     |
# | exam_date   | varchar |
# +-------------+---------+
# (student_id, subject, exam_date) is the primary key for this table.
# Each row contains information about a student's score in a specific
# subject on a particular exam date. score is between 0 and 100
# (inclusive).
#
# Write a solution to find the students who have shown improvement. A
# student is considered to have shown improvement if they meet both of
# these conditions:
#
# Have taken exams in the same subject on at least two different dates
#
# Their latest score in that subject is higher than their first score
#
# Return the result table ordered by student_id, subject in ascending
# order.
#
# The result format is in the following example.
#
# Example:
#
# Input:
#
# Scores table:
#
# +------------+----------+-------+------------+
# | student_id | subject  | score | exam_date  |
# +------------+----------+-------+------------+
# | 101        | Math     | 70    | 2023-01-15 |
# | 101        | Math     | 85    | 2023-02-15 |
# | 101        | Physics  | 65    | 2023-01-15 |
# | 101        | Physics  | 60    | 2023-02-15 |
# | 102        | Math     | 80    | 2023-01-15 |
# | 102        | Math     | 85    | 2023-02-15 |
# | 103        | Math     | 90    | 2023-01-15 |
# | 104        | Physics  | 75    | 2023-01-15 |
# | 104        | Physics  | 85    | 2023-02-15 |
# +------------+----------+-------+------------+
#
# Output:
#
# +------------+----------+-------------+--------------+
# | student_id | subject  | first_score | latest_score |
# +------------+----------+-------------+--------------+
# | 101        | Math     | 70          | 85           |
# | 102        | Math     | 80          | 85           |
# | 104        | Physics  | 75          | 85           |
# +------------+----------+-------------+--------------+
#
# Explanation:
#
# Student 101 in Math: Improved from 70 to 85
#
# Student 101 in Physics: No improvement (dropped from 65 to 60)
#
# Student 102 in Math: Improved from 80 to 85
#
# Student 103 in Math: Only one exam, not eligible
#
# Student 104 in Physics: Improved from 75 to 85
#
# Result table is ordered by student_id, subject.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Per (student_id, subject), take the earliest and latest exam scores; keep
        pairs with at least two exams where the latest score is strictly higher.

        Algorithm:
        - Aggregate MIN/MAX exam_date per student+subject (HAVING COUNT >= 2).
        - Join back for first_score and latest_score; filter latest > first.
        - ORDER BY student_id, subject.

        Complexity: O(N log N) with sorts/joins.
        """
        self.sql = """
SELECT
    b.student_id,
    b.subject,
    s1.score AS first_score,
    s2.score AS latest_score
FROM (
    SELECT
        student_id,
        subject,
        MIN(exam_date) AS first_date,
        MAX(exam_date) AS latest_date
    FROM Scores
    GROUP BY student_id, subject
    HAVING COUNT(*) >= 2
) AS b
JOIN Scores AS s1
  ON s1.student_id = b.student_id
 AND s1.subject = b.subject
 AND s1.exam_date = b.first_date
JOIN Scores AS s2
  ON s2.student_id = b.student_id
 AND s2.subject = b.subject
 AND s2.exam_date = b.latest_date
WHERE s2.score > s1.score
ORDER BY b.student_id, b.subject;
"""
        return self.sql
# @lc code=end
