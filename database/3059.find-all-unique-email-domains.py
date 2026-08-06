#
# @lc app=leetcode id=3059 lang=python3
#
# [3059] Find All Unique Email Domains
#
# https://leetcode.com/problems/find-all-unique-email-domains/description/
#
# database
# Easy (70.27%)
# Likes:    13
# Dislikes: 8
# Total Accepted:    4.5K
# Total Submissions: 6.4K
# Testcase Example:  "{\"headers\":{\"Emails\":[\"id\",\"email\"]},\"rows\":{\"Emails\":[[336,\"hwkiy@test.edu\"],[489,\"adcmaf@outlook.com\"],[449,\"vrzmwyum@yahoo.com\"],[95,\"tof@test.edu\"],[320,\"jxhbagkpm@example.org\"],[411,\"zxcf@outlook.com\"]]}}"
#
#
# Table: Emails
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | id          | int     |
# | email       | varchar |
# +-------------+---------+
# id is the primary key (column with unique values) for this table.
# Each row of this table contains an email. The emails will not contain
# uppercase letters.
#
# Write a solution to find all unique email domains and count the number
# of individuals associated with each domain. Consider only those domains
# that end with .com.
#
# Return the result table orderd by email domains in ascending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Emails table:
# +-----+-----------------------+
# | id  | email                 |
# +-----+-----------------------+
# | 336 | hwkiy@test.edu        |
# | 489 | adcmaf@outlook.com    |
# | 449 | vrzmwyum@yahoo.com    |
# | 95  | tof@test.edu          |
# | 320 | jxhbagkpm@example.org |
# | 411 | zxcf@outlook.com      |
# +----+------------------------+
# Output:
# +--------------+-------+
# | email_domain | count |
# +--------------+-------+
# | outlook.com  | 2     |
# | yahoo.com    | 1     |
# +--------------+-------+
# Explanation:
# - The valid domains ending with ".com" are only "outlook.com" and
# "yahoo.com", with respective counts of 2 and 1.
# Output table is ordered by email_domains in ascending order.
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Emails(id, email). Unique domains ending in .com with counts.
        Order by email_domain ASC.

        Algorithm:
        - SUBSTRING_INDEX(email, '@', -1); filter LIKE '%.com'; GROUP BY domain.

        Complexity: O(N).
        """
        self.sql = """
SELECT
    SUBSTRING_INDEX(email, '@', -1) AS email_domain,
    COUNT(*) AS count
FROM Emails
WHERE email LIKE '%.com'
GROUP BY 1
ORDER BY 1;
"""
        return self.sql
# @lc code=end

