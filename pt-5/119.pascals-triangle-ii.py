#
# @lc app=leetcode id=119 lang=python3
#
# [119] Pascal's Triangle II
#
# https://leetcode.com/problems/pascals-triangle-ii/description/
#
# algorithms
# Easy (67.83%)
# Likes:    5368
# Dislikes: 372
# Total Accepted:    1.3M
# Total Submissions: 1.9M
# Testcase Example:  "3"
#
# Given an integer rowIndex, return the rowIndex^th (0-indexed) row of the
# Pascal's triangle.
#
# In Pascal's triangle, each number is the sum of the two numbers directly
# above it as shown:
#
# Example 1:
#
# Input: rowIndex = 3
# Output: [1,3,3,1]
#
# Example 2:
#
# Input: rowIndex = 0
# Output: [1]
#
# Example 3:
#
# Input: rowIndex = 1
# Output: [1,1]
#
# Constraints:
#
# 0 <= rowIndex <= 33
#
# Follow up: Could you optimize your algorithm to use only O(rowIndex) extra
# space?
#

# @lc code=start
from typing import List
class Solution:
    def getRow(self, rowIndex: int) -> List[int]:
        """
        Interview explanation:
        Only one row is needed, so update an array in place from right to left.
        Updating right-to-left preserves still-needed previous values when
        computing row[j] += row[j-1].

        Algorithm:
        - Start with [1].
        - For each new row length, append 1 then for j from end-1 down to 1:
          row[j] += row[j-1].

        Complexity: O(rowIndex^2) time, O(rowIndex) space.
        """
        row = [1]
        for _ in range(rowIndex):
            row.append(1)
            for j in range(len(row) - 2, 0, -1):
                row[j] += row[j - 1]
        return row
# @lc code=end
