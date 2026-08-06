#
# @lc app=leetcode id=1070 lang=python3
#
# [1070] Product Sales Analysis III
#
# https://leetcode.com/problems/product-sales-analysis-iii/description/
#
# algorithms
# Medium (46.36%)
# Likes:    824
# Dislikes: 1140
# Total Accepted:    488K
# Total Submissions: 1.1M
# Testcase Example:  "{\"headers\":{\"Sales\":[\"sale_id\",\"product_id\",\"year\",\"quantity\",\"price\"]},\"rows\":{\"Sales\":[[1,100,2008,10,5000],[2,100,2009,12,5000],[7,200,2011,15,9000]]}}"
#
# Table: Sales
#
# +-------------+-------+
# | Column Name | Type |
# +-------------+-------+
# | sale_id | int |
# | product_id | int |
# | year | int |
# | quantity | int |
# | price | int |
# +-------------+-------+
# (sale_id, year) is the primary key (combination of columns with unique
# values) of this table.
# Each row records a sale of a product in a given year.
# A product may have multiple sales entries in the same year.
# Note that the per-unit price.
#
# Write a solution to find all sales that occurred in the first year each
# product was sold.
#
# For each product_id, identify the earliest year it appears in the Sales
# table.
#
# Return all sales entries for that product in that year.
#
# Return a table with the following columns: product_id, first_year, quantity,
# and price.
#
# Return the result in any order.
#
# Example 1:
#
# Input:
# Sales table:
# +---------+------------+------+----------+-------+
# | sale_id | product_id | year | quantity | price |
# +---------+------------+------+----------+-------+
# | 1 | 100 | 2008 | 10 | 5000 |
# | 2 | 100 | 2009 | 12 | 5000 |
# | 7 | 200 | 2011 | 15 | 9000 |
# +---------+------------+------+----------+-------+
#
# Output:
# +------------+------------+----------+-------+
# | product_id | first_year | quantity | price |
# +------------+------------+----------+-------+
# | 100 | 2008 | 10 | 5000 |
# | 200 | 2011 | 15 | 9000 |
# +------------+------------+----------+-------+
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Keep only sales that happened in each product's first year. Compute
        MIN(year) per product, then join back to Sales for that year.

        Algorithm:
        - CTE/subquery: first_year = MIN(year) GROUP BY product_id.
        - JOIN Sales where year = first_year; alias year as first_year.

        Complexity: O(N) with aggregation + join.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT s.product_id, s.year AS first_year, s.quantity, s.price
    FROM Sales s
    JOIN (
        SELECT product_id, MIN(year) AS first_year
        FROM Sales
        GROUP BY product_id
    ) t ON s.product_id = t.product_id AND s.year = t.first_year;
    """
# @lc code=end
