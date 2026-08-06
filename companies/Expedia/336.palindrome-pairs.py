#
# @lc app=leetcode id=336 lang=python3
#
# [336] Palindrome Pairs
#
# https://leetcode.com/problems/palindrome-pairs/description/
#
# algorithms
# Hard (37.45%)
# Likes:    4655
# Dislikes: 481
# Total Accepted:    246K
# Total Submissions: 658K
# Testcase Example:  "[\"abcd\",\"dcba\",\"lls\",\"s\",\"sssll\"]"
#
# You are given a 0-indexed array of unique strings words.
#
# A palindrome pair is a pair of integers (i, j) such that:
#
# 0 <= i, j < words.length,
#
# i != j, and
#
# words[i] + words[j] (the concatenation of the two strings) is a palindrome.
#
# Return an array of all the palindrome pairs of words.
#
# You must write an algorithm with O(sum of words[i].length) runtime
# complexity.
#
# Example 1:
#
# Input: words = ["abcd","dcba","lls","s","sssll"]
# Output: [[0,1],[1,0],[3,2],[2,4]]
# Explanation: The palindromes are ["abcddcba","dcbaabcd","slls","llssssll"]
#
# Example 2:
#
# Input: words = ["bat","tab","cat"]
# Output: [[0,1],[1,0]]
# Explanation: The palindromes are ["battab","tabbat"]
#
# Example 3:
#
# Input: words = ["a",""]
# Output: [[0,1],[1,0]]
# Explanation: The palindromes are ["a","a"]
#
# Constraints:
#
# 1 <= words.length <= 5000
#
# 0 <= words[i].length <= 300
#
# words[i] consists of lowercase English letters.
#

# @lc code=start
from typing import Dict, List


class Solution:
    def palindromePairs(self, words: List[str]) -> List[List[int]]:
        """
        Interview explanation:
        Hash reverse: for each word, check if its reverse exists (full pair),
        and for every split, if one side is a palindrome and the reverse of the
        other side is in the map, form a pair.

        Algorithm:
        - Map word -> index.
        - For each word w at i, for every split j:
          - left=w[:j], right=w[j:].
          - If left is pal and reverse(right) in map (≠ i), append [that, i].
          - If j>0 and right is pal and reverse(left) in map, append [i, that].
        - j from 0..len covers empty-prefix/suffix (empty is palindrome).

        Complexity: O(n * L^2) time, O(n * L) space.
        """
        def is_pal(s: str, lo: int = 0, hi: int = -1) -> bool:
            if hi < 0:
                hi = len(s) - 1
            while lo < hi:
                if s[lo] != s[hi]:
                    return False
                lo += 1
                hi -= 1
            return True

        index: Dict[str, int] = {w: i for i, w in enumerate(words)}
        res: List[List[int]] = []
        for i, w in enumerate(words):
            for j in range(len(w) + 1):
                left, right = w[:j], w[j:]
                if is_pal(left):
                    rrev = right[::-1]
                    if rrev in index and index[rrev] != i:
                        res.append([index[rrev], i])
                if j < len(w) and is_pal(right):
                    lrev = left[::-1]
                    if lrev in index and index[lrev] != i:
                        res.append([i, index[lrev]])
        return res

    def palindromePairs_trie(self, words: List[str]) -> List[List[int]]:
        """
        Interview explanation:
        Alternate: trie of reversed words; while inserting/searching, detect
        palindrome suffixes/prefixes to emit pairs — same asymptotic, cleaner
        for very skewed lengths.

        Algorithm:
        - Insert reverse of each word into a trie storing word index.
        - For each word, walk trie; when remaining suffix/prefix is palindrome
          and a word ends, record the pair.

        Complexity: O(n * L^2) time, O(n * L) space.
        """
        class Node:
            __slots__ = ("ch", "idx", "pals")

            def __init__(self) -> None:
                self.ch: Dict[str, "Node"] = {}
                self.idx = -1
                self.pals: List[int] = []

        def is_pal(s: str, lo: int, hi: int) -> bool:
            while lo < hi:
                if s[lo] != s[hi]:
                    return False
                lo += 1
                hi -= 1
            return True

        root = Node()
        for i, w in enumerate(words):
            node = root
            rev = w[::-1]
            for j, c in enumerate(rev):
                if is_pal(rev, j, len(rev) - 1):
                    node.pals.append(i)
                if c not in node.ch:
                    node.ch[c] = Node()
                node = node.ch[c]
            node.idx = i
            node.pals.append(i)

        res: List[List[int]] = []
        for i, w in enumerate(words):
            node = root
            for j, c in enumerate(w):
                if node.idx >= 0 and node.idx != i and is_pal(w, j, len(w) - 1):
                    res.append([i, node.idx])
                if c not in node.ch:
                    node = None
                    break
                node = node.ch[c]
            if node is None:
                continue
            for j in node.pals:
                if j != i:
                    res.append([i, j])
        return res
# @lc code=end
