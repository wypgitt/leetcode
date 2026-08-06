#
# @lc app=leetcode id=619 lang=python3
#
# [619] Biggest Single Number
#
# https://leetcode.com/problems/biggest-single-number/description/
#
# algorithms
# Easy (71.85%)
# Likes:    1027
# Dislikes: 203
# Total Accepted:    611K
# Total Submissions: 850K
# Testcase Example:  "{\"headers\": {\"MyNumbers\": [\"num\"]}, \"rows\": {\"MyNumbers\": [[8],[8],[3],[3],[1],[4],[5],[6]]}}"
#
# Table: MyNumbers
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | num | int |
# +-------------+------+
# This table may contain duplicates (In other words, there is no primary key
# for this table in SQL).
# Each row of this table contains an integer.
#
# A single number is a number that appeared only once in the MyNumbers table.
#
# Find the largest single number. If there is no single number, report null.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# MyNumbers table:
# +-----+
# | num |
# +-----+
# | 8 |
# | 8 |
# | 3 |
# | 3 |
# | 1 |
# | 4 |
# | 5 |
# | 6 |
# +-----+
# Output:
# +-----+
# | num |
# +-----+
# | 6 |
# +-----+
# Explanation: The single numbers are 1, 4, 5, and 6.
# Since 6 is the largest single number, we return it.
#
# Example 2:
#
# Input:
# MyNumbers table:
# +-----+
# | num |
# +-----+
# | 8 |
# | 8 |
# | 7 |
# | 7 |
# | 3 |
# | 3 |
# | 3 |
# +-----+
# Output:
# +------+
# | num |
# +------+
# | null |
# +------+
# Explanation: There are no single numbers in the input table so we return
# null.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Largest number that appears exactly once (single number). NULL if none.

        Algorithm:
        - GROUP BY num HAVING COUNT(*) = 1; outer MAX(num).

        Complexity: O(N).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT MAX(num) AS num
    FROM (
        SELECT num
        FROM MyNumbers
        GROUP BY num
        HAVING COUNT(*) = 1
    ) t;
    """
# @lc code=end
