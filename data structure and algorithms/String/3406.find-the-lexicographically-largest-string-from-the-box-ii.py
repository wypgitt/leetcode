#
# @lc app=leetcode id=3406 lang=python3
#
# [3406] Find the Lexicographically Largest String From the Box II
#
# https://leetcode.com/problems/find-the-lexicographically-largest-string-from-the-box-ii/description/
#
# algorithms
# Hard (49.97%)
# Likes:    8
# Dislikes: 1
# Total Accepted:    749
# Total Submissions: 1.5K
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
# A string a is lexicographically smaller than a string b if in the first
# position where a and b differ, string a has a letter that appears
# earlier in the alphabet than the corresponding letter in b.
#
# If the first min(a.length, b.length) characters do not differ, then the
# shorter string is the lexicographically smaller one.
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
# 1 <= word.length <= 2 * 10^5
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
        Same as Box I, but n <= 2e5 so we need O(n). The answer is a prefix
        (length <= n-numFriends+1) of the lexicographically last substring.

        Algorithm:
        - If numFriends==1 return word.
        - Two-pointer last-substring scan (LeetCode 1163); truncate to maxLen.

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
