#
# @lc app=leetcode id=2289 lang=python3
#
# [2289] Steps to Make Array Non-decreasing
#
# https://leetcode.com/problems/steps-to-make-array-non-decreasing/description/
#
# algorithms
# Medium (25.12%)
# Likes:    1426
# Dislikes: 150
# Total Accepted:    32.9K
# Total Submissions: 131K
# Testcase Example:  "[5,3,4,4,7,3,6,11,8,5,11]"
#
# You are given a 0-indexed integer array nums. In one step, remove all elements
# nums[i] where nums[i - 1] > nums[i] for all 0 < i < nums.length.
#
# Return the number of steps performed until nums becomes a non-decreasing
# array.
#
#
#
# Example 1:
#
# Input: nums = [5,3,4,4,7,3,6,11,8,5,11]
# Output: 3
# Explanation: The following are the steps performed:
# - Step 1: [5,3,4,4,7,3,6,11,8,5,11] becomes [5,4,4,7,6,11,11]
# - Step 2: [5,4,4,7,6,11,11] becomes [5,4,7,11,11]
# - Step 3: [5,4,7,11,11] becomes [5,7,11,11]
# [5,7,11,11] is a non-decreasing array. Therefore, we return 3.
#
# Example 2:
#
# Input: nums = [4,5,7,7,13]
# Output: 0
# Explanation: nums is already a non-decreasing array. Therefore, we return 0.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^5
#
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def totalSteps(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Each step remove all nums[i] with nums[i-1] > nums[i] simultaneously.
        Return steps until non-decreasing.

        Algorithm:
        - Monotonic decreasing stack of (value, steps_to_remove); track max steps.

        Complexity: O(n) time, O(n) space.
        """
        stack = []  # (val, steps)
        ans = 0
        for x in nums:
            steps = 0
            while stack and stack[-1][0] <= x:
                steps = max(steps, stack.pop()[1])
            if stack:
                steps += 1
            else:
                steps = 0
            ans = max(ans, steps)
            stack.append((x, steps))
        return ans
# @lc code=end
