#
# @lc app=leetcode id=3139 lang=python3
#
# [3139] Minimum Cost to Equalize Array
#
# https://leetcode.com/problems/minimum-cost-to-equalize-array/description/
#
# algorithms
# Hard (18.98%)
# Likes:    151
# Dislikes: 24
# Total Accepted:    6.7K
# Total Submissions: 35.3K
# Testcase Example:  "[4,1]\n5\n2"
#
#
# You are given an integer array nums and two integers cost1 and cost2.
# You are allowed to perform either of the following operations any number
# of times:
#
# Choose an index i from nums and increase nums[i] by 1 for a cost of
# cost1.
#
# Choose two different indices i, j, from nums and increase nums[i] and
# nums[j] by 1 for a cost of cost2.
#
# Return the minimum cost required to make all elements in the array
# equal.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: nums = [4,1], cost1 = 5, cost2 = 2
#
# Output: 15
#
# Explanation:
#
# The following operations can be performed to make the values equal:
#
# Increase nums[1] by 1 for a cost of 5. nums becomes [4,2].
#
# Increase nums[1] by 1 for a cost of 5. nums becomes [4,3].
#
# Increase nums[1] by 1 for a cost of 5. nums becomes [4,4].
#
# The total cost is 15.
#
# Example 2:
#
# Input: nums = [2,3,3,3,5], cost1 = 2, cost2 = 1
#
# Output: 6
#
# Explanation:
#
# The following operations can be performed to make the values equal:
#
# Increase nums[0] and nums[1] by 1 for a cost of 1. nums becomes
# [3,4,3,3,5].
#
# Increase nums[0] and nums[2] by 1 for a cost of 1. nums becomes
# [4,4,4,3,5].
#
# Increase nums[0] and nums[3] by 1 for a cost of 1. nums becomes
# [5,4,4,4,5].
#
# Increase nums[1] and nums[2] by 1 for a cost of 1. nums becomes
# [5,5,5,4,5].
#
# Increase nums[3] by 1 for a cost of 2. nums becomes [5,5,5,5,5].
#
# The total cost is 6.
#
# Example 3:
#
# Input: nums = [3,5,3], cost1 = 1, cost2 = 3
#
# Output: 4
#
# Explanation:
#
# The following operations can be performed to make the values equal:
#
# Increase nums[0] by 1 for a cost of 1. nums becomes [4,5,3].
#
# Increase nums[0] by 1 for a cost of 1. nums becomes [5,5,3].
#
# Increase nums[2] by 1 for a cost of 1. nums becomes [5,5,4].
#
# Increase nums[2] by 1 for a cost of 1. nums becomes [5,5,5].
#
# The total cost is 4.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^6
#
# 1 <= cost1 <= 10^6
#
# 1 <= cost2 <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def minCostToEqualizeArray(
        self, nums: List[int], cost1: int, cost2: int
    ) -> int:
        """
        Interview explanation:
        Raise all elements to a common target T >= max(nums). Op1: +1 to one
        index (cost1); Op2: +1 to two distinct indices (cost2). Minimize cost;
        mod 10^9+7.

        Algorithm:
        - If 2*cost1 <= cost2, only Op1: cost = sum(T-a)*cost1 at T=max.
        - Else Op2 is useful: for each candidate T in [max, 2*max-min], let
          s = total increments, mx = max single need; do
          op2 = min(s//2, s-mx), cost = op2*cost2 + (s-2*op2)*cost1.
        - Take the minimum over T.

        Complexity: O(n + (max-min)) time, O(1) extra space.
        """
        MOD = 10**9 + 7
        n = len(nums)
        if n == 1:
            return 0
        mx, mn = max(nums), min(nums)
        base = sum(mx - x for x in nums)
        if cost1 * 2 <= cost2:
            return base * cost1 % MOD

        def cost_for(target: int) -> int:
            s = sum(target - x for x in nums)
            mxi = target - mn
            op2 = min(s // 2, s - mxi)
            return op2 * cost2 + (s - 2 * op2) * cost1

        ans = cost_for(mx)
        for t in range(mx + 1, 2 * mx - mn + 1):
            ans = min(ans, cost_for(t))
        return ans % MOD
# @lc code=end
