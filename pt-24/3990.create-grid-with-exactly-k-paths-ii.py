#
# @lc app=leetcode id=3990 lang=python3
#
# [3990] Create Grid With Exactly K Paths II
#
# https://leetcode.com/problems/create-grid-with-exactly-k-paths-ii/description/
#
# algorithms
# Hard (74.67%)
# Likes:    5
# Dislikes: 1
# Total Accepted:    168
# Total Submissions: 225
# Testcase Example:  "2"
#
#
# You are given an integer k.
#
# Construct any grid consisting only of the characters '.' and '#', where:
#
# '.' represents a free cell.
#
# '#' represents an obstacle cell.
#
# The grid must contain at most 25 rows and at most 25 columns.
#
# A valid path is a sequence of free cells that:
#
# Starts at the top-left cell (0, 0).
#
# Ends at the bottom-right cell (m - 1, n - 1), where m and n are the
# dimensions of your constructed grid.
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
# Input: k = 2
#
# Output: ["..#","#..","#.."]
#
# Explanation:
#
# The grid contains exactly 2 valid paths from (0, 0) to (2, 2):
#
# (0, 0) → (0, 1) → (1, 1) → (1, 2) → (2, 2)
#
# (0, 0) → (0, 1) → (1, 1) → (2, 1) → (2, 2)
#
# Example 2:
#
# Input: k = 3
#
# Output: ["...","#..","#.."]
#
# Explanation:
#
# ​​​​​​​
#
# The grid contains exactly 3 valid paths from (0, 0) to (2, 2):
#
# (0, 0) → (0, 1) → (0, 2) → (1, 2) → (2, 2)
#
# (0, 0) → (0, 1) → (1, 1) → (1, 2) → (2, 2)
#
# (0, 0) → (0, 1) → (1, 1) → (2, 1) → (2, 2)
#
# Constraints:​​​​​​​
#
# 1 <= k <= 1000
#

# @lc code=start
import math


class Solution:
    def createGrid(self, k: int) -> list[str]:
        """
        Interview explanation:
        Construct any '.'/'#' grid (<=25 x 25) with exactly k right/down paths.
        Prefer exact binomial empty grids or a k x 2 corridor; otherwise start
        from an empty grid with >= k paths and greedily add obstacles.

        Algorithm:
        - If k <= 25: return k rows of "..".
        - Else if some m,n have C(m+n-2, m-1) == k: return all '.'.
        - Else among empty grids with paths >= k, greedily place obstacles
          that reduce the path count without going below k.

        Complexity: fine under 25 x 25 construction limits.
        """
        def count(g: list[list[str]]) -> int:
            m, n = len(g), len(g[0])
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

        if k <= 25:
            return [".." for _ in range(k)]

        for m in range(1, 26):
            for n in range(1, 26):
                if math.comb(m + n - 2, min(m - 1, n - 1)) == k:
                    return ["." * n for _ in range(m)]

        def reduce_to(m: int, n: int, target: int):
            g = [["."] * n for _ in range(m)]
            cells = [
                (i, j)
                for i in range(m)
                for j in range(n)
                if (i, j) not in ((0, 0), (m - 1, n - 1))
            ]
            while True:
                cur = count(g)
                if cur == target:
                    return ["".join(row) for row in g]
                if cur < target:
                    return None
                best_move = None
                best_cp = cur
                for i, j in cells:
                    if g[i][j] == "#":
                        continue
                    g[i][j] = "#"
                    cp = count(g)
                    g[i][j] = "."
                    if target <= cp < best_cp:
                        best_cp = cp
                        best_move = (i, j)
                if not best_move:
                    return None
                g[best_move[0]][best_move[1]] = "#"

        cands = []
        for m in range(1, 26):
            for n in range(1, 26):
                p = math.comb(m + n - 2, min(m - 1, n - 1))
                if p >= k:
                    cands.append((p - k, m * n, m, n))
        cands.sort()
        for _, __, m, n in cands:
            ans = reduce_to(m, n, k)
            if ans:
                return ans
        return []
# @lc code=end
