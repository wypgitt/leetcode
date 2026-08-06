#
# @lc app=leetcode id=3552 lang=python3
#
# [3552] Grid Teleportation Traversal
#
# https://leetcode.com/problems/grid-teleportation-traversal/description/
#
# algorithms
# Medium (23.80%)
# Likes:    147
# Dislikes: 13
# Total Accepted:    14.5K
# Total Submissions: 61.1K
# Testcase Example:  "[\"A..\",\".A.\",\"...\"]"
#
#
# You are given a 2D character grid matrix of size m x n, represented as
# an array of strings, where matrix[i][j] represents the cell at the
# intersection of the i^th row and j^th column. Each cell is one of the
# following:
#
# '.' representing an empty cell.
#
# '#' representing an obstacle.
#
# An uppercase letter ('A'-'Z') representing a teleportation portal.
#
# You start at the top-left cell (0, 0), and your goal is to reach the
# bottom-right cell (m - 1, n - 1). You can move from the current cell to
# any adjacent cell (up, down, left, right) as long as the destination
# cell is within the grid bounds and is not an obstacle.
#
# If you step on a cell containing a portal letter and you haven't used
# that portal letter before, you may instantly teleport to any other cell
# in the grid with the same letter. This teleportation does not count as a
# move, but each portal letter can be used at most once during your
# journey.
#
# Return the minimum number of moves required to reach the bottom-right
# cell. If it is not possible to reach the destination, return -1.
#
# Example 1:
#
# Input: matrix = ["A..",".A.","..."]
#
# Output: 2
#
# Explanation:
#
# Before the first move, teleport from (0, 0) to (1, 1).
#
# In the first move, move from (1, 1) to (1, 2).
#
# In the second move, move from (1, 2) to (2, 2).
#
# Example 2:
#
# Input: matrix = [".#...",".#.#.",".#.#.","...#."]
#
# Output: 13
#
# Explanation:
#
# Constraints:
#
# 1 <= m == matrix.length <= 10^3
#
# 1 <= n == matrix[i].length <= 10^3
#
# matrix[i][j] is either '#', '.', or an uppercase English letter.
#
# matrix[0][0] is not an obstacle.
#

# @lc code=start
from collections import defaultdict, deque
from itertools import pairwise
from math import inf
from typing import List


class Solution:
    def minMoves(self, matrix: List[str]) -> int:
        """
        Interview explanation:
        Moves cost 1; using a letter portal once teleports to any other cell with
        the same letter at cost 0. Shortest path with 0/1 edge weights.

        Algorithm (0-1 BFS):
        - Index all portal cells by letter.
        - Deque BFS from (0,0): adjacent steps append (cost +1); on first visit
          to a letter, push all its portals to the front (cost +0) and drop the letter.
        - Return dist to bottom-right, or -1.

        Complexity: O(m * n) time and space.
        """
        m, n = len(matrix), len(matrix[0])
        portals = defaultdict(list)
        for i, row in enumerate(matrix):
            for j, c in enumerate(row):
                if c.isalpha():
                    portals[c].append((i, j))

        dist = [[inf] * n for _ in range(m)]
        dist[0][0] = 0
        q = deque([(0, 0)])
        dirs = (-1, 0, 1, 0, -1)

        while q:
            i, j = q.popleft()
            d = dist[i][j]
            if i == m - 1 and j == n - 1:
                return d
            c = matrix[i][j]
            if c in portals:
                for x, y in portals[c]:
                    if d < dist[x][y]:
                        dist[x][y] = d
                        q.appendleft((x, y))
                del portals[c]
            for a, b in pairwise(dirs):
                x, y = i + a, j + b
                if 0 <= x < m and 0 <= y < n and matrix[x][y] != "#" and d + 1 < dist[x][y]:
                    dist[x][y] = d + 1
                    q.append((x, y))
        return -1
# @lc code=end
