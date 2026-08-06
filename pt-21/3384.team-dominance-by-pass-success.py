#
# @lc app=leetcode id=3384 lang=python3
#
# [3384] Team Dominance by Pass Success
#
# https://leetcode.com/problems/team-dominance-by-pass-success/description/
#
# database
# Hard (71.38%)
# Likes:    5
# Dislikes: 0
# Total Accepted:    1.6K
# Total Submissions: 2.3K
# Testcase Example:  "{\"headers\":{\"Teams\":[\"player_id\",\"team_name\"],\"Passes\":[\"pass_from\",\"time_stamp\",\"pass_to\"]},\"rows\":{\"Teams\":[[1,\"Arsenal\"],[2,\"Arsenal\"],[3,\"Arsenal\"],[4,\"Chelsea\"],[5,\"Chelsea\"],[6,\"Chelsea\"]],\"Passes\":[[1,\"00:15\",2],[2,\"00:45\",3],[3,\"01:15\",1],[4,\"00:30\",1],[2,\"46:00\",3],[3,\"46:15\",4],[1,\"46:45\",2],[5,\"46:30\",6]]}}"
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
# (pass_from, time_stamp) is the primary key for this table.
# pass_from is a foreign key to player_id from Teams table.
# Each row represents a pass made during a match, time_stamp represents
# the time in minutes (00:00-90:00) when the pass was made,
# pass_to is the player_id of the player receiving the pass.
#
# Write a solution to calculate the dominance score for each team in both
# halves of the match. The rules are as follows:
#
# A match is divided into two halves: first half (00:00-45:00 minutes) and
# second half (45:01-90:00 minutes)
#
# The dominance score is calculated based on successful and intercepted
# passes:
#
# When pass_to is a player from the same team: +1 point
#
# When pass_to is a player from the opposing team (interception): -1 point
#
# A higher dominance score indicates better passing performance
#
# Return the result table ordered by team_name and half_number in
# ascending order.
#
# The result format is in the following example.
#
# Example:
#
# Input:
#
# Teams table:
#
# +------------+-----------+
# | player_id  | team_name |
# +------------+-----------+
# | 1          | Arsenal   |
# | 2          | Arsenal   |
# | 3          | Arsenal   |
# | 4          | Chelsea   |
# | 5          | Chelsea   |
# | 6          | Chelsea   |
# +------------+-----------+
#
# Passes table:
#
# +-----------+------------+---------+
# | pass_from | time_stamp | pass_to |
# +-----------+------------+---------+
# | 1         | 00:15      | 2       |
# | 2         | 00:45      | 3       |
# | 3         | 01:15      | 1       |
# | 4         | 00:30      | 1       |
# | 2         | 46:00      | 3       |
# | 3         | 46:15      | 4       |
# | 1         | 46:45      | 2       |
# | 5         | 46:30      | 6       |
# +-----------+------------+---------+
#
# Output:
#
# +-----------+-------------+-----------+
# | team_name | half_number | dominance |
# +-----------+-------------+-----------+
# | Arsenal   | 1           | 3         |
# | Arsenal   | 2           | 1         |
# | Chelsea   | 1           | -1        |
# | Chelsea   | 2           | 1         |
# +-----------+-------------+-----------+
#
# Explanation:
#
# First Half (00:00-45:00):
#
# Arsenal's passes:
#
# 1 → 2 (00:15): Successful pass (+1)
#
# 2 → 3 (00:45): Successful pass (+1)
#
# 3 → 1 (01:15): Successful pass (+1)
#
# Chelsea's passes:
#
# 4 → 1 (00:30): Intercepted by Arsenal (-1)
#
# Second Half (45:01-90:00):
#
# Arsenal's passes:
#
# 2 → 3 (46:00): Successful pass (+1)
#
# 3 → 4 (46:15): Intercepted by Chelsea (-1)
#
# 1 → 2 (46:45): Successful pass (+1)
#
# Chelsea's passes:
#
# 5 → 6 (46:30): Successful pass (+1)
#
# The results are ordered by team_name and then half_number
#

# @lc code=start

class Solution:
    def solve(self) -> str:
        """
        Interview explanation:
        Premium SQL: Teams(player_id, team_name), Passes(pass_from, time_stamp,
        pass_to). Per team and half, +1 same-team pass, -1 interception.

        Algorithm:
        - Join passer/receiver teams; half = 1 if time_stamp <= '45:00' else 2.
        - GROUP BY team_name, half_number; SUM signed points; ORDER BY both ASC.

        Complexity: O(P log P).
        """
        self.sql = """
SELECT
    t1.team_name,
    CASE WHEN p.time_stamp <= '45:00' THEN 1 ELSE 2 END AS half_number,
    SUM(CASE WHEN t1.team_name = t2.team_name THEN 1 ELSE -1 END) AS dominance
FROM Passes p
JOIN Teams t1 ON p.pass_from = t1.player_id
JOIN Teams t2 ON p.pass_to = t2.player_id
GROUP BY 1, 2
ORDER BY 1, 2;
"""
        return self.sql
# @lc code=end
