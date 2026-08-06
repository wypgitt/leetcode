#
# @lc app=leetcode id=1465 lang=python3
#
# [1465] Maximum Area of a Piece of Cake After Horizontal and Vertical Cuts
#
# https://leetcode.com/problems/maximum-area-of-a-piece-of-cake-after-horizontal-and-vertical-cuts/description/
#
# algorithms
# Medium (41.51%)
# Likes:    2647
# Dislikes: 353
# Total Accepted:    178K
# Total Submissions: 429K
# Testcase Example:  "5"
#
# You are given a rectangular cake of size h x w and two arrays of integers
# horizontalCuts and verticalCuts where:
#
# horizontalCuts[i] is the distance from the top of the rectangular cake to the
# i^th horizontal cut and similarly, and
#
# verticalCuts[j] is the distance from the left of the rectangular cake to the
# j^th vertical cut.
#
# Return the maximum area of a piece of cake after you cut at each horizontal
# and vertical position provided in the arrays horizontalCuts and verticalCuts.
# Since the answer can be a large number, return this modulo 10^9 + 7.
#
# Example 1:
#
# Input: h = 5, w = 4, horizontalCuts = [1,2,4], verticalCuts = [1,3]
# Output: 4
# Explanation: The figure above represents the given rectangular cake. Red
# lines are the horizontal and vertical cuts. After you cut the cake, the green
# piece of cake has the maximum area.
#
# Example 2:
#
# Input: h = 5, w = 4, horizontalCuts = [3,1], verticalCuts = [1]
# Output: 6
# Explanation: The figure above represents the given rectangular cake. Red
# lines are the horizontal and vertical cuts. After you cut the cake, the green
# and yellow pieces of cake have the maximum area.
#
# Example 3:
#
# Input: h = 5, w = 4, horizontalCuts = [3], verticalCuts = [3]
# Output: 9
#
# Constraints:
#
# 2 <= h, w <= 10^9
#
# 1 <= horizontalCuts.length <= min(h - 1, 10^5)
#
# 1 <= verticalCuts.length <= min(w - 1, 10^5)
#
# 1 <= horizontalCuts[i] < h
#
# 1 <= verticalCuts[i] < w
#
# All the elements in horizontalCuts are distinct.
#
# All the elements in verticalCuts are distinct.
#

# @lc code=start
from typing import List


class Solution:
    def maxArea(
        self, h: int, w: int, horizontalCuts: List[int], verticalCuts: List[int]
    ) -> int:
        """
        Interview explanation:
        Cake cuts into a grid; max piece area = max horizontal gap * max
        vertical gap (gaps include borders 0 and h/w).

        Algorithm:
        - Sort cuts; scan consecutive diffs (with 0 and h/w); multiply max gaps mod 1e9+7.

        Complexity: O(H log H + V log V) time, O(1) extra.
        """
        MOD = 10**9 + 7
        hs = sorted(horizontalCuts)
        vs = sorted(verticalCuts)

        def max_gap(cuts, end):
            prev = 0
            best = 0
            for c in cuts:
                best = max(best, c - prev)
                prev = c
            return max(best, end - prev)

        return (max_gap(hs, h) * max_gap(vs, w)) % MOD
# @lc code=end
