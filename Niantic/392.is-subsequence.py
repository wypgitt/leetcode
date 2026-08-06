#
# @lc app=leetcode id=392 lang=python3
#
# [392] Is Subsequence
#
# https://leetcode.com/problems/is-subsequence/description/
#
# algorithms
# Easy (49.3%)
# Likes:    10935
# Dislikes: 623
# Total Accepted:    2.6M
# Total Submissions: 5.3M
# Testcase Example:  "\"abc\""
#
# Given two strings s and t, return true if s is a subsequence of t, or false
# otherwise.
#
# A subsequence of a string is a new string that is formed from the original
# string by deleting some (can be none) of the characters without disturbing
# the relative positions of the remaining characters. (i.e., "ace" is a
# subsequence of "abcde" while "aec" is not).
#
# Example 1:
#
# Input: s = "abc", t = "ahbgdc"
# Output: true
#
# Example 2:
#
# Input: s = "axc", t = "ahbgdc"
# Output: false
#
# Constraints:
#
# 0 <= s.length <= 100
#
# 0 <= t.length <= 10^4
#
# s and t consist only of lowercase English letters.
#
# Follow up: Suppose there are lots of incoming s, say s_1, s_2, ..., s_k where
# k >= 10^9, and you want to check one by one to see if t has its subsequence.
# In this scenario, how would you change your code?
#

# @lc code=start
import bisect
from collections import defaultdict


class Solution:
    def isSubsequence(self, s: str, t: str) -> bool:
        """
        Interview explanation:
        Two pointers: advance in t; when chars match, advance in s. s is a
        subsequence iff we consume all of s.

        Algorithm:
        - i = 0; for ch in t: if i < len(s) and s[i]==ch: i += 1
        - return i == len(s)

        Complexity: O(|t|) time, O(1) space.
        """
        i = 0
        for ch in t:
            if i < len(s) and s[i] == ch:
                i += 1
        return i == len(s)

    def isSubsequenceFollowUp(self, s: str, t: str) -> bool:
        """
        Interview explanation:
        Follow-up (many s against fixed t): preprocess t's char→sorted indices,
        then for each s greedily binary-search the next index after prev.

        Algorithm:
        - Build map[c] = list of positions in t.
        - prev = -1; for ch in s: bisect_right in map[ch] for > prev; fail if none.

        Complexity: preprocess O(|t|), each query O(|s| log |t|).
        """
        positions = defaultdict(list)
        for i, ch in enumerate(t):
            positions[ch].append(i)
        prev = -1
        for ch in s:
            idxs = positions[ch]
            j = bisect.bisect_right(idxs, prev)
            if j == len(idxs):
                return False
            prev = idxs[j]
        return True
# @lc code=end
