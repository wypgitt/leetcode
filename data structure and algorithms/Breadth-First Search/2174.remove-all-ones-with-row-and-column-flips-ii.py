#
# @lc app=leetcode id=2174 lang=python3
#
# [2174] Remove All Ones With Row and Column Flips II
#
# https://leetcode.com/problems/remove-all-ones-with-row-and-column-flips-ii/description/
#
# algorithms
# Medium (67.40%)
# Likes:    94
# Dislikes: 24
# Total Accepted:    5.8K
# Total Submissions: 8.6K
# Testcase Example:  "[[1,1,1],[1,1,1],[0,1,0]]"
#
#
# You are given a 0-indexed m x n binary matrix grid.
#
# In one operation, you can choose any i and j that meet the following
# conditions:
#
# 0 <= i < m
#
# 0 <= j < n
#
# grid[i][j] == 1
#
# and change the values of all cells in row i and column j to zero.
#
# Return the minimum number of operations needed to remove all 1's from
# grid.
#
# Example 1:
#
# Input: grid = [[1,1,1],[1,1,1],[0,1,0]]
# Output: 2
# Explanation:
# In the first operation, change all cell values of row 1 and column 1 to
# zero.
# In the second operation, change all cell values of row 0 and column 0 to
# zero.
#
# Example 2:
#
# Input: grid = [[0,1,0],[1,0,1],[0,1,0]]
# Output: 2
# Explanation:
# In the first operation, change all cell values of row 1 and column 0 to
# zero.
# In the second operation, change all cell values of row 2 and column 1 to
# zero.
# Note that we cannot perform an operation using row 1 and column 1
# because grid[1][1] != 1.
#
# Example 3:
#
# Input: grid = [[0,0],[0,0]]
# Output: 0
# Explanation:
# There are no 1's to remove so return 0.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 15
#
# 1 <= m * n <= 15
#
# grid[i][j] is either 0 or 1.
#
# @lc code=start
from typing import List
from collections import deque


class Solution:
    def removeOnes(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium. Binary grid; operation: pick a cell that is 1 and set its entire
        row and column to 0. Minimize operations to clear all ones. m*n <= 15.

        Algorithm:
        (BFS on bitmasks)
        - Encode grid as bitmask; from each state, for every originally-1 cell
          (or every current-1), apply row+col clear; BFS shortest path to 0.

        Complexity: O(2^{mn} * mn * (m+n)) time, O(2^{mn}) space.
        """
        m, n = len(grid), len(grid[0])
        state = 0
        ones = []
        for i in range(m):
            for j in range(n):
                if grid[i][j]:
                    state |= 1 << (i * n + j)
                    ones.append((i, j))
        if state == 0:
            return 0
        q = deque([state])
        vis = {state}
        ans = 0
        while q:
            for _ in range(len(q)):
                cur = q.popleft()
                if cur == 0:
                    return ans
                for i, j in ones:
                    if ((cur >> (i * n + j)) & 1) == 0:
                        continue
                    nxt = cur
                    for r in range(m):
                        nxt &= ~(1 << (r * n + j))
                    for c in range(n):
                        nxt &= ~(1 << (i * n + c))
                    if nxt not in vis:
                        vis.add(nxt)
                        q.append(nxt)
            ans += 1
        return -1

    def removeOnes_dfs(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: DFS/memo on mask; try operating on each remaining 1.

        Algorithm:
        - Memoized recursion minimizing 1 + dfs(after flip).

        Complexity: Same order as BFS.
        """
        from functools import cache

        m, n = len(grid), len(grid[0])
        start = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j]:
                    start |= 1 << (i * n + j)

        @cache
        def dfs(mask: int) -> int:
            if mask == 0:
                return 0
            best = m * n
            for i in range(m):
                for j in range(n):
                    if (mask >> (i * n + j)) & 1:
                        nxt = mask
                        for r in range(m):
                            nxt &= ~(1 << (r * n + j))
                        for c in range(n):
                            nxt &= ~(1 << (i * n + c))
                        best = min(best, 1 + dfs(nxt))
            return best

        return dfs(start)
# @lc code=end
