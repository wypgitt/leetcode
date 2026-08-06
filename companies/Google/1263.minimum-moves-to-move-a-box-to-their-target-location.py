#
# @lc app=leetcode id=1263 lang=python3
#
# [1263] Minimum Moves to Move a Box to Their Target Location
#
# https://leetcode.com/problems/minimum-moves-to-move-a-box-to-their-target-location/description/
#
# algorithms
# Hard (49.96%)
# Likes:    895
# Dislikes: 61
# Total Accepted:    33.0K
# Total Submissions: 66.1K
# Testcase Example:  "[[\"#\",\"#\",\"#\",\"#\",\"#\",\"#\"],[\"#\",\"T\",\"#\",\"#\",\"#\",\"#\"],[\"#\",\".\",\".\",\"B\",\".\",\"#\"],[\"#\",\".\",\"#\",\"#\",\".\",\"#\"],[\"#\",\".\",\".\",\".\",\"S\",\"#\"],[\"#\",\"#\",\"#\",\"#\",\"#\",\"#\"]]"
#
# A storekeeper is a game in which the player pushes boxes around in a
# warehouse trying to get them to target locations.
#
# The game is represented by an m x n grid of characters grid where each
# element is a wall, floor, or box.
#
# Your task is to move the box 'B' to the target position 'T' under the
# following rules:
#
# The character 'S' represents the player. The player can move up, down, left,
# right in grid if it is a floor (empty cell).
#
# The character '.' represents the floor which means a free cell to walk.
#
# The character '#' represents the wall which means an obstacle (impossible to
# walk there).
#
# There is only one box 'B' and one target cell 'T' in the grid.
#
# The box can be moved to an adjacent free cell by standing next to the box and
# then moving in the direction of the box. This is a push.
#
# The player cannot walk through the box.
#
# Return the minimum number of pushes to move the box to the target. If there
# is no way to reach the target, return -1.
#
# Example 1:
#
# Input: grid = [["#","#","#","#","#","#"],
# ["#","T","#","#","#","#"],
# ["#",".",".","B",".","#"],
# ["#",".","#","#",".","#"],
# ["#",".",".",".","S","#"],
# ["#","#","#","#","#","#"]]
# Output: 3
# Explanation: We return only the number of times the box is pushed.
#
# Example 2:
#
# Input: grid = [["#","#","#","#","#","#"],
# ["#","T","#","#","#","#"],
# ["#",".",".","B",".","#"],
# ["#","#","#","#",".","#"],
# ["#",".",".",".","S","#"],
# ["#","#","#","#","#","#"]]
# Output: -1
#
# Example 3:
#
# Input: grid = [["#","#","#","#","#","#"],
# ["#","T",".",".","#","#"],
# ["#",".","#","B",".","#"],
# ["#",".",".",".",".","#"],
# ["#",".",".",".","S","#"],
# ["#","#","#","#","#","#"]]
# Output: 5
# Explanation: push the box down, left, left, up and up.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 20
#
# grid contains only characters '.', '#', 'S', 'T', or 'B'.
#
# There is only one character 'S', 'B', and 'T' in the grid.
#

# @lc code=start

from typing import List
from collections import deque


class Solution:
    def minPushBox(self, grid: List[List[str]]) -> int:
        """
        Interview explanation:
        Sokoban-style: push box 'B' to target 'T' with player 'S'. State is
        (box_r, box_c, player_r, player_c). BFS on pushes: for each of 4 push
        directions, check player can walk to the cell opposite the push
        without crossing the box (BFS walk on floors), then push costs +1.

        Algorithm:
        - Locate S,B,T. BFS queue of (br,bc,pr,pc,pushes); visited (br,bc,pr,pc)
          can reduce to (br,bc, push_dir) but full state is fine for small grids.
        - For each push dir: need player reach (br-dr,bc-dc) and next box cell
          in bounds and not wall; enqueue new state with pushes+1.
        - Return pushes when box on T; else -1.

        Complexity: O((mn)^2) states/walks on m,n<=20.
        """
        m, n = len(grid), len(grid[0])
        sr = sc = br = bc = tr = tc = -1
        for i in range(m):
            for j in range(n):
                if grid[i][j] == "S":
                    sr, sc = i, j
                elif grid[i][j] == "B":
                    br, bc = i, j
                elif grid[i][j] == "T":
                    tr, tc = i, j

        def can_walk(pr: int, pc: int, tr_: int, tc_: int, boxr: int, boxc: int) -> bool:
            if (pr, pc) == (tr_, tc_):
                return True
            q = deque([(pr, pc)])
            seen = {(pr, pc)}
            while q:
                r, c = q.popleft()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if (
                        0 <= nr < m
                        and 0 <= nc < n
                        and (nr, nc) not in seen
                        and grid[nr][nc] != "#"
                        and (nr, nc) != (boxr, boxc)
                    ):
                        if (nr, nc) == (tr_, tc_):
                            return True
                        seen.add((nr, nc))
                        q.append((nr, nc))
            return False

        q = deque([(br, bc, sr, sc, 0)])
        visited = {(br, bc, sr, sc)}
        while q:
            boxr, boxc, pr, pc, pushes = q.popleft()
            if (boxr, boxc) == (tr, tc):
                return pushes
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nbr, nbc = boxr + dr, boxc + dc
                stand_r, stand_c = boxr - dr, boxc - dc
                if not (0 <= nbr < m and 0 <= nbc < n):
                    continue
                if grid[nbr][nbc] == "#":
                    continue
                if not (0 <= stand_r < m and 0 <= stand_c < n):
                    continue
                if grid[stand_r][stand_c] == "#":
                    continue
                if not can_walk(pr, pc, stand_r, stand_c, boxr, boxc):
                    continue
                state = (nbr, nbc, boxr, boxc)
                if state in visited:
                    continue
                visited.add(state)
                q.append((nbr, nbc, boxr, boxc, pushes + 1))
        return -1
# @lc code=end
