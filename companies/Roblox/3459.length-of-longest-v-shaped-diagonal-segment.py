#
# @lc app=leetcode id=3459 lang=python3
#
# [3459] Length of Longest V-Shaped Diagonal Segment
#
# https://leetcode.com/problems/length-of-longest-v-shaped-diagonal-segment/description/
#
# algorithms
# Hard (55.92%)
# Likes:    376
# Dislikes: 67
# Total Accepted:    74.4K
# Total Submissions: 133K
# Testcase Example:  "[[2,2,1,2,2],[2,0,2,2,0],[2,0,1,1,0],[1,0,2,2,2],[2,0,0,2,2]]"
#
#
# You are given a 2D integer matrix grid of size n x m, where each element
# is either 0, 1, or 2.
#
# A V-shaped diagonal segment is defined as:
#
# The segment starts with 1.
#
# The subsequent elements follow this infinite sequence: 2, 0, 2, 0, ....
#
# The segment:
#
# Starts along a diagonal direction (top-left to bottom-right,
# bottom-right to top-left, top-right to bottom-left, or bottom-left to
# top-right).
#
# Continues the sequence in the same diagonal direction.
#
# Makes at most one clockwise 90-degree turn to another diagonal direction
# while maintaining the sequence.
#
# Return the length of the longest V-shaped diagonal segment. If no valid
# segment exists, return 0.
#
# Example 1:
#
# Input: grid =
# [[2,2,1,2,2],[2,0,2,2,0],[2,0,1,1,0],[1,0,2,2,2],[2,0,0,2,2]]
#
# Output: 5
#
# Explanation:
#
# The longest V-shaped diagonal segment has a length of 5 and follows
# these coordinates: (0,2) → (1,3) → (2,4), takes a 90-degree clockwise
# turn at (2,4), and continues as (3,3) → (4,2).
#
# Example 2:
#
# Input: grid =
# [[2,2,2,2,2],[2,0,2,2,0],[2,0,1,1,0],[1,0,2,2,2],[2,0,0,2,2]]
#
# Output: 4
#
# Explanation:
#
# The longest V-shaped diagonal segment has a length of 4 and follows
# these coordinates: (2,3) → (3,2), takes a 90-degree clockwise turn at
# (3,2), and continues as (2,1) → (1,0).
#
# Example 3:
#
# Input: grid =
# [[1,2,2,2,2],[2,2,2,2,0],[2,0,0,0,0],[0,0,2,2,2],[2,0,0,2,0]]
#
# Output: 5
#
# Explanation:
#
# The longest V-shaped diagonal segment has a length of 5 and follows
# these coordinates: (0,0) → (1,1) → (2,2) → (3,3) → (4,4).
#
# Example 4:
#
# Input: grid = [[1]]
#
# Output: 1
#
# Explanation:
#
# The longest V-shaped diagonal segment has a length of 1 and follows
# these coordinates: (0,0).
#
# Constraints:
#
# n == grid.length
#
# m == grid[i].length
#
# 1 <= n, m <= 500
#
# grid[i][j] is either 0, 1 or 2.
#

# @lc code=start

from functools import cache
from typing import List


class Solution:
    def lenOfVDiagonal(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Longest diagonal walk starting at 1 then alternating 2,0,2,0... with at most
        one clockwise 90° turn.

        Algorithm:
        - DFS+memo from each 1 in each of 4 diagonal dirs with a "turn left" flag.
        - From (i,j,dir,turns_left): step to next cell if it matches target; optionally
          turn clockwise once.

        Complexity: O(n*m) states (pos × 4 dirs × 2 turn flags), O(n*m) space.
        """
        m, n = len(grid), len(grid[0])
        # dirs[k], dirs[k+1]: (1,1),(1,-1),(-1,-1),(-1,1) — clockwise cycle
        dirs = (1, 1, -1, -1, 1)

        @cache
        def dfs(i: int, j: int, k: int, turns: int) -> int:
            x, y = i + dirs[k], j + dirs[k + 1]
            target = 2 if grid[i][j] == 1 else 2 - grid[i][j]
            if not (0 <= x < m and 0 <= y < n) or grid[x][y] != target:
                return 0
            best = dfs(x, y, k, turns)
            if turns:
                best = max(best, dfs(x, y, (k + 1) % 4, 0))
            return 1 + best

        ans = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j] == 1:
                    for k in range(4):
                        ans = max(ans, dfs(i, j, k, 1) + 1)
        return ans
# @lc code=end
