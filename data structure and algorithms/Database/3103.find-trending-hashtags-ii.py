#
# @lc app=leetcode id=3103 lang=python3
#
# [3103] Find Trending Hashtags II 
#
# https://leetcode.com/problems/find-trending-hashtags-ii/description/
#
# database
# Hard (66.38%)
# Likes:    11
# Dislikes: 2
# Total Accepted:    1.7K
# Total Submissions: 2.6K
# Testcase Example:  "{\"headers\":{\"Tweets\":[\"user_id\",\"tweet_id\",\"tweet\",\"tweet_date\"]},\"rows\":{\"Tweets\":[[135,13,\"Enjoying a great start to the day. #HappyDay #MorningVibes\",\"2024-02-01\"],[136,14,\"Another #HappyDay with good vibes! #FeelGood\",\"2024-02-03\"],[137,15,\"Productivity peaks! #WorkLife #ProductiveDay\",\"2024-02-04\"],[138,16,\"Exploring new tech frontiers. #TechLife #Innovation\",\"2024-02-04\"],[139,17,\"Gratitude for today's moments. #HappyDay #Thankful\",\"2024-02-05\"],[140,18,\"Innovation drives us. #TechLife #FutureTech\",\"2024-02-07\"],[141,19,\"Connecting with nature's serenity. #Nature #Peaceful\",\"2024-02-09\"]]}}"
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
# It is guaranteed that all tweet_date are valid dates in February 2024.
#
# Write a solution to find the top 3 trending hashtags in February 2024.
# Every tweet may contain several hashtags.
#
# Return the result table ordered by count of hashtag, hashtag in
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
# +---------+----------+------------------------------------------------------------+------------+
# | user_id | tweet_id | tweet
# | tweet_date |
# +---------+----------+------------------------------------------------------------+------------+
# | 135     | 13       | Enjoying a great start to the day. #HappyDay
# #MorningVibes | 2024-02-01 |
# | 136     | 14       | Another #HappyDay with good vibes! #FeelGood
# | 2024-02-03 |
# | 137     | 15       | Productivity peaks! #WorkLife #ProductiveDay
# | 2024-02-04 |
# | 138     | 16       | Exploring new tech frontiers. #TechLife
# #Innovation        | 2024-02-04 |
# | 139     | 17       | Gratitude for today's moments. #HappyDay
# #Thankful         | 2024-02-05 |
# | 140     | 18       | Innovation drives us. #TechLife #FutureTech
# | 2024-02-07 |
# | 141     | 19       | Connecting with nature's serenity. #Nature
# #Peaceful       | 2024-02-09 |
# +---------+----------+------------------------------------------------------------+------------+
#
# Output:
#
# +-----------+-------+
# | hashtag   | count |
# +-----------+-------+
# | #HappyDay | 3     |
# | #TechLife | 2     |
# | #WorkLife | 1     |
# +-----------+-------+
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
# Note: Output table is sorted in descending order by count and hashtag
# respectively.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Tweets in Feb 2024; each tweet may hold several hashtags.
        Return top 3 hashtags by frequency, then hashtag DESC.

        Algorithm:
        - Recursive CTE: REGEXP_SUBSTR first #token, strip it, repeat while '#'.
        - GROUP BY hashtag; ORDER BY count DESC, hashtag DESC; LIMIT 3.

        Complexity: O(N * L) string work.
        """
        self.sql = """
WITH RECURSIVE FebruaryTweets AS (
    SELECT tweet
    FROM Tweets
    WHERE YEAR(tweet_date) = 2024 AND MONTH(tweet_date) = 2
),
HashtagToTweet AS (
    SELECT
        REGEXP_SUBSTR(tweet, '#[^\\s]+') AS hashtag,
        REGEXP_REPLACE(tweet, '#[^\\s]+', '', 1, 1) AS tweet
    FROM FebruaryTweets
    UNION ALL
    SELECT
        REGEXP_SUBSTR(tweet, '#[^\\s]+') AS hashtag,
        REGEXP_REPLACE(tweet, '#[^\\s]+', '', 1, 1) AS tweet
    FROM HashtagToTweet
    WHERE POSITION('#' IN tweet) > 0
)
SELECT hashtag, COUNT(*) AS count
FROM HashtagToTweet
GROUP BY hashtag
ORDER BY count DESC, hashtag DESC
LIMIT 3;
"""
        return self.sql
# @lc code=end
