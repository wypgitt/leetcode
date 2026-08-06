#
# @lc app=leetcode id=182 lang=python3
#
# [182] Duplicate Emails
#
# https://leetcode.com/problems/duplicate-emails/description/
#
# algorithms
# Easy (74.13%)
# Likes:    2496
# Dislikes: 89
# Total Accepted:    1.3M
# Total Submissions: 1.7M
# Testcase Example:  "{\"headers\": {\"Person\": [\"id\", \"email\"]}, \"rows\": {\"Person\": [[1, \"a@b.com\"], [2, \"c@d.com\"], [3, \"a@b.com\"]]}}"
#
# Table: Person
#
# +-------------+---------+
# | Column Name | Type |
# +-------------+---------+
# | id | int |
# | email | varchar |
# +-------------+---------+
# id is the primary key (column with unique values) for this table.
# Each row of this table contains an email. The emails will not contain
# uppercase letters.
#
# Write a solution to report all the duplicate emails. Note that it's
# guaranteed that the email field is not NULL.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Person table:
# +----+---------+
# | id | email |
# +----+---------+
# | 1 | a@b.com |
# | 2 | c@d.com |
# | 3 | a@b.com |
# +----+---------+
# Output:
# +---------+
# | Email |
# +---------+
# | a@b.com |
# +---------+
# Explanation: a@b.com is repeated two times.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Duplicates are emails that appear more than once — GROUP BY email and
        keep groups with COUNT(*) > 1.

        Algorithm:
        - SELECT email FROM Person GROUP BY email HAVING COUNT(*) > 1.

        Complexity: O(P) with hash aggregation; index on email helps grouping.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT email AS Email
    FROM Person
    GROUP BY email
    HAVING COUNT(*) > 1;
    """
# @lc code=end
