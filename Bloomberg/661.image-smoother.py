#
# @lc app=leetcode id=661 lang=python3
#
# [661] Image Smoother
#
# https://leetcode.com/problems/image-smoother/description/
#
# algorithms
# Easy (69.48%)
# Likes:    1252
# Dislikes: 3001
# Total Accepted:    207K
# Total Submissions: 297K
# Testcase Example:  "[[1,1,1],[1,0,1],[1,1,1]]"
#
# An image smoother is a filter of the size 3 x 3 that can be applied to each
# cell of an image by rounding down the average of the cell and the eight
# surrounding cells (i.e., the average of the nine cells in the blue smoother).
# If one or more of the surrounding cells of a cell is not present, we do not
# consider it in the average (i.e., the average of the four cells in the red
# smoother).
#
# Given an m x n integer matrix img representing the grayscale of an image,
# return the image after applying the smoother on each cell of it.
#
# Example 1:
#
# Input: img = [[1,1,1],[1,0,1],[1,1,1]]
# Output: [[0,0,0],[0,0,0],[0,0,0]]
# Explanation:
# For the points (0,0), (0,2), (2,0), (2,2): floor(3/4) = floor(0.75) = 0
# For the points (0,1), (1,0), (1,2), (2,1): floor(5/6) = floor(0.83333333) = 0
# For the point (1,1): floor(8/9) = floor(0.88888889) = 0
#
# Example 2:
#
# Input: img = [[100,200,100],[200,50,200],[100,200,100]]
# Output: [[137,141,137],[141,138,141],[137,141,137]]
# Explanation:
# For the points (0,0), (0,2), (2,0), (2,2): floor((100+200+200+50)/4) =
# floor(137.5) = 137
# For the points (0,1), (1,0), (1,2), (2,1): floor((200+200+50+200+100+100)/6)
# = floor(141.666667) = 141
# For the point (1,1): floor((50+200+200+200+200+100+100+100+100)/9) =
# floor(138.888889) = 138
#
# Constraints:
#
# m == img.length
#
# n == img[i].length
#
# 1 <= m, n <= 200
#
# 0 <= img[i][j] <= 255
#

# @lc code=start
from typing import List


class Solution:
    def imageSmoother(self, img: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Each cell becomes the floor average of itself and its valid 8-neighbors
        (cells outside the grid are ignored). Build a new matrix so updates do
        not pollute neighbors still being averaged.

        Algorithm:
        - For every (i, j), sum values and count cells in the 3x3 window clipped
          to bounds; write sum // count into the result.

        Complexity: O(m*n) time, O(m*n) space for the answer matrix.
        """
        m, n = len(img), len(img[0])
        res = [[0] * n for _ in range(m)]
        for i in range(m):
            for j in range(n):
                total = cnt = 0
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        ni, nj = i + di, j + dj
                        if 0 <= ni < m and 0 <= nj < n:
                            total += img[ni][nj]
                            cnt += 1
                res[i][j] = total // cnt
        return res
# @lc code=end
