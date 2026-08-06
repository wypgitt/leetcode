#
# @lc app=leetcode id=676 lang=python3
#
# [676] Implement Magic Dictionary
#
# https://leetcode.com/problems/implement-magic-dictionary/description/
#
# algorithms
# Medium (58.05%)
# Likes:    1484
# Dislikes: 216
# Total Accepted:    110K
# Total Submissions: 189K
# Testcase Example:  "[\"MagicDictionary\", \"buildDict\", \"search\", \"search\", \"search\", \"search\"]"
#
# Design a data structure that is initialized with a list of different words.
# Provided a string, you should determine if you can change exactly one
# character in this string to match any word in the data structure.
#
# Implement the MagicDictionary class:
#
# MagicDictionary() Initializes the object.
#
# void buildDict(String[] dictionary) Sets the data structure with an array of
# distinct strings dictionary.
#
# bool search(String searchWord) Returns true if you can change exactly one
# character in searchWord to match any string in the data structure, otherwise
# returns false.
#
# Example 1:
#
# Input
# ["MagicDictionary", "buildDict", "search", "search", "search", "search"]
# [[], [["hello", "leetcode"]], ["hello"], ["hhllo"], ["hell"], ["leetcoded"]]
# Output
# [null, null, false, true, false, false]
#
# Explanation
# MagicDictionary magicDictionary = new MagicDictionary();
# magicDictionary.buildDict(["hello", "leetcode"]);
# magicDictionary.search("hello"); // return False
# magicDictionary.search("hhllo"); // We can change the second 'h' to 'e' to
# match "hello" so we return True
# magicDictionary.search("hell"); // return False
# magicDictionary.search("leetcoded"); // return False
#
# Constraints:
#
# 1 <= dictionary.length <= 100
#
# 1 <= dictionary[i].length <= 100
#
# dictionary[i] consists of only lower-case English letters.
#
# All the strings in dictionary are distinct.
#
# 1 <= searchWord.length <= 100
#
# searchWord consists of only lower-case English letters.
#
# buildDict will be called only once before search.
#
# At most 100 calls will be made to search.
#

# @lc code=start
from typing import List


class MagicDictionary:
    def __init__(self):
        """
        Interview explanation:
        Dictionary search allowing exactly one character difference. Group words
        by length; for each query, compare against same-length words and count
        mismatches.

        Algorithm:
        - Store words in a list (or length buckets).

        Complexity: O(1) init.
        """
        self.words: List[str] = []

    def buildDict(self, dictionary: List[str]) -> None:
        """
        Interview explanation:
        Store the dictionary for later exact-one-edit searches.

        Algorithm:
        - Keep a copy of the word list.

        Complexity: O(N) time/space for N words.
        """
        self.words = list(dictionary)

    def search(self, searchWord: str) -> bool:
        """
        Interview explanation:
        Return True iff some dictionary word differs in exactly one position
        (same length implied).

        Algorithm:
        - For each word of equal length, count mismatches; succeed if == 1.

        Complexity: O(N * L) time, O(1) extra space.
        """
        for w in self.words:
            if len(w) != len(searchWord):
                continue
            diff = 0
            for a, b in zip(w, searchWord):
                if a != b:
                    diff += 1
                    if diff > 1:
                        break
            if diff == 1:
                return True
        return False


# Your MagicDictionary object will be instantiated and called as such:
# obj = MagicDictionary()
# obj.buildDict(dictionary)
# param_2 = obj.search(searchWord)
# @lc code=end
