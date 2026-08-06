#
# @lc app=leetcode id=735 lang=python3
#
# [735] Asteroid Collision
#
# https://leetcode.com/problems/asteroid-collision/description/
#
# algorithms
# Medium (48.64%)
# Likes:    9566
# Dislikes: 1314
# Total Accepted:    1.1M
# Total Submissions: 2.3M
# Testcase Example:  "[5,10,-5]"
#
# We are given an array asteroids of integers representing asteroids in a row.
# The indices of the asteroid in the array represent their relative position in
# space.
#
# For each asteroid, the absolute value represents its size, and the sign
# represents its direction (positive meaning right, negative meaning left).
# Each asteroid moves at the same speed.
#
# Find out the state of the asteroids after all collisions. If two asteroids
# meet, the smaller one will explode. If both are the same size, both will
# explode. Two asteroids moving in the same direction will never meet.
#
# Example 1:
#
# Input: asteroids = [5,10,-5]
# Output: [5,10]
# Explanation: The 10 and -5 collide resulting in 10. The 5 and 10 never
# collide.
#
# Example 2:
#
# Input: asteroids = [8,-8]
# Output: []
# Explanation: The 8 and -8 collide exploding each other.
#
# Example 3:
#
# Input: asteroids = [10,2,-5]
# Output: [10]
# Explanation: The 2 and -5 collide resulting in -5. The 10 and -5 collide
# resulting in 10.
#
# Example 4:
#
# Input: asteroids = [3,5,-6,2,-1,4]
# Output: [-6,2,4]
# Explanation: The asteroid -6 makes the asteroid 3 and 5 explode, and then
# continues going left. On the other side, the asteroid 2 destroys -1. Since 2
# and 4 are both moving right, they never collide.
#
# Constraints:
#
# 2 <= asteroids.length <= 10^4
#
# -1000 <= asteroids[i] <= 1000
#
# asteroids[i] != 0
#


# @lc code=start
from typing import List


class Solution:
    def asteroidCollision(self, asteroids: List[int]) -> List[int]:
        """
        Interview explanation:
        Simulate collisions with a stack. Only a right-moving top and a new
        left-moving asteroid can collide. Smaller explodes; equal both explode;
        survivors stay on the stack (same direction never collide).

        Algorithm:
        - For each a: while stack top > 0 and a < 0: resolve collision
          - if |top| < |a|: pop; continue
          - if |top| == |a|: pop; a = 0 (both gone)
          - else: a = 0 (a destroyed)
        - If a != 0: push a

        Complexity: O(n) time, O(n) space.
        """
        stack: List[int] = []
        for a in asteroids:
            while stack and stack[-1] > 0 and a < 0:
                if stack[-1] < -a:
                    stack.pop()
                    continue
                if stack[-1] == -a:
                    stack.pop()
                a = 0
                break
            if a:
                stack.append(a)
        return stack
# @lc code=end

