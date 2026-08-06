#
# @lc app=leetcode id=3304 lang=python3
#
# [3304] Find the K-th Character in String Game I
#
# https://leetcode.com/problems/find-the-k-th-character-in-string-game-i/description/
#
# algorithms
# Easy (81.56%)
# Likes:    658
# Dislikes: 139
# Total Accepted:    217.8K
# Total Submissions: 267K
# Testcase Example:  "5"
#
#
# Alice and Bob are playing a game. Initially, Alice has a string word =
# "a".
#
# You are given a positive integer k.
#
# Now Bob will ask Alice to perform the following operation forever:
#
# Generate a new string by changing each character in word to its next
# character in the English alphabet, and append it to the original word.
#
# For example, performing the operation on "c" generates "cd" and
# performing the operation on "zb" generates "zbac".
#
# Return the value of the k^th character in word, after enough operations
# have been done for word to have at least k characters.
#
# Example 1:
#
# Input: k = 5
#
# Output: "b"
#
# Explanation:
#
# Initially, word = "a". We need to do the operation three times:
#
# Generated string is "b", word becomes "ab".
#
# Generated string is "bc", word becomes "abbc".
#
# Generated string is "bccd", word becomes "abbcbccd".
#
# Example 2:
#
# Input: k = 10
#
# Output: "c"
#
# Constraints:
#
# 1 <= k <= 500
#

# @lc code=start
class Solution:
    def kthCharacter(self, k: int) -> str:
        """
        Interview explanation:
        Start from "a"; each op appends the alphabet-next of the whole string
        (length doubles). The k-th char equals 'a' plus how many times we took
        the incremented half on the path to index k.

        Algorithm:
        - That count is popcount(k - 1) for 1-indexed k.

        Complexity: O(log k) time, O(1) space.
        """
        return chr(ord("a") + (k - 1).bit_count())

    def kthCharacter_sim(self, k: int) -> str:
        """
        Interview explanation:
        Direct simulation is fine for k <= 500.

        Algorithm:
        - Grow the string until length >= k; each step append next-letters.

        Complexity: O(k) time, O(k) space.
        """
        word = ["a"]
        while len(word) < k:
            word.extend(
                chr((ord(c) - ord("a") + 1) % 26 + ord("a")) for c in list(word)
            )
        return word[k - 1]
# @lc code=end
