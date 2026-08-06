#
# @lc app=leetcode id=940 lang=python3
#
# [940] Distinct Subsequences II
#
# https://leetcode.com/problems/distinct-subsequences-ii/description/
#
# algorithms
# Hard (44.18%)
# Likes:    1850
# Dislikes: 40
# Total Accepted:    53.8K
# Total Submissions: 122K
# Testcase Example:  "\"abc\""
#
# Given a string s, return the number of distinct non-empty subsequences of s.
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# A subsequence of a string is a new string that is formed from the original
# string by deleting some (can be none) of the characters without disturbing
# the relative positions of the remaining characters. (i.e., "ace" is a
# subsequence of "abcde" while "aec" is not.
#
# Example 1:
#
# Input: s = "abc"
# Output: 7
# Explanation: The 7 distinct subsequences are "a", "b", "c", "ab", "ac", "bc",
# and "abc".
#
# Example 2:
#
# Input: s = "aba"
# Output: 6
# Explanation: The 6 distinct subsequences are "a", "b", "ab", "aa", "ba", and
# "aba".
#
# Example 3:
#
# Input: s = "aaa"
# Output: 3
# Explanation: The 3 distinct subsequences are "a", "aa" and "aaa".
#
# Constraints:
#
# 1 <= s.length <= 2000
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def distinctSubseqII(self, s: str) -> int:
        """
        Interview explanation:
        DP: endswith[c] = number of distinct subsequences ending with c.
        Processing char c: new subsequences = (1 + sum(all endswith)) by
        appending c to every previous subsequence (plus singleton c); this
        replaces endswith[c] (old ones ending with c are subsumed).

        Algorithm (DP):
        - MOD=1e9+7; end=[0]*26
        - For ch in s: end[ch] = (1 + sum(end)) % MOD
        - Return sum(end) % MOD

        Complexity: O(n * 26) time, O(26) space.
        """
        MOD = 10**9 + 7
        end = [0] * 26
        for ch in s:
            end[ord(ch) - 97] = (1 + sum(end)) % MOD
        return sum(end) % MOD
# @lc code=end

