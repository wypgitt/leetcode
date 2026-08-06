#
# @lc app=leetcode id=2868 lang=python3
#
# [2868] The Wording Game
#
# https://leetcode.com/problems/the-wording-game/description/
#
# algorithms
# Hard (56.13%)
# Likes:    10
# Dislikes: 6
# Total Accepted:    820
# Total Submissions: 1.5K
# Testcase Example:  "[\"avokado\",\"dabar\"]\n[\"brazil\"]"
#
#
# Alice and Bob each have a lexicographically sorted array of strings
# named a and b respectively.
#
# They are playing a wording game with the following rules:
#
# On each turn, the current player should play a word from their list such
# that the new word is closely greater than the last played word; then
# it's the other player's turn.
#
# If a player can't play a word on their turn, they lose.
#
# Alice starts the game by playing her lexicographically smallest word.
#
# Given a and b, return true if Alice can win knowing that both players
# play their best, and false otherwise.
#
# A word w is closely greater than a word z if the following conditions
# are met:
#
# w is lexicographically greater than z.
#
# If w_1 is the first letter of w and z_1 is the first letter of z, w_1
# should either be equal to z_1 or be the letter after z_1 in the
# alphabet.
#
# For example, the word "care" is closely greater than "book" and "car",
# but is not closely greater than "ant" or "cook".
#
# A string s is lexicographically greater than a string t if in the first
# position where s and t differ, string s has a letter that appears later
# in the alphabet than the corresponding letter in t. If the first
# min(s.length, t.length) characters do not differ, then the longer string
# is the lexicographically greater one.
#
# Example 1:
#
# Input: a = ["avokado","dabar"], b = ["brazil"]
# Output: false
# Explanation: Alice must start the game by playing the word "avokado"
# since it's her smallest word, then Bob plays his only word, "brazil",
# which he can play because its first letter, 'b', is the letter after
# Alice's word's first letter, 'a'.
# Alice can't play a word since the first letter of the only word left is
# not equal to 'b' or the letter after 'b', 'c'.
# So, Alice loses, and the game ends.
#
# Example 2:
#
# Input: a = ["ananas","atlas","banana"], b =
# ["albatros","cikla","nogomet"]
# Output: true
# Explanation: Alice must start the game by playing the word "ananas".
# Bob can't play a word since the only word he has that starts with the
# letter 'a' or 'b' is "albatros", which is smaller than Alice's word.
# So Alice wins, and the game ends.
#
# Example 3:
#
# Input: a = ["hrvatska","zastava"], b = ["bijeli","galeb"]
# Output: true
# Explanation: Alice must start the game by playing the word "hrvatska".
# Bob can't play a word since the first letter of both of his words are
# smaller than the first letter of Alice's word, 'h'.
# So Alice wins, and the game ends.
#
# Constraints:
#
# 1 <= a.length, b.length <= 10^5
#
# a[i] and b[i] consist only of lowercase English letters.
#
# a and b are lexicographically sorted.
#
# All the words in a and b combined are distinct.
#
# The sum of the lengths of all the words in a and b combined does not
# exceed 10^6.
#
# @lc code=start
from typing import List


class Solution:
    def canAliceWin(self, a: List[str], b: List[str]) -> bool:
        """
        Interview explanation:
        Premium: Alice and Bob have sorted word lists. Alice starts with her
        smallest word. A play must be closely greater than the last word:
        lexicographically greater, and first letter equal or next in alphabet.
        Return whether Alice wins with optimal play.

        Algorithm:
        - Two pointers over sorted lists; each player always plays the earliest
          legal remaining word (optimal because later words are larger).
        - Simulate until a player cannot move.

        Alternate: keep only the max word per starting letter, then walk letters.

        Complexity: O(|a| + |b|) time, O(1) extra space.
        """
        i, j = 1, 0
        bob_turn = True
        w = a[0]
        while True:
            if bob_turn:
                if j == len(b):
                    return True
                bj = b[j]
                if (bj[0] == w[0] and w < bj) or (ord(bj[0]) - ord(w[0]) == 1):
                    w = bj
                    bob_turn = False
                j += 1
            else:
                if i == len(a):
                    return False
                ai = a[i]
                if (ai[0] == w[0] and w < ai) or (ord(ai[0]) - ord(w[0]) == 1):
                    w = ai
                    bob_turn = True
                i += 1
# @lc code=end
