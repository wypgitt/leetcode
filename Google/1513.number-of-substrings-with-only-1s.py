#
# @lc app=leetcode id=1513 lang=python3
#
# [1513] Number of Substrings With Only 1s
#
# https://leetcode.com/problems/number-of-substrings-with-only-1s/description/
#
# algorithms
# Medium (57.37%)
# Likes:    1241
# Dislikes: 42
# Total Accepted:    163K
# Total Submissions: 285K
# Testcase Example:  "\"0110111\""
#
# Given a binary string s, return the number of substrings with all characters
# 1's. Since the answer may be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: s = "0110111"
# Output: 9
# Explanation: There are 9 substring in total with only 1's characters.
# "1" -> 5 times.
# "11" -> 3 times.
# "111" -> 1 time.
#
# Example 2:
#
# Input: s = "101"
# Output: 2
# Explanation: Substring "1" is shown 2 times in s.
#
# Example 3:
#
# Input: s = "111111"
# Output: 21
# Explanation: Each substring contains only 1's characters.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s[i] is either '0' or '1'.
#

# @lc code=start
class Solution:
    def numSub(self, s: str) -> int:
        """
        Interview explanation:
        Count substrings of only '1's. A run of length L contributes L*(L+1)/2
        substrings. Scan runs (or accumulate streak).

        Algorithm:
        - streak=0; for ch: streak=streak+1 if '1' else 0; ans+=streak; mod 1e9+7.

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        ans = streak = 0
        for ch in s:
            if ch == "1":
                streak += 1
                ans = (ans + streak) % MOD
            else:
                streak = 0
        return ans

    def numSub_runs(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: explicitly find each run of ones of length L; add L*(L+1)/2.

        Algorithm:
        - Two pointers over runs; ans += L*(L+1)//2 % MOD.

        Complexity: O(n) time, O(1) space.
        """
        MOD = 10**9 + 7
        ans = i = 0
        n = len(s)
        while i < n:
            if s[i] != "1":
                i += 1
                continue
            j = i
            while j < n and s[j] == "1":
                j += 1
            L = j - i
            ans = (ans + L * (L + 1) // 2) % MOD
            i = j
        return ans
# @lc code=end
