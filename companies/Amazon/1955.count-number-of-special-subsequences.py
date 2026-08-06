#
# @lc app=leetcode id=1955 lang=python3
#
# [1955] Count Number of Special Subsequences
#
# https://leetcode.com/problems/count-number-of-special-subsequences/description/
#
# algorithms
# Hard (53.06%)
# Likes:    552
# Dislikes: 11
# Total Accepted:    16.1K
# Total Submissions: 30.4K
# Testcase Example:  "[0,1,2,2]"
#
# A sequence is special if it consists of a positive number of 0s, followed by
# a positive number of 1s, then a positive number of 2s.
#
# For example, [0,1,2] and [0,0,1,1,1,2] are special.
#
# In contrast, [2,1,0], [1], and [0,1,2,0] are not special.
#
# Given an array nums (consisting of only integers 0, 1, and 2), return the
# number of different subsequences that are special. Since the answer may be
# very large, return it modulo 10^9 + 7.
#
# A subsequence of an array is a sequence that can be derived from the array by
# deleting some or no elements without changing the order of the remaining
# elements. Two subsequences are different if the set of indices chosen are
# different.
#
# Example 1:
#
# Input: nums = [0,1,2,2]
# Output: 3
# Explanation: The special subsequences are bolded [0,1,2,2], [0,1,2,2], and
# [0,1,2,2].
#
# Example 2:
#
# Input: nums = [2,2,0,0]
# Output: 0
# Explanation: There are no special subsequences in [2,2,0,0].
#
# Example 3:
#
# Input: nums = [0,1,2,0,1,2]
# Output: 7
# Explanation: The special subsequences are bolded:
# - [0,1,2,0,1,2]
# - [0,1,2,0,1,2]
# - [0,1,2,0,1,2]
# - [0,1,2,0,1,2]
# - [0,1,2,0,1,2]
# - [0,1,2,0,1,2]
# - [0,1,2,0,1,2]
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 2
#

# @lc code=start
from typing import List


class Solution:
    def countSpecialSubsequences(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count subsequences of form 0+1+2+. Maintain ways for stages 0 / 01 / 012.

        Algorithm:
        - MOD=1e9+7; a,b,c ways. On 0: a=2a+1; on 1: b=2b+a; on 2: c=2c+b.

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        a = b = c = 0
        for x in nums:
            if x == 0:
                a = (2 * a + 1) % MOD
            elif x == 1:
                b = (2 * b + a) % MOD
            else:
                c = (2 * c + b) % MOD
        return c

    def countSpecialSubsequences_dp(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate explicit 3-state DP array with the same transitions.

        Algorithm:
        - dp[0/1/2] with doubling + carry-from-previous.

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        dp = [0, 0, 0]
        for x in nums:
            if x == 0:
                dp[0] = (dp[0] * 2 + 1) % MOD
            elif x == 1:
                dp[1] = (dp[1] * 2 + dp[0]) % MOD
            else:
                dp[2] = (dp[2] * 2 + dp[1]) % MOD
        return dp[2]
# @lc code=end

