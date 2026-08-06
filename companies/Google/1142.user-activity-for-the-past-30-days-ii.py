#
# @lc app=leetcode id=1142 lang=python3
#
# [1142] User Activity for the Past 30 Days II
#
# https://leetcode.com/problems/user-activity-for-the-past-30-days-ii/description/
#
# database
# Easy (35.62%)
# Likes:    108
# Dislikes: 380
# Total Accepted:    50K
# Total Submissions: 140.3K
# Testcase Example:  "{\"headers\":{\"Activity\":[\"user_id\",\"session_id\",\"activity_date\",\"activity_type\"]},\"rows\":{\"Activity\":[[1,1,\"2019-07-20\",\"open_session\"],[1,1,\"2019-07-20\",\"scroll_down\"],[1,1,\"2019-07-20\",\"end_session\"],[2,4,\"2019-07-20\",\"open_session\"],[2,4,\"2019-07-21\",\"send_message\"],[2,4,\"2019-07-21\",\"end_session\"],[3,2,\"2019-07-21\",\"open_session\"],[3,2,\"2019-07-21\",\"send_message\"],[3,2,\"2019-07-21\",\"end_session\"],[3,5,\"2019-07-21\",\"open_session\"],[3,5,\"2019-07-21\",\"scroll_down\"],[3,5,\"2019-07-21\",\"end_session\"],[4,3,\"2019-06-25\",\"open_session\"],[4,3,\"2019-06-25\",\"end_session\"]]}}"
#
#
# Table: Activity
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | user_id       | int     |
# | session_id    | int     |
# | activity_date | date    |
# | activity_type | enum    |
# +---------------+---------+
# This table may have duplicate rows.
# The activity_type column is an ENUM (category) of type ('open_session',
# 'end_session', 'scroll_down', 'send_message').
# The table shows the user activities for a social media website.
# Note that each session belongs to exactly one user.
#
# Write a solution to find the average number of sessions per user for a
# period of 30 days ending 2019-07-27 inclusively, rounded to 2 decimal
# places. The sessions we want to count for a user are those with at least
# one activity in that time period.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Activity table:
# +---------+------------+---------------+---------------+
# | user_id | session_id | activity_date | activity_type |
# +---------+------------+---------------+---------------+
# | 1       | 1          | 2019-07-20    | open_session  |
# | 1       | 1          | 2019-07-20    | scroll_down   |
# | 1       | 1          | 2019-07-20    | end_session   |
# | 2       | 4          | 2019-07-20    | open_session  |
# | 2       | 4          | 2019-07-21    | send_message  |
# | 2       | 4          | 2019-07-21    | end_session   |
# | 3       | 2          | 2019-07-21    | open_session  |
# | 3       | 2          | 2019-07-21    | send_message  |
# | 3       | 2          | 2019-07-21    | end_session   |
# | 3       | 5          | 2019-07-21    | open_session  |
# | 3       | 5          | 2019-07-21    | scroll_down   |
# | 3       | 5          | 2019-07-21    | end_session   |
# | 4       | 3          | 2019-06-25    | open_session  |
# | 4       | 3          | 2019-06-25    | end_session   |
# +---------+------------+---------------+---------------+
# Output:
# +---------------------------+
# | average_sessions_per_user |
# +---------------------------+
# | 1.33                      |
# +---------------------------+
# Explanation: User 1 and 2 each had 1 session in the past 30 days while
# user 3 had 2 sessions so the average is (1 + 1 + 2) / 3 = 1.33.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Average sessions per user over the 30 days ending
        2019-07-27 (inclusive). Round to 2 decimals; 0.00 if no users.

        Algorithm:
        - Filter date window; COUNT(DISTINCT session_id)/COUNT(DISTINCT user_id).
        - IFNULL/COALESCE for empty result.

        Complexity: O(N).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT
        IFNULL(
            ROUND(
                COUNT(DISTINCT session_id) / COUNT(DISTINCT user_id),
                2
            ),
            0.00
        ) AS average_sessions_per_user
    FROM Activity
    WHERE activity_date BETWEEN '2019-06-28' AND '2019-07-27';
    """
# @lc code=end
