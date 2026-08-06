#
# @lc app=leetcode id=3382 lang=python3
#
# [3382] Maximum Area Rectangle With Point Constraints II
#
# https://leetcode.com/problems/maximum-area-rectangle-with-point-constraints-ii/description/
#
# algorithms
# Hard (23.56%)
# Likes:    50
# Dislikes: 9
# Total Accepted:    3.4K
# Total Submissions: 14.4K
# Testcase Example:  "[1,1,3,3]\n[1,3,1,3]"
#
#
# There are n points on an infinite plane. You are given two integer
# arrays xCoord and yCoord where (xCoord[i], yCoord[i]) represents the
# coordinates of the i^th point.
#
# Your task is to find the maximum area of a rectangle that:
#
# Can be formed using four of these points as its corners.
#
# Does not contain any other point inside or on its border.
#
# Has its edges parallel to the axes.
#
# Return the maximum area that you can obtain or -1 if no such rectangle
# is possible.
#
# Example 1:
#
# Input: xCoord = [1,1,3,3], yCoord = [1,3,1,3]
#
# Output: 4
#
# Explanation:
#
# We can make a rectangle with these 4 points as corners and there is no
# other point that lies inside or on the border. Hence, the maximum
# possible area would be 4.
#
# Example 2:
#
# Input: xCoord = [1,1,3,3,2], yCoord = [1,3,1,3,2]
#
# Output: -1
#
# Explanation:
#
# There is only one rectangle possible is with points [1,1], [1,3], [3,1]
# and [3,3] but [2,2] will always lie inside it. Hence, returning -1.
#
# Example 3:
#
# Input: xCoord = [1,1,3,3,1,3], yCoord = [1,3,1,3,2,2]
#
# Output: 2
#
# Explanation:
#
# The maximum area rectangle is formed by the points [1,3], [1,2], [3,2],
# [3,3], which has an area of 2. Additionally, the points [1,1], [1,2],
# [3,1], [3,2] also form a valid rectangle with the same area.
#
# Constraints:
#
# 1 <= xCoord.length == yCoord.length <= 2 * 10^5
#
# 0 <= xCoord[i], yCoord[i] <= 8 * 10^7
#
# All the given points are unique.
#

# @lc code=start

from typing import List


class Solution:
    def maxRectangleArea(self, xCoord: List[int], yCoord: List[int]) -> int:
        """
        Interview explanation:
        Axis-aligned empty rectangles use consecutive y-pairs on the same vertical
        line as right edge; the prior matching left edge is empty iff the point
        count in the y-range grew by exactly 2 since that left x.

        Algorithm:
        - Sort points by (x, y). Fenwick counts points by discretized y.
        - For each vertical adjacent pair (same x), if lookup[(yL,yR)] shows
          count increased by 2 only, area (x-xLeft)*(yR-yL) is valid; refresh lookup.

        Complexity: O(n log n) time, O(n) space.
        """
        class BIT:
            def __init__(self, n: int):
                self.bit = [0] * (n + 1)

            def add(self, i: int, val: int) -> None:
                i += 1
                while i < len(self.bit):
                    self.bit[i] += val
                    i += i & -i

            def query(self, i: int) -> int:
                i += 1
                ret = 0
                while i > 0:
                    ret += self.bit[i]
                    i -= i & -i
                return ret

        points = sorted(zip(xCoord, yCoord))
        y_to_idx = {y: i for i, y in enumerate(sorted(set(yCoord)))}
        bit = BIT(len(y_to_idx))
        lookup: dict[tuple[int, int], tuple[int, int]] = {}
        ans = -1
        for i, (x, y) in enumerate(points):
            yi = y_to_idx[y]
            bit.add(yi, 1)
            if i == 0 or points[i - 1][0] != x:
                continue
            prev_yi = y_to_idx[points[i - 1][1]]
            curr = bit.query(yi) - bit.query(prev_yi - 1)
            key = (prev_yi, yi)
            if key in lookup and lookup[key][0] == curr - 2:
                ans = max(ans, (x - lookup[key][1]) * (y - points[i - 1][1]))
            lookup[key] = (curr, x)
        return ans
# @lc code=end
