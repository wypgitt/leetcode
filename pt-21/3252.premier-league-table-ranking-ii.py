#
# @lc app=leetcode id=3252 lang=python3
#
# [3252] Premier League Table Ranking II
#
# https://leetcode.com/problems/premier-league-table-ranking-ii/description/
#
# database
# Medium (55.56%)
# Likes:    11
# Dislikes: 12
# Total Accepted:    2.2K
# Total Submissions: 4K
# Testcase Example:  "{\"headers\": {\"TeamStats\": [\"team_id\", \"team_name\", \"matches_played\", \"wins\", \"draws\", \"losses\"]}, \"rows\": {\"TeamStats\": [[1, \"Chelsea\", 22, 13, 2, 7], [2, \"Nottingham Forest\", 27, 6, 6, 15], [3, \"Liverpool\", 17, 1, 8, 8], [4, \"Aston Villa\", 20, 1, 6, 13], [5, \"Fulham\", 31, 18, 1, 12], [6, \"Burnley\", 26, 6, 9, 11], [7, \"Newcastle United\", 33, 11, 10, 12], [8, \"Sheffield United\", 20, 18, 2, 0], [9, \"Luton Town\", 5, 4, 0, 1], [10, \"Everton\", 14, 2, 6, 6]]}}"
#
#
# Table: TeamStats
#
# +------------------+---------+
# | Column Name      | Type    |
# +------------------+---------+
# | team_id          | int     |
# | team_name        | varchar |
# | matches_played   | int     |
# | wins             | int     |
# | draws            | int     |
# | losses           | int     |
# +------------------+---------+
# team_id is the unique key for this table.
# This table contains team id, team name, matches_played, wins, draws, and
# losses.
#
# Write a solution to calculate the points, position, and tier for each
# team in the league. Points are calculated as follows:
#
# 3 points for a win
#
# 1 point for a draw
#
# 0 points for a loss
#
# Note: Teams with the same points must be assigned the same position.
#
# Tier ranking:
#
# Divide the league into 3 tiers based on points:
#
# Tier 1: Top 33% of teams
#
# Tier 2: Middle 33% of teams
#
# Tier 3: Bottom 34% of teams
#
# In case of ties at tier boundaries, place tied teams in the higher tier.
#
# Return the result table ordered by points in descending, and then by
# team_name in ascending order.
#
# The query result format is in the following example.
#
# Example:
#
# Input:
#
# TeamStats table:
#
# +---------+-------------------+----------------+------+-------+--------+
# | team_id | team_name         | matches_played | wins | draws | losses |
# +---------+-------------------+----------------+------+-------+--------+
# | 1       | Chelsea           | 22             | 13   | 2     | 7      |
# | 2       | Nottingham Forest | 27             | 6    | 6     | 15     |
# | 3       | Liverpool         | 17             | 1    | 8     | 8      |
# | 4       | Aston Villa       | 20             | 1    | 6     | 13     |
# | 5       | Fulham            | 31             | 18   | 1     | 12     |
# | 6       | Burnley           | 26             | 6    | 9     | 11     |
# | 7       | Newcastle United  | 33             | 11   | 10    | 12     |
# | 8       | Sheffield United  | 20             | 18   | 2     | 0      |
# | 9       | Luton Town        | 5              | 4    | 0     | 1      |
# | 10      | Everton           | 14             | 2    | 6     | 6      |
# +---------+-------------------+----------------+------+-------+--------+
#
# Output:
#
# +-------------------+--------+----------+---------+
# | team_name         | points | position | tier    |
# +-------------------+--------+----------+---------+
# | Sheffield United  | 56     | 1        | Tier 1  |
# | Fulham            | 55     | 2        | Tier 1  |
# | Newcastle United  | 43     | 3        | Tier 1  |
# | Chelsea           | 41     | 4        | Tier 1  |
# | Burnley           | 27     | 5        | Tier 2  |
# | Nottingham Forest | 24     | 6        | Tier 2  |
# | Everton           | 12     | 7        | Tier 2  |
# | Luton Town        | 12     | 7        | Tier 2  |
# | Liverpool         | 11     | 9        | Tier 3  |
# | Aston Villa       | 9      | 10       | Tier 3  |
# +-------------------+--------+----------+---------+
#
# Explanation:
#
# Sheffield United has 56 points (18 wins * 3 points + 2 draws * 1 point)
# and is in position 1.
#
# Fulham has 55 points (18 wins * 3 points + 1 draw * 1 point) and is in
# position 2.
#
# Newcastle United has 43 points (11 wins * 3 points + 10 draws * 1 point)
# and is in position 3.
#
# Chelsea has 41 points (13 wins * 3 points + 2 draws * 1 point) and is in
# position 4.
#
# Burnley has 27 points (6 wins * 3 points + 9 draws * 1 point) and is in
# position 5.
#
# Nottingham Forest has 24 points (6 wins * 3 points + 6 draws * 1 point)
# and is in position 6.
#
# Everton and Luton Town both have 12 points, with Everton having 2 wins *
# 3 points + 6 draws * 1 point, and Luton Town having 4 wins * 3 points.
# Both teams share position 7.
#
# Liverpool has 11 points (1 win * 3 points + 8 draws * 1 point) and is in
# position 9.
#
# Aston Villa has 9 points (1 win * 3 points + 6 draws * 1 point) and is
# in position 10.
#
# Tier Calculation:
#
# Tier 1: The top 33% of teams based on points. Sheffield United, Fulham,
# Newcastle United, and Chelsea fall into Tier 1.
#
# Tier 2: The middle 33% of teams. Burnley, Nottingham Forest, Everton,
# and Luton Town fall into Tier 2.
#
# Tier 3: The bottom 34% of teams. Liverpool and Aston Villa fall into
# Tier 3.
#

# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: points + RANK position, then split into Tier 1/2/3 by
        CEIL(N/3) and CEIL(2N/3) position cutoffs (ties go to the higher tier).

        Algorithm:
        - CTE with points, RANK(), COUNT(*) OVER().
        - CASE on position vs CEIL cutoffs; order by points DESC, name ASC.

        Complexity: O(N log N).
        """
        self.sql = """
WITH T AS (
    SELECT
        team_name,
        wins * 3 + draws AS points,
        RANK() OVER (ORDER BY wins * 3 + draws DESC) AS position,
        COUNT(1) OVER () AS total_teams
    FROM TeamStats
)
SELECT
    team_name,
    points,
    position,
    CASE
        WHEN position <= CEIL(total_teams / 3.0) THEN 'Tier 1'
        WHEN position <= CEIL(2 * total_teams / 3.0) THEN 'Tier 2'
        ELSE 'Tier 3'
    END AS tier
FROM T
ORDER BY points DESC, team_name;
"""
        return self.sql
# @lc code=end
