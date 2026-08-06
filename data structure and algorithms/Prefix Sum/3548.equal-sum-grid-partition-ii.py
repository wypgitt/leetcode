#
# @lc app=leetcode id=3548 lang=python3
#
# [3548] Equal Sum Grid Partition II
#
# https://leetcode.com/problems/equal-sum-grid-partition-ii/description/
#
# algorithms
# Hard (39.47%)
# Likes:    340
# Dislikes: 75
# Total Accepted:    69.1K
# Total Submissions: 175K
# Testcase Example:  "[[1,4],[2,3]]"
#
#
# You are given an m x n matrix grid of positive integers. Your task is to
# determine if it is possible to make either one horizontal or one
# vertical cut on the grid such that:
#
# Each of the two resulting sections formed by the cut is non-empty.
#
# The sum of elements in both sections is equal, or can be made equal by
# discounting at most one single cell in total (from either section).
#
# If a cell is discounted, the rest of the section must remain connected.
#
# Return true if such a partition exists; otherwise, return false.
#
# Note: A section is connected if every cell in it can be reached from any
# other cell by moving up, down, left, or right through other cells in the
# section.
#
# Example 1:
#
# Input: grid = [[1,4],[2,3]]
#
# Output: true
#
# Explanation:
#
# A horizontal cut after the first row gives sums 1 + 4 = 5 and 2 + 3 = 5,
# which are equal. Thus, the answer is true.
#
# Example 2:
#
# Input: grid = [[1,2],[3,4]]
#
# Output: true
#
# Explanation:
#
# A vertical cut after the first column gives sums 1 + 3 = 4 and 2 + 4 =
# 6.
#
# By discounting 2 from the right section (6 - 2 = 4), both sections have
# equal sums and remain connected. Thus, the answer is true.
#
# Example 3:
#
# Input: grid = [[1,2,4],[2,3,5]]
#
# Output: false
#
# Explanation:
#
# A horizontal cut after the first row gives 1 + 2 + 4 = 7 and 2 + 3 + 5 =
# 10.
#
# By discounting 3 from the bottom section (10 - 3 = 7), both sections
# have equal sums, but they do not remain connected as it splits the
# bottom section into two parts ([2] and [5]). Thus, the answer is false.
#
# Example 4:
#
# Input: grid = [[4,1,8],[3,2,6]]
#
# Output: false
#
# Explanation:
#
# No valid cut exists, so the answer is false.
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
from collections import defaultdict
from typing import List


class Solution:
    def canPartitionGrid(self, grid: List[List[int]]) -> bool:
        """
        Interview explanation:
        Same one-cut idea as Partition I, but sums may be equalized by
        discounting one cell from the heavier side if that side stays connected.

        Algorithm:
        - Enumerate horizontal cuts while maintaining side sums and value counts.
        - Equal sums → true. Else if heavier side contains value = diff and
          removal keeps connectivity (2D rectangle, or endpoint of a 1-row /
          1-col strip), return true.
        - Transpose and repeat for vertical cuts.

        Complexity: O(m * n) time and space.
        """
        return self._check(grid) or self._check([list(row) for row in zip(*grid)])

    def _check(self, g: List[List[int]]) -> bool:
        m, n = len(g), len(g[0])
        s1 = s2 = 0
        cnt1: dict = defaultdict(int)
        cnt2: dict = defaultdict(int)
        for row in g:
            for x in row:
                s2 += x
                cnt2[x] += 1
        for i in range(m - 1):
            for x in g[i]:
                s1 += x
                s2 -= x
                cnt1[x] += 1
                cnt2[x] -= 1
            if s1 == s2:
                return True
            if s1 < s2:
                diff = s2 - s1
                if cnt2[diff]:
                    if (
                        (m - i - 1 > 1 and n > 1)
                        or (i == m - 2 and (g[i + 1][0] == diff or g[i + 1][-1] == diff))
                        or (n == 1 and (g[i + 1][0] == diff or g[-1][0] == diff))
                    ):
                        return True
            else:
                diff = s1 - s2
                if cnt1[diff]:
                    if (
                        (i + 1 > 1 and n > 1)
                        or (i == 0 and (g[0][0] == diff or g[0][-1] == diff))
                        or (n == 1 and (g[0][0] == diff or g[i][0] == diff))
                    ):
                        return True
        return False
# @lc code=end
