#
# @lc app=leetcode id=3568 lang=python3
#
# [3568] Minimum Moves to Clean the Classroom
#
# https://leetcode.com/problems/minimum-moves-to-clean-the-classroom/description/
#
# algorithms
# Medium (27.07%)
# Likes:    131
# Dislikes: 16
# Total Accepted:    9.5K
# Total Submissions: 35K
# Testcase Example:  "[\"S.\", \"XL\"]\n2"
#
#
# You are given an m x n grid classroom where a student volunteer is
# tasked with cleaning up litter scattered around the room. Each cell in
# the grid is one of the following:
#
# 'S': Starting position of the student
#
# 'L': Litter that must be collected (once collected, the cell becomes
# empty)
#
# 'R': Reset area that restores the student's energy to full capacity,
# regardless of their current energy level (can be used multiple times)
#
# 'X': Obstacle the student cannot pass through
#
# '.': Empty space
#
# You are also given an integer energy, representing the student's maximum
# energy capacity. The student starts with this energy from the starting
# position 'S'.
#
# Each move to an adjacent cell (up, down, left, or right) costs 1 unit of
# energy. If the energy reaches 0, the student can only continue if they
# are on a reset area 'R', which resets the energy to its maximum capacity
# energy.
#
# Return the minimum number of moves required to collect all litter items,
# or -1 if it's impossible.
#
# Example 1:
#
# Input: classroom = ["S.", "XL"], energy = 2
#
# Output: 2
#
# Explanation:
#
# The student starts at cell (0, 0) with 2 units of energy.
#
# Since cell (1, 0) contains an obstacle 'X', the student cannot move
# directly downward.
#
# A valid sequence of moves to collect all litter is as follows:
#
# Move 1: From (0, 0) → (0, 1) with 1 unit of energy and 1 unit remaining.
#
# Move 2: From (0, 1) → (1, 1) to collect the litter 'L'.
#
# The student collects all the litter using 2 moves. Thus, the output is
# 2.
#
# Example 2:
#
# Input: classroom = ["LS", "RL"], energy = 4
#
# Output: 3
#
# Explanation:
#
# The student starts at cell (0, 1) with 4 units of energy.
#
# A valid sequence of moves to collect all litter is as follows:
#
# Move 1: From (0, 1) → (0, 0) to collect the first litter 'L' with 1 unit
# of energy used and 3 units remaining.
#
# Move 2: From (0, 0) → (1, 0) to 'R' to reset and restore energy back to
# 4.
#
# Move 3: From (1, 0) → (1, 1) to collect the second litter 'L'.
#
# The student collects all the litter using 3 moves. Thus, the output is
# 3.
#
# Example 3:
#
# Input: classroom = ["L.S", "RXL"], energy = 3
#
# Output: -1
#
# Explanation:
#
# No valid path collects all 'L'.
#
# Constraints:
#
# 1 <= m == classroom.length <= 20
#
# 1 <= n == classroom[i].length <= 20
#
# classroom[i][j] is one of 'S', 'L', 'R', 'X', or '.'
#
# 1 <= energy <= 50
#
# There is exactly one 'S' in the grid.
#
# There are at most 10 'L' cells in the grid.
#

# @lc code=start

from typing import List
from collections import deque


class Solution:
    def minMoves(self, classroom: List[str], energy: int) -> int:
        """
        Interview explanation:
        Collect all litter under an energy budget with optional resets on 'R'.
        BFS on state (r, c, energy_left, litter_mask); ≤10 litters so 2^L is fine.

        Algorithm:
        - Index each 'L'; start BFS from 'S' with full energy and full mask of
          remaining litter.
        - Move 4-way; cost 1 energy; landing on 'R' refills; landing on 'L'
          clears that bit. Skip 'X' / zero energy before moving.
        - First time mask==0 → answer; track visited[r][c][e][mask].

        Complexity: O(m·n·E·2^L) time and space.
        """
        m, n = len(classroom), len(classroom[0])
        litter_id = [[-1] * n for _ in range(m)]
        sr = sc = 0
        cnt = 0
        for i in range(m):
            for j in range(n):
                ch = classroom[i][j]
                if ch == 'S':
                    sr, sc = i, j
                elif ch == 'L':
                    litter_id[i][j] = cnt
                    cnt += 1
        if cnt == 0:
            return 0

        full = (1 << cnt) - 1
        vis = [
            [[[False] * (1 << cnt) for _ in range(energy + 1)] for _ in range(n)]
            for _ in range(m)
        ]
        q = deque([(sr, sc, energy, full)])
        vis[sr][sc][energy][full] = True
        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
        steps = 0
        while q:
            for _ in range(len(q)):
                r, c, e, mask = q.popleft()
                if mask == 0:
                    return steps
                if e <= 0:
                    continue
                for dr, dc in dirs:
                    nr, nc = r + dr, c + dc
                    if not (0 <= nr < m and 0 <= nc < n):
                        continue
                    if classroom[nr][nc] == 'X':
                        continue
                    ne = energy if classroom[nr][nc] == 'R' else e - 1
                    nmask = mask
                    lid = litter_id[nr][nc]
                    if lid >= 0:
                        nmask &= ~(1 << lid)
                    if not vis[nr][nc][ne][nmask]:
                        vis[nr][nc][ne][nmask] = True
                        q.append((nr, nc, ne, nmask))
            steps += 1
        return -1
# @lc code=end
