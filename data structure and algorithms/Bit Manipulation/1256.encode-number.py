#
# @lc app=leetcode id=1256 lang=python3
#
# [1256] Encode Number
#
# https://leetcode.com/problems/encode-number/description/
#
# algorithms
# Medium (70.34%)
# Likes:    82
# Dislikes: 259
# Total Accepted:    8.8K
# Total Submissions: 12.5K
# Testcase Example:  "23"
#
#
# Given a non-negative integer num, Return its encoding string.
#
#
#
# The encoding is done by converting the integer to a string using a
# secret function that you should deduce from the following table:
#
#
#
#
#
#
#
#
# Example 1:
#
#
#
#
# Input: num = 23
# Output: "1000"
#
#
#
#
# Example 2:
#
#
#
#
# Input: num = 107
# Output: "101100"
#
#
#
#
#
#
# Constraints:
#
#
#
#
#
# 0 <= num <= 10^9
#
# @lc code=start

class Solution:
    def encode(self, num: int) -> str:
        """
        Interview explanation:
        Premium. Encoding maps 0->"", 1->"0", 2->"1", 3->"00", ... which is
        exactly the binary representation of (num+1) with the leading 1 removed.

        Algorithm:
        - Compute bin(num+1)[3:] (skip '0b' and the leading '1').

        Complexity: O(log num) time and space.
        """
        return bin(num + 1)[3:]

    def encode_loop(self, num: int) -> str:
        """
        Interview explanation:
        Alternate: build bits of num+1 manually then drop the MSB.

        Algorithm:
        - n=num+1; collect n%2 while n>1 (skip final 1); reverse join.

        Complexity: O(log num) time and space.
        """
        n = num + 1
        bits = []
        while n > 1:
            bits.append(str(n % 2))
            n //= 2
        return "".join(reversed(bits))
# @lc code=end
