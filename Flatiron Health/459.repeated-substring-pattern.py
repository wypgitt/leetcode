#
# @lc app=leetcode id=459 lang=python3
#
# [459] Repeated Substring Pattern
#
# https://leetcode.com/problems/repeated-substring-pattern/description/
#
# algorithms
# Easy (48.61%)
# Likes:    6922
# Dislikes: 572
# Total Accepted:    640K
# Total Submissions: 1.3M
# Testcase Example:  "\"abab\""
#
# Given a string s, check if it can be constructed by taking a substring of it
# and appending multiple copies of the substring together.
#
# Example 1:
#
# Input: s = "abab"
# Output: true
# Explanation: It is the substring "ab" twice.
#
# Example 2:
#
# Input: s = "aba"
# Output: false
#
# Example 3:
#
# Input: s = "abcabcabcabc"
# Output: true
# Explanation: It is the substring "abc" four times or the substring "abcabc"
# twice.
#
# Constraints:
#
# 1 <= s.length <= 10^4
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def repeatedSubstringPattern(self, s: str) -> bool:
        """
        Interview explanation:
        Classic trick: s is made of repeated substring iff s is found inside
        (s+s)[1:-1] — removing first and last char of the doubled string.

        Algorithm:
        - Return s in (s + s)[1:-1].

        Complexity: O(n) average time (string find), O(n) space.
        """
        return s in (s + s)[1:-1]

    def repeatedSubstringPattern_kmp(self, s: str) -> bool:
        """
        Interview explanation:
        Alternate classic: KMP LPS. If n % (n - lps[-1]) == 0 and lps[-1] > 0,
        the string is a repetition of the prefix of length n - lps[-1].

        Algorithm:
        - Build LPS for s; period = n - lps[n-1]; return lps[-1] > 0 and n % period == 0.

        Complexity: O(n) time and space.
        """
        n = len(s)
        lps = [0] * n
        length = 0
        i = 1
        while i < n:
            if s[i] == s[length]:
                length += 1
                lps[i] = length
                i += 1
            elif length:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
        return lps[-1] > 0 and n % (n - lps[-1]) == 0
# @lc code=end
