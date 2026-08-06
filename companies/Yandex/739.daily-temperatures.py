#
# @lc app=leetcode id=739 lang=python3
#
# [739] Daily Temperatures
#
# https://leetcode.com/problems/daily-temperatures/description/
#
# algorithms
# Medium (69.01%)
# Likes:    14904
# Dislikes: 380
# Total Accepted:    1.9M
# Total Submissions: 2.7M
# Testcase Example:  "[73,74,75,71,69,72,76,73]"
#
# Given an array of integers temperatures represents the daily temperatures,
# return an array answer such that answer[i] is the number of days you have to
# wait after the i^th day to get a warmer temperature. If there is no future
# day for which this is possible, keep answer[i] == 0 instead.
#
# Example 1:
#
# Input: temperatures = [73,74,75,71,69,72,76,73]
# Output: [1,1,4,2,1,1,0,0]
#
# Example 2:
#
# Input: temperatures = [30,40,50,60]
# Output: [1,1,1,0]
#
# Example 3:
#
# Input: temperatures = [30,60,90]
# Output: [1,1,0]
#
# Constraints:
#
# 1 <= temperatures.length <= 10^5
#
# 30 <= temperatures[i] <= 100
#


# @lc code=start
from typing import List


class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        """
        Interview explanation:
        Monotonic decreasing stack of indices. For each day i, pop cooler days
        whose next warmer day is i; answer[popped] = i - popped.

        Algorithm:
        - ans = [0]*n; stack = []
        - For i, t in enumerate(temperatures):
          while stack and temperatures[stack[-1]] < t:
            j = stack.pop(); ans[j] = i - j
          stack.append(i)

        Complexity: O(n) time, O(n) space.
        """
        n = len(temperatures)
        ans = [0] * n
        stack: List[int] = []
        for i, t in enumerate(temperatures):
            while stack and temperatures[stack[-1]] < t:
                j = stack.pop()
                ans[j] = i - j
            stack.append(i)
        return ans
# @lc code=end

