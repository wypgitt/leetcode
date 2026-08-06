#
# @lc app=leetcode id=2013 lang=python3
#
# [2013] Detect Squares
#
# https://leetcode.com/problems/detect-squares/description/
#
# algorithms
# Medium (52.84%)
# Likes:    1026
# Dislikes: 259
# Total Accepted:    113.9K
# Total Submissions: 215.5K
# Testcase Example:  "[\"DetectSquares\",\"add\",\"add\",\"add\",\"count\",\"count\",\"add\",\"count\"]\n[[],[[3,10]],[[11,2]],[[3,2]],[[11,10]],[[14,8]],[[11,2]],[[11,10]]]"
#
# You are given a stream of points on the X-Y plane. Design an algorithm that:
#
#
# Adds new points from the stream into a data structure. Duplicate points are
# allowed and should be treated as different points.
#
#
# Given a query point, counts the number of ways to choose three points from the
# data structure such that the three points and the query point form an
# axis-aligned square with positive area.
#
# An axis-aligned square is a square whose edges are all the same length and are
# either parallel or perpendicular to the x-axis and y-axis.
#
# Implement the DetectSquares class:
#
#
# DetectSquares() Initializes the object with an empty data structure.
#
#
# void add(int[] point) Adds a new point point = [x, y] to the data structure.
#
#
# int count(int[] point) Counts the number of ways to form axis-aligned squares
# with point point = [x, y] as described above.
#
#
#
# Example 1:
#
# Input
# ["DetectSquares", "add", "add", "add", "count", "count", "add", "count"]
# [[], [[3, 10]], [[11, 2]], [[3, 2]], [[11, 10]], [[14, 8]], [[11, 2]], [[11,
# 10]]]
# Output
# [null, null, null, null, 1, 0, null, 2]
#
# Explanation
# DetectSquares detectSquares = new DetectSquares();
# detectSquares.add([3, 10]);
# detectSquares.add([11, 2]);
# detectSquares.add([3, 2]);
# detectSquares.count([11, 10]); // return 1. You can choose:
#                                //   - The first, second, and third points
# detectSquares.count([14, 8]);  // return 0. The query point cannot form a
# square with any points in the data structure.
# detectSquares.add([11, 2]);    // Adding duplicate points is allowed.
# detectSquares.count([11, 10]); // return 2. You can choose:
#                                //   - The first, second, and third points
#                                //   - The first, third, and fourth points
#
#
#
# Constraints:
#
#
# point.length == 2
#
#
# 0 <= x, y <= 1000
#
#
# At most 3000 calls in total will be made to add and count.
#

# @lc code=start
from typing import List
from collections import defaultdict, Counter


class DetectSquares:

    def __init__(self):
        """
        Interview explanation:
        Store points on plane; support add and count axis-aligned squares with
        a query point as one corner.

        Algorithm:
        - Map x -> Counter of y frequencies.

        Complexity: O(1) init beyond maps.
        """
        self.pts = defaultdict(Counter)

    def add(self, point: List[int]) -> None:
        """
        Interview explanation:
        Insert a point (duplicates allowed / multiply count).

        Algorithm:
        - Increment frequency of y under x.

        Complexity: O(1).
        """
        x, y = point
        self.pts[x][y] += 1

    def count(self, point: List[int]) -> int:
        """
        Interview explanation:
        Count ways to form axis-aligned squares with point as a corner.

        Algorithm:
        - For each other y2 sharing x, side = y2-y; check (x+/-side, y) and
          (x+/-side, y2); sum products of counts.

        Complexity: O(k) for k y-values at same x; O(1) extra space.
        """
        x, y = point
        ans = 0
        for y2, c2 in self.pts[x].items():
            if y2 == y:
                continue
            d = y2 - y
            for x2 in (x + d, x - d):
                ans += c2 * self.pts[x2][y] * self.pts[x2][y2]
        return ans


# Your DetectSquares object will be instantiated and called as such:
# obj = DetectSquares()
# obj.add(point)
# param_2 = obj.count(point)
# @lc code=end
