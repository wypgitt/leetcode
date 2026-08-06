#
# @lc app=leetcode id=734 lang=python3
#
# [734] Sentence Similarity
#
# https://leetcode.com/problems/sentence-similarity/description/
#
# algorithms
# Easy (44.88%)
# Likes:    69
# Dislikes: 73
# Total Accepted:    76.7K
# Total Submissions: 171K
# Testcase Example:  "[\"great\",\"acting\",\"skills\"]\n[\"fine\",\"drama\",\"talent\"]\n[[\"great\",\"fine\"],[\"drama\",\"acting\"],[\"skills\",\"talent\"]]"
#
#
# We can represent a sentence as an array of words, for example, the
# sentence "I am happy with leetcode" can be represented as arr =
# ["I","am",happy","with","leetcode"].
#
# Given two sentences sentence1 and sentence2 each represented as a string
# array and given an array of string pairs similarPairs where
# similarPairs[i] = [x_i, y_i] indicates that the two words x_i and y_i
# are similar.
#
# Return true if sentence1 and sentence2 are similar, or false if they are
# not similar.
#
# Two sentences are similar if:
#
# They have the same length (i.e., the same number of words)
#
# sentence1[i] and sentence2[i] are similar.
#
# Notice that a word is always similar to itself, also notice that the
# similarity relation is not transitive. For example, if the words a and b
# are similar, and the words b and c are similar, a and c are not
# necessarily similar.
#
# Example 1:
#
# Input: sentence1 = ["great","acting","skills"], sentence2 =
# ["fine","drama","talent"], similarPairs =
# [["great","fine"],["drama","acting"],["skills","talent"]]
# Output: true
# Explanation: The two sentences have the same length and each word i of
# sentence1 is also similar to the corresponding word in sentence2.
#
# Example 2:
#
# Input: sentence1 = ["great"], sentence2 = ["great"], similarPairs = []
# Output: true
# Explanation: A word is similar to itself.
#
# Example 3:
#
# Input: sentence1 = ["great"], sentence2 = ["doubleplus","good"],
# similarPairs = [["great","doubleplus"]]
# Output: false
# Explanation: As they don't have the same length, we return false.
#
# Constraints:
#
# 1 <= sentence1.length, sentence2.length <= 1000
#
# 1 <= sentence1[i].length, sentence2[i].length <= 20
#
# sentence1[i] and sentence2[i] consist of English letters.
#
# 0 <= similarPairs.length <= 1000
#
# similarPairs[i].length == 2
#
# 1 <= x_i.length, y_i.length <= 20
#
# x_i and y_i consist of lower-case and upper-case English letters.
#
# All the pairs (x_i,_ y_i) are distinct.
#
# @lc code=start
from typing import List


class Solution:
    def areSentencesSimilar(
        self, sentence1: List[str], sentence2: List[str], similarPairs: List[List[str]]
    ) -> bool:
        """
        Interview explanation:
        Premium. Two sentences are similar if they have the same length and each
        aligned pair of words is equal or appears (in either order) in similarPairs.
        Similarity is not transitive here (see Sentence Similarity II).

        Algorithm:
        - If lengths differ: False
        - Put frozenset({a,b}) for each similar pair into a set
        - For each i: if words differ and frozenset not in pairs: False

        Complexity: O(n + P) time, O(P) space.
        """
        if len(sentence1) != len(sentence2):
            return False
        pairs = {frozenset(p) for p in similarPairs}
        for a, b in zip(sentence1, sentence2):
            if a != b and frozenset((a, b)) not in pairs:
                return False
        return True
# @lc code=end

