#
# @lc app=leetcode id=3806 lang=python3
#
# [3806] Maximum Bitwise AND After Increment Operations
#
# https://leetcode.com/problems/maximum-bitwise-and-after-increment-operations/description/
#
# algorithms
# Hard (32.36%)
# Likes:    81
# Dislikes: 3
# Total Accepted:    7.2K
# Total Submissions: 22.1K
# Testcase Example:  "[3,1,2]\n8\n2"
#
#
# You are given an integer array nums and two integers k and m.
#
# You may perform at most k operations. In one operation, you may choose
# any index i and increase nums[i] by 1.
#
# Return an integer denoting the maximum possible bitwise AND of any
# subset of size m after performing up to k operations optimally.
#
# Example 1:
#
# Input: nums = [3,1,2], k = 8, m = 2
#
# Output: 6
#
# Explanation:
#
# We need a subset of size m = 2. Choose indices [0, 2].
#
# Increase nums[0] = 3 to 6 using 3 operations, and increase nums[2] = 2
# to 6 using 4 operations.
#
# The total number of operations used is 7, which is not greater than k =
# 8.
#
# The two chosen values become [6, 6], and their bitwise AND is 6, which
# is the maximum possible.
#
# Example 2:
#
# Input: nums = [1,2,8,4], k = 7, m = 3
#
# Output: 4
#
# Explanation:
#
# We need a subset of size m = 3. Choose indices [0, 1, 3].
#
# Increase nums[0] = 1 to 4 using 3 operations, increase nums[1] = 2 to 4
# using 2 operations, and keep nums[3] = 4.
#
# The total number of operations used is 5, which is not greater than k =
# 7.
#
# The three chosen values become [4, 4, 4], and their bitwise AND is 4,
# which is the maximum possible.​​​​​​​
#
# Example 3:
#
# Input: nums = [1,1], k = 3, m = 2
#
# Output: 2
#
# Explanation:
#
# We need a subset of size m = 2. Choose indices [0, 1].
#
# Increase both values from 1 to 2 using 1 operation each.
#
# The total number of operations used is 2, which is not greater than k =
# 3.
#
# The two chosen values become [2, 2], and their bitwise AND is 2, which
# is the maximum possible.
#
# Constraints:
#
# 1 <= n == nums.length <= 5 * 10^4
#
# 1 <= nums[i] <= 10^9
#
# 1 <= k <= 10^9
#
# 1 <= m <= n
#

# @lc code=start
from typing import List


class Solution:
    MAX_BIT = 31

    def maximumAND(self, nums: List[int], k: int, m: int) -> int:
        """
        Interview explanation:
        After at most k increments, maximize the AND of some m-element subset.
        Build the answer bit by bit from high to low.

        Algorithm:
        - Greedily try setting each bit in the candidate mask.
        - Feasibility: cost to make each nums[i] contain all mask bits; take the
          m cheapest costs and check their sum is <= k.
        - Cost: raise value so every required missing bit is covered (carry).

        Complexity: O(B * n log n) time with B≈31, O(n) space.
        """
        ans = 0

        for bit in range(self.MAX_BIT, -1, -1):
            candidate = ans | (1 << bit)
            if self._can_make(nums, k, m, candidate):
                ans = candidate

        return ans

    def _can_make(self, nums: List[int], budget: int, count: int, mask: int) -> bool:
        costs = [self._cost_to_contain(value, mask) for value in nums]
        costs.sort()
        return sum(costs[:count]) <= budget

    def _cost_to_contain(self, value: int, mask: int) -> int:
        target = value

        for bit in range(self.MAX_BIT, -1, -1):
            if (mask >> bit) & 1 and not ((target >> bit) & 1):
                target = ((target >> bit) + 1) << bit
                target |= mask & ((1 << bit) - 1)

        return target - value
# @lc code=end
