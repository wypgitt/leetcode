#
# @lc app=leetcode id=1439 lang=python3
#
# [1439] Find the Kth Smallest Sum of a Matrix With Sorted Rows
#
# https://leetcode.com/problems/find-the-kth-smallest-sum-of-a-matrix-with-sorted-rows/description/
#
# algorithms
# Hard (62.43%)
# Likes:    1309
# Dislikes: 21
# Total Accepted:    44.9K
# Total Submissions: 72.0K
# Testcase Example:  "[[1,3,11],[2,4,6]]"
#
# You are given an m x n matrix mat that has its rows sorted in non-decreasing
# order and an integer k.
#
# You are allowed to choose exactly one element from each row to form an array.
#
# Return the k^th smallest array sum among all possible arrays.
#
# Example 1:
#
# Input: mat = [[1,3,11],[2,4,6]], k = 5
# Output: 7
# Explanation: Choosing one element from each row, the first k smallest sum
# are:
# [1,2], [1,4], [3,2], [3,4], [1,6]. Where the 5th sum is 7.
#
# Example 2:
#
# Input: mat = [[1,3,11],[2,4,6]], k = 9
# Output: 17
#
# Example 3:
#
# Input: mat = [[1,10,10],[1,4,5],[2,3,6]], k = 7
# Output: 9
# Explanation: Choosing one element from each row, the first k smallest sum
# are:
# [1,1,2], [1,1,3], [1,4,2], [1,4,3], [1,1,6], [1,5,2], [1,5,3]. Where the 7th
# sum is 9.
#
# Constraints:
#
# m == mat.length
#
# n == mat.length[i]
#
# 1 <= m, n <= 40
#
# 1 <= mat[i][j] <= 5000
#
# 1 <= k <= min(200, n^m)
#
# mat[i] is a non-decreasing array.
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def kthSmallest(self, mat: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Each row sorted; pick one from each row; find k-th smallest sum.
        Iteratively merge: maintain top-k smallest sums after adding each row
        via a min-heap / bounded merge.

        Algorithm:
        (row-by-row heap merge)
        - start with [0]; for each row, generate new sums with heap, keep k smallest.

        Complexity: O(m * k * n log (k*n)) roughly O(m k n log(kn)), space O(k*n).
        """
        prev = [0]
        for row in mat:
            heap = []
            for s in prev:
                for x in row:
                    heapq.heappush(heap, s + x)
            # keep only k smallest
            prev = [heapq.heappop(heap) for _ in range(min(k, len(heap)))]
        return prev[k - 1]

    def kthSmallest_binary(self, mat: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Alternate: binary search on sum value; count how many combinations <= mid
        with DFS pruning (classic for this problem).

        Algorithm:
        - lo=sum first cols, hi=sum last; count(mid) via DFS; binary search k-th.

        Complexity: O((hi-lo) log * search) with pruned DFS; practical for constraints.
        """
        m, n = len(mat), len(mat[0])
        lo = sum(r[0] for r in mat)
        hi = sum(r[-1] for r in mat)

        def count_leq(limit: int) -> int:
            # count combinations with sum <= limit, capped at k
            self.cnt = 0

            def dfs(r: int, s: int) -> None:
                if self.cnt >= k:
                    return
                if r == m:
                    self.cnt += 1
                    return
                for j in range(n):
                    if s + mat[r][j] > limit:
                        break
                    dfs(r + 1, s + mat[r][j])

            dfs(0, 0)
            return self.cnt

        while lo < hi:
            mid = (lo + hi) // 2
            if count_leq(mid) >= k:
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
