#
# @lc app=leetcode id=196 lang=python3
#
# [196] Delete Duplicate Emails
#
# https://leetcode.com/problems/delete-duplicate-emails/description/
#
# algorithms
# Easy (66.48%)
# Likes:    2160
# Dislikes: 431
# Total Accepted:    1.0M
# Total Submissions: 1.6M
# Testcase Example:  "{\"headers\": {\"Person\": [\"id\", \"email\"]}, \"rows\": {\"Person\": [[1, \"john@example.com\"], [2, \"bob@example.com\"], [3, \"john@example.com\"]]}}"
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
# Write a solution to delete all duplicate emails, keeping only one unique
# email with the smallest id.
#
# For SQL users, please note that you are supposed to write a DELETE statement
# and not a SELECT one.
#
# For Pandas users, please note that you are supposed to modify Person in
# place.
#
# After running your script, the answer shown is the Person table. The driver
# will first compile and run your piece of code and then show the Person table.
# The final order of the Person table does not matter.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Person table:
# +----+------------------+
# | id | email |
# +----+------------------+
# | 1 | john@example.com |
# | 2 | bob@example.com |
# | 3 | john@example.com |
# +----+------------------+
# Output:
# +----+------------------+
# | id | email |
# +----+------------------+
# | 1 | john@example.com |
# | 2 | bob@example.com |
# +----+------------------+
# Explanation: john@example.com is repeated two times. We keep the row with the
# smallest Id = 1.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Self-join Person to itself on email and delete the row with the larger
        id whenever a duplicate exists — keeps the smallest id per email.

        Algorithm:
        - DELETE p1 FROM Person p1 JOIN Person p2
          ON p1.email = p2.email AND p1.id > p2.id.

        Complexity: O(P) with indexes on email/id; each duplicate pair drives
        a delete candidate.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    DELETE p1
    FROM Person p1
    JOIN Person p2
        ON p1.email = p2.email
       AND p1.id > p2.id;
    """
# @lc code=end
