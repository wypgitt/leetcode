#
# @lc app=leetcode id=1738 lang=python3
#
# [1738] Find Kth Largest XOR Coordinate Value
#
# https://leetcode.com/problems/find-kth-largest-xor-coordinate-value/description/
#
# algorithms
# Medium (64.5%)
# Likes:    542
# Dislikes: 86
# Total Accepted:    31.8K
# Total Submissions: 49.2K
# Testcase Example:  "[[5,2],[1,6]]"
#
# You are given a 2D matrix of size m x n, consisting of non-negative integers.
# You are also given an integer k.
#
# The value of coordinate (a, b) of the matrix is the XOR of all matrix[i][j]
# where 0 <= i <= a < m and 0 <= j <= b < n (0-indexed).
#
# Find the k^th largest value (1-indexed) of all the coordinates of matrix.
#
# Example 1:
#
# Input: matrix = [[5,2],[1,6]], k = 1
# Output: 7
# Explanation: The value of coordinate (0,1) is 5 XOR 2 = 7, which is the
# largest value.
#
# Example 2:
#
# Input: matrix = [[5,2],[1,6]], k = 2
# Output: 5
# Explanation: The value of coordinate (0,0) is 5 = 5, which is the 2nd largest
# value.
#
# Example 3:
#
# Input: matrix = [[5,2],[1,6]], k = 3
# Output: 4
# Explanation: The value of coordinate (1,0) is 5 XOR 1 = 4, which is the 3rd
# largest value.
#
# Constraints:
#
# m == matrix.length
#
# n == matrix[i].length
#
# 1 <= m, n <= 1000
#
# 0 <= matrix[i][j] <= 10^6
#
# 1 <= k <= m * n
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def kthLargestValue(self, matrix: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        2D prefix XOR of the top-left submatrix; return the k-th largest value
        among all cells of that prefix matrix.

        Algorithm:
        - pref[i][j] = m[i][j] ^ pref[i-1][j] ^ pref[i][j-1] ^ pref[i-1][j-1]
        - Collect values; sort descending; return [k-1].

        Complexity: O(mn log(mn)) time, O(mn) space.
        """
        m, n = len(matrix), len(matrix[0])
        pref = [[0] * n for _ in range(m)]
        vals = []
        for i in range(m):
            for j in range(n):
                v = matrix[i][j]
                if i:
                    v ^= pref[i - 1][j]
                if j:
                    v ^= pref[i][j - 1]
                if i and j:
                    v ^= pref[i - 1][j - 1]
                pref[i][j] = v
                vals.append(v)
        vals.sort(reverse=True)
        return vals[k - 1]

    def kthLargestValue_heap(self, matrix: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Alternate: maintain a size-k min-heap of the largest values seen.

        Algorithm:
        - Same prefix XOR; push/replace into heap of size k; return heap[0].

        Complexity: O(mn log k) time, O(mn) space.
        """
        m, n = len(matrix), len(matrix[0])
        pref = [[0] * n for _ in range(m)]
        h = []
        for i in range(m):
            for j in range(n):
                v = matrix[i][j]
                if i:
                    v ^= pref[i - 1][j]
                if j:
                    v ^= pref[i][j - 1]
                if i and j:
                    v ^= pref[i - 1][j - 1]
                pref[i][j] = v
                if len(h) < k:
                    heapq.heappush(h, v)
                elif v > h[0]:
                    heapq.heapreplace(h, v)
        return h[0]
# @lc code=end
