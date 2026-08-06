#
# @lc app=leetcode id=3204 lang=python3
#
# [3204] Bitwise User Permissions Analysis
#
# https://leetcode.com/problems/bitwise-user-permissions-analysis/description/
#
# database
# Medium (92.37%)
# Likes:    9
# Dislikes: 3
# Total Accepted:    2.3K
# Total Submissions: 2.5K
# Testcase Example:  "{\"headers\":{\"user_permissions\":[\"user_id\",\"permissions\"]},\"rows\":{\"user_permissions\":[[1,5],[2,12],[3,7],[4,3]]}}"
#
#
# Table: user_permissions
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | user_id     | int     |
# | permissions | int     |
# +-------------+---------+
# user_id is the primary key.
# Each row of this table contains the user ID and their permissions
# encoded as an integer.
#
# Consider that each bit in the permissions integer represents a different
# access level or feature that a user has.
#
# Write a solution to calculate the following:
#
# common_perms: The access level granted to all users. This is computed
# using a bitwise AND operation on the permissions column.
#
# any_perms: The access level granted to any user. This is computed using
# a bitwise OR operation on the permissions column.
#
# Return the result table in any order.
#
# The result format is shown in the following example.
#
# Example:
#
# Input:
#
# user_permissions table:
#
# +---------+-------------+
# | user_id | permissions |
# +---------+-------------+
# | 1       | 5           |
# | 2       | 12          |
# | 3       | 7           |
# | 4       | 3           |
# +---------+-------------+
#
# Output:
#
# +-------------+--------------+
# | common_perms | any_perms   |
# +--------------+-------------+
# | 0            | 15          |
# +--------------+-------------+
#
# Explanation:
#
# common_perms: Represents the bitwise AND result of all permissions:
#
# For user 1 (5): 5 (binary 0101)
#
# For user 2 (12): 12 (binary 1100)
#
# For user 3 (7): 7 (binary 0111)
#
# For user 4 (3): 3 (binary 0011)
#
# Bitwise AND: 5 & 12 & 7 & 3 = 0 (binary 0000)
#
# any_perms: Represents the bitwise OR result of all permissions:
#
# Bitwise OR: 5 | 12 | 7 | 3 = 15 (binary 1111)
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: user_permissions(user_id, permissions). Compute bitwise AND
        across all users (common_perms) and bitwise OR (any_perms).

        Algorithm:
        - SELECT BIT_AND(permissions), BIT_OR(permissions) from the table.

        Complexity: O(N).
        """
        self.sql = """
SELECT
    BIT_AND(permissions) AS common_perms,
    BIT_OR(permissions) AS any_perms
FROM user_permissions;
"""
        return self.sql
# @lc code=end
