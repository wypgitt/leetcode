#
# @lc app=leetcode id=1267 lang=python3
#
# [1267] Count Servers that Communicate
#
# https://leetcode.com/problems/count-servers-that-communicate/description/
#
# algorithms
# Medium (73.57%)
# Likes:    1928
# Dislikes: 109
# Total Accepted:    203K
# Total Submissions: 276K
# Testcase Example:  "[[1,0],[0,1]]"
#
# You are given a map of a server center, represented as a m * n integer matrix
# grid, where 1 means that on that cell there is a server and 0 means that it
# is no server. Two servers are said to communicate if they are on the same row
# or on the same column.
#
# Return the number of servers that communicate with any other server.
#
# Example 1:
#
# Input: grid = [[1,0],[0,1]]
# Output: 0
# Explanation: No servers can communicate with others.
#
# Example 2:
#
# Input: grid = [[1,0],[1,1]]
# Output: 3
# Explanation: All three servers can communicate with at least one other
# server.
#
# Example 3:
#
# Input: grid = [[1,1,0,0],[0,0,1,0],[0,0,1,0],[0,0,0,1]]
# Output: 4
# Explanation: The two servers in the first row can communicate with each
# other. The two servers in the third column can communicate with each other.
# The server at right bottom corner can't communicate with any other server.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m <= 250
#
# 1 <= n <= 250
#
# grid[i][j] == 0 or 1
#

# @lc code=start

from typing import List


class Solution:
    def countServers(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        A server communicates if another server shares its row or column.
        Count servers per row/col; a server counts if its row count>1 or col
        count>1.

        Algorithm:
        - row[i]=sum row; col[j]=sum col.
        - Count cells with grid==1 and (row[i]>1 or col[j]>1).

        Complexity: O(m*n) time, O(m+n) space.
        """
        m, n = len(grid), len(grid[0])
        row = [sum(grid[i][j] for j in range(n)) for i in range(m)]
        col = [sum(grid[i][j] for i in range(m)) for j in range(n)]
        ans = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j] and (row[i] > 1 or col[j] > 1):
                    ans += 1
        return ans
# @lc code=end
