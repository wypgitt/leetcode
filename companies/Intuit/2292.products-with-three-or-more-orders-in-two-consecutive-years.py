#
# @lc app=leetcode id=2292 lang=python3
#
# [2292] Products With Three or More Orders in Two Consecutive Years
#
# https://leetcode.com/problems/products-with-three-or-more-orders-in-two-consecutive-years/description/
#
# database
# Medium (40.78%)
# Likes:    65
# Dislikes: 29
# Total Accepted:    11K
# Total Submissions: 26.9K
# Testcase Example:  "{\"headers\": {\"Orders\": [\"order_id\", \"product_id\", \"quantity\", \"purchase_date\"]}, \"rows\": {\"Orders\": [[1, 1, 7, \"2020-03-16\"], [2, 1, 4, \"2020-12-02\"], [3, 1, 7, \"2020-05-10\"], [4, 1, 6, \"2021-12-23\"], [5, 1, 5, \"2021-05-21\"], [6, 1, 6, \"2021-10-11\"], [7, 2, 6, \"2022-10-11\"]]}}"
#
#
# Table: Orders
#
# +---------------+------+
# | Column Name   | Type |
# +---------------+------+
# | order_id      | int  |
# | product_id    | int  |
# | quantity      | int  |
# | purchase_date | date |
# +---------------+------+
# order_id contains unique values.
# Each row in this table contains the ID of an order, the id of the
# product purchased, the quantity, and the purchase date.
#
# Write a solution to report the IDs of all the products that were ordered
# three or more times in two consecutive years.
#
# Return the result table in any order.
#
# The result format is shown in the following example.
#
# Example 1:
#
# Input:
# Orders table:
# +----------+------------+----------+---------------+
# | order_id | product_id | quantity | purchase_date |
# +----------+------------+----------+---------------+
# | 1        | 1          | 7        | 2020-03-16    |
# | 2        | 1          | 4        | 2020-12-02    |
# | 3        | 1          | 7        | 2020-05-10    |
# | 4        | 1          | 6        | 2021-12-23    |
# | 5        | 1          | 5        | 2021-05-21    |
# | 6        | 1          | 6        | 2021-10-11    |
# | 7        | 2          | 6        | 2022-10-11    |
# +----------+------------+----------+---------------+
# Output:
# +------------+
# | product_id |
# +------------+
# | 1          |
# +------------+
# Explanation:
# Product 1 was ordered in 2020 three times and in 2021 three times. Since
# it was ordered three times in two consecutive years, we include it in
# the answer.
# Product 2 was ordered one time in 2022. We do not include it in the
# answer.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        SQL: Orders(order_id, product_id, quantity, purchase_date). Report
        product_ids ordered >=3 times in two consecutive years.

        Algorithm:
        - Aggregate counts by (product_id, year); self-join consecutive years
          both with count >= 3.

        Complexity: O(N).
        """
        self.sql = '''
WITH P AS (
    SELECT product_id, YEAR(purchase_date) AS y
    FROM Orders
    GROUP BY product_id, YEAR(purchase_date)
    HAVING COUNT(1) >= 3
)
SELECT DISTINCT p1.product_id
FROM P p1
JOIN P p2 ON p1.product_id = p2.product_id AND p1.y = p2.y - 1
'''
        return self.sql
# @lc code=end
