#
# @lc app=leetcode id=3312 lang=python3
#
# [3312] Sorted GCD Pair Queries
#
# https://leetcode.com/problems/sorted-gcd-pair-queries/description/
#
# algorithms
# Hard (58.47%)
# Likes:    351
# Dislikes: 24
# Total Accepted:    74.2K
# Total Submissions: 126.8K
# Testcase Example:  "[2,3,4]\n[0,2,2]"
#
#
# You are given an integer array nums of length n and an integer array
# queries.
#
# Let gcdPairs denote an array obtained by calculating the GCD of all
# possible pairs (nums[i], nums[j]), where 0 <= i < j < n, and then
# sorting these values in ascending order.
#
# For each query queries[i], you need to find the element at index
# queries[i] in gcdPairs.
#
# Return an integer array answer, where answer[i] is the value at
# gcdPairs[queries[i]] for each query.
#
# The term gcd(a, b) denotes the greatest common divisor of a and b.
#
# Example 1:
#
# Input: nums = [2,3,4], queries = [0,2,2]
#
# Output: [1,2,2]
#
# Explanation:
#
# gcdPairs = [gcd(nums[0], nums[1]), gcd(nums[0], nums[2]), gcd(nums[1],
# nums[2])] = [1, 2, 1].
#
# After sorting in ascending order, gcdPairs = [1, 1, 2].
#
# So, the answer is [gcdPairs[queries[0]], gcdPairs[queries[1]],
# gcdPairs[queries[2]]] = [1, 2, 2].
#
# Example 2:
#
# Input: nums = [4,4,2,1], queries = [5,3,1,0]
#
# Output: [4,2,1,1]
#
# Explanation:
#
# gcdPairs sorted in ascending order is [1, 1, 1, 2, 2, 4].
#
# Example 3:
#
# Input: nums = [2,2], queries = [0,0]
#
# Output: [2,2]
#
# Explanation:
#
# gcdPairs = [2].
#
# Constraints:
#
# 2 <= n == nums.length <= 10^5
#
# 1 <= nums[i] <= 5 * 10^4
#
# 1 <= queries.length <= 10^5
#
# 0 <= queries[i] < n * (n - 1) / 2
#

# @lc code=start
import bisect
from typing import List


class Solution:
    def gcdValues(self, nums: List[int], queries: List[int]) -> List[int]:
        """
        Interview explanation:
        gcdPairs is all pairwise GCDs sorted. Answer many index queries without
        materializing n^2 pairs via multiplicative counting.

        Algorithm:
        - freq[v] counts values. For each d, count pairs with d | gcd, then
          inclusion over multiples yields count of pairs with gcd == d.
        - Prefix those counts; bisect each query into the sorted gcd stream.

        Complexity: O(M log M + Q log M) with M = max(nums), O(M) space.
        """
        mx = max(nums)
        freq = [0] * (mx + 1)
        for x in nums:
            freq[x] += 1

        multiples = [0] * (mx + 1)
        for d in range(1, mx + 1):
            c = 0
            for m in range(d, mx + 1, d):
                c += freq[m]
            multiples[d] = c * (c - 1) // 2

        gcd_cnt = [0] * (mx + 1)
        for d in range(mx, 0, -1):
            gcd_cnt[d] = multiples[d]
            for m in range(2 * d, mx + 1, d):
                gcd_cnt[d] -= gcd_cnt[m]

        pref = [0] * (mx + 1)
        for d in range(1, mx + 1):
            pref[d] = pref[d - 1] + gcd_cnt[d]

        return [bisect.bisect_right(pref, q) for q in queries]
# @lc code=end
