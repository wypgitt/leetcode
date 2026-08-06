#
# @lc app=leetcode id=1917 lang=python3
#
# [1917] Leetcodify Friends Recommendations
#
# https://leetcode.com/problems/leetcodify-friends-recommendations/description/
#
# database
# Hard (28.88%)
# Likes:    69
# Dislikes: 61
# Total Accepted:    9.2K
# Total Submissions: 32K
# Testcase Example:  "{\"headers\":{\"Listens\":[\"user_id\",\"song_id\",\"day\"],\"Friendship\":[\"user1_id\",\"user2_id\"]},\"rows\":{\"Listens\":[[1,10,\"2021-03-15\"],[1,11,\"2021-03-15\"],[1,12,\"2021-03-15\"],[2,10,\"2021-03-15\"],[2,11,\"2021-03-15\"],[2,12,\"2021-03-15\"],[3,10,\"2021-03-15\"],[3,11,\"2021-03-15\"],[3,12,\"2021-03-15\"],[4,10,\"2021-03-15\"],[4,11,\"2021-03-15\"],[4,13,\"2021-03-15\"],[5,10,\"2021-03-16\"],[5,11,\"2021-03-16\"],[5,12,\"2021-03-16\"]],\"Friendship\":[[1,2]]}}"
#
#
# Table: Listens
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | user_id     | int     |
# | song_id     | int     |
# | day         | date    |
# +-------------+---------+
# This table may contain duplicates (In other words, there is no primary
# key for this table in SQL).
# Each row of this table indicates that the user user_id listened to the
# song song_id on the day day.
#
# Table: Friendship
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | user1_id      | int     |
# | user2_id      | int     |
# +---------------+---------+
# In SQL,(user1_id, user2_id) is the primary key for this table.
# Each row of this table indicates that the users user1_id and user2_id
# are friends.
# Note that user1_id < user2_id.
#
# Recommend friends to Leetcodify users. We recommend user x to user y if:
#
# Users x and y are not friends, and
#
# Users x and y listened to the same three or more different songs on the
# same day.
#
# Note that friend recommendations are unidirectional, meaning if user x
# and user y should be recommended to each other, the result table should
# have both user x recommended to user y and user y recommended to user x.
# Also, note that the result table should not contain duplicates (i.e.,
# user y should not be recommended to user x multiple times.).
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Listens table:
# +---------+---------+------------+
# | user_id | song_id | day        |
# +---------+---------+------------+
# | 1       | 10      | 2021-03-15 |
# | 1       | 11      | 2021-03-15 |
# | 1       | 12      | 2021-03-15 |
# | 2       | 10      | 2021-03-15 |
# | 2       | 11      | 2021-03-15 |
# | 2       | 12      | 2021-03-15 |
# | 3       | 10      | 2021-03-15 |
# | 3       | 11      | 2021-03-15 |
# | 3       | 12      | 2021-03-15 |
# | 4       | 10      | 2021-03-15 |
# | 4       | 11      | 2021-03-15 |
# | 4       | 13      | 2021-03-15 |
# | 5       | 10      | 2021-03-16 |
# | 5       | 11      | 2021-03-16 |
# | 5       | 12      | 2021-03-16 |
# +---------+---------+------------+
# Friendship table:
# +----------+----------+
# | user1_id | user2_id |
# +----------+----------+
# | 1        | 2        |
# +----------+----------+
# Output:
# +---------+----------------+
# | user_id | recommended_id |
# +---------+----------------+
# | 1       | 3              |
# | 2       | 3              |
# | 3       | 1              |
# | 3       | 2              |
# +---------+----------------+
# Explanation:
# Users 1 and 2 listened to songs 10, 11, and 12 on the same day, but they
# are already friends.
# Users 1 and 3 listened to songs 10, 11, and 12 on the same day. Since
# they are not friends, we recommend them to each other.
# Users 1 and 4 did not listen to the same three songs.
# Users 1 and 5 listened to songs 10, 11, and 12, but on different days.
#
# Similarly, we can see that users 2 and 3 listened to songs 10, 11, and
# 12 on the same day and are not friends, so we recommend them to each
# other.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Recommend user pairs who listened to ≥3 same songs on the
        same day and are not already friends. Output (user_id, recommended_id)
        for both directions, distinct, ordered.

        Algorithm:
        - Self-join Listens on day+song with user1<user2; count distinct songs ≥3;
          anti-join Friendship (both orientations); expand to both directions.

        Complexity: O(L^2) join worst-case with aggregation.
        """
        return self.sql

    sql = """
    WITH pairs AS (
        SELECT l1.user_id AS u1, l2.user_id AS u2, l1.day
        FROM Listens l1
        JOIN Listens l2
          ON l1.day = l2.day AND l1.song_id = l2.song_id AND l1.user_id < l2.user_id
        GROUP BY l1.user_id, l2.user_id, l1.day
        HAVING COUNT(DISTINCT l1.song_id) >= 3
    ),
    friends AS (
        SELECT user1_id AS u1, user2_id AS u2 FROM Friendship
        UNION
        SELECT user2_id, user1_id FROM Friendship
    ),
    rec AS (
        SELECT DISTINCT p.u1 AS user_id, p.u2 AS recommended_id
        FROM pairs p
        LEFT JOIN friends f ON p.u1 = f.u1 AND p.u2 = f.u2
        WHERE f.u1 IS NULL
        UNION
        SELECT DISTINCT p.u2, p.u1
        FROM pairs p
        LEFT JOIN friends f ON p.u1 = f.u1 AND p.u2 = f.u2
        WHERE f.u1 IS NULL
    )
    SELECT user_id, recommended_id
    FROM rec
    ORDER BY user_id, recommended_id;
    """
# @lc code=end
