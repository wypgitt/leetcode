#
# @lc app=leetcode id=542 lang=python3
#
# [542] 01 Matrix
#
# https://leetcode.com/problems/01-matrix/description/
#
# algorithms
# Medium (54.63%)
# Likes:    10916
# Dislikes: 452
# Total Accepted:    959K
# Total Submissions: 1.8M
# Testcase Example:  "[[0,0,0],[0,1,0],[0,0,0]]"
#
# Given an m x n binary matrix mat, return the distance of the nearest 0 for
# each cell.
#
# The distance between two cells sharing a common edge is 1.
#
# Example 1:
#
# Input: mat = [[0,0,0],[0,1,0],[0,0,0]]
# Output: [[0,0,0],[0,1,0],[0,0,0]]
#
# Example 2:
#
# Input: mat = [[0,0,0],[0,1,0],[1,1,1]]
# Output: [[0,0,0],[0,1,0],[1,2,1]]
#
# Constraints:
#
# m == mat.length
#
# n == mat[i].length
#
# 1 <= m, n <= 10^4
#
# 1 <= m * n <= 10^4
#
# mat[i][j] is either 0 or 1.
#
# There is at least one 0 in mat.
#
# Note: This question is the same as 1765:
# https://leetcode.com/problems/map-of-highest-peak/
#

# @lc code=start
from collections import deque
from typing import List
class Solution:
    def updateMatrix(self, mat: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Multi-source BFS from all zeros: distance to nearest 0 is BFS level.
        Initialize queue with all 0 cells (dist 0); ones start as inf/unseen.

        Algorithm:
        - Enqueue all 0s; set 1s to a large sentinel.
        - BFS 4-direction; relax neighbor = cur + 1 when smaller.

        Complexity: O(m*n) time and space.
        """
        m, n = len(mat), len(mat[0])
        INF = m * n
        q = deque()
        for i in range(m):
            for j in range(n):
                if mat[i][j] == 0:
                    q.append((i, j))
                else:
                    mat[i][j] = INF
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        while q:
            i, j = q.popleft()
            for di, dj in dirs:
                ni, nj = i + di, j + dj
                if 0 <= ni < m and 0 <= nj < n and mat[ni][nj] > mat[i][j] + 1:
                    mat[ni][nj] = mat[i][j] + 1
                    q.append((ni, nj))
        return mat
# @lc code=end

