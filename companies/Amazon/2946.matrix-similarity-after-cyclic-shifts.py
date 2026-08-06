#
# @lc app=leetcode id=2946 lang=python3
#
# [2946] Matrix Similarity After Cyclic Shifts
#
# https://leetcode.com/problems/matrix-similarity-after-cyclic-shifts/description/
#
# algorithms
# Easy (74.43%)
# Likes:    478
# Dislikes: 92
# Total Accepted:    133.2K
# Total Submissions: 179K
# Testcase Example:  "[[1,2,3],[4,5,6],[7,8,9]]\n4"
#
#
# You are given an m x n integer matrix mat and an integer k. The matrix
# rows are 0-indexed.
#
# The following proccess happens k times:
#
# Even-indexed rows (0, 2, 4, ...) are cyclically shifted to the left.
#
# Odd-indexed rows (1, 3, 5, ...) are cyclically shifted to the right.
#
# Return true if the final modified matrix after k steps is identical to
# the original matrix, and false otherwise.
#
# Example 1:
#
# Input: mat = [[1,2,3],[4,5,6],[7,8,9]], k = 4
#
# Output: false
#
# Explanation:
#
# In each step left shift is applied to rows 0 and 2 (even indices), and
# right shift to row 1 (odd index).
#
# Example 2:
#
# Input: mat = [[1,2,1,2],[5,5,5,5],[6,3,6,3]], k = 2
#
# Output: true
#
# Explanation:
#
# Example 3:
#
# Input: mat = [[2,2],[2,2]], k = 3
#
# Output: true
#
# Explanation:
#
# As all the values are equal in the matrix, even after performing cyclic
# shifts the matrix will remain the same.
#
# Constraints:
#
# 1 <= mat.length <= 25
#
# 1 <= mat[i].length <= 25
#
# 1 <= mat[i][j] <= 25
#
# 1 <= k <= 50
#

# @lc code=start
from typing import List


class Solution:
    def areSimilar(self, mat: List[List[int]], k: int) -> bool:
        """
        Interview explanation:
        Even rows shift left by k, odd rows shift right by k; check identity.

        Algorithm:
        - Effective shift is k % n (row length). Compare each row to its
          cyclically shifted version.

        Complexity: O(m*n) time, O(1) extra.
        """
        if not mat or not mat[0]:
            return True
        cols = len(mat[0])
        k %= cols
        for i, row in enumerate(mat):
            if i % 2 == 0:
                # left shift by k equals original iff row[j] == row[(j+k)%cols]
                if row != row[k:] + row[:k]:
                    return False
            else:
                # right shift by k
                if row != row[-k:] + row[:-k] if k else row:
                    return False
        return True

    def areSimilar_index(self, mat: List[List[int]], k: int) -> bool:
        """
        Interview explanation:
        Alternate index-wise comparison without building new rows.

        Algorithm:
        - For even rows check mat[i][j] == mat[i][(j+k)%n]; odd: (j-k)%n.

        Complexity: O(m*n) time, O(1) space.
        """
        cols = len(mat[0])
        k %= cols
        for i, row in enumerate(mat):
            for j, v in enumerate(row):
                src = (j + k) % cols if i % 2 == 0 else (j - k) % cols
                if v != row[src]:
                    return False
        return True
# @lc code=end

