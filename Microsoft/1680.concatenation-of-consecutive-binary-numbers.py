#
# @lc app=leetcode id=1680 lang=python3
#
# [1680] Concatenation of Consecutive Binary Numbers
#
# https://leetcode.com/problems/concatenation-of-consecutive-binary-numbers/description/
#
# algorithms
# Medium (66.69%)
# Likes:    1779
# Dislikes: 450
# Total Accepted:    196K
# Total Submissions: 294K
# Testcase Example:  "1"
#
# Given an integer n, return the decimal value of the binary string formed by
# concatenating the binary representations of 1 to n in order, modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 1
# Output: 1
# Explanation: "1" in binary corresponds to the decimal value 1.
#
# Example 2:
#
# Input: n = 3
# Output: 27
# Explanation: In binary, 1, 2, and 3 corresponds to "1", "10", and "11".
# After concatenating them, we have "11011", which corresponds to the decimal
# value 27.
#
# Example 3:
#
# Input: n = 12
# Output: 505379714
# Explanation: The concatenation results in
# "1101110010111011110001001101010111100".
# The decimal value of that is 118505380540.
# After modulo 10^9 + 7, the result is 505379714.
#
# Constraints:
#
# 1 <= n <= 10^5
#

# @lc code=start
class Solution:
    def concatenatedBinary(self, n: int) -> int:
        """
        Interview explanation:
        Concatenate binary of 1..n; return decimal mod 10^9+7. Maintain bit length
        of current number; when i is power of 2, length increases.

        Algorithm:
        - ans=0; length=0; MOD=10**9+7; for i in 1..n: if i&(i-1)==0: length++;
          ans = ((ans<<length)|i) % MOD

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        ans = 0
        length = 0
        for i in range(1, n + 1):
            if i & (i - 1) == 0:
                length += 1
            ans = ((ans << length) | i) % MOD
        return ans

    def concatenatedBinary_bit_length(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: use i.bit_length() each step instead of power-of-two tracking.

        Algorithm:
        - ans=0; for i in 1..n: ans=((ans<<i.bit_length())|i)%MOD

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        ans = 0
        for i in range(1, n + 1):
            ans = ((ans << i.bit_length()) | i) % MOD
        return ans
# @lc code=end
