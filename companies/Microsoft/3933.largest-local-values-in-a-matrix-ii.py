#
# @lc app=leetcode id=3933 lang=python3
#
# [3933] Largest Local Values in a Matrix II
#
# https://leetcode.com/problems/largest-local-values-in-a-matrix-ii/description/
#
# algorithms
# Medium (18.78%)
# Likes:    64
# Dislikes: 10
# Total Accepted:    9.2K
# Total Submissions: 49.2K
# Testcase Example:  "[[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,2,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]"
#
#
# You are given an n x m integer matrix matrix containing non-negative
# integers.
#
# A non-zero cell (row, col) checks the cells near it as follows:
#
# Let x = matrix[row][col].
#
# Consider every cell within x rows and x columns of (row, col).
#
# Ignore cells that are outside the matrix.
#
# Ignore the cells where both the row distance and column distance are
# exactly x.
#
# The cell (row, col) is a local maximum if it is non-zero and no
# considered cell has a value greater than x.
#
# Return an integer denoting the number of local maximums in matrix.
#
# ​​​​​​​Example 1:
#
# Input: matrix =
# [[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,2,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]
#
# Output: 1
#
# ​​​​​​​​​​​​​​​​​​​​​
#
# Explanation:
#
# For the non-zero cell (3, 3), x = matrix[3][3] = 2.
#
# The highlighted cells are the considered cells within x rows and x
# columns of (3, 3).
#
# The four cells with both row and column distances equal to x = 2 are
# ignored.
#
# No considered cell has a value greater than 2, so (3, 3) is a local
# maximum.
#
# There are no other non-zero cells, so the answer is 1.
#
# Example 2:
#
# Input: matrix = [[1,2],[3,4]]
#
# Output: 1
#
# Explanation:
#
# Only the cell with value 4 is a local maximum. Every other non-zero cell
# considers a cell with a greater value.
#
# Example 3:
#
# Input: matrix = [[1,0,1],[0,1,0],[1,0,1]]
#
# Output: 5
#
# Explanation:
#
# For a cell with value 1, the considered cells are the cell itself and
# its 4-directionally adjacent cells that are inside the matrix.
#
# Each of the five cells with value 1 only considers cells with values 0
# or 1, so all five of them are local maximums.
#
# Example 4:
#
# Input: matrix = [[1,1],[1,1]]
#
# Output: 4
#
# Explanation:
#
# All cells have the same value. Therefore, no cell considers another cell
# with a greater value, so all 4 cells are local maximums.
#
# Constraints:
#
# 1 <= n == matrix.length <= 200
#
# 1 <= m == matrix[i].length <= 200
#
# 0 <= matrix[i][j] <= 200
#

# @lc code=start

class Solution:
    def countLocalMaximums(self, matrix: list[list[int]]) -> int:
        """
        Interview explanation:
        A non-zero cell x is a local maximum if no cell in its x-radius square
        (excluding the four strict corners at distance x,x) exceeds x.
        Use per-row sparse tables for fast row-range maxima.

        Algorithm:
        - Build 1D sparse tables on each row for O(1) range max.
        - For each non-zero (r,c) with value x, take max over the clipped square
          rows; on the |dr|==x boundary rows, skip |dc|==x corners.
        - Count cells whose region max is <= x.

        Complexity: O(n*m*n) time, O(n*m log m) space.
        """
        n, m = len(matrix), len(matrix[0])
        LOG = max(1, m.bit_length())
        st = [[[0] * m for _ in range(n)] for _ in range(LOG)]
        for i in range(n):
            for j in range(m):
                st[0][i][j] = matrix[i][j]
        for k in range(1, LOG):
            half = 1 << (k - 1)
            span = 1 << k
            for i in range(n):
                rowk, rowp = st[k][i], st[k - 1][i]
                for j in range(m - span + 1):
                    rowk[j] = max(rowp[j], rowp[j + half])

        def row_max(i: int, L: int, R: int) -> int:
            if L > R:
                return -1
            length = R - L + 1
            k = length.bit_length() - 1
            return max(st[k][i][L], st[k][i][R - (1 << k) + 1])

        ans = 0
        for r in range(n):
            for c in range(m):
                x = matrix[r][c]
                if x == 0:
                    continue
                r1, r2 = max(0, r - x), min(n - 1, r + x)
                c1, c2 = max(0, c - x), min(m - 1, c + x)
                mx = -1
                for i in range(r1, r2 + 1):
                    if abs(i - r) == x:
                        for j in range(c1, c2 + 1):
                            if abs(j - c) == x:
                                continue
                            if matrix[i][j] > mx:
                                mx = matrix[i][j]
                    else:
                        mx = max(mx, row_max(i, c1, c2))
                if mx <= x:
                    ans += 1
        return ans
# @lc code=end
