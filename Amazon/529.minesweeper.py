#
# @lc app=leetcode id=529 lang=python3
#
# [529] Minesweeper
#
# https://leetcode.com/problems/minesweeper/description/
#
# algorithms
# Medium (68.87%)
# Likes:    2102
# Dislikes: 1090
# Total Accepted:    210K
# Total Submissions: 304K
# Testcase Example:  "[[\"E\",\"E\",\"E\",\"E\",\"E\"],[\"E\",\"E\",\"M\",\"E\",\"E\"],[\"E\",\"E\",\"E\",\"E\",\"E\"],[\"E\",\"E\",\"E\",\"E\",\"E\"]]"
#
# Let's play the minesweeper game (Wikipedia, online game)!
#
# You are given an m x n char matrix board representing the game board where:
#
# 'M' represents an unrevealed mine,
#
# 'E' represents an unrevealed empty square,
#
# 'B' represents a revealed blank square that has no adjacent mines (i.e.,
# above, below, left, right, and all 4 diagonals),
#
# digit ('1' to '8') represents how many mines are adjacent to this revealed
# square, and
#
# 'X' represents a revealed mine.
#
# You are also given an integer array click where click = [click_r, click_c]
# represents the next click position among all the unrevealed squares ('M' or
# 'E').
#
# Return the board after revealing this position according to the following
# rules:
#
# If a mine 'M' is revealed, then the game is over. You should change it to
# 'X'.
#
# If an empty square 'E' with no adjacent mines is revealed, then change it to
# a revealed blank 'B' and all of its adjacent unrevealed squares should be
# revealed recursively.
#
# If an empty square 'E' with at least one adjacent mine is revealed, then
# change it to a digit ('1' to '8') representing the number of adjacent mines.
#
# Return the board when no more squares will be revealed.
#
# Example 1:
#
# Input: board =
# [["E","E","E","E","E"],["E","E","M","E","E"],["E","E","E","E","E"],["E","E","E","E","E"]],
# click = [3,0]
# Output:
# [["B","1","E","1","B"],["B","1","M","1","B"],["B","1","1","1","B"],["B","B","B","B","B"]]
#
# Example 2:
#
# Input: board =
# [["B","1","E","1","B"],["B","1","M","1","B"],["B","1","1","1","B"],["B","B","B","B","B"]],
# click = [1,2]
# Output:
# [["B","1","E","1","B"],["B","1","X","1","B"],["B","1","1","1","B"],["B","B","B","B","B"]]
#
# Constraints:
#
# m == board.length
#
# n == board[i].length
#
# 1 <= m, n <= 50
#
# board[i][j] is either 'M', 'E', 'B', or a digit from '1' to '8'.
#
# click.length == 2
#
# 0 <= click_r < m
#
# 0 <= click_c < n
#
# board[click_r][click_c] is either 'M' or 'E'.
#

# @lc code=start
from collections import deque
from typing import List
class Solution:
    def updateBoard(self, board: List[List[str]], click: List[int]) -> List[List[str]]:
        """
        Interview explanation:
        If click is a mine ('M'), mark 'X'. Otherwise reveal: count adjacent
        mines; if > 0 write the digit, else write 'B' and flood-fill neighbors
        (DFS/BFS) like classic Minesweeper.

        Algorithm:
        - Handle mine click.
        - DFS/BFS from click; for each 'E' cell, count neighbors that are 'M'.
        - Digit or 'B'; recurse/enqueue only when 'B'.

        Complexity: O(m*n) time and space worst case.
        """
        m, n = len(board), len(board[0])
        r, c = click
        if board[r][c] == "M":
            board[r][c] = "X"
            return board

        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        def count_mines(i: int, j: int) -> int:
            cnt = 0
            for di, dj in dirs:
                ni, nj = i + di, j + dj
                if 0 <= ni < m and 0 <= nj < n and board[ni][nj] == "M":
                    cnt += 1
            return cnt

        def dfs(i: int, j: int) -> None:
            if not (0 <= i < m and 0 <= j < n) or board[i][j] != "E":
                return
            mines = count_mines(i, j)
            if mines:
                board[i][j] = str(mines)
                return
            board[i][j] = "B"
            for di, dj in dirs:
                dfs(i + di, j + dj)

        dfs(r, c)
        return board

    def updateBoard_bfs(self, board: List[List[str]], click: List[int]) -> List[List[str]]:
        """
        Interview explanation:
        Alternate: same rules with BFS flood-fill instead of DFS recursion.

        Complexity: O(m*n) time and space.
        """
        m, n = len(board), len(board[0])
        r, c = click
        if board[r][c] == "M":
            board[r][c] = "X"
            return board

        dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        def count_mines(i: int, j: int) -> int:
            return sum(
                0 <= i + di < m and 0 <= j + dj < n and board[i + di][j + dj] == "M"
                for di, dj in dirs
            )

        q = deque([(r, c)])
        while q:
            i, j = q.popleft()
            if board[i][j] != "E":
                continue
            mines = count_mines(i, j)
            if mines:
                board[i][j] = str(mines)
            else:
                board[i][j] = "B"
                for di, dj in dirs:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < m and 0 <= nj < n and board[ni][nj] == "E":
                        q.append((ni, nj))
        return board
# @lc code=end

