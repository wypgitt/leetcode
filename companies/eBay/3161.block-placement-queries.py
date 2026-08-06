#
# @lc app=leetcode id=3161 lang=python3
#
# [3161] Block Placement Queries
#
# https://leetcode.com/problems/block-placement-queries/description/
#
# algorithms
# Hard (41.43%)
# Likes:    335
# Dislikes: 47
# Total Accepted:    67.1K
# Total Submissions: 162K
# Testcase Example:  "[[1,2],[2,3,3],[2,3,1],[2,2,2]]"
#
#
# There exists an infinite number line, with its origin at 0 and extending
# towards the positive x-axis.
#
# You are given a 2D array queries, which contains two types of queries:
#
# For a query of type 1, queries[i] = [1, x]. Build an obstacle at
# distance x from the origin. It is guaranteed that there is no obstacle
# at distance x when the query is asked.
#
# For a query of type 2, queries[i] = [2, x, sz]. Check if it is possible
# to place a block of size sz anywhere in the range [0, x] on the line,
# such that the block entirely lies in the range [0, x]. A block cannot be
# placed if it intersects with any obstacle, but it may touch it. Note
# that you do not actually place the block. Queries are separate.
#
# Return a boolean array results, where results[i] is true if you can
# place the block specified in the i^th query of type 2, and false
# otherwise.
#
# Example 1:
#
# Input: queries = [[1,2],[2,3,3],[2,3,1],[2,2,2]]
#
# Output: [false,true,true]
#
# Explanation:
#
# For query 0, place an obstacle at x = 2. A block of size at most 2 can
# be placed before x = 3.
#
# Example 2:
#
# Input: queries = [[1,7],[2,7,6],[1,2],[2,7,5],[2,7,6]]
#
# Output: [true,true,false]
#
# Explanation:
#
# Place an obstacle at x = 7 for query 0. A block of size at most 7 can be
# placed before x = 7.
#
# Place an obstacle at x = 2 for query 2. Now, a block of size at most 5
# can be placed before x = 7, and a block of size at most 2 before x = 2.
#
# Constraints:
#
# 1 <= queries.length <= 15 * 10^4
#
# 2 <= queries[i].length <= 3
#
# 1 <= queries[i][0] <= 2
#
# 1 <= x, sz <= min(5 * 10^4, 3 * queries.length)
#
# The input is generated such that for queries of type 1, no obstacle
# exists at distance x when the query is asked.
#
# The input is generated such that there is at least one query of type 2.
#

# @lc code=start
from typing import List


class Solution:
    def getResults(self, queries: List[List[int]]) -> List[bool]:
        """
        Interview explanation:
        Online obstacles on [0, +∞). Type-1 places an obstacle; type-2 asks if a
        block of size sz fits entirely in [0, x] without crossing obstacles.

        Algorithm:
        - Maintain obstacles (plus sentinel) in a position min/max segtree.
        - Store gap length at each obstacle's right endpoint in a max segtree.
        - Insert x: split gap (L,R) into (L,x) and (x,R).
        - Query: max complete gap with right end <= last obstacle ≤ x, and
          the partial gap x - that obstacle.

        Complexity: O(Q log C) time with C≤5e4, O(C) space.
        """
        SENT = 50001
        n = SENT + 1

        class MaxSeg:
            def __init__(self, size: int):
                self.size = size
                self.t = [0] * (4 * size)

            def update(self, idx: int, val: int, node: int = 1, l: int = 0, r: int | None = None) -> None:
                if r is None:
                    r = self.size - 1
                if l == r:
                    self.t[node] = val
                    return
                m = (l + r) // 2
                if idx <= m:
                    self.update(idx, val, node * 2, l, m)
                else:
                    self.update(idx, val, node * 2 + 1, m + 1, r)
                self.t[node] = max(self.t[node * 2], self.t[node * 2 + 1])

            def query(self, ql: int, qr: int, node: int = 1, l: int = 0, r: int | None = None) -> int:
                if r is None:
                    r = self.size - 1
                if qr < l or r < ql or ql > qr:
                    return 0
                if ql <= l and r <= qr:
                    return self.t[node]
                m = (l + r) // 2
                return max(
                    self.query(ql, qr, node * 2, l, m),
                    self.query(ql, qr, node * 2 + 1, m + 1, r),
                )

        class PosSeg:
            INF = 10**9

            def __init__(self, size: int):
                self.size = size
                self.mn = [self.INF] * (4 * size)
                self.mx = [-self.INF] * (4 * size)

            def update(self, idx: int, on: bool, node: int = 1, l: int = 0, r: int | None = None) -> None:
                if r is None:
                    r = self.size - 1
                if l == r:
                    if on:
                        self.mn[node] = self.mx[node] = l
                    else:
                        self.mn[node] = self.INF
                        self.mx[node] = -self.INF
                    return
                m = (l + r) // 2
                if idx <= m:
                    self.update(idx, on, node * 2, l, m)
                else:
                    self.update(idx, on, node * 2 + 1, m + 1, r)
                self.mn[node] = min(self.mn[node * 2], self.mn[node * 2 + 1])
                self.mx[node] = max(self.mx[node * 2], self.mx[node * 2 + 1])

            def query_max(self, ql: int, qr: int, node: int = 1, l: int = 0, r: int | None = None) -> int:
                if r is None:
                    r = self.size - 1
                if qr < l or r < ql or ql > qr:
                    return -self.INF
                if ql <= l and r <= qr:
                    return self.mx[node]
                m = (l + r) // 2
                return max(
                    self.query_max(ql, qr, node * 2, l, m),
                    self.query_max(ql, qr, node * 2 + 1, m + 1, r),
                )

            def query_min(self, ql: int, qr: int, node: int = 1, l: int = 0, r: int | None = None) -> int:
                if r is None:
                    r = self.size - 1
                if qr < l or r < ql or ql > qr:
                    return self.INF
                if ql <= l and r <= qr:
                    return self.mn[node]
                m = (l + r) // 2
                return min(
                    self.query_min(ql, qr, node * 2, l, m),
                    self.query_min(ql, qr, node * 2 + 1, m + 1, r),
                )

        gap = MaxSeg(n)
        pos = PosSeg(n)
        pos.update(0, True)
        pos.update(SENT, True)
        gap.update(SENT, SENT)

        ans: List[bool] = []
        for q in queries:
            if q[0] == 1:
                x = q[1]
                left = pos.query_max(0, x - 1)
                right = pos.query_min(x + 1, SENT)
                pos.update(x, True)
                gap.update(x, x - left)
                gap.update(right, right - x)
            else:
                x, sz = q[1], q[2]
                left = pos.query_max(0, x)
                best = gap.query(1, left) if left >= 1 else 0
                best = max(best, x - left)
                ans.append(best >= sz)
        return ans
# @lc code=end
