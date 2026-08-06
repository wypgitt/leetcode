#
# @lc app=leetcode id=3350 lang=python3
#
# [3350] Adjacent Increasing Subarrays Detection II
#
# https://leetcode.com/problems/adjacent-increasing-subarrays-detection-ii/description/
#
# algorithms
# Medium (58.89%)
# Likes:    494
# Dislikes: 22
# Total Accepted:    121.5K
# Total Submissions: 206.3K
# Testcase Example:  "[2,5,7,8,9,2,3,4,3,1]"
#
#
# Given an array nums of n integers, your task is to find the maximum
# value of k for which there exist two adjacent subarrays of length k
# each, such that both subarrays are strictly increasing. Specifically,
# check if there are two subarrays of length k starting at indices a and b
# (a < b), where:
#
# Both subarrays nums[a..a + k - 1] and nums[b..b + k - 1] are strictly
# increasing.
#
# The subarrays must be adjacent, meaning b = a + k.
#
# Return the maximum possible value of k.
#
# A subarray is a contiguous non-empty sequence of elements within an
# array.
#
# Example 1:
#
# Input: nums = [2,5,7,8,9,2,3,4,3,1]
#
# Output: 3
#
# Explanation:
#
# The subarray starting at index 2 is [7, 8, 9], which is strictly
# increasing.
#
# The subarray starting at index 5 is [2, 3, 4], which is also strictly
# increasing.
#
# These two subarrays are adjacent, and 3 is the maximum possible value of
# k for which two such adjacent strictly increasing subarrays exist.
#
# Example 2:
#
# Input: nums = [1,2,3,4,4,4,4,5,6,7]
#
# Output: 2
#
# Explanation:
#
# The subarray starting at index 0 is [1, 2], which is strictly
# increasing.
#
# The subarray starting at index 2 is [3, 4], which is also strictly
# increasing.
#
# These two subarrays are adjacent, and 2 is the maximum possible value of
# k for which two such adjacent strictly increasing subarrays exist.
#
# Constraints:
#
# 2 <= nums.length <= 2 * 10^5
#
# -10^9 <= nums[i] <= 10^9
#

# @lc code=start

from typing import List


class Solution:
    def maxIncreasingSubarrays(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Largest k with two adjacent strictly increasing length-k subarrays.
        Within one increasing run of length L, k ≤ L//2; across two runs of
        lengths a,b, k ≤ min(a,b).

        Algorithm:
        - Scan runs; track previous and current strictly-increasing lengths.
        - ans = max(cur//2, min(prev, cur)) over the scan.

        Complexity: O(n) time, O(1) space.
        """
        ans = prev = cur = 0
        for i, x in enumerate(nums):
            if i and x > nums[i - 1]:
                cur += 1
            else:
                prev, cur = cur, 1
            ans = max(ans, cur // 2, min(prev, cur))
        return ans
# @lc code=end
