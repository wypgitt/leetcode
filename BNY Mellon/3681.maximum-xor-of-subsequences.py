#
# @lc app=leetcode id=3681 lang=python3
#
# [3681] Maximum XOR of Subsequences
#
# https://leetcode.com/problems/maximum-xor-of-subsequences/description/
#
# algorithms
# Hard (51.62%)
# Likes:    68
# Dislikes: 10
# Total Accepted:    8.1K
# Total Submissions: 15.7K
# Testcase Example:  "[1,2,3]"
#
#
# You are given an integer array nums of length n where each element is a
# non-negative integer.
#
# Select two subsequences of nums (they may be empty and are allowed to
# overlap), each preserving the original order of elements, and let:
#
# X be the bitwise XOR of all elements in the first subsequence.
#
# Y be the bitwise XOR of all elements in the second subsequence.
#
# Return the maximum possible value of X XOR Y.
#
# Note: The XOR of an empty subsequence is 0.
#
# Example 1:
#
# Input: nums = [1,2,3]
#
# Output: 3
#
# Explanation:
#
# Choose subsequences:
#
# First subsequence [2], whose XOR is 2.
#
# Second subsequence [2,3], whose XOR is 1.
#
# Then, XOR of both subsequences = 2 XOR 1 = 3.
#
# This is the maximum XOR value achievable from any two subsequences.
#
# Example 2:
#
# Input: nums = [5,2]
#
# Output: 7
#
# Explanation:
#
# Choose subsequences:
#
# First subsequence [5], whose XOR is 5.
#
# Second subsequence [2], whose XOR is 2.
#
# Then, XOR of both subsequences = 5 XOR 2 = 7.
#
# This is the maximum XOR value achievable from any two subsequences.
#
# Constraints:
#
# 2 <= nums.length <= 10^5
#
# 0 <= nums[i] <= 10^9
#

# @lc code=start
from typing import List


class Solution:
    def maxXorSubsequences(self, nums: List[int]) -> int:
        """
        Interview explanation:
        X XOR Y equals the XOR of elements that lie in exactly one of the two
        subsequences, so any subset XOR is achievable. Maximize subset XOR via
        a linear basis (Gaussian elimination over GF(2)).

        Algorithm:
        - Insert each number into a 32-bit XOR basis (MSB bucket).
        - Greedily XOR basis vectors from high bit to low to maximize the value.

        Complexity: O(n * B) time, O(B) space with B = 32.
        """
        basis = [0] * 32
        for x in nums:
            cur = x
            for b in range(31, -1, -1):
                if not (cur & (1 << b)):
                    continue
                if basis[b] == 0:
                    basis[b] = cur
                    break
                cur ^= basis[b]
        ans = 0
        for b in range(31, -1, -1):
            if (ans ^ basis[b]) > ans:
                ans ^= basis[b]
        return ans

    def maxXorSubsequences_gauss(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Alternate classic presentation: eliminate on a mutable copy, then XOR
        all remaining pivots (also yields the maximum subset XOR).

        Algorithm:
        - For bit 31..0, pick a pivot with that bit, swap into place, eliminate.
        - XOR every leftover nonzero row.

        Complexity: O(n * B) time, O(n) space.
        """
        arr = nums[:]
        n = len(arr)
        idx = 0
        for bit in range(31, -1, -1):
            piv = idx
            while piv < n and (arr[piv] & (1 << bit)) == 0:
                piv += 1
            if piv == n:
                continue
            arr[idx], arr[piv] = arr[piv], arr[idx]
            for i in range(n):
                if i != idx and arr[i] & (1 << bit):
                    arr[i] ^= arr[idx]
            idx += 1
        ans = 0
        for x in arr:
            ans ^= x
        return ans
# @lc code=end
