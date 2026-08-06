#
# @lc app=leetcode id=2741 lang=python3
#
# [2741] Special Permutations
#
# https://leetcode.com/problems/special-permutations/description/
#
# algorithms
# Medium (29.64%)
# Likes:    594
# Dislikes: 66
# Total Accepted:    18.4K
# Total Submissions: 62.1K
# Testcase Example:  "[2,3,6]"
#
# You are given a 0-indexed integer array nums containing n distinct positive
# integers. A permutation of nums is called special if:
#
#
# For all indexes 0 <= i < n - 1, either nums[i] % nums[i+1] == 0 or nums[i+1] %
# nums[i] == 0.
#
# Return the total number of special permutations. As the answer could be large,
# return it modulo 10^9 + 7.
#
#
#
# Example 1:
#
# Input: nums = [2,3,6]
# Output: 2
# Explanation: [3,6,2] and [2,6,3] are the two special permutations of nums.
#
# Example 2:
#
# Input: nums = [1,4,3]
# Output: 2
# Explanation: [3,1,4] and [4,1,3] are the two special permutations of nums.
#
#
#
# Constraints:
#
#
# 2 <= nums.length <= 14
#
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from functools import cache
from typing import List


class Solution:
    def specialPerm(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count permutations where each adjacent pair has one dividing the other, mod 1e9+7.

        Algorithm:
        - Bitmask DP: dp(mask, last) = ways to place remaining using last index.
          Transition if nums[i]%nums[last]==0 or vice versa.

        Complexity: O(n^2 * 2^n) time, O(n * 2^n) space.
        """
        mod = 10**9 + 7
        n = len(nums)

        @cache
        def dp(mask: int, last: int) -> int:
            if mask == (1 << n) - 1:
                return 1
            tot = 0
            for i in range(n):
                if mask >> i & 1:
                    continue
                if last == -1 or nums[i] % nums[last] == 0 or nums[last] % nums[i] == 0:
                    tot = (tot + dp(mask | (1 << i), i)) % mod
            return tot

        return dp(0, -1)

    def specialPerm_dp(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate naming for the bitmask DP count.

        Algorithm:
        - Same dp(mask, last).

        Complexity: O(n^2 * 2^n) time, O(n * 2^n) space.
        """
        return self.specialPerm(nums)
# @lc code=end
