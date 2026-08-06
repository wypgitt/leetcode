#
# @lc app=leetcode id=3533 lang=python3
#
# [3533] Concatenated Divisibility
#
# https://leetcode.com/problems/concatenated-divisibility/description/
#
# algorithms
# Hard (30.49%)
# Likes:    53
# Dislikes: 7
# Total Accepted:    6.5K
# Total Submissions: 21.4K
# Testcase Example:  "[3,12,45]\n5"
#
#
# You are given an array of positive integers nums and a positive integer
# k.
#
# A permutation of nums is said to form a divisible concatenation if, when
# you concatenate the decimal representations of the numbers in the order
# specified by the permutation, the resulting number is divisible by k.
#
# Return the lexicographically smallest permutation (when considered as a
# list of integers) that forms a divisible concatenation. If no such
# permutation exists, return an empty list.
#
# Example 1:
#
# Input: nums = [3,12,45], k = 5
#
# Output: [3,12,45]
#
# Explanation:
#
#                         Permutation
#                         Concatenated Value
#                         Divisible by 5
#
#                         [3, 12, 45]
#                         31245
#                         Yes
#
#                         [3, 45, 12]
#                         34512
#                         No
#
#                         [12, 3, 45]
#                         12345
#                         Yes
#
#                         [12, 45, 3]
#                         12453
#                         No
#
#                         [45, 3, 12]
#                         45312
#                         No
#
#                         [45, 12, 3]
#                         45123
#                         No
#
# The lexicographically smallest permutation that forms a divisible
# concatenation is [3,12,45].
#
# Example 2:
#
# Input: nums = [10,5], k = 10
#
# Output: [5,10]
#
# Explanation:
#
#                         Permutation
#                         Concatenated Value
#                         Divisible by 10
#
#                         [5, 10]
#                         510
#                         Yes
#
#                         [10, 5]
#                         105
#                         No
#
# The lexicographically smallest permutation that forms a divisible
# concatenation is [5,10].
#
# Example 3:
#
# Input: nums = [1,2,3], k = 5
#
# Output: []
#
# Explanation:
#
# Since no permutation of nums forms a valid divisible concatenation,
# return an empty list.
#
# Constraints:
#
# 1 <= nums.length <= 13
#
# 1 <= nums[i] <= 10^5
#
# 1 <= k <= 100
#

# @lc code=start
from functools import lru_cache
from typing import List


class Solution:
    def concatenatedDivisibility(self, nums: List[int], k: int) -> List[int]:
        """
        Interview explanation:
        n ≤ 13, so search permutations via bitmask DP on used set and running
        value mod k. Reconstruct the lexicographically smallest successful order.

        Algorithm:
        - Precompute each num % k and 10^{len(num)} % k for concatenation.
        - can(mask, rem) = whether remaining numbers can reach rem→0 mod k.
        - Greedily append the smallest unused nums[i] that keeps can true.

        Complexity: O(2^n * n * k) time, O(2^n * k) space.
        """
        n = len(nums)
        mods = [x % k for x in nums]
        mul = [pow(10, len(str(x)), k) for x in nums]
        order = sorted(range(n), key=lambda i: nums[i])

        @lru_cache(None)
        def can(mask: int, rem: int) -> bool:
            if mask == (1 << n) - 1:
                return rem == 0
            for i in range(n):
                if mask & (1 << i):
                    continue
                nxt = (rem * mul[i] + mods[i]) % k
                if can(mask | (1 << i), nxt):
                    return True
            return False

        if not can(0, 0):
            return []

        ans: List[int] = []
        mask = 0
        rem = 0
        for _ in range(n):
            for i in order:
                if mask & (1 << i):
                    continue
                nxt = (rem * mul[i] + mods[i]) % k
                if can(mask | (1 << i), nxt):
                    ans.append(nums[i])
                    mask |= 1 << i
                    rem = nxt
                    break
        return ans
# @lc code=end
