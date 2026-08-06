#
# @lc app=leetcode id=1515 lang=python3
#
# [1515] Best Position for a Service Centre
#
# https://leetcode.com/problems/best-position-for-a-service-centre/description/
#
# algorithms
# Hard (35.56%)
# Likes:    248
# Dislikes: 274
# Total Accepted:    20.2K
# Total Submissions: 56.8K
# Testcase Example:  "[[0,1],[1,0],[1,2],[2,1]]"
#
# A delivery company wants to build a new service center in a new city. The
# company knows the positions of all the customers in this city on a 2D-Map and
# wants to build the new center in a position such that the sum of the
# euclidean distances to all customers is minimum.
#
# Given an array positions where positions[i] = [x_i, y_i] is the position of
# the ith customer on the map, return the minimum sum of the euclidean
# distances to all customers.
#
# In other words, you need to choose the position of the service center
# [x_centre, y_centre] such that the following formula is minimized:
#
# Answers within 10^-5 of the actual value will be accepted.
#
# Example 1:
#
# Input: positions = [[0,1],[1,0],[1,2],[2,1]]
# Output: 4.00000
# Explanation: As shown, you can see that choosing [x_centre, y_centre] = [1,
# 1] will make the distance to each customer = 1, the sum of all distances is 4
# which is the minimum possible we can achieve.
#
# Example 2:
#
# Input: positions = [[1,1],[3,3]]
# Output: 2.82843
# Explanation: The minimum possible sum of distances = sqrt(2) + sqrt(2) =
# 2.82843
#
# Constraints:
#
# 1 <= positions.length <= 50
#
# positions[i].length == 2
#
# 0 <= x_i, y_i <= 100
#

# @lc code=start
from typing import List
import math


class Solution:
    def getMinDistSum(self, positions: List[List[int]]) -> float:
        """
        Interview explanation:
        Geometric median of points (minimize sum of Euclidean distances). No
        closed form; use gradient descent / Weiszfeld, or ternary search /
        coordinate descent on the convex objective.

        Algorithm:
        - Start at centroid; iteratively move opposite the unit-vector sum
          (subgradient); shrink step when no improvement; stop when step small.

        Complexity: O(I * n) time for I iterations, O(1) extra.
        """
        n = len(positions)
        x = sum(p[0] for p in positions) / n
        y = sum(p[1] for p in positions) / n

        def dist_sum(cx: float, cy: float) -> float:
            return sum(math.hypot(cx - px, cy - py) for px, py in positions)

        step = 100.0
        eps = 1e-7
        while step > eps:
            dx = dy = 0.0
            for px, py in positions:
                d = math.hypot(x - px, y - py)
                if d > 0:
                    dx += (x - px) / d
                    dy += (y - py) / d
            nx, ny = x - step * dx, y - step * dy
            if dist_sum(nx, ny) < dist_sum(x, y):
                x, y = nx, ny
            else:
                step *= 0.5
        return dist_sum(x, y)
# @lc code=end
