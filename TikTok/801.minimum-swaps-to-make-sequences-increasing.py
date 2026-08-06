#
# @lc app=leetcode id=801 lang=python3
#
# [801] Minimum Swaps To Make Sequences Increasing
#
# https://leetcode.com/problems/minimum-swaps-to-make-sequences-increasing/description/
#
# algorithms
# Hard (41.84%)
# Likes:    2962
# Dislikes: 140
# Total Accepted:    102K
# Total Submissions: 244K
# Testcase Example:  "[1,3,5,4]"
#
# You are given two integer arrays of the same length nums1 and nums2. In one
# operation, you are allowed to swap nums1[i] with nums2[i].
#
# For example, if nums1 = [1,2,3,8], and nums2 = [5,6,7,4], you can swap the
# element at i = 3 to obtain nums1 = [1,2,3,4] and nums2 = [5,6,7,8].
#
# Return the minimum number of needed operations to make nums1 and nums2
# strictly increasing. The test cases are generated so that the given input
# always makes it possible.
#
# An array arr is strictly increasing if and only if arr[0] < arr[1] < arr[2] <
# ... < arr[arr.length - 1].
#
# Example 1:
#
# Input: nums1 = [1,3,5,4], nums2 = [1,2,3,7]
# Output: 1
# Explanation:
# Swap nums1[3] and nums2[3]. Then the sequences are:
# nums1 = [1, 3, 5, 7] and nums2 = [1, 2, 3, 4]
# which are both strictly increasing.
#
# Example 2:
#
# Input: nums1 = [0,3,5,8,9], nums2 = [2,1,4,6,9]
# Output: 1
#
# Constraints:
#
# 2 <= nums1.length <= 10^5
#
# nums2.length == nums1.length
#
# 0 <= nums1[i], nums2[i] <= 2 * 10^5
#

# @lc code=start

from typing import List
from functools import lru_cache


class Solution:
    def minSwap(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        At each index decide swap or not so both sequences stay strictly
        increasing. DP with two states: min swaps ending without / with a swap
        at i. Transitions check previous pair vs current with/without swap.

        Algorithm (DP):
        - keep, swap = 0, 1 for i=0.
        - For i≥1: compute nkeep, nswap from whether A[i]>A[i-1] and B same,
          and cross case A[i]>B[i-1] and B[i]>A[i-1].

        Complexity: O(n) time, O(1) space.
        """
        n = len(nums1)
        keep, swap = 0, 1
        for i in range(1, n):
            nkeep = nswap = n
            if nums1[i] > nums1[i - 1] and nums2[i] > nums2[i - 1]:
                nkeep = keep
                nswap = swap + 1
            if nums1[i] > nums2[i - 1] and nums2[i] > nums1[i - 1]:
                nkeep = min(nkeep, swap)
                nswap = min(nswap, keep + 1)
            keep, swap = nkeep, nswap
        return min(keep, swap)

    def minSwap_memo(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Top-down memo: dfs(i, swapped) = min swaps from i given whether i-1
        was swapped. Same state machine as bottom-up DP.

        Algorithm:
        - At i, try keep or swap if valid vs prev; memoize.

        Complexity: O(n) time, O(n) space.
        """
        n = len(nums1)

        @lru_cache(None)
        def dfs(i: int, swapped: int) -> int:
            if i == n:
                return 0
            prev_a = nums2[i - 1] if swapped else nums1[i - 1]
            prev_b = nums1[i - 1] if swapped else nums2[i - 1]
            ans = 10**9
            # keep
            if nums1[i] > prev_a and nums2[i] > prev_b:
                ans = min(ans, dfs(i + 1, 0))
            # swap
            if nums2[i] > prev_a and nums1[i] > prev_b:
                ans = min(ans, 1 + dfs(i + 1, 1))
            return ans

        return min(dfs(1, 0), 1 + dfs(1, 1))
# @lc code=end
