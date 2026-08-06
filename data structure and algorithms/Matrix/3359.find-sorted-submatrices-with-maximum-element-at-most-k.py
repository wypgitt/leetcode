#
# @lc app=leetcode id=3359 lang=python3
#
# [3359] Find Sorted Submatrices With Maximum Element at Most K
#
# https://leetcode.com/problems/find-sorted-submatrices-with-maximum-element-at-most-k/description/
#
# algorithms
# Hard (51.65%)
# Likes:    7
# Dislikes: 3
# Total Accepted:    470
# Total Submissions: 910
# Testcase Example:  "[[4,3,2,1],[8,7,6,1]]\n3"
#
#
# You are given a 2D matrix grid of size m x n. You are also given a
# non-negative integer k.
#
# Return the number of submatrices of grid that satisfy the following
# conditions:
#
# The maximum element in the submatrix less than or equal to k.
#
# Each row in the submatrix is sorted in non-increasing order.
#
# A submatrix (x1, y1, x2, y2) is a matrix that forms by choosing all
# cells grid[x][y] where x1 <= x <= x2 and y1 <= y <= y2.
#
# Example 1:
#
# Input: grid = [[4,3,2,1],[8,7,6,1]], k = 3
#
# Output: 8
#
# Explanation:
#
# The 8 submatrices are:
#
# [[1]]
#
# [[1]]
#
# [[2,1]]
#
# [[3,2,1]]
#
# [[1],[1]]
#
# [[2]]
#
# [[3]]
#
# [[3,2]]
#
# Example 2:
#
# Input: grid = [[1,1,1],[1,1,1],[1,1,1]], k = 1
#
# Output: 36
#
# Explanation:
#
# There are 36 submatrices of grid. All submatrices have their maximum
# element equal to 1.
#
# Example 3:
#
# Input: grid = [[1]], k = 1
#
# Output: 1
#
# Constraints:
#
# 1 <= m == grid.length <= 10^3
#
# 1 <= n == grid[i].length <= 10^3
#
# 1 <= grid[i][j] <= 10^9
#
# 1 <= k <= 10^9
#
# ​​​​​​
#

# @lc code=start

from typing import List


class Solution:
    def countSubmatrices(self, grid: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Count submatrices with max ≤ k and every row non-increasing. Treat each
        column as a right edge: heights[i] = longest valid non-increasing suffix
        ending at (i,j) with values ≤ k. Count histogram submatrices via mono stack.

        Algorithm:
        - Sweep columns right→left updating heights.
        - For each heights array, stack DP: dp[i] = submatrices ending at row i.

        Complexity: O(m*n) time, O(m) space.
        """
        m, n = len(grid), len(grid[0])
        heights = [0] * m
        ans = 0

        def count(h: List[int]) -> int:
            dp = [0] * len(h)
            stk: List[int] = []
            res = 0
            for i, val in enumerate(h):
                while stk and h[stk[-1]] >= val:
                    stk.pop()
                if stk:
                    dp[i] = dp[stk[-1]] + val * (i - stk[-1])
                else:
                    dp[i] = val * (i + 1)
                stk.append(i)
                res += dp[i]
            return res

        for j in range(n - 1, -1, -1):
            for i in range(m):
                if grid[i][j] > k:
                    heights[i] = 0
                elif j + 1 < n and grid[i][j] >= grid[i][j + 1]:
                    heights[i] += 1
                else:
                    heights[i] = 1
            ans += count(heights)
        return ans
# @lc code=end
