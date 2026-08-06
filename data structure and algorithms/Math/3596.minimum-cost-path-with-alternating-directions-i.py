#
# @lc app=leetcode id=3596 lang=python3
#
# [3596] Minimum Cost Path with Alternating Directions I
#
# https://leetcode.com/problems/minimum-cost-path-with-alternating-directions-i/description/
#
# algorithms
# Medium (70.77%)
# Likes:    10
# Dislikes: 8
# Total Accepted:    523
# Total Submissions: 739
# Testcase Example:  "1\n1"
#
#
# You are given two integers m and n representing the number of rows and
# columns of a grid, respectively.
#
# The cost to enter cell (i, j) is defined as (i + 1) * (j + 1).
#
# The path will always begin by entering cell (0, 0) on move 1 and paying
# the entrance cost.
#
# At each step, you move to an adjacent cell, following an alternating
# pattern:
#
# On odd-numbered moves, you must move either right or down.
#
# On even-numbered moves, you must move either left or up.
#
# Return the minimum total cost required to reach (m - 1, n - 1). If it is
# impossible, return -1.
#
# Example 1:
#
# Input: m = 1, n = 1
#
# Output: 1
#
# Explanation:
#
# You start at cell (0, 0).
#
# The cost to enter (0, 0) is (0 + 1) * (0 + 1) = 1.
#
# Since you're at the destination, the total cost is 1.
#
# Example 2:
#
# Input: m = 2, n = 1
#
# Output: 3
#
# Explanation:
#
# You start at cell (0, 0) with cost (0 + 1) * (0 + 1) = 1.
#
# Move 1 (odd): You can move down to (1, 0) with cost (1 + 1) * (0 + 1) =
# 2.
#
# Thus, the total cost is 1 + 2 = 3.
#
# Constraints:
#
# 1 <= m, n <= 10^6
#

# @lc code=start

class Solution:
    def minCost(self, m: int, n: int) -> int:
        """
        Interview explanation:
        Odd moves only go right/down; even moves only left/up. Net progress is
        almost impossible — only 1×1 and the two length-2 corridors are reachable.

        Algorithm:
        - (1,1) → cost 1; (2,1) or (1,2) → cost 3; otherwise -1.

        Complexity: O(1) time, O(1) space.
        """
        if m == 1 and n == 1:
            return 1
        if (m == 2 and n == 1) or (m == 1 and n == 2):
            return 3
        return -1
# @lc code=end
