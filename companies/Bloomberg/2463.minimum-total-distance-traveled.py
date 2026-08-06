#
# @lc app=leetcode id=2463 lang=python3
#
# [2463] Minimum Total Distance Traveled
#
# https://leetcode.com/problems/minimum-total-distance-traveled/description/
#
# algorithms
# Hard (63.14%)
# Likes:    1232
# Dislikes: 42
# Total Accepted:    136.2K
# Total Submissions: 215.6K
# Testcase Example:  "[0,4,6]\n[[2,2],[6,2]]"
#
# There are some robots and factories on the X-axis. You are given an integer
# array robot where robot[i] is the position of the i^th robot. You are also
# given a 2D integer array factory where factory[j] = [position_j, limit_j]
# indicates that position_j is the position of the j^th factory and that the
# j^th factory can repair at most limit_j robots.
#
# The positions of each robot are unique. The positions of each factory are also
# unique. Note that a robot can be in the same position as a factory initially.
#
# All the robots are initially broken; they keep moving in one direction. The
# direction could be the negative or the positive direction of the X-axis. When
# a robot reaches a factory that did not reach its limit, the factory repairs
# the robot, and it stops moving.
#
# At any moment, you can set the initial direction of moving for some robot.
# Your target is to minimize the total distance traveled by all the robots.
#
# Return the minimum total distance traveled by all the robots. The test cases
# are generated such that all the robots can be repaired.
#
# Note that
#
#
# All robots move at the same speed.
#
#
# If two robots move in the same direction, they will never collide.
#
#
# If two robots move in opposite directions and they meet at some point, they do
# not collide. They cross each other.
#
#
# If a robot passes by a factory that reached its limits, it crosses it as if it
# does not exist.
#
#
# If the robot moved from a position x to a position y, the distance it moved is
# |y - x|.
#
#
#
# Example 1:
#
# Input: robot = [0,4,6], factory = [[2,2],[6,2]]
# Output: 4
# Explanation: As shown in the figure:
# - The first robot at position 0 moves in the positive direction. It will be
# repaired at the first factory.
# - The second robot at position 4 moves in the negative direction. It will be
# repaired at the first factory.
# - The third robot at position 6 will be repaired at the second factory. It
# does not need to move.
# The limit of the first factory is 2, and it fixed 2 robots.
# The limit of the second factory is 2, and it fixed 1 robot.
# The total distance is |2 - 0| + |2 - 4| + |6 - 6| = 4. It can be shown that we
# cannot achieve a better total distance than 4.
#
# Example 2:
#
# Input: robot = [1,-1], factory = [[-2,1],[2,1]]
# Output: 2
# Explanation: As shown in the figure:
# - The first robot at position 1 moves in the positive direction. It will be
# repaired at the second factory.
# - The second robot at position -1 moves in the negative direction. It will be
# repaired at the first factory.
# The limit of the first factory is 1, and it fixed 1 robot.
# The limit of the second factory is 1, and it fixed 1 robot.
# The total distance is |2 - 1| + |(-2) - (-1)| = 2. It can be shown that we
# cannot achieve a better total distance than 2.
#
#
#
# Constraints:
#
#
# 1 <= robot.length, factory.length <= 100
#
#
# factory[j].length == 2
#
#
# -10^9 <= robot[i], position_j <= 10^9
#
#
# 0 <= limit_j <= robot.length
#
#
# The input will be generated such that it is always possible to repair every
# robot.
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def minimumTotalDistance(self, robot: List[int], factory: List[List[int]]) -> int:
        """
        Interview explanation:
        Assign each robot to a factory (within capacity) minimizing total
        |robot-factory| travel. Factories have limited repair slots.

        Algorithm:
        - Sort robots/factories; DP over robots and expanded factory slots
          (each slot can take one robot).

        Complexity: O(R * F * R) ~ O(R^2 * F) time with memo, O(R*S) space.
        """
        robot.sort()
        factory.sort()
        slots = []
        for pos, lim in factory:
            slots.extend([pos] * lim)
        m, n = len(robot), len(slots)

        @lru_cache(None)
        def dp(i: int, j: int) -> int:
            if i == m:
                return 0
            if j == n:
                return 10**18
            skip = dp(i, j + 1)
            take = abs(robot[i] - slots[j]) + dp(i + 1, j + 1)
            return min(skip, take)

        return dp(0, 0)
# @lc code=end

