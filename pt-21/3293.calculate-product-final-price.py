#
# @lc app=leetcode id=3293 lang=python3
#
# [3293] Calculate Product Final Price
#
# https://leetcode.com/problems/calculate-product-final-price/description/
#
# database
# Medium (78.73%)
# Likes:    10
# Dislikes: 1
# Total Accepted:    3.1K
# Total Submissions: 3.9K
# Testcase Example:  "{\"headers\":{\"Products\":[\"product_id\",\"category\",\"price\"],\"Discounts\":[\"category\",\"discount\"]},\"rows\":{\"Products\":[[1,\"Electronics\",1000],[2,\"Clothing\",50],[3,\"Electronics\",1200],[4,\"Home\",500]],\"Discounts\":[[\"Electronics\",10],[\"Clothing\",20]]}}"
#
#
# Table: Products
#
# +------------+---------+
# | Column Name| Type    |
# +------------+---------+
# | product_id | int     |
# | category   | varchar |
# | price      | decimal |
# +------------+---------+
# product_id is the unique key for this table.
# Each row includes the product's ID, its category, and its price.
#
# Table: Discounts
#
# +------------+---------+
# | Column Name| Type    |
# +------------+---------+
# | category   | varchar |
# | discount   | int     |
# +------------+---------+
# category is the primary key for this table.
# Each row contains a product category and the percentage discount applied
# to that category (values range from 0 to 100).
#
# Write a solution to find the final price of each product after applying
# the category discount. If a product's category has no associated
# discount, its price remains unchanged.
#
# Return the result table ordered by product_id in ascending order.
#
# The result format is in the following example.
#
# Example:
#
# Input:
#
# Products table:
#
# +------------+-------------+-------+
# | product_id | category    | price |
# +------------+-------------+-------+
# | 1          | Electronics | 1000  |
# | 2          | Clothing    | 50    |
# | 3          | Electronics | 1200  |
# | 4          | Home        | 500   |
# +------------+-------------+-------+
#
# Discounts table:
#
# +------------+----------+
# | category   | discount |
# +------------+----------+
# | Electronics| 10       |
# | Clothing   | 20       |
# +------------+----------+
#
# Output:
#
# +------------+------------+-------------+
# | product_id | final_price| category    |
# +------------+------------+-------------+
# | 1          | 900        | Electronics |
# | 2          | 40         | Clothing    |
# | 3          | 1080       | Electronics |
# | 4          | 500        | Home        |
# +------------+------------+-------------+
#
# Explanation:
#
# For product 1, it belongs to the Electronics category which has a 10%
# discount, so the final price is 1000 - (10% of 1000) = 900.
#
# For product 2, it belongs to the Clothing category which has a 20%
# discount, so the final price is 50 - (20% of 50) = 40.
#
# For product 3, it belongs to the Electronics category and receives a 10%
# discount, so the final price is 1200 - (10% of 1200) = 1080.
#
# For product 4, no discount is available for the Home category, so the
# final price remains 500.
#
# Result table is ordered by product_id in ascending order.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Products(product_id, category, price) and
        Discounts(category, discount). Final price after category % off;
        unchanged if no discount row.

        Algorithm:
        - LEFT JOIN Discounts on category.
        - final_price = price * (100 - COALESCE(discount, 0)) / 100.
        - ORDER BY product_id.

        Complexity: O(N).
        """
        self.sql = """
SELECT
    p.product_id,
    p.price * (100 - COALESCE(d.discount, 0)) / 100 AS final_price,
    p.category
FROM
    Products p
    LEFT JOIN Discounts d ON p.category = d.category
ORDER BY
    p.product_id;
"""
        return self.sql
# @lc code=end
