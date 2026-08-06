#
# @lc app=leetcode id=733 lang=python3
#
# [733] Flood Fill
#
# https://leetcode.com/problems/flood-fill/description/
#
# algorithms
# Easy (68.72%)
# Likes:    9611
# Dislikes: 964
# Total Accepted:    1.5M
# Total Submissions: 2.2M
# Testcase Example:  "[[1,1,1],[1,1,0],[1,0,1]]"
#
# You are given an image represented by an m x n grid of integers image, where
# image[i][j] represents the pixel value of the image. You are also given three
# integers sr, sc, and color. Your task is to perform a flood fill on the image
# starting from the pixel image[sr][sc].
#
# To perform a flood fill:
#
# Begin with the starting pixel and change its color to color.
#
# Perform the same process for each pixel that is directly adjacent (pixels
# that share a side with the original pixel, either horizontally or vertically)
# and shares the same color as the starting pixel.
#
# Keep repeating this process by checking neighboring pixels of the updated
# pixels and modifying their color if it matches the original color of the
# starting pixel.
#
# The process stops when there are no more adjacent pixels of the original
# color to update.
#
# Return the modified image after performing the flood fill.
#
# Example 1:
#
# Input: image = [[1,1,1],[1,1,0],[1,0,1]], sr = 1, sc = 1, color = 2
#
# Output: [[2,2,2],[2,2,0],[2,0,1]]
#
# Explanation:
#
# From the center of the image with position (sr, sc) = (1, 1) (i.e., the red
# pixel), all pixels connected by a path of the same color as the starting
# pixel (i.e., the blue pixels) are colored with the new color.
#
# Note the bottom corner is not colored 2, because it is not horizontally or
# vertically connected to the starting pixel.
#
# Example 2:
#
# Input: image = [[0,0,0],[0,0,0]], sr = 0, sc = 0, color = 0
#
# Output: [[0,0,0],[0,0,0]]
#
# Explanation:
#
# The starting pixel is already colored with 0, which is the same as the target
# color. Therefore, no changes are made to the image.
#
# Constraints:
#
# m == image.length
#
# n == image[i].length
#
# 1 <= m, n <= 50
#
# 0 <= image[i][j], color < 2^16
#
# 0 <= sr < m
#
# 0 <= sc < n
#


# @lc code=start
from collections import deque
from typing import List


class Solution:
    def floodFill(
        self, image: List[List[int]], sr: int, sc: int, color: int
    ) -> List[List[int]]:
        """
        Interview explanation:
        Classic flood fill / connected component recoloring. From (sr,sc), DFS
        (or BFS) through 4-adjacent pixels sharing the original color and paint
        them with the new color. If already the target color, return as-is.

        Algorithm (DFS):
        - old = image[sr][sc]; if old == color: return image
        - Recurse/stack to 4-neighbors with value old; set to color

        Complexity: O(mn) time and space.
        """
        old = image[sr][sc]
        if old == color:
            return image
        m, n = len(image), len(image[0])

        def dfs(r: int, c: int) -> None:
            if not (0 <= r < m and 0 <= c < n) or image[r][c] != old:
                return
            image[r][c] = color
            dfs(r + 1, c)
            dfs(r - 1, c)
            dfs(r, c + 1)
            dfs(r, c - 1)

        dfs(sr, sc)
        return image

    def floodFill_bfs(
        self, image: List[List[int]], sr: int, sc: int, color: int
    ) -> List[List[int]]:
        """
        Interview explanation:
        Alternate classic: BFS queue flood fill with the same recoloring rule.

        Algorithm:
        - If old == color: return
        - Queue (sr,sc); while queue: paint neighbors equal to old

        Complexity: O(mn) time and space.
        """
        old = image[sr][sc]
        if old == color:
            return image
        m, n = len(image), len(image[0])
        q = deque([(sr, sc)])
        image[sr][sc] = color
        while q:
            r, c = q.popleft()
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < m and 0 <= nc < n and image[nr][nc] == old:
                    image[nr][nc] = color
                    q.append((nr, nc))
        return image
# @lc code=end

