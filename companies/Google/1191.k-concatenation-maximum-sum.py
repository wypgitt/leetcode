#
# @lc app=leetcode id=1191 lang=python3
#
# [1191] K-Concatenation Maximum Sum
#
# https://leetcode.com/problems/k-concatenation-maximum-sum/description/
#
# algorithms
# Medium (25.95%)
# Likes:    1523
# Dislikes: 134
# Total Accepted:    47.5K
# Total Submissions: 183K
# Testcase Example:  "[1,2]"
#
# Given an integer array arr and an integer k, modify the array by repeating it
# k times.
#
# For example, if arr = [1, 2] and k = 3 then the modified array will be [1, 2,
# 1, 2, 1, 2].
#
# Return the maximum sub-array sum in the modified array. Note that the length
# of the sub-array can be 0 and its sum in that case is 0.
#
# As the answer can be very large, return the answer modulo 10^9 + 7.
#
# Example 1:
#
# Input: arr = [1,2], k = 3
# Output: 9
#
# Example 2:
#
# Input: arr = [1,-2,1], k = 5
# Output: 2
#
# Example 3:
#
# Input: arr = [-1,-2], k = 7
# Output: 0
#
# Constraints:
#
# 1 <= arr.length <= 10^5
#
# 1 <= k <= 10^5
#
# -10^4 <= arr[i] <= 10^4
#

# @lc code=start

from typing import List


class Solution:
    def kConcatenationMaxSum(self, arr: List[int], k: int) -> int:
        """
        Interview explanation:
        Max subarray sum over arr repeated k times (empty → 0). Within one
        copy: Kadane. Across copies: max_suffix + max_prefix, and if total
        sum > 0 insert (k-2) full copies between them.

        Algorithm:
        - kadane(arr); max prefix / suffix sums (can be 0 if negative).
        - If k==1: max(0, kadane).
        - Else: max(kadane, prefix+suffix + max(0, k-2)*total if we only add
          middle when total>0: prefix+suffix+(k-2)*total when total>0 else
          prefix+suffix). Clamp at 0; mod 10^9+7.

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7

        def kadane(nums: List[int]) -> int:
            best = cur = 0
            for x in nums:
                cur = max(0, cur + x)
                best = max(best, cur)
            return best

        one = kadane(arr)
        if k == 1:
            return one % MOD

        total = sum(arr)
        pref = cur = 0
        for x in arr:
            cur += x
            pref = max(pref, cur)
        suf = cur = 0
        for x in reversed(arr):
            cur += x
            suf = max(suf, cur)

        if total > 0:
            cross = suf + pref + (k - 2) * total
        else:
            cross = suf + pref
        return max(0, one, cross) % MOD
# @lc code=end
