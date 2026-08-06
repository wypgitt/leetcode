#
# @lc app=leetcode id=53 lang=python3
#
# [53] Maximum Subarray
#
# https://leetcode.com/problems/maximum-subarray/description/
#
# algorithms
# Medium (53.27%)
# Likes:    37891
# Dislikes: 1614
# Total Accepted:    6.1M
# Total Submissions: 11.4M
# Testcase Example:  '[-2,1,-3,4,-1,2,1,-5,4]'
#
# Given an integer array nums, find the subarray with the largest sum, and
# return its sum.
# 
# 
# Example 1:
# 
# 
# Input: nums = [-2,1,-3,4,-1,2,1,-5,4]
# Output: 6
# Explanation: The subarray [4,-1,2,1] has the largest sum 6.
# 
# 
# Example 2:
# 
# 
# Input: nums = [1]
# Output: 1
# Explanation: The subarray [1] has the largest sum 1.
# 
# 
# Example 3:
# 
# 
# Input: nums = [5,4,-1,7,8]
# Output: 23
# Explanation: The subarray [5,4,-1,7,8] has the largest sum 23.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 10^5
# -10^4 <= nums[i] <= 10^4
# 
# 
# 
# Follow up: If you have figured out the O(n) solution, try coding another
# solution using the divide and conquer approach, which is more subtle.
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def maxSubArray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Kadane's algorithm tracks the best subarray ending at the current index.
        Either extend the previous subarray or start fresh at nums[i]. The global
        maximum over those local best values is the answer.

        Edge cases and tests:
        - All negative values return the largest single value.
        - One element returns itself.
        - A negative prefix is dropped when starting fresh is better.

        Complexity: O(n) time, O(1) space.
        """
        current = best = nums[0]
        for num in nums[1:]:
            current = max(num, current + num)
            best = max(best, current)
        return best
# @lc code=end


