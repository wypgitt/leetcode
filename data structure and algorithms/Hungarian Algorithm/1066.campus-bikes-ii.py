#
# @lc app=leetcode id=1066 lang=python3
#
# [1066] Campus Bikes II
#
# https://leetcode.com/problems/campus-bikes-ii/description/
#
# algorithms
# Medium (55.84%)
# Likes:    969
# Dislikes: 89
# Total Accepted:    57.8K
# Total Submissions: 103.4K
# Testcase Example:  "[[0,0],[2,1]]\n[[1,2],[3,3]]"
#
#
# On a campus represented as a 2D grid, there are n workers and m bikes,
# with n <= m. Each worker and bike is a 2D coordinate on this grid.
#
# We assign one unique bike to each worker so that the sum of the
# Manhattan distances between each worker and their assigned bike is
# minimized.
#
# Return the minimum possible sum of Manhattan distances between each
# worker and their assigned bike.
#
# The Manhattan distance between two points p1 and p2 is Manhattan(p1, p2)
# = |p1.x - p2.x| + |p1.y - p2.y|.
#
# Example 1:
#
# Input: workers = [[0,0],[2,1]], bikes = [[1,2],[3,3]]
# Output: 6
# Explanation:
# We assign bike 0 to worker 0, bike 1 to worker 1. The Manhattan distance
# of both assignments is 3, so the output is 6.
#
# Example 2:
#
# Input: workers = [[0,0],[1,1],[2,0]], bikes = [[1,0],[2,2],[2,1]]
# Output: 4
# Explanation:
# We first assign bike 0 to worker 0, then assign bike 1 to worker 1 or
# worker 2, bike 2 to worker 2 or worker 1. Both assignments lead to sum
# of the Manhattan distances as 4.
#
# Example 3:
#
# Input: workers = [[0,0],[1,0],[2,0],[3,0],[4,0]], bikes =
# [[0,999],[1,999],[2,999],[3,999],[4,999]]
# Output: 4995
#
# Constraints:
#
# n == workers.length
#
# m == bikes.length
#
# 1 <= n <= m <= 10
#
# workers[i].length == 2
#
# bikes[i].length == 2
#
# 0 <= workers[i][0], workers[i][1], bikes[i][0], bikes[i][1] < 1000
#
# All the workers and the bikes locations are unique.
#
# @lc code=start
from functools import lru_cache
from typing import List


class Solution:
    def assignBikes(self, workers: List[List[int]], bikes: List[List[int]]) -> int:
        """
        Interview explanation:
        Premium. Assign each worker a distinct bike minimizing total Manhattan
        distance. Bitmask DP over used bikes: dfs(i, mask) = min cost to assign
        workers[i:] with bikes in mask already taken.

        Algorithm:
        - dfs(worker_idx, bike_mask): try each free bike; recurse
        - Memoize; return dfs(0,0)

        Complexity: O(W * 2^B * B) time, O(W * 2^B) space.
        """
        W, B = len(workers), len(bikes)

        @lru_cache(None)
        def dfs(i: int, mask: int) -> int:
            if i == W:
                return 0
            best = float("inf")
            wx, wy = workers[i]
            for j in range(B):
                if mask & (1 << j):
                    continue
                bx, by = bikes[j]
                cost = abs(wx - bx) + abs(wy - by)
                best = min(best, cost + dfs(i + 1, mask | (1 << j)))
            return best

        return dfs(0, 0)

    def assignBikes_bottom_up(self, workers: List[List[int]], bikes: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate bottom-up DP on bike masks: dp[mask] = min cost to assign
        popcount(mask) workers using those bikes (workers assigned in order).

        Algorithm:
        - dp[0]=0; for each mask, i=popcount; try add a free bike for worker i

        Complexity: O(2^B * B) time (W<=B), O(2^B) space.
        """
        W, B = len(workers), len(bikes)
        INF = 10**9
        dp = [INF] * (1 << B)
        dp[0] = 0
        for mask in range(1 << B):
            i = bin(mask).count("1")
            if i >= W:
                continue
            if dp[mask] >= INF:
                continue
            wx, wy = workers[i]
            for j in range(B):
                if mask & (1 << j):
                    continue
                bx, by = bikes[j]
                nmask = mask | (1 << j)
                dp[nmask] = min(dp[nmask], dp[mask] + abs(wx - bx) + abs(wy - by))
        ans = INF
        for mask in range(1 << B):
            if bin(mask).count("1") == W:
                ans = min(ans, dp[mask])
        return ans
# @lc code=end
