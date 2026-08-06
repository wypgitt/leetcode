#
# @lc app=leetcode id=2387 lang=python3
#
# [2387] Median of a Row Wise Sorted Matrix
#
# https://leetcode.com/problems/median-of-a-row-wise-sorted-matrix/description/
#
# algorithms
# Medium (70.94%)
# Likes:    91
# Dislikes: 9
# Total Accepted:    6.3K
# Total Submissions: 8.9K
# Testcase Example:  "[[1,1,2],[2,3,3],[1,3,4]]"
#
#
# Given an m x n matrix grid containing an odd number of integers where
# each row is sorted in non-decreasing order, return the median of the
# matrix.
#
# You must solve the problem in less than O(m * n) time complexity.
#
# Example 1:
#
# Input: grid = [[1,1,2],[2,3,3],[1,3,4]]
# Output: 2
# Explanation: The elements of the matrix in sorted order are
# 1,1,1,2,2,3,3,3,4. The median is 2.
#
# Example 2:
#
# Input: grid = [[1,1,3,3,4]]
# Output: 3
# Explanation: The elements of the matrix in sorted order are 1,1,3,3,4.
# The median is 3.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 500
#
# m and n are both odd.
#
# 1 <= grid[i][j] <= 10^6
#
# grid[i] is sorted in non-decreasing order.
#
# @lc code=start

from typing import List
from bisect import bisect_right, bisect_left


class Solution:
    def matrixMedian(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium: m x n matrix (m,n odd), each row sorted. Find median of all
        elements in < O(mn) time.

        Algorithm:
        - Binary search value x; count how many <= x via bisect per row; find
          smallest x with count >= (mn+1)//2.

        Complexity: O(m log n log M) time, O(1) space.
        """
        m, n = len(grid), len(grid[0])
        target = (m * n + 1) // 2
        lo, hi = 1, 10**6
        while lo < hi:
            mid = (lo + hi) // 2
            cnt = sum(bisect_right(row, mid) for row in grid)
            if cnt >= target:
                hi = mid
            else:
                lo = mid + 1
        return lo

    def matrixMedian_binary_search(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: same binary search using bisect_left on value range with key.

        Algorithm:
        - bisect_left(range, target, key=count_le).

        Complexity: O(m log n log M) time, O(1) space.
        """
        m, n = len(grid), len(grid[0])
        target = (m * n + 1) // 2

        def count(x: int) -> int:
            return sum(bisect_right(row, x) for row in grid)

        return bisect_left(range(10**6 + 1), target, key=count)
# @lc code=end
