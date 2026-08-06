#
# @lc app=leetcode id=174 lang=python3
#
# [174] Dungeon Game
#
# https://leetcode.com/problems/dungeon-game/description/
#
# algorithms
# Hard (41.92%)
# Likes:    6328
# Dislikes: 118
# Total Accepted:    316K
# Total Submissions: 754K
# Testcase Example:  "[[-2,-3,3],[-5,-10,1],[10,30,-5]]"
#
# The demons had captured the princess and imprisoned her in the bottom-right
# corner of a dungeon. The dungeon consists of m x n rooms laid out in a 2D
# grid. Our valiant knight was initially positioned in the top-left room and
# must fight his way through dungeon to rescue the princess.
#
# The knight has an initial health point represented by a positive integer. If
# at any point his health point drops to 0 or below, he dies immediately.
#
# Some of the rooms are guarded by demons (represented by negative integers),
# so the knight loses health upon entering these rooms; other rooms are either
# empty (represented as 0) or contain magic orbs that increase the knight's
# health (represented by positive integers).
#
# To reach the princess as quickly as possible, the knight decides to move only
# rightward or downward in each step.
#
# Return the knight's minimum initial health so that he can rescue the
# princess.
#
# Note that any room can contain threats or power-ups, even the first room the
# knight enters and the bottom-right room where the princess is imprisoned.
#
# Example 1:
#
# Input: dungeon = [[-2,-3,3],[-5,-10,1],[10,30,-5]]
# Output: 7
# Explanation: The initial health of the knight must be at least 7 if he
# follows the optimal path: RIGHT-> RIGHT -> DOWN -> DOWN.
#
# Example 2:
#
# Input: dungeon = [[0]]
# Output: 1
#
# Constraints:
#
# m == dungeon.length
#
# n == dungeon[i].length
#
# 1 <= m, n <= 200
#
# -1000 <= dungeon[i][j] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def calculateMinimumHP(self, dungeon: List[List[int]]) -> int:
        """
        Interview explanation:
        DP from the princess cell upward/leftward: at each cell compute the
        minimum HP needed before entering so that HP stays positive after the
        room effect and along an optimal path to the end.

        Algorithm:
        - dp[i][j] = min HP required on entering (i, j).
        - dp[m-1][n-1] = max(1, 1 - dungeon[m-1][n-1]).
        - For other cells: need = min(dp_right, dp_down) - dungeon[i][j];
          dp[i][j] = max(1, need).
        - Use a 1D rolling array from bottom-right.

        Complexity: O(m * n) time, O(n) space.
        """
        m, n = len(dungeon), len(dungeon[0])
        dp = [float("inf")] * (n + 1)
        dp[n - 1] = 1
        for i in range(m - 1, -1, -1):
            for j in range(n - 1, -1, -1):
                need = min(dp[j], dp[j + 1]) - dungeon[i][j]
                dp[j] = 1 if need <= 1 else need
        return int(dp[0])
# @lc code=end
