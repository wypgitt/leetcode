#
# @lc app=leetcode id=1949 lang=python3
#
# [1949] Strong Friendship
#
# https://leetcode.com/problems/strong-friendship/description/
#
# database
# Medium (54.70%)
# Likes:    167
# Dislikes: 86
# Total Accepted:    17.2K
# Total Submissions: 31.5K
# Testcase Example:  "{\"headers\":{\"Friendship\":[\"user1_id\",\"user2_id\"]},\"rows\":{\"Friendship\":[[1,2],[1,3],[2,3],[1,4],[2,4],[1,5],[2,5],[1,7],[3,7],[1,6],[3,6],[2,6]]}}"
#
#
# Table: Friendship
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | user1_id    | int  |
# | user2_id    | int  |
# +-------------+------+
# (user1_id, user2_id) is the primary key (combination of columns with
# unique values) for this table.
# Each row of this table indicates that the users user1_id and user2_id
# are friends.
# Note that user1_id < user2_id.
#
# A friendship between a pair of friends x and y is strong if x and y have
# at least three common friends.
#
# Write a solution to find all the strong friendships.
#
# Note that the result table should not contain duplicates with user1_id <
# user2_id.
#
# Return the result table in any order.
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
# | 2        | 3        |
# | 1        | 4        |
# | 2        | 4        |
# | 1        | 5        |
# | 2        | 5        |
# | 1        | 7        |
# | 3        | 7        |
# | 1        | 6        |
# | 3        | 6        |
# | 2        | 6        |
# +----------+----------+
# Output:
# +----------+----------+---------------+
# | user1_id | user2_id | common_friend |
# +----------+----------+---------------+
# | 1        | 2        | 4             |
# | 1        | 3        | 3             |
# +----------+----------+---------------+
# Explanation:
# Users 1 and 2 have 4 common friends (3, 4, 5, and 6).
# Users 1 and 3 have 3 common friends (2, 6, and 7).
# We did not include the friendship of users 2 and 3 because they only
# have two common friends (1 and 6).
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Strong friendship: two friends sharing ≥3 common friends.
        Friendship is undirected; store with user1_id < user2_id in output.

        Algorithm:
        - Normalize edges both ways; for each friend pair (a,b), count users f
          friends with both; HAVING COUNT >= 3.

        Complexity: O(F * D^2) style joins.
        """
        return self.sql

    sql = """
    WITH f AS (
        SELECT user1_id AS u, user2_id AS v FROM Friendship
        UNION ALL
        SELECT user2_id, user1_id FROM Friendship
    ),
    pairs AS (
        SELECT LEAST(a.user1_id, a.user2_id) AS user1_id,
               GREATEST(a.user1_id, a.user2_id) AS user2_id
        FROM Friendship a
    )
    SELECT p.user1_id, p.user2_id, COUNT(*) AS common_friend
    FROM pairs p
    JOIN f f1 ON f1.u = p.user1_id
    JOIN f f2 ON f2.u = p.user2_id AND f2.v = f1.v
    GROUP BY p.user1_id, p.user2_id
    HAVING COUNT(*) >= 3
    ORDER BY p.user1_id, p.user2_id;
    """
# @lc code=end
