#
# @lc app=leetcode id=1285 lang=python3
#
# [1285] Find the Start and End Number of Continuous Ranges
#
# https://leetcode.com/problems/find-the-start-and-end-number-of-continuous-ranges/description/
#
# database
# Medium (81.91%)
# Likes:    593
# Dislikes: 36
# Total Accepted:    50.8K
# Total Submissions: 62K
# Testcase Example:  "{\"headers\":{\"Logs\":[\"log_id\"]},\"rows\":{\"Logs\":[[1],[2],[3],[7],[8],[10]]}}"
#
#
# Table: Logs
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | log_id        | int     |
# +---------------+---------+
# log_id is the column of unique values for this table.
# Each row of this table contains the ID in a log Table.
#
# Write a solution to find the start and end number of continuous ranges
# in the table Logs.
#
# Return the result table ordered by start_id.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Logs table:
# +------------+
# | log_id     |
# +------------+
# | 1          |
# | 2          |
# | 3          |
# | 7          |
# | 8          |
# | 10         |
# +------------+
# Output:
# +------------+--------------+
# | start_id   | end_id       |
# +------------+--------------+
# | 1          | 3            |
# | 7          | 8            |
# | 10         | 10           |
# +------------+--------------+
# Explanation:
# The result table should contain all ranges in table Logs.
# From 1 to 3 is contained in the table.
# From 4 to 6 is missing in the table
# From 7 to 8 is contained in the table.
# Number 9 is missing from the table.
# Number 10 is contained in the table.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. Find continuous ranges in Logs (consecutive log_id values).
        Group by (log_id - row_number) island key; MIN/MAX per group.

        Algorithm:
        - WITH ordered rows: rn = ROW_NUMBER() OVER (ORDER BY log_id).
        - Group by log_id - rn; SELECT MIN as start_id, MAX as end_id.
        - ORDER BY start_id.

        Complexity: O(N log N) for window sort.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT MIN(log_id) AS start_id, MAX(log_id) AS end_id
    FROM (
        SELECT
            log_id,
            log_id - ROW_NUMBER() OVER (ORDER BY log_id) AS grp
        FROM Logs
    ) t
    GROUP BY grp
    ORDER BY start_id;
    """
# @lc code=end
