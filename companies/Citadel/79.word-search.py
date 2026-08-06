#
# @lc app=leetcode id=79 lang=python3
#
# [79] Word Search
#
# https://leetcode.com/problems/word-search/description/
#
# algorithms
# Medium (47.30%)
# Likes:    17715
# Dislikes: 757
# Total Accepted:    2.5M
# Total Submissions: 5.3M
# Testcase Example:  '[["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]\n"ABCCED"'
#
# Given an m x n grid of characters board and a string word, return true if
# word exists in the grid.
# 
# The word can be constructed from letters of sequentially adjacent cells,
# where adjacent cells are horizontally or vertically neighboring. The same
# letter cell may not be used more than once.
# 
# 
# Example 1:
# 
# 
# Input: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word
# = "ABCCED"
# Output: true
# 
# 
# Example 2:
# 
# 
# Input: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word
# = "SEE"
# Output: true
# 
# 
# Example 3:
# 
# 
# Input: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word
# = "ABCB"
# Output: false
# 
# 
# 
# Constraints:
# 
# 
# m == board.length
# n = board[i].length
# 1 <= m, n <= 6
# 1 <= word.length <= 15
# board and word consists of only lowercase and uppercase English letters.
# 
# 
# 
# Follow up: Could you use search pruning to make your solution faster with a
# larger board?
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:
        """
        Interview explanation:
        This is DFS backtracking on a grid. From any cell matching word[0], walk
        four directions to match the next character. Mark the current cell as
        visited during the path to enforce the rule that a cell cannot be reused,
        then restore it when backtracking.

        Edge cases and tests:
        - Word of length 1.
        - Paths requiring turns.
        - Reuse of the same cell must be rejected.
        - Character frequency precheck can reject impossible words early.

        Complexity: O(m*n*4^L) worst-case time, O(L) recursion space.
        """
        from collections import Counter

        m, n = len(board), len(board[0])
        board_count = Counter(ch for row in board for ch in row)
        word_count = Counter(word)
        for ch, count in word_count.items():
            if board_count[ch] < count:
                return False

        def dfs(r: int, c: int, index: int) -> bool:
            if index == len(word):
                return True
            if r < 0 or r == m or c < 0 or c == n or board[r][c] != word[index]:
                return False

            saved = board[r][c]
            board[r][c] = '#'
            found = (
                dfs(r + 1, c, index + 1) or
                dfs(r - 1, c, index + 1) or
                dfs(r, c + 1, index + 1) or
                dfs(r, c - 1, index + 1)
            )
            board[r][c] = saved
            return found

        for r in range(m):
            for c in range(n):
                if dfs(r, c, 0):
                    return True
        return False
# @lc code=end


