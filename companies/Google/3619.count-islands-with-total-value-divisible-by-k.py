#
# @lc app=leetcode id=3619 lang=python3
#
# [3619] Count Islands With Total Value Divisible by K
#
# https://leetcode.com/problems/count-islands-with-total-value-divisible-by-k/description/
#
# algorithms
# Medium (56.15%)
# Likes:    74
# Dislikes: 2
# Total Accepted:    33.3K
# Total Submissions: 59.3K
# Testcase Example:  "[[0,2,1,0,0],[0,5,0,0,5],[0,0,1,0,0],[0,1,4,7,0],[0,2,0,0,8]]\n5"
#
#
# You are given an m x n matrix grid and a positive integer k. An island
# is a group of positive integers (representing land) that are
# 4-directionally connected (horizontally or vertically).
#
# The total value of an island is the sum of the values of all cells in
# the island.
#
# Return the number of islands with a total value divisible by k.
#
# Example 1:
#
# Input: grid =
# [[0,2,1,0,0],[0,5,0,0,5],[0,0,1,0,0],[0,1,4,7,0],[0,2,0,0,8]], k = 5
#
# Output: 2
#
# Explanation:
#
# The grid contains four islands. The islands highlighted in blue have a
# total value that is divisible by 5, while the islands highlighted in red
# do not.
#
# Example 2:
#
# Input: grid = [[3,0,3,0], [0,3,0,3], [3,0,3,0]], k = 3
#
# Output: 6
#
# Explanation:
#
# The grid contains six islands, each with a total value that is divisible
# by 3.
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
# 0 <= grid[i][j] <= 10^6
#
# 1 <= k <= 10^6
#

# @lc code=start

from collections import deque
from typing import List


class Solution:
    def countIslands(self, grid: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Sum values of each 4-connected island of positive cells; count those
        whose sum is divisible by k.

        Algorithm:
        - DFS flood-fill; accumulate island sum; check sum % k == 0.

        Complexity: O(m*n) time, O(m*n) space worst-case recursion/stack.
        """
        m, n = len(grid), len(grid[0])
        ans = 0

        def dfs(i: int, j: int) -> int:
            if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] == 0:
                return 0
            s = grid[i][j]
            grid[i][j] = 0
            s += dfs(i + 1, j)
            s += dfs(i - 1, j)
            s += dfs(i, j + 1)
            s += dfs(i, j - 1)
            return s

        for i in range(m):
            for j in range(n):
                if grid[i][j] > 0:
                    total = dfs(i, j)
                    if total % k == 0:
                        ans += 1
        return ans

    def countIslands_bfs(self, grid: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Alternate iterative BFS flood-fill for the same island sums.

        Algorithm:
        - Queue 4-directional expansion; test sum % k.

        Complexity: O(m*n) time, O(m*n) space.
        """
        m, n = len(grid), len(grid[0])
        ans = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j] == 0:
                    continue
                q = deque([(i, j)])
                total = grid[i][j]
                grid[i][j] = 0
                while q:
                    x, y = q.popleft()
                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] > 0:
                            total += grid[nx][ny]
                            grid[nx][ny] = 0
                            q.append((nx, ny))
                if total % k == 0:
                    ans += 1
        return ans
# @lc code=end
