#
# @lc app=leetcode id=1072 lang=python3
#
# [1072] Flip Columns For Maximum Number of Equal Rows
#
# https://leetcode.com/problems/flip-columns-for-maximum-number-of-equal-rows/description/
#
# algorithms
# Medium (78.49%)
# Likes:    1348
# Dislikes: 131
# Total Accepted:    120K
# Total Submissions: 153K
# Testcase Example:  "[[0,1],[1,1]]"
#
# You are given an m x n binary matrix matrix.
#
# You can choose any number of columns in the matrix and flip every cell in
# that column (i.e., Change the value of the cell from 0 to 1 or vice versa).
#
# Return the maximum number of rows that have all values equal after some
# number of flips.
#
# Example 1:
#
# Input: matrix = [[0,1],[1,1]]
# Output: 1
# Explanation: After flipping no values, 1 row has all values equal.
#
# Example 2:
#
# Input: matrix = [[0,1],[1,0]]
# Output: 2
# Explanation: After flipping values in the first column, both rows have equal
# values.
#
# Example 3:
#
# Input: matrix = [[0,0,0],[0,0,1],[1,1,0]]
# Output: 2
# Explanation: After flipping values in the first two columns, the last two
# rows have equal values.
#
# Constraints:
#
# m == matrix.length
#
# n == matrix[i].length
#
# 1 <= m, n <= 300
#
# matrix[i][j] is either 0 or 1.
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def maxEqualRowsAfterFlips(self, matrix: List[List[int]]) -> int:
        """
        Interview explanation:
        Flipping columns makes two rows equal iff they have the same pattern
        or complementary pattern. Normalize each row by XOR with its first bit
        so patterns and complements map to the same key; answer is the most
        frequent key.

        Algorithm (pattern frequency):
        - For each row, pattern = tuple(x ^ row[0] for x in row).
        - Return max frequency of patterns.

        Complexity: O(m·n) time, O(m·n) space.
        """
        cnt = Counter()
        for row in matrix:
            pattern = tuple(x ^ row[0] for x in row)
            cnt[pattern] += 1
        return max(cnt.values())
# @lc code=end
