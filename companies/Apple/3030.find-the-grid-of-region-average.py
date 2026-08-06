#
# @lc app=leetcode id=3030 lang=python3
#
# [3030] Find the Grid of Region Average
#
# https://leetcode.com/problems/find-the-grid-of-region-average/description/
#
# algorithms
# Medium (43.94%)
# Likes:    93
# Dislikes: 137
# Total Accepted:    12.5K
# Total Submissions: 28.5K
# Testcase Example:  "[[5,6,7,10],[8,9,10,10],[11,12,13,10]]\n3"
#
#
# You are given m x n grid image which represents a grayscale image, where
# image[i][j] represents a pixel with intensity in the range [0..255]. You
# are also given a non-negative integer threshold.
#
# Two pixels are adjacent if they share an edge.
#
# A region is a 3 x 3 subgrid where the absolute difference in intensity
# between any two adjacent pixels is less than or equal to threshold.
#
# All pixels in a region belong to that region, note that a pixel can
# belong to multiple regions.
#
# You need to calculate a m x n grid result, where result[i][j] is the
# average intensity of the regions to which image[i][j] belongs, rounded
# down to the nearest integer. If image[i][j] belongs to multiple regions,
# result[i][j] is the average of the rounded-down average intensities of
# these regions, rounded down to the nearest integer. If image[i][j] does
# not belong to any region, result[i][j] is equal to image[i][j].
#
# Return the grid result.
#
# Example 1:
#
# Input: image = [[5,6,7,10],[8,9,10,10],[11,12,13,10]], threshold = 3
#
# Output: [[9,9,9,9],[9,9,9,9],[9,9,9,9]]
#
# Explanation:
#
# There are two regions as illustrated above. The average intensity of the
# first region is 9, while the average intensity of the second region is
# 9.67 which is rounded down to 9. The average intensity of both of the
# regions is (9 + 9) / 2 = 9. As all the pixels belong to either region 1,
# region 2, or both of them, the intensity of every pixel in the result is
# 9.
#
# Please note that the rounded-down values are used when calculating the
# average of multiple regions, hence the calculation is done using 9 as
# the average intensity of region 2, not 9.67.
#
# Example 2:
#
# Input: image = [[10,20,30],[15,25,35],[20,30,40],[25,35,45]], threshold
# = 12
#
# Output: [[25,25,25],[27,27,27],[27,27,27],[30,30,30]]
#
# Explanation:
#
# There are two regions as illustrated above. The average intensity of the
# first region is 25, while the average intensity of the second region is
# 30. The average intensity of both of the regions is (25 + 30) / 2 = 27.5
# which is rounded down to 27.
#
# All the pixels in row 0 of the image belong to region 1, hence all the
# pixels in row 0 in the result are 25. Similarly, all the pixels in row 3
# in the result are 30. The pixels in rows 1 and 2 of the image belong to
# region 1 and region 2, hence their assigned value is 27 in the result.
#
# Example 3:
#
# Input: image = [[5,6,7],[8,9,10],[11,12,13]], threshold = 1
#
# Output: [[5,6,7],[8,9,10],[11,12,13]]
#
# Explanation:
#
# There is only one 3 x 3 subgrid, while it does not have the condition on
# difference of adjacent pixels, for example, the difference between
# image[0][0] and image[1][0] is |5 - 8| = 3 > threshold = 1. None of them
# belong to any valid regions, so the result should be the same as image.
#
# Constraints:
#
# 3 <= n, m <= 500
#
# 0 <= image[i][j] <= 255
#
# 0 <= threshold <= 255
#

# @lc code=start

from typing import List


class Solution:
    def resultGrid(self, image: List[List[int]], threshold: int) -> List[List[int]]:
        """
        Interview explanation:
        Valid 3x3 regions have adjacent |diff|<=threshold. Each pixel's result
        is the floor-average of the floor-averages of regions covering it
        (or the original value if uncovered).

        Algorithm:
        - Enumerate every top-left of a 3x3; validate horizontal/vertical edges.
        - On valid region, add floor(sum/9) into sum/count grids for all 9 cells.
        - Final cell = sum//count if count>0 else image[i][j].

        Complexity: O(m*n) time, O(m*n) space.
        """
        m, n = len(image), len(image[0])
        total = [[0] * n for _ in range(m)]
        count = [[0] * n for _ in range(m)]

        def is_region(r: int, c: int) -> bool:
            for i in range(r, r + 3):
                for j in range(c, c + 3):
                    if i + 1 < r + 3 and abs(image[i][j] - image[i + 1][j]) > threshold:
                        return False
                    if j + 1 < c + 3 and abs(image[i][j] - image[i][j + 1]) > threshold:
                        return False
            return True

        for i in range(m - 2):
            for j in range(n - 2):
                if not is_region(i, j):
                    continue
                avg = (
                    sum(image[x][y] for x in range(i, i + 3) for y in range(j, j + 3))
                    // 9
                )
                for x in range(i, i + 3):
                    for y in range(j, j + 3):
                        total[x][y] += avg
                        count[x][y] += 1

        return [
            [
                total[i][j] // count[i][j] if count[i][j] else image[i][j]
                for j in range(n)
            ]
            for i in range(m)
        ]
# @lc code=end
