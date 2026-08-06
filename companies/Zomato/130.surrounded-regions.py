"""
Approach: Mark border-connected 'O' cells as safe, then flip every remaining 'O'.
Data structure: a deque performs iterative BFS and avoids recursion-depth issues on large boards.
Interview logic: an 'O' is uncapturable exactly when it can reach the border through other 'O' cells. Finding those safe cells first lets the rest be flipped confidently.
Complexity: O(mn) time, O(mn) worst-case queue space.
Tests and edge cases: empty board; all-border regions stay 'O'; fully enclosed regions become 'X'.
"""
from __future__ import annotations
from collections import deque
from typing import List

# @lc code=start
from collections import deque
class Solution:
    def solve(self, board: List[List[str]]) -> None:
        if not board or not board[0]:
            return
        rows, cols = len(board), len(board[0])
        q = deque()
        def mark(r: int, c: int) -> None:
            if board[r][c] == 'O':
                board[r][c] = 'S'
                q.append((r, c))
        for r in range(rows):
            mark(r, 0); mark(r, cols - 1)
        for c in range(cols):
            mark(0, c); mark(rows - 1, c)
        while q:
            r, c = q.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == 'O':
                    board[nr][nc] = 'S'
                    q.append((nr, nc))
        for r in range(rows):
            for c in range(cols):
                if board[r][c] == 'O':
                    board[r][c] = 'X'
                elif board[r][c] == 'S':
                    board[r][c] = 'O'
# @lc code=end
