#
# @lc app=leetcode id=197 lang=python3
#
# [197] Rising Temperature
#
# https://leetcode.com/problems/rising-temperature/description/
#
# algorithms
# Easy (51.84%)
# Likes:    4373
# Dislikes: 748
# Total Accepted:    1.6M
# Total Submissions: 3.1M
# Testcase Example:  "{\"headers\": {\"Weather\": [\"id\", \"recordDate\", \"temperature\"]}, \"rows\": {\"Weather\": [[1, \"2015-01-01\", 10], [2, \"2015-01-02\", 25], [3, \"2015-01-03\", 20], [4, \"2015-01-04\", 30]]}}"
#
# Table: Weather
#
# +---------------+---------+
# | Column Name | Type |
# +---------------+---------+
# | id | int |
# | recordDate | date |
# | temperature | int |
# +---------------+---------+
# id is the column with unique values for this table.
# There are no different rows with the same recordDate.
# This table contains information about the temperature on a certain day.
#
# Write a solution to find all dates' id with higher temperatures compared to
# its previous dates (yesterday).
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Weather table:
# +----+------------+-------------+
# | id | recordDate | temperature |
# +----+------------+-------------+
# | 1 | 2015-01-01 | 10 |
# | 2 | 2015-01-02 | 25 |
# | 3 | 2015-01-03 | 20 |
# | 4 | 2015-01-04 | 30 |
# +----+------------+-------------+
# Output:
# +----+
# | id |
# +----+
# | 2 |
# | 4 |
# +----+
# Explanation:
# In 2015-01-02, the temperature was higher than the previous day (10 -> 25).
# In 2015-01-04, the temperature was higher than the previous day (20 -> 30).
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Self-join Weather so each day pairs with yesterday (date difference 1),
        then keep rows warmer than that previous day.

        Algorithm:
        - JOIN Weather w1 to w2 ON DATEDIFF(w1.recordDate, w2.recordDate) = 1.
        - WHERE w1.temperature > w2.temperature; SELECT w1.id.

        Complexity: O(W) with index on recordDate; otherwise join cost
        relative to Weather size.

        Alternate:
        - JOIN ON w1.recordDate = DATE_ADD(w2.recordDate, INTERVAL 1 DAY).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT w1.id
    FROM Weather w1
    JOIN Weather w2
        ON DATEDIFF(w1.recordDate, w2.recordDate) = 1
    WHERE w1.temperature > w2.temperature;
    """
# @lc code=end
