#
# @lc app=leetcode id=218 lang=python3
#
# [218] The Skyline Problem
#
# https://leetcode.com/problems/the-skyline-problem/description/
#
# algorithms
# Hard (45.72%)
# Likes:    6256
# Dislikes: 286
# Total Accepted:    362K
# Total Submissions: 793K
# Testcase Example:  "[[2,9,10],[3,7,15],[5,12,12],[15,20,10],[19,24,8]]"
#
# A city's skyline is the outer contour of the silhouette formed by all the
# buildings in that city when viewed from a distance. Given the locations and
# heights of all the buildings, return the skyline formed by these buildings
# collectively.
#
# The geometric information of each building is given in the array buildings
# where buildings[i] = [left_i, right_i, height_i]:
#
# left_i is the x coordinate of the left edge of the i^th building.
#
# right_i is the x coordinate of the right edge of the i^th building.
#
# height_i is the height of the i^th building.
#
# You may assume all buildings are perfect rectangles grounded on an absolutely
# flat surface at height 0.
#
# The skyline should be represented as a list of "key points" sorted by their
# x-coordinate in the form [[x_1,y_1],[x_2,y_2],...]. Each key point is the
# left endpoint of some horizontal segment in the skyline except the last point
# in the list, which always has a y-coordinate 0 and is used to mark the
# skyline's termination where the rightmost building ends. Any ground between
# the leftmost and rightmost buildings should be part of the skyline's contour.
#
# Note: There must be no consecutive horizontal lines of equal height in the
# output skyline. For instance, [...,[2 3],[4 5],[7 5],[11 5],[12 7],...] is
# not acceptable; the three lines of height 5 should be merged into one in the
# final output as such: [...,[2 3],[4 5],[12 7],...]
#
# Example 1:
#
# Input: buildings = [[2,9,10],[3,7,15],[5,12,12],[15,20,10],[19,24,8]]
# Output: [[2,10],[3,15],[7,12],[12,0],[15,10],[20,8],[24,0]]
# Explanation:
# Figure A shows the buildings of the input.
# Figure B shows the skyline formed by those buildings. The red points in
# figure B represent the key points in the output list.
#
# Example 2:
#
# Input: buildings = [[0,2,3],[2,5,3]]
# Output: [[0,3],[5,0]]
#
# Constraints:
#
# 1 <= buildings.length <= 10^4
#
# 0 <= left_i < right_i <= 2^31 - 1
#
# 1 <= height_i <= 2^31 - 1
#
# buildings is sorted by left_i in non-decreasing order.
#

# @lc code=start
import heapq
from typing import List, Tuple


class Solution:
    def getSkyline(self, buildings: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Sweep left-to-right over building edges. At each x, maintain active
        heights in a max-heap. A skyline key point appears when the current
        max height changes.

        Algorithm:
        - Create events: (L, -H, R) for starts, (R, 0, 0) for ends; sort.
        - Process events in order; push ( -H, R ) into heap on start.
        - Pop heap tops that end at/before current x.
        - If max height differs from last key point, append [x, height].

        Complexity: O(n log n) time, O(n) space.
        """
        events: List[Tuple[int, int, int]] = []
        for L, R, H in buildings:
            events.append((L, -H, R))
            events.append((R, 0, 0))
        events.sort()

        # live: (-height, end_x); sentinel height 0
        live: List[Tuple[int, int]] = [(0, float("inf"))]
        ans: List[List[int]] = []
        prev_h = 0

        for x, neg_h, R in events:
            if neg_h < 0:
                heapq.heappush(live, (neg_h, R))
            while live[0][1] <= x:
                heapq.heappop(live)
            cur_h = -live[0][0]
            if cur_h != prev_h:
                ans.append([x, cur_h])
                prev_h = cur_h
        return ans
# @lc code=end
