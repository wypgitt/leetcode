#
# @lc app=leetcode id=2653 lang=python3
#
# [2653] Sliding Subarray Beauty
#
# https://leetcode.com/problems/sliding-subarray-beauty/description/
#
# algorithms
# Medium (37.81%)
# Likes:    761
# Dislikes: 141
# Total Accepted:    37.8K
# Total Submissions: 99.8K
# Testcase Example:  "[1,-1,-3,-2,3]\n3\n2"
#
# Given an integer array nums containing n integers, find the beauty of each
# subarray of size k.
#
# The beauty of a subarray is the x^th smallest integer in the subarray if it is
# negative, or 0 if there are fewer than x negative integers.
#
# Return an integer array containing n - k + 1 integers, which denote the beauty
# of the subarrays in order from the first index in the array.
#
#
#
#
# A subarray is a contiguous non-empty sequence of elements within an array.
#
#
#
#
#
# Example 1:
#
# Input: nums = [1,-1,-3,-2,3], k = 3, x = 2
# Output: [-1,-2,-2]
# Explanation: There are 3 subarrays with size k = 3.
# The first subarray is [1, -1, -3] and the 2^nd smallest negative integer is
# -1.
# The second subarray is [-1, -3, -2] and the 2^nd smallest negative integer is
# -2.
# The third subarray is [-3, -2, 3] and the 2^nd smallest negative integer is
# -2.
#
# Example 2:
#
# Input: nums = [-1,-2,-3,-4,-5], k = 2, x = 2
# Output: [-1,-2,-3,-4]
# Explanation: There are 4 subarrays with size k = 2.
# For [-1, -2], the 2^nd smallest negative integer is -1.
# For [-2, -3], the 2^nd smallest negative integer is -2.
# For [-3, -4], the 2^nd smallest negative integer is -3.
# For [-4, -5], the 2^nd smallest negative integer is -4.
#
# Example 3:
#
# Input: nums = [-3,1,2,-3,0,-3], k = 2, x = 1
# Output: [-3,0,-3,-3,-3]
# Explanation: There are 5 subarrays with size k = 2.
# For [-3, 1], the 1^st smallest negative integer is -3.
# For [1, 2], there is no negative integer so the beauty is 0.
# For [2, -3], the 1^st smallest negative integer is -3.
# For [-3, 0], the 1^st smallest negative integer is -3.
# For [0, -3], the 1^st smallest negative integer is -3.
#
#
#
# Constraints:
#
#
# n == nums.length
#
#
# 1 <= n <= 10^5
#
#
# 1 <= k <= n
#
#
# 1 <= x <= k
#
#
# -50 <= nums[i] <= 50
#

# @lc code=start

from typing import List


class Solution:
    def getSubarrayBeauty(self, nums: List[int], k: int, x: int) -> List[int]:
        """
        Interview explanation:
        For each window of size k, beauty = x-th smallest negative (or 0 if fewer than x negatives).

        Algorithm:
        - Maintain freq of values in [-50, -1]. Slide window; scan freqs for x-th smallest.

        Complexity: O(n * 50) time, O(1) extra space.
        """
        freq = [0] * 51  # freq[v] counts value -v
        ans: List[int] = []

        def beauty() -> int:
            need = x
            for v in range(50, 0, -1):
                need -= freq[v]
                if need <= 0:
                    return -v
            return 0

        for i, num in enumerate(nums):
            if num < 0:
                freq[-num] += 1
            if i >= k:
                old = nums[i - k]
                if old < 0:
                    freq[-old] -= 1
            if i >= k - 1:
                ans.append(beauty())
        return ans
# @lc code=end
