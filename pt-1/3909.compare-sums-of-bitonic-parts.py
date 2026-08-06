#
# @lc app=leetcode id=3909 lang=python3
#
# [3909] Compare Sums of Bitonic Parts
#
# https://leetcode.com/problems/compare-sums-of-bitonic-parts/description/
#
# algorithms
# Medium (53.63%)
# Likes:    25
# Dislikes: 2
# Total Accepted:    26.2K
# Total Submissions: 48.8K
# Testcase Example:  "[1,3,2,1]"
#
#
# You are given a bitonic array nums of length n.
#
# Split the array into two parts:
#
# Ascending part: from index 0 to the peak element (inclusive).
#
# Descending part: from the peak element to index n - 1 (inclusive).
#
# The peak element belongs to both parts.
#
# Return:
#
# 0 if the sum of the ascending part is greater.
#
# 1 if the sum of the descending part is greater.
#
# -1 if both sums are equal.
#
# Notes:
#
# A bitonic array is an array that is strictly increasing up to a single
# peak element and then strictly decreasing.
#
# An array is said to be strictly increasing if each element is strictly
# greater than its previous one (if exists).
#
# An array is said to be strictly decreasing if each element is strictly
# smaller than its previous one (if exists).
#
# Example 1:
#
# Input: nums = [1,3,2,1]
#
# Output: 1
#
# Explanation:
#
# Peak element is nums[1] = 3
#
# Ascending part = [1, 3], sum is 1 + 3 = 4
#
# Descending part = [3, 2, 1], sum is 3 + 2 + 1 = 6
#
# Since the descending part has a larger sum, return 1.
#
# Example 2:
#
# Input: nums = [2,4,5,2]
#
# Output: 0
#
# Explanation:
#
# Peak element is nums[2] = 5
#
# Ascending part = [2, 4, 5], sum is 2 + 4 + 5 = 11
#
# Descending part = [5, 2], sum is 5 + 2 = 7
#
# Since the ascending part has a larger sum, return 0.
#
# Example 3:
#
# Input: nums = [1,2,4,3]
#
# Output: -1
#
# Explanation:
#
# Peak element is nums[2] = 4
#
# Ascending part = [1, 2, 4], sum is 1 + 2 + 4 = 7
#
# Descending part = [4, 3], sum is 4 + 3 = 7
#
# Since both parts have equal sums, return -1.
#
# Constraints:
#
# 3 <= n == nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#
# nums is a bitonic array.
#

# @lc code=start
class Solution:
    def compareBitonicSums(self, nums: list[int]) -> int:
        """
        Interview explanation:
        Bitonic array: find the peak, compare sum of ascending part [0..peak]
        vs descending part [peak..n-1] (peak counted in both).

        Algorithm:
        - Locate peak index (unique maximum).
        - Sum both sides; return 0 / 1 / -1 for ascending greater / descending
          greater / equal.

        Complexity: O(n) time, O(1) space.
        """
        peak = max(range(len(nums)), key=nums.__getitem__)

        ascending_sum = 0
        for i in range(peak + 1):
            ascending_sum += nums[i]

        descending_sum = 0
        for i in range(peak, len(nums)):
            descending_sum += nums[i]

        if ascending_sum > descending_sum:
            return 0
        if descending_sum > ascending_sum:
            return 1
        return -1
# @lc code=end
