#
# @lc app=leetcode id=302 lang=python3
#
# [302] Smallest Rectangle Enclosing Black Pixels
#
# https://leetcode.com/problems/smallest-rectangle-enclosing-black-pixels/description/
#
# algorithms
# Hard (60.96%)
# Likes:    565
# Dislikes: 107
# Total Accepted:    57.7K
# Total Submissions: 94.7K
# Testcase Example:  "[[\"0\",\"0\",\"1\",\"0\"],[\"0\",\"1\",\"1\",\"0\"],[\"0\",\"1\",\"0\",\"0\"]]\n0\n2"
#
#
# You are given an m x n binary matrix image where 0 represents a white
# pixel and 1 represents a black pixel.
#
# The black pixels are connected (i.e., there is only one black region).
# Pixels are connected horizontally and vertically.
#
# Given two integers x and y that represents the location of one of the
# black pixels, return the area of the smallest (axis-aligned) rectangle
# that encloses all black pixels.
#
# You must write an algorithm with less than O(mn) runtime complexity
#
# Example 1:
#
# Input: image = [["0","0","1","0"],["0","1","1","0"],["0","1","0","0"]],
# x = 0, y = 2
# Output: 6
#
# Example 2:
#
# Input: image = [["1"]], x = 0, y = 0
# Output: 1
#
# Constraints:
#
# m == image.length
#
# n == image[i].length
#
# 1 <= m, n <= 100
#
# image[i][j] is either '0' or '1'.
#
# 0 <= x < m
#
# 0 <= y < n
#
# image[x][y] == '1'.
#
# The black pixels in the image only form one component.
#
# @lc code=start
from typing import List


class Solution:
    def minArea(self, image: List[List[str]], x: int, y: int) -> int:
        """
        Interview explanation:
        Black pixels form one connected component. Find min/max row and column
        containing '1' via binary search on rows/cols (projected presence).

        Algorithm:
        - Binary search left boundary in columns [0, y], right in [y, n).
        - Binary search top in rows [0, x], bottom in [x, m).
        - Area = (right-left+1)*(bottom-top+1).

        Complexity: O(m log n + n log m) time, O(1) space.
        """
        m, n = len(image), len(image[0])

        def col_has_black(c: int, r1: int, r2: int) -> bool:
            return any(image[r][c] == "1" for r in range(r1, r2 + 1))

        def row_has_black(r: int, c1: int, c2: int) -> bool:
            return any(image[r][c] == "1" for c in range(c1, c2 + 1))

        def search_left(lo: int, hi: int) -> int:
            while lo < hi:
                mid = (lo + hi) // 2
                if col_has_black(mid, 0, m - 1):
                    hi = mid
                else:
                    lo = mid + 1
            return lo

        def search_right(lo: int, hi: int) -> int:
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if col_has_black(mid, 0, m - 1):
                    lo = mid
                else:
                    hi = mid - 1
            return lo

        def search_top(lo: int, hi: int) -> int:
            while lo < hi:
                mid = (lo + hi) // 2
                if row_has_black(mid, 0, n - 1):
                    hi = mid
                else:
                    lo = mid + 1
            return lo

        def search_bottom(lo: int, hi: int) -> int:
            while lo < hi:
                mid = (lo + hi + 1) // 2
                if row_has_black(mid, 0, n - 1):
                    lo = mid
                else:
                    hi = mid - 1
            return lo

        left = search_left(0, y)
        right = search_right(y, n - 1)
        top = search_top(0, x)
        bottom = search_bottom(x, m - 1)
        return (right - left + 1) * (bottom - top + 1)
# @lc code=end

