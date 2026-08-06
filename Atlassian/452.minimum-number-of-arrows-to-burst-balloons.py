#
# @lc app=leetcode id=452 lang=python3
#
# [452] Minimum Number of Arrows to Burst Balloons
#
# https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/description/
#
# algorithms
# Medium (61.77%)
# Likes:    8179
# Dislikes: 277
# Total Accepted:    822K
# Total Submissions: 1.3M
# Testcase Example:  "[[10,16],[2,8],[1,6],[7,12]]"
#
# There are some spherical balloons taped onto a flat wall that represents the
# XY-plane. The balloons are represented as a 2D integer array points where
# points[i] = [x_start, x_end] denotes a balloon whose horizontal diameter
# stretches between x_start and x_end. You do not know the exact y-coordinates
# of the balloons.
#
# Arrows can be shot up directly vertically (in the positive y-direction) from
# different points along the x-axis. A balloon with x_start and x_end is burst
# by an arrow shot at x if x_start <= x <= x_end. There is no limit to the
# number of arrows that can be shot. A shot arrow keeps traveling up
# infinitely, bursting any balloons in its path.
#
# Given the array points, return the minimum number of arrows that must be shot
# to burst all balloons.
#
# Example 1:
#
# Input: points = [[10,16],[2,8],[1,6],[7,12]]
# Output: 2
# Explanation: The balloons can be burst by 2 arrows:
# - Shoot an arrow at x = 6, bursting the balloons [2,8] and [1,6].
# - Shoot an arrow at x = 11, bursting the balloons [10,16] and [7,12].
#
# Example 2:
#
# Input: points = [[1,2],[3,4],[5,6],[7,8]]
# Output: 4
# Explanation: One arrow needs to be shot for each balloon for a total of 4
# arrows.
#
# Example 3:
#
# Input: points = [[1,2],[2,3],[3,4],[4,5]]
# Output: 2
# Explanation: The balloons can be burst by 2 arrows:
# - Shoot an arrow at x = 2, bursting the balloons [1,2] and [2,3].
# - Shoot an arrow at x = 4, bursting the balloons [3,4] and [4,5].
#
# Constraints:
#
# 1 <= points.length <= 10^5
#
# points[i].length == 2
#
# -2^31 <= x_start < x_end <= 2^31 - 1
#

# @lc code=start
from typing import List


class Solution:
    def findMinArrowShots(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Greedy by end points: one arrow at the earliest balloon end bursts
        all overlapping balloons that start ≤ that end. Sort by xend, shoot,
        skip until a balloon starts after the arrow.

        Algorithm:
        - Sort points by end ascending.
        - arrows = 0; cur_end = -inf.
        - For each [start, end]: if start > cur_end, shoot (arrows++),
          cur_end = end.

        Complexity: O(n log n) time, O(1)/O(n) space (sort).
        """
        if not points:
            return 0
        points.sort(key=lambda p: p[1])
        arrows = 0
        cur_end = float("-inf")
        for start, end in points:
            if start > cur_end:
                arrows += 1
                cur_end = end
        return arrows
# @lc code=end
