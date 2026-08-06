#
# @lc app=leetcode id=3451 lang=python3
#
# [3451] Find Invalid IP Addresses
#
# https://leetcode.com/problems/find-invalid-ip-addresses/description/
#
# database
# Hard (48.14%)
# Likes:    41
# Dislikes: 10
# Total Accepted:    14.2K
# Total Submissions: 29.5K
# Testcase Example:  "{\"headers\": {\"logs\": [\"log_id\", \"ip\", \"status_code\"]}, \"rows\": {\"logs\": [[8, \"127.0.0.1\", 200], [9, \"192.168..1\", 400]]}}"
#
#
# Table:  logs
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | log_id      | int     |
# | ip          | varchar |
# | status_code | int     |
# +-------------+---------+
# log_id is the unique key for this table.
# Each row contains server access log information including IP address and
# HTTP status code.
#
# Write a solution to find invalid IP addresses. An IPv4 address is
# invalid if it meets any of these conditions:
#
# Contains numbers greater than 255 in any octet
#
# Has leading zeros in any octet (like 01.02.03.04)
#
# Has less or more than 4 octets
#
# Return the result table ordered by invalid_count, ip in descending order
# respectively.
#
# The result format is in the following example.
#
# Example:
#
# Input:
#
# logs table:
#
# +--------+---------------+-------------+
# | log_id | ip            | status_code |
# +--------+---------------+-------------+
# | 1      | 192.168.1.1   | 200         |
# | 2      | 256.1.2.3     | 404         |
# | 3      | 192.168.001.1 | 200         |
# | 4      | 192.168.1.1   | 200         |
# | 5      | 192.168.1     | 500         |
# | 6      | 256.1.2.3     | 404         |
# | 7      | 192.168.001.1 | 200         |
# +--------+---------------+-------------+
#
# Output:
#
# +---------------+--------------+
# | ip            | invalid_count|
# +---------------+--------------+
# | 256.1.2.3     | 2            |
# | 192.168.001.1 | 2            |
# | 192.168.1     | 1            |
# +---------------+--------------+
#
# Explanation:
#
# 256.1.2.3 is invalid because 256 > 255
#
# 192.168.001.1 is invalid because of leading zeros
#
# 192.168.1 is invalid because it has only 3 octets
#
# The output table is ordered by invalid_count, ip in descending order
# respectively.
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: find invalid IPv4 strings in logs — wrong octet count, leading
        zeros, or any octet > 255 — and count occurrences per ip.

        Algorithm:
        - Filter with LENGTH/REPLACE for '.' count, REGEXP for leading zeros, and
          numeric comparisons via SUBSTRING_INDEX for >255.
        - GROUP BY ip; ORDER BY invalid_count DESC, ip DESC.

        Complexity: O(N log N) for grouping/sorting.
        """
        self.sql = """
SELECT
    ip,
    COUNT(*) AS invalid_count
FROM logs
WHERE
    LENGTH(ip) - LENGTH(REPLACE(ip, '.', '')) != 3
    OR SUBSTRING_INDEX(ip, '.', 1) REGEXP '^0[0-9]'
    OR SUBSTRING_INDEX(SUBSTRING_INDEX(ip, '.', 2), '.', -1) REGEXP '^0[0-9]'
    OR SUBSTRING_INDEX(SUBSTRING_INDEX(ip, '.', 3), '.', -1) REGEXP '^0[0-9]'
    OR SUBSTRING_INDEX(ip, '.', -1) REGEXP '^0[0-9]'
    OR SUBSTRING_INDEX(ip, '.', 1) > 255
    OR SUBSTRING_INDEX(SUBSTRING_INDEX(ip, '.', 2), '.', -1) > 255
    OR SUBSTRING_INDEX(SUBSTRING_INDEX(ip, '.', 3), '.', -1) > 255
    OR SUBSTRING_INDEX(ip, '.', -1) > 255
GROUP BY ip
ORDER BY invalid_count DESC, ip DESC;
"""
        return self.sql
# @lc code=end
