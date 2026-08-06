#
# @lc app=leetcode id=1765 lang=python3
#
# [1765] Map of Highest Peak
#
# https://leetcode.com/problems/map-of-highest-peak/description/
#
# algorithms
# Medium (76.12%)
# Likes:    1590
# Dislikes: 117
# Total Accepted:    169K
# Total Submissions: 222K
# Testcase Example:  "[[0,1],[0,0]]"
#
# You are given an integer matrix isWater of size m x n that represents a map
# of land and water cells.
#
# If isWater[i][j] == 0, cell (i, j) is a land cell.
#
# If isWater[i][j] == 1, cell (i, j) is a water cell.
#
# You must assign each cell a height in a way that follows these rules:
#
# The height of each cell must be non-negative.
#
# If the cell is a water cell, its height must be 0.
#
# Any two adjacent cells must have an absolute height difference of at most 1.
# A cell is adjacent to another cell if the former is directly north, east,
# south, or west of the latter (i.e., their sides are touching).
#
# Find an assignment of heights such that the maximum height in the matrix is
# maximized.
#
# Return an integer matrix height of size m x n where height[i][j] is cell (i,
# j)'s height. If there are multiple solutions, return any of them.
#
# Example 1:
#
# Input: isWater = [[0,1],[0,0]]
# Output: [[1,0],[2,1]]
# Explanation: The image shows the assigned heights of each cell.
# The blue cell is the water cell, and the green cells are the land cells.
#
# Example 2:
#
# Input: isWater = [[0,0,1],[1,0,0],[0,0,0]]
# Output: [[1,1,0],[0,1,1],[1,2,2]]
# Explanation: A height of 2 is the maximum possible height of any assignment.
# Any height assignment that has a maximum height of 2 while still meeting the
# rules will also be accepted.
#
# Constraints:
#
# m == isWater.length
#
# n == isWater[i].length
#
# 1 <= m, n <= 1000
#
# isWater[i][j] is 0 or 1.
#
# There is at least one water cell.
#
# Note: This question is the same as 542:
# https://leetcode.com/problems/01-matrix/
#

# @lc code=start
from typing import List
from collections import deque


class Solution:
    def highestPeak(self, isWater: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Assign heights ≥0 with water cells height 0; maximize the highest peak
        under |h[a]-h[b]|≤1 for adjacent cells. Multi-source BFS from all water
        cells gives the maximum feasible height (= distance to nearest water).

        Algorithm:
        - Queue all water cells at height 0; BFS fill neighbors with dist+1.

        Complexity: O(R*C) time and space.
        """
        R, C = len(isWater), len(isWater[0])
        height = [[-1] * C for _ in range(R)]
        q = deque()
        for r in range(R):
            for c in range(C):
                if isWater[r][c]:
                    height[r][c] = 0
                    q.append((r, c))
        while q:
            r, c = q.popleft()
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= nr < R and 0 <= nc < C and height[nr][nc] == -1:
                    height[nr][nc] = height[r][c] + 1
                    q.append((nr, nc))
        return height

    def highestPeak_inplace(self, isWater: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Alternate: reuse isWater as the height matrix (water→0, land→sentinel)
        then same multi-source BFS.

        Algorithm:
        - Convert cells; BFS update in place.

        Complexity: O(R*C) time and space (queue).
        """
        R, C = len(isWater), len(isWater[0])
        q = deque()
        for r in range(R):
            for c in range(C):
                if isWater[r][c] == 1:
                    isWater[r][c] = 0
                    q.append((r, c))
                else:
                    isWater[r][c] = -1
        while q:
            r, c = q.popleft()
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= nr < R and 0 <= nc < C and isWater[nr][nc] == -1:
                    isWater[nr][nc] = isWater[r][c] + 1
                    q.append((nr, nc))
        return isWater
# @lc code=end
