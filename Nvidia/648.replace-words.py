#
# @lc app=leetcode id=648 lang=python3
#
# [648] Replace Words
#
# https://leetcode.com/problems/replace-words/description/
#
# algorithms
# Medium (68.88%)
# Likes:    3144
# Dislikes: 220
# Total Accepted:    328K
# Total Submissions: 476K
# Testcase Example:  "[\"cat\",\"bat\",\"rat\"]"
#
# In English, we have a concept called root, which can be followed by some
# other word to form another longer word - let's call this word derivative. For
# example, when the root "help" is followed by the word "ful", we can form a
# derivative "helpful".
#
# Given a dictionary consisting of many roots and a sentence consisting of
# words separated by spaces, replace all the derivatives in the sentence with
# the root forming it. If a derivative can be replaced by more than one root,
# replace it with the root that has the shortest length.
#
# Return the sentence after the replacement.
#
# Example 1:
#
# Input: dictionary = ["cat","bat","rat"], sentence = "the cattle was rattled
# by the battery"
# Output: "the cat was rat by the bat"
#
# Example 2:
#
# Input: dictionary = ["a","b","c"], sentence = "aadsfasf absbs bbab cadsfafs"
# Output: "a a b c"
#
# Constraints:
#
# 1 <= dictionary.length <= 1000
#
# 1 <= dictionary[i].length <= 100
#
# dictionary[i] consists of only lower-case letters.
#
# 1 <= sentence.length <= 10^6
#
# sentence consists of only lower-case letters and spaces.
#
# The number of words in sentence is in the range [1, 1000]
#
# The length of each word in sentence is in the range [1, 1000]
#
# Every two consecutive words in sentence will be separated by exactly one
# space.
#
# sentence does not have leading or trailing spaces.
#

# @lc code=start

from typing import List


class Solution:
    def replaceWords(self, dictionary: List[str], sentence: str) -> str:
        """
        Interview explanation:
        Replace each word by its shortest dictionary root prefix. Trie of roots;
        for each word walk trie until end-of-word.

        Algorithm:
        - Build trie; end marker on root words.
        - For each word, walk until end or mismatch; replace with root if found.

        Complexity: O(total chars in dict + sentence) time/space.
        """
        trie = {}
        for w in dictionary:
            node = trie
            for ch in w:
                node = node.setdefault(ch, {})
            node["#"] = True

        def root_of(word: str) -> str:
            node = trie
            for i, ch in enumerate(word):
                if ch not in node:
                    return word
                node = node[ch]
                if "#" in node:
                    return word[: i + 1]
            return word

        return " ".join(root_of(w) for w in sentence.split())
# @lc code=end
