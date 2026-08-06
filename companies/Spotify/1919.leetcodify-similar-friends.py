#
# @lc app=leetcode id=1919 lang=python3
#
# [1919] Leetcodify Similar Friends
#
# https://leetcode.com/problems/leetcodify-similar-friends/description/
#
# database
# Hard (43.40%)
# Likes:    61
# Dislikes: 6
# Total Accepted:    8K
# Total Submissions: 18.5K
# Testcase Example:  "{\"headers\":{\"Listens\":[\"user_id\",\"song_id\",\"day\"],\"Friendship\":[\"user1_id\",\"user2_id\"]},\"rows\":{\"Listens\":[[1,10,\"2021-03-15\"],[1,11,\"2021-03-15\"],[1,12,\"2021-03-15\"],[2,10,\"2021-03-15\"],[2,11,\"2021-03-15\"],[2,12,\"2021-03-15\"],[3,10,\"2021-03-15\"],[3,11,\"2021-03-15\"],[3,12,\"2021-03-15\"],[4,10,\"2021-03-15\"],[4,11,\"2021-03-15\"],[4,13,\"2021-03-15\"],[5,10,\"2021-03-16\"],[5,11,\"2021-03-16\"],[5,12,\"2021-03-16\"]],\"Friendship\":[[1,2],[2,4],[2,5]]}}"
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
# This table may contain duplicate rows.
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
# (user1_id, user2_id) is the primary key (combination of columns with
# unique values) for this table.
# Each row of this table indicates that the users user1_id and user2_id
# are friends.
# Note that user1_id < user2_id.
#
# Write a solution to report the similar friends of Leetcodify users. A
# user x and user y are similar friends if:
#
# Users x and y are friends, and
#
# Users x and y listened to the same three or more different songs on the
# same day.
#
# Return the result table in any order. Note that you must return the
# similar pairs of friends the same way they were represented in the input
# (i.e., always user1_id < user2_id).
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
# | 2        | 4        |
# | 2        | 5        |
# +----------+----------+
# Output:
# +----------+----------+
# | user1_id | user2_id |
# +----------+----------+
# | 1        | 2        |
# +----------+----------+
# Explanation:
# Users 1 and 2 are friends, and they listened to songs 10, 11, and 12 on
# the same day. They are similar friends.
# Users 1 and 3 listened to songs 10, 11, and 12 on the same day, but they
# are not friends.
# Users 2 and 4 are friends, but they did not listen to the same three
# different songs.
# Users 2 and 5 are friends and listened to songs 10, 11, and 12, but they
# did not listen to them on the same day.
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Among existing friendships, keep pairs that listened to ≥3
        of the same songs on the same day (similar friends).

        Algorithm:
        - Normalize Friendship so user1_id < user2_id; join Listens self-pair
          on day+song; HAVING COUNT DISTINCT songs ≥ 3; DISTINCT friend pairs.

        Complexity: O(L^2 + F) with aggregation.
        """
        return self.sql

    sql = """
    WITH f AS (
        SELECT LEAST(user1_id, user2_id) AS user1_id,
               GREATEST(user1_id, user2_id) AS user2_id
        FROM Friendship
    )
    SELECT DISTINCT f.user1_id, f.user2_id
    FROM f
    JOIN Listens l1 ON l1.user_id = f.user1_id
    JOIN Listens l2 ON l2.user_id = f.user2_id
                   AND l1.day = l2.day AND l1.song_id = l2.song_id
    GROUP BY f.user1_id, f.user2_id, l1.day
    HAVING COUNT(DISTINCT l1.song_id) >= 3
    ORDER BY f.user1_id, f.user2_id;
    """
# @lc code=end
