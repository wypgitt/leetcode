#
# @lc app=leetcode id=16 lang=python3
#
# [16] 3Sum Closest
#
# https://leetcode.com/problems/3sum-closest/description/
#
# algorithms
# Medium (48.50%)
# Likes:    11671
# Dislikes: 623
# Total Accepted:    1.8M
# Total Submissions: 3.8M
# Testcase Example:  '[-1,2,1,-4]\n1'
#
# Given an integer array nums of length n and an integer target, find three
# integers at distinct indices in nums such that the sum is closest to target.
# 
# Return the sum of the three integers.
# 
# You may assume that each input would have exactly one solution.
# 
# 
# Example 1:
# 
# 
# Input: nums = [-1,2,1,-4], target = 1
# Output: 2
# Explanation: The sum that is closest to the target is 2. (-1 + 2 + 1 = 2).
# 
# 
# Example 2:
# 
# 
# Input: nums = [0,0,0], target = 1
# Output: 0
# Explanation: The sum that is closest to the target is 0. (0 + 0 + 0 = 0).
# 
# 
# 
# Constraints:
# 
# 
# 3 <= nums.length <= 500
# -1000 <= nums[i] <= 1000
# -10^4 <= target <= 10^4
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def threeSumClosest(self, nums: List[int], target: int) -> int:
        """
        Interview explanation:
        Like 3Sum, sorting lets us fix one value and use two pointers for the
        remaining pair. Instead of collecting exact matches, keep the sum with
        the smallest absolute difference from target. Pointer movement is still
        valid because increasing left raises the sum and decreasing right lowers
        it in sorted order.

        Edge cases and tests:
        - Exactly three numbers return their sum.
        - Exact target can return immediately.
        - Negative and positive mixes are handled by sorted pointer movement.

        Complexity: O(n^2) time, O(1) extra space after in-place sort.
        """
        nums.sort()
        closest = nums[0] + nums[1] + nums[2]

        for i in range(len(nums) - 2):
            left, right = i + 1, len(nums) - 1
            while left < right:
                total = nums[i] + nums[left] + nums[right]
                if abs(total - target) < abs(closest - target):
                    closest = total
                if total == target:
                    return target
                if total < target:
                    left += 1
                else:
                    right -= 1

        return closest
# @lc code=end


