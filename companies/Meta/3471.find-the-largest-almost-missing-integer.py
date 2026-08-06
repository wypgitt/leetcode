#
# @lc app=leetcode id=3471 lang=python3
#
# [3471] Find the Largest Almost Missing Integer
#
# https://leetcode.com/problems/find-the-largest-almost-missing-integer/description/
#
# algorithms
# Easy (37.43%)
# Likes:    116
# Dislikes: 46
# Total Accepted:    37.7K
# Total Submissions: 100.8K
# Testcase Example:  "[3,9,2,1,7]\n3"
#
#
# You are given an integer array nums and an integer k.
#
# An integer x is almost missing from nums if x appears in exactly one
# subarray of size k within nums.
#
# Return the largest almost missing integer from nums. If no such integer
# exists, return -1.
#
# A subarray is a contiguous sequence of elements within an array.
#
# Example 1:
#
# Input: nums = [3,9,2,1,7], k = 3
#
# Output: 7
#
# Explanation:
#
# 1 appears in 2 subarrays of size 3: [9, 2, 1] and [2, 1, 7].
#
# 2 appears in 3 subarrays of size 3: [3, 9, 2], [9, 2, 1], [2, 1, 7].
#
# 3 appears in 1 subarray of size 3: [3, 9, 2].
#
# 7 appears in 1 subarray of size 3: [2, 1, 7].
#
# 9 appears in 2 subarrays of size 3: [3, 9, 2], and [9, 2, 1].
#
# We return 7 since it is the largest integer that appears in exactly one
# subarray of size k.
#
# Example 2:
#
# Input: nums = [3,9,7,2,1,7], k = 4
#
# Output: 3
#
# Explanation:
#
# 1 appears in 2 subarrays of size 4: [9, 7, 2, 1], [7, 2, 1, 7].
#
# 2 appears in 3 subarrays of size 4: [3, 9, 7, 2], [9, 7, 2, 1], [7, 2,
# 1, 7].
#
# 3 appears in 1 subarray of size 4: [3, 9, 7, 2].
#
# 7 appears in 3 subarrays of size 4: [3, 9, 7, 2], [9, 7, 2, 1], [7, 2,
# 1, 7].
#
# 9 appears in 2 subarrays of size 4: [3, 9, 7, 2], [9, 7, 2, 1].
#
# We return 3 since it is the largest and only integer that appears in
# exactly one subarray of size k.
#
# Example 3:
#
# Input: nums = [0,0], k = 1
#
# Output: -1
#
# Explanation:
#
# There is no integer that appears in only one subarray of size 1.
#
# Constraints:
#
# 1 <= nums.length <= 50
#
# 0 <= nums[i] <= 50
#
# 1 <= k <= nums.length
#

# @lc code=start
import collections
from typing import List


class Solution:
    def largestInteger(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Count how many length-k windows contain each value. Only special cases
        matter: k == n (whole array), k == 1 (unique elements), or endpoints
        when 1 < k < n (only ends can appear in exactly one window).

        Algorithm:
        - If k == n: return max(nums).
        - If k == 1: return max unique element (freq == 1), else -1.
        - Else: among nums[0] and nums[-1], keep those with global freq 1;
          return their max or -1.

        Complexity: O(n) time, O(U) space.
        """
        if k == len(nums):
            return max(nums)
        count = collections.Counter(nums)
        if k == 1:
            return max((x for x in nums if count[x] == 1), default=-1)
        return max(
            nums[0] if count[nums[0]] == 1 else -1,
            nums[-1] if count[nums[-1]] == 1 else -1,
        )

    def largestInteger_brute(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: explicitly count window presence per value.

        Algorithm:
        - For each window, add distinct values to a Counter of window hits.
        - Return max value with count == 1, else -1.

        Complexity: O(n k) time, O(U) space.
        """
        n = len(nums)
        hits = collections.Counter()
        for i in range(n - k + 1):
            for x in set(nums[i : i + k]):
                hits[x] += 1
        candidates = [x for x, c in hits.items() if c == 1]
        return max(candidates) if candidates else -1
# @lc code=end

