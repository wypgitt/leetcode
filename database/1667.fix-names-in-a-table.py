#
# @lc app=leetcode id=1667 lang=python3
#
# [1667] Fix Names in a Table
#
# https://leetcode.com/problems/fix-names-in-a-table/description/
#
# algorithms
# Easy (60.62%)
# Likes:    1104
# Dislikes: 146
# Total Accepted:    489K
# Total Submissions: 807K
# Testcase Example:  "{\"headers\":{\"Users\":[\"user_id\",\"name\"]},\"rows\":{\"Users\":[[1,\"aLice\"],[2,\"bOB\"]]}}"
#
# Table: Users
#
# +----------------+---------+
# | Column Name | Type |
# +----------------+---------+
# | user_id | int |
# | name | varchar |
# +----------------+---------+
# user_id is the primary key (column with unique values) for this table.
# This table contains the ID and the name of the user. The name consists of
# only lowercase and uppercase characters.
#
# Write a solution to fix the names so that only the first character is
# uppercase and the rest are lowercase.
#
# Return the result table ordered by user_id.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Users table:
# +---------+-------+
# | user_id | name |
# +---------+-------+
# | 1 | aLice |
# | 2 | bOB |
# +---------+-------+
# Output:
# +---------+-------+
# | user_id | name |
# +---------+-------+
# | 1 | Alice |
# | 2 | Bob |
# +---------+-------+
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Fix names: first char uppercase, rest lowercase (Users.name).

        Algorithm:
        - SELECT user_id, CONCAT(UPPER(LEFT(name,1)), LOWER(SUBSTRING(name,2)))
          ORDER BY user_id.

        Complexity: O(U).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT user_id,
           CONCAT(UPPER(LEFT(name, 1)), LOWER(SUBSTRING(name, 2))) AS name
    FROM Users
    ORDER BY user_id;
    """
# @lc code=end
