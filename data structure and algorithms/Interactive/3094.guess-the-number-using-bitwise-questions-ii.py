#
# @lc app=leetcode id=3094 lang=python3
#
# [3094] Guess the Number Using Bitwise Questions II
#
# https://leetcode.com/problems/guess-the-number-using-bitwise-questions-ii/description/
#
# algorithms
# Medium (83.00%)
# Likes:    15
# Dislikes: 4
# Total Accepted:    1.2K
# Total Submissions: 1.4K
# Testcase Example:  "31"
#
#
# There is a number n between 0 and 2^30 - 1 (both inclusive) that you
# have to find.
#
# There is a pre-defined API int commonBits(int num) that helps you with
# your mission. But here is the challenge, every time you call this
# function, n changes in some way. But keep in mind, that you have to find
# the initial value of n.
#
# commonBits(int num) acts as follows:
#
# Calculate count which is the number of bits where both n and num have
# the same value in that position of their binary representation.
#
# n = n XOR num
#
# Return count.
#
# Return the number n.
#
# Note: In this world, all numbers are between 0 and 2^30 - 1 (both
# inclusive), thus for counting common bits, we see only the first 30 bits
# of those numbers.
#
# Constraints:
#
# 0 <= n <= 2^30 - 1
#
# 0 <= num <= 2^30 - 1
#
# If you ask for some num out of the given range, the output wouldn't be
# reliable.
#

# @lc code=start
# Definition of commonBits API.
# def commonBits(num: int) -> int:

class Solution:
    def findNumber(self) -> int:
        """
        Interview explanation:
        commonBits(num) returns how many of the first 30 bits match n, then
        XORs n ^= num. Recover the initial n bit by bit.

        Algorithm:
        - For each bit i, call commonBits(1<<i) twice (second undoes the XOR).
        - If the first count > second, bit i of the original n was 1 (matching
          improved when that bit was 1 before the flip).

        Complexity: O(1) queries (30 bits * 2), O(1) space.
        """
        n = 0
        for i in range(30):
            count1 = commonBits(1 << i)
            count2 = commonBits(1 << i)
            if count1 > count2:
                n |= 1 << i
        return n
# @lc code=end
