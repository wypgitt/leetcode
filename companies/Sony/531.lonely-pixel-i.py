#
# @lc app=leetcode id=531 lang=python3
#
# [531] Lonely Pixel I
#
# https://leetcode.com/problems/lonely-pixel-i/description/
#
# algorithms
# Medium (62.72%)
# Likes:    454
# Dislikes: 41
# Total Accepted:    48.7K
# Total Submissions: 77.7K
# Testcase Example:  "[[\"W\",\"W\",\"B\"],[\"W\",\"B\",\"W\"],[\"B\",\"W\",\"W\"]]"
#
#
# Given an m x n picture consisting of black 'B' and white 'W' pixels,
# return the number of black lonely pixels.
#
# A black lonely pixel is a character 'B' that located at a specific
# position where the same row and same column don't have any other black
# pixels.
#
# Example 1:
#
# Input: picture = [["W","W","B"],["W","B","W"],["B","W","W"]]
# Output: 3
# Explanation: All the three 'B's are black lonely pixels.
#
# Example 2:
#
# Input: picture = [["B","B","B"],["B","B","W"],["B","B","B"]]
# Output: 0
#
# Constraints:
#
# m == picture.length
#
# n == picture[i].length
#
# 1 <= m, n <= 500
#
# picture[i][j] is 'W' or 'B'.
#
# @lc code=start
from typing import List
class Solution:
    def findLonelyPixel(self, picture: List[List[str]]) -> int:
        """
        Interview explanation:
        A black pixel 'B' is lonely if it is the only 'B' in its row and column.
        Count 'B's per row and column, then count cells that are 'B' with both
        counts equal to 1.

        Algorithm:
        - First pass: row_count[i], col_count[j].
        - Second pass: count picture[i][j] == 'B' with row_count[i] == col_count[j] == 1.

        Complexity: O(m*n) time, O(m+n) space.
        """
        if not picture or not picture[0]:
            return 0
        m, n = len(picture), len(picture[0])
        row_count = [0] * m
        col_count = [0] * n
        for i in range(m):
            for j in range(n):
                if picture[i][j] == "B":
                    row_count[i] += 1
                    col_count[j] += 1
        ans = 0
        for i in range(m):
            for j in range(n):
                if picture[i][j] == "B" and row_count[i] == 1 and col_count[j] == 1:
                    ans += 1
        return ans
# @lc code=end

