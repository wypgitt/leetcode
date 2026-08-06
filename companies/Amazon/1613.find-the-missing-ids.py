#
# @lc app=leetcode id=1613 lang=python3
#
# [1613] Find the Missing IDs
#
# https://leetcode.com/problems/find-the-missing-ids/description/
#
# database
# Medium (72.85%)
# Likes:    238
# Dislikes: 31
# Total Accepted:    23.7K
# Total Submissions: 32.5K
# Testcase Example:  "{\"headers\": {\"Customers\": [\"customer_id\", \"customer_name\"]}, \"rows\": {\"Customers\": [[1, \"Alice\"], [4, \"Bob\"], [5, \"Charlie\"]]}}"
#
#
# Table: Customers
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | customer_id   | int     |
# | customer_name | varchar |
# +---------------+---------+
# customer_id is the column with unique values for this table.
# Each row of this table contains the name and the id customer.
#
# Write a solution to find the missing customer IDs. The missing IDs are
# ones that are not in the Customers table but are in the range between 1
# and the maximum customer_id present in the table.
#
# Notice that the maximum customer_id will not exceed 100.
#
# Return the result table ordered by ids in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Customers table:
# +-------------+---------------+
# | customer_id | customer_name |
# +-------------+---------------+
# | 1           | Alice         |
# | 4           | Bob           |
# | 5           | Charlie       |
# +-------------+---------------+
# Output:
# +-----+
# | ids |
# +-----+
# | 2   |
# | 3   |
# +-----+
# Explanation:
# The maximum customer_id present in the table is 5, so in the range
# [1,5], IDs 2 and 3 are missing from the table.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Find missing ids in [1, MAX(customer_id)] not present in Customers.

        Algorithm:
        - Recursive CTE generate 1..max_id; LEFT JOIN Customers; keep NULLs; ORDER BY id.

        Complexity: O(M) where M = max customer_id.
        """
        return self.sql

    sql = """
    WITH RECURSIVE ids AS (
        SELECT 1 AS id
        UNION ALL
        SELECT id + 1 FROM ids
        WHERE id < (SELECT MAX(customer_id) FROM Customers)
    )
    SELECT i.id AS ids
    FROM ids i
    LEFT JOIN Customers c ON i.id = c.customer_id
    WHERE c.customer_id IS NULL
    ORDER BY i.id;
    """
# @lc code=end
