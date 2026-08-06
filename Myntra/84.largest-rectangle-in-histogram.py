#
# @lc app=leetcode id=84 lang=python3
#
# [84] Largest Rectangle in Histogram
#
# https://leetcode.com/problems/largest-rectangle-in-histogram/description/
#
# algorithms
# Hard (50.58%)
# Likes:    19945
# Dislikes: 397
# Total Accepted:    1.7M
# Total Submissions: 3.3M
# Testcase Example:  "[2,1,5,6,2,3]"
#
# Given an array of integers heights representing the histogram's bar height
# where the width of each bar is 1, return the area of the largest rectangle in
# the histogram.
#
# Example 1:
#
# Input: heights = [2,1,5,6,2,3]
# Output: 10
# Explanation: The above is a histogram where width of each bar is 1.
# The largest rectangle is shown in the red area, which has an area = 10 units.
#
# Example 2:
#
# Input: heights = [2,4]
# Output: 4
#
# Constraints:
#
# 1 <= heights.length <= 10^5
#
# 0 <= heights[i] <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def largestRectangleArea(self, heights: List[int]) -> int:
        """
        Interview explanation:
        For each bar, the largest rectangle with that bar as the shortest uses
        the nearest strictly shorter bars on left and right as bounds.
        A monotonic increasing stack finds those bounds in one pass.

        Algorithm:
        - Append a sentinel 0 height to flush the stack.
        - While current height < height at stack top, pop and compute
          area = height[popped] * (i - new_top - 1).
        - Push index i.

        Complexity: O(n) time, O(n) space.
        """
        stack: List[int] = [-1]
        best = 0
        for i, h in enumerate(heights + [0]):
            while stack[-1] != -1 and heights[stack[-1]] > h:
                height = heights[stack.pop()]
                width = i - stack[-1] - 1
                best = max(best, height * width)
            stack.append(i)
        return best
# @lc code=end
