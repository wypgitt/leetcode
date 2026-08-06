#
# @lc app=leetcode id=2099 lang=python3
#
# [2099] Find Subsequence of Length K With the Largest Sum
#
# https://leetcode.com/problems/find-subsequence-of-length-k-with-the-largest-sum/description/
#
# algorithms
# Easy (57.28%)
# Likes:    1767
# Dislikes: 184
# Total Accepted:    184.7K
# Total Submissions: 322.4K
# Testcase Example:  "[2,1,3,3]\n2"
#
# You are given an integer array nums and an integer k. You want to find a
# subsequence of nums of length k that has the largest sum.
#
# Return any such subsequence as an integer array of length k.
#
# A subsequence is an array that can be derived from another array by deleting
# some or no elements without changing the order of the remaining elements.
#
#
#
# Example 1:
#
# Input: nums = [2,1,3,3], k = 2
# Output: [3,3]
# Explanation:
# The subsequence has the largest sum of 3 + 3 = 6.
#
# Example 2:
#
# Input: nums = [-1,-2,3,4], k = 3
# Output: [-1,3,4]
# Explanation:
# The subsequence has the largest sum of -1 + 3 + 4 = 6.
#
# Example 3:
#
# Input: nums = [3,4,3,3], k = 2
# Output: [3,4]
# Explanation:
# The subsequence has the largest sum of 3 + 4 = 7.
# Another possible subsequence is [4, 3].
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 1000
#
#
# -10^5 <= nums[i] <= 10^5
#
#
# 1 <= k <= nums.length
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def maxSubsequence(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Subsequence of length k with largest sum, preserving relative order.

        Algorithm:
        - Take k largest values by (value, index); sort chosen by index; return values.

        Complexity: O(n log k) time, O(k) space.
        """
        top = heapq.nlargest(k, range(len(nums)), key=lambda i: nums[i])
        top.sort()
        return [nums[i] for i in top]

    def maxSubsequence_sort(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        Alternate: sort indexed pairs by value, keep top k, restore order.

        Algorithm:
        - Sort (val, idx) descending; take k; sort by idx.

        Complexity: O(n log n) time, O(n) space.
        """
        idx = sorted(range(len(nums)), key=lambda i: nums[i], reverse=True)[:k]
        idx.sort()
        return [nums[i] for i in idx]
# @lc code=end
