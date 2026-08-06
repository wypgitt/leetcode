#
# @lc app=leetcode id=3529 lang=python3
#
# [3529] Count Cells in Overlapping Horizontal and Vertical Substrings
#
# https://leetcode.com/problems/count-cells-in-overlapping-horizontal-and-vertical-substrings/description/
#
# algorithms
# Medium (27.19%)
# Likes:    65
# Dislikes: 15
# Total Accepted:    7.9K
# Total Submissions: 29K
# Testcase Example:  "[[\"a\",\"a\",\"c\",\"c\"],[\"b\",\"b\",\"b\",\"c\"],[\"a\",\"a\",\"b\",\"a\"],[\"c\",\"a\",\"a\",\"c\"],[\"a\",\"a\",\"b\",\"a\"]]\n\"abaca\""
#
#
# You are given an m x n matrix grid consisting of characters and a string
# pattern.
#
# A horizontal substring is a contiguous sequence of characters read from
# left to right. If the end of a row is reached before the substring is
# complete, it wraps to the first column of the next row and continues as
# needed. You do not wrap from the bottom row back to the top.
#
# A vertical substring is a contiguous sequence of characters read from
# top to bottom. If the bottom of a column is reached before the substring
# is complete, it wraps to the first row of the next column and continues
# as needed. You do not wrap from the last column back to the first.
#
# Count the number of cells in the matrix that satisfy the following
# condition:
#
# The cell must be part of at least one horizontal substring and at least
# one vertical substring, where both substrings are equal to the given
# pattern.
#
# Return the count of these cells.
#
# Example 1:
#
# Input: grid =
# [["a","a","c","c"],["b","b","b","c"],["a","a","b","a"],["c","a","a","c"],["a","a","b","a"]],
# pattern = "abaca"
#
# Output: 1
#
# Explanation:
#
# The pattern "abaca" appears once as a horizontal substring (colored
# blue) and once as a vertical substring (colored red), intersecting at
# one cell (colored purple).
#
# Example 2:
#
# Input: grid =
# [["c","a","a","a"],["a","a","b","a"],["b","b","a","a"],["a","a","b","a"]],
# pattern = "aba"
#
# Output: 4
#
# Explanation:
#
# The cells colored above are all part of at least one horizontal and one
# vertical substring matching the pattern "aba".
#
# Example 3:
#
# Input: grid = [["a"]], pattern = "a"
#
# Output: 1
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 1000
#
# 1 <= m * n <= 10^5
#
# 1 <= pattern.length <= m * n
#
# grid and pattern consist of only lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def countCells(self, grid: List[List[str]], pattern: str) -> int:
        """
        Interview explanation:
        Flatten the grid into a row-major string and a column-major string; mark
        every cell covered by a pattern match in each flattening; count cells
        covered in both.

        Algorithm:
        - KMP find all occurrences in each flattened string.
        - Difference array mark match intervals, map indices back to (r, c).
        - Count cells with both horizontal and vertical coverage.

        Complexity: O(m*n + |pattern|) time, O(m*n) space.
        """
        m, n = len(grid), len(grid[0])
        p = pattern
        plen = len(p)

        def kmp_lps(s: str) -> List[int]:
            lps = [0] * len(s)
            length = 0
            i = 1
            while i < len(s):
                if s[i] == s[length]:
                    length += 1
                    lps[i] = length
                    i += 1
                elif length:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
            return lps

        def mark(flat: str, horizontal: bool) -> List[List[bool]]:
            N = len(flat)
            diff = [0] * (N + 1)
            lps = kmp_lps(p)
            i = j = 0
            while i < N:
                if flat[i] == p[j]:
                    i += 1
                    j += 1
                    if j == plen:
                        start = i - plen
                        diff[start] += 1
                        diff[i] -= 1
                        j = lps[j - 1]
                elif j:
                    j = lps[j - 1]
                else:
                    i += 1
            covered = [[False] * n for _ in range(m)]
            cur = 0
            for k in range(N):
                cur += diff[k]
                if cur > 0:
                    if horizontal:
                        r, c = divmod(k, n)
                    else:
                        c, r = divmod(k, m)  # k = c * m + r
                    covered[r][c] = True
            return covered

        row_flat = "".join("".join(row) for row in grid)
        col_flat = "".join(grid[i][j] for j in range(n) for i in range(m))
        h = mark(row_flat, True)
        v = mark(col_flat, False)
        return sum(1 for i in range(m) for j in range(n) if h[i][j] and v[i][j])
# @lc code=end
