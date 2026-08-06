#
# @lc app=leetcode id=3599 lang=python3
#
# [3599] Partition Array to Minimize XOR
#
# https://leetcode.com/problems/partition-array-to-minimize-xor/description/
#
# algorithms
# Medium (41.71%)
# Likes:    117
# Dislikes: 7
# Total Accepted:    14.9K
# Total Submissions: 35.6K
# Testcase Example:  "[1,2,3]\n2"
#
#
# You are given an integer array nums and an integer k.
#
# Your task is to partition nums into k non-empty subarrays. For each
# subarray, compute the bitwise XOR of all its elements.
#
# Return the minimum possible value of the maximum XOR among these k
# subarrays.
#
# Example 1:
#
# Input: nums = [1,2,3], k = 2
#
# Output: 1
#
# Explanation:
#
# The optimal partition is [1] and [2, 3].
#
# XOR of the first subarray is 1.
#
# XOR of the second subarray is 2 XOR 3 = 1.
#
# The maximum XOR among the subarrays is 1, which is the minimum possible.
#
# Example 2:
#
# Input: nums = [2,3,3,2], k = 3
#
# Output: 2
#
# Explanation:
#
# The optimal partition is [2], [3, 3], and [2].
#
# XOR of the first subarray is 2.
#
# XOR of the second subarray is 3 XOR 3 = 0.
#
# XOR of the third subarray is 2.
#
# The maximum XOR among the subarrays is 2, which is the minimum possible.
#
# Example 3:
#
# Input: nums = [1,1,2,3,1], k = 2
#
# Output: 0
#
# Explanation:
#
# The optimal partition is [1, 1] and [2, 3, 1].
#
# XOR of the first subarray is 1 XOR 1 = 0.
#
# XOR of the second subarray is 2 XOR 3 XOR 1 = 0.
#
# The maximum XOR among the subarrays is 0, which is the minimum possible.
#
# Constraints:
#
# 1 <= nums.length <= 250
#
# 1 <= nums[i] <= 10^9
#
# 1 <= k <= n
#

# @lc code=start

from typing import List


class Solution:
    def minXor(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Minimize the max subarray-XOR over a partition into k contiguous parts.
        Classic DP on prefix XORs.

        Algorithm:
        - prefix[i] = XOR of nums[:i].
        - dp[i] = min possible max-XOR partitioning first i elems into current
          part count; transition dp[i] = min_j max(dp[j], prefix[i]^prefix[j]).

        Complexity: O(n^2 k) time, O(n) space.
        """
        n = len(nums)
        pref = [0] * (n + 1)
        for i, x in enumerate(nums):
            pref[i + 1] = pref[i] ^ x

        INF = 10**18
        dp = [INF] * (n + 1)
        dp[0] = 0
        for parts in range(1, k + 1):
            for i in range(n, parts - 1, -1):
                best = INF
                for j in range(parts - 1, i):
                    best = min(best, max(dp[j], pref[i] ^ pref[j]))
                dp[i] = best
        return dp[n]
# @lc code=end
