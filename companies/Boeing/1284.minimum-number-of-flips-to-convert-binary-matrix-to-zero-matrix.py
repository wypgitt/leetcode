#
# @lc app=leetcode id=1284 lang=python3
#
# [1284] Minimum Number of Flips to Convert Binary Matrix to Zero Matrix
#
# https://leetcode.com/problems/minimum-number-of-flips-to-convert-binary-matrix-to-zero-matrix/description/
#
# algorithms
# Hard (72.94%)
# Likes:    1014
# Dislikes: 105
# Total Accepted:    41.0K
# Total Submissions: 56.2K
# Testcase Example:  "[[0,0],[0,1]]"
#
# Given a m x n binary matrix mat. In one step, you can choose one cell and
# flip it and all the four neighbors of it if they exist (Flip is changing 1 to
# 0 and 0 to 1). A pair of cells are called neighbors if they share one edge.
#
# Return the minimum number of steps required to convert mat to a zero matrix
# or -1 if you cannot.
#
# A binary matrix is a matrix with all cells equal to 0 or 1 only.
#
# A zero matrix is a matrix with all cells equal to 0.
#
# Example 1:
#
# Input: mat = [[0,0],[0,1]]
# Output: 3
# Explanation: One possible solution is to flip (1, 0) then (0, 1) and finally
# (1, 1) as shown.
#
# Example 2:
#
# Input: mat = [[0]]
# Output: 0
# Explanation: Given matrix is a zero matrix. We do not need to change it.
#
# Example 3:
#
# Input: mat = [[1,0,0],[1,0,0]]
# Output: -1
# Explanation: Given matrix cannot be a zero matrix.
#
# Constraints:
#
# m == mat.length
#
# n == mat[i].length
#
# 1 <= m, n <= 3
#
# mat[i][j] is either 0 or 1.
#

# @lc code=start

from typing import List
from collections import deque


class Solution:
    def minFlips(self, mat: List[List[int]]) -> int:
        """
        Interview explanation:
        Flip cell toggles itself and neighbors. m*n<=9 so BFS over 2^{mn}
        bitmasks. Encode matrix as bitmask; each flip XORs a precomputed mask.

        Algorithm:
        - Encode start; BFS from mask; for each cell position apply flip mask;
          return dist when reach 0; else -1.

        Complexity: O(mn * 2^{mn}) time/space.
        """
        m, n = len(mat), len(mat[0])
        start = 0
        for i in range(m):
            for j in range(n):
                if mat[i][j]:
                    start |= 1 << (i * n + j)

        flip_masks = []
        for i in range(m):
            for j in range(n):
                mask = 0
                for di, dj in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    ni, nj = i + di, j + dj
                    if 0 <= ni < m and 0 <= nj < n:
                        mask |= 1 << (ni * n + nj)
                flip_masks.append(mask)

        q = deque([(start, 0)])
        seen = {start}
        while q:
            state, dist = q.popleft()
            if state == 0:
                return dist
            for mask in flip_masks:
                nxt = state ^ mask
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, dist + 1))
        return -1
# @lc code=end
