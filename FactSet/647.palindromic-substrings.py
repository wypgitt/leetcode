#
# @lc app=leetcode id=647 lang=python3
#
# [647] Palindromic Substrings
#
# https://leetcode.com/problems/palindromic-substrings/description/
#
# algorithms
# Medium (73.08%)
# Likes:    11650
# Dislikes: 258
# Total Accepted:    1.2M
# Total Submissions: 1.7M
# Testcase Example:  "\"abc\""
#
# Given a string s, return the number of palindromic substrings in it.
#
# A string is a palindrome when it reads the same backward as forward.
#
# A substring is a contiguous sequence of characters within the string.
#
# Example 1:
#
# Input: s = "abc"
# Output: 3
# Explanation: Three palindromic strings: "a", "b", "c".
#
# Example 2:
#
# Input: s = "aaa"
# Output: 6
# Explanation: Six palindromic strings: "a", "a", "a", "aa", "aa", "aaa".
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# s consists of lowercase English letters.
#

# @lc code=start

class Solution:
    def countSubstrings(self, s: str) -> int:
        """
        Interview explanation:
        Count palindromic substrings by expanding around every center (odd and
        even length).

        Algorithm:
        - For each i, expand (i,i) and (i,i+1) while s[L]==s[R]; count each.

        Complexity: O(N^2) time, O(1) space.
        """
        n = len(s)
        ans = 0

        def expand(l: int, r: int) -> int:
            cnt = 0
            while l >= 0 and r < n and s[l] == s[r]:
                cnt += 1
                l -= 1
                r += 1
            return cnt

        for i in range(n):
            ans += expand(i, i)
            ans += expand(i, i + 1)
        return ans

    def countSubstrings_dp(self, s: str) -> int:
        """
        Interview explanation:
        Alternate classic: DP boolean table dp[i][j] = s[i]==s[j] and
        (j-i<2 or dp[i+1][j-1]); count True cells.

        Algorithm:
        - Fill by increasing length; ans += 1 when dp[i][j].

        Complexity: O(N^2) time and space.
        """
        n = len(s)
        dp = [[False] * n for _ in range(n)]
        ans = 0
        for i in range(n - 1, -1, -1):
            for j in range(i, n):
                if s[i] == s[j] and (j - i < 2 or dp[i + 1][j - 1]):
                    dp[i][j] = True
                    ans += 1
        return ans
# @lc code=end
