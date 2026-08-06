#
# @lc app=leetcode id=3247 lang=python3
#
# [3247] Number of Subsequences with Odd Sum
#
# https://leetcode.com/problems/number-of-subsequences-with-odd-sum/description/
#
# algorithms
# Medium (47.56%)
# Likes:    13
# Dislikes: 2
# Total Accepted:    1.2K
# Total Submissions: 2.4K
# Testcase Example:  "[1,1,1]"
#
#
# Given an array nums, return the number of subsequences with an odd sum
# of elements.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: nums = [1,1,1]
#
# Output: 4
#
# Explanation:
#
# The odd-sum subsequences are: [1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1,
# 1].
#
# Example 2:
#
# Input: nums = [1,2,2]
#
# Output: 4
#
# Explanation:
#
# The odd-sum subsequences are: [1, 2, 2], [1, 2, 2], [1, 2, 2], [1, 2,
# 2].
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def subsequenceCount(self, nums: List[int]) -> int:
        """
        Interview explanation:
        A subsequence has odd sum iff it contains an odd count of odd numbers.
        Evens may be chosen freely. If there is at least one odd, exactly half
        of the 2^n subsequences (including empty's complement) have odd sum:
        2^{n-1}.

        Algorithm:
        - If any odd exists, return 2^{n-1} mod 1e9+7; else 0.

        Complexity: O(n) time, O(1) space.

        Alternate: DP tracking (even_sum_count, odd_sum_count) while scanning.
        """
        MOD = 10**9 + 7
        if any(x & 1 for x in nums):
            return pow(2, len(nums) - 1, MOD)
        return 0

    def subsequenceCount_dp(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate: maintain counts of even-sum / odd-sum subsequences so far.

        Algorithm:
        - For each x, append to existing subsequences and update parity counts.

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        even, odd = 1, 0  # empty subsequence has even sum
        for x in nums:
            if x & 1:
                even, odd = (even + odd) % MOD, (odd + even) % MOD
            else:
                even, odd = (even * 2) % MOD, (odd * 2) % MOD
        return (odd) % MOD
# @lc code=end
