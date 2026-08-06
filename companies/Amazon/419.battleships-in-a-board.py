#
# @lc app=leetcode id=419 lang=python3
#
# [419] Battleships in a Board
#
# https://leetcode.com/problems/battleships-in-a-board/description/
#
# algorithms
# Medium (77.7%)
# Likes:    2540
# Dislikes: 1032
# Total Accepted:    293K
# Total Submissions: 377K
# Testcase Example:  "[[\"X\",\".\",\".\",\"X\"],[\".\",\".\",\".\",\"X\"],[\".\",\".\",\".\",\"X\"]]"
#
# Given an m x n matrix board where each cell is a battleship 'X' or empty '.',
# return the number of the battleships on board.
#
# Battleships can only be placed horizontally or vertically on board. In other
# words, they can only be made of the shape 1 x k (1 row, k columns) or k x 1
# (k rows, 1 column), where k can be of any size. At least one horizontal or
# vertical cell separates between two battleships (i.e., there are no adjacent
# battleships).
#
# Example 1:
#
# Input: board = [["X",".",".","X"],[".",".",".","X"],[".",".",".","X"]]
# Output: 2
#
# Example 2:
#
# Input: board = [["."]]
# Output: 0
#
# Constraints:
#
# m == board.length
#
# n == board[i].length
#
# 1 <= m, n <= 200
#
# board[i][j] is either '.' or 'X'.
#
# Follow up: Could you do it in one-pass, using only O(1) extra memory and
# without modifying the values board?
#

# @lc code=start

from typing import List


class Solution:
    def countBattleships(self, board: List[List[str]]) -> int:
        """
        Interview explanation:
        Battleships are 1×k or k×1 with no adjacency. Count only the "head" of
        each ship: an 'X' with no 'X' immediately above or to the left.

        Algorithm:
        - Scan all cells; if board[i][j]=='X' and (i==0 or above!='X') and
          (j==0 or left!='X'), increment count.

        Complexity: O(mn) time, O(1) space.
        """
        if not board:
            return 0
        m, n = len(board), len(board[0])
        count = 0
        for i in range(m):
            for j in range(n):
                if board[i][j] != "X":
                    continue
                if i > 0 and board[i - 1][j] == "X":
                    continue
                if j > 0 and board[i][j - 1] == "X":
                    continue
                count += 1
        return count

    def countBattleshipsDFS(self, board: List[List[str]]) -> int:
        """
        Interview explanation:
        Alternate: DFS/flood-fill each unvisited 'X' component as one ship
        (mutates a copy or marks visited).

        Algorithm:
        - For each 'X', increment and DFS-mark the whole ship as visited.

        Complexity: O(mn) time/space.
        """
        if not board:
            return 0
        m, n = len(board), len(board[0])
        visited = [[False] * n for _ in range(m)]
        count = 0

        def dfs(r: int, c: int) -> None:
            if r < 0 or r >= m or c < 0 or c >= n or visited[r][c] or board[r][c] != "X":
                return
            visited[r][c] = True
            dfs(r + 1, c)
            dfs(r - 1, c)
            dfs(r, c + 1)
            dfs(r, c - 1)

        for i in range(m):
            for j in range(n):
                if board[i][j] == "X" and not visited[i][j]:
                    count += 1
                    dfs(i, j)
        return count
# @lc code=end
