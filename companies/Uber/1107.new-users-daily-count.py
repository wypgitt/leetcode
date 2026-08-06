#
# @lc app=leetcode id=1107 lang=python3
#
# [1107] New Users Daily Count
#
# https://leetcode.com/problems/new-users-daily-count/description/
#
# database
# Medium (44.42%)
# Likes:    168
# Dislikes: 177
# Total Accepted:    45.8K
# Total Submissions: 103K
# Testcase Example:  "{\"headers\":{\"Traffic\":[\"user_id\",\"activity\",\"activity_date\"]},\"rows\":{\"Traffic\":[[1,\"login\",\"2019-05-01\"],[1,\"homepage\",\"2019-05-01\"],[1,\"logout\",\"2019-05-01\"],[2,\"login\",\"2019-06-21\"],[2,\"logout\",\"2019-06-21\"],[3,\"login\",\"2019-01-01\"],[3,\"jobs\",\"2019-01-01\"],[3,\"logout\",\"2019-01-01\"],[4,\"login\",\"2019-06-21\"],[4,\"groups\",\"2019-06-21\"],[4,\"logout\",\"2019-06-21\"],[5,\"login\",\"2019-03-01\"],[5,\"logout\",\"2019-03-01\"],[5,\"login\",\"2019-06-21\"],[5,\"logout\",\"2019-06-21\"]]}}"
#
#
# Table: Traffic
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | user_id       | int     |
# | activity      | enum    |
# | activity_date | date    |
# +---------------+---------+
# This table may have duplicate rows.
# The activity column is an ENUM (category) type of ('login', 'logout',
# 'jobs', 'groups', 'homepage').
#
# Write a solution to reports for every date within at most 90 days from
# today, the number of users that logged in for the first time on that
# date. Assume today is 2019-06-30.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Traffic table:
# +---------+----------+---------------+
# | user_id | activity | activity_date |
# +---------+----------+---------------+
# | 1       | login    | 2019-05-01    |
# | 1       | homepage | 2019-05-01    |
# | 1       | logout   | 2019-05-01    |
# | 2       | login    | 2019-06-21    |
# | 2       | logout   | 2019-06-21    |
# | 3       | login    | 2019-01-01    |
# | 3       | jobs     | 2019-01-01    |
# | 3       | logout   | 2019-01-01    |
# | 4       | login    | 2019-06-21    |
# | 4       | groups   | 2019-06-21    |
# | 4       | logout   | 2019-06-21    |
# | 5       | login    | 2019-03-01    |
# | 5       | logout   | 2019-03-01    |
# | 5       | login    | 2019-06-21    |
# | 5       | logout   | 2019-06-21    |
# +---------+----------+---------------+
# Output:
# +------------+-------------+
# | login_date | user_count  |
# +------------+-------------+
# | 2019-05-01 | 1           |
# | 2019-06-21 | 2           |
# +------------+-------------+
# Explanation:
# Note that we only care about dates with non zero user count.
# The user with id 5 first logged in on 2019-03-01 so he's not counted on
# 2019-06-21.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. For each day in the 90-day window ending 2019-06-30, count
        users whose first login falls on that day.

        Algorithm:
        - First login per user: MIN(activity_date) WHERE activity = 'login'.
        - Filter first_login in [2019-04-01, 2019-06-30]; GROUP BY date COUNT.

        Complexity: O(T) over Traffic.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT login_date, COUNT(user_id) AS user_count
    FROM (
        SELECT user_id, MIN(activity_date) AS login_date
        FROM Traffic
        WHERE activity = 'login'
        GROUP BY user_id
    ) t
    WHERE login_date BETWEEN '2019-04-01' AND '2019-06-30'
    GROUP BY login_date;
    """
# @lc code=end
