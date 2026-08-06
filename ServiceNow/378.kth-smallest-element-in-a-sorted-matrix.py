#
# @lc app=leetcode id=378 lang=python3
#
# [378] Kth Smallest Element in a Sorted Matrix
#
# https://leetcode.com/problems/kth-smallest-element-in-a-sorted-matrix/description/
#
# algorithms
# Medium (64.91%)
# Likes:    10675
# Dislikes: 399
# Total Accepted:    834K
# Total Submissions: 1.3M
# Testcase Example:  "[[1,5,9],[10,11,13],[12,13,15]]"
#
# Given an n x n matrix where each of the rows and columns is sorted in
# ascending order, return the k^th smallest element in the matrix.
#
# Note that it is the k^th smallest element in the sorted order, not the k^th
# distinct element.
#
# You must find a solution with a memory complexity better than O(n^2).
#
# Example 1:
#
# Input: matrix = [[1,5,9],[10,11,13],[12,13,15]], k = 8
# Output: 13
# Explanation: The elements in the matrix are [1,5,9,10,11,12,13,13,15], and
# the 8^th smallest number is 13
#
# Example 2:
#
# Input: matrix = [[-5]], k = 1
# Output: -5
#
# Constraints:
#
# n == matrix.length == matrix[i].length
#
# 1 <= n <= 300
#
# -10^9 <= matrix[i][j] <= 10^9
#
# All the rows and columns of matrix are guaranteed to be sorted in
# non-decreasing order.
#
# 1 <= k <= n^2
#
# Follow up:
#
# Could you solve the problem with a constant memory (i.e., O(1) memory
# complexity)?
#
# Could you solve the problem in O(n) time complexity? The solution may be too
# advanced for an interview but you may find reading this paper fun.
#

# @lc code=start
import heapq
from typing import List


class Solution:
    def kthSmallest(self, matrix: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Primary: binary search on value. Count how many matrix entries are
        ≤ mid via staircase from bottom-left; adjust lo/hi until lo is the
        k-th smallest. O(1) extra memory (follow-up friendly).

        Algorithm:
        - lo, hi = matrix[0][0], matrix[-1][-1]
        - While lo < hi: mid = (lo+hi)//2; if count(≤mid) >= k: hi = mid
          else lo = mid + 1
        - count: start (n-1, 0); move up or right like Young tableau.

        Complexity: O(n log(max-min)) time, O(1) space.
        """
        n = len(matrix)
        lo, hi = matrix[0][0], matrix[-1][-1]

        def count_le(x: int) -> int:
            i, j = n - 1, 0
            cnt = 0
            while i >= 0 and j < n:
                if matrix[i][j] <= x:
                    cnt += i + 1
                    j += 1
                else:
                    i -= 1
            return cnt

        while lo < hi:
            mid = (lo + hi) // 2
            if count_le(mid) >= k:
                hi = mid
            else:
                lo = mid + 1
        return lo

    def kthSmallestHeap(self, matrix: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Alternate equally common: min-heap of row heads (or first column).
        Pop k times, pushing the next element in the same row — like merge
        of n sorted lists.

        Algorithm:
        - Seed heap with (matrix[i][0], i, 0) for each row.
        - Pop k-1 times; push (matrix[r][c+1], r, c+1) if in range.
        - Return final popped value.

        Complexity: O(k log n) time, O(n) space.
        """
        n = len(matrix)
        heap = [(matrix[i][0], i, 0) for i in range(n)]
        heapq.heapify(heap)
        for _ in range(k - 1):
            _, r, c = heapq.heappop(heap)
            if c + 1 < n:
                heapq.heappush(heap, (matrix[r][c + 1], r, c + 1))
        return heap[0][0]
# @lc code=end
