#
# @lc app=leetcode id=3390 lang=python3
#
# [3390] Longest Team Pass Streak
#
# https://leetcode.com/problems/longest-team-pass-streak/description/
#
# database
# Hard (40.34%)
# Likes:    3
# Dislikes: 10
# Total Accepted:    1.1K
# Total Submissions: 2.8K
# Testcase Example:  "{\"headers\":{\"Teams\":[\"player_id\",\"team_name\"],\"Passes\":[\"pass_from\",\"time_stamp\",\"pass_to\"]},\"rows\":{\"Teams\":[[1,\"Arsenal\"],[2,\"Arsenal\"],[3,\"Arsenal\"],[4,\"Arsenal\"],[5,\"Chelsea\"],[6,\"Chelsea\"],[7,\"Chelsea\"],[8,\"Chelsea\"]],\"Passes\":[[1,\"00:05\",2],[2,\"00:07\",3],[3,\"00:08\",4],[4,\"00:10\",5],[6,\"00:15\",7],[7,\"00:17\",8],[8,\"00:20\",6],[6,\"00:22\",5],[1,\"00:25\",2],[2,\"00:27\",3]]}}"
#
#
# Table: Teams
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | player_id   | int     |
# | team_name   | varchar |
# +-------------+---------+
# player_id is the unique key for this table.
# Each row contains the unique identifier for player and the name of one
# of the teams participating in that match.
#
# Table: Passes
#
# +-------------+---------+
# | Column Name | Type    |
# +-------------+---------+
# | pass_from   | int     |
# | time_stamp  | varchar |
# | pass_to     | int     |
# +-------------+---------+
# (pass_from, time_stamp) is the unique key for this table.
# pass_from is a foreign key to player_id from Teams table.
# Each row represents a pass made during a match, time_stamp represents
# the time in minutes (00:00-90:00) when the pass was made,
# pass_to is the player_id of the player receiving the pass.
#
# Write a solution to find the longest successful pass streak for each
# team during the match. The rules are as follows:
#
# A successful pass streak is defined as consecutive passes where:
#
# Both the pass_from and pass_to players belong to the same team
#
# A streak breaks when either:
#
# The pass is intercepted (received by a player from the opposing team)
#
# Return the result table ordered by team_name in ascending order.
#
# The result format is in the following example.
#
# Example:
#
# Input:
#
# Teams table:
#
# +-----------+-----------+
# | player_id | team_name |
# +-----------+-----------+
# | 1         | Arsenal   |
# | 2         | Arsenal   |
# | 3         | Arsenal   |
# | 4         | Arsenal   |
# | 5         | Chelsea   |
# | 6         | Chelsea   |
# | 7         | Chelsea   |
# | 8         | Chelsea   |
# +-----------+-----------+
#
# Passes table:
#
# +-----------+------------+---------+
# | pass_from | time_stamp | pass_to |
# +-----------+------------+---------+
# | 1         | 00:05      | 2       |
# | 2         | 00:07      | 3       |
# | 3         | 00:08      | 4       |
# | 4         | 00:10      | 5       |
# | 6         | 00:15      | 7       |
# | 7         | 00:17      | 8       |
# | 8         | 00:20      | 6       |
# | 6         | 00:22      | 5       |
# | 1         | 00:25      | 2       |
# | 2         | 00:27      | 3       |
# +-----------+------------+---------+
#
# Output:
#
# +-----------+----------------+
# | team_name | longest_streak |
# +-----------+----------------+
# | Arsenal   | 3              |
# | Chelsea   | 4              |
# +-----------+----------------+
#
# Explanation:
#
# Arsenal's streaks:
#
# First streak: 3 passes (1→2→3→4) ended when player 4 passed to Chelsea's
# player 5
#
# Second streak: 2 passes (1→2→3)
#
# Longest streak = 3
#
# Chelsea's streaks:
#
# First streak: 3 passes (6→7→8→6→5)
#
# Longest streak = 4
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: longest run of consecutive same-team passes per team
        (streak breaks on interception). Order by team_name ASC.

        Algorithm:
        - Flag same-team passes; cumulative sum of interceptions per team partitions
          streaks; MAX(COUNT) of successful rows per (team, group).

        Complexity: O(P log P).
        """
        self.sql = """
WITH PassesWithTeams AS (
    SELECT
        t1.team_name AS team_name,
        p.time_stamp,
        CASE WHEN t1.team_name = t2.team_name THEN 1 ELSE 0 END AS same_team
    FROM Passes p
    JOIN Teams t1 ON p.pass_from = t1.player_id
    JOIN Teams t2 ON p.pass_to = t2.player_id
),
StreakGroups AS (
    SELECT
        team_name,
        same_team,
        SUM(CASE WHEN same_team = 0 THEN 1 ELSE 0 END) OVER (
            PARTITION BY team_name ORDER BY time_stamp
        ) AS group_id
    FROM PassesWithTeams
),
StreakLengths AS (
    SELECT team_name, group_id, COUNT(*) AS streak_length
    FROM StreakGroups
    WHERE same_team = 1
    GROUP BY 1, 2
)
SELECT team_name, MAX(streak_length) AS longest_streak
FROM StreakLengths
GROUP BY 1
ORDER BY 1;
"""
        return self.sql
# @lc code=end
