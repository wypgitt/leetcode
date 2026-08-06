#
# @lc app=leetcode id=3279 lang=python3
#
# [3279] Maximum Total Area Occupied by Pistons
#
# https://leetcode.com/problems/maximum-total-area-occupied-by-pistons/description/
#
# algorithms
# Hard (40.78%)
# Likes:    5
# Dislikes: 3
# Total Accepted:    542
# Total Submissions: 1.3K
# Testcase Example:  "5\n[2,5]\n\"UD\""
#
#
# There are several pistons in an old car engine, and we want to calculate
# the maximum possible area under the pistons.
#
# You are given:
#
# An integer height, representing the maximum height a piston can reach.
#
# An integer array positions, where positions[i] is the current position
# of piston i, which is equal to the current area under it.
#
# A string directions, where directions[i] is the current moving direction
# of piston i, 'U' for up, and 'D' for down.
#
# Each second:
#
# Every piston moves in its current direction 1 unit. e.g., if the
# direction is up, positions[i] is incremented by 1.
#
# If a piston has reached one of the ends, i.e., positions[i] == 0 or
# positions[i] == height, its direction will change.
#
# Return the maximum possible area under all the pistons.
#
# Example 1:
#
# Input: height = 5, positions = [2,5], directions = "UD"
#
# Output: 7
#
# Explanation:
#
# The current position of the pistons has the maximum possible area under
# it.
#
# Example 2:
#
# Input: height = 6, positions = [0,0,6,3], directions = "UUDU"
#
# Output: 15
#
# Explanation:
#
# After 3 seconds, the pistons will be in positions [3, 3, 3, 6], which
# has the maximum possible area under it.
#
# Constraints:
#
# 1 <= height <= 10^6
#
# 1 <= positions.length == directions.length <= 10^5
#
# 0 <= positions[i] <= height
#
# directions[i] is either 'U' or 'D'.
#

# @lc code=start

from typing import List


class Solution:
    def maxArea(self, height: int, positions: List[int], directions: str) -> int:
        """
        Interview explanation:
        Each piston bounces in [0, height]; total area is the sum of positions.
        Motion is periodic with period 2*height. Track the derivative (#up - #down)
        and update it by ±2 at bounce times via a difference array.

        Algorithm:
        - cur = sum(positions); rate = (#U) - (#D).
        - For U at p: rate -= 2 at time (height-p); += 2 at (2*height-p).
        - For D at p: rate += 2 at time p; -= 2 at (height+p).
        - For t = 1..2*height: cur += rate; ans = max(ans, cur); rate += diff[t].

        Complexity: O(n + height) time, O(height) space.
        """
        H = height
        diff = [0] * (2 * H + 1)
        cur = 0
        rate = 0
        for pos, d in zip(positions, directions):
            cur += pos
            if d == 'U':
                rate += 1
                diff[H - pos] -= 2
                diff[2 * H - pos] += 2
            else:
                rate -= 1
                diff[pos] += 2
                diff[H + pos] -= 2
        ans = cur
        for t in range(1, 2 * H + 1):
            cur += rate
            if cur > ans:
                ans = cur
            rate += diff[t]
        return ans
# @lc code=end
