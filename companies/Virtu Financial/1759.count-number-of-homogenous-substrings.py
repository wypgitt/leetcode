#
# @lc app=leetcode id=1759 lang=python3
#
# [1759] Count Number of Homogenous Substrings
#
# https://leetcode.com/problems/count-number-of-homogenous-substrings/description/
#
# algorithms
# Medium (57.34%)
# Likes:    1592
# Dislikes: 104
# Total Accepted:    135K
# Total Submissions: 236K
# Testcase Example:  "\"abbcccaa\""
#
# Given a string s, return the number of homogenous substrings of s. Since the
# answer may be too large, return it modulo 10^9 + 7.
#
# A string is homogenous if all the characters of the string are the same.
#
# A substring is a contiguous sequence of characters within a string.
#
# Example 1:
#
# Input: s = "abbcccaa"
# Output: 13
# Explanation: The homogenous substrings are listed as below:
# "a" appears 3 times.
# "aa" appears 1 time.
# "b" appears 2 times.
# "bb" appears 1 time.
# "c" appears 3 times.
# "cc" appears 2 times.
# "ccc" appears 1 time.
# 3 + 1 + 2 + 1 + 3 + 2 + 1 = 13.
#
# Example 2:
#
# Input: s = "xy"
# Output: 2
# Explanation: The homogenous substrings are "x" and "y".
#
# Example 3:
#
# Input: s = "zzzzz"
# Output: 15
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of lowercase letters.
#

# @lc code=start
class Solution:
    def countHomogenous(self, s: str) -> int:
        """
        Interview explanation:
        Homogenous substring = contiguous equal chars. A run of length L
        contributes L*(L+1)/2 substrings. Sum over runs mod 10^9+7.

        Algorithm:
        - Scan runs; for length L add L*(L+1)//2.

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        ans = i = 0
        n = len(s)
        while i < n:
            j = i
            while j < n and s[j] == s[i]:
                j += 1
            L = j - i
            ans = (ans + L * (L + 1) // 2) % MOD
            i = j
        return ans

    def countHomogenous_streak(self, s: str) -> int:
        """
        Interview explanation:
        Alternate one-pass: maintain current streak; at each index add streak
        (# of new homogenous substrings ending here).

        Algorithm:
        - streak resets on char change; ans = (ans + streak) % MOD.

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        ans = streak = 0
        prev = ""
        for ch in s:
            streak = streak + 1 if ch == prev else 1
            prev = ch
            ans = (ans + streak) % MOD
        return ans
# @lc code=end
