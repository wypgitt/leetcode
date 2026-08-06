#
# @lc app=leetcode id=191 lang=python3
#
# [191] Number of 1 Bits
#
# https://leetcode.com/problems/number-of-1-bits/description/
#
# algorithms
# Easy (77.29%)
# Likes:    7217
# Dislikes: 1372
# Total Accepted:    2.2M
# Total Submissions: 2.9M
# Testcase Example:  "11"
#
# Given a positive integer n, write a function that returns the number of set
# bits in its binary representation (also known as the Hamming weight).
#
# Example 1:
#
# Input: n = 11
#
# Output: 3
#
# Explanation:
#
# The input binary string 1011 has a total of three set bits.
#
# Example 2:
#
# Input: n = 128
#
# Output: 1
#
# Explanation:
#
# The input binary string 10000000 has a total of one set bit.
#
# Example 3:
#
# Input: n = 2147483645
#
# Output: 30
#
# Explanation:
#
# The input binary string 1111111111111111111111111111101 has a total of thirty
# set bits.
#
# Constraints:
#
# 1 <= n <= 2^31 - 1
#
# Follow up: If this function is called many times, how would you optimize it?
#

# @lc code=start
class Solution:
    def hammingWeight(self, n: int) -> int:
        """
        Interview explanation:
        Brian Kernighan's algorithm: n &= n - 1 clears the lowest set bit each
        iteration, so the loop runs once per set bit.

        Algorithm:
        - count = 0; while n: n &= n - 1; count += 1; return count.

        Complexity: O(k) time for k set bits, O(1) space.
        """
        count = 0
        while n:
            n &= n - 1
            count += 1
        return count

    def hammingWeight_bin(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: convert to binary string / use bit_count and count ones.

        Algorithm:
        - return bin(n).count("1") (or n.bit_count() on modern Python).

        Complexity: O(log n) time, O(log n) space for the binary string.
        """
        return bin(n).count("1")
# @lc code=end
