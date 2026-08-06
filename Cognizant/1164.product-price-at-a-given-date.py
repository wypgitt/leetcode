#
# @lc app=leetcode id=1164 lang=python3
#
# [1164] Product Price at a Given Date
#
# https://leetcode.com/problems/product-price-at-a-given-date/description/
#
# algorithms
# Medium (58.31%)
# Likes:    1463
# Dislikes: 338
# Total Accepted:    370K
# Total Submissions: 635K
# Testcase Example:  "{\"headers\":{\"Products\":[\"product_id\",\"new_price\",\"change_date\"]},\"rows\":{\"Products\":[[1,20,\"2019-08-14\"],[2,50,\"2019-08-14\"],[1,30,\"2019-08-15\"],[1,35,\"2019-08-16\"],[2,65,\"2019-08-17\"],[3,20,\"2019-08-18\"]]}}"
#
# Table: Products
#
# +---------------+---------+
# | Column Name | Type |
# +---------------+---------+
# | product_id | int |
# | new_price | int |
# | change_date | date |
# +---------------+---------+
# (product_id, change_date) is the primary key (combination of columns with
# unique values) of this table.
# Each row of this table indicates that the price of some product was changed
# to a new price at some date.
#
# Initially, all products have price 10.
#
# Write a solution to find the prices of all products on the date 2019-08-16.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Products table:
# +------------+-----------+-------------+
# | product_id | new_price | change_date |
# +------------+-----------+-------------+
# | 1 | 20 | 2019-08-14 |
# | 2 | 50 | 2019-08-14 |
# | 1 | 30 | 2019-08-15 |
# | 1 | 35 | 2019-08-16 |
# | 2 | 65 | 2019-08-17 |
# | 3 | 20 | 2019-08-18 |
# +------------+-----------+-------------+
# Output:
# +------------+-------+
# | product_id | price |
# +------------+-------+
# | 2 | 50 |
# | 1 | 35 |
# | 3 | 10 |
# +------------+-------+
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Price of each product on 2019-08-16; initial price is 10 if no change
        on or before that date.

        Algorithm:
        - UNION: products with only changes after date → price 10; else latest
          new_price with change_date <= '2019-08-16'.

        Complexity: O(N).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT product_id, 10 AS price
    FROM Products
    GROUP BY product_id
    HAVING MIN(change_date) > '2019-08-16'

    UNION ALL

    SELECT product_id, new_price AS price
    FROM Products
    WHERE (product_id, change_date) IN (
        SELECT product_id, MAX(change_date)
        FROM Products
        WHERE change_date <= '2019-08-16'
        GROUP BY product_id
    );
    """
# @lc code=end
