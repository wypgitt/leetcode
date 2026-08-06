#
# @lc app=leetcode id=1253 lang=python3
#
# [1253] Reconstruct a 2-Row Binary Matrix
#
# https://leetcode.com/problems/reconstruct-a-2-row-binary-matrix/description/
#
# algorithms
# Medium (49.16%)
# Likes:    485
# Dislikes: 35
# Total Accepted:    35.5K
# Total Submissions: 72.3K
# Testcase Example:  "2"
#
# Given the following details of a matrix with n columns and 2 rows :
#
# The matrix is a binary matrix, which means each element in the matrix can be
# 0 or 1.
#
# The sum of elements of the 0-th(upper) row is given as upper.
#
# The sum of elements of the 1-st(lower) row is given as lower.
#
# The sum of elements in the i-th column(0-indexed) is colsum[i], where colsum
# is given as an integer array with length n.
#
# Your task is to reconstruct the matrix with upper, lower and colsum.
#
# Return it as a 2-D integer array.
#
# If there are more than one valid solution, any of them will be accepted.
#
# If no valid solution exists, return an empty 2-D array.
#
# Example 1:
#
# Input: upper = 2, lower = 1, colsum = [1,1,1]
# Output: [[1,1,0],[0,0,1]]
# Explanation: [[1,0,1],[0,1,0]], and [[0,1,1],[1,0,0]] are also correct
# answers.
#
# Example 2:
#
# Input: upper = 2, lower = 3, colsum = [2,2,1,1]
# Output: []
#
# Example 3:
#
# Input: upper = 5, lower = 5, colsum = [2,1,2,0,1,0,1,2,0,1]
# Output: [[1,1,1,0,1,0,0,1,0,0],[1,0,1,0,0,0,1,1,0,1]]
#
# Constraints:
#
# 1 <= colsum.length <= 10^5
#
# 0 <= upper, lower <= colsum.length
#
# 0 <= colsum[i] <= 2
#

# @lc code=start

from typing import List


class Solution:
    def reconstructMatrix(
        self, upper: int, lower: int, colsum: List[int]
    ) -> List[List[int]]:
        """
        Interview explanation:
        Build 2-row 0/1 matrix with given row sums and column sums. Columns
        with sum 2 must be [1,1]; sum 0 must be [0,0]; sum 1 goes to the row
        that still has remaining quota (prefer upper if upper remaining >=
        lower remaining, or greedily assign to whichever still needs).

        Algorithm:
        - If sum(colsum)!=upper+lower: impossible [].
        - Place all 2's first subtracting from both upper/lower.
        - For sum-1 columns: if upper>0 put in top else bottom; fail if both 0.
        - Final upper/lower must be 0.

        Complexity: O(n) time, O(n) space.
        """
        n = len(colsum)
        if sum(colsum) != upper + lower:
            return []
        res = [[0] * n for _ in range(2)]
        for j, s in enumerate(colsum):
            if s == 2:
                res[0][j] = res[1][j] = 1
                upper -= 1
                lower -= 1
        if upper < 0 or lower < 0:
            return []
        for j, s in enumerate(colsum):
            if s == 1:
                if upper > 0:
                    res[0][j] = 1
                    upper -= 1
                elif lower > 0:
                    res[1][j] = 1
                    lower -= 1
                else:
                    return []
        if upper or lower:
            return []
        return res
# @lc code=end
