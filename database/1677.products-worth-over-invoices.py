#
# @lc app=leetcode id=1677 lang=python3
#
# [1677] Product's Worth Over Invoices
#
# https://leetcode.com/problems/products-worth-over-invoices/description/
#
# database
# Easy (38.64%)
# Likes:    40
# Dislikes: 136
# Total Accepted:    20.7K
# Total Submissions: 53.7K
# Testcase Example:  "{\"headers\":{\"Product\":[\"product_id\",\"name\"],\"Invoice\":[\"invoice_id\",\"product_id\",\"rest\",\"paid\",\"canceled\",\"refunded\"]},\"rows\":{\"Product\":[[0,\"ham\"],[1,\"bacon\"]],\"Invoice\":[[23,0,2,0,5,0],[12,0,0,4,0,3],[1,1,1,1,0,1],[2,1,1,0,1,1],[3,1,0,1,1,1],[4,1,1,1,1,0]]}}"
#
#
# Table: Product
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | product_id  | int     |
# | name        | varchar |
# +-------------+---------+
# product_id is the column with unique values for this table.
# This table contains the ID and the name of the product. The name
# consists of only lowercase English letters. No two products have the
# same name.
#
# Table: Invoice
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | invoice_id  | int  |
# | product_id  | int  |
# | rest        | int  |
# | paid        | int  |
# | canceled    | int  |
# | refunded    | int  |
# +-------------+------+
# invoice_id is the column with unique values for this table and the id of
# this invoice.
# product_id is the id of the product for this invoice.
# rest is the amount left to pay for this invoice.
# paid is the amount paid for this invoice.
# canceled is the amount canceled for this invoice.
# refunded is the amount refunded for this invoice.
#
# Write a solution that will, for all products, return each product name
# with the total amount due, paid, canceled, and refunded across all
# invoices.
#
# Return the result table ordered by product_name.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Product table:
# +------------+-------+
# | product_id | name  |
# +------------+-------+
# | 0          | ham   |
# | 1          | bacon |
# +------------+-------+
# Invoice table:
# +------------+------------+------+------+----------+----------+
# | invoice_id | product_id | rest | paid | canceled | refunded |
# +------------+------------+------+------+----------+----------+
# | 23         | 0          | 2    | 0    | 5        | 0        |
# | 12         | 0          | 0    | 4    | 0        | 3        |
# | 1          | 1          | 1    | 1    | 0        | 1        |
# | 2          | 1          | 1    | 0    | 1        | 1        |
# | 3          | 1          | 0    | 1    | 1        | 1        |
# | 4          | 1          | 1    | 1    | 1        | 0        |
# +------------+------------+------+------+----------+----------+
# Output:
# +-------+------+------+----------+----------+
# | name  | rest | paid | canceled | refunded |
# +-------+------+------+----------+----------+
# | bacon | 3    | 3    | 3        | 3        |
# | ham   | 2    | 4    | 5        | 3        |
# +-------+------+------+----------+----------+
# Explanation:
# - The amount of money left to pay for bacon is 1 + 1 + 0 + 1 = 3
# - The amount of money paid for bacon is 1 + 0 + 1 + 1 = 3
# - The amount of money canceled for bacon is 0 + 1 + 1 + 1 = 3
# - The amount of money refunded for bacon is 1 + 1 + 1 + 0 = 3
# - The amount of money left to pay for ham is 2 + 0 = 2
# - The amount of money paid for ham is 0 + 4 = 4
# - The amount of money canceled for ham is 5 + 0 = 5
# - The amount of money refunded for ham is 0 + 3 = 3
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. For each product, report name, rest (sum invoice.rest),
        paid (sum paid), canceled (sum canceled), refunded (sum refunded).
        Include products with no invoices as zeros. Order by name.

        Algorithm:
        - LEFT JOIN Invoice on product_id; GROUP BY product; IFNULL(SUM(...),0).

        Complexity: O(P+I).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT p.name,
           IFNULL(SUM(i.rest), 0) AS rest,
           IFNULL(SUM(i.paid), 0) AS paid,
           IFNULL(SUM(i.canceled), 0) AS canceled,
           IFNULL(SUM(i.refunded), 0) AS refunded
    FROM Product p
    LEFT JOIN Invoice i ON p.product_id = i.product_id
    GROUP BY p.product_id, p.name
    ORDER BY p.name;
    """
# @lc code=end
