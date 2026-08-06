#
# @lc app=leetcode id=1318 lang=python3
#
# [1318] Minimum Flips to Make a OR b Equal to c
#
# https://leetcode.com/problems/minimum-flips-to-make-a-or-b-equal-to-c/description/
#
# algorithms
# Medium (72.06%)
# Likes:    2155
# Dislikes: 113
# Total Accepted:    206K
# Total Submissions: 286K
# Testcase Example:  "2"
#
# Given 3 positives numbers a, b and c. Return the minimum flips required in
# some bits of a and b to make ( a OR b == c ). (bitwise OR operation).
#
# Flip operation consists of change any single bit 1 to 0 or change the bit 0
# to 1 in their binary representation.
#
# Example 1:
#
# Input: a = 2, b = 6, c = 5
# Output: 3
# Explanation: After flips a = 1 , b = 4 , c = 5 such that (a OR b == c)
#
# Example 2:
#
# Input: a = 4, b = 2, c = 7
# Output: 1
#
# Example 3:
#
# Input: a = 1, b = 2, c = 3
# Output: 0
#
# Constraints:
#
# 1 <= a <= 10^9
#
# 1 <= b <= 10^9
#
# 1 <= c <= 10^9
#

# @lc code=start
class Solution:
    def minFlips(self, a: int, b: int, c: int) -> int:
        """
        Interview explanation:
        Bitwise: for each bit of c, make (a|b) match via flips on a/b bits.
        If c bit=1 need at least one of a/b set (0 or 1 flip). If c bit=0 both
        must be 0 (flip each that is 1).

        Algorithm:
        - For each bit 0..31 compare and accumulate flips.

        Complexity: O(1) time (32 bits), O(1) space.
        """
        flips = 0
        for i in range(32):
            abit = (a >> i) & 1
            bbit = (b >> i) & 1
            cbit = (c >> i) & 1
            if cbit == 1:
                if abit == 0 and bbit == 0:
                    flips += 1
            else:
                flips += abit + bbit
        return flips
# @lc code=end

