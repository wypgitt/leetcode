#
# @lc app=leetcode id=1330 lang=python3
#
# [1330] Reverse Subarray To Maximize Array Value
#
# https://leetcode.com/problems/reverse-subarray-to-maximize-array-value/description/
#
# algorithms
# Hard (44.37%)
# Likes:    498
# Dislikes: 61
# Total Accepted:    9.2K
# Total Submissions: 20.8K
# Testcase Example:  "[2,3,1,5,4]"
#
# You are given an integer array nums. The value of this array is defined as
# the sum of |nums[i] - nums[i + 1]| for all 0 <= i < nums.length - 1.
#
# You are allowed to select any subarray of the given array and reverse it. You
# can perform this operation only once.
#
# Find maximum possible value of the final array.
#
# Example 1:
#
# Input: nums = [2,3,1,5,4]
# Output: 10
# Explanation: By reversing the subarray [3,1,5] the array becomes [2,5,1,3,4]
# whose value is 10.
#
# Example 2:
#
# Input: nums = [2,4,9,24,2,1,10]
# Output: 68
#
# Constraints:
#
# 2 <= nums.length <= 3 * 10^4
#
# -10^5 <= nums[i] <= 10^5
#
# The answer is guaranteed to fit in a 32-bit integer.
#

# @lc code=start
from typing import List


class Solution:
    def maxValueAfterReverse(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Value = sum |a[i]-a[i+1]|. Reverse one subarray. Base value plus max
        gain from reversing [i..j]. Classic case analysis: gain comes from
        replacing endpoints; track min of max-pair and max of min-pair among
        adjacent pairs; also check reverses touching array ends.

        Algorithm:
        - total = sum |diff|; best extra from:
          (1) reverse prefix/suffix style endpoint swaps
          (2) 2*max(0, mx-mn) where mn=min(max(a[i],a[i+1])), mx=max(min(...))

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums)
        total = sum(abs(nums[i] - nums[i + 1]) for i in range(n - 1))
        # endpoint reversals
        best = 0
        for i in range(n - 1):
            best = max(best, abs(nums[0] - nums[i + 1]) - abs(nums[i] - nums[i + 1]))
            best = max(best, abs(nums[-1] - nums[i]) - abs(nums[i] - nums[i + 1]))
        # interior
        mn = float("inf")
        mx = float("-inf")
        for i in range(n - 1):
            a, b = nums[i], nums[i + 1]
            mn = min(mn, max(a, b))
            mx = max(mx, min(a, b))
        best = max(best, 2 * (mx - mn))
        return total + best
# @lc code=end

