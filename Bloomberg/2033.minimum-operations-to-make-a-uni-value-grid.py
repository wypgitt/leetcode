#
# @lc app=leetcode id=2033 lang=python3
#
# [2033] Minimum Operations to Make a Uni-Value Grid
#
# https://leetcode.com/problems/minimum-operations-to-make-a-uni-value-grid/description/
#
# algorithms
# Medium (70.75%)
# Likes:    1266
# Dislikes: 79
# Total Accepted:    224.2K
# Total Submissions: 316.9K
# Testcase Example:  "[[2,4],[6,8]]\n2"
#
# You are given a 2D integer grid of size m x n and an integer x. In one
# operation, you can add x to or subtract x from any element in the grid.
#
# A uni-value grid is a grid where all the elements of it are equal.
#
# Return the minimum number of operations to make the grid uni-value. If it is
# not possible, return -1.
#
#
#
# Example 1:
#
# Input: grid = [[2,4],[6,8]], x = 2
# Output: 4
# Explanation: We can make every element equal to 4 by doing the following:
# - Add x to 2 once.
# - Subtract x from 6 once.
# - Subtract x from 8 twice.
# A total of 4 operations were used.
#
# Example 2:
#
# Input: grid = [[1,5],[2,3]], x = 1
# Output: 5
# Explanation: We can make every element equal to 3.
#
# Example 3:
#
# Input: grid = [[1,2],[3,4]], x = 2
# Output: -1
# Explanation: It is impossible to make every element equal.
#
#
#
# Constraints:
#
#
# m == grid.length
#
#
# n == grid[i].length
#
#
# 1 <= m, n <= 10^5
#
#
# 1 <= m * n <= 10^5
#
#
# 1 <= x, grid[i][j] <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def minOperations(self, grid: List[List[int]], x: int) -> int:
        """
        Interview explanation:
        Make all grid values equal by +/- x; return min ops or -1 if impossible.

        Algorithm:
        - All values must share same remainder mod x. Target = median; sum |v-t|/x.

        Complexity: O(mn log(mn)) time, O(mn) space.
        """
        vals = [v for row in grid for v in row]
        r = vals[0] % x
        if any(v % x != r for v in vals):
            return -1
        vals.sort()
        med = vals[len(vals) // 2]
        return sum(abs(v - med) // x for v in vals)
# @lc code=end
