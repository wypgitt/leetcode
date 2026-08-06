#
# @lc app=leetcode id=3462 lang=python3
#
# [3462] Maximum Sum With at Most K Elements
#
# https://leetcode.com/problems/maximum-sum-with-at-most-k-elements/description/
#
# algorithms
# Medium (60.48%)
# Likes:    116
# Dislikes: 5
# Total Accepted:    41.4K
# Total Submissions: 68.4K
# Testcase Example:  "[[1,2],[3,4]]\n[1,2]\n2"
#
#
# You are given a 2D integer matrix grid of size n x m, an integer array
# limits of length n, and an integer k. The task is to find the maximum
# sum of at most k elements from the matrix grid such that:
#
# The number of elements taken from the i^th row of grid does not exceed
# limits[i].
#
# Return the maximum sum.
#
# Example 1:
#
# Input: grid = [[1,2],[3,4]], limits = [1,2], k = 2
#
# Output: 7
#
# Explanation:
#
# From the second row, we can take at most 2 elements. The elements taken
# are 4 and 3.
#
# The maximum possible sum of at most 2 selected elements is 4 + 3 = 7.
#
# Example 2:
#
# Input: grid = [[5,3,7],[8,2,6]], limits = [2,2], k = 3
#
# Output: 21
#
# Explanation:
#
# From the first row, we can take at most 2 elements. The element taken is
# 7.
#
# From the second row, we can take at most 2 elements. The elements taken
# are 8 and 6.
#
# The maximum possible sum of at most 3 selected elements is 7 + 8 + 6 =
# 21.
#
# Constraints:
#
# n == grid.length == limits.length
#
# m == grid[i].length
#
# 1 <= n, m <= 500
#
# 0 <= grid[i][j] <= 10^5
#
# 0 <= limits[i] <= m
#
# 0 <= k <= min(n * m, sum(limits))
#

# @lc code=start
from typing import List


class Solution:
    def maxSum(self, grid: List[List[int]], limits: List[int], k: int) -> int:
        """
        Interview explanation:
        From each row take at most limits[i] largest values, then globally take
        the top k among those candidates.

        Algorithm:
        - For each row, sort descending and keep the first limits[i] entries.
        - Sort all candidates descending; sum the first k.

        Complexity: O(n m log m + (sum limits) log) time, O(sum limits) space.
        """
        candidates: List[int] = []
        for row, lim in zip(grid, limits):
            candidates.extend(sorted(row, reverse=True)[:lim])
        candidates.sort(reverse=True)
        return sum(candidates[:k])

    def maxSum_heap(self, grid: List[List[int]], limits: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: push row-limited candidates into a min-heap of size k.

        Algorithm:
        - Collect top limits[i] per row; maintain a size-k min-heap of values.

        Complexity: O(n m log m + N log k) time, O(k) space beyond candidates.
        """
        import heapq

        candidates: List[int] = []
        for row, lim in zip(grid, limits):
            candidates.extend(sorted(row, reverse=True)[:lim])
        if k == 0:
            return 0
        heap: List[int] = []
        for x in candidates:
            if len(heap) < k:
                heapq.heappush(heap, x)
            elif x > heap[0]:
                heapq.heapreplace(heap, x)
        return sum(heap)
# @lc code=end

