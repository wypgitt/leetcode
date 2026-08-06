#
# @lc app=leetcode id=3351 lang=python3
#
# [3351] Sum of Good Subsequences
#
# https://leetcode.com/problems/sum-of-good-subsequences/description/
#
# algorithms
# Hard (31.35%)
# Likes:    162
# Dislikes: 9
# Total Accepted:    12.7K
# Total Submissions: 40.7K
# Testcase Example:  "[1,2,1]"
#
#
# You are given an integer array nums. A good subsequence is defined as a
# subsequence of nums where the absolute difference between any two
# consecutive elements in the subsequence is exactly 1.
#
# Return the sum of all possible good subsequences of nums.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Note that a subsequence of size 1 is considered good by definition.
#
# Example 1:
#
# Input: nums = [1,2,1]
#
# Output: 14
#
# Explanation:
#
# Good subsequences are: [1], [2], [1], [1,2], [2,1], [1,2,1].
#
# The sum of elements in these subsequences is 14.
#
# Example 2:
#
# Input: nums = [3,4,5]
#
# Output: 40
#
# Explanation:
#
# Good subsequences are: [3], [4], [5], [3,4], [4,5], [3,4,5].
#
# The sum of elements in these subsequences is 40.
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^5
#

# @lc code=start

from typing import List
from collections import defaultdict


class Solution:
    def sumOfGoodSubsequences(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Good subsequence: consecutive elements differ by exactly 1. Sum values
        over all good subsequences (singletons included), mod 1e9+7.

        Algorithm:
        - Process left→right. count[v]/total[v] = # / sum of good subsequences
          ending with v so far.
        - For x: append to endings x±1, plus singleton; add new sums to answer.

        Complexity: O(n) time, O(U) space for distinct values.
        """
        MOD = 10**9 + 7
        count: dict[int, int] = defaultdict(int)
        total: dict[int, int] = defaultdict(int)
        ans = 0
        for x in nums:
            new_c = (1 + count[x - 1] + count[x + 1]) % MOD
            new_s = (
                x
                + total[x - 1]
                + x * count[x - 1]
                + total[x + 1]
                + x * count[x + 1]
            ) % MOD
            ans = (ans + new_s) % MOD
            count[x] = (count[x] + new_c) % MOD
            total[x] = (total[x] + new_s) % MOD
        return ans
# @lc code=end
