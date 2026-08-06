#
# @lc app=leetcode id=1771 lang=python3
#
# [1771] Maximize Palindrome Length From Subsequences
#
# https://leetcode.com/problems/maximize-palindrome-length-from-subsequences/description/
#
# algorithms
# Hard (38.66%)
# Likes:    571
# Dislikes: 18
# Total Accepted:    15.2K
# Total Submissions: 39.4K
# Testcase Example:  "\"cacb\""
#
# You are given two strings, word1 and word2. You want to construct a string in
# the following manner:
#
# Choose some non-empty subsequence subsequence1 from word1.
#
# Choose some non-empty subsequence subsequence2 from word2.
#
# Concatenate the subsequences: subsequence1 + subsequence2, to make the
# string.
#
# Return the length of the longest palindrome that can be constructed in the
# described manner. If no palindromes can be constructed, return 0.
#
# A subsequence of a string s is a string that can be made by deleting some
# (possibly none) characters from s without changing the order of the remaining
# characters.
#
# A palindrome is a string that reads the same forward as well as backward.
#
# Example 1:
#
# Input: word1 = "cacb", word2 = "cbba"
# Output: 5
# Explanation: Choose "ab" from word1 and "cba" from word2 to make "abcba",
# which is a palindrome.
#
# Example 2:
#
# Input: word1 = "ab", word2 = "ab"
# Output: 3
# Explanation: Choose "ab" from word1 and "a" from word2 to make "aba", which
# is a palindrome.
#
# Example 3:
#
# Input: word1 = "aa", word2 = "bb"
# Output: 0
# Explanation: You cannot construct a palindrome from the described method, so
# return 0.
#
# Constraints:
#
# 1 <= word1.length, word2.length <= 1000
#
# word1 and word2 consist of lowercase English letters.
#

# @lc code=start
class Solution:
    def longestPalindrome(self, word1: str, word2: str) -> int:
        """
        Interview explanation:
        Build a palindrome using a subsequence of word1+word2 that must take
        ≥1 char from each. Compute LPS DP on s=word1+word2, but only accept
        palindromes that cross the boundary (use both sides).

        Algorithm:
        - s = word1+word2; n=len(s); split=len(word1).
        - dp[i][j] = LPS length in s[i..j].
        - When s[i]==s[j] and i<split<=j: ans = max(ans, dp[i][j]).

        Complexity: O(n^2) time and space.
        """
        s = word1 + word2
        n = len(s)
        split = len(word1)
        dp = [[0] * n for _ in range(n)]
        ans = 0
        for i in range(n - 1, -1, -1):
            dp[i][i] = 1
            for j in range(i + 1, n):
                if s[i] == s[j]:
                    dp[i][j] = dp[i + 1][j - 1] + 2 if j - i > 1 else 2
                    if i < split <= j:
                        ans = max(ans, dp[i][j])
                else:
                    dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
        return ans
# @lc code=end
