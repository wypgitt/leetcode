#
# @lc app=leetcode id=947 lang=python3
#
# [947] Most Stones Removed with Same Row or Column
#
# https://leetcode.com/problems/most-stones-removed-with-same-row-or-column/description/
#
# algorithms
# Medium (63.35%)
# Likes:    6545
# Dislikes: 710
# Total Accepted:    427K
# Total Submissions: 675K
# Testcase Example:  "[[0,0],[0,1],[1,0],[1,2],[2,1],[2,2]]"
#
# On a 2D plane, we place n stones at some integer coordinate points. Each
# coordinate point may have at most one stone.
#
# A stone can be removed if it shares either the same row or the same column as
# another stone that has not been removed.
#
# Given an array stones of length n where stones[i] = [x_i, y_i] represents the
# location of the i^th stone, return the largest possible number of stones that
# can be removed.
#
# Example 1:
#
# Input: stones = [[0,0],[0,1],[1,0],[1,2],[2,1],[2,2]]
# Output: 5
# Explanation: One way to remove 5 stones is as follows:
# 1. Remove stone [2,2] because it shares the same row as [2,1].
# 2. Remove stone [2,1] because it shares the same column as [0,1].
# 3. Remove stone [1,2] because it shares the same row as [1,0].
# 4. Remove stone [1,0] because it shares the same column as [0,0].
# 5. Remove stone [0,1] because it shares the same row as [0,0].
# Stone [0,0] cannot be removed since it does not share a row/column with
# another stone still on the plane.
#
# Example 2:
#
# Input: stones = [[0,0],[0,2],[1,1],[2,0],[2,2]]
# Output: 3
# Explanation: One way to make 3 moves is as follows:
# 1. Remove stone [2,2] because it shares the same row as [2,0].
# 2. Remove stone [2,0] because it shares the same column as [0,0].
# 3. Remove stone [0,2] because it shares the same row as [0,0].
# Stones [0,0] and [1,1] cannot be removed since they do not share a row/column
# with another stone still on the plane.
#
# Example 3:
#
# Input: stones = [[0,0]]
# Output: 0
# Explanation: [0,0] is the only stone on the plane, so you cannot remove it.
#
# Constraints:
#
# 1 <= stones.length <= 1000
#
# 0 <= x_i, y_i <= 10^4
#
# No two stones are at the same coordinate point.
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def removeStones(self, stones: List[List[int]]) -> int:
        """
        Interview explanation:
        Stones sharing a row or column are connected. In a connected component
        of size k you can remove k-1 stones. Answer = n - (#components).
        Union-Find on stones (or on row/col ids).

        Algorithm (Union-Find):
        - Map row r → node, col c → node + offset; union each stone's row & col
        - components = unique roots among used nodes
        - Return len(stones) - components

        Complexity: O(n α(n)) time, O(n) space.
        """
        parent = {}

        def find(x: int) -> int:
            parent.setdefault(x, x)
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        # distinguish rows and cols
        OFFSET = 10001
        for r, c in stones:
            union(r, c + OFFSET)

        roots = {find(r) for r, c in stones}
        return len(stones) - len(roots)

    def removeStones_dfs(self, stones: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate classic: build graph (edge if same row/col), DFS count
        components; answer = n - components.

        Algorithm (DFS):
        - Index stones; adj via row/col maps
        - DFS unmarked stones; count components
        - Return n - components

        Complexity: O(n^2) naive edges or O(n) with row/col lists; O(n) space.
        """
        n = len(stones)
        rows = defaultdict(list)
        cols = defaultdict(list)
        for i, (r, c) in enumerate(stones):
            rows[r].append(i)
            cols[c].append(i)
        seen = [False] * n

        def dfs(i: int) -> None:
            seen[i] = True
            r, c = stones[i]
            for j in rows[r]:
                if not seen[j]:
                    dfs(j)
            for j in cols[c]:
                if not seen[j]:
                    dfs(j)

        comps = 0
        for i in range(n):
            if not seen[i]:
                dfs(i)
                comps += 1
        return n - comps
# @lc code=end

