#
# @lc app=leetcode id=1969 lang=python3
#
# [1969] Minimum Non-Zero Product of the Array Elements
#
# https://leetcode.com/problems/minimum-non-zero-product-of-the-array-elements/description/
#
# algorithms
# Medium (37.6%)
# Likes:    297
# Dislikes: 401
# Total Accepted:    17.1K
# Total Submissions: 45.6K
# Testcase Example:  "1"
#
# You are given a positive integer p. Consider an array nums (1-indexed) that
# consists of the integers in the inclusive range [1, 2^p - 1] in their binary
# representations. You are allowed to do the following operation any number of
# times:
#
# Choose two elements x and y from nums.
#
# Choose a bit in x and swap it with its corresponding bit in y. Corresponding
# bit refers to the bit that is in the same position in the other integer.
#
# For example, if x = 1101 and y = 0011, after swapping the 2^nd bit from the
# right, we have x = 1111 and y = 0001.
#
# Find the minimum non-zero product of nums after performing the above
# operation any number of times. Return this product modulo 10^9 + 7.
#
# Note: The answer should be the minimum product before the modulo operation is
# done.
#
# Example 1:
#
# Input: p = 1
# Output: 1
# Explanation: nums = [1].
# There is only one element, so the product equals that element.
#
# Example 2:
#
# Input: p = 2
# Output: 6
# Explanation: nums = [01, 10, 11].
# Any swap would either make the product 0 or stay the same.
# Thus, the array product of 1 * 2 * 3 = 6 is already minimized.
#
# Example 3:
#
# Input: p = 3
# Output: 1512
# Explanation: nums = [001, 010, 011, 100, 101, 110, 111]
# - In the first operation we can swap the leftmost bit of the second and fifth
# elements.
# - The resulting array is [001, 110, 011, 100, 001, 110, 111].
# - In the second operation we can swap the middle bit of the third and fourth
# elements.
# - The resulting array is [001, 110, 001, 110, 001, 110, 111].
# The array product is 1 * 6 * 1 * 6 * 1 * 6 * 7 = 1512, which is the minimum
# possible product.
#
# Constraints:
#
# 1 <= p <= 60
#

# @lc code=start
class Solution:
    def minNonZeroProduct(self, p: int) -> int:
        """
        Interview explanation:
        Array is all integers in [1, 2^p - 1]. Pair x with (2^p-1-x) via swaps
        that preserve pairwise products structure: leave max M=2^p-1, and
        (M-1) appears 2^{p-1}-1 times. Answer M * (M-1)^(2^{p-1}-1) mod 1e9+7.

        Algorithm:
        - MOD=1e9+7; M=(1<<p)-1; return M * pow(M-1, (1<<(p-1))-1, MOD) % MOD.

        Complexity: O(log exponent) time, O(1) space.
        """
        MOD = 10**9 + 7
        M = (1 << p) - 1
        return M * pow(M - 1, (1 << (p - 1)) - 1, MOD) % MOD

    def minNonZeroProduct_clarity(self, p: int) -> int:
        """
        Interview explanation:
        Alternate same formula with named variables for interview narration.

        Algorithm:
        - max_val = 2^p-1; pairs = 2^{p-1}-1; modular exponentiation.

        Complexity: O(log pairs) time, O(1) space.
        """
        MOD = 10**9 + 7
        max_val = (1 << p) - 1
        pairs = (1 << (p - 1)) - 1
        return (max_val % MOD) * pow(max_val - 1, pairs, MOD) % MOD
# @lc code=end

