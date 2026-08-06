#
# @lc app=leetcode id=1859 lang=python3
#
# [1859] Sorting the Sentence
#
# https://leetcode.com/problems/sorting-the-sentence/description/
#
# algorithms
# Easy (84.17%)
# Likes:    2410
# Dislikes: 84
# Total Accepted:    245K
# Total Submissions: 291K
# Testcase Example:  "\"is2 sentence4 This1 a3\""
#
# A sentence is a list of words that are separated by a single space with no
# leading or trailing spaces. Each word consists of lowercase and uppercase
# English letters.
#
# A sentence can be shuffled by appending the 1-indexed word position to each
# word then rearranging the words in the sentence.
#
# For example, the sentence "This is a sentence" can be shuffled as "sentence4
# a3 is2 This1" or "is2 sentence4 This1 a3".
#
# Given a shuffled sentence s containing no more than 9 words, reconstruct and
# return the original sentence.
#
# Example 1:
#
# Input: s = "is2 sentence4 This1 a3"
# Output: "This is a sentence"
# Explanation: Sort the words in s to their original positions "This1 is2 a3
# sentence4", then remove the numbers.
#
# Example 2:
#
# Input: s = "Myself2 Me1 I4 and3"
# Output: "Me Myself and I"
# Explanation: Sort the words in s to their original positions "Me1 Myself2
# and3 I4", then remove the numbers.
#
# Constraints:
#
# 2 <= s.length <= 200
#
# s consists of lowercase and uppercase English letters, spaces, and digits
# from 1 to 9.
#
# The number of words in s is between 1 and 9.
#
# The words in s are separated by a single space.
#
# s contains no leading or trailing spaces.
#

# @lc code=start
class Solution:
    def sortSentence(self, s: str) -> str:
        """
        Interview explanation:
        Words shuffled with 1-indexed position appended. Sort by that digit and
        strip the trailing index.

        Algorithm:
        - Split; sort by int(word[-1]); join word[:-1].

        Complexity: O(n log n) on word count (≤9) ≈ O(L).
        """
        words = s.split()
        words.sort(key=lambda w: int(w[-1]))
        return " ".join(w[:-1] for w in words)

    def sortSentence_array(self, s: str) -> str:
        """
        Interview explanation:
        Alternate: place each word into a fixed slot by its index (1..n).

        Algorithm:
        - arr = ['']*n; for w: arr[int(w[-1])-1]=w[:-1]; join.

        Complexity: O(L) time.
        """
        words = s.split()
        arr = [""] * len(words)
        for w in words:
            arr[int(w[-1]) - 1] = w[:-1]
        return " ".join(arr)
# @lc code=end
