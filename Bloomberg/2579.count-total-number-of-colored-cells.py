#
# @lc app=leetcode id=2579 lang=python3
#
# [2579] Count Total Number of Colored Cells
#
# https://leetcode.com/problems/count-total-number-of-colored-cells/description/
#
# algorithms
# Medium (66.18%)
# Likes:    850
# Dislikes: 95
# Total Accepted:    209K
# Total Submissions: 315.9K
# Testcase Example:  "1"
#
# There exists an infinitely large two-dimensional grid of uncolored unit cells.
# You are given a positive integer n, indicating that you must do the following
# routine for n minutes:
#
#
# At the first minute, color any arbitrary unit cell blue.
#
#
# Every minute thereafter, color blue every uncolored cell that touches a blue
# cell.
#
# Below is a pictorial representation of the state of the grid after minutes 1,
# 2, and 3.
#
# Return the number of colored cells at the end of n minutes.
#
#
#
# Example 1:
#
# Input: n = 1
# Output: 1
# Explanation: After 1 minute, there is only 1 blue cell, so we return 1.
#
# Example 2:
#
# Input: n = 2
# Output: 5
# Explanation: After 2 minutes, there are 4 colored cells on the boundary and 1
# in the center, so we return 5.
#
#
#
# Constraints:
#
#
# 1 <= n <= 10^5
#

# @lc code=start
class Solution:
    def coloredCells(self, n: int) -> int:
        """
        Interview explanation:
        Starting from 1 cell, each minute add a diamond layer; total after n minutes.

        Algorithm:
        - Closed form: 1 + 4*(0+1+...+(n-1)) = 1 + 2*n*(n-1).

        Complexity: O(1) time and space.
        """
        return 1 + 2 * n * (n - 1)

    def coloredCells_math(self, n: int) -> int:
        """
        Interview explanation:
        Same closed-form diamond area formula.

        Algorithm:
        - n^2 + (n-1)^2.

        Complexity: O(1) time and space.
        """
        return n * n + (n - 1) * (n - 1)
# @lc code=end
