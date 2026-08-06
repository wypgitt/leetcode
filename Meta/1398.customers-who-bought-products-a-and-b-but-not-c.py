#
# @lc app=leetcode id=1398 lang=python3
#
# [1398] Customers Who Bought Products A and B but Not C
#
# https://leetcode.com/problems/customers-who-bought-products-a-and-b-but-not-c/description/
#
# database
# Medium (71.44%)
# Likes:    328
# Dislikes: 18
# Total Accepted:    70.1K
# Total Submissions: 98.1K
# Testcase Example:  "{\"headers\":{\"Customers\":[\"customer_id\",\"customer_name\"],\"Orders\":[\"order_id\",\"customer_id\",\"product_name\"]},\"rows\":{\"Customers\":[[1,\"Daniel\"],[2,\"Diana\"],[3,\"Elizabeth\"],[4,\"Jhon\"]],\"Orders\":[[10,1,\"A\"],[20,1,\"B\"],[30,1,\"D\"],[40,1,\"C\"],[50,2,\"A\"],[60,3,\"A\"],[70,3,\"B\"],[80,3,\"D\"],[90,4,\"C\"]]}}"
#
#
# Table: Customers
#
# +---------------------+---------+
# | Column Name         | Type    |
# +---------------------+---------+
# | customer_id         | int     |
# | customer_name       | varchar |
# +---------------------+---------+
# customer_id is the column with unique values for this table.
# customer_name is the name of the customer.
#
# Table: Orders
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | order_id      | int     |
# | customer_id   | int     |
# | product_name  | varchar |
# +---------------+---------+
# order_id is the column with unique values for this table.
# customer_id is the id of the customer who bought the product
# "product_name".
#
# Write a solution to report the customer_id and customer_name of
# customers who bought products "A", "B" but did not buy the product "C"
# since we want to recommend them to purchase this product.
#
# Return the result table ordered by customer_id.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Customers table:
# +-------------+---------------+
# | customer_id | customer_name |
# +-------------+---------------+
# | 1           | Daniel        |
# | 2           | Diana         |
# | 3           | Elizabeth     |
# | 4           | Jhon          |
# +-------------+---------------+
# Orders table:
# +------------+--------------+---------------+
# | order_id   | customer_id  | product_name  |
# +------------+--------------+---------------+
# | 10         |     1        |     A         |
# | 20         |     1        |     B         |
# | 30         |     1        |     D         |
# | 40         |     1        |     C         |
# | 50         |     2        |     A         |
# | 60         |     3        |     A         |
# | 70         |     3        |     B         |
# | 80         |     3        |     D         |
# | 90         |     4        |     C         |
# +------------+--------------+---------------+
# Output:
# +-------------+---------------+
# | customer_id | customer_name |
# +-------------+---------------+
# | 3           | Elizabeth     |
# +-------------+---------------+
# Explanation: Only the customer_id with id 3 bought the product A and B
# but not the product C.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. Customers who bought both A and B but never C.

        Algorithm:
        - Filter Orders product_name IN ('A','B','C'); GROUP BY customer
        - HAVING SUM(A)>0 AND SUM(B)>0 AND SUM(C)=0; join Customers for name

        Complexity: O(O + C) over orders/customers.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT c.customer_id, c.customer_name
    FROM Customers c
    JOIN Orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.customer_name
    HAVING SUM(o.product_name = 'A') > 0
       AND SUM(o.product_name = 'B') > 0
       AND SUM(o.product_name = 'C') = 0
    ORDER BY c.customer_id;
    """
# @lc code=end
