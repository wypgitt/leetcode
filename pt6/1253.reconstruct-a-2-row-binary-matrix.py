#
# @lc app=leetcode id=1253 lang=python3
#
# [1253] Reconstruct a 2-Row Binary Matrix
#
# https://leetcode.com/problems/reconstruct-a-2-row-binary-matrix/description/
#
# algorithms
# Medium (48.93%)
# Likes:    484
# Dislikes: 35
# Total Accepted:    34.7K
# Total Submissions: 70.9K
# Testcase Example:  '2\n1\n[1,1,1]'
#
# Given the following details of a matrix with n columns and 2 rows :
# 
# 
# The matrix is a binary matrix, which means each element in the matrix can be
# 0 or 1.
# The sum of elements of the 0-th(upper) row is given as upper.
# The sum of elements of the 1-st(lower) row is given as lower.
# The sum of elements in the i-th column(0-indexed) is colsum[i], where colsum
# is given as an integer array with length n.
# 
# 
# Your task is to reconstruct the matrix with upper, lower and colsum.
# 
# Return it as a 2-D integer array.
# 
# If there are more than one valid solution, any of them will be accepted.
# 
# If no valid solution exists, return an empty 2-D array.
# 
# 
# Example 1:
# 
# 
# Input: upper = 2, lower = 1, colsum = [1,1,1]
# Output: [[1,1,0],[0,0,1]]
# Explanation: [[1,0,1],[0,1,0]], and [[0,1,1],[1,0,0]] are also correct
# answers.
# 
# 
# Example 2:
# 
# 
# Input: upper = 2, lower = 3, colsum = [2,2,1,1]
# Output: []
# 
# 
# Example 3:
# 
# 
# Input: upper = 5, lower = 5, colsum = [2,1,2,0,1,0,1,2,0,1]
# Output: [[1,1,1,0,1,0,0,1,0,0],[1,0,1,0,0,0,1,1,0,1]]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= colsum.length <= 10^5
# 0 <= upper, lower <= colsum.length
# 0 <= colsum[i] <= 2
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def reconstructMatrix(self, upper: int, lower: int, colsum: List[int]) -> List[List[int]]:
        top = [0] * len(colsum)
        bottom = [0] * len(colsum)

        for i, col in enumerate(colsum):
            if col == 2:
                top[i] = bottom[i] = 1
                upper -= 1
                lower -= 1

        if upper < 0 or lower < 0:
            return []

        for i, col in enumerate(colsum):
            if col == 1:
                if upper > 0:
                    top[i] = 1
                    upper -= 1
                elif lower > 0:
                    bottom[i] = 1
                    lower -= 1
                else:
                    return []

        return [top, bottom] if upper == 0 and lower == 0 else []
# @lc code=end

# Explanation
# -----------
# Columns with colsum = 2 are forced: both rows must contain 1 there. Assign
# those first and reduce upper/lower. Columns with colsum = 1 can go to either
# row, so fill the upper row while it still needs ones, then the lower row.
#
# This greedy choice is safe because all remaining colsum = 1 columns are
# interchangeable; only the remaining row sums matter.
#
# Edge cases: forced 2-columns can exceed upper or lower; not enough 1-columns
# to satisfy a row; if upper and lower are not both zero at the end, no valid
# matrix exists.
#
# Time complexity: O(n).
# Space complexity: O(n) for the two output rows.
