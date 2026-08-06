#
# @lc app=leetcode id=1699 lang=python3
#
# [1699] Number of Calls Between Two Persons
#
# https://leetcode.com/problems/number-of-calls-between-two-persons/description/
#
# database
# Medium (80.79%)
# Likes:    312
# Dislikes: 16
# Total Accepted:    54.2K
# Total Submissions: 67.1K
# Testcase Example:  "{\"headers\":{\"Calls\":[\"from_id\",\"to_id\",\"duration\"]},\"rows\":{\"Calls\":[[1,2,59],[2,1,11],[1,3,20],[3,4,100],[3,4,200],[3,4,200],[4,3,499]]}}"
#
#
# Table: Calls
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | from_id     | int     |
# | to_id       | int     |
# | duration    | int     |
# +-------------+---------+
# This table does not have a primary key (column with unique values), it
# may contain duplicates.
# This table contains the duration of a phone call between from_id and
# to_id.
# from_id != to_id
#
# Write a solution to report the number of calls and the total call
# duration between each pair of distinct persons (person1, person2) where
# person1 < person2.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Calls table:
# +---------+-------+----------+
# | from_id | to_id | duration |
# +---------+-------+----------+
# | 1       | 2     | 59       |
# | 2       | 1     | 11       |
# | 1       | 3     | 20       |
# | 3       | 4     | 100      |
# | 3       | 4     | 200      |
# | 3       | 4     | 200      |
# | 4       | 3     | 499      |
# +---------+-------+----------+
# Output:
# +---------+---------+------------+----------------+
# | person1 | person2 | call_count | total_duration |
# +---------+---------+------------+----------------+
# | 1       | 2       | 2          | 70             |
# | 1       | 3       | 1          | 20             |
# | 3       | 4       | 4          | 999            |
# +---------+---------+------------+----------------+
# Explanation:
# Users 1 and 2 had 2 calls and the total duration is 70 (59 + 11).
# Users 1 and 3 had 1 call and the total duration is 20.
# Users 3 and 4 had 4 calls and the total duration is 999 (100 + 200 + 200
# + 499).
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. For each unordered pair of persons who called each other,
        report person1 < person2, call count, and total duration.

        Algorithm:
        - Normalize (LEAST(from_id,to_id), GREATEST(...)); GROUP BY; SUM(duration).

        Complexity: O(C).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        LEAST(from_id, to_id) AS person1,
        GREATEST(from_id, to_id) AS person2,
        COUNT(*) AS call_count,
        SUM(duration) AS total_duration
    FROM Calls
    GROUP BY LEAST(from_id, to_id), GREATEST(from_id, to_id);
    """
# @lc code=end
