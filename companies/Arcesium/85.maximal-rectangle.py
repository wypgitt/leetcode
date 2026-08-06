#
# @lc app=leetcode id=85 lang=python3
#
# [85] Maximal Rectangle
#
# https://leetcode.com/problems/maximal-rectangle/description/
#
# algorithms
# Hard (59.49%)
# Likes:    12226
# Dislikes: 228
# Total Accepted:    850K
# Total Submissions: 1.4M
# Testcase Example:  "[[\"1\",\"0\",\"1\",\"0\",\"0\"],[\"1\",\"0\",\"1\",\"1\",\"1\"],[\"1\",\"1\",\"1\",\"1\",\"1\"],[\"1\",\"0\",\"0\",\"1\",\"0\"]]"
#
# Given a rows x cols binary matrix filled with 0's and 1's, find the largest
# rectangle containing only 1's and return its area.
#
# Example 1:
#
# Input: matrix =
# [["1","0","1","0","0"],["1","0","1","1","1"],["1","1","1","1","1"],["1","0","0","1","0"]]
# Output: 6
# Explanation: The maximal rectangle is shown in the above picture.
#
# Example 2:
#
# Input: matrix = [["0"]]
# Output: 0
#
# Example 3:
#
# Input: matrix = [["1"]]
# Output: 1
#
# Constraints:
#
# rows == matrix.length
#
# cols == matrix[i].length
#
# 1 <= rows, cols <= 200
#
# matrix[i][j] is '0' or '1'.
#

# @lc code=start
from typing import List


class Solution:
    def maximalRectangle(self, matrix: List[List[str]]) -> int:
        """
        Interview explanation:
        Treat each row as the base of a histogram: heights[j] = consecutive
        '1's ending at this row in column j. Largest rectangle in that
        histogram (monotonic stack) is a candidate; take the global max.

        Algorithm:
        - Initialize heights of length cols to 0.
        - For each row, update heights (reset on '0'), then run histogram
          largest-rectangle with a sentinel 0.

        Complexity: O(rows * cols) time, O(cols) space.
        """
        if not matrix or not matrix[0]:
            return 0

        cols = len(matrix[0])
        heights = [0] * (cols + 1)
        best = 0

        for row in matrix:
            for j in range(cols):
                heights[j] = heights[j] + 1 if row[j] == "1" else 0

            stack = [-1]
            for i, h in enumerate(heights):
                while stack[-1] != -1 and heights[stack[-1]] > h:
                    height = heights[stack.pop()]
                    width = i - stack[-1] - 1
                    best = max(best, height * width)
                stack.append(i)

        return best
# @lc code=end
