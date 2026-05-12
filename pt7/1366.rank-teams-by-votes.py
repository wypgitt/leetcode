#
# @lc app=leetcode id=1366 lang=python3
#
# [1366] Rank Teams by Votes
#
# https://leetcode.com/problems/rank-teams-by-votes/description/
#
# algorithms
# Medium (60.11%)
# Likes:    1570
# Dislikes: 198
# Total Accepted:    103.4K
# Total Submissions: 172K
# Testcase Example:  '["ABC","ACB","ABC","ACB","ACB"]'
#
# In a special ranking system, each voter gives a rank from highest to lowest
# to all teams participating in the competition.
# 
# The ordering of teams is decided by who received the most position-one votes.
# If two or more teams tie in the first position, we consider the second
# position to resolve the conflict, if they tie again, we continue this process
# until the ties are resolved. If two or more teams are still tied after
# considering all positions, we rank them alphabetically based on their team
# letter.
# 
# You are given an array of strings votes which is the votes of all voters in
# the ranking systems. Sort all teams according to the ranking system described
# above.
# 
# Return a string of all teams sorted by the ranking system.
# 
# 
# Example 1:
# 
# 
# Input: votes = ["ABC","ACB","ABC","ACB","ACB"]
# Output: "ACB"
# Explanation: 
# Team A was ranked first place by 5 voters. No other team was voted as first
# place, so team A is the first team.
# Team B was ranked second by 2 voters and ranked third by 3 voters.
# Team C was ranked second by 3 voters and ranked third by 2 voters.
# As most of the voters ranked C second, team C is the second team, and team B
# is the third.
# 
# 
# Example 2:
# 
# 
# Input: votes = ["WXYZ","XYZW"]
# Output: "XWYZ"
# Explanation:
# X is the winner due to the tie-breaking rule. X has the same votes as W for
# the first position, but X has one vote in the second position, while W does
# not have any votes in the second position. 
# 
# 
# Example 3:
# 
# 
# Input: votes = ["ZMNAGUEDSJYLBOPHRQICWFXTVK"]
# Output: "ZMNAGUEDSJYLBOPHRQICWFXTVK"
# Explanation: Only one voter, so their votes are used for the ranking.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= votes.length <= 1000
# 1 <= votes[i].length <= 26
# votes[i].length == votes[j].length for 0 <= i, j < votes.length.
# votes[i][j] is an English uppercase letter.
# All characters of votes[i] are unique.
# All the characters that occur in votes[0] also occur in votes[j] where 1 <= j
# < votes.length.
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import List


class Solution:
    def rankTeams(self, votes: List[str]) -> str:
        teams = votes[0]
        positions = len(teams)
        counts = {team: [0] * positions for team in teams}

        for vote in votes:
            for position, team in enumerate(vote):
                counts[team][position] += 1

        ranked = sorted(
            teams,
            key=lambda team: tuple([-counts[team][position] for position in range(positions)] + [team]),
        )
        return "".join(ranked)
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Teams are compared by how many first-place votes they have, then second-place
# votes, and so on. If every position count ties, alphabetical order wins.
#
# Data structure:
# `counts[team][position]` stores how many votes ranked `team` at `position`.
#
# Walkthrough:
# 1. Initialize a count list for every team in the first vote.
# 2. For every vote, increment the team's count at each position.
# 3. Sort teams by negative counts at every position so larger counts come
#    first.
# 4. Append the team letter itself as the final tie-breaker.
#
# Edge cases:
# - Only one vote: sorting reproduces that vote.
# - Complete tie across all positions: alphabetical order decides.
# - One team: answer is that team.
#
# Complexity:
# - Time: O(v * t + t log t * t), where v is votes and t is teams. Since
#   t <= 26, this is very small.
# - Space: O(t^2) for the ranking counts.
