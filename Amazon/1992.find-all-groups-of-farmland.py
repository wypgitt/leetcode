#
# @lc app=leetcode id=1992 lang=python3
#
# [1992] Find All Groups of Farmland
#
# https://leetcode.com/problems/find-all-groups-of-farmland/description/
#
# algorithms
# Medium (75.47%)
# Likes:    1450
# Dislikes: 92
# Total Accepted:    144K
# Total Submissions: 191K
# Testcase Example:  "[[1,0,0],[0,1,1],[0,1,1]]"
#
# You are given a 0-indexed m x n binary matrix land where a 0 represents a
# hectare of forested land and a 1 represents a hectare of farmland.
#
# To keep the land organized, there are designated rectangular areas of
# hectares that consist entirely of farmland. These rectangular areas are
# called groups. No two groups are adjacent, meaning farmland in one group is
# not four-directionally adjacent to another farmland in a different group.
#
# land can be represented by a coordinate system where the top left corner of
# land is (0, 0) and the bottom right corner of land is (m-1, n-1). Find the
# coordinates of the top left and bottom right corner of each group of
# farmland. A group of farmland with a top left corner at (r_1, c_1) and a
# bottom right corner at (r_2, c_2) is represented by the 4-length array [r_1,
# c_1, r_2, c_2].
#
# Return a 2D array containing the 4-length arrays described above for each
# group of farmland in land. If there are no groups of farmland, return an
# empty array. You may return the answer in any order.
#
# Example 1:
#
# Input: land = [[1,0,0],[0,1,1],[0,1,1]]
# Output: [[0,0,0,0],[1,1,2,2]]
# Explanation:
# The first group has a top left corner at land[0][0] and a bottom right corner
# at land[0][0].
# The second group has a top left corner at land[1][1] and a bottom right
# corner at land[2][2].
#
# Example 2:
#
# Input: land = [[1,1],[1,1]]
# Output: [[0,0,1,1]]
# Explanation:
# The first group has a top left corner at land[0][0] and a bottom right corner
# at land[1][1].
#
# Example 3:
#
# Input: land = [[0]]
# Output: []
# Explanation:
# There are no groups of farmland.
#
# Constraints:
#
# m == land.length
#
# n == land[i].length
#
# 1 <= m, n <= 300
#
# land consists of only 0's and 1's.
#
# Groups of farmland are rectangular in shape.
#

# @lc code=start
from typing import List


class Solution:
    def findFarmland(self, land: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Rectangular groups of 1s (farmland). Scan for top-left corners; expand
        to bottom-right by walking right/down while cells are 1; mark visited 0.

        Algorithm:
        - For each land[r][c]==1: expand c2 while right is 1; r2 while down is 1;
          zero the rectangle; append [r,c,r2,c2].

        Complexity: O(mn) time, O(1) extra besides output.
        """
        m, n = len(land), len(land[0])
        ans = []
        for r in range(m):
            for c in range(n):
                if land[r][c] == 0:
                    continue
                r2, c2 = r, c
                while c2 + 1 < n and land[r][c2 + 1] == 1:
                    c2 += 1
                while r2 + 1 < m and land[r2 + 1][c] == 1:
                    r2 += 1
                for i in range(r, r2 + 1):
                    for j in range(c, c2 + 1):
                        land[i][j] = 0
                ans.append([r, c, r2, c2])
        return ans

    def findFarmland_bfs(self, land: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Alternate BFS/DFS flood-fill tracking min/max row/col of each component
        (rectangles guaranteed by problem).

        Algorithm:
        - On each unvisited 1, BFS; track bounds; mark visited.

        Complexity: O(mn) time, O(mn) space.
        """
        from collections import deque

        m, n = len(land), len(land[0])
        ans = []
        for r in range(m):
            for c in range(n):
                if land[r][c] != 1:
                    continue
                q = deque([(r, c)])
                land[r][c] = 0
                r1 = c1 = 10**9
                r2 = c2 = -1
                while q:
                    i, j = q.popleft()
                    r1, c1 = min(r1, i), min(c1, j)
                    r2, c2 = max(r2, i), max(c2, j)
                    for ni, nj in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)):
                        if 0 <= ni < m and 0 <= nj < n and land[ni][nj] == 1:
                            land[ni][nj] = 0
                            q.append((ni, nj))
                ans.append([r1, c1, r2, c2])
        return ans
# @lc code=end

