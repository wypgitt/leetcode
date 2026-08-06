#
# @lc app=leetcode id=1820 lang=python3
#
# [1820] Maximum Number of Accepted Invitations
#
# https://leetcode.com/problems/maximum-number-of-accepted-invitations/description/
#
# algorithms
# Medium (52.81%)
# Likes:    238
# Dislikes: 68
# Total Accepted:    11.3K
# Total Submissions: 21.5K
# Testcase Example:  "[[1,1,1],[1,0,1],[0,0,1]]"
#
#
# There are m boys and n girls in a class attending an upcoming party.
#
# You are given an m x n integer matrix grid, where grid[i][j] equals 0 or
# 1. If grid[i][j] == 1, then that means the i^th boy can invite the j^th
# girl to the party. A boy can invite at most one girl, and a girl can
# accept at most one invitation from a boy.
#
# Return the maximum possible number of accepted invitations.
#
# Example 1:
#
# Input: grid = [[1,1,1],
#                [1,0,1],
#                [0,0,1]]
# Output: 3
# Explanation: The invitations are sent as follows:
# - The 1^st boy invites the 2^nd girl.
# - The 2^nd boy invites the 1^st girl.
# - The 3^rd boy invites the 3^rd girl.
#
# Example 2:
#
# Input: grid = [[1,0,1,0],
#                [1,0,0,0],
#                [0,0,1,0],
#                [1,1,1,0]]
# Output: 3
# Explanation: The invitations are sent as follows:
# -The 1^st boy invites the 3^rd girl.
# -The 2^nd boy invites the 1^st girl.
# -The 3^rd boy invites no one.
# -The 4^th boy invites the 2^nd girl.
#
# Constraints:
#
# grid.length == m
#
# grid[i].length == n
#
# 1 <= m, n <= 200
#
# grid[i][j] is either 0 or 1.
#
# @lc code=start
from typing import List


class Solution:
    def maximumInvitations(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium: bipartite matching boys×girls where grid[i][j]=1 means invite OK.
        Maximum accepted invitations = maximum matching (DFS augmenting paths /
        Kuhn's algorithm).

        Algorithm (DFS bipartite matching):
        - match[girl]=boy or -1; for each boy try dfs to find augmenting path.
        - Count successful matches.

        Complexity: O(V*E) time, O(V) space.
        """
        m, n = len(grid), len(grid[0])
        match = [-1] * n

        def dfs(boy: int, seen: List[bool]) -> bool:
            for girl in range(n):
                if grid[boy][girl] and not seen[girl]:
                    seen[girl] = True
                    if match[girl] == -1 or dfs(match[girl], seen):
                        match[girl] = boy
                        return True
            return False

        ans = 0
        for boy in range(m):
            if dfs(boy, [False] * n):
                ans += 1
        return ans
# @lc code=end
