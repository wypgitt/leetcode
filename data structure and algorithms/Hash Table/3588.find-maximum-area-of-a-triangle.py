#
# @lc app=leetcode id=3588 lang=python3
#
# [3588] Find Maximum Area of a Triangle
#
# https://leetcode.com/problems/find-maximum-area-of-a-triangle/description/
#
# algorithms
# Medium (29.84%)
# Likes:    54
# Dislikes: 13
# Total Accepted:    12.6K
# Total Submissions: 42.2K
# Testcase Example:  "[[1,1],[1,2],[3,2],[3,3]]"
#
#
# You are given a 2D array coords of size n x 2, representing the
# coordinates of n points in an infinite Cartesian plane.
#
# Find twice the maximum area of a triangle with its corners at any three
# elements from coords, such that at least one side of this triangle is
# parallel to the x-axis or y-axis. Formally, if the maximum area of such
# a triangle is A, return 2 * A.
#
# If no such triangle exists, return -1.
#
# Note that a triangle cannot have zero area.
#
# Example 1:
#
# Input: coords = [[1,1],[1,2],[3,2],[3,3]]
#
# Output: 2
#
# Explanation:
#
# The triangle shown in the image has a base 1 and height 2. Hence its
# area is 1/2 * base * height = 1.
#
# Example 2:
#
# Input: coords = [[1,1],[2,2],[3,3]]
#
# Output: -1
#
# Explanation:
#
# The only possible triangle has corners (1, 1), (2, 2), and (3, 3). None
# of its sides are parallel to the x-axis or the y-axis.
#
# Constraints:
#
# 1 <= n == coords.length <= 10^5
#
# 1 <= coords[i][0], coords[i][1] <= 10^6
#
# All coords[i] are unique.
#

# @lc code=start

from collections import defaultdict
from typing import List


class Solution:
    def maxArea(self, coords: List[List[int]]) -> int:
        """
        Interview explanation:
        Need a triangle with a side // axes. Base = vertical (same x) or
        horizontal (same y); height uses the farthest point in x or y.

        Algorithm:
        - Global min/max x,y. Per-x store min/max y; per-y store min/max x.
        - For each vertical base at x: 2A = (maxy-miny) * max(x-minX, maxX-x).
        - Analogous for horizontal bases; return max or -1.

        Complexity: O(n) time, O(n) space.
        """
        min_x = min(x for x, _ in coords)
        max_x = max(x for x, _ in coords)
        min_y = min(y for _, y in coords)
        max_y = max(y for _, y in coords)

        max_y_at_x: dict[int, int] = defaultdict(lambda: -10**18)
        min_y_at_x: dict[int, int] = defaultdict(lambda: 10**18)
        max_x_at_y: dict[int, int] = defaultdict(lambda: -10**18)
        min_x_at_y: dict[int, int] = defaultdict(lambda: 10**18)
        for x, y in coords:
            max_y_at_x[x] = max(max_y_at_x[x], y)
            min_y_at_x[x] = min(min_y_at_x[x], y)
            max_x_at_y[y] = max(max_x_at_y[y], x)
            min_x_at_y[y] = min(min_x_at_y[y], x)

        best = 0
        for x in max_y_at_x:
            base = max_y_at_x[x] - min_y_at_x[x]
            if base:
                best = max(best, base * max(x - min_x, max_x - x))
        for y in max_x_at_y:
            base = max_x_at_y[y] - min_x_at_y[y]
            if base:
                best = max(best, base * max(y - min_y, max_y - y))
        return best if best else -1
# @lc code=end
