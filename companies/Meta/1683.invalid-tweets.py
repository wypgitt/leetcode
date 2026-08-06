#
# @lc app=leetcode id=1683 lang=python3
#
# [1683] Invalid Tweets
#
# https://leetcode.com/problems/invalid-tweets/description/
#
# algorithms
# Easy (85.2%)
# Likes:    1541
# Dislikes: 381
# Total Accepted:    1.5M
# Total Submissions: 1.8M
# Testcase Example:  "{\"headers\":{\"Tweets\":[\"tweet_id\",\"content\"]},\"rows\":{\"Tweets\":[[1,\"Let us Code\"],[2,\"More than fifteen chars are here!\"]]}}"
#
# Table: Tweets
#
# +----------------+---------+
# | Column Name | Type |
# +----------------+---------+
# | tweet_id | int |
# | content | varchar |
# +----------------+---------+
# tweet_id is the primary key (column with unique values) for this table.
# content consists of alphanumeric characters, '!', or ' ' and no other special
# characters.
# This table contains all the tweets in a social media app.
#
# Write a solution to find the IDs of the invalid tweets. The tweet is invalid
# if the number of characters used in the content of the tweet is strictly
# greater than 15.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Tweets table:
# +----------+-----------------------------------+
# | tweet_id | content |
# +----------+-----------------------------------+
# | 1 | Let us Code |
# | 2 | More than fifteen chars are here! |
# +----------+-----------------------------------+
# Output:
# +----------+
# | tweet_id |
# +----------+
# | 2 |
# +----------+
# Explanation:
# Tweet 1 has length = 11. It is a valid tweet.
# Tweet 2 has length = 33. It is an invalid tweet.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Invalid tweets: content length strictly greater than 15.

        Algorithm:
        - SELECT tweet_id FROM Tweets WHERE CHAR_LENGTH(content) > 15;

        Complexity: O(T).
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT tweet_id
    FROM Tweets
    WHERE CHAR_LENGTH(content) > 15;
    """
# @lc code=end
