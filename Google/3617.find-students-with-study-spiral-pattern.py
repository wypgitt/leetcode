#
# @lc app=leetcode id=3617 lang=python3
#
# [3617] Find Students with Study Spiral Pattern
#
# https://leetcode.com/problems/find-students-with-study-spiral-pattern/description/
#
# database
# Hard (24.03%)
# Likes:    41
# Dislikes: 13
# Total Accepted:    4.7K
# Total Submissions: 19.7K
# Testcase Example:  "{\"headers\":{\"students\":[\"student_id\",\"student_name\",\"major\"],\"study_sessions\":[\"session_id\",\"student_id\",\"subject\",\"session_date\",\"hours_studied\"]},\"rows\":{\"students\":[[1,\"Alice Chen\",\"Computer Science\"],[2,\"Bob Johnson\",\"Mathematics\"],[3,\"Carol Davis\",\"Physics\"],[4,\"David Wilson\",\"Chemistry\"],[5,\"Emma Brown\",\"Biology\"]],\"study_sessions\":[[1,1,\"Math\",\"2023-10-01\",2.5],[2,1,\"Physics\",\"2023-10-02\",3.0],[3,1,\"Chemistry\",\"2023-10-03\",2.0],[4,1,\"Math\",\"2023-10-04\",2.5],[5,1,\"Physics\",\"2023-10-05\",3.0],[6,1,\"Chemistry\",\"2023-10-06\",2.0],[7,2,\"Algebra\",\"2023-10-01\",4.0],[8,2,\"Calculus\",\"2023-10-02\",3.5],[9,2,\"Statistics\",\"2023-10-03\",2.5],[10,2,\"Geometry\",\"2023-10-04\",3.0],[11,2,\"Algebra\",\"2023-10-05\",4.0],[12,2,\"Calculus\",\"2023-10-06\",3.5],[13,2,\"Statistics\",\"2023-10-07\",2.5],[14,2,\"Geometry\",\"2023-10-08\",3.0],[15,3,\"Biology\",\"2023-10-01\",2.0],[16,3,\"Chemistry\",\"2023-10-02\",2.5],[17,3,\"Biology\",\"2023-10-03\",2.0],[18,3,\"Chemistry\",\"2023-10-04\",2.5],[19,4,\"Organic\",\"2023-10-01\",3.0],[20,4,\"Physical\",\"2023-10-05\",2.5]]}}"
#
#
# Table: students
#
# +--------------+---------+
# | Column Name  | Type    |
# +--------------+---------+
# | student_id   | int     |
# | student_name | varchar |
# | major        | varchar |
# +--------------+---------+
# student_id is the unique identifier for this table.
# Each row contains information about a student and their academic major.
#
# Table: study_sessions
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | session_id    | int     |
# | student_id    | int     |
# | subject       | varchar |
# | session_date  | date    |
# | hours_studied | decimal |
# +---------------+---------+
# session_id is the unique identifier for this table.
# Each row represents a study session by a student for a specific subject.
#
# Write a solution to find students who follow the Study Spiral Pattern -
# students who consistently study multiple subjects in a rotating cycle.
#
# A Study Spiral Pattern means a student studies at least 3 different
# subjects in a repeating sequence
#
# The pattern must repeat for at least 2 complete cycles (minimum 6 study
# sessions)
#
# Sessions must be consecutive dates with no gaps longer than 2 days
# between sessions
#
# Calculate the cycle length (number of different subjects in the pattern)
#
# Calculate the total study hours across all sessions in the pattern
#
# Only include students with cycle length of at least 3 subjects
#
# Return the result table ordered by cycle length in descending order,
# then by total study hours in descending order.
#
# The result format is in the following example.
#
# Example:
#
# Input:
#
# students table:
#
# +------------+--------------+------------------+
# | student_id | student_name | major            |
# +------------+--------------+------------------+
# | 1          | Alice Chen   | Computer Science |
# | 2          | Bob Johnson  | Mathematics      |
# | 3          | Carol Davis  | Physics          |
# | 4          | David Wilson | Chemistry        |
# | 5          | Emma Brown   | Biology          |
# +------------+--------------+------------------+
#
# study_sessions table:
#
# +------------+------------+------------+--------------+---------------+
# | session_id | student_id | subject    | session_date | hours_studied |
# +------------+------------+------------+--------------+---------------+
# | 1          | 1          | Math       | 2023-10-01   | 2.5           |
# | 2          | 1          | Physics    | 2023-10-02   | 3.0           |
# | 3          | 1          | Chemistry  | 2023-10-03   | 2.0           |
# | 4          | 1          | Math       | 2023-10-04   | 2.5           |
# | 5          | 1          | Physics    | 2023-10-05   | 3.0           |
# | 6          | 1          | Chemistry  | 2023-10-06   | 2.0           |
# | 7          | 2          | Algebra    | 2023-10-01   | 4.0           |
# | 8          | 2          | Calculus   | 2023-10-02   | 3.5           |
# | 9          | 2          | Statistics | 2023-10-03   | 2.5           |
# | 10         | 2          | Geometry   | 2023-10-04   | 3.0           |
# | 11         | 2          | Algebra    | 2023-10-05   | 4.0           |
# | 12         | 2          | Calculus   | 2023-10-06   | 3.5           |
# | 13         | 2          | Statistics | 2023-10-07   | 2.5           |
# | 14         | 2          | Geometry   | 2023-10-08   | 3.0           |
# | 15         | 3          | Biology    | 2023-10-01   | 2.0           |
# | 16         | 3          | Chemistry  | 2023-10-02   | 2.5           |
# | 17         | 3          | Biology    | 2023-10-03   | 2.0           |
# | 18         | 3          | Chemistry  | 2023-10-04   | 2.5           |
# | 19         | 4          | Organic    | 2023-10-01   | 3.0           |
# | 20         | 4          | Physical   | 2023-10-05   | 2.5           |
# +------------+------------+------------+--------------+---------------+
#
# Output:
#
# +------------+--------------+------------------+--------------+-------------------+
# | student_id | student_name | major            | cycle_length |
# total_study_hours |
# +------------+--------------+------------------+--------------+-------------------+
# | 2          | Bob Johnson  | Mathematics      | 4            | 26.0
# |
# | 1          | Alice Chen   | Computer Science | 3            | 15.0
# |
# +------------+--------------+------------------+--------------+-------------------+
#
# Explanation:
#
# Alice Chen (student_id = 1):
#
# Study sequence: Math → Physics → Chemistry → Math → Physics → Chemistry
#
# Pattern: 3 subjects (Math, Physics, Chemistry) repeating for 2 complete
# cycles
#
# Consecutive dates: Oct 1-6 with no gaps > 2 days
#
# Cycle length: 3 subjects
#
# Total hours: 2.5 + 3.0 + 2.0 + 2.5 + 3.0 + 2.0 = 15.0 hours
#
# Bob Johnson (student_id = 2):
#
# Study sequence: Algebra → Calculus → Statistics → Geometry → Algebra →
# Calculus → Statistics → Geometry
#
# Pattern: 4 subjects (Algebra, Calculus, Statistics, Geometry) repeating
# for 2 complete cycles
#
# Consecutive dates: Oct 1-8 with no gaps > 2 days
#
# Cycle length: 4 subjects
#
# Total hours: 4.0 + 3.5 + 2.5 + 3.0 + 4.0 + 3.5 + 2.5 + 3.0 = 26.0 hours
#
# Students not included:
#
# Carol Davis (student_id = 3): Only 2 subjects (Biology, Chemistry) -
# doesn't meet minimum 3 subjects requirement
#
# David Wilson (student_id = 4): Only 2 study sessions with a 4-day gap -
# doesn't meet consecutive dates requirement
#
# Emma Brown (student_id = 5): No study sessions recorded
#
# The result table is ordered by cycle_length in descending order, then by
# total_study_hours in descending order.
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Find students whose consecutive sessions (gaps ≤ 2 days) form a
        repeating subject cycle of length ≥ 3 for ≥ 2 full periods.

        Algorithm:
        - LAG gaps; split into contiguous groups where gap ≤ 2.
        - GROUP_CONCAT subjects; require sessions ≥ 6, distinct ≥ 3,
          sessions % cycle_length = 0, and REPEAT(prefix) matches the sequence.
        - Join students; order by cycle_length DESC, hours DESC.

        Complexity: O(S log S) window/sort work over sessions.
        """
        self.sql = """
WITH gaps_cte AS (
    SELECT
        student_id,
        subject,
        session_date,
        hours_studied,
        DATEDIFF(
            session_date,
            LAG(session_date) OVER (
                PARTITION BY student_id ORDER BY session_date
            )
        ) AS gap
    FROM study_sessions
),
groups_cte AS (
    SELECT
        student_id,
        subject,
        session_date,
        hours_studied,
        SUM(CASE WHEN gap IS NULL OR gap > 2 THEN 1 ELSE 0 END) OVER (
            PARTITION BY student_id ORDER BY session_date
        ) AS group_id
    FROM gaps_cte
),
patterns_cte AS (
    SELECT
        g.student_id,
        g.group_id,
        GROUP_CONCAT(g.subject ORDER BY g.session_date SEPARATOR ',') AS seq,
        COUNT(*) AS total_sessions,
        COUNT(DISTINCT g.subject) AS cycle_length,
        ROUND(SUM(g.hours_studied), 1) AS total_study_hours
    FROM groups_cte g
    GROUP BY g.student_id, g.group_id
    HAVING total_sessions >= 6
       AND cycle_length >= 3
       AND total_sessions % cycle_length = 0
       AND REPEAT(
             CONCAT(SUBSTRING_INDEX(seq, ',', cycle_length), ','),
             total_sessions / cycle_length
           ) = CONCAT(seq, ',')
)
SELECT
    p.student_id,
    s.student_name,
    s.major,
    p.cycle_length,
    p.total_study_hours
FROM patterns_cte p
INNER JOIN students s ON p.student_id = s.student_id
ORDER BY p.cycle_length DESC, p.total_study_hours DESC;
"""
        return self.sql
# @lc code=end
