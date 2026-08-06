#
# @lc app=leetcode id=1264 lang=python3
#
# [1264] Page Recommendations
#
# https://leetcode.com/problems/page-recommendations/description/
#
# database
# Medium (65.47%)
# Likes:    266
# Dislikes: 27
# Total Accepted:    55.4K
# Total Submissions: 84.5K
# Testcase Example:  "{\"headers\":{\"Friendship\":[\"user1_id\",\"user2_id\"],\"Likes\":[\"user_id\",\"page_id\"]},\"rows\":{\"Friendship\":[[1,2],[1,3],[1,4],[2,3],[2,4],[2,5],[6,1]],\"Likes\":[[1,88],[2,23],[3,24],[4,56],[5,11],[6,33],[2,77],[3,77],[6,88]]}}"
#
#
# Table: Friendship
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | user1_id      | int     |
# | user2_id      | int     |
# +---------------+---------+
# (user1_id, user2_id) is the primary key (combination of columns with
# unique values) for this table.
# Each row of this table indicates that there is a friendship relation
# between user1_id and user2_id.
#
# Table: Likes
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | user_id     | int     |
# | page_id     | int     |
# +-------------+---------+
# (user_id, page_id) is the primary key (combination of columns with
# unique values) for this table.
# Each row of this table indicates that user_id likes page_id.
#
# Write a solution to recommend pages to the user with user_id = 1 using
# the pages that your friends liked. It should not recommend pages you
# already liked.
#
# Return result table in any order without duplicates.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Friendship table:
# +----------+----------+
# | user1_id | user2_id |
# +----------+----------+
# | 1        | 2        |
# | 1        | 3        |
# | 1        | 4        |
# | 2        | 3        |
# | 2        | 4        |
# | 2        | 5        |
# | 6        | 1        |
# +----------+----------+
# Likes table:
# +---------+---------+
# | user_id | page_id |
# +---------+---------+
# | 1       | 88      |
# | 2       | 23      |
# | 3       | 24      |
# | 4       | 56      |
# | 5       | 11      |
# | 6       | 33      |
# | 2       | 77      |
# | 3       | 77      |
# | 6       | 88      |
# +---------+---------+
# Output:
# +------------------+
# | recommended_page |
# +------------------+
# | 23               |
# | 24               |
# | 56               |
# | 33               |
# | 77               |
# +------------------+
# Explanation:
# User one is friend with users 2, 3, 4 and 6.
# Suggested pages are 23 from user 2, 24 from user 3, 56 from user 3 and
# 33 from user 6.
# Page 77 is suggested from both user 2 and user 3.
# Page 88 is not suggested because user 1 already likes it.
#
# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium. Recommend pages liked by friends of user_id=1 that user 1 has
        not liked. Friendship is undirected (user1_id/user2_id).

        Algorithm:
        - Friends of 1: user2 where user1=1 UNION user1 where user2=1.
        - Pages friends like MINUS pages user 1 likes; DISTINCT page_id.

        Complexity: O(F + L) with indexes on friendship/likes.
        """
        return self.sql

    # LeetCode SQL — paste into SQL editor
    sql = """
    SELECT DISTINCT l.page_id AS recommended_page
    FROM Likes l
    WHERE l.user_id IN (
        SELECT user2_id FROM Friendship WHERE user1_id = 1
        UNION
        SELECT user1_id FROM Friendship WHERE user2_id = 1
    )
    AND l.page_id NOT IN (
        SELECT page_id FROM Likes WHERE user_id = 1
    );
    """
# @lc code=end
