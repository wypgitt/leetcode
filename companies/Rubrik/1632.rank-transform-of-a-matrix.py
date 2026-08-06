#
# @lc app=leetcode id=1632 lang=python3
#
# [1632] Rank Transform of a Matrix
#
# https://leetcode.com/problems/rank-transform-of-a-matrix/description/
#
# algorithms
# Hard (42.49%)
# Likes:    949
# Dislikes: 60
# Total Accepted:    28.4K
# Total Submissions: 66.9K
# Testcase Example:  "[[1,2],[3,4]]"
#
# Given an m x n matrix, return a new matrix answer where answer[row][col] is
# the rank of matrix[row][col].
#
# The rank is an integer that represents how large an element is compared to
# other elements. It is calculated using the following rules:
#
# The rank is an integer starting from 1.
#
# If two elements p and q are in the same row or column, then:
#
# If p < q then rank(p) < rank(q)
#
# If p == q then rank(p) == rank(q)
#
# If p > q then rank(p) > rank(q)
#
# The rank should be as small as possible.
#
# The test cases are generated so that answer is unique under the given rules.
#
# Example 1:
#
# Input: matrix = [[1,2],[3,4]]
# Output: [[1,2],[2,3]]
# Explanation:
# The rank of matrix[0][0] is 1 because it is the smallest integer in its row
# and column.
# The rank of matrix[0][1] is 2 because matrix[0][1] > matrix[0][0] and
# matrix[0][0] is rank 1.
# The rank of matrix[1][0] is 2 because matrix[1][0] > matrix[0][0] and
# matrix[0][0] is rank 1.
# The rank of matrix[1][1] is 3 because matrix[1][1] > matrix[0][1],
# matrix[1][1] > matrix[1][0], and both matrix[0][1] and matrix[1][0] are rank
# 2.
#
# Example 2:
#
# Input: matrix = [[7,7],[7,7]]
# Output: [[1,1],[1,1]]
#
# Example 3:
#
# Input: matrix = [[20,-21,14],[-19,4,19],[22,-47,24],[-19,4,19]]
# Output: [[4,2,3],[1,3,4],[5,1,6],[1,3,4]]
#
# Constraints:
#
# m == matrix.length
#
# n == matrix[i].length
#
# 1 <= m, n <= 500
#
# -10^9 <= matrix[row][col] <= 10^9
#

# @lc code=start
from typing import List
from collections import defaultdict


class Solution:
    def matrixRankTransform(self, matrix: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Rank of cell > ranks of smaller values in same row/col; equal values that
        share row/col get same rank. Process values ascending; UF for equal group.

        Algorithm (sort + Union-Find):
        - Group positions by value. For each value: UF union same-row/col positions;
          rank = 1+max(rowMax[r], colMax[c]) over group; update row/col maxima.

        Complexity: O(mn log(mn) α) time, O(mn) space.
        """
        m, n = len(matrix), len(matrix[0])
        pos = defaultdict(list)
        for i in range(m):
            for j in range(n):
                pos[matrix[i][j]].append((i, j))
        row_max = [0] * m
        col_max = [0] * n
        ans = [[0] * n for _ in range(m)]

        for val in sorted(pos):
            parent = {}

            def find(x):
                parent.setdefault(x, x)
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x

            def union(a, b):
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[rb] = ra

            cells = pos[val]
            for i, j in cells:
                # union row i with col ~j using distinct keys
                union(("r", i), ("c", j))
            group_rank = {}
            for i, j in cells:
                root = find(("r", i))
                group_rank[root] = max(
                    group_rank.get(root, 0), row_max[i], col_max[j]
                )
            for i, j in cells:
                rnk = group_rank[find(("r", i))] + 1
                ans[i][j] = rnk
                row_max[i] = max(row_max[i], rnk)
                col_max[j] = max(col_max[j], rnk)
        return ans

    def matrixRankTransform_naive_groups(self, matrix: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        Alternate clarity version of the same pipeline: group by value, union
        positions sharing a row or column via explicit parent array on cell ids.

        Algorithm (value groups + UF on cells):
        - Sort unique values; for each value's cells, UF if same row/col;
          rank[group]=1+max row/col max among members; write and update maxima.

        Complexity: O(mn log(mn) α) time, O(mn) space.
        """
        m, n = len(matrix), len(matrix[0])
        pos = defaultdict(list)
        for i in range(m):
            for j in range(n):
                pos[matrix[i][j]].append((i, j))
        row_max = [0] * m
        col_max = [0] * n
        ans = [[0] * n for _ in range(m)]
        for val in sorted(pos):
            cells = pos[val]
            k = len(cells)
            parent = list(range(k))

            def find(x: int) -> int:
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x

            row_idx = {}
            col_idx = {}
            for t, (i, j) in enumerate(cells):
                if i in row_idx:
                    parent[find(t)] = find(row_idx[i])
                else:
                    row_idx[i] = t
                if j in col_idx:
                    parent[find(t)] = find(col_idx[j])
                else:
                    col_idx[j] = t
            best = {}
            for t, (i, j) in enumerate(cells):
                r = find(t)
                best[r] = max(best.get(r, 0), row_max[i], col_max[j])
            for t, (i, j) in enumerate(cells):
                rnk = best[find(t)] + 1
                ans[i][j] = rnk
                row_max[i] = max(row_max[i], rnk)
                col_max[j] = max(col_max[j], rnk)
        return ans
# @lc code=end
