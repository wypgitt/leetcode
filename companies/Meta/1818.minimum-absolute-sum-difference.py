#
# @lc app=leetcode id=1818 lang=python3
#
# [1818] Minimum Absolute Sum Difference
#
# https://leetcode.com/problems/minimum-absolute-sum-difference/description/
#
# algorithms
# Medium (32.71%)
# Likes:    1112
# Dislikes: 81
# Total Accepted:    33.9K
# Total Submissions: 104K
# Testcase Example:  "[1,7,5]"
#
# You are given two positive integer arrays nums1 and nums2, both of length n.
#
# The absolute sum difference of arrays nums1 and nums2 is defined as the sum
# of |nums1[i] - nums2[i]| for each 0 <= i < n (0-indexed).
#
# You can replace at most one element of nums1 with any other element in nums1
# to minimize the absolute sum difference.
#
# Return the minimum absolute sum difference after replacing at most one
# element in the array nums1. Since the answer may be large, return it modulo
# 10^9 + 7.
#
# |x| is defined as:
#
# x if x >= 0, or
#
# -x if x < 0.
#
# Example 1:
#
# Input: nums1 = [1,7,5], nums2 = [2,3,5]
# Output: 3
# Explanation: There are two possible optimal solutions:
# - Replace the second element with the first: [1,7,5] => [1,1,5], or
# - Replace the second element with the third: [1,7,5] => [1,5,5].
# Both will yield an absolute sum difference of |1-2| + (|1-3| or |5-3|) +
# |5-5| = 3.
#
# Example 2:
#
# Input: nums1 = [2,4,6,8,10], nums2 = [2,4,6,8,10]
# Output: 0
# Explanation: nums1 is equal to nums2 so no replacement is needed. This will
# result in an
# absolute sum difference of 0.
#
# Example 3:
#
# Input: nums1 = [1,10,4,4,2,7], nums2 = [9,3,5,1,7,4]
# Output: 20
# Explanation: Replace the first element with the second: [1,10,4,4,2,7] =>
# [10,10,4,4,2,7].
# This yields an absolute sum difference of |10-9| + |10-3| + |4-5| + |4-1| +
# |2-7| + |7-4| = 20
#
# Constraints:
#
# n == nums1.length
#
# n == nums2.length
#
# 1 <= n <= 10^5
#
# 1 <= nums1[i], nums2[i] <= 10^5
#

# @lc code=start
from typing import List
import bisect


class Solution:
    def minAbsoluteSumDiff(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Sum |a[i]-b[i]|; may replace one a[i] with any other a[j] to minimize sum.
        For each i, best replacement is closest value in sorted nums1 to nums2[i].

        Algorithm (sort + binary search):
        - base = sum |a-b|; sorted unique nums1; for each i compute max saving
          base_diff - min |cand-b[i]|; answer (base-max_save)%MOD.

        Complexity: O(n log n) time, O(n) space.
        """
        MOD = 10**9 + 7
        n = len(nums1)
        base = 0
        diffs = []
        for a, b in zip(nums1, nums2):
            d = abs(a - b)
            base += d
            diffs.append(d)
        sorted_a = sorted(nums1)
        best_save = 0
        for i, b in enumerate(nums2):
            if diffs[i] == 0:
                continue
            j = bisect.bisect_left(sorted_a, b)
            for idx in (j - 1, j):
                if 0 <= idx < n:
                    best_save = max(best_save, diffs[i] - abs(sorted_a[idx] - b))
        return (base - best_save) % MOD
# @lc code=end
