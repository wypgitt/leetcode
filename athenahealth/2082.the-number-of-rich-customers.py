#
# @lc app=leetcode id=2082 lang=python3
#
# [2082] The Number of Rich Customers
#
# https://leetcode.com/problems/the-number-of-rich-customers/description/
#
# database
# Easy (77.28%)
# Likes:    101
# Dislikes: 25
# Total Accepted:    31.7K
# Total Submissions: 41K
# Testcase Example:  "{\"headers\":{\"Store\":[\"bill_id\",\"customer_id\",\"amount\"]},\"rows\":{\"Store\":[[6,1,549],[8,1,834],[4,2,394],[11,3,657],[13,3,257]]}}"
#
#
# Table: Store
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | bill_id     | int  |
# | customer_id | int  |
# | amount      | int  |
# +-------------+------+
# bill_id is the primary key (column with unique values) for this table.
# Each row contains information about the amount of one bill and the
# customer associated with it.
#
# Write a solution to report the number of customers who had at least one
# bill with an amount strictly greater than 500.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Store table:
# +---------+-------------+--------+
# | bill_id | customer_id | amount |
# +---------+-------------+--------+
# | 6       | 1           | 549    |
# | 8       | 1           | 834    |
# | 4       | 2           | 394    |
# | 11      | 3           | 657    |
# | 13      | 3           | 257    |
# +---------+-------------+--------+
# Output:
# +------------+
# | rich_count |
# +------------+
# | 2          |
# +------------+
# Explanation:
# Customer 1 has two bills with amounts strictly greater than 500.
# Customer 2 does not have any bills with an amount strictly greater than
# 500.
# Customer 3 has one bill with an amount strictly greater than 500.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Store(bill_id, customer_id, amount). Count distinct
        customers who have at least one bill with amount > 500.

        Algorithm:
        - COUNT(DISTINCT customer_id) WHERE amount > 500.

        Complexity: O(N).
        """
        self.sql = """
        SELECT COUNT(DISTINCT customer_id) AS rich_count
        FROM Store
        WHERE amount > 500
        """
        return self.sql
# @lc code=end
