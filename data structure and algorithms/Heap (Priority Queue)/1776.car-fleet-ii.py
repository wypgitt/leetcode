#
# @lc app=leetcode id=1776 lang=python3
#
# [1776] Car Fleet II
#
# https://leetcode.com/problems/car-fleet-ii/description/
#
# algorithms
# Hard (58.22%)
# Likes:    982
# Dislikes: 41
# Total Accepted:    34.6K
# Total Submissions: 59.4K
# Testcase Example:  "[[1,2],[2,1],[4,3],[7,2]]"
#
# There are n cars traveling at different speeds in the same direction along a
# one-lane road. You are given an array cars of length n, where cars[i] =
# [position_i, speed_i] represents:
#
# position_i is the distance between the i^th car and the beginning of the road
# in meters. It is guaranteed that position_i < position_i+1.
#
# speed_i is the initial speed of the i^th car in meters per second.
#
# For simplicity, cars can be considered as points moving along the number
# line. Two cars collide when they occupy the same position. Once a car
# collides with another car, they unite and form a single car fleet. The cars
# in the formed fleet will have the same position and the same speed, which is
# the initial speed of the slowest car in the fleet.
#
# Return an array answer, where answer[i] is the time, in seconds, at which the
# i^th car collides with the next car, or -1 if the car does not collide with
# the next car. Answers within 10^-5 of the actual answers are accepted.
#
# Example 1:
#
# Input: cars = [[1,2],[2,1],[4,3],[7,2]]
# Output: [1.00000,-1.00000,3.00000,-1.00000]
# Explanation: After exactly one second, the first car will collide with the
# second car, and form a car fleet with speed 1 m/s. After exactly 3 seconds,
# the third car will collide with the fourth car, and form a car fleet with
# speed 2 m/s.
#
# Example 2:
#
# Input: cars = [[3,4],[5,4],[6,3],[9,1]]
# Output: [2.00000,1.00000,1.50000,-1.00000]
#
# Constraints:
#
# 1 <= cars.length <= 10^5
#
# 1 <= position_i, speed_i <= 10^6
#
# position_i < position_i+1
#

# @lc code=start
from typing import List


class Solution:
    def getCollisionTimes(self, cars: List[List[int]]) -> List[float]:
        """
        Interview explanation:
        Cars go right; faster catch slower ahead. Collision time of i with a
        fleet ahead: use a monotonic stack of candidates to the right. From
        right to left, pop cars that i will never hit (faster or hit after
        that car already collided into someone further).

        Algorithm:
        - ans[i]=-1 default; stack of indices (increasing position, right side).
        - While stack: if speed[i] <= speed[top] or collision time with top
          is after top's own collision: pop; else break.
        - Compute time with new top if any.

        Complexity: O(n) time, O(n) space.
        """
        n = len(cars)
        ans = [-1.0] * n
        stack = []
        for i in range(n - 1, -1, -1):
            p, s = cars[i]
            while stack:
                j = stack[-1]
                pj, sj = cars[j]
                if s <= sj:
                    stack.pop()
                    continue
                # time to catch j
                t = (pj - p) / (s - sj)
                if ans[j] >= 0 and t > ans[j]:
                    stack.pop()
                    continue
                break
            if stack:
                j = stack[-1]
                ans[i] = (cars[j][0] - p) / (s - cars[j][1])
            stack.append(i)
        return ans
# @lc code=end
