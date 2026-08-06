#
# @lc app=leetcode id=2362 lang=python3
#
# [2362] Generate the Invoice
#
# https://leetcode.com/problems/generate-the-invoice/description/
#
# database
# Hard (76.18%)
# Likes:    35
# Dislikes: 30
# Total Accepted:    5.8K
# Total Submissions: 7.6K
# Testcase Example:  "{\"headers\":{\"Products\":[\"product_id\",\"price\"],\"Purchases\":[\"invoice_id\",\"product_id\",\"quantity\"]},\"rows\":{\"Products\":[[1,100],[2,200]],\"Purchases\":[[1,1,2],[3,2,1],[2,2,3],[2,1,4],[4,1,10]]}}"
#
#
# Table: Products
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | product_id  | int  |
# | price       | int  |
# +-------------+------+
# product_id contains unique values.
# Each row in this table shows the ID of a product and the price of one
# unit.
#
# Table: Purchases
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | invoice_id  | int  |
# | product_id  | int  |
# | quantity    | int  |
# +-------------+------+
# (invoice_id, product_id) is the primary key (combination of columns with
# unique values) for this table.
# Each row in this table shows the quantity ordered from one product in an
# invoice.
#
# Write a solution to show the details of the invoice with the highest
# price. If two or more invoices have the same price, return the details
# of the one with the smallest invoice_id.
#
# Return the result table in any order.
#
# The result format is shown in the following example.
#
# Example 1:
#
# Input:
# Products table:
# +------------+-------+
# | product_id | price |
# +------------+-------+
# | 1          | 100   |
# | 2          | 200   |
# +------------+-------+
# Purchases table:
# +------------+------------+----------+
# | invoice_id | product_id | quantity |
# +------------+------------+----------+
# | 1          | 1          | 2        |
# | 3          | 2          | 1        |
# | 2          | 2          | 3        |
# | 2          | 1          | 4        |
# | 4          | 1          | 10       |
# +------------+------------+----------+
# Output:
# +------------+----------+-------+
# | product_id | quantity | price |
# +------------+----------+-------+
# | 2          | 3        | 600   |
# | 1          | 4        | 400   |
# +------------+----------+-------+
# Explanation:
# Invoice 1: price = (2 * 100) = $200
# Invoice 2: price = (4 * 100) + (3 * 200) = $1000
# Invoice 3: price = (1 * 200) = $200
# Invoice 4: price = (10 * 100) = $1000
#
# The highest price is $1000, and the invoices with the highest prices are
# 2 and 4. We return the details of the one with the smallest ID, which is
# invoice 2.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Products(product_id, price), Purchases(invoice_id,
        product_id, quantity). Show line items of the invoice with highest
        total price (tie -> smallest invoice_id): product_id, quantity,
        line price = quantity*price.

        Algorithm:
        - Join; aggregate invoice totals; pick top invoice; return its lines.

        Complexity: O(N).
        """
        self.sql = """
WITH
  P AS (
    SELECT *
    FROM Purchases
    JOIN Products USING (product_id)
  ),
  T AS (
    SELECT invoice_id, SUM(price * quantity) AS amount
    FROM P
    GROUP BY invoice_id
    ORDER BY amount DESC, invoice_id
    LIMIT 1
  )
SELECT product_id, quantity, (quantity * price) AS price
FROM P
JOIN T USING (invoice_id);
"""
        return self.sql
# @lc code=end
