#
# @lc app=leetcode id=3089 lang=python3
#
# [3089] Find Bursty Behavior
#
# https://leetcode.com/problems/find-bursty-behavior/description/
#
# database
# Medium (37.99%)
# Likes:    11
# Dislikes: 21
# Total Accepted:    2.6K
# Total Submissions: 6.9K
# Testcase Example:  "{\"headers\": {\"Posts\": [\"post_id\", \"user_id\", \"post_date\"]}, \"rows\": {\"Posts\": [[1, 1, \"2024-02-27\"], [2, 5, \"2024-02-06\"], [3, 3, \"2024-02-25\"], [4, 3, \"2024-02-14\"], [5, 3, \"2024-02-06\"], [6, 2, \"2024-02-25\"]]}}"
#
#
# Table: Posts
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | post_id     | int     |
# | user_id     | int     |
# | post_date   | date    |
# +-------------+---------+
# post_id is the primary key (column with unique values) for this table.
# Each row of this table contains post_id, user_id, and post_date.
#
# Write a solution to find users who demonstrate bursty behavior in their
# posting patterns during February 2024. Bursty behavior is defined as any
# period of 7 consecutive days where a user's posting frequency is at
# least twice to their average weekly posting frequency for February 2024.
#
# Note: Only include the dates from February 1 to February 28 in your
# analysis, which means you should count February as having exactly 4
# weeks.
#
# Return the result table orderd by user_id in ascending order.
#
# The result format is in the following example.
#
# Example:
#
# Input:
#
# Posts table:
#
# +---------+---------+------------+
# | post_id | user_id | post_date  |
# +---------+---------+------------+
# | 1       | 1       | 2024-02-27 |
# | 2       | 5       | 2024-02-06 |
# | 3       | 3       | 2024-02-25 |
# | 4       | 3       | 2024-02-14 |
# | 5       | 3       | 2024-02-06 |
# | 6       | 2       | 2024-02-25 |
# +---------+---------+------------+
#
# Output:
#
# +---------+----------------+------------------+
# | user_id | max_7day_posts | avg_weekly_posts |
# +---------+----------------+------------------+
# | 1       | 1              | 0.2500           |
# | 2       | 1              | 0.2500           |
# | 5       | 1              | 0.2500           |
# +---------+----------------+------------------+
#
# Explanation:
#
# User 1: Made only 1 post in February, resulting in an average of 0.25
# posts per week and a max of 1 post in any 7-day period.
#
# User 2: Also made just 1 post, with the same average and max 7-day
# posting frequency as User 1.
#
# User 5: Like Users 1 and 2, User 5 made only 1 post throughout February,
# leading to the same average and max 7-day posting metrics.
#
# User 3: Although User 3 made more posts than the others (3 posts), they
# did not reach twice the average weekly posts in their consecutive 7-day
# window, so they are not listed in the output.
#
# Note: Output table is ordered by user_id in ascending order.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Posts in Feb 2024. Bursty if some 7-day window has post count
        >= 2 * (Feb posts / 4 weeks). Return user_id, max_7day_posts, avg_weekly_posts.

        Algorithm:
        - Self-join posts per user on [d, d+6]; take MAX window count.
        - Join avg weekly = COUNT/4; HAVING max >= 2 * avg; ORDER BY user_id.

        Complexity: O(N^2) worst-case joins, typically fine for LC sizes.
        """
        self.sql = """
WITH
    FebPosts AS (
        SELECT *
        FROM Posts
        WHERE post_date BETWEEN '2024-02-01' AND '2024-02-28'
    ),
    P AS (
        SELECT
            p1.user_id AS user_id,
            COUNT(1) AS cnt
        FROM FebPosts AS p1
        JOIN FebPosts AS p2
            ON p1.user_id = p2.user_id
            AND p2.post_date BETWEEN p1.post_date AND DATE_ADD(p1.post_date, INTERVAL 6 DAY)
        GROUP BY p1.user_id, p1.post_id
    ),
    T AS (
        SELECT
            user_id,
            COUNT(1) / 4 AS avg_weekly_posts
        FROM FebPosts
        GROUP BY 1
    )
SELECT
    user_id,
    MAX(cnt) AS max_7day_posts,
    avg_weekly_posts
FROM P
JOIN T USING (user_id)
GROUP BY 1
HAVING max_7day_posts >= avg_weekly_posts * 2
ORDER BY 1;
"""
        return self.sql
# @lc code=end
