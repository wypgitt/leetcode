#
# @lc app=leetcode id=1082 lang=python3
#
# [1082] Sales Analysis I
#
# https://leetcode.com/problems/sales-analysis-i/description/
#
# database
# Easy (74.81%)
# Likes:    204
# Dislikes: 82
# Total Accepted:    69K
# Total Submissions: 92.2K
# Testcase Example:  "{\"headers\":{\"Product\":[\"product_id\",\"product_name\",\"unit_price\"],\"Sales\":[\"seller_id\",\"product_id\",\"buyer_id\",\"sale_date\",\"quantity\",\"price\"]},\"rows\":{\"Product\":[[1,\"S8\",1000],[2,\"G4\",800],[3,\"iPhone\",1400]],\"Sales\":[[1,1,1,\"2019-01-21\",2,2000],[1,2,2,\"2019-02-17\",1,800],[2,2,3,\"2019-06-02\",1,800],[3,3,4,\"2019-05-13\",2,2800]]}}"
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
# This table can have repeated rows.
# product_id is a foreign key (reference column) to the Product table.
# Each row of this table contains some information about one sale.
#
# Write a solution that reports the best seller by total sales price, If
# there is a tie, report them all.
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
# | 2         | 2          | 3        | 2019-06-02 | 1        | 800   |
# | 3         | 3          | 4        | 2019-05-13 | 2        | 2800  |
# +-----------+------------+----------+------------+----------+-------+
# Output:
# +-------------+
# | seller_id   |
# +-------------+
# | 1           |
# | 3           |
# +-------------+
# Explanation: Both sellers with id 1 and 3 sold products with the most
# total price of 2800.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. Report seller_id(s) with the highest total sales price
        (SUM(price)). Ties return all such sellers.

        Algorithm:
        - GROUP BY seller_id SUM(price); keep those equal to MAX total.

        Complexity: O(S) aggregation over Sales.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT seller_id
    FROM Sales
    GROUP BY seller_id
    HAVING SUM(price) = (
        SELECT SUM(price)
        FROM Sales
        GROUP BY seller_id
        ORDER BY SUM(price) DESC
        LIMIT 1
    );
    """
# @lc code=end
