#
# @lc app=leetcode id=939 lang=python3
#
# [939] Minimum Area Rectangle
#
# https://leetcode.com/problems/minimum-area-rectangle/description/
#
# algorithms
# Medium (55.46%)
# Likes:    2117
# Dislikes: 298
# Total Accepted:    183K
# Total Submissions: 330K
# Testcase Example:  "[[1,1],[1,3],[3,1],[3,3],[2,2]]"
#
# You are given an array of points in the X-Y plane points where points[i] =
# [x_i, y_i].
#
# Return the minimum area of a rectangle formed from these points, with sides
# parallel to the X and Y axes. If there is not any such rectangle, return 0.
#
# Example 1:
#
# Input: points = [[1,1],[1,3],[3,1],[3,3],[2,2]]
# Output: 4
#
# Example 2:
#
# Input: points = [[1,1],[1,3],[3,1],[3,3],[4,1],[4,3]]
# Output: 2
#
# Constraints:
#
# 1 <= points.length <= 500
#
# points[i].length == 2
#
# 0 <= x_i, y_i <= 4 * 10^4
#
# All the given points are unique.
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def minAreaRect(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Axis-aligned rectangle = two distinct diagonals sharing x/y pairwise.
        Group points by x-coordinate; for each pair of y's at a column, check
        if that y-pair appeared in a previous column → form rectangle.

        Algorithm:
        - cols: x -> sorted list of y
        - last[(y1,y2)] = previous x with both y1,y2
        - For each x ascending, for each pair y1<y2 in that column: if (y1,y2)
          seen, area = (x-prev)*(y2-y1); track min; update last

        Complexity: O(n^2) time worst, O(n) space.
        """
        by_x = defaultdict(list)
        for x, y in points:
            by_x[x].append(y)
        last = {}
        ans = float('inf')
        for x in sorted(by_x):
            ys = sorted(by_x[x])
            for i in range(len(ys)):
                for j in range(i + 1, len(ys)):
                    y1, y2 = ys[i], ys[j]
                    if (y1, y2) in last:
                        ans = min(ans, (x - last[(y1, y2)]) * (y2 - y1))
                    last[(y1, y2)] = x
        return 0 if ans == float('inf') else ans

    def minAreaRect_diagonal(self, points: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: put all points in a set; for every pair as potential diagonal
        (different x and y), check the other two corners exist; compute area.

        Algorithm:
        - set of (x,y); for i<j pairs with x1!=x2 and y1!=y2: if (x1,y2),(x2,y1)
          in set → update min area |x1-x2|*|y1-y2|

        Complexity: O(n^2) time, O(n) space.
        """
        pts = {(x, y) for x, y in points}
        arr = list(pts)
        ans = float('inf')
        n = len(arr)
        for i in range(n):
            x1, y1 = arr[i]
            for j in range(i + 1, n):
                x2, y2 = arr[j]
                if x1 != x2 and y1 != y2 and (x1, y2) in pts and (x2, y1) in pts:
                    ans = min(ans, abs(x1 - x2) * abs(y1 - y2))
        return 0 if ans == float('inf') else ans
# @lc code=end

