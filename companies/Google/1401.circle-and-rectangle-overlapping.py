#
# @lc app=leetcode id=1401 lang=python3
#
# [1401] Circle and Rectangle Overlapping
#
# https://leetcode.com/problems/circle-and-rectangle-overlapping/description/
#
# algorithms
# Medium (50.34%)
# Likes:    408
# Dislikes: 85
# Total Accepted:    25.2K
# Total Submissions: 50.1K
# Testcase Example:  "1"
#
# You are given a circle represented as (radius, xCenter, yCenter) and an
# axis-aligned rectangle represented as (x1, y1, x2, y2), where (x1, y1) are
# the coordinates of the bottom-left corner, and (x2, y2) are the coordinates
# of the top-right corner of the rectangle.
#
# Return true if the circle and rectangle are overlapped otherwise return
# false. In other words, check if there is any point (x_i, y_i) that belongs to
# the circle and the rectangle at the same time.
#
# Example 1:
#
# Input: radius = 1, xCenter = 0, yCenter = 0, x1 = 1, y1 = -1, x2 = 3, y2 = 1
# Output: true
# Explanation: Circle and rectangle share the point (1,0).
#
# Example 2:
#
# Input: radius = 1, xCenter = 1, yCenter = 1, x1 = 1, y1 = -3, x2 = 2, y2 = -1
# Output: false
#
# Example 3:
#
# Input: radius = 1, xCenter = 0, yCenter = 0, x1 = -1, y1 = 0, x2 = 0, y2 = 1
# Output: true
#
# Constraints:
#
# 1 <= radius <= 2000
#
# -10^4 <= xCenter, yCenter <= 10^4
#
# -10^4 <= x1 < x2 <= 10^4
#
# -10^4 <= y1 < y2 <= 10^4
#

# @lc code=start
class Solution:
    def checkOverlap(self, radius: int, xCenter: int, yCenter: int, x1: int, y1: int, x2: int, y2: int) -> bool:
        """
        Interview explanation:
        Circle-rectangle overlap iff distance from circle center to the closest
        point on the axis-aligned rectangle is <= radius. Clamp center to the
        rectangle bounds to get that closest point.

        Algorithm:
        - closest_x = clamp(xCenter, x1, x2); closest_y = clamp(yCenter, y1, y2)
        - dx, dy = xCenter-closest_x, yCenter-closest_y
        - return dx*dx + dy*dy <= radius*radius

        Complexity: O(1) time, O(1) space.
        """
        dx = xCenter - min(max(xCenter, x1), x2)
        dy = yCenter - min(max(yCenter, y1), y2)
        return dx * dx + dy * dy <= radius * radius

    def checkOverlap_corners(self, radius: int, xCenter: int, yCenter: int, x1: int, y1: int, x2: int, y2: int) -> bool:
        """
        Interview explanation:
        Alternate geometry view: same clamp formula, written with explicit
        nearest-point construction (equivalent classic solution).

        Algorithm:
        - Build nearest rectangle point via clamp; compare squared distance.

        Complexity: O(1) time, O(1) space.
        """
        nearest_x = x1 if xCenter < x1 else (x2 if xCenter > x2 else xCenter)
        nearest_y = y1 if yCenter < y1 else (y2 if yCenter > y2 else yCenter)
        return (xCenter - nearest_x) ** 2 + (yCenter - nearest_y) ** 2 <= radius ** 2
# @lc code=end
