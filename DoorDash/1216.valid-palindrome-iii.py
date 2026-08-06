#
# @lc app=leetcode id=1216 lang=python3
#
# [1216] Valid Palindrome III
#
# https://leetcode.com/problems/valid-palindrome-iii/description/
#
# algorithms
# Hard (49.17%)
# Likes:    844
# Dislikes: 15
# Total Accepted:    109.5K
# Total Submissions: 222.8K
# Testcase Example:  "\"abcdeca\"\n2"
#
#
# Given a string s and an integer k, return true if s is a k-palindrome.
#
# A string is k-palindrome if it can be transformed into a palindrome by
# removing at most k characters from it.
#
# Example 1:
#
# Input: s = "abcdeca", k = 2
# Output: true
# Explanation: Remove 'b' and 'e' characters.
#
# Example 2:
#
# Input: s = "abbababa", k = 1
# Output: true
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# s consists of only lowercase English letters.
#
# 1 <= k <= s.length
#
# @lc code=start
class Solution:
    def isValidPalindrome(self, s: str, k: int) -> bool:
        """
        Interview explanation:
        Premium. Can s become a palindrome by deleting at most k chars?
        Equivalent: len(s) - LPS(s) <= k where LPS is longest palindromic
        subsequence (= LCS(s, reverse(s))).

        Algorithm:
        - DP LCS between s and s[::-1]; return n - LCS <= k
        - Space-optimized 1D DP for LCS

        Complexity: O(n^2) time/space (can O(n) space).
        """
        n = len(s)
        rev = s[::-1]
        prev = [0] * (n + 1)
        for i in range(1, n + 1):
            cur = [0] * (n + 1)
            for j in range(1, n + 1):
                if s[i - 1] == rev[j - 1]:
                    cur[j] = prev[j - 1] + 1
                else:
                    cur[j] = max(prev[j], cur[j - 1])
            prev = cur
        return n - prev[n] <= k

    def isValidPalindrome_dp(self, s: str, k: int) -> bool:
        """
        Interview explanation:
        Alternate interval DP: dp[i][j] = min deletions to make s[i..j] palindrome.
        Return dp[0][n-1] <= k.

        Algorithm:
        - If s[i]==s[j]: dp[i][j]=dp[i+1][j-1]; else 1+min(dp[i+1][j], dp[i][j-1])

        Complexity: O(n^2) time/space.
        """
        n = len(s)
        dp = [[0] * n for _ in range(n)]
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                if s[i] == s[j]:
                    dp[i][j] = dp[i + 1][j - 1] if length > 2 else 0
                else:
                    dp[i][j] = 1 + min(dp[i + 1][j], dp[i][j - 1])
        return dp[0][n - 1] <= k
# @lc code=end
