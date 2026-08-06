#
# @lc app=leetcode id=3058 lang=python3
#
# [3058] Friends With No Mutual Friends
#
# https://leetcode.com/problems/friends-with-no-mutual-friends/description/
#
# database
# Medium (48.84%)
# Likes:    20
# Dislikes: 3
# Total Accepted:    3.3K
# Total Submissions: 6.7K
# Testcase Example:  "{\"headers\":{\"Friends\":[\"user_id1\",\"user_id2\"]},\"rows\":{\"Friends\":[[1,2],[2,3],[2,4],[1,5],[6,7],[3,4],[2,5],[8,9]]}}"
#
#
# Table: Friends
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | user_id1    | int  |
# | user_id2    | int  |
# +-------------+------+
# (user_id1, user_id2) is the primary key (combination of columns with
# unique values) for this table.
# Each row contains user id1, user id2, both of whom are friends with each
# other.
#
# Write a solution to find all pairs of users who are friends with each
# other and have no mutual friends.
#
# Return the result table ordered by user_id1, user_id2 in ascending
# order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Friends table:
# +----------+----------+
# | user_id1 | user_id2 |
# +----------+----------+
# | 1        | 2        |
# | 2        | 3        |
# | 2        | 4        |
# | 1        | 5        |
# | 6        | 7        |
# | 3        | 4        |
# | 2        | 5        |
# | 8        | 9        |
# +----------+----------+
# Output:
# +----------+----------+
# | user_id1 | user_id2 |
# +----------+----------+
# | 6        | 7        |
# | 8        | 9        |
# +----------+----------+
# Explanation:
# - Users 1 and 2 are friends with each other, but they share a mutual
# friend with user ID 5, so this pair is not included.
# - Users 2 and 3 are friends, they both share a mutual friend with user
# ID 4, resulting in exclusion, similarly for users 2 and 4 who share a
# mutual friend with user ID 3, hence not included.
# - Users 1 and 5 are friends with each other, but they share a mutual
# friend with user ID 2, so this pair is not included.
# - Users 6 and 7, as well as users 8 and 9, are friends with each other,
# and they don't have any mutual friends, hence included.
# - Users 3 and 4 are friends with each other, but their mutual connection
# with user ID 2 means they are not included, similarly for users 2 and 5
# are friends but are excluded due to their mutual connection with user ID
# 1.
# Output table is ordered by user_id1 in ascending order.
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Friends(user_id1, user_id2) undirected edges. Pairs that are
        friends and share no mutual friend. Order by user_id1, user_id2 ASC.

        Algorithm:
        - Expand to undirected adjacency; for each edge, NOT EXISTS a common neighbor.

        Complexity: O(E * deg^2) via joins / anti-join.
        """
        self.sql = """
WITH F AS (
    SELECT user_id1 AS u, user_id2 AS v FROM Friends
    UNION ALL
    SELECT user_id2 AS u, user_id1 AS v FROM Friends
)
SELECT f.user_id1, f.user_id2
FROM Friends AS f
WHERE NOT EXISTS (
    SELECT 1
    FROM
        F AS a
        JOIN F AS b ON a.v = b.v
    WHERE
        a.u = f.user_id1
        AND b.u = f.user_id2
        AND a.v <> f.user_id1
        AND a.v <> f.user_id2
)
ORDER BY 1, 2;
"""
        return self.sql
# @lc code=end

