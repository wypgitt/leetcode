#
# @lc app=leetcode id=966 lang=python3
#
# [966] Vowel Spellchecker
#
# https://leetcode.com/problems/vowel-spellchecker/description/
#
# algorithms
# Medium (61.43%)
# Likes:    857
# Dislikes: 1003
# Total Accepted:    142K
# Total Submissions: 231K
# Testcase Example:  "[\"KiTe\",\"kite\",\"hare\",\"Hare\"]"
#
# Given a wordlist, we want to implement a spellchecker that converts a query
# word into a correct word.
#
# For a given query word, the spell checker handles two categories of spelling
# mistakes:
#
# Capitalization: If the query matches a word in the wordlist
# (case-insensitive), then the query word is returned with the same case as the
# case in the wordlist.
#
# Example: wordlist = ["yellow"], query = "YellOw": correct = "yellow"
#
# Example: wordlist = ["Yellow"], query = "yellow": correct = "Yellow"
#
# Example: wordlist = ["yellow"], query = "yellow": correct = "yellow"
#
# Vowel Errors: If after replacing the vowels ('a', 'e', 'i', 'o', 'u') of the
# query word with any vowel individually, it matches a word in the wordlist
# (case-insensitive), then the query word is returned with the same case as the
# match in the wordlist.
#
# Example: wordlist = ["YellOw"], query = "yollow": correct = "YellOw"
#
# Example: wordlist = ["YellOw"], query = "yeellow": correct = "" (no match)
#
# Example: wordlist = ["YellOw"], query = "yllw": correct = "" (no match)
#
# In addition, the spell checker operates under the following precedence rules:
#
# When the query exactly matches a word in the wordlist (case-sensitive), you
# should return the same word back.
#
# When the query matches a word up to capitalization, you should return the
# first such match in the wordlist.
#
# When the query matches a word up to vowel errors, you should return the first
# such match in the wordlist.
#
# If the query has no matches in the wordlist, you should return the empty
# string.
#
# Given some queries, return a list of words answer, where answer[i] is the
# correct word for query = queries[i].
#
# Example 1:
#
# Input: wordlist = ["KiTe","kite","hare","Hare"], queries =
# ["kite","Kite","KiTe","Hare","HARE","Hear","hear","keti","keet","keto"]
# Output: ["kite","KiTe","KiTe","Hare","hare","","","KiTe","","KiTe"]
#
# Example 2:
#
# Input: wordlist = ["yellow"], queries = ["YellOw"]
# Output: ["yellow"]
#
# Constraints:
#
# 1 <= wordlist.length, queries.length <= 5000
#
# 1 <= wordlist[i].length, queries[i].length <= 7
#
# wordlist[i] and queries[i] consist only of only English letters.
#

# @lc code=start
from typing import Dict, List, Set


class Solution:
    def spellchecker(self, wordlist: List[str], queries: List[str]) -> List[str]:
        """
        Interview explanation:
        Match query by priority: (1) exact, (2) case-insensitive first in list,
        (3) vowel-error (aeiou treated equal) first in list, else "".

        Algorithm:
        - exact = set(wordlist)
        - lower_map: lowercase → first word
        - vowel_map: lower with vowels→'#' → first word
        - For each query: check exact, then lower, then vowel pattern

        Complexity: O(W + Q) time for total chars, O(W) space.
        """
        def devowel(w: str) -> str:
            return ''.join('*' if c in 'aeiou' else c for c in w)

        exact: Set[str] = set(wordlist)
        lower_map: Dict[str, str] = {}
        vowel_map: Dict[str, str] = {}
        for w in wordlist:
            low = w.lower()
            lower_map.setdefault(low, w)
            vowel_map.setdefault(devowel(low), w)

        ans = []
        for q in queries:
            if q in exact:
                ans.append(q)
                continue
            low = q.lower()
            if low in lower_map:
                ans.append(lower_map[low])
            elif devowel(low) in vowel_map:
                ans.append(vowel_map[devowel(low)])
            else:
                ans.append('')
        return ans
# @lc code=end

