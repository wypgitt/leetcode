#
# @lc app=leetcode id=1337 lang=python3
#
# [1337] The K Weakest Rows in a Matrix
#
# https://leetcode.com/problems/the-k-weakest-rows-in-a-matrix/description/
#
# algorithms
# Easy (74.46%)
# Likes:    4368
# Dislikes: 242
# Total Accepted:    432K
# Total Submissions: 580K
# Testcase Example:  "[[1,1,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,1,0,0,0],[1,1,1,1,1]]"
#
# You are given an m x n binary matrix mat of 1's (representing soldiers) and
# 0's (representing civilians). The soldiers are positioned in front of the
# civilians. That is, all the 1's will appear to the left of all the 0's in
# each row.
#
# A row i is weaker than a row j if one of the following is true:
#
# The number of soldiers in row i is less than the number of soldiers in row j.
#
# Both rows have the same number of soldiers and i < j.
#
# Return the indices of the k weakest rows in the matrix ordered from weakest
# to strongest.
#
# Example 1:
#
# Input: mat =
# [[1,1,0,0,0],
# [1,1,1,1,0],
# [1,0,0,0,0],
# [1,1,0,0,0],
# [1,1,1,1,1]],
# k = 3
# Output: [2,0,3]
# Explanation:
# The number of soldiers in each row is:
# - Row 0: 2
# - Row 1: 4
# - Row 2: 1
# - Row 3: 2
# - Row 4: 5
# The rows ordered from weakest to strongest are [2,0,3,1,4].
#
# Example 2:
#
# Input: mat =
# [[1,0,0,0],
# [1,1,1,1],
# [1,0,0,0],
# [1,0,0,0]],
# k = 2
# Output: [0,2]
# Explanation:
# The number of soldiers in each row is:
# - Row 0: 1
# - Row 1: 4
# - Row 2: 1
# - Row 3: 1
# The rows ordered from weakest to strongest are [0,2,3,1].
#
# Constraints:
#
# m == mat.length
#
# n == mat[i].length
#
# 2 <= n, m <= 100
#
# 1 <= k <= m
#
# matrix[i][j] is either 0 or 1.
#

# @lc code=start
import heapq
from typing import List


class Solution:
    def kWeakestRows(self, mat: List[List[int]], k: int) -> List[int]:
        """
        Interview explanation:
        Weakness = number of 1s (soldiers) in a row (rows are sorted 1s then 0s).
        Return k weakest row indices; ties by smaller index. Binary search count
        ones per row + heap of size k.

        Algorithm (binary search + heap):
        - For each row bisect first 0; push (ones, idx) to max-heap of size k /
          or collect and sort.

        Complexity: O(m log n + m log k) time.
        """
        def ones(row: List[int]) -> int:
            lo, hi = 0, len(row)
            while lo < hi:
                mid = (lo + hi) // 2
                if row[mid] == 1:
                    lo = mid + 1
                else:
                    hi = mid
            return lo

        # max-heap of (-ones, -idx) wait we want weakest: min-heap by (ones, idx)
        strength = [(ones(row), i) for i, row in enumerate(mat)]
        return [i for _, i in heapq.nsmallest(k, strength)]

    def kWeakestRows_sort(self, mat: List[List[int]], k: int) -> List[int]:
        """
        Interview explanation:
        Alternate: sum each row (or bisect) and sort all by (ones, index).

        Algorithm:
        - strength list; sort; take first k indices.

        Complexity: O(m n + m log m) or O(m log n + m log m).
        """
        strength = [(sum(row), i) for i, row in enumerate(mat)]
        strength.sort()
        return [i for _, i in strength[:k]]
# @lc code=end

