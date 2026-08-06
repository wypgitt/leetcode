#
# @lc app=leetcode id=3563 lang=python3
#
# [3563] Lexicographically Smallest String After Adjacent Removals
#
# https://leetcode.com/problems/lexicographically-smallest-string-after-adjacent-removals/description/
#
# algorithms
# Hard (17.96%)
# Likes:    53
# Dislikes: 4
# Total Accepted:    4.3K
# Total Submissions: 23.8K
# Testcase Example:  "\"abc\""
#
#
# You are given a string s consisting of lowercase English letters.
#
# You can perform the following operation any number of times (including
# zero):
#
# Remove any pair of adjacent characters in the string that are
# consecutive in the alphabet, in either order (e.g., 'a' and 'b', or 'b'
# and 'a').
#
# Shift the remaining characters to the left to fill the gap.
#
# Return the lexicographically smallest string that can be obtained after
# performing the operations optimally.
#
# Note: Consider the alphabet as circular, thus 'a' and 'z' are
# consecutive.
#
# Example 1:
#
# Input: s = "abc"
#
# Output: "a"
#
# Explanation:
#
# Remove "bc" from the string, leaving "a" as the remaining string.
#
# No further operations are possible. Thus, the lexicographically smallest
# string after all possible removals is "a".
#
# Example 2:
#
# Input: s = "bcda"
#
# Output: ""
#
# Explanation:
#
# ​​​​​​​Remove "cd" from the string, leaving "ba" as the remaining
# string.
#
# Remove "ba" from the string, leaving "" as the remaining string.
#
# No further operations are possible. Thus, the lexicographically smallest
# string after all possible removals is "".
#
# Example 3:
#
# Input: s = "zdce"
#
# Output: "zdce"
#
# Explanation:
#
# Remove "dc" from the string, leaving "ze" as the remaining string.
#
# No further operations are possible on "ze".
#
# However, since "zdce" is lexicographically smaller than "ze", the
# smallest string after all possible removals is "zdce".
#
# Constraints:
#
# 1 <= s.length <= 250
#
# s consists only of lowercase English letters.
#

# @lc code=start

class Solution:
    def lexicographicallySmallestString(self, s: str) -> str:
        """
        Interview explanation:
        Removals are optional and order matters for the final string. Interval DP
        finds the lex-smallest residue of every substring.

        Algorithm:
        - dp[i][j] = lex-smallest string obtainable from s[i:j].
        - Keep s[i] + dp[i+1][j], or if s[i] pairs with s[k] and dp[i+1][k] == "",
          take dp[k+1][j] (pair deleted after middle collapses).
        - Consecutive means |a-b| in {1, 25}.

        Complexity: O(n^3) time (string compares add a factor), O(n^2) space.
        """
        n = len(s)

        def consecutive(a: str, b: str) -> bool:
            d = abs(ord(a) - ord(b))
            return d == 1 or d == 25

        dp = [[''] * (n + 1) for _ in range(n + 1)]
        for length in range(1, n + 1):
            for i in range(n - length + 1):
                j = i + length
                best = s[i] + dp[i + 1][j]
                for k in range(i + 1, j):
                    if consecutive(s[i], s[k]) and dp[i + 1][k] == '':
                        cand = dp[k + 1][j]
                        if cand < best:
                            best = cand
                dp[i][j] = best
        return dp[0][n]
# @lc code=end
