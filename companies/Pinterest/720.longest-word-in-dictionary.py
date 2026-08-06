#
# @lc app=leetcode id=720 lang=python3
#
# [720] Longest Word in Dictionary
#
# https://leetcode.com/problems/longest-word-in-dictionary/description/
#
# algorithms
# Medium (55.26%)
# Likes:    2105
# Dislikes: 1511
# Total Accepted:    200K
# Total Submissions: 362K
# Testcase Example:  "[\"w\",\"wo\",\"wor\",\"worl\",\"world\"]"
#
# Given an array of strings words representing an English Dictionary, return
# the longest word in words that can be built one character at a time by other
# words in words.
#
# If there is more than one possible answer, return the longest word with the
# smallest lexicographical order. If there is no answer, return the empty
# string.
#
# Note that the word should be built from left to right with each additional
# character being added to the end of a previous word.
#
# Example 1:
#
# Input: words = ["w","wo","wor","worl","world"]
# Output: "world"
# Explanation: The word "world" can be built one character at a time by "w",
# "wo", "wor", and "worl".
#
# Example 2:
#
# Input: words = ["a","banana","app","appl","ap","apply","apple"]
# Output: "apple"
# Explanation: Both "apply" and "apple" can be built from other words in the
# dictionary. However, "apple" is lexicographically smaller than "apply".
#
# Constraints:
#
# 1 <= words.length <= 1000
#
# 1 <= words[i].length <= 30
#
# words[i] consists of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def longestWord(self, words: List[str]) -> str:
        """
        Interview explanation:
        Longest word that can be built one character at a time from other words
        in the dictionary (every prefix present). Tie-break: smallest
        lexicographical. Sort + set of valid words, or Trie of words with DFS.

        Algorithm (sort + set):
        - Sort by length then lex. Build set of good words starting with "".
        - A word is good if word[:-1] is good; track best.

        Complexity: O(N log N + total chars) time, O(total chars) space.
        """
        words.sort()
        good = {""}
        best = ""
        for w in words:
            if w[:-1] in good:
                good.add(w)
                if len(w) > len(best):
                    best = w
        return best

    def longestWordTrie(self, words: List[str]) -> str:
        """
        Interview explanation:
        Trie approach: insert all words; DFS only along end-of-word nodes to
        ensure every prefix is itself a word; track longest / lex-smallest.

        Algorithm:
        - Build trie with is_end flags. DFS from root children that are words.

        Complexity: O(total chars) time/space.
        """
        trie = {}
        for w in words:
            node = trie
            for c in w:
                node = node.setdefault(c, {})
            node["#"] = True

        best = ""

        def dfs(node: dict, path: str) -> None:
            nonlocal best
            if path:
                if len(path) > len(best) or (len(path) == len(best) and path < best):
                    best = path
            for c, child in node.items():
                if c == "#":
                    continue
                if "#" in child:
                    dfs(child, path + c)

        dfs(trie, "")
        return best
# @lc code=end
