#
# @lc app=leetcode id=3951 lang=python3
#
# [3951] Minimum Energy to Maintain Brightness
#
# https://leetcode.com/problems/minimum-energy-to-maintain-brightness/description/
#
# algorithms
# Medium (54.11%)
# Likes:    48
# Dislikes: 31
# Total Accepted:    25.9K
# Total Submissions: 47.9K
# Testcase Example:  "5\n5\n[[6,12]]"
#
#
# You are given an integer n, representing n light bulbs arranged in a
# line and indexed from 0 to n - 1.
#
# You are also given an integer brightness and a 2D integer array
# intervals, where intervals[i] = [start_i, end_i] represents an inclusive
# time interval during which the lighting requirement must be satisfied.
#
# At each time unit, every bulb can independently be either on or off. A
# bulb that is on illuminates its own position and its adjacent positions,
# if they exist.
#
# The total illumination at a time unit is the number of illuminated
# positions. Each position is counted at most once.
#
# For every integer time unit covered by at least one interval in
# intervals, the total illumination must be at least brightness. At time
# units not covered by any interval, all bulbs may remain off. Each bulb
# that is on consumes 1 unit of energy for that time unit.
#
# Return an integer denoting the minimum total energy required.
#
# Example 1:
#
# Input: n = 5, brightness = 5, intervals = [[6,12]]
#
# Output: 14
#
# Explanation:
#
# Turn on the light bulbs at positions 1 and 4.
#
# Current state of line: 0 1 0 0 1.
#
# All 5 positions are illuminated, so the required brightness is reached.
#
# The active interval has length 12 - 6 + 1 = 7, so the total energy is 2
# * 7 = 14.
#
# Example 2:
#
# Input: n = 2, brightness = 1, intervals = [[0,0],[2,2]]
#
# Output: 2
#
# Explanation:
#
# Turn on one light bulb during each active interval.
#
# Each interval has length 1, so the total active time is 1 + 1 = 2.
#
# The total energy is 1 * 2 = 2.
#
# Example 3:
#
# Input: n = 4, brightness = 2, intervals = [[1,3],[2,4]]
#
# Output: 4
#
# Explanation:
#
# Turn on one light bulb. It can illuminate at least 2 positions.
#
# The active intervals overlap, so the total active time is the length of
# [1,4], which is 4.
#
# The total energy is 1 * 4 = 4.
#
# Constraints:
#
# 1 <= n <= 10^6
#
# 1 <= brightness <= n
#
# 1 <= intervals.length <= 10^5
#
# intervals[i] == [start_i, end_i]
#
# 0 <= start_i <= end_i <= 10^9
#

# @lc code=start
class Solution:
    def minEnergy(self, n: int, brightness: int, intervals: list[list[int]]) -> int:
        """
        Interview explanation:
        Energy = (#bulbs on) × (union length of active times). Each bulb covers
        up to 3 positions, so need ceil(brightness/3) bulbs.

        Algorithm:
        - bulbs = (brightness + 2) // 3.
        - Merge intervals to get total active length; multiply.

        Complexity: O(m log m) time, O(m) space.
        """
        bulbs = (brightness + 2) // 3
        intervals = sorted(intervals)
        total = 0
        cs, ce = intervals[0]
        for s, e in intervals[1:]:
            if s > ce:
                total += ce - cs + 1
                cs, ce = s, e
            else:
                ce = max(ce, e)
        total += ce - cs + 1
        return bulbs * total
# @lc code=end
