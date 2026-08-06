#
# @lc app=leetcode id=2267 lang=python3
#
# [2267]  Check if There Is a Valid Parentheses String Path
#
# https://leetcode.com/problems/check-if-there-is-a-valid-parentheses-string-path/description/
#
# algorithms
# Hard (40.57%)
# Likes:    546
# Dislikes: 9
# Total Accepted:    21.2K
# Total Submissions: 52.3K
# Testcase Example:  "[[\"(\",\"(\",\"(\"],[\")\",\"(\",\")\"],[\"(\",\"(\",\")\"],[\"(\",\"(\",\")\"]]"
#
# A parentheses string is a non-empty string consisting only of '(' and ')'. It
# is valid if any of the following conditions is true:
#
#
# It is ().
#
#
# It can be written as AB (A concatenated with B), where A and B are valid
# parentheses strings.
#
#
# It can be written as (A), where A is a valid parentheses string.
#
# You are given an m x n matrix of parentheses grid. A valid parentheses string
# path in the grid is a path satisfying all of the following conditions:
#
#
# The path starts from the upper left cell (0, 0).
#
#
# The path ends at the bottom-right cell (m - 1, n - 1).
#
#
# The path only ever moves down or right.
#
#
# The resulting parentheses string formed by the path is valid.
#
# Return true if there exists a valid parentheses string path in the grid.
# Otherwise, return false.
#
#
#
# Example 1:
#
# Input: grid = [["(","(","("],[")","(",")"],["(","(",")"],["(","(",")"]]
# Output: true
# Explanation: The above diagram shows two possible paths that form valid
# parentheses strings.
# The first path shown results in the valid parentheses string "()(())".
# The second path shown results in the valid parentheses string "((()))".
# Note that there may be other valid parentheses string paths.
#
# Example 2:
#
# Input: grid = [[")",")"],["(","("]]
# Output: false
# Explanation: The two possible paths form the parentheses strings "))(" and
# ")((". Since neither of them are valid parentheses strings, we return false.
#
#
#
# Constraints:
#
#
# m == grid.length
#
#
# n == grid[i].length
#
#
# 1 <= m, n <= 100
#
#
# grid[i][j] is either '(' or ')'.
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def hasValidPath(self, grid: List[List[str]]) -> bool:
        """
        Interview explanation:
        Path from (0,0) to (m-1,n-1) only right/down; parentheses balance never
        negative and ends at 0.

        Algorithm:
        - DFS+memo on (r,c,bal); prune impossible by remaining length.

        Complexity: O(m*n*min(m+n, mn)) time/space.
        """
        m, n = len(grid), len(grid[0])
        if (m + n - 1) % 2:
            return False

        @lru_cache(None)
        def dfs(r: int, c: int, bal: int) -> bool:
            if bal < 0 or bal > m + n - r - c:
                return False
            ch = grid[r][c]
            bal += 1 if ch == "(" else -1
            if bal < 0:
                return False
            if r == m - 1 and c == n - 1:
                return bal == 0
            if r + 1 < m and dfs(r + 1, c, bal):
                return True
            if c + 1 < n and dfs(r, c + 1, bal):
                return True
            return False

        return dfs(0, 0, 0)

# @lc code=end
