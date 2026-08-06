#
# @lc app=leetcode id=1681 lang=python3
#
# [1681] Minimum Incompatibility
#
# https://leetcode.com/problems/minimum-incompatibility/description/
#
# algorithms
# Hard (41.62%)
# Likes:    305
# Dislikes: 101
# Total Accepted:    11.7K
# Total Submissions: 28.0K
# Testcase Example:  "[1,2,1,4]"
#
# You are given an integer array nums and an integer k. You are asked to
# distribute this array into k subsets of equal size such that there are no two
# equal elements in the same subset.
#
# A subset's incompatibility is the difference between the maximum and minimum
# elements in that array.
#
# Return the minimum possible sum of incompatibilities of the k subsets after
# distributing the array optimally, or return -1 if it is not possible.
#
# A subset is a group integers that appear in the array with no particular
# order.
#
# Example 1:
#
# Input: nums = [1,2,1,4], k = 2
# Output: 4
# Explanation: The optimal distribution of subsets is [1,2] and [1,4].
# The incompatibility is (2-1) + (4-1) = 4.
# Note that [1,1] and [2,4] would result in a smaller sum, but the first subset
# contains 2 equal elements.
#
# Example 2:
#
# Input: nums = [6,3,8,1,3,1,2,2], k = 4
# Output: 6
# Explanation: The optimal distribution of subsets is [1,2], [2,3], [6,8], and
# [1,3].
# The incompatibility is (2-1) + (3-2) + (8-6) + (3-1) = 6.
#
# Example 3:
#
# Input: nums = [5,3,3,6,3,3], k = 3
# Output: -1
# Explanation: It is impossible to distribute nums into 3 subsets where no two
# elements are equal in the same subset.
#
# Constraints:
#
# 1 <= k <= nums.length <= 16
#
# nums.length is divisible by k
#
# 1 <= nums[i] <= nums.length
#

# @lc code=start
from typing import List
from functools import lru_cache
from collections import Counter


class Solution:
    def minimumIncompatibility(self, nums: List[int], k: int) -> int:
        """
        Interview explanation:
        Split n numbers into k subsets of size n/k with distinct values each;
        minimize sum of (max-min) over subsets. Bitmask DP over used indices;
        n<=16 so 2^n feasible with enumeration of valid subsets of size sz.

        Algorithm (bitmask DP):
        - Precompute valid masks of size sz with unique values and their cost.
        - dp[mask]=min cost to cover mask with valid blocks; iterate.

        Complexity: O(3^n) or O(2^n * C) time, O(2^n) space.
        """
        n = len(nums)
        sz = n // k
        # Early impossible: some value appears > k times
        if max(Counter(nums).values()) > k:
            return -1

        # valid subset masks
        valid = {}
        for mask in range(1 << n):
            if bin(mask).count("1") != sz:
                continue
            vals = [nums[i] for i in range(n) if mask >> i & 1]
            if len(vals) != len(set(vals)):
                continue
            valid[mask] = max(vals) - min(vals)

        full = (1 << n) - 1
        INF = 10**9
        dp = [INF] * (1 << n)
        dp[0] = 0
        for mask in range(1 << n):
            if dp[mask] == INF:
                continue
            # build next block from unused bits
            unused = full ^ mask
            # pick smallest unused index to reduce symmetry
            if unused == 0:
                continue
            # enumerate submasks of unused that are valid
            sub = unused
            while sub:
                if sub in valid:
                    dp[mask | sub] = min(dp[mask | sub], dp[mask] + valid[sub])
                sub = (sub - 1) & unused
        return -1 if dp[full] >= INF else dp[full]
# @lc code=end
