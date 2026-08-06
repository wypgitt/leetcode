#
# @lc app=leetcode id=118 lang=python3
#
# [118] Pascal's Triangle
#
# https://leetcode.com/problems/pascals-triangle/description/
#
# algorithms
# Easy (79.26%)
# Likes:    15138
# Dislikes: 573
# Total Accepted:    2.8M
# Total Submissions: 3.5M
# Testcase Example:  "5"
#
# Given an integer numRows, return the first numRows of Pascal's triangle.
#
# In Pascal's triangle, each number is the sum of the two numbers directly
# above it as shown:
#
# Example 1:
#
# Input: numRows = 5
# Output: [[1],[1,1],[1,2,1],[1,3,3,1],[1,4,6,4,1]]
#
# Example 2:
#
# Input: numRows = 1
# Output: [[1]]
#
# Constraints:
#
# 1 <= numRows <= 30
#

# @lc code=start
from typing import List
class Solution:
    def generate(self, numRows: int) -> List[List[int]]:
        """
        Interview explanation:
        Build Pascal's triangle row by row. Each interior value is the sum of
        the two values above it from the previous row.

        Algorithm:
        - Start with [[1]].
        - For each next row of length i+1, ends are 1; middle j is
          prev[j-1] + prev[j].

        Complexity: O(numRows^2) time and space (output size).
        """
        triangle: List[List[int]] = [[1]]
        for i in range(1, numRows):
            prev = triangle[-1]
            row = [1]
            for j in range(1, i):
                row.append(prev[j - 1] + prev[j])
            row.append(1)
            triangle.append(row)
        return triangle
# @lc code=end
