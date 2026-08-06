#
# @lc app=leetcode id=1549 lang=python3
#
# [1549] The Most Recent Orders for Each Product
#
# https://leetcode.com/problems/the-most-recent-orders-for-each-product/description/
#
# database
# Medium (64.99%)
# Likes:    141
# Dislikes: 12
# Total Accepted:    39.7K
# Total Submissions: 61.1K
# Testcase Example:  "{\"headers\":{\"Customers\":[\"customer_id\",\"name\"],\"Orders\":[\"order_id\",\"order_date\",\"customer_id\",\"product_id\"],\"Products\":[\"product_id\",\"product_name\",\"price\"]},\"rows\":{\"Customers\":[[1,\"Winston\"],[2,\"Jonathan\"],[3,\"Annabelle\"],[4,\"Marwan\"],[5,\"Khaled\"]],\"Orders\":[[1,\"2020-07-31\",1,1],[2,\"2020-7-30\",2,2],[3,\"2020-08-29\",3,3],[4,\"2020-07-29\",4,1],[5,\"2020-06-10\",1,2],[6,\"2020-08-01\",2,1],[7,\"2020-08-01\",3,1],[8,\"2020-08-03\",1,2],[9,\"2020-08-07\",2,3],[10,\"2020-07-15\",1,2]],\"Products\":[[1,\"keyboard\",120],[2,\"mouse\",80],[3,\"screen\",600],[4,\"hard disk\",450]]}}"
#
#
# Table: Customers
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | customer_id   | int     |
# | name          | varchar |
# +---------------+---------+
# customer_id is the column with unique values for this table.
# This table contains information about the customers.
#
# Table: Orders
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | order_id      | int     |
# | order_date    | date    |
# | customer_id   | int     |
# | product_id    | int     |
# +---------------+---------+
# order_id is the column with unique values for this table.
# This table contains information about the orders made by customer_id.
# There will be no product ordered by the same user more than once in one
# day.
#
# Table: Products
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | product_id    | int     |
# | product_name  | varchar |
# | price         | int     |
# +---------------+---------+
# product_id is the column with unique values for this table.
# This table contains information about the Products.
#
# Write a solution to find the most recent order(s) of each product.
#
# Return the result table ordered by product_name in ascending order and
# in case of a tie by the product_id in ascending order. If there still a
# tie, order them by order_id in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Customers table:
# +-------------+-----------+
# | customer_id | name      |
# +-------------+-----------+
# | 1           | Winston   |
# | 2           | Jonathan  |
# | 3           | Annabelle |
# | 4           | Marwan    |
# | 5           | Khaled    |
# +-------------+-----------+
# Orders table:
# +----------+------------+-------------+------------+
# | order_id | order_date | customer_id | product_id |
# +----------+------------+-------------+------------+
# | 1        | 2020-07-31 | 1           | 1          |
# | 2        | 2020-07-30 | 2           | 2          |
# | 3        | 2020-08-29 | 3           | 3          |
# | 4        | 2020-07-29 | 4           | 1          |
# | 5        | 2020-06-10 | 1           | 2          |
# | 6        | 2020-08-01 | 2           | 1          |
# | 7        | 2020-08-01 | 3           | 1          |
# | 8        | 2020-08-03 | 1           | 2          |
# | 9        | 2020-08-07 | 2           | 3          |
# | 10       | 2020-07-15 | 1           | 2          |
# +----------+------------+-------------+------------+
# Products table:
# +------------+--------------+-------+
# | product_id | product_name | price |
# +------------+--------------+-------+
# | 1          | keyboard     | 120   |
# | 2          | mouse        | 80    |
# | 3          | screen       | 600   |
# | 4          | hard disk    | 450   |
# +------------+--------------+-------+
# Output:
# +--------------+------------+----------+------------+
# | product_name | product_id | order_id | order_date |
# +--------------+------------+----------+------------+
# | keyboard     | 1          | 6        | 2020-08-01 |
# | keyboard     | 1          | 7        | 2020-08-01 |
# | mouse        | 2          | 8        | 2020-08-03 |
# | screen       | 3          | 3        | 2020-08-29 |
# +--------------+------------+----------+------------+
# Explanation:
# keyboard's most recent order is in 2020-08-01, it was ordered two times
# this day.
# mouse's most recent order is in 2020-08-03, it was ordered only once
# this day.
# screen's most recent order is in 2020-08-29, it was ordered only once
# this day.
# The hard disk was never ordered and we do not include it in the result
# table.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. For each product, the most recent order(s) (max order_date).
        Return product_name, product_id, order_id, order_date ordered by
        product_name, product_id, order_id.

        Algorithm:
        - RANK() OVER (PARTITION BY product_id ORDER BY order_date DESC)=1;
          join Products; or join with MAX(order_date) per product.

        Complexity: O(O log O).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT p.product_name, p.product_id, o.order_id, o.order_date
    FROM Products p
    JOIN Orders o ON p.product_id = o.product_id
    WHERE (o.product_id, o.order_date) IN (
        SELECT product_id, MAX(order_date)
        FROM Orders
        GROUP BY product_id
    )
    ORDER BY p.product_name, p.product_id, o.order_id;
    """
# @lc code=end
