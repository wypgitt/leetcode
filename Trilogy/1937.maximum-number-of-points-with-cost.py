#
# @lc app=leetcode id=1937 lang=python3
#
# [1937] Maximum Number of Points with Cost
#
# https://leetcode.com/problems/maximum-number-of-points-with-cost/description/
#
# algorithms
# Medium (41.62%)
# Likes:    3285
# Dislikes: 243
# Total Accepted:    161K
# Total Submissions: 386K
# Testcase Example:  "[[1,2,3],[1,5,1],[3,1,1]]"
#
# You are given an m x n integer matrix points (0-indexed). Starting with 0
# points, you want to maximize the number of points you can get from the
# matrix.
#
# To gain points, you must pick one cell in each row. Picking the cell at
# coordinates (r, c) will add points[r][c] to your score.
#
# However, you will lose points if you pick a cell too far from the cell that
# you picked in the previous row. For every two adjacent rows r and r + 1
# (where 0 <= r < m - 1), picking cells at coordinates (r, c_1) and (r + 1,
# c_2) will subtract abs(c_1 - c_2) from your score.
#
# Return the maximum number of points you can achieve.
#
# abs(x) is defined as:
#
# x for x >= 0.
#
# -x for x < 0.
#
# Example 1:
#
# Input: points = [[1,2,3],[1,5,1],[3,1,1]]
# Output: 9
# Explanation:
# The blue cells denote the optimal cells to pick, which have coordinates (0,
# 2), (1, 1), and (2, 0).
# You add 3 + 5 + 3 = 11 to your score.
# However, you must subtract abs(2 - 1) + abs(1 - 0) = 2 from your score.
# Your final score is 11 - 2 = 9.
#
# Example 2:
#
# Input: points = [[1,5],[2,3],[4,2]]
# Output: 11
# Explanation:
# The blue cells denote the optimal cells to pick, which have coordinates (0,
# 1), (1, 1), and (2, 0).
# You add 5 + 3 + 4 = 12 to your score.
# However, you must subtract abs(1 - 1) + abs(1 - 0) = 1 from your score.
# Your final score is 12 - 1 = 11.
#
# Constraints:
#
# m == points.length
#
# n == points[r].length
#
# 1 <= m, n <= 10^5
#
# 1 <= m * n <= 10^5
#
# 0 <= points[r][c] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def maxPoints(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Pick one cell per row; score = sum values - |col diffs|. Naive DP O(m n^2);
        optimize transitions with left/right prefix maxima: left[j]=max(left[j-1],dp[j])+?
        Actually: left[j] = max(left[j-1]-1, dp[j]); right similarly.

        Algorithm:
        - dp = points[0]. For each next row: compute left/right envelopes from dp;
          ndp[j] = points[r][j] + max(left[j], right[j]).

        Complexity: O(m n) time, O(n) space.
        """
        m, n = len(points), len(points[0])
        dp = points[0][:]
        for r in range(1, m):
            left = [0] * n
            right = [0] * n
            left[0] = dp[0]
            for j in range(1, n):
                left[j] = max(left[j - 1] - 1, dp[j])
            right[-1] = dp[-1]
            for j in range(n - 2, -1, -1):
                right[j] = max(right[j + 1] - 1, dp[j])
            dp = [points[r][j] + max(left[j], right[j]) for j in range(n)]
        return max(dp)
# @lc code=end
