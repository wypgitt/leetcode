#
# @lc app=leetcode id=1813 lang=python3
#
# [1813] Sentence Similarity III
#
# https://leetcode.com/problems/sentence-similarity-iii/description/
#
# algorithms
# Medium (48.39%)
# Likes:    1076
# Dislikes: 164
# Total Accepted:    134K
# Total Submissions: 278K
# Testcase Example:  "\"My name is Haley\""
#
# You are given two strings sentence1 and sentence2, each representing a
# sentence composed of words. A sentence is a list of words that are separated
# by a single space with no leading or trailing spaces. Each word consists of
# only uppercase and lowercase English characters.
#
# Two sentences s1 and s2 are considered similar if it is possible to insert an
# arbitrary sentence (possibly empty) inside one of these sentences such that
# the two sentences become equal. Note that the inserted sentence must be
# separated from existing words by spaces.
#
# For example,
#
# s1 = "Hello Jane" and s2 = "Hello my name is Jane" can be made equal by
# inserting "my name is" between "Hello" and "Jane" in s1.
#
# s1 = "Frog cool" and s2 = "Frogs are cool" are not similar, since although
# there is a sentence "s are" inserted into s1, it is not separated from "Frog"
# by a space.
#
# Given two sentences sentence1 and sentence2, return true if sentence1 and
# sentence2 are similar. Otherwise, return false.
#
# Example 1:
#
# Input: sentence1 = "My name is Haley", sentence2 = "My Haley"
#
# Output: true
#
# Explanation:
#
# sentence2 can be turned to sentence1 by inserting "name is" between "My" and
# "Haley".
#
# Example 2:
#
# Input: sentence1 = "of", sentence2 = "A lot of words"
#
# Output: false
#
# Explanation:
#
# No single sentence can be inserted inside one of the sentences to make it
# equal to the other.
#
# Example 3:
#
# Input: sentence1 = "Eating right now", sentence2 = "Eating"
#
# Output: true
#
# Explanation:
#
# sentence2 can be turned to sentence1 by inserting "right now" at the end of
# the sentence.
#
# Constraints:
#
# 1 <= sentence1.length, sentence2.length <= 100
#
# sentence1 and sentence2 consist of lowercase and uppercase English letters
# and spaces.
#
# The words in sentence1 and sentence2 are separated by a single space.
#

# @lc code=start
class Solution:
    def areSentencesSimilar(self, sentence1: str, sentence2: str) -> bool:
        """
        Interview explanation:
        Sentences similar if one can be obtained by inserting one sentence
        (possibly empty) into the other as a contiguous word sequence —
        equivalently: after removing a common prefix and suffix of words,
        one side is empty.

        Algorithm (two pointers on words):
        - Split to words; let a be longer; strip matching prefix/suffix with b;
          remaining of shorter must be empty.

        Complexity: O(n) time, O(n) space.
        """
        w1, w2 = sentence1.split(), sentence2.split()
        if len(w1) < len(w2):
            w1, w2 = w2, w1
        i, j = 0, 0
        n1, n2 = len(w1), len(w2)
        while i < n2 and w1[i] == w2[i]:
            i += 1
        while j < n2 - i and w1[n1 - 1 - j] == w2[n2 - 1 - j]:
            j += 1
        return i + j >= n2
# @lc code=end
