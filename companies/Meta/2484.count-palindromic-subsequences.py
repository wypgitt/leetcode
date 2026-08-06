#
# @lc app=leetcode id=2484 lang=python3
#
# [2484] Count Palindromic Subsequences
#
# https://leetcode.com/problems/count-palindromic-subsequences/description/
#
# algorithms
# Hard (41.76%)
# Likes:    644
# Dislikes: 32
# Total Accepted:    23.8K
# Total Submissions: 57.1K
# Testcase Example:  "\"103301\""
#
# Given a string of digits s, return the number of palindromic subsequences of s
# having length 5. Since the answer may be very large, return it modulo 10^9 +
# 7.
#
# Note:
#
#
# A string is palindromic if it reads the same forward and backward.
#
#
# A subsequence is a string that can be derived from another string by deleting
# some or no characters without changing the order of the remaining characters.
#
#
#
# Example 1:
#
# Input: s = "103301"
# Output: 2
# Explanation:
# There are 6 possible subsequences of length 5:
# "10330","10331","10301","10301","13301","03301".
# Two of them (both equal to "10301") are palindromic.
#
# Example 2:
#
# Input: s = "0000000"
# Output: 21
# Explanation: All 21 subsequences are "00000", which is palindromic.
#
# Example 3:
#
# Input: s = "9999900000"
# Output: 2
# Explanation: The only two palindromic subsequences are "99999" and "00000".
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 10^4
#
#
# s consists of digits.
#

# @lc code=start
class Solution:
    def countPalindromes(self, s: str) -> int:
        """
        Interview explanation:
        Count length-5 palindromic subsequences (mod 1e9+7). Form abXba.

        Algorithm:
        - Pref[i][a][b]: count of subsequence "ab" in s[:i]; suf similarly to
          the right; for each center index multiply matching pairs.

        Complexity: O(100 n) time, O(100 n) space.
        """
        mod = 10**9 + 7
        n = len(s)
        pre = [[[0] * 10 for _ in range(10)] for _ in range(n + 2)]
        suf = [[[0] * 10 for _ in range(10)] for _ in range(n + 2)]
        t = [ord(c) - 48 for c in s]
        c = [0] * 10
        for i, v in enumerate(t, 1):
            for j in range(10):
                for k in range(10):
                    pre[i][j][k] = pre[i - 1][j][k]
            for j in range(10):
                pre[i][j][v] += c[j]
            c[v] += 1
        c = [0] * 10
        for i in range(n, 0, -1):
            v = t[i - 1]
            for j in range(10):
                for k in range(10):
                    suf[i][j][k] = suf[i + 1][j][k]
            for j in range(10):
                suf[i][j][v] += c[j]
            c[v] += 1
        ans = 0
        for i in range(1, n + 1):
            for j in range(10):
                for k in range(10):
                    ans += pre[i - 1][j][k] * suf[i + 1][j][k]
                    ans %= mod
        return ans
# @lc code=end

