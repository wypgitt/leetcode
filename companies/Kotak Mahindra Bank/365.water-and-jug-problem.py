#
# @lc app=leetcode id=365 lang=python3
#
# [365] Water and Jug Problem
#
# https://leetcode.com/problems/water-and-jug-problem/description/
#
# algorithms
# Medium (46.13%)
# Likes:    1727
# Dislikes: 1523
# Total Accepted:    156K
# Total Submissions: 339K
# Testcase Example:  "3"
#
# You are given two jugs with capacities x liters and y liters. You have an
# infinite water supply. Return whether the total amount of water in both jugs
# may reach target using the following operations:
#
# Fill either jug completely with water.
#
# Completely empty either jug.
#
# Pour water from one jug into another until the receiving jug is full, or the
# transferring jug is empty.
#
# Example 1:
#
# Input: x = 3, y = 5, target = 4
#
# Output: true
#
# Explanation:
#
# Follow these steps to reach a total of 4 liters:
#
# Fill the 5-liter jug (0, 5).
#
# Pour from the 5-liter jug into the 3-liter jug, leaving 2 liters (3, 2).
#
# Empty the 3-liter jug (0, 2).
#
# Transfer the 2 liters from the 5-liter jug to the 3-liter jug (2, 0).
#
# Fill the 5-liter jug again (2, 5).
#
# Pour from the 5-liter jug into the 3-liter jug until the 3-liter jug is full.
# This leaves 4 liters in the 5-liter jug (3, 4).
#
# Empty the 3-liter jug. Now, you have exactly 4 liters in the 5-liter jug (0,
# 4).
#
# Reference: The Die Hard example.
#
# Example 2:
#
# Input: x = 2, y = 6, target = 5
#
# Output: false
#
# Example 3:
#
# Input: x = 1, y = 2, target = 3
#
# Output: true
#
# Explanation: Fill both jugs. The total amount of water in both jugs is equal
# to 3 now.
#
# Constraints:
#
# 1 <= x, y, target <= 10^3
#

# @lc code=start
import math


class Solution:
    def canMeasureWater(self, x: int, y: int, target: int) -> bool:
        """
        Interview explanation:
        Bézout's identity: measurable amounts are multiples of gcd(x, y)
        (operations correspond to ±x, ±y). Also need target <= x + y.

        Algorithm:
        - If target == 0 return True; if target > x + y return False.
        - Return target % gcd(x, y) == 0 (gcd(0,0) edge: only 0 measurable).

        Complexity: O(log(min(x,y))) time, O(1) space.
        """
        if target == 0:
            return True
        if target > x + y:
            return False
        if x == 0 and y == 0:
            return False
        return target % math.gcd(x, y) == 0
# @lc code=end
