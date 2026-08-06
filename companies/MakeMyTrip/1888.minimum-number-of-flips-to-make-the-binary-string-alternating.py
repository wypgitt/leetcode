#
# @lc app=leetcode id=1888 lang=python3
#
# [1888] Minimum Number of Flips to Make the Binary String Alternating
#
# https://leetcode.com/problems/minimum-number-of-flips-to-make-the-binary-string-alternating/description/
#
# algorithms
# Medium (53.69%)
# Likes:    1830
# Dislikes: 122
# Total Accepted:    130K
# Total Submissions: 243K
# Testcase Example:  "\"111000\""
#
# You are given a binary string s. You are allowed to perform two types of
# operations on the string in any sequence:
#
# Type-1: Remove the character at the start of the string s and append it to
# the end of the string.
#
# Type-2: Pick any character in s and flip its value, i.e., if its value is '0'
# it becomes '1' and vice-versa.
#
# Return the minimum number of type-2 operations you need to perform such that
# s becomes alternating.
#
# The string is called alternating if no two adjacent characters are equal.
#
# For example, the strings "010" and "1010" are alternating, while the string
# "0100" is not.
#
# Example 1:
#
# Input: s = "111000"
# Output: 2
# Explanation: Use the first operation two times to make s = "100011".
# Then, use the second operation on the third and sixth elements to make s =
# "101010".
#
# Example 2:
#
# Input: s = "010"
# Output: 0
# Explanation: The string is already alternating.
#
# Example 3:
#
# Input: s = "1110"
# Output: 1
# Explanation: Use the second operation on the second element to make s =
# "1010".
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s[i] is either '0' or '1'.
#

# @lc code=start
class Solution:
    def minFlips(self, s: str) -> int:
        """
        Interview explanation:
        Can rotate (type-1) and flip bits (type-2). Min flips to make alternating.
        Double string + sliding window of length n vs patterns 0101… and 1010….

        Algorithm (sliding window on s+s):
        - Build alt0/alt1 of length 2n; maintain mismatch counts for window n;
          answer = min over windows and both patterns.

        Complexity: O(n) time, O(n) space.
        """
        n = len(s)
        s2 = s + s
        alt0 = "".join("01"[i % 2] for i in range(2 * n))
        alt1 = "".join("10"[i % 2] for i in range(2 * n))
        diff0 = diff1 = 0
        ans = n
        for i in range(2 * n):
            if s2[i] != alt0[i]:
                diff0 += 1
            if s2[i] != alt1[i]:
                diff1 += 1
            if i >= n:
                if s2[i - n] != alt0[i - n]:
                    diff0 -= 1
                if s2[i - n] != alt1[i - n]:
                    diff1 -= 1
            if i >= n - 1:
                ans = min(ans, diff0, diff1)
        return ans

    def minFlips_even_odd_counts(self, s: str) -> int:
        """
        Interview explanation:
        Classic alternate when n is even: rotations preserve even/odd parity
        pairing with target; answer is min flips for 01-repeat vs 10-repeat on s
        (rotation cannot help beyond that for even n). For odd n, rotation changes
        parity — fall back to sliding-window method.

        Algorithm:
        - If n odd: return minFlips(s).
        - Else: count mismatches vs "01"* and "10"*; return min.

        Complexity: O(n) time, O(1) extra when n even.
        """
        n = len(s)
        if n % 2 == 1:
            return self.minFlips(s)
        d0 = sum(ch != "01"[i % 2] for i, ch in enumerate(s))
        d1 = sum(ch != "10"[i % 2] for i, ch in enumerate(s))
        return min(d0, d1)
# @lc code=end
