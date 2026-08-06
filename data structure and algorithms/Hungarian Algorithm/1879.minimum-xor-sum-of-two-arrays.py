#
# @lc app=leetcode id=1879 lang=python3
#
# [1879] Minimum XOR Sum of Two Arrays
#
# https://leetcode.com/problems/minimum-xor-sum-of-two-arrays/description/
#
# algorithms
# Hard (51.74%)
# Likes:    727
# Dislikes: 13
# Total Accepted:    22.1K
# Total Submissions: 42.7K
# Testcase Example:  "[1,2]"
#
# You are given two integer arrays nums1 and nums2 of length n.
#
# The XOR sum of the two integer arrays is (nums1[0] XOR nums2[0]) + (nums1[1]
# XOR nums2[1]) + ... + (nums1[n - 1] XOR nums2[n - 1]) (0-indexed).
#
# For example, the XOR sum of [1,2,3] and [3,2,1] is equal to (1 XOR 3) + (2
# XOR 2) + (3 XOR 1) = 2 + 0 + 2 = 4.
#
# Rearrange the elements of nums2 such that the resulting XOR sum is minimized.
#
# Return the XOR sum after the rearrangement.
#
# Example 1:
#
# Input: nums1 = [1,2], nums2 = [2,3]
# Output: 2
# Explanation: Rearrange nums2 so that it becomes [3,2].
# The XOR sum is (1 XOR 3) + (2 XOR 2) = 2 + 0 = 2.
#
# Example 2:
#
# Input: nums1 = [1,0,3], nums2 = [5,3,4]
# Output: 8
# Explanation: Rearrange nums2 so that it becomes [5,4,3].
# The XOR sum is (1 XOR 5) + (0 XOR 4) + (3 XOR 3) = 4 + 4 + 0 = 8.
#
# Constraints:
#
# n == nums1.length
#
# n == nums2.length
#
# 1 <= n <= 14
#
# 0 <= nums1[i], nums2[i] <= 10^7
#

# @lc code=start
from typing import List


class Solution:
    def minimumXORSum(self, nums1: List[int], nums2: List[int]) -> int:
        """
        Interview explanation:
        Rearrange nums2 to minimize sum (nums1[i] XOR nums2[i]). Assignment
        problem on n≤14 → DP over bitmasks of used nums2 indices.

        Algorithm (bitmask DP):
        - dp[mask] = min cost assigning first popcount(mask) of nums1 to used bits.
        - Transition: for unused j, try nums1[i]^nums2[j].

        Complexity: O(n^2 * 2^n) time, O(2^n) space.
        """
        n = len(nums1)
        INF = 10**18
        dp = [INF] * (1 << n)
        dp[0] = 0
        for mask in range(1 << n):
            i = bin(mask).count("1")
            if i >= n:
                continue
            for j in range(n):
                if mask & (1 << j) == 0:
                    nmask = mask | (1 << j)
                    dp[nmask] = min(dp[nmask], dp[mask] + (nums1[i] ^ nums2[j]))
        return dp[(1 << n) - 1]
# @lc code=end
