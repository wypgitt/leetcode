#
# @lc app=leetcode id=748 lang=python3
#
# [748] Shortest Completing Word
#
# https://leetcode.com/problems/shortest-completing-word/description/
#
# algorithms
# Easy (63.56%)
# Likes:    644
# Dislikes: 1133
# Total Accepted:    115K
# Total Submissions: 181K
# Testcase Example:  "\"1s3 PSt\""
#
# Given a string licensePlate and an array of strings words, find the shortest
# completing word in words.
#
# A completing word is a word that contains all the letters in licensePlate.
# Ignore numbers and spaces in licensePlate, and treat letters as case
# insensitive. If a letter appears more than once in licensePlate, then it must
# appear in the word the same number of times or more.
#
# For example, if licensePlate = "aBc 12c", then it contains letters 'a', 'b'
# (ignoring case), and 'c' twice. Possible completing words are "abccdef",
# "caaacab", and "cbca".
#
# Return the shortest completing word in words. It is guaranteed an answer
# exists. If there are multiple shortest completing words, return the first one
# that occurs in words.
#
# Example 1:
#
# Input: licensePlate = "1s3 PSt", words = ["step","steps","stripe","stepple"]
# Output: "steps"
# Explanation: licensePlate contains letters 's', 'p', 's' (ignoring case), and
# 't'.
# "step" contains 't' and 'p', but only contains 1 's'.
# "steps" contains 't', 'p', and both 's' characters.
# "stripe" is missing an 's'.
# "stepple" is missing an 's'.
# Since "steps" is the only word containing all the letters, that is the
# answer.
#
# Example 2:
#
# Input: licensePlate = "1s3 456", words = ["looks","pest","stew","show"]
# Output: "pest"
# Explanation: licensePlate only contains the letter 's'. All the words contain
# 's', but among these "pest", "stew", and "show" are shortest. The answer is
# "pest" because it is the word that appears earliest of the 3.
#
# Constraints:
#
# 1 <= licensePlate.length <= 7
#
# licensePlate contains digits, letters (uppercase or lowercase), or space ' '.
#
# 1 <= words.length <= 1000
#
# 1 <= words[i].length <= 15
#
# words[i] consists of lower case English letters.
#


# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def shortestCompletingWord(self, licensePlate: str, words: List[str]) -> str:
        """
        Interview explanation:
        Completing word must cover all letters in the plate (ignore digits/spaces,
        case-insensitive). Among completing words, pick the shortest; ties keep
        the earliest in the list.

        Algorithm:
        - need = Counter of lowercase letters in licensePlate
        - For each word: if need <= Counter(word) and shorter (or first): update

        Complexity: O(P + W * L) time; O(1) extra for letter counters (26).
        """
        need = Counter(c.lower() for c in licensePlate if c.isalpha())
        best = None
        for w in words:
            if need <= Counter(w) and (best is None or len(w) < len(best)):
                best = w
        return best
# @lc code=end

