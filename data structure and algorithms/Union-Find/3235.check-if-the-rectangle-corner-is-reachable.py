#
# @lc app=leetcode id=3235 lang=python3
#
# [3235] Check if the Rectangle Corner Is Reachable
#
# https://leetcode.com/problems/check-if-the-rectangle-corner-is-reachable/description/
#
# algorithms
# Hard (25.18%)
# Likes:    123
# Dislikes: 42
# Total Accepted:    8.3K
# Total Submissions: 33K
# Testcase Example:  "3\n4\n[[2,1,1]]"
#
#
# You are given two positive integers xCorner and yCorner, and a 2D array
# circles, where circles[i] = [x_i, y_i, r_i] denotes a circle with center
# at (x_i, y_i) and radius r_i.
#
# There is a rectangle in the coordinate plane with its bottom left corner
# at the origin and top right corner at the coordinate (xCorner, yCorner).
# You need to check whether there is a path from the bottom left corner to
# the top right corner such that the entire path lies inside the
# rectangle, does not touch or lie inside any circle, and touches the
# rectangle only at the two corners.
#
# Return true if such a path exists, and false otherwise.
#
# Example 1:
#
# Input: xCorner = 3, yCorner = 4, circles = [[2,1,1]]
#
# Output: true
#
# Explanation:
#
# The black curve shows a possible path between (0, 0) and (3, 4).
#
# Example 2:
#
# Input: xCorner = 3, yCorner = 3, circles = [[1,1,2]]
#
# Output: false
#
# Explanation:
#
# No path exists from (0, 0) to (3, 3).
#
# Example 3:
#
# Input: xCorner = 3, yCorner = 3, circles = [[2,1,1],[1,2,1]]
#
# Output: false
#
# Explanation:
#
# No path exists from (0, 0) to (3, 3).
#
# Example 4:
#
# Input: xCorner = 4, yCorner = 4, circles = [[5,5,1]]
#
# Output: true
#
# Explanation:
#
# Constraints:
#
# 3 <= xCorner, yCorner <= 10^9
#
# 1 <= circles.length <= 1000
#
# circles[i].length == 3
#
# 1 <= x_i, y_i, r_i <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def canReachCorner(self, xCorner: int, yCorner: int, circles: List[List[int]]) -> bool:
        """
        Interview explanation:
        A path from (0,0) to (xCorner,yCorner) exists iff circles do not form a
        touching chain connecting the left/top sides to the right/bottom sides.
        Corners must also stay outside every circle.

        Algorithm:
        - Union-Find over circles + 2 virtual nodes (left/top, right/bottom).
        - Union circles that touch/overlap; union a circle with a side only if it
          intersects that side's finite segment (integer clamp distance).
        - Return false if a corner is covered or the virtual nodes connect.

        Complexity: O(m^2 α(m)) time, O(m) space for m circles.
        Alternate: BFS on the circle graph with four boundary flags.
        """
        m = len(circles)
        parent = list(range(m + 2))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        def touches_vert(cx: int, cy: int, r: int, x0: int, y1: int, y2: int) -> bool:
            if cx < x0 - r or cx > x0 + r:
                return False
            py = max(y1, min(y2, cy))
            return (cx - x0) * (cx - x0) + (cy - py) * (cy - py) <= r * r

        def touches_horiz(cx: int, cy: int, r: int, y0: int, x1: int, x2: int) -> bool:
            if cy < y0 - r or cy > y0 + r:
                return False
            px = max(x1, min(x2, cx))
            return (cx - px) * (cx - px) + (cy - y0) * (cy - y0) <= r * r

        LEFT_TOP, RIGHT_BOTTOM = m, m + 1
        X, Y = xCorner, yCorner

        for i, (x, y, r) in enumerate(circles):
            if x * x + y * y <= r * r:
                return False
            if (x - X) * (x - X) + (y - Y) * (y - Y) <= r * r:
                return False
            if touches_vert(x, y, r, 0, 0, Y) or touches_horiz(x, y, r, Y, 0, X):
                union(i, LEFT_TOP)
            if touches_vert(x, y, r, X, 0, Y) or touches_horiz(x, y, r, 0, 0, X):
                union(i, RIGHT_BOTTOM)
            for j in range(i):
                x2, y2, r2 = circles[j]
                dx, dy = x - x2, y - y2
                if dx * dx + dy * dy <= (r + r2) * (r + r2):
                    union(i, j)

        return find(LEFT_TOP) != find(RIGHT_BOTTOM)

# @lc code=end
