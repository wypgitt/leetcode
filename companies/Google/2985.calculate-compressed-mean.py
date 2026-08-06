#
# @lc app=leetcode id=2985 lang=python3
#
# [2985] Calculate Compressed Mean
#
# https://leetcode.com/problems/calculate-compressed-mean/description/
#
# database
# Easy (86.01%)
# Likes:    14
# Dislikes: 6
# Total Accepted:    6K
# Total Submissions: 7K
# Testcase Example:  "{\"headers\":{\"Orders\":[\"order_id\",\"item_count\",\"order_occurrences\"]},\"rows\":{\"Orders\":[[10,1,500],[11,2,1000],[12,3,800],[13,4,1000]]}}"
#
#
# Table: Orders
#
# +-------------------+------+
# | Column Name       | Type |
# +-------------------+------+
# | order_id          | int  |
# | item_count        | int  |
# | order_occurrences | int  |
# +-------------------+------+
# order_id is column of unique values for this table.
# This table contains order_id, item_count, and order_occurrences.
#
# Write a solution to calculate the average number of items per order,
# rounded to 2 decimal places.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Orders table:
# +----------+------------+-------------------+
# | order_id | item_count | order_occurrences |
# +----------+------------+-------------------+
# | 10       | 1          | 500               |
# | 11       | 2          | 1000              |
# | 12       | 3          | 800               |
# | 13       | 4          | 1000              |
# +----------+------------+-------------------+
# Output
# +-------------------------+
# | average_items_per_order |
# +-------------------------+
# | 2.70                    |
# +-------------------------+
# Explanation
# The calculation is as follows:
#  - Total items: (1 * 500) + (2 * 1000) + (3 * 800) + (4 * 1000) = 8900
#  - Total orders: 500 + 1000 + 800 + 1000 = 3300
#  - Therefore, the average items per order is 8900 / 3300 = 2.70
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Orders(order_id, item_count, order_occurrences). Compressed
        mean = sum(item_count * order_occurrences) / sum(order_occurrences),
        rounded to 2 decimals as average_items_per_order.

        Algorithm:
        - Single SELECT with SUM and ROUND(..., 2).

        Complexity: O(N).
        """
        self.sql = """
SELECT
    ROUND(
        SUM(item_count * order_occurrences) / SUM(order_occurrences),
        2
    ) AS average_items_per_order
FROM Orders;
"""
        return self.sql
# @lc code=end
