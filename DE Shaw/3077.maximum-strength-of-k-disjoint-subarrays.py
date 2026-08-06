#
# @lc app=leetcode id=3077 lang=python3
#
# [3077] Maximum Strength of K Disjoint Subarrays
#
# https://leetcode.com/problems/maximum-strength-of-k-disjoint-subarrays/description/
#
# algorithms
# Hard (28.29%)
# Likes:    180
# Dislikes: 76
# Total Accepted:    9.2K
# Total Submissions: 32.5K
# Testcase Example:  "[1,2,3,-1,2]\n3"
#
#
# You are given an array of integers nums with length n, and a positive
# odd integer k.
#
# Select exactly k disjoint subarrays sub_1, sub_2, ..., sub_k from nums
# such that the last element of sub_i appears before the first element of
# sub_{i+1} for all 1 <= i <= k-1. The goal is to maximize their combined
# strength.
#
# The strength of the selected subarrays is defined as:
#
# strength = k * sum(sub_1)- (k - 1) * sum(sub_2) + (k - 2) * sum(sub_3) -
# ... - 2 * sum(sub_{k-1}) + sum(sub_k)
#
# where sum(sub_i) is the sum of the elements in the i-th subarray.
#
# Return the maximum possible strength that can be obtained from selecting
# exactly k disjoint subarrays from nums.
#
# Note that the chosen subarrays don't need to cover the entire array.
#
# Example 1:
#
# Input: nums = [1,2,3,-1,2], k = 3
#
# Output: 22
#
# Explanation:
#
# The best possible way to select 3 subarrays is: nums[0..2], nums[3..3],
# and nums[4..4]. The strength is calculated as follows:
#
# strength = 3 * (1 + 2 + 3) - 2 * (-1) + 2 = 22
#
# Example 2:
#
# Input: nums = [12,-2,-2,-2,-2], k = 5
#
# Output: 64
#
# Explanation:
#
# The only possible way to select 5 disjoint subarrays is: nums[0..0],
# nums[1..1], nums[2..2], nums[3..3], and nums[4..4]. The strength is
# calculated as follows:
#
# strength = 5 * 12 - 4 * (-2) + 3 * (-2) - 2 * (-2) + (-2) = 64
#
# Example 3:
#
# Input: nums = [-1,-2,-3], k = 1
#
# Output: -1
#
# Explanation:
#
# The best possible way to select 1 subarray is: nums[0..0]. The strength
# is -1.
#
# Constraints:
#
# 1 <= n <= 10^4
#
# -10^9 <= nums[i] <= 10^9
#
# 1 <= k <= n
#
# 1 <= n * k <= 10^6
#
# k is odd.
#

# @lc code=start
from typing import List


class Solution:
    def maximumStrength(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Pick exactly k ordered disjoint subarrays; strength weights them by
        +(k), -(k-1), +(k-2), ... . DP over prefix and #subarrays used.

        Algorithm:
        - mult[j] = (k-j+1) * (+1 if j odd else -1) for j = 1..k.
        - f[j]: best with j subarrays where the j-th includes nums[i].
        - g[j]: best with j subarrays ending at or before i.
        - f[j] = mult[j]*nums[i] + max(g_prev[j-1] start, f_prev[j] extend).

        Complexity: O(n*k) time, O(k) space (n*k <= 1e6).
        """
        NEG = -(10**30)
        prev_g = [NEG] * (k + 1)
        prev_g[0] = 0
        prev_f = [NEG] * (k + 1)
        for x in nums:
            cur_f = [NEG] * (k + 1)
            cur_g = prev_g[:]
            for j in range(1, k + 1):
                mult = (k - j + 1) * (1 if j % 2 == 1 else -1)
                best = NEG
                if prev_g[j - 1] > NEG // 2:
                    best = max(best, prev_g[j - 1] + mult * x)
                if prev_f[j] > NEG // 2:
                    best = max(best, prev_f[j] + mult * x)
                cur_f[j] = best
                cur_g[j] = max(prev_g[j], cur_f[j])
            prev_f, prev_g = cur_f, cur_g
        return prev_g[k]
# @lc code=end
