#
# @lc app=leetcode id=804 lang=python3
#
# [804] Unique Morse Code Words
#
# https://leetcode.com/problems/unique-morse-code-words/description/
#
# algorithms
# Easy (83.69%)
# Likes:    2630
# Dislikes: 1555
# Total Accepted:    416K
# Total Submissions: 497K
# Testcase Example:  "[\"gin\",\"zen\",\"gig\",\"msg\"]"
#
# International Morse Code defines a standard encoding where each letter is
# mapped to a series of dots and dashes, as follows:
#
# 'a' maps to ".-",
#
# 'b' maps to "-...",
#
# 'c' maps to "-.-.", and so on.
#
# For convenience, the full table for the 26 letters of the English alphabet is
# given below:
#
# [".-","-...","-.-.","-..",".","..-.","--.","....","..",".---","-.-",".-..","--","-.","---",".--.","--.-",".-.","...","-","..-","...-",".--","-..-","-.--","--.."]
#
# Given an array of strings words where each word can be written as a
# concatenation of the Morse code of each letter.
#
# For example, "cab" can be written as "-.-..--...", which is the concatenation
# of "-.-.", ".-", and "-...". We will call such a concatenation the
# transformation of a word.
#
# Return the number of different transformations among all words we have.
#
# Example 1:
#
# Input: words = ["gin","zen","gig","msg"]
# Output: 2
# Explanation: The transformation of each word is:
# "gin" -> "--...-."
# "zen" -> "--...-."
# "gig" -> "--...--."
# "msg" -> "--...--."
# There are 2 different transformations: "--...-." and "--...--.".
#
# Example 2:
#
# Input: words = ["a"]
# Output: 1
#
# Constraints:
#
# 1 <= words.length <= 100
#
# 1 <= words[i].length <= 12
#
# words[i] consists of lowercase English letters.
#

# @lc code=start

from typing import List


class Solution:
    def uniqueMorseRepresentations(self, words: List[str]) -> int:
        """
        Interview explanation:
        Map each letter to its International Morse code, concatenate per word,
        and count distinct encodings with a set.

        Algorithm:
        - MORSE table for a..z; for each word build code string; add to set.
        - Return set size.

        Complexity: O(total chars) time, O(n) space for distinct codes.
        """
        morse = [
            ".-", "-...", "-.-.", "-..", ".", "..-.", "--.", "....", "..", ".---",
            "-.-", ".-..", "--", "-.", "---", ".--.", "--.-", ".-.", "...", "-",
            "..-", "...-", ".--", "-..-", "-.--", "--..",
        ]
        seen = set()
        for w in words:
            seen.add("".join(morse[ord(c) - 97] for c in w))
        return len(seen)
# @lc code=end
