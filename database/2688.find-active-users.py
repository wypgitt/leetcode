#
# @lc app=leetcode id=2688 lang=python3
#
# [2688] Find Active Users
#
# https://leetcode.com/problems/find-active-users/description/
#
# database
# Medium (45.01%)
# Likes:    28
# Dislikes: 8
# Total Accepted:    6.3K
# Total Submissions: 14.1K
# Testcase Example:  "{\"headers\":{\"Users\":[\"user_id\",\"item\",\"created_at\",\"amount\"]},\"rows\":{\"Users\":[[5,\"Smart Crock Pot\",\"2021-09-18\",698882],[6,\"Smart Lock\",\"2021-09-14\",11487],[6,\"Smart Thermostat\",\"2021-09-10\",674762],[8,\"Smart Light Strip\",\"2021-09-29\",630773],[4,\"Smart Cat Feeder\",\"2021-09-02\",693545],[4,\"Smart Bed\",\"2021-09-13\",170249]]}}"
#
#
# Table: Users
#
# +-------------+----------+
# | Column Name | Type     |
# +-------------+----------+
# | user_id     | int      |
# | item        | varchar  |
# | created_at  | datetime |
# | amount      | int      |
# +-------------+----------+
# This table may contain duplicate records.
# Each row includes the user ID, the purchased item, the date of purchase,
# and the purchase amount.
#
# Write a solution to identify active users. An active user is a user that
# has made a second purchase within 7 days of any other of their
# purchases.
#
# For example, if the ending date is May 31, 2023. So any date between May
# 31, 2023, and June 7, 2023 (inclusive) would be considered "within 7
# days" of May 31, 2023.
#
# Return a list of user_id which denotes the list of active users in any
# order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Users table:
# +---------+-------------------+------------+--------+
# | user_id | item              | created_at | amount |
# +---------+-------------------+------------+--------+
# | 5       | Smart Crock Pot   | 2021-09-18 | 698882 |
# | 6       | Smart Lock        | 2021-09-14 | 11487  |
# | 6       | Smart Thermostat  | 2021-09-10 | 674762 |
# | 8       | Smart Light Strip | 2021-09-29 | 630773 |
# | 4       | Smart Cat Feeder  | 2021-09-02 | 693545 |
# | 4       | Smart Bed         | 2021-09-13 | 170249 |
# +---------+-------------------+------------+--------+
# Output:
# +---------+
# | user_id |
# +---------+
# | 6       |
# +---------+
# Explanation:
# - User with user_id 5 has only one transaction, so he is not an active
# user.
# - User with user_id 6 has two transaction his first transaction was on
# 2021-09-10 and second transation was on 2021-09-14. The distance between
# the first and second transactions date is <= 7 days. So he is an active
# user.
# - User with user_id 8 has only one transaction, so he is not an active
# user.
# - User with user_id 4 has two transaction his first transaction was on
# 2021-09-02 and second transation was on 2021-09-13. The distance between
# the first and second transactions date is > 7 days. So he is not an
# active user.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Users(user_id, item, created_at, amount). Active user = made a second purchase
        within 7 days of any other of their purchases. Return distinct active user_ids.

        Algorithm:
        - Window LAG(created_at) per user ordered by date; keep rows with DATEDIFF <= 7.

        Complexity: O(N log N).
        """
        self.sql = """
SELECT DISTINCT user_id
FROM (
  SELECT
    user_id,
    created_at,
    LAG(created_at, 1) OVER (
      PARTITION BY user_id
      ORDER BY created_at
    ) AS prev_created_at
  FROM Users
) AS t
WHERE DATEDIFF(created_at, prev_created_at) <= 7;
"""
        return self.sql
# @lc code=end
