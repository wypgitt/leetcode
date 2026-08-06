#
# @lc app=leetcode id=832 lang=python3
#
# [832] Flipping an Image
#
# https://leetcode.com/problems/flipping-an-image/description/
#
# algorithms
# Easy (83.92%)
# Likes:    3756
# Dislikes: 263
# Total Accepted:    580K
# Total Submissions: 691K
# Testcase Example:  "[[1,1,0],[1,0,1],[0,0,0]]"
#
# Given an n x n binary matrix image, flip the image horizontally, then invert
# it, and return the resulting image.
#
# To flip an image horizontally means that each row of the image is reversed.
#
# For example, flipping [1,1,0] horizontally results in [0,1,1].
#
# To invert an image means that each 0 is replaced by 1, and each 1 is replaced
# by 0.
#
# For example, inverting [0,1,1] results in [1,0,0].
#
# Example 1:
#
# Input: image = [[1,1,0],[1,0,1],[0,0,0]]
# Output: [[1,0,0],[0,1,0],[1,1,1]]
# Explanation: First reverse each row: [[0,1,1],[1,0,1],[0,0,0]].
# Then, invert the image: [[1,0,0],[0,1,0],[1,1,1]]
#
# Example 2:
#
# Input: image = [[1,1,0,0],[1,0,0,1],[0,1,1,1],[1,0,1,0]]
# Output: [[1,1,0,0],[0,1,1,0],[0,0,0,1],[1,0,1,0]]
# Explanation: First reverse each row:
# [[0,0,1,1],[1,0,0,1],[1,1,1,0],[0,1,0,1]].
# Then invert the image: [[1,1,0,0],[0,1,1,0],[0,0,0,1],[1,0,1,0]]
#
# Constraints:
#
# n == image.length
#
# n == image[i].length
#
# 1 <= n <= 20
#
# images[i][j] is either 0 or 1.
#

# @lc code=start

from typing import List


class Solution:
    def flipAndInvertImage(self, image: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        For each row: reverse then invert bits (0↔1). Can do in one pass with
        two pointers swapping and XOR 1.

        Algorithm:
        - For each row, two pointers L,R: swap and invert both (careful mid).

        Complexity: O(m*n) time, O(1) extra space.
        """
        for row in image:
            l, r = 0, len(row) - 1
            while l <= r:
                row[l], row[r] = row[r] ^ 1, row[l] ^ 1
                l += 1
                r -= 1
        return image

    def flipAndInvertImage_builtin(self, image: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Clearer two-step: reverse each row, then invert every bit.

        Algorithm:
        - row[::-1] then [1-x for x in row] per row.

        Complexity: O(m*n) time, O(n) temp per row.
        """
        return [[1 - x for x in reversed(row)] for row in image]
# @lc code=end
