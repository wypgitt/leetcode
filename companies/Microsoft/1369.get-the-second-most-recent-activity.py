#
# @lc app=leetcode id=1369 lang=python3
#
# [1369] Get the Second Most Recent Activity
#
# https://leetcode.com/problems/get-the-second-most-recent-activity/description/
#
# database
# Hard (67.32%)
# Likes:    169
# Dislikes: 13
# Total Accepted:    26.9K
# Total Submissions: 39.9K
# Testcase Example:  "{\"headers\":{\"UserActivity\":[\"username\",\"activity\",\"startDate\",\"endDate\"]},\"rows\":{\"UserActivity\":[[\"Alice\",\"Travel\",\"2020-02-12\",\"2020-02-20\"],[\"Alice\",\"Dancing\",\"2020-02-21\",\"2020-02-23\"],[\"Alice\",\"Travel\",\"2020-02-24\",\"2020-02-28\"],[\"Bob\",\"Travel\",\"2020-02-11\",\"2020-02-18\"]]}}"
#
#
# Table: UserActivity
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | username      | varchar |
# | activity      | varchar |
# | startDate     | Date    |
# | endDate       | Date    |
# +---------------+---------+
# This table may contain duplicates rows.
# This table contains information about the activity performed by each
# user in a period of time.
# A person with username performed an activity from startDate to endDate.
#
# Write a solution to show the second most recent activity of each user.
#
# If the user only has one activity, return that one. A user cannot
# perform more than one activity at the same time.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# UserActivity table:
# +------------+--------------+-------------+-------------+
# | username   | activity     | startDate   | endDate     |
# +------------+--------------+-------------+-------------+
# | Alice      | Travel       | 2020-02-12  | 2020-02-20  |
# | Alice      | Dancing      | 2020-02-21  | 2020-02-23  |
# | Alice      | Travel       | 2020-02-24  | 2020-02-28  |
# | Bob        | Travel       | 2020-02-11  | 2020-02-18  |
# +------------+--------------+-------------+-------------+
# Output:
# +------------+--------------+-------------+-------------+
# | username   | activity     | startDate   | endDate     |
# +------------+--------------+-------------+-------------+
# | Alice      | Dancing      | 2020-02-21  | 2020-02-23  |
# | Bob        | Travel       | 2020-02-11  | 2020-02-18  |
# +------------+--------------+-------------+-------------+
# Explanation:
# The most recent activity of Alice is Travel from 2020-02-24 to
# 2020-02-28, before that she was dancing from 2020-02-21 to 2020-02-23.
# Bob only has one record, we just take that one.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. For each user show the second most recent activity; if only
        one activity, show that one.

        Algorithm:
        - Rank activities per username by endDate DESC (ROW_NUMBER)
        - Keep rn=2, or rn=1 when user has only one row

        Complexity: O(A log A) with window sort.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT username, activity, startDate, endDate
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (PARTITION BY username ORDER BY endDate DESC) AS rn,
            COUNT(*) OVER (PARTITION BY username) AS cnt
        FROM UserActivity
    ) t
    WHERE rn = 2 OR cnt = 1;
    """
# @lc code=end
