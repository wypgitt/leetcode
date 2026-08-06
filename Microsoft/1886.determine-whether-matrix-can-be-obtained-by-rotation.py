#
# @lc app=leetcode id=1886 lang=python3
#
# [1886] Determine Whether Matrix Can Be Obtained By Rotation
#
# https://leetcode.com/problems/determine-whether-matrix-can-be-obtained-by-rotation/description/
#
# algorithms
# Easy (68.43%)
# Likes:    1866
# Dislikes: 174
# Total Accepted:    195K
# Total Submissions: 286K
# Testcase Example:  "[[0,1],[1,0]]"
#
# Given two n x n binary matrices mat and target, return true if it is possible
# to make mat equal to target by rotating mat in 90-degree increments, or false
# otherwise.
#
# Example 1:
#
# Input: mat = [[0,1],[1,0]], target = [[1,0],[0,1]]
# Output: true
# Explanation: We can rotate mat 90 degrees clockwise to make mat equal target.
#
# Example 2:
#
# Input: mat = [[0,1],[1,1]], target = [[1,0],[0,1]]
# Output: false
# Explanation: It is impossible to make mat equal to target by rotating mat.
#
# Example 3:
#
# Input: mat = [[0,0,0],[0,1,0],[1,1,1]], target = [[1,1,1],[0,1,0],[0,0,0]]
# Output: true
# Explanation: We can rotate mat 90 degrees clockwise two times to make mat
# equal target.
#
# Constraints:
#
# n == mat.length == target.length
#
# n == mat[i].length == target[i].length
#
# 1 <= n <= 10
#
# mat[i][j] and target[i][j] are either 0 or 1.
#

# @lc code=start
from typing import List


class Solution:
    def findRotation(self, mat: List[List[int]], target: List[List[int]]) -> bool:
        """
        Interview explanation:
        Check if mat equals target after 0/90/180/270° clockwise rotation.

        Algorithm:
        - For each of 4 rotations: rotate in-place or build; compare to target.

        Complexity: O(n^2) time/space.
        """
        def rotate(a: List[List[int]]) -> List[List[int]]:
            n = len(a)
            return [[a[n - 1 - j][i] for j in range(n)] for i in range(n)]

        for _ in range(4):
            if mat == target:
                return True
            mat = rotate(mat)
        return False

    def findRotation_index(self, mat: List[List[int]], target: List[List[int]]) -> bool:
        """
        Interview explanation:
        Alternate: for each rotation mapping (i,j)→..., compare without building
        full matrices repeatedly beyond checks.

        Algorithm:
        - Check 4 mappings: (i,j), (j,n-1-i), (n-1-i,n-1-j), (n-1-j,i).

        Complexity: O(n^2) time, O(1) extra.
        """
        n = len(mat)
        checks = [True, True, True, True]
        for i in range(n):
            for j in range(n):
                if mat[i][j] != target[i][j]:
                    checks[0] = False
                if mat[i][j] != target[j][n - 1 - i]:
                    checks[1] = False
                if mat[i][j] != target[n - 1 - i][n - 1 - j]:
                    checks[2] = False
                if mat[i][j] != target[n - 1 - j][i]:
                    checks[3] = False
        return any(checks)
# @lc code=end
