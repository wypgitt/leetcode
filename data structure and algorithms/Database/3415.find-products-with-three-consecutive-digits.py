#
# @lc app=leetcode id=3415 lang=python3
#
# [3415] Find Products with Three Consecutive Digits 
#
# https://leetcode.com/problems/find-products-with-three-consecutive-digits/description/
#
# database
# Easy (80.10%)
# Likes:    4
# Dislikes: 3
# Total Accepted:    2.3K
# Total Submissions: 2.9K
# Testcase Example:  "{\"headers\":{\"Products\":[\"product_id\",\"name\"]},\"rows\":{\"Products\":[[1,\"ABC123XYZ\"],[2,\"A12B34C\"],[3,\"Product56789\"],[4,\"NoDigitsHere\"],[5,\"789Product\"],[6,\"Item003Description\"],[7,\"Product12X34\"]]}}"
#
#
# Table: Products
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | product_id  | int     |
# | name        | varchar |
# +-------------+---------+
# product_id is the unique key for this table.
# Each row of this table contains the ID and name of a product.
#
# Write a solution to find all products whose names contain a sequence of
# exactly three consecutive digits in a row.
#
# Return the result table ordered by product_id in ascending order.
#
# The result format is in the following example.
#
# Note that the name may contain multiple such sequences, but each should
# have length three.
#
# Example:
#
# Input:
#
# products table:
#
# +-------------+--------------------+
# | product_id  | name               |
# +-------------+--------------------+
# | 1           | ABC123XYZ          |
# | 2           | A12B34C            |
# | 3           | Product56789       |
# | 4           | NoDigitsHere       |
# | 5           | 789Product         |
# | 6           | Item003Description |
# | 7           | Product12X34       |
# +-------------+--------------------+
#
# Output:
#
# +-------------+--------------------+
# | product_id  | name               |
# +-------------+--------------------+
# | 1           | ABC123XYZ          |
# | 5           | 789Product         |
# | 6           | Item003Description |
# +-------------+--------------------+
#
# Explanation:
#
# Product 1: ABC123XYZ contains the digits 123.
#
# Product 5: 789Product contains the digits 789.
#
# Product 6: Item003Description contains 003, which is exactly three
# digits.
#
# Note:
#
# Results are ordered by product_id in ascending order.
#
# Only products with exactly three consecutive digits in their names are
# included in the result.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: products whose name contains a run of exactly three
        consecutive digits (not part of a longer digit run).

        Algorithm:
        - REGEXP matches digit-triple bounded by non-digits or string ends.

        Complexity: O(N * L) scan of names.
        """
        self.sql = """
SELECT
    product_id,
    name
FROM Products
WHERE
    name REGEXP '[^0-9][0-9]{3}[^0-9]'
    OR name REGEXP '^[0-9]{3}[^0-9]'
    OR name REGEXP '[^0-9][0-9]{3}$'
    OR name REGEXP '^[0-9]{3}$'
ORDER BY product_id;
"""
        return self.sql
# @lc code=end
