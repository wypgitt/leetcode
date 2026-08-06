#
# @lc app=leetcode id=3938 lang=python3
#
# [3938] Maximum Path Intersection Sum in a Grid
#
# https://leetcode.com/problems/maximum-path-intersection-sum-in-a-grid/description/
#
# algorithms
# Medium (25.38%)
# Likes:    75
# Dislikes: 3
# Total Accepted:    6.7K
# Total Submissions: 26.3K
# Testcase Example:  "[[1,2,0,-3],[1,-2,1,0],[-4,2,-1,3],[3,-3,3,-2],[-1,-5,0,1]]"
#
#
# You are given an m x n integer matrix grid.
#
# Two players move across the grid:
#
# Player 1 starts at the top-left cell (0, 0) and can move only right or
# down. Their destination is the bottom-right cell (m - 1, n - 1).
#
# Player 2 starts at the bottom-left cell (m - 1, 0) and can move only
# right or up. Their destination is the top-right cell (0, n - 1).
#
# Each player must choose a valid path from their respective starting cell
# to their destination.
#
# A cell is called shared if it belongs to both chosen paths.
#
# Return an integer denoting the maximum possible sum of values of all
# shared cells.
#
# Example 1:
#
# ​​​​​​​​​​​​​​​​​​​​​
#
# Input: grid =
# [[1,2,0,-3],[1,-2,1,0],[-4,2,-1,3],[3,-3,3,-2],[-1,-5,0,1]]
#
# Output: 4
#
# Explanation:
#
# The diagram shows one optimal choice of paths.
#
# Player 1 follows the red/purple path from the top-left cell to the
# bottom-right cell:
#
# (0, 0) → (1, 0) → (2, 0) → (2, 1) → (2, 2) → (2, 3) → (3, 3) → (4, 3)
#
# Player 2 follows the blue/purple path from the bottom-left cell to the
# top-right cell:
#
# (4, 0) → (4, 1) → (3, 1) → (2, 1) → (2, 2) → (2, 3) → (1, 3) → (0, 3)
#
# The shared cells are (2, 1), (2, 2), and (2, 3).
#
# The sum is 2 + (-1) + 3 = 4, which is the maximum possible sum.
#
# Example 2:
#
# Input: grid = [[4,-2,-3],[-1,-3,-1],[-4,2,-1]]
#
# Output: 3
#
# Explanation:
#
# One optimal pair of paths is shown in the diagram.
#
# Player 1 follows the red/purple path:
#
# (0, 0) → (1, 0) → (1, 1) → (1, 2) → (2, 2)
#
# Player 2 follows the blue/purple path:
#
# (2, 0) → (1, 0) → (0, 0) → (0, 1) → (0, 2)
#
# The shared cells are (0, 0) and (1, 0).
#
# The sum is 4 + (-1) = 3, which is the maximum possible.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 2 <= m, n <= 1000
#
# 4 <= m * n <= 5 * 10^5
#
# -100 <= grid[i][j] <= 100
#

# @lc code=start

class Solution:
    def maxScore(self, grid: list[list[int]]) -> int:
        """
        Interview explanation:
        With P1 (right/down) and P2 (right/up), any optimal shared set is a
        contiguous row segment, a contiguous column segment (length >= 2), or a
        single interior cell (strictly inside the border).

        Algorithm:
        - Kadane variant: max subarray sum of length >= 2 on every row/column.
        - Also take max grid[i][j] over 0 < i < m-1 and 0 < j < n-1.
        - Answer is the maximum among these candidates.

        Complexity: O(m*n) time, O(1) extra space.
        """
        m, n = len(grid), len(grid[0])
        ans = -10**18

        def kadane_at_least_two(arr) -> int:
            if len(arr) < 2:
                return -10**18
            best = cur = arr[0] + arr[1]
            for i in range(2, len(arr)):
                cur = max(arr[i - 1] + arr[i], cur + arr[i])
                if cur > best:
                    best = cur
            return best

        for i in range(m):
            ans = max(ans, kadane_at_least_two(grid[i]))
        for j in range(n):
            col = [grid[i][j] for i in range(m)]
            ans = max(ans, kadane_at_least_two(col))

        for i in range(1, m - 1):
            for j in range(1, n - 1):
                if grid[i][j] > ans:
                    ans = grid[i][j]
        return ans
# @lc code=end
