#
# @lc app=leetcode id=2172 lang=python3
#
# [2172] Maximum AND Sum of Array
#
# https://leetcode.com/problems/maximum-and-sum-of-array/description/
#
# algorithms
# Hard (50.93%)
# Likes:    555
# Dislikes: 33
# Total Accepted:    18.7K
# Total Submissions: 36.8K
# Testcase Example:  "[1,2,3,4,5,6]\n3"
#
# You are given an integer array nums of length n and an integer numSlots such
# that 2 * numSlots >= n. There are numSlots slots numbered from 1 to numSlots.
#
# You have to place all n integers into the slots such that each slot contains
# at most two numbers. The AND sum of a given placement is the sum of the
# bitwise AND of every number with its respective slot number.
#
#
# For example, the AND sum of placing the numbers [1, 3] into slot 1 and [4, 6]
# into slot 2 is equal to (1 AND 1) + (3 AND 1) + (4 AND 2) + (6 AND 2) = 1 + 1
# + 0 + 2 = 4.
#
# Return the maximum possible AND sum of nums given numSlots slots.
#
#
#
# Example 1:
#
# Input: nums = [1,2,3,4,5,6], numSlots = 3
# Output: 9
# Explanation: One possible placement is [1, 4] into slot 1, [2, 6] into slot 2,
# and [3, 5] into slot 3.
# This gives the maximum AND sum of (1 AND 1) + (4 AND 1) + (2 AND 2) + (6 AND
# 2) + (3 AND 3) + (5 AND 3) = 1 + 0 + 2 + 2 + 3 + 1 = 9.
#
# Example 2:
#
# Input: nums = [1,3,10,4,7,1], numSlots = 9
# Output: 24
# Explanation: One possible placement is [1, 1] into slot 1, [3] into slot 3,
# [4] into slot 4, [7] into slot 7, and [10] into slot 9.
# This gives the maximum AND sum of (1 AND 1) + (1 AND 1) + (3 AND 3) + (4 AND
# 4) + (7 AND 7) + (10 AND 9) = 1 + 1 + 3 + 4 + 7 + 8 = 24.
# Note that slots 2, 5, 6, and 8 are empty which is permitted.
#
#
#
# Constraints:
#
#
# n == nums.length
#
#
# 1 <= numSlots <= 9
#
#
# 1 <= n <= 2 * numSlots
#
#
# 1 <= nums[i] <= 15
#

# @lc code=start
from typing import List
from functools import cache


class Solution:
    def maximumANDSum(self, nums: List[int], numSlots: int) -> int:
        """
        Interview explanation:
        Place each nums[i] into one of numSlots slots (each slot holds at most
        2 numbers). Score is sum of (nums[i] AND slotNumber) over placements.
        Maximize total score.

        Algorithm:
        (bitmask DP)
        - Represent occupancy with base-3 mask (0/1/2 items per slot) or pair
          of bits per slot. DFS over index with mask of used capacities.
        - dp[mask]: max score placing next number into free capacity in mask.

        Complexity: O(n * 3^{numSlots}) time/space with n<=2*numSlots<=18.
        """
        n = len(nums)

        @cache
        def dfs(i: int, mask: int) -> int:
            if i == n:
                return 0
            best = 0
            m = mask
            for slot in range(numSlots):
                occupied = m % 3
                m //= 3
                if occupied < 2:
                    # build new mask with this slot +1
                    add = 1
                    for _ in range(slot):
                        add *= 3
                    best = max(best, (nums[i] & (slot + 1)) + dfs(i + 1, mask + add))
            return best

        return dfs(0, 0)
# @lc code=end
