#
# @lc app=leetcode id=3567 lang=python3
#
# [3567] Minimum Absolute Difference in Sliding Submatrix
#
# https://leetcode.com/problems/minimum-absolute-difference-in-sliding-submatrix/description/
#
# algorithms
# Medium (78.78%)
# Likes:    308
# Dislikes: 43
# Total Accepted:    95.9K
# Total Submissions: 121.7K
# Testcase Example:  "[[1,8],[3,-2]]\n2"
#
#
# You are given an m x n integer matrix grid and an integer k.
#
# For every contiguous k x k submatrix of grid, compute the minimum
# absolute difference between any two distinct values within that
# submatrix.
#
# Return a 2D array ans of size (m - k + 1) x (n - k + 1), where ans[i][j]
# is the minimum absolute difference in the submatrix whose top-left
# corner is (i, j) in grid.
#
# Note: If all elements in the submatrix have the same value, the answer
# will be 0.
#
# A submatrix (x1, y1, x2, y2) is a matrix that is formed by choosing all
# cells matrix[x][y] where x1 <= x <= x2 and y1 <= y <= y2.
#
# Example 1:
#
# Input: grid = [[1,8],[3,-2]], k = 2
#
# Output: [[2]]
#
# Explanation:
#
# There is only one possible k x k submatrix: [[1, 8], [3, -2]].
#
# Distinct values in the submatrix are [1, 8, 3, -2].
#
# The minimum absolute difference in the submatrix is |1 - 3| = 2. Thus,
# the answer is [[2]].
#
# Example 2:
#
# Input: grid = [[3,-1]], k = 1
#
# Output: [[0,0]]
#
# Explanation:
#
# Both k x k submatrix has only one distinct element.
#
# Thus, the answer is [[0, 0]].
#
# Example 3:
#
# Input: grid = [[1,-2,3],[2,3,5]], k = 2
#
# Output: [[1,2]]
#
# Explanation:
#
# There are two possible k × k submatrix:
#
# Starting at (0, 0): [[1, -2], [2, 3]].
#
# Distinct values in the submatrix are [1, -2, 2, 3].
#
# The minimum absolute difference in the submatrix is |1 - 2| = 1.
#
# Starting at (0, 1): [[-2, 3], [3, 5]].
#
# Distinct values in the submatrix are [-2, 3, 5].
#
# The minimum absolute difference in the submatrix is |3 - 5| = 2.
#
# Thus, the answer is [[1, 2]].
#
# Constraints:
#
# 1 <= m == grid.length <= 30
#
# 1 <= n == grid[i].length <= 30
#
# -10^5 <= grid[i][j] <= 10^5
#
# 1 <= k <= min(m, n)
#

# @lc code=start

from typing import List


class Solution:
    def minAbsDiff(self, grid: List[List[int]], k: int) -> List[List[int]]:
        """
        Interview explanation:
        For every k×k window, the min absolute difference of distinct values is
        the min gap between consecutive values after sorting the unique set.
        Same-valued windows answer 0.

        Algorithm:
        - Enumerate top-left (i, j); collect/sort unique entries in the window.
        - If one unique value → 0; else min adjacent gap in the sorted uniques.

        Complexity: O((m-k+1)(n-k+1) k^2 log k) time, O(k^2) space per window.
        """
        m, n = len(grid), len(grid[0])
        ans = [[0] * (n - k + 1) for _ in range(m - k + 1)]
        for i in range(m - k + 1):
            for j in range(n - k + 1):
                vals = sorted({
                    grid[x][y]
                    for x in range(i, i + k)
                    for y in range(j, j + k)
                })
                if len(vals) == 1:
                    ans[i][j] = 0
                else:
                    ans[i][j] = min(vals[t + 1] - vals[t] for t in range(len(vals) - 1))
        return ans
# @lc code=end
