#
# @lc app=leetcode id=305 lang=python3
#
# [305] Number of Islands II
#
# https://leetcode.com/problems/number-of-islands-ii/description/
#
# algorithms
# Hard (40.69%)
# Likes:    2004
# Dislikes: 78
# Total Accepted:    186.2K
# Total Submissions: 457.6K
# Testcase Example:  "3\n3\n[[0,0],[0,1],[1,2],[2,1]]"
#
#
# You are given an empty 2D binary grid grid of size m x n. The grid
# represents a map where 0's represent water and 1's represent land.
# Initially, all the cells of grid are water cells (i.e., all the cells
# are 0's).
#
# We may perform an add land operation which turns the water at position
# into a land. You are given an array positions where positions[i] = [r_i,
# c_i] is the position (r_i, c_i) at which we should operate the i^th
# operation.
#
# Return an array of integers answer where answer[i] is the number of
# islands after turning the cell (r_i, c_i) into a land.
#
# An island is surrounded by water and is formed by connecting adjacent
# lands horizontally or vertically. You may assume all four edges of the
# grid are all surrounded by water.
#
# Example 1:
#
# Input: m = 3, n = 3, positions = [[0,0],[0,1],[1,2],[2,1]]
# Output: [1,1,2,3]
# Explanation:
# Initially, the 2d grid is filled with water.
# - Operation #1: addLand(0, 0) turns the water at grid[0][0] into a land.
# We have 1 island.
# - Operation #2: addLand(0, 1) turns the water at grid[0][1] into a land.
# We still have 1 island.
# - Operation #3: addLand(1, 2) turns the water at grid[1][2] into a land.
# We have 2 islands.
# - Operation #4: addLand(2, 1) turns the water at grid[2][1] into a land.
# We have 3 islands.
#
# Example 2:
#
# Input: m = 1, n = 1, positions = [[0,0]]
# Output: [1]
#
# Constraints:
#
# 1 <= m, n, positions.length <= 10^4
#
# 1 <= m * n <= 10^4
#
# positions[i].length == 2
#
# 0 <= r_i < m
#
# 0 <= c_i < n
#
# Follow up: Could you solve it in time complexity O(k log(mn)), where k
# == positions.length?
#
# @lc code=start
from typing import List


class Solution:
    def numIslands2(self, m: int, n: int, positions: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Online land additions; after each add, report island count. Union-Find
        merges a new land cell with adjacent lands (4-dir).

        Algorithm:
        - parent/rank for mn cells; land set or parent[id] initialized lazily.
        - On add (r,c): if new, count++; union with each neighboring land,
          decrement count on each successful merge.

        Complexity: O(k α(mn)) for k positions, O(mn) space.
        """
        parent = [-1] * (m * n)
        rank = [0] * (m * n)
        count = 0
        ans = []

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> bool:
            ra, rb = find(a), find(b)
            if ra == rb:
                return False
            if rank[ra] < rank[rb]:
                parent[ra] = rb
            elif rank[ra] > rank[rb]:
                parent[rb] = ra
            else:
                parent[rb] = ra
                rank[ra] += 1
            return True

        for r, c in positions:
            idx = r * n + c
            if parent[idx] != -1:
                ans.append(count)
                continue
            parent[idx] = idx
            count += 1
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n:
                    nidx = nr * n + nc
                    if parent[nidx] != -1 and union(idx, nidx):
                        count -= 1
            ans.append(count)
        return ans
# @lc code=end

