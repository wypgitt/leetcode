#
# @lc app=leetcode id=183 lang=python3
#
# [183] Customers Who Never Order
#
# https://leetcode.com/problems/customers-who-never-order/description/
#
# algorithms
# Easy (72.17%)
# Likes:    3127
# Dislikes: 163
# Total Accepted:    1.4M
# Total Submissions: 1.9M
# Testcase Example:  "{\"headers\": {\"Customers\": [\"id\", \"name\"], \"Orders\": [\"id\", \"customerId\"]}, \"rows\": {\"Customers\": [[1, \"Joe\"], [2, \"Henry\"], [3, \"Sam\"], [4, \"Max\"]], \"Orders\": [[1, 3], [2, 1]]}}"
#
# Table: Customers
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | id | int |
# | name | varchar |
# +-------------+---------+
# id is the primary key (column with unique values) for this table.
# Each row of this table indicates the ID and name of a customer.
#
# Table: Orders
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | id | int |
# | customerId | int |
# +-------------+------+
# id is the primary key (column with unique values) for this table.
# customerId is a foreign key (reference columns) of the ID from the Customers
# table.
# Each row of this table indicates the ID of an order and the ID of the
# customer who ordered it.
#
# Write a solution to find all customers who never order anything.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Customers table:
# +----+-------+
# | id | name |
# +----+-------+
# | 1 | Joe |
# | 2 | Henry |
# | 3 | Sam |
# | 4 | Max |
# +----+-------+
# Orders table:
# +----+------------+
# | id | customerId |
# +----+------------+
# | 1 | 3 |
# | 2 | 1 |
# +----+------------+
# Output:
# +-----------+
# | Customers |
# +-----------+
# | Henry |
# | Max |
# +-----------+
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Customers with no matching order row — LEFT JOIN Orders and keep rows
        where the order side is NULL (anti-join pattern).

        Algorithm:
        - FROM Customers c LEFT JOIN Orders o ON c.id = o.customerId.
        - WHERE o.id IS NULL; SELECT c.name.

        Complexity: O(C + O) with indexes on customer keys; otherwise join
        cost relative to table sizes.

        Alternate:
        - NOT IN / NOT EXISTS against Orders.customerId.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT c.name AS Customers
    FROM Customers c
    LEFT JOIN Orders o
        ON c.id = o.customerId
    WHERE o.id IS NULL;
    """
# @lc code=end
