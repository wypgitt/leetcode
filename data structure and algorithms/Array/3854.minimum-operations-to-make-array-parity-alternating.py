#
# @lc app=leetcode id=3854 lang=python3
#
# [3854] Minimum Operations to Make Array Parity Alternating
#
# https://leetcode.com/problems/minimum-operations-to-make-array-parity-alternating/description/
#
# algorithms
# Medium (17.45%)
# Likes:    87
# Dislikes: 14
# Total Accepted:    8.7K
# Total Submissions: 50K
# Testcase Example:  "[-2,-3,1,4]"
#
#
# You are given an integer array nums.
#
# An array is called parity alternating if for every index i where 0 <= i
# < n - 1, nums[i] and nums[i + 1] have different parity (one is even and
# the other is odd).
#
# In one operation, you may choose any index i and either increase nums[i]
# by 1 or decrease nums[i] by 1.
#
# Return an integer array answer of length 2 where:
#
# answer[0] is the minimum number of operations required to make the array
# parity alternating.
#
# answer[1] is the minimum possible value of max(nums) - min(nums) taken
# over all arrays that are parity alternating and can be obtained by
# performing exactly answer[0] operations.
#
# An array of length 1 is considered parity alternating.
#
# Example 1:
#
# Input: nums = [-2,-3,1,4]
#
# Output: [2,6]
#
# Explanation:
#
# Applying the following operations:
#
# Increase nums[2] by 1, resulting in nums = [-2, -3, 2, 4].
#
# Decrease nums[3] by 1, resulting in nums = [-2, -3, 2, 3].
#
# The resulting array is parity alternating, and the value of max(nums) -
# min(nums) = 3 - (-3) = 6 is the minimum possible among all parity
# alternating arrays obtainable using exactly 2 operations.
#
# Example 2:
#
# Input: nums = [0,2,-2]
#
# Output: [1,3]
#
# Explanation:
#
# Applying the following operation:
#
# Decrease nums[1] by 1, resulting in nums = [0, 1, -2].
#
# The resulting array is parity alternating, and the value of max(nums) -
# min(nums) = 1 - (-2) = 3 is the minimum possible among all parity
# alternating arrays obtainable using exactly 1 operation.
#
# Example 3:
#
# Input: nums = [7]
#
# Output: [0,0]
#
# Explanation:
#
# No operations are required. The array is already parity alternating, and
# the value of max(nums) - min(nums) = 7 - 7 = 0, which is the minimum
# possible.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# -10^9 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def makeParityAlternating(self, nums: List[int]) -> List[int]:
        """
        Interview explanation:
        Make parities alternate with ±1 flips (each flip changes parity). Try both
        target patterns; among min-op patterns, minimize final max-min.

        Algorithm:
        - For target parity of even indices k∈{0,1}, count mismatches (ops).
        - For range: keep unmatched as-is; for a flip of x use x+1 in the min
          and x-1 in the max (greedy bounds). All-equal arrays become range 1.
        - Return the lexicographically smaller [ops, range].

        Complexity: O(n) time, O(1) space.
        """
        def calc(target: int) -> List[int]:
            ops = 0
            mn, mx = float("inf"), float("-inf")
            for i, x in enumerate(nums):
                if (x & 1) == ((i & 1) ^ target):
                    mn = min(mn, x)
                    mx = max(mx, x)
                else:
                    ops += 1
                    mn = min(mn, x + 1)
                    mx = max(mx, x - 1)
            if len(nums) == 1:
                return [0, 0]
            if max(nums) == min(nums):
                return [ops, 1]
            return [ops, mx - mn]

        return min(calc(0), calc(1))
# @lc code=end
