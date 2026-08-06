#
# @lc app=leetcode id=478 lang=python3
#
# [478] Generate Random Point in a Circle
#
# https://leetcode.com/problems/generate-random-point-in-a-circle/description/
#
# algorithms
# Medium (42.86%)
# Likes:    483
# Dislikes: 784
# Total Accepted:    54.6K
# Total Submissions: 127.4K
# Testcase Example:  '["Solution","randPoint","randPoint","randPoint"]\n[[1.0,0.0,0.0],[],[],[]]'
#
# Given the radius and the position of the center of a circle, implement the
# function randPoint which generates a uniform random point inside the circle.
# 
# Implement the Solution class:
# 
# 
# Solution(double radius, double x_center, double y_center) initializes the
# object with the radius of the circle radius and the position of the center
# (x_center, y_center).
# randPoint() returns a random point inside the circle. A point on the
# circumference of the circle is considered to be in the circle. The answer is
# returned as an array [x, y].
# 
# 
# 
# Example 1:
# 
# 
# Input
# ["Solution", "randPoint", "randPoint", "randPoint"]
# [[1.0, 0.0, 0.0], [], [], []]
# Output
# [null, [-0.02493, -0.38077], [0.82314, 0.38945], [0.36572, 0.17248]]
# 
# Explanation
# Solution solution = new Solution(1.0, 0.0, 0.0);
# solution.randPoint(); // return [-0.02493, -0.38077]
# solution.randPoint(); // return [0.82314, 0.38945]
# solution.randPoint(); // return [0.36572, 0.17248]
# 
# 
# 
# Constraints:
# 
# 
# 0 < radius <= 10^8
# -10^7 <= x_center, y_center <= 10^7
# At most 3 * 10^4 calls will be made to randPoint.
# 
# 
#

# @lc code=start
import math
import random
from typing import List


class Solution:
    def __init__(self, radius: float, x_center: float, y_center: float):
        self.radius = radius
        self.x_center = x_center
        self.y_center = y_center

    def randPoint(self) -> List[float]:
        angle = random.random() * 2 * math.pi
        distance = self.radius * math.sqrt(random.random())
        return [self.x_center + distance * math.cos(angle),
                self.y_center + distance * math.sin(angle)]
# @lc code=end

"""
Interview explanation:
Choose a random angle uniformly in [0, 2pi). The radius cannot be chosen uniformly, because that would over-sample the center; circle area grows with r^2. If U is uniform, sqrt(U) * R gives the correct radial distribution.

Data structure: store the circle parameters on the object; each call independently samples two random numbers.

Edge cases: any center coordinates work. Points on the boundary are allowed, and floating-point randomness makes exact boundary probability negligible.

Complexity: O(1) time and O(1) space per generated point.
"""
