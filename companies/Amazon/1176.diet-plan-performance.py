#
# @lc app=leetcode id=1176 lang=python3
#
# [1176] Diet Plan Performance
#
# https://leetcode.com/problems/diet-plan-performance/description/
#
# algorithms
# Easy (56.11%)
# Likes:    174
# Dislikes: 297
# Total Accepted:    42.5K
# Total Submissions: 75.8K
# Testcase Example:  "[1,2,3,4,5]\n1\n3\n3"
#
#
# A dieter consumes calories[i] calories on the i-th day.
#
# Given an integer k, for every consecutive sequence of k days
# (calories[i], calories[i+1], ..., calories[i+k-1] for all 0 <= i <=
# n-k), they look at T, the total calories consumed during that sequence
# of k days (calories[i] + calories[i+1] + ... + calories[i+k-1]):
#
# If T < lower, they performed poorly on their diet and lose 1 point;
#
# If T > upper, they performed well on their diet and gain 1 point;
#
# Otherwise, they performed normally and there is no change in points.
#
# Initially, the dieter has zero points. Return the total number of points
# the dieter has after dieting for calories.length days.
#
# Note that the total points can be negative.
#
# Example 1:
#
# Input: calories = [1,2,3,4,5], k = 1, lower = 3, upper = 3
# Output: 0
# Explanation: Since k = 1, we consider each element of the array
# separately and compare it to lower and upper.
# calories[0] and calories[1] are less than lower so 2 points are lost.
# calories[3] and calories[4] are greater than upper so 2 points are
# gained.
#
# Example 2:
#
# Input: calories = [3,2], k = 2, lower = 0, upper = 1
# Output: 1
# Explanation: Since k = 2, we consider subarrays of length 2.
# calories[0] + calories[1] > upper so 1 point is gained.
#
# Example 3:
#
# Input: calories = [6,5,0,0], k = 2, lower = 1, upper = 5
# Output: 0
# Explanation:
# calories[0] + calories[1] > upper so 1 point is gained.
# lower <= calories[1] + calories[2] <= upper so no change in points.
# calories[2] + calories[3] < lower so 1 point is lost.
#
# Constraints:
#
# 1 <= k <= calories.length <= 10^5
#
# 0 <= calories[i] <= 20000
#
# 0 <= lower <= upper
#
# @lc code=start

from typing import List


class Solution:
    def dietPlanPerformance(self, calories: List[int], k: int, lower: int, upper: int) -> int:
        """
        Interview explanation:
        Premium: sliding window of k consecutive days. Window sum < lower → -1
        point; > upper → +1; else 0. Total points over all windows.

        Algorithm (sliding window):
        - Sum first k days; score. Slide: add calories[i], drop calories[i-k].

        Complexity: O(n) time, O(1) space.
        """
        n = len(calories)
        window = sum(calories[:k])
        points = 0

        def score(s: int) -> int:
            if s < lower:
                return -1
            if s > upper:
                return 1
            return 0

        points += score(window)
        for i in range(k, n):
            window += calories[i] - calories[i - k]
            points += score(window)
        return points
# @lc code=end
