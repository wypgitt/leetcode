#
# @lc app=leetcode id=3988 lang=python3
#
# [3988] Create Grid With Exactly K Paths I
#
# https://leetcode.com/problems/create-grid-with-exactly-k-paths-i/description/
#
# algorithms
# Medium (32.78%)
# Likes:    50
# Dislikes: 13
# Total Accepted:    8.7K
# Total Submissions: 26.6K
# Testcase Example:  "2\n3\n2"
#
#
# You are given three integers m, n, and k.
#
# Construct any m x n grid consisting only of the characters '.' and '#',
# where:
#
# '.' represents a free cell.
#
# '#' represents an obstacle cell.
#
# A valid path is a sequence of free cells that:
#
# Starts at the top-left cell (0, 0).
#
# Ends at the bottom-right cell (m - 1, n - 1).
#
# Moves only:
#
# Right, from (i, j) to (i, j + 1), or
#
# Down, from (i, j) to (i + 1, j).
#
# Return any grid such that there are exactly k valid paths from the
# top-left cell to the bottom-right cell. If no such grid exists, return
# an empty array.
#
# Example 1:
#
# Input: m = 2, n = 3, k = 2
#
# Output: ["...","#.."]
#
# Explanation:
#
# There are exactly k = 2 valid paths from (0, 0) to (1, 2):
#
# (0, 0) → (0, 1) → (0, 2) → (1, 2)
#
# (0, 0) → (0, 1) → (1, 1) → (1, 2)
#
# Example 2:
#
# Input: m = 3, n = 3, k = 4
#
# Output: ["..#","...","#.."]
#
# Explanation:
#
# There are exactly k = 4 valid paths from (0, 0) to (2, 2):
#
# (0, 0) → (0, 1) → (1, 1) → (1, 2) → (2, 2)
#
# (0, 0) → (0, 1) → (1, 1) → (2, 1) → (2, 2)
#
# (0, 0) → (1, 0) → (1, 1) → (1, 2) → (2, 2)
#
# (0, 0) → (1, 0) → (1, 1) → (2, 1) → (2, 2)
#
# Example 3:
#
# Input: m = 1, n = 4, k = 2
#
# Output: []
#
# Explanation:​
#
# No grid exists with exactly k = 2 valid paths for a 1 x 4 grid, so the
# answer is an empty array.
#
# Constraints:
#
# 1 <= m, n <= 10
#
# 1 <= k <= 4
#

# @lc code=start
import math
from itertools import combinations


class Solution:
    def createGrid(self, m: int, n: int, k: int) -> list[str]:
        """
        Interview explanation:
        Build any m x n '.'/'#' grid with exactly k right/down paths from
        (0,0) to (m-1,n-1). With k <= 4 and m,n <= 10, use corridor/gadgets
        plus small brute force when needed.

        Algorithm:
        - Impossible if k > C(m+n-2, m-1), or if a 1-row/1-col grid and k != 1.
        - Try all-'.', a 2 x k gadget + corridor, a k x 2 gadget + corridor,
          a single corridor (k=1), then enumerate few obstacles / full masks
          on tiny grids.

        Complexity: polynomial in tiny constraints; O(1) for gadget cases.
        """
        if k > math.comb(m + n - 2, m - 1):
            return []
        if m == 1 or n == 1:
            return ["." * n] * m if k == 1 else []

        def count(g: list[list[str]]) -> int:
            dp = [[0] * n for _ in range(m)]
            dp[0][0] = 1
            for i in range(m):
                for j in range(n):
                    if g[i][j] == "#":
                        dp[i][j] = 0
                        continue
                    if i == 0 and j == 0:
                        continue
                    v = 0
                    if i:
                        v += dp[i - 1][j]
                    if j:
                        v += dp[i][j - 1]
                    dp[i][j] = v
            return dp[-1][-1]

        def fmt(g: list[list[str]]) -> list[str]:
            return ["".join(row) for row in g]

        g = [["."] * n for _ in range(m)]
        if count(g) == k:
            return fmt(g)

        if m >= 2 and n >= k:
            g = [["#"] * n for _ in range(m)]
            for j in range(k):
                g[0][j] = g[1][j] = "."
            for j in range(k, n):
                g[1][j] = "."
            for i in range(2, m):
                g[i][n - 1] = "."
            if count(g) == k:
                return fmt(g)

        if n >= 2 and m >= k:
            g = [["#"] * n for _ in range(m)]
            for i in range(k):
                g[i][0] = g[i][1] = "."
            for i in range(k, m):
                g[i][1] = "."
            for j in range(2, n):
                g[m - 1][j] = "."
            if count(g) == k:
                return fmt(g)

        if k == 1:
            g = [["#"] * n for _ in range(m)]
            for j in range(n):
                g[0][j] = "."
            for i in range(m):
                g[i][n - 1] = "."
            return fmt(g)

        cells = [
            (i, j)
            for i in range(m)
            for j in range(n)
            if (i, j) not in ((0, 0), (m - 1, n - 1))
        ]
        if len(cells) <= 16:
            for mask in range(1 << len(cells)):
                g = [["."] * n for _ in range(m)]
                for b, (i, j) in enumerate(cells):
                    if mask >> b & 1:
                        g[i][j] = "#"
                if count(g) == k:
                    return fmt(g)
            return []

        for num in range(1, 7):
            for obs in combinations(cells, num):
                g = [["."] * n for _ in range(m)]
                for i, j in obs:
                    g[i][j] = "#"
                if count(g) == k:
                    return fmt(g)
        return []
# @lc code=end
