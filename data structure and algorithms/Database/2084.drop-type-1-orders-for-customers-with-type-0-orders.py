#
# @lc app=leetcode id=2084 lang=python3
#
# [2084] Drop Type 1 Orders for Customers With Type 0 Orders
#
# https://leetcode.com/problems/drop-type-1-orders-for-customers-with-type-0-orders/description/
#
# database
# Medium (86.59%)
# Likes:    98
# Dislikes: 20
# Total Accepted:    14.9K
# Total Submissions: 17.3K
# Testcase Example:  "{\"headers\":{\"Orders\":[\"order_id\",\"customer_id\",\"order_type\"]},\"rows\":{\"Orders\":[[1,1,0],[2,1,0],[11,2,0],[12,2,1],[21,3,1],[22,3,0],[31,4,1],[32,4,1]]}}"
#
#
# Table: Orders
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | order_id    | int  |
# | customer_id | int  |
# | order_type  | int  |
# +-------------+------+
# order_id is the column with unique values for this table.
# Each row of this table indicates the ID of an order, the ID of the
# customer who ordered it, and the order type.
# The orders could be of type 0 or type 1.
#
# Write a solution to report all the orders based on the following
# criteria:
#
# If a customer has at least one order of type 0, do not report any order
# of type 1 from that customer.
#
# Otherwise, report all the orders of the customer.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Orders table:
# +----------+-------------+------------+
# | order_id | customer_id | order_type |
# +----------+-------------+------------+
# | 1        | 1           | 0          |
# | 2        | 1           | 0          |
# | 11       | 2           | 0          |
# | 12       | 2           | 1          |
# | 21       | 3           | 1          |
# | 22       | 3           | 0          |
# | 31       | 4           | 1          |
# | 32       | 4           | 1          |
# +----------+-------------+------------+
# Output:
# +----------+-------------+------------+
# | order_id | customer_id | order_type |
# +----------+-------------+------------+
# | 31       | 4           | 1          |
# | 32       | 4           | 1          |
# | 1        | 1           | 0          |
# | 2        | 1           | 0          |
# | 11       | 2           | 0          |
# | 22       | 3           | 0          |
# +----------+-------------+------------+
# Explanation:
# Customer 1 has two orders of type 0. We return both of them.
# Customer 2 has one order of type 0 and one order of type 1. We only
# return the order of type 0.
# Customer 3 has one order of type 0 and one order of type 1. We only
# return the order of type 0.
# Customer 4 has two orders of type 1. We return both of them.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Orders(order_id, customer_id, order_type) type 0/1.
        If a customer has any type-0 order, drop all their type-1 orders;
        otherwise keep all (type-1 only) orders. Return remaining orders.

        Algorithm:
        - Keep rows where order_type=0 OR customer has no type-0 orders.

        Complexity: O(N).
        """
        self.sql = """
        SELECT order_id, customer_id, order_type
        FROM Orders
        WHERE order_type = 0
           OR customer_id NOT IN (
                SELECT DISTINCT customer_id FROM Orders WHERE order_type = 0
           )
        """
        return self.sql
# @lc code=end
