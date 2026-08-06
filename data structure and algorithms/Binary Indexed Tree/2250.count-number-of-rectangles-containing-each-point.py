#
# @lc app=leetcode id=2250 lang=python3
#
# [2250] Count Number of Rectangles Containing Each Point
#
# https://leetcode.com/problems/count-number-of-rectangles-containing-each-point/description/
#
# algorithms
# Medium (37.84%)
# Likes:    558
# Dislikes: 141
# Total Accepted:    24K
# Total Submissions: 63.3K
# Testcase Example:  "[[1,2],[2,3],[2,5]]\n[[2,1],[1,4]]"
#
# You are given a 2D integer array rectangles where rectangles[i] = [l_i, h_i]
# indicates that i^th rectangle has a length of l_i and a height of h_i. You are
# also given a 2D integer array points where points[j] = [x_j, y_j] is a point
# with coordinates (x_j, y_j).
#
# The i^th rectangle has its bottom-left corner point at the coordinates (0, 0)
# and its top-right corner point at (l_i, h_i).
#
# Return an integer array count of length points.length where count[j] is the
# number of rectangles that contain the j^th point.
#
# The i^th rectangle contains the j^th point if 0 <= x_j <= l_i and 0 <= y_j <=
# h_i. Note that points that lie on the edges of a rectangle are also considered
# to be contained by that rectangle.
#
#
#
# Example 1:
#
# Input: rectangles = [[1,2],[2,3],[2,5]], points = [[2,1],[1,4]]
# Output: [2,1]
# Explanation:
# The first rectangle contains no points.
# The second rectangle contains only the point (2, 1).
# The third rectangle contains the points (2, 1) and (1, 4).
# The number of rectangles that contain the point (2, 1) is 2.
# The number of rectangles that contain the point (1, 4) is 1.
# Therefore, we return [2, 1].
#
# Example 2:
#
# Input: rectangles = [[1,1],[2,2],[3,3]], points = [[1,3],[1,1]]
# Output: [1,3]
# Explanation:
# The first rectangle contains only the point (1, 1).
# The second rectangle contains only the point (1, 1).
# The third rectangle contains the points (1, 3) and (1, 1).
# The number of rectangles that contain the point (1, 3) is 1.
# The number of rectangles that contain the point (1, 1) is 3.
# Therefore, we return [1, 3].
#
#
#
# Constraints:
#
#
# 1 <= rectangles.length, points.length <= 5 * 10^4
#
#
# rectangles[i].length == points[j].length == 2
#
#
# 1 <= l_i, x_j <= 10^9
#
#
# 1 <= h_i, y_j <= 100
#
#
# All the rectangles are unique.
#
#
# All the points are unique.
#

# @lc code=start
from typing import List
import bisect
from collections import defaultdict


class Solution:
    def countRectangles(self, rectangles: List[List[int]], points: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Rectangles from (0,0) to (l,h). For each point (x,y) count rectangles with
        l>=x and h>=y. Heights are in [1,100].

        Algorithm:
        - Group rectangle lengths by height; sort lengths per height.
        - For point (x,y), sum over h>=y the number of lengths >= x via binary
          search.

        Complexity: O((R+P) * H + R log R) time with H<=100, O(R) space.
        """
        by_h = defaultdict(list)
        for l, h in rectangles:
            by_h[h].append(l)
        for h in by_h:
            by_h[h].sort()
        ans = []
        for x, y in points:
            cnt = 0
            for h in range(y, 101):
                arr = by_h.get(h)
                if not arr:
                    continue
                # number of l >= x
                i = bisect.bisect_left(arr, x)
                cnt += len(arr) - i
            ans.append(cnt)
        return ans
# @lc code=end
