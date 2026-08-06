#
# @lc app=leetcode id=762 lang=python3
#
# [762] Prime Number of Set Bits in Binary Representation
#
# https://leetcode.com/problems/prime-number-of-set-bits-in-binary-representation/description/
#
# algorithms
# Easy (78.96%)
# Likes:    1040
# Dislikes: 526
# Total Accepted:    268K
# Total Submissions: 339K
# Testcase Example:  "6"
#
# Given two integers left and right, return the count of numbers in the
# inclusive range [left, right] having a prime number of set bits in their
# binary representation.
#
# Recall that the number of set bits an integer has is the number of 1's
# present when written in binary.
#
# For example, 21 written in binary is 10101, which has 3 set bits.
#
# Example 1:
#
# Input: left = 6, right = 10
# Output: 4
# Explanation:
# 6 -> 110 (2 set bits, 2 is prime)
# 7 -> 111 (3 set bits, 3 is prime)
# 8 -> 1000 (1 set bit, 1 is not prime)
# 9 -> 1001 (2 set bits, 2 is prime)
# 10 -> 1010 (2 set bits, 2 is prime)
# 4 numbers have a prime number of set bits.
#
# Example 2:
#
# Input: left = 10, right = 15
# Output: 5
# Explanation:
# 10 -> 1010 (2 set bits, 2 is prime)
# 11 -> 1011 (3 set bits, 3 is prime)
# 12 -> 1100 (2 set bits, 2 is prime)
# 13 -> 1101 (3 set bits, 3 is prime)
# 14 -> 1110 (3 set bits, 3 is prime)
# 15 -> 1111 (4 set bits, 4 is not prime)
# 5 numbers have a prime number of set bits.
#
# Constraints:
#
# 1 <= left <= right <= 10^6
#
# 0 <= right - left <= 10^4
#


# @lc code=start
class Solution:
    def countPrimeSetBits(self, left: int, right: int) -> int:
        """
        Interview explanation:
        For each number in [left, right], count set bits; check if that count
        is prime. Counts are at most 20 for 32-bit constraints here, so a small
        prime set suffices.

        Algorithm:
        - primes = {2,3,5,7,11,13,17,19}
        - Count how many n have bin(n).count('1') in primes

        Complexity: O((right-left+1) * bitwidth) time, O(1) space.
        """
        primes = {2, 3, 5, 7, 11, 13, 17, 19}
        return sum(n.bit_count() in primes for n in range(left, right + 1))
# @lc code=end

