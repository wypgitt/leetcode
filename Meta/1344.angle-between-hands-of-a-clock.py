#
# @lc app=leetcode id=1344 lang=python3
#
# [1344] Angle Between Hands of a Clock
#
# https://leetcode.com/problems/angle-between-hands-of-a-clock/description/
#
# algorithms
# Medium (69.84%)
# Likes:    1699
# Dislikes: 265
# Total Accepted:    276K
# Total Submissions: 396K
# Testcase Example:  "12"
#
# Given two numbers, hour and minutes, return the smaller angle (in degrees)
# formed between the hour and the minute hand.
#
# Answers within 10^-5 of the actual value will be accepted as correct.
#
# Example 1:
#
# Input: hour = 12, minutes = 30
# Output: 165
#
# Example 2:
#
# Input: hour = 3, minutes = 30
# Output: 75
#
# Example 3:
#
# Input: hour = 3, minutes = 15
# Output: 7.5
#
# Constraints:
#
# 1 <= hour <= 12
#
# 0 <= minutes <= 59
#

# @lc code=start
class Solution:
    def angleClock(self, hour: int, minutes: int) -> float:
        """
        Interview explanation:
        Minute hand: 6 deg/min. Hour hand: 30 deg/hour + 0.5 deg/min.
        Angle = min(|h-m|, 360-|h-m|).

        Algorithm:
        - Compute positions; return min delta.

        Complexity: O(1).
        """
        h = (hour % 12) * 30 + minutes * 0.5
        m = minutes * 6
        diff = abs(h - m)
        return min(diff, 360 - diff)
# @lc code=end

