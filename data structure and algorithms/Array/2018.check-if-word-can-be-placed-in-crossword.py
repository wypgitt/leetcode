#
# @lc app=leetcode id=2018 lang=python3
#
# [2018] Check if Word Can Be Placed In Crossword
#
# https://leetcode.com/problems/check-if-word-can-be-placed-in-crossword/description/
#
# algorithms
# Medium (50.83%)
# Likes:    335
# Dislikes: 311
# Total Accepted:    29.5K
# Total Submissions: 58.1K
# Testcase Example:  "[[\"#\",\" \",\"#\"],[\" \",\" \",\"#\"],[\"#\",\"c\",\" \"]]\n\"abc\""
#
# You are given an m x n matrix board, representing the current state of a
# crossword puzzle. The crossword contains lowercase English letters (from
# solved words), ' ' to represent any empty cells, and '#' to represent any
# blocked cells.
#
# A word can be placed horizontally (left to right or right to left) or
# vertically (top to bottom or bottom to top) in the board if:
#
#
# It does not occupy a cell containing the character '#'.
#
#
# The cell each letter is placed in must either be ' ' (empty) or match the
# letter already on the board.
#
#
# There must not be any empty cells ' ' or other lowercase letters directly left
# or right of the word if the word was placed horizontally.
#
#
# There must not be any empty cells ' ' or other lowercase letters directly
# above or below the word if the word was placed vertically.
#
# Given a string word, return true if word can be placed in board, or false
# otherwise.
#
#
#
# Example 1:
#
# Input: board = [["#", " ", "#"], [" ", " ", "#"], ["#", "c", " "]], word =
# "abc"
# Output: true
# Explanation: The word "abc" can be placed as shown above (top to bottom).
#
# Example 2:
#
# Input: board = [[" ", "#", "a"], [" ", "#", "c"], [" ", "#", "a"]], word =
# "ac"
# Output: false
# Explanation: It is impossible to place the word because there will always be a
# space/letter above or below it.
#
# Example 3:
#
# Input: board = [["#", " ", "#"], [" ", " ", "#"], ["#", " ", "c"]], word =
# "ca"
# Output: true
# Explanation: The word "ca" can be placed as shown above (right to left).
#
#
#
# Constraints:
#
#
# m == board.length
#
#
# n == board[i].length
#
#
# 1 <= m * n <= 2 * 10^5
#
#
# board[i][j] will be ' ', '#', or a lowercase English letter.
#
#
# 1 <= word.length <= max(m, n)
#
#
# word will contain only lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def placeWordInCrossword(self, board: List[List[str]], word: str) -> bool:
        """
        Interview explanation:
        Place word in an empty slot between '#'/borders horizontally or
        vertically; cells must be space or matching letter; reverse allowed.

        Algorithm:
        - Extract all slots of length len(word); test word and reverse.

        Complexity: O(mn * L) time, O(L) space.
        """
        m, n = len(board), len(board[0])
        L = len(word)

        def fits(cells, w):
            return all(c == ' ' or c == ch for c, ch in zip(cells, w))

        def check_slot(cells):
            if len(cells) != L:
                return False
            return fits(cells, word) or fits(cells, word[::-1])

        for i in range(m):
            j = 0
            while j < n:
                if board[i][j] == '#':
                    j += 1
                    continue
                k = j
                while k < n and board[i][k] != '#':
                    k += 1
                if check_slot([board[i][t] for t in range(j, k)]):
                    return True
                j = k
        for j in range(n):
            i = 0
            while i < m:
                if board[i][j] == '#':
                    i += 1
                    continue
                k = i
                while k < m and board[k][j] != '#':
                    k += 1
                if check_slot([board[t][j] for t in range(i, k)]):
                    return True
                i = k
        return False
# @lc code=end
