#
# @lc app=leetcode id=1292 lang=python3
#
# [1292] Maximum Side Length of a Square with Sum Less than or Equal to Threshold
#
# https://leetcode.com/problems/maximum-side-length-of-a-square-with-sum-less-than-or-equal-to-threshold/description/
#
# algorithms
# Medium (65.44%)
# Likes:    1555
# Dislikes: 126
# Total Accepted:    128K
# Total Submissions: 195K
# Testcase Example:  "[[1,1,3,2,4,3,2],[1,1,3,2,4,3,2],[1,1,3,2,4,3,2]]"
#
# Given a m x n matrix mat and an integer threshold, return the maximum
# side-length of a square with a sum less than or equal to threshold or return
# 0 if there is no such square.
#
# Example 1:
#
# Input: mat = [[1,1,3,2,4,3,2],[1,1,3,2,4,3,2],[1,1,3,2,4,3,2]], threshold = 4
# Output: 2
# Explanation: The maximum side length of square with sum less than or equal to
# 4 is 2 as shown.
#
# Example 2:
#
# Input: mat = [[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2]],
# threshold = 1
# Output: 0
#
# Constraints:
#
# m == mat.length
#
# n == mat[i].length
#
# 1 <= m, n <= 300
#
# 0 <= mat[i][j] <= 10^4
#
# 0 <= threshold <= 10^5
#

# @lc code=start

from typing import List


class Solution:
    def maxSideLength(self, mat: List[List[int]], threshold: int) -> int:
        """
        Interview explanation:
        Max square side with sum <= threshold. 2D prefix sums + binary search
        on side length (or grow side while checking).

        Algorithm:
        - Build prefix[m+1][n+1].
        - Binary search side L in 0..min(m,n); check any square of side L
          via prefix sum <= threshold.

        Complexity: O(m*n log min(m,n)) time, O(m*n) space.
        """
        m, n = len(mat), len(mat[0])
        pref = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                pref[i][j] = (
                    mat[i - 1][j - 1]
                    + pref[i - 1][j]
                    + pref[i][j - 1]
                    - pref[i - 1][j - 1]
                )

        def square_sum(r2: int, c2: int, L: int) -> int:
            r1, c1 = r2 - L, c2 - L
            return pref[r2][c2] - pref[r1][c2] - pref[r2][c1] + pref[r1][c1]

        def ok(L: int) -> bool:
            if L == 0:
                return True
            for i in range(L, m + 1):
                for j in range(L, n + 1):
                    if square_sum(i, j, L) <= threshold:
                        return True
            return False

        lo, hi = 0, min(m, n)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if ok(mid):
                lo = mid
            else:
                hi = mid - 1
        return lo

    def maxSideLength_grow(self, mat: List[List[int]], threshold: int) -> int:
        """
        Interview explanation:
        Alternate: iterate cells as bottom-right; grow side while sum ok.

        Algorithm:
        - Prefix sums; for each cell try increasing L from previous best.

        Complexity: O(m*n*min(m,n)) time worst-case, often faster in practice.
        """
        m, n = len(mat), len(mat[0])
        pref = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                pref[i][j] = (
                    mat[i - 1][j - 1]
                    + pref[i - 1][j]
                    + pref[i][j - 1]
                    - pref[i - 1][j - 1]
                )
        ans = 0
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                L = ans + 1
                while i >= L and j >= L:
                    s = (
                        pref[i][j]
                        - pref[i - L][j]
                        - pref[i][j - L]
                        + pref[i - L][j - L]
                    )
                    if s <= threshold:
                        ans = L
                        L += 1
                    else:
                        break
        return ans
# @lc code=end
