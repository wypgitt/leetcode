#
# @lc app=leetcode id=3444 lang=python3
#
# [3444] Minimum Increments for Target Multiples in an Array
#
# https://leetcode.com/problems/minimum-increments-for-target-multiples-in-an-array/description/
#
# algorithms
# Hard (27.48%)
# Likes:    89
# Dislikes: 7
# Total Accepted:    7K
# Total Submissions: 25.3K
# Testcase Example:  "[1,2,3]\n[4]"
#
#
# You are given two arrays, nums and target.
#
# In a single operation, you may increment any element of nums by 1.
#
# Return the minimum number of operations required so that each element in
# target has at least one multiple in nums.
#
# Example 1:
#
# Input: nums = [1,2,3], target = [4]
#
# Output: 1
#
# Explanation:
#
# The minimum number of operations required to satisfy the condition is 1.
#
# Increment 3 to 4 with just one operation, making 4 a multiple of itself.
#
# Example 2:
#
# Input: nums = [8,4], target = [10,5]
#
# Output: 2
#
# Explanation:
#
# The minimum number of operations required to satisfy the condition is 2.
#
# Increment 8 to 10 with 2 operations, making 10 a multiple of both 5 and
# 10.
#
# Example 3:
#
# Input: nums = [7,9,10], target = [7]
#
# Output: 0
#
# Explanation:
#
# Target 7 already has a multiple in nums, so no additional operations are
# needed.
#
# Constraints:
#
# 1 <= nums.length <= 5 * 10^4
#
# 1 <= target.length <= 4
#
# target.length <= nums.length
#
# 1 <= nums[i], target[i] <= 10^4
#

# @lc code=start

from functools import reduce
from math import inf, lcm
from typing import List


class Solution:
    def minimumIncrements(self, nums: List[int], target: List[int]) -> int:
        """
        Interview explanation:
        Each nums[i] can be bumped to cover a subset of targets by becoming a
        multiple of that subset's LCM. Cover all targets with min total bumps.

        Algorithm:
        - Precompute LCM for every nonempty target subset (bitmask, m<=4).
        - dp[mask] = min cost to cover targets in mask.
        - For each num, for each subset cost (lcm - num%lcm)%lcm, update
          dp[prev|subset] from dp[prev].

        Complexity: O(n * 3^m) / O(n * 4^m) style bitmask DP; m<=4 so tiny.
        """
        m = len(target)
        max_mask = 1 << m
        mask_to_lcm = {}
        for mask in range(1, max_mask):
            subset = [target[i] for i in range(m) if mask >> i & 1]
            mask_to_lcm[mask] = reduce(lcm, subset, 1)

        dp = [inf] * max_mask
        dp[0] = 0
        for num in nums:
            mask_to_cost = []
            for mask, L in mask_to_lcm.items():
                r = num % L
                mask_to_cost.append((mask, 0 if r == 0 else L - r))
            new_dp = dp[:]
            for prev in range(max_mask):
                if dp[prev] == inf:
                    continue
                for mask, cost in mask_to_cost:
                    nxt = prev | mask
                    new_dp[nxt] = min(new_dp[nxt], dp[prev] + cost)
            dp = new_dp
        return int(dp[-1])
# @lc code=end
