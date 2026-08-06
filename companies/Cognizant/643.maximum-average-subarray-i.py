#
# @lc app=leetcode id=643 lang=python3
#
# [643] Maximum Average Subarray I
#
# https://leetcode.com/problems/maximum-average-subarray-i/description/
#
# algorithms
# Easy (48.76%)
# Likes:    4517
# Dislikes: 387
# Total Accepted:    1.3M
# Total Submissions: 2.7M
# Testcase Example:  "[1,12,-5,-6,50,3]"
#
# You are given an integer array nums consisting of n elements, and an integer
# k.
#
# Find a contiguous subarray whose length is equal to k that has the maximum
# average value and return this value. Any answer with a calculation error less
# than 10^-5 will be accepted.
#
# Example 1:
#
# Input: nums = [1,12,-5,-6,50,3], k = 4
# Output: 12.75000
# Explanation: Maximum average is (12 - 5 - 6 + 50) / 4 = 51 / 4 = 12.75
#
# Example 2:
#
# Input: nums = [5], k = 1
# Output: 5.00000
#
# Constraints:
#
# n == nums.length
#
# 1 <= k <= n <= 10^5
#
# -10^4 <= nums[i] <= 10^4
#

# @lc code=start

from typing import List


class Solution:
    def findMaxAverage(self, nums: List[int], k: int) -> float:
        """
        Interview explanation:
        Maximum average of a fixed-length k window = max sum / k. Sliding window.

        Algorithm:
        - Sum first k; slide: add nums[i], remove nums[i-k]; track max sum.
        - Return max_sum / k.

        Complexity: O(N) time, O(1) space.
        """
        window = sum(nums[:k])
        best = window
        for i in range(k, len(nums)):
            window += nums[i] - nums[i - k]
            if window > best:
                best = window
        return best / k
# @lc code=end
