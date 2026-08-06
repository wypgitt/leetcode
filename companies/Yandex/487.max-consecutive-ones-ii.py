#
# @lc app=leetcode id=487 lang=python3
#
# [487] Max Consecutive Ones II
#
# https://leetcode.com/problems/max-consecutive-ones-ii/description/
#
# algorithms
# Medium (52.10%)
# Likes:    1614
# Dislikes: 27
# Total Accepted:    186.2K
# Total Submissions: 357.5K
# Testcase Example:  "[1,0,1,1,0]"
#
#
# Given a binary array nums, return the maximum number of consecutive 1's
# in the array if you can flip at most one 0.
#
# Example 1:
#
# Input: nums = [1,0,1,1,0]
# Output: 4
# Explanation:
# - If we flip the first zero, nums becomes [1,1,1,1,0] and we have 4
# consecutive ones.
# - If we flip the second zero, nums becomes [1,0,1,1,1] and we have 3
# consecutive ones.
# The max number of consecutive ones is 4.
#
# Example 2:
#
# Input: nums = [1,0,1,1,0,1]
# Output: 4
# Explanation:
# - If we flip the first zero, nums becomes [1,1,1,1,0,1] and we have 4
# consecutive ones.
# - If we flip the second zero, nums becomes [1,0,1,1,1,1] and we have 4
# consecutive ones.
# The max number of consecutive ones is 4.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# nums[i] is either 0 or 1.
#
# Follow up: What if the input numbers come in one by one as an infinite
# stream? In other words, you can't store all numbers coming from the
# stream as it's too large to hold in memory. Could you solve it
# efficiently?
#
# @lc code=start
from typing import List


class Solution:
    def findMaxConsecutiveOnes(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Premium. Longest consecutive 1s after flipping at most one 0.
        Sliding window: expand right; when zeros in window exceed 1, move left
        past a zero. Track max window length.

        Algorithm:
        - left = zeros = ans = 0
        - For right, x in nums: if x==0: zeros++
          while zeros > 1: if nums[left]==0: zeros--; left++
          ans = max(ans, right-left+1)

        Complexity: O(n) time, O(1) space.
        """
        left = zeros = ans = 0
        for right, x in enumerate(nums):
            if x == 0:
                zeros += 1
            while zeros > 1:
                if nums[left] == 0:
                    zeros -= 1
                left += 1
            ans = max(ans, right - left + 1)
        return ans
# @lc code=end
