#
# @lc app=leetcode id=1267 lang=python3
#
# [1267] Count Servers that Communicate
#
# https://leetcode.com/problems/count-servers-that-communicate/description/
#
# algorithms
# Medium (73.52%)
# Likes:    1917
# Dislikes: 109
# Total Accepted:    200.8K
# Total Submissions: 273.1K
# Testcase Example:  '[[1,0],[0,1]]'
#
# You are given a map of a server center, represented as a m * n integer matrix
# grid, where 1 means that on that cell there is a server and 0 means that it
# is no server. Two servers are said to communicate if they are on the same row
# or on the same column.
# 
# Return the number of servers that communicate with any other server.
# 
# 
# Example 1:
# 
# 
# 
# 
# Input: grid = [[1,0],[0,1]]
# Output: 0
# Explanation: No servers can communicate with others.
# 
# Example 2:
# 
# 
# 
# 
# Input: grid = [[1,0],[1,1]]
# Output: 3
# Explanation: All three servers can communicate with at least one other
# server.
# 
# 
# Example 3:
# 
# 
# 
# 
# Input: grid = [[1,1,0,0],[0,0,1,0],[0,0,1,0],[0,0,0,1]]
# Output: 4
# Explanation: The two servers in the first row can communicate with each
# other. The two servers in the third column can communicate with each other.
# The server at right bottom corner can't communicate with any other
# server.
# 
# 
# 
# Constraints:
# 
# 
# m == grid.length
# n == grid[i].length
# 1 <= m <= 250
# 1 <= n <= 250
# grid[i][j] == 0 or 1
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def countServers(self, grid: List[List[int]]) -> int:
        rows = [sum(row) for row in grid]
        cols = [sum(grid[r][c] for r in range(len(grid))) for c in range(len(grid[0]))]

        total = 0
        for r, row in enumerate(grid):
            for c, has_server in enumerate(row):
                if has_server and (rows[r] > 1 or cols[c] > 1):
                    total += 1

        return total
# @lc code=end

# Explanation
# -----------
# A server communicates if another server exists in the same row or same
# column. Precompute row counts and column counts, then count each server whose
# row count or column count is greater than one.
#
# Row and column count arrays are the right data structure because they turn
# each cell's communication test into O(1).
#
# Edge cases: a single isolated server is not counted; two servers sharing a
# row both count; an all-zero grid returns 0.
#
# Time complexity: O(mn).
# Space complexity: O(m + n).
