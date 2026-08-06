#
# @lc app=leetcode id=1062 lang=python3
#
# [1062] Longest Repeating Substring
#
# https://leetcode.com/problems/longest-repeating-substring/description/
#
# algorithms
# Medium (63.46%)
# Likes:    731
# Dislikes: 76
# Total Accepted:    58.4K
# Total Submissions: 92.1K
# Testcase Example:  "\"abcd\""
#
#
# Given a string s, return the length of the longest repeating substrings.
# If no repeating substring exists, return 0.
#
# Example 1:
#
# Input: s = "abcd"
# Output: 0
# Explanation: There is no repeating substring.
#
# Example 2:
#
# Input: s = "abbaba"
# Output: 2
# Explanation: The longest repeating substrings are "ab" and "ba", each of
# which occurs twice.
#
# Example 3:
#
# Input: s = "aabcaabdaab"
# Output: 3
# Explanation: The longest repeating substring is "aab", which occurs 3
# times.
#
# Constraints:
#
# 1 <= s.length <= 2000
#
# s consists of lowercase English letters.
#
# @lc code=start
class Solution:
    def longestRepeatingSubstring(self, s: str) -> int:
        """
        Interview explanation:
        Premium. Longest substring that appears at least twice (may overlap).
        Binary search length L; check duplicates via set of rolling hashes or
        substring set.

        Algorithm:
        - lo=0,hi=n-1; while lo<hi: mid; if has_dup(mid): lo=mid else hi=mid-1
        - has_dup: set of s[i:i+L]

        Complexity: O(n^2) with plain substrings / O(n log n) expected with RH.
        """
        n = len(s)

        def has_dup(L: int) -> bool:
            seen = set()
            for i in range(n - L + 1):
                sub = s[i : i + L]
                if sub in seen:
                    return True
                seen.add(sub)
            return False

        lo, hi = 0, n - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if has_dup(mid):
                lo = mid
            else:
                hi = mid - 1
        return lo

    def longestRepeatingSubstring_dp(self, s: str) -> int:
        """
        Interview explanation:
        Alternate DP: dp[i][j] = longest common suffix of s[:i] and s[:j]
        with i!=j; answer max dp[i][j].

        Algorithm:
        - For i,j >0: if s[i-1]==s[j-1]: dp[i][j]=dp[i-1][j-1]+1
        - Track global max (only when i!=j implicit by separate endings)

        Complexity: O(n^2) time and space.
        """
        n = len(s)
        dp = [[0] * (n + 1) for _ in range(n + 1)]
        best = 0
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if s[i - 1] == s[j - 1] and i != j:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                    best = max(best, dp[i][j])
        return best
# @lc code=end
