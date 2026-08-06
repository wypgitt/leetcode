#
# @lc app=leetcode id=1757 lang=python3
#
# [1757] Recyclable and Low Fat Products
#
# https://leetcode.com/problems/recyclable-and-low-fat-products/description/
#
# algorithms
# Easy (88.62%)
# Likes:    3426
# Dislikes: 133
# Total Accepted:    2.5M
# Total Submissions: 2.9M
# Testcase Example:  "{\"headers\":{\"Products\":[\"product_id\",\"low_fats\",\"recyclable\"]},\"rows\":{\"Products\":[[\"0\",\"Y\",\"N\"],[\"1\",\"Y\",\"Y\"],[\"2\",\"N\",\"Y\"],[\"3\",\"Y\",\"Y\"],[\"4\",\"N\",\"N\"]]}}"
#
# Table: Products
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | product_id | int |
# | low_fats | enum |
# | recyclable | enum |
# +-------------+---------+
# product_id is the primary key (column with unique values) for this table.
# low_fats is an ENUM (category) of type ('Y', 'N') where 'Y' means this
# product is low fat and 'N' means it is not.
# recyclable is an ENUM (category) of types ('Y', 'N') where 'Y' means this
# product is recyclable and 'N' means it is not.
#
# Write a solution to find the ids of products that are both low fat and
# recyclable.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Products table:
# +-------------+----------+------------+
# | product_id | low_fats | recyclable |
# +-------------+----------+------------+
# | 0 | Y | N |
# | 1 | Y | Y |
# | 2 | N | Y |
# | 3 | Y | Y |
# | 4 | N | N |
# +-------------+----------+------------+
# Output:
# +-------------+
# | product_id |
# +-------------+
# | 1 |
# | 3 |
# +-------------+
# Explanation: Only products 1 and 3 are both low fat and recyclable.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Filter Products that are both low fat and recyclable ('Y').

        Algorithm:
        - SELECT product_id FROM Products WHERE low_fats='Y' AND recyclable='Y'

        Complexity: O(N) table scan.
        """
        return self.sql

    sql = """
    SELECT product_id
    FROM Products
    WHERE low_fats = 'Y' AND recyclable = 'Y';
    """
# @lc code=end
