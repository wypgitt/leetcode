#
# @lc app=leetcode id=2543 lang=python3
#
# [2543] Check if Point Is Reachable
#
# https://leetcode.com/problems/check-if-point-is-reachable/description/
#
# algorithms
# Hard (45.23%)
# Likes:    265
# Dislikes: 52
# Total Accepted:    11.4K
# Total Submissions: 25.2K
# Testcase Example:  "6\n9"
#
# There exists an infinitely large grid. You are currently at point (1, 1), and
# you need to reach the point (targetX, targetY) using a finite number of steps.
#
# In one step, you can move from point (x, y) to any one of the following
# points:
#
#
# (x, y - x)
#
#
# (x - y, y)
#
#
# (2 * x, y)
#
#
# (x, 2 * y)
#
# Given two integers targetX and targetY representing the X-coordinate and
# Y-coordinate of your final position, return true if you can reach the point
# from (1, 1) using some number of steps, and false otherwise.
#
#
#
# Example 1:
#
# Input: targetX = 6, targetY = 9
# Output: false
# Explanation: It is impossible to reach (6,9) from (1,1) using any sequence of
# moves, so false is returned.
#
# Example 2:
#
# Input: targetX = 4, targetY = 7
# Output: true
# Explanation: You can follow the path (1,1) -> (1,2) -> (1,4) -> (1,8) -> (1,7)
# -> (2,7) -> (4,7).
#
#
#
# Constraints:
#
#
# 1 <= targetX, targetY <= 10^9
#

# @lc code=start
import math


class Solution:
    def isReachable(self, targetX: int, targetY: int) -> bool:
        """
        Interview explanation:
        From (1,1) moves: (x,y-x), (x-y,y), (2x,y), (x,2y). Reach (tx,ty)?

        Algorithm:
        - Subtract moves mirror Euclidean gcd; doubling only multiplies by 2.
        - Reachable iff gcd(tx,ty) is a power of 2.

        Complexity: O(log min(tx,ty)) time, O(1) space.
        """
        g = math.gcd(targetX, targetY)
        return g > 0 and (g & (g - 1)) == 0

    def isReachable_euclid(self, targetX: int, targetY: int) -> bool:
        """
        Interview explanation:
        Classic alternate: Euclidean reduction while stripping factors of 2
        (reverse of subtract / double moves).

        Algorithm:
        - While x!=y: swap so x>=y; if x even halve else x-=y (and allow
          later halvings). Finally x(=y) must be a power of 2.

        Complexity: O(log min(tx,ty)) time, O(1) space.
        """
        x, y = targetX, targetY
        while x != y:
            if x < y:
                x, y = y, x
            if x % 2 == 0:
                x //= 2
            elif y % 2 == 0:
                y //= 2
            else:
                x -= y
        return x > 0 and (x & (x - 1)) == 0
# @lc code=end
