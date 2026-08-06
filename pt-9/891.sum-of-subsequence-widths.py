#
# @lc app=leetcode id=891 lang=python3
#
# [891] Sum of Subsequence Widths
#
# https://leetcode.com/problems/sum-of-subsequence-widths/description/
#
# algorithms
# Hard (40.96%)
# Likes:    743
# Dislikes: 173
# Total Accepted:    27.6K
# Total Submissions: 67.4K
# Testcase Example:  "[2,1,3]"
#
# The width of a sequence is the difference between the maximum and minimum
# elements in the sequence.
#
# Given an array of integers nums, return the sum of the widths of all the
# non-empty subsequences of nums. Since the answer may be very large, return it
# modulo 10^9 + 7.
#
# A subsequence is a sequence that can be derived from an array by deleting
# some or no elements without changing the order of the remaining elements. For
# example, [3,6,2,7] is a subsequence of the array [0,3,1,6,2,2,7].
#
# Example 1:
#
# Input: nums = [2,1,3]
# Output: 6
# Explanation: The subsequences are [1], [2], [3], [2,1], [2,3], [1,3],
# [2,1,3].
# The corresponding widths are 0, 0, 0, 1, 1, 2, 2.
# The sum of these widths is 6.
#
# Example 2:
#
# Input: nums = [2]
# Output: 0
#
# Constraints:
#
# 1 <= nums.length <= 10^5
#
# 1 <= nums[i] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def sumSubseqWidths(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Width = max-min of subsequence. Sort; each nums[i] is max in 2^i
        subsequences of left elements, min in 2^(n-1-i) of right — contribute
        nums[i]*(2^i - 2^(n-1-i)).

        Algorithm:
        - Sort. ans = sum nums[i] * (pow2[i] - pow2[n-1-i]) % MOD.

        Complexity: O(n log n) time, O(n) space for powers.
        """
        MOD = 10**9 + 7
        nums = sorted(nums)
        n = len(nums)
        pow2 = [1] * n
        for i in range(1, n):
            pow2[i] = (pow2[i - 1] * 2) % MOD
        ans = 0
        for i, x in enumerate(nums):
            ans = (ans + x * (pow2[i] - pow2[n - 1 - i])) % MOD
        return ans
# @lc code=end

