#
# @lc app=leetcode id=3899 lang=python3
#
# [3899] Angles of a Triangle
#
# https://leetcode.com/problems/angles-of-a-triangle/description/
#
# algorithms
# Medium (62.37%)
# Likes:    39
# Dislikes: 36
# Total Accepted:    35.1K
# Total Submissions: 56.3K
# Testcase Example:  "[3,4,5]"
#
#
# You are given a positive integer array sides of length 3.
#
# Determine if there exists a triangle with positive area whose three side
# lengths are given by the elements of sides.
#
# If such a triangle exists, return an array of three floating-point
# numbers representing its internal angles (in degrees), sorted in
# non-decreasing order. Otherwise, return an empty array.
#
# Answers within 10^-5 of the actual answer will be accepted.
#
# Example 1:
#
# Input: sides = [3,4,5]
#
# Output: [36.86990,53.13010,90.00000]
#
# Explanation:
#
# You can form a right-angled triangle with side lengths 3, 4, and 5. The
# internal angles of this triangle are approximately 36.869897646,
# 53.130102354, and 90 degrees respectively.
#
# Example 2:
#
# Input: sides = [2,4,2]
#
# Output: []
#
# Explanation:
#
# You cannot form a triangle with positive area using side lengths 2, 4,
# and 2.
#
# Constraints:
#
# sides.length == 3
#
# 1 <= sides[i] <= 1000
#

# @lc code=start
import math


class Solution:
    def internalAngles(self, sides: list[int]) -> list[float]:
        """
        Interview explanation:
        If three lengths form a positive-area triangle, return its interior
        angles in degrees (sorted); else [].

        Algorithm:
        - Sort sides; reject if a + b <= c (degenerate).
        - Law of cosines for each angle opposite a side; convert via acos.

        Complexity: O(1) time, O(1) space.
        """
        a, b, c = sorted(sides)

        if a + b <= c:
            return []

        angles = [
            self._angle(a, b, c),
            self._angle(b, a, c),
            self._angle(c, a, b),
        ]
        angles.sort()
        return angles

    def _angle(self, opposite: int, side1: int, side2: int) -> float:
        cos_value = (side1 * side1 + side2 * side2 - opposite * opposite) / (2 * side1 * side2)
        cos_value = max(-1.0, min(1.0, cos_value))
        return math.degrees(math.acos(cos_value))
# @lc code=end
