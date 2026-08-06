#
# @lc app=leetcode id=3403 lang=python3
#
# [3403] Find the Lexicographically Largest String From the Box I
#
# https://leetcode.com/problems/find-the-lexicographically-largest-string-from-the-box-i/description/
#
# algorithms
# Medium (40.93%)
# Likes:    493
# Dislikes: 131
# Total Accepted:    112.3K
# Total Submissions: 274.4K
# Testcase Example:  "\"dbca\"\n2"
#
#
# You are given a string word, and an integer numFriends.
#
# Alice is organizing a game for her numFriends friends. There are
# multiple rounds in the game, where in each round:
#
# word is split into numFriends non-empty strings, such that no previous
# round has had the exact same split.
#
# All the split words are put into a box.
#
# Find the lexicographically largest string from the box after all the
# rounds are finished.
#
# Example 1:
#
# Input: word = "dbca", numFriends = 2
#
# Output: "dbc"
#
# Explanation:
#
# All possible splits are:
#
# "d" and "bca".
#
# "db" and "ca".
#
# "dbc" and "a".
#
# Example 2:
#
# Input: word = "gggg", numFriends = 4
#
# Output: "g"
#
# Explanation:
#
# The only possible split is: "g", "g", "g", and "g".
#
# Constraints:
#
# 1 <= word.length <= 5 * 10^3
#
# word consists only of lowercase English letters.
#
# 1 <= numFriends <= word.length
#

# @lc code=start
class Solution:
    def answerString(self, word: str, numFriends: int) -> str:
        """
        Interview explanation:
        Every split piece is a contiguous substring. With numFriends parts,
        the longest possible piece has length n-numFriends+1. For a fixed
        start, longer is always lexicographically larger as a prefix rule,
        so the answer is the max among all substrings of that max length
        (truncated at end of word). If numFriends==1, only the whole word.

        Algorithm:
        - Special-case numFriends==1.
        - Enumerate start i; take word[i:i+maxLen]; keep the max string.

        Complexity: O(n^2) time, O(n) space.
        """
        if numFriends == 1:
            return word
        n = len(word)
        max_len = n - numFriends + 1
        ans = ""
        for i in range(n):
            ans = max(ans, word[i : i + max_len])
        return ans

    def answerString_lastSubstring(self, word: str, numFriends: int) -> str:
        """
        Interview explanation:
        Optimal O(n) view: the lexicographically largest substring of length
        at most maxLen is a prefix of the last substring in lex order.

        Algorithm:
        - If numFriends==1 return word.
        - Find last substring start via two-pointer scan; truncate to maxLen.

        Complexity: O(n) time, O(n) space.
        """
        if numFriends == 1:
            return word
        s = self._lastSubstring(word)
        return s[: min(len(s), len(word) - numFriends + 1)]

    def _lastSubstring(self, s: str) -> str:
        i, j, k = 0, 1, 0
        n = len(s)
        while j + k < n:
            if s[i + k] == s[j + k]:
                k += 1
            elif s[i + k] > s[j + k]:
                j = j + k + 1
                k = 0
            else:
                i = max(i + k + 1, j)
                j = i + 1
                k = 0
        return s[i:]
# @lc code=end
