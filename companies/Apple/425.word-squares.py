#
# @lc app=leetcode id=425 lang=python3
#
# [425] Word Squares
#
# https://leetcode.com/problems/word-squares/description/
#
# algorithms
# Hard (54.74%)
# Likes:    1125
# Dislikes: 75
# Total Accepted:    84K
# Total Submissions: 153.5K
# Testcase Example:  "[\"area\",\"lead\",\"wall\",\"lady\",\"ball\"]"
#
#
# Given an array of unique strings words, return all the word squares you
# can build from words. The same word from words can be used multiple
# times. You can return the answer in any order.
#
# A sequence of strings forms a valid word square if the k^th row and
# column read the same string, where 0 <= k < max(numRows, numColumns).
#
# For example, the word sequence ["ball","area","lead","lady"] forms a
# word square because each word reads the same both horizontally and
# vertically.
#
# Example 1:
#
# Input: words = ["area","lead","wall","lady","ball"]
# Output: [["ball","area","lead","lady"],["wall","area","lead","lady"]]
# Explanation:
# The output consists of two word squares. The order of output does not
# matter (just the order of words in each word square matters).
#
# Example 2:
#
# Input: words = ["abat","baba","atan","atal"]
# Output: [["baba","abat","baba","atal"],["baba","abat","baba","atan"]]
# Explanation:
# The output consists of two word squares. The order of output does not
# matter (just the order of words in each word square matters).
#
# Constraints:
#
# 1 <= words.length <= 1000
#
# 1 <= words[i].length <= 4
#
# All words[i] have the same length.
#
# words[i] consists of only lowercase English letters.
#
# All words[i] are unique.
#
# @lc code=start

from collections import defaultdict
from typing import Dict, List


class Solution:
    def wordSquares(self, words: List[str]) -> List[List[str]]:
        """
        Interview explanation:
        Backtracking with a prefix trie/map: build a square row by row; the next
        row must start with the prefix formed by column i of already chosen words.

        Algorithm:
        - Build prefix -> list of words map.
        - Backtrack: if len(path)==L done; else prefix = ''.join(w[len(path)] for w in path);
          try each word with that prefix.

        Complexity: O(N * L * 26^L) worst-case style; practical with pruning. O(N*L) space for prefixes.
        """
        if not words:
            return []
        L = len(words[0])
        prefixes: Dict[str, List[str]] = defaultdict(list)
        for w in words:
            for i in range(L + 1):
                prefixes[w[:i]].append(w)

        ans: List[List[str]] = []

        def bt(path: List[str]) -> None:
            if len(path) == L:
                ans.append(path[:])
                return
            pref = "".join(w[len(path)] for w in path)
            for w in prefixes[pref]:
                path.append(w)
                bt(path)
                path.pop()

        for w in words:
            bt([w])
        return ans
# @lc code=end
