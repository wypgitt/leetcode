#
# @lc app=leetcode id=1083 lang=python3
#
# [1083] Sales Analysis II
#
# https://leetcode.com/problems/sales-analysis-ii/description/
#
# database
# Easy (50.16%)
# Likes:    282
# Dislikes: 49
# Total Accepted:    67.8K
# Total Submissions: 135.2K
# Testcase Example:  "{\"headers\":{\"Product\":[\"product_id\",\"product_name\",\"unit_price\"],\"Sales\":[\"seller_id\",\"product_id\",\"buyer_id\",\"sale_date\",\"quantity\",\"price\"]},\"rows\":{\"Product\":[[1,\"S8\",1000],[2,\"G4\",800],[3,\"iPhone\",1400]],\"Sales\":[[1,1,1,\"2019-01-21\",2,2000],[1,2,2,\"2019-02-17\",1,800],[2,1,3,\"2019-06-02\",1,800],[3,3,3,\"2019-05-13\",2,2800]]}}"
#
#
# Table: Product
#
# +--------------+---------+
# | Column Name  | Type    |
# +--------------+---------+
# | product_id   | int     |
# | product_name | varchar |
# | unit_price   | int     |
# +--------------+---------+
# product_id is the primary key (column with unique values) of this table.
# Each row of this table indicates the name and the price of each product.
#
# Table: Sales
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | seller_id   | int     |
# | product_id  | int     |
# | buyer_id    | int     |
# | sale_date   | date    |
# | quantity    | int     |
# | price       | int     |
# +-------------+---------+
# This table might have repeated rows.
# product_id is a foreign key (reference column) to the Product table.
# buyer_id is never NULL.
# sale_date is never NULL.
# Each row of this table contains some information about one sale.
#
# Write a solution to report the buyers who have bought S8 but not iPhone.
# Note that S8 and iPhone are products presented in the Product table.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Product table:
# +------------+--------------+------------+
# | product_id | product_name | unit_price |
# +------------+--------------+------------+
# | 1          | S8           | 1000       |
# | 2          | G4           | 800        |
# | 3          | iPhone       | 1400       |
# +------------+--------------+------------+
# Sales table:
# +-----------+------------+----------+------------+----------+-------+
# | seller_id | product_id | buyer_id | sale_date  | quantity | price |
# +-----------+------------+----------+------------+----------+-------+
# | 1         | 1          | 1        | 2019-01-21 | 2        | 2000  |
# | 1         | 2          | 2        | 2019-02-17 | 1        | 800   |
# | 2         | 1          | 3        | 2019-06-02 | 1        | 800   |
# | 3         | 3          | 3        | 2019-05-13 | 2        | 2800  |
# +-----------+------------+----------+------------+----------+-------+
# Output:
# +-------------+
# | buyer_id    |
# +-------------+
# | 1           |
# +-------------+
# Explanation: The buyer with id 1 bought an S8 but did not buy an iPhone.
# The buyer with id 3 bought both.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. Buyers who bought S8 but never bought iPhone.

        Algorithm:
        - JOIN Sales⋈Product; filter buyers with product_name = 'S8'.
        - Exclude buyers who appear with product_name = 'iPhone'.

        Complexity: O(S) with joins/filters.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT DISTINCT s.buyer_id
    FROM Sales s
    JOIN Product p ON s.product_id = p.product_id
    WHERE p.product_name = 'S8'
      AND s.buyer_id NOT IN (
          SELECT s2.buyer_id
          FROM Sales s2
          JOIN Product p2 ON s2.product_id = p2.product_id
          WHERE p2.product_name = 'iPhone'
      );
    """
# @lc code=end
