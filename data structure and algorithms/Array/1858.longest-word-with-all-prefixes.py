#
# @lc app=leetcode id=1858 lang=python3
#
# [1858] Longest Word With All Prefixes
#
# https://leetcode.com/problems/longest-word-with-all-prefixes/description/
#
# algorithms
# Medium (73.34%)
# Likes:    207
# Dislikes: 7
# Total Accepted:    16.3K
# Total Submissions: 22.2K
# Testcase Example:  "[\"k\",\"ki\",\"kir\",\"kira\",\"kiran\"]"
#
#
# Given an array of strings words, find the longest string in words such
# that every prefix of it is also in words.
#
# For example, let words = ["a", "app", "ap"]. The string "app" has
# prefixes "ap" and "a", all of which are in words.
#
# Return the string described above. If there is more than one string with
# the same length, return the lexicographically smallest one, and if no
# string exists, return "".
#
# Example 1:
#
# Input: words = ["k","ki","kir","kira", "kiran"]
# Output: "kiran"
# Explanation: "kiran" has prefixes "kira", "kir", "ki", and "k", and all
# of them appear in words.
#
# Example 2:
#
# Input: words = ["a", "banana", "app", "appl", "ap", "apply", "apple"]
# Output: "apple"
# Explanation: Both "apple" and "apply" have all their prefixes in words.
# However, "apple" is lexicographically smaller, so we return that.
#
# Example 3:
#
# Input: words = ["abc", "bc", "ab", "qwe"]
# Output: ""
#
# Constraints:
#
# 1 <= words.length <= 10^5
#
# 1 <= words[i].length <= 10^5
#
# 1 <= sum(words[i].length) <= 10^5
#
# words[i] consists only of lowercase English letters.
#
# @lc code=start
from typing import List


class Solution:
    def longestWord(self, words: List[str]) -> str:
        """
        Interview explanation:
        Premium: longest word such that every prefix is also in words; ties →
        lexicographically smallest. Sort by length then lex; grow a valid set.

        Algorithm (sort + set):
        - Sort words by (len, word). valid={' '}. For w: if w[:-1] in valid: add;
          track best.

        Complexity: O(n log n + total chars) time.
        """
        words = sorted(words, key=lambda w: (len(w), w))
        valid = {""}
        best = ""
        for w in words:
            if w[:-1] in valid:
                valid.add(w)
                if len(w) > len(best):
                    best = w
        return best

    def longestWord_trie(self, words: List[str]) -> str:
        """
        Interview explanation:
        Classic alternate: insert all into a Trie; DFS only along end-marked
        nodes (every prefix exists); track longest / lex-smallest.

        Algorithm (Trie DFS):
        - Insert words; DFS from root collecting path when node.is_end.
        - Prefer longer, then smaller lex.

        Complexity: O(total chars) time/space.
        """
        trie = {}
        for w in words:
            node = trie
            for ch in w:
                node = node.setdefault(ch, {})
            node["#"] = True

        best = ""

        def dfs(node, path: str):
            nonlocal best
            if path:
                if len(path) > len(best) or (len(path) == len(best) and path < best):
                    best = path
            for ch in sorted(k for k in node if k != "#"):
                child = node[ch]
                if "#" in child:
                    dfs(child, path + ch)

        dfs(trie, "")
        return best
# @lc code=end
