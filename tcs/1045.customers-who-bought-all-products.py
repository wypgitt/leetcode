#
# @lc app=leetcode id=1045 lang=python3
#
# [1045] Customers Who Bought All Products
#
# https://leetcode.com/problems/customers-who-bought-all-products/description/
#
# algorithms
# Medium (64.34%)
# Likes:    1210
# Dislikes: 98
# Total Accepted:    533K
# Total Submissions: 828K
# Testcase Example:  "{\"headers\":{\"Customer\":[\"customer_id\",\"product_key\"],\"Product\":[\"product_key\"]},\"rows\":{\"Customer\":[[1,5],[2,6],[3,5],[3,6],[1,6]],\"Product\":[[5],[6]]}}"
#
# Table: Customer
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | customer_id | int |
# | product_key | int |
# +-------------+---------+
# This table may contain duplicates rows.
# customer_id is not NULL.
# product_key is a foreign key (reference column) to Product table.
#
# Table: Product
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | product_key | int |
# +-------------+---------+
# product_key is the primary key (column with unique values) for this table.
#
# Write a solution to report the customer ids from the Customer table that
# bought all the products in the Product table.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Customer table:
# +-------------+-------------+
# | customer_id | product_key |
# +-------------+-------------+
# | 1 | 5 |
# | 2 | 6 |
# | 3 | 5 |
# | 3 | 6 |
# | 1 | 6 |
# +-------------+-------------+
# Product table:
# +-------------+
# | product_key |
# +-------------+
# | 5 |
# | 6 |
# +-------------+
# Output:
# +-------------+
# | customer_id |
# +-------------+
# | 1 |
# | 3 |
# +-------------+
# Explanation:
# The customers who bought all the products (5 and 6) are customers with IDs 1
# and 3.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Customers who bought every product: distinct product_key count per
        customer equals the total number of products.

        Algorithm:
        - GROUP BY customer_id HAVING COUNT(DISTINCT product_key) =
          (SELECT COUNT(*) FROM Product)

        Complexity: O(n) scan with hash aggregate.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT customer_id
    FROM Customer
    GROUP BY customer_id
    HAVING COUNT(DISTINCT product_key) = (SELECT COUNT(*) FROM Product);
    """
# @lc code=end
