#
# @lc app=leetcode id=2893 lang=python3
#
# [2893] Calculate Orders Within Each Interval
#
# https://leetcode.com/problems/calculate-orders-within-each-interval/description/
#
# database
# Medium (67.21%)
# Likes:    24
# Dislikes: 3
# Total Accepted:    4.5K
# Total Submissions: 6.7K
# Testcase Example:  "{\"headers\": {\"Orders\": [\"minute\", \"order_count\"]}, \"rows\": {\"Orders\":[[1,0],[2,2],[3,4],[4,6],[5,1],[6,4],[7,1],[8,2],[9,4],[10,1],[11,4],[12,6]]}}"
#
#
# Table: Orders
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | minute      | int  |
# | order_count | int  |
# +-------------+------+
# minute is the primary key for this table.
# Each row of this table contains the minute and number of orders received
# during that specific minute. The total number of rows will be a multiple
# of 6.
#
# Write a query to calculate total orders within each interval. Each
# interval is defined as a combination of 6 minutes.
#
# Minutes 1 to 6 fall within interval 1, while minutes 7 to 12 belong to
# interval 2, and so forth.
#
# Return the result table ordered by interval_no in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Orders table:
# +--------+-------------+
# | minute | order_count |
# +--------+-------------+
# | 1      | 0           |
# | 2      | 2           |
# | 3      | 4           |
# | 4      | 6           |
# | 5      | 1           |
# | 6      | 4           |
# | 7      | 1           |
# | 8      | 2           |
# | 9      | 4           |
# | 10     | 1           |
# | 11     | 4           |
# | 12     | 6           |
# +--------+-------------+
# Output:
# +-------------+--------------+
# | interval_no | total_orders |
# +-------------+--------------+
# | 1           | 17           |
# | 2           | 18           |
# +-------------+--------------+
# Explanation:
# - Interval number 1 comprises minutes from 1 to 6. The total orders in
# these six minutes are (0 + 2 + 4 + 6 + 1 + 4) = 17.
# - Interval number 2 comprises minutes from 7 to 12. The total orders in
# these six minutes are (1 + 2 + 4 + 1 + 4 + 6) = 18.
# Returning table orderd by interval_no in ascending order.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Orders(minute, order_count). Group minutes into intervals of
        6 (1-6 -> 1, 7-12 -> 2, ...) and sum order_count per interval.

        Algorithm:
        - CEIL(minute/6) as interval_no; SUM(order_count); ORDER BY interval_no.

        Alternate: window SUM ROWS 5 PRECEDING and keep minute % 6 = 0.

        Complexity: O(N).
        """
        self.sql = """
SELECT
  CEIL(minute / 6) AS interval_no,
  SUM(order_count) AS total_orders
FROM Orders
GROUP BY 1
ORDER BY 1;
"""
        return self.sql
# @lc code=end
