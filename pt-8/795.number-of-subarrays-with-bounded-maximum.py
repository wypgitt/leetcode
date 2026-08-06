#
# @lc app=leetcode id=795 lang=python3
#
# [795] Number of Subarrays with Bounded Maximum
#
# https://leetcode.com/problems/number-of-subarrays-with-bounded-maximum/description/
#
# algorithms
# Medium (55.21%)
# Likes:    2469
# Dislikes: 136
# Total Accepted:    93.3K
# Total Submissions: 169K
# Testcase Example:  "[2,1,4,3]"
#
# Given an integer array nums and two integers left and right, return the
# number of contiguous non-empty subarrays such that the value of the maximum
# array element in that subarray is in the range [left, right].
#
# The test cases are generated so that the answer will fit in a 32-bit integer.
#
# Example 1:
#
# Input: nums = [2,1,4,3], left = 2, right = 3
# Output: 3
# Explanation: There are three subarrays that meet the requirements: [2], [2,
# 1], [3].
#
# Example 2:
#
# Input: nums = [2,9,2,5,6], left = 2, right = 8
# Output: 7
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^9
#
# 0 <= left <= right <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def numSubarrayBoundedMax(self, nums: List[int], left: int, right: int) -> int:
        """
        Interview explanation:
        Count subarrays whose maximum is in [left, right]. Equivalent to
        (# subarrays with max <= right) - (# with max <= left-1). Or one-pass:
        track last index > right (reset) and last index in [left,right]; add
        contribution of valid endings.

        Algorithm (one-pass):
        - prev_gt = prev_in = -1
        - For i,x: if x > right: prev_gt = i
          if left <= x <= right: prev_in = i
          ans += max(0, prev_in - prev_gt)

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        prev_gt = prev_in = -1
        for i, x in enumerate(nums):
            if x > right:
                prev_gt = i
            if left <= x <= right:
                prev_in = i
            ans += max(0, prev_in - prev_gt)
        return ans
# @lc code=end

