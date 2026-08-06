#
# @lc app=leetcode id=3206 lang=python3
#
# [3206] Alternating Groups I
#
# https://leetcode.com/problems/alternating-groups-i/description/
#
# algorithms
# Easy (69.39%)
# Likes:    175
# Dislikes: 10
# Total Accepted:    77.4K
# Total Submissions: 111.5K
# Testcase Example:  "[1,1,1]"
#
#
# There is a circle of red and blue tiles. You are given an array of
# integers colors. The color of tile i is represented by colors[i]:
#
# colors[i] == 0 means that tile i is red.
#
# colors[i] == 1 means that tile i is blue.
#
# Every 3 contiguous tiles in the circle with alternating colors (the
# middle tile has a different color from its left and right tiles) is
# called an alternating group.
#
# Return the number of alternating groups.
#
# Note that since colors represents a circle, the first and the last tiles
# are considered to be next to each other.
#
# Example 1:
#
# Input: colors = [1,1,1]
#
# Output: 0
#
# Explanation:
#
# Example 2:
#
# Input: colors = [0,1,0,0,1]
#
# Output: 3
#
# Explanation:
#
# Alternating groups:
#
# Constraints:
#
# 3 <= colors.length <= 100
#
# 0 <= colors[i] <= 1
#

# @lc code=start
from typing import List


class Solution:
    def numberOfAlternatingGroups(self, colors: List[int]) -> int:
        """
        Interview explanation:
        Circular tiles; count length-3 windows where the middle color differs
        from both neighbors (strictly alternating triple).

        Algorithm:
        - For each i, check colors[i] != colors[(i+1)%n] != colors[(i+2)%n]
          with middle different from both sides.

        Complexity: O(n) time, O(1) space.
        """
        n = len(colors)
        ans = 0
        for i in range(n):
            a, b, c = colors[i], colors[(i + 1) % n], colors[(i + 2) % n]
            if a != b and b != c:
                ans += 1
        return ans
# @lc code=end
