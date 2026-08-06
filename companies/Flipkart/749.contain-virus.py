#
# @lc app=leetcode id=749 lang=python3
#
# [749] Contain Virus
#
# https://leetcode.com/problems/contain-virus/description/
#
# algorithms
# Hard (55.58%)
# Likes:    453
# Dislikes: 468
# Total Accepted:    20.0K
# Total Submissions: 36.1K
# Testcase Example:  "[[0,1,0,0,0,0,0,1],[0,1,0,0,0,0,0,1],[0,0,0,0,0,0,0,1],[0,0,0,0,0,0,0,0]]"
#
# A virus is spreading rapidly, and your task is to quarantine the infected
# area by installing walls.
#
# The world is modeled as an m x n binary grid isInfected, where
# isInfected[i][j] == 0 represents uninfected cells, and isInfected[i][j] == 1
# represents cells contaminated with the virus. A wall (and only one wall) can
# be installed between any two 4-directionally adjacent cells, on the shared
# boundary.
#
# Every night, the virus spreads to all neighboring cells in all four
# directions unless blocked by a wall. Resources are limited. Each day, you can
# install walls around only one region (i.e., the affected area (continuous
# block of infected cells) that threatens the most uninfected cells the
# following night). There will never be a tie.
#
# Return the number of walls used to quarantine all the infected regions. If
# the world will become fully infected, return the number of walls used.
#
# Example 1:
#
# Input: isInfected =
# [[0,1,0,0,0,0,0,1],[0,1,0,0,0,0,0,1],[0,0,0,0,0,0,0,1],[0,0,0,0,0,0,0,0]]
# Output: 10
# Explanation: There are 2 contaminated regions.
# On the first day, add 5 walls to quarantine the viral region on the left. The
# board after the virus spreads is:
#
# On the second day, add 5 walls to quarantine the viral region on the right.
# The virus is fully contained.
#
# Example 2:
#
# Input: isInfected = [[1,1,1],[1,0,1],[1,1,1]]
# Output: 4
# Explanation: Even though there is only one cell saved, there are 4 walls
# built.
# Notice that walls are only built on the shared boundary of two different
# cells.
#
# Example 3:
#
# Input: isInfected =
# [[1,1,1,0,0,0,0,0,0],[1,0,1,0,1,1,1,1,1],[1,1,1,0,0,0,0,0,0]]
# Output: 13
# Explanation: The region on the left only builds two new walls.
#
# Constraints:
#
# m == isInfected.length
#
# n == isInfected[i].length
#
# 1 <= m, n <= 50
#
# isInfected[i][j] is either 0 or 1.
#
# There is always a contiguous viral region throughout the described process
# that will infect strictly more uncontaminated squares in the next round.
#


# @lc code=start
from typing import List, Set, Tuple


class Solution:
    def containVirus(self, isInfected: List[List[int]]) -> int:
        """
        Interview explanation:
        Simulate days: find each infected region, its uninfected threatened set,
        and perimeter (walls needed). Quarantine the region threatening the most
        cells (install walls = its perimeter), mark it contained; then remaining
        infected regions expand into threatened cells. Repeat until no threats.

        Algorithm:
        - While True:
          - DFS each unvisited infected cell to get region, threats, perimeter
          - If no threats: break
          - Quarantine max-threat region (set cells to -1); walls += perimeter
          - Expand other regions into threat cells (set to 1)

        Complexity: O(D * m * n) time for D days (bounded by mn); O(mn) space.
        """
        m, n = len(isInfected), len(isInfected[0])
        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
        walls = 0

        def dfs(r, c, seen, region, threats, perim):
            seen.add((r, c))
            region.append((r, c))
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n:
                    if isInfected[nr][nc] == 1 and (nr, nc) not in seen:
                        dfs(nr, nc, seen, region, threats, perim)
                    elif isInfected[nr][nc] == 0:
                        threats.add((nr, nc))
                        perim[0] += 1

        while True:
            seen: Set[Tuple[int, int]] = set()
            regions = []
            for i in range(m):
                for j in range(n):
                    if isInfected[i][j] == 1 and (i, j) not in seen:
                        region: List[Tuple[int, int]] = []
                        threats: Set[Tuple[int, int]] = set()
                        perim = [0]
                        dfs(i, j, seen, region, threats, perim)
                        regions.append((region, threats, perim[0]))
            if not regions:
                break
            regions.sort(key=lambda x: len(x[1]), reverse=True)
            if not regions[0][1]:
                break
            # quarantine
            for r, c in regions[0][0]:
                isInfected[r][c] = -1
            walls += regions[0][2]
            # expand others
            for region, threats, _ in regions[1:]:
                for r, c in threats:
                    isInfected[r][c] = 1
        return walls
# @lc code=end

