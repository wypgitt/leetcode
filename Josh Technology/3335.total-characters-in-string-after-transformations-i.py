#
# @lc app=leetcode id=3335 lang=python3
#
# [3335] Total Characters in String After Transformations I
#
# https://leetcode.com/problems/total-characters-in-string-after-transformations-i/description/
#
# algorithms
# Medium (45.65%)
# Likes:    618
# Dislikes: 47
# Total Accepted:    118K
# Total Submissions: 258.6K
# Testcase Example:  "\"abcyy\"\n2"
#
#
# You are given a string s and an integer t, representing the number of
# transformations to perform. In one transformation, every character in s
# is replaced according to the following rules:
#
# If the character is 'z', replace it with the string "ab".
#
# Otherwise, replace it with the next character in the alphabet. For
# example, 'a' is replaced with 'b', 'b' is replaced with 'c', and so on.
#
# Return the length of the resulting string after exactly t
# transformations.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: s = "abcyy", t = 2
#
# Output: 7
#
# Explanation:
#
# First Transformation (t = 1):
#
# 'a' becomes 'b'
#
# 'b' becomes 'c'
#
# 'c' becomes 'd'
#
# 'y' becomes 'z'
#
# 'y' becomes 'z'
#
# String after the first transformation: "bcdzz"
#
# Second Transformation (t = 2):
#
# 'b' becomes 'c'
#
# 'c' becomes 'd'
#
# 'd' becomes 'e'
#
# 'z' becomes "ab"
#
# 'z' becomes "ab"
#
# String after the second transformation: "cdeabab"
#
# Final Length of the string: The string is "cdeabab", which has 7
# characters.
#
# Example 2:
#
# Input: s = "azbk", t = 1
#
# Output: 5
#
# Explanation:
#
# First Transformation (t = 1):
#
# 'a' becomes 'b'
#
# 'z' becomes "ab"
#
# 'b' becomes 'c'
#
# 'k' becomes 'l'
#
# String after the first transformation: "babcl"
#
# Final Length of the string: The string is "babcl", which has 5
# characters.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists only of lowercase English letters.
#
# 1 <= t <= 10^5
#

# @lc code=start

class Solution:
    def lengthAfterTransformations(self, s: str, t: int) -> int:
        """
        Interview explanation:
        Each transform: letter -> next letter; 'z' -> "ab". Track length via
        26 frequency counts for t steps.

        Algorithm:
        - cnt[c] frequencies; each step shift forward, with z contributing to a
          and b.
        - Alternate: matrix exponentiation (see problem II) when t is huge.

        Complexity: O(|s| + 26 t) time, O(1) space.
        """
        MOD = 10**9 + 7
        cnt = [0] * 26
        for ch in s:
            cnt[ord(ch) - 97] += 1
        for _ in range(t):
            nxt = [0] * 26
            for i in range(25):
                nxt[i + 1] = cnt[i]
            nxt[0] = cnt[25]
            nxt[1] = (nxt[1] + cnt[25]) % MOD
            cnt = nxt
        return sum(cnt) % MOD
# @lc code=end

