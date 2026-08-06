#
# @lc app=leetcode id=626 lang=python3
#
# [626] Exchange Seats
#
# https://leetcode.com/problems/exchange-seats/description/
#
# algorithms
# Medium (74.61%)
# Likes:    1950
# Dislikes: 614
# Total Accepted:    489K
# Total Submissions: 655K
# Testcase Example:  "{\"headers\": {\"Seat\": [\"id\",\"student\"]}, \"rows\": {\"Seat\": [[1,\"Abbot\"],[2,\"Doris\"],[3,\"Emerson\"],[4,\"Green\"],[5,\"Jeames\"]]}}"
#
# Table: Seat
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | id | int |
# | student | varchar |
# +-------------+---------+
# id is the primary key (unique value) column for this table.
# Each row of this table indicates the name and the ID of a student.
# The ID sequence always starts from 1 and increments continuously.
#
# Write a solution to swap the seat id of every two consecutive students. If
# the number of students is odd, the id of the last student is not swapped.
#
# Return the result table ordered by id in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Seat table:
# +----+---------+
# | id | student |
# +----+---------+
# | 1 | Abbot |
# | 2 | Doris |
# | 3 | Emerson |
# | 4 | Green |
# | 5 | Jeames |
# +----+---------+
# Output:
# +----+---------+
# | id | student |
# +----+---------+
# | 1 | Doris |
# | 2 | Abbot |
# | 3 | Green |
# | 4 | Emerson |
# | 5 | Jeames |
# +----+---------+
# Explanation:
# Note that if the number of students is odd, there is no need to change the
# last one's seat.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Swap every two consecutive students by seat id; last odd seat stays put.

        Algorithm:
        - Odd id → id+1 if exists; even id → id-1; else keep id.
        - ORDER BY new id.

        Complexity: O(N).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        CASE
            WHEN id % 2 = 1 AND id + 1 <= (SELECT MAX(id) FROM Seat) THEN id + 1
            WHEN id % 2 = 0 THEN id - 1
            ELSE id
        END AS id,
        student
    FROM Seat
    ORDER BY id;
    """
# @lc code=end
