#
# @lc app=leetcode id=1610 lang=python3
#
# [1610] Maximum Number of Visible Points
#
# https://leetcode.com/problems/maximum-number-of-visible-points/description/
#
# algorithms
# Hard (38.36%)
# Likes:    632
# Dislikes: 769
# Total Accepted:    55.2K
# Total Submissions: 144K
# Testcase Example:  "[[2,1],[2,2],[3,3]]"
#
# You are given an array points, an integer angle, and your location, where
# location = [pos_x, pos_y] and points[i] = [x_i, y_i] both denote integral
# coordinates on the X-Y plane.
#
# Initially, you are facing directly east from your position. You cannot move
# from your position, but you can rotate. In other words, pos_x and pos_y
# cannot be changed. Your field of view in degrees is represented by angle,
# determining how wide you can see from any given view direction. Let d be the
# amount in degrees that you rotate counterclockwise. Then, your field of view
# is the inclusive range of angles [d - angle/2, d + angle/2].
#
# Your browser does not support the video tag or this video format.
#
# You can see some set of points if, for each point, the angle formed by the
# point, your position, and the immediate east direction from your position is
# in your field of view.
#
# There can be multiple points at one coordinate. There may be points at your
# location, and you can always see these points regardless of your rotation.
# Points do not obstruct your vision to other points.
#
# Return the maximum number of points you can see.
#
# Example 1:
#
# Input: points = [[2,1],[2,2],[3,3]], angle = 90, location = [1,1]
# Output: 3
# Explanation: The shaded region represents your field of view. All points can
# be made visible in your field of view, including [3,3] even though [2,2] is
# in front and in the same line of sight.
#
# Example 2:
#
# Input: points = [[2,1],[2,2],[3,4],[1,1]], angle = 90, location = [1,1]
# Output: 4
# Explanation: All points can be made visible in your field of view, including
# the one at your location.
#
# Example 3:
#
# Input: points = [[1,0],[2,1]], angle = 13, location = [1,1]
# Output: 1
# Explanation: You can only see one of the two points, as shown above.
#
# Constraints:
#
# 1 <= points.length <= 10^5
#
# points[i].length == 2
#
# location.length == 2
#
# 0 <= angle < 360
#
# 0 <= pos_x, pos_y, x_i, y_i <= 100
#

# @lc code=start
from typing import List
import math


class Solution:
    def visiblePoints(self, points: List[List[int]], angle: int, location: List[int]) -> int:
        """
        Interview explanation:
        Points at location always visible. Others: convert to polar angles relative
        to location; circular sliding window of width `angle` maximizes visible.

        Algorithm (angles + sliding window):
        - Count same-as-location. Compute atan2 angles; sort; duplicate +2π for circle.
        - Two pointers: max number of angles in window of size angle (radians).

        Complexity: O(n log n) time, O(n) space.
        """
        lx, ly = location
        same = 0
        angles = []
        for x, y in points:
            if x == lx and y == ly:
                same += 1
            else:
                angles.append(math.atan2(y - ly, x - lx))
        angles.sort()
        angles += [a + 2 * math.pi for a in angles]
        rad = math.radians(angle)
        ans = left = 0
        for right in range(len(angles)):
            while angles[right] - angles[left] > rad:
                left += 1
            ans = max(ans, right - left + 1)
        # only first half of duplicated list is meaningful for window start
        return ans + same

    def visiblePoints_deque(self, points: List[List[int]], angle: int, location: List[int]) -> int:
        """
        Interview explanation:
        Same geometry; use explicit deque window for clarity in interviews.

        Algorithm (deque window):
        - Sort angles; for each angle as right end, popleft while span > angle;
          track max window size + same-location count.

        Complexity: O(n log n) time, O(n) space.
        """
        from collections import deque

        lx, ly = location
        same = 0
        angles = []
        for x, y in points:
            if x == lx and y == ly:
                same += 1
            else:
                angles.append(math.atan2(y - ly, x - lx))
        angles.sort()
        angles += [a + 2 * math.pi for a in angles]
        rad = math.radians(angle)
        window = deque()
        ans = 0
        for a in angles:
            window.append(a)
            while window and a - window[0] > rad:
                window.popleft()
            ans = max(ans, len(window))
        return ans + same
# @lc code=end
