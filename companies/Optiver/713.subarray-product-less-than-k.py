#
# @lc app=leetcode id=713 lang=python3
#
# [713] Subarray Product Less Than K
#
# https://leetcode.com/problems/subarray-product-less-than-k/description/
#
# algorithms
# Medium (54.84%)
# Likes:    7641
# Dislikes: 237
# Total Accepted:    659K
# Total Submissions: 1.2M
# Testcase Example:  "[686, 28, 455, 675, 605, 29, 942, 48, 502, 889, 854, 206, 231, 796, 272, 565, 887, 969, 558, 13, 22, 455, 145, 804, 15]"
#
# Given an array of integers nums and an integer k, return the number of
# contiguous subarrays where the product of all the elements in the subarray is
# strictly less than k.
#
# Example 1:
#
# Input: nums = [10,5,2,6], k = 100
# Output: 8
# Explanation: The 8 subarrays that have product less than 100 are:
# [10], [5], [2], [6], [10, 5], [5, 2], [2, 6], [5, 2, 6]
# Note that [10, 5, 2] is not included as the product of 100 is not strictly
# less than k.
#
# Example 2:
#
# Input: nums = [1,2,3], k = 0
# Output: 0
#
# Constraints:
#
# 1 <= nums.length <= 3 * 10^4
#
# 1 <= nums[i] <= 1000
#
# 0 <= k <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def numSubarrayProductLessThanK(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count contiguous subarrays with product < k. Sliding window: expand
        right multiplying; shrink left while product >= k; all windows ending
        at right with start in [left, right] are valid (right-left+1).

        Algorithm:
        - If k <= 1 return 0. prod=1, left=0, ans=0; for right: prod*=nums[right];
          while prod>=k: prod//=nums[left]; left++. ans += right-left+1.

        Complexity: O(n) time, O(1) space.
        """
        if k <= 1:
            return 0
        prod = 1
        left = ans = 0
        for right, x in enumerate(nums):
            prod *= x
            while prod >= k:
                prod //= nums[left]
                left += 1
            ans += right - left + 1
        return ans
# @lc code=end
