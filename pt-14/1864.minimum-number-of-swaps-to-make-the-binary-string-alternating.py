#
# @lc app=leetcode id=1864 lang=python3
#
# [1864] Minimum Number of Swaps to Make the Binary String Alternating
#
# https://leetcode.com/problems/minimum-number-of-swaps-to-make-the-binary-string-alternating/description/
#
# algorithms
# Medium (44.02%)
# Likes:    633
# Dislikes: 38
# Total Accepted:    37.1K
# Total Submissions: 84.3K
# Testcase Example:  "\"111000\""
#
# Given a binary string s, return the minimum number of character swaps to make
# it alternating, or -1 if it is impossible.
#
# The string is called alternating if no two adjacent characters are equal. For
# example, the strings "010" and "1010" are alternating, while the string
# "0100" is not.
#
# Any two characters may be swapped, even if they are not adjacent.
#
# Example 1:
#
# Input: s = "111000"
# Output: 1
# Explanation: Swap positions 1 and 4: "111000" -> "101010"
# The string is now alternating.
#
# Example 2:
#
# Input: s = "010"
# Output: 0
# Explanation: The string is already alternating, no swaps are needed.
#
# Example 3:
#
# Input: s = "1110"
# Output: -1
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# s[i] is either '0' or '1'.
#

# @lc code=start
class Solution:
    def minSwaps(self, s: str) -> int:
        """
        Interview explanation:
        Make binary string alternating with swaps (or -1). Count 0s/1s; if
        |c0-c1|>1 impossible. Try patterns starting with 0 and/or 1; swaps =
        mismatches/2.

        Algorithm:
        - c0,c1 = counts; if abs>1: -1.
        - cost(start): mismatches where s[i]!= expected; return mismatches//2.
        - If c0==c1: min(cost(0),cost(1)); elif c1>c0: cost(1) else cost(0).

        Complexity: O(n) time, O(1) space.
        """
        c0 = s.count("0")
        c1 = len(s) - c0
        if abs(c0 - c1) > 1:
            return -1

        def cost(start: int) -> int:
            # start=0 means pattern 0101..., start=1 means 1010...
            mis = 0
            for i, ch in enumerate(s):
                expect = str((start + i) % 2)
                if ch != expect:
                    mis += 1
            return mis // 2

        if c0 == c1:
            return min(cost(0), cost(1))
        return cost(1) if c1 > c0 else cost(0)
# @lc code=end
