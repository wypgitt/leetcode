#
# @lc app=leetcode id=3750 lang=python3
#
# [3750] Minimum Number of Flips to Reverse Binary String
#
# https://leetcode.com/problems/minimum-number-of-flips-to-reverse-binary-string/description/
#
# algorithms
# Easy (76.98%)
# Likes:    41
# Dislikes: 1
# Total Accepted:    35.2K
# Total Submissions: 45.7K
# Testcase Example:  "7"
#
#
# You are given a positive integer n.
#
# Let s be the binary representation of n without leading zeros.
#
# The reverse of a binary string s is obtained by writing the characters
# of s in the opposite order.
#
# You may flip any bit in s (change 0 → 1 or 1 → 0). Each flip affects
# exactly one bit.
#
# Return the minimum number of flips required to make s equal to the
# reverse of its original form.
#
# Example 1:
#
# Input: n = 7
#
# Output: 0
#
# Explanation:
#
# The binary representation of 7 is "111". Its reverse is also "111",
# which is the same. Hence, no flips are needed.
#
# Example 2:
#
# Input: n = 10
#
# Output: 4
#
# Explanation:
#
# The binary representation of 10 is "1010". Its reverse is "0101". All
# four bits must be flipped to make them equal. Thus, the minimum number
# of flips required is 4.
#
# Constraints:
#
# 1 <= n <= 10^9
#

# @lc code=start
class Solution:
    def minimumFlips(self, n: int) -> int:
        """
        Interview explanation:
        Target is the reverse of the original binary string. Flips change s toward
        that fixed target, so answer is the Hamming distance between s and reverse(s).

        Algorithm:
        - Compare bit i with bit (L-1-i) for the binary length L of n.

        Complexity: O(log n) time, O(1) space.
        """
        s = bin(n)[2:]
        return sum(s[i] != s[-1 - i] for i in range(len(s)))

    def minimumFlips_bits(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: same check with bit operations (no string).

        Algorithm:
        - Let L = bit_length; count positions where bit i != bit L-1-i.

        Complexity: O(log n) time, O(1) space.
        """
        L = n.bit_length()
        ans = 0
        for i in range(L):
            a = (n >> i) & 1
            b = (n >> (L - 1 - i)) & 1
            ans += a != b
        return ans
# @lc code=end
