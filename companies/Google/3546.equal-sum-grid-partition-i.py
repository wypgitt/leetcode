#
# @lc app=leetcode id=3546 lang=python3
#
# [3546] Equal Sum Grid Partition I
#
# https://leetcode.com/problems/equal-sum-grid-partition-i/description/
#
# algorithms
# Medium (52.92%)
# Likes:    401
# Dislikes: 18
# Total Accepted:    131.6K
# Total Submissions: 248.7K
# Testcase Example:  "[[1,4],[2,3]]"
#
#
# You are given an m x n matrix grid of positive integers. Your task is to
# determine if it is possible to make either one horizontal or one
# vertical cut on the grid such that:
#
# Each of the two resulting sections formed by the cut is non-empty.
#
# The sum of the elements in both sections is equal.
#
# Return true if such a partition exists; otherwise return false.
#
# Example 1:
#
# Input: grid = [[1,4],[2,3]]
#
# Output: true
#
# Explanation:
#
# A horizontal cut between row 0 and row 1 results in two non-empty
# sections, each with a sum of 5. Thus, the answer is true.
#
# Example 2:
#
# Input: grid = [[1,3],[2,4]]
#
# Output: false
#
# Explanation:
#
# No horizontal or vertical cut results in two non-empty sections with
# equal sums. Thus, the answer is false.
#
# Constraints:
#
# 1 <= m == grid.length <= 10^5
#
# 1 <= n == grid[i].length <= 10^5
#
# 2 <= m * n <= 10^5
#
# 1 <= grid[i][j] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def canPartitionGrid(self, grid: List[List[int]]) -> bool:
        """
        Interview explanation:
        One straight cut (horizontal or vertical) must split the grid into two
        non-empty parts with equal sums, so the total sum must be even and some
        proper prefix of rows/columns must sum to total/2.

        Algorithm:
        - Compute total; if odd, impossible.
        - Check row prefixes and column prefixes for sum == total // 2.

        Complexity: O(m * n) time, O(n) space.
        """
        m, n = len(grid), len(grid[0])
        total = sum(sum(row) for row in grid)
        if total % 2:
            return False
        half = total // 2

        s = 0
        for i in range(m - 1):
            s += sum(grid[i])
            if s == half:
                return True

        col_sums = [0] * n
        for row in grid:
            for j, x in enumerate(row):
                col_sums[j] += x
        s = 0
        for j in range(n - 1):
            s += col_sums[j]
            if s == half:
                return True
        return False
# @lc code=end
