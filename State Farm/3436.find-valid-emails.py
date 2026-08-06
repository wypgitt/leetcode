#
# @lc app=leetcode id=3436 lang=python3
#
# [3436] Find Valid Emails
#
# https://leetcode.com/problems/find-valid-emails/description/
#
# database
# Easy (43.31%)
# Likes:    67
# Dislikes: 9
# Total Accepted:    35.3K
# Total Submissions: 81.6K
# Testcase Example:  "{\"headers\":{\"Users\":[\"user_id\",\"email\"]},\"rows\":{\"Users\":[[1,\"alice@example.com\"],[2,\"bob_at_example.com\"],[3,\"charlie@example.net\"],[4,\"david@domain.com\"],[5,\"eve@invalid\"]]}}"
#
#
# Table: Users
#
# +-----------------+---------+
# | Column Name     | Type    |
# +-----------------+---------+
# | user_id         | int     |
# | email           | varchar |
# +-----------------+---------+
# (user_id) is the unique key for this table.
# Each row contains a user's unique ID and email address.
#
# Write a solution to find all the valid email addresses. A valid email
# address meets the following criteria:
#
# It contains exactly one @ symbol.
#
# It ends with .com.
#
# The part before the @ symbol contains only alphanumeric characters and
# underscores.
#
# The part after the @ symbol and before .com contains a domain name that
# contains only letters.
#
# Return the result table ordered by user_id in ascending order.
#
# Example:
#
# Input:
#
# Users table:
#
# +---------+---------------------+
# | user_id | email               |
# +---------+---------------------+
# | 1       | alice@example.com   |
# | 2       | bob_at_example.com  |
# | 3       | charlie@example.net |
# | 4       | david@domain.com    |
# | 5       | eve@invalid         |
# +---------+---------------------+
#
# Output:
#
# +---------+-------------------+
# | user_id | email             |
# +---------+-------------------+
# | 1       | alice@example.com |
# | 4       | david@domain.com  |
# +---------+-------------------+
#
# Explanation:
#
# alice@example.com is valid because it contains one @, alice is
# alphanumeric, and example.com starts with a letter and ends with .com.
#
# bob_at_example.com is invalid because it contains an underscore instead
# of an @.
#
# charlie@example.net is invalid because the domain does not end with
# .com.
#
# david@domain.com is valid because it meets all criteria.
#
# eve@invalid is invalid because the domain does not end with .com.
#
# Result table is ordered by user_id in ascending order.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Valid emails have exactly one @, local part [A-Za-z0-9_]+, domain letters
        only, and must end with .com.

        Algorithm:
        - REGEXP local@[A-Za-z]+.com with alphanumeric/underscore local part;
          ORDER BY user_id.

        Complexity: O(N).
        """
        self.sql = """
SELECT
    user_id,
    email
FROM Users
WHERE email REGEXP '^[A-Za-z0-9_]+@[A-Za-z]+\\.com$'
ORDER BY user_id;
"""
        return self.sql
# @lc code=end
