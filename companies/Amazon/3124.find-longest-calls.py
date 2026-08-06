#
# @lc app=leetcode id=3124 lang=python3
#
# [3124] Find Longest Calls
#
# https://leetcode.com/problems/find-longest-calls/description/
#
# database
# Medium (63.98%)
# Likes:    7
# Dislikes: 5
# Total Accepted:    3.3K
# Total Submissions: 5.2K
# Testcase Example:  "{\"headers\":{\"Contacts\":[\"id\",\"first_name\",\"last_name\"],\"Calls\":[\"contact_id\",\"type\",\"duration\"]},\"rows\":{\"Contacts\":[[1,\"John\",\"Doe\"],[2,\"Jane\",\"Smith\"],[3,\"Alice\",\"Johnson\"],[4,\"Michael\",\"Brown\"],[5,\"Emily\",\"Davis\"]],\"Calls\":[[1,\"incoming\",120],[1,\"outgoing\",180],[2,\"incoming\",300],[2,\"outgoing\",240],[3,\"incoming\",150],[3,\"outgoing\",360],[4,\"incoming\",420],[4,\"outgoing\",200],[5,\"incoming\",180],[5,\"outgoing\",280]]}}"
#
#
# Table: Contacts
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | id          | int     |
# | first_name  | varchar |
# | last_name   | varchar |
# +-------------+---------+
# id is the primary key (column with unique values) of this table.
# id is a foreign key (reference column) to Calls table.
# Each row of this table contains id, first_name, and last_name.
#
# Table: Calls
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | contact_id  | int  |
# | type        | enum |
# | duration    | int  |
# +-------------+------+
# (contact_id, type, duration) is the primary key (column with unique
# values) of this table.
# type is an ENUM (category) type of ('incoming', 'outgoing').
# Each row of this table contains information about calls, comprising of
# contact_id, type, and duration in seconds.
#
# Write a solution to find the three longest incoming and outgoing calls.
#
# Return the result table ordered by type, duration, and first_name in
# descending order and duration must be formatted as HH:MM:SS.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
#
# Contacts table:
#
# +----+------------+-----------+
# | id | first_name | last_name |
# +----+------------+-----------+
# | 1  | John       | Doe       |
# | 2  | Jane       | Smith     |
# | 3  | Alice      | Johnson   |
# | 4  | Michael    | Brown     |
# | 5  | Emily      | Davis     |
# +----+------------+-----------+
#
# Calls table:
#
# +------------+----------+----------+
# | contact_id | type     | duration |
# +------------+----------+----------+
# | 1          | incoming | 120      |
# | 1          | outgoing | 180      |
# | 2          | incoming | 300      |
# | 2          | outgoing | 240      |
# | 3          | incoming | 150      |
# | 3          | outgoing | 360      |
# | 4          | incoming | 420      |
# | 4          | outgoing | 200      |
# | 5          | incoming | 180      |
# | 5          | outgoing | 280      |
# +------------+----------+----------+
#
# Output:
#
# +-----------+----------+-------------------+
# | first_name| type     | duration_formatted|
# +-----------+----------+-------------------+
# | Alice     | outgoing | 00:06:00          |
# | Emily     | outgoing | 00:04:40          |
# | Jane      | outgoing | 00:04:00          |
# | Michael   | incoming | 00:07:00          |
# | Jane      | incoming | 00:05:00          |
# | Emily     | incoming | 00:03:00          |
# +-----------+----------+-------------------+
#
# Explanation:
#
# Alice had an outgoing call lasting 6 minutes.
#
# Emily had an outgoing call lasting 4 minutes and 40 seconds.
#
# Jane had an outgoing call lasting 4 minutes.
#
# Michael had an incoming call lasting 7 minutes.
#
# Jane had an incoming call lasting 5 minutes.
#
# Emily had an incoming call lasting 3 minutes.
#
# Note: Output table is sorted by type, duration, and first_name in
# descending order.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Contacts(id, first_name, last_name), Calls(contact_id, type,
        duration). For each type ('incoming'/'outgoing'), take the 3 longest
        calls; format duration as HH:MM:SS. Order by type, duration, first_name
        all DESC.

        Algorithm:
        - JOIN Calls to Contacts; ROW_NUMBER() PARTITION BY type ORDER BY
          duration DESC; keep rn <= 3; format seconds; ORDER BY type DESC,
          duration DESC, first_name DESC.

        Complexity: O(N log N).
        """
        self.sql = """
WITH ranked AS (
  SELECT
    c.first_name,
    cl.type,
    cl.duration,
    ROW_NUMBER() OVER (
      PARTITION BY cl.type
      ORDER BY cl.duration DESC
    ) AS rn
  FROM Calls cl
  JOIN Contacts c ON c.id = cl.contact_id
)
SELECT
  first_name,
  type,
  CONCAT(
    LPAD(FLOOR(duration / 3600), 2, '0'), ':',
    LPAD(FLOOR((duration % 3600) / 60), 2, '0'), ':',
    LPAD(duration % 60, 2, '0')
  ) AS duration_formatted
FROM ranked
WHERE rn <= 3
ORDER BY type DESC, duration DESC, first_name DESC;
"""
        return self.sql
# @lc code=end
