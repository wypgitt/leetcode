#
# @lc app=leetcode id=2173 lang=python3
#
# [2173] Longest Winning Streak
#
# https://leetcode.com/problems/longest-winning-streak/description/
#
# database
# Hard (54.53%)
# Likes:    105
# Dislikes: 4
# Total Accepted:    8.1K
# Total Submissions: 14.8K
# Testcase Example:  "{\"headers\":{\"Matches\":[\"player_id\",\"match_day\",\"result\"]},\"rows\":{\"Matches\":[[1,\"2022-01-17\",\"Win\"],[1,\"2022-01-18\",\"Win\"],[1,\"2022-01-25\",\"Win\"],[1,\"2022-01-31\",\"Draw\"],[1,\"2022-02-08\",\"Win\"],[2,\"2022-02-06\",\"Lose\"],[2,\"2022-02-08\",\"Lose\"],[3,\"2022-03-30\",\"Win\"]]}}"
#
#
# Table: Matches
#
# +-------------+------+
# | Column Name | Type |
# +-------------+------+
# | player_id   | int  |
# | match_day   | date |
# | result      | enum |
# +-------------+------+
# (player_id, match_day) is the primary key (combination of columns with
# unique values) for this table.
# Each row of this table contains the ID of a player, the day of the match
# they played, and the result of that match.
# The result column is an ENUM (category) type of ('Win', 'Draw', 'Lose').
#
# The winning streak of a player is the number of consecutive wins
# uninterrupted by draws or losses.
#
# Write a solution to count the longest winning streak for each player.
#
# Return the result table in any order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Matches table:
# +-----------+------------+--------+
# | player_id | match_day  | result |
# +-----------+------------+--------+
# | 1         | 2022-01-17 | Win    |
# | 1         | 2022-01-18 | Win    |
# | 1         | 2022-01-25 | Win    |
# | 1         | 2022-01-31 | Draw   |
# | 1         | 2022-02-08 | Win    |
# | 2         | 2022-02-06 | Lose   |
# | 2         | 2022-02-08 | Lose   |
# | 3         | 2022-03-30 | Win    |
# +-----------+------------+--------+
# Output:
# +-----------+----------------+
# | player_id | longest_streak |
# +-----------+----------------+
# | 1         | 3              |
# | 2         | 0              |
# | 3         | 1              |
# +-----------+----------------+
# Explanation:
# Player 1:
# From 2022-01-17 to 2022-01-25, player 1 won 3 consecutive matches.
# On 2022-01-31, player 1 had a draw.
# On 2022-02-08, player 1 won a match.
# The longest winning streak was 3 matches.
#
# Player 2:
# From 2022-02-06 to 2022-02-08, player 2 lost 2 consecutive matches.
# The longest winning streak was 0 matches.
#
# Player 3:
# On 2022-03-30, player 3 won a match.
# The longest winning streak was 1 match.
#
# Follow up: If we are interested in calculating the longest streak
# without losing (i.e., win or draw), how will your solution change?
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL. Matches(player_id, match_day, result in Win/Draw/Lose).
        For each player, longest consecutive Win streak (by match_day). Include
        players with streak 0.

        Algorithm:
        - Island trick: ROW_NUMBER by player - ROW_NUMBER by player+result groups
          consecutive same results; SUM(result='Win') per group; MAX per player.

        Complexity: O(N log N) window sorts.
        """
        return self.sql

    sql = """
    WITH
    S AS (
        SELECT
            player_id,
            result,
            ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY match_day)
              - ROW_NUMBER() OVER (PARTITION BY player_id, result ORDER BY match_day) AS grp
        FROM Matches
    ),
    T AS (
        SELECT player_id, SUM(result = 'Win') AS streak
        FROM S
        GROUP BY player_id, grp
    )
    SELECT player_id, MAX(streak) AS longest_streak
    FROM T
    GROUP BY player_id;
    """
# @lc code=end
