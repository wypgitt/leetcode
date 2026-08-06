#
# @lc app=leetcode id=571 lang=python3
#
# [571] Find Median Given Frequency of Numbers
#
# https://leetcode.com/problems/find-median-given-frequency-of-numbers/description/
#
# database
# Hard (42.18%)
# Likes:    321
# Dislikes: 79
# Total Accepted:    36.8K
# Total Submissions: 87.2K
# Testcase Example:  "{\"headers\": {\"Numbers\": [\"num\", \"frequency\"]}, \"rows\": {\"Numbers\": [[0, 7], [1, 1], [2, 3], [3, 1]]}}"
#
#
# Table: Numbers
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | num         | int  |
# | frequency   | int  |
# +-------------+------+
# num is the primary key (column with unique values) for this table.
# Each row of this table shows the frequency of a number in the database.
#
# The median is the value separating the higher half from the lower half
# of a data sample.
#
# Write a solution to report the median of all the numbers in the database
# after decompressing the Numbers table. Round the median to one decimal
# point.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Numbers table:
# +-----+-----------+
# | num | frequency |
# +-----+-----------+
# | 0   | 7         |
# | 1   | 1         |
# | 2   | 3         |
# | 3   | 1         |
# +-----+-----------+
# Output:
# +--------+
# | median |
# +--------+
# | 0.0    |
# +--------+
# Explanation:
# If we decompress the Numbers table, we will get [0, 0, 0, 0, 0, 0, 0, 1,
# 2, 2, 2, 3], so the median is (0 + 0) / 2 = 0.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium: Numbers stores value + Frequency of a sorted multiset. The
        median is the middle element (average of two middles if even length).
        Use cumulative frequency to find which Number(s) cover position
        total/2 (and the next when needed); AVG handles odd/even.

        Algorithm:
        - Window: cum_sum = running SUM(Frequency) ordered by Number;
          mid = total/2.0.
        - Keep rows where mid is in (cum_sum - Frequency, cum_sum] (inclusive
          bounds via BETWEEN).
        - SELECT AVG(Number) AS median.

        Complexity: O(U log U) sort/window over U distinct numbers.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT AVG(Number) AS median
    FROM (
        SELECT
            Number,
            Frequency,
            SUM(Frequency) OVER (ORDER BY Number) AS cum_sum,
            SUM(Frequency) OVER () / 2.0 AS mid
        FROM Numbers
    ) t
    WHERE mid BETWEEN (cum_sum - Frequency) AND cum_sum;
    """
# @lc code=end


