#
# @lc app=leetcode id=2718 lang=python3
#
# [2718] Sum of Matrix After Queries
#
# https://leetcode.com/problems/sum-of-matrix-after-queries/description/
#
# algorithms
# Medium (32.35%)
# Likes:    737
# Dislikes: 28
# Total Accepted:    25.6K
# Total Submissions: 79.2K
# Testcase Example:  "3\n[[0,0,1],[1,2,2],[0,2,3],[1,0,4]]"
#
# You are given an integer n and a 0-indexed 2D array queries where queries[i] =
# [type_i, index_i, val_i].
#
# Initially, there is a 0-indexed n x n matrix filled with 0's. For each query,
# you must apply one of the following changes:
#
#
# if type_i == 0, set the values in the row with index_i to val_i, overwriting
# any previous values.
#
#
# if type_i == 1, set the values in the column with index_i to val_i,
# overwriting any previous values.
#
# Return the sum of integers in the matrix after all queries are applied.
#
#
#
# Example 1:
#
# Input: n = 3, queries = [[0,0,1],[1,2,2],[0,2,3],[1,0,4]]
# Output: 23
# Explanation: The image above describes the matrix after each query. The sum of
# the matrix after all queries are applied is 23.
#
# Example 2:
#
# Input: n = 3, queries = [[0,0,4],[0,1,2],[1,0,1],[0,2,3],[1,2,1]]
# Output: 17
# Explanation: The image above describes the matrix after each query. The sum of
# the matrix after all queries are applied is 17.
#
#
#
# Constraints:
#
#
# 1 <= n <= 10^4
#
#
# 1 <= queries.length <= 5 * 10^4
#
#
# queries[i].length == 3
#
#
# 0 <= type_i <= 1
#
#
# 0 <= index_i < n
#
#
# 0 <= val_i <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def matrixSumQueries(self, n: int, queries: List[List[int]]) -> int:
        """
        Interview explanation:
        Start n×n zeros; queries set entire row or column to val. Return final matrix sum.

        Algorithm:
        - Process queries reverse: each cell written by last query wins. Track seen rows/cols;
          when setting a new row, add val * (n - seen_cols), similarly for cols.

        Complexity: O(q) time, O(n) space.
        """
        seen_row = [False] * n
        seen_col = [False] * n
        rows = cols = 0
        ans = 0
        for typ, idx, val in reversed(queries):
            if typ == 0:
                if seen_row[idx]:
                    continue
                seen_row[idx] = True
                rows += 1
                ans += val * (n - cols)
            else:
                if seen_col[idx]:
                    continue
                seen_col[idx] = True
                cols += 1
                ans += val * (n - rows)
        return ans
# @lc code=end
