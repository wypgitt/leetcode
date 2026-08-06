#
# @lc app=leetcode id=1212 lang=python3
#
# [1212] Team Scores in Football Tournament
#
# https://leetcode.com/problems/team-scores-in-football-tournament/description/
#
# database
# Medium (55.77%)
# Likes:    331
# Dislikes: 26
# Total Accepted:    53K
# Total Submissions: 95.1K
# Testcase Example:  "{\"headers\": {\"Teams\": [\"team_id\", \"team_name\"], \"Matches\": [\"match_id\", \"host_team\", \"guest_team\", \"host_goals\", \"guest_goals\"]}, \"rows\": {\"Teams\": [[10, \"Leetcode FC\"], [20, \"NewYork FC\"], [30, \"Atlanta FC\"], [40, \"Chicago FC\"], [50, \"Toronto FC\"]], \"Matches\": [[1, 10, 20, 3, 0], [2, 30, 10, 2, 2], [3, 10, 50, 5, 1], [4, 20, 30, 1, 0], [5, 50, 30, 1, 0]]}}"
#
#
# Table: Teams
#
# +---------------+----------+
# | Column Name   | Type     |
# +---------------+----------+
# | team_id       | int      |
# | team_name     | varchar  |
# +---------------+----------+
# team_id is the column with unique values of this table.
# Each row of this table represents a single football team.
#
# Table: Matches
#
# +---------------+---------+
# | Column Name   | Type    |
# +---------------+---------+
# | match_id      | int     |
# | host_team     | int     |
# | guest_team    | int     |
# | host_goals    | int     |
# | guest_goals   | int     |
# +---------------+---------+
# match_id is the column of unique values of this table.
# Each row is a record of a finished match between two different teams.
# Teams host_team and guest_team are represented by their IDs in the Teams
# table (team_id), and they scored host_goals and guest_goals goals,
# respectively.
#
# You would like to compute the scores of all teams after all matches.
# Points are awarded as follows:
#
# A team receives three points if they win a match (i.e., Scored more
# goals than the opponent team).
#
# A team receives one point if they draw a match (i.e., Scored the same
# number of goals as the opponent team).
#
# A team receives no points if they lose a match (i.e., Scored fewer goals
# than the opponent team).
#
# Write a solution that selects the team_id, team_name and num_points of
# each team in the tournament after all described matches.
#
# Return the result table ordered by num_points in decreasing order. In
# case of a tie, order the records by team_id in increasing order.
#
# The result format is in the following example.
#
# Example 1:
#
# Input:
# Teams table:
# +-----------+--------------+
# | team_id   | team_name    |
# +-----------+--------------+
# | 10        | Leetcode FC  |
# | 20        | NewYork FC   |
# | 30        | Atlanta FC   |
# | 40        | Chicago FC   |
# | 50        | Toronto FC   |
# +-----------+--------------+
# Matches table:
# +------------+--------------+---------------+-------------+--------------+
# | match_id   | host_team    | guest_team    | host_goals  | guest_goals
# |
# +------------+--------------+---------------+-------------+--------------+
# | 1          | 10           | 20            | 3           | 0
# |
# | 2          | 30           | 10            | 2           | 2
# |
# | 3          | 10           | 50            | 5           | 1
# |
# | 4          | 20           | 30            | 1           | 0
# |
# | 5          | 50           | 30            | 1           | 0
# |
# +------------+--------------+---------------+-------------+--------------+
# Output:
# +------------+--------------+---------------+
# | team_id    | team_name    | num_points    |
# +------------+--------------+---------------+
# | 10         | Leetcode FC  | 7             |
# | 20         | NewYork FC   | 3             |
# | 50         | Toronto FC   | 3             |
# | 30         | Atlanta FC   | 1             |
# | 40         | Chicago FC   | 0             |
# +------------+--------------+---------------+
#
# @lc code=start
class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Compute each team's points from Matches: win=3, draw=1, loss=0 for
        host and guest. Left join Teams to aggregated points; COALESCE 0.

        Algorithm:
        - UNION ALL host/guest scores from Matches; SUM by team_id
        - LEFT JOIN Teams; ORDER BY num_points DESC, team_id ASC

        Complexity: O(N).
        """
        return self.sql

    sql = """
    SELECT t.team_id, t.team_name,
           COALESCE(SUM(p.points), 0) AS num_points
    FROM Teams t
    LEFT JOIN (
        SELECT host_team AS team_id,
               CASE WHEN host_goals > guest_goals THEN 3
                    WHEN host_goals = guest_goals THEN 1
                    ELSE 0 END AS points
        FROM Matches
        UNION ALL
        SELECT guest_team AS team_id,
               CASE WHEN guest_goals > host_goals THEN 3
                    WHEN guest_goals = host_goals THEN 1
                    ELSE 0 END AS points
        FROM Matches
    ) p ON t.team_id = p.team_id
    GROUP BY t.team_id, t.team_name
    ORDER BY num_points DESC, t.team_id ASC;
    """
# @lc code=end
