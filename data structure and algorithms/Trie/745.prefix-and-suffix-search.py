#
# @lc app=leetcode id=745 lang=python3
#
# [745] Prefix and Suffix Search
#
# https://leetcode.com/problems/prefix-and-suffix-search/description/
#
# algorithms
# Hard (41.07%)
# Likes:    2362
# Dislikes: 500
# Total Accepted:    113K
# Total Submissions: 275K
# Testcase Example:  "[\"WordFilter\",\"f\"]"
#
# Design a special dictionary that searches the words in it by a prefix and a
# suffix.
#
# Implement the WordFilter class:
#
# WordFilter(string[] words) Initializes the object with the words in the
# dictionary.
#
# f(string pref, string suff) Returns the index of the word in the dictionary,
# which has the prefix pref and the suffix suff. If there is more than one
# valid index, return the largest of them. If there is no such word in the
# dictionary, return -1.
#
# Example 1:
#
# Input
# ["WordFilter", "f"]
# [[["apple"]], ["a", "e"]]
# Output
# [null, 0]
# Explanation
# WordFilter wordFilter = new WordFilter(["apple"]);
# wordFilter.f("a", "e"); // return 0, because the word at index 0 has prefix =
# "a" and suffix = "e".
#
# Constraints:
#
# 1 <= words.length <= 10^4
#
# 1 <= words[i].length <= 7
#
# 1 <= pref.length, suff.length <= 7
#
# words[i], pref and suff consist of lowercase English letters only.
#
# At most 10^4 calls will be made to the function f.
#


# @lc code=start
from typing import Dict, List


class WordFilter:
    """
    Interview explanation:
    Index every word by all suffix#prefix keys (or wrap as '{suffix}#{prefix}')
    mapping to the largest index. Query f(pref, suff) looks up suff#pref.
    """

    def __init__(self, words: List[str]):
        """
        Interview explanation:
        Precompute for each word all combinations of suffix and prefix joined
        by '#', storing the word's index (later words overwrite earlier).

        Algorithm:
        - For each index, word: for all i,j suffixes/prefixes, map key -> index

        Complexity: O(sum L^2) time and space for word lengths L.
        """
        self.lookup: Dict[str, int] = {}
        for idx, word in enumerate(words):
            L = len(word)
            for i in range(L + 1):
                for j in range(L + 1):
                    self.lookup[word[i:] + "#" + word[:j]] = idx

    def f(self, pref: str, suff: str) -> int:
        """
        Interview explanation:
        Return the largest index of a word with given prefix and suffix, or -1.

        Algorithm:
        - Return lookup.get(suff + '#' + pref, -1)

        Complexity: O(1) average time after hashing the key of length |pref|+|suff|.
        """
        return self.lookup.get(suff + "#" + pref, -1)


# Your WordFilter object will be instantiated and called as such:
# obj = WordFilter(words)
# param_1 = obj.f(pref,suff)
# @lc code=end

