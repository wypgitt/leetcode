#
# @lc app=leetcode id=472 lang=python3
#
# [472] Concatenated Words
#
# https://leetcode.com/problems/concatenated-words/description/
#
# algorithms
# Hard (49.9%)
# Likes:    4089
# Dislikes: 294
# Total Accepted:    273K
# Total Submissions: 547K
# Testcase Example:  "[\"cat\",\"cats\",\"catsdogcats\",\"dog\",\"dogcatsdog\",\"hippopotamuses\",\"rat\",\"ratcatdogcat\"]"
#
# Given an array of strings words (without duplicates), return all the
# concatenated words in the given list of words.
#
# A concatenated word is defined as a string that is comprised entirely of at
# least two shorter words (not necessarily distinct) in the given array.
#
# Example 1:
#
# Input: words =
# ["cat","cats","catsdogcats","dog","dogcatsdog","hippopotamuses","rat","ratcatdogcat"]
# Output: ["catsdogcats","dogcatsdog","ratcatdogcat"]
# Explanation: "catsdogcats" can be concatenated by "cats", "dog" and "cats";
# "dogcatsdog" can be concatenated by "dog", "cats" and "dog";
# "ratcatdogcat" can be concatenated by "rat", "cat", "dog" and "cat".
#
# Example 2:
#
# Input: words = ["cat","dog","catdog"]
# Output: ["catdog"]
#
# Constraints:
#
# 1 <= words.length <= 10^4
#
# 1 <= words[i].length <= 30
#
# words[i] consists of only lowercase English letters.
#
# All the strings of words are unique.
#
# 1 <= sum(words[i].length) <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def findAllConcatenatedWordsInADict(self, words: List[str]) -> List[str]:
        """
        Interview explanation:
        A concatenated word is formed by ≥2 shorter dictionary words. Word-break
        DP (or Trie + DFS) against the set of all words: for each word, check
        if it can be segmented into other words from the set.

        Algorithm (DP):
        - Process words short→long; word_set holds only shorter words so far.
        - Word-break DP: dp[j] if some i with dp[i] and word[i:j] in set.
        - If formable, it is concatenated; then add word to the set.

        Complexity: O(N * L^2) with set lookups (N words, L max length), O(total chars) space.
        """
        word_set: set = set()
        ans = []

        def can_form(word: str) -> bool:
            m = len(word)
            if not word_set or m == 0:
                return False
            dp = [False] * (m + 1)
            dp[0] = True
            for j in range(1, m + 1):
                for i in range(j):
                    if dp[i] and word[i:j] in word_set:
                        dp[j] = True
                        break
            return dp[m]

        # short → long: only shorter words are available as parts
        for w in sorted(words, key=len):
            if can_form(w):
                ans.append(w)
            word_set.add(w)
        return ans

    def findAllConcatenatedWordsInADict_trie(self, words: List[str]) -> List[str]:
        """
        Interview explanation:
        Alternate classic: build Trie of all words; DFS/backtrack with memo
        counting how many word ends are used along a path. Concatenated iff
        can reach end with ≥2 words.

        Complexity: O(total chars * L) build/search, O(total chars) space.
        """
        class Node:
            __slots__ = ("ch", "end")

            def __init__(self):
                self.ch = {}
                self.end = False

        root = Node()
        for w in sorted(words, key=len):
            node = root
            for c in w:
                node = node.ch.setdefault(c, Node())
            node.end = True

        memo = {}

        def dfs(word: str, start: int) -> int:
            key = (id(word), start)
            if key in memo:
                return memo[key]
            node = root
            best = 0
            for i in range(start, len(word)):
                c = word[i]
                if c not in node.ch:
                    break
                node = node.ch[c]
                if node.end:
                    if i + 1 == len(word):
                        best = max(best, 1)
                    else:
                        nxt = dfs(word, i + 1)
                        if nxt:
                            best = max(best, 1 + nxt)
            memo[key] = best
            return best

        return [w for w in words if len(w) > 0 and dfs(w, 0) >= 2]
# @lc code=end
