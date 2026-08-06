#
# @lc app=leetcode id=288 lang=python3
#
# [288] Unique Word Abbreviation
#
# https://leetcode.com/problems/unique-word-abbreviation/description/
#
# algorithms
# Medium (28.00%)
# Likes:    222
# Dislikes: 1868
# Total Accepted:    83.2K
# Total Submissions: 297K
# Testcase Example:  "[\"ValidWordAbbr\",\"isUnique\",\"isUnique\",\"isUnique\",\"isUnique\",\"isUnique\"]\n[[[\"deer\",\"door\",\"cake\",\"card\"]],[\"dear\"],[\"cart\"],[\"cane\"],[\"make\"],[\"cake\"]]"
#
#
# The abbreviation of a word is a concatenation of its first letter, the
# number of characters between the first and last letter, and its last
# letter. If a word has only two characters, then it is an abbreviation of
# itself.
#
# For example:
#
# dog --> d1g because there is one letter between the first letter 'd' and
# the last letter 'g'.
#
# internationalization --> i18n because there are 18 letters between the
# first letter 'i' and the last letter 'n'.
#
# it --> it because any word with only two characters is an abbreviation
# of itself.
#
# Implement the ValidWordAbbr class:
#
# ValidWordAbbr(String[] dictionary) Initializes the object with a
# dictionary of words.
#
# boolean isUnique(string word) Returns true if either of the following
# conditions are met (otherwise returns false):
#
# There is no word in dictionary whose abbreviation is equal to word's
# abbreviation.
#
# For any word in dictionary whose abbreviation is equal to word's
# abbreviation, that word and word are the same.
#
# Example 1:
#
# Input
# ["ValidWordAbbr", "isUnique", "isUnique", "isUnique", "isUnique",
# "isUnique"]
# [[["deer", "door", "cake", "card"]], ["dear"], ["cart"], ["cane"],
# ["make"], ["cake"]]
# Output
# [null, false, true, false, true, true]
#
# Explanation
# ValidWordAbbr validWordAbbr = new ValidWordAbbr(["deer", "door", "cake",
# "card"]);
# validWordAbbr.isUnique("dear"); // return false, dictionary word "deer"
# and word "dear" have the same abbreviation "d2r" but are not the same.
# validWordAbbr.isUnique("cart"); // return true, no words in the
# dictionary have the abbreviation "c2t".
# validWordAbbr.isUnique("cane"); // return false, dictionary word "cake"
# and word "cane" have the same abbreviation  "c2e" but are not the same.
# validWordAbbr.isUnique("make"); // return true, no words in the
# dictionary have the abbreviation "m2e".
# validWordAbbr.isUnique("cake"); // return true, because "cake" is
# already in the dictionary and no other word in the dictionary has "c2e"
# abbreviation.
#
# Constraints:
#
# 1 <= dictionary.length <= 3 * 10^4
#
# 1 <= dictionary[i].length <= 20
#
# dictionary[i] consists of lowercase English letters.
#
# 1 <= word.length <= 20
#
# word consists of lowercase English letters.
#
# At most 5000 calls will be made to isUnique.
#
# @lc code=start
from typing import List


class ValidWordAbbr:
    def __init__(self, dictionary: List[str]):
        """
        Interview explanation:
        Abbreviation of a word is first + (len-2) + last (or the word itself if
        len <= 2). A word is unique if no other dictionary word shares its abbr
        (same word may appear multiple times).

        Algorithm:
        - Map abbr → the unique dictionary word, or "" if conflicting words exist.
        - isUnique(word): abbr missing, or maps to the same word.

        Complexity: O(N) preprocess, O(1) query (word length L for hashing).
        """
        self.abbr = {}
        for w in dictionary:
            a = self._abbr(w)
            if a not in self.abbr:
                self.abbr[a] = w
            elif self.abbr[a] != w:
                self.abbr[a] = ""

    def _abbr(self, word: str) -> str:
        if len(word) <= 2:
            return word
        return word[0] + str(len(word) - 2) + word[-1]

    def isUnique(self, word: str) -> bool:
        """
        Interview explanation:
        word is unique if no *other* dictionary word shares its abbreviation
        (identical dictionary copies of word are allowed).

        Algorithm:
        - a = abbr(word); unique if a missing from map or maps to the same word.

        Complexity: O(L) time for word length L, O(1) extra space.
        """
        a = self._abbr(word)
        return a not in self.abbr or self.abbr[a] == word


# Your ValidWordAbbr object will be instantiated and called as such:
# obj = ValidWordAbbr(dictionary)
# param_1 = obj.isUnique(word)
# @lc code=end

