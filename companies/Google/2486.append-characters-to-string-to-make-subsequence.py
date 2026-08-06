#
# @lc app=leetcode id=2486 lang=python3
#
# [2486] Append Characters to String to Make Subsequence
#
# https://leetcode.com/problems/append-characters-to-string-to-make-subsequence/description/
#
# algorithms
# Medium (73.11%)
# Likes:    1211
# Dislikes: 91
# Total Accepted:    231K
# Total Submissions: 315.9K
# Testcase Example:  "\"coaching\"\n\"coding\""
#
# You are given two strings s and t consisting of only lowercase English
# letters.
#
# Return the minimum number of characters that need to be appended to the end of
# s so that t becomes a subsequence of s.
#
# A subsequence is a string that can be derived from another string by deleting
# some or no characters without changing the order of the remaining characters.
#
#
#
# Example 1:
#
# Input: s = "coaching", t = "coding"
# Output: 4
# Explanation: Append the characters "ding" to the end of s so that s =
# "coachingding".
# Now, t is a subsequence of s ("coachingding").
# It can be shown that appending any 3 characters to the end of s will never
# make t a subsequence.
#
# Example 2:
#
# Input: s = "abcde", t = "a"
# Output: 0
# Explanation: t is already a subsequence of s ("abcde").
#
# Example 3:
#
# Input: s = "z", t = "abcde"
# Output: 5
# Explanation: Append the characters "abcde" to the end of s so that s =
# "zabcde".
# Now, t is a subsequence of s ("zabcde").
# It can be shown that appending any 4 characters to the end of s will never
# make t a subsequence.
#
#
#
# Constraints:
#
#
# 1 <= s.length, t.length <= 10^5
#
#
# s and t consist only of lowercase English letters.
#

# @lc code=start
class Solution:
    def appendCharacters(self, s: str, t: str) -> int:
        """
        Interview explanation:
        Min chars to append to s so t becomes a subsequence.

        Algorithm:
        - Two pointers: match t greedily in s; answer is unmatched suffix length.

        Complexity: O(|s|+|t|) time, O(1) space.
        """
        j = 0
        for ch in s:
            if j < len(t) and ch == t[j]:
                j += 1
        return len(t) - j

    def appendCharacters_two_pointers(self, s: str, t: str) -> int:
        """
        Interview explanation:
        Same two-pointer matching, explicit indices.

        Algorithm:
        - i over s, j over t; return len(t)-j.

        Complexity: O(n+m) time, O(1) space.
        """
        i = j = 0
        while i < len(s) and j < len(t):
            if s[i] == t[j]:
                j += 1
            i += 1
        return len(t) - j
# @lc code=end

