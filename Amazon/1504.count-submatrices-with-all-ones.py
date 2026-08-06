#
# @lc app=leetcode id=1504 lang=python3
#
# [1504] Count Submatrices With All Ones
#
# https://leetcode.com/problems/count-submatrices-with-all-ones/description/
#
# algorithms
# Medium (71.0%)
# Likes:    2696
# Dislikes: 221
# Total Accepted:    151K
# Total Submissions: 212K
# Testcase Example:  "[[1,0,1],[1,1,0],[1,1,0]]"
#
# Given an m x n binary matrix mat, return the number of submatrices that have
# all ones.
#
# Example 1:
#
# Input: mat = [[1,0,1],[1,1,0],[1,1,0]]
# Output: 13
# Explanation:
# There are 6 rectangles of side 1x1.
# There are 2 rectangles of side 1x2.
# There are 3 rectangles of side 2x1.
# There is 1 rectangle of side 2x2.
# There is 1 rectangle of side 3x1.
# Total number of rectangles = 6 + 2 + 3 + 1 + 1 = 13.
#
# Example 2:
#
# Input: mat = [[0,1,1,0],[0,1,1,1],[1,1,1,0]]
# Output: 24
# Explanation:
# There are 8 rectangles of side 1x1.
# There are 5 rectangles of side 1x2.
# There are 2 rectangles of side 1x3.
# There are 4 rectangles of side 2x1.
# There are 2 rectangles of side 2x2.
# There are 2 rectangles of side 3x1.
# There is 1 rectangle of side 3x2.
# Total number of rectangles = 8 + 5 + 2 + 4 + 2 + 2 + 1 = 24.
#
# Constraints:
#
# 1 <= m, n <= 150
#
# mat[i][j] is either 0 or 1.
#

# @lc code=start
from typing import List


class Solution:
    def numSubmat(self, mat: List[List[int]]) -> int:
        """
        Interview explanation:
        Count all-1 submatrices. Treat each row as histogram bottom: height[j]
        = consecutive 1s above. For each right edge, scan left with min height.

        Algorithm:
        - For each row update heights; for j from 0..n-1 walk k=j..0 adding min_h.

        Complexity: O(m*n^2) time, O(n) space.
        """
        if not mat:
            return 0
        m, n = len(mat), len(mat[0])
        height = [0] * n
        ans = 0
        for i in range(m):
            for j in range(n):
                height[j] = height[j] + 1 if mat[i][j] else 0
            for j in range(n):
                min_h = height[j]
                for k in range(j, -1, -1):
                    min_h = min(min_h, height[k])
                    if min_h == 0:
                        break
                    ans += min_h
        return ans

    def numSubmat_stack(self, mat: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: histogram + monotonic stack — count submatrices ending at
        each column in amortized O(1) per bar.

        Algorithm:
        - Maintain increasing stack of (h, width); accumulate contribution cur.

        Complexity: O(m*n) time, O(n) space.
        """
        if not mat:
            return 0
        m, n = len(mat), len(mat[0])
        height = [0] * n
        ans = 0
        for i in range(m):
            for j in range(n):
                height[j] = height[j] + 1 if mat[i][j] else 0
            stack: list[tuple[int, int]] = []
            cur = 0
            for h in height:
                width = 1
                while stack and stack[-1][0] >= h:
                    prev_h, prev_w = stack.pop()
                    cur -= prev_h * prev_w
                    width += prev_w
                stack.append((h, width))
                cur += h * width
                ans += cur
        return ans
# @lc code=end
