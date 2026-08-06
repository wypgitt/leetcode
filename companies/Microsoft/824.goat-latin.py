#
# @lc app=leetcode id=824 lang=python3
#
# [824] Goat Latin
#
# https://leetcode.com/problems/goat-latin/description/
#
# algorithms
# Easy (70.12%)
# Likes:    1040
# Dislikes: 1305
# Total Accepted:    252K
# Total Submissions: 359K
# Testcase Example:  "\"I speak Goat Latin\""
#
# You are given a string sentence that consist of words separated by spaces.
# Each word consists of lowercase and uppercase letters only.
#
# We would like to convert the sentence to "Goat Latin" (a made-up language
# similar to Pig Latin.) The rules of Goat Latin are as follows:
#
# If a word begins with a vowel ('a', 'e', 'i', 'o', or 'u'), append "ma" to
# the end of the word.
#
# For example, the word "apple" becomes "applema".
#
# If a word begins with a consonant (i.e., not a vowel), remove the first
# letter and append it to the end, then add "ma".
#
# For example, the word "goat" becomes "oatgma".
#
# Add one letter 'a' to the end of each word per its word index in the
# sentence, starting with 1.
#
# For example, the first word gets "a" added to the end, the second word gets
# "aa" added to the end, and so on.
#
# Return the final sentence representing the conversion from sentence to Goat
# Latin.
#
# Example 1:
#
# Input: sentence = "I speak Goat Latin"
# Output: "Imaa peaksmaaa oatGmaaaa atinLmaaaaa"
#
# Example 2:
#
# Input: sentence = "The quick brown fox jumped over the lazy dog"
# Output: "heTmaa uickqmaaa rownbmaaaa oxfmaaaaa umpedjmaaaaaa overmaaaaaaa
# hetmaaaaaaaa azylmaaaaaaaaa ogdmaaaaaaaaaa"
#
# Constraints:
#
# 1 <= sentence.length <= 150
#
# sentence consists of English letters and spaces.
#
# sentence has no leading or trailing spaces.
#
# All the words in sentence are separated by a single space.
#

# @lc code=start

class Solution:
    def toGoatLatin(self, sentence: str) -> str:
        """
        Interview explanation:
        Goat Latin: if word starts with vowel keep it; else move first letter
        to end. Append "ma" then i+1 a's for the i-th word (1-indexed).

        Algorithm:
        - Split words; transform each; join with spaces.

        Complexity: O(n) time, O(n) space.
        """
        vowels = set("aeiouAEIOU")
        out = []
        for i, w in enumerate(sentence.split(), 1):
            if w[0] in vowels:
                t = w
            else:
                t = w[1:] + w[0]
            out.append(t + "ma" + "a" * i)
        return " ".join(out)
# @lc code=end
