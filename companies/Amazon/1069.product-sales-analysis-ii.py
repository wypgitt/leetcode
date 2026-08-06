#
# @lc app=leetcode id=1069 lang=python3
#
# [1069] Product Sales Analysis II
#
# https://leetcode.com/problems/product-sales-analysis-ii/description/
#
# database
# Easy (82.67%)
# Likes:    85
# Dislikes: 182
# Total Accepted:    63.2K
# Total Submissions: 76.5K
# Testcase Example:  "{\"headers\":{\"Sales\":[\"sale_id\",\"product_id\",\"year\",\"quantity\",\"price\"],\"Product\":[\"product_id\",\"product_name\"]},\"rows\":{\"Sales\":[[1,100,2008,10,5000],[2,100,2009,12,5000],[7,200,2011,15,9000]],\"Product\":[[100,\"Nokia\"],[200,\"Apple\"],[300,\"Samsung\"]]}}"
#
#
# Table: Sales
#
# +-------------+-------+
# | Column Name | Type  |
# +-------------+-------+
# | sale_id     | int   |
# | product_id  | int   |
# | year        | int   |
# | quantity    | int   |
# | price       | int   |
# +-------------+-------+
# (sale_id, year) is the primary key (combination of columns with unique
# values) of this table.
# product_id is a foreign key (reference column) to Product table.
# Each row of this table shows a sale on the product product_id in a
# certain year.
# Note that the price is per unit.
#
# Table: Product
#
# +--------------+---------+
# | Column Name  | Type    |
# +--------------+---------+
# | product_id   | int     |
# | product_name | varchar |
# +--------------+---------+
# product_id is the primary key (column with unique values) of this table.
# Each row of this table indicates the product name of each product.
#
# Write a solution that reports the total quantity sold for every product
# id.
#
# Return the resulting table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Sales table:
# +---------+------------+------+----------+-------+
# | sale_id | product_id | year | quantity | price |
# +---------+------------+------+----------+-------+
# | 1       | 100        | 2008 | 10       | 5000  |
# | 2       | 100        | 2009 | 12       | 5000  |
# | 7       | 200        | 2011 | 15       | 9000  |
# +---------+------------+------+----------+-------+
# Product table:
# +------------+--------------+
# | product_id | product_name |
# +------------+--------------+
# | 100        | Nokia        |
# | 200        | Apple        |
# | 300        | Samsung      |
# +------------+--------------+
# Output:
# +--------------+----------------+
# | product_id   | total_quantity |
# +--------------+----------------+
# | 100          | 22             |
# | 200          | 15             |
# +--------------+----------------+
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. For each product, report the total quantity sold (sum of all
        sales rows for that product_id).

        Algorithm:
        - GROUP BY product_id; SUM(quantity) AS total_quantity.

        Complexity: O(N) aggregation over Sales.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT product_id, SUM(quantity) AS total_quantity
    FROM Sales
    GROUP BY product_id;
    """
# @lc code=end
