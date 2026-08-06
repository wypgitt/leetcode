#
# @lc app=leetcode id=1004 lang=python3
#
# [1004] Max Consecutive Ones III
#
# https://leetcode.com/problems/max-consecutive-ones-iii/description/
#
# algorithms
# Medium (68.19%)
# Likes:    10702
# Dislikes: 195
# Total Accepted:    1.5M
# Total Submissions: 2.2M
# Testcase Example:  "[1,1,1,0,0,0,1,1,1,1,0]"
#
# Given a binary array nums and an integer k, return the maximum number of
# consecutive 1's in the array if you can flip at most k 0's.
#
# Example 1:
#
# Input: nums = [1,1,1,0,0,0,1,1,1,1,0], k = 2
# Output: 6
# Explanation: [1,1,1,0,0,1,1,1,1,1,1]
# Bolded numbers were flipped from 0 to 1. The longest subarray is underlined.
#
# Example 2:
#
# Input: nums = [0,0,1,1,0,0,1,1,1,0,1,1,0,0,0,1,1,1,1], k = 3
# Output: 10
# Explanation: [0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1]
# Bolded numbers were flipped from 0 to 1. The longest subarray is underlined.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# nums[i] is either 0 or 1.
#
# 0 <= k <= nums.length
#

# @lc code=start
from typing import List


class Solution:
    def longestOnes(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Longest subarray with at most k zeros (flips). Classic sliding window:
        expand right, shrink left when zeros exceed k; track max window length.

        Algorithm:
        - left=0, zeros=0, best=0
        - For right in 0..n-1: if nums[right]==0: zeros++
          while zeros>k: if nums[left]==0: zeros--; left++
          best = max(best, right-left+1)

        Complexity: O(n) time, O(1) space.
        """
        left = zeros = best = 0
        for right, x in enumerate(nums):
            if x == 0:
                zeros += 1
            while zeros > k:
                if nums[left] == 0:
                    zeros -= 1
                left += 1
            best = max(best, right - left + 1)
        return best

    def longestOnes_binary_search(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: prefix zeros; for each right endpoint binary-search the
        leftmost left such that zeros in [left,right] <= k.

        Algorithm:
        - pref[i] = zeros in nums[:i]
        - For right: find smallest left with pref[right+1]-pref[left] <= k
        - Maximize right-left+1

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        pref = [0] * (n + 1)
        for i, x in enumerate(nums):
            pref[i + 1] = pref[i] + (x == 0)
        best = 0
        for right in range(n):
            lo, hi = 0, right + 1
            while lo < hi:
                mid = (lo + hi) // 2
                if pref[right + 1] - pref[mid] <= k:
                    hi = mid
                else:
                    lo = mid + 1
            best = max(best, right - lo + 1)
        return best
# @lc code=end
