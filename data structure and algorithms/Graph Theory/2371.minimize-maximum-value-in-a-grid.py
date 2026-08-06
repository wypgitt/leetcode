#
# @lc app=leetcode id=2371 lang=python3
#
# [2371] Minimize Maximum Value in a Grid
#
# https://leetcode.com/problems/minimize-maximum-value-in-a-grid/description/
#
# algorithms
# Hard (69.81%)
# Likes:    147
# Dislikes: 6
# Total Accepted:    7.6K
# Total Submissions: 10.9K
# Testcase Example:  "[[3,1],[2,5]]"
#
#
# You are given an m x n integer matrix grid containing distinct positive
# integers.
#
# You have to replace each integer in the matrix with a positive integer
# satisfying the following conditions:
#
# The relative order of every two elements that are in the same row or
# column should stay the same after the replacements.
#
# The maximum number in the matrix after the replacements should be as
# small as possible.
#
# The relative order stays the same if for all pairs of elements in the
# original matrix such that grid[r_1][c_1] > grid[r_2][c_2] where either
# r_1 == r_2 or c_1 == c_2, then it must be true that grid[r_1][c_1] >
# grid[r_2][c_2] after the replacements.
#
# For example, if grid = [[2, 4, 5], [7, 3, 9]] then a good replacement
# could be either grid = [[1, 2, 3], [2, 1, 4]] or grid = [[1, 2, 3], [3,
# 1, 4]].
#
# Return the resulting matrix. If there are multiple answers, return any
# of them.
#
# Example 1:
#
# Input: grid = [[3,1],[2,5]]
# Output: [[2,1],[1,2]]
# Explanation: The above diagram shows a valid replacement.
# The maximum number in the matrix is 2. It can be shown that no smaller
# value can be obtained.
#
# Example 2:
#
# Input: grid = [[10]]
# Output: [[1]]
# Explanation: We replace the only number in the matrix with 1.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 1000
#
# 1 <= m * n <= 10^5
#
# 1 <= grid[i][j] <= 10^9
#
# grid consists of distinct integers.
#
# @lc code=start

from typing import List


class Solution:
    def minScore(self, grid: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Premium: Replace distinct positives so row/col relative order preserved,
        minimize the maximum value in the resulting matrix.

        Algorithm:
        - Sort cells by value; assign each max(row_max[r], col_max[c]) + 1;
          update row/col maxima.

        Complexity: O(mn log(mn)) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        cells = [(grid[i][j], i, j) for i in range(m) for j in range(n)]
        cells.sort()
        row_max = [0] * m
        col_max = [0] * n
        ans = [[0] * n for _ in range(m)]
        for _, i, j in cells:
            ans[i][j] = max(row_max[i], col_max[j]) + 1
            row_max[i] = col_max[j] = ans[i][j]
        return ans
# @lc code=end
