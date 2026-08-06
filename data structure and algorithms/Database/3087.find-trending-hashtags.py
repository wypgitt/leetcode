#
# @lc app=leetcode id=3087 lang=python3
#
# [3087] Find Trending Hashtags
#
# https://leetcode.com/problems/find-trending-hashtags/description/
#
# database
# Medium (61.51%)
# Likes:    8
# Dislikes: 6
# Total Accepted:    3K
# Total Submissions: 4.8K
# Testcase Example:  "{\"headers\":{\"Tweets\":[\"user_id\",\"tweet_id\",\"tweet\",\"tweet_date\"]},\"rows\":{\"Tweets\":[[135,13,\"Enjoying a great start to the day. #HappyDay\",\"2024-02-01\"],[136,14,\"Another #HappyDay with good \",\"2024-02-03\"],[137,15,\"Productivity peaks! #WorkLife\",\"2024-02-04\"],[138,16,\"Exploring new tech frontiers. #TechLife\",\"2024-02-04\"],[139,17,\"Gratitude for today's moments. #HappyDay\",\"2024-02-05\"],[140,18,\"Innovation drives us. #TechLife\",\"2024-02-07\"],[141,19,\"Connecting with nature's serenity. #Nature\",\"2024-02-09\"]]}}"
#
#
# Table: Tweets
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | user_id     | int     |
# | tweet_id    | int     |
# | tweet_date  | date    |
# | tweet       | varchar |
# +-------------+---------+
# tweet_id is the primary key (column with unique values) for this table.
# Each row of this table contains user_id, tweet_id, tweet_date and tweet.
#
# Write a solution to find the top 3 trending hashtags in February 2024.
# Each tweet only contains one hashtag.
#
# Return the result table orderd by count of hashtag, hashtag in
# descending order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
#
# Tweets table:
#
# +---------+----------+----------------------------------------------+------------+
# | user_id | tweet_id | tweet                                        |
# tweet_date |
# +---------+----------+----------------------------------------------+------------+
# | 135     | 13       | Enjoying a great start to the day! #HappyDay |
# 2024-02-01 |
# | 136     | 14       | Another #HappyDay with good vibes!           |
# 2024-02-03 |
# | 137     | 15       | Productivity peaks! #WorkLife                |
# 2024-02-04 |
# | 138     | 16       | Exploring new tech frontiers. #TechLife      |
# 2024-02-04 |
# | 139     | 17       | Gratitude for today's moments. #HappyDay     |
# 2024-02-05 |
# | 140     | 18       | Innovation drives us. #TechLife              |
# 2024-02-07 |
# | 141     | 19       | Connecting with nature's serenity. #Nature   |
# 2024-02-09 |
# +---------+----------+----------------------------------------------+------------+
#
# Output:
#
# +-----------+--------------+
# | hashtag   | hashtag_count|
# +-----------+--------------+
# | #HappyDay | 3            |
# | #TechLife | 2            |
# | #WorkLife | 1            |
# +-----------+--------------+
#
# Explanation:
#
# #HappyDay: Appeared in tweet IDs 13, 14, and 17, with a total count of 3
# mentions.
#
# #TechLife: Appeared in tweet IDs 16 and 18, with a total count of 2
# mentions.
#
# #WorkLife: Appeared in tweet ID 15, with a total count of 1 mention.
#
# Note: Output table is sorted in descending order by hashtag_count and
# hashtag respectively.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Tweets(user_id, tweet_id, tweet, tweet_date). Each February
        2024 tweet has one hashtag; return top 3 by count, then hashtag DESC.

        Algorithm:
        - Filter Feb 2024; extract hashtag after '#'; group/count; ORDER + LIMIT 3.

        Complexity: O(N).
        """
        self.sql = """
SELECT
    CONCAT('#', SUBSTRING_INDEX(SUBSTRING_INDEX(tweet, '#', -1), ' ', 1)) AS hashtag,
    COUNT(*) AS hashtag_count
FROM Tweets
WHERE tweet_date BETWEEN '2024-02-01' AND '2024-02-29'
GROUP BY hashtag
ORDER BY hashtag_count DESC, hashtag DESC
LIMIT 3;
"""
        return self.sql
# @lc code=end
