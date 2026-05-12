#
# @lc app=leetcode id=1344 lang=python3
#
# [1344] Angle Between Hands of a Clock
#
# https://leetcode.com/problems/angle-between-hands-of-a-clock/description/
#
# algorithms
# Medium (64.43%)
# Likes:    1376
# Dislikes: 248
# Total Accepted:    144.1K
# Total Submissions: 223.6K
# Testcase Example:  '12\n30'
#
# Given two numbers, hour and minutes, return the smaller angle (in degrees)
# formed between the hour and the minute hand.
# 
# Answers within 10^-5 of the actual value will be accepted as correct.
# 
# 
# Example 1:
# 
# 
# Input: hour = 12, minutes = 30
# Output: 165
# 
# 
# Example 2:
# 
# 
# Input: hour = 3, minutes = 30
# Output: 75
# 
# 
# Example 3:
# 
# 
# Input: hour = 3, minutes = 15
# Output: 7.5
# 
# 
# 
# Constraints:
# 
# 
# 1 <= hour <= 12
# 0 <= minutes <= 59
# 
# 
#

# @lc code=start
from __future__ import annotations


class Solution:
    def angleClock(self, hour: int, minutes: int) -> float:
        hour %= 12
        minute_angle = minutes * 6
        hour_angle = hour * 30 + minutes * 0.5
        difference = abs(hour_angle - minute_angle)
        return min(difference, 360 - difference)
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Convert each hand position to degrees from 12 o'clock, take the absolute
# difference, then return the smaller of that angle and its complement.
#
# Math:
# - Minute hand: 360 degrees / 60 minutes = 6 degrees per minute.
# - Hour hand: 360 degrees / 12 hours = 30 degrees per hour, plus 0.5 degrees
#   per minute because it moves continuously.
#
# Edge cases:
# - Hour 12 should behave like 0 degrees, so use `hour %= 12`.
# - The direct difference may be more than 180; the smaller angle is
#   `360 - difference`.
# - Minutes 0 means the hour hand is exactly on the hour mark.
#
# Complexity:
# - Time: O(1).
# - Space: O(1).
