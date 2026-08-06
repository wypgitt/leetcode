#
# @lc app=leetcode id=3134 lang=python3
#
# [3134] Find the Median of the Uniqueness Array
#
# https://leetcode.com/problems/find-the-median-of-the-uniqueness-array/description/
#
# algorithms
# Hard (30.60%)
# Likes:    180
# Dislikes: 13
# Total Accepted:    9.4K
# Total Submissions: 30.8K
# Testcase Example:  "[1,2,3]"
#
#
# You are given an integer array nums. The uniqueness array of nums is the
# sorted array that contains the number of distinct elements of all the
# subarrays of nums. In other words, it is a sorted array consisting of
# distinct(nums[i..j]), for all 0 <= i <= j < nums.length.
#
# Here, distinct(nums[i..j]) denotes the number of distinct elements in
# the subarray that starts at index i and ends at index j.
#
# Return the median of the uniqueness array of nums.
#
# Note that the median of an array is defined as the middle element of the
# array when it is sorted in non-decreasing order. If there are two
# choices for a median, the smaller of the two values is taken.
#
# Example 1:
#
# Input: nums = [1,2,3]
#
# Output: 1
#
# Explanation:
#
# The uniqueness array of nums is [distinct(nums[0..0]),
# distinct(nums[1..1]), distinct(nums[2..2]), distinct(nums[0..1]),
# distinct(nums[1..2]), distinct(nums[0..2])] which is equal to [1, 1, 1,
# 2, 2, 3]. The uniqueness array has a median of 1. Therefore, the answer
# is 1.
#
# Example 2:
#
# Input: nums = [3,4,3,4,5]
#
# Output: 2
#
# Explanation:
#
# The uniqueness array of nums is [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3,
# 3, 3]. The uniqueness array has a median of 2. Therefore, the answer is
# 2.
#
# Example 3:
#
# Input: nums = [4,3,5,4]
#
# Output: 2
#
# Explanation:
#
# The uniqueness array of nums is [1, 1, 1, 1, 2, 2, 2, 3, 3, 3]. The
# uniqueness array has a median of 2. Therefore, the answer is 2.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def medianOfUniquenessArray(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Uniqueness array = sorted distinct-counts of all subarrays. Return its
        median (lower middle when even length).

        Algorithm:
        - Binary search median M. Count subarrays with at most M distinct via
          sliding window; need that count >= (total_subarrays + 1) // 2.
        - Smallest such M is the median.

        Complexity: O(n log n) time, O(n) space.
        """
        n = len(nums)
        total = n * (n + 1) // 2
        need = (total + 1) // 2

        def count_at_most(k: int) -> int:
            freq: dict = defaultdict(int)
            left = 0
            distinct = 0
            ans = 0
            for right, x in enumerate(nums):
                if freq[x] == 0:
                    distinct += 1
                freq[x] += 1
                while distinct > k:
                    freq[nums[left]] -= 1
                    if freq[nums[left]] == 0:
                        distinct -= 1
                    left += 1
                ans += right - left + 1
            return ans

        lo, hi = 1, n
        while lo < hi:
            mid = (lo + hi) // 2
            if count_at_most(mid) >= need:
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
