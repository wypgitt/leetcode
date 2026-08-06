#
# @lc app=leetcode id=3208 lang=python3
#
# [3208] Alternating Groups II
#
# https://leetcode.com/problems/alternating-groups-ii/description/
#
# algorithms
# Medium (59.94%)
# Likes:    776
# Dislikes: 74
# Total Accepted:    162.4K
# Total Submissions: 270.9K
# Testcase Example:  "[0,1,0,1,0]\n3"
#
#
# There is a circle of red and blue tiles. You are given an array of
# integers colors and an integer k. The color of tile i is represented by
# colors[i]:
#
# colors[i] == 0 means that tile i is red.
#
# colors[i] == 1 means that tile i is blue.
#
# An alternating group is every k contiguous tiles in the circle with
# alternating colors (each tile in the group except the first and last one
# has a different color from its left and right tiles).
#
# Return the number of alternating groups.
#
# Note that since colors represents a circle, the first and the last tiles
# are considered to be next to each other.
#
# Example 1:
#
# Input: colors = [0,1,0,1,0], k = 3
#
# Output: 3
#
# Explanation:
#
# Alternating groups:
#
# Example 2:
#
# Input: colors = [0,1,0,0,1,0,1], k = 6
#
# Output: 2
#
# Explanation:
#
# Alternating groups:
#
# Example 3:
#
# Input: colors = [1,1,0,1], k = 4
#
# Output: 0
#
# Explanation:
#
# Constraints:
#
# 3 <= colors.length <= 10^5
#
# 0 <= colors[i] <= 1
#
# 3 <= k <= colors.length
#

# @lc code=start
from typing import List


class Solution:
    def numberOfAlternatingGroups(self, colors: List[int], k: int) -> int:
        """
        Interview explanation:
        Circular array; count windows of length k that are fully alternating
        (every adjacent pair differs).

        Algorithm:
        - Walk indices 1 .. n+k-2 on the circle, tracking the current streak of
          alternating adjacent colors.
        - Whenever streak >= k, the window ending at that index is valid.

        Complexity: O(n) time, O(1) space.
        """
        n = len(colors)
        ans = 0
        streak = 1
        for i in range(1, n + k - 1):
            if colors[i % n] != colors[(i - 1) % n]:
                streak += 1
            else:
                streak = 1
            if streak >= k:
                ans += 1
        return ans
# @lc code=end
