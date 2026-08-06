#
# @lc app=leetcode id=3742 lang=python3
#
# [3742] Maximum Path Score in a Grid
#
# https://leetcode.com/problems/maximum-path-score-in-a-grid/description/
#
# algorithms
# Medium (53.50%)
# Likes:    269
# Dislikes: 13
# Total Accepted:    85.4K
# Total Submissions: 159.6K
# Testcase Example:  "[[0, 1],[2, 0]]\n1"
#
#
# You are given an m x n grid where each cell contains one of the values
# 0, 1, or 2. You are also given an integer k.
#
# You start from the top-left corner (0, 0) and want to reach the
# bottom-right corner (m - 1, n - 1) by moving only right or down.
#
# Each cell contributes a specific score and incurs an associated cost,
# according to their cell values:
#
# 0: adds 0 to your score and costs 0.
#
# 1: adds 1 to your score and costs 1.
#
# 2: adds 2 to your score and costs 1. ​​​​​​​
#
# Return the maximum score achievable without exceeding a total cost of k,
# or -1 if no valid path exists.
#
# Note: If you reach the last cell but the total cost exceeds k, the path
# is invalid.
#
# Example 1:
#
# Input: grid = [[0, 1],[2, 0]], k = 1
#
# Output: 2
#
# Explanation:​​​​​​​
#
# The optimal path is:
#
#                         Cell
#                         grid[i][j]
#                         Score
#                         Total
#
#                         Score
#                         Cost
#                         Total
#
#                         Cost
#
#                         (0, 0)
#                         0
#                         0
#                         0
#                         0
#                         0
#
#                         (1, 0)
#                         2
#                         2
#                         2
#                         1
#                         1
#
#                         (1, 1)
#                         0
#                         0
#                         2
#                         0
#                         1
#
# Thus, the maximum possible score is 2.
#
# Example 2:
#
# Input: grid = [[0, 1],[1, 2]], k = 1
#
# Output: -1
#
# Explanation:
#
# There is no path that reaches cell (1, 1)​​​​​​​ without exceeding cost
# k. Thus, the answer is -1.
#
# Constraints:
#
# 1 <= m, n <= 200
#
# 0 <= k <= 10^3​​​​​​​
#
# ^​​​​​​​grid[0][0] == 0
#
# 0 <= grid[i][j] <= 2
#

# @lc code=start
from typing import List


class Solution:
    def maxPathScore(self, grid: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Only right/down moves; each cell adds its value to score and costs 1
        unless the value is 0. Maximize score with total cost <= k.

        Algorithm:
        - DP[i][j][c] = max score to reach (i, j) with exact cost c (-1 = impossible).
        - Transition right/down, paying the destination cell's cost and adding its value.

        Complexity: O(m n k) time and space.
        """
        m, n = len(grid), len(grid[0])
        dp = [[[-1] * (k + 1) for _ in range(n)] for _ in range(m)]
        dp[0][0][0] = 0
        for i in range(m):
            for j in range(n):
                for c in range(k + 1):
                    if dp[i][j][c] < 0:
                        continue
                    for ni, nj in ((i + 1, j), (i, j + 1)):
                        if ni >= m or nj >= n:
                            continue
                        nc = c + (0 if grid[ni][nj] == 0 else 1)
                        if nc > k:
                            continue
                        dp[ni][nj][nc] = max(dp[ni][nj][nc], dp[i][j][c] + grid[ni][nj])
        return max(dp[-1][-1])

    def maxPathScore_dijkstra(self, grid: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Alternate: state (r, c, cost) with best-first search maximizing score.

        Algorithm:
        - Max-heap of (score, i, j, cost); relax right/down neighbors within budget.

        Complexity: O(m n k log(m n k)) time, O(m n k) space.
        """
        import heapq

        m, n = len(grid), len(grid[0])
        best = [[[-1] * (k + 1) for _ in range(n)] for _ in range(m)]
        best[0][0][0] = 0
        heap = [(0, 0, 0, 0)]  # (-score, i, j, cost)
        while heap:
            nscore, i, j, c = heapq.heappop(heap)
            score = -nscore
            if score != best[i][j][c]:
                continue
            if i == m - 1 and j == n - 1:
                return score
            for ni, nj in ((i + 1, j), (i, j + 1)):
                if ni >= m or nj >= n:
                    continue
                nc = c + (0 if grid[ni][nj] == 0 else 1)
                if nc > k:
                    continue
                nsc = score + grid[ni][nj]
                if nsc > best[ni][nj][nc]:
                    best[ni][nj][nc] = nsc
                    heapq.heappush(heap, (-nsc, ni, nj, nc))
        return -1
# @lc code=end
