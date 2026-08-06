#
# @lc app=leetcode id=1951 lang=python3
#
# [1951] All the Pairs With the Maximum Number of Common Followers
#
# https://leetcode.com/problems/all-the-pairs-with-the-maximum-number-of-common-followers/description/
#
# database
# Medium (69.71%)
# Likes:    101
# Dislikes: 7
# Total Accepted:    14.6K
# Total Submissions: 21K
# Testcase Example:  "{\"headers\":{\"Relations\":[\"user_id\",\"follower_id\"]},\"rows\":{\"Relations\":[[1,3],[2,3],[7,3],[1,4],[2,4],[7,4],[1,5],[2,6],[7,5]]}}"
#
#
# Table: Relations
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | user_id     | int  |
# | follower_id | int  |
# +-------------+------+
# (user_id, follower_id) is the primary key (combination of columns with
# unique values) for this table.
# Each row of this table indicates that the user with ID follower_id is
# following the user with ID user_id.
#
# Write a solution to find all the pairs of users with the maximum number
# of common followers. In other words, if the maximum number of common
# followers between any two users is maxCommon, then you have to return
# all pairs of users that have maxCommon common followers.
#
# The result table should contain the pairs user1_id and user2_id where
# user1_id < user2_id.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Relations table:
# +---------+-------------+
# | user_id | follower_id |
# +---------+-------------+
# | 1       | 3           |
# | 2       | 3           |
# | 7       | 3           |
# | 1       | 4           |
# | 2       | 4           |
# | 7       | 4           |
# | 1       | 5           |
# | 2       | 6           |
# | 7       | 5           |
# +---------+-------------+
# Output:
# +----------+----------+
# | user1_id | user2_id |
# +----------+----------+
# | 1        | 7        |
# +----------+----------+
# Explanation:
# Users 1 and 2 have two common followers (3 and 4).
# Users 1 and 7 have three common followers (3, 4, and 5).
# Users 2 and 7 have two common followers (3 and 4).
# Since the maximum number of common followers between any two users is 3,
# we return all pairs of users with three common followers, which is only
# the pair (1, 7). We return the pair as (1, 7), not as (7, 1).
# Note that we do not have any information about the users that follow
# users 3, 4, and 5, so we consider them to have 0 followers.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Among user pairs, find those with the maximum number of
        shared followers. Return (user1_id, user2_id) with user1_id < user2_id.

        Algorithm:
        - Self-join Relations on follower_id with user_id < user_id.
        - GROUP BY pair; keep rows whose count equals the global MAX count.

        Complexity: O(R^2) worst-case join; typical O(R * F) with hashing.
        """
        return self.sql

    sql = """
    WITH pairs AS (
        SELECT a.user_id AS user1_id, b.user_id AS user2_id, COUNT(*) AS cnt
        FROM Relations a
        JOIN Relations b
          ON a.follower_id = b.follower_id AND a.user_id < b.user_id
        GROUP BY a.user_id, b.user_id
    )
    SELECT user1_id, user2_id
    FROM pairs
    WHERE cnt = (SELECT MAX(cnt) FROM pairs);
    """

    def solve_rank(self) -> str:
        """
        Interview explanation:
        Alternate SQL: RANK() over common-follower counts; keep rank = 1.

        Algorithm:
        - Same pairs CTE; filter RANK() OVER (ORDER BY cnt DESC) = 1.

        Complexity: same join; ranking O(P log P) on pair count.
        """
        return self.sql_rank

    sql_rank = """
    WITH pairs AS (
        SELECT a.user_id AS user1_id, b.user_id AS user2_id, COUNT(*) AS cnt
        FROM Relations a
        JOIN Relations b
          ON a.follower_id = b.follower_id AND a.user_id < b.user_id
        GROUP BY a.user_id, b.user_id
    )
    SELECT user1_id, user2_id
    FROM (
        SELECT user1_id, user2_id, RANK() OVER (ORDER BY cnt DESC) AS rk
        FROM pairs
    ) t
    WHERE rk = 1;
    """
# @lc code=end

