#
# @lc app=leetcode id=497 lang=python3
#
# [497] Random Point in Non-overlapping Rectangles
#
# https://leetcode.com/problems/random-point-in-non-overlapping-rectangles/description/
#
# algorithms
# Medium (40.34%)
# Likes:    530
# Dislikes: 692
# Total Accepted:    55.5K
# Total Submissions: 138K
# Testcase Example:  "[\"Solution\",\"pick\",\"pick\",\"pick\",\"pick\",\"pick\"]"
#
# You are given an array of non-overlapping axis-aligned rectangles rects where
# rects[i] = [a_i, b_i, x_i, y_i] indicates that (a_i, b_i) is the bottom-left
# corner point of the i^th rectangle and (x_i, y_i) is the top-right corner
# point of the i^th rectangle. Design an algorithm to pick a random integer
# point inside the space covered by one of the given rectangles. A point on the
# perimeter of a rectangle is included in the space covered by the rectangle.
#
# Any integer point inside the space covered by one of the given rectangles
# should be equally likely to be returned.
#
# Note that an integer point is a point that has integer coordinates.
#
# Implement the Solution class:
#
# Solution(int[][] rects) Initializes the object with the given rectangles
# rects.
#
# int[] pick() Returns a random integer point [u, v] inside the space covered
# by one of the given rectangles.
#
# Example 1:
#
# Input
# ["Solution", "pick", "pick", "pick", "pick", "pick"]
# [[[[-2, -2, 1, 1], [2, 2, 4, 6]]], [], [], [], [], []]
# Output
# [null, [1, -2], [1, -1], [-1, -2], [-2, -2], [0, 0]]
#
# Explanation
# Solution solution = new Solution([[-2, -2, 1, 1], [2, 2, 4, 6]]);
# solution.pick(); // return [1, -2]
# solution.pick(); // return [1, -1]
# solution.pick(); // return [-1, -2]
# solution.pick(); // return [-2, -2]
# solution.pick(); // return [0, 0]
#
# Constraints:
#
# 1 <= rects.length <= 100
#
# rects[i].length == 4
#
# -10^9 <= a_i < x_i <= 10^9
#
# -10^9 <= b_i < y_i <= 10^9
#
# x_i - a_i <= 2000
#
# y_i - b_i <= 2000
#
# All the rectangles do not overlap.
#
# At most 10^4 calls will be made to pick.
#

# @lc code=start
import bisect
import random
from typing import List


class Solution:
    def __init__(self, rects: List[List[int]]):
        """
        Interview explanation:
        Sample a rectangle proportional to its integer point count
        (width * height), then sample a uniform integer point inside it.
        Prefix sums of areas + binary search for weighted pick.

        Algorithm:
        - areas[i] = (x2-x1+1)*(y2-y1+1); prefix cumulative sums.
        - Store rects.

        Complexity: O(n) init, O(n) space.
        """
        self.rects = rects
        self.prefix = []
        total = 0
        for a, b, c, d in rects:
            total += (c - a + 1) * (d - b + 1)
            self.prefix.append(total)

    def pick(self) -> List[int]:
        """
        Interview explanation:
        Draw r in [1, total_points]; bisect prefix to choose rectangle; then
        uniform random x in [a,c], y in [b,d].

        Algorithm:
        - r = randint(1, prefix[-1]); i = bisect_left(prefix, r)
        - Return [randint(a,c), randint(b,d)] for rects[i].

        Complexity: O(log n) time, O(1) space.
        """
        r = random.randint(1, self.prefix[-1])
        i = bisect.bisect_left(self.prefix, r)
        a, b, c, d = self.rects[i]
        return [random.randint(a, c), random.randint(b, d)]


# Your Solution object will be instantiated and called as such:
# obj = Solution(rects)
# param_1 = obj.pick()
# @lc code=end
