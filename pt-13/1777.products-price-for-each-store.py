#
# @lc app=leetcode id=1777 lang=python3
#
# [1777] Product's Price for Each Store
#
# https://leetcode.com/problems/products-price-for-each-store/description/
#
# database
# Easy (82.05%)
# Likes:    142
# Dislikes: 13
# Total Accepted:    25.2K
# Total Submissions: 30.7K
# Testcase Example:  "{\"headers\":{\"Products\":[\"product_id\",\"store\",\"price\"]},\"rows\":{\"Products\":[[\"0\",\"store1\",\"95\"],[\"0\",\"store3\",\"105\"],[\"0\",\"store2\",\"100\"],[\"1\",\"store1\",\"70\"],[\"1\",\"store3\",\"80\"]]}}"
#
#
# Table: Products
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | product_id  | int     |
# | store       | enum    |
# | price       | int     |
# +-------------+---------+
# In SQL, (product_id, store) is the primary key for this table.
# store is a category of type ('store1', 'store2', 'store3') where each
# represents the store this product is available at.
# price is the price of the product at this store.
#
# Find the price of each product in each store.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Products table:
# +-------------+--------+-------+
# | product_id  | store  | price |
# +-------------+--------+-------+
# | 0           | store1 | 95    |
# | 0           | store3 | 105   |
# | 0           | store2 | 100   |
# | 1           | store1 | 70    |
# | 1           | store3 | 80    |
# +-------------+--------+-------+
# Output:
# +-------------+--------+--------+--------+
# | product_id  | store1 | store2 | store3 |
# +-------------+--------+--------+--------+
# | 0           | 95     | 100    | 105    |
# | 1           | 70     | null   | 80     |
# +-------------+--------+--------+--------+
# Explanation:
# Product 0 price's are 95 for store1, 100 for store2 and, 105 for store3.
# Product 1 price's are 70 for store1, 80 for store3 and, it's not sold in
# store2.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Products(product_id, store, price) → pivot to one row per
        product with store1/store2/store3 price columns (NULL if absent).

        Algorithm:
        - GROUP BY product_id with conditional MAX(CASE WHEN store=...).

        Complexity: O(N) aggregation.
        """
        return self.sql

    sql = """
    SELECT
        product_id,
        MAX(CASE WHEN store = 'store1' THEN price END) AS store1,
        MAX(CASE WHEN store = 'store2' THEN price END) AS store2,
        MAX(CASE WHEN store = 'store3' THEN price END) AS store3
    FROM Products
    GROUP BY product_id;
    """
# @lc code=end
