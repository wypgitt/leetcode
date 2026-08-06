#
# @lc app=leetcode id=2865 lang=python3
#
# [2865] Beautiful Towers I
#
# https://leetcode.com/problems/beautiful-towers-i/description/
#
# algorithms
# Medium (44.86%)
# Likes:    383
# Dislikes: 60
# Total Accepted:    35.6K
# Total Submissions: 79.3K
# Testcase Example:  "[5,3,4,1,1]"
#
#
# You are given an array heights of n integers representing the number of
# bricks in n consecutive towers. Your task is to remove some bricks to
# form a mountain-shaped tower arrangement. In this arrangement, the tower
# heights are non-decreasing, reaching a maximum peak value with one or
# multiple consecutive towers and then non-increasing.
#
# Return the maximum possible sum of heights of a mountain-shaped tower
# arrangement.
#
# Example 1:
#
# Input: heights = [5,3,4,1,1]
#
# Output: 13
#
# Explanation:
#
# We remove some bricks to make heights = [5,3,3,1,1], the peak is at
# index 0.
#
# Example 2:
#
# Input: heights = [6,5,3,9,2,7]
#
# Output: 22
#
# Explanation:
#
# We remove some bricks to make heights = [3,3,3,9,2,2], the peak is at
# index 3.
#
# Example 3:
#
# Input: heights = [3,2,5,5,2,3]
#
# Output: 18
#
# Explanation:
#
# We remove some bricks to make heights = [2,2,5,5,2,2], the peak is at
# index 2 or 3.
#
# Constraints:
#
# 1 <= n == heights.length <= 10^3
#
# 1 <= heights[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maximumSumOfHeights(self, heights: List[int]) -> int:
        """
        Interview explanation:
        Build a mountain (non-decreasing to a peak, then non-increasing) with
        heights[i] <= original[i]; maximize sum. n <= 1000.

        Algorithm:
        - Try each peak i; expand left/right taking running min with heights[j].

        Complexity: O(n^2) time, O(1) extra space.
        """
        n = len(heights)
        ans = 0
        for peak in range(n):
            total = heights[peak]
            cur = heights[peak]
            for j in range(peak - 1, -1, -1):
                cur = min(cur, heights[j])
                total += cur
            cur = heights[peak]
            for j in range(peak + 1, n):
                cur = min(cur, heights[j])
                total += cur
            ans = max(ans, total)
        return ans
# @lc code=end
